# 01: Un solo flujo para cambiar de póster

**What to build:** la rotación de pósters y el pase a la portada siguiente con click derecho usan un solo flujo y solo se diferencian en cómo eligen la imagen. Desaparece el manejo del origen que hoy no tiene efecto en ese flujo: las imágenes que se registran ahí nunca son nuevas de OMDb, y la elegida ya está registrada cuando se aplica. Para el usuario no cambia nada.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] La rotación y la portada siguiente comparten el flujo de registrar las imágenes y aplicar la elegida
- [x] Una película con menos de dos pósters no cambia en ninguno de los dos casos
- [x] La rotación sigue eligiendo al azar un póster distinto del actual
- [x] La portada siguiente sigue el orden de preferencia, vuelve al primero después del último y arranca por el primero si el actual no está en el set
- [x] Revisar la carpeta no deshace el cambio, aunque el póster elegido sea el bajado de OMDb
- [x] Un póster bajado de OMDb conserva su origen después de rotar o pasar a la portada siguiente
- [x] Los tests de pósters pasan sin cambiar lo que verifican
