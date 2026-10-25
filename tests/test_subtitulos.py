from pelis import subtitulos
from pelis.subtitulos import Linea, elegir_audio, elegir_subtitulo

SRT = "1\n00:00:01,000 --> 00:00:03,000\n¡Mamá, tengo miedo!\n\n2\n00:00:04,000 --> 00:00:05,500\nAñoranza\n"


def test_leer_utf8(tmp_path):
    ruta = tmp_path / "a.srt"
    ruta.write_text(SRT, encoding="utf-8")
    eventos, codificacion = subtitulos.leer(ruta)
    assert codificacion == "utf-8-sig"
    assert eventos[0] == (1000, 3000, "¡Mamá, tengo miedo!")


def test_leer_cp1252(tmp_path):
    ruta = tmp_path / "a.srt"
    ruta.write_bytes(SRT.encode("cp1252"))
    eventos, codificacion = subtitulos.leer(ruta)
    assert codificacion == "cp1252"
    assert eventos[1][2] == "Añoranza"


def test_linea_texto_en():
    linea = Linea([(1000, 3000, "uno"), (2500, 4000, "dos"), (5000, 6000, "tres")])
    assert linea.texto_en(500) == ""
    assert linea.texto_en(1000) == "uno"
    assert linea.texto_en(2600) == "uno\ndos"
    assert linea.texto_en(4500) == ""
    assert linea.texto_en(5999) == "tres"


def test_externos_solo_mismo_nivel(tmp_path):
    (tmp_path / "Peli.mkv").touch()
    (tmp_path / "Peli.srt").touch()
    (tmp_path / "Peli.en.ASS").touch()
    (tmp_path / "poster.jpg").touch()
    (tmp_path / "Subs").mkdir()
    (tmp_path / "Subs" / "otro.srt").touch()
    assert [p.name for p in subtitulos.externos(tmp_path / "Peli.mkv")] == ["Peli.en.ASS", "Peli.srt"]


def test_subtitulo_mismo_nombre_gana():
    assert elegir_subtitulo("Peli.mkv", ["Peli.eng.srt", "Peli.srt"], [], "es") == ("externo", 1)


def test_subtitulo_externo_por_idioma():
    assert elegir_subtitulo("Peli.mkv", ["Peli.eng.srt", "Peli.spa.srt"], [], "es") == ("externo", 1)


def test_subtitulo_embebido_por_idioma_antes_que_unico_externo():
    embebidos = [{"idioma": "English", "titulo": ""}, {"idioma": "", "titulo": "Latino"}]
    assert elegir_subtitulo("Peli.mkv", ["subs.srt"], embebidos, "es") == ("embebido", 1)


def test_subtitulo_unico_externo():
    assert elegir_subtitulo("Peli.mkv", ["subs.srt"], [{"idioma": "English", "titulo": ""}], "es") == ("externo", 0)


def test_subtitulo_ninguno():
    assert elegir_subtitulo("Peli.mkv", ["a.srt", "b.srt"], [], "es") is None


def test_audio_por_metadatos_y_despues_titulo():
    pistas = [{"idioma": "English", "titulo": ""}, {"idioma": "", "titulo": "Castellano"}, {"idioma": "Spanish", "titulo": ""}]
    assert elegir_audio(pistas, "es") == 2
    assert elegir_audio(pistas[:2], "es") == 1
    assert elegir_audio(pistas[:1], "es") == -1
