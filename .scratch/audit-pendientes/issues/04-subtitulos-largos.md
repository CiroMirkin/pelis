# 04: Los subtítulos largos se ven todo el tiempo que duran

**What to build:** un subtítulo externo sigue en pantalla mientras esté vigente, aunque se le superpongan muchas líneas. Hoy, para saber qué texto va en un instante, solo se miran los 5 eventos que empezaron último. En un `.ass` con un cartel de 10 s y seis líneas de diálogo que empiezan en ese lapso, el cartel desaparece antes de tiempo. Los `.srt` comunes no tienen este problema.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Un test con un evento largo y al menos 6 eventos que empiezan mientras dura: el texto largo se ve durante todo su rango.
- [x] Los tests de subtítulos que ya existen siguen pasando.
- [x] Mostrar un archivo de unas 1500 líneas sigue siendo instantáneo (no hace falta un índice).

## Dónde

- `Linea.texto_en` (`src/pelis/subtitulos.py:41`) recorta con `self.eventos[max(0, i - 5):i]`.
- Arreglo simple: guardar en `__init__` la duración máxima de un evento (`max(e - s)`). En `texto_en`, retroceder desde `i` mientras `inicio > ms - duracion_max`. La complejidad sigue siendo `O(log n + k)` y el orden de las líneas no cambia (por inicio).
- Tests en `tests/test_subtitulos.py`.
