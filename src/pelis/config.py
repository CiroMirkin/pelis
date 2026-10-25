"""Lectura de pelis.toml y resolución de rutas."""

import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


class ErrorConfig(Exception):
    pass


@dataclass
class Config:
    app_dir: Path
    biblioteca: Path
    omdb_api_key: str
    tmdb_api_key: str
    idiomas_sinopsis: list
    audio_preferido: str
    subs_preferido: str

    @property
    def db_path(self):
        return self.app_dir / "pelis.db"


def app_dir_por_defecto():
    """En el build de PyInstaller, app/ es la carpeta de arriba de win/ o linux/."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent.parent
    raise ErrorConfig("Corriendo desde el código hay que indicar la carpeta app con --app-dir")


def cargar(app_dir):
    app_dir = Path(app_dir).resolve()
    archivo = app_dir / "pelis.toml"
    if not archivo.is_file():
        raise ErrorConfig(f"No existe {archivo}")
    with open(archivo, "rb") as f:
        datos = tomllib.load(f)
    if "biblioteca" not in datos:
        raise ErrorConfig(f"Falta 'biblioteca' en {archivo}")
    biblioteca = Path(datos["biblioteca"])
    if not biblioteca.is_absolute():
        biblioteca = app_dir / biblioteca
    return Config(
        app_dir=app_dir,
        biblioteca=biblioteca.resolve(),
        omdb_api_key=datos.get("omdb_api_key", "").strip(),
        tmdb_api_key=datos.get("tmdb_api_key", "").strip(),
        idiomas_sinopsis=list(datos.get("idiomas_sinopsis", ["es-MX", "es-ES"])),
        audio_preferido=datos.get("audio_preferido", "es"),
        subs_preferido=datos.get("subs_preferido", "es"),
    )
