# Mostrar el país con su bandera en el detalle

Status: done

Ver la sección "País con bandera" de la spec.

## Qué
- Junto a `pais` en el detalle, la bandera de cada país; las coproducciones muestran varias en fila
- Mapeo del texto de OMDb a código ISO 3166-1 alfa-2, resuelto en el frontend (los nombres de OMDb no siempre son los del estándar, ej. "UK", "West Germany", "Soviet Union")
- Sacar la lista de países a cubrir de la base real (`SELECT DISTINCT pais FROM peliculas` en `dev/pelis.db`)
- Un país sin mapear se muestra solo como texto, sin romper nada

## Criterio de terminado
- [ ] Todos los países de la biblioteca real tienen bandera (ninguno sin mapear): se verifica en `02-verificar-navegar`, `dev/pelis.db` solo tiene 9 países y están todos
- [x] Una coproducción muestra varias banderas en fila

## Hecho (25/10/2026)
- Banderas SVG de [flag-icons](https://github.com/lipis/flag-icons) (MIT) en `src/pelis/qml/banderas/`, una por código ISO
- Mapeo en `src/pelis/qml/paises.js`: todos los países actuales más alias de OMDb ("UK", "USA", "Korea", "Czechia"…). Los históricos van al país sucesor: West/East Germany → Alemania, Soviet Union → Rusia, Yugoslavia → Serbia, Czechoslovakia → República Checa
- Solo la bandera; el nombre del país aparece como tooltip al pasar el mouse (pedido del usuario)
