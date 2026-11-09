# Build de Linux y prueba de base compartida en Mint

Status: ready-for-human

Armar el build con `tools/build_linux.sh` y probar en Linux Mint con el disco NTFS, compartiendo la base con Windows. Anotar en `LINUX.md` los paquetes de sistema que hayan hecho falta (ej. `libxcb-cursor0`).

## Criterio de terminado
- [ ] `pelis.sh` abre el build de PyInstaller desde la raíz del disco
- [x] Reproducir → pausar → cerrar → reabrir retoma en la misma posición, en Mint
- [x] Una película empezada en Mint se retoma en la misma posición en Windows (base compartida + rutas relativas)
- [ ] Una película marcada como vista en Windows aparece vista en Mint (rutas relativas)
- [ ] "Abrir carpeta" del detalle abre el explorador de archivos en Mint

## Comments

- 07/11/2026: los builds y la actualización funcionan. Falta probar la base compartida: que una película marcada como vista en Windows aparezca vista en Mint.
- 08/11/2026: retomar funciona en Mint, y una película empezada en Mint se retoma bien en Windows. Falta la prueba de «vista».
