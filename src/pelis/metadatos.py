"""Metadatos de una película: el único que los guarda en la base y escribe pelis.json.

pelis.json es la copia portátil de lo que está en la base (docs/adr/0001-pelis-json-copia-portatil.md).
"""

from pathlib import Path

from . import archivo_metadatos, db
from .omdb import ErrorRed


def obtener(datos_omdb, tmdb, idiomas):
    """Respuesta de OMDb -> metadatos, con la sinopsis de TMDb en el primer idioma de `idiomas` que tenga.

    Usa la red (TMDb) y no toca la base. Devuelve (metadatos, aviso); el aviso dice si TMDb no respondió.
    """
    sinopsis = _texto(datos_omdb.get("Plot"))
    m = {
        "imdb_id": datos_omdb.get("imdbID"),
        "year": _anio(datos_omdb.get("Year")),
        "sinopsis": sinopsis,
        "sinopsis_idioma": "en" if sinopsis else None,
        "pais": _texto(datos_omdb.get("Country")),
        "genero": _texto(datos_omdb.get("Genre")),
        "director": _lista(datos_omdb.get("Director")),
        "elenco": _lista(datos_omdb.get("Actors")),
        "poster_url": _texto(datos_omdb.get("Poster")),
        "metadatos_origen": "omdb",
    }
    if tmdb is None or not m["imdb_id"]:
        return m, ""
    try:
        texto, idioma = tmdb.sinopsis(m["imdb_id"], list(idiomas))
    except ErrorRed as e:
        return m, f"TMDb no respondió ({e}); sinopsis en inglés."
    if texto:
        m["sinopsis"], m["sinopsis_idioma"] = texto, idioma
    return m, ""


def _lista(valor):
    if not valor or valor == "N/A":
        return []
    return [x.strip() for x in valor.split(",") if x.strip()]


def _texto(valor):
    return None if not valor or valor == "N/A" else valor


def _anio(valor):
    valor = _texto(valor)
    return int(valor[:4]) if valor and valor[:4].isdigit() else None


def aplicar(conn, biblioteca, pelicula_id, metadatos, explicita):
    """Guarda `metadatos` (campos de pelis.json), hace commit y reescribe pelis.json. Devuelve un aviso o "".

    explicita: alguien eligió estos datos (edición, corregir match, pelis.json) y el título y el año se
    guardan tal cual. Si no (match automático del escaneo), ganan los de la carpeta y OMDb completa.
    """
    p = db.pelicula(conn, pelicula_id)
    if explicita:
        titulo, year = metadatos.get("titulo") or p["titulo"], metadatos.get("year")
    else:
        titulo, year = p["titulo"], p["year"] or metadatos.get("year")
    db.fijar_metadatos(
        conn, pelicula_id, titulo, year,
        imdb_id=metadatos.get("imdb_id"),
        sinopsis=metadatos.get("sinopsis"),
        sinopsis_idioma=metadatos.get("sinopsis_idioma"),
        pais=metadatos.get("pais"),
        genero=metadatos.get("genero"),
        poster_url=metadatos.get("poster_url"),
        origen=metadatos.get("metadatos_origen") or "omdb",
        directores=metadatos.get("director") or [],
        actores=metadatos.get("elenco") or [],
    )
    conn.commit()
    return escribir_archivo(conn, biblioteca, pelicula_id)


def del_registro(p):
    """Fila de `db.pelicula` -> contenido de pelis.json."""
    return {
        "titulo": p["titulo"],
        "imdb_id": p["omdb_id"],
        "year": p["year"],
        "sinopsis": p["sinopsis"],
        "sinopsis_idioma": p["sinopsis_idioma"],
        "pais": p["pais"],
        "genero": p["genero"],
        "director": p["director"],
        "elenco": p["actor"],
        "poster_url": p["poster_url"],
        "metadatos_origen": p["metadatos_origen"],
    }


def escribir_archivo(conn, biblioteca, pelicula_id):
    """Reescribe pelis.json con lo que está en la base. Devuelve un aviso o ""."""
    p = db.pelicula(conn, pelicula_id)
    carpeta = Path(biblioteca) / p["folder_path"]
    if not carpeta.is_dir():
        return ""
    try:
        archivo_metadatos.leer(carpeta)
    except archivo_metadatos.ArchivoInvalido as e:
        return f"«{p['folder_path']}»: pelis.json inválido ({e}); no se reescribió."
    try:
        archivo_metadatos.escribir(carpeta, del_registro(p))
    except OSError as e:
        return (f"«{p['folder_path']}»: no se pudo escribir pelis.json ({e}). "
                "Los datos quedaron guardados y se reintenta en el próximo escaneo.")
    return ""


def sincronizar(conn, biblioteca):
    """Reescribe los pelis.json que no coinciden con la base (o que faltan). Devuelve (inválidos, sin_escribir).

    Ambas son listas [(carpeta, motivo)]. Las carpetas que no están (disco desconectado) se saltean sin avisar.
    """
    invalidos, sin_escribir = [], []
    for pelicula_id in db.con_metadatos(conn):
        p = db.pelicula(conn, pelicula_id)
        carpeta = Path(biblioteca) / p["folder_path"]
        if not carpeta.is_dir():
            continue
        try:
            archivo = archivo_metadatos.leer(carpeta)
        except archivo_metadatos.ArchivoInvalido as e:
            invalidos.append((p["folder_path"], str(e)))
            continue
        if archivo and _completar_desde_archivo(conn, p, archivo):
            p = db.pelicula(conn, pelicula_id)
        if archivo is not None and {c: archivo.get(c) for c in archivo_metadatos.CAMPOS} == del_registro(p):
            continue
        if aviso := escribir_archivo(conn, biblioteca, pelicula_id):
            sin_escribir.append((p["folder_path"], aviso))
    return invalidos, sin_escribir


def _completar_desde_archivo(conn, p, archivo):
    """Bases anteriores a las columnas sinopsis_idioma y poster_url: las toma del archivo de la misma película."""
    if (archivo.get("imdb_id") or "").lower() != (p["omdb_id"] or "").lower():
        return False
    faltan = {c: archivo.get(c) if p[c] is None else None for c in ("sinopsis_idioma", "poster_url")}
    if not any(faltan.values()):
        return False
    db.completar_extras(conn, p["id"], **faltan)
    conn.commit()
    return True
