"""Prototipo descartable de la fase 0: reproductor QML + QtMultimedia con overlay propio de subtítulos.

Uso:
    python prototipo/main.py [video] [--autotest]

Sin video, toma el primero de ../Peliculas. Con --autotest recorre los puntos del
criterio de terminado solo (sin sonido), los escribe en la consola y se cierra.
"""

import bisect
import sys
from pathlib import Path

import pysubs2
from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtMultimedia import QVideoSink
from PySide6.QtQml import QQmlApplicationEngine

RAIZ = Path(__file__).resolve().parent.parent
VIDEOS = {".mkv", ".mp4", ".avi", ".m4v", ".mov", ".wmv", ".ts", ".webm"}
SUBS = {".srt", ".ass", ".vtt"}


def leer_subtitulo(ruta):
    """Devuelve (eventos, codificación). Prueba UTF-8 (con o sin BOM) y si falla cp1252."""
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            archivo = pysubs2.load(str(ruta), encoding=codificacion)
        except UnicodeDecodeError:
            continue
        eventos = [(e.start, e.end, e.plaintext) for e in archivo if not e.is_comment and e.plaintext.strip()]
        eventos.sort()
        return eventos, codificacion
    raise ValueError(f"no se pudo decodificar {ruta}")


class Backend(QObject):
    externosChanged = Signal()
    textoEmbebidoChanged = Signal()
    eventosChanged = Signal()

    def __init__(self, video, autotest):
        super().__init__()
        self._video = Path(video)
        self._autotest = autotest
        self._externos = sorted(p for p in self._video.parent.iterdir() if p.suffix.lower() in SUBS)
        self._eventos = []
        self._inicios = []
        self._codificacion = ""
        self._texto_embebido = ""
        self._salida = None
        # El MediaPlayer escribe en este sink; cada frame se reenvía al sink del VideoOutput
        # sin el texto de subtítulo, para que Qt no lo dibuje y lo dibuje solo nuestro overlay.
        self._entrada = QVideoSink(self)
        self._entrada.videoFrameChanged.connect(self._reenviar)
        self._entrada.subtitleTextChanged.connect(self._embebido)

    def _reenviar(self, frame):
        if self._salida is not None:
            frame.setSubtitleText("")
            self._salida.setVideoFrame(frame)

    def _embebido(self, texto):
        self._texto_embebido = texto
        self.textoEmbebidoChanged.emit()

    @Property(QObject, constant=True)
    def entrada(self):
        return self._entrada

    @Slot(QObject)
    def setSalida(self, sink):
        self._salida = sink

    @Property(QUrl, constant=True)
    def videoUrl(self):
        return QUrl.fromLocalFile(str(self._video))

    @Property(str, constant=True)
    def titulo(self):
        return self._video.parent.name

    @Property(bool, constant=True)
    def autotest(self):
        return self._autotest

    @Property("QStringList", notify=externosChanged)
    def externos(self):
        return [p.name for p in self._externos]

    @Property(int, constant=True)
    def externoMismoNombre(self):
        for i, p in enumerate(self._externos):
            if p.stem == self._video.stem:
                return i
        return -1

    @Property(str, notify=textoEmbebidoChanged)
    def textoEmbebido(self):
        return self._texto_embebido

    @Property(str, notify=eventosChanged)
    def codificacion(self):
        return self._codificacion

    @Property(int, notify=eventosChanged)
    def cantidadEventos(self):
        return len(self._eventos)

    @Slot(int)
    def cargarExterno(self, indice):
        if indice < 0:
            self._eventos, self._codificacion = [], ""
        else:
            self._eventos, self._codificacion = leer_subtitulo(self._externos[indice])
        self._inicios = [e[0] for e in self._eventos]
        self.eventosChanged.emit()

    @Slot(int, result=str)
    def textoEn(self, ms):
        i = bisect.bisect_right(self._inicios, ms)
        lineas = [t for s, e, t in self._eventos[max(0, i - 5):i] if e > ms]
        return "\n".join(lineas)

    @Slot(int, result=int)
    def eventoDesde(self, ms):
        """Inicio del primer evento externo a partir de ms (-1 si no hay), para el autotest."""
        i = bisect.bisect_left(self._inicios, ms)
        return self._inicios[i] if i < len(self._inicios) else -1


def primer_video():
    for carpeta in sorted((RAIZ / "Peliculas").iterdir()):
        if carpeta.is_dir():
            for p in sorted(carpeta.iterdir()):
                if p.suffix.lower() in VIDEOS:
                    return p
    sys.exit("No hay videos en Peliculas/")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    autotest = "--autotest" in sys.argv
    video = Path(args[0]) if args else primer_video()

    app = QGuiApplication(sys.argv)
    backend = Backend(video, autotest)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(Path(__file__).with_name("Reproductor.qml"))
    if not engine.rootObjects():
        sys.exit(1)
    codigo = app.exec()
    del engine  # antes que backend, para que QML no lo lea ya destruido al cerrar
    sys.exit(codigo)


if __name__ == "__main__":
    main()
