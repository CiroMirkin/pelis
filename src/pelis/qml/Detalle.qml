import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "paises.js" as Paises
import "duracion.js" as Duracion
import "navegacion.js" as Navegacion

Page {
    id: pagina
    required property int peliculaId
    property var p: ({})

    function recargar() {
        // Cambiar el modelo recrea las miniaturas, y la enfocada perdería el foco
        let enfocada = -1
        for (let i = 0; i < miniaturas.count; i++)
            if (miniaturas.itemAt(i).activeFocus)
                enfocada = i
        p = puente.pelicula(peliculaId)
        if (enfocada >= 0) {
            if (capturas.length > 0)
                enfocarCaptura(Math.min(enfocada, capturas.length - 1))
            else
                reproducir.forceActiveFocus()
        }
    }
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
        font.letterSpacing: 0.3
        color: Tema.tenue
    }
    component Rotulo: Text {
        Layout.alignment: Qt.AlignTop
        Layout.topMargin: Tema.px(2)
        font.family: Tema.rotulo
        font.pixelSize: Tema.px(13)
        font.weight: Font.DemiBold
        font.letterSpacing: 0.3
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
                    onClicked: Navegacion.abrirPersona(pagina.StackView.view, nombre.modelData.nombre)
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

    // Índice de la última captura vista en el visor; al volver, el foco va ahí y no a Reproducir
    property int volverACaptura: -1

    Component.onCompleted: { recargar(); reproducir.forceActiveFocus() }
    StackView.onActivated: {
        ahora = new Date()
        recargar()
        if (volverACaptura >= 0 && capturas.length > 0)
            enfocarCaptura(Math.min(volverACaptura, capturas.length - 1))
        else
            reproducir.forceActiveFocus()
        volverACaptura = -1
    }

    function abrirVisor(i) {
        const visor = pagina.StackView.view.push("Visor.qml",
            { capturas: pagina.capturas, indice: i, peliculaId: pagina.peliculaId })
        visor.cerrado.connect(ultima => pagina.volverACaptura = ultima)
    }

    function enfocarCaptura(i) {
        // El Flow acomoda recién antes de pintar; mostrarEnPantalla necesita la posición ya
        grillaCapturas.forceLayout()
        const item = miniaturas.itemAt(i)
        if (item) item.forceActiveFocus()
    }

    // Lleva el desplazamiento lo justo para que `item` quede a la vista
    function mostrarEnPantalla(item) {
        const margen = Tema.px(24)
        const y = item.mapToItem(desplazable.contentItem, 0, 0).y
        if (y - margen < desplazable.contentY)
            desplazable.contentY = Math.max(0, y - margen)
        else if (y + item.height + margen > desplazable.contentY + desplazable.height)
            desplazable.contentY = Math.min(desplazable.contentHeight - desplazable.height,
                                            y + item.height + margen - desplazable.height)
    }

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
        BotonPantallaCompleta {
            id: botonPantalla
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: Tema.px(40)
        }
        Text {
            id: aviso
            visible: false
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: botonPantalla.left
            anchors.rightMargin: Tema.px(20)
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
        id: desplazable
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
                    color: Tema.tenue
                }
                Image {
                    id: poster
                    anchors.fill: parent
                    source: pagina.p.poster || ""
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    retainWhileLoading: true  // al cambiar de portada no parpadea el título de respaldo
                    sourceSize.width: 640
                }
                // Play sobre el poster: adorno, el click lo atiende zonaPoster.
                // Excepción a la Regla de la Etiqueta Única pedida por el usuario
                Rectangle {
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.margins: Tema.px(14)
                    width: Tema.px(52)
                    height: width
                    radius: width / 2
                    color: zonaPoster.pressedButtons & Qt.LeftButton ? Qt.darker(Tema.etiqueta, 1.15)
                           : zonaPoster.containsMouse ? Qt.lighter(Tema.etiqueta, 1.08) : Tema.etiqueta
                    Image {
                        anchors.centerIn: parent
                        anchors.horizontalCenterOffset: Tema.px(2)  // el triángulo se ve centrado corrido un poco a la derecha
                        source: "iconos/play-oscuro.svg"
                        sourceSize: Qt.size(Tema.px(24), Tema.px(24))
                    }
                }
                // Izquierdo reproduce; derecho pasa a la portada siguiente
                MouseArea {
                    id: zonaPoster
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: mouse => {
                        if (mouse.button === Qt.LeftButton)
                            pagina.reproducirPelicula()
                        else if (puente.siguientePortada(pagina.peliculaId))
                            pagina.recargar()
                    }
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
                        Keys.onDownPressed: pagina.enfocarCaptura(0)
                        onClicked: pagina.reproducirPelicula()
                    }
                    Boton {
                        id: marcar
                        icono: pagina.p.vista ? "visto" : ""
                        text: pagina.p.vista ? "Vista" : "Marcar como vista"
                        KeyNavigation.left: reproducir
                        KeyNavigation.right: mas
                        Keys.onDownPressed: pagina.enfocarCaptura(0)
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
                    font.letterSpacing: 0.2
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

        // Cuadros guardados con «.» en el reproductor; abren el visor con click, Enter o Espacio
        Column {
            id: seccionCapturas
            visible: pagina.capturas.length > 0
            x: fila.x
            y: fila.y + fila.height + Tema.px(48)
            width: fila.width
            spacing: Tema.px(14)

            Rotulo { text: "Capturas" }
            Flow {
                id: grillaCapturas
                readonly property int celda: Tema.px(160)
                // Miniaturas por fila, como las acomoda el Flow: para ↑/↓
                readonly property int columnas: Math.max(1, Math.floor((width + spacing) / (celda + spacing)))
                width: parent.width
                spacing: Tema.px(12)
                Repeater {
                    id: miniaturas
                    model: pagina.capturas
                    // Ancho fijo y alto según la proporción del cuadro; 16:9 mientras carga
                    delegate: Item {
                        id: miniatura
                        required property var modelData
                        required property int index
                        width: grillaCapturas.celda
                        height: imagen.status === Image.Ready ? width * imagen.implicitHeight / imagen.implicitWidth : width * 9 / 16
                        Accessible.role: Accessible.Button
                        Accessible.name: "Captura " + (index + 1)

                        function moverA(i) { if (i !== index) pagina.enfocarCaptura(i) }
                        onActiveFocusChanged: if (activeFocus) pagina.mostrarEnPantalla(miniatura)
                        Keys.onLeftPressed: moverA(Math.max(0, index - 1))
                        Keys.onRightPressed: moverA(Math.min(miniaturas.count - 1, index + 1))
                        Keys.onUpPressed: {
                            if (index >= grillaCapturas.columnas)
                                moverA(index - grillaCapturas.columnas)
                            else {
                                reproducir.forceActiveFocus()
                                desplazable.contentY = 0
                            }
                        }
                        Keys.onDownPressed: {
                            const cols = grillaCapturas.columnas, ultima = miniaturas.count - 1
                            // Desde la anteúltima fila, si abajo no hay, va a la última captura
                            if (Math.floor(index / cols) < Math.floor(ultima / cols))
                                moverA(Math.min(ultima, index + cols))
                        }
                        Keys.onReturnPressed: pagina.abrirVisor(index)
                        Keys.onEnterPressed: pagina.abrirVisor(index)
                        Keys.onSpacePressed: pagina.abrirVisor(index)

                        // Halo del tubo fluorescente, como en las tarjetas del catálogo
                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: -Tema.px(6)
                            radius: Tema.px(6)
                            color: "transparent"
                            border.width: Tema.px(3)
                            border.color: Tema.tubo
                            opacity: miniatura.activeFocus ? 1 : 0
                            Behavior on opacity { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
                        }
                        Image {
                            id: imagen
                            anchors.fill: parent
                            source: miniatura.modelData.url
                            fillMode: Image.PreserveAspectFit
                            asynchronous: true
                            sourceSize.width: grillaCapturas.celda * Screen.devicePixelRatio
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: pagina.abrirVisor(miniatura.index)
                        }
                    }
                }
            }
        }
    }
}
