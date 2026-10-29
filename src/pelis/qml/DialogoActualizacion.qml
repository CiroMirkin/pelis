import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// «…» › «Buscar actualización»: consulta la última Release y muestra si hay una versión nueva
Popup {
    id: dialogo
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(Tema.px(560), parent.width - 48)
    height: Math.min(contenido.implicitHeight + Tema.px(64), parent.height - 48)
    padding: Tema.px(26)
    modal: true
    onClosed: cerrado()

    signal cerrado()
    property var respuesta: null
    readonly property string otroSistema: Qt.platform.os === "windows" ? "Linux" : "Windows"

    function iniciar() {
        respuesta = null
        open()
        puente.buscarActualizacion()
    }

    background: Rectangle {
        color: Tema.estante
        radius: Tema.px(4)
        border.width: 1
        border.color: Tema.linea
    }
    Overlay.modal: Rectangle { color: Qt.alpha(Tema.noche, 0.8) }

    Connections {
        target: puente
        function onActualizacionRespondio(respuesta) {
            dialogo.respuesta = respuesta
            cerrar.forceActiveFocus()
        }
    }

    ScrollView {
        anchors.fill: parent
        clip: true

        ColumnLayout {
            id: contenido
            width: dialogo.availableWidth
            spacing: Tema.px(16)

            Text {
                text: {
                    const r = dialogo.respuesta
                    if (!r) return "Buscando actualización…"
                    if (r.error) return "Sin conexión"
                    if (r.alDia) return "Estás al día"
                    return "Hay una versión nueva"
                }
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
                color: Tema.crema
            }

            ProgressBar {
                visible: !dialogo.respuesta
                Layout.fillWidth: true
                indeterminate: true
            }

            Text {
                visible: !!dialogo.respuesta
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                font.family: Tema.texto
                font.pixelSize: Tema.px(15)
                color: dialogo.respuesta && dialogo.respuesta.error ? Tema.alerta : Tema.crema
                text: {
                    const r = dialogo.respuesta
                    if (!r) return ""
                    if (r.error) return r.error
                    if (r.alDia) return "Tenés la última versión (v" + puente.version + ")."
                    return "v" + puente.version + " → v" + r.nueva.version
                }
            }

            // Notas de la Release, en Markdown
            Text {
                visible: !!(dialogo.respuesta && dialogo.respuesta.nueva && dialogo.respuesta.nueva.notas)
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                textFormat: Text.MarkdownText
                text: visible ? dialogo.respuesta.nueva.notas : ""
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.crema
            }

            Text {
                visible: !!(dialogo.respuesta && dialogo.respuesta.nueva)
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                text: "Si también usás este disco en " + dialogo.otroSistema
                      + ", actualizá desde ahí también: cada sistema tiene su propia copia de Pelis."
                font.family: Tema.texto
                font.pixelSize: Tema.px(13)
                color: Tema.tenue
            }

            Boton {
                id: cerrar
                visible: !!dialogo.respuesta
                Layout.alignment: Qt.AlignRight
                principal: true
                text: "Cerrar"
                onClicked: dialogo.close()
            }
        }
    }
}
