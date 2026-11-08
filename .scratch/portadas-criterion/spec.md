# Portadas de Criterion

Status: ready-for-agent

Anotada el 2026-11-07. Para revisión.

## Problem Statement

A quien usa Pelis le gustan mucho las portadas de The Criterion Collection y quiere verlas en el catálogo. Hoy los pósters vienen de OMDb: suelen ser de 300×450 y no siempre son la mejor imagen disponible. Criterion no tiene una API oficial, `criterion.com` responde 403 de Cloudflare a clientes HTTP simples, y no hay forma de integrarlo como se integra OMDb. Sin una solución, la única alternativa es buscar y bajar cada portada a mano.

## Solution

Empaquetar con la app un dataset estático que mapea IMDb ID → edición de Criterion (spine y URL de la portada en `_large`). El dataset se arma una vez con un script de desarrollo a partir de un snapshot archivado del catálogo de Criterion y de Wikidata, y viaja dentro del build: en tiempo de ejecución no se scrapea nada.

Con ese dataset, Pelis baja la portada a `posters/criterion.jpg`, la registra en el set de pósters de la película con origen `criterion` y la suma a la rotación. No desplaza al póster actual ni a las imágenes propias: solo pasa a ser actual si la película no tenía ninguno. La descarga ocurre en el escaneo y también desde una opción de menú para las películas ya escaneadas. El dataset se refresca con `python tools/criterion.py`.

## User Stories

1. Como usuario, cuando escaneo la biblioteca, las películas que tienen edición de Criterion reciben su portada automáticamente.
2. Como usuario, las portadas ya bajadas no se vuelven a bajar en cada escaneo.
3. Como usuario, una portada de Criterion no reemplaza al póster actual ni a mis imágenes propias: se suma al set para poder rotar.
4. Como usuario, si una película no tenía ningún póster, la portada de Criterion pasa a ser la actual y deja de estar incompleta.
5. Como usuario, «pasar a la portada siguiente» incluye la portada de Criterion en el orden del set.
6. Como usuario, «Renovar portadas» puede elegir la portada de Criterion al rotar.
7. Como usuario, puedo traer las portadas de Criterion de las películas ya escaneadas desde el menú del catálogo, con progreso y un resumen al terminar.
8. Como usuario, si estoy sin internet el escaneo sigue funcionando: las portadas quedan para el próximo intento y el informe lo avisa.
9. Como usuario, si una descarga falla, no se corta el escaneo ni se marcan las películas como fallidas.
10. Como usuario, el catálogo y la reproducción siguen funcionando sin red; el dataset viaja con la app.
11. Como usuario, una película sin edición de Criterion no cambia en nada.
12. Como usuario, un box set que no tiene un único IMDb ID no recibe una portada equivocada: queda como está.
13. Como usuario, si borro `posters/criterion.jpg`, el próximo escaneo la vuelve a bajar.
14. Como usuario, si renombro o muevo la carpeta de la película, la portada de Criterion se mueve con ella y no se baja de nuevo.
15. Como usuario, si corrijo el match de IMDb y la película nueva no tiene edición de Criterion, la portada vieja no queda dando vueltas como si fuera de esta película.
16. Como usuario, la portada de Criterion conserva su origen al rotar o pasar de portada, así «revisar la carpeta» no la confunde con una imagen nueva.
17. Como usuario, un archivo propio que ya se llame `criterion.jpg` en `posters/` no se pisa.
18. Como mantenedor, puedo refrescar el dataset con `python tools/criterion.py` y la app lo usa en el siguiente arranque.
19. Como mantenedor, el dataset entra en el build de PyInstaller sin tocar el código de carga.
20. Como mantenedor, el script de refresco no depende de la app para funcionar y su salida es determinista, así el diff se puede revisar.
21. Como usuario, veo las portadas de Criterion en alta resolución (1288×1600) en vez de las 300×450 de OMDb.
22. Como usuario, la descarga de portadas no bloquea la UI: puedo seguir usando el catálogo mientras corre.

