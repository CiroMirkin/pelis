@echo off
rem Lanzador de Pelis para Windows. Va en la raiz del disco, junto a pelis-app\ y Peliculas\.
set "APP=%~dp0pelis-app\app"
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
