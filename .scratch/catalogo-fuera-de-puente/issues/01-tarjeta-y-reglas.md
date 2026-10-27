# catalogo.py con la tarjeta y las reglas del catálogo

Status: done

## Qué
- Mover `periodos`, `en_periodo` y `url_poster` (pasado a `pathlib`) a `src/pelis/catalogo.py`; agregar `es_incompleta` y `tarjeta`
- `Catalogo.recargar` y `Puente.peliculasDe` usan `tarjeta`

## Criterio de terminado
- [ ] Tests de `tarjeta`: progreso con duración 0, sin progreso y a la mitad; póster con espacios y "ñ"
- [ ] Tests de `es_incompleta`: sin datos, sin póster, póster borrado del disco
- [ ] Test de `peliculasDe`: tarjeta + roles
