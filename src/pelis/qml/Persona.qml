import QtQuick
import QtQuick.Controls

// Todas las películas de la biblioteca donde participa una persona (dirección o elenco)
Page {
    id: pagina
    required property string nombre
    property var peliculas: []

    function recargar() { peliculas = puente.peliculasDe(nombre) }
    function abrir(id) { pagina.StackView.view.push("Detalle.qml", { peliculaId: id }) }
    function rol(roles) {
        return roles.length > 1 ? "Dirección y elenco" : roles[0] === "director" ? "Dirección" : "Elenco"
    }

    Component.onCompleted: { recargar(); grilla.forceActiveFocus() }
    StackView.onActivated: { recargar(); grilla.forceActiveFocus() }

    Shortcut {
        sequence: "Esc"
        enabled: pagina.StackView.status === StackView.Active
        onActivated: pagina.StackView.view.pop()
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
    }

    Column {
        id: encabezado
        x: Tema.px(40)
        y: Tema.px(32)
        width: parent.width - Tema.px(80)
        spacing: Tema.px(6)
        Text {
            width: parent.width
            text: pagina.nombre
            elide: Text.ElideRight
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(40)
            font.weight: Font.Bold
            font.capitalization: Font.AllUppercase
            color: Tema.crema
        }
        Text {
            text: pagina.peliculas.length === 1 ? "1 película" : pagina.peliculas.length + " películas"
            font.family: Tema.rotulo
            font.pixelSize: Tema.px(16)
            font.capitalization: Font.AllUppercase
            font.letterSpacing: 0.8
            color: Tema.tenue
        }
    }

    GridView {
        id: grilla
        readonly property int columnas: Math.max(2, Math.floor((width - leftMargin - rightMargin) / Tema.px(184)))
        anchors.top: encabezado.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        leftMargin: Tema.px(40)
        rightMargin: Tema.px(12)
        topMargin: Tema.px(28)
        cellWidth: Math.floor((width - leftMargin - rightMargin) / columnas)
        cellHeight: Math.round((cellWidth - Tema.px(28)) * 1.5) + Tema.px(104)
        clip: true
        focus: true
        model: pagina.peliculas
        highlightFollowsCurrentItem: false
        ScrollBar.vertical: ScrollBar {}
        Keys.onReturnPressed: if (currentItem) pagina.abrir(currentItem.peliculaId)
        Keys.onEnterPressed: if (currentItem) pagina.abrir(currentItem.peliculaId)

        delegate: Item {
            id: celda
            required property int index
            required property var modelData
            readonly property int peliculaId: modelData.peliculaId
            width: grilla.cellWidth
            height: grilla.cellHeight

            Column {
                width: parent.width - Tema.px(28)
                spacing: Tema.px(2)
                Tarjeta {
                    width: parent.width
                    titulo: celda.modelData.titulo
                    anio: celda.modelData.anio
                    poster: celda.modelData.poster
                    progreso: celda.modelData.progreso
                    vista: celda.modelData.vista
                    encendida: celda.GridView.isCurrentItem && (grilla.activeFocus || zona.containsMouse)
                }
                Text {
                    text: pagina.rol(celda.modelData.roles)
                    font.family: Tema.rotulo
                    font.pixelSize: Tema.px(13)
                    font.weight: Font.DemiBold
                    font.letterSpacing: 1
                    font.capitalization: Font.AllUppercase
                    color: Tema.tenue
                }
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
}
