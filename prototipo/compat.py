"""Script de compatibilidad de la fase 0: intenta abrir cada video de la biblioteca con QtMultimedia.

Uso:
    python prototipo/compat.py [biblioteca]      (por defecto ../Peliculas)

Para cada video informa si cargó, duración, si tiene video, pistas de audio y de
subtítulos (con idioma/título) y el error si falló. Al final resume los que fallaron.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QEventLoop, QLocale, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtMultimedia import QMediaMetaData, QMediaPlayer

VIDEOS = {".mkv", ".mp4", ".avi", ".m4v", ".mov", ".wmv", ".ts", ".webm"}
TIMEOUT_MS = 20000


def describir_pista(md):
    partes = []
    titulo = md.stringValue(QMediaMetaData.Key.Title)
    if titulo:
        partes.append(titulo)
    idioma = md.value(QMediaMetaData.Key.Language)
    if idioma is not None and idioma != QLocale.Language.AnyLanguage:
        partes.append(QLocale.languageToCode(idioma))
    return " · ".join(partes) or "?"


def probar(player, video):
    loop = QEventLoop()
    errores = []

    def estado(s):
        if s in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.InvalidMedia):
            loop.quit()

    def error(_codigo, texto):
        errores.append(texto)
        loop.quit()

    player.mediaStatusChanged.connect(estado)
    player.errorOccurred.connect(error)
    QTimer.singleShot(TIMEOUT_MS, loop.quit)
    player.setSource(QUrl.fromLocalFile(str(video)))
    loop.exec()
    player.mediaStatusChanged.disconnect(estado)
    player.errorOccurred.disconnect(error)

    ok = player.mediaStatus() == QMediaPlayer.MediaStatus.LoadedMedia and not errores
    resultado = {
        "ok": ok,
        "error": "; ".join(errores) or ("" if ok else f"estado {player.mediaStatus().name}"),
        "duracion_s": player.duration() // 1000,
        "video": player.hasVideo(),
        "audio": [describir_pista(md) for md in player.audioTracks()],
        "subs": [describir_pista(md) for md in player.subtitleTracks()],
    }
    player.setSource(QUrl())
    return resultado


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    biblioteca = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "Peliculas"
    videos = sorted(p for p in biblioteca.rglob("*") if p.is_file() and p.suffix.lower() in VIDEOS)
    if not videos:
        sys.exit(f"No hay videos en {biblioteca}")

    app = QGuiApplication(sys.argv)
    player = QMediaPlayer()
    fallidos = []
    for video in videos:
        r = probar(player, video)
        nombre = video.relative_to(biblioteca)
        if r["ok"]:
            m, s = divmod(r["duracion_s"], 60)
            print(f"OK    {nombre}")
            print(f"      {m}:{s:02d} · video={r['video']} · audio={r['audio']} · subs={r['subs']}")
        else:
            print(f"FALLA {nombre}\n      {r['error']}")
            fallidos.append(nombre)

    print(f"\n{len(videos) - len(fallidos)}/{len(videos)} se abren correctamente")
    for nombre in fallidos:
        print(f"  falla: {nombre}")
    del app


if __name__ == "__main__":
    main()
