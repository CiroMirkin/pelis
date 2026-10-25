---
name: Pelis
description: Catálogo y reproductor de una colección propia de películas, con la estética de un videoclub de barrio, reducida a lo esencial.
colors:
  noche: "#0e131c"
  estante: "#161d2a"
  caja: "#1d2636"
  linea: "#2a3548"
  crema: "#f1ebde"
  tenue: "#9aa6bb"
  etiqueta: "#e0453a"
  sobre-etiqueta: "#0e131c"
  tubo: "#dfeaff"
  alerta: "#ff9a7a"
typography:
  marca:
    fontFamily: "Archivo Narrow"
    fontSize: "26px"
    fontWeight: 700
    letterSpacing: "2px"
  titular:
    fontFamily: "Archivo Narrow"
    fontSize: "40px"
    fontWeight: 700
    lineHeight: 0.95
  rotulo:
    fontFamily: "Archivo Narrow"
    fontSize: "15px"
    fontWeight: 600
    letterSpacing: "0.6px"
  cuerpo:
    fontFamily: "Atkinson Hyperlegible"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.35
  titulo-tarjeta:
    fontFamily: "Atkinson Hyperlegible"
    fontSize: "15px"
    fontWeight: 700
  detalle:
    fontFamily: "Atkinson Hyperlegible"
    fontSize: "12px"
    fontWeight: 400
rounded:
  caja: "2px"
  boton: "3px"
  panel: "4px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "20px"
  lg: "40px"
components:
  boton-principal:
    backgroundColor: "{colors.etiqueta}"
    textColor: "{colors.sobre-etiqueta}"
    typography: "{typography.rotulo}"
    rounded: "{rounded.boton}"
    height: "38px"
    padding: "0 16px 0 14px"
  boton-secundario:
    backgroundColor: "transparent"
    textColor: "{colors.crema}"
    typography: "{typography.rotulo}"
    rounded: "{rounded.boton}"
    height: "38px"
    padding: "0 16px 0 14px"
  boton-secundario-hover:
    backgroundColor: "{colors.caja}"
  tarjeta-pelicula:
    backgroundColor: "{colors.caja}"
    rounded: "{rounded.caja}"
  panel:
    backgroundColor: "{colors.estante}"
    rounded: "{rounded.panel}"
    padding: "20px"
---

# Design System: Pelis

## Overview

**Creative North Star: "El estante del videoclub, a la noche"**

Pelis se ve como el videoclub del barrio cuando ya cerró: un local azul oscuro, cajas en fila sobre estantes, etiquetas de alquiler pegadas y un solo color fuerte que marca lo que importa. Es nostálgico de los 70, 80 y 90 sin disfrazarse: nada de neón, cintas, rayas de VHS ni texturas. Lo retro está en la tipografía condensada de caja de video y en la etiqueta roja; todo lo demás es mínimo, para que los posters sean los protagonistas.

La interfaz es oscura porque se usa de noche, en una pantalla, con las luces bajas. La densidad es baja y tranquila: una grilla de posters, pocas palabras, un botón principal por pantalla.

**Key Characteristics:**
- Fondo azul noche plano, sin degradés ni sombras de profundidad.
- Un solo color de acento, el rojo de etiqueta, reservado a la acción principal y a las marcas de estado.
- Títulos y rótulos en mayúscula condensada (Archivo Narrow); textos de lectura en Atkinson Hyperlegible.
- Las cajas (posters) van en filas limpias, sin líneas entre ellas; la elegida se ilumina como bajo un tubo fluorescente.

## Colors

Paleta restringida: neutros azulados de local a la noche, crema de etiqueta para el texto y un único rojo.

