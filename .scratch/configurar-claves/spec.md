# Configurar las claves desde la app

Status: needs-triage

Anotada el 2026-11-01.

## Idea
Poder cargar las claves de OMDb y TMDb (y quizás el resto de `pelis.toml`: idiomas de sinopsis, audio y subtítulos preferidos) desde la app.

## Contexto
Sale de `.scratch/elegir-biblioteca/spec.md`. En modo instalado no hay `pelis.toml`: la app arranca sin claves y deja las películas como *pendientes*. La única forma de cargarlas es crear a mano un `pelis.toml` en la carpeta de datos (`%APPDATA%\Pelis` o `~/.local/share/pelis`), lo que no es razonable para alguien que instaló la app.

## Por definir
- Dónde se guardan (`preferencias.ini` o escribir el `.toml`) y cuál gana si hay en los dos lados.
- Dónde va la pantalla (menú «…», o un aviso cuando hay películas pendientes por falta de clave).
- Si después de cargarlas se reescanean las pendientes enseguida.
