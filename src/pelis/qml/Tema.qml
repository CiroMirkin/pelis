pragma Singleton
import QtQuick

// Videoclub de barrio, minimal: azul de local cerrado, crema de etiqueta y un solo rojo de etiqueta de alquiler.
QtObject {
    // Escala general de tamaños (1 = escritorio); queda para un futuro modo TV
    property real escala: 1

    readonly property color noche: "#0e131c"
    readonly property color estante: "#161d2a"
    readonly property color caja: "#1d2636"
    readonly property color linea: "#2a3548"
    readonly property color crema: "#f1ebde"
    readonly property color tenue: "#9aa6bb"
    readonly property color etiqueta: "#e0453a"
    readonly property color sobreEtiqueta: "#0e131c"
    readonly property color tubo: "#dfeaff"
    readonly property color alerta: "#ff9a7a"

    readonly property FontLoader _atkinson: FontLoader { source: "fuentes/AtkinsonHyperlegible-Regular.ttf" }
    readonly property FontLoader _atkinsonNegrita: FontLoader { source: "fuentes/AtkinsonHyperlegible-Bold.ttf" }
    readonly property FontLoader _archivo: FontLoader { source: "fuentes/ArchivoNarrow.ttf" }
    readonly property string texto: _atkinson.name
    readonly property string rotulo: _archivo.name

    function px(n) { return Math.round(n * escala) }
}
