# Disco externo: compartir la biblioteca con los discos

Status: needs-triage

Anotada el 2026-11-14. Decisiones cerradas el 2026-11-14.

## Idea
La app de la compu suma al catálogo las pelis de uno o varios discos externos, sin copiarlas. Cada disco trae su propia copia de Pelis con su propia db.

## Contexto
La app es portable: la carpeta `app/` (con `pelis.db`, `pelis.toml`, `preferencias.ini`) viaja con el disco. La biblioteca de cada app se resuelve con `config.cargar` (gana `preferencias.ini`, después `pelis.toml`). La db no tiene número de versión: `db.py` migra mirando columnas con `PRAGMA table_info`.

## Decisiones

### Qué se comparte
- Solo el catálogo visible. Vistas, progreso y metadatos de cada peli viven en la db de donde está la peli y no se sincronizan.
- La db de la compu no guarda ningún registro de las pelis de un disco. Al sacar el disco, desaparecen de la app.
- Varios discos a la vez, cada uno como una fuente de pelis.

### Detección
- Automática: un disco entra si en su raíz tiene `app/` con `pelis.db`, sin importar letra de unidad ni punto de montaje.
- Manual: «Agregar disco…» en el menú «…» abre el selector de carpeta. La ruta se guarda en `preferencias.ini` (no en la db) y se reintenta en cada arranque; si el disco no está montado, se omite en silencio. Los agregados a mano se pueden quitar de una lista; los detectados solos no se guardan.
- Ocultar y mostrar: cualquier disco se puede ocultar desde esa lista. Se guarda en `preferencias.ini` por identificador (ruta de `app/` más etiqueta del volumen).
- Carpeta de películas del disco: se resuelve con `config.cargar` sobre su `app/`. Si no resuelve ninguna biblioteca, el disco se omite con un aviso.
- Se descarta un disco cuya biblioteca o cuya `app/` sea la de esta misma app (comparando rutas reales resueltas), para no duplicar.
- Funciona aunque la compu no haya elegido biblioteca: la pantalla «no encuentro la biblioteca» no tapa los discos.

### Sondeo
- Con la app abierta, un sondeo con `QStorageInfo` cada ~3 segundos detecta discos que entran o salen; las pelis aparecen o desaparecen sin reiniciar.
- Durante una reproducción no se buscan discos. Solo se verifica, cada pocos segundos, que siga el disco de la peli en curso.
- Si se saca ese disco, se pausa y se avisa «Se sacó el disco X», sin intentar guardar el progreso.
- Al terminar la reproducción, se hace un sondeo completo unos 10 segundos después.

### Catálogo
- Una peli repetida entre compu y disco da dos tarjetas, sin cruzar por IMDb ID. Las que vienen de un disco llevan una insignia con la etiqueta del volumen (o el nombre de la carpeta de montaje si no tiene); las de la compu, sin insignia. El detalle muestra de dónde viene.
- Las pelis del disco entran en búsqueda, filtros, «Recomendación» y «Pre-selección».
- «Escanear biblioteca» solo toca la biblioteca de la compu; los discos los escanea su propia app.
- La papelera de una peli del disco la mueve a la papelera de ese disco. También está disponible desde la app del propio disco.

### Escritura y versiones
- Las ediciones de una peli del disco (vista, progreso, metadatos, póster, capturas) se guardan en la db y la carpeta del disco.
- La compu nunca migra la db del disco.
- El esquema se compara por tablas y columnas contra las que la compu espera, sin tocar `db.py` ni agregar `user_version`. Si coinciden, lectura y escritura; si no, solo lectura.
- La db se abre con un tiempo de espera corto. Si está bloqueada (por ejemplo, la app del disco abierta), solo lectura en vez de fallar. Cuando se libera, el próximo sondeo la reabre en lectura y escritura.
- Un disco en solo lectura se puede ver, reproducir y abrir en su carpeta. Todo lo que escribe (vista, progreso, editar metadatos, póster, capturas, papelera) se deshabilita. Un solo aviso al abrir la fuente en ese modo.

## Fuera de alcance
- Sincronizar vistas o progreso entre compu y disco.
- Copiar pelis entre compu y disco.
- Ponerle versión a la db.
