# Fase 4 — Reproductor+

Refinamientos del reproductor sobre lo hecho en el MVP. Los ajustes se aplican a los subtítulos externos, que pasan por el overlay propio. Los embebidos los dibuja el `VideoOutput` de Qt con su estilo (22/10/2026: quitarles el texto en un sink intermedio copiaba cada frame a RAM y la reproducción se trababa).

## Alcance

### Subtítulos
- Tamaño y color de letra. Hecho (22/10/2026): global (en `preferencias.ini`), se cambia desde el panel «Audio y subtítulos» del reproductor como en Stremio: tamaño de 50 % a 200 % en pasos de 25 %, y cinco colores (blanco, amarillo, celeste, verde, rosa). Se aplica a los externos; los embebidos los dibuja Qt con su estilo.
- Sincronización manual (adelantar / atrasar)
- Elección manual de la codificación de caracteres, para los casos que la detección automática del MVP (UTF-8 → cp1252) no resuelve

### Duración y hora estimada de fin
- Hecho (22/10/2026), adelantado desde esta fase: en el reproductor ("Termina 23:47" junto a la duración, se refresca cada segundo, también en pausa) y en el detalle ("Si empezás / seguís ahora, termina a las…"). En el detalle solo aparece si la película ya se abrió alguna vez, porque la duración la da el reproductor al cargar.
- Hora estimada de finalización calculada al vuelo: `ahora() + (duracion_ms - progreso_ms)`
- Se recalcula si se pausa

## Decisiones abiertas para esta fase
- Si la sincronización y la codificación son globales o por película (tamaño y color quedaron globales).

## Criterio de terminado
- [ ] Un `.srt` con una codificación que la detección automática no resuelve se ve correctamente eligiéndola a mano
- [ ] Ajustar la sincronización corrige un subtítulo desfasado
- [ ] La hora de fin estimada es correcta y se actualiza al pausar
