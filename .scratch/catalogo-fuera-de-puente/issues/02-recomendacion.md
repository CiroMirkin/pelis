# Recomendacion como máquina de estados

Status: done
Blocked by: 01

## Qué
- Clase `Recomendacion` en `catalogo.py` (ver spec); Puente la usa y emite `recomendadaChanged` cuando un método devuelve True

## Criterio de terminado
- [ ] Se elige una sola vez; con biblioteca vacía se reintenta; cerrada no se vuelve a elegir
- [ ] `empezo` con otro id no la toca; `poster` y `duracion` sin cambio devuelven False
