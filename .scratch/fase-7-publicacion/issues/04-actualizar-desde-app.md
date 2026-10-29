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
- [x] Cortar la actualización a la mitad (ej. sin red en la descarga) deja la versión anterior funcionando
- [x] Un hash que no coincide aborta sin reemplazar nada
- [ ] Una versión nueva que no arranca se restaura sola al volver a abrir con el lanzador

## Comments

- 29/10/2026: descarga, verificación, script y vuelta atrás en `actualizacion.py`; botón, progreso y «Cancelar» en `DialogoActualizacion.qml`; limpieza al arrancar en `__main__.py`; restauración en `Pelis.bat` y `pelis.sh`. Testigo y carpeta de descarga llevan el nombre del sistema (`actualizando-linux`, `actualizacion-win`) porque `app/` es compartida.
- Linux probado de punta a punta con el build real, contra una Release falsa servida en local: bajó y verificó el `.tar.gz`, cerró, el script cambió `linux/`, abrió el binario nuevo y este borró `linux.anterior` y el testigo; `pelis.toml` y `pelis.db` intactos. Los tests corren el script y el lanzador de Linux de verdad (cambio, argumentos, vuelta atrás).
- Windows: el `.bat` solo está probado como texto. Falta correrlo de verdad: se prueba con la primera RC (issue 06). Queda abierto el primer criterio para Windows.
