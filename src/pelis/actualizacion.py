"""Buscar e instalar versiones nuevas desde las Releases de GitHub (fase 7 de publicación)."""

import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import requests

from . import __version__

API = "https://api.github.com/repos/CiroMirkin/pelis/releases/latest"  # ignora las pre-releases
API_TODAS = "https://api.github.com/repos/CiroMirkin/pelis/releases"
TIMEOUT = 15
RE_VERSION = re.compile(r"v?(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?")


class ErrorRed(Exception):
    """No se pudo consultar GitHub (sin conexión, timeout, respuesta rara)."""


def clave(version):
    """Clave para comparar versiones: '0.2.0-rc1' < '0.2.0' < '0.2.1'. None si no es una versión."""
    m = RE_VERSION.fullmatch(version)
    if not m:
        return None
    mayor, menor, parche, rc = m.groups()
    return int(mayor), int(menor), int(parche), int(rc) if rc else float("inf")


def es_mas_nueva(tag, actual=__version__):
    nueva, vieja = clave(tag), clave(actual)
    return nueva is not None and vieja is not None and nueva > vieja


def en_build():
    """La opción solo tiene sentido en el build de PyInstaller: desde el código no hay nada que reemplazar."""
    return getattr(sys, "frozen", False)


def buscar(sesion=requests, actual=__version__, prerelease=False):
    """Consulta la última Release. Devuelve {'version', 'notas', 'paquetes'} si es más nueva, o None.

    Con `prerelease` (la app abierta con --prerelease) mira todas y toma la más nueva, RC incluidas.
    """
    try:
        r = sesion.get(API_TODAS if prerelease else API, headers={"Accept": "application/vnd.github+json"},
                       timeout=TIMEOUT)
        if r.status_code == 404:  # todavía no hay ninguna Release
            return None
        r.raise_for_status()
        if prerelease:
            candidatas = [x for x in r.json() if not x.get("draft") and clave(x["tag_name"])]
            if not candidatas:
                return None
            release = max(candidatas, key=lambda x: clave(x["tag_name"]))
        else:
            release = r.json()
        tag = release["tag_name"]
    except (requests.RequestException, ValueError, KeyError, TypeError) as e:
        raise ErrorRed(str(e)) from e
    if not es_mas_nueva(tag, actual):
        return None
    return {
        "version": tag.removeprefix("v"),
        "notas": release.get("body") or "",
        "paquetes": {a["name"]: a["browser_download_url"] for a in release.get("assets", [])},
    }


# --- instalar ---

CHUNK = 1 << 16


class ErrorActualizacion(Exception):
    """La actualización no se puede aplicar; el mensaje es para el usuario."""


class Cancelado(Exception):
    """El usuario canceló la descarga."""


@dataclass(frozen=True)
class Instalacion:
    """Lugares del build: raiz/pelis-app/app/<win|linux>/, los mismos que arman build_win.bat y build_linux.sh.

    `app/` la comparten los dos sistemas, así que todo lo de una actualización lleva el nombre del sistema.
    """

    programa: Path

    @property
    def sistema(self):
        return self.programa.name

    @property
    def windows(self):
        return self.sistema == "win"

    @property
    def app(self):
        return self.programa.parent

    @property
    def raiz(self):
        return self.app.parent.parent

    @property
    def descarga(self):
        return self.app / f"actualizacion-{self.sistema}"

    @property
    def anterior(self):
        return self.app / f"{self.sistema}.anterior"

    @property
    def testigo(self):
        return self.app / f"actualizando-{self.sistema}"

    @property
    def ejecutable(self):
        return "pelis.exe" if self.windows else "pelis"

    @property
    def lanzador(self):
        return "Pelis.bat" if self.windows else "pelis.sh"

    def paquete(self, version):
        return f"Pelis-windows-v{version}.zip" if self.windows else f"Pelis-linux-v{version}.tar.gz"


def instalacion_actual():
    return Instalacion(Path(sys.executable).resolve().parent)


def leer_sumas(texto):
    """Formato de sha256sum: '<hash>  <nombre>' por línea -> {nombre: hash}."""
    sumas = {}
    for linea in texto.splitlines():
        partes = linea.split(maxsplit=1)
        if len(partes) == 2:
            sumas[partes[1].lstrip("*")] = partes[0].lower()
    return sumas


def sha256(archivo):
    h = hashlib.sha256()
    with open(archivo, "rb") as f:
        for bloque in iter(lambda: f.read(CHUNK), b""):
            h.update(bloque)
    return h.hexdigest()


