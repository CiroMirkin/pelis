# Calidad de la película en el detalle

Acotado en un grilling (2026-11-19).

## Problema
El detalle no dice si el archivo de video tiene buena o mala calidad. Hoy no se mide la resolución en ningún lado.

## Decisiones
- Calidad es técnica, del archivo de video: no es una nota de crítica ni una valoración del usuario.
- Criterio solo por resolución, sin bitrate: Alta si ancho >= 1280 o altura >= 720; Baja en cualquier otro caso (así una película 2.35:1 a 720p, de 1280x536, sale Alta).
- Fuente: `QMediaPlayer.metaData` (`Resolution`), leída en la misma pasada que la duración (`Puente._medir_duracion`), sin ffprobe. Se guarda en una columna nueva de la base.
- Se muestra solo en el detalle, en la línea de datos junto a la duración: `2019   *   Drama   *   2 h 5 min   *   Alta   *   🇦🇷`. No va en las tarjetas.
- Las películas que ya tienen duración pero no resolución se miden al abrir el detalle y en segundo plano al escanear, igual que la duración.
- En un disco en solo lectura no se mide, así que no se muestra.
- Si no se conoce o Qt no la entrega, el tramo se omite; sin texto de relleno.

## Fuera de alcance
- Filtro de calidad en el catálogo.
- Bitrate, códec o más de dos niveles.
