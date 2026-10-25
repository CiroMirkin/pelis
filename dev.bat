@echo off
rem Corre Pelis desde el código, con la carpeta app de desarrollo (dev\).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo No existe .venv. Crealo con:
    echo   py -3.12 -m venv .venv
    echo   .venv\Scripts\python -m pip install -e .[dev]
    pause
    exit /b 1
)
set "PYTHONPATH=%~dp0src"
".venv\Scripts\python.exe" -m pelis --app-dir "%~dp0dev" %*
if errorlevel 1 pause
