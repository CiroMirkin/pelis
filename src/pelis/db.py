"""Base SQLite: esquema y consultas. Las rutas guardadas son relativas a la raíz de la biblioteca."""

import sqlite3

ESQUEMA = """
CREATE TABLE IF NOT EXISTS peliculas (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo            TEXT NOT NULL,
    year              INTEGER,
    folder_path       TEXT NOT NULL UNIQUE,
    video_path        TEXT NOT NULL,
    sinopsis          TEXT,
    pais              TEXT,
    genero            TEXT,
    poster_actual_id      INTEGER REFERENCES posters(id),
    poster_actualizado_en DATETIME,
    watched           BOOLEAN DEFAULT 0,
    watched_at        DATETIME,
    progreso_ms       INTEGER DEFAULT 0,
    duracion_ms       INTEGER,
    omdb_id           TEXT,
    omdb_estado       TEXT DEFAULT 'pendiente',
    fecha_agregada    DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado            TEXT DEFAULT 'activa',
    fecha_papelera    DATETIME,
    metadatos_origen  TEXT DEFAULT 'omdb',
    sinopsis_idioma   TEXT,
    poster_url        TEXT
);

CREATE TABLE IF NOT EXISTS posters (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pelicula_id     INTEGER NOT NULL REFERENCES peliculas(id),
    path            TEXT NOT NULL,
    origen          TEXT NOT NULL,
    fecha_agregado  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personas (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS pelicula_personas (
    pelicula_id  INTEGER NOT NULL REFERENCES peliculas(id),
    persona_id   INTEGER NOT NULL REFERENCES personas(id),
    rol          TEXT NOT NULL,
    PRIMARY KEY (pelicula_id, persona_id, rol)
);
"""


def conectar(ruta):
    conn = sqlite3.connect(ruta)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(ESQUEMA)
    # Bases creadas antes de que existieran estas columnas
    existentes = {f["name"] for f in conn.execute("PRAGMA table_info(peliculas)")}
    for columna in ("sinopsis_idioma", "poster_url"):
        if columna not in existentes:
            conn.execute(f"ALTER TABLE peliculas ADD COLUMN {columna} TEXT")
    return conn


# --- escaneo ---

def peliculas_por_carpeta(conn):
    return {r["folder_path"]: r for r in conn.execute("SELECT id, folder_path, estado, omdb_estado FROM peliculas")}


def insertar_pelicula(conn, titulo, year, folder_path, video_path):
    cur = conn.execute(
        "INSERT INTO peliculas (titulo, year, folder_path, video_path) VALUES (?, ?, ?, ?)",
        (titulo, year, folder_path, video_path),
    )
    return cur.lastrowid


def fijar_metadatos(conn, pelicula_id, titulo, year, imdb_id=None, sinopsis=None, sinopsis_idioma=None, pais=None,
                    genero=None, poster_url=None, origen="omdb", directores=(), actores=()):
    """Guarda los metadatos tal cual, sin reglas: las decide `metadatos.aplicar`."""
    conn.execute(
        """UPDATE peliculas SET omdb_estado = 'encontrada', titulo = ?, year = ?, omdb_id = ?, sinopsis = ?,
           sinopsis_idioma = ?, pais = ?, genero = ?, poster_url = ?, metadatos_origen = ? WHERE id = ?""",
        (titulo, year, imdb_id, sinopsis, sinopsis_idioma, pais, genero, poster_url, origen, pelicula_id),
    )
    _fijar_personas(conn, pelicula_id, directores, actores)


def completar_extras(conn, pelicula_id, sinopsis_idioma, poster_url):
    """Campos que antes solo vivían en pelis.json; no pisa lo que la base ya tiene."""
    conn.execute(
        """UPDATE peliculas SET sinopsis_idioma = COALESCE(sinopsis_idioma, ?), poster_url = COALESCE(poster_url, ?)
           WHERE id = ?""",
        (sinopsis_idioma, poster_url, pelicula_id),
    )


def con_metadatos(conn):
    """Ids de las activas con datos de IMDb: las que tienen un pelis.json que mantener."""
    return [f[0] for f in conn.execute(
        "SELECT id FROM peliculas WHERE omdb_estado = 'encontrada' AND estado = 'activa' ORDER BY id")]


def _fijar_personas(conn, pelicula_id, directores, actores):
    conn.execute("DELETE FROM pelicula_personas WHERE pelicula_id = ?", (pelicula_id,))
    for rol, nombres in (("director", directores), ("actor", actores)):
        for nombre in nombres:
            conn.execute("INSERT OR IGNORE INTO personas (nombre) VALUES (?)", (nombre,))
            persona_id = conn.execute("SELECT id FROM personas WHERE nombre = ?", (nombre,)).fetchone()[0]
            conn.execute(
                "INSERT OR IGNORE INTO pelicula_personas (pelicula_id, persona_id, rol) VALUES (?, ?, ?)",
                (pelicula_id, persona_id, rol),
            )


