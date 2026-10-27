# Edición manual, corregir match y fusión por metadatos.aplicar

Status: done
Blocked by: 01

## Qué
- `edicion.aplicar_omdb`, `guardar_manual` y `fusionar` guardan con `aplicar(..., explicita=True)`. Corregir match arma el dict con el título actual y el año de OMDb (o el actual si OMDb no trae)
- Se borran `edicion._escribir_archivo`, `edicion._archivo_actual` y `db.guardar_metadatos` (el "no encontrada" del escaneo pasa a una función propia de `db`); `db.fijar_anio` deja de usarse desde `edicion`
- `Puente` muestra el aviso que devuelve `aplicar` en edición manual y corregir match

## Criterio de terminado
- [x] Tests existentes de `test_edicion.py` pasan
- [x] Con la carpeta de solo lectura, la edición queda guardada y la app muestra el aviso
