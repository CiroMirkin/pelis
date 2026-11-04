# Recomendar a pedido

Status: ready-for-agent

Acotada en un grilling (2026-11-03).

## Idea
La **Recomendada** deja de aparecer sola al abrir la app. El catálogo ofrece un botón «Recomendar»: al tocarlo se muestra la recomendación y el botón desaparece hasta la próxima apertura.

## Decisiones

### Botón
- **Lugar**: en la barra del catálogo, a la derecha del selector de época. Si Época no se muestra (un solo período), queda a la derecha de «Todas / Sin ver / Vistas».
- **Aspecto**: `Boton` secundario, con contorno crema y el texto «Recomendar» (se ve en mayúsculas), sin ícono. Sin rojo: no compite con la acción principal.
- **Búsqueda y filtros**: se oculta con búsqueda o con los filtros de vistas, época e incompletas, igual que la franja. Por eso nunca convive con el chip «Sin datos o portada».
- **Sin candidatas**: si no hay ninguna película activa, sin ver y sin empezar, se oculta. Reaparece si un escaneo trae candidatas.
- **Foco**: al activarlo, el foco pasa a la grilla. No va a la ✕ de la franja porque un Enter de más la descartaría y gastaría la recomendación de esa apertura.

### Elección
- **Momento**: al hacer click. Al abrir la app no se hace ningún trabajo para la recomendación.
- **Criterio**: sin cambios (`db.recomendada`): al azar entre las activas, sin ver y sin empezar.
- **Duración**: si a la película le falta, se mide al elegirla.
- **Se quitan**: la elección al arrancar (`puente.py:237`) y el reintento al terminar cada escaneo (`puente.py:623`).

### Franja
- **Sin cambios**: póster, título, año, género, duración y ✕; un toque abre el detalle.
- **Rótulo**: «Recomendación» en lugar de «Recomendación del día».
- **Filtros**: una franja ya pedida se oculta con búsqueda o filtros y vuelve a verse al quitarlos, como hoy.

### Una por apertura
- **Consumo**: el botón se gasta solo al tocarlo. Después no vuelve hasta reabrir la app, aunque la franja se cierre con ✕, se empiece la película o se marque vista. No hay un «otra» para pedir una distinta.
- **«Marcar todas como vistas»**: no consume un botón sin usar (hoy llama a `cerrarRecomendacion`, `puente.py:353`). Si después un escaneo trae películas nuevas, el botón reaparece. Si la franja estaba a la vista, se cierra como hoy.
- **Estado**: vive solo en memoria, en `Recomendacion`; no se guarda en la base. Cualquier reinicio lo restablece, incluido el de una actualización. Entrar al detalle y volver no.

## Alcance

### Código
- `catalogo.py`: `Recomendacion` distingue «sin usar» de «ya usada».
- `puente.py`: un slot nuevo elige la película y una propiedad nueva indica si el botón se puede mostrar; se recalcula cuando cambian las candidatas.
- `Catalogo.qml`: el botón y el rótulo nuevo.

### Tests
- `tests/test_catalogo.py`: ajustar a la nueva lógica, incluido el caso de marcar todas sin haber usado el botón.

### Docs
- `GLOSSARY.md`, `docs/casos-de-uso.md`, `README.md` y `DESIGN.md` describen hoy el comportamiento automático y el nombre «Recomendación del día».
