import json

import pytest

from pelis import archivo_metadatos, db, edicion, metadatos
from pelis.escaneo import escanear, importar_sin_red

from test_escaneo import DATOS_ALIEN, OmdbFalso, carpeta

DATOS_ALIENS = {
    "Title": "Aliens", "Year": "1986", "imdbID": "tt0090605", "Plot": "57 años después...",
    "Country": "UK, USA", "Genre": "Action, Sci-Fi", "Director": "James Cameron",
    "Actors": "Sigourney Weaver, Michael Biehn", "Poster": "https://ejemplo/aliens.jpg",
}


class OmdbConBusqueda(OmdbFalso):
    def __init__(self, respuestas=None, busquedas=None):
        super().__init__(respuestas)
        self.busquedas = busquedas or {}
        self.posters = []

    def buscar(self, titulo, year=None):
        self.consultas.append(("s", titulo, year))
        return self.busquedas.get((titulo, year), [])

    def bajar_poster(self, url, destino):
        self.posters.append(url)
        destino.write_bytes(url.encode())


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


def leer_json(biblioteca, nombre):
    return json.loads((biblioteca / nombre / "pelis.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("texto, esperado", [
    ("tt0078748", "tt0078748"),
    ("https://www.imdb.com/title/tt0078748/?ref_=fn_al_tt_1", "tt0078748"),
    ("TT12345678", "tt12345678"),
    ("Alien 1979", None),
])
def test_imdb_id_de(texto, esperado):
    assert edicion.imdb_id_de(texto) == esperado


@pytest.mark.parametrize("texto, esperado", [
    ("Alien 1979", ("Alien", 1979)),
    ("Alien (1979)", ("Alien", 1979)),
    ("Alien", ("Alien", None)),
    ("1917", ("1917", None)),
    ("2001 1968", ("2001", 1968)),
])
def test_separar_anio(texto, esperado):
    assert edicion.separar_anio(texto) == esperado


def test_guardar_manual_completa_una_no_encontrada(biblioteca, conn):
    carpeta(biblioteca, "Gatillero (2025)", "Gatillero.mp4")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["omdb_estado"] == "no_encontrada"

    edicion.guardar_manual(conn, biblioteca, 1, {
        "titulo": "Gatillero", "anio": "2025", "sinopsis": "Un sicario...", "pais": "Argentina",
        "genero": "Acción", "director": "Cristian Tapia Marchiori", "elenco": "Sergio Podeley, Lautaro Delgado",
    })

    p = db.pelicula(conn, 1)
    assert (p["metadatos_origen"], p["omdb_estado"], p["pais"]) == ("manual", "encontrada", "Argentina")
    assert p["actor"] == ["Sergio Podeley", "Lautaro Delgado"]
    archivo = leer_json(biblioteca, "Gatillero (2025)")
    assert archivo["metadatos_origen"] == "manual"
    assert archivo["elenco"] == ["Sergio Podeley", "Lautaro Delgado"]


def test_guardar_manual_cambia_titulo_y_anio_y_sobrevive_a_una_base_nueva(biblioteca, conn, tmp_path):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    edicion.guardar_manual(conn, biblioteca, 1, {
        "titulo": "Alien, el octavo pasajero", "anio": "1980", "director": "Ridley Scott", "elenco": "",
    })
    p = db.pelicula(conn, 1)
    assert (p["titulo"], p["year"], p["actor"]) == ("Alien, el octavo pasajero", 1980, [])

    nueva = db.conectar(tmp_path / "otra.db")
    importar_sin_red(nueva, biblioteca)
    p = db.pelicula(nueva, 1)
    nueva.close()
    assert (p["titulo"], p["metadatos_origen"], p["director"]) == ("Alien, el octavo pasajero", "manual", ["Ridley Scott"])


@pytest.mark.parametrize("campos, error", [
    ({"titulo": "  "}, "título"),
    ({"titulo": "Alien", "anio": "79"}, "año"),
    ({"titulo": "Alien", "anio": "mil"}, "año"),
])
def test_guardar_manual_valida(biblioteca, conn, campos, error):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    importar_sin_red(conn, biblioteca)
    with pytest.raises(edicion.DatoInvalido, match=error):
        edicion.guardar_manual(conn, biblioteca, 1, campos)


def test_guardar_manual_conserva_poster_url_y_el_idioma_si_no_cambia_la_sinopsis(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    campos = {"titulo": "Alien", "anio": "1979", "sinopsis": "En el espacio..."}
    edicion.guardar_manual(conn, biblioteca, 1, campos)
    archivo = leer_json(biblioteca, "Alien (1979)")
    assert (archivo["poster_url"], archivo["sinopsis_idioma"]) == ("https://ejemplo/alien.jpg", "en")

    edicion.guardar_manual(conn, biblioteca, 1, {**campos, "sinopsis": "En el espacio nadie te oye gritar."})
    assert leer_json(biblioteca, "Alien (1979)")["sinopsis_idioma"] is None


def test_guardar_manual_sin_poder_escribir_pelis_json_queda_en_la_base_y_avisa(biblioteca, conn, monkeypatch):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))

    def falla(carpeta, datos):
        raise PermissionError("solo lectura")

    monkeypatch.setattr(archivo_metadatos, "escribir", falla)
    aviso = edicion.guardar_manual(conn, biblioteca, 1, {"titulo": "Alien", "anio": "1980"})
    assert "solo lectura" in aviso
    assert db.pelicula(conn, 1)["year"] == 1980


