import QtQuick
import QtQuick.Controls

// Botón «…» que despliega un menú de opciones secundarias (OpcionMenu)
Boton {
    id: mas
    default property alias opciones: menu.contentData
    property bool alinearDerecha: false

    icono: "mas"
    soloIcono: true
    text: "Más opciones"
    Accessible.name: text
    onClicked: menu.visible ? menu.close() : menu.open()
    Keys.onDownPressed: menu.open()

    Menu {
        id: menu
        x: mas.alinearDerecha ? mas.width - width : 0
        y: mas.height + Tema.px(6)
        padding: Tema.px(6)
        onClosed: mas.forceActiveFocus()
        background: Rectangle {
            implicitWidth: Tema.px(260)
            color: Tema.estante
            radius: Tema.px(4)
            border.width: 1
            border.color: Tema.linea
        }
    }
}
