import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "paises.js" as Paises
import "duracion.js" as Duracion

Page {
    id: pagina
    required property int peliculaId
    property var p: ({})

    function recargar() { p = puente.pelicula(peliculaId) }
    Connections {
        target: puente
        function onDuracionMedida(id, ms) { if (id === pagina.peliculaId) pagina.recargar() }
        // Una captura que termina de escribirse después de volver del reproductor
        function onCapturaGuardada(ok) { if (ok && pagina.StackView.status === StackView.Active) pagina.recargar() }
    }
    readonly property var directores: p.directores || []
    readonly property var actores: p.actores || []
    readonly property var capturas: p.capturas || []

    component Meta: Text {
        font.family: Tema.rotulo
        font.pixelSize: Tema.px(16)
        font.capitalization: Font.AllUppercase
        font.letterSpacing: 0.8
        color: Tema.tenue
    }
    component Rotulo: Text {
        Layout.alignment: Qt.AlignTop
        Layout.topMargin: Tema.px(2)
        font.family: Tema.rotulo
        font.pixelSize: Tema.px(13)
        font.weight: Font.DemiBold
        font.letterSpacing: 1
        font.capitalization: Font.AllUppercase
        color: Tema.tenue
    }

    // Nombres separados por comas; los que están en otras películas de la biblioteca llevan a su listado
    component Personas: Flow {
        id: flujo
        property var personas: []
        Layout.fillWidth: true
        Repeater {
            model: flujo.personas
            delegate: Text {
                id: nombre
                required property var modelData
                required property int index
                readonly property bool enlace: modelData.otras > 0
                text: modelData.nombre + (index < flujo.personas.length - 1 ? ",\u00a0" : "")
                font.family: Tema.texto
                font.pixelSize: Tema.px(15)
                lineHeight: 1.25
                color: Tema.crema
                // Subrayado tenue que se enciende al pasar el mouse; la coma queda afuera
                Rectangle {
                    visible: nombre.enlace
                    x: 0
                    y: nombre.font.pixelSize * 1.2
                    width: medida.advanceWidth
                    height: 1
                    color: zonaNombre.containsMouse ? Tema.crema : Qt.alpha(Tema.crema, 0.35)
                }
                TextMetrics { id: medida; font: nombre.font; text: nombre.modelData.nombre }
                MouseArea {
                    id: zonaNombre
                    enabled: nombre.enlace
                    width: medida.advanceWidth
                    height: parent.height
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: pagina.StackView.view.push("Persona.qml", { nombre: nombre.modelData.nombre })
                }
            }
        }
    }
    function reproducirPelicula() { pagina.StackView.view.push("Reproductor.qml", { peliculaId: pagina.peliculaId }) }
    function formatear(ms) {
        const s = Math.floor(ms / 1000)
        const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60
        return (h > 0 ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(s % 60).padStart(2, "0")
    }

    // Hora a la que termina si se empieza (o continúa) ahora; se refresca cada 20 s
    property date ahora: new Date()
    Timer {
        interval: 20000
        repeat: true
        running: pagina.StackView.status === StackView.Active
        onTriggered: pagina.ahora = new Date()
    }
    readonly property string horaFin: p.duracion > 0
        ? Qt.formatTime(new Date(ahora.getTime() + Math.max(0, p.duracion - p.progreso)), "HH:mm") : ""

    Component.onCompleted: { recargar(); reproducir.forceActiveFocus() }
    StackView.onActivated: { ahora = new Date(); recargar(); reproducir.forceActiveFocus() }

    background: Rectangle { color: Tema.noche }

    header: Rectangle {
        implicitHeight: Tema.px(68)
        color: Tema.noche
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Tema.linea }
        Boton {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: Tema.px(40)
            text: "Volver"
            icono: "volver"
            focusPolicy: Qt.TabFocus
            onClicked: pagina.StackView.view.pop()
        }
        Text {
            id: aviso
            visible: false
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: Tema.px(40)
            color: Tema.crema
            font.family: Tema.texto
            font.pixelSize: Tema.px(14)
            Timer { id: ocultarAviso; interval: 4000; onTriggered: aviso.visible = false }
        }
    }

    // Confirmación breve en la barra, ej. al volver de «Editar datos»
    function avisar(texto) {
        aviso.text = texto
        aviso.visible = true
        ocultarAviso.restart()
    }

    Shortcut {
        sequence: "Esc"
        enabled: pagina.StackView.status === StackView.Active
        onActivated: pagina.StackView.view.pop()
    }

    Flickable {
        anchors.fill: parent
        contentHeight: (seccionCapturas.visible ? seccionCapturas.y + seccionCapturas.height : fila.y + fila.height)
                       + Tema.px(40)
        clip: true
        ScrollBar.vertical: ScrollBar {}

        RowLayout {
            id: fila
            x: Tema.px(40)
            y: Tema.px(40)
            width: parent.width - Tema.px(80)
            spacing: Tema.px(40)

            Rectangle {
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: Tema.px(280)
                Layout.preferredHeight: Tema.px(420)
                radius: Tema.px(2)
                color: Tema.caja
                clip: true
                Text {
                    visible: poster.status !== Image.Ready
                    anchors.fill: parent
                    anchors.margins: Tema.px(20)
                    text: pagina.p.titulo || ""
                    wrapMode: Text.WordWrap
                    verticalAlignment: Text.AlignBottom
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(28)
                    font.weight: Font.Bold
                    font.capitalization: Font.AllUppercase
                    color: Tema.tenue
                }
                Image {
                    id: poster
                    anchors.fill: parent
                    source: pagina.p.poster || ""
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    sourceSize.width: 640
                }
                // Play sobre el poster: excepción a la Regla de la Etiqueta Única pedida por el usuario
                AbstractButton {
                    id: playPoster
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.margins: Tema.px(14)
                    width: Tema.px(52)
                    height: width
                    focusPolicy: Qt.NoFocus
                    hoverEnabled: true
                    Accessible.name: reproducir.text
                    onClicked: pagina.reproducirPelicula()
                    background: Rectangle {
                        radius: width / 2
                        color: playPoster.down ? Qt.darker(Tema.etiqueta, 1.15)
                               : playPoster.hovered ? Qt.lighter(Tema.etiqueta, 1.08) : Tema.etiqueta
                    }
                    contentItem: Item {
                        Image {
                            anchors.centerIn: parent
                            anchors.horizontalCenterOffset: Tema.px(2)  // el triángulo se ve centrado corrido un poco a la derecha
                            source: "iconos/play-oscuro.svg"
                            sourceSize: Qt.size(Tema.px(24), Tema.px(24))
                        }
                    }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }
            }

            ColumnLayout {
                Layout.alignment: Qt.AlignTop
                Layout.fillWidth: true
                Layout.maximumWidth: Tema.px(860)
                spacing: Tema.px(16)

                Text {
                    Layout.fillWidth: true
                    text: pagina.p.titulo || ""
                    wrapMode: Text.WordWrap
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(40)
                    font.weight: Font.Bold
                    font.capitalization: Font.AllUppercase
                    lineHeight: 0.95
                    color: Tema.crema
                }
                Flow {
                    id: meta
                    readonly property var paises: Paises.separar(pagina.p.pais)
                    Layout.fillWidth: true
                    spacing: Tema.px(10)
                    Meta {
                        readonly property string base: [pagina.p.anio || "", pagina.p.genero, Duracion.texto(pagina.p.duracion)].filter(x => x).join("   *   ")
                        visible: base !== ""
                        text: base + (meta.paises.length ? "   *" : "")
                    }
                    Repeater {
                        model: meta.paises
                        // Solo la bandera, con el nombre al pasar el mouse; un país sin mapear queda como texto
                        Item {
                            id: pais
                            readonly property bool conBandera: modelData.codigo !== ""
                            width: conBandera ? bandera.width : nombrePais.width
                            height: nombrePais.height
                            Image {
                                id: bandera
                                anchors.verticalCenter: parent.verticalCenter
                                visible: pais.conBandera
                                source: visible ? "banderas/" + modelData.codigo + ".svg" : ""
                                sourceSize: Qt.size(Tema.px(20), Tema.px(15))
                            }
                            Meta { id: nombrePais; visible: !pais.conBandera; text: modelData.nombre }
                            HoverHandler { id: sobrePais; enabled: pais.conBandera }
                            ToolTip.visible: sobrePais.hovered
                            ToolTip.text: modelData.nombre
                            ToolTip.delay: 300
                        }
                    }
                }
                Text {
                    // Pendiente se resuelve sola en el próximo escaneo con internet; no encontrada pide buscarla
                    readonly property var avisos: ({
                        pendiente: "Faltan los datos de esta película: se completan la próxima vez que escanees con internet, o cargalos desde «…» › «Editar datos».",
                        no_encontrada: "No encontramos los datos de esta película. Buscala en IMDb o cargalos a mano desde «…» › «Editar datos»."
                    })
                    visible: text !== ""
                    Layout.fillWidth: true
                    text: avisos[pagina.p.omdbEstado] || ""
                    wrapMode: Text.WordWrap
                    font.family: Tema.texto
                    font.pixelSize: Tema.px(14)
                    color: Tema.alerta
                }

                Flow {
                    Layout.fillWidth: true
                    Layout.topMargin: Tema.px(8)
                    spacing: Tema.px(12)
                    Boton {
                        id: reproducir
                        principal: true
                        icono: "play"
                        text: pagina.p.progreso > 0 ? "Continuar desde " + pagina.formatear(pagina.p.progreso) : "Reproducir"
                        KeyNavigation.right: marcar
                        onClicked: pagina.reproducirPelicula()
                    }
                    Boton {
                        id: marcar
                        icono: pagina.p.vista ? "visto" : ""
                        text: pagina.p.vista ? "Vista" : "Marcar como vista"
                        KeyNavigation.left: reproducir
                        KeyNavigation.right: mas
                        onClicked: { puente.marcarVista(pagina.peliculaId, !pagina.p.vista); pagina.recargar() }
                    }
                    BotonMas {
                        id: mas
                        KeyNavigation.left: marcar
                        OpcionMenu {
                            text: "Editar datos"
                            icono: "editar"
                            onTriggered: pagina.StackView.view.push("Editar.qml", { peliculaId: pagina.peliculaId })
                        }
                        OpcionMenu {
                            text: "Abrir carpeta"
                            icono: "carpeta"
                            onTriggered: puente.abrirCarpeta(pagina.peliculaId)
                        }
                        OpcionMenu {
                            text: "Abrir en otro reproductor"
                            icono: "abrir"
                            onTriggered: puente.abrirConSistema(pagina.peliculaId)
                        }
                    }
                }
                Text {
                    visible: pagina.horaFin !== ""
                    text: (pagina.p.progreso > 0 ? "Si seguís ahora, termina a las " : "Si empezás ahora, termina a las ")
                          + pagina.horaFin
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(15)
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 0.6
                    font.features: { "tnum": 1 }
                    color: Tema.tenue
                }

                Text {
                    visible: !!pagina.p.sinopsis
                    Layout.fillWidth: true
                    Layout.topMargin: Tema.px(14)
                    text: pagina.p.sinopsis || ""
                    wrapMode: Text.WordWrap
                    lineHeight: 1.35
                    font.family: Tema.texto
                    font.pixelSize: Tema.px(15)
                    color: Tema.crema
                }

                GridLayout {
                    Layout.topMargin: Tema.px(8)
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: Tema.px(18)
                    rowSpacing: Tema.px(10)

                    Rotulo { visible: pagina.directores.length > 0; text: "Dirección" }
                    Personas { visible: pagina.directores.length > 0; personas: pagina.directores }
                    Rotulo { visible: pagina.actores.length > 0; text: "Elenco" }
                    Personas { visible: pagina.actores.length > 0; personas: pagina.actores }
                }
            }
        }

        // Cuadros guardados con «.» en el reproductor; solo para mirar
        Column {
            id: seccionCapturas
            visible: pagina.capturas.length > 0
            x: fila.x
            y: fila.y + fila.height + Tema.px(48)
            width: fila.width
            spacing: Tema.px(14)

            Rotulo { text: "Capturas" }
            Flow {
                width: parent.width
                spacing: Tema.px(12)
                Repeater {
                    model: pagina.capturas
                    // Ancho fijo y alto según la proporción del cuadro; 16:9 mientras carga
                    delegate: Image {
                        required property string modelData
                        width: Tema.px(160)
                        height: status === Image.Ready ? width * implicitHeight / implicitWidth : width * 9 / 16
                        source: modelData
                        fillMode: Image.PreserveAspectFit
                        asynchronous: true
                        sourceSize.width: 320
                    }
                }
            }
        }
    }
}
