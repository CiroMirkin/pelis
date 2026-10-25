# Elegir a mano la codificación de un subtítulo externo

Status: ready-for-agent
Blocked by: 01

Para los casos que la detección automática (UTF-8 → cp1252) no resuelve: un selector de codificación en el panel «Audio y subtítulos» que vuelve a leer el archivo con `pysubs2`. Dónde se guarda la elección lo define el ticket 01.

## Criterio de terminado
- [ ] Un `.srt` con una codificación que la detección no resuelve (ej. ISO-8859-15, UTF-16) se ve bien eligiéndola a mano
- [ ] Test de la lectura con codificación forzada sin UI
