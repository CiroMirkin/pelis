"""Guardado de las claves de API desde la app, con validación contra OMDb y TMDb."""

import threading

from PySide6.QtCore import Property, QObject, Signal

from . import db
from .config import CLAVES, aplicar_preferencias
from .omdb import ErrorRed, Omdb
from .tmdb import Tmdb


class GestorClaves(QObject):
    validandoChanged = Signal()
    # Resultado de guardar las claves: {guardado, errores: {omdb?, tmdb?}, sinVerificar, omdbVacia (se borró la clave de OMDb en este guardado), pendientes}
    respondio = Signal("QVariantMap")
    _listas = Signal(object)  # desde el hilo de la validación

    def __init__(self, config, preferencias, conn, parent=None):
        super().__init__(parent)
        self._config = config
        self._preferencias = preferencias
        self._conn = conn
        self._validando = False
        aplicar_preferencias(config, preferencias)
        self._listas.connect(self._terminar)

    @Property(bool, notify=validandoChanged)
    def validando(self):
        return self._validando

    def claves(self):
        return {nombre: getattr(self._config, atributo) for nombre, atributo in CLAVES.items()}

    def guardar(self, omdb, tmdb):
        """Solo valida las claves que cambiaron y no guarda ninguna si alguna falla."""
        if self._validando:
            return
        nuevas = {"omdb": omdb.strip(), "tmdb": tmdb.strip()}
        actuales = self.claves()
        cambiadas = {n: c for n, c in nuevas.items() if c != actuales[n]}
        clientes = {"omdb": Omdb, "tmdb": Tmdb}
        self._validando = True
        self.validandoChanged.emit()

        def correr():
            errores, sin_verificar = {}, False
            for nombre, clave in cambiadas.items():
                if not clave:
                    continue
                try:
                    if not clientes[nombre](clave).clave_valida():
                        errores[nombre] = "La clave no es válida."
                except ErrorRed:
                    # Sin conexión no se bloquea el guardado porque la clave se guarda igual y se avisa
                    sin_verificar = True
            self._listas.emit((cambiadas, errores, sin_verificar))

        threading.Thread(target=correr, daemon=True).start()

    def _terminar(self, resultado):
        cambiadas, errores, sin_verificar = resultado
        self._validando = False
        self.validandoChanged.emit()
        if errores:
            self.respondio.emit({"guardado": False, "errores": errores, "sinVerificar": False,
                                 "omdbVacia": False, "pendientes": 0})
            return
        for nombre, clave in cambiadas.items():
            self._preferencias.setValue(f"claves/{nombre}", clave)
            setattr(self._config, CLAVES[nombre], clave)
        self._preferencias.sync()
        self.respondio.emit({"guardado": True, "errores": {}, "sinVerificar": sin_verificar,
                             "omdbVacia": "omdb" in cambiadas and not cambiadas["omdb"],
                             "pendientes": db.cantidad_pendientes(self._conn) if cambiadas.get("omdb") else 0})
