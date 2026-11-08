---
name: Pelis
description: Catálogo y reproductor de una colección propia de películas, con la estética de un videoclub de barrio, reducida a lo esencial.
colors:
  noche: "#0b0b0b"
  estante: "#1b1d1c"
  caja: "#242625"
  linea: "#303231"
  crema: "#f4f4f2"
  tenue: "#8e908f"
  etiqueta: "#fd3a04"
  sobre-etiqueta: "#0b0b0b"
  tubo: "#ffffff"
  alerta: "#ff9a7a"
typography:
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

Pelis se ve como el videoclub del barrio cuando ya cerró: un local a oscuras, cajas en fila sobre estantes, etiquetas de alquiler pegadas y un solo color fuerte que marca lo que importa. Es nostálgico de los 70, 80 y 90 sin disfrazarse: nada de neón, cintas, rayas de VHS ni texturas. Lo retro está en la tipografía condensada de caja de video y en la etiqueta naranja; todo lo demás es mínimo, para que los posters sean los protagonistas.

La interfaz es oscura porque se usa de noche, en una pantalla, con las luces bajas. La densidad es baja y tranquila: una grilla de posters, pocas palabras, un botón principal por pantalla.

**Key Characteristics:**
- Fondo casi negro plano, sin degradés ni sombras de profundidad.
- Un solo color de acento, el naranja de etiqueta, reservado a la acción principal y a las marcas de estado.
- Títulos y rótulos en la condensada Archivo Narrow; textos de lectura en Atkinson Hyperlegible.
- Las cajas (posters) van en filas limpias, sin líneas entre ellas; la elegida se ilumina como bajo un tubo fluorescente.

## Colors

Paleta restringida: grises carbón neutros, blanco roto para el texto y un único naranja.

