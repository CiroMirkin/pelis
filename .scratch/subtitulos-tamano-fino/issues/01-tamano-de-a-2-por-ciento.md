# 01: Tamaño de subtítulos de a 2 %

**What to build:** los botones − y + de «Tamaño» en el panel «Audio y subtítulos» del reproductor cambian el tamaño de los subtítulos externos de a 2 % en lugar de 25 %, siempre entre 50 % y 200 %. El tamaño se sigue recordando para todas las películas.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Desde 100 %, el + lleva a 102 % y el − a 98 %
- [x] El porcentaje mostrado y el tamaño real no acumulan errores de redondeo después de muchos pasos
- [x] Un tamaño ya guardado fuera de la nueva grilla sigue valiendo: desde 125 %, el + lleva a 127 %
- [x] El − se desactiva en 50 % y el + en 200 %, y ningún paso se pasa de esos límites
- [x] El tamaño elegido se recuerda al cerrar la app y en otras películas
- [x] Los casos de uso ya no hablan de 7 pasos
