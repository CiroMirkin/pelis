import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic
import QtQuick.Layouts

// Editar los datos de una película: traerlos de IMDb (por ID, link o buscando el título) o a mano
Page {
    id: pagina
    required property int peliculaId
    property var d: ({})
    property var candidatos: []
    property string estadoImdb: ""   // resultado de la última consulta a IMDb
    property bool errorImdb: false
    property string errorGuardar: ""
    property bool guardando: false
    property string imdbPendiente: ""  // ID a aplicar cuando se confirme

    readonly property var campos: ({
        titulo: titulo.text, anio: anio.text, pais: pais.text, genero: genero.text,
        director: director.text, elenco: elenco.text, sinopsis: sinopsis.text,
    })
    readonly property bool modificado: Object.keys(campos).some(k => campos[k] !== (d[k] || ""))

    function cargar() {
        d = puente.datosEdicion(peliculaId)
        titulo.text = d.titulo; anio.text = d.anio; pais.text = d.pais; genero.text = d.genero
        director.text = d.director; elenco.text = d.elenco; sinopsis.text = d.sinopsis
    }

    function guardar() {
        if (guardando || !modificado) return
        guardando = true
        errorGuardar = puente.guardarEdicion(peliculaId, campos)
        guardando = false
        if (errorGuardar === "") {
            const pila = pagina.StackView.view
            pila.pop()
            pila.currentItem.avisar("Datos guardados")
        }
    }

    function buscar() {
        if (busqueda.text.trim() === "" || puente.consultandoImdb) return
        candidatos = []
        estadoImdb = ""
        // Un ID o un link reemplaza los datos enseguida: se confirma antes si hay algo que perder
        const id = (busqueda.text.match(/tt\d{7,}/i) || [""])[0]
        if (id) usar(id.toLowerCase())
        else puente.buscarEnImdb(peliculaId, busqueda.text)
    }

    function usar(imdbId) {
        if (d.origen === "manual" || modificado) {
            imdbPendiente = imdbId
            confirmar.open()
        } else {
            aplicar(imdbId)
        }
    }

    function aplicar(imdbId) {
        estadoImdb = ""
        puente.usarImdb(peliculaId, imdbId)
    }

    Component.onCompleted: { cargar(); (d.origen === "" ? busqueda : titulo).forceActiveFocus() }

    Connections {
        target: puente
        function onImdbRespondio(r) {
            pagina.errorImdb = !!r.error
            if (r.error) {
                pagina.estadoImdb = r.error
            } else if (r.candidatos) {
                pagina.candidatos = r.candidatos
                pagina.estadoImdb = r.candidatos.length ? "" : "IMDb no encontró ninguna película con ese título."
            } else if (r.aplicado) {
                pagina.candidatos = []
                pagina.cargar()
                pagina.estadoImdb = ["Listo: los datos son los de IMDb (" + pagina.d.imdbId + ").", r.aviso]
                    .filter(x => x).join("\n")
            }
        }
    }

    Shortcut {
        sequence: "Esc"
        enabled: pagina.StackView.status === StackView.Active && !confirmar.opened
        onActivated: pagina.StackView.view.pop()
    }
    Shortcut {
        sequences: [StandardKey.Save]
        // Igual que el botón: sin cambios no se guarda (si no, quedaría como editado a mano)
        enabled: pagina.StackView.status === StackView.Active && guardar.enabled && !confirmar.opened
        onActivated: pagina.guardar()
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
                Layout.fillWidth: true
                text: pagina.d.carpeta || ""
                elide: Text.ElideMiddle
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                color: Tema.tenue
            }
        }
    }

    // Rótulo de sección y de campo, como en el detalle
    component Rotulo: Text {
        font.family: Tema.rotulo
        font.pixelSize: Tema.px(13)
        font.weight: Font.DemiBold
        font.letterSpacing: 1
        font.capitalization: Font.AllUppercase
        color: Tema.tenue
    }
    component Titulo: Text {
        font.family: Tema.rotulo
        font.pixelSize: Tema.px(22)
        font.weight: Font.Bold
        font.capitalization: Font.AllUppercase
        color: Tema.crema
    }
    component Nota: Text {
        Layout.fillWidth: true
        wrapMode: Text.WordWrap
        font.family: Tema.texto
        font.pixelSize: Tema.px(14)
        color: Tema.tenue
    }

    Flickable {
        id: desplazable
        anchors.fill: parent
        contentHeight: columna.implicitHeight + Tema.px(80)
        clip: true
        ScrollBar.vertical: ScrollBar {}

        ColumnLayout {
            id: columna
            x: Tema.px(40)
            y: Tema.px(40)
            width: Math.min(desplazable.width - Tema.px(80), Tema.px(860))
            spacing: Tema.px(14)

            // --- IMDb ---
            Titulo { text: "Traer de IMDb" }
            // Resincronizar el ID actual va aparte de la búsqueda: no usa lo escrito en el campo
            Nota {
                visible: !!pagina.d.imdbId
                text: "Ahora: " + pagina.d.imdbId + (pagina.d.origen === "manual" ? ", con datos editados a mano." : ".")
            }
            RowLayout {
                visible: !!pagina.d.imdbId
                spacing: Tema.px(12)
                Boton {
                    text: "Volver a traer " + pagina.d.imdbId
                    enabled: pagina.d.conClave === true && !puente.consultandoImdb
                    onClicked: pagina.usar(pagina.d.imdbId)
                }
                Nota { text: "Reemplaza los datos por los actuales de IMDb." }
            }
            Nota {
                Layout.topMargin: pagina.d.imdbId ? Tema.px(8) : 0
                text: pagina.d.imdbId
                      ? "Si no es la película correcta, buscala por título o pegá su ID o su link de IMDb."
                      : "Buscala por título (podés agregar el año) o pegá su ID (tt0078748) o su link de IMDb."
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: Tema.px(12)
                Campo {
                    id: busqueda
                    Layout.fillWidth: true
                    enabled: pagina.d.conClave === true
                    placeholderText: "Título, ID o link de IMDb"
                    onAccepted: pagina.buscar()
                    KeyNavigation.tab: botonBuscar
                }
                Boton {
                    id: botonBuscar
                    text: "Buscar"
                    enabled: pagina.d.conClave === true && !puente.consultandoImdb && busqueda.text.trim() !== ""
                    onClicked: pagina.buscar()
                }
            }
            Nota {
                visible: pagina.d.conClave === false
                text: "Para traer datos de IMDb falta omdb_api_key en pelis.toml."
                color: Tema.alerta
            }
            RowLayout {
                visible: puente.consultandoImdb
                spacing: Tema.px(10)
                BusyIndicator { running: visible; implicitWidth: Tema.px(28); implicitHeight: Tema.px(28) }
                Nota { text: "Consultando IMDb…" }
            }
            Nota {
                visible: pagina.estadoImdb !== "" && !puente.consultandoImdb
                text: pagina.estadoImdb
                color: pagina.errorImdb ? Tema.alerta : Tema.crema
            }

            // Candidatos de la búsqueda por título
            Repeater {
                model: pagina.candidatos
                delegate: AbstractButton {
                    id: candidato
                    required property var modelData
                    Layout.fillWidth: true
                    implicitHeight: Tema.px(84)
                    hoverEnabled: true
                    focusPolicy: Qt.StrongFocus
                    onClicked: pagina.usar(modelData.imdbId)
                    Keys.onReturnPressed: clicked()
                    Keys.onEnterPressed: clicked()
                    background: Rectangle {
                        radius: Tema.px(3)
                        color: candidato.down ? Tema.linea : candidato.hovered ? Tema.caja : Tema.estante
                        border.width: candidato.visualFocus ? Tema.px(3) : 0
                        border.color: Tema.tubo
                    }
                    contentItem: RowLayout {
                        spacing: Tema.px(14)
                        Rectangle {
                            Layout.leftMargin: Tema.px(8)
                            Layout.preferredWidth: Tema.px(46)
                            Layout.preferredHeight: Tema.px(68)
                            color: Tema.caja
                            Image {
                                anchors.fill: parent
                                source: candidato.modelData.poster
                                fillMode: Image.PreserveAspectCrop
                                asynchronous: true
                                sourceSize.width: 92
                            }
                        }
                        Text {
                            Layout.fillWidth: true
                            text: candidato.modelData.titulo
                            elide: Text.ElideRight
                            font.family: Tema.texto
                            font.pixelSize: Tema.px(16)
                            font.bold: true
                            color: Tema.crema
                        }
                        Text {
                            Layout.rightMargin: Tema.px(16)
                            text: candidato.modelData.anio + "   " + candidato.modelData.imdbId
                            font.family: Tema.rotulo
                            font.pixelSize: Tema.px(15)
                            font.features: { "tnum": 1 }
                            color: Tema.tenue
                        }
                    }
                }
            }

            // --- A mano ---
            Rectangle { Layout.fillWidth: true; Layout.topMargin: Tema.px(18); height: 1; color: Tema.linea }
            Titulo { Layout.topMargin: Tema.px(10); text: "Datos" }
            Nota { text: "Lo que cambies acá queda guardado como editado a mano, en la base y en el pelis.json de la carpeta." }

            GridLayout {
                Layout.fillWidth: true
                Layout.topMargin: Tema.px(6)
                columns: 2
                columnSpacing: Tema.px(18)
                rowSpacing: Tema.px(12)

                Rotulo { text: "Título" }
                Campo { id: titulo; Layout.fillWidth: true }
                Rotulo { text: "Año" }
                Campo {
                    id: anio
                    Layout.preferredWidth: Tema.px(110)
                    inputMethodHints: Qt.ImhDigitsOnly
                    validator: RegularExpressionValidator { regularExpression: /\d{0,4}/ }
                }
                Rotulo { text: "País" }
                Campo { id: pais; Layout.fillWidth: true; placeholderText: "Separados por comas" }
                Rotulo { text: "Género" }
                Campo { id: genero; Layout.fillWidth: true; placeholderText: "Separados por comas" }
                Rotulo { text: "Dirección" }
                Campo { id: director; Layout.fillWidth: true; placeholderText: "Nombres separados por comas" }
                Rotulo { text: "Elenco" }
                Campo { id: elenco; Layout.fillWidth: true; placeholderText: "Nombres separados por comas" }
                Rotulo { Layout.alignment: Qt.AlignTop; Layout.topMargin: Tema.px(10); text: "Sinopsis" }
                Basic.TextArea {
                    id: sinopsis
                    Layout.fillWidth: true
                    Layout.minimumHeight: Tema.px(140)
                    wrapMode: TextEdit.Wrap
                    color: Tema.crema
                    selectionColor: Tema.etiqueta
                    selectedTextColor: Tema.sobreEtiqueta
                    font.family: Tema.texto
                    font.pixelSize: Tema.px(15)
                    padding: Tema.px(12)
                    leftPadding: Tema.px(14)
                    KeyNavigation.priority: KeyNavigation.BeforeItem
                    KeyNavigation.tab: guardar
                    background: Rectangle {
                        radius: Tema.px(3)
                        color: sinopsis.activeFocus ? Tema.caja : "transparent"
                        border.width: sinopsis.activeFocus ? Tema.px(2) : 1
                        border.color: sinopsis.activeFocus ? Tema.tubo : Qt.alpha(Tema.crema, 0.35)
                    }
                }
            }

            Nota {
                visible: pagina.errorGuardar !== ""
                text: pagina.errorGuardar
                color: Tema.alerta
            }
            RowLayout {
                Layout.topMargin: Tema.px(8)
                spacing: Tema.px(12)
                Boton {
                    id: guardar
                    principal: true
                    text: "Guardar"
                    enabled: pagina.modificado && !pagina.guardando
                    onClicked: pagina.guardar()
                }
                Boton {
                    text: "Descartar cambios"
                    visible: pagina.modificado
                    onClicked: { pagina.cargar(); pagina.errorGuardar = "" }
                }
            }
        }
    }

    Popup {
        id: confirmar
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: Math.min(Tema.px(520), parent.width - 48)
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
            Titulo { text: "¿Reemplazar los datos?" }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                text: (pagina.modificado ? "Tenés cambios sin guardar en el formulario. " : "")
                      + (pagina.d.origen === "manual" ? "Los datos de esta película se editaron a mano. " : "")
                      + "Si seguís, se reemplazan por los de IMDb (" + pagina.imdbPendiente + ")."
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
                    text: "Reemplazar"
                    onClicked: { confirmar.close(); pagina.aplicar(pagina.imdbPendiente) }
                }
            }
        }
    }
}
