# metadatos.obtener: mapeo de OMDb y sinopsis de TMDb en un lugar

Status: done
Blocked by: 01

## Qué
- `obtener` en `metadatos.py` (ver spec): mapeo de la respuesta de OMDb + sinopsis de TMDb en el primer idioma disponible; red, sin base
- El escaneo y `Puente` (corregir match) lo usan. Se borran `escaneo.metadatos_de_omdb`, `escaneo._sinopsis_traducida` y `edicion.traer`; la bajada del póster de corregir match queda en `edicion`

## Criterio de terminado
- [x] Tests existentes de escaneo y edición pasan
- [x] TMDb caído: sinopsis en inglés y un solo texto de aviso para escaneo y corregir match