def con_omdb_id(conn, omdb_id, fuera_de):
    """Id de un registro activo o faltante con ese omdb_id cuya carpeta no está en `fuera_de`, o None."""
    for fila in conn.execute(
        "SELECT id, folder_path FROM peliculas WHERE lower(omdb_id) = lower(?) AND estado IN ('activa', 'faltante')",
        (omdb_id,),
    ):
        if fila["folder_path"] not in fuera_de:
            return fila["id"]
    return None


def reasignar(conn, pelicula_id, folder_path, video_path):
    """Mueve el registro a otra carpeta (renombrada), con sus posters, y lo vuelve a activar."""
    viejo = conn.execute("SELECT folder_path FROM peliculas WHERE id = ?", (pelicula_id,)).fetchone()[0]
    conn.execute(
        "UPDATE peliculas SET folder_path = ?, video_path = ?, estado = 'activa' WHERE id = ?",
        (folder_path, video_path, pelicula_id),
    )
    conn.execute(
        "UPDATE posters SET path = ? || substr(path, ?) WHERE pelicula_id = ? AND substr(path, 1, ?) = ?",
        (folder_path, len(viejo) + 1, pelicula_id, len(viejo) + 1, viejo + "/"),
    )


def fusionar(conn, faltante_id, nueva_id):
    """El registro faltante pasa a la carpeta de `nueva_id`, que se borra.

    Conserva progreso, vista y metadatos del faltante; si este no tenía metadatos, toma los de la
    nueva. Los posters pasan a ser los de la carpeta nueva.
    """
    f = conn.execute("SELECT * FROM peliculas WHERE id = ?", (faltante_id,)).fetchone()
    n = conn.execute("SELECT * FROM peliculas WHERE id = ?", (nueva_id,)).fetchone()
    conn.execute("UPDATE peliculas SET poster_actual_id = NULL WHERE id = ?", (faltante_id,))
    conn.execute("DELETE FROM posters WHERE pelicula_id = ?", (faltante_id,))
    conn.execute("UPDATE posters SET pelicula_id = ? WHERE pelicula_id = ?", (faltante_id, nueva_id))
    if f["omdb_estado"] != "encontrada" and n["omdb_estado"] == "encontrada":
        conn.execute("DELETE FROM pelicula_personas WHERE pelicula_id = ?", (faltante_id,))
        conn.execute("UPDATE pelicula_personas SET pelicula_id = ? WHERE pelicula_id = ?", (faltante_id, nueva_id))
        conn.execute(
            """UPDATE peliculas SET titulo = ?, year = ?, sinopsis = ?, sinopsis_idioma = ?, pais = ?, genero = ?,
               poster_url = ?, omdb_id = ?, omdb_estado = ?, metadatos_origen = ? WHERE id = ?""",
            (n["titulo"], n["year"], n["sinopsis"], n["sinopsis_idioma"], n["pais"], n["genero"], n["poster_url"],
             n["omdb_id"], n["omdb_estado"], n["metadatos_origen"], faltante_id),
        )
    conn.execute("DELETE FROM pelicula_personas WHERE pelicula_id = ?", (nueva_id,))
    conn.execute("DELETE FROM peliculas WHERE id = ?", (nueva_id,))
    conn.execute(
        """UPDATE peliculas SET folder_path = ?, video_path = ?, estado = 'activa', poster_actual_id = ?,
           poster_actualizado_en = ?, duracion_ms = COALESCE(?, duracion_ms),
           progreso_ms = CASE WHEN progreso_ms > 0 THEN progreso_ms ELSE ? END,
           watched = MAX(watched, ?), watched_at = COALESCE(watched_at, ?) WHERE id = ?""",
        (n["folder_path"], n["video_path"], n["poster_actual_id"], n["poster_actualizado_en"], n["duracion_ms"],
         n["progreso_ms"], n["watched"], n["watched_at"], faltante_id),
    )


def marcar_no_encontrada(conn, pelicula_id):
    conn.execute("UPDATE peliculas SET omdb_estado = 'no_encontrada' WHERE id = ?", (pelicula_id,))


def marcar_pendiente(conn, pelicula_id):
    conn.execute("UPDATE peliculas SET omdb_estado = 'pendiente' WHERE id = ?", (pelicula_id,))


def cambiar_estado(conn, pelicula_id, estado):
    conn.execute("UPDATE peliculas SET estado = ? WHERE id = ?", (estado, pelicula_id))


# --- app ---

def catalogo(conn):
    return conn.execute(
        """SELECT p.id, p.titulo, p.year, p.watched, p.progreso_ms, p.duracion_ms, p.omdb_estado, po.path AS poster,
                  (SELECT group_concat(pe.nombre, ' | ') FROM pelicula_personas pp
                   JOIN personas pe ON pe.id = pp.persona_id WHERE pp.pelicula_id = p.id) AS personas
           FROM peliculas p LEFT JOIN posters po ON po.id = p.poster_actual_id
           WHERE p.estado = 'activa'
           ORDER BY p.watched, (p.progreso_ms > 0 AND NOT p.watched) DESC, p.titulo COLLATE NOCASE"""
    ).fetchall()


