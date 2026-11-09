import pytest

from pelis import db
from pelis.reproduccion import Sesion

UNA_HORA = 3_600_000


@pytest.fixture
def conn():
    conn = db.conectar(":memory:")
    yield conn
    conn.close()


def nueva(conn, progreso=0, titulo="Alien"):
    pelicula_id = db.insertar_pelicula(conn, titulo, None, titulo, f"{titulo}/{titulo}.mkv")
    db.guardar_progreso(conn, pelicula_id, progreso)
    return pelicula_id


def progreso(conn, pelicula_id):
    return db.pelicula(conn, pelicula_id)["progreso_ms"]


def test_salir_antes_de_3_minutos_no_la_deja_empezada(conn):
    p = nueva(conn)
    sesion = Sesion(conn, p)
    sesion.cargo(UNA_HORA)

    assert sesion.salio(179_999) is None
    assert progreso(conn, p) == 0


def test_salir_desde_los_3_minutos_guarda_el_progreso(conn):
    p = nueva(conn)
    sesion = Sesion(conn, p)
    sesion.cargo(UNA_HORA)

    assert sesion.salio(180_000) == "empezada"
    assert progreso(conn, p) == 180_000


def test_retomar_arranca_15_segundos_antes_del_progreso(conn):
    assert Sesion(conn, nueva(conn, progreso=2_400_000)).cargo(UNA_HORA) == 2_385_000
    assert Sesion(conn, nueva(conn, progreso=10_000, titulo="Dune")).cargo(UNA_HORA) == 0


def test_pausar_guarda_el_progreso(conn):
    p = nueva(conn)
    sesion = Sesion(conn, p)
    sesion.cargo(UNA_HORA)

    assert sesion.pauso(600_000) == "empezada"
    assert progreso(conn, p) == 600_000


def test_llegar_al_final_la_marca_vista_y_vuelve_al_principio(conn):
    p = nueva(conn, progreso=600_000)
    sesion = Sesion(conn, p)
    sesion.cargo(UNA_HORA)

    assert sesion.termino() == "vista"
    assert progreso(conn, p) == 0
    assert db.pelicula(conn, p)["watched"] == 1


def test_salir_despues_del_final_no_pisa_el_progreso(conn):
    p = nueva(conn)
    sesion = Sesion(conn, p)
    sesion.cargo(UNA_HORA)
    sesion.termino()

    assert sesion.salio(UNA_HORA) is None
    assert progreso(conn, p) == 0


def test_volver_a_reproducir_despues_del_final_vuelve_a_guardar_al_salir(conn):
    p = nueva(conn)
    sesion = Sesion(conn, p)
    sesion.cargo(UNA_HORA)
    sesion.termino()
    sesion.reanudo()

    assert sesion.salio(600_000) == "empezada"
    assert progreso(conn, p) == 600_000


def test_una_visita_no_toca_el_progreso_ni_la_vista(conn):
    p = nueva(conn, progreso=600_000)
    sesion = Sesion(conn, p, visita_ms=1_200_000)
    sesion.cargo(UNA_HORA)

    assert sesion.pauso(1_500_000) is None
    assert sesion.termino() is None
    sesion.reanudo()
    assert sesion.salio(2_000_000) is None
    assert progreso(conn, p) == 600_000
    assert db.pelicula(conn, p)["watched"] == 0


def test_una_visita_arranca_5_segundos_antes_acotada_al_final(conn):
    p = nueva(conn)

    assert Sesion(conn, p, visita_ms=30_000).cargo(60_000) == 25_000
    assert Sesion(conn, p, visita_ms=59_000).cargo(60_000) == 54_000
    assert Sesion(conn, p, visita_ms=70_000).cargo(60_000) == 55_000
    assert Sesion(conn, p, visita_ms=3_000).cargo(60_000) == 0


def test_una_visita_sin_duracion_arranca_5_segundos_antes_sin_acotar(conn):
    assert Sesion(conn, nueva(conn), visita_ms=90_000).cargo(0) == 85_000


def test_los_avisos_antes_de_cargar_no_guardan_nada(conn):
    p = nueva(conn, progreso=600_000)
    sesion = Sesion(conn, p)

    assert sesion.pauso(900_000) is None
    assert sesion.termino() is None
    assert sesion.salio(900_000) is None
    assert progreso(conn, p) == 600_000
    assert db.pelicula(conn, p)["watched"] == 0


def test_salir_dos_veces_guarda_una_sola_vez(conn):
    p = nueva(conn)
    sesion = Sesion(conn, p)
    sesion.cargo(UNA_HORA)
    sesion.salio(600_000)

    assert sesion.salio(900_000) is None
    assert sesion.pauso(900_000) is None
    assert progreso(conn, p) == 600_000


def test_cambiar_de_pista_no_vuelve_a_mover_el_arranque(conn):
    # QtMultimedia vuelve a avisar la carga al cambiar de pista de audio o subtítulos
    sesion = Sesion(conn, nueva(conn, progreso=600_000))
    sesion.cargo(UNA_HORA)

    assert sesion.cargo(UNA_HORA) is None


def test_cargar_guarda_la_duracion(conn):
    p = nueva(conn)
    Sesion(conn, p).cargo(UNA_HORA)

    assert db.pelicula(conn, p)["duracion_ms"] == UNA_HORA


def test_una_duracion_desconocida_no_borra_la_medida(conn):
    p = nueva(conn)
    db.guardar_duracion(conn, p, UNA_HORA)
    Sesion(conn, p).cargo(0)

    assert db.pelicula(conn, p)["duracion_ms"] == UNA_HORA


@pytest.mark.xfail(strict=True, reason="T9: el umbral de 3 min cruzado con el retroceso de 15 s; la regla se decide aparte")
def test_retomar_y_salir_enseguida_no_pierde_el_progreso(conn):
    p = nueva(conn, progreso=185_000)
    sesion = Sesion(conn, p)
    assert sesion.cargo(UNA_HORA) == 170_000

    sesion.salio(175_000)

    assert progreso(conn, p) >= 175_000
