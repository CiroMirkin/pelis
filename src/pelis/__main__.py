"""Arranque: python -m pelis [--app-dir <carpeta app>]"""

import argparse
import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QTimer, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from . import config as configuracion


def fallar(mensaje):
    """Sin consola (build de PyInstaller) el mensaje va a pelis-error.log y a un cuadro de diálogo."""
    if getattr(sys, "frozen", False):
        log = Path(sys.executable).resolve().parent.parent / "pelis-error.log"
        try:
            log.write_text(mensaje + "\n", encoding="utf-8")
        except OSError:
            pass
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, mensaje, "Pelis", 0x10)
    sys.exit(mensaje)


class Arranque(QObject):
    """Abre la ventana con el spinner y, ya pintada, carga el resto."""

    def __init__(self, config, prerelease):
        super().__init__()
        self.config = config
        self.prerelease = prerelease
        self.puente = None
        self._empezado = False
        self.avisos = []
        self.engine = QQmlApplicationEngine()
        self.engine.warnings.connect(lambda ws: self.avisos.extend(w.toString() for w in ws))
        self.engine.load(Path(__file__).parent / "qml" / "Main.qml")
        if not self.engine.rootObjects():
            fallar("No se pudo cargar la interfaz:\n" + "\n".join(self.avisos))
        self.ventana = self.engine.rootObjects()[0]
        # frameSwapped viene del hilo de render. Una ventana minimizada no lo emite: de ahí el timer.
        self.ventana.frameSwapped.connect(self.seguir, Qt.QueuedConnection)
        QTimer.singleShot(1000, self.seguir)

    @Slot()
    def seguir(self):
        if self._empezado:
            return
        self._empezado = True
        self.ventana.frameSwapped.disconnect(self.seguir)
        try:
            # Importan QtMultimedia y requests, que son gran parte de la espera: van después de la ventana
            from . import actualizacion
            from .puente import Puente

            self.puente = Puente(self.config, prerelease=self.prerelease)
            self.engine.rootContext().setContextProperty("puente", self.puente)
            self.ventana.setProperty("listo", True)
            if not self.ventana.findChild(QObject, "pila").property("depth"):
                fallar("No se pudo cargar la interfaz:\n" + "\n".join(self.avisos))
            if actualizacion.en_build():
                # Arrancó bien: si venía de actualizar, ya no hace falta la versión anterior
                actualizacion.terminar(actualizacion.instalacion_actual())
        except Exception as e:
            fallar(f"No se pudo iniciar Pelis:\n{e}")

    def cerrar(self):
        del self.ventana, self.engine  # antes que el puente, para que QML no lo lea ya destruido al cerrar
        if self.puente:
            self.puente.cerrar()


def main():
    parser = argparse.ArgumentParser(prog="pelis")
    parser.add_argument("--app-dir", help="carpeta con pelis.toml y pelis.db")
    parser.add_argument("--prerelease", action="store_true", help="ofrecer también versiones de prueba (RC)")
    args = parser.parse_args()

    try:
        app_dir = Path(args.app_dir) if args.app_dir else configuracion.app_dir_por_defecto()
        config = configuracion.cargar(app_dir)
    except configuracion.ErrorConfig as e:
        fallar(f"Error de configuración: {e}")
    if not config.biblioteca.is_dir():
        fallar(f"No existe la biblioteca: {config.biblioteca}")

    os.environ.setdefault("QT_QUICK_CONTROLS_MATERIAL_THEME", "Dark")
    if sys.platform.startswith("linux"):
        # Con GLX (el default en X11) los frames de VAAPI se copian a RAM antes de ir a la GPU;
        # con EGL se muestran sin copia y el video va fluido en máquinas modestas.
        os.environ.setdefault("QT_XCB_GL_INTEGRATION", "xcb_egl")
    QQuickStyle.setStyle("Material")
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Pelis")

    arranque = Arranque(config, args.prerelease)
    codigo = app.exec()
    arranque.cerrar()
    sys.exit(codigo)


if __name__ == "__main__":
    main()
