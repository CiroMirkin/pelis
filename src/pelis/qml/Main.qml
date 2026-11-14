import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

ApplicationWindow {
    id: ventana
    width: 1280
    height: 800
    minimumWidth: 640
    minimumHeight: 480
    visible: true
    title: "Pelis"
    color: Tema.noche
    font.family: Tema.texto
    font.pixelSize: Tema.px(14)
    Material.theme: Material.Dark
    Material.accent: Tema.etiqueta
    Material.background: Tema.estante
    Material.foreground: Tema.crema

    // Lo prende __main__.py cuando el puente está listo: antes de eso `puente` no existe
    property bool listo: false
    onListoChanged: pila.push(puente.hayBiblioteca ? "Catalogo.qml" : "SinBiblioteca.qml", {}, StackView.Immediate)

    // Corre en el hilo de render, así sigue girando mientras se carga lo pesado
    BusyIndicator {
        anchors.centerIn: parent
        implicitWidth: Tema.px(56)
        implicitHeight: Tema.px(56)
        running: !ventana.listo
        visible: running
    }

    StackView {
        id: pila
        objectName: "pila"
        anchors.fill: parent
    }
}
