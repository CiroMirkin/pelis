.pragma library

// Navegación entre películas y personas: como máximo tres niveles sobre el catálogo
// (película › persona › película), así se vuelve al catálogo con tres «Volver».
// La persona siempre queda en el segundo nivel, encima de la película desde la que se empezó.

const NIVEL_PERSONA = 2  // 0 = catálogo, 1 = película de origen

function abrirPersona(pila, nombre) {
    if (pila.depth <= NIVEL_PERSONA)
        return pila.push("Persona.qml", { nombre: nombre })
    const persona = pila.get(NIVEL_PERSONA)
    // La misma persona que ya estaba: se vuelve a ella sin pasar por la película intermedia
    if (persona.nombre === nombre) {
        pila.pop(persona)
        return persona
    }
    return pila.replace(persona, "Persona.qml", { nombre: nombre })
}

// Desde una persona: queda en el tercer nivel, porque la persona siempre está en el segundo
function abrirPelicula(pila, id) {
    return pila.push("Detalle.qml", { peliculaId: id })
}
