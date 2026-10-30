# 01: Terminar una peli la marca vista y la saca de "a medias"

**What to build:** cuando el video llega al final en el reproductor, la película queda vista y su progreso vuelve a 0. En el catálogo pasa del grupo "a medias" al de vistas, y si se vuelve a abrir arranca desde el principio. Hoy, al terminar, el reproductor queda "detenido" (no "en pausa") con la posición igual a la duración: no se marca vista, y al salir se guarda la posición del final, así que "Continuar" la abre en el final y termina enseguida.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Al llegar al final (fin del medio), la película queda marcada como vista.
- [x] El progreso guardado queda en 0, también después de salir del reproductor.
- [x] Si era la **Recomendada**, la recomendación se cierra.
- [x] Al volver al catálogo, la **Tarjeta** aparece entre las vistas, sin barra de progreso.
- [x] Salir o pausar antes del final sigue guardando la posición como hasta ahora.

## Comments

- 29/10/2026: `Reproductor.qml` llama a `puente.terminar` al llegar a `EndOfMedia`, que guarda progreso 0 y marca vista (eso también cierra la **Recomendada**). Una marca `terminada` evita que salir guarde la posición del final; se borra si se vuelve a reproducir. Comprobado con un clip de 2 s que el `MediaPlayer` de este Qt emite `EndOfMedia` con la posición igual a la duración. Se prueba en la app con `v0.3.0-rc2`.
