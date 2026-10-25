# Workflow de GitHub Actions que publica los builds

Status: ready-for-agent
Blocked by: 01

Ver "Workflow de publicación en GitHub" en la spec.

- Se dispara con un tag `vX.Y.Z`, que tiene que coincidir con la versión de `pyproject.toml`
- Dos jobs: `windows-latest` con `tools/build_win.bat`, `ubuntu-latest` con `tools/build_linux.sh` (instala `libxcb-cursor0` antes)
- Corre `pytest` en los dos sistemas antes de armar; si falla, no publica
- Sube `Pelis-windows-vX.Y.Z.zip` y `Pelis-linux-vX.Y.Z.zip` (lo que va en la raíz del disco) a una Release con ese tag

## Criterio de terminado
- [ ] Subir un tag publica una Release con los dos zips, con los tests pasando
