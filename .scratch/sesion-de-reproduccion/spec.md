# Sesión de reproducción

Candidato 1 de la revisión de arquitectura del 2026-11-08, acotado en un grilling el mismo día.

## Problema
La regla de qué pasa con el Progreso y la Vista mientras se reproduce está repartida en siete lugares, y la mitad vive en QML sin tests:
- `Reproductor.qml`: los flags `inicializado`, `terminada` e `inicio` (`inicio < 0` decide si es Visita en `:65` y `:166`), el acotado `duration - 5000` (`:132`) y el reinicio de `terminada` al dar play (`:172`).
- `Main.qml:41-44`: al cerrar la app busca un `guardarProgreso` a ciegas en `pila.currentItem`.
- `Visor.qml:55`: resta los 5 s del «Ir a».
- `puente.py`: `guardarProgreso` (umbral y recomendada), `terminar` (progreso 0 y vista), `guardarDuracion`, y `abrir`, que arma `retomarDesde`.
- `catalogo.py`: `progreso_a_guardar` (3 min) y `posicion_de_retomar` (15 s), que son reglas del reproductor y no del catálogo.

El bug de «Ir a» (57ce148) se arregló solo en QML. Cada regla nueva del reproductor (por ejemplo, fbfd04e, retomar 15 s antes) cae en un lugar distinto.

## Decisiones
- **Sin cambios de comportamiento.** Las reglas de hoy se mantienen:
  - una Visita no toca el Progreso ni marca Vista, aunque llegue al final;
  - antes de 3 minutos el Progreso se guarda en 0;
  - llegar al final deja el Progreso en 0 y la marca Vista;
  - volver a dar play después del final hace que salir guarde de nuevo;
  - pausar guarda el Progreso;
  - al retomar, arranca 15 s antes del Progreso guardado;
  - una Visita arranca 5 s antes de la posición pedida, acotada a 5 s antes del final.
- **`src/pelis/reproduccion.py`**, en Python puro y sin Qt, con la clase `Sesion`: la sesión de reproducción de una película, desde que se abre hasta que se sale. Interfaz:
  - `Sesion(conn, pelicula_id, visita_ms=None)`. Con `visita_ms` es una Visita.
  - `cargo(duracion_ms) → int`: devuelve la posición de arranque en ms y guarda la duración si es mayor que 0.
  - `pauso(posicion_ms) → Resultado`: guarda el Progreso.
  - `reanudo()`: después del final, vuelve a habilitar que salir guarde.
  - `termino() → Resultado`: deja el Progreso en 0 y marca Vista, salvo en una Visita.
  - `salio(posicion_ms) → Resultado`: guarda el Progreso, salvo si terminó o es una Visita.
  - `Resultado` vale `"empezada"` (se guardó un Progreso mayor que 0), `"vista"` o `None`.
- **Orden de los avisos**: lo que llega antes de `cargo` se ignora y devuelve `None` (hoy eso lo hace `inicializado`). Lo que llega después del primer `salio` también se ignora; así salir con Esc y cerrar la ventana no guardan dos veces.
- **La sesión no conoce la recomendada ni el catálogo.** Solo escribe en la base y devuelve el `Resultado`.
- **`progreso_a_guardar`, `posicion_de_retomar` y sus constantes** se mudan de `catalogo.py` a `reproduccion.py`, como detalles privados.
- **Puente** guarda la sesión abierta y es el único adaptador de Qt:
  - `abrir(pelicula_id, visita_ms)` crea la `Sesion`. Ya no devuelve `retomarDesde`.
  - Hay un slot fino por aviso: `reproduccionCargo(duracion) → int`, `reproduccionPauso(pos)`, `reproduccionReanudo()`, `reproduccionTermino()` y `reproduccionSalio(pos)`. No reciben `peliculaId`.
  - Cada slot traduce el `Resultado`. Con `"empezada"` cierra la recomendada si es esa película, como hoy en `guardarProgreso`. Con `"vista"` hace lo mismo que `marcarVista`: cierra la recomendada y recarga el catálogo. Con una duración nueva avisa a `Recomendacion.duracion`.
  - Se van los slots `guardarProgreso`, `terminar` y `guardarDuracion`.
