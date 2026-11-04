# 01: Botón de pantalla completa fijo en el header

**What to build:** el botón de pantalla completa, que hoy solo está en el reproductor y el visor, aparece también en el header del catálogo, el detalle, la persona y faltantes. «Editar datos» no lo muestra. La pantalla completa pasa a ser un estado de la ventana: se mantiene al navegar entre páginas y solo cambia cuando el usuario la cambia. Hoy, salir del reproductor o del visor la quita siempre; eso deja de pasar, para que entrar a una película y volver al catálogo no saque de pantalla completa.

Reproductor y visor tienen duplicados el estado y la función de alternar. Antes de sumar páginas, todo pasa a un único componente de botón, que usan las seis.

Decisiones (2026-11-03):
- Salir del reproductor o del visor no cambia la pantalla completa. Si se activó durante la película y se vuelve con «Volver», el catálogo también queda en pantalla completa.
- `Esc` y `F` siguen funcionando igual que hoy en el reproductor y el visor. En las demás páginas no cambian de significado: ahí la pantalla completa se alterna solo con el botón, porque `Esc` ya limpia la búsqueda o vuelve, y `F` podría chocar con lo que se escribe en el buscador.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] El botón se ve en el header del catálogo, el detalle, la persona y faltantes, en el extremo derecho. En el catálogo queda a la derecha del botón «…».
- [x] «Editar datos» no muestra el botón.
- [x] El botón alterna la pantalla completa, y el ícono y el texto reflejan el estado actual, también si cambió con `F` o `Esc` en el reproductor o el visor.
- [x] Reproductor y visor usan el mismo componente, y su botón sigue en el lugar de siempre.
- [x] Navegar entre páginas no cambia la pantalla completa, tampoco al pasar por «Editar datos».
- [x] Salir del reproductor o del visor con «Volver» deja la ventana como estaba. `Esc` en pantalla completa la sigue quitando primero, y el segundo `Esc` sale.
- [x] En el detalle, el aviso temporal de la derecha del header no se superpone con el botón.
- [x] El botón no le saca el foco a la grilla ni al buscador, y no rompe la navegación con teclado.

## Comments

2026-11-03: implementado en la rama `feat/pantalla-completa-fija`. `BotonPantallaCompleta.qml` nuevo, con el estado y el alternar que estaban duplicados en reproductor y visor; `salir()` de los dos ya no toca la ventana.

Smoke test offscreen con eventos de mouse y teclado simulados, sin avisos de QML: los criterios pasan, incluida la posición en catálogo y faltantes y que el aviso del detalle termine antes del botón. La plataforma offscreen no tiene gestor de ventanas, así que falta probar a mano:
- Cómo se ve el botón en cada header y el cambio real a pantalla completa.
- Salir de pantalla completa con la ventana maximizada: va a `Windowed`, como antes, y puede que no vuelva a quedar maximizada.

2026-11-03: el usuario lo probó en la app y dio el OK.
