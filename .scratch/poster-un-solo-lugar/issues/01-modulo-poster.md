# poster.py con revisar y rotar

Status: ready-for-agent

## Qué
- `src/pelis/poster.py` con `revisar` y `rotar` (ver spec), movidos desde `escaneo.actualizar_poster` y `escaneo.rotar_posters` junto con el set (`posters_de`, `carpeta_posters`, constantes)
- El SQL de escritura de `posters` sale de `db.py` y queda privado en `poster.py`; las consultas de listado con `JOIN posters` y `db.reasignar` se quedan
- Se saca el origen `manual` de la regla de `revisar`
- `revisar` y `rotar` hacen su commit; se va el de `puente.py:287`
- Escaneo, edición (fusión) y Puente llaman a `poster.revisar`/`poster.rotar`. Mientras no esté la 02, `edicion` y `Escaneo._bajar_poster` pueden usar helpers internos de `poster.py`
- `tests/test_poster.py` con los tests de póster y rotación de `test_escaneo.py`, contra `poster.*`

## Criterio de terminado
- [ ] Sin cambios de comportamiento: la suite pasa
- [ ] `db.py` no tiene funciones de escritura de `posters`
- [ ] Nada fuera de `poster.py` menciona el origen `manual` de un póster
- [ ] Los tests de reglas del póster están en `test_poster.py`
