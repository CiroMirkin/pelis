#!/usr/bin/env bash
# Lanzador de Pelis para Linux. Va en la raiz del disco, junto a pelis-app/ y Peliculas/.
APP="$(cd "$(dirname "$0")" && pwd)/pelis-app/app"
# Una actualización que no llegó a arrancar deja el testigo: vuelve la versión anterior
if [ -e "$APP/actualizando-linux" ]; then
    if [ -d "$APP/linux.anterior" ]; then
        rm -rf "$APP/linux"
        mv "$APP/linux.anterior" "$APP/linux"
    fi
    rm -f "$APP/actualizando-linux"
fi
if [ ! -x "$APP/linux/pelis" ]; then
    echo "No se encuentra \"$APP/linux/pelis\"."
    exit 1
fi
if [ ! -f "$APP/pelis.toml" ]; then
    echo "Falta la configuracion \"$APP/pelis.toml\"."
    echo "Copia \"$APP/pelis.toml.ejemplo\" como pelis.toml y completa las claves."
    exit 1
fi
exec "$APP/linux/pelis" "$@"
