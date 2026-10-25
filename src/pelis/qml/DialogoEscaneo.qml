import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: dialogo
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(Tema.px(660), parent.width - 48)
    height: Math.min(contenido.implicitHeight + Tema.px(64), parent.height - 48)
    padding: Tema.px(26)
    modal: true
    closePolicy: puente.escaneando ? Popup.NoAutoClose : Popup.CloseOnEscape

    property int actual: 0
    property int total: 0
    property string nombre: ""
    property var informe: null

    function iniciar() {
        actual = 0; total = 0; nombre = ""; informe = null
        open()
        puente.escanear()
    }

    function seccion(titulo, items) {
        return items.length ? titulo + " (" + items.length + "):\n  " + items.join("\n  ") : ""
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
        function onEscaneoProgreso(actual, total, nombre) {
            dialogo.actual = actual; dialogo.total = total; dialogo.nombre = nombre
        }
        function onEscaneoTerminado(informe) {
            dialogo.informe = informe
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
                text: dialogo.informe ? "Listo" : "Buscando películas…"
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
                color: Tema.crema
            }

            // Progreso
            ColumnLayout {
                visible: !dialogo.informe
                Layout.fillWidth: true
                spacing: Tema.px(10)
                ProgressBar {
                    Layout.fillWidth: true
                    from: 0
                    to: Math.max(1, dialogo.total)
                    value: dialogo.actual
                    indeterminate: dialogo.total === 0
                }
                Text {
                    Layout.fillWidth: true
                    text: dialogo.total ? dialogo.actual + " de " + dialogo.total + "  *  " + dialogo.nombre : ""
                    elide: Text.ElideRight
                    font.family: Tema.texto
                    font.pixelSize: Tema.px(14)
                    color: Tema.tenue
                }
            }

            // Informe
            Text {
                visible: !!dialogo.informe
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.crema
                text: {
                    const i = dialogo.informe
                    if (!i) return ""
                    if (i.error) return "El escaneo falló:\n" + i.error
                    return [
                        "Agregadas: " + i.agregadas,
                        dialogo.seccion("Metadatos leídos de pelis.json", i.desdeArchivo),
                        dialogo.seccion("No encontradas en OMDb", i.noEncontradas),
                        dialogo.seccion("Pendientes de metadatos", i.pendientes),
                        dialogo.seccion("Faltantes (carpeta no existe; reasignalas desde «…» › «Faltantes»)", i.faltantes),
                        dialogo.seccion("Reaparecidas", i.reactivadas),
                        dialogo.seccion("Carpetas renombradas (conservan progreso y vista)", i.reasignadas),
                        dialogo.seccion("Carpetas con problemas", i.problemas.map(p => p.carpeta + " — " + p.motivo)),
                        dialogo.seccion("pelis.json inválidos (ignorados, no se sobrescriben)", i.archivosInvalidos.map(p => p.carpeta + " — " + p.motivo)),
                        i.aviso,
                    ].filter(x => x).join("\n\n")
                }
            }

            Boton {
                id: cerrar
                visible: !!dialogo.informe
                Layout.alignment: Qt.AlignRight
                principal: true
                text: "Cerrar"
                onClicked: dialogo.close()
            }
        }
    }
}
