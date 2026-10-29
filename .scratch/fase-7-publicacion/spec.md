# Fase 7 — Publicación y actualizaciones

Publicar los builds de Windows y Linux en GitHub y que la app se actualice sola, pero solo cuando el usuario lo pide.

Pedido del usuario (22/10/2026). Decisiones abiertas cerradas en un grilling (29/10/2026).

## Alcance

### Repositorio y versión
- `CiroMirkin/pelis` en GitHub, **público**: las Releases se leen sin token. Antes del primer push se revisa que el historial no tenga claves de OMDb ni TMDb.
- La versión vive en un solo lugar: `__version__` en `src/pelis/__init__.py`. `pyproject.toml` la toma de ahí (versión dinámica). Semver: patch para arreglos, minor para features, major para cambios que rompen.
- Pre-releases con sufijo `-rcN` (`0.2.0-rc1`). Una RC es menor que su versión final.
- La primera Release es `v0.2.0`, que ya trae el actualizador.
- El `.exe` no se firma: se acepta el aviso de SmartScreen.

### Comando de versión
- `tools/version.py patch|minor|major|final [--rc]`, con el Python del venv del sistema donde se corre (Windows o Mint). La skill de proyecto `/version` (`.claude/skills/version/`) lo corre, muestra las notas y, si se le pide, las reescribe en lenguaje de usuario antes de confirmar.
- Se niega si hay cambios sin commitear o si no está en `main`.
- Al empezar hace `git pull --ff-only`: si `main` estaba atrás la pone al día; si divergió de `origin/main`, se niega sin tocar nada. Nunca hace merge ni rebase.
- No corre los tests: los corre el workflow.
- Sube `__version__`, arma las notas, commitea `chore: versión vX.Y.Z` y crea el tag anotado `vX.Y.Z` con las notas como mensaje.
- **Notas**: los commits `feat` y `fix` desde la última versión final, agrupados en «Nuevo» y «Arreglos». Se muestran antes de confirmar, con la opción de editarlas en `$EDITOR` (o el Bloc de notas en Windows).
- Muestra un resumen (versión vieja → nueva, notas) y pide confirmación `s/N`. Justo antes del push hace otro `git pull --ff-only`: si trae algo, aborta y pide correrlo de nuevo, porque las notas quedarían incompletas. Después pushea el commit y el tag.
- Con `N`, el commit y el tag quedan locales y el comando dice cómo pushearlos o deshacerlos.
- **RC**: `minor --rc` (o `patch`/`major`) da `X.Y.Z-rc1`; `--rc` sin nivel da la siguiente RC de la misma versión; `final` saca el sufijo. Con una RC abierta, `patch`/`minor`/`major` sin `--rc` se niegan: primero se cierra con `final`. Las notas de una RC y de su final cubren desde la última versión final.

### Workflow de publicación en GitHub
- GitHub Actions con un job por sistema: `windows-latest` corre `tools/build_win.bat` y `ubuntu-24.04` (la base de Mint 22.3, fijada) corre `tools/build_linux.sh`. Los dos usan el mismo `pelis.spec`.
- Se dispara al pushear un tag `v*`, que publica la Release, o a mano (`workflow_dispatch`), que solo sube los paquetes como artifacts del run. Con tag, falla si no coincide con `__version__`.
- Antes de armar corre los tests (`pytest`) en los dos sistemas; si fallan, no se publica.
- Linux: el job instala `libxcb-cursor0` antes de armar, para que PyInstaller lo incluya.
- Paquetes, con lo que va en la raíz del disco: `Pelis-windows-vX.Y.Z.zip` y `Pelis-linux-vX.Y.Z.tar.gz` (el tar conserva los permisos de ejecución). Se publican junto con un `SHA256SUMS` de los dos.
- El texto de la Release es el mensaje del tag anotado. Un tag con `-rc` se publica como pre-release.

### Buscar actualización
- Opción «Buscar actualización» en el menú «…» del catálogo. **No hay búsqueda automática** al abrir la app.
- Consulta `https://api.github.com/repos/CiroMirkin/pelis/releases/latest` en un hilo aparte y compara su tag con la versión de la app. Con `--prerelease` al arrancar, mira todas las Releases (`/releases`) y toma la más nueva, RC incluidas.
- Muestra el resultado en un popup sobre el catálogo: «Estás al día (v0.2.0)» o «Hay una versión nueva: v0.3.0», con las notas de la Release y un botón «Actualizar». El popup recuerda que en el otro sistema hay que actualizar aparte.
- Sin internet o con GitHub caído: un mensaje claro, sin romper nada.
- Desde el código (`dev.sh`, `dev.bat`, sin build) la opción se muestra deshabilitada: no hay nada que reemplazar.

### Actualizar (al presionar el botón)
- Baja el paquete del sistema actual y el `SHA256SUMS` a una carpeta temporal junto a `pelis-app/app/`. Muestra una barra de progreso con porcentaje y deja «Cancelar» solo mientras descarga.
- Verifica el hash. Si no coincide, aborta y deja todo como estaba.
- Avisa «Pelis se va a cerrar y volver a abrir» y lo hace solo, guardando el progreso como al cerrar.
- Reemplaza la carpeta del programa de ese sistema (`pelis-app/app/win/` o `pelis-app/app/linux/`, las mismas que arman `build_win.bat` y `build_linux.sh`), su lanzador (`Pelis.bat` o `pelis.sh`) y `pelis.toml.ejemplo`. **Nunca toca** `pelis.toml`, `pelis.db`, `preferencias.ini`, la carpeta del otro sistema ni la biblioteca.
- Cada sistema actualiza solo su carpeta. Que Windows y Linux queden en versiones distintas del mismo disco no rompe la base: las migraciones solo agregan columnas.
- Un ejecutable no puede reemplazarse a sí mismo mientras corre (en Windows directamente no se puede). La app escribe un script chico (`.bat` en Windows, `.sh` en Linux) que espera a que la app se cierre, renombra la carpeta vieja a `win.anterior` o `linux.anterior`, pone la nueva, deja el testigo `actualizando` y vuelve a abrir la app.
- **Volver atrás**: la app nueva borra `*.anterior` y el testigo recién cuando cargó la interfaz bien. Si encuentran el testigo al abrir, `Pelis.bat` y `pelis.sh` restauran `*.anterior` como la carpeta del programa antes de arrancar.

## Criterio de terminado
- [ ] `tools/version.py` y `/version` publican una versión de punta a punta, con las negativas y las RC como dice la spec
- [ ] Subir un tag publica una Release con los paquetes de Windows y Linux y el `SHA256SUMS`, armados en GitHub, con los tests pasando
- [ ] «Buscar actualización» informa bien los tres casos: al día, hay versión nueva y sin conexión
- [ ] «Actualizar» en Windows y en Linux deja la versión nueva funcionando, con la base, la configuración y el progreso intactos
- [ ] Cortar la actualización a la mitad (por ejemplo, sin red durante la descarga) deja la versión anterior funcionando
- [ ] Una versión nueva que no arranca se restaura sola al volver a abrir con el lanzador
- [ ] Una RC se prueba de punta a punta con `--prerelease` sin que la vean las apps sin esa opción
