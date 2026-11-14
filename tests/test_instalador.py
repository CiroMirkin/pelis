import hashlib
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import requests
from test_actualizacion import Servidor, _esperar

from pelis import actualizacion, instalador


def _release_instalador(version, windows, datos=b"instalador", sumas=None):
    nombre = instalador.nombre_instalador(version, windows)
    sumas = sumas if sumas is not None else f"{hashlib.sha256(datos).hexdigest()}  {nombre}\n"
    nueva = {"version": version, "notas": "", "paquetes": {n: f"https://x/{n}" for n in (nombre, "SHA256SUMS")}}
    return nueva, {nombre: datos, "SHA256SUMS": sumas.encode()}


@pytest.fixture
def temporal(tmp_path, monkeypatch):
    """La carpeta donde el instalador deja la descarga: tiene que quedar vacía si algo sale mal."""
    carpeta = tmp_path / "temporal"
    carpeta.mkdir()
    monkeypatch.setattr(instalador.tempfile, "tempdir", str(carpeta))
    return carpeta


def _con_pkexec_en_el_path(monkeypatch, tmp_path, hay):
    bin_falso = tmp_path / "bin-pkexec"
    bin_falso.mkdir()
    if hay:
        (bin_falso / "pkexec").write_text("#!/bin/sh\n")
        (bin_falso / "pkexec").chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_falso))


@pytest.fixture
def con_pkexec(monkeypatch, tmp_path):
    _con_pkexec_en_el_path(monkeypatch, tmp_path, hay=True)


@pytest.mark.parametrize("windows, nombre", [(True, "Pelis-windows-v0.2.0-setup.exe"), (False, "Pelis-linux-v0.2.0.deb")])
def test_descarga_el_instalador_de_su_sistema_y_verifica_el_hash(con_pkexec, windows, nombre):
    nueva, archivos = _release_instalador("0.2.0", windows)
    avance = []
    archivo = instalador.preparar_instalador(nueva, Servidor(archivos), progreso=avance.append, windows=windows)
    try:
        assert archivo.name == nombre and archivo.read_bytes() == b"instalador"
        assert avance and avance[-1] == 1.0
    finally:
        shutil.rmtree(archivo.parent)


def test_rechaza_un_instalador_danado_y_no_deja_archivos(con_pkexec, temporal):
    nueva, archivos = _release_instalador("0.2.0", False, sumas=f"{'0' * 64}  Pelis-linux-v0.2.0.deb\n")
    with pytest.raises(actualizacion.ErrorActualizacion, match="dañada"):
        instalador.preparar_instalador(nueva, Servidor(archivos), windows=False)
    assert list(temporal.iterdir()) == []


def test_rechaza_un_instalador_que_sha256sums_no_menciona(con_pkexec, temporal):
    nueva, archivos = _release_instalador("0.2.0", False, sumas=f"{'a' * 64}  otro-archivo.deb\n")
    with pytest.raises(actualizacion.ErrorActualizacion, match="dañada"):
        instalador.preparar_instalador(nueva, Servidor(archivos), windows=False)
    assert list(temporal.iterdir()) == []


def test_cancelar_o_cortar_la_descarga_no_deja_archivos(con_pkexec, temporal):
    nueva, archivos = _release_instalador("0.2.0", False, datos=os.urandom(300_000))
    with pytest.raises(actualizacion.Cancelado):
        instalador.preparar_instalador(nueva, Servidor(archivos), cancelado=lambda: True, windows=False)
    with pytest.raises(actualizacion.ErrorRed):
        instalador.preparar_instalador(nueva, Servidor(archivos, corte=requests.ConnectionError("x")), windows=False)
    assert list(temporal.iterdir()) == []


def test_avisa_si_la_release_no_trae_el_instalador(con_pkexec):
    nueva = {"version": "0.2.0", "notas": "", "paquetes": {"SHA256SUMS": "u"}}
    with pytest.raises(actualizacion.ErrorActualizacion, match="no trae"):
        instalador.preparar_instalador(nueva, Servidor({}), windows=False)


