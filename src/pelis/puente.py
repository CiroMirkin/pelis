"""Puente entre la lógica en Python y la UI en QML."""

import logging
import os
import random
import sqlite3
import sys
import threading
from dataclasses import asdict
from datetime import date
from pathlib import Path

from PySide6.QtCore import (
    Property, QAbstractListModel, QBuffer, QCoreApplication, QModelIndex, QObject, QSettings, QThread, QTimer, Qt,
    QUrl, Signal, Slot,
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtMultimedia import QMediaPlayer

from . import __version__, actualizacion, capturas, db, edicion, instalador, metadatos, pantalla, poster, subtitulos
from .catalogo import (
    CLAVES_TARJETA, Recomendacion, en_periodo, es_incompleta, filmografia, periodos, tarjeta,
    url_poster,
)
from . import nombres
from .nombres import idioma_de, normalizar
from .reproduccion import Sesion
from .escaneo import escanear, importar_sin_red
from .claves import GestorClaves
from .discos import Discos, Fuente, id_global, separar, volumenes_montados
from .config import texto_de_biblioteca
from .omdb import ErrorRed, Omdb
from .tmdb import Tmdb

log = logging.getLogger(__name__)

SOLO_LECTURA = "Este disco está en solo lectura: no se puede cambiar nada de sus películas."


class ModeloCatalogo(QAbstractListModel):
    ROLES = {Qt.UserRole + 1 + i: clave.encode() for i, clave in enumerate(CLAVES_TARJETA)}

    periodosChanged = Signal()
    periodoChanged = Signal()
    vistasChanged = Signal()
    incompletasChanged = Signal()

    def __init__(self, parent=None, anio_actual=None):
        super().__init__(parent)
        self._todas = []
        self._filas = []
        self._palabras = []
        self._vistas = "todas"  # "todas", "vistas" o "noVistas"
        self._anio_actual = anio_actual  # None = el de hoy
        self._periodo = ""  # "" = todos, "1960s" = una década, "2025" = un año
        self._periodos = []
        self._solo_incompletas = False

    def recargar(self, filas, biblioteca, discos=()):
        self._todas = self._tarjetas(filas, biblioteca, 0, "")
        if discos:
            for filas_disco, biblioteca_disco, indice, etiqueta in discos:
                self._todas += self._tarjetas(filas_disco, biblioteca_disco, indice, etiqueta)
            # Cada db viene ordenada por separado entonces se ordena de nuevo como lo hace db.catalogo
            self._todas.sort(key=lambda t: (t["vista"], not (t["progreso"] > 0 and not t["vista"]),
                                            t["titulo"].casefold()))
        self.incompletasChanged.emit()
        # Solo las épocas presentes en la biblioteca, nunca vacías
        opciones = [{"clave": c, "etiqueta": e}
                    for c, e in periodos([f["anio"] for f in self._todas], self._anio_actual or date.today().year)]
        if opciones != self._periodos:
            self._periodos = opciones
            self.periodosChanged.emit()
        if self._periodo and self._periodo not in [o["clave"] for o in opciones]:
            self._periodo = ""
            self.periodoChanged.emit()
        self._aplicar()

    @staticmethod
    def _tarjetas(filas, biblioteca, indice, etiqueta):
        return [
            {
                **tarjeta({**dict(f), "id": id_global(indice, f["id"])}, biblioteca),
                "disco": etiqueta,
                "_busqueda": normalizar(f"{f['titulo']} | {f['personas'] or ''}"),
                "_incompleta": es_incompleta(f, biblioteca),
            }
            for f in filas
        ]

    @Property(list, notify=periodosChanged)
    def periodos(self):
        return self._periodos

    @Property(str, notify=periodoChanged)
    def periodo(self):
        return self._periodo

    @Property(str, notify=vistasChanged)
    def vistas(self):
        return self._vistas

    def _poner_vistas(self, cuales):
        if cuales != self._vistas:
            self._vistas = cuales
            self.vistasChanged.emit()

    @Slot(str)
    def filtrarPeriodo(self, clave):
        if clave != self._periodo:
            self._periodo = clave
            self.periodoChanged.emit()
            # Elegir otra época es pedir algo nuevo entonces se suelta el filtro de vistas
            if clave:
                self._poner_vistas("todas")
        self._aplicar()

    @Property(int, notify=incompletasChanged)
    def cantidadIncompletas(self):
        return sum(f["_incompleta"] for f in self._todas)

    @Property(bool, notify=incompletasChanged)
    def soloIncompletas(self):
        return self._solo_incompletas

    @Slot(bool)
    def filtrarIncompletas(self, solo):
        """Deja solo las películas sin datos o sin portada."""
        self._solo_incompletas = solo
        self.incompletasChanged.emit()
        self._aplicar()

    @Slot(str)
    def filtrar(self, texto):
        """Deja las películas cuyo título, director o reparto contienen todas las palabras de `texto`."""
        palabras = normalizar(texto).split()
        # Buscar otra cosa es pedir algo nuevo entonces se suelta el filtro de vistas para que no esconda el resultado.
        # Repetir la misma búsqueda (Enter, ↓, la espera de 300 ms) no lo toca.
        if palabras and palabras != self._palabras:
            self._poner_vistas("todas")
        self._palabras = palabras
        self._aplicar()

    @Slot(str)
    def filtrarVistas(self, cuales):
        self._poner_vistas(cuales if cuales in ("todas", "vistas", "noVistas") else "todas")
        self._aplicar()

    def _aplicar(self):
        vista = {"vistas": True, "noVistas": False}.get(self._vistas)
        self.beginResetModel()
        self._filas = [
            f for f in self._todas
            if (vista is None or f["vista"] == vista)
            and en_periodo(f["anio"], self._periodo)
            and (not self._solo_incompletas or f["_incompleta"])
            and all(p in f["_busqueda"] for p in self._palabras)
        ]
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._filas)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in self.ROLES:
            return None
        return self._filas[index.row()][self.ROLES[role].decode()]

    def roleNames(self):
        return self.ROLES


