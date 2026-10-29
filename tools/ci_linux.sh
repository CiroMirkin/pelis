#!/usr/bin/env bash
# Corre el job de Linux de .github/workflows/publicar.yml en un contenedor ubuntu:24.04 limpio:
# tests, build y arranque del binario. Usa el uv de esta máquina, montado en el contenedor.
# Prueba el árbol de trabajo tal como está, con los cambios sin commitear y sin lo ignorado.
set -euo pipefail
cd "$(dirname "$0")/.."
UV="$(command -v uv)" || { echo "Falta uv"; exit 1; }
exec docker run --rm -v "$PWD":/src:ro -v "$UV":/usr/local/bin/uv:ro ubuntu:24.04 bash -c '
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive UV_PROJECT_ENVIRONMENT=.venv-linux QT_QPA_PLATFORM=offscreen
apt-get update -qq
apt-get install -y -qq git ca-certificates $(grep -v "^#" /src/tools/paquetes-linux.txt) >/dev/null
git config --global --add safe.directory "*"
mkdir /w && (cd /src && git ls-files -co --exclude-standard -z | tar --null -T - -c) | tar -x -C /w && cd /w
echo "== Tests"
uv run --locked pytest -q
echo "== Build"
tools/build_linux.sh >/tmp/build.log 2>&1 || { tail -30 /tmp/build.log; exit 1; }
echo "== Librerías que el build no trae y el sistema no tiene"
find dist/Pelis-linux -name "*.so*" -o -name pelis -type f | xargs -r ldd 2>/dev/null | grep "not found" | sort -u || true
echo "== Arranque"
mkdir -p /tmp/app /tmp/Peliculas
echo "biblioteca = \"/tmp/Peliculas\"" > /tmp/app/pelis.toml
set +e
timeout 10 dist/Pelis-linux/pelis-app/app/linux/pelis --app-dir /tmp/app
codigo=$?
set -e
if [ "$codigo" = 124 ]; then echo "Arrancó y siguió abierta 10 s: OK"; else echo "Salió con $codigo"; exit 1; fi
'