def faltantes(conn):
    return conn.execute(
        """SELECT id, titulo, year, folder_path, progreso_ms, watched FROM peliculas
           WHERE estado = 'faltante' ORDER BY titulo COLLATE NOCASE"""
    ).fetchall()


def activas_recientes(conn):
    """Activas, las agregadas último primero: entre ellas suele estar la carpeta renombrada."""
    return conn.execute(
        """SELECT id, titulo, year, folder_path FROM peliculas WHERE estado = 'activa'
           ORDER BY fecha_agregada DESC, id DESC"""
    ).fetchall()


def recomendada(conn):
    """Una película al azar para ver: activa, no vista y sin empezar (las empezadas ya van primero)."""
    return conn.execute(
        """SELECT p.id, p.titulo, p.year, p.genero, p.duracion_ms, p.video_path, po.path AS poster
           FROM peliculas p LEFT JOIN posters po ON po.id = p.poster_actual_id
           WHERE p.estado = 'activa' AND NOT p.watched AND COALESCE(p.progreso_ms, 0) = 0
           ORDER BY random() LIMIT 1"""
    ).fetchone()


def personas_de(conn, pelicula_id, rol):
    """[(nombre, otras)] de la película: `otras` es en cuántas otras películas activas participa."""
    return [(r[0], r[1]) for r in conn.execute(
        """SELECT pe.nombre,
                  (SELECT count(DISTINCT pp2.pelicula_id) FROM pelicula_personas pp2
                   JOIN peliculas p2 ON p2.id = pp2.pelicula_id
                   WHERE pp2.persona_id = pe.id AND pp2.pelicula_id != ? AND p2.estado = 'activa')
           FROM pelicula_personas pp JOIN personas pe ON pe.id = pp.persona_id
           WHERE pp.pelicula_id = ? AND pp.rol = ? ORDER BY pe.rowid""",
        (pelicula_id, pelicula_id, rol),
    )]


def peliculas_de_persona(conn, nombre):
    """Películas activas donde participa `nombre`, con sus roles ('director', 'actor'), por año."""
    return conn.execute(
        """SELECT p.id, p.titulo, p.year, p.watched, p.progreso_ms, p.duracion_ms, p.omdb_estado, po.path AS poster,
                  group_concat(pp.rol) AS roles
           FROM peliculas p
           JOIN pelicula_personas pp ON pp.pelicula_id = p.id
           JOIN personas pe ON pe.id = pp.persona_id
           LEFT JOIN posters po ON po.id = p.poster_actual_id
           WHERE pe.nombre = ? AND p.estado = 'activa'
           GROUP BY p.id ORDER BY p.year IS NULL, p.year, p.titulo COLLATE NOCASE""",
        (nombre,),
    ).fetchall()


def pelicula(conn, pelicula_id):
    fila = conn.execute(
        """SELECT p.*, po.path AS poster FROM peliculas p
           LEFT JOIN posters po ON po.id = p.poster_actual_id WHERE p.id = ?""",
        (pelicula_id,),
    ).fetchone()
    if fila is None:
        return None
    datos = dict(fila)
    for rol in ("director", "actor"):
        datos[rol] = [r[0] for r in conn.execute(
            """SELECT pe.nombre FROM pelicula_personas pp JOIN personas pe ON pe.id = pp.persona_id
               WHERE pp.pelicula_id = ? AND pp.rol = ? ORDER BY pe.rowid""",
            (pelicula_id, rol),
        )]
    return datos


def guardar_progreso(conn, pelicula_id, progreso_ms):
    conn.execute("UPDATE peliculas SET progreso_ms = ? WHERE id = ?", (progreso_ms, pelicula_id))
    conn.commit()


def guardar_duracion(conn, pelicula_id, duracion_ms):
    conn.execute("UPDATE peliculas SET duracion_ms = ? WHERE id = ?", (duracion_ms, pelicula_id))
    conn.commit()


def marcar_vista(conn, pelicula_id, vista):
    conn.execute(
        "UPDATE peliculas SET watched = ?, watched_at = CASE WHEN ? THEN CURRENT_TIMESTAMP END WHERE id = ?",
        (1 if vista else 0, 1 if vista else 0, pelicula_id),
    )
    conn.commit()


def sin_ver(conn):
    return conn.execute("SELECT count(*) FROM peliculas WHERE estado = 'activa' AND NOT watched").fetchone()[0]


def marcar_todas_vistas(conn):
    """Marca como vistas todas las activas que no lo estaban; devuelve cuántas."""
    cur = conn.execute(
        "UPDATE peliculas SET watched = 1, watched_at = CURRENT_TIMESTAMP WHERE estado = 'activa' AND NOT watched"
    )
    conn.commit()
    return cur.rowcount