### Primary
- **Naranja etiqueta** (#fd3a04): la etiqueta de alquiler. Solo en el botón principal de cada pantalla (Reproducir / Continuar, Cerrar), en la tira de progreso y la etiqueta «Vista» de los posters, en el marcador de la pista elegida y en la barra de avance del reproductor. Sobre él, el texto va en noche (#0b0b0b), nunca en blanco: en blanco no se lee a tamaño de rótulo.

### Neutral
- **Noche** (#0b0b0b): fondo de todas las pantallas.
- **Estante** (#1b1d1c): superficies elevadas: paneles, diálogos.
- **Caja** (#242625): fondo del poster mientras carga o cuando no hay imagen; hover de botones secundarios y filas.
- **Línea** (#303231): separadores de barras y paneles, bordes de paneles.
- **Crema** (#f4f4f2, blanco roto; conserva el nombre): texto principal, bordes de botones secundarios (al 55%).
- **Tenue** (#8e908f): texto secundario: años, conteos, rótulos de sección, detalles de pistas.
- **Tubo** (#ffffff): el contorno de foco, la luz blanca del tubo fluorescente.
- **Alerta** (#ff9a7a): avisos y errores en texto.

### Named Rules
**La Regla de la Etiqueta Única.** El naranja marca una sola cosa por pantalla para hacer (el botón principal) y los estados de las películas. Ni los títulos ni los fondos van en naranja. Única excepción, pedida por el usuario: en el detalle, un botón redondo naranja de 52px con el play oscuro en la esquina inferior derecha del poster, que invita a hacer click en todo el poster: es un adorno, y es el poster el que hace lo mismo que el botón principal.

## Typography

**Display Font:** Archivo Narrow (variable, con fallback a la sans del sistema)
**Body Font:** Atkinson Hyperlegible (regular y negrita)

**Character:** La condensada es la letra del lomo de una caja de video y del cartel del local; la Atkinson, diseñada para leerse sin esfuerzo, carga las sinopsis, los títulos de las tarjetas y todo lo que se lee de corrido. Las dos van incluidas en la app (`src/pelis/qml/fuentes/`, licencia OFL), nunca dependen de internet.

### Hierarchy
- **Titular** (Archivo Narrow 700, 40px, interlineado 0.95): título de la película en el detalle.
- **Rótulo** (Archivo Narrow 600, 13–16px, tracking 0.2–0.4px): botones, años, la línea de año, género y país (separados con «*», nunca con «·»), rótulos «Dirección» / «Elenco» / «Audio» / «Subtítulos», tiempos del reproductor (con cifras tabulares).
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
**La Regla del Tubo.** Lo elegido no se levanta ni se agranda: se ilumina con un contorno de 3px en tubo (#ffffff), separado 4–6px del borde, que aparece en 140ms con salida suave.

## Shapes

Formas de caja de video: esquinas casi rectas (2px en posters, 3px en botones, 4px en paneles). Lo único redondo es la etiqueta «Vista», un círculo naranja pegado en diagonal (−10°) sobre la esquina del poster, como una etiqueta autoadhesiva, y el play sobre el poster del detalle.

## Components

### Buttons
- **Shape:** casi rectos (3px), 38px de alto.
- **Principal:** relleno naranja etiqueta, texto noche en rótulo, ícono oscuro. Uno por pantalla.
- **Secundario:** sin relleno, borde crema al 55% de 2px, texto crema; hover con fondo caja.
- **Foco:** contorno tubo de 3px, separado 4px.
- **Solo ícono:** mismos estilos con el texto oculto (play/pausa, pantalla completa).
- **Sin borde:** secundario sin contorno, para acciones menores como la ✕ de descartar; se marca solo con el fondo caja al pasar el mouse.
- **Íconos:** SVG propios de trazo recto (`src/pelis/qml/iconos/`), en crema y en versión oscura para el botón principal. Nunca caracteres Unicode.

### Cards / Containers
- **Tarjeta de película:** poster 2:3 sobre fondo caja, sin borde ni sombra; si no hay imagen, el título en rótulo tenue abajo a la izquierda. Debajo, solo título y año (compromiso fijo del producto). Progreso: tira naranja de 6px al pie, con el largo exacto de lo visto. Vista: etiqueta redonda naranja.
- **Panel de audio y subtítulos:** superficie estante con borde línea, dos columnas («Audio» | «Subtítulos») separadas por una línea; cada opción es una fila con el idioma en español y un detalle debajo; la elegida lleva un cuadrado naranja de 8px a la izquierda y el nombre en negrita. Las listas tienen una altura máxima y scrollean por separado; el bloque de estilo (tamaño, color, nota) queda fijo al pie. Un toque fuera del panel lo cierra.
- **Recomendación:** se pide con un botón secundario «Recomendación» en la barra del catálogo. Franja estante con borde línea entre la barra y la grilla: poster chico, rótulo «Recomendación» tenue, título en rótulo crema y año; toda la franja abre la ficha y una ✕ sin borde en la esquina superior derecha la descarta. Sin naranja: no compite con la acción principal.
- **Selector de época:** botón secundario con el valor elegido («Época», «Los 80s» o «2025») y una flecha; opciones «Todos», décadas hasta los 2000 («Los 60s», «Los 2000») y los últimos 4 años sueltos; despliega una lista estante con borde línea, filas de 36px en rótulo y la elegida marcada con el cuadrado naranja de 8px, como el panel de pistas. Se maneja con flechas, Enter y Esc.
- **Arranque:** mientras carga, la ventana noche vacía con un spinner naranja centrado, sin texto.
- **Diálogo de escaneo:** misma superficie estante, título en rótulo, fondo atenuado en noche al 80%.

### Navigation
- Barra superior de 68px sobre noche con una línea de 1px abajo. En el catálogo: el buscador a la izquierda, seguido del filtro «Todas / Sin ver / Vistas» (rótulos; el elegido en crema y subrayado en crema, los demás en tenue) y el selector de época, conteo y el botón «…» a la derecha («Escanear biblioteca» y, si hay, «Faltantes (N)»). En el detalle: «Volver» con flecha.
- **Botón «…» (BotonMas):** botón solo ícono con tres puntos que despliega las opciones secundarias de la pantalla en un menú estante con borde línea; cada opción lleva ícono y texto en rótulo, y se marca con fondo caja. En el detalle: «Editar datos» y «Abrir en otro reproductor».
- La grilla se recorre con las flechas y se abre con Enter; el detalle arranca con el foco en el botón principal.

## Do's and Don'ts

### Do:
- **Do** usar `Tema` para todo color, fuente y tamaño; ningún hex suelto en las pantallas.
- **Do** dejar que los posters pongan el color: la interfaz alrededor queda en noche, crema y tenue.
- **Do** escribir los idiomas de las pistas en español («Francés», «Inglés») y el resto del texto en lenguaje común.

### Don't:
- **Don't** usar rojo ni otro acento: el único acento es el naranja.
- **Don't** sumar datos a la tarjeta del catálogo más allá de poster, título, año y las marcas de progreso y vista.
- **Don't** usar selectores desplegables (ComboBox) para audio y subtítulos: van en el panel de dos columnas.
- **Don't** poner líneas o bordes entre las filas del catálogo: el usuario lo descartó.
- **Don't** agregar neón, ruido de VHS, texturas, degradés de color ni sombras para "hacer retro".
