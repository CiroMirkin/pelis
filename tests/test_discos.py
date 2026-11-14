import sqlite3
import sys
import time

import pytest
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtGui import QColor, QImage

from pelis import db
from pelis.config import Config
from pelis.discos import INTERVALO, separar
from pelis.puente import Puente
from pelis.reproduccion import Sesion


class Volumenes:
    """Lo que ve el sondeo: se le suman y se le sacan discos como si se enchufaran."""

    def __init__(self):
        self.montados = []

    def __call__(self):
        return list(self.montados)


def crear_disco(raiz, nombre="Disco", peliculas=("Alien",), con_toml=True, con_duracion=True, archivos=()):
    """Un disco con su propia app: app/pelis.db, app/pelis.toml y la carpeta de películas al lado.
    `archivos` se crean dentro de la carpeta de cada película."""
    disco = raiz / nombre
    (disco / "app").mkdir(parents=True)
    (disco / "Peliculas").mkdir()
    if con_toml:
        (disco / "app" / "pelis.toml").write_text('biblioteca = "../Peliculas"\n')
    conn = db.conectar(disco / "app" / "pelis.db")
    for titulo in peliculas:
        (disco / "Peliculas" / titulo).mkdir()
        (disco / "Peliculas" / titulo / f"{titulo}.mp4").touch()
        for archivo in archivos:
            (disco / "Peliculas" / titulo / archivo).touch()
        pid = db.insertar_pelicula(conn, titulo, 1979, titulo, f"{titulo}/{titulo}.mp4")
        if con_duracion:
            db.guardar_duracion(conn, pid, 1000)
    conn.commit()
    conn.close()
    return disco


def en_solo_lectura(disco):
    """Le agrega a la db una columna que esta versión no conoce, así que la compu la abre en solo lectura."""
    conn = sqlite3.connect(disco / "app" / "pelis.db")
    conn.execute("ALTER TABLE peliculas ADD COLUMN de_otra_version TEXT")
    conn.commit()
    conn.close()


@pytest.fixture
def volumenes():
    return Volumenes()


@pytest.fixture
def puente(tmp_path, volumenes):
    QCoreApplication.instance() or QCoreApplication([])
    (tmp_path / "compu" / "app").mkdir(parents=True)
    biblioteca = tmp_path / "compu" / "Peliculas"
    biblioteca.mkdir(parents=True)
    p = Puente(Config(tmp_path / "compu" / "app", biblioteca, "", "", [], "", ""), volumenes=volumenes)
    while p._hilo is not None:  # la importación al abrir bloquea las acciones que escriben portadas
        QCoreApplication.processEvents()
    yield p
    p.cerrar()


def titulos(puente):
    return [f["titulo"] for f in puente.catalogo._filas]


def tarjeta_de(puente, titulo):
    return next(f for f in puente.catalogo._filas if f["titulo"] == titulo)


