"""Interpretación de nombres de carpetas y archivos: título, año, IMDb ID e idioma."""

import re
import unicodedata

RE_IMDB_CARPETA = re.compile(r"\[tt\d+\]", re.IGNORECASE)
RE_IMDB = re.compile(r"tt\d{7,}", re.IGNORECASE)
RE_ANIO_AL_FINAL = re.compile(r"^(.*?)[\s(]+(\d{4})\)?\s*$")
ANIO_MIN, ANIO_MAX = 1880, 2100
RE_ANIO_FINAL = re.compile(r"^(.*?)\s*\((\d{4})\)$")
RE_ANIO_INICIAL = re.compile(r"^\((\d{4})\)\s*(.+)$")
RE_ANIO_SUELTO = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
RE_PALABRAS = re.compile(r"[a-zà-ÿ]+")

ALIAS_IDIOMA = {
    "es": {"es", "esp", "spa", "spanish", "español", "espanol", "latino", "castellano"},
    "en": {"en", "eng", "english"},
}


def imdb_id(texto):
    """IMDb ID que aparece en `texto` (suelto, entre corchetes o en un link de imdb.com), en minúsculas, o None.

    Un IMDb ID real es `tt` y 7 o más dígitos: `tt123` no lo es.
    """
    m = RE_IMDB.search(texto or "")
    return m.group(0).lower() if m else None


def anio_valido(anio):
    return ANIO_MIN <= anio <= ANIO_MAX


def separar_anio(texto):
    """"Alien 1979" o "Alien (1979)" -> ("Alien", 1979); sin año válido al final -> (texto, None)."""
    texto = texto.strip()
    m = RE_ANIO_AL_FINAL.match(texto)
    if m and m.group(1).strip() and anio_valido(int(m.group(2))):
        return m.group(1).strip(), int(m.group(2))
    return texto, None


def parsear_carpeta(nombre):
    """'Alien (1979) [tt0078748]' -> ('Alien', 1979, 'tt0078748'). Año e ID son opcionales."""
    imdb = imdb_id(" ".join(RE_IMDB_CARPETA.findall(nombre)))
    resto = RE_IMDB_CARPETA.sub("", nombre).strip()
    if m := RE_ANIO_FINAL.match(resto):
        titulo, anio = m.group(1), int(m.group(2))
    elif m := RE_ANIO_INICIAL.match(resto):
        titulo, anio = m.group(2), int(m.group(1))
    else:
        titulo, anio = resto, None
    return titulo.strip(), anio, imdb


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
