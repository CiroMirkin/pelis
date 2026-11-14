import pytest

from pelis.omdb import ErrorRed
from pelis.tmdb import Tmdb


class RespuestaFalsa:
    def __init__(self, status_code):
        self.status_code = status_code


class SesionFalsa:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.pedidos = []

    def get(self, url, params, timeout):
        self.pedidos.append(params)
        return self.respuesta


def tmdb_con(status_code):
    tmdb = Tmdb("k1")
    tmdb.sesion = SesionFalsa(RespuestaFalsa(status_code))
    return tmdb


def test_clave_aceptada_es_valida():
    assert tmdb_con(200).clave_valida() is True


def test_clave_rechazada_no_es_valida():
    assert tmdb_con(401).clave_valida() is False


@pytest.mark.parametrize("status", [429, 500, 503])
def test_error_del_servidor_no_dice_si_la_clave_sirve(status):
    with pytest.raises(ErrorRed):
        tmdb_con(status).clave_valida()


def test_la_clave_se_envia_en_la_consulta():
    tmdb = tmdb_con(200)
    tmdb.clave_valida()
    assert tmdb.sesion.pedidos[0]["api_key"] == "k1"
