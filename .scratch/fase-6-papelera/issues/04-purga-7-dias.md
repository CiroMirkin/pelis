# Purgar la papelera al iniciar la app

Status: ready-for-agent
Blocked by: 01, 03

Al iniciar, las carpetas en papelera con `fecha_papelera` de más de 7 días se borran del disco y recién ahí se borra su registro (y sus filas en `posters` y `pelicula_personas`).

## Criterio de terminado
- [ ] Simulando 8 días, la carpeta se borra del disco y el registro de la base; nada más cambia
