# 01: Filtro de época: décadas hasta los 2000 y últimos años

**What to build:** el selector de época del catálogo ofrece las décadas hasta «Los 2000» inclusive (2000-2009) y, aparte, los últimos 4 años, como hasta ahora. Los años intermedios no tienen opción propia: desaparece «Los 2010» y «Los 2020» tampoco aparece cuando pase a ser una década anterior. Una película de 2015 o de 2021 solo se ve en «Todos».

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Con películas de 1964, 2004, 2015, 2021 y 2025 en 2026, el selector ofrece «Todos», «Los 60s», «Los 2000» y «2025»
- [x] Las décadas anteriores a los 50 («Los 40s» y demás) siguen apareciendo si hay películas de esos años
- [x] Los últimos 4 años, incluido el actual, siguen yendo sueltos
- [x] En 2031, una película de 2021 no genera «Los 2020» y una de 2029 aparece como «2029»
- [x] Una película de un año intermedio aparece en «Todos» y no en ninguna otra opción
- [x] Siguen apareciendo solo las épocas con películas, y el filtro sigue oculto si no hay más de una
- [x] Los tests de períodos reflejan la regla nueva
- [x] Los casos de uso y `DESIGN.md` describen la regla nueva