### Primary
- **Rojo etiqueta** (#e0453a): la etiqueta de alquiler. Solo en el botón principal de cada pantalla (Reproducir / Continuar, Cerrar), en la tira de progreso y la etiqueta «VISTA» de los posters, en el marcador de la pista elegida y en la barra de avance del reproductor. Sobre él, el texto va en noche (#0e131c), nunca en blanco.

### Neutral
- **Noche** (#0e131c): fondo de todas las pantallas.
- **Estante** (#161d2a): superficies elevadas: paneles, diálogos.
- **Caja** (#1d2636): fondo del poster mientras carga o cuando no hay imagen; hover de botones secundarios y filas.
- **Línea** (#2a3548): separadores de barras y paneles, bordes de paneles.
- **Crema** (#f1ebde): texto principal, bordes de botones secundarios (al 55%).
- **Tenue** (#9aa6bb): texto secundario: años, conteos, rótulos de sección, detalles de pistas.
- **Tubo** (#dfeaff): el contorno de foco, la luz fría del tubo fluorescente.
- **Alerta** (#ff9a7a): avisos y errores en texto.

### Named Rules
**La Regla de la Etiqueta Única.** El rojo marca una sola cosa por pantalla para hacer (el botón principal) y los estados de las películas. Ni la marca «PELIS», ni los títulos, ni los fondos van en rojo. Única excepción, pedida por el usuario: en el detalle, un botón redondo rojo de 52px con el play oscuro en la esquina inferior derecha del poster, que hace lo mismo que el botón principal.

## Typography

**Display Font:** Archivo Narrow (variable, con fallback a la sans del sistema)
**Body Font:** Atkinson Hyperlegible (regular y negrita)

**Character:** La condensada en mayúscula es la letra del lomo de una caja de video y del cartel del local; la Atkinson, diseñada para leerse sin esfuerzo, carga las sinopsis, los títulos de las tarjetas y todo lo que se lee de corrido. Las dos van incluidas en la app (`src/pelis/qml/fuentes/`, licencia OFL), nunca dependen de internet.

### Hierarchy
- **Marca** (Archivo Narrow 700, 26px, tracking 2px, mayúscula): «PELIS» en la barra del catálogo, en crema.
- **Titular** (Archivo Narrow 700, 40px, interlineado 0.95, mayúscula): título de la película en el detalle.
- **Rótulo** (Archivo Narrow 600, 13–16px, tracking 0.6–1px, mayúscula): botones, años, la línea de año, género y país (separados con «*», nunca con «·»), rótulos «DIRECCIÓN» / «ELENCO» / «AUDIO» / «SUBTÍTULOS», tiempos del reproductor (con cifras tabulares).
- **Título de tarjeta** (Atkinson 700, 15px): título bajo cada poster.
- **Cuerpo** (Atkinson 400, 15px, interlineado 1.35, máximo ~860px de ancho): sinopsis, director, elenco, informes.
- **Detalle** (Atkinson 400, 12px): segunda línea de las opciones de pista (nombre de archivo, «SDH», «Forced»).
- **Subtítulos del video** (Atkinson 700, blanco con contorno negro, alto de ventana / 24, mínimo 20px).

### Named Rules
**La Regla del Lomo.** Los números (años, tiempos) van en la condensada: la Atkinson dibuja el cero tachado y en una app de películas eso se lee técnico.

## Layout

Márgenes laterales de 40px. El catálogo es una grilla que reparte el ancho en columnas de al menos 184px; los posters respetan 2:3 y las filas se separan solo por espacio, sin líneas. El detalle pone el poster (280×420) a la izquierda y la información a la derecha, con el texto limitado a ~860px. En el reproductor, los controles flotan sobre el video en una barra superior (68px) y una inferior (100px), con degradé a negro, y se ocultan a los 3 segundos. Todos los tamaños pasan por `Tema.px()`, una escala que hoy vale 1 y queda lista para un futuro modo TV.

## Elevation & Depth

Plano. No hay sombras: la profundidad se marca con capas de tono (noche → estante → caja) y bordes de 1px en línea. La única luz es la del foco.

### Named Rules
**La Regla del Tubo.** Lo elegido no se levanta ni se agranda: se ilumina con un contorno de 3px en tubo (#dfeaff), separado 4–6px del borde, que aparece en 140ms con salida suave.

## Shapes

Formas de caja de video: esquinas casi rectas (2px en posters, 3px en botones, 4px en paneles). Lo único redondo es la etiqueta «VISTA», un círculo rojo pegado en diagonal (−10°) sobre la esquina del poster, como una etiqueta autoadhesiva, y el play sobre el poster del detalle.

## Components

### Buttons
- **Shape:** casi rectos (3px), 38px de alto.
- **Principal:** relleno rojo etiqueta, texto noche en rótulo mayúscula, ícono oscuro. Uno por pantalla.
- **Secundario:** sin relleno, borde crema al 55% de 2px, texto crema; hover con fondo caja.
- **Foco:** contorno tubo de 3px, separado 4px.
- **Solo ícono:** mismos estilos con el texto oculto (play/pausa, pantalla completa).
- **Sin borde:** secundario sin contorno, para acciones menores como la ✕ de descartar; se marca solo con el fondo caja al pasar el mouse.
- **Íconos:** SVG propios de trazo recto (`src/pelis/qml/iconos/`), en crema y en versión oscura para el botón principal. Nunca caracteres Unicode.

### Cards / Containers
- **Tarjeta de película:** poster 2:3 sobre fondo caja, sin borde ni sombra; si no hay imagen, el título en rótulo mayúscula tenue abajo a la izquierda. Debajo, solo título y año (compromiso fijo del producto). Progreso: tira roja de 6px al pie, con el largo exacto de lo visto. Vista: etiqueta redonda roja.
- **Panel de audio y subtítulos:** superficie estante con borde línea, dos columnas («AUDIO» | «SUBTÍTULOS») separadas por una línea; cada opción es una fila con el idioma en español y un detalle debajo; la elegida lleva un cuadrado rojo de 8px a la izquierda y el nombre en negrita.
- **Recomendación del día:** franja estante con borde línea entre la barra y la grilla: poster chico, rótulo «RECOMENDACIÓN DEL DÍA» tenue, título en rótulo crema y año; toda la franja abre la ficha y una ✕ sin borde en la esquina superior derecha la descarta. Sin rojo: no compite con la acción principal.
- **Selector de época:** botón secundario con el valor elegido («ÉPOCA», «LOS 80S» o «2025») y una flecha; opciones «Todos», décadas («Los 60s», «Los 2000») y los últimos 4 años sueltos; despliega una lista estante con borde línea, filas de 36px en rótulo y la elegida marcada con el cuadrado rojo de 8px, como el panel de pistas. Se maneja con flechas, Enter y Esc.
- **Diálogo de escaneo:** misma superficie estante, título en rótulo, fondo atenuado en noche al 80%.

### Navigation
- Barra superior de 68px sobre noche con una línea de 1px abajo. En el catálogo: «PELIS» y el buscador a la izquierda, seguidos del filtro «TODAS / SIN VER / VISTAS» (rótulos; el elegido en crema y subrayado en crema, los demás en tenue) y el selector de época, conteo y el botón «…» a la derecha («Escanear biblioteca» y, si hay, «Faltantes (N)»). En el detalle: «Volver» con flecha.
- **Botón «…» (BotonMas):** botón solo ícono con tres puntos que despliega las opciones secundarias de la pantalla en un menú estante con borde línea; cada opción lleva ícono y texto en rótulo, y se marca con fondo caja. En el detalle: «Editar datos» y «Abrir en otro reproductor».
- La grilla se recorre con las flechas y se abre con Enter; el detalle arranca con el foco en el botón principal.

## Do's and Don'ts

### Do:
- **Do** usar `Tema` para todo color, fuente y tamaño; ningún hex suelto en las pantallas.
- **Do** dejar que los posters pongan el color: la interfaz alrededor queda en noche, crema y tenue.
- **Do** escribir los idiomas de las pistas en español («Francés», «Inglés») y el resto del texto en lenguaje común.

### Don't:
- **Don't** poner la marca «PELIS» en rojo ni en una etiqueta: el usuario lo descartó.
- **Don't** usar naranja: el acento es rojo.
- **Don't** sumar datos a la tarjeta del catálogo más allá de poster, título, año y las marcas de progreso y vista.
- **Don't** usar selectores desplegables (ComboBox) para audio y subtítulos: van en el panel de dos columnas.
- **Don't** poner líneas o bordes entre las filas del catálogo: el usuario lo descartó.
- **Don't** agregar neón, ruido de VHS, texturas, degradés de color ni sombras para "hacer retro".
