# Eliminar una película: mover su carpeta a la papelera

Status: ready-for-agent
Blocked by: 01, 02

- Botón "Eliminar" en el detalle (menú «…»), con confirmación
- Al confirmar, la carpeta completa se mueve (no se copia) a `<biblioteca>/.papelera/`
- En la base: `estado = 'papelera'` y `fecha_papelera` = fecha del movimiento; el registro no se borra

## Criterio de terminado
- [ ] Los tests del ticket 01 pasan
- [ ] Eliminar mueve la carpeta y la oculta del catálogo