def _aviso_archivos(sin_escribir):
    if len(sin_escribir) <= 1:
        return "".join(aviso for _, aviso in sin_escribir)
    return (f"No se pudo escribir pelis.json en {len(sin_escribir)} carpetas, entre ellas «{sin_escribir[0][0]}». "
            "Los datos quedaron guardados y se reintenta en el próximo escaneo.")


class TrabajoEscaneo(QObject):
    progreso = Signal(int, int, str)
    terminado = Signal("QVariantMap")

    def __init__(self, config, sin_red=False):
        super().__init__()
        self.config = config
        self.sin_red = sin_red

    @Slot()
    def correr(self):
        try:
            conn = db.conectar(self.config.db_path)
            try:
                if self.sin_red:
                    informe = importar_sin_red(conn, self.config.biblioteca)
                    poster.rotar(conn, self.config.biblioteca)
                    self.terminado.emit({"sumadas": informe.agregadas + len(informe.reactivadas), "error": ""})
                    return
                omdb = Omdb(self.config.omdb_api_key) if self.config.omdb_api_key else None
                tmdb = Tmdb(self.config.tmdb_api_key) if self.config.tmdb_api_key else None
                informe = escanear(conn, self.config.biblioteca, omdb, self.progreso.emit,
                                   tmdb, self.config.idiomas_sinopsis)
            finally:
                conn.close()
        except Exception as e:  # el informe muestra el error en vez de dejar el diálogo colgado
            self.terminado.emit({"error": f"{type(e).__name__}: {e}"})
            return
        datos = asdict(informe)
        self.terminado.emit({
            "agregadas": datos["agregadas"],
            "noEncontradas": datos["no_encontradas"],
            "pendientes": datos["pendientes"],
            "faltantes": datos["faltantes"],
            "reactivadas": datos["reactivadas"],
            "reasignadas": [f"{v} → {n}" for v, n in datos["reasignadas"]],
            "problemas": [{"carpeta": c, "motivo": m} for c, m in datos["problemas"]],
            "desdeArchivo": datos["desde_archivo"],
            "archivosInvalidos": [{"carpeta": c, "motivo": m} for c, m in datos["archivos_invalidos"]],
            "sinClaveOmdb": not self.config.omdb_api_key,
            "aviso": "\n\n".join(a for a in (datos["aviso_omdb"], datos["aviso_tmdb"],
                                               _aviso_archivos(datos["archivos_sin_escribir"])) if a),
            "error": "",
        })


