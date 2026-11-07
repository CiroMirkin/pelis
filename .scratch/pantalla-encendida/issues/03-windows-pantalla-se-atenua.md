# 03: En Windows la pantalla se atenúa mientras se reproduce

**What to build:** mientras una película se reproduce en Windows, la pantalla no se atenúa, no se apaga y no se bloquea. Hoy se atenúa. Hay un pedido con `SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)` (`src/pelis/pantalla.py:32`), pero no alcanza o no llega a hacer efecto.

**Blocked by:** None.

**Status:** needs-info

## Hipótesis

1. **La llamada falla sin avisar.** No se mira el valor que devuelve `SetThreadExecutionState` (0 es error), así que el log no muestra nada.
2. **El pedido no frena la atenuación.** En notebooks, "Atenuar la pantalla" (y la atenuación adaptable o por presencia de Windows 11) puede ignorar `ES_DISPLAY_REQUIRED`. Los reproductores usan `PowerCreateRequest` + `PowerSetRequest(PowerRequestDisplayRequired)`, y eso también figura en `powercfg /requests` con nombre y motivo.
3. **El pedido se suelta enseguida.** Si `reproduciendo` cambia a falso un instante (por ejemplo, al buscar o al cambiar de pista), se manda `ES_CONTINUOUS` solo y el pedido queda liberado.

## Lo que falta saber (lo hace el usuario en Windows)

- [ ] Con una película reproduciéndose, correr `powercfg /requests` en una consola **como administrador** y anotar qué aparece en `DISPLAY:` y `SYSTEM:`.
- [ ] ¿Es una notebook? ¿Está activada la atenuación adaptable (Configuración → Sistema → Energía, o Pantalla → Brillo)?
- [ ] ¿Se atenúa a los cuántos minutos? ¿Ese tiempo coincide con "Atenuar la pantalla después de"?

## Criterio de terminado

- [ ] Reproduciendo más tiempo que la atenuación y el apagado configurados, la pantalla sigue con el brillo normal.
- [ ] Pausado o fuera del reproductor, la pantalla se atenúa y se apaga como siempre.
- [ ] Si el pedido falla, queda en el log.
