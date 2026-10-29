# Workflow de GitHub Actions que publica los builds

Status: ready-for-agent
Blocked by: 01, 05

Ver "Workflow de publicación en GitHub" en la spec.

- Se dispara con un tag `v*`, que tiene que coincidir con `__version__`, o a mano (`workflow_dispatch`, solo artifacts)
- Dos jobs: `windows-latest` con `tools/build_win.bat`, `ubuntu-24.04` con `tools/build_linux.sh` (instala `libxcb-cursor0` antes)
- Instala las dependencias con `uv` (`astral-sh/setup-uv`) desde `uv.lock`, con `--locked`: el build de GitHub usa las mismas versiones que el local
- Corre `pytest` en los dos sistemas antes de armar; si falla, no publica
- Sube `Pelis-windows-vX.Y.Z.zip`, `Pelis-linux-vX.Y.Z.tar.gz` y `SHA256SUMS` a una Release con ese tag
- Texto de la Release: el mensaje del tag anotado. Tags `-rcN` como pre-release

## Criterio de terminado
- [x] Subir un tag publica una Release con los dos paquetes y el `SHA256SUMS`, con los tests pasando
- [ ] Un tag que no coincide con `__version__` falla sin publicar
- [x] El disparo manual deja los paquetes como artifacts sin crear Release

## Comments

- 29/10/2026: `.github/workflows/publicar.yml`. El disparo manual pasó en los dos sistemas (run 40905304749 sobre `f89a1e3`): `Pelis-windows-v0.1.0` (58 MB) y `Pelis-linux-v0.1.0` (87 MB) como artifacts.
- El primer run falló: a `ubuntu-24.04` le faltaba `libpulse0`, y en Windows dos tests daban por hecho un disco que distingue mayúsculas. Los paquetes de Linux viven en `tools/paquetes-linux.txt`, que usan el workflow y `tools/ci_linux.sh`. Ese script corre el job de Linux en local, en un contenedor `ubuntu:24.04` limpio.
- Quedan sin probar el camino con tag (Release, `SHA256SUMS`, notas, pre-release) y el tag que no coincide. Se prueban con la primera RC (`/version minor --rc`).
- 29/10/2026: el tag `v0.3.0-rc1` publicó la pre-release con los dos paquetes, `SHA256SUMS` y las notas del tag (run 40920401654). Falta probar un tag que no coincide.
