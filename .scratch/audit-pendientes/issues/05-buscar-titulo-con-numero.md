# 05: Buscar en IMDb un título que termina en número

**What to build:** en «Editar datos», buscar por título encuentra las películas cuyo título termina en un número que parece un año. Hoy el texto se separa en título y año antes de consultar OMDb, y cualquier número entre 1800 y 2099 al final se toma como año: «Blade Runner 2049» se busca como «Blade Runner» del año 2049, y «Wonder Woman 1984» igual. OMDb no devuelve nada y el usuario tiene que saber que puede pegar el IMDb ID. El arreglo: si se separó un año y la búsqueda vino vacía, buscar una vez más con el texto completo y sin año.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] «Blade Runner 2049» muestra candidatos aunque OMDb no tenga nada para «Blade Runner» en 2049.
- [ ] «Aliens 1986» sigue buscando «Aliens» con año 1986 y no hace una segunda consulta si esa trae resultados.
- [ ] Un texto sin año al final hace una sola consulta, como hoy.
- [ ] Tests con un OMDb falso, sin red, que cubren los tres casos.
