"""Buscar una versión nueva en las Releases de GitHub (fase 7 de publicación)."""

import re
import sys

import requests

from . import __version__

API = "https://api.github.com/repos/CiroMirkin/pelis/releases/latest"
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


def buscar(sesion=requests, actual=__version__):
    """Consulta la última Release. Devuelve {'version', 'notas', 'paquetes'} si es más nueva, o None."""
    try:
        r = sesion.get(API, headers={"Accept": "application/vnd.github+json"}, timeout=TIMEOUT)
        if r.status_code == 404:  # todavía no hay ninguna Release
            return None
        r.raise_for_status()
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
