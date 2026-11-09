# reproduccion.Sesion con sus tests

Status: ready-for-agent

## Qué
- `src/pelis/reproduccion.py` con `Sesion` y `Resultado` (ver spec), en Python puro.
- Mudar `progreso_a_guardar`, `posicion_de_retomar`, `PROGRESO_MINIMO_MS` y `RETROCESO_AL_RETOMAR_MS` desde `catalogo.py`. Mientras no esté la 02, `puente.py` puede importarlos desde `reproduccion`.
- `tests/test_reproduccion.py` con TDD, contra `Sesion` y SQLite real, cubriendo la lista de la spec. Los tests de esas dos funciones se van de `test_catalogo.py`.

## Criterio de terminado
- [ ] `Sesion` cumple las siete reglas de la spec, cada una con su test.
- [ ] Los avisos antes de `cargo` y después del primer `salio` no escriben en la base.
- [ ] Están todos los tests de la lista de `test_reproduccion.py` de la spec. `retomar_y_salir_enseguida_no_pierde_el_progreso` está marcado `xfail` (T9).
- [ ] `catalogo.py` no tiene reglas del reproductor.
- [ ] La suite pasa.
