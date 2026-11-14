# Un solo reconocedor de IMDb ID y de año

Status: done

Candidato 5 de `ignore/architecture-review-20261022-235128.html`. Decisiones tomadas el 2026-11-13.

## Problema
El IMDb ID es la clave que une las dos fuentes: OMDb trae los datos por ID y TMDb (`find`) trae la sinopsis en español por el mismo ID. Hoy hay cuatro reglas para reconocerlo y tres para el año, y aceptan cosas distintas:

| Lugar | IMDb ID |
|---|---|
| `nombres.py` (`RE_IMDB`, carpeta del escaneo) | `[tt\d+]` entre corchetes, cualquier cantidad de dígitos |
| `edicion.py` (`ID_IMDB`, `imdb_id_de`) | `tt\d{7,}` en cualquier parte (también un link) |
| `Editar.qml` (`buscar`) | la misma regex de `edicion.py`, copiada |
| `archivo_metadatos.py` (`leer`) | cualquier string que empiece con `tt` |

| Lugar | Año |
|---|---|
| `nombres.py` | `(1979)` en la carpeta, `19xx`/`20xx` suelto en el video |
| `edicion.py` (`ANIO_FINAL`) | número 1800 a 2099 al final del texto de búsqueda |
| `edicion.py` (`guardar_manual`) | formulario válido entre 1880 y 2100 |

Consecuencias: una carpeta `Alien [tt123]` se acepta y se manda a OMDb y TMDb, pero el mismo `tt123` en el editor no se reconoce; un `pelis.json` con `"imdb_id": "tt"` pasa la validación; el rango del año depende de dónde se escriba.

## Decisiones
- **`nombres.py` es la única fuente.** Interfaz pública nueva:
  - `imdb_id(texto) → str | None`: el primer `tt` seguido de 7 o más dígitos, sin importar mayúsculas, en minúsculas. Sirve para un ID suelto, entre corchetes o dentro de un link. Cualquier otra cosa devuelve `None`.
  - `separar_anio(texto) → (titulo, anio | None)`: el `edicion.separar_anio` de hoy, movido. El año final es un número de 4 cifras al final, solo o entre paréntesis, dentro del rango válido.
  - `ANIO_MIN = 1880`, `ANIO_MAX = 2100` y `anio_valido(n) → bool`: el único rango, usado por `separar_anio` y por el formulario de edición.
- **Carpeta del escaneo**: `parsear_carpeta` sigue exigiendo corchetes y los saca del título, pero devuelve el ID solo si `imdb_id` lo acepta. `[tt123]` se descarta y la película se busca por título.
- **`pelis.json`**: `archivo_metadatos.leer` considera inválido un `imdb_id` que no sea string o para el que `nombres.imdb_id` devuelva `None` (la misma `ArchivoInvalido` de hoy).
- **Editor**: `Puente` expone un slot `imdbIdDe(texto) → str` (`""` si no hay) y `Editar.qml` lo usa; se borra la regex del QML. `Puente.buscarEnImdb` usa `nombres.imdb_id`.
- Se borran de `edicion.py`: `ID_IMDB`, `ANIO_FINAL`, `imdb_id_de`, `separar_anio` y el rango fijo de `guardar_manual`.
- **Cambio de comportamiento aceptado**: un ID corto o inventado en el nombre de carpeta o en `pelis.json` deja de aceptarse. Los IDs reales de IMDb tienen 7 dígitos o más.

## Fuera de alcance
- El año del nombre del video (`19xx`/`20xx` suelto) y el de la carpeta entre paréntesis: son heurísticas de nombres de archivo, no un reconocedor de texto escrito por el usuario. Quedan en `nombres.py` como están.
- El reintento sin año de `edicion.candidatos` (audit-pendientes/05): ya está hecho y no cambia.
- Cambiar cómo OMDb o TMDb usan el ID.
