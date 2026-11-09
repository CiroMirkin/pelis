"""La sesión de reproducción de una película, sin Qt: qué pasa con el Progreso y la Vista."""

from . import db

PROGRESO_MINIMO_MS = 3 * 60 * 1000  # antes de esto, salir no la deja empezada


def progreso_a_guardar(ms):
    return ms if ms >= PROGRESO_MINIMO_MS else 0


RETROCESO_AL_RETOMAR_MS = 15 * 1000  # para recuperar el hilo de la escena


def posicion_de_retomar(progreso_ms):
    """Dónde arranca el reproductor al seguir una película empezada. El progreso guardado no cambia."""
    return max(0, progreso_ms - RETROCESO_AL_RETOMAR_MS)


ANTICIPO_DE_VISITA_MS = 5 * 1000  # una Visita arranca un poco antes de la posición pedida


class Sesion:
    def __init__(self, conn, pelicula_id, visita_ms=None):
        """Con `visita_ms` es una Visita: arranca ahí y no toca el Progreso ni la Vista."""
        self.conn = conn
        self.pelicula_id = pelicula_id
        self.visita_ms = visita_ms
        # Al terminar ya se guardó progreso 0; salir no debe guardar la posición del final
        self._terminada = False
        # QtMultimedia avisa pausas antes de cargar; tras salir, el cierre de la ventana vuelve a avisar
        self._abierta = False
        self._salio = False

    def _activa(self):
        return self._abierta and not self._salio

    def cargo(self, duracion_ms):
        """El video cargó: devuelve la posición de arranque en ms, o None si ya había cargado."""
        if self._abierta:
            return None
        self._abierta = True
        if duracion_ms > 0:
            db.guardar_duracion(self.conn, self.pelicula_id, duracion_ms)
        if self.visita_ms is not None:
            desde = max(0, self.visita_ms - ANTICIPO_DE_VISITA_MS)
            # Acotado antes del final, para que se llegue a ver algo
            return min(desde, max(0, duracion_ms - ANTICIPO_DE_VISITA_MS)) if duracion_ms > 0 else desde
        return posicion_de_retomar(db.pelicula(self.conn, self.pelicula_id)["progreso_ms"] or 0)

    def pauso(self, posicion_ms):
        return self._guardar(posicion_ms)

    def reanudo(self):
        """Volvió a reproducir: si había llegado al final, salir vuelve a guardar."""
        self._terminada = False

    def termino(self):
        """Llegó al final: queda vista y la próxima vez arranca del principio."""
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
        ms = progreso_a_guardar(posicion_ms)
        db.guardar_progreso(self.conn, self.pelicula_id, ms)
        return "empezada" if ms > 0 else None
