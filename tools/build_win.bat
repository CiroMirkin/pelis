@echo off
rem Arma dist\Pelis-win\ (listo para copiar a la raiz del disco) con PyInstaller.
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
    echo No existe .venv. Crealo con:
    echo   py -3.12 -m venv .venv
    echo   .venv\Scripts\python -m pip install -e .[dev]
    exit /b 1
)
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --distpath build\dist --workpath build\work tools\pelis.spec
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
