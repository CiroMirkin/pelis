import QtQuick
import QtQuick.Controls

// Botón de la app: el principal es la etiqueta naranja (uno por pantalla); el resto, contorno crema.
Button {
    id: boton
    property bool principal: false
    property string icono: ""
    property bool soloIcono: false
    // Secundario sin contorno (ej. la ✕ de descartar): solo se marca al pasar el mouse
    property bool sinBorde: false

    implicitHeight: Tema.px(38)
    leftPadding: soloIcono ? Tema.px(9) : Tema.px(14)
    rightPadding: soloIcono ? Tema.px(9) : Tema.px(16)
    focusPolicy: Qt.StrongFocus
    hoverEnabled: true

    Keys.onReturnPressed: clicked()
    Keys.onEnterPressed: clicked()

    contentItem: Row {
        spacing: Tema.px(8)
        Image {
            visible: boton.icono !== ""
            anchors.verticalCenter: parent.verticalCenter
            source: boton.icono ? "iconos/" + boton.icono + (boton.principal ? "-oscuro" : "") + ".svg" : ""
            sourceSize: Qt.size(Tema.px(18), Tema.px(18))
        }
        Text {
            visible: !boton.soloIcono
            anchors.verticalCenter: parent.verticalCenter
            text: boton.text
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(15)
            font.weight: Font.DemiBold
            font.capitalization: Font.AllUppercase
            font.letterSpacing: 0.6
            color: boton.principal ? Tema.sobreEtiqueta : Tema.crema
        }
    }

    background: Item {
        implicitHeight: Tema.px(38)

        // Foco: la caja se ilumina como bajo el tubo fluorescente
        Rectangle {
            visible: boton.visualFocus
            anchors.fill: parent
            anchors.margins: -Tema.px(4)
            radius: Tema.px(6)
            color: "transparent"
            border.width: Tema.px(3)
            border.color: Tema.tubo
        }
        Rectangle {
            anchors.fill: parent
            radius: Tema.px(3)
            color: boton.principal
                   ? (boton.down ? Qt.darker(Tema.etiqueta, 1.15) : Tema.etiqueta)
                   : (boton.down ? Tema.linea : boton.hovered ? Tema.caja : "transparent")
            border.width: boton.principal || boton.sinBorde ? 0 : 2
            border.color: Qt.alpha(Tema.crema, boton.enabled ? 0.55 : 0.2)
        }
    }
}
