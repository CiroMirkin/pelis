# 01: Terminar una peli la marca vista y la saca de "a medias"

**What to build:** cuando el video llega al final en el reproductor, la película queda vista y su progreso vuelve a 0. En el catálogo pasa del grupo "a medias" al de vistas, y si se vuelve a abrir arranca desde el principio. Hoy, al terminar, el reproductor queda "detenido" (no "en pausa") con la posición igual a la duración: no se marca vista, y al salir se guarda la posición del final, así que "Continuar" la abre en el final y termina enseguida.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Al llegar al final (fin del medio), la película queda marcada como vista.
- [ ] El progreso guardado queda en 0, también después de salir del reproductor.
- [ ] Si era la **Recomendada**, la recomendación se cierra.
- [ ] Al volver al catálogo, la **Tarjeta** aparece entre las vistas, sin barra de progreso.
- [ ] Salir o pausar antes del final sigue guardando la posición como hasta ahora.
