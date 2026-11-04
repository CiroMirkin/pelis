import QtQuick

// Pantalla completa de la ventana. No toma el foco: alternarla no se lo saca a la grilla ni al buscador.
Boton {
    readonly property bool completa: Window.window && Window.window.visibility === Window.FullScreen

    function alternar() {
        Window.window.visibility = completa ? Window.Windowed : Window.FullScreen
    }

    soloIcono: true
    icono: completa ? "ventana" : "pantalla"
    text: completa ? "Salir de pantalla completa" : "Pantalla completa"
    Accessible.name: text
    focusPolicy: Qt.NoFocus
    onClicked: alternar()
}
