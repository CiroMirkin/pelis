pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Visor de capturas: una por vez, ajustada a la ventana sobre negro. Se pasa con los botones de
// los lados, ←/→ o arrastrando; es circular. «Ir a» abre el reproductor en ese momento.
Page {
    id: pagina
    required property var capturas  // [{ url, momento }] en el orden de la grilla del detalle
    required property int indice
    required property int peliculaId
    property bool controlesVisibles: true
    // Arranca apagada en cada apertura y queda como está al pasar de captura
    property bool tercios: false
    // Corrimiento horizontal del carril de imágenes: lo arrastrado o lo animado
    property real desplazamiento: 0
    property int direccion: 0  // hacia dónde va la animación en curso: -1, 0 o 1
    readonly property int total: capturas.length
    readonly property var actual: capturas[indice] || ({})
    readonly property bool conMomento: actual.momento !== undefined && actual.momento !== null
    readonly property bool activa: pagina.StackView.status === StackView.Active

    // Al cerrar o ir al reproductor: al volver, el detalle deja el foco en la última captura vista
    signal cerrado(int indice)

    background: Rectangle { color: "black" }

    function circular(i) { return (i % total + total) % total }

    // Siempre HH:MM:SS, como el nombre del archivo
    function formatear(ms) {
        const s = Math.floor(ms / 1000)
        return [Math.floor(s / 3600), Math.floor(s / 60) % 60, s % 60].map(n => String(n).padStart(2, "0")).join(":")
    }

    function mostrarControles() {
        controlesVisibles = true
        ocultar.restart()
    }

    function salir() {
        terminarAnimacion()
        cerrado(indice)
        pagina.StackView.view.pop()
    }

    function irAlMomento() {
        terminarAnimacion()
        if (!conMomento)
            return
        cerrado(indice)
        // El visor se reemplaza para que Esc en el reproductor vuelva al detalle.
        // Es una Visita entonces arranca unos segundos antes del momento de la captura.
        pagina.StackView.view.replace("Reproductor.qml", { peliculaId: pagina.peliculaId, inicio: actual.momento })
    }

    // Termina la animación en curso: la vecina pasa a ser la actual y el carril vuelve a 0
    function asentar() {
        if (direccion !== 0)
            indice = circular(indice + direccion)
        direccion = 0
        desplazamiento = 0
    }

    function terminarAnimacion() {
        if (deslizar.running) {
            deslizar.stop()
            asentar()
        }
    }

    // Anima el carril hacia la vecina (+1 siguiente, -1 anterior) o de vuelta a su lugar (0)
    function animarHacia(dir) {
        deslizar.stop()
        direccion = dir
        deslizar.to = -dir * carril.width
        deslizar.start()
    }

    function pasar(dir) {
        mostrarControles()
        if (total < 2)
            return
        terminarAnimacion()
        animarHacia(dir)
    }

    Component.onCompleted: forceActiveFocus()
    // Cualquier tecla muestra los controles; las de navegación las toman los Shortcut de abajo
    Keys.onPressed: (evento) => { mostrarControles(); evento.accepted = false }

    NumberAnimation {
        id: deslizar
        target: pagina
        property: "desplazamiento"
        duration: 220
        easing.type: Easing.OutCubic
        onFinished: pagina.asentar()
    }

    // Tres lugares: anterior, actual y siguiente, uno al lado del otro. Las fuentes ya cargadas
    // quedan en la caché de Qt, así que al asentar la nueva actual aparece sin recargar.
    Item {
        id: carril
        anchors.fill: parent
        clip: true

        Repeater {
            model: 3
            delegate: Item {
                id: lugar
                required property int index
                readonly property int captura: pagina.circular(pagina.indice + index - 1)
                x: (index - 1) * carril.width + pagina.desplazamiento
                width: carril.width
                height: carril.height
                visible: index === 1 || pagina.total > 1

                Image {
                    id: imagen
                    anchors.fill: parent
                    source: lugar.visible && pagina.total > 0 ? pagina.capturas[lugar.captura].url : ""
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                    // Sin zoom, más resolución que la pantalla no se ve. Fijo para no recargar al redimensionar.
                    sourceSize.width: Screen.width * Screen.devicePixelRatio
                    sourceSize.height: Screen.height * Screen.devicePixelRatio
                }

                // Grilla de tercios: solo sobre lo visible de la imagen, no sobre las bandas negras
                Item {
                    visible: pagina.tercios && imagen.status === Image.Ready
                    anchors.centerIn: parent
                    width: imagen.paintedWidth
                    height: imagen.paintedHeight
                    Repeater {
                        model: [1, 2]
                        Rectangle {
                            required property int modelData
                            x: Math.round(parent.width * modelData / 3)
                            width: Tema.px(1)
                            height: parent.height
                            color: Qt.alpha(Tema.etiqueta, 0.8)
                        }
                    }
                    Repeater {
                        model: [1, 2]
                        Rectangle {
                            required property int modelData
                            y: Math.round(parent.height * modelData / 3)
                            width: parent.width
                            height: Tema.px(1)
                            color: Qt.alpha(Tema.etiqueta, 0.8)
                        }
                    }
                }
            }
        }

        // La imagen sigue al mouse; al soltar pasa a la vecina si se arrastró más de 1/4 del
        // ancho o con un gesto rápido, y si no vuelve a su lugar
        DragHandler {
            id: arrastre
            target: null
            enabled: pagina.total > 1
            yAxis.enabled: false
            property real velocidad: 0
            property real ultimoMovimiento: 0
            onActiveChanged: {
                if (active) {
                    pagina.terminarAnimacion()
                    return
                }
                const dx = pagina.desplazamiento
                // Si se quedó quieto antes de soltar, la última velocidad ya no cuenta
                const rapido = Date.now() - ultimoMovimiento < 100
                    && Math.abs(velocidad) > 800 && Math.sign(velocidad) === Math.sign(dx)
                pagina.animarHacia(Math.abs(dx) > carril.width / 4 || rapido ? (dx < 0 ? 1 : -1) : 0)
            }
            onTranslationChanged: {
                if (active) {
                    pagina.desplazamiento = translation.x
                    ultimoMovimiento = Date.now()
                }
            }
            onCentroidChanged: if (active) velocidad = centroid.velocity.x
        }
    }

    // Mover el mouse muestra los controles; los clicks pasan de largo (el fondo no cierra)
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.NoButton
        hoverEnabled: true
        cursorShape: pagina.controlesVisibles ? Qt.ArrowCursor : Qt.BlankCursor
        onPositionChanged: pagina.mostrarControles()
    }

    Timer {
        id: ocultar
        interval: 3000
        running: true
        onTriggered: {
            if (!hoverArriba.hovered && !hoverBarra.hovered && !anterior.hovered && !siguiente.hovered)
                pagina.controlesVisibles = false
            else
                restart()
        }
    }

    // Barra superior: volver y pantalla completa
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
            Boton { text: "Volver"; icono: "volver"; focusPolicy: Qt.NoFocus; onClicked: pagina.salir() }
            Item { Layout.fillWidth: true }
            BotonPantallaCompleta { id: botonPantalla }
        }
    }

    // Botones de los lados
    component Lateral: Boton {
        anchors.verticalCenter: parent.verticalCenter
        visible: pagina.total > 1 && opacity > 0
        opacity: pagina.controlesVisibles ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
        soloIcono: true
        focusPolicy: Qt.NoFocus
    }
    Lateral {
        id: anterior
        anchors.left: parent.left
        anchors.leftMargin: Tema.px(32)
        icono: "anterior"
        text: "Anterior"
        onClicked: pagina.pasar(-1)
    }
    Lateral {
        id: siguiente
        anchors.right: parent.right
        anchors.rightMargin: Tema.px(32)
        icono: "siguiente"
        text: "Siguiente"
        onClicked: pagina.pasar(1)
    }

    // Barra inferior: momento, posición, «Ir a» y grilla de tercios
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: Tema.px(80)
        opacity: pagina.controlesVisibles ? 1 : 0
        visible: opacity > 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
        gradient: Gradient {
            GradientStop { position: 0; color: "transparent" }
            GradientStop { position: 1; color: "#dd000000" }
        }
        HoverHandler { id: hoverBarra }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Tema.px(32)
            anchors.rightMargin: Tema.px(32)
            anchors.bottomMargin: Tema.px(14)
            anchors.topMargin: Tema.px(20)
            spacing: Tema.px(20)

            Text {
                visible: pagina.conMomento
                text: pagina.conMomento ? pagina.formatear(pagina.actual.momento) : ""
                color: Tema.crema
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(15)
                font.features: { "tnum": 1 }
            }
            Text {
                text: (pagina.indice + 1) + " de " + pagina.total
                color: Tema.tenue
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(15)
                font.letterSpacing: 0.2
                font.features: { "tnum": 1 }
            }
            Item { Layout.fillWidth: true }
            Boton {
                visible: pagina.conMomento
                principal: true
                icono: "play"
                text: pagina.conMomento ? "Ir a " + pagina.formatear(pagina.actual.momento) : ""
                focusPolicy: Qt.NoFocus
                onClicked: pagina.irAlMomento()
            }
            Boton {
                soloIcono: true
                icono: "tercios"
                text: pagina.tercios ? "Ocultar grilla de tercios" : "Mostrar grilla de tercios"
                checkable: true
                focusPolicy: Qt.NoFocus
                onToggled: pagina.tercios = checked
            }
        }
    }

    Shortcut { enabled: pagina.activa; sequence: "Left"; onActivated: pagina.pasar(-1) }
    Shortcut { enabled: pagina.activa; sequence: "Right"; onActivated: pagina.pasar(1) }
    Shortcut { enabled: pagina.activa; sequence: "F"; onActivated: { botonPantalla.alternar(); pagina.mostrarControles() } }
    Shortcut {
        enabled: pagina.activa
        sequence: "Esc"
        onActivated: {
            if (botonPantalla.completa) {
                botonPantalla.alternar()
                pagina.mostrarControles()
            } else {
                pagina.salir()
            }
        }
    }
}
