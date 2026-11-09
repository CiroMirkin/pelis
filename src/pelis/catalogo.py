"""Reglas del catálogo, sin Qt: épocas, tarjetas, incompletas y la recomendada."""

ULTIMA_DECADA = 2000  # las posteriores no se agrupan
ANIOS_SUELTOS = 4  # los últimos años, incluido el actual, se filtran de a uno

PROGRESO_MINIMO_MS = 3 * 60 * 1000  # antes de esto, salir no la deja empezada


def progreso_a_guardar(ms):
    return ms if ms >= PROGRESO_MINIMO_MS else 0


RETROCESO_AL_RETOMAR_MS = 15 * 1000  # para recuperar el hilo de la escena


def posicion_de_retomar(progreso_ms):
    """Dónde arranca el reproductor al seguir una película empezada. El progreso guardado no cambia."""
    return max(0, progreso_ms - RETROCESO_AL_RETOMAR_MS)


CLAVES_TARJETA = ("peliculaId", "titulo", "anio", "poster", "progreso", "vista")


def periodos(anios, anio_actual):
    """Opciones del filtro de época para los años presentes: [(clave, etiqueta)].

    Las décadas hasta ULTIMA_DECADA van agrupadas ("Los 60s", "Los 2000"); de los últimos
    ANIOS_SUELTOS años, cada uno va aparte. Los años intermedios no tienen opción propia.
    """
    decadas = sorted({a // 10 * 10 for a in anios if a and a // 10 * 10 <= ULTIMA_DECADA})
    sueltos = sorted({a for a in anios if a and anio_actual - ANIOS_SUELTOS < a <= anio_actual})
    return ([(f"{d}s", f"Los {d % 100}s" if 1910 <= d < 2000 else f"Los {d}") for d in decadas]
            + [(str(a), str(a)) for a in sueltos])


def en_periodo(anio, clave):
    if not clave:
        return True
    if not anio:
        return False
    if clave.endswith("s"):
        return anio // 10 * 10 == int(clave[:-1])
    return anio == int(clave)


def url_poster(biblioteca, relativa):
    """URL del poster con la fecha del archivo: si se reemplaza (mismo nombre), Qt no muestra el viejo de caché."""
    if not relativa:
        return ""
    ruta = (biblioteca / relativa).absolute()
    try:
        return f"{ruta.as_uri()}?v={ruta.stat().st_mtime_ns}"
    except OSError:
        return ruta.as_uri()


def es_incompleta(fila, biblioteca):
    """Sin datos de IMDb o sin un poster que exista en el disco."""
    return (fila["omdb_estado"] != "encontrada"
            or not fila["poster"] or not (biblioteca / fila["poster"]).is_file())


def tarjeta(fila, biblioteca):
    """Una película como se muestra en una grilla (catálogo o filmografía)."""
    return {
        "peliculaId": fila["id"],
        "titulo": fila["titulo"],
        "anio": fila["year"] or 0,
        "poster": url_poster(biblioteca, fila["poster"]),
        "progreso": fila["progreso_ms"] / fila["duracion_ms"] if fila["duracion_ms"] and fila["progreso_ms"] else 0.0,
        "vista": bool(fila["watched"]),
    }


def filmografia(filas, biblioteca):
    """Películas de una persona: la tarjeta más sus roles ('actor', 'director')."""
    return [{**tarjeta(f, biblioteca), "roles": sorted(set(f["roles"].split(",")))} for f in filas]


class Recomendacion:
    """La película que se ofrece a pedido, una por apertura. Cada método devuelve si `datos` cambió."""

    def __init__(self):
        self.datos = {}
        self.usada = False  # ya se pidió en esta apertura; cerrar la franja no la devuelve

    def elegir(self, fila, biblioteca):
        """Se elige una vez por apertura; sin `fila` (sin candidatas) no se gasta."""
        if self.usada or fila is None:
            return False
        self.usada = True
        self.datos = {
            "id": fila["id"],
            "titulo": fila["titulo"],
            "anio": fila["year"] or 0,
            "genero": fila["genero"] or "",
            "duracion": fila["duracion_ms"] or 0,
            "poster": url_poster(biblioteca, fila["poster"]),
        }
        return True

    def cerrar(self):
        if not self.datos:
            return False
        self.datos = {}
        return True

    def empezo(self, pelicula_id):
        # Una vez empezada o vista, la recomendación ya cumplió
        return self.datos.get("id") == pelicula_id and self.cerrar()

    def poster(self, url):
        if not self.datos or url == self.datos["poster"]:
            return False
        self.datos = {**self.datos, "poster": url}
        return True

    def duracion(self, pelicula_id, ms):
        if self.datos.get("id") != pelicula_id or ms == self.datos["duracion"]:
            return False
        self.datos = {**self.datos, "duracion": ms}
        return True
