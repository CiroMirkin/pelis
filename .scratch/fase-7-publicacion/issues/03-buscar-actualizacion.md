# «Buscar actualización» en el menú del catálogo

Status: done
Blocked by: 01, 05

- Opción en el menú «…» del catálogo; nunca se busca sola al abrir
- Consulta `releases/latest` de `CiroMirkin/pelis` en un hilo aparte y compara el tag con `__version__` (semver con `-rcN`, una RC es menor que su final)
- Popup sobre el catálogo: «Estás al día (vX)» o «Hay una versión nueva: vY» con las notas de la Release, un botón «Actualizar» y el recordatorio de actualizar también desde el otro sistema
- Sin internet o con GitHub caído: mensaje claro, sin romper nada
- Corriendo desde el código (`dev.sh`, `dev.bat`), la opción aparece deshabilitada

## Criterio de terminado
- [x] Informa bien los tres casos: al día, versión nueva y sin conexión
- [x] Test de la comparación de versiones (con RC) y de la respuesta de la API sin UI

## Comments

- 29/10/2026: `actualizacion.py` (sin Qt), slot `buscarActualizacion` en el puente y `DialogoActualizacion.qml`. Probado con un arnés que simula el build: al día (contra la API real, que da 404 porque todavía no hay Releases), versión nueva con las notas en Markdown, y sin conexión.
- El botón «Actualizar» del popup lo suma el issue 04, junto con lo que hace.
- `OpcionMenu` ahora se ve tenue cuando está deshabilitada; también afecta a «Renovar portadas» durante un escaneo.
