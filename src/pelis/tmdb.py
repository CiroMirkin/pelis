"""Cliente de TMDb (https://www.themoviedb.org), solo para la sinopsis en español."""

import requests

from .omdb import ErrorRed

URL = "https://api.themoviedb.org/3/find/{imdb_id}"
URL_CONFIGURACION = "https://api.themoviedb.org/3/configuration"
TIMEOUT = 15


class Tmdb:
    def __init__(self, api_key):
        self.api_key = api_key
        self.sesion = requests.Session()

    def sinopsis(self, imdb_id, idiomas):
        """Primera sinopsis no vacía en el orden de `idiomas` (ej. ["es-MX", "es-ES"]).

        Devuelve (texto, idioma) o (None, None) si TMDb no la tiene en ninguno.
        """
        for idioma in idiomas:
            try:
                r = self.sesion.get(
                    URL.format(imdb_id=imdb_id),
                    params={"api_key": self.api_key, "external_source": "imdb_id", "language": idioma},
                    timeout=TIMEOUT,
                )
                r.raise_for_status()
                resultados = r.json().get("movie_results") or []
            except (requests.RequestException, ValueError) as e:
                raise ErrorRed(str(e)) from e
            texto = (resultados[0].get("overview") or "").strip() if resultados else ""
            if texto:
                return texto, idioma
        return None, None

    def clave_valida(self):
        """Lanza ErrorRed si no se pudo saber (sin red, error del servidor...)."""
        try:
            r = self.sesion.get(URL_CONFIGURACION, params={"api_key": self.api_key}, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise ErrorRed(str(e)) from e
        if r.status_code == 200:
            return True
        if r.status_code == 401:
            return False
        raise ErrorRed(f"HTTP {r.status_code}")
