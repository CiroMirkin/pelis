# Casos de uso

Pelis es un catálogo y reproductor de escritorio para una colección propia de películas guardada en un disco. Sirve para elegir qué ver, mirarlo y retomar lo que quedó a medias, sin cuentas ni servidor y sin depender de internet salvo para traer datos y pósters.

## Actores

* **Espectador**: cualquiera que usa la app para elegir una película, verla, retomarla o marcarla como vista (el dueño, su familia, sus amigos).
* **Dueño de la biblioteca**: arma las carpetas de películas en el disco, busca sus datos, corrige los que vinieron mal y ordena las que cambiaron de lugar. La app no distingue permisos: es un rol, no una cuenta.

## Resumen

* **[Biblioteca](#biblioteca)**: una carpeta por película en el disco; el nombre de la carpeta es el título.
* **[Películas nuevas al abrir](#películas-nuevas-al-abrir)**: la app suma sola, sin internet, lo que se copió desde la última vez.
* **[Escanear biblioteca](#escanear-biblioteca)**: busca en internet los datos y pósters de las películas que no los tienen, y muestra un informe.
* **[Catálogo](#catálogo)**: grilla de pósters con búsqueda y filtros por vistas, época y datos incompletos.
* **[Recomendación del día](#recomendación-del-día)**: al abrir, sugiere al azar una película que no se vio ni se empezó.
* **[Detalle](#detalle)**: sinopsis, datos, dirección y elenco, a qué hora termina, y acceso a reproducir.
* **[Personas](#personas)**: ver todas las películas de la biblioteca de un director o actor.
* **[Reproductor](#reproductor)**: reproducción con audio y subtítulos elegidos solos y pantalla completa.
* **[Progreso y vistas](#progreso-y-vistas)**: se recuerda dónde quedó cada película y cuáles ya se vieron.
* **[Editar datos](#editar-datos)**: corregir o completar los datos de una película, desde IMDb o a mano.
* **[Pósters](#pósters)**: cada película usa sus propias imágenes y va rotando entre ellas.
* **[Faltantes](#faltantes)**: recuperar una película cuya carpeta cambió de nombre o de lugar sin perder su historial.

## Biblioteca

* Como dueño de la biblioteca, agrego una película creando una carpeta para ella dentro de la biblioteca, con su video adentro.
  * Cada película es una carpeta directa de la biblioteca, con exactamente un video. Una carpeta sin video o con más de uno no se suma y aparece en el informe del escaneo como "carpeta con problemas".
  * El nombre de la carpeta es el título que se muestra. El año puede ir al final o al principio: `Alien (1979)` o `(1979) Alien`.
  * Los subtítulos van sueltos al lado del video, nunca en subcarpetas.
  * Si la película se equivoca de datos al buscarlos, se puede indicar su código de IMDb en el nombre de la carpeta, por ejemplo `Alien (1979) [tt0078748]`.

* Como dueño de la biblioteca, puedo copiar una película de una biblioteca a otra copiando su carpeta entera.
  * Los datos de la película viajan dentro de su carpeta: en la otra biblioteca entra con todos sus datos y su póster, sin consultar internet.
  * Lo visto y el progreso no viajan: son de cada biblioteca.
  * Si la carpeta copiada no trae sus datos, aparece con el título de la carpeta hasta el próximo escaneo.

## Películas nuevas al abrir

* Como espectador, al abrir la app veo las películas que se copiaron a la biblioteca desde la última vez, sin hacer nada.
  * No usa internet.
  * Las que traen sus datos entran completas; las demás entran con el título de la carpeta y quedan pendientes de datos hasta el próximo escaneo.
  * Un aviso dice cuántas se sumaron ("Se sumaron 3 películas") y se va solo a los 8 segundos.
  * Una película que había desaparecido y volvió a estar se vuelve a mostrar.
  * Una carpeta renombrada se reconoce como la misma película si tiene su código de IMDb, y conserva su progreso y si está vista.
  * Las carpetas que no están no se ocultan al abrir: un disco desconectado no hace desaparecer nada.

## Escanear biblioteca

* Como dueño de la biblioteca, escaneo la biblioteca para buscar los datos de las películas que no los tienen.
  * Se dispara siempre a mano.
  * Muestra el avance, película por película ("12 de 70").
  * Usa internet. Si se corta, las que faltan quedan pendientes y se reintentan en el próximo escaneo.
  * Para encontrar cada película prueba, en orden: el código de IMDb si lo tiene, el título y año de la carpeta, el título y año del nombre del video, y por último el título solo.
  * La sinopsis se trae en español (primero latino, después de España); si no hay en español, queda en inglés.
  * El título siempre sigue siendo el de la carpeta; el año de la carpeta también gana, y si la carpeta no lo tiene se completa con el encontrado.
  * Si la película no tiene póster propio, se descarga uno.
  * Si se pide escanear mientras la app todavía está sumando las películas nuevas al abrir, el escaneo arranca apenas termina.

* Como dueño de la biblioteca, al terminar el escaneo veo un informe.
  * Cuántas películas se agregaron.
  * Cuáles tomaron los datos que ya traían en su carpeta.
  * Cuáles no se encontraron (hay que buscarlas o cargarlas a mano).
  * Cuáles quedaron pendientes por falta de internet.
  * Cuáles faltan porque su carpeta ya no está: se ocultan del catálogo y se pueden reasignar (ver Faltantes).
  * Cuáles reaparecieron y cuáles cambiaron de carpeta conservando progreso y vista.
  * Qué carpetas tienen problemas y por qué ("no tiene video", "tiene 2 videos").

## Catálogo

* Como espectador, veo todas las películas en una grilla con su póster, título y año.
  * Las que están a medias aparecen primero, con una barra de progreso sobre el póster; después las que no vi; las vistas al final, marcadas. Dentro de cada grupo, por título alfabético.
  * Se ve cuántas películas hay en pantalla ("70 películas").
  * Si la biblioteca está vacía, se indica cómo cargarla.

* Como espectador, puedo buscar por título, director o reparto.
  * No distingue mayúsculas ni acentos: "almodovar" encuentra "Almodóvar".
  * Con varias palabras, muestra las películas que tienen todas.
  * Si nada coincide, se avisa.

* Como espectador, puedo filtrar por Todas, Sin ver o Vistas.

* Como espectador, puedo filtrar por época.
  * Las décadas anteriores a la actual van agrupadas ("Los 60s", "Los 2000").
  * Cada uno de los últimos 4 años, incluido el actual, va aparte.
  * Solo aparecen las épocas que tienen películas en la biblioteca, y el filtro solo se muestra si hay más de una.

* Como dueño de la biblioteca, puedo ver solo las películas a las que les faltan datos o póster.
  * Se ve cuántas hay; si no hay ninguna, el filtro no se ofrece.

* Como espectador, puedo marcar de una vez todas las que faltan ver.
  * Pide confirmación diciendo cuántas se van a marcar.
  * Solo se ofrece si queda alguna sin ver.

* Como espectador, puedo renovar en el momento el póster de las películas que tienen más de uno.
  * Avisa cuántas se renovaron, o que no había ninguna para renovar.
  * No está disponible mientras se escanea.

## Recomendación del día

* Como espectador, al abrir la app veo arriba del catálogo una película recomendada, con su póster, título, año, género y duración.
  * Se elige al azar entre las que no vi ni empecé, una vez por cada vez que abro la app.
  * Tocándola abro su detalle.
  * Desaparece si la descarto, si la empiezo a ver o si la marco como vista (sola o junto con todas las demás), y no vuelve hasta la próxima vez que abra la app.
  * Se oculta mientras busco o filtro por vistas, por época o por datos incompletos.

## Detalle

* Como espectador, al tocar una película veo su detalle: póster, título, año, género, país (con bandera), sinopsis, dirección y elenco.
  * Si le faltan datos, se explica por qué y cómo completarlos (escanear con internet, o buscarla o cargarla a mano).
  * Un póster agregado a la carpeta aparece al abrir el detalle, sin escanear.

* Como espectador, desde el detalle reproduzco la película.
  * Si la había empezado, se ofrece continuar desde donde quedó (por ejemplo, desde 1:12:30).

* Como espectador, veo a qué hora termina la película si la empiezo o la sigo ahora ("Si seguís ahora, termina a las 23:40").
  * Se calcula con lo que falta ver y se actualiza solo con el paso del tiempo.

* Como espectador, puedo marcar o desmarcar la película como vista.

* Como espectador, puedo abrir la carpeta de la película o abrirla con otro reproductor de la computadora.

## Personas

* Como espectador, en el detalle puedo tocar a un director o actor que está en otra película de la biblioteca y ver todas sus películas.
  * Solo se pueden tocar los que aparecen en más de una película; se distinguen con un subrayado.
  * Sus películas se ordenan por año y muestran si participó en la dirección, el elenco o ambos.
  * Desde ahí puedo abrir el detalle de cualquiera de ellas.

## Reproductor

* Como espectador, miro la película en el reproductor de la app, en la misma ventana.
  * Puedo pausar, adelantar o atrasar (de a 10 segundos o de a 1 minuto) e ir a cualquier momento de la película.
  * Puedo verla en pantalla completa.
  * Los controles se ocultan solos a los 3 segundos sin mover el mouse.
  * Muestra a qué hora termina si sigo mirando.
  * Si el video no se puede reproducir, se informa el motivo.

* Como espectador, ajusto el volumen o silencio el sonido.
  * El volumen y el silencio se recuerdan para todas las películas.

* Como espectador, al empezar una película el audio y los subtítulos ya vienen elegidos en el idioma preferido (español por defecto).
  * Para el audio, elige la primera pista en ese idioma; si no hay, deja la que trae el video.
  * Para los subtítulos, en orden: un archivo de subtítulos con el mismo nombre que el video, uno externo en el idioma preferido, uno incluido en el video en ese idioma, o el único externo si hay uno solo. Si nada aplica, arranca sin subtítulos.

* Como espectador, mientras miro cambio la pista de audio y el subtítulo, o los apago.
  * Se pueden usar subtítulos sueltos en la carpeta (`.srt`, `.ass`, `.vtt`) o los que vienen dentro del video.
  * Si un archivo de subtítulos no se puede leer, se avisa y la película sigue sin subtítulos.

* Como espectador, cambio el tamaño y el color de los subtítulos.
  * Tamaño en 7 pasos, de la mitad al doble del normal; 5 colores (blanco, amarillo, celeste, verde, rosa).
  * Se recuerdan para todas las películas.
  * Solo se aplican a los subtítulos sueltos en la carpeta; los que vienen dentro del video usan su propio estilo.

## Progreso y vistas

* Como espectador, la app recuerda dónde quedé en cada película.
  * Se guarda al pausar, al salir del reproductor y al cerrar la app.
  * Al volver a reproducir, retoma exactamente donde quedó.

* Como espectador, marco una película como vista desde su detalle, o todas de una vez desde el catálogo.
  * Las vistas pasan al final del catálogo, con su marca.
  * Lo visto y el progreso son de cada biblioteca: no viajan al copiar la carpeta.

## Editar datos

* Como dueño de la biblioteca, traigo los datos de IMDb para corregir una película mal identificada o completar una que no se encontró.
  * Puedo buscar por título (opcionalmente con el año al final, "Alien 1979") y elegir entre los resultados, o pegar directamente su código (`tt0078748`) o su link de IMDb.
  * El título queda el de la película; el año pasa a ser el de la elegida.
  * Si la película tenía datos editados a mano o hay cambios sin guardar en el formulario, pide confirmación antes de reemplazarlos.
  * Si la película no tiene póster propio, también se trae el póster.
  * Necesita internet y la clave de búsqueda configurada; sin ella, se avisa y la búsqueda queda deshabilitada.

* Como dueño de la biblioteca, puedo volver a traer los datos de IMDb de una película que ya está identificada, para actualizarlos.

* Como dueño de la biblioteca, puedo cargar o corregir los datos a mano: título, año, país, género, dirección, elenco y sinopsis.
  * El título no puede quedar vacío.
  * El año es opcional; si se carga, tiene que estar entre 1880 y 2100.
  * Dirección y elenco van como nombres separados por comas.
  * Puedo descartar los cambios y volver a lo que estaba guardado.
  * Lo editado queda marcado como editado a mano y viaja con la carpeta de la película.

## Pósters

* Como dueño de la biblioteca, elijo el póster de una película poniendo una imagen en su carpeta.
  * Imágenes `.jpg`, `.jpeg` o `.png`. Cuentan las que están en una subcarpeta `posters`, y las sueltas en la carpeta cuyo nombre contiene "poster", "folder" o "cover" (en ese orden de preferencia).
  * Si no hay ninguna, se usa el póster descargado de internet.
  * Una imagen agregada después reemplaza al póster descargado; aparece al abrir el detalle o la app.
  * Si se borra el póster que se estaba usando, se toma otro de la carpeta.

* Como espectador, cada 7 días, al abrir la app, las películas con más de un póster cambian a otro al azar.
  * Siempre se elige uno distinto del actual.
  * Para sacar una imagen de la rotación, se borra de la carpeta.

## Faltantes

* Como dueño de la biblioteca, veo las películas cuya carpeta ya no está y les asigno la carpeta donde están ahora.
  * Se ve cuántas hay; si no hay ninguna, no se ofrece.
  * Para cada faltante elijo una de las carpetas de la biblioteca; las agregadas más recientemente van primero, y se pueden filtrar por nombre.
  * Pide confirmación antes de reasignar.
  * La película conserva su progreso, si está vista y sus datos; si no tenía datos y la carpeta nueva sí, toma los de la carpeta nueva.
  * La película de la carpeta nueva deja de figurar por separado: queda una sola.
  * Una carpeta renombrada que tiene su código de IMDb no necesita este paso: se reconoce sola al abrir la app o al escanear.
