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
    closePolicy: fase === "descargando" || fase === "listo" ? Popup.NoAutoClose : Popup.CloseOnEscape
    onClosed: cerrado()

    signal cerrado()
    property var respuesta: null
    property string fase: ""  // "" | "descargando" | "listo" | "fallo"
    property real avance: 0
    property string motivo: ""
    readonly property string otroSistema: Qt.platform.os === "windows" ? "Linux" : "Windows"

    function iniciar() {
        respuesta = null; fase = ""; avance = 0; motivo = ""
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
            if (respuesta.nueva) actualizar.forceActiveFocus()
            else cerrar.forceActiveFocus()
        }
        function onDescargaProgreso(fraccion) { dialogo.avance = fraccion }
        function onDescargaTerminada(motivo) {
            if (motivo) { dialogo.motivo = motivo; dialogo.fase = "fallo"; cerrar.forceActiveFocus() }
            else { dialogo.fase = "listo"; reiniciar.start() }
        }
        function onActualizandoChanged() {
            // Cancelada: vuelve a ofrecer la versión nueva
            if (!puente.actualizando && dialogo.fase === "descargando") dialogo.fase = ""
        }
    }

    // Deja leer el aviso antes de cerrar
    Timer {
        id: reiniciar
        interval: 2500
        onTriggered: puente.reiniciarParaActualizar()
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
                    if (dialogo.fase === "descargando") return "Descargando v" + r.nueva.version + "…"
                    if (dialogo.fase === "listo") return "Listo para actualizar"
                    if (dialogo.fase === "fallo") return "No se pudo actualizar"
                    return "Hay una versión nueva"
                }
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
                color: Tema.crema
            }

            ProgressBar {
                visible: !dialogo.respuesta || dialogo.fase === "descargando"
                Layout.fillWidth: true
                indeterminate: !dialogo.respuesta || dialogo.avance === 0
                value: dialogo.avance
            }

            Text {
                visible: !!dialogo.respuesta
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                font.family: Tema.texto
                font.pixelSize: Tema.px(15)
                color: dialogo.respuesta && dialogo.respuesta.error || dialogo.fase === "fallo" ? Tema.alerta : Tema.crema
                text: {
                    const r = dialogo.respuesta
                    if (!r) return ""
                    if (r.error) return r.error
                    if (dialogo.fase === "descargando") return Math.round(dialogo.avance * 100) + " %"
                    if (dialogo.fase === "listo") return "Pelis se va a cerrar y volver a abrir con la versión nueva."
                    if (dialogo.fase === "fallo") return dialogo.motivo + "\nSigue instalada la versión actual."
                    if (r.alDia) return "Tenés la última versión (v" + puente.version + ")."
                    return "v" + puente.version + " → v" + r.nueva.version
                }
            }

            // Notas de la Release, en Markdown
            Text {
                visible: !!(dialogo.respuesta && dialogo.respuesta.nueva && dialogo.respuesta.nueva.notas)
                         && dialogo.fase === ""
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                textFormat: Text.MarkdownText
                text: visible ? dialogo.respuesta.nueva.notas : ""
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.crema
            }

            Text {
                visible: !!(dialogo.respuesta && dialogo.respuesta.nueva) && dialogo.fase === ""
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                text: "Si también usás este disco en " + dialogo.otroSistema
                      + ", actualizá desde ahí también: cada sistema tiene su propia copia de Pelis."
                font.family: Tema.texto
                font.pixelSize: Tema.px(13)
                color: Tema.tenue
            }

            RowLayout {
                visible: !!dialogo.respuesta && dialogo.fase !== "listo"
                Layout.alignment: Qt.AlignRight
                spacing: Tema.px(12)
                Boton {
                    id: cerrar
                    readonly property bool ofreceNueva: !!(dialogo.respuesta && dialogo.respuesta.nueva) && dialogo.fase === ""
                    text: dialogo.fase === "descargando" ? "Cancelar" : "Cerrar"
                    principal: !ofreceNueva && dialogo.fase !== "descargando"
                    onClicked: dialogo.fase === "descargando" ? puente.cancelarActualizacion() : dialogo.close()
                }
                Boton {
                    id: actualizar
                    visible: cerrar.ofreceNueva
                    principal: true
                    text: "Actualizar"
                    onClicked: { dialogo.fase = "descargando"; dialogo.avance = 0; puente.actualizar() }
                }
            }
        }
    }
}
