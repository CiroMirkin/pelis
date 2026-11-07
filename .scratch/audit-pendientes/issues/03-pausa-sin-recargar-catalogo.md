# 03: Pausar no recarga el catálogo

**What to build:** pausar en el reproductor solo guarda el progreso. Hoy cada pausa recarga todo el catálogo: relee todas las películas, revisa en el disco el póster de cada una (dos accesos por película) y reinicia la grilla, que en ese momento no se ve. En un NTFS montado desde Linux, con cientos de películas, puede dar un tirón. El catálogo se tiene que recargar una sola vez, al volver del reproductor.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Pausar guarda el progreso y no recarga el catálogo.
- [ ] Al salir del reproductor (Esc, botón volver o cerrar la ventana), la **Tarjeta** muestra la barra de progreso actualizada y la película aparece entre las "a medias".
- [ ] El detalle, al volver del reproductor, sigue mostrando el progreso y la hora de fin actualizados.
- [ ] Si era la **Recomendada**, empezarla la sigue cerrando.

## Dónde

- `Puente.guardarProgreso` (`src/pelis/puente.py:700`) guarda, avisa a la **Recomendada** y llama a `_recargar_catalogo()`. El reproductor la llama al pausar (`Reproductor.qml:168`) y en `salir()` (`Reproductor.qml:72`).
- Propuesta: que `guardarProgreso` solo guarde y avise a la Recomendada, y que se recargue una vez al cerrar el reproductor. Hay tres salidas que tienen que terminar ahí: `salir()` (Esc o Volver), cerrar la ventana (`Main.qml:41`, `onClosing`) y `Component.onDestruction`, que hoy ya se usa para soltar la pantalla. Lo más simple es un slot nuevo (ej. `puente.salioDelReproductor()`) que llame `_recargar_catalogo()`, invocado desde `Component.onDestruction` del reproductor.
- El detalle relee el progreso al volver: revisar qué señal escucha `Detalle.qml` para que la hora de fin y el progreso no dependan del recargado del catálogo en cada pausa.
- Test en `tests/test_puente.py`: `guardarProgreso` no dispara la recarga del catálogo, y el slot de salida sí.
