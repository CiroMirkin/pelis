# 02: Tamaño de subtítulos en porcentaje entero

**What to build:** el panel de subtítulos calcula el tamaño en porcentaje entero, sin redondeos ni márgenes para compensar los decimales. Para el usuario no cambia nada: sigue moviéndose de a 2 %, entre 50 % y 200 %, y el valor guardado en las preferencias conserva su formato.

**Blocked by:** None (can start immediately)

**Status:** ready-for-human

- [x] «−» y «+» cambian el tamaño de a 2 %
- [x] El tamaño no baja de 50 % ni sube de 200 %
- [x] «−» se desactiva en 50 % y «+» en 200 %
- [x] La etiqueta muestra siempre el porcentaje actual, sin decimales
- [x] Un tamaño ya guardado se sigue leyendo bien, incluidos los de los pasos anteriores de 25 %
- [ ] Se comprobó en la app, porque no hay tests de QML

## Comments

Implementado. Se probó el `Reproductor.qml` real con Qt sin pantalla: pasos, límites, botones, etiqueta y valores guardados de 25 % dan bien. Falta mirarlo en la app abierta.
