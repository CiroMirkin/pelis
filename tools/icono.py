"""Genera assets/icono.ico, src/pelis/icono.png (el que carga la app y se empaqueta) y una vista previa a partir de assets/icono.svg con QtSvg."""
import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

RAIZ = Path(__file__).resolve().parent.parent
TAMANOS_ICO = (16, 24, 32, 48, 64, 128, 256)


def dibujar(render, lado):
    imagen = QImage(lado, lado, QImage.Format_ARGB32)
    imagen.fill(Qt.transparent)
    pintor = QPainter(imagen)
    pintor.setRenderHint(QPainter.Antialiasing)
    render.render(pintor)
    pintor.end()
    return imagen


def png_bytes(imagen):
    datos = QByteArray()
    buffer = QBuffer(datos)
    buffer.open(QIODevice.WriteOnly)
    imagen.save(buffer, "PNG")
    return bytes(datos)


def escribir_ico(destino, pngs):
    """Un .ico con cada tamaño como PNG adentro porque eso aceptan Windows y Inno Setup."""
    cabecera = struct.pack("<HHH", 0, 1, len(pngs))
    offset = 6 + 16 * len(pngs)
    entradas, cuerpo = b"", b""
    for lado, datos in pngs:
        entradas += struct.pack("<BBBBHHII", lado % 256, lado % 256, 0, 0, 1, 32, len(datos), offset)
        cuerpo += datos
        offset += len(datos)
    destino.write_bytes(cabecera + entradas + cuerpo)


def vista_previa(render, destino):
    """Los tamaños reales lado a lado para ver cómo se lee de verdad."""
    lados = (16, 32, 64, 256)
    ancho = sum(lados) + 24 * (len(lados) + 1)
    hoja = QImage(ancho, 256 + 48, QImage.Format_ARGB32)
    hoja.fill(0xFF2B2833)
    pintor = QPainter(hoja)
    x = 24
    for lado in lados:
        pintor.drawImage(x, 24, dibujar(render, lado))
        x += lado + 24
    pintor.end()
    hoja.save(str(destino))


def main():
    QGuiApplication(sys.argv)
    render = QSvgRenderer(str(RAIZ / "assets" / "icono.svg"))
    pngs = [(lado, png_bytes(dibujar(render, lado))) for lado in TAMANOS_ICO]
    escribir_ico(RAIZ / "assets" / "icono.ico", pngs)
    (RAIZ / "src" / "pelis" / "icono.png").write_bytes(pngs[-1][1])
    if len(sys.argv) > 1:
        vista_previa(render, Path(sys.argv[1]))


if __name__ == "__main__":
    main()
