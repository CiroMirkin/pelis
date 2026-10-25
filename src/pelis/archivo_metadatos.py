"""Archivo pelis.json dentro de cada carpeta de película.

- Escritura: cada vez que la película obtiene o cambia sus metadatos, se reescribe.
- Lectura: solo al escanear una carpeta que no está en la base (o una pendiente de metadatos).
- Un archivo con `metadatos_origen` está completo y se importa sin consultar OMDb.
  Uno sin ese campo (ej. escrito a mano: {"imdb_id": "tt…"}) solo fuerza el match con OMDb.
"""

import json
import os

NOMBRE = "pelis.json"
VERSION = 1
CAMPOS = ("titulo", "imdb_id", "year", "sinopsis", "sinopsis_idioma", "pais", "genero", "director", "elenco", "poster_url",
          "metadatos_origen")


class ArchivoInvalido(Exception):
    pass


def leer(carpeta):
    """Devuelve el contenido de pelis.json, None si no existe, o lanza ArchivoInvalido."""
    ruta = carpeta / NOMBRE
    if not ruta.is_file():
        return None
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ArchivoInvalido(str(e)) from e
    if not isinstance(datos, dict):
        raise ArchivoInvalido("no es un objeto JSON")
    if datos.get("version", VERSION) > VERSION:
        raise ArchivoInvalido(f"versión {datos['version']} más nueva que la soportada ({VERSION})")
    imdb_id = datos.get("imdb_id")
    if imdb_id is not None and not (isinstance(imdb_id, str) and imdb_id.lower().startswith("tt")):
        raise ArchivoInvalido(f"imdb_id inválido: {imdb_id!r}")
    return datos


def es_completo(datos):
    return bool(datos) and "metadatos_origen" in datos


def escribir(carpeta, datos):
    """Escribe pelis.json de forma atómica (archivo temporal + reemplazo)."""
    contenido = {"version": VERSION, **{k: datos.get(k) for k in CAMPOS}}
    ruta = carpeta / NOMBRE
    temporal = carpeta / (NOMBRE + ".tmp")
    temporal.write_text(json.dumps(contenido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporal, ruta)
