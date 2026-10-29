import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import zipfile
from pathlib import Path

import pytest
import requests

from pelis import actualizacion


@pytest.mark.parametrize("tag, actual, esperado", [
    ("v0.2.0", "0.1.0", True),
    ("v0.1.0", "0.1.0", False),
    ("v0.1.0", "0.2.0", False),
    ("v0.10.0", "0.9.0", True),     # numérico, no alfabético
    ("v0.2.0", "0.2.0-rc2", True),  # la final le gana a su RC
    ("v0.2.0-rc1", "0.2.0", False),
    ("v0.2.0-rc2", "0.2.0-rc1", True),
    ("v0.2.0-rc1", "0.1.5", True),
    ("nightly", "0.1.0", False),
    ("v0.2.0", "dev", False),
])
def test_es_mas_nueva(tag, actual, esperado):
    assert actualizacion.es_mas_nueva(tag, actual) is esperado


class Respuesta:
    def __init__(self, status_code=200, datos=None, error=None):
        self.status_code = status_code
        self.datos = datos
        self.error = error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        if self.error:
            raise self.error
        return self.datos


class Sesion:
    def __init__(self, respuesta=None, error=None):
        self.respuesta = respuesta
        self.error = error
        self.urls = []

    def get(self, url, **_):
        self.urls.append(url)
        if self.error:
            raise self.error
        return self.respuesta


RELEASE = {
    "tag_name": "v0.3.0",
    "body": "## Nuevo\n\n- Buscar actualización",
    "assets": [
        {"name": "Pelis-windows-v0.3.0.zip", "browser_download_url": "https://x/win.zip"},
        {"name": "SHA256SUMS", "browser_download_url": "https://x/SHA256SUMS"},
    ],
}


def test_hay_version_nueva():
    sesion = Sesion(Respuesta(datos=RELEASE))
    assert actualizacion.buscar(sesion, actual="0.2.0") == {
        "version": "0.3.0",
        "notas": "## Nuevo\n\n- Buscar actualización",
        "paquetes": {"Pelis-windows-v0.3.0.zip": "https://x/win.zip", "SHA256SUMS": "https://x/SHA256SUMS"},
    }
    assert sesion.urls == [actualizacion.API]


def test_al_dia():
    assert actualizacion.buscar(Sesion(Respuesta(datos=RELEASE)), actual="0.3.0") is None


def test_sin_releases_es_al_dia():
    assert actualizacion.buscar(Sesion(Respuesta(status_code=404)), actual="0.1.0") is None


@pytest.mark.parametrize("sesion", [
    Sesion(error=requests.ConnectionError("sin red")),
    Sesion(error=requests.Timeout("timeout")),
    Sesion(Respuesta(status_code=503)),
    Sesion(Respuesta(error=ValueError("no es JSON"))),
    Sesion(Respuesta(datos={"message": "API rate limit exceeded"})),
])
def test_sin_conexion_o_respuesta_rara(sesion):
    with pytest.raises(actualizacion.ErrorRed):
        actualizacion.buscar(sesion, actual="0.1.0")


# --- instalar ---

RAIZ_REPO = Path(__file__).resolve().parent.parent


def _paquete(inst, version, ejecutable=b"#!/bin/sh\n"):
    """Bytes del paquete de `inst.sistema` con el formato del workflow (lo que va en la raíz del disco)."""
    archivos = {
        f"pelis-app/app/{inst.sistema}/{inst.ejecutable}": ejecutable,
        f"pelis-app/app/{inst.sistema}/_internal/version.txt": version.encode(),
        "pelis-app/app/pelis.toml.ejemplo": b"biblioteca = \"\"\n",
        inst.lanzador: (RAIZ_REPO / "tools" / inst.lanzador).read_bytes(),
    }
    buffer = io.BytesIO()
    if inst.windows:
        with zipfile.ZipFile(buffer, "w") as z:
            for nombre, datos in archivos.items():
                z.writestr(nombre, datos)
    else:
        with tarfile.open(fileobj=buffer, mode="w:gz") as t:
            for nombre, datos in archivos.items():
                info = tarfile.TarInfo(nombre)
                info.size = len(datos)
                info.mode = 0o755
                t.addfile(info, io.BytesIO(datos))
    return buffer.getvalue()


class Descarga:
    def __init__(self, datos, corte=None):
        self.datos = datos
        self.corte = corte  # excepción a mitad de la descarga
        self.headers = {"Content-Length": str(len(datos))}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def raise_for_status(self):
        pass

    def iter_content(self, tamanio):
        for i in range(0, len(self.datos), tamanio):
            if self.corte and i > 0:
                raise self.corte
            yield self.datos[i:i + tamanio]


class Servidor:
    """Sesión falsa que sirve los archivos de una Release."""

    def __init__(self, archivos, corte=None):
        self.archivos = archivos
        self.corte = corte

    def get(self, url, **_):
        nombre = url.rsplit("/", 1)[1]
        return Descarga(self.archivos[nombre], self.corte if nombre != "SHA256SUMS" else None)


