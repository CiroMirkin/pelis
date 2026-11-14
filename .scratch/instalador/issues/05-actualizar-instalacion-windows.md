# Actualizar una instalación de Windows

Status: ready-for-human
Blocked by: 02, 03

Ver "Windows" y "Cómo decide la app qué mecanismo usar" en la spec.

- Si `config.portable` es falso en Windows, «Actualizar» baja `-setup.exe` en vez del zip
- Verifica el hash contra `SHA256SUMS`; si no coincide, aborta sin tocar nada
- Avisa «Pelis se va a cerrar y volver a abrir», guarda el progreso y se cierra
- Lanza el instalador con `/SILENT /CLOSEAPPLICATIONS`; este reabre la app al terminar
- Sin `*.anterior` ni testigo
- Reusa la descarga con progreso y «Cancelar» del portable

## Criterio de terminado
- [x] Test sin red del flujo (descarga, hash, comando que se lanza) y del hash que no coincide
- [ ] La instalada queda en la versión nueva con base y preferencias intactas
- [x] Cortar la descarga deja la versión anterior funcionando

## Comments

- 14/11/2026: lógica en `src/pelis/instalador.py` (el puente la usa si `config.portable` es falso) y tests en `tests/test_instalador.py`. El `.bat` solo está probado como texto. Falta correr la actualización de verdad en Windows (issue 08).
