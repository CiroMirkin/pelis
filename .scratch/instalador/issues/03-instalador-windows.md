# Instalador de Windows con Inno Setup

Status: ready-for-human
Blocked by: 01

Ver "Windows" en la spec.

- Script de Inno Setup en `tools/` que toma `dist/Pelis-win` y arma `Pelis-windows-vX.Y.Z-setup.exe`
- Instala por usuario en `%LOCALAPPDATA%\Programs\Pelis`, sin administrador
- Acceso directo en el menú de inicio con el ícono, y desinstalador
- No crea `pelis.toml`, así la app corre en modo instalado
- Desinstalar borra solo el programa, nunca `%APPDATA%\Pelis` ni la biblioteca
- Acepta `/SILENT /CLOSEAPPLICATIONS` y reabre la app al terminar
- La versión sale de `__version__` (sin el sufijo `-rcN` si Inno no lo acepta, o en `AppVersion`)

## Criterio de terminado
- [ ] Se arma el `.exe` en `windows-latest`
- [ ] Instalada, la app arranca en modo instalado y guarda los datos en `%APPDATA%\Pelis`
- [ ] Desinstalar deja la base y las preferencias

## Comments

- 14/11/2026: `tools/pelis.iss` escrito (por usuario, sin UAC, español, acceso directo, `skipifsilent` en el «Abrir Pelis»). No se pudo compilar ni probar acá (no hay Windows). Se prueba con el workflow (issue 07) y a mano (issue 08).
