"""Capturas: cuadros de la película guardados en `capturas/` dentro de su carpeta."""

import os
import re
import tempfile
from itertools import count
from pathlib import Path

EXTENSIONES = {".png", ".jpg", ".jpeg", ".webp"}
# Nombre que pone `ruta_libre`: `HH-MM-SS.ext` o `HH-MM-SS(n).ext`
CRONOLOGICA = re.compile(r"(\d{2,})-(\d{2})-(\d{2})(?:\((\d+)\))?")


def ruta_libre(carpeta_pelicula, posicion_ms):
    """Ruta para una captura en `posicion_ms`: `capturas/HH-MM-SS.png`, o `HH-MM-SS(n).png`
    con el primer n ≥ 2 libre. Nunca devuelve una que ya exista."""
    s = posicion_ms // 1000
    base = f"{s // 3600:02}-{s // 60 % 60:02}-{s % 60:02}"
    carpeta = Path(carpeta_pelicula) / "capturas"
    ruta = carpeta / f"{base}.png"
    for n in count(2):
        if not (ruta.exists() or ruta.is_symlink()):  # un symlink roto también ocupa el nombre
            return ruta
        ruta = carpeta / f"{base}({n}).png"


def guardar(carpeta_pelicula, posicion_ms, png):
    """Escribe los bytes `png` como captura en `posicion_ms` y devuelve la ruta. Crea `capturas/`
    si falta. Escribe a un temporal oculto y lo pasa al nombre final recién completo, así `listar`
    nunca ve un PNG a medias. Nunca pisa: si otra captura ocupa el nombre entre medio, prueba el
    siguiente. Lanza OSError."""
    carpeta = Path(carpeta_pelicula) / "capturas"
    carpeta.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".captura-", suffix=".tmp", dir=carpeta)
    try:
        with open(fd, "wb") as f:
            f.write(png)
        while True:
            ruta = ruta_libre(carpeta_pelicula, posicion_ms)
            try:
                _mover_sin_pisar(tmp, ruta)
            except FileExistsError:
                continue
            return ruta
    finally:
        # Disco lleno a mitad de camino, o ya movido: no dejar el temporal
        Path(tmp).unlink(missing_ok=True)


def _mover_sin_pisar(origen, destino):
    """Lleva `origen` a `destino` de una vez. FileExistsError si `destino` ya existe."""
    if os.name == "nt":
        os.rename(origen, destino)  # en Windows rename nunca pisa
        return
    try:
        os.link(origen, destino)  # falla si existe; el temporal lo borra quien llama
    except FileExistsError:
        raise
    except OSError:
        # Sistemas de archivos sin hard links (FAT, exFAT): rename sí pisa, así que se mira
        # antes. Solo queda la ventana entre mirar y renombrar.
        if destino.exists() or destino.is_symlink():
            raise FileExistsError(destino) from None
        os.rename(origen, destino)


def listar(carpeta_pelicula):
    """Imágenes de `capturas/`: primero las cronológicas por posición y sufijo (sin sufijo = 1),
    después el resto alfabético; los empates, por nombre. `[]` si la carpeta no existe."""
    carpeta = Path(carpeta_pelicula) / "capturas"
    if not carpeta.is_dir():
        return []

    def clave(ruta):
        m = CRONOLOGICA.fullmatch(ruta.stem)
        if m:
            h, mi, s, n = m.groups()
            return (0, (int(h), int(mi), int(s), int(n or 1)), "", ruta.name)
        return (1, (), ruta.name.casefold(), ruta.name)

    return sorted((r for r in carpeta.iterdir() if r.is_file() and r.suffix.lower() in EXTENSIONES), key=clave)
