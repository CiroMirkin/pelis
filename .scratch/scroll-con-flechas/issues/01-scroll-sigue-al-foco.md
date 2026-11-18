# 01: El scroll de la lista de pelis sigue al foco con las flechas

**What to build:** al recorrer la lista de películas con las flechas del teclado, la vista baja (y sube) para que la película con foco siempre quede visible. Hoy el foco pasa a filas que están fuera de pantalla y el scroll no se mueve. Vale para el catálogo y para la página de persona (películas del director), que usan la misma grilla.

Pista de causa (sin verificar): las grillas tienen `highlightFollowsCurrentItem: false`, y con eso la vista no acompaña al elemento actual al mover el foco.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] En el catálogo, con `↓` repetido, el foco llega a filas que no se veían y la vista baja hasta mostrarlas por completo, incluido el halo del foco.
- [ ] Con `↑` la vista sube igual cuando el foco sale por arriba.
- [ ] Con `←`/`→` al cambiar de fila el comportamiento es el mismo.
- [ ] Lo mismo en la página de persona.
- [ ] Pasar el mouse sobre una tarjeta no hace saltar el scroll (hoy el hover fija el elemento actual).
- [ ] Volver del detalle al catálogo mantiene la película con foco visible.
- [ ] Hay un test que falla sin el arreglo.
