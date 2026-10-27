import json
import sqlite3

import pytest

from pelis import archivo_metadatos, db, metadatos
from pelis.escaneo import escanear
from pelis.omdb import ErrorRed

from test_escaneo import DATOS_ALIEN, OmdbFalso, carpeta


@pytest.fixture
def biblioteca(tmp_path):
    raiz = tmp_path / "Peliculas"
    raiz.mkdir()
    return raiz


@pytest.fixture
def conn(tmp_path):
    c = db.conectar(tmp_path / "pelis.db")
    yield c
    c.close()


def leer_json(c):
    return json.loads((c / "pelis.json").read_text(encoding="utf-8"))


def sin_version(datos):
    return {k: v for k, v in datos.items() if k != "version"}


def test_escaneo_deja_pelis_json_igual_a_la_base_con_titulo_y_anio_de_la_carpeta(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): {**DATOS_ALIEN, "Title": "Alien: El octavo pasajero",
                                                             "Year": "1980"}}))
    p = db.pelicula(conn, 1)
    assert (p["titulo"], p["year"]) == ("Alien", 1979)
    assert sin_version(leer_json(c)) == metadatos.del_registro(p)
    assert leer_json(c)["poster_url"] == "https://ejemplo/alien.jpg"


def test_anio_corregido_a_mano_sobrevive_a_una_base_nueva(biblioteca, conn, tmp_path):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    corregido = {**leer_json(c), "titulo": "Alien, el octavo pasajero", "year": 1980, "metadatos_origen": "manual"}
    assert metadatos.aplicar(conn, biblioteca, 1, corregido, explicita=True) == ""

    otra = db.conectar(tmp_path / "nueva.db")
    escanear(otra, biblioteca, OmdbFalso())
    p = db.pelicula(otra, 1)
    assert (p["titulo"], p["year"], p["metadatos_origen"]) == ("Alien, el octavo pasajero", 1980, "manual")
    otra.close()


def test_pelis_json_viejo_sin_titulo_se_importa_con_la_carpeta_y_se_repara(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    archivo_metadatos.escribir(c, {"imdb_id": "tt0078748", "year": 1980, "metadatos_origen": "omdb"})
    escanear(conn, biblioteca, OmdbFalso())
    p = db.pelicula(conn, 1)
    assert (p["titulo"], p["year"]) == ("Alien", 1979)
    assert (leer_json(c)["titulo"], leer_json(c)["year"]) == ("Alien", 1979)


def test_pelis_json_invalido_no_se_pisa(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    (c / "pelis.json").write_text("{roto", encoding="utf-8")
    aviso = metadatos.aplicar(conn, biblioteca, 1, {"titulo": "Alien", "metadatos_origen": "manual"}, explicita=True)
    assert "inválido" in aviso
    assert (c / "pelis.json").read_text(encoding="utf-8") == "{roto"
    assert db.pelicula(conn, 1)["metadatos_origen"] == "manual"


def test_si_no_se_puede_escribir_la_base_queda_guardada_y_vuelve_un_aviso(biblioteca, conn, monkeypatch):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")

    def falla(carpeta, datos):
        raise PermissionError("solo lectura")

    monkeypatch.setattr(archivo_metadatos, "escribir", falla)
    informe = escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert db.pelicula(conn, 1)["omdb_id"] == "tt0078748"
    assert [c for c, _ in informe.archivos_sin_escribir] == ["Alien (1979)"]
    assert "solo lectura" in informe.archivos_sin_escribir[0][1]


def test_base_vieja_suma_las_columnas_nuevas(tmp_path):
    ruta = tmp_path / "vieja.db"
    vieja = sqlite3.connect(ruta)
    vieja.execute("CREATE TABLE peliculas (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL)")
    vieja.commit()
    vieja.close()
    conn = db.conectar(ruta)
    columnas = {f["name"] for f in conn.execute("PRAGMA table_info(peliculas)")}
    assert {"sinopsis_idioma", "poster_url"} <= columnas
    conn.close()


# --- sincronización ---

def test_sincronizar_repara_un_pelis_json_viejo_y_crea_uno_que_falta(biblioteca, conn):
    alien = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    aliens = carpeta(biblioteca, "Aliens (1986)", "Aliens.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN,
                                          ("Aliens", 1986): {**DATOS_ALIEN, "imdbID": "tt0090605"}}))
    # Como lo dejaba el escaneo viejo: sin título y con el año de OMDb
    archivo_metadatos.escribir(alien, {**leer_json(alien), "titulo": None, "year": 1980})
    (aliens / "pelis.json").unlink()

    informe = escanear(conn, biblioteca, OmdbFalso())
    assert informe.archivos_sin_escribir == []
    for c, id_ in ((alien, 1), (aliens, 2)):
        assert sin_version(leer_json(c)) == metadatos.del_registro(db.pelicula(conn, id_))
    assert (leer_json(alien)["titulo"], leer_json(alien)["year"]) == ("Alien", 1979)


