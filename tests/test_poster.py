import pytest

from pelis import db, poster


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


def pelicula(conn, biblioteca, nombre, *archivos):
    """Crea la carpeta con `archivos` y su registro en la base; devuelve el id."""
    c = biblioteca / nombre
    c.mkdir()
    for a in archivos:
        (c / a).parent.mkdir(exist_ok=True)
        (c / a).touch()
    return db.insertar_pelicula(conn, nombre, None, nombre, f"{nombre}/{nombre}.mp4")


def bajado(conn, biblioteca, pelicula_id, nombre):
    """Simula la bajada del poster de OMDb a `posters/poster.jpg`."""
    (biblioteca / nombre / "posters").mkdir(exist_ok=True)
    (biblioteca / nombre / "posters" / "poster.jpg").touch()
    poster._usar(conn, pelicula_id, f"{nombre}/posters/poster.jpg", "omdb")
    conn.commit()


def actual(conn, pelicula_id):
    return db.pelicula(conn, pelicula_id)["poster"]


@pytest.mark.parametrize("nombre", ["poster.jpg", "Alien-poster.png", "POSTER Alien.jpeg", "poster-goodfelas.jpg", "alien_poster_2.jpg",
                                    "AlienPoster.jpg"])
def test_poster_con_la_palabra_en_cualquier_parte(biblioteca, conn, nombre):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "fanart.jpg", nombre)
    assert poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == f"Alien (1979)/{nombre}"


def test_poster_preferencias(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "cover.jpg", "folder.jpg", "alien-poster.jpg", "poster.png")
    poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/poster.png"  # "poster" antes que folder/cover, exacto antes


def test_poster_poster_txt_no_cuenta(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "poster.txt", "Cover-alien.jpg")
    poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/Cover-alien.jpg"


def test_carpeta_posters_cuenta_toda_imagen_y_gana_a_las_sueltas(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "Posters/zeta.png", "Posters/notas.txt",
                 "Posters/viejos/poster.jpg")
    poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/Posters/zeta.png"
    assert sorted(poster._posters_de(biblioteca, "Alien (1979)")) == ["Alien (1979)/Posters/zeta.png",
                                                                      "Alien (1979)/poster.jpg"]


def test_poster_a_mano_reemplaza_al_de_omdb(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4")
    bajado(conn, biblioteca, p, "Alien (1979)")
    assert not poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/posters/poster.jpg"
    (biblioteca / "Alien (1979)" / "alien-poster.png").touch()
    assert poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/alien-poster.png"
    (biblioteca / "Alien (1979)" / "alien-poster.png").unlink()
    assert poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/posters/poster.jpg"  # borrado: vuelve al bajado
    assert conn.execute("SELECT count(*) FROM posters").fetchone()[0] == 2  # sin filas repetidas


def test_poster_actual_que_ya_no_es_poster_se_reemplaza(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "backdrop.jpg", "folder.jpg")
    poster._usar(conn, p, "Alien (1979)/backdrop.jpg", "existente")  # lo que dejaba la rotación vieja
    assert poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/folder.jpg"


def test_poster_actual_que_ya_no_es_poster_y_no_hay_otro_se_quita(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "backdrop.jpg")
    poster._usar(conn, p, "Alien (1979)/backdrop.jpg", "existente")
    assert poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) is None


def test_revisar_guarda_sin_commit_aparte(biblioteca, conn, tmp_path):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg")
    poster.revisar(conn, biblioteca, p)
    otra = db.conectar(tmp_path / "pelis.db")
    assert db.pelicula(otra, p)["poster"] == "Alien (1979)/poster.jpg"
    otra.close()


class AzarFijo:
    """Elige siempre la primera opción, para que la rotación sea predecible."""

    def choice(self, opciones):
        return opciones[0]


FUTURO = "2999-01-01 00:00:00"


def test_rotacion_cambia_a_otro_poster(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "fanart.jpg", "posters/b.png")
    poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/posters/b.png"

    assert poster.rotar(conn, biblioteca, ahora=FUTURO, azar=AzarFijo()) == 1
    assert actual(conn, p) == "Alien (1979)/poster.jpg"
    # Abrir el detalle o escanear no deshace la rotación
    assert not poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/poster.jpg"


def test_rotacion_espera_siete_dias(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "posters/b.jpg")
    poster.revisar(conn, biblioteca, p)
    assert poster.rotar(conn, biblioteca) == 0  # recién asignado
    assert poster.rotar(conn, biblioteca, ahora=FUTURO, azar=AzarFijo()) == 1
    assert poster.rotar(conn, biblioteca) == 0  # la rotación reinicia el plazo
    assert actual(conn, p) == "Alien (1979)/poster.jpg"


def test_rotacion_no_toca_peliculas_con_un_solo_poster(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "fanart.jpg", "backdrop.jpg")
    poster.revisar(conn, biblioteca, p)
    assert poster.rotar(conn, biblioteca, ahora=FUTURO) == 0
    assert actual(conn, p) == "Alien (1979)/poster.jpg"


def test_renovacion_manual_no_espera_y_reinicia_el_plazo(biblioteca, conn):
    alien = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4", "poster.jpg", "folder.jpg")
    heat = pelicula(conn, biblioteca, "Heat (1995)", "Heat.mp4", "poster.jpg")
    poster.revisar(conn, biblioteca, alien)
    poster.revisar(conn, biblioteca, heat)
    assert poster.rotar(conn, biblioteca, dias=0, azar=AzarFijo()) == 1  # Heat tiene un solo poster
    assert actual(conn, alien) == "Alien (1979)/folder.jpg"
    assert actual(conn, heat) == "Heat (1995)/poster.jpg"
    assert poster.rotar(conn, biblioteca) == 0  # la renovación reinicia los siete días


def test_rotacion_incluye_el_poster_de_omdb_sin_que_lo_desplace_otra_imagen(biblioteca, conn):
    p = pelicula(conn, biblioteca, "Alien (1979)", "Alien.mp4")
    bajado(conn, biblioteca, p, "Alien (1979)")
    (biblioteca / "Alien (1979)" / "folder.jpg").touch()
    poster.revisar(conn, biblioteca, p)
    assert actual(conn, p) == "Alien (1979)/folder.jpg"  # la imagen nueva desplaza a la de OMDb

    poster.rotar(conn, biblioteca, ahora=FUTURO, azar=AzarFijo())
    assert actual(conn, p) == "Alien (1979)/posters/poster.jpg"
    assert not poster.revisar(conn, biblioteca, p)  # folder.jpg ya no es "nueva"