def _release(inst, version, datos=None, sumas=None):
    datos = _paquete(inst, version) if datos is None else datos
    nombre = inst.paquete(version)
    sumas = sumas or f"{hashlib.sha256(datos).hexdigest()}  {nombre}\n"
    nueva = {"version": version, "notas": "", "paquetes": {n: f"https://x/{n}" for n in (nombre, "SHA256SUMS")}}
    return nueva, {nombre: datos, "SHA256SUMS": sumas.encode()}


def _instalacion(raiz, sistema="linux", version="0.1.0"):
    """Disco instalado: raiz/pelis.sh y raiz/pelis-app/app/<sistema>/ con la configuración del usuario."""
    inst = actualizacion.Instalacion(raiz / "pelis-app" / "app" / sistema)
    inst.programa.mkdir(parents=True)
    (inst.programa / "_internal").mkdir()
    (inst.programa / "_internal" / "version.txt").write_text(version)
    for nombre in ("pelis.toml", "pelis.db", "preferencias.ini"):
        (inst.app / nombre).write_text(f"del usuario: {nombre}")
    return inst


@pytest.mark.parametrize("sistema", ["linux", "win"])
def test_preparar_baja_verifica_y_extrae(tmp_path, sistema):
    inst = _instalacion(tmp_path, sistema)
    nueva, archivos = _release(inst, "0.2.0")
    avance = []
    nuevo = actualizacion.preparar(inst, nueva, Servidor(archivos), progreso=avance.append)
    assert (nuevo / "pelis-app" / "app" / sistema / "_internal" / "version.txt").read_text() == "0.2.0"
    assert (nuevo / inst.lanzador).is_file()
    assert avance and avance[-1] == 1.0
    assert (inst.programa / "_internal" / "version.txt").read_text() == "0.1.0"  # no tocó la instalación
    if sistema == "linux":
        assert os.access(nuevo / "pelis-app" / "app" / "linux" / "pelis", os.X_OK)


def test_hash_distinto_aborta_sin_tocar_nada(tmp_path):
    inst = _instalacion(tmp_path)
    nueva, archivos = _release(inst, "0.2.0", sumas=f"{'0' * 64}  Pelis-linux-v0.2.0.tar.gz\n")
    with pytest.raises(actualizacion.ErrorActualizacion, match="dañada"):
        actualizacion.preparar(inst, nueva, Servidor(archivos))
    assert not inst.descarga.exists()
    assert (inst.programa / "_internal" / "version.txt").read_text() == "0.1.0"


def test_corte_de_red_a_mitad_deja_todo_como_estaba(tmp_path):
    inst = _instalacion(tmp_path)
    nueva, archivos = _release(inst, "0.2.0", datos=os.urandom(300_000))
    with pytest.raises(actualizacion.ErrorRed):
        actualizacion.preparar(inst, nueva, Servidor(archivos, corte=requests.ConnectionError("se cortó")))
    assert not inst.descarga.exists()


def test_cancelar_borra_la_descarga(tmp_path):
    inst = _instalacion(tmp_path)
    nueva, archivos = _release(inst, "0.2.0", datos=os.urandom(300_000))
    with pytest.raises(actualizacion.Cancelado):
        actualizacion.preparar(inst, nueva, Servidor(archivos), cancelado=lambda: True)
    assert not inst.descarga.exists()


def test_release_sin_paquete_del_sistema(tmp_path):
    inst = _instalacion(tmp_path, "win")
    nueva = {"version": "0.2.0", "notas": "", "paquetes": {"Pelis-linux-v0.2.0.tar.gz": "u", "SHA256SUMS": "u"}}
    with pytest.raises(actualizacion.ErrorActualizacion, match="no trae"):
        actualizacion.preparar(inst, nueva, Servidor({}))


def test_paquete_con_otro_formato(tmp_path):
    inst = _instalacion(tmp_path)
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as t:
        info = tarfile.TarInfo("otra-cosa.txt")
        t.addfile(info, io.BytesIO(b""))
    nueva, archivos = _release(inst, "0.2.0", datos=buffer.getvalue())
    with pytest.raises(actualizacion.ErrorActualizacion, match="formato"):
        actualizacion.preparar(inst, nueva, Servidor(archivos))
    assert not inst.descarga.exists()


def test_leer_sumas():
    assert actualizacion.leer_sumas("ABC  a.zip\ndef *b.tar.gz\n\nbasura\n") == {"a.zip": "abc", "b.tar.gz": "def"}


def test_terminar_borra_anterior_y_testigo(tmp_path):
    inst = _instalacion(tmp_path)
    inst.anterior.mkdir()
    inst.testigo.touch()
    actualizacion.terminar(inst)
    assert not inst.anterior.exists() and not inst.testigo.exists()


def test_terminar_sin_testigo_no_toca_nada(tmp_path):
    inst = _instalacion(tmp_path)
    inst.anterior.mkdir()  # p. ej. de otra cosa: sin testigo no se borra
    actualizacion.terminar(inst)
    assert inst.anterior.exists()


