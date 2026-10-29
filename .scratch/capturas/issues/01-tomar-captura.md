# Tomar la captura con `.`

Status: ready-for-agent

## Qué
- `src/pelis/capturas.py` con `ruta_libre(carpeta_pelicula, posicion_ms) → Path`: `capturas/HH-MM-SS.png`, o `HH-MM-SS(n).png` con el primer `n ≥ 2` libre (ver spec)
- Slot en `Puente` que recibe el `videoSink` (o el `QImage`) y la posición: toma el cuadro en el hilo de la UI y codifica/escribe el PNG en un hilo aparte; crea `capturas/` si falta; avisa con una señal ok/error y loguea el motivo del error
- `Reproductor.qml`: `Shortcut` en `.` con `autoRepeat: false`, y el aviso discreto arriba a la derecha («Captura» / «Captura fallida» en color de alerta, ~1,5 s con fundido, sin mostrar los controles)
- `tests/test_capturas.py` para `ruta_libre`

## Criterio de terminado
- [ ] `.` guarda un PNG en resolución original, sin subtítulos externos ni embebidos, en pausa y reproduciendo
- [ ] Varias capturas en el mismo segundo dan `(2)`, `(3)`… sin pisar ninguna
- [ ] Mantener `.` apretada saca una sola captura
- [ ] La película no se traba al capturar un video 4K
- [ ] Sin permisos de escritura aparece «Captura fallida» y el motivo queda en el log
- [ ] La suite pasa