class Puente(QObject):
    escaneandoChanged = Signal()
    escaneoProgreso = Signal(int, int, str)
    escaneoTerminado = Signal("QVariantMap")
    importacionTerminada = Signal(int)
    recomendadaChanged = Signal()
    duracionMedida = Signal(int, int)
    externoChanged = Signal()
    volumenChanged = Signal()
    estiloSubsChanged = Signal()
    contadoresChanged = Signal()  # faltantes y sin ver
    consultandoImdbChanged = Signal()
    # Resultado de una consulta a IMDb: {error} | {candidatos} | {aplicado, aviso}
    imdbRespondio = Signal("QVariantMap")
    _imdbListo = Signal(object)  # desde el hilo de la consulta; se procesa en el de la UI
    bibliotecaChanged = Signal()
    validandoClavesChanged = Signal()
    clavesRespondio = Signal("QVariantMap")
    capturaGuardada = Signal(bool)  # True = escrita; False = falló y el motivo va al log
    buscandoActualizacionChanged = Signal()
    actualizacionRespondio = Signal("QVariantMap")
    _actualizacionLista = Signal(object)  # desde el hilo de la consulta
    actualizandoChanged = Signal()
    descargaProgreso = Signal(float)  # 0 a 1
    descargaTerminada = Signal(str)  # "" = lista para reiniciar; si no, el motivo para el usuario
    _descargaLista = Signal(object)  # desde el hilo de la descarga
    discosChanged = Signal()
    avisoDisco = Signal(str)
    discoSacado = Signal(str)  # la etiqueta del disco de la película en curso

    def __init__(self, config, prerelease=False, volumenes=volumenes_montados):
        super().__init__()
        self.config = config
        self._prerelease = prerelease  # --prerelease: también ofrece las RC
        self.conn = db.conectar(config.db_path)
        self._catalogo = ModeloCatalogo(self)
        # Preferencias de la app (no de la biblioteca): quedan junto a pelis.toml
        self._preferencias = QSettings(str(config.app_dir / "preferencias.ini"), QSettings.IniFormat)
        self._claves = GestorClaves(config, self._preferencias, self.conn, self)
        self._claves.validandoChanged.connect(self.validandoClavesChanged)
        self._claves.respondio.connect(self.clavesRespondio)
        self._hilo = None
        self._trabajo = None
        self._escanear_despues = False  # pidieron escanear mientras corría la importación al abrir
        self._recomendacion = Recomendacion()
        self._linea = subtitulos.Linea([])
        self._externos = []
        self._sesion = None
        self._consultando = False
        self._midiendo = set()  # ids con una medición de duración en curso
        self._imdbListo.connect(self._imdb_listo)
        self._buscando_actualizacion = False
        self._actualizacionLista.connect(self._actualizacion_lista)
        self._nueva = None  # la última versión nueva encontrada
        self._actualizando = False
        self._cancelar_descarga = threading.Event()
        self._descargado = None  # carpeta con la versión nueva (portable) o instalador bajado, listo para el cambio
        self._descargaLista.connect(self._descarga_lista)
        self._pantalla = pantalla.Pantalla()
        self._volumenes = volumenes
        self._discos = Discos(config, self._preferencias)
        self._en_curso = None
        self._sesion_id = 0
        self._sacado = False
        self._discos.sondear(self._volumenes())
        self._avisos_iniciales = self._tomar_avisos()  # se guardan porque la UI todavía no está conectada a `avisoDisco`
        self._recargar_catalogo()
        self._timer = QTimer(self)
        self._timer.setInterval(3000)
        self._timer.timeout.connect(self._sondear)
        self._timer.start()
        if self.hayBiblioteca:
            self._iniciar_escaneo(sin_red=True)

    def _local(self):
        return Fuente(0, "", self.config.app_dir, self.config.biblioteca or Path(), self.conn)

    def _fuentes(self):
        """Las que tienen películas para ofrecer: la de la compu si tiene biblioteca y los discos abiertos."""
        return ([self._local()] if self.hayBiblioteca else []) + list(self._discos.abiertas.values())

    def _resolver(self, id_ui):
        """(Fuente, id en su db) de una película de la UI; la fuente es None si su disco ya no está."""
        indice, local = separar(id_ui)
        return (self._local() if indice == 0 else self._discos.abiertas.get(indice)), local

    def _recargar_catalogo(self):
        # Sin biblioteca no hay dónde buscar los pósters entonces el catálogo local queda vacío
        filas = db.catalogo(self.conn) if self.hayBiblioteca else []
        grupos = []
        for f in self._discos.abiertas.values():
            try:
                grupos.append(([dict(r) for r in db.catalogo(f.conn)], f.biblioteca, f.indice, f.etiqueta))
            except sqlite3.Error as e:  # por un esquema de otra versión o un disco que se fue a mitad de la lectura
                log.warning("No se pudo leer el catálogo de «%s»: %s", f.etiqueta, e)
        self._catalogo.recargar(filas, self.config.biblioteca or Path(), grupos)
        self.contadoresChanged.emit()

    # --- discos externos ---

    def _tomar_avisos(self):
        avisos, self._discos.avisos = self._discos.avisos, []
        return avisos

    def _sondear(self):
        """Con una reproducción en curso solo mira que siga su disco y si no busca los discos que entran o salen."""
        if self._en_curso is not None:
            if self._en_curso.indice and not self._sacado and not self._en_curso.sigue():
                self._sacado = True
                if self._sesion is not None:
                    self._sesion.escribe = False  # porque el disco ya no está y no se intenta guardar el progreso
                self.discoSacado.emit(self._en_curso.etiqueta)
            return
        if self._discos.sondear(self._volumenes()):
            if self._recomendacion.datos and self._resolver(self._recomendacion.datos["id"])[0] is None:
                self._avisar_recomendada(self._recomendacion.cerrar())
            self._recargar_catalogo()
            self.discosChanged.emit()
        for aviso in self._tomar_avisos():
            self.avisoDisco.emit(aviso)

    @Slot(result="QVariantList")
    def avisosIniciales(self):
        avisos, self._avisos_iniciales = self._avisos_iniciales, []
        return avisos

    @Property(bool, notify=discosChanged)
    def hayDiscos(self):
        return bool(self._discos.abiertas)

    @Slot(result="QVariantList")
    def discos(self):
        return self._discos.lista()

    @Slot(str, result=str)
    def agregarDisco(self, destino):
        """Guarda un disco a mano. Devuelve un error para mostrar, o ''."""
        error = self._discos.agregar(self._carpeta(destino))
        if not error:
            self._sondear()
            self.discosChanged.emit()
        return error

    @Slot(str)
    def quitarDisco(self, clave):
        self._discos.quitar(clave)
        self._sondear()
        self.discosChanged.emit()

    @Slot(str, bool)
    def ocultarDisco(self, clave, oculto):
        self._discos.ocultar(clave, oculto)
        self._sondear()
        self.discosChanged.emit()

    # --- biblioteca ---

    @Property(bool, notify=bibliotecaChanged)
    def hayBiblioteca(self):
        return self.config.biblioteca is not None and self.config.biblioteca.is_dir()

    @Property(str, notify=bibliotecaChanged)
    def rutaBiblioteca(self):
        """Se informa aunque no exista para que la pantalla de elegir la muestre cuando el disco no está montado."""
        return str(self.config.biblioteca or "")

    @staticmethod
    def _carpeta(destino):
        return Path(QUrl(destino).toLocalFile() if destino.startswith("file:") else destino)

    @Slot(str, result=bool)
    def cambiarBibliotecaPierdePeliculas(self, destino):
        """Con la base vacía nunca avisa porque no hay nada que perder."""
        carpeta = self._carpeta(destino)
        carpetas = db.peliculas_por_carpeta(self.conn)
        return bool(carpetas) and not any((carpeta / c).is_dir() for c in carpetas)

    @Slot(str, result=bool)
    def cambiarBiblioteca(self, destino):
        """Con un escaneo en curso no cambia porque ese escaneo sigue leyendo la biblioteca anterior."""
        carpeta = self._carpeta(destino)
        if self._hilo is not None or not carpeta.is_dir():
            return False
        self._preferencias.setValue("biblioteca/ruta", texto_de_biblioteca(self.config, carpeta))
        self._preferencias.sync()
        self.config.biblioteca = carpeta.resolve()
        self._avisar_recomendada(self._recomendacion.cerrar())
        self._discos.sondear(self._volumenes())  # un disco con esta misma biblioteca se descarta
        self._recargar_catalogo()
        self.bibliotecaChanged.emit()
        return True

    # --- catálogo y detalle ---

    @Property(QObject, constant=True)
    def catalogo(self):
        return self._catalogo

    # --- recomendación a pedido ---

    @Property("QVariantMap", notify=recomendadaChanged)
    def recomendada(self):
        return self._recomendacion.datos

    def _avisar_recomendada(self, cambio):
        if cambio:
            self.recomendadaChanged.emit()

    def _candidata(self):
        """(Fuente, fila) de una película para recomendar, al azar entre las fuentes que tienen, o None."""
        candidatas = []
        for f in self._fuentes():
            try:
                fila = db.recomendada(f.conn)
            except sqlite3.Error:
                continue
            if fila is not None:
                candidatas.append((f, {**dict(fila), "id": f.global_id(fila["id"])}))
        return random.choice(candidatas) if candidatas else None

    @Property(bool, notify=contadoresChanged)
    def puedeRecomendar(self):
        return not self._recomendacion.usada and self._candidata() is not None

    @Slot()
    def recomendar(self):
        candidata = self._candidata()
        fuente, p = candidata if candidata else (None, None)
        if self._recomendacion.elegir(p, fuente.biblioteca if fuente else None):
            self.recomendadaChanged.emit()
            self.contadoresChanged.emit()
            if not p["duracion_ms"]:
                self._medir_duracion(fuente, separar(p["id"])[1], p["video_path"])

    def _medir_duracion(self, fuente, local, video_path):
        """La duración la da el reproductor al cargar; para la recomendada y el detalle se mide sin reproducir.
        En un disco en solo lectura no se mide porque no hay dónde guardarla."""
        pelicula_id = fuente.global_id(local)
        if pelicula_id in self._midiendo or not fuente.escribible:
            return
        self._midiendo.add(pelicula_id)
        medidor = QMediaPlayer(self)

        def estado(status):
            if status not in (QMediaPlayer.LoadedMedia, QMediaPlayer.InvalidMedia):
                return
            if status == QMediaPlayer.LoadedMedia and medidor.duration() > 0:
                try:
                    db.guardar_duracion(fuente.conn, local, medidor.duration())
                except sqlite3.Error as e:  # el disco se fue mientras se medía
                    log.warning("No se pudo guardar la duración en «%s»: %s", fuente.etiqueta, e)
                else:
                    self._avisar_recomendada(self._recomendacion.duracion(pelicula_id, medidor.duration()))
                    self.duracionMedida.emit(pelicula_id, medidor.duration())
            self._midiendo.discard(pelicula_id)
            medidor.deleteLater()

        medidor.mediaStatusChanged.connect(estado)
        medidor.setSource(QUrl.fromLocalFile(str(fuente.biblioteca / video_path)))

    def _posters_cambiaron(self):
        """Tras cambiar algún poster: lo refleja en el catálogo y en la recomendada, si es la suya."""
        self._recargar_catalogo()
        if self._recomendacion.datos:
            fuente, local = self._resolver(self._recomendacion.datos["id"])
            p = db.pelicula(fuente.conn, local) if fuente else None
            self._avisar_recomendada(self._recomendacion.poster(url_poster(fuente.biblioteca, p["poster"]) if p else ""))

    @Slot()
    def cerrarRecomendacion(self):
        self._avisar_recomendada(self._recomendacion.cerrar())

    @Slot(int, result="QVariantMap")
    def pelicula(self, pelicula_id):
        fuente, local = self._resolver(pelicula_id)
        p = db.pelicula(fuente.conn, local) if fuente else None
        if p is None:
            return {}
        # Al abrir el detalle se mira la carpeta: un poster agregado a mano aparece sin re-escanear
        if fuente.escribible and poster.revisar(fuente.conn, fuente.biblioteca, local):
            self._posters_cambiaron()
            p = db.pelicula(fuente.conn, local)
        if not p["duracion_ms"] and p["video_path"]:
            self._medir_duracion(fuente, local, p["video_path"])
        biblioteca = fuente.biblioteca
        return {
            "id": pelicula_id,
            "disco": fuente.etiqueta,
            "soloLectura": not fuente.escribible,
            "titulo": p["titulo"],
            "anio": p["year"] or 0,
            "sinopsis": p["sinopsis"] or "",
            "pais": p["pais"] or "",
            "genero": p["genero"] or "",
            "directores": [{"nombre": n, "otras": o} for n, o in db.personas_de(fuente.conn, local, "director")],
            "actores": [{"nombre": n, "otras": o} for n, o in db.personas_de(fuente.conn, local, "actor")],
            "omdbEstado": p["omdb_estado"],
            "poster": url_poster(biblioteca, p["poster"]),
            # Se mira la carpeta en cada apertura: las tomadas en el reproductor aparecen al volver.
            # `momento`: ms que dice el nombre, o None si no es cronológica (el visor no ofrece «Ir a»)
            "capturas": [{"url": url_poster(biblioteca, r), "momento": capturas.momento_ms(r)}
                         for r in capturas.listar(biblioteca / p["folder_path"])],
            "vista": bool(p["watched"]),
            "progreso": p["progreso_ms"] or 0,
            "duracion": p["duracion_ms"] or 0,
        }

    @Slot(bool)
    def mantenerPantalla(self, activa):
        self._pantalla.mantener(activa)

    @Slot(int, bool)
    def marcarVista(self, pelicula_id, vista):
        fuente, local = self._resolver(pelicula_id)
        if fuente is None or not fuente.escribible:
            return
        db.marcar_vista(fuente.conn, local, vista)
        if vista:
            self._avisar_recomendada(self._recomendacion.empezo(pelicula_id))
        self._recargar_catalogo()

    @Property(int, notify=contadoresChanged)
    def cantidadSinVer(self):
        return db.sin_ver(self.conn)

    @Slot()
    def marcarTodasVistas(self):
        db.marcar_todas_vistas(self.conn)
        self.cerrarRecomendacion()
        self._recargar_catalogo()

    @Slot(result=int)
    def renovarPortadas(self):
        if self._hilo is not None:  # el escaneo también escribe posters
            return 0
        rotadas = poster.rotar(self.conn, self.config.biblioteca, dias=0)
        self._posters_cambiaron()
        return rotadas

    @Slot(int, result=bool)
    def siguientePortada(self, pelicula_id):
        fuente, local = self._resolver(pelicula_id)
        if self._hilo is not None or fuente is None or not fuente.escribible:  # el escaneo también escribe posters
            return False
        cambio = poster.siguiente(fuente.conn, fuente.biblioteca, local)
        if cambio:
            self._posters_cambiaron()
        return cambio

    @Slot(str, result="QVariantList")
    def peliculasDe(self, nombre):
        """Películas de una persona, con los mismos datos que una tarjeta del catálogo, también las de los discos."""
        fuentes = self._fuentes()
        resultado = []
        for f in fuentes:
            try:
                filas = [{**dict(r), "id": f.global_id(r["id"])} for r in db.peliculas_de_persona(f.conn, nombre)]
            except sqlite3.Error:
                continue
            resultado += [{**t, "disco": f.etiqueta} for t in filmografia(filas, f.biblioteca)]
        if len(fuentes) > 1:
            resultado.sort(key=lambda t: (not t["anio"], t["anio"], t["titulo"].casefold()))
        return resultado

    @Slot(int)
    def abrirCarpeta(self, pelicula_id):
        fuente, local = self._resolver(pelicula_id)
        if fuente:
            p = db.pelicula(fuente.conn, local)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(fuente.biblioteca / p["folder_path"])))

    @Slot(int)
    def abrirConSistema(self, pelicula_id):
        fuente, local = self._resolver(pelicula_id)
        if fuente:
            p = db.pelicula(fuente.conn, local)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(fuente.biblioteca / p["video_path"])))

    # --- edición ---

    @Slot(int, result="QVariantMap")
    def datosEdicion(self, pelicula_id):
        fuente, local = self._resolver(pelicula_id)
        p = db.pelicula(fuente.conn, local)
        return {
            "titulo": p["titulo"],
            "anio": str(p["year"] or ""),
            "sinopsis": p["sinopsis"] or "",
            "pais": p["pais"] or "",
            "genero": p["genero"] or "",
            "director": ", ".join(p["director"]),
            "elenco": ", ".join(p["actor"]),
            "imdbId": p["omdb_id"] or "",
            "origen": p["metadatos_origen"] if p["omdb_estado"] == "encontrada" else "",
            "carpeta": p["folder_path"],
            "conClave": bool(self.config.omdb_api_key),
        }

    @Slot(int, "QVariantMap", result=str)
    def guardarEdicion(self, pelicula_id, campos):
        """Guarda el formulario. Devuelve un error para mostrar, o ''."""
        fuente, local = self._resolver(pelicula_id)
        if fuente is None or not fuente.escribible:
            return SOLO_LECTURA
        try:
            aviso = edicion.guardar_manual(fuente.conn, fuente.biblioteca, local, campos)
        except edicion.DatoInvalido as e:
            return str(e)
        self._recargar_catalogo()
        return aviso

    @Property(bool, notify=consultandoImdbChanged)
    def consultandoImdb(self):
        return self._consultando

    @Slot(str, result=str)
    def imdbIdDe(self, texto):
        """Devuelve '' si no hay ID porque QML no tiene None."""
        return nombres.imdb_id(texto) or ""

    @Slot(int, str)
    def buscarEnImdb(self, pelicula_id, texto):
        """Con un IMDb ID (o un link) trae los datos de esa película; con un título, lista candidatos."""
        imdb_id = nombres.imdb_id(texto)
        if imdb_id:
            self.usarImdb(pelicula_id, imdb_id)
        elif texto.strip():
            self._consultar(lambda omdb, tmdb: {"candidatos": edicion.candidatos(omdb, texto)})

    @Slot(int, str)
    def usarImdb(self, pelicula_id, imdb_id):
        """Reemplaza los metadatos por los de `imdb_id` (corregir match o resincronizar)."""
        fuente, local = self._resolver(pelicula_id)
        if fuente is None or not fuente.escribible:
            self.imdbRespondio.emit({"error": SOLO_LECTURA})
            return
        destino = poster.destino_omdb(fuente.conn, fuente.biblioteca, local, reemplazar=True)
        idiomas = self.config.idiomas_sinopsis

        def trabajo(omdb, tmdb):
            datos = omdb.por_id(imdb_id)
            if datos is None:
                return {"error": f"IMDb no tiene una película con el ID {imdb_id}."}
            encontrados, aviso = metadatos.obtener(datos, tmdb, idiomas)
            bajado = False
            if destino is not None and encontrados["poster_url"]:
                try:
                    destino.parent.mkdir(exist_ok=True)
                    omdb.bajar_poster(encontrados["poster_url"], destino)
                    bajado = True
                except ErrorRed:
                    pass
            return {"aplicar": (pelicula_id, encontrados, bajado), "aviso": aviso}

        self._consultar(trabajo)

    @Property(bool, notify=validandoClavesChanged)
    def validandoClaves(self):
        return self._claves.validando

    @Slot(result="QVariantMap")
    def claves(self):
        return self._claves.claves()

    @Slot(str, str)
    def guardarClaves(self, omdb, tmdb):
        self._claves.guardar(omdb, tmdb)

    def _consultar(self, trabajo):
        if self._consultando:
            return
        if not self.config.omdb_api_key:
            self.imdbRespondio.emit({"error": "Falta la clave de OMDb."})
            return
        omdb = Omdb(self.config.omdb_api_key)
        tmdb = Tmdb(self.config.tmdb_api_key) if self.config.tmdb_api_key else None
        self._consultando = True
        self.consultandoImdbChanged.emit()

        def correr():
            try:
                resultado = trabajo(omdb, tmdb)
            except ErrorRed as e:
                resultado = {"error": f"No se pudo consultar IMDb: {e}"}
            except Exception as e:
                resultado = {"error": f"{type(e).__name__}: {e}"}
            self._imdbListo.emit(resultado)

        threading.Thread(target=correr, daemon=True).start()

    def _imdb_listo(self, resultado):
        self._consultando = False
        self.consultandoImdbChanged.emit()
        if "aplicar" in resultado:
            pelicula_id, encontrados, bajado = resultado.pop("aplicar")
            fuente, local = self._resolver(pelicula_id)
            if fuente is None:
                resultado = {"error": "El disco de esta película ya no está."}
            else:
                aviso = edicion.aplicar_omdb(fuente.conn, fuente.biblioteca, local, encontrados, bajado)
                resultado["aviso"] = "\n\n".join(a for a in (resultado.get("aviso"), aviso) if a)
                self._posters_cambiaron()
                resultado["aplicado"] = True
        self.imdbRespondio.emit(resultado)

    # --- actualización ---

    @Property(str, constant=True)
    def version(self):
        return __version__

    @Property(bool, constant=True)
    def puedeActualizar(self):
        return actualizacion.en_build()

    @Property(bool, notify=buscandoActualizacionChanged)
    def buscandoActualizacion(self):
        return self._buscando_actualizacion

    @Slot()
    def buscarActualizacion(self):
        """Consulta la última Release en un hilo aparte y responde por `actualizacionRespondio`."""
        if self._buscando_actualizacion:
            return
        self._buscando_actualizacion = True
        self.buscandoActualizacionChanged.emit()

        def correr():
            try:
                nueva = actualizacion.buscar(prerelease=self._prerelease)
                resultado = {"nueva": nueva} if nueva else {"alDia": True}
            except actualizacion.ErrorRed as e:
                log.warning("No se pudo buscar actualización: %s", e)
                resultado = {"error": "No se pudo consultar GitHub. Revisá la conexión y probá de nuevo."}
            self._actualizacionLista.emit(resultado)

        threading.Thread(target=correr, daemon=True).start()

    def _actualizacion_lista(self, resultado):
        self._buscando_actualizacion = False
        self.buscandoActualizacionChanged.emit()
        self._nueva = resultado.get("nueva")
        self.actualizacionRespondio.emit(resultado)

    @Property(bool, notify=actualizandoChanged)
    def actualizando(self):
        return self._actualizando

    @Slot()
    def actualizar(self):
        """Baja y verifica la versión nueva en un hilo aparte; avisa el avance y el final por señales."""
        if self._actualizando or not self._nueva or not actualizacion.en_build():
            return
        self._actualizando = True
        self.actualizandoChanged.emit()
        self._cancelar_descarga.clear()
        nueva = self._nueva
        instalada = not self.config.portable

        def correr():
            try:
                if instalada:
                    nuevo = instalador.preparar_instalador(nueva, progreso=self.descargaProgreso.emit,
                                                              cancelado=self._cancelar_descarga.is_set)
                else:
                    nuevo = actualizacion.preparar(actualizacion.instalacion_actual(), nueva,
                                                   progreso=self.descargaProgreso.emit,
                                                   cancelado=self._cancelar_descarga.is_set)
                resultado = {"nuevo": nuevo}
            except actualizacion.Cancelado:
                resultado = {"cancelado": True}
            except actualizacion.ErrorActualizacion as e:
                resultado = {"error": str(e)}
            except actualizacion.ErrorRed as e:
                log.warning("Falló la descarga de la actualización: %s", e)
                resultado = {"error": "Se cortó la descarga. Revisá la conexión y probá de nuevo."}
            except Exception as e:
                log.exception("Falló la actualización")
                resultado = {"error": f"{type(e).__name__}: {e}"}
            self._descargaLista.emit(resultado)

        threading.Thread(target=correr, daemon=True).start()

    @Slot()
    def cancelarActualizacion(self):
        self._cancelar_descarga.set()

    def _descarga_lista(self, resultado):
        self._actualizando = False
        self.actualizandoChanged.emit()
        self._descargado = resultado.get("nuevo")
        if not resultado.get("cancelado"):
            self.descargaTerminada.emit(resultado.get("error", ""))

    @Slot()
    def reiniciarParaActualizar(self):
        """Deja corriendo el script que hace el cambio y cierra la app como siempre (guarda lo pendiente)."""
        if self._descargado is None:
            return
        if self.config.portable:
            script = actualizacion.escribir_script(actualizacion.instalacion_actual(), self._descargado,
                                                   os.getpid(), sys.argv[1:])
        else:
            script = instalador.escribir_script_instalador(self._descargado, os.getpid(), sys.argv[1:])
        actualizacion.lanzar(script)
        QCoreApplication.quit()

    # --- faltantes ---

    @Property(int, notify=contadoresChanged)
    def cantidadFaltantes(self):
        return len(db.faltantes(self.conn))

    @Slot(result="QVariantList")
    def faltantes(self):
        return [{"id": f["id"], "titulo": f["titulo"], "anio": f["year"] or 0, "carpeta": f["folder_path"],
                 "vista": bool(f["watched"]), "progreso": f["progreso_ms"] or 0}
                for f in db.faltantes(self.conn)]

    @Slot(result="QVariantList")
    def carpetasParaReasignar(self):
        return [{"id": f["id"], "titulo": f["titulo"], "anio": f["year"] or 0, "carpeta": f["folder_path"],
                 "busqueda": normalizar(f"{f['titulo']} {f['folder_path']}")}
                for f in db.activas_recientes(self.conn)]

    @Slot(str, result=str)
    def normalizar(self, texto):
        return normalizar(texto)

    @Slot(int, int, result=str)
    def reasignar(self, faltante_id, nueva_id):
        """El registro faltante toma la carpeta de `nueva_id`. Devuelve un error para mostrar, o ''."""
        aviso = edicion.fusionar(self.conn, self.config.biblioteca, faltante_id, nueva_id)
        self._recargar_catalogo()
        return aviso

    # --- escaneo ---

    @Property(bool, notify=escaneandoChanged)
    def escaneando(self):
        return self._hilo is not None

    @Slot()
    def escanear(self):
        if self._hilo is not None:
            if self._trabajo.sin_red:
                self._escanear_despues = True
            return
        self._iniciar_escaneo(sin_red=False)

    def _iniciar_escaneo(self, sin_red):
        self._hilo = QThread()
        self._trabajo = TrabajoEscaneo(self.config, sin_red)
        self._trabajo.moveToThread(self._hilo)
        self._hilo.started.connect(self._trabajo.correr)
        self._trabajo.progreso.connect(self.escaneoProgreso)
        self._trabajo.terminado.connect(self._escaneo_terminado)
        self._hilo.start()
        self.escaneandoChanged.emit()

    def _escaneo_terminado(self, informe):
        sin_red = self._trabajo.sin_red
        self._hilo.quit()
        self._hilo.wait()
        self._hilo = self._trabajo = None
        self._posters_cambiaron()
        self.escaneandoChanged.emit()
        if not sin_red:
            self.escaneoTerminado.emit(informe)
            return
        # Un error acá (ej. disco desconectado) no se muestra: el escaneo manual lo va a informar
        if informe.get("sumadas"):
            self.importacionTerminada.emit(informe["sumadas"])
        if self._escanear_despues:
            self._escanear_despues = False
            self.escanear()

    # --- reproducción ---

    @Slot(int, float, result="QVariantMap")
    def abrir(self, pelicula_id, visita_ms):
        """QML pasa -1 cuando no es una Visita porque no tiene None."""
        fuente, local = self._resolver(pelicula_id)
        p = db.pelicula(fuente.conn, local)
        self._sesion = Sesion(fuente.conn, local, int(visita_ms) if visita_ms >= 0 else None, fuente.escribible)
        self._sesion_id = pelicula_id
        self._en_curso = fuente
        self._sacado = False
        video = fuente.biblioteca / p["video_path"]
        self._video = video
        self._externos = subtitulos.externos(video) if video.parent.is_dir() else []
        self._linea = subtitulos.Linea([])
        return {
            "url": QUrl.fromLocalFile(str(video)).toString(),
            "titulo": p["titulo"],
            "externos": [x.name for x in self._externos],
            "soloLectura": not fuente.escribible,
        }

    @Slot(QObject, int)
    def capturar(self, sink, posicion_ms):
        """Guarda el cuadro actual de `sink` (el videoSink del reproductor) como Captura."""
        # En el hilo de la UI solo se toma el cuadro; convertirlo y codificar un 4K a PNG tarda
        # y va aparte
        cuadro = sink.videoFrame()
        if self._en_curso is None or not self._en_curso.escribible or not cuadro.isValid():
            log.warning("Captura fallida: todavía no hay cuadro")
            self.capturaGuardada.emit(False)
            return
        carpeta = self._video.parent

        def correr():
            try:
                imagen = cuadro.toImage()
                buffer = QBuffer()
                buffer.open(QBuffer.WriteOnly)
                if imagen.isNull() or not imagen.save(buffer, "PNG"):
                    raise OSError("no se pudo codificar el PNG")
                ruta = capturas.guardar(carpeta, posicion_ms, bytes(buffer.data()))
            except Exception:
                # Cualquier falla tiene que llegar al aviso, no morir en silencio con el hilo
                log.exception("Captura fallida en %s", carpeta)
                self.capturaGuardada.emit(False)
                return
            log.info("Captura guardada: %s", ruta)
            self.capturaGuardada.emit(True)

        threading.Thread(target=correr, daemon=True).start()

    @Slot("QVariantList", "QVariantList", result="QVariantMap")
    def eleccionInicial(self, pistas_audio, pistas_subs):
        audio = subtitulos.elegir_audio(pistas_audio, self.config.audio_preferido)
        sub = subtitulos.elegir_subtitulo(
            self._video, [x.name for x in self._externos], pistas_subs, self.config.subs_preferido
        )
        tipo, indice = sub if sub else ("", -1)
        return {"audio": audio, "subTipo": tipo, "subIndice": indice}

    # Avisos del reproductor a la sesión abierta; cada uno traduce lo que pasó en recomendada y catálogo

    # float y no int porque las posiciones de QML son real y un int desbordaba (3fea30d)
    @Slot(float, result=float)
    def reproduccionCargo(self, duracion_ms):
        """-1 reemplaza al None de la sesión porque un slot float no puede devolver None a QML."""
        desde = self._sesion.cargo(int(duracion_ms))
        if desde is None:
            return -1
        if duracion_ms > 0:
            self._avisar_recomendada(self._recomendacion.duracion(self._sesion_id, int(duracion_ms)))
        return desde

    @Slot(float)
    def reproduccionPauso(self, posicion_ms):
        self._resultado(self._sesion.pauso(int(posicion_ms)))

    @Slot()
    def reproduccionReanudo(self):
        self._sesion.reanudo()

    @Slot()
    def reproduccionTermino(self):
        self._resultado(self._sesion.termino())

    @Slot(float)
    def reproduccionSalio(self, posicion_ms):
        self._resultado(self._sesion.salio(int(posicion_ms)))

    def _resultado(self, resultado):
        # "empezada" no recarga el catálogo porque pausar no debe recargarlo y al salir lo recarga salioDelReproductor
        if resultado:
            self._avisar_recomendada(self._recomendacion.empezo(self._sesion_id))
        if resultado == "vista":
            self._recargar_catalogo()

    @Slot()
    def salioDelReproductor(self):
        """El reproductor se cerró: recarga el catálogo una sola vez, ya con el progreso guardado."""
        self._en_curso = None
        self._recargar_catalogo()
        QTimer.singleShot(10_000, self._sondear)  # porque durante la reproducción no se buscan discos

    def _volumen(self):
        return float(self._preferencias.value("reproductor/volumen", 1.0))

    def _set_volumen(self, valor):
        if valor != self._volumen():
            self._preferencias.setValue("reproductor/volumen", valor)
            self.volumenChanged.emit()

    def _silenciado(self):
        return self._preferencias.value("reproductor/silenciado", False, type=bool)

    def _set_silenciado(self, valor):
        if valor != self._silenciado():
            self._preferencias.setValue("reproductor/silenciado", valor)
            self.volumenChanged.emit()

    # Volumen elegido por el usuario (0..1, escala de percepción); se recuerda entre películas
    volumen = Property(float, _volumen, _set_volumen, notify=volumenChanged)
    silenciado = Property(bool, _silenciado, _set_silenciado, notify=volumenChanged)

    def _subs_tamano(self):
        return float(self._preferencias.value("subtitulos/tamano", 1.0))

    def _set_subs_tamano(self, valor):
        if valor != self._subs_tamano():
            self._preferencias.setValue("subtitulos/tamano", valor)
            self.estiloSubsChanged.emit()

    def _subs_color(self):
        return str(self._preferencias.value("subtitulos/color", "#ffffff"))

    def _set_subs_color(self, valor):
        if valor != self._subs_color():
            self._preferencias.setValue("subtitulos/color", valor)
            self.estiloSubsChanged.emit()

    # Estilo de los subtítulos del overlay, global: escala sobre el tamaño base y color del texto
    subsTamano = Property(float, _subs_tamano, _set_subs_tamano, notify=estiloSubsChanged)
    subsColor = Property(str, _subs_color, _set_subs_color, notify=estiloSubsChanged)

    @Slot(int, result=str)
    def cargarExterno(self, indice):
        """Activa un subtítulo externo (-1 = ninguno). Devuelve un error legible o ''."""
        if indice < 0:
            self._linea = subtitulos.Linea([])
        else:
            try:
                eventos, _ = subtitulos.leer(self._externos[indice])
            except Exception as e:
                self._linea = subtitulos.Linea([])
                self.externoChanged.emit()
                return f"No se pudo leer {self._externos[indice].name}: {e}"
            self._linea = subtitulos.Linea(eventos)
        self.externoChanged.emit()
        return ""

    @Slot(int, result=str)
    def textoEn(self, ms):
        return self._linea.texto_en(ms)

    @Slot(str, result=str)
    def idiomaDe(self, texto):
        """Código de idioma ('es', 'en', ...) que aparece en un nombre de archivo o título, o ''."""
        return idioma_de(texto) or ""

    def cerrar(self):
        if self._hilo is not None:
            self._hilo.quit()
            self._hilo.wait()
        self._timer.stop()
        self._discos.cerrar()
        self._preferencias.sync()
        self.conn.close()
