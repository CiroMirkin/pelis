# 0001 · pelis.json es la copia portátil de los metadatos

2026-10-27 · Aceptada

## Contexto
Cada carpeta de película tiene un `pelis.json` para que sus datos viajen con ella: copiar la carpeta a otra biblioteca, o arrancar con una base nueva, no debería obligar a volver a consultar OMDb ni perder lo corregido a mano. Hasta ahora cada camino que guardaba metadatos escribía el archivo a su manera, y el archivo y la base podían no coincidir.

## Decisión
- `pelis.json` guarda solo metadatos (título, año, IMDb ID, sinopsis y su idioma, país, género, personas, `poster_url`, origen). Vista, progreso, duración y papelera son de cada biblioteca y no viajan.
- Se lee solo cuando la base no tiene datos de esa película (carpeta nueva o pendiente de metadatos).
- La base es la fuente: si el archivo no coincide, gana la base y el archivo se reescribe. El escaneo y el arranque de la app lo sincronizan.
- La base guarda todos los campos del archivo, así el archivo es una proyección exacta de ella.
- Un archivo inválido o de una versión más nueva no se pisa nunca.

## Consecuencias
- Editar `pelis.json` a mano no cambia una película que ya tiene datos en la base; solo sirve para una carpeta nueva (por ejemplo, `{"imdb_id": "tt…"}` para forzar el match).
- Un solo módulo (`metadatos`) escribe el archivo.
