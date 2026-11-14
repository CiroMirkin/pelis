"""Actualizar una Pelis instalada (setup.exe en Windows, .deb en Linux) bajando el instalador de la Release."""

import shlex
import shutil
import sys
import tempfile
from pathlib import Path

import requests

from .actualizacion import ErrorActualizacion, bajar_verificado


def nombre_instalador(version, windows=sys.platform == "win32"):
    return f"Pelis-windows-v{version}-setup.exe" if windows else f"Pelis-linux-v{version}.deb"


def preparar_instalador(nueva, sesion=requests, progreso=lambda fraccion: None, cancelado=lambda: False,
                        windows=sys.platform == "win32"):
    """Va a una carpeta temporal porque la carpeta del programa instalado es de solo lectura en Linux."""
    nombre = nombre_instalador(nueva["version"], windows)
    if not windows and not shutil.which("pkexec"):
        raise ErrorActualizacion(
            f"Falta pkexec para instalar desde Pelis. Bajá {nombre} de la Release e instalalo con: "
            f"sudo apt install ./{nombre}")
    carpeta = Path(tempfile.mkdtemp(prefix="pelis-actualizacion-"))
    try:
        return bajar_verificado(sesion, nueva, nombre, carpeta, progreso, cancelado)
    except BaseException:
        shutil.rmtree(carpeta, ignore_errors=True)
        raise


SCRIPT_INSTALADOR_WIN = r"""@echo off
chcp 65001 >nul
rem Lo escribió Pelis al actualizar: espera a que cierre, corre el instalador y vuelve a abrir la app.
set "PID={pid}"
:esperar
tasklist /FI "PID eq %PID%" /NH 2>nul | find "%PID%" >nul && (timeout /t 1 /nobreak >nul & goto esperar)
"{instalador}" /SILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS
start "" "{exe}" {args}
(goto) 2>nul & rmdir /s /q "%~dp0"
"""

SCRIPT_INSTALADOR_LINUX = """#!/bin/sh
# Lo escribió Pelis al actualizar: espera a que cierre, instala el .deb y vuelve a abrir la app.
PID={pid}
while kill -0 "$PID" 2>/dev/null; do sleep 0.5; done
# Si se cancela la contraseña o apt falla entonces el paquete anterior queda como estaba y se abre igual
pkexec apt-get install -y {instalador}
nohup {exe} {args} >/dev/null 2>&1 &
rm -rf -- {carpeta}
"""


def escribir_script_instalador(instalador, pid, args=(), exe=None, windows=sys.platform == "win32"):
    """Queda junto al instalador para que el script borre toda la carpeta al terminar."""
    exe = Path(exe or sys.executable)
    instalador = Path(instalador)
    if windows:
        texto = SCRIPT_INSTALADOR_WIN.format(pid=pid, instalador=instalador, exe=exe,
                                             args=" ".join(f'"{a}"' for a in args))
        script = instalador.parent / "actualizar.bat"
        script.write_text(texto.replace("\n", "\r\n"), encoding="utf-8")
    else:
        texto = SCRIPT_INSTALADOR_LINUX.format(pid=pid, instalador=shlex.quote(str(instalador)),
                                               exe=shlex.quote(str(exe)), carpeta=shlex.quote(str(instalador.parent)),
                                               args=" ".join(shlex.quote(a) for a in args))
        script = instalador.parent / "actualizar.sh"
        script.write_text(texto, encoding="utf-8")
    return script
