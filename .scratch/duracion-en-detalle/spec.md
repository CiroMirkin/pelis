# Duración de la película en el detalle

Acotado en un grilling (2026-10-25).

## Problema
El detalle no muestra cuánto dura la película. `duracion_ms` solo se conoce si la película se reprodujo alguna vez o salió como recomendada (se mide sin reproducir).

## Decisiones
- Se muestra en la línea de datos del detalle, entre género y países: `2019   *   DRAMA   *   2 h 5 min   *   🇦🇷`.
- Formato redondeado al minuto: `2 h 5 min`, `2 h` (minutos en 0), `45 min`. Función compartida en `qml/duracion.js`, usada por `Detalle.qml` y la recomendada de `Catalogo.qml` (que pasa a mostrar `2 h` en vez de `2 h 0 min`).
- Fuente: `duracion_ms` de la base; si falta, al abrir el detalle se mide el archivo con `Puente._medir_duracion` (QMediaPlayer) y queda guardada.
- Al terminar la medición, Puente emite una señal y el detalle abierto se recarga solo (aparecen duración y hora de fin).
- Si no se conoce o no se puede medir, ese tramo se omite; sin texto de relleno.

## Fuera de alcance
- Medir durante el escaneo.
- `Runtime` de OMDb.
