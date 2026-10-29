"""Puente entre la lógica en Python y la UI en QML."""

import logging
import threading
from dataclasses import asdict
from datetime import date
from pathlib import Path

from PySide6.QtCore import (
    Property, QAbstractListModel, QBuffer, QModelIndex, QObject, QSettings, QThread, Qt, QUrl, Signal, Slot,
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtMultimedia import QMediaPlayer

from . import __version__, actualizacion, capturas, db, edicion, metadatos, poster, subtitulos
from .catalogo import (
    CLAVES_TARJETA, Recomendacion, en_periodo, es_incompleta, filmografia, periodos, tarjeta, url_poster,
)
from .nombres import idioma_de, normalizar
from .escaneo import escanear, importar_sin_red
from .omdb import ErrorRed, Omdb
from .tmdb import Tmdb

log = logging.getLogger(__name__)


class ModeloCatalogo(QAbstractListModel):
    ROLES = {Qt.UserRole + 1 + i: clave.encode() for i, clave in enumerate(CLAVES_TARJETA)}

    periodosChanged = Signal()
    periodoChanged = Signal()
    incompletasChanged = Signal()

    def __init__(self, parent=None, anio_actual=None):
        super().__init__(parent)
        self._todas = []
        self._filas = []
        self._palabras = []
        self._vista = None  # None = todas, True = vistas, False = no vistas
        self._anio_actual = anio_actual  # None = el de hoy
        self._periodo = ""  # "" = todos, "1960s" = una década, "2025" = un año
        self._periodos = []
        self._solo_incompletas = False

    def recargar(self, filas, biblioteca):
        self._todas = [
            {
                **tarjeta(f, biblioteca),
                "_busqueda": normalizar(f"{f['titulo']} | {f['personas'] or ''}"),
                "_incompleta": es_incompleta(f, biblioteca),
            }
            for f in filas
        ]
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

    @Property(list, notify=periodosChanged)
    def periodos(self):
        return self._periodos

    @Property(str, notify=periodoChanged)
    def periodo(self):
        return self._periodo

    @Slot(str)
    def filtrarPeriodo(self, clave):
        if clave != self._periodo:
            self._periodo = clave
            self.periodoChanged.emit()
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
        self._palabras = normalizar(texto).split()
        self._aplicar()

    @Slot(str)
    def filtrarVistas(self, cuales):
        """cuales: "todas", "vistas" o "noVistas"."""
        self._vista = {"vistas": True, "noVistas": False}.get(cuales)
        self._aplicar()

    def _aplicar(self):
        self.beginResetModel()
        self._filas = [
            f for f in self._todas
            if (self._vista is None or f["vista"] == self._vista)
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
    capturaGuardada = Signal(bool)  # True = escrita; False = falló y el motivo va al log
    buscandoActualizacionChanged = Signal()
    actualizacionRespondio = Signal("QVariantMap")
    _actualizacionLista = Signal(object)  # desde el hilo de la consulta

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.conn = db.conectar(config.db_path)
        self._catalogo = ModeloCatalogo(self)
        # Preferencias de la app (no de la biblioteca): quedan junto a pelis.toml
        self._preferencias = QSettings(str(config.app_dir / "preferencias.ini"), QSettings.IniFormat)
        self._hilo = None
        self._trabajo = None
        self._escanear_despues = False  # pidieron escanear mientras corría la importación al abrir
        self._recomendacion = Recomendacion()
        self._linea = subtitulos.Linea([])
        self._externos = []
        self._consultando = False
        self._midiendo = set()  # ids con una medición de duración en curso
        self._imdbListo.connect(self._imdb_listo)
        self._buscando_actualizacion = False
        self._actualizacionLista.connect(self._actualizacion_lista)
        self._recargar_catalogo()
        self._elegir_recomendada()
        self._iniciar_escaneo(sin_red=True)

    def _recargar_catalogo(self):
        self._catalogo.recargar(db.catalogo(self.conn), self.config.biblioteca)
        self.contadoresChanged.emit()

    def _ruta(self, relativa):
        return self.config.biblioteca / relativa

    # --- catálogo y detalle ---

    @Property(QObject, constant=True)
    def catalogo(self):
        return self._catalogo

    # --- recomendación al abrir ---

    @Property("QVariantMap", notify=recomendadaChanged)
    def recomendada(self):
        return self._recomendacion.datos

    def _avisar_recomendada(self, cambio):
        if cambio:
            self.recomendadaChanged.emit()

    def _elegir_recomendada(self):
        """Se elige una vez por apertura; si la biblioteca estaba vacía, se reintenta tras importar."""
        if self._recomendacion.datos:
            return
        p = db.recomendada(self.conn)
        if self._recomendacion.elegir(p, self.config.biblioteca):
            self.recomendadaChanged.emit()
            if not p["duracion_ms"]:
                self._medir_duracion(p["id"], p["video_path"])

    def _medir_duracion(self, pelicula_id, video_path):
        """La duración la da el reproductor al cargar; para la recomendada y el detalle se mide sin reproducir."""
        if pelicula_id in self._midiendo:
            return
        self._midiendo.add(pelicula_id)
        medidor = QMediaPlayer(self)

        def estado(status):
            if status not in (QMediaPlayer.LoadedMedia, QMediaPlayer.InvalidMedia):
                return
            if status == QMediaPlayer.LoadedMedia and medidor.duration() > 0:
                db.guardar_duracion(self.conn, pelicula_id, medidor.duration())
                self._avisar_recomendada(self._recomendacion.duracion(pelicula_id, medidor.duration()))
                self.duracionMedida.emit(pelicula_id, medidor.duration())
            self._midiendo.discard(pelicula_id)
            medidor.deleteLater()

        medidor.mediaStatusChanged.connect(estado)
        medidor.setSource(QUrl.fromLocalFile(str(self._ruta(video_path))))

    def _refrescar_poster_recomendada(self):
        """El poster pudo cambiar (rotación, escaneo) después de elegir la recomendada."""
        if not self._recomendacion.datos:
            return
        p = db.pelicula(self.conn, self._recomendacion.datos["id"])
        self._avisar_recomendada(self._recomendacion.poster(url_poster(self.config.biblioteca, p["poster"]) if p else ""))

    @Slot()
    def cerrarRecomendacion(self):
        self._avisar_recomendada(self._recomendacion.cerrar())

    @Slot(int, result="QVariantMap")
    def pelicula(self, pelicula_id):
        p = db.pelicula(self.conn, pelicula_id)
        if p is None:
            return {}
        # Al abrir el detalle se mira la carpeta: un poster agregado a mano aparece sin re-escanear
        if poster.revisar(self.conn, self.config.biblioteca, pelicula_id):
            self._recargar_catalogo()
            p = db.pelicula(self.conn, pelicula_id)
        if not p["duracion_ms"] and p["video_path"]:
            self._medir_duracion(pelicula_id, p["video_path"])
        return {
            "id": p["id"],
            "titulo": p["titulo"],
            "anio": p["year"] or 0,
            "sinopsis": p["sinopsis"] or "",
            "pais": p["pais"] or "",
            "genero": p["genero"] or "",
            "directores": [{"nombre": n, "otras": o} for n, o in db.personas_de(self.conn, pelicula_id, "director")],
            "actores": [{"nombre": n, "otras": o} for n, o in db.personas_de(self.conn, pelicula_id, "actor")],
            "omdbEstado": p["omdb_estado"],
            "poster": url_poster(self.config.biblioteca, p["poster"]),
            # Se mira la carpeta en cada apertura: las tomadas en el reproductor aparecen al volver
            "capturas": [url_poster(self.config.biblioteca, r) for r in capturas.listar(self._ruta(p["folder_path"]))],
            "vista": bool(p["watched"]),
            "progreso": p["progreso_ms"] or 0,
            "duracion": p["duracion_ms"] or 0,
        }

    @Slot(int, bool)
    def marcarVista(self, pelicula_id, vista):
        db.marcar_vista(self.conn, pelicula_id, vista)
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
        self._recargar_catalogo()
        self._refrescar_poster_recomendada()
        return rotadas

    @Slot(str, result="QVariantList")
    def peliculasDe(self, nombre):
        """Películas de una persona, con los mismos datos que una tarjeta del catálogo."""
        return filmografia(db.peliculas_de_persona(self.conn, nombre), self.config.biblioteca)

    @Slot(int)
    def abrirCarpeta(self, pelicula_id):
        p = db.pelicula(self.conn, pelicula_id)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._ruta(p["folder_path"]))))

    @Slot(int)
    def abrirConSistema(self, pelicula_id):
        p = db.pelicula(self.conn, pelicula_id)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._ruta(p["video_path"]))))

    # --- edición ---

    @Slot(int, result="QVariantMap")
    def datosEdicion(self, pelicula_id):
        p = db.pelicula(self.conn, pelicula_id)
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
        try:
            aviso = edicion.guardar_manual(self.conn, self.config.biblioteca, pelicula_id, campos)
        except edicion.DatoInvalido as e:
            return str(e)
        self._recargar_catalogo()
        return aviso

    @Property(bool, notify=consultandoImdbChanged)
    def consultandoImdb(self):
        return self._consultando

    @Slot(int, str)
    def buscarEnImdb(self, pelicula_id, texto):
        """Con un IMDb ID (o un link) trae los datos de esa película; con un título, lista candidatos."""
        imdb_id = edicion.imdb_id_de(texto)
        if imdb_id:
            self.usarImdb(pelicula_id, imdb_id)
        elif texto.strip():
            self._consultar(lambda omdb, tmdb: {"candidatos": edicion.candidatos(omdb, texto)})

    @Slot(int, str)
    def usarImdb(self, pelicula_id, imdb_id):
        """Reemplaza los metadatos por los de `imdb_id` (corregir match o resincronizar)."""
        destino = edicion.destino_poster(self.conn, self.config.biblioteca, pelicula_id)
        idiomas = self.config.idiomas_sinopsis

        def trabajo(omdb, tmdb):
            datos = omdb.por_id(imdb_id)
            if datos is None:
                return {"error": f"IMDb no tiene una película con el ID {imdb_id}."}
            encontrados, aviso = metadatos.obtener(datos, tmdb, idiomas)
            bajado = edicion.bajar_poster(omdb, encontrados["poster_url"], destino)
            return {"aplicar": (pelicula_id, encontrados, bajado), "aviso": aviso}

        self._consultar(trabajo)

    def _consultar(self, trabajo):
        if self._consultando:
            return
        if not self.config.omdb_api_key:
            self.imdbRespondio.emit({"error": "Falta omdb_api_key en pelis.toml."})
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
            aviso = edicion.aplicar_omdb(self.conn, self.config.biblioteca, pelicula_id, encontrados, bajado)
            resultado["aviso"] = "\n\n".join(a for a in (resultado.get("aviso"), aviso) if a)
            self._recargar_catalogo()
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
                nueva = actualizacion.buscar()
                resultado = {"nueva": nueva} if nueva else {"alDia": True}
            except actualizacion.ErrorRed as e:
                log.warning("No se pudo buscar actualización: %s", e)
                resultado = {"error": "No se pudo consultar GitHub. Revisá la conexión y probá de nuevo."}
            self._actualizacionLista.emit(resultado)

        threading.Thread(target=correr, daemon=True).start()

    def _actualizacion_lista(self, resultado):
        self._buscando_actualizacion = False
        self.buscandoActualizacionChanged.emit()
        self.actualizacionRespondio.emit(resultado)

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
        self._recargar_catalogo()
        self._elegir_recomendada()
        self._refrescar_poster_recomendada()
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

    @Slot(int, result="QVariantMap")
    def abrir(self, pelicula_id):
        p = db.pelicula(self.conn, pelicula_id)
        video = self._ruta(p["video_path"])
        self._video = video
        self._externos = subtitulos.externos(video) if video.parent.is_dir() else []
        self._linea = subtitulos.Linea([])
        return {
            "url": QUrl.fromLocalFile(str(video)).toString(),
            "titulo": p["titulo"],
            "progreso": p["progreso_ms"] or 0,
            "externos": [x.name for x in self._externos],
        }

    @Slot(QObject, int)
    def capturar(self, sink, posicion_ms):
        """Guarda el cuadro actual de `sink` (el videoSink del reproductor) como Captura."""
        # En el hilo de la UI solo se toma el cuadro; convertirlo y codificar un 4K a PNG tarda
        # y va aparte
        cuadro = sink.videoFrame()
        if not cuadro.isValid():
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

    @Slot(int, int)
    def guardarProgreso(self, pelicula_id, ms):
        db.guardar_progreso(self.conn, pelicula_id, ms)
        if ms > 0:
            self._avisar_recomendada(self._recomendacion.empezo(pelicula_id))
        self._recargar_catalogo()

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

    @Slot(int, int)
    def guardarDuracion(self, pelicula_id, ms):
        db.guardar_duracion(self.conn, pelicula_id, ms)

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
        self._preferencias.sync()
        self.conn.close()
