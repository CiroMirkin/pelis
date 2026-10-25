import QtQuick
import QtQuick.Controls

// Selector de época: un botón que despliega las décadas y los años recientes presentes en la biblioteca
AbstractButton {
    id: selector
    property var periodos: []  // [{clave, etiqueta}], armados en Python
    property string periodo: ""
    signal elegido(string clave)

    readonly property var todas: [{ clave: "", etiqueta: "Todos" }].concat(periodos)

    function etiqueta(clave) {
        const o = todas.find(o => o.clave === clave)
        return o ? o.etiqueta : ""
    }

    implicitHeight: Tema.px(38)
    leftPadding: Tema.px(14)
    rightPadding: Tema.px(10)
    focusPolicy: Qt.TabFocus
    hoverEnabled: true
    onClicked: lista.visible ? lista.close() : lista.open()
    Keys.onReturnPressed: clicked()
    Keys.onEnterPressed: clicked()
    Keys.onDownPressed: lista.open()

    contentItem: Row {
        spacing: Tema.px(6)
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: selector.periodo === "" ? "Época" : selector.etiqueta(selector.periodo)
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(15)
            font.weight: Font.DemiBold
            font.capitalization: Font.AllUppercase
            font.letterSpacing: 0.6
            color: Tema.crema
        }
        Image {
            anchors.verticalCenter: parent.verticalCenter
            source: "iconos/abajo.svg"
            sourceSize: Qt.size(Tema.px(16), Tema.px(16))
            rotation: lista.visible ? 180 : 0
        }
    }

    background: Item {
        Rectangle {
            visible: selector.visualFocus
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
            color: selector.down || lista.visible ? Tema.linea : selector.hovered ? Tema.caja : "transparent"
            border.width: 2
            border.color: Qt.alpha(Tema.crema, 0.55)
        }
    }

    Popup {
        id: lista
        y: selector.height + Tema.px(6)
        width: Math.max(selector.width, Tema.px(210))
        height: Math.min(opciones.contentHeight + topPadding + bottomPadding, Tema.px(380))
        padding: Tema.px(6)
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
        onOpened: {
            opciones.currentIndex = Math.max(0, selector.todas.findIndex(o => o.clave === selector.periodo))
            opciones.positionViewAtIndex(opciones.currentIndex, ListView.Contain)
            opciones.forceActiveFocus()
        }
        onClosed: selector.forceActiveFocus()
        background: Rectangle {
            color: Tema.estante
            radius: Tema.px(4)
            border.width: 1
            border.color: Tema.linea
        }

        ListView {
            id: opciones
            anchors.fill: parent
            clip: true
            model: selector.todas
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar {}
            Keys.onReturnPressed: elegir(currentIndex)
            Keys.onEnterPressed: elegir(currentIndex)

            function elegir(i) {
                selector.elegido(selector.todas[i].clave)
                lista.close()
            }

            delegate: Rectangle {
                id: fila
                required property int index
                required property var modelData
                readonly property bool elegida: modelData.clave === selector.periodo
                width: ListView.view.width
                height: Tema.px(36)
                radius: Tema.px(3)
                color: zona.containsMouse || (fila.ListView.isCurrentItem && opciones.activeFocus) ? Tema.caja : "transparent"

                Rectangle {
                    visible: fila.elegida
                    anchors.left: parent.left
                    anchors.leftMargin: Tema.px(10)
                    anchors.verticalCenter: parent.verticalCenter
                    width: Tema.px(8)
                    height: width
                    color: Tema.etiqueta
                }
                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: Tema.px(28)
                    anchors.verticalCenter: parent.verticalCenter
                    text: fila.modelData.etiqueta
                    // En la condensada: la Atkinson dibuja el cero tachado (Regla del Lomo)
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(16)
                    font.letterSpacing: 0.3
                    font.bold: fila.elegida
                    color: Tema.crema
                }
                MouseArea {
                    id: zona
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: opciones.elegir(fila.index)
                }
            }
        }
    }
}
