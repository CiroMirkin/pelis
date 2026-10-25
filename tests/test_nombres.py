import pytest

from pelis.nombres import idioma_de, normalizar, parsear_carpeta, parsear_video


@pytest.mark.parametrize("nombre, esperado", [
    ("Alien (1979)", ("Alien", 1979, None)),
    ("(1979) Alien", ("Alien", 1979, None)),
    ("Alien (1979) [tt0078748]", ("Alien", 1979, "tt0078748")),
    ("Gatillero (2025) [TT1234567]", ("Gatillero", 2025, "tt1234567")),
    ("Kill Bill Vol. 1 (2003)", ("Kill Bill Vol. 1", 2003, None)),
    ("Red Desert (1964)", ("Red Desert", 1964, None)),
    ("Punch-Drunk Love", ("Punch-Drunk Love", None, None)),
    ("2001 A Space Odyssey (1968)", ("2001 A Space Odyssey", 1968, None)),
])
def test_parsear_carpeta(nombre, esperado):
    assert parsear_carpeta(nombre) == esperado


@pytest.mark.parametrize("archivo, esperado", [
    ("Red.Desert.1964.1080p.BluRay.x264-[YTS.AM].mp4", ("Red Desert", 1964)),
    ("Alpha (2025) 1080p .mkv", ("Alpha", 2025)),
    ("Alien.Romulus.2024.1080p.WEB.mkv", ("Alien Romulus", 2024)),
    ("2001.A.Space.Odyssey.1968.mkv", ("2001 A Space Odyssey", 1968)),
    ("Blade_Runner_1982_Final_Cut.mkv", ("Blade Runner", 1982)),
    ("pelicula.1080p.mkv", (None, None)),
])
def test_parsear_video(archivo, esperado):
    assert parsear_video(archivo) == esperado


@pytest.mark.parametrize("texto, esperado", [
    ("Alien.spa", "es"),
    ("Alien.Español", "es"),
    ("Latino", "es"),
    ("Castellano Forzados", "es"),
    ("Spanish", "es"),
    ("English SDH", "en"),
    ("Alien.eng", "en"),
    ("Alien 1979", None),
    ("Ukrainian", None),
    ("", None),
    (None, None),
])
def test_idioma_de(texto, esperado):
    assert idioma_de(texto) == esperado


def test_idioma_de_con_preferido():
    assert idioma_de("English", "es") is None
    assert idioma_de("English", "en") == "en"
    assert idioma_de("Alien.fr", "fr") == "fr"


@pytest.mark.parametrize("texto, esperado", [
    ("Pedro Almodóvar", "pedro almodovar"),
    ("ÉL", "el"),
    ("Peña", "pena"),
    ("Kill Bill Vol. 1", "kill bill vol. 1"),
])
def test_normalizar(texto, esperado):
    assert normalizar(texto) == esperado
