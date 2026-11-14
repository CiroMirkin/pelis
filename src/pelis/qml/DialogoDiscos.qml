import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Se abre desde «…» › «Discos…»: los discos que la app conoce, para ocultarlos, mostrarlos o quitar los agregados a mano
Popup {
    id: dialogo
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(Tema.px(600), parent.width - 48)
    height: Math.min(contenido.implicitHeight + Tema.px(52), parent.height - 48)
    padding: Tema.px(26)
    modal: true
    closePolicy: Popup.CloseOnEscape
    onClosed: cerrado()

    signal cerrado()
    property var lista: []

    function iniciar() {
        lista = puente.discos()
        open()
        cerrar.forceActiveFocus()
    }

    background: Rectangle {
        color: Tema.estante
        radius: Tema.px(4)
        border.width: 1
        border.color: Tema.linea
    }
    Overlay.modal: Rectangle { color: Qt.alpha(Tema.noche, 0.8) }

    // Un disco que entra o sale mientras el diálogo está abierto
    Connections {
        target: puente
        function onDiscosChanged() { dialogo.lista = puente.discos() }
    }

    ColumnLayout {
        id: contenido
        width: dialogo.availableWidth
        spacing: Tema.px(16)

        Text {
            text: "Discos"
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(22)
            font.weight: Font.Bold
            color: Tema.crema
        }
        Text {
            visible: dialogo.lista.length === 0
            Layout.fillWidth: true
            text: "No hay discos con Pelis. Conectá uno o agregalo desde «…» › «Agregar disco…»."
            wrapMode: Text.WordWrap
            font.family: Tema.texto
            font.pixelSize: Tema.px(15)
            color: Tema.tenue
        }

        Repeater {
            model: dialogo.lista
            delegate: RowLayout {
                id: fila
                required property var modelData
                Layout.fillWidth: true
                spacing: Tema.px(12)

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Tema.px(2)
                    Text {
                        Layout.fillWidth: true
                        text: fila.modelData.etiqueta
                        elide: Text.ElideRight
                        font.family: Tema.rotulo
                        font.pixelSize: Tema.px(17)
                        font.weight: Font.DemiBold
                        color: fila.modelData.oculto ? Tema.tenue : Tema.crema
                    }
                    Text {
                        Layout.fillWidth: true
                        text: fila.modelData.ruta + (fila.modelData.oculto ? ", oculto"
                              : fila.modelData.soloLectura ? ", solo lectura"
                              : !fila.modelData.abierto ? ", sin carpeta de películas" : "")
                        elide: Text.ElideMiddle
                        font.family: Tema.texto
                        font.pixelSize: Tema.px(13)
                        color: Tema.tenue
                    }
                }
                Boton {
                    text: fila.modelData.oculto ? "Mostrar" : "Ocultar"
                    onClicked: puente.ocultarDisco(fila.modelData.id, !fila.modelData.oculto)
                }
                Boton {
                    visible: fila.modelData.manual
                    text: "Quitar"
                    onClicked: puente.quitarDisco(fila.modelData.id)
                }
            }
        }

        Boton {
            id: cerrar
            Layout.alignment: Qt.AlignRight
            principal: true
            text: "Cerrar"
            onClicked: dialogo.close()
        }
    }
}
