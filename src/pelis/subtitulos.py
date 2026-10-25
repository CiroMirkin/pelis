"""Subtítulos externos y elección automática de pistas de audio y subtítulos."""

import bisect
from pathlib import Path

import pysubs2

from .nombres import idioma_de

EXTENSIONES = {".srt", ".ass", ".vtt"}


def externos(video):
    """Subtítulos al mismo nivel que el video (nunca en subcarpetas)."""
    video = Path(video)
    return sorted(p for p in video.parent.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONES)


def leer(ruta):
    """Devuelve (eventos, codificación); eventos = [(inicio_ms, fin_ms, texto)] ordenados.

    Prueba UTF-8 (con o sin BOM) y si falla cp1252.
    """
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            archivo = pysubs2.load(str(ruta), encoding=codificacion)
        except UnicodeDecodeError:
            continue
        eventos = sorted((e.start, e.end, e.plaintext) for e in archivo if not e.is_comment and e.plaintext.strip())
        return eventos, codificacion
    raise ValueError(f"No se pudo decodificar {ruta}")


class Linea:
    """Busca el texto visible en un instante dentro de una lista de eventos."""

    def __init__(self, eventos):
        self.eventos = eventos
        self.inicios = [e[0] for e in eventos]

    def texto_en(self, ms):
        i = bisect.bisect_right(self.inicios, ms)
        return "\n".join(t for s, e, t in self.eventos[max(0, i - 5):i] if e > ms)


def _idioma_pista(pista, preferido):
    return idioma_de(pista.get("idioma"), preferido) or idioma_de(pista.get("titulo"), preferido)


def elegir_subtitulo(video, nombres_externos, pistas_embebidas, preferido):
    """Elige el subtítulo a activar al abrir una película.

    pistas_embebidas: [{"idioma": ..., "titulo": ...}]
    Devuelve ("externo", i), ("embebido", i) o None.
    """
    stem = Path(video).stem.lower()
    for i, nombre in enumerate(nombres_externos):
        if Path(nombre).stem.lower() == stem:
            return "externo", i
    for i, nombre in enumerate(nombres_externos):
        if idioma_de(Path(nombre).stem, preferido):
            return "externo", i
    for i, pista in enumerate(pistas_embebidas):
        if _idioma_pista(pista, preferido):
            return "embebido", i
    if len(nombres_externos) == 1:
        return "externo", 0
    return None


def elegir_audio(pistas, preferido):
    """Índice de la pista de audio en el idioma preferido (metadatos y después título), o -1."""
    for i, pista in enumerate(pistas):
        if idioma_de(pista.get("idioma"), preferido):
            return i
    for i, pista in enumerate(pistas):
        if idioma_de(pista.get("titulo"), preferido):
            return i
    return -1
