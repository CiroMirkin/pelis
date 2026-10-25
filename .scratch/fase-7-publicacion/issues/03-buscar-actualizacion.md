# «Buscar actualización» en el menú del catálogo

Status: ready-for-agent
Blocked by: 01

- Opción en el menú «…» del catálogo; nunca se busca sola al abrir
- Consulta `releases/latest` de la API de GitHub en un hilo aparte y compara el tag con la versión de la app
- Muestra «Estás al día (vX)» o «Hay una versión nueva: vY» con las notas de la Release y un botón «Actualizar»
- Sin internet o con GitHub caído: mensaje claro, sin romper nada
- Corriendo desde el código (`dev.sh`), la opción aparece deshabilitada

## Criterio de terminado
- [ ] Informa bien los tres casos: al día, versión nueva y sin conexión
- [ ] Test de la comparación de versiones y de la respuesta de la API sin UI
