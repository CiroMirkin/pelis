import pytest

from pelis.omdb import ErrorRed, Omdb


class RespuestaFalsa:
    def __init__(self, datos=None, error_json=None, status_code=200):
        self._datos = datos
        self._error_json = error_json
        self.status_code = status_code

    def json(self):
        if self._error_json is not None:
            raise self._error_json
        return self._datos


class SesionFalsa:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = []

    def get(self, url, **kwargs):
        self.llamadas.append((url, kwargs))
        return self.respuesta


def omdb_con(respuesta):
    omdb = Omdb("clave")
    omdb.sesion = SesionFalsa(respuesta)
    return omdb


@pytest.mark.parametrize("error", ["Movie not found!", "Incorrect IMDb ID."])
def test_sin_pelicula_no_es_error_de_red(error):
    omdb = omdb_con(RespuestaFalsa({"Response": "False", "Error": error}))
    assert omdb.por_titulo("No existe", 2020) is None


@pytest.mark.parametrize("error", ["Invalid API key!", "Request limit reached!"])
def test_clave_y_limite_son_error_de_red(error):
    omdb = omdb_con(RespuestaFalsa({"Response": "False", "Error": error}))
    with pytest.raises(ErrorRed, match=error):
        omdb.por_titulo("Alien", 1979)


def test_respuesta_que_no_es_json_es_error_de_red():
    omdb = omdb_con(RespuestaFalsa(error_json=ValueError("no es JSON")))
    with pytest.raises(ErrorRed):
        omdb.por_id("tt0078748")


def test_buscar_traduce_demasiados_resultados():
    omdb = omdb_con(RespuestaFalsa({"Response": "False", "Error": "Too many results."}))
    with pytest.raises(ErrorRed, match="año"):
        omdb.buscar("Alien")
