# nombres.imdb_id como única regla del IMDb ID

Status: done

## Qué
- `nombres.imdb_id(texto)` (ver spec); `parsear_carpeta` devuelve el ID solo si es válido y saca igual los corchetes del título
- `archivo_metadatos.leer` valida con `nombres.imdb_id`
- `Puente.buscarEnImdb` usa `nombres.imdb_id`; se borran `edicion.ID_IMDB` y `edicion.imdb_id_de`
- Los tests de `test_edicion.py::test_imdb_id_de` pasan a `test_nombres.py`

## Criterio de terminado
- [x] `imdb_id` acepta `tt0078748`, `TT0078748`, un link de imdb.com y `[tt0078748]`; rechaza `tt`, `tt123`, `""` y `None`
- [x] Una carpeta `Alien [tt123]` no manda ningún ID al escaneo y queda `Alien` como título
- [x] Un `pelis.json` con `"imdb_id": "tt"` o `"tt123"` es `ArchivoInvalido`
- [x] `grep 'tt\\d'` en `src/` solo encuentra `nombres.py`
