# reproduccion.Sesion con sus tests

Status: done

## Qué
- `src/pelis/reproduccion.py` con `Sesion` y `Resultado` (ver spec), en Python puro.
- Mudar `progreso_a_guardar`, `posicion_de_retomar`, `PROGRESO_MINIMO_MS` y `RETROCESO_AL_RETOMAR_MS` desde `catalogo.py`. Mientras no esté la 02, `puente.py` puede importarlos desde `reproduccion`.
- `tests/test_reproduccion.py` con TDD, contra `Sesion` y SQLite real, cubriendo la lista de la spec. Los tests de esas dos funciones se van de `test_catalogo.py`.

## Criterio de terminado
- [x] `Sesion` cumple las siete reglas de la spec, cada una con su test.
- [x] Los avisos antes de `cargo` y después del primer `salio` no escriben en la base.
- [x] Están todos los tests de la lista de `test_reproduccion.py` de la spec. `retomar_y_salir_enseguida_no_pierde_el_progreso` está marcado `xfail` (T9).
- [x] `catalogo.py` no tiene reglas del reproductor.
- [x] La suite pasa.

## Comments
- `cargo` devuelve `None` en la segunda carga (test `cambiar_de_pista_no_vuelve_a_mover_el_arranque`): sin `inicializado` en QML, la sesión tiene que frenar el LoadedMedia repetido. En la 02, `cargaInicial` llama primero a `reproduccionCargo` y no hace nada si devuelve -1.
- Sumado `una_duracion_desconocida_no_borra_la_medida`, que replica el `if (player.duration > 0)` de hoy.
- `progreso_a_guardar` y `posicion_de_retomar` siguen públicas porque Puente las usa hasta la 02; ahí pasan a privadas.
- T9 es `xfail(strict=True)`: si la regla se arregla, el test avisa para sacarle la marca.
