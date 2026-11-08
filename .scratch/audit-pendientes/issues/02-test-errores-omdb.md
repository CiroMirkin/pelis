# 02: Test del clasificador de errores de OMDb

**What to build:** un test que falle si se confunde "OMDb no tiene la película" con un error de clave o de límite. Hoy el cliente de OMDb decide comparando el texto del error: "not found" o "Incorrect IMDb ID" dejan la película **No encontrada** (para siempre); cualquier otro error la deja **Pendiente** y el escaneo la reintenta. Ningún test pasa por esa decisión: los tests de escaneo usan un OMDb falso.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] El test simula las respuestas HTTP de OMDb, sin red.
- [x] `"Movie not found!"` y `"Incorrect IMDb ID."` se tratan como "no está" (sin error).
- [x] `"Invalid API key!"` y `"Request limit reached!"` se tratan como error de red (quedan pendientes).
- [x] Una respuesta que no es JSON también se trata como error de red.

## Dónde

- La decisión está en `Omdb._consultar` (`src/pelis/omdb.py:18`): `None` es "no está" y `ErrorRed` deja la película pendiente.
- El test va en un `tests/test_omdb.py` nuevo. Hay que reemplazar `Omdb.sesion` por un doble cuyo `get()` devuelva un objeto con `json()` y `status_code`; para el caso "no es JSON", `json()` lanza `ValueError`. No hace falta agregar dependencias como `responses`.
- Sumar el caso `"Too many results."` de `buscar()`: se convierte en `ErrorRed` con el mensaje que pide agregar el año.
