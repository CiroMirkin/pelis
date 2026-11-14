# nombres.separar_anio y un solo rango de año

Status: done

## Qué
- `nombres.separar_anio`, `ANIO_MIN`, `ANIO_MAX` y `anio_valido` (ver spec); `edicion.candidatos` y `guardar_manual` los usan
- Se borran `edicion.ANIO_FINAL`, `edicion.separar_anio` y los literales 1880 y 2100 de `edicion.py`

## Criterio de terminado
- [x] «Alien 1979» y «Alien (1979)» dan `("Alien", 1979)`; «Alien» da `("Alien", None)`
- [x] «Blade Runner 2049» sigue encontrando candidatos (el reintento sin año no cambia)
- [x] 1879 y 2101 son inválidos en el formulario y no se toman como año al final de la búsqueda; 1880 y 2100 sí
- [x] Los tests de `separar_anio` pasan a `test_nombres.py`
