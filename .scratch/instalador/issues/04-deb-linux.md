# Paquete .deb para Ubuntu y Debian

Status: done
Blocked by: 01

Ver "Linux" en la spec.

- Script en `tools/` que arma `Pelis-linux-vX.Y.Z.deb` con `dpkg-deb --build` a partir de `build/dist/pelis`
- Contenido: `/opt/pelis/`, enlace `/usr/bin/pelis`, `.desktop` en `/usr/share/applications/`, ícono en `/usr/share/icons/`
- `Depends:` sale de `tools/paquetes-linux.txt`, sin duplicar la lista
- Una RC se versiona con `~` (`0.4.0~rc1`)
- No incluye `pelis.toml`, así la app corre en modo instalado

## Criterio de terminado
- [x] `apt install ./pelis.deb` en un `ubuntu:24.04` limpio trae las dependencias y deja `pelis` funcionando (se prueba con `tools/ci_linux.sh`)
- [x] Aparece en el menú de aplicaciones con el ícono
- [x] `0.4.0~rc1` se puede actualizar a `0.4.0` con `apt`

## Comments

- 14/11/2026: `tools/build_deb.sh`. `tools/ci_linux.sh` ahora arma el `.deb` y lo instala en un `ubuntu:24.04` limpio, donde arranca. El usuario lo instaló en Mint y anda con sus datos. El orden `0.4.0~rc1 < 0.4.0` se comprobó con `dpkg --compare-versions`.
