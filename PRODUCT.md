# Product

<!-- impeccable:product-schema 1 -->

## Platform

desktop

Aplicación de escritorio nativa (no web): Python 3.12 + PySide6 con QML (Qt Quick Controls, estilo Material oscuro) y QtMultimedia. Corre en Windows y Linux Mint. Fuera de los valores del esquema (web / ios / android / adaptive): las convenciones de interacción son las de una app de escritorio con mouse y teclado, más uso a distancia en una TV.

## Users

- El dueño de la biblioteca y su familia y amigos. Hay usuarios no técnicos: la interfaz tiene que entenderse sola y no exponer términos internos (OMDb, TMDb, `pelis.json`, "escanear" como concepto técnico) más de lo necesario.
- Tarea: elegir una película de la colección propia y verla, o retomar una que quedó a medias.

## Product Purpose

Catálogo y reproductor de una biblioteca personal de películas guardada en disco (una carpeta por película), sin servidor y sin cuentas. Éxito: abrir la app y estar viendo algo en pocos pasos, sobre todo retomando lo que se estaba viendo, y poder recorrer la colección para decidir qué ver.

## Positioning

Proyecto personal, no comercial: no se vende, no se distribuye al público, no compite con nada ni necesita convencer a nadie. Existe para uso propio y de la familia y amigos. Lo que lo define es que funciona sobre los archivos propios, sin servidor ni cuentas: la biblioteca, la base y los metadatos viven en el disco (incluso un disco compartido entre Windows y Linux) y el catálogo y la reproducción andan sin internet.

## Operating Context

- Escenario actual: PC de escritorio (monitor cerca, mouse y teclado). El uso en una TV a distancia queda para más adelante y hoy no es prioridad; no hay que romperlo, pero no guía las decisiones.
- Flujo: catálogo (grilla de posters) → detalle → reproductor en la misma ventana; pantalla completa en la misma ventana.
- El escaneo de la biblioteca se dispara a mano y muestra un informe al final.
- Internet solo para metadatos (OMDb, sinopsis en español de TMDb) y posters; todo lo demás funciona sin red.

## Capabilities and Constraints

- Catálogo con poster, título (siempre el nombre de la carpeta), año, progreso y marca de vista.
- Detalle: sinopsis (en español cuando TMDb la tiene), año, género, país, director, elenco; reproducir / continuar desde X, marcar como vista, abrir con el reproductor del sistema.
- Reproductor propio: play/pausa, seek, ±10 s, pista de audio, subtítulos (externos `.srt`/`.ass`/`.vtt` y embebidos, dibujados por un overlay propio), pantalla completa, controles que se ocultan a los 3 s. Atajos: espacio, ←/→, F, doble click, Esc.
- Progreso guardado al pausar, salir y cerrar; retoma exactamente donde quedó.
- Interfaz en español (rioplatense en los textos).
- Fases siguientes ya planificadas (`.scratch/`): filtros y personas clickeables, edición de metadatos y corregir match, ajustes de subtítulos y hora estimada de fin, galería de posters, papelera.
- Sin decidir: manejo con control remoto específico (más allá del teclado).

## Brand Commitments

- Nombre: "Pelis".
- El home (catálogo) se mantiene como está: grilla donde cada película muestra solo poster, título y año. Las marcas de progreso y de vista aparecen sobre el poster solo cuando corresponden. No sumar más datos a la tarjeta.

## Evidence on Hand

- Biblioteca real de unas 70 películas, muchas no anglosajonas (coreanas, japonesas, francesas, argentinas). Posters de OMDb o existentes en cada carpeta.
- No hay logo, marca ni assets propios. No inventar testimonios ni métricas.

## Product Principles

1. Retomar primero: lo que quedó a medias tiene que estar a un paso.
2. Explorar con placer: la colección se recorre por sus posters y su información, no por listas técnicas.
3. Se explica sola: alguien que nunca la usó la entiende sin ayuda; lo técnico queda escondido o explicado en lenguaje común.
4. Cómoda en el escritorio: se usa con mouse y también con teclado.
5. Nada se pierde: progreso, vistas y metadatos se guardan solos.

## Accessibility & Inclusion

- Uso con teclado y foco visible.
- (Futuro) Textos y controles legibles a distancia de sala, si se usa en una TV.