## Implementation Decisions

### Dataset

- Archivo `src/pelis/datos/criterion.json`, empaquetado con la app.
- Estructura:

  ```json
  {
    "generado": "2026-11-07",
    "snapshot": "20260715",
    "peliculas": {
      "tt0047478": {
        "spine": 2,
        "film_id": 165,
        "url": "https://s3.amazonaws.com/criterion-production/..._large.jpg"
      }
    }
  }
  ```

- Clave: IMDb ID en minúsculas (`tt…`). Valor: spine, film ID de Criterion y URL de la portada.
- Solo entran filas con IMDb ID y URL de portada. Los box sets sin un único IMDb ID quedan afuera.
- Las URL se normalizan a `_large` cuando el listado trae `_thumbnail`, `_small` o `_medium`. Las variantes `_original` y `.png` se dejan tal cual.
- El archivo se escribe ordenado y con un encabezado de procedencia para que el diff sea revisable. Pesa ~400 KB.
- Se agrega `(raiz/src/pelis/datos, "pelis/datos")` a `datas` en `tools/pelis.spec`.

### Módulo `src/pelis/criterion.py`

- `cargar()` lee y cachea el JSON. `portada(imdb_id, datos=None)` devuelve la entrada o `None`; acepta un dataset inyectado para los tests.
- `aplicar(conn, biblioteca, pelicula_id, datos=None, descargar=descargar)` es la única entrada para sincronizar una película:
  - Si no hay entrada para su IMDb ID y no hay una portada registrada con origen `criterion`, no hace nada.
  - Si hay entrada y la portada ya está registrada y el archivo existe, no hace nada.
  - Si hay entrada y falta el archivo, lo baja a `posters/criterion.jpg` (resolviendo la subcarpeta como ya lo hace `poster._carpeta_posters`), lo registra con `poster.registrar(..., "criterion")` y, solo si `poster._actual(...)` es `None`, lo pone como actual con `poster._usar`.
  - Si no hay entrada pero hay una portada registrada con origen `criterion` (match corregido), borra el archivo y la fila. Si era la actual, limpia `poster_actual_id` para que `poster.revisar` elija otra.
  - Si `posters/criterion.jpg` existe pero no está registrado con origen `criterion`, lo trata como archivo del usuario y no lo toca.
  - Hace commit al terminar. Propaga `ErrorRed` si la descarga falla; en ese caso no registra nada ni deja cambios a medias.
- `traer_faltantes(conn, biblioteca, progreso=lambda actual, total, nombre: None, datos=None, descargar=descargar)` recorre las películas activas con `omdb_id` que tienen entrada en el dataset o una portada registrada con origen `criterion` (para limpiar las que quedaron de un match viejo), llama a `aplicar` en cada una, informa progreso y devuelve `{"descargadas": n, "fallidas": m, "aviso": ""}`. Ante el primer `ErrorRed` corta el recorrido y devuelve el aviso, para no encadenar timeouts.
- `descargar(url, destino)` usa `requests` con el mismo `TIMEOUT` de OMDb y lanza `ErrorRed`.
- `url_large(url)` es la función pura de normalización de URL, compartida con el script.

### Política de póster (`src/pelis/poster.py`)

- Los orígenes pasan a ser `existente`, `omdb` y `criterion`. Se agrega `DESCARGADOS = ("omdb", "criterion")`.
- Se agrega `_descargados`, que devuelve `{path: origen}` para los dos orígenes descargados. `_bajados` sigue existiendo con su significado actual (solo OMDb) para no cambiar cuándo se baja un póster de OMDb.
- En `_revisar`, una imagen propia nueva desplaza a cualquier póster descargado (no solo al de OMDb), y el fallback sin imágenes propias elige entre los descargados conservando el origen de la fila.
- `_cambiar` ya conserva el origen de las filas registradas: la rotación y «portada siguiente» no convierten una portada de Criterion en `existente`.
- Actualizar el docstring del módulo con el origen nuevo.

