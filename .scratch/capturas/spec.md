# Capturas de pantalla

Status: needs-triage

Futura feature, anotada el 2026-10-26. Sin acotar todavía.

## Idea
- En el reproductor, la tecla `.` toma una captura del frame actual de la película.
- La captura se guarda en una carpeta `screenshots/` junto al archivo de la película.
- El detalle de la película tiene una sección «Capturas» que muestra las capturas guardadas.

## Preguntas abiertas
- Nombre del archivo: ¿con la posición en la película (`01-23-45.png`)? Así quedan ordenadas y se sabe de qué momento son.
- Formato: PNG (sin pérdida) o JPG (más liviano).
- Si la captura incluye los subtítulos del overlay propio o solo el frame del video.
- Cómo tomar el frame: `VideoOutput.grabToImage` (lo que se ve, escalado a la ventana) o el `QVideoFrame` del `videoSink` (resolución original).
- Aviso visual al capturar (destello, toast).
- Películas que comparten carpeta: ¿una sola `screenshots/` mezclada o una subcarpeta por película?
- En el detalle: grilla de miniaturas, qué pasa al hacer click (verla grande, saltar a ese momento), si se pueden borrar desde la app.
- Que el escaneo ignore la carpeta `screenshots/`.
