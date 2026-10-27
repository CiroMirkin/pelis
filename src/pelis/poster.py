"""Política del póster: el set de cada película, cuál es el actual y la rotación (regla 4 de biblioteca-multimedia).

Es el único que escribe en la tabla `posters`. Orígenes: `existente` (una imagen de la carpeta) u `omdb`
(el bajado a `posters/poster.jpg`).
"""

import random
import re
from pathlib import Path

EXTENSIONES_POSTER = {".jpg", ".jpeg", ".png"}
# En orden de preferencia; la palabra puede estar en cualquier parte del nombre ("Alien-poster", "poster_2")
PALABRAS_POSTER = ["poster", "folder", "cover"]
DIAS_ROTACION = 7


def revisar(conn, biblioteca, pelicula_id):
    """Revisa la carpeta y cambia el poster si hace falta; devuelve True si cambió.

    Mientras el archivo del poster actual exista y siga siendo un poster, se respeta (puede venir de la
    rotación). Solo una imagen nueva (no registrada) desplaza al poster bajado de OMDb. Si el archivo
    actual se borró o ya no cuenta como poster (p. ej. un `backdrop.jpg` de la rotación vieja), se
    busca otro.
    """
    cambio = _revisar(conn, biblioteca, pelicula_id)
    conn.commit()
    return cambio


def _revisar(conn, biblioteca, pelicula_id):
    folder_path = conn.execute("SELECT folder_path FROM peliculas WHERE id = ?", (pelicula_id,)).fetchone()[0]
    if not (Path(biblioteca) / folder_path).is_dir():
        return False
    validos = _posters_de(biblioteca, folder_path)
    actual = _actual(conn, pelicula_id)
    bajados = _bajados(conn, pelicula_id)
    if actual and (Path(biblioteca) / actual["path"]).is_file() and actual["path"] in validos:
        if actual["origen"] != "omdb":
            return False
        registrados = _registrados(conn, pelicula_id)
        nuevo = next((r for r in validos if r not in registrados), None)
        if nuevo is None:
            return False
        _usar(conn, pelicula_id, nuevo, "existente")
        return True
    encontrado = next((r for r in validos if r not in bajados), None)
    if encontrado is not None:
        ruta, origen = encontrado, "existente"
    else:
        # Sin imágenes propias: se vuelve al de OMDb
        ruta = next((p for p in sorted(bajados) if (Path(biblioteca) / p).is_file()), None)
        if ruta is None:
            if actual is None:
                return False
            conn.execute("UPDATE peliculas SET poster_actual_id = NULL WHERE id = ?", (pelicula_id,))
            return True
        origen = "omdb"
    if actual and actual["path"] == ruta:
        return False
    _usar(conn, pelicula_id, ruta, origen)
    return True


def rotar(conn, biblioteca, ahora="now", azar=random, dias=DIAS_ROTACION):
    """Cambia el poster de las películas que llevan `dias` días con el mismo (0 = todas, a mano).

    El set son los posters de la película (`_posters_de`); se elige al azar uno distinto del actual. Las
    películas con un solo poster no cambian. Devuelve cuántas rotaron.
    """
    vencidas = conn.execute(
        """SELECT id, folder_path FROM peliculas WHERE estado = 'activa'
           AND (poster_actualizado_en IS NULL OR poster_actualizado_en <= datetime(?, ?))""",
        (ahora, f"-{dias} days"),
    ).fetchall()
    rotadas = 0
    for fila in vencidas:
        imagenes = sorted(_posters_de(biblioteca, fila["folder_path"]))
        if len(imagenes) < 2:
            continue
        bajados = _bajados(conn, fila["id"])
        # Registrarlas todas evita que revisar tome una como "nueva" y deshaga la rotación
        registrados = _registrados(conn, fila["id"])
        for ruta in imagenes:
            if ruta not in registrados:
                _insertar(conn, fila["id"], ruta, "omdb" if ruta in bajados else "existente")
        actual = _actual(conn, fila["id"])
        elegida = azar.choice([r for r in imagenes if not actual or r != actual["path"]])
        _usar(conn, fila["id"], elegida, "omdb" if elegida in bajados else "existente")
        rotadas += 1
    conn.commit()
    return rotadas


def _carpeta_posters(carpeta):
    """La subcarpeta `posters` de la película (sin importar mayúsculas), o dónde crearla si no está."""
    return next((d for d in carpeta.iterdir() if d.is_dir() and d.name.lower() == "posters"), carpeta / "posters")


def _imagenes(carpeta):
    return [p for p in carpeta.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONES_POSTER]


def _posters_de(biblioteca, folder_path):
    """Rutas (relativas a la biblioteca) de los posters de la película, en orden de preferencia.

    Primero toda imagen de `posters/`, sea cual sea su nombre; después las sueltas en la carpeta de la
    película según PALABRAS_POSTER. En cada grupo, primero la que se llama exactamente así
    ("poster.jpg") y después por nombre.
    """
    carpeta = Path(biblioteca) / folder_path
    if not carpeta.is_dir():
        return []
    sub = _carpeta_posters(carpeta)
    elegidas = sorted(_imagenes(sub), key=lambda p: (p.stem.lower() != "poster", p.name.lower())) if sub.is_dir() else []
    sueltas = _imagenes(carpeta)
    for palabra in PALABRAS_POSTER:
        candidatos = [p for p in sueltas if re.search(palabra, p.stem, re.IGNORECASE)]
        elegidas += sorted(candidatos, key=lambda p: (p.stem.lower() != palabra, p.name.lower()))
        sueltas = [p for p in sueltas if p not in candidatos]
    return [f"{folder_path}/{p.relative_to(carpeta).as_posix()}" for p in elegidas]


def _actual(conn, pelicula_id):
    """(path, origen) del poster actual, o None."""
    return conn.execute(
        """SELECT po.path, po.origen FROM peliculas p JOIN posters po ON po.id = p.poster_actual_id
           WHERE p.id = ?""",
        (pelicula_id,),
    ).fetchone()


def _registrados(conn, pelicula_id):
    return {r[0] for r in conn.execute("SELECT path FROM posters WHERE pelicula_id = ?", (pelicula_id,))}


def _bajados(conn, pelicula_id):
    return {r[0] for r in conn.execute(
        "SELECT path FROM posters WHERE pelicula_id = ? AND origen = 'omdb'", (pelicula_id,))}


def _insertar(conn, pelicula_id, path, origen):
    return conn.execute(
        "INSERT INTO posters (pelicula_id, path, origen) VALUES (?, ?, ?)", (pelicula_id, path, origen)).lastrowid


def _usar(conn, pelicula_id, path, origen):
    """Pone `path` como poster actual, reusando su fila si ya estaba registrado."""
    fila = conn.execute("SELECT id FROM posters WHERE pelicula_id = ? AND path = ?", (pelicula_id, path)).fetchone()
    poster_id = fila[0] if fila else _insertar(conn, pelicula_id, path, origen)
    conn.execute(
        "UPDATE peliculas SET poster_actual_id = ?, poster_actualizado_en = CURRENT_TIMESTAMP WHERE id = ?",
        (poster_id, pelicula_id),
    )