### Edición (`src/pelis/edicion.py`)

- `destino_poster` sigue mirando solo `_bajados` (OMDb): tener una portada de Criterion no dispara la descarga de un póster de OMDb donde antes no la había.
- `aplicar_omdb` considera actuales reemplazables a los dos orígenes descargados (`actual["origen"] in poster.DESCARGADOS`), así un póster de OMDb corrige el match aunque la actual sea de Criterion.

### Escaneo (`src/pelis/escaneo.py`)

- `Informe` suma `aviso_criterion: str`.
- En `ejecutar`, para cada película activa que no está en papelera y tiene `omdb_id`, se llama a `criterion.aplicar` después de `poster.revisar`. Es barato para las que no tienen edición de Criterion: solo consulta el dataset.
- En `_guardar`, después de `_bajar_poster`, se llama a `criterion.aplicar` para las películas nuevas o recién matcheadas.
- El primer `ErrorRed` de Criterion durante un escaneo corta los intentos siguientes y deja el aviso en `informe.aviso_criterion`, igual que el patrón de `omdb_caido`.
- `TrabajoEscaneo` pasa el aviso como `avisoCriterion` y `DialogoEscaneo.qml` lo muestra en el informe, junto a los avisos de OMDb y TMDb.
- El escaneo sin red (`importar_sin_red`) no intenta bajar portadas.

### UI (`src/pelis/puente.py` y QML)

- `TrabajoCriterion(QObject)` corre `criterion.traer_faltantes` en un `QThread`, con señales `progreso(int, int, str)` y `terminado(QVariantMap)`.
- `Puente.traerPortadasCriterion()` arranca el trabajo y reutiliza `_hilo` para que «Renovar portadas» y «portada siguiente» no escriban pósters al mismo tiempo. Emite `criterionProgreso` y `criterionTerminado`.
- Al terminar, llama a `_posters_cambiaron()`.
- `Catalogo.qml` suma la opción «Traer portadas de Criterion» al menú «…», con un `DialogoPortadas.qml` chico, modelado sobre `DialogoEscaneo.qml`: barra de progreso, texto de la película en curso y resumen («Se trajeron N portadas» / «No hay portadas para traer» / aviso de error).
- La opción se deshabilita mientras `puente.escaneando` sea verdadero.

### Script de refresco (`tools/criterion.py`)

- Uso: `python tools/criterion.py [--salida src/pelis/datos/criterion.json]`.
- Pasos:
  1. Resolver el snapshot archivado del listado `criterion.com/shop/browse/list?sort=spine_number` con la API de disponibilidad de Wayback, fijando el timestamp `20260715`.
  2. `parsear_listado(html)` → filas con `film_id`, `spine`, título y URL de portada. Función pura.
  3. Consultar Wikidata por SPARQL: ítems con `P9584` (Criterion film ID), `P345` (IMDb ID) y opcionalmente `P12279` (spine).
  4. `unir(listado, wikidata)` → diccionario por IMDb ID. Función pura.
  5. Normalizar las URL con `url_large` y escribir el JSON ordenado.
- Si el snapshot o Wikidata no responden, el script falla con un mensaje claro y no escribe un dataset parcial.
- No se ejecuta desde la app ni en el build.

## Testing Decisions

Se testea en los cuatro puntos acordados, de arriba hacia abajo y sin agregar seams nuevos fuera de `criterion`:

1. **Dataset puro** — `tests/test_criterion.py`:
   - `portada` encuentra por IMDb ID, ignora mayúsculas y devuelve `None` si no está.
   - `url_large` normaliza `_thumbnail`, `_small` y `_medium`, y respeta `_original` y `.png`.
   - `parsear_listado` y `unir` con HTML/JSON inline chicos, sin red.

