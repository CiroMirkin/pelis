import QtQuick
import QtQuick.Controls

// Opción de un BotonMas: ícono (opcional) y texto en rótulo
MenuItem {
    id: opcion
    property string icono: ""
    implicitHeight: visible ? Tema.px(40) : 0
    leftPadding: Tema.px(12)
    rightPadding: Tema.px(16)
    contentItem: Row {
        spacing: Tema.px(10)
        Image {
            anchors.verticalCenter: parent.verticalCenter
            source: opcion.icono ? "iconos/" + opcion.icono + ".svg" : ""
            width: Tema.px(18)
            sourceSize: Qt.size(Tema.px(18), Tema.px(18))
        }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: opcion.text
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(16)
            font.letterSpacing: 0.3
            color: Tema.crema
        }
    }
    background: Rectangle {
        radius: Tema.px(3)
        color: opcion.highlighted || opcion.down ? Tema.caja : "transparent"
    }
}
