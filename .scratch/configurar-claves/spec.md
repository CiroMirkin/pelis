# Configurar las claves desde la app

Status: ready-for-agent

Anotada el 2026-11-01. Decisiones cerradas en un grilling el 2026-11-08.

## Idea
Poder cargar las claves de OMDb y TMDb desde la app, sin editar `pelis.toml` a mano.

## Contexto
Hoy las claves salen de `omdb_api_key` y `tmdb_api_key` en `pelis.toml`. Se leen una sola vez al arrancar (`config.cargar`). La de OMDb hace falta para los metadatos: sin ella, el escaneo deja las películas como *pendientes*. La de TMDb es opcional y sirve para las sinopsis en español. Cuando falta la clave, el usuario solo ve el aviso «Falta omdb_api_key en pelis.toml», y la única salida es editar el archivo.

Además, `.scratch/elegir-biblioteca/spec.md` define un modo instalado en el que `pelis.toml` es opcional y la app no lo crea. Ahí no habría ninguna forma razonable de cargar las claves.

## Alcance
Solo las dos claves. Los idiomas de sinopsis, el audio y los subtítulos preferidos siguen en `pelis.toml`.

## Decisiones

### Dónde se guardan
- Se guardan en `preferencias.ini` (`QSettings`), igual que la biblioteca en elegir-biblioteca. La app no escribe `pelis.toml`.
- Precedencia, para cada clave por separado: gana la de `preferencias.ini`; si ahí no está, se usa la de `pelis.toml`, que sirve como valor inicial para las copias existentes, sin migrar nada; si tampoco está, la clave queda vacía.
- Si la clave se borró desde la app, en `preferencias.ini` queda guardada como `""`. Una clave vacía guardada ahí también gana: borrar desde la app no hace reaparecer la de `pelis.toml`.
- Consecuencia aceptada: cuando una clave ya se guardó desde la app, editarla a mano en `pelis.toml` no tiene efecto.

### Punto de entrada
- Una opción «Claves de API…» en el menú «…» del header.
- Un botón «Configurar clave» en el aviso del diálogo de escaneo cuando falta la de OMDb.
- Los dos abren el mismo modal.

### Modal
- Un campo por clave, OMDb y TMDb, enmascarado (`••••`), con el valor actual precargado y un botón de ojo para mostrarla.
- Al lado de cada campo, un enlace «Conseguir clave»: `https://www.omdbapi.com/apikey.aspx` y la página de API de TMDb (`https://www.themoviedb.org/settings/api`).
- Un solo botón «Guardar» para las dos.

### Validación al guardar
- Solo se validan las claves que cambiaron, con una consulta real: OMDb con un IMDb ID conocido y TMDb con `/configuration`. Corre fuera del hilo de la UI.
- Todo o nada: si alguna es inválida no se guarda ninguna, y el error aparece debajo de ese campo.
- Sin red se guarda igual, con el aviso «No se pudo verificar».
- Un campo vacío borra la clave, en las dos. Si se borra la de OMDb, se avisa que sin clave las películas nuevas quedan pendientes, pero no se bloquea.

### Aplicar en caliente
- Al guardar se actualiza el `Config` en memoria. La clave nueva vale enseguida, sin reiniciar: el próximo escaneo y «Buscar en IMDb» del detalle ya la usan.
- Si hay un escaneo en curso, sigue con la clave con la que empezó. La nueva vale desde el próximo.

### Pendientes
- Después de guardar una clave de OMDb nueva, el modal ofrece el botón «Buscar datos de las pendientes ahora», que lanza un escaneo. No se lanza solo.
- Solo aparece si hay películas pendientes. Mientras corre un escaneo, queda deshabilitado.

### Textos y docs
- Los avisos dejan de nombrar `pelis.toml` y pasan a decir «Falta la clave de OMDb»: `escaneo.py` (`aviso_omdb`) y `puente.py` (error de `imdbRespondio`).
- README y `pelis.toml.ejemplo`: mencionar que las claves también se configuran desde la app, en «…» → «Claves de API…», y que la de la app gana.

## Relación con elegir-biblioteca
Los dos tickets son independientes. Este se hace primero. Comparten la regla de precedencia (gana `preferencias.ini` y `pelis.toml` es el valor inicial), así que conviene que la lectura de `preferencias.ini` con fallback al toml quede en un solo lugar, para que elegir-biblioteca la reuse.
