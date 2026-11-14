import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Se abre desde «…» › «Claves de API…» y evita editar pelis.toml
Popup {
    id: dialogo
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(Tema.px(560), parent.width - 48)
    height: Math.min(contenido.implicitHeight + Tema.px(64), parent.height - 48)
    padding: Tema.px(26)
    modal: true
    closePolicy: puente.validandoClaves ? Popup.NoAutoClose : Popup.CloseOnEscape
    onClosed: cerrado()

    signal cerrado()
    signal escanearPendientes()
    property var errores: ({})
    property var respuesta: null  // Mientras no sea null el diálogo muestra el resultado y el botón pasa de Guardar a Cerrar

    function iniciar() {
        const c = puente.claves()
        omdb.text = c.omdb
        tmdb.text = c.tmdb
        errores = {}; respuesta = null
        open()
        omdb.forceActiveFocus()
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
        function onClavesRespondio(r) {
            dialogo.errores = r.errores
            dialogo.respuesta = r.guardado ? r : null
            if (!r.guardado) return
            if (!r.sinVerificar && !r.omdbVacia && r.pendientes === 0) dialogo.close()
            else if (r.pendientes > 0 && !puente.escaneando) buscarPendientes.forceActiveFocus()
            else cerrar.forceActiveFocus()
        }
    }

    component CampoClave: ColumnLayout {
        id: fila
        property string rotulo
        property string enlace
        property string error: ""
        property alias text: campo.text
        spacing: Tema.px(6)
        Layout.fillWidth: true

        RowLayout {
            Layout.fillWidth: true
            Text {
                text: fila.rotulo
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(16)
                color: Tema.crema
            }
            Item { Layout.fillWidth: true }
            Text {
                text: "Conseguir clave"
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                font.underline: true
                color: Tema.crema
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: Qt.openUrlExternally(fila.enlace)
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: Tema.px(8)
            Campo {
                id: campo
                Layout.fillWidth: true
                echoMode: ver.checked ? TextInput.Normal : TextInput.Password
                passwordCharacter: "•"
                onTextChanged: dialogo.errores = ({})
                onAccepted: guardar.clicked()
            }
            Boton {
                id: ver
                checkable: true
                text: checked ? "Ocultar" : "Mostrar"
                focusPolicy: Qt.TabFocus
            }
        }
        Text {
            visible: fila.error !== ""
            Layout.fillWidth: true
            text: fila.error
            wrapMode: Text.WordWrap
            font.family: Tema.texto
            font.pixelSize: Tema.px(14)
            color: Tema.alerta
        }
    }

    ScrollView {
        anchors.fill: parent
        clip: true
        contentWidth: availableWidth
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ColumnLayout {
            id: contenido
            width: dialogo.availableWidth
            spacing: Tema.px(16)

            Text {
                text: "Claves de API"
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                color: Tema.crema
            }

            Text {
                Layout.fillWidth: true
                text: "La de OMDb trae los datos de las películas. La de TMDb es opcional: sirve para las sinopsis en español. Dejar un campo vacío borra esa clave."
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.tenue
            }

            CampoClave {
                id: omdb
                rotulo: "OMDb"
                enlace: "https://www.omdbapi.com/apikey.aspx"
                error: dialogo.errores.omdb || ""
            }
            CampoClave {
                id: tmdb
                rotulo: "TMDb"
                enlace: "https://www.themoviedb.org/settings/api"
                error: dialogo.errores.tmdb || ""
            }

            Text {
                readonly property var r: dialogo.respuesta
                visible: !!r && text !== ""
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.crema
                text: !r ? "" : [
                    "Claves guardadas.",
                    r.sinVerificar ? "No se pudo verificar: no hay conexión con el servicio. Se guardó igual." : "",
                    r.omdbVacia ? "Sin la clave de OMDb, las películas nuevas quedan pendientes de datos." : "",
                    r.pendientes > 0 ? r.pendientes + (r.pendientes === 1 ? " película está pendiente de datos." : " películas están pendientes de datos.") : "",
                ].filter(x => x).join("\n")
            }

            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: Tema.px(10)
                BusyIndicator {
                    running: visible
                    visible: puente.validandoClaves
                    implicitWidth: Tema.px(28); implicitHeight: Tema.px(28)
                }
                Boton {
                    id: buscarPendientes
                    visible: !!dialogo.respuesta && dialogo.respuesta.pendientes > 0
                    enabled: !puente.escaneando
                    text: "Buscar datos de las pendientes ahora"
                    onClicked: { dialogo.close(); dialogo.escanearPendientes() }
                }
                Boton {
                    id: cerrar
                    text: dialogo.respuesta ? "Cerrar" : "Cancelar"
                    enabled: !puente.validandoClaves
                    onClicked: dialogo.close()
                }
                Boton {
                    id: guardar
                    visible: !dialogo.respuesta
                    principal: true
                    enabled: !puente.validandoClaves
                    text: "Guardar"
                    onClicked: puente.guardarClaves(omdb.text, tmdb.text)
                }
            }
        }
    }
}
