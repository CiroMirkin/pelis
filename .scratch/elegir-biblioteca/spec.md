# Elegir la biblioteca

Status: ready-for-agent

Anotada el 2026-11-01. Decisiones cerradas el 2026-11-01.

## Idea
Poder elegir desde la app qué carpeta es la biblioteca, en vez de que salga fija de `pelis.toml`. Es el paso que falta para tener un instalador además de la versión portable. Las dos versiones pueden elegirla.

## Contexto
Hoy la biblioteca es lo que diga `biblioteca` en `pelis.toml` (por defecto `../../Peliculas`, relativa a `app/`). La base (`pelis.db`), `pelis.toml`, `preferencias.ini` y `go2tv.log` viven todos en `app/`, un nivel arriba del ejecutable (`config.app_dir`). Eso es lo que hace a la app portable: se copia la carpeta al disco y anda en Windows y en Mint.

Pero también impide un instalador: un instalador pone el ejecutable en un lugar de solo lectura (`C:\Program Files\Pelis`, `/opt/pelis`), donde no se pueden escribir la base ni las preferencias, y no hay forma de decirle dónde están las películas sin editar un `.toml` a mano. Si no encuentra la biblioteca, la app solo muestra "No existe la biblioteca" y se cierra.

## Alcance
Este ticket saca lo que bloquea al instalador: que la app funcione instalada (datos en la carpeta del usuario) y que la biblioteca se elija desde la app. El instalador en sí (Inno Setup en Windows, `.deb` o AppImage en Mint) queda para otro ticket.

## Decisiones

### Modo portable o instalado
- **Portable** si existe `pelis.toml` en `app/` (la carpeta de arriba del ejecutable, como hoy). **Instalada** si no.
- El modo dev (`--app-dir`) no cambia.

### Datos en modo instalado
- Una sola carpeta con la misma estructura que `app/` (`pelis.db`, `pelis.toml`, `preferencias.ini`, `go2tv.log`):
  - Windows: `%APPDATA%\Pelis`
  - Mint: `~/.local/share/pelis`
- Esa carpeta pasa a ser `config.app_dir`; el resto del código no cambia. Se crea si no existe.

### `pelis.toml`
- En modo instalado es **opcional**: la app no lo crea. Si existe en la carpeta de datos (puesto a mano), se lee; si no, todo toma los valores por defecto (sin claves de OMDb/TMDb, idiomas por defecto). Sin claves la app ya funciona: deja las películas como *pendientes*.
- La clave `biblioteca` deja de ser obligatoria en los dos modos (no más «Falta 'biblioteca'»).
- Cargar las claves desde la app es otro ticket, que se hace antes que este: `.scratch/configurar-claves/spec.md`. Usa la misma precedencia (gana `preferencias.ini` y `pelis.toml` es el valor inicial): reusar ese lector en vez de escribir otro.

### Dónde se guarda la elección
- En `preferencias.ini` (`QSettings`), en los dos modos. No se escribe el `.toml`.
- Precedencia: la biblioteca de `preferencias.ini` gana; si no hay, se usa `biblioteca` de `pelis.toml` (valor inicial de las copias portables existentes, sin migración); si tampoco hay, no hay biblioteca y se muestra la pantalla de elegir.
- Formato de la ruta:
  - **Portable**: relativa a `app/` cuando se puede (en Windows, mismo disco; en Linux, siempre), absoluta cuando no. Así el disco compartido anda montado como `E:\` en Windows y en `/media/...` en Mint.
  - **Instalado**: siempre absoluta.

### Cuando no hay biblioteca o no existe
- En vez de "No existe la biblioteca" y cerrarse, la app muestra una pantalla que dice que no la encuentra, con la ruta guardada (si había una: puede ser que el disco no esté montado) y un botón «Elegir carpeta…» que abre el selector de carpeta nativo.
- Si se cancela el selector, la app sigue en esa pantalla y se puede cerrar.

### Cambiarla después
- Opción «Cambiar biblioteca…» en el menú «…»: abre el selector, muestra el aviso (ver abajo) si corresponde, guarda la elección y escanea enseguida la carpeta nueva.
- Deshabilitada mientras hay un escaneo corriendo.

### La base al cambiar de biblioteca
- Una sola base: no hay una base por biblioteca. Las rutas de la base son relativas a la raíz, así que la misma biblioteca movida anda sin tocar nada.
- Aviso de confirmación («las películas de la biblioteca anterior van a quedar como faltantes») **solo** si la carpeta nueva no contiene ninguna de las carpetas de películas que hay en la base. Si la base está vacía (primera apertura), no hay aviso.
- El aviso aplica igual al selector del menú y al de la pantalla de «no encuentro la biblioteca».
