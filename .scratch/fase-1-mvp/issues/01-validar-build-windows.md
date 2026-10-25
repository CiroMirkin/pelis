# Validar el build de Windows desde el disco

Status: ready-for-human

`tools\build_win.bat` arma `dist\Pelis-win\`, pero la verificación quedó a medias. Ya incluye el diseño nuevo.

## Criterio de terminado
- [ ] El build copiado a `Pelis\app\win\` abre con `Pelis.bat` desde la raíz del disco, sin Python instalado
- [ ] Escanea, muestra el catálogo y reproduce una película con subtítulos
- [ ] Usa `pelis.db`, `pelis.toml` y `preferencias.ini` de `app\`