- **QML**:
  - `Reproductor.qml` pierde `inicializado`, `terminada`, las comparaciones con `inicio` y el acotado. Le pasa a `abrir` el `inicio` (-1 si no es Visita) y solo informa los avisos de `MediaPlayer`.
  - El Reproductor escucha él mismo el cierre de la ventana y avisa `salio` con la posición. `Main.qml` deja de mirar `guardarProgreso`.
  - `Component.onDestruction` sigue haciendo solo lo de hoy: suelta el bloqueo de pantalla y llama a `salioDelReproductor` para recargar el catálogo una vez.
  - `Visor.qml` pasa el momento de la captura sin restarle 5 s.

## Tests
Validado con la skill `tool:audit-tests` el 2026-11-08. Los ids T* son de ese reporte.

### `tests/test_reproduccion.py`
Los tests van contra `Sesion`, con SQLite real en `tmp_path`, y verifican leyendo la base (`db.pelicula`). Cada nombre es una regla:
- `salir_antes_de_3_minutos_no_la_deja_empezada` y `salir_desde_los_3_minutos_guarda_el_progreso`: 179 999 ms guarda 0 y 180 000 ms guarda 180 000. Reemplazan `test_progreso_cuenta_desde_los_3_minutos` (T1, T3).
- `retomar_arranca_15_segundos_antes_del_progreso`: con progreso 2 400 000, `cargo` devuelve 2 385 000. Con progreso 10 000, devuelve 0. Reemplaza `test_retomar_arranca_15_segundos_antes` (T1, T6).
- `pausar_guarda_el_progreso`.
- `llegar_al_final_la_marca_vista_y_vuelve_al_principio`: `termino` devuelve `"vista"`, deja el progreso en 0 y `watched` en 1 (T5).
- `salir_despues_del_final_no_pisa_el_progreso` y `volver_a_reproducir_despues_del_final_vuelve_a_guardar_al_salir`.
- `una_visita_no_toca_el_progreso_ni_la_vista`: pausar, salir y llegar al final no cambian el progreso previo ni `watched`. Es la regresión de 57ce148 (T7).
- `una_visita_arranca_5_segundos_antes_acotada_al_final`: con duración 60 000, pedir 30 000 da 25 000, pedir 59 000 da 54 000, pedir 70 000 da 55 000 y pedir 3 000 da 0.
- `una_visita_sin_duracion_arranca_5_segundos_antes_sin_acotar`: con duración 0, pedir 90 000 da 85 000 (T8).
- `salir_dos_veces_guarda_una_sola_vez`: el segundo `salio` con otra posición no cambia lo guardado.
- `los_avisos_antes_de_cargar_no_guardan_nada`.
- `cargar_guarda_la_duracion`.
- `retomar_y_salir_enseguida_no_pierde_el_progreso` va **marcado `xfail`** (T9). Con progreso 185 000, `cargo` arranca en 170 000. Salir en 175 000 hoy guarda 0, por el umbral de 3 min cruzado con el retroceso de 15 s. La regla se decide aparte, y este test queda rojo como recordatorio.

Los tests de `progreso_a_guardar` y `posicion_de_retomar` se van de `test_catalogo.py`.

### `tests/test_puente.py`
Quedan solo los tests de traducción. En lugar de reemplazar `_recargar_catalogo`, que es privado, cuentan las emisiones de la señal pública `puente.catalogo.modelReset` (T2):
- `pausar_no_recarga_el_catalogo`: reemplaza `test_guardar_progreso_no_recarga_el_catalogo` (b87e4d6).
- `empezar_la_recomendada_la_cierra`: después de abrir, cargar y pausar en 300 000, `puente.recomendada` queda vacía (T4).
- `llegar_al_final_recarga_el_catalogo_con_la_pelicula_vista`.
- `salir_del_reproductor_recarga_el_catalogo`: el test de hoy, pero contando `modelReset`.

QML sigue sin tests, pero ya no decide nada.

## Fuera de alcance
- Pistas de audio, subtítulos y capturas (`eleccionInicial`, `textoEn`, `cargarExterno`, `capturar`, `_video`, `_externos`, `_linea`). Pueden ser un candidato aparte.
- `marcarVista` y `marcarTodasVistas` desde el detalle o el catálogo: son a mano y no forman parte de una sesión.
- Glosario: ya se agregaron Visita, Progreso y Vista.
