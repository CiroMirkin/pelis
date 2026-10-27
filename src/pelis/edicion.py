"""Edición de metadatos desde la app: a mano, corrigiendo el match de IMDb y reasignando faltantes.

Cada cambio se guarda con `metadatos`, en la base y en el pelis.json de la carpeta, así sobrevive a una base nueva.
"""

import re
from pathlib import Path

from . import db, metadatos, poster
from .omdb import ErrorRed

ID_IMDB = re.compile(r"tt\d{7,}", re.IGNORECASE)
ANIO_FINAL = re.compile(r"^(.*?)[\s(]+((?:18|19|20)\d\d)\)?\s*$")


class DatoInvalido(Exception):
    pass


def imdb_id_de(texto):
    """IMDb ID que aparece en `texto` (ej. un link de imdb.com), o None."""
    m = ID_IMDB.search(texto or "")
    return m.group(0).lower() if m else None


def separar_anio(texto):
    """"Alien 1979" o "Alien (1979)" -> ("Alien", 1979); sin año -> (texto, None)."""
    texto = texto.strip()
    m = ANIO_FINAL.match(texto)
    return (m.group(1).strip(), int(m.group(2))) if m and m.group(1).strip() else (texto, None)


def candidatos(omdb, texto):
    """Películas de OMDb que coinciden con `texto` (título, opcionalmente con el año al final)."""
    titulo, anio = separar_anio(texto)
    return [
        {
            "imdbId": c.get("imdbID", ""),
            "titulo": c.get("Title", ""),
            "anio": c.get("Year", ""),
            "poster": c["Poster"] if c.get("Poster", "N/A") != "N/A" else "",
        }
        for c in omdb.buscar(titulo, anio)
    ]


def bajar_poster(omdb, url, destino):
    """Baja el poster de OMDb a `destino` (de `destino_poster`); devuelve si se pudo. Corre fuera del hilo de la UI."""
    if destino is None or not url:
        return False
    try:
        destino.parent.mkdir(exist_ok=True)
        omdb.bajar_poster(url, destino)
    except ErrorRed:
        return False
    return True


def destino_poster(conn, biblioteca, pelicula_id):
    """Dónde bajar el poster de OMDb, o None si la película tiene uno propio que no hay que pisar."""
    p = db.pelicula(conn, pelicula_id)
    actual = poster._actual(conn, pelicula_id)
    if actual is not None and actual["origen"] != "omdb":
        return None
    return poster._carpeta_posters(Path(biblioteca) / p["folder_path"]) / "poster.jpg"


def aplicar_omdb(conn, biblioteca, pelicula_id, datos, poster_bajado):
    """Reemplaza los metadatos (y personas) por los traídos de OMDb. Devuelve un aviso o "".

    El título queda el actual; el año pasa a ser el de la película elegida (o el actual si OMDb no trae).
    """
    p = db.pelicula(conn, pelicula_id)
    aviso = metadatos.aplicar(conn, biblioteca, pelicula_id,
                              {**datos, "titulo": p["titulo"], "year": datos.get("year") or p["year"]}, explicita=True)
    if poster_bajado:
        destino = poster._carpeta_posters(Path(biblioteca) / p["folder_path"]) / "poster.jpg"
        poster._usar(conn, pelicula_id, destino.relative_to(biblioteca).as_posix(), "omdb")
        conn.commit()
    return aviso


def _lista(texto):
    return [x.strip() for x in (texto or "").split(",") if x.strip()]


def guardar_manual(conn, biblioteca, pelicula_id, campos):
    """Guarda lo editado en el formulario y deja `metadatos_origen = 'manual'`.

    `campos`: titulo, anio (texto, puede ir vacío), sinopsis, pais, genero, director y elenco
    (nombres separados por comas). Lanza DatoInvalido con un mensaje para mostrar; devuelve un aviso o "".
    """
    titulo = (campos.get("titulo") or "").strip()
    if not titulo:
        raise DatoInvalido("El título no puede quedar vacío.")
    anio_texto = str(campos.get("anio") or "").strip()
    if anio_texto and not (anio_texto.isdigit() and 1880 <= int(anio_texto) <= 2100):
        raise DatoInvalido(f"El año «{anio_texto}» no es válido.")
    anio = int(anio_texto) if anio_texto else None
    p = db.pelicula(conn, pelicula_id)
    sinopsis = (campos.get("sinopsis") or "").strip() or None
    return metadatos.aplicar(conn, biblioteca, pelicula_id, {
        "titulo": titulo,
        "year": anio,
        "imdb_id": p["omdb_id"],
        "sinopsis": sinopsis,
        "sinopsis_idioma": p["sinopsis_idioma"] if sinopsis == (p["sinopsis"] or None) else None,
        "pais": (campos.get("pais") or "").strip() or None,
        "genero": (campos.get("genero") or "").strip() or None,
        "director": _lista(campos.get("director")),
        "elenco": _lista(campos.get("elenco")),
        "poster_url": p["poster_url"],
        "metadatos_origen": "manual",
    }, explicita=True)


def fusionar(conn, biblioteca, faltante_id, nueva_id):
    """Reasignación manual: el registro faltante toma la carpeta de `nueva_id`. Devuelve un aviso o ""."""
    db.fusionar(conn, faltante_id, nueva_id)
    p = db.pelicula(conn, faltante_id)
    poster.revisar(conn, biblioteca, faltante_id)
    if p["omdb_estado"] != "encontrada":
        return ""
    return metadatos.escribir_archivo(conn, biblioteca, faltante_id)
