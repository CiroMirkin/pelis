# 01: La ventana abre con un spinner antes de cargar lo pesado

**What to build:** al abrir la app, la ventana aparece enseguida con un spinner, y el catálogo la reemplaza cuando terminó de cargar. Hoy no se ve nada hasta que están cargados QtMultimedia, `requests` y la interfaz completa.

**Blocked by:** None (can start immediately).

**Status:** done

## Criterio de terminado
- [x] La ventana se pinta antes de importar el puente y QtMultimedia.
- [x] El spinner sigue girando mientras se carga (corre en el hilo de render; en Linux el render loop es `threaded`).
- [x] Un error durante la carga cierra la app con el mensaje, sin spinner eterno (probado con una base corrupta).
- [x] Los `*.anterior` de una actualización se borran recién con el catálogo cargado.
- [x] Probarlo a ojo en Linux con el build en `~/Vídeos`.
- [x] Probarlo en Windows: ahí el render loop puede no ser el mismo.

## Comments

- 05/11/2026: el catálogo no era la causa: con 19 películas `db.catalogo` más tarjetas e incompletas tarda unos 10 ms. La espera es el arranque de PyInstaller, Qt y QtMultimedia.
- Tiempo hasta la primera señal de ventana, build en `~/Vídeos`, 3 corridas de cada uno, en una máquina con SSD:

  | | rc5 | con spinner |
  |---|---|---|
  | Frío (caché de la carpeta del programa vaciada) | 3,0–3,4 s | 2,1–3,1 s |
  | Tibio | 1,7–2,0 s | 1,2 s |

  El tiempo total hasta el catálogo no baja: cambia que antes se ve la ventana. Lo que queda antes de la ventana es PyInstaller y Qt; para bajarlo habría que recortar el paquete, y no está hecho.

- 07/11/2026: el usuario confirma que el spinner anda bien.
