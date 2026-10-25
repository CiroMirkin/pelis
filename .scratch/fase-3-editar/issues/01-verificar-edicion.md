# Verificar la edición en la app con la biblioteca real

Status: ready-for-human

Todo está cubierto por `tests/test_edicion.py`; falta probarlo en la app.

## Criterio de terminado
- [ ] Una película "no encontrada" se completa a mano y queda con `metadatos_origen = 'manual'`
- [ ] Corregir match reemplaza metadatos y personas
- [ ] Renombrar una carpeta con match y re-escanear la reasigna sola, conservando progreso y vista
- [ ] La reasignación manual funciona para un registro sin `omdb_id`
