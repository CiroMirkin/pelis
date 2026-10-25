# Fase 7 — Publicación y actualizaciones

Publicar los builds de Windows y Linux en GitHub y que la app se actualice sola, pero solo cuando el usuario lo pide.

Pedido del usuario (22/10/2026).

## Alcance

### Workflow de publicación en GitHub
- GitHub Actions con dos jobs, uno por sistema: `windows-latest` corre `tools/build_win.bat` y `ubuntu-latest` corre `tools/build_linux.sh`. Los dos usan el mismo `pelis.spec`.
- Se dispara al subir un tag de versión (`v0.2.0`); la versión sale de `pyproject.toml` y el tag tiene que coincidir.
- Antes de armar, corre los tests (`pytest`) en los dos sistemas; si fallan, no se publica.
- Cada job sube un `.zip` con lo que va en la raíz del disco (`Pelis-windows-v0.2.0.zip`, `Pelis-linux-v0.2.0.zip`) a una Release de GitHub con ese tag.
- Linux: el job instala `libxcb-cursor0` antes de armar, para que PyInstaller lo incluya.

### Buscar actualización
- Opción «Buscar actualización» en el menú «…» del catálogo. **No hay búsqueda automática** al abrir la app.
- Consulta `https://api.github.com/repos/<usuario>/<repo>/releases/latest` en un hilo aparte y compara su tag con la versión de la app.
- Muestra el resultado: «Estás al día (v0.2.0)» o «Hay una versión nueva: v0.3.0», con las notas de la Release y un botón «Actualizar».
- Sin internet o con GitHub caído: un mensaje claro, sin romper nada.

### Actualizar (al presionar el botón)
- Baja el `.zip` del sistema actual a una carpeta temporal junto a `Pelis/app/` y lo descomprime.
- Solo reemplaza la carpeta del programa de ese sistema (`Pelis/app/win/` o `Pelis/app/linux/`, las mismas que arman `build_win.bat` y `build_linux.sh`) y el lanzador. **Nunca toca** `pelis.toml`, `pelis.db`, `preferencias.ini` ni la biblioteca.
- Un ejecutable no puede reemplazarse a sí mismo mientras corre (en Windows directamente no se puede): la app escribe un script chico (`.bat` en Windows, `.sh` en Linux) que espera a que la app se cierre, cambia la carpeta vieja por la nueva y vuelve a abrir la app. La app se cierra sola después de lanzarlo, guardando el progreso como al cerrar.
- Si algo falla a mitad de camino, queda la versión anterior: la carpeta vieja se renombra (`win.anterior` o `linux.anterior`) y se borra recién cuando la nueva arrancó bien.
- Desde el código (`dev.sh`, sin build) la opción se muestra deshabilitada: no hay nada que reemplazar.

## Decisiones abiertas
- Nombre del repositorio y si es público o privado. Privado obliga a un token para leer las Releases, que habría que guardar en `pelis.toml`.
- El proyecto todavía no es un repositorio git: hay que crearlo y definir qué queda afuera (`dev/`, `Peliculas/`, `.venv*/`, `build/`, `dist/`).
- Esquema de versiones (semver) y quién sube el número en `pyproject.toml`.
- Windows marca los `.exe` sin firma con SmartScreen la primera vez; firmar el ejecutable tiene costo.

## Criterio de terminado
- [ ] Subir un tag publica una Release con los zips de Windows y Linux, armados en GitHub, con los tests pasando
- [ ] «Buscar actualización» informa bien los tres casos: al día, hay versión nueva y sin conexión
- [ ] «Actualizar» en Windows y en Linux deja la versión nueva funcionando, con la base, la configuración y el progreso intactos
- [ ] Cortar la actualización a la mitad (por ejemplo, sin red durante la descarga) deja la versión anterior funcionando
