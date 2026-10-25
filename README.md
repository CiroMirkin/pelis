# Pelis

Catálogo y reproductor de escritorio para tu propia colección de películas. Sin servidor, sin cuentas: la biblioteca, la base y los metadatos viven en el disco.

![Python 3.12](https://img.shields.io/badge/python-3.12-3776ab?logo=python&logoColor=white)
![PySide6 / QML](https://img.shields.io/badge/UI-PySide6%20%2B%20QML-41cd52?logo=qt&logoColor=white)
![Windows | Linux Mint](https://img.shields.io/badge/plataforma-Windows%20%7C%20Linux%20Mint-555)

[Qué hace](#qué-hace) • [Cómo empezar](#cómo-empezar) • [Configuración](#configuración) • [La biblioteca](#la-biblioteca) • [Atajos](#atajos-de-teclado) • [Desarrollo](#desarrollo)

Pelis recorre una carpeta con una subcarpeta por película, busca los metadatos en OMDb (y la sinopsis en español en TMDb) y arma una grilla de posters. Desde ahí abrís el detalle y la mirás en el reproductor propio, que guarda dónde quedaste. Todo menos la búsqueda de metadatos y posters funciona sin internet.

Está pensada para un disco compartido (NTFS) que se monta tanto en Windows como en Linux Mint con una sola base, aunque también anda instalada en una sola PC.

## Qué hace

- **Catálogo** en grilla de posters con título y año; las que están a medias aparecen primero, con su barra de progreso, y las vistas al final. Filtros Todas / Sin ver / Vistas y por época (décadas y los últimos 4 años).
- **Marcar todas como vistas** desde «…» en el catálogo, con confirmación.
- **Recomendación del día**: al abrir, la app recomienda al azar una película que no viste ni empezaste.
- **Buscador** por título, director y reparto, sin distinguir mayúsculas ni acentos.
- **Detalle** con sinopsis, año, género, país, director y elenco. Reproducir, continuar, marcar como vista o abrir con el reproductor del sistema.
- **Personas**: en el detalle, un director o actor que está en otra película de la biblioteca se puede tocar y muestra todas sus películas.
- **Abrir carpeta**: desde «…» en el detalle, abre la carpeta de la película en el explorador.
- **Reproductor propio** sobre QtMultimedia: seek, pista de audio, subtítulos externos (`.srt`/`.ass`/`.vtt`, UTF-8 o Windows-1252) y embebidos, pantalla completa y controles que se ocultan solos. El tamaño y el color de los subtítulos externos se cambian desde el panel «Audio y subtítulos» y se recuerdan para todas las películas.
- **Elección automática** de audio y subtítulos según el idioma preferido.
- **Progreso guardado** al pausar, salir y cerrar; retoma exactamente donde quedó.
- **Hora de fin**: el detalle y el reproductor muestran a qué hora termina la película si la ves ahora.
- **Editar datos**: desde el detalle, traer los de IMDb buscando por título o pegando el ID o el link (corrige un match equivocado o completa una "no encontrada"), volver a traerlos, o cargarlos a mano. Lo editado queda en la base y en el `pelis.json`.
- **Faltantes**: una carpeta renombrada se reconoce sola por su IMDb ID y conserva progreso y vista. Si no tiene ID, desde «…» › «Faltantes» en el catálogo se le asigna su carpeta nueva a mano.
- **Rotación de posters**: cada 7 días, al abrir la app, las películas con más de una imagen en su carpeta cambian de poster al azar. Para sacar una imagen de la rotación, borrala de la carpeta.
- **Metadatos portables**: cada película guarda un `pelis.json` en su carpeta, así una base nueva se reconstruye sin volver a consultar OMDb.
- **Carpetas nuevas al abrir**: la app suma sola, sin internet, las películas que copiaste a la biblioteca desde la última vez.

## Cómo empezar

### Requisitos

- [Python 3.12](https://www.python.org/downloads/) (exactamente 3.12)
- Una clave de [OMDb](https://www.omdbapi.com/apikey.aspx) para los metadatos (opcional, sin ella no busca nada)
- Una clave de [TMDb](https://www.themoviedb.org/settings/api) para la sinopsis en español (opcional)

### Correr desde el código

```bash
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e .[dev]
```

Creá `dev/pelis.toml` a partir de [`tools/pelis.toml.ejemplo`](tools/pelis.toml.ejemplo) y apuntá `biblioteca` a tu carpeta de películas. Después:

```bash
dev.bat
```

`dev.bat` es un atajo para `python -m pelis --app-dir dev`. La carpeta que pasás en `--app-dir` es donde viven `pelis.toml`, la base `pelis.db` y `preferencias.ini`.

> [!TIP]
> Al abrir, la app suma sola las carpetas nuevas, sin consultar internet. Las que no traen `pelis.json` aparecen como pendientes de metadatos: usá **«…» › Escanear biblioteca** para buscarles los datos en OMDb y TMDb. El escaneo completo se dispara siempre a mano y muestra un informe al terminar.

### Armar el ejecutable de Windows

```bash
tools\build_win.bat
```

Genera `dist\Pelis-win\` con PyInstaller, listo para copiar a la raíz del disco:

```
D:\
├── Peliculas\          biblioteca, una carpeta por película
├── pelis-app\
│   └── app\
│       ├── win\        pelis.exe + _internal\
│       ├── pelis.db    se crea sola al primer arranque
│       └── pelis.toml  copiado de pelis.toml.ejemplo
└── Pelis.bat           lanzador
```

Qt y FFmpeg van dentro del build, no hace falta instalar nada más.

> [!NOTE]
> Para el set-up, el build y el lanzador de Linux (`app/linux/`, `pelis.sh`) ver [`LINUX.md`](LINUX.md).

## Configuración

`pelis.toml` vive en la carpeta app:

```toml
biblioteca       = "../../Peliculas"   # relativa a la carpeta de pelis.toml, o absoluta
omdb_api_key     = ""                  # vacío = no busca metadatos
tmdb_api_key     = ""                  # vacío = sinopsis de OMDb en inglés
idiomas_sinopsis = ["es-MX", "es-ES"]  # orden en que se prueban en TMDb
audio_preferido  = "es"
subs_preferido   = "es"
```

Con una ruta relativa, el mismo disco funciona con cualquier letra de unidad o punto de montaje. En la base, las rutas de las películas se guardan relativas a `biblioteca`.

## La biblioteca

Cada película es una subcarpeta directa de la biblioteca, con exactamente un video:

```
Peliculas\
└── Babel (2006)\
    ├── Babel 2006 (1080p x265 10bit Tigole).mkv
    ├── opensubtitles.srt
    ├── poster.jpg
    └── pelis.json
```

- **El nombre de la carpeta es el título** que se muestra, siempre. El año puede ir al final `Alien (1979)` o al principio `(1979) Alien`.
- **Poster**: una imagen (`.jpg`, `.jpeg`, `.png`) con la palabra `poster` en cualquier parte del nombre (`poster.jpg`, `Alien-poster.png`, `poster_2.jpg`); si no hay, una con `folder` y después una con `cover`. Si no hay ninguna, lo baja de OMDb como `poster.jpg`. Si después agregás una imagen a la carpeta, reemplaza a la de OMDb: aparece al abrir la ficha o la app.
- **Subtítulos externos**: sueltos al lado del video, nunca en subcarpetas. Se buscan al abrir el reproductor, así que no hace falta re-escanear.
- **Forzar el match**: si OMDb no la encuentra por título, creá un `pelis.json` con solo `{"imdb_id": "tt0078748"}` y volvé a escanear.
- **Copiar películas entre bibliotecas**: copiá la carpeta entera y abrí la app. Si trae su `pelis.json`, entra con todos los datos y el poster; si no, aparece con el título de la carpeta hasta el próximo escaneo. Lo visto y el progreso no viajan: viven en la base, no en el `pelis.json`.

> [!IMPORTANT]
> Una carpeta sin video o con más de uno no se importa y aparece en el informe del escaneo como "carpeta con problemas".

### Al abrir la app y al escanear

| | Al abrir la app | Escanear biblioteca |
|---|---|---|
| Carpetas nuevas con `pelis.json` completo | Se suman con sus datos | Se suman con sus datos |
| Carpetas nuevas sin `pelis.json` | Se suman como pendientes | Busca en OMDb y TMDb y escribe el `pelis.json` |
| Pendientes de metadatos | Siguen pendientes | Busca en OMDb y TMDb |
| Carpetas que ya no están | No se tocan | Se marcan faltantes y se ocultan |
| Faltantes que volvieron | Se reactivan | Se reactivan |
| Carpetas renombradas (mismo IMDb ID) | Toman el registro viejo | Toman el registro viejo |
| Usa internet | No | Sí |

## Atajos de teclado

| Dónde | Tecla | Acción |
|---|---|---|
| Catálogo | `Ctrl+F` o `/` | Ir al buscador |
| Catálogo | `Esc` | Limpiar la búsqueda |
| Detalle | `Esc` | Volver al catálogo |
| Editar datos | `Ctrl+S` | Guardar |
| Editar datos, Faltantes | `Esc` | Volver |
| Reproductor | `Espacio` | Play / pausa |
| Reproductor | `←` / `→` | −10 s / +10 s |
| Reproductor | `Ctrl+←` / `Ctrl+→` | −1 min / +1 min |
| Reproductor | `↑` / `↓` | Subir / bajar volumen |
| Reproductor | `M` | Silenciar |
| Reproductor | `F` o doble click | Pantalla completa |
| Reproductor | `Esc` | Salir de pantalla completa, o volver al detalle |

## Desarrollo

```
src/pelis/
├── __main__.py           arranque (python -m pelis)
├── config.py             pelis.toml y rutas
├── db.py                 SQLite, SQL a mano
├── escaneo.py            escaneo de la biblioteca, importación al abrir e informe
├── nombres.py            título, año e idioma desde nombres de carpetas y archivos
├── archivo_metadatos.py  lectura y escritura de pelis.json
├── omdb.py, tmdb.py      clientes de metadatos
├── subtitulos.py         lectura de subtítulos externos
├── puente.py             expone modelos y slots a QML
└── qml/                  interfaz (catálogo, detalle, reproductor)
```

Los módulos de lógica no importan Qt, así que se testean sin UI:

```bash
.venv\Scripts\python -m pytest
```

El plan completo, con las reglas de escaneo y las fases siguientes (filtros, edición de metadatos, papelera), está en [`.scratch/`](.scratch/biblioteca-multimedia/spec.md). Las decisiones de producto y de diseño visual están en [`PRODUCT.md`](PRODUCT.md) y [`DESIGN.md`](DESIGN.md).
