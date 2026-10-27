"""Escaneo de la biblioteca (reglas en .scratch/biblioteca-multimedia/spec.md)."""

from dataclasses import dataclass, field
from pathlib import Path

from . import archivo_metadatos, db, metadatos, poster
from .nombres import parsear_carpeta, parsear_video
from .omdb import ErrorRed

EXTENSIONES_VIDEO = {".mkv", ".mp4", ".avi", ".m4v", ".mov", ".wmv", ".ts", ".webm"}


@dataclass
class Informe:
    agregadas: int = 0
    no_encontradas: list = field(default_factory=list)
    pendientes: list = field(default_factory=list)
    faltantes: list = field(default_factory=list)
    reactivadas: list = field(default_factory=list)
    reasignadas: list = field(default_factory=list)  # [(carpeta vieja, carpeta nueva)]
    problemas: list = field(default_factory=list)  # [(carpeta, motivo)]
    desde_archivo: list = field(default_factory=list)  # importadas desde pelis.json, sin OMDb
    archivos_invalidos: list = field(default_factory=list)  # [(carpeta, motivo)]
    archivos_sin_escribir: list = field(default_factory=list)  # [(carpeta, aviso)]: pelis.json que no se pudo escribir
    aviso_omdb: str = ""
    aviso_tmdb: str = ""


def buscar_en_omdb(omdb, nombre_carpeta, nombre_video, imdb_id=None):
    """Cascada de match. Devuelve los datos de OMDb o None; ErrorRed se propaga.

    imdb_id (de pelis.json) tiene prioridad sobre el [tt…] del nombre de la carpeta.
    """
    titulo, anio, imdb_id_carpeta = parsear_carpeta(nombre_carpeta)
    imdb_id = imdb_id or imdb_id_carpeta
    titulo_video, anio_video = parsear_video(nombre_video)
    intentos = []
    if imdb_id:
        intentos.append(lambda: omdb.por_id(imdb_id))
    if anio:
        intentos.append(lambda: omdb.por_titulo(titulo, anio))
    if titulo_video and anio_video:
        intentos.append(lambda: omdb.por_titulo(titulo_video, anio_video))
    intentos.append(lambda: omdb.por_titulo(titulo))
    for intento in intentos:
        if datos := intento():
            return datos
    return None


