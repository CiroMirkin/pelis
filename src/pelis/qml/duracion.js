.pragma library

// Duración vacia si no existe o redondeada al minuto si existe: "2 h 5 min", "2 h", "45 min"
function texto(ms) {
    const minutos = Math.round((ms || 0) / 60000)
    if (minutos <= 0)
        return ""
    const h = Math.floor(minutos / 60), m = minutos % 60
    return h === 0 ? m + " min" : m === 0 ? h + " h" : h + " h " + m + " min"
}
