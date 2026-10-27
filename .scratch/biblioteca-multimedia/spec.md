# Pelis

Plan general: objetivo, stack y decisiones transversales. El detalle de cada etapa está en `.scratch/fase-N-*/spec.md`, con sus tickets en `issues/`.

## Objetivo
App de escritorio portable para Windows y Linux Mint, sin servidor, que combina:
- Reproductor propio (controles propios sobre QtMultimedia)
- UI: estilo catálogo tipo Stremio (grid de posters, detalle de película)
- Metadatos: OMDb API, más la sinopsis en español de TMDb

La única conexión a internet es para consultar OMDb y TMDb y bajar posters. El catálogo y la reproducción funcionan sin red.

## Stack
- Lenguaje: Python 3.12 (la misma versión en Windows y en Linux Mint)
- UI: PySide6 con QML. La lógica en Python se expone a QML con modelos (`QAbstractListModel`) y slots.
- Reproductor: QtMultimedia (`MediaPlayer` + `VideoOutput`, backend FFmpeg incluido en los wheels de PySide6). Sin VLC.
  - Subtítulos externos dibujados por un overlay propio en QML y leídos con `pysubs2`. Los embebidos los dibuja el `VideoOutput` de Qt: tomarlos como texto obligaba a pasar cada frame por un sink intermedio, que lo copiaba a RAM y trababa la reproducción.
  - Que QtMultimedia reproduzca la biblioteca real es el mayor riesgo técnico; se valida en la fase 0. Plan B: libmpv.
- Base de datos: SQLite (`sqlite3` de la stdlib, SQL a mano, sin ORM), una sola base compartida por ambos sistemas
- Configuración: `tomllib` de la stdlib (solo lectura)
- Metadatos: OMDb API (`plot=full`) con `requests`, consulta única por película, cacheada en SQLite
- Sinopsis en español: TMDb (`/3/find/{imdb_id}`), buscando por el IMDb ID que dio OMDb, en el orden de `idiomas_sinopsis` (por defecto `es-MX` y después `es-ES`). Si no hay clave, TMDb no la tiene en ningún idioma o no responde, queda la de OMDb en inglés. Si TMDb falla, no se insiste en el resto del escaneo y el informe lo avisa.
- Dependencias: `PySide6`, `requests`, `pysubs2`; `pytest` solo para desarrollo

## Código fuente
```
pelis/
├── src/pelis/
│   ├── __main__.py   -- arranque (python -m pelis)
│   ├── config.py     -- pelis.toml + resolución de rutas
│   ├── db.py         -- esquema y consultas
│   ├── nombres.py    -- título, año, [tt…] (única implementación; la usa el escaneo)
│   ├── escaneo.py    -- reglas de escaneo + informe
│   ├── omdb.py       -- cliente OMDb
│   ├── subtitulos.py -- pistas, alias de idioma, elección automática
│   └── qml/          -- Catalogo.qml, Detalle.qml, Reproductor.qml
├── tests/
├── .scratch/        -- specs y tickets por fase
└── pyproject.toml
```
- Los módulos de lógica (`nombres`, `escaneo`, `subtitulos`, `db`, `omdb`) no importan Qt, para poder testearlos sin UI.

## Distribución
- Durante el desarrollo la app se corre desde el código (`python -m pelis`), con un venv por máquina fuera del disco compartido.
- Al cerrar el MVP se empaqueta con PyInstaller `--onedir`, un build por sistema (`app/win/`, `app/linux/`). Qt y el backend FFmpeg van dentro del build; no hay que instalar nada más en Windows. En Mint puede hacer falta algún paquete de sistema para Qt (ej. `libxcb-cursor0`); se confirma en la fase 0.

## Disco y portabilidad
La app soporta dos formas de instalación, con el mismo binario y la misma lógica:

