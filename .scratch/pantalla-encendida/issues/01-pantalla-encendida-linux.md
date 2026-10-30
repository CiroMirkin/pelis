# 01: La pantalla no se bloquea mientras se reproduce (Linux)

**What to build:** mientras una película se reproduce en el reproductor, el sistema no bloquea la pantalla por inactividad (en Cinnamon pasaba a los 15 minutos y pedía la contraseña). Al pausar, salir del reproductor o cerrar la app, el bloqueo por inactividad vuelve a funcionar normal.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human

- [x] Reproduciendo, la sesión queda inhibida para inactividad (comprobado con `IsInhibited` de `org.gnome.SessionManager`).
- [x] Pausar o salir del reproductor libera el permiso.
- [x] Si el sistema no ofrece el servicio, la película se reproduce igual y el error queda en el log.
- [ ] Con el ejecutable instalado, mirar más de 15 minutos sin tocar nada y que la pantalla no se bloquee.
- [ ] Pausado más de 15 minutos, la pantalla se bloquea como siempre.

## Comments

- 29/10/2026: el código ya está y los tests pasan. El pedido se hace con `Inhibit` de `org.freedesktop.ScreenSaver` por D-Bus, desde una conexión propia. Para liberarlo se cierra esa conexión, porque `UnInhibit` exige un uint32 que PySide6 no sabe mandar. Lo que falta es probarlo en la app instalada.
