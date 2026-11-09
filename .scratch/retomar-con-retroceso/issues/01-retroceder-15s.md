# 01: Retomar 15 s antes del progreso guardado

**What to build:** al reproducir una película empezada, el reproductor arranca 15 s antes del progreso guardado (nunca antes de 0), para retomar el hilo de la escena. El progreso guardado no cambia: el retroceso se aplica solo al arrancar. Una **Visita** («Ir a» desde el visor de capturas) sigue arrancando en la posición exacta. Los 15 s son fijos, no configurables.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Con progreso guardado, la reproducción arranca 15 s antes de ese punto.
- [x] Si el retroceso daría menos de 0, arranca en 0.
- [x] Sin progreso guardado, arranca desde el principio como hoy.
- [x] Una Visita arranca en la posición pedida, sin retroceso.
- [x] El progreso en la base no cambia al abrir; «Continuar desde» del detalle sigue mostrando el valor guardado.
- [x] El cálculo es una función pura del catálogo con su test.