def descargar(sesion, url, destino, progreso=lambda fraccion: None, cancelado=lambda: False):
    try:
        with sesion.get(url, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length") or 0)
            hecho = 0
            with open(destino, "wb") as f:
                for bloque in r.iter_content(CHUNK):
                    if cancelado():
                        raise Cancelado()
                    f.write(bloque)
                    hecho += len(bloque)
                    if total:
                        progreso(min(hecho / total, 1.0))
    except requests.RequestException as e:
        raise ErrorRed(str(e)) from e


def preparar(inst, nueva, sesion=requests, progreso=lambda fraccion: None, cancelado=lambda: False):
    """Baja y verifica el paquete de este sistema y lo extrae en `inst.descarga`; devuelve la carpeta extraída.

    No toca la instalación: si algo falla o se cancela, borra la descarga y deja todo como estaba.
    """
    nombre = inst.paquete(nueva["version"])
    urls = nueva["paquetes"]
    if nombre not in urls or "SHA256SUMS" not in urls:
        raise ErrorActualizacion(f"La versión {nueva['version']} no trae el paquete para este sistema.")
    shutil.rmtree(inst.descarga, ignore_errors=True)
    inst.descarga.mkdir(parents=True)
    try:
        sumas_archivo = inst.descarga / "SHA256SUMS"
        descargar(sesion, urls["SHA256SUMS"], sumas_archivo, cancelado=cancelado)
        esperado = leer_sumas(sumas_archivo.read_text(encoding="utf-8")).get(nombre)
        archivo = inst.descarga / nombre
        descargar(sesion, urls[nombre], archivo, progreso, cancelado)
        if esperado is None or sha256(archivo) != esperado:
            raise ErrorActualizacion("La descarga llegó dañada (no coincide con SHA256SUMS). Probá de nuevo.")
        nuevo = inst.descarga / "nuevo"
        if inst.windows:
            with zipfile.ZipFile(archivo) as z:
                z.extractall(nuevo)
        else:
            with tarfile.open(archivo) as t:
                t.extractall(nuevo, filter="data")
        archivo.unlink()
        if not (nuevo / "pelis-app" / "app" / inst.sistema / inst.ejecutable).is_file() \
                or not (nuevo / inst.lanzador).is_file():
            raise ErrorActualizacion("El paquete descargado no tiene el formato esperado.")
        return nuevo
    except BaseException:
        shutil.rmtree(inst.descarga, ignore_errors=True)
        raise


SCRIPT_WIN = r"""@echo off
chcp 65001 >nul
rem Lo escribió Pelis al actualizar: espera a que cierre, cambia la carpeta del programa y la vuelve a abrir.
set "PID={pid}"
set "APP={app}"
set "RAIZ={raiz}"
set "NUEVO={nuevo}"
:esperar
tasklist /FI "PID eq %PID%" /NH 2>nul | find "%PID%" >nul && (timeout /t 1 /nobreak >nul & goto esperar)
if exist "%APP%\win.anterior" rmdir /s /q "%APP%\win.anterior"
set /a INTENTOS=0
:mover
move "%APP%\win" "%APP%\win.anterior" >nul 2>nul && goto poner
set /a INTENTOS+=1
if %INTENTOS% lss 10 (timeout /t 1 /nobreak >nul & goto mover)
goto abrir
:poner
move "%NUEVO%\pelis-app\app\win" "%APP%\win" >nul 2>nul || (move "%APP%\win.anterior" "%APP%\win" >nul & goto abrir)
copy /y "%NUEVO%\Pelis.bat" "%RAIZ%\Pelis.bat" >nul
copy /y "%NUEVO%\pelis-app\app\pelis.toml.ejemplo" "%APP%\pelis.toml.ejemplo" >nul
type nul > "%APP%\actualizando-win"
:abrir
rmdir /s /q "%APP%\actualizacion-win"
start "" "%APP%\win\pelis.exe" {args}
(goto) 2>nul & del "%~f0"
"""

SCRIPT_LINUX = """#!/bin/sh
# Lo escribió Pelis al actualizar: espera a que cierre, cambia la carpeta del programa y la vuelve a abrir.
PID={pid}
APP={app}
RAIZ={raiz}
NUEVO={nuevo}
while kill -0 "$PID" 2>/dev/null; do sleep 0.5; done
rm -rf "$APP/linux.anterior"
if mv "$APP/linux" "$APP/linux.anterior"; then
    if mv "$NUEVO/pelis-app/app/linux" "$APP/linux"; then
        cp "$NUEVO/pelis.sh" "$RAIZ/pelis.sh" && chmod +x "$RAIZ/pelis.sh"
        cp "$NUEVO/pelis-app/app/pelis.toml.ejemplo" "$APP/pelis.toml.ejemplo"
        : > "$APP/actualizando-linux"
    else
        mv "$APP/linux.anterior" "$APP/linux"
    fi
fi
rm -rf "$APP/actualizacion-linux"
nohup "$APP/linux/pelis" {args} >/dev/null 2>&1 &
rm -f -- "$0"
"""


def escribir_script(inst, nuevo, pid, args=()):
    """Escribe en `app/` el script que hace el cambio cuando Pelis cierra; devuelve su ruta."""
    if inst.windows:
        texto = SCRIPT_WIN.format(pid=pid, app=inst.app, raiz=inst.raiz, nuevo=nuevo,
                                  args=" ".join(f'"{a}"' for a in args))
        script = inst.app / "actualizar-win.bat"
        script.write_text(texto.replace("\n", "\r\n"), encoding="utf-8")
    else:
        texto = SCRIPT_LINUX.format(pid=pid, app=shlex.quote(str(inst.app)), raiz=shlex.quote(str(inst.raiz)),
                                    nuevo=shlex.quote(str(nuevo)), args=" ".join(shlex.quote(a) for a in args))
        script = inst.app / "actualizar-linux.sh"
        script.write_text(texto, encoding="utf-8")
    return script


def lanzar(script):
    """Corre el script desprendido de Pelis, para que siga vivo cuando la app cierre."""
    if script.suffix == ".bat":
        subprocess.Popen(["cmd", "/c", str(script)], close_fds=True,
                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
    else:
        # PyInstaller apunta LD_LIBRARY_PATH a sus librerías; el script usa las del sistema
        env = dict(os.environ)
        if "LD_LIBRARY_PATH_ORIG" in env:
            env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH_ORIG"]
        else:
            env.pop("LD_LIBRARY_PATH", None)
        subprocess.Popen(["/bin/sh", str(script)], start_new_session=True, env=env, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def terminar(inst):
    """Al arrancar bien después de actualizar: borra la versión anterior y el testigo."""
    if inst.testigo.exists():
        shutil.rmtree(inst.anterior, ignore_errors=True)
        inst.testigo.unlink(missing_ok=True)
