# Fase 5 — Posters

Varios posters por película y rotación automática.

## Alcance

### Galería por película
- Muestra todos los posters asociados (`posters`)
- Fijar uno manualmente (actualiza `poster_actual_id` y resetea `poster_actualizado_en`)
- Eliminar alguno del set

### Sumar poster
- Botón "Sumar poster": abre el selector de archivos nativo del sistema, copia la imagen a la carpeta de la película con numeración automática (`poster_1.jpg`, `poster_2.jpg`, …) e inserta el registro con `origen = 'manual'`

### Rotación automática
- Cada 7 días, si `poster_actualizado_en` venció, se rota a un poster aleatorio del set (distinto al actual si hay más de uno) y se actualizan `poster_actual_id` + `poster_actualizado_en`
- Se evalúa al iniciar la app

## Decisiones abiertas para esta fase
- Si "eliminar poster" borra el archivo del disco o solo el registro (sobre todo para posters `existente` como `folder.jpg`, que también usa el Explorador de Windows)
- Qué pasa al eliminar el poster actual

## Hecho (22/10/2026): solo la rotación
Decisiones del usuario: el set es **toda imagen de la carpeta** (`.jpg`, `.jpeg`, `.png`, cualquier nombre), no hay galería ni «Sumar poster», y la app no quita ni borra posters: para sacar uno de la rotación se borra el archivo a mano.
- `rotar_posters` corre al abrir la app, en el hilo de la importación sin red. Rota las activas con `poster_actualizado_en` de 7 días o más; elige al azar una imagen distinta de la actual. Con una sola imagen no cambia nada.
- Antes de elegir, registra todas las imágenes en `posters`. `actualizar_poster` ahora respeta el poster actual mientras su archivo exista, y solo una imagen **no registrada** desplaza al bajado de OMDb; así abrir el detalle o escanear no deshace la rotación.
- Las URLs de los posters llevan la fecha del archivo (`?v=`), para que Qt no muestre uno viejo de caché.

## Cambio (25/10/2026): carpeta `posters`
El set de la rotación deja de ser «toda imagen de la carpeta»: ahora son los posters de la regla 4 de [biblioteca-multimedia](../biblioteca-multimedia/spec.md) (toda imagen de `posters\` más las sueltas con `poster`/`folder`/`cover`). `backdrop`, `fanart`, etc. ya no rotan. La migración es solo de código: las sueltas viejas siguen contando y la app no mueve archivos. El poster de OMDb se baja a `posters\poster.jpg`.

## Cambio (27/10/2026): política en `poster.py`
La rotación pasa a `poster.rotar` y la revisión de la carpeta a `poster.revisar`; se saca el origen `manual`, que nada escribía. Ver [poster-un-solo-lugar](../poster-un-solo-lugar/spec.md).

## Criterio de terminado
- [ ] Sumar 2 posters a una película, fijar uno, y verlo en el catálogo
- [x] Simulando el vencimiento de 7 días, el poster rota a otro distinto (`test_rotacion_*`)
