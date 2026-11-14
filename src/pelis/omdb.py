"""Cliente de OMDb (http://www.omdbapi.com)."""

import requests

URL = "https://www.omdbapi.com/"
TIMEOUT = 15


class ErrorRed(Exception):
    """No se pudo consultar OMDb (sin conexión, timeout, clave inválida, límite diario...)."""


class Omdb:
    def __init__(self, api_key):
        self.api_key = api_key
        self.sesion = requests.Session()

    def _consultar(self, **params):
        try:
            r = self.sesion.get(URL, params={"apikey": self.api_key, "plot": "full", **params}, timeout=TIMEOUT)
            datos = r.json()
        except (requests.RequestException, ValueError) as e:
            raise ErrorRed(str(e)) from e
        if datos.get("Response") == "True":
            return datos
        error = datos.get("Error", "")
        # "Movie not found!" / "Incorrect IMDb ID." son "no está"; el resto (clave, límite) es un error
        if "not found" in error.lower() or "incorrect imdb id" in error.lower():
            return None
        raise ErrorRed(error or f"HTTP {r.status_code}")

    def clave_valida(self):
        """Lanza ErrorRed si no se pudo saber (sin red, límite diario...)."""
        try:
            # tt0111161 es Sueños de libertad y solo es un ID real cualquiera para que la consulta sea válida
            datos = self.sesion.get(URL, params={"apikey": self.api_key, "i": "tt0111161"}, timeout=TIMEOUT).json()
        except (requests.RequestException, ValueError) as e:
            raise ErrorRed(str(e)) from e
        if datos.get("Response") == "True":
            return True
        # OMDb responde HTTP 401 con "Invalid API key!" y lo único estable para distinguirlo del límite diario es el texto
        if "api key" in datos.get("Error", "").lower():
            return False
        raise ErrorRed(datos.get("Error", "respuesta inesperada"))

    def por_id(self, imdb_id):
        try:
            return self._consultar(i=imdb_id)
        except ErrorRed as e:
            # Así responde OMDb a un ID bien formado que no tiene (uno mal formado es "Incorrect IMDb ID.")
            if str(e) == "Error getting data.":
                return None
            raise

    def por_titulo(self, titulo, year=None):
        params = {"t": titulo, "type": "movie"}
        if year:
            params["y"] = str(year)
        return self._consultar(**params)

    def buscar(self, titulo, year=None):
        """Candidatos de OMDb (?s=) para elegir a mano: lista de respuestas cortas, vacía si no hay."""
        params = {"s": titulo, "type": "movie"}
        if year:
            params["y"] = str(year)
        try:
            datos = self._consultar(**params)
        except ErrorRed as e:
            if "too many" in str(e).lower():
                raise ErrorRed("Hay demasiados resultados; agregá el año o más palabras del título.") from e
            raise
        return (datos or {}).get("Search") or []

    def bajar_poster(self, url, destino):
        try:
            r = self.sesion.get(url, timeout=TIMEOUT)
            r.raise_for_status()
        except requests.RequestException as e:
            raise ErrorRed(str(e)) from e
        destino.write_bytes(r.content)
