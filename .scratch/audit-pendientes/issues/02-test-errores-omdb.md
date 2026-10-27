# 02: Test del clasificador de errores de OMDb

**What to build:** un test que falle si se confunde "OMDb no tiene la película" con un error de clave o de límite. Hoy el cliente de OMDb decide comparando el texto del error: "not found" o "Incorrect IMDb ID" dejan la película **No encontrada** (para siempre); cualquier otro error la deja **Pendiente** y el escaneo la reintenta. Ningún test pasa por esa decisión: los tests de escaneo usan un OMDb falso.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] El test simula las respuestas HTTP de OMDb, sin red.
- [ ] `"Movie not found!"` y `"Incorrect IMDb ID."` se tratan como "no está" (sin error).
- [ ] `"Invalid API key!"` y `"Request limit reached!"` se tratan como error de red (quedan pendientes).
- [ ] Una respuesta que no es JSON también se trata como error de red.
