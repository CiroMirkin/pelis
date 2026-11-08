from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QJSEngine

FUENTE = (Path(__file__).parents[1] / "src/pelis/qml/navegacion.js").read_text().replace(".pragma library", "")

# Pila falsa con la misma forma que StackView: depth, get, push, pop(hasta) y replace(cual, url, props)
PILA = """
function Pila(pantallas) {
    this.pantallas = pantallas
    Object.defineProperty(this, "depth", { get: () => this.pantallas.length })
    this.get = (i) => this.pantallas[i]
    this.push = (url, props) => { const p = Object.assign({ url: url, objectName: url === "Persona.qml" ? "persona" : "" }, props); this.pantallas.push(p); return p }
    this.pop = (hasta) => { this.pantallas.length = this.pantallas.indexOf(hasta) + 1 }
    this.replace = (cual, url, props) => { this.pantallas.length = this.pantallas.indexOf(cual); return this.push(url, props) }
    this.ruta = () => this.pantallas.map(p => p.nombre || p.peliculaId || p.url).join(" > ")
}
const catalogo = { url: "Catalogo.qml" }
const pelicula = (id) => ({ url: "Detalle.qml", peliculaId: id, objectName: "" })
const persona = (nombre) => ({ url: "Persona.qml", nombre: nombre, objectName: "persona" })
"""


def ruta(guion):
    QCoreApplication.instance() or QCoreApplication([])
    motor = QJSEngine()
    resultado = motor.evaluate(FUENTE + PILA + guion)
    assert not resultado.isError(), resultado.toString()
    return resultado.toString()


def test_abrir_otra_vez_la_misma_persona_vuelve_a_ella_sin_la_pelicula_intermedia():
    assert ruta("""
        const pila = new Pila([catalogo, pelicula(1), persona("Ridley Scott"), pelicula(2)])
        abrirPersona(pila, "Ridley Scott")
        pila.ruta()
    """) == "Catalogo.qml > 1 > Ridley Scott"


def test_otra_persona_reemplaza_a_la_del_segundo_nivel():
    assert ruta("""
        const pila = new Pila([catalogo, pelicula(1), persona("Ridley Scott"), pelicula(2)])
        abrirPersona(pila, "Sigourney Weaver")
        pila.ruta()
    """) == "Catalogo.qml > 1 > Sigourney Weaver"


def test_la_primera_persona_se_apila_sobre_la_pelicula():
    assert ruta("""
        const pila = new Pila([catalogo, pelicula(1)])
        abrirPersona(pila, "Ridley Scott")
        pila.ruta()
    """) == "Catalogo.qml > 1 > Ridley Scott"


def test_no_pisa_una_pantalla_ajena_que_quedo_en_el_segundo_nivel():
    assert ruta("""
        const pila = new Pila([catalogo, pelicula(1), { url: "Editar.qml", objectName: "" }])
        abrirPersona(pila, "Ridley Scott")
        pila.ruta()
    """) == "Catalogo.qml > 1 > Editar.qml > Ridley Scott"
