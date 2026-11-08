# Ajustes de interfaz: navegación, catálogo y reproductor

Status: ready-for-agent

## Problem Statement

Varias asperezas de uso cotidiano en Pelis:

- El panel «Audio y subtítulos» del reproductor crece sin límite cuando una película trae muchas pistas o archivos de subtítulos, y tapa la pantalla. Además, tocar el video fuera del panel no lo cierra: hay que volver a tocar el botón o apretar Esc.
- Al saltar entre personas y películas (película › director › otra película › director › otra película), «Volver» desanda cada paso, incluidas películas intermedias por las que ya no interesa pasar. Es tedioso y la pila crece con la misma persona repetida.
- En la barra del catálogo, el botón de la **Recomendada** no se ve de la misma altura que el resto de los controles.
- En el reproductor está la hora a la que termina la película, pero no la hora actual (en pantalla completa no hay reloj a la vista).
- Toda la interfaz grita: títulos, rótulos y botones van en mayúscula. La barra del catálogo repite «PELIS», que no aporta nada.
- Al buscar o al elegir una época estando en «Sin ver» o «Vistas», el resultado queda recortado por ese filtro sin que el usuario lo note, y parece que la película buscada no está.

## Solution

- El panel «Audio y subtítulos» tiene una altura máxima; si el contenido no entra, scrollea. Un toque en cualquier lugar fuera del panel lo cierra.
- Abrir una persona o una película que ya está en la pila de navegación no apila una pantalla nueva: vuelve a esa pantalla, descartando lo que estaba encima. Así la pila nunca repite una pantalla y «Volver» lleva al director sin pasar por las películas intermedias.
- Todos los controles de la barra del catálogo miden lo mismo de alto.
- En el reproductor, arriba de «Termina HH:MM», aparece «Hora: HH:MM» con la hora actual.
- La interfaz deja de forzar mayúsculas: cada texto se muestra como está escrito. La barra del catálogo ya no muestra «PELIS». El botón «Recomendar» pasa a decir «Recomendación».
- Buscar un texto o elegir una época pone el filtro de vistas en «Todas».

## User Stories

### Panel de audio y subtítulos

1. Como espectador, quiero que el panel «Audio y subtítulos» no pase de una altura máxima, para que no tape la película ni se salga de la ventana cuando hay muchas pistas.
2. Como espectador, quiero poder scrollear las listas de audio y subtítulos cuando no entran, para llegar a cualquier pista.
3. Como espectador, quiero que los controles de estilo de subtítulos (tamaño y color) sigan accesibles aunque haya muchas pistas, para no tener que buscarlos al fondo de una lista larga.
4. Como espectador, quiero que tocar fuera del panel (sobre el video, la barra o la barra superior) lo cierre, para volver a la película con un solo toque.
5. Como espectador, quiero que tocar el botón «Audio y subtítulos» con el panel abierto lo cierre (y no lo cierre y lo reabra), para que el botón siga funcionando como interruptor.
6. Como espectador, quiero que Esc siga cerrando el panel, para no perder el atajo que ya uso.
7. Como espectador, quiero que el toque que cierra el panel no pause ni reanude la película ni cambie la posición, para que cerrar el panel no tenga efectos secundarios.

### Navegación entre personas y películas

8. Como usuario que explora la filmografía de un director, quiero que al volver a abrir a ese director desde una película se me lleve a la pantalla del director que ya tenía abierta, para no acumular copias de la misma persona.
9. Como usuario, quiero que «Volver» desde el director me lleve a la película desde la que lo abrí por primera vez, para salir de la exploración en pocos pasos.
10. Como usuario, quiero que en el recorrido película › director › otra película › director › otra película, «Volver» desde la última película me lleve directo al director, sin pasar por la película intermedia.
11. Como usuario, quiero que lo mismo valga para una película: si la abro desde otra persona y ya estaba en la pila, vuelvo a ella en lugar de abrir una copia.
12. Como usuario, quiero que la pantalla a la que se vuelve recupere su estado normal (lista recargada, foco en la grilla), igual que cuando se llega con «Volver».
13. Como usuario, quiero que Esc se comporte igual que el botón «Volver», para que teclado y mouse lleven al mismo lugar.
14. Como usuario, quiero que abrir una persona o una película que no está en la pila siga funcionando como hoy, para no perder la navegación normal.
15. Como usuario, quiero que una persona se identifique por su nombre y una película por su id al decidir si «ya está en la pila», para que dos personas o películas distintas nunca se confundan.

