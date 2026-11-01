# Visor de capturas

Status: ready-for-agent
Blocked by: 02

Pedido el 2026-10-29, acotado en un grilling (2026-11-01). Decisiones en la spec: secciones «Sección Capturas» (interacción y foco), «Visor», «Ir al momento» y «Grilla de tercios».

## Qué
- `Detalle.qml`: las miniaturas abren el visor con click, y con `Enter`/`Espacio` cuando tienen foco. Foco de teclado en la grilla (entrar con `↓` desde los botones, flechas dentro, `↑` desde la primera fila para salir), con desplazamiento para que la enfocada se vea. Al volver del visor, el foco queda en la última captura vista.
- `Visor.qml` nuevo: recibe la lista de capturas, el índice inicial y el `peliculaId`. Muestra la imagen ajustada sobre fondo negro, con botones laterales, `←`/`→`, arrastre con animación y navegación circular. La barra de abajo lleva el momento, «n de N», «Ir a HH:MM:SS» y el toggle de la grilla de tercios. Los controles se ocultan tras unos segundos sin actividad. `F` alterna la pantalla completa; `Esc` la quita primero y después vuelve al detalle.
- El momento de cada captura sale del nombre (`capturas.CRONOLOGICA`). `Puente.pelicula` puede devolver, junto a cada URL, el momento en ms (o `null` si no es cronológica), así QML no tiene que parsear nombres.
- `Reproductor.qml`: una propiedad opcional con la posición de arranque (ms) que, si viene, reemplaza a `info.progreso` en el seek inicial. «Ir a» hace `replace` del visor por el reproductor con `max(0, momento − 5000)`, acotado a la duración.
- Tests: que el momento se extraiga del nombre (con y sin sufijo `(n)`, y `null` en las no cronológicas).

## Criterio de terminado
- [ ] Click en una miniatura abre el visor en esa captura; con teclado se llega a la grilla y `Enter`/`Espacio` la abre
- [ ] `←`/`→`, los botones y el arrastre pasan de captura; de la última se va a la primera y viceversa
- [ ] Un arrastre corto vuelve la imagen a su lugar
- [ ] Los controles se ocultan solos y vuelven al mover el mouse o tocar una tecla
- [ ] «Ir a 01:23:45» abre el reproductor en 01:23:40; `Esc` ahí vuelve al detalle, no al visor
- [ ] Una captura sin nombre `HH-MM-SS` no muestra «Ir a»
- [ ] La grilla de tercios aparece solo sobre la imagen, roja al 80 %, sigue visible al ocultar los controles, se mantiene al pasar de captura y arranca apagada al reabrir
- [ ] `Esc` en pantalla completa la quita; el segundo `Esc` vuelve al detalle con el foco en la última captura vista
- [ ] La suite pasa
