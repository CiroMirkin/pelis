import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

ApplicationWindow {
    id: win
    width: 1280
    height: 720
    visible: true
    color: "black"
    title: backend.titulo

    // 0 = ninguno, 1 = externo, 2 = embebido
    property int modoSubs: 0
    property bool controlesVisibles: true
    // QtMultimedia vuelve a emitir LoadedMedia al cambiar de pista; la elección automática va una sola vez
    property bool inicializado: false
    readonly property bool pantallaCompleta: visibility === Window.FullScreen

    function formatear(ms) {
        const s = Math.floor(ms / 1000)
        const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, seg = s % 60
        return (h > 0 ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(seg).padStart(2, "0")
    }

    function etiquetaPista(md, i) {
        const partes = [md.stringValue(MediaMetaData.Title), md.stringValue(MediaMetaData.Language)].filter(x => x)
        return "#" + (i + 1) + (partes.length ? " · " + partes.join(" · ") : "")
    }

    function alternarPantallaCompleta() {
        win.visibility = pantallaCompleta ? Window.Windowed : Window.FullScreen
    }

    function elegirSubs(indice) {
        // indice del combo: 0 = ninguno, luego externos, luego embebidos
        const nExt = backend.externos.length
        if (indice === 0) {
            modoSubs = 0; backend.cargarExterno(-1); player.activeSubtitleTrack = -1
        } else if (indice <= nExt) {
            modoSubs = 1; player.activeSubtitleTrack = -1; backend.cargarExterno(indice - 1)
        } else {
            modoSubs = 2; backend.cargarExterno(-1); player.activeSubtitleTrack = indice - 1 - nExt
        }
    }

    MediaPlayer {
        id: player
        source: backend.videoUrl
        videoOutput: backend.entrada
        audioOutput: AudioOutput { id: salidaAudio; volume: backend.autotest ? 0 : 1 }
        onErrorOccurred: (error, errorString) => {
            errorTexto.text = "Error: " + errorString
            console.log("[proto] ERROR", error, errorString)
        }
        onMediaStatusChanged: {
            if (mediaStatus === MediaPlayer.LoadedMedia && !inicializado) {
                inicializado = true
                const ext = backend.externoMismoNombre
                const indice = ext >= 0 ? ext + 1 : 0
                comboSubs.currentIndex = indice
                elegirSubs(indice)
                play()
            }
        }
    }

    VideoOutput {
        id: video
        anchors.fill: parent
        Component.onCompleted: backend.setSalida(video.videoSink)
    }

    // Overlay propio de subtítulos (externos y embebidos)
    Text {
        id: subtitulo
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: controlesVisibles ? barra.height + 24 : 48
        width: parent.width * 0.85
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WordWrap
        color: "white"
        style: Text.Outline
        styleColor: "black"
        font.pixelSize: Math.max(22, win.height / 22)
        text: modoSubs === 1 ? backend.textoEn(player.position)
            : modoSubs === 2 ? backend.textoEmbebido : ""
    }

    Text {
        id: errorTexto
        anchors.centerIn: parent
        color: "#ff7070"
        font.pixelSize: 20
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: controlesVisibles ? Qt.ArrowCursor : Qt.BlankCursor
        onPositionChanged: { controlesVisibles = true; ocultar.restart() }
        onClicked: player.playbackState === MediaPlayer.PlayingState ? player.pause() : player.play()
        onDoubleClicked: alternarPantallaCompleta()
    }

    Timer {
        id: ocultar
        interval: 3000
        running: true
        onTriggered: if (!barra.hovered) controlesVisibles = false
    }

    Rectangle {
        id: barra
        property bool hovered: hoverBarra.hovered
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 96
        opacity: controlesVisibles ? 1 : 0
        visible: opacity > 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
        gradient: Gradient {
            GradientStop { position: 0; color: "transparent" }
            GradientStop { position: 1; color: "#cc000000" }
        }
        HoverHandler { id: hoverBarra }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 4

            RowLayout {
                Layout.fillWidth: true
                Label { text: formatear(player.position); color: "white" }
                Slider {
                    id: seek
                    Layout.fillWidth: true
                    from: 0
                    to: Math.max(1, player.duration)
                    value: pressed ? value : player.position
                    onMoved: player.position = value
                }
                Label { text: formatear(player.duration); color: "white" }
            }

            RowLayout {
                Layout.fillWidth: true
                Button {
                    text: player.playbackState === MediaPlayer.PlayingState ? "Pausa" : "Play"
                    onClicked: player.playbackState === MediaPlayer.PlayingState ? player.pause() : player.play()
                }
                Item { Layout.fillWidth: true }
                Label { text: "Audio"; color: "white" }
                ComboBox {
                    id: comboAudio
                    Layout.preferredWidth: 220
                    model: player.audioTracks.map((md, i) => etiquetaPista(md, i))
                    currentIndex: player.activeAudioTrack
                    onActivated: (i) => player.activeAudioTrack = i
                }
                Label { text: "Subtítulos"; color: "white" }
                ComboBox {
                    id: comboSubs
                    Layout.preferredWidth: 280
                    model: ["Ninguno"]
                        .concat(backend.externos.map(n => "Externo · " + n))
                        .concat(player.subtitleTracks.map((md, i) => "Embebido " + etiquetaPista(md, i)))
                    onActivated: (i) => elegirSubs(i)
                }
                Button {
                    text: pantallaCompleta ? "Salir" : "Pantalla completa"
                    onClicked: alternarPantallaCompleta()
                }
            }
        }
    }

    Shortcut { sequence: "Space"; onActivated: player.playbackState === MediaPlayer.PlayingState ? player.pause() : player.play() }
    Shortcut { sequence: "Left"; onActivated: player.position = Math.max(0, player.position - 10000) }
    Shortcut { sequence: "Right"; onActivated: player.position = Math.min(player.duration, player.position + 10000) }
    Shortcut { sequence: "F"; onActivated: alternarPantallaCompleta() }
    Shortcut { sequence: "Esc"; onActivated: pantallaCompleta ? alternarPantallaCompleta() : Qt.quit() }

    // --autotest: recorre el criterio de terminado y escribe los resultados en la consola
    property int paso: 0
    property var textosEmbebidos: []
    Connections {
        target: backend
        enabled: backend.autotest
        function onTextoEmbebidoChanged() {
            if (backend.textoEmbebido && textosEmbebidos.length < 5) textosEmbebidos.push(backend.textoEmbebido)
        }
    }
    Timer {
        id: chequeoExterno
        interval: 700
        onTriggered: console.log("[proto] externo texto en pantalla:", JSON.stringify(subtitulo.text), "en", player.position)
    }
    Timer {
        running: backend.autotest
        interval: 3000
        repeat: true
        onTriggered: {
            const log = (...a) => console.log("[proto]", ...a)
            switch (paso++) {
            case 0:
                log("duracion", formatear(player.duration), "video", player.hasVideo, "estado", player.mediaStatus)
                log("audio", JSON.stringify(player.audioTracks.map((md, i) => etiquetaPista(md, i))), "activa", player.activeAudioTrack)
                log("subs embebidos", JSON.stringify(player.subtitleTracks.map((md, i) => etiquetaPista(md, i))))
                log("subs externos", JSON.stringify(backend.externos), "activado", backend.externoMismoNombre)
                log("posicion tras 3s", player.position, "salida de audio", salidaAudio.device.description, "volumen", salidaAudio.volume)
                player.pause()
                break
            case 1:
                log("pausado", player.playbackState === MediaPlayer.PausedState, "posicion", player.position)
                player.position = Math.floor(player.duration / 2)
                player.play()
                break
            case 2:
                log("seek a la mitad -> posicion", player.position)
                if (player.audioTracks.length > 1) player.activeAudioTrack = 1
                if (backend.externos.length > 0) {
                    elegirSubs(1)
                    const t = backend.eventoDesde(player.position + 1000)
                    if (t >= 0) { player.position = t + 300; chequeoExterno.start() }
                }
                break
            case 3:
                log("audio activa", player.activeAudioTrack)
                log("externo codificacion", backend.codificacion, "eventos", backend.cantidadEventos)
                if (player.subtitleTracks.length > 0) {
                    elegirSubs(1 + backend.externos.length)
                    player.position = Math.floor(player.duration / 3)
                }
                win.visibility = Window.FullScreen
                break
            case 4:
            case 5:
            case 6:
                break
            case 7:
                log("pantalla completa", pantallaCompleta, win.width + "x" + win.height)
                log("embebidos recibidos", JSON.stringify(textosEmbebidos))
                log("embebido texto en pantalla:", JSON.stringify(subtitulo.text), "modo", modoSubs, "pista", player.activeSubtitleTrack, "emb", JSON.stringify(backend.textoEmbebido))
                Qt.quit()
            }
        }
    }
}
