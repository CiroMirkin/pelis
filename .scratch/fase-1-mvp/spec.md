# Fase 1 — MVP

Ver el catálogo, tener metadatos y retomar una película donde quedó, en Windows y en Linux Mint con la misma base.

Requiere: fase 0 terminada (biblioteca limpia, reproductor validado). Las reglas de escaneo, el esquema y la configuración están en [biblioteca-multimedia](../biblioteca-multimedia/spec.md).

## Estado
- Código en `src/pelis/`, tests en `tests/` (`pytest`). Se corre con `dev.bat`, que usa `dev/` como carpeta app (`dev/pelis.toml` apunta a `../Peliculas`).
- Hecho: config, esquema, escaneo con informe, cliente OMDb, catálogo, detalle, reproductor (audio/subs automáticos, overlay, controles, atajos), progreso al pausar/salir/cerrar, marcar vista, abrir con el reproductor del sistema, buscador (título, director y reparto), volumen con deslizador y atajos, películas en progreso primero.
- Decisión tomada al implementar: una carpeta `faltante` que vuelve a aparecer se reactiva en el siguiente escaneo (sale en el informe como "reaparecida").
- Primer escaneo real (21/10/2026): 127 encontradas, 19 no encontradas (13%). Queda por debajo del 20%: la fase 2 va antes que la 3.
- Empaquetado Windows: `tools\build_win.bat` arma `dist\Pelis-win\` (spec en `tools\pelis.spec`). El build se armó, pero la verificación quedó a medias (el subagente se detuvo) ; ya incluye el diseño nuevo (videoclub minimal).
- El volumen y el silencio se guardan en `preferencias.ini`, junto a `pelis.toml` (preferencia de la app, no de la biblioteca).
- Pendiente: validar el build desde el disco, Linux Mint e instalación local.

## Alcance

### Infraestructura
- Lectura de `pelis.toml`; `biblioteca` puede ser relativa a la carpeta de `pelis.toml` o absoluta
- Creación de `pelis.db` con el esquema completo (incluye tablas de fases posteriores, para no migrar)
- Tests con `pytest` para `nombres`, `escaneo` y `subtitulos` (sin UI), usando nombres reales de la biblioteca
- Empaquetado con PyInstaller `--onedir` en `app/win/` y `app/linux/` (último paso del MVP); lanzadores `Pelis.bat` y `pelis.sh`

### Escaneo
- Botón "Escanear biblioteca": abre un diálogo modal con el progreso ("12/87 · Alien (1979)"); el trabajo corre en un `QThread` para no congelar la UI
- Todas las reglas de escaneo del plan general: un video por carpeta, detección de poster, cascada de match con OMDb, estados `no_encontrada`/`pendiente`/`faltante`
- Informe al final: cantidad de películas agregadas, no encontradas, faltantes, y carpetas con problemas con su motivo
- Personas: director y elenco de OMDb se guardan normalizados en `personas` + `pelicula_personas`
- `pelis.json` por carpeta: se escribe tras cada match con OMDb y se lee al escanear carpetas nuevas o pendientes (reglas en el plan general). El informe lista las importadas desde el archivo y los archivos inválidos.

### Catálogo
- Grid de posters con el título de la carpeta
- Barra de progreso sobre el poster (`progreso_ms / duracion_ms`)
- Indicador de vista
- Las películas `faltante` no se muestran
- **Orden:** las películas en progreso van primero, después las sin ver y al final las vistas (22/10/2026); dentro de cada grupo, por título. "En progreso" = `progreso_ms > 0` y no marcada como vista. No cambia el esquema. El orden se mantiene con el buscador activo.
- **Buscador:** campo de búsqueda en la barra superior del catálogo que filtra la grilla mientras se escribe, con una pequeña espera (unos 300 ms desde la última tecla) para no refrescar la grilla con cada letra. Busca por título, director y reparto, sin distinguir mayúsculas ni acentos ("almodovar" encuentra "Almodóvar"). Atajo para ir al buscador (Ctrl+F o /) y Esc para limpiarlo. Sin resultados, un mensaje que lo diga. Las tarjetas no cambian: siguen mostrando solo poster, título y año. Más adelante se combina con los filtros de la fase 2.

### Detalle de película
- Título (de la carpeta), año, sinopsis, país (texto), género, director y elenco (texto plano)
- Aviso "Metadatos no encontrados" si no hubo match (sin formulario de edición; eso es fase 3)
- Botón reproducir
- Botón "Abrir con el reproductor del sistema", siempre visible (no guarda progreso). Es la salida para los archivos que QtMultimedia no pueda reproducir.
- Marcar / desmarcar como vista (manual; completa o limpia `watched_at`)

### Reproducción
- Reproductor propio sobre QtMultimedia, en la misma ventana (catálogo → detalle → reproductor). Esc o "Volver" regresan al detalle.
- Barra de controles superpuesta al video: play/pausa, seek con tiempo actual y total, selector de audio, selector de subtítulos, pantalla completa. Se oculta a los 3 s sin mover el mouse, junto con el cursor.
- Teclado: espacio = play/pausa, ←/→ = ±10 s, Ctrl+←/→ = ±1 min, F o doble click = pantalla completa, Esc = salir de pantalla completa (o volver, si no está en pantalla completa)
- Pantalla completa = la misma ventana en fullscreen
- **Volumen:** control de volumen en la barra del reproductor (botón de silencio + deslizador) y atajos de teclado: ↑/↓ = subir/bajar volumen, M = silenciar. Al cambiarlo, la barra se muestra con el nivel. El volumen elegido se recuerda entre películas.
- `duracion_ms` se obtiene del reproductor al cargar y se guarda

### Audio
- Al abrir se elige la pista que coincide con `audio_preferido`: primero por el idioma de los metadatos de la pista, después por su título usando la misma tabla de alias que los subtítulos. Si nada coincide, queda la pista por defecto del archivo.
- La elección manual no se guarda.

### Subtítulos
- **Los `.srt` externos son requisito obligatorio del MVP.**
- Externos: `.srt`/`.ass`/`.vtt` al mismo nivel que el video (nunca en subcarpetas), buscados al abrir el reproductor. Se leen con `pysubs2` probando UTF-8 (con o sin BOM) y, si falla, cp1252.
- Embebidos: se listan desde el archivo y su texto se toma del `videoSink`.
- Todos se dibujan con el mismo overlay propio (un solo estilo).
- Alias de idioma (en el nombre del archivo o en el título de la pista): `es`, `esp`, `spa`, `spanish`, `español`, `latino`, `castellano` → español; `en`, `eng`, `english` → inglés
- Activación automática al abrir, en orden:
  1. El externo con el mismo nombre que el video
  2. Un externo que coincide con `subs_preferido` por idioma en el nombre
  3. Un embebido cuyo idioma coincide con `subs_preferido`
  4. El único externo, si hay uno solo
  5. Ninguno

### Progreso
- `progreso_ms` se guarda **solo** al pausar y al cerrar el reproductor o la app (sin guardado periódico)
- Al reabrir, retoma exactamente donde quedó (incluso si es en los créditos)

## Fuera de alcance
Filtros, banderas, personas clickeables, edición de metadatos, corregir match, galería de posters, papelera, estilo de subtítulos, hora estimada de fin.

## Criterio de terminado
- [ ] "Escanear biblioteca" sobre la biblioteca real carga todo; cada carpeta termina importada (con metadatos o como "no encontrada") o listada en el informe de problemas
- [ ] Grid con posters; detalle con todos los campos
- [ ] Reproducir → pausar → cerrar → reabrir retoma en la misma posición, en Windows y en Linux Mint
- [ ] Marcar una película como vista en Windows y verla marcada en Linux Mint (prueba de base compartida + rutas relativas)
- [ ] La barra de progreso del poster refleja el avance
- [ ] Instalación local: con `app\` en una unidad interna y `biblioteca` absoluta apuntando a otra, escanea y reproduce igual
- [ ] Un `.srt` externo en Windows-1252 se ve con acentos y `ñ` correctos sin tocar nada
- [ ] La activación automática de audio y subtítulos elige lo esperado en al menos una película con varias pistas
- [ ] `Pelis.bat` y `pelis.sh` abren el build de PyInstaller desde la raíz del disco
- [ ] Con una base nueva sobre la misma biblioteca, el escaneo importa todo desde los `pelis.json` sin consultar OMDb
- [ ] Las películas en progreso aparecen primero
- [ ] El buscador encuentra películas por título, director y reparto, ignorando mayúsculas y acentos
- [ ] El volumen se controla con el deslizador y con ↑/↓/M
- [ ] Medir el porcentaje de "no encontradas" para decidir si la fase 3 pasa antes que la 2
