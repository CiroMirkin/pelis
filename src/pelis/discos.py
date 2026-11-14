"""Discos externos: cada uno trae su propia app (app/pelis.db) y la compu suma sus películas al catálogo sin copiarlas.

Sin Qt salvo `volumenes_montados` y QSettings (que llega de afuera), para que se testee con carpetas comunes.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import config as configuracion
from . import db

log = logging.getLogger(__name__)

INTERVALO = 1_000_000  # id de la UI = indice de la fuente * INTERVALO + id en su db; la compu es la fuente 0
ESPERA_DB = 0.5  # segundos: la db del disco puede estar tomada por su propia app
TABLAS = ("peliculas", "posters", "personas", "pelicula_personas")


def _es_archivo(ruta):
    """Un punto de montaje del sistema (ej. /boot/efi) puede negar el acceso: eso es que no hay disco ahí."""
    try:
        return Path(ruta).is_file()
    except OSError:
        return False


def _es_carpeta(ruta):
    try:
        return Path(ruta).is_dir()
    except OSError:
        return False


def id_global(indice, id_local):
    return indice * INTERVALO + id_local


def separar(id_ui):
    """(indice de la fuente, id en su db)"""
    return divmod(id_ui, INTERVALO)


@dataclass
class Fuente:
    """Una db con su biblioteca: la de la compu (indice 0, sin etiqueta) o la de un disco."""
    indice: int
    etiqueta: str
    app_dir: Path
    biblioteca: Path
    conn: sqlite3.Connection
    escribible: bool = True
    bloqueada: bool = False  # solo lectura porque la db estaba tomada y no por su esquema
    clave: str = ""

    def global_id(self, id_local):
        return id_global(self.indice, id_local)

    def sigue(self):
        """Si el disco sigue ahí: la db y la carpeta de películas existen."""
        try:
            return _es_archivo(self.app_dir / "pelis.db") and _es_carpeta(self.biblioteca)
        except OSError:
            return False

    def cerrar(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass


@dataclass
class Entrada:
    """Un disco visible para el usuario, esté abierto, oculto o descartado."""
    clave: str
    app_dir: Path
    etiqueta: str
    manual: bool
    oculto: bool = False


def clave_de(app_dir, etiqueta):
    return f"{Path(app_dir).resolve()}|{etiqueta}"


def volumenes_montados():
    """[(raíz, etiqueta)] de lo montado. Sin nombre de volumen, la etiqueta es el nombre de la carpeta de montaje."""
    from PySide6.QtCore import QStorageInfo

    res = []
    for v in QStorageInfo.mountedVolumes():
        if not (v.isValid() and v.isReady()):
            continue
        raiz = Path(v.rootPath())
        res.append((raiz, v.name() or raiz.name or str(raiz).rstrip("\\/")))
    return res


def esquema(conn):
    """{tabla: columnas} de las tablas que la compu espera."""
    return {t: {f["name"] for f in conn.execute(f"PRAGMA table_info({t})")} for t in TABLAS}


def _esquema_esperado():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(db.ESQUEMA)
    try:
        return esquema(conn)
    finally:
        conn.close()


ESQUEMA_ESPERADO = _esquema_esperado()


def abrir_db(ruta):
    """(conexión, escribible, bloqueada). La compu nunca migra la db del disco.

    Escribible si el esquema coincide con el esperado y nadie más la tiene tomada.
    """
    ruta = Path(ruta).resolve()
    solo_lectura = sqlite3.connect(ruta.as_uri() + "?mode=ro", uri=True, timeout=ESPERA_DB)
    solo_lectura.row_factory = sqlite3.Row
    try:
        coincide = esquema(solo_lectura) == ESQUEMA_ESPERADO
    except sqlite3.Error:
        coincide = False
    if not coincide:
        return solo_lectura, False, False
    rw = sqlite3.connect(ruta, timeout=ESPERA_DB)
    rw.row_factory = sqlite3.Row
    try:
        rw.execute("BEGIN IMMEDIATE")
        rw.rollback()
    except sqlite3.OperationalError as e:
        rw.close()
        return solo_lectura, False, "locked" in str(e)
    solo_lectura.close()
    rw.execute("PRAGMA foreign_keys = ON")
    return rw, True, False


class Discos:
    """Los discos abiertos y la lista de los conocidos. El hilo de la UI llama a `sondear` cada pocos segundos."""

    def __init__(self, config, preferencias):
        self.config = config
        self._preferencias = preferencias
        self.abiertas = {}
        self.conocidas = {}  # clave -> Entrada, sin los descartados
        self._indices = {}  # clave -> indice, estable mientras corre la app
        self._descartadas = set()
        self._avisadas = set()
        self.avisos = []  # para mostrar una vez

    # --- lo guardado en preferencias.ini ---

    def _lista(self, clave):
        try:
            datos = json.loads(str(self._preferencias.value(clave, "[]")) or "[]")
        except ValueError:
            return []
        return [str(x) for x in datos] if isinstance(datos, list) else []

    def _guardar(self, clave, valores):
        self._preferencias.setValue(clave, json.dumps(valores))
        self._preferencias.sync()

    def manuales(self):
        return self._lista("discos/manuales")

    def ocultos(self):
        return self._lista("discos/ocultos")

    def agregar(self, carpeta):
        """Guarda la carpeta (la raíz del disco o su app/). Devuelve un error para mostrar, o ''."""
        app = self._app_de(Path(carpeta))
        if app is None:
            return "Esa carpeta no tiene una app de Pelis (app/pelis.db)."
        if self._es_esta_app(app):
            return "Esa es la app que estás usando."
        texto = str(app.resolve())
        manuales = self.manuales()
        if texto not in manuales:
            self._guardar("discos/manuales", manuales + [texto])
        return ""

    def quitar(self, clave):
        """Solo los agregados a mano: los detectados solos no se guardan."""
        entrada = self.conocidas.get(clave)
        if entrada is None or not entrada.manual:
            return
        self._guardar("discos/manuales", [m for m in self.manuales() if m != str(entrada.app_dir.resolve())])

    def ocultar(self, clave, oculto):
        ocultos = [o for o in self.ocultos() if o != clave]
        self._guardar("discos/ocultos", ocultos + [clave] if oculto else ocultos)

    # --- sondeo ---

    @staticmethod
    def _app_de(carpeta):
        for app in (carpeta / "app", carpeta):
            if _es_archivo(app / "pelis.db"):
                return app
        return None

    def _es_esta_app(self, app):
        try:
            return Path(app).resolve() == Path(self.config.app_dir).resolve()
        except OSError:
            return False

    @staticmethod
    def _etiqueta(app, volumenes):
        """El nombre del volumen que contiene a `app`, o el de la carpeta del disco si es solo la raíz."""
        app = app.resolve()
        mejor = None
        for raiz, etiqueta in volumenes:
            if raiz.parent != raiz and (raiz == app or raiz in app.parents):
                if mejor is None or len(raiz.parts) > len(mejor[0].parts):
                    mejor = (raiz, etiqueta)
        return mejor[1] if mejor else app.parent.name or str(app)

    def _entradas(self, volumenes):
        ocultos = set(self.ocultos())
        entradas = {}
        for raiz, etiqueta in volumenes:
            if _es_archivo(raiz / "app" / "pelis.db") and not self._es_esta_app(raiz / "app"):
                e = Entrada(clave_de(raiz / "app", etiqueta), raiz / "app", etiqueta, manual=False)
                entradas[e.clave] = e
        for texto in self.manuales():
            app = Path(texto)
            if _es_archivo(app / "pelis.db") and not self._es_esta_app(app):
                e = Entrada(clave_de(app, self._etiqueta(app, volumenes)), app, self._etiqueta(app, volumenes), manual=True)
                entradas[e.clave] = e
        for e in entradas.values():
            e.oculto = e.clave in ocultos
        return entradas

    def sondear(self, volumenes):
        """Abre los discos que aparecieron y cierra los que salieron o se ocultaron. Devuelve si cambió algo."""
        entradas = self._entradas(volumenes)
        cambio = False
        for clave in [c for c in list(self._descartadas) if c not in entradas]:
            self._descartadas.discard(clave)
        for indice, fuente in list(self.abiertas.items()):
            e = entradas.get(fuente.clave)
            if e is None or e.oculto or not fuente.sigue():
                fuente.cerrar()
                del self.abiertas[indice]
                cambio = True
        for clave, e in entradas.items():
            if e.oculto or clave in self._descartadas:
                continue
            abierta = next((f for f in self.abiertas.values() if f.clave == clave), None)
            if abierta is None:
                fuente = self._abrir(e)
                if fuente is None:
                    continue
                self.abiertas[fuente.indice] = fuente
                cambio = True
                if not fuente.escribible:
                    self.avisos.append(self._aviso_solo_lectura(fuente))
            elif abierta.bloqueada:
                # Se liberó: el próximo sondeo la reabre en lectura y escritura
                nueva = self._abrir(e, indice=abierta.indice)
                if nueva is not None and nueva.escribible:
                    abierta.cerrar()
                    self.abiertas[abierta.indice] = nueva
                    cambio = True
                elif nueva is not None:
                    nueva.cerrar()
        self.conocidas = {c: e for c, e in entradas.items() if c not in self._descartadas}
        return cambio

    @staticmethod
    def _aviso_solo_lectura(fuente):
        motivo = "la está usando su propia app" if fuente.bloqueada else "es de otra versión de Pelis"
        return f"«{fuente.etiqueta}» se abrió en solo lectura porque {motivo}."

    def _abrir(self, entrada, indice=None):
        try:
            disco = configuracion.cargar(entrada.app_dir, portable=False)
            from PySide6.QtCore import QSettings
            ini = entrada.app_dir / "preferencias.ini"
            if _es_archivo(ini):
                configuracion.aplicar_preferencias(disco, QSettings(str(ini), QSettings.IniFormat))
        except (configuracion.ErrorConfig, OSError, ValueError) as e:
            self._avisar(entrada, f"No se pudo leer la configuración de «{entrada.etiqueta}»: {e}")
            return None
        if disco.biblioteca is None or not _es_carpeta(disco.biblioteca):
            self._avisar(entrada, f"«{entrada.etiqueta}» no tiene una carpeta de películas: se omite.")
            return None
        local = self.config.biblioteca
        if local is not None and disco.biblioteca == Path(local).resolve():
            self._descartadas.add(entrada.clave)
            return None
        try:
            conn, escribible, bloqueada = abrir_db(entrada.app_dir / "pelis.db")
        except sqlite3.Error as e:
            self._avisar(entrada, f"No se pudo abrir la base de «{entrada.etiqueta}»: {e}")
            return None
        if indice is None:
            indice = self._indices.setdefault(entrada.clave, len(self._indices) + 1)
        return Fuente(indice, entrada.etiqueta, entrada.app_dir, disco.biblioteca, conn, escribible, bloqueada,
                      entrada.clave)

    def _avisar(self, entrada, texto):
        if entrada.clave not in self._avisadas:
            self._avisadas.add(entrada.clave)
            self.avisos.append(texto)
            log.warning(texto)

    def cerrar(self):
        for f in self.abiertas.values():
            f.cerrar()
        self.abiertas.clear()

    def lista(self):
        """Todos los conocidos para la lista de la UI, abiertos o no."""
        abiertas = {f.clave: f for f in self.abiertas.values()}
        return [{"id": e.clave, "etiqueta": e.etiqueta, "ruta": str(e.app_dir.parent), "manual": e.manual,
                 "oculto": e.oculto, "abierto": e.clave in abiertas,
                 "soloLectura": e.clave in abiertas and not abiertas[e.clave].escribible}
                for e in self.conocidas.values()]
