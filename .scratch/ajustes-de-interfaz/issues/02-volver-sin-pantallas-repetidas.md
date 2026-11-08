# 02: Volver sin pasar por pantallas repetidas

**What to build:** abrir una persona o una película que ya está en la pila de navegación vuelve a esa pantalla (desapilando lo que tenía encima) en lugar de apilar una copia. En película › director › otra película › director › otra película, «Volver» desde la última lleva al director, y de ahí a la primera película. La regla vive en un helper de navegación compartido por Detalle y Persona (estilo `duracion.js`). Ver spec: «Navegación».

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Una persona se identifica por nombre y una película por id; si ya está en la pila, se desapila hasta ella.
- [x] Si no está, se apila como hoy.
- [x] La pantalla a la que se vuelve recarga y deja el foco en la grilla, igual que con «Volver».
- [x] Esc y el botón «Volver» llevan al mismo lugar.
- [x] Reproductor, visor, editar y faltantes no cambian.
- [x] Verificado a mano en la app con el recorrido de la spec.

## Comments

- 08/11/2026: el usuario pidió como máximo 3 «Volver» hasta el catálogo. La regla queda: película (nivel 1) › persona (nivel 2) › película (nivel 3). Abrir una persona desde el nivel 3 vuelve a la misma persona si coincide o la reemplaza si es otra; una película que ya estaba en la pila se puede repetir (Alien › Ridley Scott › Alien). Reemplaza la regla de «no repetir pantallas». Reproductor, visor y editar siguen apilándose encima.
