---
name: version
description: Publica una versión nueva de Pelis (patch, minor, major, final, o una RC) o muestra la ayuda (help, ayuda) con tools/version.py, que sube __version__, commitea, crea el tag con las notas y pushea; el workflow arma la Release. Usar cuando el usuario escriba "/version" o pida publicar, sacar o etiquetar una versión o una RC.
---

# Versión

`tools/version.py` hace todo. Esta skill lo corre, muestra las notas y pide la confirmación. Las reglas están en `.scratch/fase-7-publicacion/spec.md` («Comando de versión»).

## Ayuda

Con `/version help` o `/version ayuda`, mostrá esto y no corras nada:

| Comando | Qué publica |
|---|---|
| `/version patch` | Arreglos: `0.2.0` → `0.2.1` |
| `/version minor` | Features nuevas: `0.2.1` → `0.3.0` |
| `/version major` | Cambios que rompen: `0.3.0` → `1.0.0` |
| `/version minor --rc` | Pre-release para probar: `0.3.0-rc1`. También con `patch` o `major` |
| `/version --rc` | Siguiente RC de la misma versión: `-rc1` → `-rc2` |
| `/version final` | Cierra la RC y publica la versión: `0.3.0-rc2` → `0.3.0` |

- Antes de publicar muestra la versión nueva y las notas (los `feat` y `fix` desde la última versión final), y pide confirmación. Si se lo pedís, reescribe las notas en lenguaje de usuario.
- Se niega con cambios sin commitear, fuera de `main`, o si `main` divergió de `origin/main`. Con una RC abierta, solo acepta `final` o `--rc`.
- Las RC solo las ven las apps abiertas con `--prerelease`.
- Sin la skill: `python tools/version.py <nivel> [--rc]`, con `--ver` para ver sin publicar.

## Pasos

1. **Preparar main**: el script solo corre en `main` y los cambios viven en `dev`. Si estás en `dev` con todo commiteado, pusheá `dev` (con `--force-with-lease` solo si el usuario lo pidió), pasá a `main` y traé `dev`: `git merge --ff-only dev`, y si `main` divergió (tiene su `chore: versión vX`, que `dev` no), `git merge dev -m "chore: merge dev en main"`. Pedí el sí del usuario antes del merge. Hecho cuando `git log main..dev` está vacío.
2. **Python**: `python3` en Linux, `py -3` en Windows. El script solo usa la biblioteca estándar, así que no hace falta el entorno de `uv`.
3. **Vista previa**: `<python> tools/version.py <nivel> [--rc] --ver`. El nivel sale del pedido (`patch`, `minor`, `major` o `final`; `--rc` solo, sin nivel, para la siguiente RC). Si no lo dice, preguntalo. Si el script se niega («No se puede: …»), mostrá el motivo y pará: no arregles el repo por tu cuenta.
4. **Notas**: mostrá la versión vieja → nueva y las notas tal como salieron. Las lee el usuario final en la app. Si te pide reescribirlas, hacelo en lenguaje de usuario, en español, sin nombres de módulos ni jerga, y conservá los encabezados `## Nuevo` y `## Arreglos`. Guardalas en un archivo del scratchpad.
5. **Confirmación**: preguntá si publica. Pushear dispara la Release pública, así que no sigas sin un sí explícito para esta versión.
6. **Publicar**: `<python> tools/version.py <nivel> [--rc] --si [--notas <archivo>]`.
7. **Volver a dev**: con el tag publicado, `git checkout dev && git merge --ff-only main` para que `dev` reciba el commit `chore: versión` y no vuelvan a divergir. Luego `git push origin dev`.
8. **Reportar** el tag publicado. Si el script avisó que `origin/main` cambió, pasá sus instrucciones para deshacer y no las corras sin que te lo pidan.
