---
name: copiar-build
description: Arma la build de Pelis de una rama y la instala en un destino (un disco o Vídeos), actualizando solo la app del sistema operativo actual.
disable-model-invocation: true
---

# Copiar build

Arma la build de una rama y con ella reemplaza el programa del sistema actual en una instalación de Pelis. En el destino se escribe solo lo que pertenece al programa: `pelis-app/app/<so>`, `pelis-app/app/<so>.anterior`, `pelis-app/app/pelis.toml.ejemplo` y el lanzador de la raíz. Todo lo demás es del usuario y queda como está: `pelis.toml` (las keys), `pelis.db`, `preferencias.ini`, `go2tv.log`, `Peliculas/` y la carpeta y el lanzador del otro sistema.

| Sistema | `<so>` | Script de build | Sale en | Lanzador |
|---|---|---|---|---|
| Linux | `linux` | `tools/build_linux.sh` | `dist/Pelis-linux/` | `pelis.sh` |
| Windows | `win` | `tools/build_win.bat` | `dist\Pelis-win\` | `Pelis.bat` |

## Pasos

1. **Preguntá rama y destino**, siempre, con AskUserQuestion, aunque la conversación ya sugiera cuáles son. Para la rama ofrecé las de `git branch`. Para el destino ofrecé la carpeta de Vídeos (`xdg-user-dir VIDEOS`) y los discos montados que tengan `pelis-app/app/` (en Linux, `/media/$USER/*`). Listo cuando el usuario eligió las dos cosas.

2. **Revisá el destino.** Si existe `<destino>/pelis-app/app/`, anotá qué hay adentro. Si no existe, preguntá si es una instalación nueva antes de crearla con `mkdir -p`. Listo cuando `<destino>/pelis-app/app/` existe y sabés qué tenía.

3. **Armá la build en un worktree aparte**, así el árbol de trabajo del usuario queda como está:
   ```
   git worktree add <scratchpad>/build-<rama> <rama>
   <scratchpad>/build-<rama>/tools/build_linux.sh
   ```
   Listo cuando el script imprime `Listo:` y la carpeta `pelis-app/app/<so>` existe en el `dist/` del worktree. Si falla, mostrá el error y pará.

4. **Rotá y copiá el programa**, igual que el actualizador de la app (`src/pelis/actualizacion.py`): el `<so>.anterior` viejo se va, el `<so>` actual pasa a ser `<so>.anterior` (el lanzador vuelve a esa versión si la nueva no arranca), y se copia la build nueva como `<so>`. Si te deniegan borrar el `<so>.anterior` viejo, renombralo a `<so>.anterior.<fecha>` y avisá al usuario que quedó un respaldo de más. Usá `cp -r` sin preservar permisos: los discos suelen ser exFAT o NTFS.

5. **Copiá los archivos sueltos del programa** desde el `dist/` del worktree: `pelis-app/app/pelis.toml.ejemplo` y el lanzador a la raíz del destino (en Linux, después `chmod +x`).

6. **Verificá** con `sync` y `diff -rq` entre la build y `<destino>/pelis-app/app/<so>`. Listo cuando el diff sale vacío.

7. **Borrá el worktree** con `git worktree remove`.

## Informe

Cerrá con: la rama y el commit que se copiaron, la ruta de destino, el resultado del diff, qué quedó como `<so>.anterior` y la confirmación de que `pelis.toml`, `pelis.db` y `preferencias.ini` están igual que antes.
