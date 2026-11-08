pragma Singleton
import QtQuick

// Los colores y cuándo usar cada uno están en DESIGN.md y hay que cambiar los dos archivos juntos.
// Los nombres (noche, crema, etiqueta…) vienen de la paleta anterior y se mantienen aunque ya no describan el color.
QtObject {
    // Escala general de tamaños (1 = escritorio); queda para un futuro modo TV
    property real escala: 1

    readonly property color noche: "#0b0b0b"
    readonly property color estante: "#1b1d1c"
    readonly property color caja: "#242625"
    readonly property color linea: "#303231"
    readonly property color crema: "#f4f4f2"
    readonly property color tenue: "#8e908f"
    readonly property color etiqueta: "#fd3a04"
    readonly property color sobreEtiqueta: "#0b0b0b"
    readonly property color tubo: "#ffffff"
    readonly property color alerta: "#ff9a7a"

    readonly property FontLoader _atkinson: FontLoader { source: "fuentes/AtkinsonHyperlegible-Regular.ttf" }
    readonly property FontLoader _atkinsonNegrita: FontLoader { source: "fuentes/AtkinsonHyperlegible-Bold.ttf" }
    readonly property FontLoader _archivo: FontLoader { source: "fuentes/ArchivoNarrow.ttf" }
    readonly property string texto: _atkinson.name
    readonly property string rotulo: _archivo.name

    function px(n) { return Math.round(n * escala) }
}