### Barra del catálogo

16. Como usuario, quiero que el botón de la Recomendada tenga la misma altura que «Todas / Sin ver / Vistas», el selector de época y el resto de los botones, para que la barra se vea pareja.
17. Como usuario, quiero que la barra no muestre «PELIS», para tener más lugar y menos ruido.
18. Como usuario, quiero que el buscador quede alineado al margen izquierdo de la barra sin el hueco que dejaba la marca, para que la barra no arranque con un espacio vacío.
19. Como usuario, quiero que el botón diga «Recomendación», para que el nombre coincida con el de la franja que abre.

### Hora en el reproductor

20. Como espectador, quiero ver la hora actual («Hora: HH:MM») arriba de «Termina HH:MM», para saber qué hora es sin salir de pantalla completa.
21. Como espectador, quiero que la hora se actualice sola mientras miro, para que no quede desfasada.
22. Como espectador, quiero que la hora use el mismo formato de 24 horas y las mismas cifras tabulares que «Termina», para leer las dos de un vistazo.
23. Como espectador, quiero que «Hora» se vea aunque la duración todavía no se conozca, porque la hora actual no depende de la película.

### Sin mayúsculas forzadas

24. Como usuario, quiero que títulos, rótulos y botones se muestren tal como están escritos y no forzados a mayúscula, para que la interfaz se lea con más calma.
25. Como usuario, quiero que los títulos de películas y los nombres de personas se vean con su capitalización real, para reconocerlos como en IMDb.
26. Como usuario, quiero que los rótulos («Dirección», «Elenco», «Audio», «Subtítulos», «Recomendación», «Época») estén escritos con mayúscula inicial, para que sin la mayúscula forzada no queden en minúscula.

### Filtros del catálogo

27. Como usuario en «Sin ver» o «Vistas», quiero que al buscar un texto el filtro de vistas pase a «Todas», para encontrar la película aunque esté del otro lado del filtro.
28. Como usuario en «Sin ver» o «Vistas», quiero que al elegir una época el filtro de vistas pase a «Todas», para ver todo lo de esa época.
29. Como usuario, quiero que el subrayado de «Todas» se vea elegido cuando el filtro se restablece solo, para que la barra muestre la verdad.
30. Como usuario, quiero poder volver a elegir «Sin ver» o «Vistas» después de buscar o elegir época, y que entonces se combine con la búsqueda y la época, para acotar a propósito.
31. Como usuario, quiero que borrar la búsqueda o volver la época a «Todos» no cambie el filtro de vistas, porque eso no es pedir algo nuevo.
32. Como usuario, quiero que la Recomendada y su botón respeten estas reglas como hoy (se ocultan con búsqueda, «Vistas», época o incompletas), para que nada cambie ahí.

## Implementation Decisions

