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

    StackView {
        id: pila
        objectName: "pila"
        anchors.fill: parent
        initialItem: "Catalogo.qml"
    }

    // Cerrar la app con el reproductor abierto también guarda el progreso
    onClosing: {
        if (pila.currentItem && pila.currentItem.guardarProgreso)
            pila.currentItem.guardarProgreso()
    }
}