def test_corregir_match_reemplaza_metadatos_personas_y_poster_de_omdb(biblioteca, conn):
    carpeta(biblioteca, "Aliens (1986)", "Aliens.mp4")
    # El match automático salió mal: quedó Alien
    escanear(conn, biblioteca, OmdbFalso({("Aliens", 1986): DATOS_ALIEN}))
    omdb = OmdbConBusqueda({"tt0090605": DATOS_ALIENS})

    destino = edicion.destino_poster(conn, biblioteca, 1)
    encontrados, aviso = metadatos.obtener(omdb.por_id("tt0090605"), None, [])
    bajado = edicion.bajar_poster(omdb, encontrados["poster_url"], destino)
    edicion.aplicar_omdb(conn, biblioteca, 1, encontrados, bajado)

    p = db.pelicula(conn, 1)
    assert (p["titulo"], p["omdb_id"], p["year"], p["director"]) == ("Aliens", "tt0090605", 1986, ["James Cameron"])
    assert p["actor"] == ["Sigourney Weaver", "Michael Biehn"]
    assert p["poster"] == "Aliens (1986)/posters/poster.jpg"
    assert (biblioteca / "Aliens (1986)" / "posters" / "poster.jpg").read_bytes() == b"https://ejemplo/aliens.jpg"
    assert leer_json(biblioteca, "Aliens (1986)")["imdb_id"] == "tt0090605"
    assert aviso == ""


def test_corregir_match_no_pisa_un_poster_propio(biblioteca, conn):
    carpeta(biblioteca, "Aliens (1986)", "Aliens.mp4", "folder.jpg")
    escanear(conn, biblioteca, OmdbFalso({("Aliens", 1986): DATOS_ALIEN}))
    assert edicion.destino_poster(conn, biblioteca, 1) is None


def test_candidatos_separa_el_anio(conn):
    omdb = OmdbConBusqueda(busquedas={("Aliens", 1986): [
        {"Title": "Aliens", "Year": "1986", "imdbID": "tt0090605", "Type": "movie", "Poster": "N/A"},
    ]})
    assert edicion.candidatos(omdb, "Aliens 1986") == [
        {"imdbId": "tt0090605", "titulo": "Aliens", "anio": "1986", "poster": ""},
    ]


def test_escaneo_reasigna_carpeta_renombrada_conservando_progreso_y_vista(biblioteca, conn):
    vieja = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    db.guardar_progreso(conn, 1, 60000)
    db.marcar_vista(conn, 1, True)

    vieja.rename(biblioteca / "Alien - Director's Cut (1979)")
    omdb = OmdbFalso()
    informe = escanear(conn, biblioteca, omdb)

    assert informe.agregadas == 0
    assert informe.faltantes == []
    assert informe.reasignadas == [("Alien (1979)", "Alien - Director's Cut (1979)")]
    assert omdb.consultas == []
    p = db.pelicula(conn, 1)
    assert (p["folder_path"], p["video_path"]) == ("Alien - Director's Cut (1979)", "Alien - Director's Cut (1979)/Alien.mp4")
    assert (p["estado"], p["progreso_ms"], p["watched"]) == ("activa", 60000, 1)
    assert p["poster"] == "Alien - Director's Cut (1979)/posters/poster.jpg"


def test_escaneo_reasigna_un_faltante_por_el_id_del_nombre(biblioteca, conn):
    vieja = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    (vieja / "pelis.json").unlink()
    vieja.rename(biblioteca.parent / "afuera")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["estado"] == "faltante"

    (biblioteca.parent / "afuera").rename(biblioteca / "Alien [tt0078748]")
    informe = importar_sin_red(conn, biblioteca)
    assert informe.reasignadas == [("Alien (1979)", "Alien [tt0078748]")]
    assert db.pelicula(conn, 1)["estado"] == "activa"


def test_reasignacion_manual_sin_omdb_id(biblioteca, conn):
    vieja = carpeta(biblioteca, "Pelicula casera", "casera.mp4")
    importar_sin_red(conn, biblioteca)
    db.guardar_progreso(conn, 1, 5000)
    vieja.rename(biblioteca / "Casera (2020)")
    escanear(conn, biblioteca, None)
    assert db.pelicula(conn, 1)["estado"] == "faltante"
    assert db.pelicula(conn, 2)["folder_path"] == "Casera (2020)"

    edicion.fusionar(conn, biblioteca, 1, 2)

    assert db.pelicula(conn, 2) is None
    p = db.pelicula(conn, 1)
    assert (p["folder_path"], p["estado"], p["progreso_ms"]) == ("Casera (2020)", "activa", 5000)
    assert db.faltantes(conn) == []


def test_reasignacion_manual_toma_los_metadatos_de_la_nueva_si_el_faltante_no_tenia(biblioteca, conn):
    vieja = carpeta(biblioteca, "Alien", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso())
    db.marcar_vista(conn, 1, True)
    vieja.rename(biblioteca / "Alien (1979)")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))

    edicion.fusionar(conn, biblioteca, 1, 2)

    p = db.pelicula(conn, 1)
    assert (p["omdb_id"], p["watched"], p["director"]) == ("tt0078748", 1, ["Ridley Scott"])
    assert p["poster"] == "Alien (1979)/posters/poster.jpg"
    assert archivo_metadatos.leer(biblioteca / "Alien (1979)")["imdb_id"] == "tt0078748"
