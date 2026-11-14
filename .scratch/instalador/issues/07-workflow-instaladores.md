# El workflow publica los instaladores

Status: ready-for-human
Blocked by: 02, 03, 04

Ver "Nombres de los archivos de la Release" y "Pruebas" en la spec.

- El job de `windows-latest` arma el `-setup.exe` (instala Inno Setup si no viene en la imagen)
- El job de `ubuntu-24.04` arma el `.deb`
- La Release sube los cuatro archivos y un `SHA256SUMS` que los incluye
- El texto de la Release explica en una línea cuál elegir: instalador o portable
- El disparo manual deja los cuatro como artifacts sin crear Release

## Criterio de terminado
- [ ] Un tag publica la Release con los cuatro archivos y el `SHA256SUMS`
- [ ] El disparo manual deja los artifacts sin Release

## Comments

- 14/11/2026: `publicar.yml` arma el `-setup.exe` (instala Inno Setup con choco si falta) y el `.deb`, y los suma a artifacts, Release y `SHA256SUMS`. Falta correr el workflow (disparo manual y una RC).
