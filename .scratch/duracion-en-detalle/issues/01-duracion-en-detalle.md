# Mostrar la duración en el detalle

Status: done

## Qué
- `qml/duracion.js` con `texto(ms)`; `Catalogo.qml` y `Detalle.qml` lo usan
- `Puente.pelicula` mide la duración si falta (una medición por película a la vez) y `Puente` emite `duracionMedida(int, int)`
- `Detalle.qml` recarga al recibir `duracionMedida` de su película

## Criterio de terminado
- [x] Película nunca reproducida: al abrir el detalle aparece la duración y la hora de fin sin reabrir
- [x] Película ya medida: la duración aparece de entrada, sin volver a medir
- [x] `7500000` ms → `2 h 5 min`; `7200000` → `2 h`; `2700000` → `45 min`; `0` → nada
- [x] Archivo que no se puede medir: la línea queda como antes

## Comments

2026-10-25: implementado. Formato verificado con node; medición probada sobre una copia de `dev/` (Mikey And Nicky → 6382959 ms, señal `duracionMedida` recibida; archivo inexistente no muestra nada). 125 tests pasan, qmllint limpio. Pendiente a mano: ver en pantalla que la duración y la hora de fin aparecen solas al abrir el detalle de una película nunca reproducida.
