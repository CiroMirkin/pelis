# Actualizar una instalación de Linux

Status: ready-for-human
Blocked by: 02, 04

Ver "Linux" y "Cómo decide la app qué mecanismo usar" en la spec.

- Si `config.portable` es falso en Linux, «Actualizar» baja el `.deb`
- Verifica el hash contra `SHA256SUMS`; si no coincide, aborta sin tocar nada
- Avisa «Pelis se va a cerrar y volver a abrir» y se cierra
- Un script corre `pkexec apt install ./pelis_X.deb` y reabre `pelis` con los mismos argumentos
- Si el usuario cancela la contraseña o `apt` falla, el script reabre la versión anterior
- Si no hay `pkexec`, muestra el comando para correr a mano

## Criterio de terminado
- [x] Test del script con un `pkexec` y un `apt` falsos: éxito, cancelación y falla de `apt`
- [ ] La instalada queda en la versión nueva con base y preferencias intactas
- [ ] Cancelar la contraseña deja la versión anterior abierta

## Comments

- 14/11/2026: mismo módulo `instalador.py`. Usa `apt-get install -y` (hace lo mismo que `apt install` y sirve para scripts) y baja el `.deb` a una carpeta temporal. Falta probar la actualización real con una RC (issue 08).
