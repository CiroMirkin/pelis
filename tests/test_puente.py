import pytest
from PySide6.QtCore import QCoreApplication

from pelis import db, poster
from pelis.catalogo import url_poster
from pelis.config import Config
from pelis.omdb import ErrorRed
from pelis.puente import Puente


def esperar_importacion(puente):
    while puente._hilo is not None:
        QCoreApplication.processEvents()


def importar(puente):
    puente._iniciar_escaneo(sin_red=True)
    esperar_importacion(puente)


@pytest.fixture
def puente(tmp_path):
    QCoreApplication.instance() or QCoreApplication([])
    biblioteca = tmp_path / "Peliculas"
    biblioteca.mkdir()
    p = Puente(Config(tmp_path, biblioteca, "", "", [], "", ""))
    esperar_importacion(p)
    yield p
    p.conn.close()


def pelicula(puente, nombre, *archivos):
    """Película con duración (no hay que medirla) y su poster registrado, si tiene."""
    carpeta = puente.config.biblioteca / nombre
    carpeta.mkdir()
    for a in archivos:
        (carpeta / a).parent.mkdir(exist_ok=True)
        (carpeta / a).touch()
    pelicula_id = db.insertar_pelicula(puente.conn, nombre, None, nombre, f"{nombre}/{nombre}.mp4")
    db.guardar_duracion(puente.conn, pelicula_id, 1000)
    poster.revisar(puente.conn, puente.config.biblioteca, pelicula_id)
    return pelicula_id


def url(puente, relativa):
    return url_poster(puente.config.biblioteca, relativa)


def bajado(puente, pelicula_id, nombre):
    (puente.config.biblioteca / nombre / "posters").mkdir(exist_ok=True)
    (puente.config.biblioteca / nombre / "posters" / "poster.jpg").touch()
    poster._usar(puente.conn, pelicula_id, f"{nombre}/posters/poster.jpg", "omdb")
    puente.conn.commit()


def test_abrir_el_detalle_con_una_imagen_nueva_actualiza_la_recomendada(puente):
    p = pelicula(puente, "Alien")
    bajado(puente, p, "Alien")
    puente.recomendar()
    (puente.config.biblioteca / "Alien" / "folder.jpg").touch()

    puente.pelicula(p)

    assert puente.recomendada["poster"] == url(puente, "Alien/folder.jpg")


def test_abrir_el_detalle_sin_el_poster_no_deja_una_imagen_rota_en_la_recomendada(puente):
    p = pelicula(puente, "Alien", "poster.jpg")
    puente.recomendar()
    assert puente.recomendada["poster"] == url(puente, "Alien/poster.jpg")
    (puente.config.biblioteca / "Alien" / "poster.jpg").unlink()

    puente.pelicula(p)

    assert puente.recomendada["poster"] == ""


def test_aplicar_datos_de_imdb_con_poster_bajado_actualiza_la_recomendada(puente):
    p = pelicula(puente, "Alien")
    puente.recomendar()
    destino = puente.config.biblioteca / "Alien" / "posters" / "poster.jpg"
    destino.parent.mkdir()
    destino.touch()

    puente._imdb_listo({"aplicar": (p, {"omdb_id": "tt0078748", "omdb_estado": "encontrada"}, True)})

    assert puente.recomendada["poster"] == url(puente, "Alien/posters/poster.jpg")


def test_el_cambio_de_poster_de_otra_pelicula_no_altera_la_recomendada(puente):
    pelicula(puente, "Alien", "poster.jpg")
    puente.recomendar()
    otra = pelicula(puente, "Aliens", "poster.jpg", "folder.jpg")
    antes = puente.recomendada

    assert puente.siguientePortada(otra)
    (puente.config.biblioteca / "Aliens" / "cover.jpg").touch()
    puente.pelicula(otra)

    assert puente.recomendada == antes


def test_pasar_a_la_portada_siguiente_actualiza_catalogo_y_recomendada(puente):
    p = pelicula(puente, "Alien", "poster.jpg", "folder.jpg")
    puente.recomendar()

    assert puente.siguientePortada(p)

    esperado = url(puente, "Alien/folder.jpg")
    assert puente.recomendada["poster"] == esperado
    assert [f["poster"] for f in puente.catalogo._filas] == [esperado]


def test_renovar_las_portadas_actualiza_catalogo_y_recomendada(puente):
    pelicula(puente, "Alien", "poster.jpg", "folder.jpg")
    puente.recomendar()

    assert puente.renovarPortadas() == 1

    esperado = url(puente, "Alien/folder.jpg")
    assert puente.recomendada["poster"] == esperado
    assert [f["poster"] for f in puente.catalogo._filas] == [esperado]


def test_terminar_un_escaneo_actualiza_catalogo_y_recomendada(puente):
    p = pelicula(puente, "Alien", "Alien.mp4", "poster.jpg", "folder.jpg")
    puente.recomendar()
    puente.conn.execute("UPDATE peliculas SET poster_actualizado_en = NULL WHERE id = ?", (p,))  # le toca rotar
    puente.conn.commit()

    importar(puente)

    esperado = url(puente, "Alien/folder.jpg")
    assert puente.recomendada["poster"] == esperado
    assert [f["poster"] for f in puente.catalogo._filas] == [esperado]


def contar_recargas(puente):
    recargas = []
    puente.catalogo.modelReset.connect(lambda: recargas.append(True))
    return recargas


def vista_en_catalogo(puente, pelicula_id):
    modelo = puente.catalogo
    rol = {v: k for k, v in modelo.roleNames().items()}
    filas = [modelo.index(i, 0) for i in range(modelo.rowCount())]
    return next(modelo.data(f, rol[b"vista"]) for f in filas if modelo.data(f, rol[b"peliculaId"]) == pelicula_id)


