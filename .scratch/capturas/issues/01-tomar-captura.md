# Tomar la captura con `.`

Status: done

## Qué
- `src/pelis/capturas.py` con `ruta_libre(carpeta_pelicula, posicion_ms) → Path`: `capturas/HH-MM-SS.png`, o `HH-MM-SS(n).png` con el primer `n ≥ 2` libre (ver spec)
- Slot en `Puente` que recibe el `videoSink` (o el `QImage`) y la posición: toma el cuadro en el hilo de la UI y codifica/escribe el PNG en un hilo aparte; crea `capturas/` si falta; avisa con una señal ok/error y loguea el motivo del error
- `Reproductor.qml`: `Shortcut` en `.` con `autoRepeat: false`, y el aviso discreto arriba a la derecha («Captura» / «Captura fallida» en color de alerta, ~1,5 s con fundido, sin mostrar los controles)
- `tests/test_capturas.py` para `ruta_libre`

## Criterio de terminado
- [ ] `.` guarda un PNG en resolución original, sin subtítulos externos ni embebidos, en pausa y reproduciendo
- [x] Varias capturas en el mismo segundo dan `(2)`, `(3)`… sin pisar ninguna
- [ ] Mantener `.` apretada saca una sola captura
- [ ] La película no se traba al capturar un video 4K
- [ ] Sin permisos de escritura aparece «Captura fallida» y el motivo queda en el log
- [x] La suite pasa

## Comments
- Verificado sin abrir la app: `tests/test_capturas.py` (nombres, sufijos, horas en dos dígitos, `guardar` no pisa) y un smoke test offscreen de `Puente.capturar` con un `QVideoSink` y un cuadro 4K sintético: PNG de 3840×2160, `(2)` en el mismo segundo, sin cuadro → señal de error, carpeta sin permisos → señal de error con el `Permiso denegado` en el log. La lectura del cuadro en el hilo de la UI tardó ~50 ms por captura (CPU, sin RHI).
- Sin tildar porque hay que abrir la app con una película real: que el PNG salga sin subtítulos (externos y embebidos) en pausa y reproduciendo, que `autoRepeat: false` dé una sola captura al mantener `.`, que un 4K real no se trabe (con decodificación por hardware `toImage()` baja el cuadro de la GPU), y que el aviso «Captura fallida» se vea en la UI.
- El motivo va al log con `logging` (`pelis.puente`); sin configuración, los `warning` salen por stderr.
