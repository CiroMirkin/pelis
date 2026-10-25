# Correr compat.py sobre toda la biblioteca en Windows y en Mint

Status: ready-for-human

`prototipo/compat.py` intenta abrir cada video con QtMultimedia y reporta si cargó, duración, pistas de audio y subtítulos, y el error si falló. Falta correrlo sobre la biblioteca completa en los dos sistemas (en Mint, desde el disco NTFS).

## Criterio de terminado
- [ ] Corrido en Windows sobre toda la biblioteca
- [ ] Corrido en Linux Mint sobre toda la biblioteca, desde el disco NTFS
- [ ] Si una parte relevante no se reproduce, evaluar libmpv antes de seguir; fallas aisladas se cubren con "Abrir con el reproductor del sistema"