def test_un_disco_con_app_entra_al_catalogo_y_al_sacarlo_desaparece(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    t = tarjeta_de(puente, "Alien")
    assert t["disco"] == "Disco"
    assert separar(t["peliculaId"])[0] == 1
    assert puente.hayDiscos

    volumenes.montados = []
    puente._sondear()
    assert titulos(puente) == []
    assert not puente.hayDiscos


def test_la_db_de_la_compu_no_guarda_nada_de_un_disco(puente, volumenes, tmp_path):
    volumenes.montados = [(crear_disco(tmp_path), "Disco")]
    puente._sondear()
    assert puente.conn.execute("SELECT count(*) FROM peliculas").fetchone()[0] == 0


def test_las_ediciones_de_una_peli_del_disco_van_a_la_db_del_disco(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    pid = tarjeta_de(puente, "Alien")["peliculaId"]
    puente.marcarVista(pid, True)
    assert tarjeta_de(puente, "Alien")["vista"]
    assert puente.pelicula(pid)["disco"] == "Disco"
    puente._discos.cerrar()
    conn = sqlite3.connect(disco / "app" / "pelis.db")
    assert conn.execute("SELECT watched FROM peliculas").fetchone()[0] == 1
    conn.close()


def test_peli_repetida_en_compu_y_disco_da_dos_tarjetas(puente, volumenes, tmp_path):
    carpeta = puente.config.biblioteca / "Alien"
    carpeta.mkdir()
    db.insertar_pelicula(puente.conn, "Alien", 1979, "Alien", "Alien/Alien.mp4")
    puente.conn.commit()
    volumenes.montados = [(crear_disco(tmp_path), "Disco")]
    puente._sondear()
    assert sorted(f["disco"] for f in puente.catalogo._filas) == ["", "Disco"]


def test_esquema_distinto_es_solo_lectura_y_avisa_una_vez(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    en_solo_lectura(disco)
    avisos = []
    puente.avisoDisco.connect(avisos.append)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    puente._sondear()
    pid = tarjeta_de(puente, "Alien")["peliculaId"]
    assert puente.pelicula(pid)["soloLectura"]
    puente.marcarVista(pid, True)
    assert not tarjeta_de(puente, "Alien")["vista"]
    assert puente.guardarEdicion(pid, {}).startswith("Este disco está en solo lectura")
    assert len(avisos) == 1 and "solo lectura" in avisos[0]


def test_una_base_tomada_por_otra_app_se_abre_en_solo_lectura_hasta_que_se_libera(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    ocupante = sqlite3.connect(disco / "app" / "pelis.db")
    ocupante.execute("BEGIN IMMEDIATE")
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    pid = tarjeta_de(puente, "Alien")["peliculaId"]
    assert puente.pelicula(pid)["soloLectura"]

    ocupante.rollback()
    ocupante.close()
    puente._sondear()
    assert not puente.pelicula(pid)["soloLectura"]


def test_se_descarta_el_disco_que_es_esta_misma_app_aunque_su_biblioteca_sea_otra(puente, volumenes):
    (puente.config.app_dir.parent / "Otras").mkdir()
    (puente.config.app_dir / "pelis.toml").write_text('biblioteca = "../Otras"\n')
    volumenes.montados = [(puente.config.app_dir.parent, "Compu")]
    puente._sondear()
    assert not puente.hayDiscos
    assert puente._discos.lista() == []


def test_se_descarta_el_disco_con_la_misma_biblioteca(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    (disco / "app" / "pelis.toml").write_text(f'biblioteca = "{puente.config.biblioteca}"\n')
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    assert not puente.hayDiscos


def test_un_disco_sin_biblioteca_se_omite_con_un_aviso(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path, con_toml=False)
    avisos = []
    puente.avisoDisco.connect(avisos.append)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    puente._sondear()
    assert not puente.hayDiscos
    assert len(avisos) == 1 and "Disco" in avisos[0]


def test_la_biblioteca_del_disco_la_gana_su_preferencias_ini(puente, volumenes, tmp_path):
    from PySide6.QtCore import QSettings

    disco = crear_disco(tmp_path)
    otra = disco / "Otras"
    otra.mkdir()
    ajustes = QSettings(str(disco / "app" / "preferencias.ini"), QSettings.IniFormat)
    ajustes.setValue("biblioteca/ruta", "../Otras")
    ajustes.sync()
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    assert next(iter(puente._discos.abiertas.values())).biblioteca == otra.resolve()


def test_funciona_sin_biblioteca_en_la_compu(tmp_path, volumenes):
    QCoreApplication.instance() or QCoreApplication([])
    volumenes.montados = [(crear_disco(tmp_path), "Disco")]
    (tmp_path / "compu").mkdir()
    p = Puente(Config(tmp_path / "compu", None, "", "", [], "", ""), volumenes=volumenes)
    try:
        assert not p.hayBiblioteca and p.hayDiscos
        assert titulos(p) == ["Alien"]
    finally:
        p.cerrar()


def test_ocultar_un_disco_lo_saca_y_mostrarlo_lo_devuelve(puente, volumenes, tmp_path):
    volumenes.montados = [(crear_disco(tmp_path), "Disco")]
    puente._sondear()
    clave = puente.discos()[0]["id"]
    puente.ocultarDisco(clave, True)
    assert titulos(puente) == [] and puente.discos()[0]["oculto"]
    puente.ocultarDisco(clave, False)
    assert titulos(puente) == ["Alien"]


def test_disco_agregado_a_mano_se_guarda_se_reintenta_y_se_quita(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    assert puente.agregarDisco(str(disco)) == ""
    assert titulos(puente) == ["Alien"]
    assert puente.discos()[0]["manual"]

    # Reabrir la app: el disco sigue en preferencias.ini
    puente._discos.cerrar()
    puente._sondear()
    assert titulos(puente) == ["Alien"]

    puente.quitarDisco(puente.discos()[0]["id"])
    assert titulos(puente) == []


def test_agregar_una_carpeta_sin_app_da_error(puente, tmp_path):
    (tmp_path / "vacia").mkdir()
    assert "no tiene una app" in puente.agregarDisco(str(tmp_path / "vacia"))


def test_los_detectados_solos_no_se_pueden_quitar(puente, volumenes, tmp_path):
    volumenes.montados = [(crear_disco(tmp_path), "Disco")]
    puente._sondear()
    puente.quitarDisco(puente.discos()[0]["id"])
    assert titulos(puente) == ["Alien"]


def test_dos_discos_a_la_vez_tienen_ids_distintos(puente, volumenes, tmp_path):
    volumenes.montados = [(crear_disco(tmp_path, "A"), "A"), (crear_disco(tmp_path, "B"), "B")]
    puente._sondear()
    ids = [f["peliculaId"] for f in puente.catalogo._filas]
    assert len(set(ids)) == 2 and all(i >= INTERVALO for i in ids)


def test_el_disco_que_vuelve_conserva_su_indice(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    antes = tarjeta_de(puente, "Alien")["peliculaId"]
    volumenes.montados = []
    puente._sondear()
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    assert tarjeta_de(puente, "Alien")["peliculaId"] == antes


def test_la_recomendada_puede_ser_de_un_disco_y_se_cierra_al_sacarlo(puente, volumenes, tmp_path):
    volumenes.montados = [(crear_disco(tmp_path), "Disco")]
    puente._sondear()
    puente.recomendar()
    assert puente.recomendada["titulo"] == "Alien"
    volumenes.montados = []
    puente._sondear()
    assert puente.recomendada == {}


def test_la_filmografia_incluye_las_pelis_del_disco(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    conn = sqlite3.connect(disco / "app" / "pelis.db")
    conn.execute("INSERT INTO personas (nombre) VALUES ('Ridley Scott')")
    conn.execute("INSERT INTO pelicula_personas VALUES (1, 1, 'director')")
    conn.commit()
    conn.close()
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    peliculas = puente.peliculasDe("Ridley Scott")
    assert [(p["titulo"], p["disco"]) for p in peliculas] == [("Alien", "Disco")]


@pytest.mark.skipif(sys.platform == "win32", reason="Windows no deja renombrar una db abierta, que es como se simula sacar el disco")
def test_avisa_si_se_saca_el_disco_en_plena_reproduccion_y_no_guarda_el_progreso(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    pid = tarjeta_de(puente, "Alien")["peliculaId"]
    puente.abrir(pid, -1)
    puente.reproduccionCargo(10 * 60 * 1000)
    avisos = []
    puente.discoSacado.connect(avisos.append)

    volumenes.montados = []
    (disco / "app" / "pelis.db").rename(disco / "app" / "movida.db")
    puente._sondear()
    puente._sondear()
    assert avisos == ["Disco"]
    puente.reproduccionSalio(10 * 60 * 1000)
    assert puente.hayDiscos  # durante la reproducción no se busca ni se cierra nada

    (disco / "app" / "movida.db").rename(disco / "app" / "pelis.db")
    puente.salioDelReproductor()
    conn = sqlite3.connect(disco / "app" / "pelis.db")
    assert conn.execute("SELECT progreso_ms FROM peliculas").fetchone()[0] == 0
    conn.close()


def test_una_reproduccion_de_un_disco_en_solo_lectura_no_guarda_duracion_progreso_ni_vista(tmp_path):
    conn = db.conectar(tmp_path / "p.db")
    pid = db.insertar_pelicula(conn, "X", None, "X", "X/x.mp4")
    sesion = Sesion(conn, pid, escribe=False)
    sesion.cargo(10 * 60 * 1000)
    assert sesion.pauso(5 * 60 * 1000) is None
    assert sesion.termino() is None
    row = conn.execute("SELECT progreso_ms, duracion_ms, watched FROM peliculas").fetchone()
    assert tuple(row) == (0, None, 0)


def test_no_cambia_la_portada_de_una_peli_de_un_disco_en_solo_lectura(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path, archivos=("poster.jpg", "folder.jpg"))
    en_solo_lectura(disco)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    pid = tarjeta_de(puente, "Alien")["peliculaId"]
    assert not puente.siguientePortada(pid)


def test_rechaza_traer_datos_de_imdb_para_una_peli_de_un_disco_en_solo_lectura(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    en_solo_lectura(disco)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    pid = tarjeta_de(puente, "Alien")["peliculaId"]
    respuestas = []
    puente.imdbRespondio.connect(respuestas.append)
    puente.usarImdb(pid, "tt0078748")
    assert len(respuestas) == 1 and "solo lectura" in respuestas[0]["error"]


class CuadroFalso:
    def isValid(self):
        return True

    def toImage(self):
        imagen = QImage(4, 4, QImage.Format_RGB32)
        imagen.fill(QColor("red"))
        return imagen


class SinkFalso:
    def videoFrame(self):
        return CuadroFalso()


def test_no_guarda_capturas_de_un_disco_en_solo_lectura(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    en_solo_lectura(disco)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    pid = tarjeta_de(puente, "Alien")["peliculaId"]
    puente.abrir(pid, -1)
    resultados = []
    puente.capturaGuardada.connect(resultados.append)
    puente.capturar(SinkFalso(), 5000)
    time.sleep(0.5)  # una captura que sí se escribiera lo haría en otro hilo
    assert resultados == [False]
    assert not (disco / "Peliculas" / "Alien" / "capturas").exists()


def test_no_mide_la_duracion_de_una_peli_de_un_disco_en_solo_lectura(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path, con_duracion=False)
    en_solo_lectura(disco)
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    puente.pelicula(tarjeta_de(puente, "Alien")["peliculaId"])
    assert puente._midiendo == set()


def test_ordena_juntas_las_pelis_de_la_compu_y_del_disco_con_las_vistas_al_final(puente, volumenes, tmp_path):
    db.insertar_pelicula(puente.conn, "Zeta", 1990, "Zeta", "Zeta/Zeta.mp4")
    puente.conn.commit()
    disco = crear_disco(tmp_path, peliculas=("Alfa", "Mono"))
    conn = sqlite3.connect(disco / "app" / "pelis.db")
    conn.execute("UPDATE peliculas SET watched = 1 WHERE titulo = 'Mono'")
    conn.commit()
    conn.close()
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    assert titulos(puente) == ["Alfa", "Zeta", "Mono"]


def test_ordena_por_anio_la_filmografia_de_la_compu_y_del_disco(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    conn = sqlite3.connect(disco / "app" / "pelis.db")
    conn.execute("INSERT INTO personas (nombre) VALUES ('Ridley Scott')")
    conn.execute("INSERT INTO pelicula_personas VALUES (1, 1, 'director')")
    conn.commit()
    conn.close()
    zeta = db.insertar_pelicula(puente.conn, "Zeta", 1990, "Zeta", "Zeta/Zeta.mp4")
    puente.conn.execute("INSERT INTO personas (nombre) VALUES ('Ridley Scott')")
    puente.conn.execute("INSERT INTO pelicula_personas VALUES (?, 1, 'director')", (zeta,))
    puente.conn.commit()
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    assert [p["titulo"] for p in puente.peliculasDe("Ridley Scott")] == ["Alien", "Zeta"]


def test_diez_segundos_despues_de_salir_del_reproductor_busca_los_discos_de_nuevo(puente, volumenes, tmp_path, monkeypatch):
    class TimerFalso(QTimer):
        llamadas = []

        @staticmethod
        def singleShot(ms, funcion):
            TimerFalso.llamadas.append((ms, funcion))

    monkeypatch.setattr("pelis.puente.QTimer", TimerFalso)
    volumenes.montados = [(crear_disco(tmp_path), "Disco")]
    puente._sondear()
    puente.abrir(tarjeta_de(puente, "Alien")["peliculaId"], -1)
    volumenes.montados = []
    puente.salioDelReproductor()
    ms, buscar = TimerFalso.llamadas[0]
    assert ms == 10_000
    assert puente.hayDiscos
    buscar()
    assert not puente.hayDiscos


def test_un_disco_agregado_a_mano_muestra_la_etiqueta_de_su_volumen(puente, volumenes, tmp_path):
    disco = crear_disco(tmp_path)
    volumenes.montados = [(tmp_path, "Mi volumen")]
    puente.agregarDisco(str(disco))
    assert tarjeta_de(puente, "Alien")["disco"] == "Mi volumen"


def test_un_disco_que_no_se_puede_leer_no_rompe_el_catalogo_de_la_compu(puente, volumenes, tmp_path):
    db.insertar_pelicula(puente.conn, "Zeta", 1990, "Zeta", "Zeta/Zeta.mp4")
    puente.conn.commit()
    disco = crear_disco(tmp_path)
    conn = sqlite3.connect(disco / "app" / "pelis.db")
    conn.execute("ALTER TABLE posters RENAME TO posters_vieja")
    conn.commit()
    conn.close()
    volumenes.montados = [(disco, "Disco")]
    puente._sondear()
    assert titulos(puente) == ["Zeta"]


def test_no_deja_agregar_la_app_que_se_esta_usando(puente):
    assert "la app que estás usando" in puente.agregarDisco(str(puente.config.app_dir))
    assert puente.discos() == []
