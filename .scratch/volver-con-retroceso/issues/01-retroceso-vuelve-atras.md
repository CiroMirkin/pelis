# 01: Retroceso vuelve a la vista anterior

**What to build:** además de `Esc`, la tecla Retroceso (la de borrar hacia atrás, no `Supr`) vuelve a la vista anterior en las pantallas que hoy se cierran con `Esc`: detalle, persona, editar, faltantes, visor de capturas y reproductor. Retroceso solo sirve para volver: en el reproductor y el visor siempre vuelve a la vista anterior, sin la cadena de `Esc` (cerrar panel, salir de pantalla completa). En el catálogo no hay a dónde volver, así que no hace nada (no limpia la búsqueda).

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Retroceso vuelve a la vista anterior desde detalle, persona, editar, faltantes, visor y reproductor.
- [ ] En el reproductor y el visor vuelve directo, aunque haya un panel abierto o esté en pantalla completa.
- [ ] En los campos de texto (editar, buscador del catálogo) Retroceso sigue borrando y no cambia de vista.
- [ ] Con un diálogo o confirmación abierta, Retroceso no vuelve a la vista de atrás.
- [ ] En el catálogo, Retroceso no hace nada.
- [ ] `Esc` sigue funcionando como hasta ahora en todas las pantallas.
- [ ] Hay un test que falla sin el cambio.
