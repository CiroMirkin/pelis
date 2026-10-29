# 06: Al corregir el match se reemplaza el póster de OMDb equivocado

**What to build:** cuando el usuario corrige el match de IMDb, el póster bajado de OMDb para la película equivocada se reemplaza por el de la correcta, aunque el póster actual sea una imagen propia. Hoy, si el actual es una imagen de la carpeta, no se baja nada. El caso: el escaneo matchea mal y baja `posters/poster.jpg` de otra película; el usuario agrega una imagen propia, que pasa a ser la actual; después corrige el match. El `poster.jpg` equivocado queda en la carpeta, sigue en la rotación y vuelve a aparecer cada 7 días. La única salida hoy es borrarlo a mano.

Regla nueva:
- Si la película tiene un póster bajado de OMDb, o no tiene ninguno, al corregir el match se baja el nuevo encima de `posters/poster.jpg`.
- Si la película solo tiene imágenes propias, no se baja nada (como hoy).
- El póster actual pasa a ser el bajado solo si el actual era de OMDb o no había ninguno; una imagen propia que es la actual se respeta.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Con un póster de OMDb en el set y una imagen propia como actual, corregir el match reemplaza el archivo de OMDb y la imagen propia sigue siendo la actual.
- [ ] Con el póster de OMDb como actual, corregir el match lo reemplaza y sigue siendo el actual (comportamiento de hoy).
- [ ] Con solo imágenes propias, corregir el match no baja nada.
- [ ] Tests en la suite de edición que cubren los tres casos, sin red.
