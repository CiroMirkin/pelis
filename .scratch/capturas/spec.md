# Capturas de pantalla

Status: done

Anotada el 2026-10-26, acotada en un grilling (2026-10-29).

## Idea
En el reproductor, la tecla `.` guarda una **Captura** del cuadro actual. El detalle de la película muestra las capturas guardadas en una sección «Capturas».

## Decisiones

### Tomar la captura (reproductor)
- **Tecla `.`**: funciona en pausa o reproduciendo, en ventana o pantalla completa. `autoRepeat: false`: una pulsación, una captura.
- **Fuente**: el `QVideoFrame` de `video.videoSink` (`videoFrame().toImage()`), en resolución original. No lleva subtítulos: los externos son el `Text` del overlay y los embebidos los dibuja `VideoOutput` aparte. Se lee un solo cuadro al apretar, no un sink intermedio (ver el comentario de `Reproductor.qml:167`).
- **Hilo**: el cuadro se toma en el hilo de la UI; la codificación PNG y la escritura van a un hilo aparte para no trabar la película.
- **Destino**: `capturas/` dentro de la carpeta de la película (se crea si falta). Cada película tiene su carpeta propia: el escaneo rechaza carpetas con más de un video.
- **Nombre**: la posición al apretar, truncada al segundo, con horas siempre en dos dígitos: `00-12-34.png`. Si ya existe: `00-12-34(2).png`, `(3)`, etc. Nunca se pisa una captura.
- **Formato**: PNG.
- **Aviso**: cuando el archivo ya está escrito, texto chico en la esquina superior derecha, color tenue, sin caja de fondo y con contorno negro fino. Dice solo «Captura» y se desvanece en ~1,5 s. No muestra los controles.
- **Errores** (todavía no hay cuadro, sin permisos, disco lleno): el mismo aviso dice «Captura fallida» en color de alerta; el motivo va al log.
- **Escaneo**: sin cambios. Solo mira archivos de primer nivel de cada carpeta (`escaneo.py:106`), así que ignora `capturas/`.

### Sección «Capturas» (detalle)
- **Lugar**: ancho completo, debajo de la fila de póster y columna.
- **Vacía**: si `capturas/` no existe o no tiene imágenes, la sección no aparece.
- **Archivos**: toda imagen `.png`, `.jpg`, `.jpeg`, `.webp` de `capturas/`, sin distinguir mayúsculas en la extensión.
- **Orden**: primero las cronológicas (nombre exactamente `HH-MM-SS.ext` o `HH-MM-SS(n).ext`), por posición y después por número de sufijo (sin sufijo = 1). Ojo: por nombre, `01-23-45(2).png` queda antes que `01-23-45.png`. Al final, las demás, alfabéticas sin distinguir mayúsculas.
- **Grilla**: miniaturas de ~160 px de ancho con la proporción original del cuadro, celdas de ancho fijo que se acomodan en filas. Se decodifican achicadas (`sourceSize`) y asíncronas.
- **Sin interacción**: sin click, tooltip ni foco de teclado.
- **Refresco**: la carpeta se vuelve a mirar al mostrar el detalle, así que al volver del reproductor aparecen las nuevas sin re-escanear.

## Fuera de alcance
- Ver una captura grande, saltar a su momento, borrarla desde la app.
- JPG u otro formato al capturar.
