"""Capturas: cuadros de la película guardados en `capturas/` dentro de su carpeta."""

from itertools import count
from pathlib import Path


def ruta_libre(carpeta_pelicula, posicion_ms):
    """Ruta para una captura en `posicion_ms`: `capturas/HH-MM-SS.png`, o `HH-MM-SS(n).png`
    con el primer n ≥ 2 libre. Nunca devuelve una que ya exista."""
    s = posicion_ms // 1000
    base = f"{s // 3600:02}-{s // 60 % 60:02}-{s % 60:02}"
    carpeta = Path(carpeta_pelicula) / "capturas"
    ruta = carpeta / f"{base}.png"
    for n in count(2):
        if not ruta.exists():
            return ruta
        ruta = carpeta / f"{base}({n}).png"


def guardar(carpeta_pelicula, posicion_ms, png):
    """Escribe los bytes `png` como captura en `posicion_ms` y devuelve la ruta. Crea `capturas/`
    si falta. Si otra captura ocupa el nombre entre medio, prueba el siguiente. Lanza OSError."""
    while True:
        ruta = ruta_libre(carpeta_pelicula, posicion_ms)
        ruta.parent.mkdir(exist_ok=True)
        try:
            f = open(ruta, "xb")
        except FileExistsError:
            continue
        try:
            with f:
                f.write(png)
        except OSError:
            # Disco lleno a mitad de camino: no dejar un PNG roto
            ruta.unlink(missing_ok=True)
            raise
        return ruta
