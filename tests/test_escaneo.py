import json
import shutil

import pytest

from pelis import db
from pelis.escaneo import escanear, importar_sin_red
from pelis.omdb import ErrorRed


class OmdbFalso:
    """Responde según un diccionario {(titulo, year) o imdb_id: datos}."""

    def __init__(self, respuestas=None, caido=False):
        self.respuestas = respuestas or {}
        self.caido = caido
        self.consultas = []

    def por_id(self, imdb_id):
        self.consultas.append(imdb_id)
        if self.caido:
            raise ErrorRed("sin red")
        return self.respuestas.get(imdb_id)

    def por_titulo(self, titulo, year=None):
        self.consultas.append((titulo, year))
        if self.caido:
            raise ErrorRed("sin red")
        return self.respuestas.get((titulo, year))

    def bajar_poster(self, url, destino):
        destino.write_bytes(b"jpg")


DATOS_ALIEN = {
    "Title": "Alien", "Year": "1979", "imdbID": "tt0078748", "Plot": "En el espacio...",
    "Country": "UK, USA", "Genre": "Horror, Sci-Fi", "Director": "Ridley Scott",
    "Actors": "Sigourney Weaver, Tom Skerritt", "Poster": "https://ejemplo/alien.jpg",
}


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


def carpeta(raiz, nombre, *archivos):
    c = raiz / nombre
    c.mkdir()
    for a in archivos:
        (c / a).parent.mkdir(exist_ok=True)
        (c / a).touch()
    return c


def test_importa_con_metadatos_y_baja_poster(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "Alien.srt", "Thumbs.db")
    informe = escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))

    assert informe.agregadas == 1
    p = db.pelicula(conn, 1)
    assert (p["titulo"], p["year"], p["folder_path"], p["video_path"]) == ("Alien", 1979, "Alien (1979)", "Alien (1979)/Alien.mp4")
    assert p["omdb_estado"] == "encontrada"
    assert p["director"] == ["Ridley Scott"]
    assert p["actor"] == ["Sigourney Weaver", "Tom Skerritt"]
    assert p["poster"] == "Alien (1979)/posters/poster.jpg"
    assert (biblioteca / "Alien (1979)" / "posters" / "poster.jpg").exists()


def test_poster_existente_no_se_descarga(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "backdrop.jpg", "Folder.JPG")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/Folder.JPG"
    assert not (biblioteca / "Alien (1979)" / "posters").exists()


def test_poster_agregado_despues_se_toma_al_escanear(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] is None
    (c / "poster-alien.jpg").touch()
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/poster-alien.jpg"


def test_bajada_de_omdb_usa_la_carpeta_posters_existente(biblioteca, conn):
    (carpeta(biblioteca, "Alien (1979)", "Alien.mp4") / "Posters").mkdir()
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/Posters/poster.jpg"
    assert not (biblioteca / "Alien (1979)" / "posters").exists()


def test_cascada_usa_imdb_id_primero(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979) [tt0078748]", "x.mkv")
    omdb = OmdbFalso({"tt0078748": DATOS_ALIEN})
    escanear(conn, biblioteca, omdb)
    assert omdb.consultas == ["tt0078748"]
    assert db.pelicula(conn, 1)["titulo"] == "Alien"


def test_cascada_cae_al_nombre_del_video(biblioteca, conn):
    carpeta(biblioteca, "Desierto rojo (1964)", "Red.Desert.1964.1080p.BluRay.mp4")
    omdb = OmdbFalso({("Red Desert", 1964): {**DATOS_ALIEN, "Title": "Red Desert"}})
    escanear(conn, biblioteca, omdb)
    assert omdb.consultas == [("Desierto rojo", 1964), ("Red Desert", 1964)]
    assert db.pelicula(conn, 1)["omdb_estado"] == "encontrada"


def test_no_encontrada_se_agrega_igual(biblioteca, conn):
    carpeta(biblioteca, "Rarísima (2030)", "r.mkv")
    informe = escanear(conn, biblioteca, OmdbFalso())
    assert informe.no_encontradas == ["Rarísima (2030)"]
    assert db.pelicula(conn, 1)["omdb_estado"] == "no_encontrada"


def test_carpetas_con_problemas(biblioteca, conn):
    carpeta(biblioteca, "Sin video (2025)", "poster.jpg")
    carpeta(biblioteca, "Dos videos (2011)", "a.avi", "a.mp4")
    informe = escanear(conn, biblioteca, OmdbFalso())
    assert informe.agregadas == 0
    assert sorted(informe.problemas) == [("Dos videos (2011)", "tiene 2 videos"), ("Sin video (2025)", "no tiene video")]


