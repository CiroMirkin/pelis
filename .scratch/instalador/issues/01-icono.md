# Diseñar el ícono de Pelis

Status: done

Ver "Ícono" en la spec.

- Dibujar una colilla de cigarrillo en `assets/icono.svg`: silueta simple y legible a 16 px, filtro naranja, cuerpo crema y un poco de ceniza gris, sobre un fondo redondeado oscuro
- Script en `tools/` (sin dependencias nuevas) que genera de ahí el `.ico` de Windows (varios tamaños) y el `.png` de Linux
- Vista previa en PNG a 16, 32, 64 y 256 px para que el usuario la revise; se itera hasta que le guste
- Usarlo como ícono de la ventana de la app

## Criterio de terminado
- [x] El usuario aprobó el diseño
- [x] `assets/icono.svg` y `tools/icono.py`, que genera `assets/icono.ico` y `src/pelis/icono.png`
- [x] La ventana de la app muestra el ícono

## Comments

- 14/11/2026: el usuario aprobó el diseño: colilla en diagonal (35°), brasa arriba a la derecha, sin humo. El `.png` vive en `src/pelis/icono.png` porque la app lo carga (`setWindowIcon`) y `pelis.spec` lo empaqueta; el `.ico` es el del `.exe` (`icon=` en `pelis.spec`). Falta ver la ventana y el `.exe` con el ícono en un build real.
