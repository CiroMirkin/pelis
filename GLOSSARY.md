# Glosario

**Tarjeta**: los datos de una película tal como se muestran en una grilla (catálogo o filmografía de una persona): id, título, año, póster, fracción de progreso y si está vista. Se arma en `catalogo.tarjeta`.

**Incompleta**: película sin datos de IMDb (`omdb_estado` distinto de `encontrada`) o sin un póster que exista en el disco.

**Pendiente** / **No encontrada**: estados de los datos de IMDb. Pendiente: no se pudo consultar (sin internet o sin clave); el próximo escaneo con red la reintenta. No encontrada: OMDb respondió que no la tiene; hace falta buscarla o cargarla a mano.

**Recomendada**: una película al azar, activa, no vista y sin empezar, que se ofrece al abrir la app. Se elige una vez por apertura y se cierra cuando el usuario la descarta, la empieza o la marca vista.
