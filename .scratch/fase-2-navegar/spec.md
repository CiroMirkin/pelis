# Fase 2 — Navegar

Encontrar qué ver dentro de la biblioteca.

## Estado
- Hecho (22/10/2026): filtro vista / no vista ("Todas / Sin ver / Vistas", combinado con el buscador) y recomendación aleatoria al iniciar (franja "Recomendación del día" arriba de la grilla).
- Hecho (22/10/2026): filtro por época, como selector desplegable en la barra, combinado con el filtro de vistas y el buscador. Opciones: "Todos", las décadas anteriores a la actual agrupadas ("Los 60s", "Los 2000", "Los 2010") y cada uno de los últimos 4 años, incluido el actual ("2023" … "2026"). Los años de la década actual anteriores a esos 4 (hoy 2020–2022) no tienen opción propia: solo se ven con "Todos". Solo aparecen las opciones con películas; el selector se oculta si hay una sola; si la elegida deja de existir tras un escaneo, vuelve a "Todos". Las películas sin año solo aparecen con "Todos".
- Decisión tomada al implementar: la recomendación excluye también las empezadas (ya aparecen primero en el catálogo) y desaparece al descartarla, al empezarla o al marcarla vista. Se oculta mientras hay una búsqueda o el filtro está en "Vistas".
- Hecho (25/10/2026): banderas solas, con el nombre del país como tooltip (un país sin mapear se muestra como texto); los países que ya no existen usan la bandera del país sucesor (Soviet Union → Rusia, West Germany → Alemania). Hecho (22/10/2026): botón de play sobre el poster del detalle; abrir ubicación («Abrir carpeta» en el menú «…» del detalle); personas clickeables (subrayado tenue que se enciende al pasar el mouse; el listado es una página con la grilla de sus películas por año y el rol en cada una). «Otra película» cuenta solo las activas, y ser director y actor de la misma cuenta una vez.

## Alcance

### Filtro vista / no vista
- Filtro en catálogo: Todas / Vistas / No vistas

### Filtro por década
- Calculado dinámicamente desde `year` (`(year / 10) * 10`), sin campo nuevo en SQLite
- Solo se muestran las décadas presentes en la biblioteca (nunca décadas vacías)
- Combinable con el filtro de vistas/no vistas

### Personas clickeables
- En el detalle, cada nombre es clickeable solo si esa persona participa en al menos otra película de la biblioteca (contando filas en `pelicula_personas` para esa persona, excluyendo la película actual)
- Sin coincidencias, el nombre se muestra como texto plano
- Al hacer click, lleva a un listado con todas las películas donde participa esa persona

### País con bandera
- Se muestra `pais` junto a su bandera
- Mapeo texto de OMDb → código ISO 3166-1 alfa-2, resuelto en el frontend (los nombres de OMDb no siempre coinciden con el estándar)
- Coproducciones: varias banderas en fila

### Abrir ubicación
- Botón que abre `folder_path` en el explorador del sistema (Explorador en Windows, `xdg-open` en Linux)

### Recomendación aleatoria al iniciar
- Al abrir la app, se elige al azar una película no vista (`watched = 0`, `estado = 'activa'`, sin progreso)
- Cambia en cada apertura
- Si no quedan películas sin ver, no se muestra recomendación

### Botón de play sobre el poster
- Pedido del usuario (22/10/2026): un botón de play en la esquina inferior derecha del poster **del detalle de la película** (solo ahí; las tarjetas del catálogo y la recomendación del día no lo llevan)
- Hace lo mismo que el botón principal: reproduce, o continúa desde donde quedó
- Se ve siempre (no depende del mouse)
- Estilo: botón redondo rojo etiqueta con el triángulo de play (oscuro, como el ícono del botón principal) centrado
- Es una excepción decidida por el usuario a la Regla de la Etiqueta Única (el detalle ya tiene el botón principal rojo): al implementarlo, anotarla en DESIGN.md

## Criterio de terminado
- [ ] Filtros de vistas y década funcionan combinados y nunca muestran décadas vacías
- [ ] Un actor presente en 2+ películas es clickeable y lleva al listado correcto; uno presente en 1 sola no
- [ ] Banderas correctas para todos los países de la biblioteca real (ninguno sin mapear)
- [ ] Abrir ubicación funciona en ambos sistemas
- [ ] El botón de play del poster del detalle reproduce (o continúa) igual que el botón principal
