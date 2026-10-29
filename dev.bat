@echo off
rem Corre Pelis desde el código, con la carpeta app de desarrollo (dev\). uv instala lo que falte según uv.lock.
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
    echo Falta uv: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)
set "UV_PROJECT_ENVIRONMENT=.venv"
uv run --locked python -m pelis --app-dir "%~dp0dev" %*
if errorlevel 1 pause