- **Disco compartido** (uso actual): todo vive en un mismo disco **NTFS**, montado tanto en Windows como en Linux Mint (Mint lo monta con `ntfs-3g`, que viene instalado). Cada sistema corre su propio ejecutable (`app\win\` y `app/linux/`, con sus lanzadores `Pelis.bat` y `pelis.sh`) y los dos comparten los datos: `pelis.db`, `pelis.toml`, `preferencias.ini` y la biblioteca.
- **Local en una PC**: la carpeta `app\` y la biblioteca viven en los discos internos de una sola PC (NTFS, ext4, lo que sea). Puede ser la misma unidad o unidades distintas (ej. app en `C:\Pelis\app`, biblioteca en `E:\Peliculas`).

Lo que cambia entre las dos es solo el valor de `biblioteca` en `pelis.toml` (ver Configuración). El ejemplo de abajo es el de disco compartido.

```
D:\
├── Peliculas\              -- biblioteca (una carpeta por película)
├── Pelis\
│   └── app\                -- carpeta de distribución
│       ├── win\             -- build PyInstaller Windows (pelis.exe + _internal\)
│       ├── linux\           -- build PyInstaller Linux (pelis + _internal/)
│       ├── pelis.db         -- base SQLite compartida
│       └── pelis.toml       -- configuración
├── Pelis.bat               -- lanzador Windows: app\win\pelis.exe (usa %~dp0, relativo)
└── pelis.sh                -- lanzador Linux: app/linux/pelis (relativo a su propia ubicación)
```

- El código fuente puede vivir en cualquier lado; la app nunca lo lee.
- No se usan `.lnk` ni `.desktop` dentro del disco porque guardan rutas absolutas y se rompen si cambia la letra de unidad o el punto de montaje. Si querés un ícono, armás un acceso directo local en cada sistema que apunte al lanzador.
- **Rutas:** la raíz de la biblioteca sale de `pelis.toml`; las rutas de películas en SQLite son siempre relativas a esa raíz (`Alien (1979)/Alien.mp4`). Así la misma base funciona con `D:\` en Windows y `/media/<usuario>/<disco>/` en Mint, y también si la biblioteca se mueve a otra ubicación (solo cambia `pelis.toml`).
- La base y la configuración viven siempre en `app\`, un nivel arriba de los builds `win\`/`linux\`, en ambas formas de instalación. Corriendo desde el código, la carpeta `app` se indica con `python -m pelis --app-dir <ruta>`.
- Nunca se usan las dos instancias a la vez (un solo sistema operativo activo).
- Windows no distingue mayúsculas en los nombres de archivo y Linux sí, aun sobre el mismo NTFS. Por eso las rutas de la base se arman siempre con los nombres tal como los lista el disco, separadas con `/`, y nunca a partir de texto escrito a mano.
- Los dos builds del disco tienen que ser de la misma versión: se actualizan juntos (cada uno armado en su sistema) para que los dos lean la base y los `pelis.json` de la misma forma.

## Configuración (`pelis.toml`)
```toml
biblioteca      = "../../Peliculas"   # relativa a la carpeta de pelis.toml (app\), o absoluta
omdb_api_key    = "xxxxxxxx"
tmdb_api_key    = "xxxxxxxx"            # opcional: sinopsis en español
idiomas_sinopsis = ["es-MX", "es-ES"]   # orden de preferencia en TMDb
audio_preferido = "es"
subs_preferido  = "es"
```

- `biblioteca` acepta ruta **relativa a la carpeta de `pelis.toml`** (disco compartido: funciona con cualquier letra de unidad o punto de montaje) o **absoluta** (instalación local con la biblioteca en otra unidad, ej. `E:\Peliculas` o `/home/ciro/Peliculas`).

## Estructura de biblioteca en disco
Cada película vive en su propia carpeta directa de la raíz:

```
D:\Peliculas\
├── Alien (1979)\
│   ├── Alien.mp4
│   ├── Alien.srt
│   ├── posters\
│   │   ├── poster.jpg
│   │   └── criterion.png
│   └── pelis.json
```

- **Nombre de carpeta** = título que se muestra en el catálogo, siempre (nunca se reemplaza por el de OMDb). Puede incluir año `(1979)` al final o al principio. El IMDb ID para forzar el match va en `pelis.json`, no en el nombre (`[tt…]` en el nombre se sigue aceptando por compatibilidad, pero no se usa).
- **Metadatos:** `pelis.json` (ver abajo).
- **Video:** exactamente uno por carpeta. El nombre del archivo es libre (nombres de release tipo `Alien.Romulus.2024.1080p...` están bien).
- **Posters:** toda imagen dentro de la subcarpeta `posters\` (con cualquier nombre), más las imágenes sueltas con nombre reconocido (ver reglas de escaneo). Cualquier otra imagen suelta (`backdrop`, `landscape`, `logo`, etc.) se ignora y nunca se muestra como poster.
- **Subtítulos externos:** `.srt`/`.ass`/`.vtt` sueltos en la carpeta, al mismo nivel que el video. Los que estén en subcarpetas (`Subs\`, etc.) no se usan. Se buscan al abrir el reproductor, no en el escaneo, así que un subtítulo agregado después aparece sin re-escanear.

## Archivo de metadatos `pelis.json`
Cada carpeta de película guarda sus metadatos en `pelis.json`, para que viajen con la película y una base nueva o perdida se pueda reconstruir sin consultar OMDb ni perder ediciones manuales.

```json
{
  "version": 1,
  "imdb_id": "tt0078748",
  "year": 1979,
  "sinopsis": "…",
  "sinopsis_idioma": "es-MX",
  "pais": "UK, USA",
  "genero": "Horror, Sci-Fi",
  "director": ["Ridley Scott"],
  "elenco": ["Sigourney Weaver", "Tom Skerritt"],
  "poster_url": "https://…",
  "metadatos_origen": "omdb"
}
```

- **Escritura:** se mantiene actualizado. Se reescribe (de forma atómica) cada vez que la película obtiene o cambia sus metadatos: match con OMDb en el escaneo y, desde la fase 3, edición manual, corregir match y resincronizar. No se escribe para películas no encontradas o pendientes.
- **Lectura:** solo durante el escaneo (o la importación al abrir la app), cuando la carpeta no está en la base (o está pendiente de metadatos). En cualquier otro momento la base es la única fuente de verdad.
- **Completo vs. mínimo:** un archivo con `metadatos_origen` está completo y se importa sin consultar OMDb. Uno sin ese campo, por ejemplo escrito a mano como `{"imdb_id": "tt32275943"}`, solo fuerza el match: se consulta OMDb por ese ID y después el archivo se completa.
- **Inválido** (JSON roto, versión más nueva, `imdb_id` mal formado): se ignora, se reporta en el informe del escaneo y no se sobrescribe, para no perder lo que haya escrito a mano.
- No guarda visto, `watched_at` ni progreso: cambian seguido y esos datos viven solo en la base.
- El título no se guarda: siempre sale del nombre de la carpeta.

## Reglas de escaneo
1. El escaneo completo se dispara manualmente con "Escanear biblioteca". Al abrir la app corre una importación sin red: suma las carpetas nuevas (con los datos de `pelis.json` si está completo, si no quedan pendientes de metadatos) y reactiva faltantes, pero no consulta OMDb/TMDb ni marca faltantes.
2. Cada subcarpeta directa de la raíz es una película. Las subcarpetas internas (ej. `Subs\`) se ignoran.
3. **Video:** extensiones `.mkv`, `.mp4`, `.avi`, `.m4v`, `.mov`, `.wmv`, `.ts`, `.webm`. Todo lo demás se ignora (`Thumbs.db`, `.goutputstream-*`, `.srt.txt`, …). Si la carpeta tiene 0 o más de 1 video, **no se importa** y aparece en el informe "carpetas con problemas" al final del escaneo, con el motivo.
4. **Poster:** el set de posters de la película es la unión de:
   - toda imagen (`.jpg`/`.jpeg`/`.png`, cualquier nombre) directamente dentro de la subcarpeta `posters` (ese nombre exacto, sin importar mayúsculas; sus subcarpetas no se miran);
   - las imágenes sueltas en la carpeta de la película cuyo nombre contenga `poster`, `folder` o `cover`, en cualquier parte y sin importar mayúsculas (`poster.jpg`, `Alien-poster.png`, `folder.jpg`). Así los posters sueltos de antes de la carpeta siguen andando sin mover archivos.

   Para elegir uno, primero va `posters\` y después las sueltas (`poster`, luego `folder`, luego `cover`); en cada grupo gana la que se llama exactamente así y después el orden alfabético. La elegida se importa con `origen = 'existente'`. Si no hay ninguno, se descarga de OMDb y se guarda como `posters\poster.jpg` (creando la carpeta). La carpeta se vuelve a mirar en cada escaneo, en la importación al abrir y al abrir el detalle de la película: una imagen agregada a mano reemplaza a la bajada de OMDb, y si se borra el archivo del poster actual, o ya no entra en el set (p. ej. un `backdrop.jpg` que había dejado la rotación vieja), se busca otro (o se vuelve al de OMDb, o la película queda sin poster).
5. **Match con OMDb**, en orden, hasta que uno funcione:
   0. Si `pelis.json` está completo, se importa de ahí y no se consulta OMDb
   1. `imdb_id` de `pelis.json` (o `[tt…]` en el nombre de carpeta, por compatibilidad)
   2. Título + año de la carpeta (`Título (año)` o `(año) Título`)
   3. Título + año sacados del nombre del archivo de video (texto antes del año, con `.` y `_` reemplazados por espacios)
   4. Solo el título de la carpeta
   5. Si ninguno funciona, la película se agrega igual como "no encontrada": título de la carpeta, resto de los campos vacíos
6. Solo se procesan carpetas nuevas (comparando `folder_path`); las existentes no se tocan. Metadatos se consultan una sola vez; re-sincronizar es manual (fase 3).
7. **Carpetas faltantes:** si un registro activo apunta a una carpeta que ya no existe, pasa a `estado = 'faltante'` y se oculta del catálogo, sin borrarlo. La reasignación es de la fase 3.
8. Si una consulta a OMDb falla por red, la película queda con `omdb_estado = 'pendiente'` y el próximo escaneo la reintenta.

## Esquema SQLite

```sql
CREATE TABLE peliculas (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo            TEXT NOT NULL,              -- nombre de la carpeta, sin año ni [tt]
    year              INTEGER,
    folder_path       TEXT NOT NULL UNIQUE,       -- relativa a la raíz de la biblioteca
    video_path        TEXT NOT NULL,              -- relativa a la raíz de la biblioteca
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
    omdb_estado       TEXT DEFAULT 'pendiente',   -- 'encontrada' | 'no_encontrada' | 'pendiente'
    fecha_agregada    DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado            TEXT DEFAULT 'activa',      -- 'activa' | 'faltante' | 'papelera'
    fecha_papelera    DATETIME,
    metadatos_origen  TEXT DEFAULT 'omdb'         -- 'omdb' | 'manual'
);

CREATE TABLE posters (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pelicula_id     INTEGER NOT NULL REFERENCES peliculas(id),
    path            TEXT NOT NULL,                -- relativa a la raíz de la biblioteca
    origen          TEXT NOT NULL,                -- 'omdb' | 'existente'
    fecha_agregado  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE personas (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE
);

CREATE TABLE pelicula_personas (
    pelicula_id  INTEGER NOT NULL REFERENCES peliculas(id),
    persona_id   INTEGER NOT NULL REFERENCES personas(id),
    rol          TEXT NOT NULL,   -- 'actor' | 'director'
    PRIMARY KEY (pelicula_id, persona_id, rol)
);
```

## Fases

| Fase | Archivo | Contenido |
|---|---|---|
| 0 | [fase-0-preparacion](../fase-0-preparacion/spec.md) | Limpieza de la biblioteca (script de sugerencias + checklist manual) y prototipo del reproductor en QML + QtMultimedia |
| 1 | [fase-1-mvp](../fase-1-mvp/spec.md) | **MVP:** escaneo, OMDb, catálogo, detalle, reproducción con audio/subtítulos, progreso, vista/no vista |
| 2 | [fase-2-navegar](../fase-2-navegar/spec.md) | Filtros, personas clickeables, banderas, abrir ubicación, recomendación aleatoria |
| 3 | [fase-3-editar](../fase-3-editar/spec.md) | Edición manual de metadatos, corregir match, resincronizar, reasignar faltantes |
| 4 | [fase-4-reproductor](../fase-4-reproductor/spec.md) | Estilo/sincronización/codificación manual de subtítulos, hora estimada de fin |
| 5 | [fase-5-posters](../fase-5-posters/spec.md) | Galería de posters, sumar poster, rotación cada 7 días |
| 6 | [fase-6-papelera](../fase-6-papelera/spec.md) | Eliminar película con papelera de 7 días (tests primero) |
| 7 | [fase-7-publicacion](../fase-7-publicacion/spec.md) | Workflow de GitHub que publica los builds de Windows y Linux; buscar actualización y actualizar desde la app, solo al presionar un botón |

**Regla de reordenamiento:** si después del primer escaneo real más del 20% de las películas queda como "no encontrada", la fase 3 pasa adelante de la fase 2.

## Ideas futuras (no implementar todavía)

### Wizard de configuración
- Asistente al primer arranque para elegir la carpeta de la biblioteca, cargar la API key de OMDb y los idiomas preferidos, y escribir `pelis.toml`.

### Detección de idioma de subtítulos por contenido
- Para `.srt` sin idioma en el nombre, detectar el idioma leyendo el texto.

### Vista calendario de películas vistas
- Calendario tipo heatmap: cada día coloreado según cuántas películas se marcaron como vistas ese día
- Se calcula agrupando por `DATE(watched_at)`, sin campo nuevo en SQLite
- Click en un día muestra el listado de películas vistas ese día

### Migración a Raspberry Pi con acceso remoto
- Mover la app de "escritorio local" a un servidor corriendo en una Raspberry Pi, accesible por internet
- Implica repensar la arquitectura: de app de escritorio (PySide6 + QtMultimedia) a modelo cliente/servidor (servidor en la Pi + cliente web o app liviana que consume la API), similar al modelo de Plex
- Requiere autenticación, ya que deja de ser una app aislada en la propia máquina
- El disco con las películas tendría que estar conectado físicamente a la Pi o accesible por red desde ella
- Pendiente de definir: cómo se sirve el video (transcodificación o streaming directo) y el mecanismo de autenticación
