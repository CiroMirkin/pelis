# Visor de capturas

Status: done
Blocked by: 02

Pedido el 2026-10-29, acotado en un grilling (2026-11-01). Decisiones en la spec: secciones «Sección Capturas» (interacción y foco), «Visor», «Ir al momento» y «Grilla de tercios».

## Qué
- `Detalle.qml`: las miniaturas abren el visor con click, y con `Enter`/`Espacio` cuando tienen foco. Foco de teclado en la grilla (entrar con `↓` desde los botones, flechas dentro, `↑` desde la primera fila para salir), con desplazamiento para que la enfocada se vea. Al volver del visor, el foco queda en la última captura vista.
- `Visor.qml` nuevo: recibe la lista de capturas, el índice inicial y el `peliculaId`. Muestra la imagen ajustada sobre fondo negro, con botones laterales, `←`/`→`, arrastre con animación y navegación circular. La barra de abajo lleva el momento, «n de N», «Ir a HH:MM:SS» y el toggle de la grilla de tercios. Los controles se ocultan tras unos segundos sin actividad. `F` alterna la pantalla completa; `Esc` la quita primero y después vuelve al detalle.
- El momento de cada captura sale del nombre (`capturas.CRONOLOGICA`). `Puente.pelicula` puede devolver, junto a cada URL, el momento en ms (o `null` si no es cronológica), así QML no tiene que parsear nombres.
- `Reproductor.qml`: una propiedad opcional con la posición de arranque (ms) que, si viene, reemplaza a `info.progreso` en el seek inicial. «Ir a» hace `replace` del visor por el reproductor con `max(0, momento − 5000)`, acotado a la duración.
- Tests: que el momento se extraiga del nombre (con y sin sufijo `(n)`, y `null` en las no cronológicas).

## Criterio de terminado
- [x] Click en una miniatura abre el visor en esa captura; con teclado se llega a la grilla y `Enter`/`Espacio` la abre
- [x] `←`/`→`, los botones y el arrastre pasan de captura; de la última se va a la primera y viceversa
- [x] Un arrastre corto vuelve la imagen a su lugar
- [x] Los controles se ocultan solos y vuelven al mover el mouse o tocar una tecla
- [x] «Ir a 01:23:45» abre el reproductor en 01:23:40; `Esc` ahí vuelve al detalle, no al visor
- [x] Una captura sin nombre `HH-MM-SS` no muestra «Ir a»
- [ ] La grilla de tercios aparece solo sobre la imagen, roja al 80 %, sigue visible al ocultar los controles, se mantiene al pasar de captura y arranca apagada al reabrir
- [x] `Esc` en pantalla completa la quita; el segundo `Esc` vuelve al detalle con el foco en la última captura vista
- [x] La suite pasa

## Comments

2026-11-01: implementado. `capturas.momento_ms` saca la posición del nombre con `CRONOLOGICA` (tests: con y sin sufijo `(n)`, 100 h o más, `None` en las no cronológicas). `Puente.pelicula` devuelve cada captura como `{url, momento}`. `Visor.qml` nuevo (registrado en `qmldir`), íconos `anterior`, `siguiente` y `tercios`; `Boton` pinta `checked` como apretado para el toggle de la grilla. `Reproductor.qml` tiene `inicio` (ms, -1 = usar el progreso), acotado a la duración en la carga inicial. 208 tests pasan. qmllint: `Visor.qml` sin avisos; en `Detalle.qml` solo suman avisos `unqualified` del mismo tipo que los que ya había (delegates que usan ids de afuera).

Smoke test offscreen (`QT_QPA_PLATFORM=offscreen`, biblioteca de prueba con un video de 20 s hecho con ffmpeg y tres capturas: `00-00-03.png`, `00-00-12.png`, `foto.png`), con eventos de teclado y mouse simulados, sin avisos de QML:
- `↓` desde Reproducir entra a la primera miniatura, `→` pasa, `↑` desde la primera fila vuelve a Reproducir; `Enter`, `Espacio` y click abren el visor en esa captura.
- `←`/`→`, el botón Siguiente y el arrastre pasan de captura, circular en los dos sentidos; arrastre de 100 px lento vuelve a su lugar, 500 px pasa, gesto rápido de 120 px pasa.
- La captura no cronológica no tiene momento (oculta el momento e «Ir a»).
- Controles ocultos a los 3 s con el mouse fuera de las barras; vuelven con una tecla y al mover el mouse.
- La grilla de tercios se prende con el botón, sigue al pasar de captura y con los controles ocultos, y arranca apagada al reabrir.
- `F` pone pantalla completa, `Esc` la quita, el segundo `Esc` vuelve al detalle con el foco en la última captura vista.
- «Ir a 00:00:12» reemplaza el visor por el reproductor con `inicio` 7000 y el video arranca ahí; `Esc` en el reproductor vuelve al detalle.

Queda para probar a mano abriendo la app:
- Cómo se ve la grilla de tercios: que quede solo sobre la imagen (no sobre las bandas negras), roja al 80 % y de 1 px; por eso ese criterio no está tildado.
- Que el halo de foco de las miniaturas se vea bien y que la página se desplace para mostrar la enfocada con muchas capturas.
- La sensación del arrastre con un mouse o touchpad real (umbral de 1/4 y velocidad de 800 px/s) y que no parpadee al asentar con PNG 4K.
- Que el cursor se oculte junto con los controles y que el reproductor con «Ir a» desde pantalla completa se vea bien.
- `↓` desde «…» abre su menú (como antes), así que a la grilla se entra desde Reproducir o «Marcar como vista».

2026-11-03: publicado en `v0.3.0-rc3`; las pruebas manuales dieron OK. El code review del merge dejó arreglos en `fix/visor-review`: «Ir a» arranca como máximo 5 s antes del final, `inicio` pasa a `real`, al volver de «Ir a» el foco queda en la última captura vista, `salir` e `irAlMomento` terminan la animación antes de actuar, el foco de las miniaturas sobrevive a un cambio de la lista, una velocidad vieja ya no cuenta como gesto rápido, `Esc` en pantalla completa muestra los controles y las imágenes del visor se limitan a la resolución de la pantalla. `↓` desde «…» sigue abriendo su menú, y la spec ya lo dice.
