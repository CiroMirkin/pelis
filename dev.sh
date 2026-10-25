#!/usr/bin/env bash
# Corre Pelis desde el código, con la carpeta app de desarrollo (dev/).
cd "$(dirname "$0")"
if [ ! -x ".venv-linux/bin/python" ]; then
    echo "No existe .venv-linux. Crealo con:"
    echo "  python3.12 -m venv .venv-linux"
    echo "  .venv-linux/bin/python -m pip install -e .[dev]"
    exit 1
fi
PYTHONPATH="$PWD/src" exec .venv-linux/bin/python -m pelis --app-dir "$PWD/dev" "$@"
