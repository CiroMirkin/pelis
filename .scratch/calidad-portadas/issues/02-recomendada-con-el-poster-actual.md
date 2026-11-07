# 02: La recomendada siempre muestra el póster actual

**What to build:** si el póster de la Recomendada cambia, la franja lo refleja al volver al catálogo, en vez de quedarse con una imagen vieja o rota. Hoy pasa cuando abrir el detalle encuentra un póster distinto en la carpeta y cuando se aplican datos traídos de IMDb con un póster bajado. Todo cambio de póster usa una sola operación para actualizar el catálogo y la Recomendada, así un caso nuevo no puede actualizar solo uno de los dos.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Abrir el detalle de la Recomendada con una imagen nueva en su carpeta actualiza el póster de la franja
- [x] Abrir el detalle de la Recomendada después de borrar su póster actualiza la franja y no deja una imagen rota
- [x] Aplicar datos de IMDb con un póster bajado a la Recomendada actualiza el póster de la franja
- [x] Un cambio de póster en otra película no altera la Recomendada
- [x] Renovar las portadas, pasar a la portada siguiente y terminar un escaneo siguen actualizando el catálogo y la Recomendada
- [x] Hay tests de regresión para el caso de abrir el detalle y el de aplicar datos de IMDb
