# Validar el build de Windows desde el disco

Status: done

`tools\build_win.bat` arma `dist\Pelis-win\`, pero la verificación quedó a medias. Ya incluye el diseño nuevo.

## Criterio de terminado
- [x] El build copiado a `Pelis\app\win\` abre con `Pelis.bat` desde la raíz del disco, sin Python instalado
- [x] Escanea, muestra el catálogo y reproduce una película con subtítulos
- [x] Usa `pelis.db`, `pelis.toml` y `preferencias.ini` de `app\`

## Comments

- 07/11/2026: el usuario confirma que el build de Windows funciona.
