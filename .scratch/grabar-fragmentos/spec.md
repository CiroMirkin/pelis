# Grabar fragmentos de una película

Status: needs-triage

Anotada el 2026-10-29.

## Idea
En el reproductor, poder marcar un inicio y un fin y guardar ese tramo de la película como un video aparte, igual que una **Captura** pero en movimiento.

## Por definir
- Cómo se marcan el inicio y el fin (teclas, botones en la barra) y si se puede ajustar antes de guardar.
- Dónde se guarda. Lo natural es junto a las capturas, en la carpeta de la película.
- Si lleva sonido y subtítulos. Los externos son un overlay propio, así que no están en el video.
- Si se corta sin recodificar (rápido, pero arranca en el keyframe más cercano) o recodificando (exacto, pero lento). Cualquiera de las dos necesita FFmpeg: QtMultimedia reproduce, pero no exporta tramos.
