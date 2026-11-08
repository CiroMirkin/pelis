# 02: Volver sin pasar por pantallas repetidas

**What to build:** abrir una persona o una película que ya está en la pila de navegación vuelve a esa pantalla (desapilando lo que tenía encima) en lugar de apilar una copia. En película › director › otra película › director › otra película, «Volver» desde la última lleva al director, y de ahí a la primera película. La regla vive en un helper de navegación compartido por Detalle y Persona (estilo `duracion.js`). Ver spec: «Navegación».

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Una persona se identifica por nombre y una película por id; si ya está en la pila, se desapila hasta ella.
- [ ] Si no está, se apila como hoy.
- [ ] La pantalla a la que se vuelve recarga y deja el foco en la grilla, igual que con «Volver».
- [ ] Esc y el botón «Volver» llevan al mismo lugar.
- [ ] Reproductor, visor, editar y faltantes no cambian.
- [ ] Verificado a mano en la app con el recorrido de la spec.
