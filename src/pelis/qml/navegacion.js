.pragma library

// Entre películas y personas hay como máximo tres niveles sobre el catálogo (película › persona › película) para que se vuelva al catálogo con tres «Volver».
// La persona siempre queda en el segundo nivel encima de la película desde la que se empezó.

const NIVEL_PERSONA = 2  // 0 = catálogo, 1 = película de origen

function abrirPersona(pila, nombre) {
    const persona = pila.depth > NIVEL_PERSONA ? pila.get(NIVEL_PERSONA) : null
    // Si en el segundo nivel quedó otra pantalla (no la abrió este archivo) se apila como siempre para no pisarla
    if (!persona || persona.objectName !== "persona")
        return pila.push("Persona.qml", { nombre: nombre })
    // Si es la misma persona que ya estaba se vuelve a ella y se descarta la película intermedia
    if (persona.nombre === nombre) {
        pila.pop(persona)
        return persona
    }
    return pila.replace(persona, "Persona.qml", { nombre: nombre })
}

// Abierta desde una persona la película queda en el tercer nivel porque la persona siempre está en el segundo
function abrirPelicula(pila, id) {
    return pila.push("Detalle.qml", { peliculaId: id })
}
