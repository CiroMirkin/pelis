import pytest
import requests

from pelis import actualizacion


@pytest.mark.parametrize("tag, actual, esperado", [
    ("v0.2.0", "0.1.0", True),
    ("v0.1.0", "0.1.0", False),
    ("v0.1.0", "0.2.0", False),
    ("v0.10.0", "0.9.0", True),     # numérico, no alfabético
    ("v0.2.0", "0.2.0-rc2", True),  # la final le gana a su RC
    ("v0.2.0-rc1", "0.2.0", False),
    ("v0.2.0-rc2", "0.2.0-rc1", True),
    ("v0.2.0-rc1", "0.1.5", True),
    ("nightly", "0.1.0", False),
    ("v0.2.0", "dev", False),
])
def test_es_mas_nueva(tag, actual, esperado):
    assert actualizacion.es_mas_nueva(tag, actual) is esperado


class Respuesta:
    def __init__(self, status_code=200, datos=None, error=None):
        self.status_code = status_code
        self.datos = datos
        self.error = error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        if self.error:
            raise self.error
        return self.datos


class Sesion:
    def __init__(self, respuesta=None, error=None):
        self.respuesta = respuesta
        self.error = error
        self.urls = []

    def get(self, url, **_):
        self.urls.append(url)
        if self.error:
            raise self.error
        return self.respuesta


RELEASE = {
    "tag_name": "v0.3.0",
    "body": "## Nuevo\n\n- Buscar actualización",
    "assets": [
        {"name": "Pelis-windows-v0.3.0.zip", "browser_download_url": "https://x/win.zip"},
        {"name": "SHA256SUMS", "browser_download_url": "https://x/SHA256SUMS"},
    ],
}


def test_hay_version_nueva():
    sesion = Sesion(Respuesta(datos=RELEASE))
    assert actualizacion.buscar(sesion, actual="0.2.0") == {
        "version": "0.3.0",
        "notas": "## Nuevo\n\n- Buscar actualización",
        "paquetes": {"Pelis-windows-v0.3.0.zip": "https://x/win.zip", "SHA256SUMS": "https://x/SHA256SUMS"},
    }
    assert sesion.urls == [actualizacion.API]


def test_al_dia():
    assert actualizacion.buscar(Sesion(Respuesta(datos=RELEASE)), actual="0.3.0") is None


def test_sin_releases_es_al_dia():
    assert actualizacion.buscar(Sesion(Respuesta(status_code=404)), actual="0.1.0") is None


@pytest.mark.parametrize("sesion", [
    Sesion(error=requests.ConnectionError("sin red")),
    Sesion(error=requests.Timeout("timeout")),
    Sesion(Respuesta(status_code=503)),
    Sesion(Respuesta(error=ValueError("no es JSON"))),
    Sesion(Respuesta(datos={"message": "API rate limit exceeded"})),
])
def test_sin_conexion_o_respuesta_rara(sesion):
    with pytest.raises(actualizacion.ErrorRed):
        actualizacion.buscar(sesion, actual="0.1.0")
