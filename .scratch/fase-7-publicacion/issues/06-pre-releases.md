# Probar una versión como pre-release

Status: ready-for-agent
Blocked by: 04, 05

Para probar el actualizador de punta a punta en el disco propio antes de publicar la versión para todos.

- `tools/version.py ... --rc` publica `vX.Y.Z-rcN`; el workflow la marca como pre-release (issue 02)
- La app acepta `--prerelease` al arrancar: «Buscar actualización» mira todas las Releases (`/releases`) y toma la más nueva, RC incluidas
- Sin `--prerelease`, `releases/latest` ignora las RC, como hace GitHub

## Criterio de terminado
- [ ] Una app con `--prerelease` encuentra e instala una RC
- [ ] Una app sin `--prerelease` no la ve
- [ ] Una app en `-rcN` se actualiza a la final de esa versión