def test_avisa_el_comando_a_mano_si_falta_pkexec(monkeypatch, tmp_path):
    _con_pkexec_en_el_path(monkeypatch, tmp_path, hay=False)
    nueva, archivos = _release_instalador("0.2.0", False)
    with pytest.raises(actualizacion.ErrorActualizacion, match="sudo apt install ./Pelis-linux-v0.2.0.deb"):
        instalador.preparar_instalador(nueva, Servidor(archivos), windows=False)


def test_instala_en_silencio_y_reabre_la_app_con_los_mismos_argumentos(tmp_path):
    archivo = tmp_path / "Pelis-windows-v0.2.0-setup.exe"
    script = instalador.escribir_script_instalador(archivo, 4321, ["--prerelease"],
                                                   exe=Path(r"C:\Pelis\pelis.exe"), windows=True)
    texto = script.read_bytes().decode("utf-8")
    assert script.name == "actualizar.bat" and "\r\n" in texto
    assert 'set "PID=4321"' in texto
    linea = next(l for l in texto.splitlines() if str(archivo) in l)
    for flag in ("/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"):
        assert flag in linea.split()
    assert 'start "" "C:\\Pelis\\pelis.exe" "--prerelease"' in texto


def _correr_script_linux(tmp_path, pkexec_sale_con):
    """Corre el script con pkexec, apt-get y la app falsos, que anotan lo que pasa en registro.txt."""
    bin_falso = tmp_path / "bin"
    bin_falso.mkdir()
    registro = tmp_path / "registro.txt"
    viejo = subprocess.Popen(["sleep", "0.5"])  # la app que todavía está cerrándose
    threading.Thread(target=viejo.wait, daemon=True).start()
    # pkexec corre lo que le pasan, salvo que el usuario cancele (126)
    pkexec = bin_falso / "pkexec"
    pkexec.write_text(f'#!/bin/sh\n[ {pkexec_sale_con} = 0 ] || exit {pkexec_sale_con}\nexec "$@"\n')
    apt = bin_falso / "apt-get"
    apt.write_text(f'#!/bin/sh\nkill -0 {viejo.pid} 2>/dev/null && echo "apt con app abierta" >> {registro}\n'
                   f'echo "apt $@" >> {registro}\n')
    exe = tmp_path / "pelis"
    exe.write_text(f'#!/bin/sh\necho "abrio $@" >> {registro}\n')
    for f in (pkexec, apt, exe):
        f.chmod(0o755)
    carpeta = tmp_path / "descarga"
    carpeta.mkdir()
    archivo = carpeta / "Pelis-linux-v0.2.0.deb"
    archivo.write_bytes(b"deb")
    script = instalador.escribir_script_instalador(archivo, viejo.pid, ["--prerelease"], exe=exe, windows=False)
    entorno = {**os.environ, "PATH": f"{bin_falso}:{os.environ['PATH']}"}
    subprocess.run(["/bin/sh", str(script)], check=True, timeout=20, env=entorno)
    assert _esperar(lambda: "abrio" in (registro.read_text() if registro.exists() else ""))
    return registro.read_text().splitlines(), archivo, carpeta


@pytest.mark.skipif(sys.platform == "win32", reason="corre el script de Linux")
def test_instala_el_paquete_con_permisos_de_administrador_cuando_la_app_ya_cerro(tmp_path):
    lineas, archivo, carpeta = _correr_script_linux(tmp_path, pkexec_sale_con=0)
    assert lineas == [f"apt install -y {archivo}", "abrio --prerelease"]
    assert _esperar(lambda: not carpeta.exists())


@pytest.mark.skipif(sys.platform == "win32", reason="corre el script de Linux")
def test_no_instala_si_se_cancela_la_contrasena_y_abre_la_app_igual(tmp_path):
    lineas, _, carpeta = _correr_script_linux(tmp_path, pkexec_sale_con=126)
    assert lineas == ["abrio --prerelease"]
    assert _esperar(lambda: not carpeta.exists())
