"""Mantener la pantalla encendida mientras se reproduce: sin esto el sistema la bloquea por
inactividad en medio de la película."""

import logging
import sys

log = logging.getLogger(__name__)

_CONEXION = "pelis-pantalla"


class Pantalla:
    def __init__(self):
        self._activa = False

    def mantener(self, activa):
        if activa == self._activa:
            return
        try:
            if sys.platform == "win32":
                _windows(activa)
            elif sys.platform.startswith("linux"):
                _linux(activa)
        except Exception:
            log.exception("No se pudo %s el bloqueo de pantalla", "evitar" if activa else "devolver")
            return
        self._activa = activa


def _windows(activa):
    import ctypes

    ES_CONTINUOUS, ES_SYSTEM_REQUIRED, ES_DISPLAY_REQUIRED = 0x80000000, 0x1, 0x2
    flags = ES_CONTINUOUS | (ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED if activa else 0)
    ctypes.windll.kernel32.SetThreadExecutionState(flags)


def _linux(activa):
    from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage

    if not activa:
        # El servicio suelta el permiso cuando se va quien lo pidió. Cerrar la conexión propia
        # evita UnInhibit, que exige un uint32 que PySide6 no sabe mandar.
        QDBusConnection.disconnectFromBus(_CONEXION)
        return
    bus = QDBusConnection.connectToBus(QDBusConnection.SessionBus, _CONEXION)
    servicio = QDBusInterface("org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver",
                              "org.freedesktop.ScreenSaver", bus)
    respuesta = servicio.call("Inhibit", "Pelis", "Reproduciendo una película")
    if respuesta.type() == QDBusMessage.ErrorMessage:
        QDBusConnection.disconnectFromBus(_CONEXION)
        raise RuntimeError(respuesta.errorMessage())
