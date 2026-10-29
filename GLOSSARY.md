# Glosario

**Tarjeta**: los datos de una película tal como se muestran en una grilla (catálogo o filmografía de una persona): id, título, año, póster, fracción de progreso y si está vista. Se arma en `catalogo.tarjeta`.

**Incompleta**: película sin datos de IMDb (`omdb_estado` distinto de `encontrada`) o sin un póster que exista en el disco.

**Pendiente** / **No encontrada**: estados de los datos de IMDb. Pendiente: no se pudo consultar (sin internet o sin clave); el próximo escaneo con red la reintenta. No encontrada: OMDb respondió que no la tiene; hace falta buscarla o cargarla a mano.

**Recomendada**: una película al azar, activa, no vista y sin empezar, que se ofrece al abrir la app. Se elige una vez por apertura y se cierra cuando el usuario la descarta, la empieza o la marca vista.

**Metadatos**: los datos de IMDb/OMDb de una película: título, año, IMDb ID, sinopsis y su idioma, país, género, directores, elenco, URL del póster y origen (`omdb`, `manual`). No incluyen vista, progreso ni duración. Se guardan solo a través de `metadatos.aplicar`.

**pelis.json**: copia portátil de los metadatos dentro de la carpeta de cada película. Se lee solo si la base no tiene datos; si no coincide, gana la base (ADR 0001).

**Captura**: imagen PNG de un cuadro de la película, en resolución original y sin subtítulos, tomada con la tecla `.` en el reproductor. Se guarda en `capturas/` dentro de la carpeta de la película, con la posición como nombre (`01-23-45.png`).
