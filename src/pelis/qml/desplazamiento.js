.pragma library

// Hasta dónde hay que mover contentY para que una fila quede entera dentro de la vista, con `margen` de más a cada lado para el halo del foco, que sobresale de la tarjeta.
// GridView con highlightFollowsCurrentItem en false no acompaña al elemento actual, entonces el foco pasa a filas fuera de pantalla sin que la vista se mueva.
function contentYParaVer(contentY, vista, y, alto, margen, minimo, maximo) {
    let destino = contentY
    if (y - margen < contentY)
        destino = y - margen
    else if (y + alto + margen > contentY + vista)
        destino = y + alto + margen - vista
    return Math.max(minimo, Math.min(destino, maximo))
}