def _esperar(condicion, segundos=10):
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        if condicion():
            return True
        time.sleep(0.05)
    return False


@pytest.mark.skipif(sys.platform == "win32", reason="corre el script de Linux")
def test_script_linux_cambia_la_version_y_la_vuelve_a_abrir(tmp_path):
    inst = _instalacion(tmp_path)
    # El "programa" nuevo deja constancia de que arrancó y con qué argumentos
    arranco = tmp_path / "arranco.txt"
    ejecutable = f'#!/bin/sh\necho "$@" > {arranco}\n'.encode()
    nueva, archivos = _release(inst, "0.2.0", datos=_paquete(inst, "0.2.0", ejecutable))
    nuevo = actualizacion.preparar(inst, nueva, Servidor(archivos))
    viejo = subprocess.Popen(["sleep", "0.5"])  # la app que todavía está cerrándose
    # Se recoge en paralelo, como hace su padre real: si no, queda zombi y kill -0 la sigue viendo
    threading.Thread(target=viejo.wait, daemon=True).start()
    script = actualizacion.escribir_script(inst, nuevo, viejo.pid, ["--prerelease", "con espacio"])
    subprocess.run(["/bin/sh", str(script)], check=True, timeout=20)

    assert _esperar(arranco.exists)
    assert arranco.read_text().strip() == "--prerelease con espacio"
    assert (inst.programa / "_internal" / "version.txt").read_text() == "0.2.0"
    assert (inst.anterior / "_internal" / "version.txt").read_text() == "0.1.0"
    assert inst.testigo.exists()
    assert (inst.raiz / "pelis.sh").is_file() and (inst.app / "pelis.toml.ejemplo").is_file()
    for nombre in ("pelis.toml", "pelis.db", "preferencias.ini"):
        assert (inst.app / nombre).read_text() == f"del usuario: {nombre}"
    assert not inst.descarga.exists() and not script.exists()


@pytest.mark.skipif(sys.platform == "win32", reason="corre el lanzador de Linux")
def test_lanzador_linux_restaura_si_la_nueva_no_arranco(tmp_path):
    inst = _instalacion(tmp_path)
    shutil.copy(RAIZ_REPO / "tools" / "pelis.sh", inst.raiz / "pelis.sh")
    # Quedó como después del cambio: la nueva en linux/, la vieja en linux.anterior/ y el testigo
    inst.programa.rename(inst.anterior)
    inst.programa.mkdir()
    (inst.programa / "pelis").write_text("#!/bin/sh\nexit 1\n")
    (inst.anterior / "pelis").write_text("#!/bin/sh\necho vieja\n")
    (inst.anterior / "pelis").chmod(0o755)
    inst.testigo.touch()

    r = subprocess.run(["bash", str(inst.raiz / "pelis.sh")], capture_output=True, text=True, timeout=10)
    assert r.stdout.strip() == "vieja"
    assert (inst.programa / "_internal" / "version.txt").read_text() == "0.1.0"
    assert not inst.anterior.exists() and not inst.testigo.exists()


def test_script_windows_lleva_rutas_y_argumentos(tmp_path):
    inst = _instalacion(tmp_path, "win")
    script = actualizacion.escribir_script(inst, inst.descarga / "nuevo", 4321, ["--prerelease"])
    texto = script.read_bytes().decode("utf-8")
    assert script.name == "actualizar-win.bat"
    assert "\r\n" in texto and "\n" not in texto.replace("\r\n", "")
    assert 'set "PID=4321"' in texto
    assert f'set "APP={inst.app}"' in texto
    assert f'start "" "%APP%\\win\\pelis.exe" "--prerelease"' in texto


TODAS = [
    {"tag_name": "v0.2.0", "draft": False, "body": "final", "assets": []},
    {"tag_name": "v0.3.0-rc2", "draft": False, "body": "rc2", "assets": []},
    {"tag_name": "v0.3.0-rc1", "draft": False, "body": "rc1", "assets": []},
    {"tag_name": "v0.4.0", "draft": True, "body": "borrador", "assets": []},
]


def test_con_prerelease_toma_la_mas_nueva_rc_incluidas():
    sesion = Sesion(Respuesta(datos=TODAS))
    assert actualizacion.buscar(sesion, actual="0.2.0", prerelease=True)["version"] == "0.3.0-rc2"
    assert sesion.urls == [actualizacion.API_TODAS]


def test_con_prerelease_al_dia_y_sin_releases():
    assert actualizacion.buscar(Sesion(Respuesta(datos=TODAS)), actual="0.3.0-rc2", prerelease=True) is None
    assert actualizacion.buscar(Sesion(Respuesta(datos=[])), actual="0.1.0", prerelease=True) is None


def test_desde_una_rc_se_actualiza_a_su_final():
    final = {"tag_name": "v0.3.0", "body": "", "assets": []}
    assert actualizacion.buscar(Sesion(Respuesta(datos=final)), actual="0.3.0-rc2")["version"] == "0.3.0"
