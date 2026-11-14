# 02: Tests de discos sin tocar estado privado del puente

**What to build:** que `tests/test_discos.py` pruebe los discos por la interfaz pública del puente y no por sus atributos privados, para que se pueda refactorizar el puente sin romper los tests. Hoy los tests llaman a `puente._sondear()`, leen `catalogo._filas` y tocan `puente._discos`. Renombrar `_sondear` deja 18 de 21 tests en rojo y renombrar `_filas` deja 12 en rojo (auditoría de tests, hallazgo T11).

**Blocked by:** None (can start immediately).

**Status:** needs-triage

## Decisión pendiente

Hay que decidir la interfaz pública antes de tocar los tests, porque cambia código de producción. Propuesta de partida:

- Un slot `sondearDiscos()` en `Puente` que haga lo que hoy hace `_sondear`, para que los tests no llamen a un método privado.
- Leer el modelo con `data()` y `rowCount()` (o un helper de test que los use) en vez de `catalogo._filas`.
- Una forma pública de cerrar los discos (hoy `puente._discos.cerrar()`) y de saber qué mide el puente (hoy `puente._midiendo`).

## Dónde

- Los usos están en `tests/test_discos.py`: unos 27 llamados a `_sondear()`, 4 lecturas de `_filas`, y accesos a `puente._discos` y `puente._midiendo`. Los tests agregados después de la auditoría también los usan.
- Los slots a exponer están en `src/pelis/puente.py` (sección «discos externos»).

## Criterio de hecho

- [ ] Ningún test de `tests/test_discos.py` empieza con `_` en un atributo del puente o del modelo.
- [ ] Renombrar los métodos internos de sondeo y de filas del catálogo deja los tests en verde.
- [ ] Los mutantes de la auditoría siguen muriendo (guardas de solo lectura, orden, sondeo a los 10 segundos, esquema roto).
