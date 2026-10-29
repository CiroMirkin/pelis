# Workflow de GitHub Actions que publica los builds

Status: ready-for-agent
Blocked by: 01, 05

Ver "Workflow de publicación en GitHub" en la spec.

- Se dispara con un tag `v*`, que tiene que coincidir con `__version__`, o a mano (`workflow_dispatch`, solo artifacts)
- Dos jobs: `windows-latest` con `tools/build_win.bat`, `ubuntu-24.04` con `tools/build_linux.sh` (instala `libxcb-cursor0` antes)
- Corre `pytest` en los dos sistemas antes de armar; si falla, no publica
- Sube `Pelis-windows-vX.Y.Z.zip`, `Pelis-linux-vX.Y.Z.tar.gz` y `SHA256SUMS` a una Release con ese tag
- Texto de la Release: el mensaje del tag anotado. Tags `-rcN` como pre-release

## Criterio de terminado
- [ ] Subir un tag publica una Release con los dos paquetes y el `SHA256SUMS`, con los tests pasando
- [ ] Un tag que no coincide con `__version__` falla sin publicar
- [ ] El disparo manual deja los paquetes como artifacts sin crear Release
