# Nombres nuevos de los portables

Status: done

Ver "Nombres de los archivos de la Release" en la spec.

- `Pelis-windows-vX.Y.Z-portable.zip` y `Pelis-linux-vX.Y.Z-portable.tar.gz` en `.github/workflows/publicar.yml`
- `Instalacion.paquete` en `actualizacion.py` busca los nombres nuevos; sin fallback a los viejos
- El texto de la Release nombra los portables «(Portable)»
- Actualizar los tests que usan los nombres viejos

## Criterio de terminado
- [x] El workflow sube los portables con los nombres nuevos y los incluye en `SHA256SUMS`
- [x] Un portable se actualiza buscando el nombre nuevo (test sin red)

## Comments

- 14/11/2026: nombres nuevos en `publicar.yml` y `Instalacion.paquete`, tests actualizados (34 pasan). El texto de la Release agrega al final una línea que explica qué es «(Portable)»; el issue 07 la completa con el instalador.
