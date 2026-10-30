from pathlib import Path

from pelis import db, poster
from pelis.catalogo import (
    Recomendacion, es_incompleta, filmografia, periodos, progreso_a_guardar, tarjeta, url_poster,
)
from pelis.puente import ModeloCatalogo


def catalogo(*peliculas, anio_actual=2026):
    """peliculas: (titulo, year, vista)"""
    conn = db.conectar(":memory:")
    for titulo, year, vista in peliculas:
        pelicula_id = db.insertar_pelicula(conn, titulo, year, titulo, f"{titulo}/{titulo}.mkv")
        db.marcar_vista(conn, pelicula_id, vista)
    modelo = ModeloCatalogo(anio_actual=anio_actual)
    modelo.recargar(db.catalogo(conn), Path("."))
    return modelo, conn


def titulos(modelo):
    return [f["titulo"] for f in modelo._filas]


def test_periodos_decadas_agrupadas_y_ultimos_cuatro_anios_sueltos():
    anios = [1942, 1964, 1968, 2004, 2015, 2021, 2023, 2025, 2026, None]
    assert periodos(anios, 2026) == [
        ("1940s", "Los 40s"), ("1960s", "Los 60s"), ("2000s", "Los 2000"), ("2010s", "Los 2010"),
        ("2023", "2023"), ("2025", "2025"), ("2026", "2026"),
    ]


def test_periodos_al_cambiar_de_decada():
    # En 2031 la de 2020 ya es una década anterior; sueltos: 2028 a 2031
    assert periodos([2021, 2029, 2031], 2031) == [("2020s", "Los 2020"), ("2029", "2029"), ("2031", "2031")]


def test_filtros_de_vistas_periodo_y_busqueda_se_combinan():
    modelo, _ = catalogo(("Alien", 1979, True), ("Aliens", 1986, False), ("Brazil", 1985, True),
                         ("Alpha", 2025, False), ("Sin año", None, False))
    modelo.filtrarPeriodo("1980s")
    assert titulos(modelo) == ["Aliens", "Brazil"]
    modelo.filtrarVistas("noVistas")
    assert titulos(modelo) == ["Aliens"]
    modelo.filtrar("brazil")
    assert titulos(modelo) == []
    modelo.filtrar("")
    modelo.filtrarPeriodo("2025")
    assert titulos(modelo) == ["Alpha"]
    modelo.filtrarPeriodo("")
    assert titulos(modelo) == ["Aliens", "Alpha", "Sin año"]


def test_periodo_elegido_que_desaparece_vuelve_a_todos():
    modelo, conn = catalogo(("Alien", 1979, False), ("Brazil", 1985, False))
    modelo.filtrarPeriodo("1970s")
    db.cambiar_estado(conn, 1, "faltante")
    modelo.recargar(db.catalogo(conn), Path("."))
    assert modelo.periodo == ""
    assert [p["clave"] for p in modelo.periodos] == ["1980s"]
    assert titulos(modelo) == ["Brazil"]


def test_filtro_incompletas_sin_datos_o_sin_portada(tmp_path):
    conn = db.conectar(":memory:")
    for titulo in ("Completa", "Sin datos", "Sin poster", "Poster borrado"):
        pelicula_id = db.insertar_pelicula(conn, titulo, None, titulo, f"{titulo}/{titulo}.mkv")
        if titulo != "Sin datos":
            db.fijar_metadatos(conn, pelicula_id, titulo, None)
        (tmp_path / titulo).mkdir()
        if titulo != "Sin poster":
            (tmp_path / titulo / "poster.jpg").write_bytes(b"")
            poster.revisar(conn, tmp_path, pelicula_id)
    (tmp_path / "Poster borrado" / "poster.jpg").unlink()
    modelo = ModeloCatalogo(anio_actual=2026)
    modelo.recargar(db.catalogo(conn), tmp_path)
    assert modelo.cantidadIncompletas == 3
    modelo.filtrarIncompletas(True)
    assert titulos(modelo) == ["Poster borrado", "Sin datos", "Sin poster"]
    modelo.filtrar("datos")
    assert titulos(modelo) == ["Sin datos"]
    modelo.filtrar("")
    modelo.filtrarIncompletas(False)
    assert len(titulos(modelo)) == 4


