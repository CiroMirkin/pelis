# Sacar las reglas del Catálogo y la Recomendada fuera de Puente

Candidato 2 de `ignore/architecture-review-20261022-235128.html`, acotado en un grilling (2026-10-25).

## Problema
La tarjeta del catálogo se arma en dos lugares (`Catalogo.recargar` y `Puente.peliculasDe`) y el ciclo de la recomendada vive en `Puente`, un QObject sin tests. El filtrado ya tenía tests (`tests/test_catalogo.py`).

## Decisiones
- `src/pelis/catalogo.py`, Python puro: `periodos`, `en_periodo`, `es_incompleta`, `url_poster` (con `pathlib`: `as_uri()` + `?v=mtime_ns`), `tarjeta(fila, biblioteca)` con claves `str` (`peliculaId, titulo, anio, poster, progreso, vista`) y la clase `Recomendacion`.
- `Recomendacion`: `elegir(fila, biblioteca)`, `cerrar()`, `empezo(pelicula_id)`, `poster(url)`, `duracion(pelicula_id, ms)` devuelven `bool` (hubo cambio); `datos` es el dict para QML. Se elige una vez por apertura; con biblioteca vacía (`fila=None`) se reintenta; cerrada no se vuelve a elegir. Puente consulta la base, emite `recomendadaChanged` y mide la duración (QMediaPlayer).
- El modelo Qt pasa a llamarse `ModeloCatalogo`, deriva sus `ROLES` de la tarjeta y guarda `_busqueda` / `_incompleta` aparte. Sus filtros son `@Slot` (`filtrar`, `filtrarVistas`, `filtrarPeriodo`, `filtrarIncompletas`); se borran los pass-through de Puente.
- `peliculasDe` = `{**tarjeta(f, biblioteca), "roles": ...}`.
- `Detalle.qml` mantiene la diferencia pendiente / no encontrada (pendiente se resuelve sola al escanear con internet; no encontrada pide acción), con una tabla de avisos por estado en vez de comparar contra "encontrada".

## Fuera de alcance
- Mensajes de `OSError` al escribir `pelis.json` (candidato 1, Metadatos).
- Slots `normalizar` e `idiomaDe`.
- Comillas alrededor de `biblioteca` en `pelis.toml`.
