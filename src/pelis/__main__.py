"""Arranque: python -m pelis [--app-dir <carpeta app>]"""

import argparse
import os
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from . import actualizacion, config as configuracion
from .puente import Puente


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

    puente = Puente(config, prerelease=args.prerelease)
    engine = QQmlApplicationEngine()
    avisos = []
    engine.warnings.connect(lambda ws: avisos.extend(w.toString() for w in ws))
    engine.rootContext().setContextProperty("puente", puente)
    engine.load(Path(__file__).parent / "qml" / "Main.qml")
    if not engine.rootObjects():
        fallar("No se pudo cargar la interfaz:\n" + "\n".join(avisos))
    if actualizacion.en_build():
        # Arrancó bien: si venía de actualizar, ya no hace falta la versión anterior
        actualizacion.terminar(actualizacion.instalacion_actual())
    codigo = app.exec()
    del engine  # antes que el puente, para que QML no lo lea ya destruido al cerrar
    puente.cerrar()
    sys.exit(codigo)


if __name__ == "__main__":
    main()
