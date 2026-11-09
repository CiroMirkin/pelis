"""Las reglas de Progreso, Vista y arranque mientras se reproduce, sin Qt para que se testeen sin el reproductor."""

from . import db

PROGRESO_MINIMO_MS = 3 * 60 * 1000  # para que abrir una peli y mirar el arranque no la deje empezada


def _progreso_a_guardar(ms):
    return ms if ms >= PROGRESO_MINIMO_MS else 0


RETROCESO_AL_RETOMAR_MS = 15 * 1000  # para recuperar el hilo de la escena


def _posicion_de_retomar(progreso_ms):
    """El retroceso es solo al arrancar y el progreso guardado no cambia."""
    return max(0, progreso_ms - RETROCESO_AL_RETOMAR_MS)


ANTICIPO_DE_VISITA_MS = 5 * 1000  # para ver un poco de contexto antes del cuadro de la captura


class Sesion:
    """Cada aviso devuelve "empezada", "vista" o None para que quien llama reaccione sin conocer las reglas."""

    def __init__(self, conn, pelicula_id, visita_ms=None):
        """Con `visita_ms` es una Visita y no toca el Progreso ni la Vista."""
        self.conn = conn
        self.pelicula_id = pelicula_id
        self.visita_ms = visita_ms
        # Al terminar ya se guardó progreso 0 entonces salir no debe pisarlo con la posición del final
        self._terminada = False
        # QtMultimedia avisa pausas antes de cargar.
        # Después de salir con Esc, el cierre de la ventana vuelve a avisar la salida.
        self._abierta = False
        self._salio = False

    def _activa(self):
        return self._abierta and not self._salio

    def cargo(self, duracion_ms):
        """Devuelve None desde la segunda carga porque QtMultimedia vuelve a avisar al cambiar de pista."""
        if self._abierta:
            return None
        self._abierta = True
        if duracion_ms > 0:
            db.guardar_duracion(self.conn, self.pelicula_id, duracion_ms)
        if self.visita_ms is not None:
            desde = max(0, self.visita_ms - ANTICIPO_DE_VISITA_MS)
            # Acotado antes del final para que se llegue a ver algo
            return min(desde, max(0, duracion_ms - ANTICIPO_DE_VISITA_MS)) if duracion_ms > 0 else desde
        return _posicion_de_retomar(db.pelicula(self.conn, self.pelicula_id)["progreso_ms"] or 0)

    def pauso(self, posicion_ms):
        return self._guardar(posicion_ms)

    def reanudo(self):
        """Si había llegado al final y vuelve a reproducir entonces salir guarda de nuevo."""
        self._terminada = False

    def termino(self):
        """El progreso vuelve a 0 para que la próxima vez arranque del principio."""
        if not self._activa():
            return None
        self._terminada = True
        if self.visita_ms is not None:
            return None
        db.guardar_progreso(self.conn, self.pelicula_id, 0)
        db.marcar_vista(self.conn, self.pelicula_id, True)
        return "vista"

    def salio(self, posicion_ms):
        resultado = self._guardar(posicion_ms)
        self._salio = True
        return resultado

    def _guardar(self, posicion_ms):
        if not self._activa() or self._terminada or self.visita_ms is not None:
            return None
        ms = _progreso_a_guardar(posicion_ms)
        db.guardar_progreso(self.conn, self.pelicula_id, ms)
        return "empezada" if ms > 0 else None
