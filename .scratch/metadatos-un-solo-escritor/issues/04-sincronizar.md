# metadatos.sincronizar al final de cada escaneo y al abrir la app

Status: done
Blocked by: 01, 03

## Qué
- `sincronizar(conn, biblioteca)` en `metadatos.py` (ver spec): compara cada película con datos contra su `pelis.json` y reescribe solo lo que difiere; saltea inválidos y carpetas ausentes
- Primera pasada: llena `sinopsis_idioma` y `poster_url` desde el archivo existente si es válido y coincide el IMDb ID
- `Escaneo.ejecutar` lo llama al final (cubre `escanear` e `importar_sin_red`); los avisos van al `Informe`

## Criterio de terminado
- [x] Repara un `pelis.json` viejo con `titulo: null` y crea uno que falta
- [x] Un archivo que ya coincide no se reescribe (mismo mtime)
- [x] No toca carpetas ausentes ni películas en la papelera
