#!/usr/bin/env bash
# Arma dist/Pelis-linux/ (listo para copiar a la raiz del disco) con PyInstaller.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null; then
    echo "Falta uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi
export UV_PROJECT_ENVIRONMENT=.venv-linux
uv run --locked python -m PyInstaller --noconfirm --clean --distpath build/dist --workpath build/work tools/pelis.spec

SALIDA="dist/Pelis-linux"
rm -rf "$SALIDA"
mkdir -p "$SALIDA/pelis-app/app"
cp -a build/dist/pelis "$SALIDA/pelis-app/app/linux"
cp tools/pelis.toml.ejemplo "$SALIDA/pelis-app/app/"
cp tools/pelis.sh "$SALIDA/"
chmod +x "$SALIDA/pelis.sh"
echo "Listo: $SALIDA"
