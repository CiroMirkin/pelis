# 03: Pausar no recarga el catálogo

**What to build:** pausar en el reproductor solo guarda el progreso. Hoy cada pausa recarga todo el catálogo: relee todas las películas, revisa en el disco el póster de cada una (dos accesos por película) y reinicia la grilla, que en ese momento no se ve. En un NTFS montado desde Linux, con cientos de películas, puede dar un tirón. El catálogo se tiene que recargar una sola vez, al volver del reproductor.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Pausar guarda el progreso y no recarga el catálogo.
- [ ] Al salir del reproductor (Esc, botón volver o cerrar la ventana), la **Tarjeta** muestra la barra de progreso actualizada y la película aparece entre las "a medias".
- [ ] El detalle, al volver del reproductor, sigue mostrando el progreso y la hora de fin actualizados.
- [ ] Si era la **Recomendada**, empezarla la sigue cerrando.
