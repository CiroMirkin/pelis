@echo off
rem Lanzador de Pelis para Windows. Va en la raiz del disco, junto a pelis-app\ y Peliculas\.
set "APP=%~dp0pelis-app\app"
rem Una actualizacion que no llego a arrancar deja el testigo: vuelve la version anterior
if exist "%APP%\actualizando-win" (
    if exist "%APP%\win.anterior" (
        if exist "%APP%\win" rmdir /s /q "%APP%\win"
        move "%APP%\win.anterior" "%APP%\win" >nul
    )
    del "%APP%\actualizando-win"
)
if not exist "%APP%\win\pelis.exe" (
    echo No se encuentra "%APP%\win\pelis.exe".
    pause
    exit /b 1
)
if not exist "%APP%\pelis.toml" (
    echo Falta la configuracion "%APP%\pelis.toml".
    echo Copia "%APP%\pelis.toml.ejemplo" como pelis.toml y completa las claves.
    pause
    exit /b 1
)
start "" "%APP%\win\pelis.exe" %*
