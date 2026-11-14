# Editar.qml pregunta a Python si el texto es un IMDb ID

Status: ready-for-agent

Blocked by: 01

## Qué
- Slot `Puente.imdbIdDe(texto) → str` (`""` si no hay ID) sobre `nombres.imdb_id`
- `Editar.qml:buscar` lo usa en lugar de la regex

## Criterio de terminado
- [ ] Test del slot: ID suelto, link y texto sin ID
- [ ] En la app, pegar un link de IMDb reemplaza los datos y un título lista candidatos
- [ ] No queda ninguna regex de `tt\d` en `src/pelis/qml/`
