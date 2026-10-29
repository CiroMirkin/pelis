#!/usr/bin/env bash
# Corre Pelis desde el código, con la carpeta app de desarrollo (dev/). uv instala lo que falte según uv.lock.
cd "$(dirname "$0")"
if ! command -v uv >/dev/null; then
    echo "Falta uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi
export UV_PROJECT_ENVIRONMENT=.venv-linux
exec uv run --locked python -m pelis --app-dir "$PWD/dev" "$@"
