# Fase 6 — Papelera

Eliminar películas con retención de 7 días.

## Requisito previo: tests
Antes de implementar el movido o borrado real, debe existir un test automatizado que verifique que la operación afecta únicamente la carpeta de la película especificada (por `folder_path`/`id`) y ninguna otra carpeta de la biblioteca ni de la papelera. El test cubre:
- Mover solo la carpeta correcta
- No tocar carpetas hermanas
- No eliminar nada fuera de la carpeta papelera al vencer el plazo de 7 días

## Alcance
- Botón "Eliminar" con confirmación previa
- Al confirmar, la carpeta completa se **mueve** (no se copia) a `<biblioteca>/.papelera/`
- En SQLite: `estado = 'papelera'` y `fecha_papelera` = fecha del movimiento. El registro no se borra todavía
- Al iniciar la app: las carpetas en papelera con `fecha_papelera` de más de 7 días se eliminan del disco, y recién ahí se borra el registro
- El escaneo ignora `.papelera` (y en general cualquier carpeta que empiece con `.`)

## A futuro
- Restaurar: mover la carpeta de vuelta a su `folder_path` original y `estado` vuelve a `'activa'`

## Criterio de terminado
- [ ] Tests en verde antes de cualquier código que mueva o borre
- [ ] Eliminar mueve la carpeta y la oculta del catálogo
- [ ] Simulando 8 días, la carpeta se borra del disco y el registro de la base; nada más cambia