2. **Aplicación a la base** — `tests/test_criterion.py`, con `tmp_path`, `db.conectar` y un `descargar` falso, siguiendo el patrón de `tests/test_poster.py`:
   - Baja una sola vez a `posters/criterion.jpg` y registra origen `criterion`.
   - No cambia el póster actual cuando ya hay uno.
   - Pasa a ser actual cuando la película no tenía póster.
   - Es idempotente: la segunda llamada no descarga.
   - Borra la portada vieja cuando el IMDb ID actual ya no tiene edición de Criterion.
   - No pisa un `criterion.jpg` no registrado.
   - `traer_faltantes` recorre solo activas con `omdb_id`, informa progreso y corta ante `ErrorRed`.

3. **Política de póster** — se extienden los tests existentes de `tests/test_poster.py`:
   - Una portada `criterion` en `posters/` forma parte del set y de la rotación.
   - `_revisar` no deja que una portada de Criterion desplace una imagen propia.
   - Sin póster actual, `_revisar` elige la de Criterion y conserva el origen.
   - «Portada siguiente» conserva el origen `criterion`.
   - `aplicar_omdb` reemplaza una portada de Criterion actual cuando llega un póster de OMDb.
   - `destino_poster` no cambia su decisión por tener una portada de Criterion (sigue mirando solo OMDb).

4. **Script de refresco** — `tests/test_criterion.py` cubre las funciones puras; el acceso a Wayback y Wikidata no se testea (es un script de desarrollo, igual que el resto de `tools/`).

También se cubre en `tests/test_escaneo.py`:
- Un escaneo baja la portada de una película matcheada.
- Un segundo escaneo no la vuelve a bajar.
- Un `ErrorRed` de Criterion no marca la película como fallida, deja el aviso y el escaneo sigue.
- Una película sin IMDb ID o sin edición de Criterion queda igual.

## Out of Scope

- API oficial de Criterion: no existe.
- Scrapear `criterion.com` en tiempo de ejecución: Cloudflare lo bloquea y el catálogo debe andar sin red.
- Box sets y ediciones sin un único IMDb ID (~150 filas del listado).
- Mostrar el número de spine, un distintivo «Criterion» o un filtro de colección en el catálogo.
- Elegir tamaño de portada o bajar varias variantes: siempre `_large`, con la URL original como fallback.
- Un botón por película para «usar esta portada ahora»: la portada entra al set y se elige rotando o con «portada siguiente».
- Actualizar el dataset desde la app o automáticamente al arrancar.
- Contenido de Criterion Channel, ensayos, Eclipse u otros productos que no sean la película.
- Resolver permisos o licencias: las imágenes son de Criterion, igual que las de OMDb/TMDb.

## Further Notes

- El listado archivado que se usó tiene 1.862 filas; 1.708 tienen film ID y todas traen imagen. El cruce con Wikidata deja 1.684 películas con IMDb ID y portada.
- Ejemplo verificado: `tt0047478` (Seven Samurai) → spine 2, film ID 165, `https://www.criterion.com/films/165`.
- Las imágenes viven en `s3.amazonaws.com/criterion-production/...`, que no está detrás de Cloudflare. `_large.jpg` devuelve 1288×1600.
- Variantes vistas en el listado: 178 filas con `_small.jpg`, 2 con `_original.jpg` y 1 `.png`.
- El nombre `posters/criterion.jpg` es fijo a propósito: la subcarpeta se resuelve sin importar mayúsculas y `db.reasignar` mueve la fila del póster junto con la película.
- No hace falta migración de base: `posters.origen` es TEXT sin restricción.
- Si el usuario borra el archivo pero queda la fila, `aplicar` lo detecta por la existencia del archivo y lo vuelve a bajar.
- La portada de Criterion no entra en `pelis.json`: es un archivo de la carpeta y una fila de `posters`, no un metadato.
- El circuito de corte ante `ErrorRed` evita 1.700 timeouts de 15 segundos cuando no hay red.
- Para revisar el dataset sin la app: `python -c "import json; d=json.load(open('src/pelis/datos/criterion.json')); print(len(d['peliculas']))"`.
