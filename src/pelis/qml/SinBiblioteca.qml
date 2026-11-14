import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Pantalla de arranque cuando no hay biblioteca guardada o la carpeta no está (ej. el disco no está montado)
Page {
    id: pagina
    background: Rectangle { color: Tema.noche }
    Component.onCompleted: elegir.forceActiveFocus()

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(Tema.px(560), parent.width - 48)
        spacing: Tema.px(18)
        Text {
            Layout.fillWidth: true
            text: puente.rutaBiblioteca ? "No encuentro la biblioteca" : "Elegí la carpeta de tus películas"
            wrapMode: Text.WordWrap
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(26)
            font.weight: Font.Bold
            color: Tema.crema
        }
        Text {
            Layout.fillWidth: true
            visible: puente.rutaBiblioteca !== ""
            text: "Busqué en " + puente.rutaBiblioteca + ". Si está en un disco, revisá que esté conectado."
            wrapMode: Text.WrapAnywhere
            lineHeight: 1.3
            font.family: Tema.texto
            font.pixelSize: Tema.px(15)
            color: Tema.tenue
        }
        Boton {
            id: elegir
            principal: true
            text: "Elegir carpeta…"
            onClicked: selector.iniciar()
        }
    }

    ElegirBiblioteca {
        id: selector
        onCambiada: pagina.StackView.view.replace("Catalogo.qml", {escanearAlEntrar: true}, StackView.Immediate)
        onCerrado: elegir.forceActiveFocus()
    }
}