- **Panel de audio y subtítulos**: altura máxima relativa a la ventana (deja libre la barra superior y la de controles). Lo que scrollea es el contenido de las listas de audio y subtítulos; el bloque de estilo (tamaño, color, nota) queda fijo al pie del panel. La política de cierre pasa a cerrar con cualquier toque fuera del popup, no solo fuera de su padre. El botón que lo abre debe seguir actuando de interruptor: hay que evitar que el toque sobre él cierre el panel por fuera y su click lo reabra. Los toques que cierran el panel no deben llegar al área del video (no pausan ni muestran/ocultan controles).
- **Navegación** (actualizado 08/11/2026: como máximo tres niveles sobre el catálogo, película › persona › película; la persona siempre en el segundo nivel, la misma persona se reutiliza y otra la reemplaza; las películas sí pueden repetirse). Regla original: regla única para las pantallas de **persona** y de **detalle**: antes de apilar, se busca en la pila una pantalla del mismo tipo con la misma clave (nombre de la persona, id de la película). Si existe, se desapila hasta ella; si no, se apila como hoy. La regla vive en un solo lugar (helper de navegación compartido por Detalle y Persona, en el estilo de `duracion.js`), no duplicada en cada pantalla. El reproductor, el visor, editar y faltantes no cambian.
- **Barra del catálogo**: se quita el texto «PELIS» y el margen izquierdo del buscador que lo separaba. Todos los controles de la fila (buscador, opciones de vistas, selector de época, botón de recomendación, chip de incompletas) comparten la misma altura visible de 38 px de escala; el agente verifica en la app real cuál se desalinea y lo corrige en ese componente, sin tocar la escala general.
- **Botón de recomendación**: el texto pasa de «Recomendar» a «Recomendación». Comportamiento, lugar y reglas de visibilidad sin cambios (spec `recomendar-a-pedido`).
- **Hora actual**: se reutiliza el reloj por segundo que ya alimenta «Termina». Nueva línea «Hora: HH:MM» encima de «Termina HH:MM», mismo estilo de texto. Las dos se apilan en una columna dentro de la fila del seek.
- **Mayúsculas**: se quita la capitalización forzada en toda la app (botones, rótulos, títulos, tarjetas, diálogos, reproductor, visor). Los textos fijos se revisan para que queden en mayúscula inicial. El tracking pensado para mayúsculas puede reducirse donde quede abierto en minúscula. Se actualiza DESIGN.md: la tipografía de marca deja de existir y rótulo/titular dejan de ser «mayúscula».
- **Filtro de vistas**: el estado del filtro de vistas pasa a vivir en el modelo del catálogo (`ModeloCatalogo`), expuesto como propiedad con notificación, y la barra lo lee de ahí en lugar de guardarlo aparte. `filtrar` con texto no vacío y `filtrarPeriodo` con una época no vacía lo restablecen a «todas». `filtrar("")` y `filtrarPeriodo("")` no lo tocan. El cálculo de «sin filtros» de la barra pasa a leer la propiedad del modelo.
- **Glosario**: la definición de **Recomendada** menciona el botón «Recomendar»; se actualiza a «Recomendación».

## Testing Decisions

- Un buen test ejercita el comportamiento visible a través de la interfaz pública del módulo (slots y propiedades del modelo, filas resultantes), no campos privados ni el orden de llamadas.
- **Seam principal: `ModeloCatalogo`** (pytest, `tests/test_catalogo.py`). Tests nuevos:
  - en «noVistas», buscar un texto deja la propiedad de vistas en «todas» y las filas incluyen vistas y no vistas que coinciden;
  - en «vistas», elegir una época hace lo mismo;
  - buscar "" o elegir la época "" no cambia el filtro de vistas;
  - elegir «noVistas» después de buscar combina ambos filtros.
  - `test_filtros_de_vistas_periodo_y_busqueda_se_combinan` hoy elige vistas antes de buscar; hay que reescribirlo con el orden nuevo (vistas después de la búsqueda/época) para que siga probando la combinación.
  - Prior art: `test_filtros_de_vistas_periodo_y_busqueda_se_combinan`, `test_periodo_elegido_que_desaparece_vuelve_a_todos` y el helper `catalogo(...)` del mismo archivo.
- **Sin tests automáticos de QML** (el repo no tiene): navegación, panel, hora, alturas y mayúsculas se verifican a mano en la app real. Recorrido mínimo: película › director › otra película › director (vuelve al director existente) › otra película › Volver (director) › Volver (primera película); panel con muchas pistas en ventana chica; toque fuera del panel; toque en el botón con el panel abierto.

## Out of Scope

- **«Cambiar colores de pelis»**: el pedido no dice qué colores ni dónde (paleta general, tarjetas, etiqueta de vista). Queda fuera de esta spec hasta definir la dirección (por ejemplo con `/impeccable colorize`); se abre aparte.
- Cambiar fuentes o tamaños de letra más allá de ajustar el tracking por la falta de mayúsculas.
- Historial de navegación más allá de la pila (atrás/adelante, breadcrumb).
- Un reloj en otras pantallas que no sean el reproductor.
- Cambios en el criterio o el ciclo de vida de la Recomendada.

## Further Notes

- Pedido original (2026-11-08), en una sola tanda: max-height y scroll del panel de subtítulos y cierre al tocar fuera; colores; navegación sin pantallas repetidas; altura del botón «Recomendar»; «Hora: HH:MM»; sin mayúsculas, sin «PELIS», «Recomendación»; buscar o filtrar por época pasa a «Todas».
- Los ítems son independientes; conviene un ticket por bloque (panel, navegación, barra, hora, mayúsculas, filtro).
