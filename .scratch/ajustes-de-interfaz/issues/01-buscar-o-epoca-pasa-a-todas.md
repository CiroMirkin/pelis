# 01: Buscar o elegir época pasa el filtro de vistas a «Todas»

**What to build:** en el catálogo, con «Sin ver» o «Vistas» elegido, buscar un texto o elegir una época pone el filtro de vistas en «Todas», y la barra lo muestra subrayado. El estado del filtro de vistas pasa a vivir en `ModeloCatalogo` (propiedad con notificación); la barra lo lee de ahí y deja de guardarlo aparte. Ver spec: «Filtro de vistas».

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `filtrar` con texto no vacío restablece el filtro de vistas a «todas».
- [x] `filtrarPeriodo` con una época no vacía hace lo mismo.
- [x] `filtrar("")` y `filtrarPeriodo("")` no tocan el filtro de vistas.
- [x] Elegir «Sin ver» o «Vistas» después de buscar o elegir época se combina con ambos.
- [x] La barra subraya «Todas» cuando el filtro se restablece solo; la Recomendada y su botón siguen ocultándose con búsqueda, «Vistas», época o incompletas.
- [x] Tests en `tests/test_catalogo.py` para cada regla; `test_filtros_de_vistas_periodo_y_busqueda_se_combinan` reescrito con el orden nuevo.
