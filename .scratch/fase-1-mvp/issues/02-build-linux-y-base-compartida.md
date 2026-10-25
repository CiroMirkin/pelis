# Build de Linux y prueba de base compartida en Mint

Status: ready-for-human

Armar el build con `tools/build_linux.sh` y probar en Linux Mint con el disco NTFS, compartiendo la base con Windows. Anotar en `LINUX.md` los paquetes de sistema que hayan hecho falta (ej. `libxcb-cursor0`).

## Criterio de terminado
- [ ] `pelis.sh` abre el build de PyInstaller desde la raíz del disco
- [ ] Reproducir → pausar → cerrar → reabrir retoma en la misma posición, en Mint
- [ ] Una película marcada como vista en Windows aparece vista en Mint (rutas relativas)
- [ ] "Abrir carpeta" del detalle abre el explorador de archivos en Mint
