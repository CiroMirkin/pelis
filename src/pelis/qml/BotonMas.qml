import QtQuick
import QtQuick.Controls

// Botón «…» que despliega un menú de opciones secundarias (OpcionMenu)
Boton {
    id: mas
    default property alias opciones: menu.contentData
    property bool alinearDerecha: false
    // Punto rojo en la esquina porque hay algo pendiente dentro del menú
    property bool avisar: false

    icono: "mas"
    soloIcono: true
    text: "Más opciones"
    Accessible.name: text
    onClicked: menu.visible ? menu.close() : menu.open()
    Keys.onDownPressed: menu.open()

    Rectangle {
        visible: mas.avisar
        width: Tema.px(10); height: width; radius: width / 2
        x: mas.width - width - Tema.px(5); y: Tema.px(5)
        color: Tema.etiqueta
        border.width: 2; border.color: Tema.noche
    }

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
