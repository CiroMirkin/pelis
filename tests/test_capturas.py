from pelis import capturas


def test_nombre_es_la_posicion_truncada_al_segundo(tmp_path):
    # 1 h 2 min 3,999 s
    assert capturas.ruta_libre(tmp_path, 3_723_999) == tmp_path / "capturas" / "01-02-03.png"


def test_si_ya_existe_usa_el_primer_sufijo_libre(tmp_path):
    carpeta = tmp_path / "capturas"
    carpeta.mkdir()
    (carpeta / "00-12-34.png").touch()
    assert capturas.ruta_libre(tmp_path, 754_000) == carpeta / "00-12-34(2).png"
    (carpeta / "00-12-34(2).png").touch()
    assert capturas.ruta_libre(tmp_path, 754_500) == carpeta / "00-12-34(3).png"


def test_un_hueco_en_los_sufijos_se_reusa(tmp_path):
    carpeta = tmp_path / "capturas"
    carpeta.mkdir()
    for nombre in ("00-00-05.png", "00-00-05(3).png"):
        (carpeta / nombre).touch()
    assert capturas.ruta_libre(tmp_path, 5_000) == carpeta / "00-00-05(2).png"


def test_las_horas_van_siempre_en_dos_digitos(tmp_path):
    assert capturas.ruta_libre(tmp_path, 0).name == "00-00-00.png"
    assert capturas.ruta_libre(tmp_path, 36_000_000).name == "10-00-00.png"


def test_guardar_crea_la_carpeta_y_no_pisa(tmp_path):
    primera = capturas.guardar(tmp_path, 61_000, b"uno")
    segunda = capturas.guardar(tmp_path, 61_200, b"dos")
    assert (primera.name, primera.read_bytes()) == ("00-01-01.png", b"uno")
    assert (segunda.name, segunda.read_bytes()) == ("00-01-01(2).png", b"dos")


def _capturas(tmp_path, *nombres):
    carpeta = tmp_path / "capturas"
    carpeta.mkdir()
    for nombre in nombres:
        (carpeta / nombre).touch()
    return carpeta


def test_listar_ordena_por_posicion_y_sufijo(tmp_path):
    _capturas(tmp_path, "01-23-45(2).png", "00-00-10(10).png", "01-23-45.png", "00-00-10(3).png")
    assert [r.name for r in capturas.listar(tmp_path)] == [
        "00-00-10(3).png", "00-00-10(10).png", "01-23-45.png", "01-23-45(2).png"]


def test_listar_deja_las_demas_al_final_alfabeticas(tmp_path):
    _capturas(tmp_path, "foto.jpg", "Bosque.webp", "23-59-59.png", "afiche.JPEG", "1-2-3.png")
    assert [r.name for r in capturas.listar(tmp_path)] == [
        "23-59-59.png", "1-2-3.png", "afiche.JPEG", "Bosque.webp", "foto.jpg"]


def test_listar_solo_imagenes(tmp_path):
    carpeta = _capturas(tmp_path, "00-00-01.PNG", "notas.txt", "00-00-02.gif")
    (carpeta / "sub.png").mkdir()
    assert [r.name for r in capturas.listar(tmp_path)] == ["00-00-01.PNG"]


def test_listar_sin_carpeta_es_vacio(tmp_path):
    assert capturas.listar(tmp_path) == []


def test_un_symlink_roto_ocupa_el_nombre(tmp_path):
    carpeta = tmp_path / "capturas"
    carpeta.mkdir()
    (carpeta / "00-00-05.png").symlink_to(tmp_path / "no-existe")
    assert capturas.ruta_libre(tmp_path, 5_000) == carpeta / "00-00-05(2).png"
