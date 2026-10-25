from pelis import db


def test_catalogo_pone_primero_las_en_progreso_y_al_final_las_vistas():
    conn = db.conectar(":memory:")
    ids = {t: db.insertar_pelicula(conn, t, None, t, f"{t}/{t}.mkv")
           for t in ("Alien", "Babel", "Casablanca", "Dune", "Eraserhead")}
    db.guardar_progreso(conn, ids["Dune"], 60000)
    db.guardar_progreso(conn, ids["Babel"], 1000)
    # Vista con progreso (por ejemplo, terminada en los créditos): no cuenta como en progreso
    db.guardar_progreso(conn, ids["Casablanca"], 5000)
    db.marcar_vista(conn, ids["Casablanca"], True)
    db.marcar_vista(conn, ids["Alien"], True)
    assert [f["titulo"] for f in db.catalogo(conn)] == ["Babel", "Dune", "Eraserhead", "Alien", "Casablanca"]


def test_recomendada_solo_entre_activas_sin_ver_ni_empezar():
    conn = db.conectar(":memory:")
    ids = {t: db.insertar_pelicula(conn, t, None, t, f"{t}/{t}.mkv") for t in ("Alien", "Babel", "Casablanca", "Dune")}
    db.marcar_vista(conn, ids["Alien"], True)
    db.guardar_progreso(conn, ids["Babel"], 1000)
    db.cambiar_estado(conn, ids["Casablanca"], "faltante")
    assert {db.recomendada(conn)["titulo"] for _ in range(20)} == {"Dune"}

    db.marcar_vista(conn, ids["Dune"], True)
    assert db.recomendada(conn) is None


def test_marcar_todas_vistas_solo_toca_las_activas_sin_ver():
    conn = db.conectar(":memory:")
    ids = {t: db.insertar_pelicula(conn, t, None, t, f"{t}/{t}.mkv") for t in ("Alien", "Babel", "Casablanca")}
    db.marcar_vista(conn, ids["Alien"], True)
    db.cambiar_estado(conn, ids["Casablanca"], "faltante")
    assert db.sin_ver(conn) == 1
    assert db.marcar_todas_vistas(conn) == 1
    assert db.sin_ver(conn) == 0
    assert not db.pelicula(conn, ids["Casablanca"])["watched"]


def test_personas_cuentan_solo_otras_peliculas_activas():
    conn = db.conectar(":memory:")
    ids = {t: db.insertar_pelicula(conn, t, y, t, f"{t}/{t}.mkv")
           for t, y in (("Alien", 1979), ("Gladiator", 2000), ("Blade Runner", 1982), ("Legend", 1985))}
    db.guardar_metadatos(conn, ids["Alien"], "encontrada", directores=["Ridley Scott"], actores=["Sigourney Weaver"])
    db.guardar_metadatos(conn, ids["Gladiator"], "encontrada", directores=["Ridley Scott"], actores=["Russell Crowe"])
    # Director y actor en la misma película cuenta una vez
    db.guardar_metadatos(conn, ids["Blade Runner"], "encontrada", directores=["Ridley Scott"], actores=["Ridley Scott"])
    db.guardar_metadatos(conn, ids["Legend"], "encontrada", directores=["Ridley Scott"])
    db.cambiar_estado(conn, ids["Legend"], "faltante")

    assert db.personas_de(conn, ids["Alien"], "director") == [("Ridley Scott", 2)]
    assert db.personas_de(conn, ids["Alien"], "actor") == [("Sigourney Weaver", 0)]

    filas = db.peliculas_de_persona(conn, "Ridley Scott")
    assert [(f["titulo"], sorted(f["roles"].split(","))) for f in filas] == [
        ("Alien", ["director"]), ("Blade Runner", ["actor", "director"]), ("Gladiator", ["director"]),
    ]
