# Puente y QML usan la Sesion

Status: ready-for-agent

Blocked by: 01

## Qué
- `Puente.abrir(pelicula_id, visita_ms)` crea la `Sesion`. Agregar los slots `reproduccionCargo`, `reproduccionPauso`, `reproduccionReanudo`, `reproduccionTermino` y `reproduccionSalio`, que traducen el `Resultado` en recomendada y catálogo (ver spec).
- Borrar `guardarProgreso`, `terminar` y `guardarDuracion` de Puente.
- `Reproductor.qml`:
  - sin `inicializado`, `terminada`, comparaciones con `inicio` ni acotado;
  - informa los avisos de `MediaPlayer`;
  - escucha el cierre de la ventana y avisa `salio`.
- `Main.qml`: sacar el `onClosing` que busca `guardarProgreso`.
- `Visor.qml`: pasar el momento de la captura sin restar 5 s.
- `test_puente.py`: reemplazar `test_guardar_progreso_no_recarga_el_catalogo` por los tests de traducción de la spec.

## Criterio de terminado
- [ ] `grep -n "inicio <\|terminada\|inicializado" src/pelis/qml/Reproductor.qml` no encuentra nada.
- [ ] Prueba a mano:
  - seguir una película arranca 15 s antes;
  - pausar y salir guarda;
  - cerrar la app con el reproductor abierto guarda;
  - llegar al final la marca vista;
  - «Ir a» desde el visor no toca el progreso ni la vista, aunque llegue al final.
- [ ] La suite pasa.
