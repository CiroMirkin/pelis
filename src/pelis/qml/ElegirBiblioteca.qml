import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

// Selector de carpeta nativo. Si la carpeta nueva no tiene ninguna película de la base, antes de guardarla pide confirmar
Item {
    id: raiz
    property string elegida: ""

    signal cambiada()
    signal cerrado()  // Se canceló o no se pudo guardar o se pidió no seguir

    function iniciar() { selector.open() }

    function aplicar() {
        if (puente.cambiarBiblioteca(elegida)) cambiada()
        else cerrado()
    }

    FolderDialog {
        id: selector
        title: "Elegir la carpeta de películas"
        onAccepted: {
            raiz.elegida = selectedFolder.toString()
            if (puente.cambiarBibliotecaPierdePeliculas(raiz.elegida)) aviso.open()
            else raiz.aplicar()
        }
        onRejected: raiz.cerrado()
    }

    Popup {
        id: aviso
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: Math.min(Tema.px(520), parent.width - 48)
        padding: Tema.px(26)
        modal: true
        property bool seguir: false
        onOpened: { seguir = false; cancelar.forceActiveFocus() }
        onClosed: if (!seguir) raiz.cerrado()
        background: Rectangle {
            color: Tema.estante
            radius: Tema.px(4)
            border.width: 1
            border.color: Tema.linea
        }
        Overlay.modal: Rectangle { color: Qt.alpha(Tema.noche, 0.8) }

        ColumnLayout {
            width: aviso.availableWidth
            spacing: Tema.px(18)
            Text {
                text: "¿Cambiar de biblioteca?"
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                color: Tema.crema
            }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                text: "Esa carpeta no tiene ninguna de las películas de la biblioteca anterior: van a quedar como faltantes."
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
                    onClicked: aviso.close()
                }
                Boton {
                    principal: true
                    text: "Cambiar"
                    onClicked: { aviso.seguir = true; aviso.close(); raiz.aplicar() }
                }
            }
        }
    }
}
