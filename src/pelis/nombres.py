"""Interpretación de nombres de carpetas y archivos: título, año, IMDb ID e idioma."""

import re
import unicodedata

RE_IMDB = re.compile(r"\[(tt\d+)\]", re.IGNORECASE)
RE_ANIO_FINAL = re.compile(r"^(.*?)\s*\((\d{4})\)$")
RE_ANIO_INICIAL = re.compile(r"^\((\d{4})\)\s*(.+)$")
RE_ANIO_SUELTO = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
RE_PALABRAS = re.compile(r"[a-zà-ÿ]+")

ALIAS_IDIOMA = {
    "es": {"es", "esp", "spa", "spanish", "español", "espanol", "latino", "castellano"},
    "en": {"en", "eng", "english"},
}


def parsear_carpeta(nombre):
    """'Alien (1979) [tt0078748]' -> ('Alien', 1979, 'tt0078748'). Año e ID son opcionales."""
    imdb = RE_IMDB.search(nombre)
    resto = RE_IMDB.sub("", nombre).strip()
    if m := RE_ANIO_FINAL.match(resto):
        titulo, anio = m.group(1), int(m.group(2))
    elif m := RE_ANIO_INICIAL.match(resto):
        titulo, anio = m.group(2), int(m.group(1))
    else:
        titulo, anio = resto, None
    return titulo.strip(), anio, imdb.group(1).lower() if imdb else None


def parsear_video(nombre_archivo):
    """'Red.Desert.1964.1080p.BluRay.mp4' -> ('Red Desert', 1964). Sin año -> (None, None)."""
    base = nombre_archivo.rsplit(".", 1)[0] if "." in nombre_archivo else nombre_archivo
    base = base.replace(".", " ").replace("_", " ")
    for m in RE_ANIO_SUELTO.finditer(base):
        titulo = base[: m.start()].strip(" -([")
        if titulo:
            return " ".join(titulo.split()), int(m.group(1))
    return None, None


def idioma_de(texto, preferido=None):
    """Código de idioma ('es', 'en', ...) que aparece en el texto, o None.

    Si se pasa `preferido`, solo dice si el texto coincide con ese idioma.
    """
    if not texto:
        return None
    palabras = set(RE_PALABRAS.findall(texto.lower()))
    for codigo, alias in ALIAS_IDIOMA.items():
        if (preferido is None or codigo == preferido) and palabras & alias:
            return codigo
    if preferido and preferido.lower() in palabras:
        return preferido
    return None


def normalizar(texto):
    """Minúsculas y sin acentos, para buscar: 'Almodóvar' -> 'almodovar'."""
    descompuesto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in descompuesto if not unicodedata.combining(c))
