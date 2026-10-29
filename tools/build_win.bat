@echo off
rem Arma dist\Pelis-win\ (listo para copiar a la raiz del disco) con PyInstaller.
setlocal
cd /d "%~dp0.."
where uv >nul 2>nul
if errorlevel 1 (
    echo Falta uv: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)
set "UV_PROJECT_ENVIRONMENT=.venv"
uv run --locked python -m PyInstaller --noconfirm --clean --distpath build\dist --workpath build\work tools\pelis.spec
if errorlevel 1 exit /b 1

set "SALIDA=dist\Pelis-win"
if exist "%SALIDA%" rmdir /s /q "%SALIDA%"
mkdir "%SALIDA%\pelis-app\app"
robocopy "build\dist\pelis" "%SALIDA%\pelis-app\app\win" /e /nfl /ndl /njh /njs /np >nul
if errorlevel 8 exit /b 1
copy /y "tools\pelis.toml.ejemplo" "%SALIDA%\pelis-app\app\" >nul
copy /y "tools\Pelis.bat" "%SALIDA%\" >nul
echo Listo: %SALIDA%
exit /b 0