def fila(**datos):
    base = {"id": 1, "titulo": "Alien", "year": 1979, "poster": None, "progreso_ms": None,
            "duracion_ms": None, "watched": 0, "omdb_estado": "encontrada", "genero": "Terror"}
    return {**base, **datos}


def test_tarjeta_fraccion_de_progreso():
    assert tarjeta(fila(duracion_ms=0, progreso_ms=500), Path("."))["progreso"] == 0.0
    assert tarjeta(fila(duracion_ms=1000, progreso_ms=None), Path("."))["progreso"] == 0.0
    assert tarjeta(fila(duracion_ms=1000, progreso_ms=500), Path("."))["progreso"] == 0.5


def test_tarjeta_sin_poster_y_sin_anio():
    t = tarjeta(fila(year=None), Path("."))
    assert t == {"peliculaId": 1, "titulo": "Alien", "anio": 0, "poster": "", "progreso": 0.0, "vista": False}


def test_url_poster_con_espacios_y_enie(tmp_path):
    carpeta = tmp_path / "El año pasado"
    carpeta.mkdir()
    (carpeta / "poster.jpg").write_bytes(b"")
    url = url_poster(tmp_path, "El año pasado/poster.jpg")
    assert url.startswith("file://") and "El%20a%C3%B1o%20pasado/poster.jpg?v=" in url


def test_url_poster_de_archivo_borrado_sin_version(tmp_path):
    assert url_poster(tmp_path, "nada/poster.jpg") == (tmp_path / "nada/poster.jpg").as_uri()


def test_incompleta_sin_datos_sin_poster_o_poster_borrado(tmp_path):
    (tmp_path / "poster.jpg").write_bytes(b"")
    assert not es_incompleta(fila(poster="poster.jpg"), tmp_path)
    assert es_incompleta(fila(poster="poster.jpg", omdb_estado="pendiente"), tmp_path)
    assert es_incompleta(fila(poster=None), tmp_path)
    assert es_incompleta(fila(poster="borrado.jpg"), tmp_path)


def test_peliculas_de_persona_comparten_tarjeta_y_suman_roles(tmp_path):
    conn = db.conectar(":memory:")
    pelicula_id = db.insertar_pelicula(conn, "Alien", 1979, "Alien", "Alien/Alien.mkv")
    db.fijar_metadatos(conn, pelicula_id, "Alien", 1979, directores=["Ridley Scott"], actores=["Ridley Scott"])
    assert filmografia(db.peliculas_de_persona(conn, "Ridley Scott"), tmp_path) == [
        {"peliculaId": pelicula_id, "titulo": "Alien", "anio": 1979, "poster": "", "progreso": 0.0,
         "vista": False, "roles": ["actor", "director"]},
    ]


def test_recomendada_se_elige_una_sola_vez():
    r = Recomendacion()
    assert r.elegir(fila(), Path("."))
    assert not r.elegir(fila(id=2, titulo="Brazil"), Path("."))
    assert r.datos["titulo"] == "Alien"


def test_recomendada_con_biblioteca_vacia_se_reintenta():
    r = Recomendacion()
    assert not r.elegir(None, Path("."))
    assert r.elegir(fila(), Path("."))


def test_recomendada_cerrada_no_se_vuelve_a_elegir():
    r = Recomendacion()
    r.elegir(fila(), Path("."))
    assert r.cerrar()
    assert r.datos == {}
    assert not r.elegir(fila(id=2), Path("."))
    assert not r.cerrar()


def test_recomendada_empezo_solo_cierra_la_suya():
    r = Recomendacion()
    r.elegir(fila(), Path("."))
    assert not r.empezo(2)
    assert r.datos
    assert r.empezo(1)
    assert r.datos == {}


def test_recomendada_poster_y_duracion_sin_cambio_devuelven_false():
    r = Recomendacion()
    assert not r.poster("file:///x.jpg")
    r.elegir(fila(), Path("."))
    assert not r.poster("")
    assert r.poster("file:///x.jpg")
    assert not r.duracion(1, 0)
    assert not r.duracion(2, 9000)
    assert r.duracion(1, 9000)
    assert r.datos["duracion"] == 9000


def test_progreso_cuenta_desde_los_3_minutos():
    assert progreso_a_guardar(0) == 0
    assert progreso_a_guardar(179_999) == 0
    assert progreso_a_guardar(180_000) == 180_000
    assert progreso_a_guardar(2_400_000) == 2_400_000