def reproducir(puente, pelicula_id, visita_ms=-1):
    puente.abrir(pelicula_id, visita_ms)
    return puente.reproduccionCargo(3_600_000)


def test_pausar_no_recarga_el_catalogo(puente):
    p = pelicula(puente, "Alien")
    reproducir(puente, p)
    recargas = contar_recargas(puente)

    puente.reproduccionPauso(300_000)

    assert recargas == []
    assert db.pelicula(puente.conn, p)["progreso_ms"] == 300_000


def test_empezar_la_recomendada_la_cierra(puente):
    p = pelicula(puente, "Alien")
    puente.recomendar()
    assert puente.recomendada["id"] == p
    reproducir(puente, p)

    puente.reproduccionPauso(300_000)

    assert puente.recomendada == {}


def test_llegar_al_final_recarga_el_catalogo_con_la_pelicula_vista(puente):
    p = pelicula(puente, "Alien")
    importar(puente)
    reproducir(puente, p)

    puente.reproduccionTermino()

    assert vista_en_catalogo(puente, p)


def test_una_visita_arranca_desde_la_posicion_pedida(puente):
    p = pelicula(puente, "Alien")

    assert reproducir(puente, p, visita_ms=600_000) == 595_000
    assert puente.reproduccionCargo(3_600_000) == -1


def test_salir_del_reproductor_recarga_el_catalogo(puente):
    recargas = contar_recargas(puente)

    puente.salioDelReproductor()

    assert recargas == [True]


def esperar_claves(puente):
    respuestas = []
    puente.clavesRespondio.connect(respuestas.append)
    while not respuestas:
        QCoreApplication.processEvents()
    return respuestas[0]


class ClienteFalso:
    """Reemplaza a Omdb/Tmdb: `resultado` es True/False, o una excepción si no se pudo saber."""
    def __init__(self, resultado):
        self.resultado = resultado

    def __call__(self, clave):
        self.clave = clave
        return self

    def clave_valida(self):
        if isinstance(self.resultado, Exception):
            raise self.resultado
        return self.resultado


def validar_con(monkeypatch, omdb=True, tmdb=True):
    monkeypatch.setattr("pelis.puente.Omdb", ClienteFalso(omdb))
    monkeypatch.setattr("pelis.puente.Tmdb", ClienteFalso(tmdb))


def test_guardar_claves_validas_las_aplica_en_caliente_y_las_recuerda(puente, monkeypatch):
    validar_con(monkeypatch)
    puente.guardarClaves(" k1 ", "k2")
    r = esperar_claves(puente)

    assert r["guardado"] and not r["errores"]
    assert puente.claves() == {"omdb": "k1", "tmdb": "k2"}
    reabierto = Puente(Config(puente.config.app_dir, puente.config.biblioteca, "", "", [], "", ""))
    esperar_importacion(reabierto)
    assert reabierto.claves() == {"omdb": "k1", "tmdb": "k2"}
    reabierto.conn.close()


def test_una_clave_invalida_no_guarda_ninguna(puente, monkeypatch):
    validar_con(monkeypatch, omdb=True, tmdb=False)
    puente.guardarClaves("k1", "k2")
    r = esperar_claves(puente)

    assert not r["guardado"] and list(r["errores"]) == ["tmdb"]
    assert puente.claves() == {"omdb": "", "tmdb": ""}


def test_sin_red_guarda_igual_y_avisa(puente, monkeypatch):
    validar_con(monkeypatch, omdb=ErrorRed("sin conexión"))
    puente.guardarClaves("k1", "")
    r = esperar_claves(puente)

    assert r["guardado"] and r["sinVerificar"]
    assert puente.claves()["omdb"] == "k1"


def test_solo_se_validan_las_claves_que_cambiaron(puente, monkeypatch):
    validar_con(monkeypatch)
    puente.guardarClaves("k1", "k2")
    esperar_claves(puente)
    validar_con(monkeypatch, omdb=False, tmdb=False)  # si se consultara alguna, fallaría

    puente.guardarClaves("k1", "k2")
    assert esperar_claves(puente)["guardado"]


def test_vaciar_la_clave_de_omdb_se_guarda_y_avisa(puente, monkeypatch):
    validar_con(monkeypatch)
    puente.guardarClaves("k1", "")
    esperar_claves(puente)

    puente.guardarClaves("", "")
    r = esperar_claves(puente)

    assert r["guardado"] and r["omdbVacia"]
    assert puente.claves()["omdb"] == ""


def test_la_clave_guardada_en_la_app_gana_incluso_vacia_sobre_la_del_toml(tmp_path):
    QCoreApplication.instance() or QCoreApplication([])
    biblioteca = tmp_path / "Peliculas"
    biblioteca.mkdir()
    (tmp_path / "preferencias.ini").write_text("[claves]\nomdb=\n")
    p = Puente(Config(tmp_path, biblioteca, "del-toml", "tmdb-del-toml", [], "", ""))
    esperar_importacion(p)

    assert p.claves() == {"omdb": "", "tmdb": "tmdb-del-toml"}
    p.conn.close()


def test_guardar_una_clave_de_omdb_nueva_informa_cuantas_pendientes_hay(puente, monkeypatch):
    validar_con(monkeypatch)
    pelicula(puente, "Alien", "Alien.mp4")
    db.marcar_pendiente(puente.conn, 1)
    puente.conn.commit()

    puente.guardarClaves("k1", "")

    assert esperar_claves(puente)["pendientes"] == 1
