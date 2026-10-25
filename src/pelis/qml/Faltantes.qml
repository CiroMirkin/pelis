import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Reasignación manual: una película cuya carpeta ya no está toma una de las carpetas actuales
// (por ejemplo, la misma renombrada), conservando progreso, vista y datos
Page {
    id: pagina
    property var faltantes: []
    property var carpetas: []
    property int elegida: -1        // índice en `faltantes`
    property var destino: null      // carpeta a confirmar
    property string filtro: ""
    property string mensaje: ""
    readonly property var falta: elegida >= 0 && elegida < faltantes.length ? faltantes[elegida] : null
    readonly property var carpetasFiltradas: {
        const palabras = puente.normalizar(filtro).split(" ").filter(x => x)
        return carpetas.filter(c => palabras.every(p => c.busqueda.includes(p)))
    }

    function cargar() {
        faltantes = puente.faltantes()
        carpetas = puente.carpetasParaReasignar()
        elegida = faltantes.length ? Math.min(Math.max(elegida, 0), faltantes.length - 1) : -1
    }

    function reasignar() {
        const titulo = falta.titulo, carpeta = destino.carpeta
        const error = puente.reasignar(falta.id, destino.id)
        mensaje = error || "«" + titulo + "» ahora usa la carpeta " + carpeta + "."
        destino = null
        cargar()
    }

    Component.onCompleted: { cargar(); filtroCampo.forceActiveFocus() }

    Shortcut {
        sequence: "Esc"
        enabled: pagina.StackView.status === StackView.Active && !confirmar.opened
        onActivated: pagina.StackView.view.pop()
    }

    background: Rectangle { color: Tema.noche }

    header: Rectangle {
        implicitHeight: Tema.px(68)
        color: Tema.noche
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Tema.linea }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Tema.px(40)
            anchors.rightMargin: Tema.px(40)
            spacing: Tema.px(20)
            Boton {
                text: "Volver"
                icono: "volver"
                focusPolicy: Qt.TabFocus
                onClicked: pagina.StackView.view.pop()
            }
            Text {
                text: "FALTANTES"
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                font.letterSpacing: 1
                color: Tema.crema
            }
            Item { Layout.fillWidth: true }
        }
    }

    // Fila elegible de las dos listas
    component Fila: AbstractButton {
        id: fila
        property string principal: ""
        property string secundario: ""
        property bool elegida: false
        width: ListView.view ? ListView.view.width : implicitWidth
        implicitHeight: Tema.px(58)
        hoverEnabled: true
        focusPolicy: Qt.StrongFocus
        Keys.onReturnPressed: clicked()
        Keys.onEnterPressed: clicked()
        background: Rectangle {
            radius: Tema.px(3)
            color: fila.elegida ? Tema.caja : fila.down ? Tema.linea : fila.hovered ? Tema.estante : "transparent"
            border.width: fila.visualFocus ? Tema.px(3) : fila.elegida ? 1 : 0
            border.color: fila.visualFocus ? Tema.tubo : Tema.linea
        }
        contentItem: Column {
            leftPadding: Tema.px(14)
            rightPadding: Tema.px(14)
            topPadding: Tema.px(8)
            spacing: Tema.px(3)
            Text {
                width: fila.width - Tema.px(28)
                text: fila.principal
                elide: Text.ElideRight
                font.family: Tema.texto
                font.pixelSize: Tema.px(15)
                font.bold: true
                color: Tema.crema
            }
            Text {
                width: fila.width - Tema.px(28)
                text: fila.secundario
                elide: Text.ElideMiddle
                font.family: Tema.texto
                font.pixelSize: Tema.px(13)
                color: Tema.tenue
            }
        }
    }

    Text {
        visible: pagina.faltantes.length === 0
        anchors.centerIn: parent
        horizontalAlignment: Text.AlignHCenter
        lineHeight: 1.3
        text: (pagina.mensaje ? pagina.mensaje + "\n\n" : "") + "No hay películas faltantes."
        font.family: Tema.texto
        font.pixelSize: Tema.px(16)
        color: Tema.tenue
    }

    RowLayout {
        visible: pagina.faltantes.length > 0
        anchors.fill: parent
        anchors.margins: Tema.px(40)
        spacing: Tema.px(40)

        ColumnLayout {
            Layout.preferredWidth: parent.width * 0.4
            Layout.fillHeight: true
            spacing: Tema.px(12)
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: "Su carpeta ya no está en la biblioteca. Elegí una y asignale la carpeta donde está ahora."
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.tenue
            }
            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: Tema.px(4)
                model: pagina.faltantes
                ScrollBar.vertical: ScrollBar {}
                delegate: Fila {
                    required property var modelData
                    required property int index
                    principal: modelData.titulo + (modelData.anio ? " (" + modelData.anio + ")" : "")
                    secundario: modelData.carpeta + (modelData.vista ? "  ·  vista" : modelData.progreso > 0 ? "  ·  empezada" : "")
                    elegida: index === pagina.elegida
                    onClicked: pagina.elegida = index
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Tema.px(12)
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: pagina.falta ? "Carpeta para «" + pagina.falta.titulo + "». Las agregadas último van primero." : ""
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.tenue
            }
            Campo {
                id: filtroCampo
                Layout.fillWidth: true
                placeholderText: "Filtrar carpetas"
                onTextChanged: pagina.filtro = text
            }
            Text {
                visible: pagina.mensaje !== ""
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: pagina.mensaje
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.crema
            }
            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: Tema.px(4)
                model: pagina.carpetasFiltradas
                ScrollBar.vertical: ScrollBar {}
                delegate: Fila {
                    required property var modelData
                    principal: modelData.carpeta
                    secundario: "Hoy figura como «" + modelData.titulo + "»" + (modelData.anio ? " (" + modelData.anio + ")" : "")
                    onClicked: { pagina.destino = modelData; confirmar.open() }
                }
            }
        }
    }

    Popup {
        id: confirmar
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: Math.min(Tema.px(560), parent.width - 48)
        padding: Tema.px(26)
        modal: true
        onOpened: cancelar.forceActiveFocus()
        background: Rectangle {
            color: Tema.estante
            radius: Tema.px(4)
            border.width: 1
            border.color: Tema.linea
        }
        Overlay.modal: Rectangle { color: Qt.alpha(Tema.noche, 0.8) }

        ColumnLayout {
            width: confirmar.availableWidth
            spacing: Tema.px(18)
            Text {
                text: "¿REASIGNAR?"
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                color: Tema.crema
            }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                text: pagina.falta && pagina.destino
                      ? "«" + pagina.falta.titulo + "» pasa a usar la carpeta " + pagina.destino.carpeta
                        + ", con su progreso y si está vista. La entrada «" + pagina.destino.titulo
                        + "» que hoy usa esa carpeta desaparece del catálogo."
                      : ""
                font.family: Tema.texto
                font.pixelSize: Tema.px(15)
                color: Tema.crema
            }
            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: Tema.px(12)
                Boton {
                    id: cancelar
                    text: "Cancelar"
                    onClicked: confirmar.close()
                }
                Boton {
                    principal: true
                    text: "Reasignar"
                    onClicked: { confirmar.close(); pagina.reasignar() }
                }
            }
        }
    }
}
