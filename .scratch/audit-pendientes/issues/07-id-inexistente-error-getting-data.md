# 07: Un IMDb ID inexistente se toma como error de red

**What to build:** cuando OMDb no tiene un IMDb ID bien formado, la película queda **No encontrada** y no **Pendiente**. Hoy OMDb responde a esos IDs con `"Error getting data."` (no con `"Incorrect IMDb ID."`, que solo usa para IDs mal formados), y `Omdb._consultar` lo trata como error de red. Consecuencias:

- En «Editar datos», pegar `tt0000000` muestra «Error getting data.» en vez de «IMDb no tiene una película con el ID tt0000000.».
- En el escaneo, una película cuyo `imdb_id` (del JSON de la carpeta) no existe queda **Pendiente** y se reintenta en cada escaneo con red, sin terminar nunca.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `por_id` con un ID bien formado que OMDb no tiene devuelve `None` («no está»).
- [x] «Editar datos» muestra el mensaje de que IMDb no tiene esa película.
- [x] El escaneo deja la película **No encontrada**, no **Pendiente**.
- [x] `"Invalid API key!"`, `"Request limit reached!"` y una respuesta que no es JSON siguen siendo error de red.
- [x] Test en `tests/test_omdb.py` con la respuesta `"Error getting data."`.

## Decisión pendiente

No está documentado que `"Error getting data."` signifique solo «ese ID no existe»: podría ser también una falla pasajera del lado de OMDb. Si es así, tratarlo como «no está» dejaría **No encontrada** para siempre una película que en otro momento sí se encontraría. Opciones:

1. Tratarlo como «no está» siempre (simple; riesgo de falsos No encontrada).
2. Tratarlo como «no está» solo en `por_id` (en `?t=`/`?s=` no se vio esa respuesta).
3. Dejarlo como error de red en el escaneo, pero en «Editar datos» mostrar un mensaje claro («IMDb no devolvió datos para ese ID; revisá que sea correcto»).

## Dónde

- La clasificación está en `Omdb._consultar` (`src/pelis/omdb.py:18`).
- `por_id` lo usan el escaneo (`src/pelis/escaneo.py:39`) y «Corregir match» (`Puente.usarImdb`, `src/pelis/puente.py:439`).

## Evidencia

Respuestas reales de OMDb (2026-11-07):

| Consulta | `Error` |
|---|---|
| `i=tt0000000`, `i=tt9999999` | `Error getting data.` |
| `i=tt99999999`, `i=tt12`, `i=xyz` | `Incorrect IMDb ID.` |
| `t=<título inexistente>`, `s=<título inexistente>` | `Movie not found!` |
| `s=a` | `Too many results.` |

## Comments

**2026-11-07:** se eligió la opción 2: solo `por_id` trata `"Error getting data."` como «no está». En el escaneo, un ID inexistente ya no frena la cascada: se sigue con la búsqueda por título (con OMDb real, «Aliens (1986) [tt0000000]» quedó matcheada con tt0090605 y una carpeta sin título real quedó **No encontrada**).
