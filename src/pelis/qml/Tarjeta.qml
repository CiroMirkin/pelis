import QtQuick

// Tarjeta de película: caja 2:3 con poster (o el título si no hay imagen), progreso y etiqueta de vista; debajo, título y año
Column {
    id: tarjeta
    property string titulo
    property int anio
    property string poster
    property real progreso
    property bool vista
    property bool encendida  // halo del foco
    spacing: Tema.px(6)

    Item {
        width: parent.width
        height: Math.round(width * 1.5)

        // Halo del tubo fluorescente sobre la caja elegida
        Rectangle {
            anchors.fill: caja
            anchors.margins: -Tema.px(6)
            radius: Tema.px(6)
            color: "transparent"
            border.width: Tema.px(3)
            border.color: Tema.tubo
            opacity: tarjeta.encendida ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
        }

        Rectangle {
            id: caja
            anchors.fill: parent
            radius: Tema.px(2)
            color: Tema.caja
            clip: true

            Text {
                visible: imagen.status !== Image.Ready
                anchors.fill: parent
                anchors.margins: Tema.px(14)
                text: tarjeta.titulo
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignBottom
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(20)
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
                color: Tema.tenue
            }
            Image {
                id: imagen
                anchors.fill: parent
                source: tarjeta.poster
                fillMode: Image.PreserveAspectCrop
                asynchronous: true
                sourceSize.width: 400
            }
            // Progreso: largo exacto de lo visto, sin mínimos
            Rectangle {
                visible: tarjeta.progreso > 0
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                width: parent.width * Math.min(1, tarjeta.progreso)
                height: Tema.px(6)
                color: Tema.etiqueta
            }
        }

        // Vista: sticker pegado sobre la caja
        EtiquetaVista {
            visible: tarjeta.vista
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.topMargin: Tema.px(7)
            anchors.rightMargin: -Tema.px(11)
        }
    }

    Text {
        width: parent.width
        topPadding: Tema.px(6)
        text: tarjeta.titulo
        elide: Text.ElideRight
        font.family: Tema.texto
        font.pixelSize: Tema.px(15)
        font.bold: true
        color: Tema.crema
    }
    Text {
        text: tarjeta.anio > 0 ? tarjeta.anio : ""
        font.family: Tema.rotulo
        font.pixelSize: Tema.px(15)
        font.letterSpacing: 0.5
        color: Tema.tenue
    }
}
