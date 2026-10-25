import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtMultimedia

Page {
    id: pagina
    required property int peliculaId
    property var info: ({})
    // 0 = ninguno, 1 = externo, 2 = embebido
    property int modoSubs: 0
    property int revisionExterno: 0
    property bool controlesVisibles: true
    // QtMultimedia vuelve a emitir LoadedMedia al cambiar de pista; la carga inicial va una sola vez
    property bool inicializado: false
    readonly property bool reproduciendo: player.playbackState === MediaPlayer.PlayingState
    readonly property bool pantallaCompleta: Window.window && Window.window.visibility === Window.FullScreen

    background: Rectangle { color: "black" }

    function formatear(ms) {
        const s = Math.floor(ms / 1000)
        const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60
        return (h > 0 ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(s % 60).padStart(2, "0")
    }

    function pista(md) {
        return { idioma: md.stringValue(MediaMetaData.Language), titulo: md.stringValue(MediaMetaData.Title) }
    }

    // Nombres en español para las pistas; QtMultimedia los da en inglés
    readonly property var idiomas: ({
        "es": "Español", "en": "Inglés", "Spanish": "Español", "English": "Inglés", "French": "Francés",
        "Italian": "Italiano", "German": "Alemán", "Portuguese": "Portugués", "Japanese": "Japonés",
        "Korean": "Coreano", "Chinese": "Chino", "Russian": "Ruso", "Ukrainian": "Ucraniano",
        "Polish": "Polaco", "Dutch": "Neerlandés", "Swedish": "Sueco", "Danish": "Danés",
        "Norwegian": "Noruego", "Finnish": "Finlandés", "Turkish": "Turco", "Hindi": "Hindi",
        "Persian": "Persa", "Arabic": "Árabe", "Hebrew": "Hebreo", "Greek": "Griego"
    })

    function opcionPista(md, i, base) {
        const p = pista(md)
        return { nombre: idiomas[p.idioma] || p.idioma || base + " " + (i + 1), detalle: p.titulo }
    }

    readonly property var opcionesAudio: player.audioTracks.map((md, i) => opcionPista(md, i, "Pista"))
    readonly property var opcionesSubs: [{ nombre: "Sin subtítulos", detalle: "" }]
        .concat((info.externos || []).map(n => ({ nombre: idiomas[puente.idiomaDe(n)] || "Archivo de subtítulos", detalle: n })))
        .concat(player.subtitleTracks.map((md, i) => opcionPista(md, i, "Subtítulo")))
    property int indiceSubs: 0

    // Hora estimada de fin: ahora + lo que falta. Pausado, el reloj sigue y la hora se corre.
    property date ahora: new Date()
    Timer { interval: 1000; repeat: true; running: pagina.activa; onTriggered: pagina.ahora = new Date() }
    readonly property string horaFin: player.duration > 0
        ? Qt.formatTime(new Date(ahora.getTime() + Math.max(0, player.duration - player.position)), "HH:mm") : ""

    function guardarProgreso() {
        if (inicializado)
            puente.guardarProgreso(peliculaId, player.position)
    }

    function alternarPausa() {
        reproduciendo ? player.pause() : player.play()
    }

    function alternarPantallaCompleta() {
        Window.window.visibility = pantallaCompleta ? Window.Windowed : Window.FullScreen
    }

    function salir() {
        guardarProgreso()
        player.stop()
        if (pantallaCompleta) alternarPantallaCompleta()
        pagina.StackView.view.pop()
    }

    function abrirPistas() { panel.open() }

    function saltar(ms) {
        player.position = Math.max(0, Math.min(player.duration, player.position + ms))
        mostrarControles()
    }

    function cambiarVolumen(delta) {
        puente.volumen = Math.max(0, Math.min(1, Math.round((puente.volumen + delta) * 20) / 20))
        puente.silenciado = false
        mostrarControles()
    }

    function mostrarControles() {
        controlesVisibles = true
        ocultar.restart()
    }

    // índice del combo: 0 = ninguno, luego externos, luego embebidos
    function elegirSubs(indice) {
        const nExt = info.externos.length
        errorSubs.text = ""
        if (indice <= 0) {
            modoSubs = 0
            puente.cargarExterno(-1)
            player.activeSubtitleTrack = -1
        } else if (indice <= nExt) {
            modoSubs = 1
            player.activeSubtitleTrack = -1
            errorSubs.text = puente.cargarExterno(indice - 1)
        } else {
            modoSubs = 2
            puente.cargarExterno(-1)
            player.activeSubtitleTrack = indice - 1 - nExt
        }
        revisionExterno++
        indiceSubs = indice
    }

    function cargaInicial() {
        inicializado = true
        if (player.duration > 0)
            puente.guardarDuracion(peliculaId, player.duration)
        const e = puente.eleccionInicial(player.audioTracks.map(pista), player.subtitleTracks.map(pista))
        if (e.audio >= 0)
            player.activeAudioTrack = e.audio
        if (e.subTipo === "externo")
            elegirSubs(1 + e.subIndice)
        else if (e.subTipo === "embebido")
            elegirSubs(1 + info.externos.length + e.subIndice)
        else
            elegirSubs(0)
        if (info.progreso > 0)
            player.position = info.progreso
        player.play()
    }

    Component.onCompleted: {
        info = puente.abrir(peliculaId)
        player.source = info.url
    }

    MediaPlayer {
        id: player
        videoOutput: video
        audioOutput: AudioOutput {
            // El deslizador va en escala de percepción; la salida espera amplitud lineal
            volume: Math.pow(puente.volumen, 3)
            muted: puente.silenciado
        }
        onErrorOccurred: (error, errorString) => { errorVideo.text = "No se pudo reproducir: " + errorString }
        onMediaStatusChanged: {
            if (mediaStatus === MediaPlayer.LoadedMedia && !pagina.inicializado)
                pagina.cargaInicial()
        }
        onPlaybackStateChanged: {
            if (playbackState === MediaPlayer.PausedState) {
                pagina.guardarProgreso()
                pagina.mostrarControles()
            }
        }
    }

    VideoOutput {
        id: video
        anchors.fill: parent
    }

    // Overlay propio de subtítulos externos. Los embebidos los dibuja el VideoOutput: pasar los
    // frames por un sink intermedio para quitarles el texto los copiaba a RAM y la peli se trababa.
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: pagina.controlesVisibles ? barra.height + 16 : 48
        width: parent.width * 0.85
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WordWrap
        color: puente.subsColor
        style: Text.Outline
        styleColor: "black"
        font.family: Tema.texto
        font.bold: true
        font.pixelSize: Math.max(20, pagina.height / 24) * puente.subsTamano
        text: pagina.modoSubs === 1 ? (pagina.revisionExterno, puente.textoEn(player.position)) : ""
    }

    Label {
        id: errorVideo
        anchors.centerIn: parent
        width: parent.width * 0.8
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WordWrap
        color: Tema.alerta
        font.family: Tema.texto
        font.pixelSize: Tema.px(20)
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: pagina.controlesVisibles ? Qt.ArrowCursor : Qt.BlankCursor
        onPositionChanged: pagina.mostrarControles()
        onClicked: pagina.alternarPausa()
        onDoubleClicked: pagina.alternarPantallaCompleta()
    }

    Timer {
        id: ocultar
        interval: 3000
        running: true
        onTriggered: {
            if (pagina.reproduciendo && !hoverArriba.hovered && !hoverBarra.hovered && !panel.visible)
                pagina.controlesVisibles = false
            else
                restart()
        }
    }

    // Barra superior: volver y título
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Tema.px(68)
        opacity: pagina.controlesVisibles ? 1 : 0
        visible: opacity > 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
        gradient: Gradient {
            GradientStop { position: 0; color: "#cc000000" }
            GradientStop { position: 1; color: "transparent" }
        }
        HoverHandler { id: hoverArriba }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Tema.px(32)
            anchors.rightMargin: Tema.px(32)
            spacing: Tema.px(20)
            Boton { text: "Volver"; icono: "volver"; focusPolicy: Qt.NoFocus; onClicked: pagina.salir() }
            Text {
                Layout.fillWidth: true
                text: pagina.info.titulo || ""
                elide: Text.ElideRight
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(20)
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
                color: Tema.crema
            }
            Boton {
                soloIcono: true
                icono: pagina.pantallaCompleta ? "ventana" : "pantalla"
                text: pagina.pantallaCompleta ? "Salir de pantalla completa" : "Pantalla completa"
                focusPolicy: Qt.NoFocus
                onClicked: pagina.alternarPantallaCompleta()
            }
        }
    }

    // Barra inferior: controles
    Rectangle {
        id: barra
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: Tema.px(100)
        opacity: pagina.controlesVisibles ? 1 : 0
        visible: opacity > 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
        gradient: Gradient {
            GradientStop { position: 0; color: "transparent" }
            GradientStop { position: 1; color: "#dd000000" }
        }
        HoverHandler { id: hoverBarra }

        ColumnLayout {
            anchors.fill: parent
            anchors.leftMargin: Tema.px(32)
            anchors.rightMargin: Tema.px(32)
            anchors.bottomMargin: Tema.px(14)
            spacing: Tema.px(4)

            RowLayout {
                Layout.fillWidth: true
                Text { text: pagina.formatear(player.position); color: Tema.crema; font.family: Tema.rotulo; font.pixelSize: Tema.px(15); font.features: { "tnum": 1 } }
                Slider {
                    id: seek
                    Layout.fillWidth: true
                    from: 0
                    to: Math.max(1, player.duration)
                    value: pressed ? value : player.position
                    onMoved: player.position = value
                }
                Text { text: pagina.formatear(player.duration); color: Tema.tenue; font.family: Tema.rotulo; font.pixelSize: Tema.px(15); font.features: { "tnum": 1 } }
                Text {
                    visible: pagina.horaFin !== ""
                    Layout.leftMargin: Tema.px(10)
                    text: "Termina " + pagina.horaFin
                    color: Tema.tenue
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(15)
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 0.6
                    font.features: { "tnum": 1 }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Boton {
                    soloIcono: true
                    principal: true
                    icono: pagina.reproduciendo ? "pausa" : "play"
                    text: pagina.reproduciendo ? "Pausa" : "Reproducir"
                    focusPolicy: Qt.NoFocus
                    onClicked: pagina.alternarPausa()
                }
                Boton {
                    Layout.leftMargin: Tema.px(12)
                    soloIcono: true
                    icono: puente.silenciado || puente.volumen === 0 ? "silencio" : "volumen"
                    text: puente.silenciado ? "Activar sonido" : "Silenciar"
                    focusPolicy: Qt.NoFocus
                    onClicked: puente.silenciado = !puente.silenciado
                }
                Slider {
                    Layout.preferredWidth: Tema.px(120)
                    from: 0
                    to: 1
                    focusPolicy: Qt.NoFocus
                    value: pressed ? value : (puente.silenciado ? 0 : puente.volumen)
                    onMoved: { puente.volumen = value; puente.silenciado = false }
                }
                Text {
                    Layout.preferredWidth: Tema.px(44)
                    text: puente.silenciado ? "—" : Math.round(puente.volumen * 100) + "%"
                    color: Tema.tenue
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(15)
                    font.features: { "tnum": 1 }
                }
                Text { id: errorSubs; color: Tema.alerta; font.family: Tema.texto; font.pixelSize: Tema.px(13); Layout.fillWidth: true; elide: Text.ElideRight }
                Boton {
                    id: botonPistas
                    icono: "pistas"
                    text: "Audio y subtítulos"
                    focusPolicy: Qt.NoFocus
                    onClicked: panel.visible ? panel.close() : panel.open()
                }
            }
        }
    }

    // Audio y subtítulos: un panel sobre la barra, con dos listas
    Popup {
        id: panel
        x: pagina.width - width - Tema.px(32)
        y: barra.y - height + Tema.px(8)
        width: Math.min(Tema.px(560), pagina.width - Tema.px(64))
        padding: Tema.px(20)
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
        background: Rectangle {
            color: Qt.alpha(Tema.estante, 0.97)
            radius: Tema.px(4)
            border.width: 1
            border.color: Tema.linea
        }

        component Lista: ColumnLayout {
            id: lista
            property string titulo
            property var opciones: []
            property int actual: -1
            signal elegida(int indice)
            spacing: Tema.px(2)

            Text {
                text: lista.titulo
                bottomPadding: Tema.px(8)
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(14)
                font.weight: Font.DemiBold
                font.letterSpacing: 1
                font.capitalization: Font.AllUppercase
                color: Tema.tenue
            }
            Repeater {
                model: lista.opciones
                delegate: Rectangle {
                    required property int index
                    required property var modelData
                    readonly property bool elegida: index === lista.actual
                    Layout.fillWidth: true
                    implicitHeight: renglon.implicitHeight + Tema.px(14)
                    radius: Tema.px(3)
                    color: zona.containsMouse ? Tema.caja : "transparent"

                    Rectangle {
                        anchors.left: parent.left
                        anchors.leftMargin: Tema.px(8)
                        anchors.verticalCenter: parent.verticalCenter
                        width: Tema.px(8)
                        height: width
                        color: Tema.etiqueta
                        visible: parent.elegida
                    }
                    Column {
                        id: renglon
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.leftMargin: Tema.px(26)
                        anchors.rightMargin: Tema.px(8)
                        anchors.verticalCenter: parent.verticalCenter
                        Text {
                            width: parent.width
                            text: modelData.nombre
                            elide: Text.ElideRight
                            font.family: Tema.texto
                            font.pixelSize: Tema.px(15)
                            font.bold: parent.parent.elegida
                            color: Tema.crema
                        }
                        Text {
                            visible: !!modelData.detalle
                            width: parent.width
                            text: modelData.detalle || ""
                            elide: Text.ElideMiddle
                            font.family: Tema.texto
                            font.pixelSize: Tema.px(12)
                            color: Tema.tenue
                        }
                    }
                    MouseArea {
                        id: zona
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: lista.elegida(index)
                    }
                }
            }
        }

        // Estilo de subtítulos: global, se guarda en preferencias.ini
        readonly property var tamanos: [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
        readonly property var colores: ["#ffffff", "#ffe14d", "#66e0ff", "#7dff8a", "#ff9ad5"]
        function cambiarTamano(paso) {
            const i = tamanos.findIndex(t => Math.abs(t - puente.subsTamano) < 0.01)
            puente.subsTamano = tamanos[Math.max(0, Math.min(tamanos.length - 1, (i < 0 ? 2 : i) + paso))]
        }

        component Rotulo: Text {
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(14)
            font.weight: Font.DemiBold
            font.letterSpacing: 1
            font.capitalization: Font.AllUppercase
            color: Tema.tenue
        }

        ColumnLayout {
            width: panel.availableWidth
            spacing: Tema.px(16)
            RowLayout {
                Layout.fillWidth: true
                spacing: Tema.px(24)
                Lista {
                    Layout.alignment: Qt.AlignTop
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    titulo: "Audio"
                    opciones: pagina.opcionesAudio
                    actual: Math.max(0, player.activeAudioTrack)
                    onElegida: (i) => player.activeAudioTrack = i
                }
                Rectangle { Layout.fillHeight: true; width: 1; color: Tema.linea }
                Lista {
                    Layout.alignment: Qt.AlignTop
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    titulo: "Subtítulos"
                    opciones: pagina.opcionesSubs
                    actual: pagina.indiceSubs
                    onElegida: (i) => pagina.elegirSubs(i)
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Tema.linea }
            RowLayout {
                Layout.fillWidth: true
                spacing: Tema.px(12)
                Rotulo { text: "Tamaño" }
                Boton {
                    text: "−"
                    enabled: puente.subsTamano > panel.tamanos[0] + 0.01
                    focusPolicy: Qt.NoFocus
                    onClicked: panel.cambiarTamano(-1)
                }
                Text {
                    Layout.preferredWidth: Tema.px(52)
                    horizontalAlignment: Text.AlignHCenter
                    text: Math.round(puente.subsTamano * 100) + "%"
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(16)
                    font.features: { "tnum": 1 }
                    color: Tema.crema
                }
                Boton {
                    text: "+"
                    enabled: puente.subsTamano < panel.tamanos[panel.tamanos.length - 1] - 0.01
                    focusPolicy: Qt.NoFocus
                    onClicked: panel.cambiarTamano(1)
                }
                Item { Layout.fillWidth: true }
                Rotulo { text: "Color" }
                Repeater {
                    model: panel.colores
                    delegate: Rectangle {
                        required property string modelData
                        readonly property bool elegido: modelData.toLowerCase() === puente.subsColor.toLowerCase()
                        width: Tema.px(26)
                        height: width
                        radius: width / 2
                        color: modelData
                        border.width: elegido ? Tema.px(3) : 1
                        border.color: elegido ? Tema.etiqueta : Tema.linea
                        MouseArea {
                            anchors.fill: parent
                            anchors.margins: -Tema.px(4)
                            cursorShape: Qt.PointingHandCursor
                            onClicked: puente.subsColor = parent.modelData
                        }
                    }
                }
            }
            Text {
                visible: pagina.modoSubs === 2
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: "Los subtítulos que vienen dentro del archivo usan su propio estilo; el tamaño y el color se aplican a los externos."
                font.family: Tema.texto
                font.pixelSize: Tema.px(13)
                color: Tema.tenue
            }
        }
    }

    readonly property bool activa: pagina.StackView.status === StackView.Active
    Shortcut { enabled: pagina.activa; sequence: "Space"; onActivated: { pagina.alternarPausa(); pagina.mostrarControles() } }
    Shortcut { enabled: pagina.activa; sequence: "Left"; onActivated: pagina.saltar(-10000) }
    Shortcut { enabled: pagina.activa; sequence: "Right"; onActivated: pagina.saltar(10000) }
    Shortcut { enabled: pagina.activa; sequence: "Ctrl+Left"; onActivated: pagina.saltar(-60000) }
    Shortcut { enabled: pagina.activa; sequence: "Ctrl+Right"; onActivated: pagina.saltar(60000) }
    Shortcut { enabled: pagina.activa; sequence: "Up"; onActivated: pagina.cambiarVolumen(0.05) }
    Shortcut { enabled: pagina.activa; sequence: "Down"; onActivated: pagina.cambiarVolumen(-0.05) }
    Shortcut { enabled: pagina.activa; sequence: "M"; onActivated: { puente.silenciado = !puente.silenciado; pagina.mostrarControles() } }
    Shortcut { enabled: pagina.activa; sequence: "F"; onActivated: pagina.alternarPantallaCompleta() }
    Shortcut {
        enabled: pagina.activa
        sequence: "Esc"
        onActivated: panel.visible ? panel.close() : pagina.pantallaCompleta ? pagina.alternarPantallaCompleta() : pagina.salir()
    }
}