class Escaneo:
    def __init__(self, conn, biblioteca, omdb, progreso=lambda actual, total, nombre: None,
                 tmdb=None, idiomas_sinopsis=("es-MX", "es-ES"), marcar_faltantes=True):
        self.conn = conn
        self.biblioteca = Path(biblioteca)
        self.omdb = omdb  # None si no hay API key
        self.tmdb = tmdb  # None si no hay API key: la sinopsis queda la de OMDb (inglés)
        self.idiomas_sinopsis = list(idiomas_sinopsis)
        self.tmdb_caido = False
        self.progreso = progreso
        self.marcar_faltantes = marcar_faltantes
        self.informe = Informe()
        self._reasignadas = set()  # ids que pasaron a otra carpeta: no se marcan faltantes
        self.omdb_caido = False  # tras el primer error de red no se insiste: el resto queda pendiente
        if omdb is None:
            self.informe.aviso_omdb = "Falta omdb_api_key en pelis.toml: las películas quedan pendientes de metadatos."

    def ejecutar(self):
        existentes = db.peliculas_por_carpeta(self.conn)
        carpetas = sorted((p for p in self.biblioteca.iterdir() if p.is_dir()), key=lambda p: p.name.lower())
        self._presentes = {c.name for c in carpetas}

        for i, carpeta in enumerate(carpetas, 1):
            self.progreso(i, len(carpetas), carpeta.name)
            fila = existentes.get(carpeta.name)
            if fila is None:
                self._nueva(carpeta)
            else:
                if fila["estado"] == "faltante":
                    db.cambiar_estado(self.conn, fila["id"], "activa")
                    self.informe.reactivadas.append(carpeta.name)
                if fila["estado"] != "papelera":
                    poster.revisar(self.conn, self.biblioteca, fila["id"])
                    if fila["omdb_estado"] == "pendiente":
                        self._metadatos(fila["id"], carpeta)
            self.conn.commit()

        self._sincronizar_archivos()
        if not self.marcar_faltantes:
            return self.informe
        for folder_path, fila in existentes.items():
            if fila["estado"] == "activa" and folder_path not in self._presentes and fila["id"] not in self._reasignadas:
                db.cambiar_estado(self.conn, fila["id"], "faltante")
                self.informe.faltantes.append(folder_path)
        self.conn.commit()
        return self.informe

    def _sincronizar_archivos(self):
        invalidos, sin_escribir = metadatos.sincronizar(self.conn, self.biblioteca)
        # Lo que ya se informó al importar o al guardar en este mismo escaneo no se repite
        ya_informados = {c for c, _ in self.informe.archivos_invalidos + self.informe.archivos_sin_escribir}
        self.informe.archivos_invalidos += [(c, m) for c, m in invalidos if c not in ya_informados]
        self.informe.archivos_sin_escribir += [(c, a) for c, a in sin_escribir if c not in ya_informados]

    def _nueva(self, carpeta):
        videos = [p for p in carpeta.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONES_VIDEO]
        if len(videos) != 1:
            motivo = "no tiene video" if not videos else f"tiene {len(videos)} videos"
            self.informe.problemas.append((carpeta.name, motivo))
            return
        titulo, anio, imdb_id = parsear_carpeta(carpeta.name)
        archivo = self._leer_archivo(carpeta)
        video_path = f"{carpeta.name}/{videos[0].name}"
        # Una carpeta renombrada (o movida) se reconoce por su IMDb ID: el registro viejo la toma
        imdb_id = (archivo or {}).get("imdb_id") or imdb_id
        anterior = db.con_omdb_id(self.conn, imdb_id, self._presentes) if imdb_id else None
        if anterior is not None:
            viejo = self.conn.execute("SELECT folder_path FROM peliculas WHERE id = ?", (anterior,)).fetchone()[0]
            db.reasignar(self.conn, anterior, carpeta.name, video_path)
            self._reasignadas.add(anterior)
            self.informe.reasignadas.append((viejo, carpeta.name))
            poster.revisar(self.conn, self.biblioteca, anterior)
            return
        pelicula_id = db.insertar_pelicula(self.conn, titulo, anio, carpeta.name, video_path)
        self.informe.agregadas += 1
        poster.revisar(self.conn, self.biblioteca, pelicula_id)
        self._metadatos(pelicula_id, carpeta, videos[0].name, archivo)

    def _leer_archivo(self, carpeta):
        """pelis.json de la carpeta; si es inválido lo reporta y devuelve False (no se sobrescribe)."""
        try:
            return archivo_metadatos.leer(carpeta)
        except archivo_metadatos.ArchivoInvalido as e:
            self.informe.archivos_invalidos.append((carpeta.name, str(e)))
            return False

    def _metadatos(self, pelicula_id, carpeta, nombre_video=None, archivo=None):
        if nombre_video is None:
            fila = self.conn.execute("SELECT video_path FROM peliculas WHERE id = ?", (pelicula_id,)).fetchone()
            nombre_video = fila[0].rsplit("/", 1)[-1]

        if archivo is None:
            archivo = self._leer_archivo(carpeta)
        if archivo_metadatos.es_completo(archivo):
            # Sin título lo escribió una versión vieja del escaneo con el año de OMDb: no es una elección
            self._guardar(pelicula_id, carpeta, archivo, explicita=archivo.get("titulo") is not None)
            self.informe.desde_archivo.append(carpeta.name)
            return

        if self.omdb is None or self.omdb_caido:
            db.marcar_pendiente(self.conn, pelicula_id)
            self.informe.pendientes.append(carpeta.name)
            return
        try:
            datos = buscar_en_omdb(self.omdb, carpeta.name, nombre_video, (archivo or {}).get("imdb_id"))
        except ErrorRed as e:
            db.marcar_pendiente(self.conn, pelicula_id)
            self.informe.pendientes.append(carpeta.name)
            self.informe.aviso_omdb = f"OMDb no respondió ({e}); las que faltan quedan pendientes para el próximo escaneo."
            self.omdb_caido = True
            return
        if datos is None:
            db.marcar_no_encontrada(self.conn, pelicula_id)
            self.informe.no_encontradas.append(carpeta.name)
            return
        encontrados, aviso = metadatos.obtener(datos, None if self.tmdb_caido else self.tmdb, self.idiomas_sinopsis)
        if aviso:  # tras el primer error no se insiste
            self.tmdb_caido = True
            self.informe.aviso_tmdb = aviso
        self._guardar(pelicula_id, carpeta, encontrados, explicita=False, archivo_invalido=archivo is False)

    def _guardar(self, pelicula_id, carpeta, datos, explicita, archivo_invalido=False):
        aviso = metadatos.aplicar(self.conn, self.biblioteca, pelicula_id, datos, explicita)
        if aviso and not archivo_invalido:  # el inválido ya está en archivos_invalidos
            self.informe.archivos_sin_escribir.append((carpeta.name, aviso))
        self._bajar_poster(pelicula_id, carpeta, datos.get("poster_url"))

    def _bajar_poster(self, pelicula_id, carpeta, url):
        if url and self.omdb is not None and not self.omdb_caido and poster._actual(self.conn, pelicula_id) is None:
            destino = poster._carpeta_posters(carpeta)
            destino.mkdir(exist_ok=True)
            try:
                self.omdb.bajar_poster(url, destino / "poster.jpg")
            except ErrorRed:
                return
            poster._usar(self.conn, pelicula_id, f"{carpeta.name}/{destino.name}/poster.jpg", "omdb")


def escanear(conn, biblioteca, omdb, progreso=lambda actual, total, nombre: None, tmdb=None,
             idiomas_sinopsis=("es-MX", "es-ES")):
    return Escaneo(conn, biblioteca, omdb, progreso, tmdb, idiomas_sinopsis).ejecutar()


def importar_sin_red(conn, biblioteca):
    """Al abrir la app: suma las carpetas nuevas sin consultar internet.

    Las que traen pelis.json completo entran con todos sus datos; el resto queda pendiente de
    metadatos hasta el próximo escaneo. No marca faltantes: un disco desconectado no oculta nada.
    """
    return Escaneo(conn, biblioteca, None, marcar_faltantes=False).ejecutar()
