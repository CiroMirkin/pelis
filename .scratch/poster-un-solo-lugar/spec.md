# Política del póster en un solo lugar

Candidato 3 de `ignore/architecture-review-20261022-235128.html`, acotado en un grilling (2026-10-27).

## Problema
Para saber qué póster se muestra hay que leer seis lugares:
- `db.py:182-231`: 8 funciones superficiales sobre la tabla `posters`.
- `escaneo.py`: el set (`posters_de`, `carpeta_posters`), `actualizar_poster`, `rotar_posters` y `Escaneo._bajar_poster`.
- `edicion.py`: `destino_poster`, `bajar_poster` y el bloque de `aplicar_omdb` que registra el bajado.
- `puente.py`: llama a `actualizar_poster` y hace el commit (`:287`), y llama a `rotar_posters`.

Los literales `"poster.jpg"` y `"omdb"` se repiten en tres módulos. Hay dos reglas distintas para bajar de OMDb: el escaneo baja solo si no hay ningún póster (`db.tiene_poster`), y la edición baja si no hay uno propio y pisa el de OMDb. `actualizar_poster` protege el origen `manual`, pero nada lo escribe (la galería de la fase 5 quedó en `wontfix`).

## Decisiones
- **`src/pelis/poster.py`** es la única política del póster. Interfaz pública:
  - `revisar(conn, biblioteca, pelicula_id) → bool`: el `actualizar_poster` de hoy. Mira la carpeta y cambia el póster actual si hace falta.
  - `rotar(conn, biblioteca, ahora="now", azar=random, dias=7) → int`: cuántas rotaron.
  - `destino_omdb(conn, biblioteca, pelicula_id, reemplazar=False) → Path | None`: dónde bajar el póster de OMDb, o `None` si no hay que bajar.
  - `registrar_omdb(conn, biblioteca, pelicula_id)`: después de bajarlo, lo deja como póster actual.
- **Privado**: el set de pósters (`posters_de`, `carpeta_posters`, `EXTENSIONES_POSTER`, `PALABRAS_POSTER`), el nombre `posters/poster.jpg` y el SQL de escritura de `posters` (lo que hoy es `db.tiene_poster`, `agregar_poster`, `poster_actual`, `posters_registrados`, `registrar_poster`, `sin_poster`, `posters_vencidos`, `posters_bajados`, `usar_poster`).
- **El módulo no usa la red.** Quien llama baja con `omdb.bajar_poster(url, destino)` entre `destino_omdb` y `registrar_omdb`; así la edición sigue bajando fuera del hilo de la UI y registrando en él.
- **Una sola regla de descarga**: se baja si el póster actual no es `existente`. Con `reemplazar=False` (escaneo) tampoco se baja si ya hay uno de OMDb; con `reemplazar=True` (corregir match) se pisa.
- **Commit adentro**: toda función de `poster.py` que escribe hace su commit, como `metadatos.aplicar`. Se van los `conn.commit()` de `puente.py:287` y de `edicion.py:80`.
- **Orígenes**: solo `existente` y `omdb`. Se saca `manual`; la tabla no tiene `CHECK` y nunca se escribió, así que no hay migración.

## Queda donde está
- `catalogo.url_poster` (cache-busting `?v=`): es presentación.
- Las consultas de listado y detalle con `JOIN posters` en `db.py`, y `db.reasignar`/fusión, que mueven filas de `posters` como parte de la reasignación.

## Tests
Los tests de reglas del póster y de rotación pasan a `tests/test_poster.py` y llaman a `poster.*`. En `test_escaneo` y `test_edicion` queda solo la integración: el escaneo baja el póster, corregir match lo reemplaza, un póster propio no se pisa.

## Fuera de alcance
- Galería y "Sumar poster" (fase 5, `wontfix`).
- Seam de clientes de red (candidato 4) y reconocedor de IMDb ID (candidato 5).
- Glosario: no se agregan términos.
