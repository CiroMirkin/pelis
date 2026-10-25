# Recorrer los criterios del MVP en la app con la biblioteca real

Status: ready-for-human

Lo que está implementado y con tests, pero falta ver en la app.

## Criterio de terminado
- [ ] "Escanear biblioteca" carga todo: cada carpeta queda importada (con metadatos o "no encontrada") o en el informe de problemas
- [ ] Grid con posters y detalle con todos los campos
- [ ] La barra de progreso del poster refleja el avance
- [ ] Un `.srt` real en Windows-1252 se ve con acentos y `ñ` correctos sin tocar nada
- [ ] La activación automática de audio y subtítulos elige lo esperado en una película con varias pistas
- [ ] Con una base nueva sobre la misma biblioteca, el escaneo importa todo desde los `pelis.json` sin consultar OMDb
- [ ] Las películas en progreso aparecen primero
- [ ] El buscador encuentra por título, director y reparto, ignorando mayúsculas y acentos
- [ ] El volumen se controla con el deslizador y con ↑/↓/M
