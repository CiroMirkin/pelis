# Fase 0 — Preparación

Dos trabajos independientes que van antes de escribir la app: dejar la biblioteca en un estado que el escaneo pueda procesar, y probar que QtMultimedia (PySide6 + QML) reproduce la biblioteca real con subtítulos en ambos sistemas.

## A. Limpieza de la biblioteca

### A1. Renombrar la raíz (a mano)
- `D:\PELIS` → `D:\Peliculas`. Windows no distingue mayúsculas, así que `PELIS` choca con la carpeta de la app `Pelis`.

### A2. Checklist manual
- [ ] `Kill Bill`: separar en `Kill Bill Vol. 1 (2003)` y `Kill Bill Vol. 2 (2004)`, cada una con su video, subtítulo y poster
- [ ] `Midnight in Paris (2011)`: tiene un `.avi` y un `.mp4`; borrar el duplicado
- [ ] `Punch-Drunk Love (2002)`: `.goutputstream-X9MKJ3` es una copia interrumpida; verificar que el `.mp4` se reproduzca completo y borrar el temporal
- [ ] `The Legend of Hei 2 (2025)`: falta el video
- [ ] `Gatillero (2025)`: no se encontró IMDb ID; si OMDb no la encuentra, buscarla en IMDb como *Gunman* y crear su `pelis.json` con el `imdb_id`

## B. Prototipo del reproductor
Código descartable. Su único objetivo es responder si QtMultimedia (dentro de QML, con PySide6) reproduce la biblioteca real con los controles y subtítulos que necesita el MVP.

### Preparación
- Python 3.12 en Windows y en Linux Mint, con un venv por máquina fuera del disco compartido
- `pip install PySide6 pysubs2`
- En Mint, anotar qué paquetes de sistema hicieron falta para que Qt arranque (ej. `libxcb-cursor0`)

### Prototipo
- Una ventana QML con `MediaPlayer` + `VideoOutput` y una barra de controles superpuesta
- Overlay propio de subtítulos (`Text` sobre el video) alimentado por:
  - un `.srt` externo leído con `pysubs2` (UTF-8 y, si falla, cp1252)
  - el texto de los subtítulos embebidos tomado del `videoSink` (`subtitleText`), con el render propio de Qt desactivado

### Script de compatibilidad
- Recorre todos los videos de la biblioteca, intenta abrir cada uno con QtMultimedia y reporta: si cargó, duración, si tiene video, cantidad de pistas de audio y de subtítulos con su idioma/título, y el error si falló.
- Se corre en Windows y en Mint.

### Estado
- Prototipo en `prototipo/` (`main.py`, `Reproductor.qml`, `compat.py`). Python 3.12.10, PySide6 6.12.0 (FFmpeg 9.0.1 incluido), pysubs2 1.9.0.
- **Windows: validado** con `Alpha (2025)` (`.mkv`, 2 audios, 5 subs embebidos) y `Red Desert (1964)` (`.mp4`): audio, cambio de pista, `.srt` externo, embebidos por el overlay sin duplicarse, controles y pantalla completa.
- Hallazgo: QtMultimedia vuelve a emitir `LoadedMedia` al cambiar de pista; la elección automática tiene que correr una sola vez.
- **Pendiente:** `.srt` en Windows-1252 con un archivo real, Linux Mint desde el disco, y `compat.py` sobre la biblioteca completa.

### Criterio de terminado
- [ ] Una ventana QML reproduce un `.mkv` real del disco compartido en Windows y en Linux Mint
- [ ] Play, pausa, seek y pantalla completa funcionan, y los controles se ven y se pueden usar sobre el video
- [ ] Se puede leer posición y duración, y cambiar la pista de audio
- [ ] Un `.srt` externo se ve en el overlay, sincronizado, con acentos y `ñ` correctos (probar uno en UTF-8 y uno en Windows-1252)
- [ ] Un subtítulo embebido se ve en el mismo overlay, con el mismo estilo
- [ ] Se puede leer el idioma o el título de las pistas de audio y de subtítulos embebidas
- [ ] El script de compatibilidad corre sobre toda la biblioteca en ambos sistemas

### Si algo falla
Si el script muestra que una parte relevante de la biblioteca no se reproduce, o los subtítulos embebidos no se pueden leer como texto, antes de pasar a la fase 1 se evalúa libmpv como motor. Fallas aisladas no bloquean: para eso está el botón "Abrir con el reproductor del sistema" del MVP.