def test_sincronizar_no_reescribe_un_archivo_que_ya_coincide(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    antes = (c / "pelis.json").stat().st_mtime_ns
    escanear(conn, biblioteca, OmdbFalso())
    assert (c / "pelis.json").stat().st_mtime_ns == antes


def test_sincronizar_no_toca_carpetas_ausentes_ni_la_papelera(biblioteca, conn):
    alien = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    db.cambiar_estado(conn, 1, "papelera")
    conn.commit()
    (alien / "pelis.json").unlink()
    assert metadatos.sincronizar(conn, biblioteca) == ([], [])
    assert not (alien / "pelis.json").exists()

    db.cambiar_estado(conn, 1, "activa")
    conn.commit()
    alien.rename(biblioteca.parent / "afuera")
    assert metadatos.sincronizar(conn, biblioteca) == ([], [])


def test_sincronizar_informa_un_archivo_invalido_sin_pisarlo(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    (c / "pelis.json").write_text("{roto", encoding="utf-8")
    informe = escanear(conn, biblioteca, OmdbFalso())
    assert [carpeta for carpeta, _ in informe.archivos_invalidos] == ["Alien (1979)"]
    assert (c / "pelis.json").read_text(encoding="utf-8") == "{roto"


def test_sincronizar_toma_idioma_y_poster_url_del_archivo_si_la_base_no_los_tiene(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    # Base de antes de las columnas nuevas
    conn.execute("UPDATE peliculas SET sinopsis_idioma = NULL, poster_url = NULL")
    conn.commit()
    metadatos.sincronizar(conn, biblioteca)
    p = db.pelicula(conn, 1)
    assert (p["sinopsis_idioma"], p["poster_url"]) == ("en", "https://ejemplo/alien.jpg")
    assert leer_json(c)["poster_url"] == "https://ejemplo/alien.jpg"


# --- obtener ---

class TmdbFalso:
    def __init__(self, caido=False):
        self.caido = caido

    def sinopsis(self, imdb_id, idiomas):
        if self.caido:
            raise ErrorRed("sin red")
        return "En el espacio nadie...", "es-MX"


def test_obtener_mapea_omdb_y_toma_la_sinopsis_de_tmdb():
    m, aviso = metadatos.obtener({**DATOS_ALIEN, "Country": "N/A"}, TmdbFalso(), ["es-MX"])
    assert (m["imdb_id"], m["year"], m["pais"], m["elenco"]) == ("tt0078748", 1979, None, ["Sigourney Weaver", "Tom Skerritt"])
    assert (m["sinopsis"], m["sinopsis_idioma"], aviso) == ("En el espacio nadie...", "es-MX", "")


def test_obtener_con_tmdb_caido_deja_la_sinopsis_de_omdb_y_avisa():
    m, aviso = metadatos.obtener(DATOS_ALIEN, TmdbFalso(caido=True), ["es-MX"])
    assert (m["sinopsis"], m["sinopsis_idioma"]) == ("En el espacio...", "en")
    assert aviso == "TMDb no respondió (sin red); sinopsis en inglés."
