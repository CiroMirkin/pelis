# Un solo módulo de Metadatos

Candidato 1 de `ignore/architecture-review-20261022-235128.html`, acotado en un grilling (2026-10-27). Regla base en `docs/adr/0001-pelis-json-copia-portatil.md`.

## Problema
Cinco caminos guardan metadatos y escriben `pelis.json` de formas distintas:
- Escaneo con OMDb (`escaneo._guardar`): `pelis.json` es el dict de OMDb crudo (`titulo: null`, año de OMDb) mientras la base queda con el título y el año de la carpeta.
- Importar desde `pelis.json`: `insertar_pelicula` pone el año de la carpeta y `COALESCE` lo conserva; un año corregido a mano se pierde con una base nueva, y una peli copiada a otra biblioteca llega con el año de la carpeta.
- Corregir match (`edicion.aplicar_omdb`), edición manual y fusión: reconstruyen `pelis.json` desde la base, rescatando `sinopsis_idioma` y `poster_url` del archivo anterior porque la base no los guarda.
- Un `OSError` al escribir el archivo sale después del `commit` sin aviso claro.

## Decisiones
- **`pelis.json` es la copia portátil de los metadatos** (ADR 0001): se lee solo si la base no tiene datos de la película; si no coinciden, gana la base y el archivo se corrige.
- **Qué viaja**: título, año, IMDb ID, sinopsis, `sinopsis_idioma`, país, género, director, elenco, `poster_url`, `metadatos_origen`. No viajan vista, progreso, duración ni papelera.
- **Columnas nuevas** en `peliculas`: `sinopsis_idioma` y `poster_url` (`ALTER TABLE ADD COLUMN`, nullables). El archivo es una proyección exacta de la base.
- **Columna `omdb_id` sin renombrar**: código y archivo usan `imdb_id`; el módulo traduce en un solo lugar.
- **`src/pelis/metadatos.py`**:
  - `obtener(datos_omdb, tmdb, idiomas)`: red (TMDb), sin base; la consulta a OMDb la hace quien llama (cascada del escaneo o `por_id` al corregir match). Mapeo de OMDb (hoy `metadatos_de_omdb`) + sinopsis de TMDb en el primer idioma disponible (hoy `_sinopsis_traducida` y `edicion.traer`). Devuelve metadatos y aviso.
  - `aplicar(conn, biblioteca, pelicula_id, metadatos, explicita)`: base, sin red. Guarda, hace `commit` y después escribe el archivo. Si escribir falla devuelve un aviso (la base queda guardada). Nunca pisa un archivo inválido.
  - `sincronizar(conn, biblioteca)`: recorre las películas con datos (`encontrada`, activas, carpeta presente), compara el archivo contra la base y reescribe solo lo que difiere. Saltea archivos inválidos y carpetas ausentes sin avisar por las ausentes. Devuelve avisos.
- **Regla de título y año** (`explicita`):
  - `True` (edición manual, corregir match, importar `pelis.json` completo): el dict es la verdad; título y año se guardan tal cual, también vacíos. Al corregir match, `edicion` arma el dict con el título actual y el año de OMDb (o el actual si OMDb no trae).
  - `False` (match automático del escaneo): ganan el título y el año de la carpeta; OMDb completa lo que falte.
- **Todos los caminos pasan por el módulo**: escaneo con OMDb, importar desde archivo, corregir match, edición manual y fusión. Nadie más escribe `pelis.json`.
- **Sincronización** al final de `Escaneo.ejecutar`: cubre el escaneo y el arranque (`importar_sin_red`). La primera pasada llena las columnas nuevas desde los archivos existentes que sean válidos y coincidan en IMDb ID.
- `archivo_metadatos.py` queda como el formato: leer, escribir atómico, versión, `es_completo`.
- El póster lo sigue bajando el escaneo en un paso propio; el módulo solo guarda `poster_url`.
- Puente muestra el aviso que devuelve `aplicar` en edición manual y corregir match.

## Se borra
`escaneo._guardar`, `escaneo._sinopsis_traducida`, `escaneo.metadatos_de_omdb`, `edicion.traer`, `edicion._escribir_archivo`, `edicion._archivo_actual`; `db.fijar_anio` deja de usarse fuera de `db`/`metadatos`.

## Fuera de alcance
- Reconocedor único de IMDb ID y año (candidato 5).
- Política del póster (candidato 3).
- Botón "releer pelis.json".
