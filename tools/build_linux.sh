#!/usr/bin/env bash
# Arma dist/Pelis-linux/ (listo para copiar a la raiz del disco) con PyInstaller.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=".venv-linux/bin/python"
if [ ! -x "$PY" ]; then
    echo "No existe .venv-linux. Crealo con:"
    echo "  python3.12 -m venv .venv-linux"
    echo "  .venv-linux/bin/python -m pip install -e .[dev]"
    exit 1
fi
"$PY" -m PyInstaller --noconfirm --clean --distpath build/dist --workpath build/work tools/pelis.spec

SALIDA="dist/Pelis-linux"
rm -rf "$SALIDA"
mkdir -p "$SALIDA/pelis-app/app"
cp -a build/dist/pelis "$SALIDA/pelis-app/app/linux"
cp tools/pelis.toml.ejemplo "$SALIDA/pelis-app/app/"
cp tools/pelis.sh "$SALIDA/"
chmod +x "$SALIDA/pelis.sh"
echo "Listo: $SALIDA"
