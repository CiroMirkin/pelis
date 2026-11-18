from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QJSEngine

FUENTE = (Path(__file__).parents[1] / "src/pelis/qml/desplazamiento.js").read_text().replace(".pragma library", "")
QML = Path(__file__).parents[1] / "src/pelis/qml"


def destino(contentY, y):
    # Vista de 600 con filas de 300, halo de 6, rango de scroll de -28 a 1000
    QCoreApplication.instance() or QCoreApplication([])
    resultado = QJSEngine().evaluate(FUENTE + f"contentYParaVer({contentY}, 600, {y}, 300, 6, -28, 1000)")
    assert not resultado.isError(), resultado.toString()
    return resultado.toNumber()


def test_fila_visible_no_mueve_la_vista():
    assert destino(-28, 0) == -28
    assert destino(10, 300) == 10


def test_fila_que_sale_por_abajo_baja_la_vista_hasta_mostrarla_con_su_halo():
    assert destino(-28, 600) == 600 + 300 + 6 - 600


def test_fila_que_sale_por_arriba_sube_la_vista_con_el_halo():
    assert destino(900, 300) == 300 - 6


def test_no_se_pasa_del_rango_de_scroll():
    assert destino(0, 5000) == 1000
    assert destino(900, -500) == -28


def test_catalogo_y_persona_siguen_el_foco_pero_no_el_mouse():
    for nombre in ("Catalogo", "Persona"):
        fuente = (QML / f"{nombre}.qml").read_text()
        assert "contentYParaVer" in fuente, nombre
        assert "grilla.porMouse = true" in fuente, nombre
