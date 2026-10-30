# 01: El progreso cuenta recién a partir de los 3 minutos vistos

**What to build:** si se sale o se pausa antes de los 3 minutos de una película, no queda empezada: el progreso guardado es 0, no pasa a "a medias" y, si era la **Recomendada**, la recomendación sigue abierta. Sirve para abrir una peli, mirar el arranque y volver sin que cuente como empezada.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Salir o pausar antes de los 3 minutos guarda progreso 0.
- [x] La **Tarjeta** sigue sin barra de progreso y fuera de "a medias".
- [x] Si era la **Recomendada**, sigue ofreciéndose.
- [x] Desde los 3 minutos se guarda la posición como hasta ahora.
- [x] Volver atrás a menos de 3 minutos en una peli ya empezada y salir la deja sin empezar.

## Comments

- 29/10/2026: la regla vive en `catalogo.progreso_a_guardar` (con test) y la aplica `Puente.guardarProgreso`, que es por donde pasan salir y pausar. Con progreso 0 no se cierra la **Recomendada**. Al terminar la peli sigue mandando `terminar`, que no pasa por esta regla. Se prueba en la app con `v0.3.0-rc2`.
