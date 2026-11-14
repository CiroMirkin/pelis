# 01: Ver las pelis de un disco externo en la app instalada

**What to build:** al insertar un disco con pelis, la app Pelis instalada en la compu suma esas pelis a su catálogo como opciones para ver. El disco también lleva su propia copia de la app Pelis, con su propia db.

**Blocked by:** None (can start immediately).

**Status:** needs-triage

## Decisiones

- Las pelis del disco se suman al catálogo de la compu, sin copiarlas: los archivos siguen en el disco.
- Los metadatos (y portadas) vienen de la db de la app donde está la peli, es decir, la del disco. La compu los lee de ahí.
- Las ediciones de una peli del disco (marcar vista, editar metadatos) se guardan en la db del disco.
- Al sacar el disco, sus pelis dejan de verse en la app de la compu y no queda ningún registro de ellas en la db de la compu.

## Preguntas abiertas

- ¿Cómo se detecta el disco al insertarlo (montaje, etiqueta, archivo marcador)?