def test_subcarpetas_internas_se_ignoran(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    (c / "Subs").mkdir()
    (c / "Subs" / "extra.mkv").touch()
    assert escanear(conn, biblioteca, OmdbFalso()).agregadas == 1


def test_sin_red_queda_pendiente_y_se_reintenta(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    carpeta(biblioteca, "Brazil (1985)", "b.mkv")
    caido = OmdbFalso(caido=True)
    informe = escanear(conn, biblioteca, caido)
    assert informe.pendientes == ["Alien (1979)", "Brazil (1985)"]
    assert len(caido.consultas) == 1  # tras el primer error no insiste
    assert db.pelicula(conn, 2)["omdb_estado"] == "pendiente"

    informe = escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert informe.agregadas == 0
    assert db.pelicula(conn, 1)["omdb_estado"] == "encontrada"
    assert db.pelicula(conn, 2)["omdb_estado"] == "no_encontrada"


def test_sin_api_key_quedan_pendientes(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    informe = escanear(conn, biblioteca, None)
    assert informe.pendientes == ["Alien (1979)"]
    assert informe.aviso_omdb


def test_existentes_no_se_tocan_y_faltantes_se_ocultan(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    db.guardar_progreso(conn, 1, 5000)

    omdb = OmdbFalso()
    escanear(conn, biblioteca, omdb)
    assert omdb.consultas == []
    assert db.pelicula(conn, 1)["progreso_ms"] == 5000

    shutil.rmtree(biblioteca / "Alien (1979)")
    informe = escanear(conn, biblioteca, omdb)
    assert informe.faltantes == ["Alien (1979)"]
    assert db.catalogo(conn) == []
    assert db.pelicula(conn, 1)["estado"] == "faltante"

    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    informe = escanear(conn, biblioteca, omdb)
    assert informe.reactivadas == ["Alien (1979)"]
    assert len(db.catalogo(conn)) == 1


# --- pelis.json ---

def leer_json(c):
    return json.loads((c / "pelis.json").read_text(encoding="utf-8"))


def test_escribe_pelis_json_tras_match(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    datos = leer_json(c)
    assert datos["version"] == 1
    assert datos["imdb_id"] == "tt0078748"
    assert datos["director"] == ["Ridley Scott"]
    assert datos["elenco"] == ["Sigourney Weaver", "Tom Skerritt"]
    assert datos["metadatos_origen"] == "omdb"
    assert not (c / "pelis.json.tmp").exists()


def test_no_escribe_pelis_json_si_no_hay_match(biblioteca, conn):
    c = carpeta(biblioteca, "Rarísima (2030)", "r.mkv")
    escanear(conn, biblioteca, OmdbFalso())
    assert not (c / "pelis.json").exists()


def test_pelis_json_completo_se_importa_sin_omdb(biblioteca, conn, tmp_path):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))

    otra = db.conectar(tmp_path / "nueva.db")  # base nueva, misma biblioteca
    omdb = OmdbFalso()
    informe = escanear(otra, biblioteca, omdb)
    assert omdb.consultas == []
    assert informe.desde_archivo == ["Alien (1979)"]
    p = db.pelicula(otra, 1)
    assert p["omdb_estado"] == "encontrada"
    assert p["omdb_id"] == "tt0078748"
    assert p["actor"] == ["Sigourney Weaver", "Tom Skerritt"]
    otra.close()


def test_pelis_json_solo_con_imdb_id_fuerza_el_match(biblioteca, conn):
    c = carpeta(biblioteca, "Alpha (2025)", "Alpha (2025) 1080p .mkv")
    (c / "pelis.json").write_text('{"imdb_id": "tt32275943"}', encoding="utf-8")
    omdb = OmdbFalso({"tt32275943": {**DATOS_ALIEN, "Title": "Alpha", "imdbID": "tt32275943", "Year": "2026"}})
    escanear(conn, biblioteca, omdb)
    assert omdb.consultas == ["tt32275943"]
    p = db.pelicula(conn, 1)
    assert (p["titulo"], p["year"], p["omdb_id"]) == ("Alpha", 2025, "tt32275943")
    assert leer_json(c)["metadatos_origen"] == "omdb"  # quedó completo


def test_pelis_json_invalido_se_reporta_y_no_se_sobrescribe(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    (c / "pelis.json").write_text("{roto", encoding="utf-8")
    informe = escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert [carpeta for carpeta, _ in informe.archivos_invalidos] == ["Alien (1979)"]
    assert db.pelicula(conn, 1)["omdb_estado"] == "encontrada"
    assert (c / "pelis.json").read_text(encoding="utf-8") == "{roto"


def test_pendiente_usa_imdb_id_de_pelis_json_al_reintentar(biblioteca, conn):
    c = carpeta(biblioteca, "Alpha (2025)", "a.mkv")
    escanear(conn, biblioteca, OmdbFalso(caido=True))
    (c / "pelis.json").write_text('{"imdb_id": "tt32275943"}', encoding="utf-8")
    omdb = OmdbFalso({"tt32275943": {**DATOS_ALIEN, "imdbID": "tt32275943"}})
    escanear(conn, biblioteca, omdb)
    assert omdb.consultas == ["tt32275943"]
    assert db.pelicula(conn, 1)["omdb_id"] == "tt32275943"


# --- importación sin red al abrir la app ---

def test_importar_sin_red_suma_carpetas_nuevas(biblioteca, conn, tmp_path):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    carpeta(biblioteca, "Brazil (1985)", "b.mkv")

    otra = db.conectar(tmp_path / "nueva.db")  # otra compu: la carpeta de Alien llega con su pelis.json
    informe = importar_sin_red(otra, biblioteca)
    assert informe.agregadas == 2
    assert informe.desde_archivo == ["Alien (1979)"]
    assert informe.pendientes == ["Brazil (1985)"]
    assert db.pelicula(otra, 1)["omdb_id"] == "tt0078748"
    assert db.pelicula(otra, 2)["omdb_estado"] == "pendiente"
    assert len(db.catalogo(otra)) == 2
    otra.close()


def test_importar_sin_red_no_marca_faltantes(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    importar_sin_red(conn, biblioteca)
    shutil.rmtree(biblioteca / "Alien (1979)")
    informe = importar_sin_red(conn, biblioteca)
    assert informe.faltantes == []
    assert db.pelicula(conn, 1)["estado"] == "activa"


# --- sinopsis en español (TMDb) ---

class TmdbFalso:
    def __init__(self, sinopsis=None, caido=False):
        self.sinopsis_por_id = sinopsis or {}
        self.caido = caido
        self.consultas = []

    def sinopsis(self, imdb_id, idiomas):
        self.consultas.append(imdb_id)
        if self.caido:
            raise ErrorRed("sin red")
        return self.sinopsis_por_id.get(imdb_id, (None, None))


def test_sinopsis_en_espanol_de_tmdb(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    tmdb = TmdbFalso({"tt0078748": ("En el espacio nadie puede oírte gritar.", "es-ES")})
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}), tmdb=tmdb)
    assert db.pelicula(conn, 1)["sinopsis"] == "En el espacio nadie puede oírte gritar."
    datos = leer_json(c)
    assert (datos["sinopsis"], datos["sinopsis_idioma"]) == ("En el espacio nadie puede oírte gritar.", "es-ES")


def test_sin_sinopsis_en_tmdb_queda_la_de_omdb(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}), tmdb=TmdbFalso())
    assert db.pelicula(conn, 1)["sinopsis"] == "En el espacio..."
    assert leer_json(c)["sinopsis_idioma"] == "en"


def test_tmdb_caido_no_bloquea_y_no_insiste(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    carpeta(biblioteca, "Brazil (1985)", "b.mkv")
    omdb = OmdbFalso({("Alien", 1979): DATOS_ALIEN, ("Brazil", 1985): {**DATOS_ALIEN, "imdbID": "tt0088846"}})
    tmdb = TmdbFalso(caido=True)
    informe = escanear(conn, biblioteca, omdb, tmdb=tmdb)
    assert len(tmdb.consultas) == 1
    assert informe.aviso_tmdb
    assert db.pelicula(conn, 2)["omdb_estado"] == "encontrada"


def test_pelis_json_completo_no_consulta_tmdb(biblioteca, conn, tmp_path):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}), tmdb=TmdbFalso())
    otra = db.conectar(tmp_path / "nueva.db")
    tmdb = TmdbFalso()
    escanear(otra, biblioteca, OmdbFalso(), tmdb=tmdb)
    assert tmdb.consultas == []
    otra.close()
