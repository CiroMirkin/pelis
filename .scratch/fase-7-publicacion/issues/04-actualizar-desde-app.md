# Actualizar la app al presionar «Actualizar»

Status: ready-for-agent
Blocked by: 02, 03

Ver "Actualizar" en la spec.

- Baja el `.zip` del sistema actual a una carpeta temporal junto a `Pelis/app/` y lo descomprime
- Reemplaza solo la carpeta del programa de ese sistema y su lanzador; nunca toca `pelis.toml`, `pelis.db`, `preferencias.ini` ni la biblioteca
- Escribe un script (`.bat` / `.sh`) que espera a que la app se cierre, cambia las carpetas y la vuelve a abrir; la app guarda el progreso y se cierra
- La carpeta vieja se renombra (`win.anterior` o `linux.anterior`) y se borra recién cuando la nueva arrancó bien

## Criterio de terminado
- [ ] En Windows y en Linux queda la versión nueva funcionando, con base, configuración y progreso intactos
- [ ] Cortar la actualización a la mitad (ej. sin red en la descarga) deja la versión anterior funcionando
