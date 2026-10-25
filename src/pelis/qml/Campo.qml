import QtQuick
import QtQuick.Controls.Basic as Basic

// Campo de texto de la app, con el mismo estilo que el buscador del catálogo
Basic.TextField {
    id: campo
    placeholderTextColor: Tema.tenue
    color: Tema.crema
    selectionColor: Tema.etiqueta
    selectedTextColor: Tema.sobreEtiqueta
    font.family: Tema.texto
    font.pixelSize: Tema.px(15)
    leftPadding: Tema.px(14)
    rightPadding: Tema.px(14)
    verticalAlignment: TextInput.AlignVCenter
    background: Rectangle {
        implicitHeight: Tema.px(38)
        radius: Tema.px(3)
        color: campo.activeFocus ? Tema.caja : "transparent"
        border.width: campo.activeFocus ? Tema.px(2) : 1
        border.color: campo.activeFocus ? Tema.tubo : Qt.alpha(Tema.crema, 0.35)
    }
}
