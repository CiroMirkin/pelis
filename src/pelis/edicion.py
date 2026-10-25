"""Edición de metadatos desde la app: a mano, corrigiendo el match de IMDb y reasignando faltantes.

Cada cambio se guarda en la base y en el pelis.json de la carpeta, así sobrevive a una base nueva.
"""

import re
from pathlib import Path

from . import archivo_metadatos, db
from .escaneo import actualizar_poster, carpeta_posters, metadatos_de_omdb
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


def traer(omdb, tmdb, idiomas, imdb_id, destino_poster=None):
    """Metadatos de OMDb para `imdb_id` (con la sinopsis de TMDb si está), o None si no existe.

    Si `destino_poster` no es None, baja ahí el poster. Devuelve (metadatos, poster_bajado, aviso).
    Corre fuera del hilo de la UI: no toca la base.
    """
    datos = omdb.por_id(imdb_id)
    if datos is None:
        return None, False, ""
    metadatos = metadatos_de_omdb(datos)
    aviso = ""
    if tmdb is not None:
        try:
            texto, idioma = tmdb.sinopsis(imdb_id, idiomas)
        except ErrorRed as e:
            texto, idioma = None, None
            aviso = f"TMDb no respondió ({e}); la sinopsis quedó en inglés."
        if texto:
            metadatos["sinopsis"], metadatos["sinopsis_idioma"] = texto, idioma
    bajado = False
    if destino_poster is not None and metadatos.get("poster_url"):
        try:
            destino_poster.parent.mkdir(exist_ok=True)
            omdb.bajar_poster(metadatos["poster_url"], destino_poster)
            bajado = True
        except ErrorRed:
            pass
    return metadatos, bajado, aviso


def destino_poster(conn, biblioteca, pelicula_id):
    """Dónde bajar el poster de OMDb, o None si la película tiene uno propio que no hay que pisar."""
    p = db.pelicula(conn, pelicula_id)
    actual = db.poster_actual(conn, pelicula_id)
    if actual is not None and actual["origen"] != "omdb":
        return None
    return carpeta_posters(Path(biblioteca) / p["folder_path"]) / "poster.jpg"


def aplicar_omdb(conn, biblioteca, pelicula_id, metadatos, poster_bajado):
    """Reemplaza los metadatos (y personas) por los traídos de OMDb. El título queda el actual."""
    p = db.pelicula(conn, pelicula_id)
    db.guardar_metadatos(
        conn, pelicula_id, "encontrada",
        omdb_id=metadatos.get("imdb_id"),
        sinopsis=metadatos.get("sinopsis"),
        pais=metadatos.get("pais"),
        genero=metadatos.get("genero"),
        directores=metadatos.get("director") or [],
        actores=metadatos.get("elenco") or [],
        origen="omdb",
    )
    # Al corregir el match, el año es el de la película elegida
    if metadatos.get("year"):
        db.fijar_anio(conn, pelicula_id, metadatos["year"])
    if poster_bajado:
        destino = carpeta_posters(Path(biblioteca) / p["folder_path"]) / "poster.jpg"
        db.usar_poster(conn, pelicula_id, destino.relative_to(biblioteca).as_posix(), "omdb")
    conn.commit()
    _escribir_archivo(conn, biblioteca, pelicula_id, metadatos)


def _lista(texto):
    return [x.strip() for x in (texto or "").split(",") if x.strip()]


def guardar_manual(conn, biblioteca, pelicula_id, campos):
    """Guarda lo editado en el formulario y deja `metadatos_origen = 'manual'`.

    `campos`: titulo, anio (texto, puede ir vacío), sinopsis, pais, genero, director y elenco
    (nombres separados por comas). Lanza DatoInvalido con un mensaje para mostrar.
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
    db.guardar_metadatos(
        conn, pelicula_id, "encontrada",
        omdb_id=p["omdb_id"],
        sinopsis=sinopsis,
        pais=(campos.get("pais") or "").strip() or None,
        genero=(campos.get("genero") or "").strip() or None,
        directores=_lista(campos.get("director")),
        actores=_lista(campos.get("elenco")),
        origen="manual",
        titulo=titulo,
    )
    db.fijar_anio(conn, pelicula_id, anio)
    conn.commit()
    anterior = _archivo_actual(biblioteca, p["folder_path"])
    misma_sinopsis = sinopsis == (p["sinopsis"] or None)
    _escribir_archivo(conn, biblioteca, pelicula_id, {
        "sinopsis_idioma": anterior.get("sinopsis_idioma") if misma_sinopsis else None,
        "poster_url": anterior.get("poster_url"),
    })


def fusionar(conn, biblioteca, faltante_id, nueva_id):
    """Reasignación manual: el registro faltante toma la carpeta de `nueva_id`."""
    db.fusionar(conn, faltante_id, nueva_id)
    p = db.pelicula(conn, faltante_id)
    actualizar_poster(conn, biblioteca, faltante_id, p["folder_path"])
    conn.commit()
    if p["omdb_estado"] == "encontrada":
        anterior = _archivo_actual(biblioteca, p["folder_path"])
        _escribir_archivo(conn, biblioteca, faltante_id, {
            "sinopsis_idioma": anterior.get("sinopsis_idioma"),
            "poster_url": anterior.get("poster_url"),
        })


def _archivo_actual(biblioteca, folder_path):
    try:
        return archivo_metadatos.leer(Path(biblioteca) / folder_path) or {}
    except archivo_metadatos.ArchivoInvalido:
        return {}


def _escribir_archivo(conn, biblioteca, pelicula_id, extra):
    """pelis.json con lo que quedó en la base; `extra` aporta lo que la base no guarda."""
    p = db.pelicula(conn, pelicula_id)
    carpeta = Path(biblioteca) / p["folder_path"]
    if not carpeta.is_dir():
        return
    archivo_metadatos.escribir(carpeta, {
        "titulo": p["titulo"],
        "imdb_id": p["omdb_id"],
        "year": p["year"],
        "sinopsis": p["sinopsis"],
        "sinopsis_idioma": extra.get("sinopsis_idioma"),
        "pais": p["pais"],
        "genero": p["genero"],
        "director": p["director"],
        "elenco": p["actor"],
        "poster_url": extra.get("poster_url"),
        "metadatos_origen": p["metadatos_origen"],
    })
