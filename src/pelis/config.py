"""Lectura de pelis.toml y resolución de rutas."""

import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


class ErrorConfig(Exception):
    pass


@dataclass
class Config:
    app_dir: Path
    biblioteca: Path | None  # None es que todavía no se eligió ninguna
    omdb_api_key: str
    tmdb_api_key: str
    idiomas_sinopsis: list
    audio_preferido: str
    subs_preferido: str
    portable: bool = True  # False es instalada y entonces los datos van en la carpeta del usuario

    @property
    def db_path(self):
        return self.app_dir / "pelis.db"


def carpeta_de_datos():
    """Dónde vive todo lo escribible cuando la app está instalada porque el ejecutable no se puede tocar.
    Es ~/.local/share y no ~/.config porque acá van también los datos (pelis.db) y no solo configuración."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / "Pelis"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "pelis"


def app_dir_por_defecto():
    """Es portable si hay un pelis.toml en app/ (arriba del ejecutable) y si no, es instalada."""
    if not getattr(sys, "frozen", False):
        raise ErrorConfig("Corriendo desde el código hay que indicar la carpeta app con --app-dir")
    app = Path(sys.executable).resolve().parent.parent
    if (app / "pelis.toml").is_file():
        return app, True
    datos = carpeta_de_datos()
    datos.mkdir(parents=True, exist_ok=True)
    return datos, False


def resolver_biblioteca(app_dir, texto):
    ruta = Path(texto)
    return (ruta if ruta.is_absolute() else Path(app_dir) / ruta).resolve()


def texto_de_biblioteca(config, carpeta):
    """En portable se guarda relativa a app/ para que el disco ande con otra letra o punto de montaje y en instalada se guarda absoluta."""
    carpeta = Path(carpeta).resolve()
    if config.portable:
        try:
            return Path(os.path.relpath(carpeta, config.app_dir)).as_posix()
        except ValueError:  # Windows: otro disco
            pass
    return str(carpeta)


def cargar(app_dir, portable=True):
    app_dir = Path(app_dir).resolve()
    archivo = app_dir / "pelis.toml"
    if archivo.is_file():
        with open(archivo, "rb") as f:
            datos = tomllib.load(f)
    elif portable:
        raise ErrorConfig(f"No existe {archivo}")
    else:
        datos = {}
    return Config(
        app_dir=app_dir,
        biblioteca=resolver_biblioteca(app_dir, datos["biblioteca"]) if "biblioteca" in datos else None,
        omdb_api_key=datos.get("omdb_api_key", "").strip(),
        tmdb_api_key=datos.get("tmdb_api_key", "").strip(),
        idiomas_sinopsis=list(datos.get("idiomas_sinopsis", ["es-MX", "es-ES"])),
        audio_preferido=datos.get("audio_preferido", "es"),
        subs_preferido=datos.get("subs_preferido", "es"),
        portable=portable,
    )


CLAVES = {"omdb": "omdb_api_key", "tmdb": "tmdb_api_key"}


def aplicar_preferencias(config, preferencias):
    """Lo guardado desde la app en preferencias.ini gana sobre pelis.toml, que queda como valor inicial.
    Las claves ganan una por una y una guardada como "" también gana para que borrarla desde la app no haga reaparecer la del toml.
    La biblioteca vacía no gana porque la app no guarda una vacía."""
    for nombre, atributo in CLAVES.items():
        if preferencias.contains(f"claves/{nombre}"):
            setattr(config, atributo, str(preferencias.value(f"claves/{nombre}", "")).strip())
    if texto := str(preferencias.value("biblioteca/ruta", "")).strip():
        config.biblioteca = resolver_biblioteca(config.app_dir, texto)
