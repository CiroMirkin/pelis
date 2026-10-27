# metadatos.aplicar y el escaneo como primer llamador

Status: done

## Qué
- Columnas `sinopsis_idioma` y `poster_url` en `peliculas` (migración con `ALTER TABLE ADD COLUMN` si faltan)
- `src/pelis/metadatos.py` con `aplicar(conn, biblioteca, pelicula_id, metadatos, explicita)` (ver spec): guarda, `commit`, escribe `pelis.json` desde la base; un `OSError` vuelve como aviso; un archivo inválido no se pisa
- El escaneo usa `aplicar`: match automático con `explicita=False`, importar `pelis.json` completo con `explicita=True`. Se borra `escaneo._guardar`; la bajada del póster queda como paso propio del escaneo
- El aviso de escritura va al `Informe`

## Criterio de terminado
- [x] Tras un escaneo con OMDb, `pelis.json` es igual a la base: título y año de la carpeta
- [x] Un año corregido a mano sobrevive a una base nueva aunque la carpeta tenga otro año en el nombre
- [x] Un `pelis.json` inválido no se pisa
- [x] Si escribir falla, la base queda guardada y vuelve un aviso
