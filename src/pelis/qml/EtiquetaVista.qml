import QtQuick

// Etiqueta «VISTA»: estrella ondulada de picos suaves, como los stickers de oferta de antes
Item {
    id: etiqueta
    width: Tema.px(56)
    height: width
    rotation: -10

    // Picos alrededor y cuánto se meten los valles (fracción del radio)
    readonly property int picos: 12
    readonly property real profundidad: 0.15

    Canvas {
        id: forma
        anchors.fill: parent
        antialiasing: true
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            const cx = width / 2, cy = height / 2
            const exterior = Math.min(cx, cy)
            const interior = exterior * (1 - etiqueta.profundidad)
            const pasos = 360
            ctx.beginPath()
            for (let i = 0; i <= pasos; i++) {
                const a = i / pasos * 2 * Math.PI
                // Onda suave; la potencia afina un poco los picos sin dejarlos en punta
                const onda = Math.pow((1 + Math.cos(etiqueta.picos * a)) / 2, 1.4)
                const r = interior + (exterior - interior) * onda
                const x = cx + r * Math.cos(a), y = cy + r * Math.sin(a)
                i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
            }
            ctx.closePath()
            ctx.fillStyle = Tema.etiqueta
            ctx.fill()
        }
        onWidthChanged: requestPaint()
    }

    Text {
        anchors.centerIn: parent
        text: "VISTA"
        font.family: Tema.rotulo
        font.pixelSize: Tema.px(13)
        font.weight: Font.Bold
        font.letterSpacing: 0.5
        color: Tema.sobreEtiqueta
    }
}
