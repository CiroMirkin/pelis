---
name: version
description: Publica una versión nueva de Pelis (patch, minor, major, final, o una RC) con tools/version.py, que sube __version__, commitea, crea el tag con las notas y pushea; el workflow arma la Release. Usar cuando el usuario escriba "/version" o pida publicar, sacar o etiquetar una versión o una RC.
---

# Versión

`tools/version.py` hace todo. Esta skill lo corre, muestra las notas y pide la confirmación. Las reglas están en `.scratch/fase-7-publicacion/spec.md` («Comando de versión»).

## Pasos

1. **Python**: `.venv-linux/bin/python` en Linux, `.venv\Scripts\python` en Windows. El script solo usa la biblioteca estándar.
2. **Vista previa**: `<python> tools/version.py <nivel> [--rc] --ver`. El nivel sale del pedido (`patch`, `minor`, `major` o `final`; `--rc` solo, sin nivel, para la siguiente RC). Si no lo dice, preguntalo. Si el script se niega («No se puede: …»), mostrá el motivo y pará: no arregles el repo por tu cuenta.
3. **Notas**: mostrá la versión vieja → nueva y las notas tal como salieron. Las lee el usuario final en la app. Si te pide reescribirlas, hacelo en lenguaje de usuario, en español, sin nombres de módulos ni jerga, y conservá los encabezados `## Nuevo` y `## Arreglos`. Guardalas en un archivo del scratchpad.
4. **Confirmación**: preguntá si publica. Pushear dispara la Release pública, así que no sigas sin un sí explícito para esta versión.
5. **Publicar**: `<python> tools/version.py <nivel> [--rc] --si [--notas <archivo>]`.
6. **Reportar** el tag publicado. Si el script avisó que `origin/main` cambió, pasá sus instrucciones para deshacer y no las corras sin que te lo pidan.
