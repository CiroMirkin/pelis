# Probar una versión como pre-release

Status: ready-for-agent
Blocked by: 04, 05

Para probar el actualizador de punta a punta en el disco propio antes de publicar la versión para todos.

- `tools/version.py ... --rc` publica `vX.Y.Z-rcN`; el workflow la marca como pre-release (issue 02)
- La app acepta `--prerelease` al arrancar: «Buscar actualización» mira todas las Releases (`/releases`) y toma la más nueva, RC incluidas
- Sin `--prerelease`, `releases/latest` ignora las RC, como hace GitHub

## Criterio de terminado
- [x] Una app con `--prerelease` encuentra e instala una RC
- [x] Una app sin `--prerelease` no la ve
- [ ] Una app en `-rcN` se actualiza a la final de esa versión

## Comments

- 29/10/2026: `--prerelease` en `__main__.py`, que lo pasa al puente; con esa opción `actualizacion.buscar` lee `/releases` y toma la más nueva sin borradores. El script de actualización relanza con los mismos argumentos, así que la opción se mantiene. `--rc` en `tools/version.py` y la pre-release del workflow ya estaban (issues 05 y 02). Falta la prueba real con `v0.2.0-rc1`.
- 29/10/2026: publicada `v0.3.0-rc1` (salió 0.3 porque un push fallido dejó `v0.2.0-rc1` local; ya corregido en `tools/version.py`). En Linux, `./pelis.sh --prerelease` la encontró y la instaló; `releases/latest` sigue en 404, así que sin la opción no se ve. Falta la final (`/version final`) para el último criterio.
