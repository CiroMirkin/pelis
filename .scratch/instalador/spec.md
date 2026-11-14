# Instalador para Windows y Linux

Status: ready-for-human

Anotada el 2026-11-13. Decisiones cerradas el 2026-11-14 (grilling).

## Idea
Hace falta un instalador para Windows y otro para Linux. La app tiene que seguir siendo portable y la instalación es opcional, así Pelis puede vivir en la compu o en un disco y lo decide el usuario.

## Contexto
`elegir-biblioteca` (hecho) ya resolvió lo que bloqueaba al instalador: si no hay `pelis.toml` junto a la carpeta de la app (`config.portable` en falso), Pelis corre instalada y guarda la base y las preferencias en la carpeta del usuario (`%APPDATA%\Pelis` o `~/.local/share/pelis`), y la biblioteca se elige desde la app. Falta el instalador en sí.

Hoy el workflow publica `Pelis-windows-vX.zip` y `Pelis-linux-vX.tar.gz`, y `actualizacion.py` (`Instalacion.paquete`) busca esos nombres.

## Decisiones

### Formas de distribución
- Hay dos formas de tener Pelis y las dos se siguen publicando: la portable (la carpeta que se copia a un disco) y la instalada.
- Instalar es opcional. Nadie tiene que instalar para usar la app. El instalador no cambia cómo funciona la versión portable.
- Las instalaciones se actualizan con el mismo botón «Buscar actualización» que ya existe.

### Nombres de los archivos de la Release
- `Pelis-windows-vX.Y.Z-portable.zip`
- `Pelis-linux-vX.Y.Z-portable.tar.gz`
- `Pelis-windows-vX.Y.Z-setup.exe`
- `Pelis-linux-vX.Y.Z.deb`
- En el texto de la Release los portables se nombran «(Portable)». Los archivos no llevan espacios ni paréntesis.
- No hay fallback a los nombres viejos: todavía no hay una primera versión pública que los use.
- Todos entran en `SHA256SUMS`.

### Windows
- Instalador con Inno Setup, armado en el job de `windows-latest`.
- Instala por usuario en `%LOCALAPPDATA%\Programs\Pelis`, sin pedir administrador (sin UAC). Sin firma: se acepta el aviso de SmartScreen, igual que con el portable.
- Crea el acceso directo en el menú de inicio y un desinstalador.
- Actualizar: la app baja `Pelis-windows-vX-setup.exe`, verifica el hash contra `SHA256SUMS`, avisa «Pelis se va a cerrar y volver a abrir» y se cierra. Lanza el instalador con `/SILENT /CLOSEAPPLICATIONS`, que pisa la carpeta (del usuario, escribible) y reabre la app. Sin `*.anterior` ni testigo: si el instalador falla a la mitad, Inno Setup revierte lo que copió.

### Linux
- `.deb` para Ubuntu/Debian, armado con `dpkg-deb --build` en el job de `ubuntu-24.04`, después del PyInstaller. Otras distros siguen usando el portable.
- Contenido: el programa en `/opt/pelis/`, un enlace `/usr/bin/pelis`, un `.desktop` en `/usr/share/applications/` y el ícono en `/usr/share/icons/`. Las dependencias de sistema (`tools/paquetes-linux.txt`) van en `Depends:`, así `apt install ./pelis.deb` las trae.
- Versión del paquete: un tag `-rcN` se empaqueta con `~` (`0.4.0~rc1`), para que ordene antes de la final y `apt` acepte pasar de la RC a la final.
- Actualizar: la app baja el `.deb`, verifica el hash, avisa y se cierra. Un script corre `pkexec apt install ./pelis_X.deb` (diálogo gráfico de contraseña de polkit) y reabre `pelis`. Si el usuario cancela o `apt` falla, el script reabre la versión anterior, que `apt` no tocó.

### Cómo decide la app qué mecanismo usar
- `config.portable`: portable usa el reemplazo de carpeta actual; instalada baja el instalador y lo ejecuta.

### Datos
- La instalada guarda todo en `%APPDATA%\Pelis` o `~/.local/share/pelis`, separado de cualquier portable. No hay migración entre las dos formas: para pasar de una a otra se elige la biblioteca de nuevo desde la app.
- Desinstalar no borra la base, las preferencias ni la biblioteca. El README dice dónde viven por si se quieren borrar a mano.

### Ícono
- Una colilla de cigarrillo, simple y legible a 16 px, sobre un fondo redondeado oscuro. El usuario lo revisa y lo itera hasta que le guste antes de engancharlo.
- Fuente en `assets/icono.svg`; un script en `tools/` genera el `.ico` (Windows) y el `.png` (Linux). Se usa también como ícono de la ventana de la app.

### Pruebas
- Disparo manual del workflow (artifacts, sin Release) y una RC (`vX.Y.Z-rc1`). El usuario instala una versión a mano en Windows y en Linux como chequeo.
- Para ver las RC desde una instalación, se abre una vez desde la terminal con `pelis --prerelease`. No hay opción en la interfaz.

## Issues
1. `01-icono.md`, el ícono
2. `02-renombrar-portables.md`, nombres nuevos de los portables
3. `03-instalador-windows.md`, Inno Setup
4. `04-deb-linux.md`, el `.deb`
5. `05-actualizar-instalacion-windows.md`
6. `06-actualizar-instalacion-linux.md`
7. `07-workflow-instaladores.md`
8. `08-verificar-instaladores.md`, chequeo manual
