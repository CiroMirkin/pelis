# Instalador para Windows y Linux

Status: needs-triage

Anotada el 2026-11-13.

## Idea
Hace falta un instalador para Windows y otro para Linux. La app tiene que seguir siendo portable y la instalación es opcional, así Pelis puede vivir en la compu o en un disco y lo decide el usuario.

## Contexto
`elegir-biblioteca` (hecho) ya resolvió lo que bloqueaba al instalador: si no hay `pelis.toml` junto a la carpeta de la app, Pelis corre instalada y guarda la base y las preferencias en la carpeta del usuario (`%APPDATA%\Pelis` o `~/.local/share/pelis`), y la biblioteca se elige desde la app. Falta el instalador en sí.

## Decisiones cerradas
- Hay dos formas de tener Pelis y las dos se siguen publicando: la portable (la carpeta que se copia a un disco) y la instalada.
- Instalar es opcional. Nadie tiene que instalar para usar la app.
- El instalador no cambia cómo funciona la versión portable.

- Las instalaciones se actualizan con el mismo botón «Buscar actualización» que ya existe.
- La Release publica los instaladores junto con los zips portables, y se distinguen en el nombre: los portables llevan «(Portable)».

## Por decidir
- Windows: el instalador es un `.exe` armado con Inno Setup. Falta decidir si instala en `C:\Program Files\Pelis` o por usuario.
- Linux: no hay un `.exe` equivalente. Opciones: `.deb` (nativo de Mint, se instala con doble clic), AppImage (un solo archivo que se ejecuta sin instalar) o los dos.
- Qué hace el botón de actualizar en una instalación, porque no puede reemplazar su propia carpeta de solo lectura (por ejemplo, bajar el instalador nuevo y ejecutarlo).
