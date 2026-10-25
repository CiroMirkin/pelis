# Fase 3 — Editar

Corregir lo que OMDb no resolvió y recuperar registros faltantes.

**Puede ir antes que la fase 2** si tras el primer escaneo real más del 20% queda como "no encontrada".

## Alcance

### Carga y edición manual de metadatos
- El aviso "Metadatos no encontrados" lleva a un formulario para completarlos
- El mismo formulario edita metadatos existentes (vengan de OMDb o no): `titulo`, `year`, `sinopsis`, `pais`, `genero` directo; director y elenco agregando/quitando personas en `pelicula_personas` (reutiliza la persona si ya existe, la crea si no)
- `metadatos_origen` pasa a `'manual'` apenas se edita algo a mano

### Corregir match
- Botón en el detalle que busca en OMDb (`?s=`) y muestra candidatos para elegir
- Al elegir, se reemplazan los metadatos y se guarda el `omdb_id`

### Resincronizar
- Volver a consultar OMDb para una película
- Si `metadatos_origen = 'manual'`, pedir confirmación antes de pisar lo editado

### Reasignar faltantes
- **Automático:** en el escaneo, si aparece una carpeta nueva con el mismo `omdb_id` que un registro `faltante`, se reasigna ese registro (actualiza `folder_path` y `video_path`, vuelve a `activa`) conservando progreso, vista y personas
- **Manual:** vista "Faltantes" donde se elige un registro y se le asigna una de las carpetas nuevas detectadas
- Útil también cuando se renombra una carpeta para agregarle `[tt…]`

## Hecho (22/10/2026)
- Página «Editar datos» desde el detalle. Un solo campo para IMDb: con un ID o un link aplica esa película; con un título (opcionalmente con el año al final) lista candidatos de `?s=` para elegir. «Volver a traer» resincroniza por el `omdb_id` actual. Si los datos son manuales o el formulario tiene cambios sin guardar, se pide confirmación.
- Corregir match pisa el año con el de la película elegida; el título queda el de la carpeta (se cambia a mano). El poster se reemplaza solo si el actual es el bajado de OMDb.
- Director y elenco se editan como nombres separados por comas.
- `pelis.json` guarda también `titulo`, así un título editado a mano sobrevive a una base nueva.
- La reasignación automática usa el IMDb ID local (`pelis.json` o `[tt…]` del nombre), sin consultar OMDb, y corre también en la importación al abrir.
- La reasignación manual fusiona: el faltante toma la carpeta (y los posters) de una película activa, que se borra. Conserva progreso, vista y metadatos del faltante; si este no tenía metadatos, toma los de la otra.

## Criterio de terminado
Cubiertos por `tests/test_edicion.py`; falta probarlos en la app con la biblioteca real.
- [ ] Una película "no encontrada" se completa a mano y queda con `metadatos_origen = 'manual'`
- [ ] Corregir match reemplaza metadatos y personas
- [ ] Renombrar una carpeta con match y re-escanear reasigna sola, conservando progreso y vista
- [ ] Reasignación manual funciona para un registro sin `omdb_id`
