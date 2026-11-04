# Capturas de pantalla

Status: done

Anotada el 2026-10-26, acotada en un grilling (2026-10-29). El visor se sumó en otro grilling (2026-11-01).

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
- **Interacción**: click en una miniatura abre el visor en esa captura. Sin tooltip.
- **Foco de teclado**: `↓` desde Reproducir o «Marcar como vista» entra a la primera miniatura; desde «…» abre su menú. Dentro de la grilla, `←`/`→` pasan a la anterior/siguiente y `↑`/`↓` cambian de fila; `↑` desde la primera fila vuelve a los botones. `Enter` y `Espacio` abren el visor. El foco se marca como en los otros botones de la app y la página se desplaza para que la miniatura enfocada quede a la vista.
- **Refresco**: la carpeta se vuelve a mirar al mostrar el detalle, así que al volver del reproductor aparecen las nuevas sin re-escanear.

### Visor
- **Dónde**: página propia (`Visor.qml`) en el `StackView`, sobre el detalle. Ocupa la ventana tal como esté: no fuerza pantalla completa. `F` la alterna, como en el reproductor.
- **Imagen**: fondo negro, la captura ajustada a la ventana sin recortar (`PreserveAspectFit`). Sin zoom ni paneo.
- **Orden**: el mismo de la grilla (`capturas.listar`).
- **Navegación**: botones a los lados, `←`/`→` y arrastre. Sin rueda del mouse. Circular: después de la última viene la primera y antes de la primera, la última.
- **Arrastre**: la imagen sigue al mouse mientras se arrastra; al soltar pasado ~1/4 del ancho, o con un gesto rápido, pasa a la siguiente/anterior con animación; si no, vuelve a su lugar.
- **Barra de abajo**: el momento (`01:23:45`), la posición («3 de 12»), el botón «Ir a 01:23:45» y el botón de la grilla de tercios.
- **Controles que se ocultan**: los botones laterales y la barra de abajo desaparecen juntos tras unos segundos sin actividad y vuelven al mover el mouse o tocar una tecla, como en el reproductor.
- **Cerrar**: `Esc` o un botón volver arriba a la izquierda. Si está en pantalla completa, `Esc` primero la quita y un segundo `Esc` vuelve al detalle (igual que `Reproductor.qml`). Click en el fondo no cierra.
- **Foco al volver**: queda en la miniatura de la última captura vista, no en la que se abrió.

### Ir al momento
- **Botón «Ir a HH:MM:SS»**: solo en capturas cronológicas (nombre `HH-MM-SS.ext` o `HH-MM-SS(n).ext`); en las demás no aparece. Sin atajo de teclado.
- **Texto**: muestra el momento de la captura, no el del salto.
- **Posición**: el reproductor arranca en `max(0, momento − 5 s)`, acotado a la duración del video.
- **Pila**: el visor se *reemplaza* por el reproductor, así que `Esc` en el reproductor vuelve al detalle.
- **Progreso**: «Ir a» es una visita: no cambia el progreso guardado ni marca la película como vista, aunque llegue al final.

### Grilla de tercios
- **Toggle**: un botón en la barra de abajo la prende y la apaga. Sin atajo de teclado.
- **Dibujo**: 2 líneas verticales y 2 horizontales en los tercios, solo sobre el área visible de la imagen (no sobre las bandas negras), rojas al 80 % de opacidad, 1 px lógico de grosor.
- **Visibilidad**: sigue a la vista cuando se ocultan los controles.
- **Estado**: arranca apagada cada vez que se abre el visor y queda como está al pasar de captura.

## Fuera de alcance
- Borrar una captura desde la app.
- Zoom, rueda del mouse, click en el fondo para cerrar, `Enter` para «Ir a».
- JPG u otro formato al capturar.
