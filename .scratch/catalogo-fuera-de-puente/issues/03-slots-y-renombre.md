# Filtros como slots del modelo y renombre a ModeloCatalogo

Status: done
Blocked by: 01

## Qué
- `Catalogo` → `ModeloCatalogo`; sus filtros pasan a `@Slot` con nombres camelCase
- Borrar `filtrar`, `filtrarVistas`, `filtrarPeriodo`, `filtrarIncompletas` de Puente; `Catalogo.qml` llama a `puente.catalogo.*`

## Criterio de terminado
- [ ] Tests existentes pasan con los nombres nuevos
- [ ] Buscar, vistas, época e incompletas funcionan en la app
