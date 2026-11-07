# 02: La pantalla no se apaga ni se bloquea mientras se reproduce (Windows)

**What to build:** lo mismo que la 01, pero en Windows: mientras una película se reproduce, la pantalla no se apaga, no se bloquea y la compu no se suspende. Al pausar o salir del reproductor, vuelve el comportamiento normal de energía.

**Blocked by:** 01 (La pantalla no se bloquea mientras se reproduce, Linux).

**Status:** needs-info

- [ ] Con el ejecutable de Windows, mirar más tiempo que el apagado de pantalla configurado sin tocar nada, y que la pantalla siga encendida.
- [ ] Pausado, la pantalla se apaga en el tiempo configurado.
- [ ] `powercfg /requests` muestra el pedido de Pelis mientras se reproduce y deja de mostrarlo al pausar.

## Comments

- 29/10/2026: el código ya está, con `SetThreadExecutionState`, pero no se probó en Windows.

- 07/11/2026: **no funciona.** Reproduciendo en Windows, la pantalla se atenúa. Falta diagnosticar; ver la issue 03.
