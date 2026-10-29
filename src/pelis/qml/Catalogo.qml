import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic as Basic
import QtQuick.Layouts
import "duracion.js" as Duracion

Page {
    id: pagina
    background: Rectangle { color: Tema.noche }

    // Texto con el que se filtró la grilla por última vez (el campo puede ir adelantado por la espera)
    property string filtro: ""
    // "todas", "vistas" o "noVistas"
    property string vistas: "todas"

    function filtrarVistas(cuales) {
        vistas = cuales
        puente.catalogo.filtrarVistas(cuales)
    }

    // Opción del filtro de vistas: rótulo que se subraya en crema cuando está elegida
    component OpcionVistas: AbstractButton {
        id: opcion
        required property string valor
        readonly property bool elegida: pagina.vistas === valor
        implicitHeight: Tema.px(38)
        leftPadding: Tema.px(10)
        rightPadding: Tema.px(10)
        focusPolicy: Qt.TabFocus
        hoverEnabled: true
        onClicked: pagina.filtrarVistas(valor)
        Keys.onReturnPressed: clicked()
        Keys.onEnterPressed: clicked()
        contentItem: Text {
            text: opcion.text
            verticalAlignment: Text.AlignVCenter
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(15)
            font.weight: Font.DemiBold
            font.capitalization: Font.AllUppercase
            font.letterSpacing: 0.6
            color: opcion.elegida || opcion.hovered ? Tema.crema : Tema.tenue
        }
        background: Item {
            Rectangle {
                visible: opcion.visualFocus
                anchors.fill: parent
                anchors.margins: -Tema.px(4)
                radius: Tema.px(6)
                color: "transparent"
                border.width: Tema.px(3)
                border.color: Tema.tubo
            }
            Rectangle {
                visible: opcion.elegida
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.leftMargin: opcion.leftPadding
                anchors.rightMargin: opcion.rightPadding
                height: Tema.px(2)
                color: Tema.crema
            }
        }
    }

    function abrir(id) { pagina.StackView.view.push("Detalle.qml", { peliculaId: id }) }

    function filtrar(texto) {
        espera.stop()
        filtro = texto.trim()
        puente.catalogo.filtrar(filtro)
    }

    function limpiarBusqueda() {
        buscador.text = ""
        filtrar("")
        grilla.forceActiveFocus()
    }

    // Filtra unos 300 ms después de la última tecla, para no rearmar la grilla con cada letra
    Timer { id: espera; interval: 300; onTriggered: pagina.filtrar(buscador.text) }

    Shortcut {
        sequences: [StandardKey.Find, "/"]
        enabled: pagina.StackView.status === StackView.Active && !buscador.activeFocus
        onActivated: { buscador.forceActiveFocus(); buscador.selectAll() }
    }

    Component.onCompleted: grilla.forceActiveFocus()
    StackView.onActivated: grilla.forceActiveFocus()

    header: Rectangle {
        implicitHeight: Tema.px(68)
        color: Tema.noche
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Tema.linea }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Tema.px(40)
            anchors.rightMargin: Tema.px(40)
            spacing: Tema.px(20)

            Text {
                text: "PELIS"
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(26)
                font.weight: Font.Bold
                font.letterSpacing: 2
                color: Tema.crema
            }
            Basic.TextField {
                id: buscador
                Layout.preferredWidth: Tema.px(360)
                Layout.leftMargin: Tema.px(20)
                placeholderText: "Buscar título, director o reparto"
                placeholderTextColor: Tema.tenue
                color: Tema.crema
                selectionColor: Tema.etiqueta
                selectedTextColor: Tema.sobreEtiqueta
                font.family: Tema.texto
                font.pixelSize: Tema.px(15)
                leftPadding: Tema.px(14)
                rightPadding: Tema.px(14)
                verticalAlignment: TextInput.AlignVCenter
                onTextChanged: espera.restart()
                Keys.onEscapePressed: pagina.limpiarBusqueda()
                Keys.onDownPressed: { pagina.filtrar(text); grilla.forceActiveFocus() }
                Keys.onReturnPressed: { pagina.filtrar(text); grilla.forceActiveFocus() }
                Keys.onEnterPressed: { pagina.filtrar(text); grilla.forceActiveFocus() }
                background: Rectangle {
                    implicitHeight: Tema.px(38)
                    radius: Tema.px(3)
                    color: buscador.activeFocus ? Tema.caja : "transparent"
                    border.width: buscador.activeFocus ? Tema.px(2) : 1
                    border.color: buscador.activeFocus ? Tema.tubo : Qt.alpha(Tema.crema, 0.35)
                }
            }
            Row {
                spacing: Tema.px(2)
                OpcionVistas { text: "Todas"; valor: "todas" }
                OpcionVistas { text: "Sin ver"; valor: "noVistas" }
                OpcionVistas { text: "Vistas"; valor: "vistas" }
            }
            SelectorEpoca {
                id: selectorEpoca
                visible: periodos.length > 1
                periodos: puente.catalogo.periodos
                periodo: puente.catalogo.periodo
                onElegido: (clave) => puente.catalogo.filtrarPeriodo(clave)
            }
            // Filtro de incompletas activo: se quita desde acá o desde el menú
            Boton {
                visible: puente.catalogo.soloIncompletas
                text: "Sin datos o portada"
                icono: "cerrar"
                focusPolicy: Qt.TabFocus
                onClicked: puente.catalogo.filtrarIncompletas(false)
            }
            Item { Layout.fillWidth: true }
            Text {
                id: sumadas
                visible: false
                color: Tema.crema
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
                Timer { id: ocultarSumadas; interval: 8000; onTriggered: sumadas.visible = false }
                Connections {
                    target: puente
                    function onImportacionTerminada(n) {
                        sumadas.text = n === 1 ? "Se sumó 1 película" : "Se sumaron " + n + " películas"
                        sumadas.visible = true
                        ocultarSumadas.restart()
                    }
                }
            }
            Text {
                text: grilla.count === 1 ? "1 película" : grilla.count + " películas"
                color: Tema.tenue
                font.family: Tema.texto
                font.pixelSize: Tema.px(14)
            }
            BotonMas {
                alinearDerecha: true
                focusPolicy: Qt.TabFocus
                KeyNavigation.down: grilla
                OpcionMenu {
                    text: "Escanear biblioteca"
                    icono: "escanear"
                    onTriggered: dialogo.iniciar()
                }
                OpcionMenu {
                    text: "Renovar portadas"
                    icono: "renovar"
                    enabled: !puente.escaneando
                    onTriggered: {
                        const n = puente.renovarPortadas()
                        sumadas.text = n === 0 ? "No hay portadas para renovar"
                                     : n === 1 ? "Se renovó 1 portada" : "Se renovaron " + n + " portadas"
                        sumadas.visible = true
                        ocultarSumadas.restart()
                    }
                }
                OpcionMenu {
                    visible: puente.cantidadSinVer > 0
                    text: "Marcar todas como vistas"
                    icono: "visto"
                    onTriggered: confirmarVistas.open()
                }
                OpcionMenu {
                    visible: puente.catalogo.soloIncompletas || puente.catalogo.cantidadIncompletas > 0
                    text: puente.catalogo.soloIncompletas
                          ? "Ver todas"
                          : "Sin datos o portada (" + puente.catalogo.cantidadIncompletas + ")"
                    icono: "editar"
                    onTriggered: puente.catalogo.filtrarIncompletas(!puente.catalogo.soloIncompletas)
                }
                OpcionMenu {
                    visible: puente.cantidadFaltantes > 0
                    text: "Faltantes (" + puente.cantidadFaltantes + ")"
                    icono: "faltantes"
                    onTriggered: pagina.StackView.view.push("Faltantes.qml")
                }
                OpcionMenu {
                    // Desde el código no hay build que reemplazar
                    enabled: puente.puedeActualizar && !puente.buscandoActualizacion
                    text: "Buscar actualización"
                    icono: "actualizar"
                    onTriggered: actualizacion.iniciar()
                }
            }
        }
    }

    // Recomendación al abrir: una película sin ver, elegida al azar
    Rectangle {
        id: recomendacion
        readonly property var r: puente.recomendada
        visible: !!r.id && pagina.filtro === "" && pagina.vistas !== "vistas" && puente.catalogo.periodo === ""
                 && !puente.catalogo.soloIncompletas
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: visible ? Tema.px(24) : 0
        anchors.leftMargin: Tema.px(40)
        anchors.rightMargin: Tema.px(40)
        height: visible ? Tema.px(208) : 0
        radius: Tema.px(4)
        color: zonaRecomendacion.containsMouse ? Tema.caja : Tema.estante
        border.width: 1
        border.color: Tema.linea

        MouseArea {
            id: zonaRecomendacion
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: pagina.abrir(recomendacion.r.id)
        }

        RowLayout {
            anchors.fill: parent
            anchors.margins: Tema.px(14)
            anchors.rightMargin: Tema.px(64)  // lugar para la ✕ de la esquina
            spacing: Tema.px(20)

            Rectangle {
                Layout.preferredWidth: Tema.px(120)
                Layout.preferredHeight: Tema.px(180)
                radius: Tema.px(2)
                color: Tema.caja
                clip: true
                Image {
                    anchors.fill: parent
                    source: recomendacion.r.poster || ""
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    sourceSize.width: 240
                }
            }
            ColumnLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                spacing: Tema.px(4)
                Text {
                    text: "Recomendación del día"
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(13)
                    font.weight: Font.DemiBold
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 1
                    color: Tema.tenue
                }
                Text {
                    Layout.fillWidth: true
                    text: recomendacion.r.titulo || ""
                    elide: Text.ElideRight
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(32)
                    font.weight: Font.Bold
                    font.capitalization: Font.AllUppercase
                    color: Tema.crema
                }
                Text {
                    Layout.fillWidth: true
                    visible: text !== ""
                    text: [recomendacion.r.anio || "", recomendacion.r.genero,
                           Duracion.texto(recomendacion.r.duracion)].filter(x => x).join("   *   ")
                    wrapMode: Text.WordWrap
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(15)
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 0.6
                    color: Tema.tenue
                }
            }
        }

        Boton {
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: Tema.px(8)
            soloIcono: true
            sinBorde: true
            icono: "cerrar"
            text: "Descartar"
            focusPolicy: Qt.TabFocus
            onClicked: puente.cerrarRecomendacion()
        }
    }

    GridView {
        id: grilla
        readonly property int columnas: Math.max(2, Math.floor((width - leftMargin - rightMargin) / Tema.px(184)))
        anchors.top: recomendacion.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        // Márgenes dentro del recorte, para que el halo del foco no se corte en los bordes
        leftMargin: Tema.px(40)
        rightMargin: Tema.px(12)
        topMargin: Tema.px(28)
        cellWidth: Math.floor((width - leftMargin - rightMargin) / columnas)
        cellHeight: Math.round((cellWidth - Tema.px(28)) * 1.5) + Tema.px(82)
        clip: true
        focus: true
        keyNavigationWraps: false
        model: puente.catalogo
        highlightFollowsCurrentItem: false
        ScrollBar.vertical: ScrollBar {}
        Keys.onReturnPressed: if (currentItem) pagina.abrir(currentItem.peliculaId)
        Keys.onEnterPressed: if (currentItem) pagina.abrir(currentItem.peliculaId)
        Keys.onEscapePressed: if (pagina.filtro !== "" || buscador.text !== "") pagina.limpiarBusqueda()

        delegate: Item {
            id: celda
            required property int index
            required property int peliculaId
            required property string titulo
            required property int anio
            required property string poster
            required property real progreso
            required property bool vista
            readonly property bool encendida: GridView.isCurrentItem && (grilla.activeFocus || zona.containsMouse)
            width: grilla.cellWidth
            height: grilla.cellHeight

            Tarjeta {
                width: parent.width - Tema.px(28)
                titulo: celda.titulo
                anio: celda.anio
                poster: celda.poster
                progreso: celda.progreso
                vista: celda.vista
                encendida: celda.encendida
            }

            MouseArea {
                id: zona
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onEntered: grilla.currentIndex = celda.index
                onClicked: pagina.abrir(celda.peliculaId)
            }
        }
    }

    Text {
        visible: grilla.count === 0
        anchors.centerIn: parent
        text: pagina.filtro !== ""
              ? "Ninguna película coincide con «" + pagina.filtro + "».\nEsc para ver todas."
              : puente.catalogo.soloIncompletas
                ? "No hay películas sin datos o sin portada"
                  + (pagina.vistas !== "todas" || puente.catalogo.periodo !== "" ? " con estos filtros." : ".")
              : puente.catalogo.periodo !== ""
                ? "No hay películas " + (pagina.vistas === "vistas" ? "vistas " : pagina.vistas === "noVistas" ? "sin ver " : "")
                  + "de " + selectorEpoca.etiqueta(puente.catalogo.periodo).toLowerCase() + "."
              : pagina.vistas === "vistas" ? "Todavía no marcaste ninguna película como vista."
              : pagina.vistas === "noVistas" ? "Ya viste todas las películas."
              : "Todavía no hay películas.\nTocá «…» › «Escanear biblioteca» para cargarlas."
        horizontalAlignment: Text.AlignHCenter
        lineHeight: 1.3
        font.family: Tema.texto
        font.pixelSize: Tema.px(16)
        color: Tema.tenue
    }

    DialogoEscaneo { id: dialogo }

    DialogoActualizacion {
        id: actualizacion
        onCerrado: grilla.forceActiveFocus()
    }

    Popup {
        id: confirmarVistas
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: Math.min(Tema.px(520), parent.width - 48)
        padding: Tema.px(26)
        modal: true
        onOpened: cancelarVistas.forceActiveFocus()
        onClosed: grilla.forceActiveFocus()
        background: Rectangle {
            color: Tema.estante
            radius: Tema.px(4)
            border.width: 1
            border.color: Tema.linea
        }
        Overlay.modal: Rectangle { color: Qt.alpha(Tema.noche, 0.8) }

        ColumnLayout {
            width: confirmarVistas.availableWidth
            spacing: Tema.px(18)
            Text {
                text: "¿MARCAR TODAS COMO VISTAS?"
                font.family: Tema.rotulo
                font.pixelSize: Tema.px(22)
                font.weight: Font.Bold
                color: Tema.crema
            }
            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                lineHeight: 1.3
                text: (puente.cantidadSinVer === 1 ? "La película que falta ver queda marcada como vista."
                       : "Las " + puente.cantidadSinVer + " películas que faltan ver quedan marcadas como vistas.")
                      + " Para desmarcar una, hay que hacerlo desde su detalle."
                font.family: Tema.texto
                font.pixelSize: Tema.px(15)
                color: Tema.crema
            }
            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: Tema.px(12)
                Boton {
                    id: cancelarVistas
                    text: "Cancelar"
                    onClicked: confirmarVistas.close()
                }
                Boton {
                    principal: true
                    text: "Marcar todas"
                    onClicked: { confirmarVistas.close(); puente.marcarTodasVistas() }
                }
            }
        }
    }
}
