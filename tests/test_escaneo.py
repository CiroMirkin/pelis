import json
import shutil

import pytest

from pelis import db
from pelis.escaneo import actualizar_poster, escanear, importar_sin_red, posters_de, rotar_posters
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


@pytest.mark.parametrize("nombre", ["poster.jpg", "Alien-poster.png", "POSTER Alien.jpeg", "poster-goodfelas.jpg", "alien_poster_2.jpg",
                                    "AlienPoster.jpg"])
def test_poster_con_la_palabra_en_cualquier_parte(biblioteca, conn, nombre):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "fanart.jpg", nombre)
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == f"Alien (1979)/{nombre}"


def test_poster_preferencias(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "cover.jpg", "folder.jpg", "alien-poster.jpg", "poster.png")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/poster.png"  # "poster" antes que folder/cover, exacto antes


def test_poster_poster_txt_no_cuenta(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "poster.txt", "Cover-alien.jpg")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/Cover-alien.jpg"


def test_poster_agregado_despues_se_toma_al_escanear(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] is None
    (c / "poster-alien.jpg").touch()
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/poster-alien.jpg"


def test_poster_a_mano_reemplaza_al_de_omdb(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/posters/poster.jpg"
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/posters/poster.jpg"  # sin cambios, sigue el bajado
    (c / "alien-poster.png").touch()
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/alien-poster.png"
    (c / "alien-poster.png").unlink()
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/posters/poster.jpg"  # borrado: vuelve al bajado
    assert conn.execute("SELECT count(*) FROM posters").fetchone()[0] == 2  # sin filas repetidas


def test_actualizar_poster_respeta_el_elegido_a_mano(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "otra.jpg")
    escanear(conn, biblioteca, OmdbFalso())
    db.agregar_poster(conn, 1, "Alien (1979)/otra.jpg", "manual")
    (c / "poster.jpg").touch()
    assert not actualizar_poster(conn, biblioteca, 1, "Alien (1979)")
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/otra.jpg"


def test_carpeta_posters_cuenta_toda_imagen_y_gana_a_las_sueltas(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "Posters/zeta.png", "Posters/notas.txt",
            "Posters/viejos/poster.jpg")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/Posters/zeta.png"
    assert sorted(posters_de(biblioteca, "Alien (1979)")) == ["Alien (1979)/Posters/zeta.png", "Alien (1979)/poster.jpg"]


def test_bajada_de_omdb_usa_la_carpeta_posters_existente(biblioteca, conn):
    (carpeta(biblioteca, "Alien (1979)", "Alien.mp4") / "Posters").mkdir()
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/Posters/poster.jpg"
    assert not (biblioteca / "Alien (1979)" / "posters").exists()


def test_poster_actual_que_ya_no_es_poster_se_reemplaza(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "backdrop.jpg", "folder.jpg")
    escanear(conn, biblioteca, OmdbFalso())
    db.usar_poster(conn, 1, "Alien (1979)/backdrop.jpg", "existente")  # lo que dejaba la rotación vieja
    assert actualizar_poster(conn, biblioteca, 1, "Alien (1979)")
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/folder.jpg"


def test_poster_actual_que_ya_no_es_poster_y_no_hay_otro_se_quita(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "backdrop.jpg")
    escanear(conn, biblioteca, OmdbFalso())
    db.usar_poster(conn, 1, "Alien (1979)/backdrop.jpg", "existente")
    assert actualizar_poster(conn, biblioteca, 1, "Alien (1979)")
    assert db.pelicula(conn, 1)["poster"] is None


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


class AzarFijo:
    """Elige siempre la primera opción, para que la rotación sea predecible."""

    def choice(self, opciones):
        return opciones[0]


FUTURO = "2999-01-01 00:00:00"


def test_rotacion_cambia_a_otro_poster(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "fanart.jpg", "posters/b.png")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/posters/b.png"

    assert rotar_posters(conn, biblioteca, ahora=FUTURO, azar=AzarFijo()) == 1
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/poster.jpg"
    # Abrir el detalle o escanear no deshace la rotación
    assert not actualizar_poster(conn, biblioteca, 1, "Alien (1979)")
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/poster.jpg"


def test_rotacion_espera_siete_dias(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "posters/b.jpg")
    escanear(conn, biblioteca, OmdbFalso())
    assert rotar_posters(conn, biblioteca) == 0  # recién asignado
    assert rotar_posters(conn, biblioteca, ahora=FUTURO, azar=AzarFijo()) == 1
    assert rotar_posters(conn, biblioteca) == 0  # la rotación reinicia el plazo
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/poster.jpg"


def test_rotacion_no_toca_peliculas_con_un_solo_poster(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "fanart.jpg", "backdrop.jpg")
    escanear(conn, biblioteca, OmdbFalso())
    assert rotar_posters(conn, biblioteca, ahora=FUTURO) == 0
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/poster.jpg"


def test_renovacion_manual_no_espera_y_reinicia_el_plazo(biblioteca, conn):
    carpeta(biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "folder.jpg")
    carpeta(biblioteca, "Heat (1995)", "Heat.mp4", "poster.jpg")
    escanear(conn, biblioteca, OmdbFalso())
    assert rotar_posters(conn, biblioteca, dias=0, azar=AzarFijo()) == 1  # Heat tiene un solo poster
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/folder.jpg"
    assert db.pelicula(conn, 2)["poster"] == "Heat (1995)/poster.jpg"
    assert rotar_posters(conn, biblioteca) == 0  # la renovación reinicia los siete días


def test_rotacion_incluye_el_poster_de_omdb_sin_que_lo_desplace_otra_imagen(biblioteca, conn):
    c = carpeta(biblioteca, "Alien (1979)", "Alien.mp4")
    escanear(conn, biblioteca, OmdbFalso({("Alien", 1979): DATOS_ALIEN}))
    (c / "folder.jpg").touch()
    escanear(conn, biblioteca, OmdbFalso())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/folder.jpg"  # la imagen nueva desplaza a la de OMDb

    rotar_posters(conn, biblioteca, ahora=FUTURO, azar=AzarFijo())
    assert db.pelicula(conn, 1)["poster"] == "Alien (1979)/posters/poster.jpg"
    assert not actualizar_poster(conn, biblioteca, 1, "Alien (1979)")  # folder.jpg ya no es "nueva"
