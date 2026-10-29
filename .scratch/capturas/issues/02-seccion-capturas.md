# Sección «Capturas» en el detalle

Status: ready-for-agent
Blocked by: 01

## Qué
- `capturas.listar(carpeta_pelicula) → list[Path]`: imágenes `.png/.jpg/.jpeg/.webp` (sin distinguir mayúsculas) de `capturas/`, en el orden de la spec: primero las cronológicas por posición y sufijo (sin sufijo = 1), después el resto alfabético sin distinguir mayúsculas
- `Puente.pelicula` devuelve `capturas`: lista de URLs (`[]` si no hay carpeta)
- `Detalle.qml`: sección «Capturas» a ancho completo debajo de la fila póster/columna, oculta si la lista está vacía; grilla de miniaturas de ~160 px de ancho con la proporción original, `sourceSize` y `asynchronous`, sin interacción
- Tests de `listar` en `tests/test_capturas.py`

## Criterio de terminado
- [ ] `01-23-45.png` va antes que `01-23-45(2).png`; `foto.jpg` va después de todas las cronológicas
- [ ] Sin capturas, la sección no aparece
- [ ] Al volver del reproductor con capturas nuevas, se ven sin re-escanear
- [ ] Abrir el detalle con 20 PNG 4K no traba la UI
- [ ] La suite pasa
