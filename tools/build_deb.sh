#!/usr/bin/env bash
# Arma dist/Pelis-linux-vX.Y.Z.deb a partir de lo que dejó PyInstaller en build/dist/pelis (corré antes tools/build_linux.sh).
set -euo pipefail
cd "$(dirname "$0")/.."
VERSION=$(sed -nE 's/^__version__ = "(.*)"\r?$/\1/p' src/pelis/__init__.py)
# En Debian la ~ ordena antes de la final: 0.4.0~rc1 < 0.4.0 y apt deja pasar de la RC a la final
VERSION_DEB="${VERSION/-rc/~rc}"
# binutils solo hace falta para armar; el resto son las librerías que Qt necesita al correr
DEPENDE=$(grep -v "^#" tools/paquetes-linux.txt | grep -vx binutils | paste -sd, - | sed 's/,/, /g')

RAIZ="build/deb"
rm -rf "$RAIZ"
mkdir -p "$RAIZ/DEBIAN" "$RAIZ/opt" "$RAIZ/usr/bin" "$RAIZ/usr/share/applications" "$RAIZ/usr/share/icons/hicolor/256x256/apps"
cp -a build/dist/pelis "$RAIZ/opt/pelis"
ln -s /opt/pelis/pelis "$RAIZ/usr/bin/pelis"
cp src/pelis/icono.png "$RAIZ/usr/share/icons/hicolor/256x256/apps/pelis.png"
cat > "$RAIZ/usr/share/applications/pelis.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Pelis
Comment=Tu biblioteca de películas
Exec=pelis
Icon=pelis
Categories=AudioVideo;Video;Player;
Terminal=false
DESKTOP
cat > "$RAIZ/DEBIAN/control" <<CONTROL
Package: pelis
Version: $VERSION_DEB
Architecture: amd64
Maintainer: Pelis
Section: video
Priority: optional
Depends: $DEPENDE
Description: Biblioteca de películas
 Catálogo de películas locales con portadas, sinopsis y reproductor.
CONTROL

mkdir -p dist
SALIDA="dist/Pelis-linux-v$VERSION.deb"
dpkg-deb --root-owner-group -Zxz --build "$RAIZ" "$SALIDA"
echo "Listo: $SALIDA"
