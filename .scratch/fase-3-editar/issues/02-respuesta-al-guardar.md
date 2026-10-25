# Guardar la edición: bloqueo, Ctrl+S y «Buscar» vs «Volver a traer»

Status: done

Pedido del usuario (2026-10-25), para hacer después.

## Qué
- Al presionar «Guardar», el botón queda bloqueado hasta que termina el guardado (no se puede guardar dos veces)
- Si el guardado sale bien, se vuelve al detalle de la película. Ya pasa (`Editar.qml:31-35`: `pop()` + aviso «Datos guardados"); verificar que siga así
- Si falla, el botón se desbloquea y se muestra el error (`errorGuardar`)

## Bug: Ctrl+S guarda sin cambios
El `Shortcut` de `StandardKey.Save` (`Editar.qml:87-91`) solo mira que la página esté activa: no respeta `pagina.modificado` (que es lo que habilita el botón) ni que el popup de confirmación esté abierto. Con el formulario sin tocar, Ctrl+S llama a `guardar_manual`, que deja `metadatos_origen = 'manual'` y reescribe `pelis.json`. Desde ahí, «Volver a traer» y elegir otro candidato piden confirmación por «datos editados a mano» que nadie editó.
- Fix: `enabled: pagina.StackView.status === StackView.Active && guardar.enabled && !confirmar.opened`

## «Buscar» y «Volver a traer» no se distinguen
Hoy son dos botones iguales, uno al lado del otro y pegados al campo (`Editar.qml:178-189`), pero hacen cosas distintas:
- «Buscar» usa lo que está escrito en el campo (título → candidatos; ID o link → esa película)
- «Volver a traer» ignora el campo y vuelve a bajar los datos del IMDb ID actual (resincronizar)

Propuesta: sacar «Volver a traer» de la fila del campo y ponerlo junto a la línea «Ahora: tt…», con el ID en el texto («Volver a traer tt0078748») y una nota que diga que reemplaza los datos por los actuales de IMDb. La fila del campo queda solo con «Buscar».

## Criterio de terminado
- [x] Guardar deshabilitado mientras guarda; con éxito vuelve al detalle; con error se rehabilita y muestra el mensaje
- [x] Ctrl+S sin cambios no hace nada (el origen sigue siendo `omdb`)
- [x] Ctrl+S con el popup de confirmación abierto no guarda
- [x] «Volver a traer» está separado de la búsqueda y dice qué ID va a traer

## Comments

2026-10-25: implementado en `Editar.qml`. Probado offscreen sobre una copia de la biblioteca: Ctrl+S sin cambios no toca la base (origen sigue `omdb`); con cambios guarda como `manual` y vuelve al detalle. Pendiente a mano: Ctrl+S con el popup abierto y mirar el layout nuevo de «Volver a traer».

2026-10-25: probado offscreen sobre una copia de la base. Con el popup de confirmación abierto, Ctrl+S no guarda (origen sigue `omdb`); al cerrarlo, Ctrl+S guarda como `manual` y vuelve. El layout de «Volver a traer» quedó separado de la búsqueda, junto a «Ahora: tt…».
