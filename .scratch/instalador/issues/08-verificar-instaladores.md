# Verificar los instaladores a mano

Status: ready-for-human
Blocked by: 05, 06, 07

Ver "Pruebas" en la spec.

- Publicar una RC (`/version minor --rc` o la siguiente) con los cuatro archivos
- Windows: instalar el `-setup.exe`, abrir, elegir la biblioteca, desinstalar y reinstalar
- Linux: `apt install ./Pelis-linux-vX.deb`, abrir, elegir la biblioteca, desinstalar
- En cada sistema, abrir con `--prerelease`, publicar la RC siguiente y apretar «Actualizar»
- Probar cancelar la contraseña de `pkexec` en Linux
- Comprobar que una portable en un disco sigue andando y no mezcla sus datos con la instalada

## Criterio de terminado
- [ ] Instalar, abrir y desinstalar en Windows y en Linux, dejando los datos
- [ ] Actualizar de una RC a la siguiente en los dos sistemas
- [ ] Cancelar la contraseña en Linux deja la versión anterior abierta
- [ ] Portable e instalada conviven sin mezclar datos
