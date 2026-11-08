# 01: Buscar o elegir época pasa el filtro de vistas a «Todas»

**What to build:** en el catálogo, con «Sin ver» o «Vistas» elegido, buscar un texto o elegir una época pone el filtro de vistas en «Todas», y la barra lo muestra subrayado. El estado del filtro de vistas pasa a vivir en `ModeloCatalogo` (propiedad con notificación); la barra lo lee de ahí y deja de guardarlo aparte. Ver spec: «Filtro de vistas».

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] `filtrar` con texto no vacío restablece el filtro de vistas a «todas».
- [ ] `filtrarPeriodo` con una época no vacía hace lo mismo.
- [ ] `filtrar("")` y `filtrarPeriodo("")` no tocan el filtro de vistas.
- [ ] Elegir «Sin ver» o «Vistas» después de buscar o elegir época se combina con ambos.
- [ ] La barra subraya «Todas» cuando el filtro se restablece solo; la Recomendada y su botón siguen ocultándose con búsqueda, «Vistas», época o incompletas.
- [ ] Tests en `tests/test_catalogo.py` para cada regla; `test_filtros_de_vistas_periodo_y_busqueda_se_combinan` reescrito con el orden nuevo.
