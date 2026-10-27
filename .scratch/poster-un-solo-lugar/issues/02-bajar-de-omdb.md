# destino_omdb y registrar_omdb: una sola regla de descarga

Status: ready-for-agent

Blocked by: 01

## Qué
- `poster.destino_omdb(conn, biblioteca, pelicula_id, reemplazar=False)` y `poster.registrar_omdb(conn, biblioteca, pelicula_id)` (ver spec); `registrar_omdb` hace su commit
- `Escaneo._bajar_poster` usa `destino_omdb(..., reemplazar=False)` + `omdb.bajar_poster` + `registrar_omdb`
- Corregir match usa `destino_omdb(..., reemplazar=True)`; se borran `edicion.destino_poster`, `edicion.bajar_poster` y el bloque de `aplicar_omdb` que registra el bajado (y su `conn.commit()`)
- `"poster.jpg"` y el origen `"omdb"` como literales solo en `poster.py`

## Criterio de terminado
- [ ] El escaneo no baja si hay un póster `existente` ni si ya hay uno de OMDb
- [ ] Corregir match pisa el de OMDb y no toca uno `existente`
- [ ] La bajada de la edición sigue corriendo fuera del hilo de la UI
- [ ] `grep '"poster.jpg"'` en `src/` solo encuentra `poster.py`
