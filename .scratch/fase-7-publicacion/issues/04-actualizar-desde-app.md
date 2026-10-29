# Actualizar la app al presionar «Actualizar»

Status: ready-for-agent
Blocked by: 02, 03

Ver "Actualizar" en la spec.

- Baja el paquete del sistema actual y `SHA256SUMS` a una carpeta temporal junto a `pelis-app/app/`, con barra de progreso y «Cancelar» solo durante la descarga
- Verifica el hash; si no coincide, aborta sin tocar nada
- Avisa «Pelis se va a cerrar y volver a abrir», guarda el progreso y se cierra
- Reemplaza solo la carpeta del programa de ese sistema, su lanzador y `pelis.toml.ejemplo`; nunca `pelis.toml`, `pelis.db`, `preferencias.ini`, la carpeta del otro sistema ni la biblioteca
- Un script (`.bat` / `.sh`) espera a que la app se cierre, renombra la carpeta vieja a `win.anterior` o `linux.anterior`, pone la nueva, deja el testigo `actualizando` y vuelve a abrir la app
- La app nueva borra `*.anterior` y el testigo cuando cargó la interfaz bien; `Pelis.bat` y `pelis.sh` restauran `*.anterior` si encuentran el testigo al abrir

## Criterio de terminado
- [ ] En Windows y en Linux queda la versión nueva funcionando, con base, configuración y progreso intactos
- [ ] Cortar la actualización a la mitad (ej. sin red en la descarga) deja la versión anterior funcionando
- [ ] Un hash que no coincide aborta sin reemplazar nada
- [ ] Una versión nueva que no arranca se restaura sola al volver a abrir con el lanzador
