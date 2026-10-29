# Visor de capturas

Status: needs-triage

Pedido el 2026-10-29. Saca de «Fuera de alcance» de la spec el «ver una captura grande».

## Qué
- Click en una miniatura de la sección «Capturas» del detalle abre la captura en grande.
- Desde ahí se pasa a la anterior y la siguiente (slide), en el mismo orden de la grilla (`capturas.listar`).

## Preguntas abiertas
- Dónde se abre: página propia en el `StackView`, popup sobre el detalle o pantalla completa.
- Cómo se navega: flechas del teclado, botones a los lados, rueda del mouse, arrastre; si al llegar a la última vuelve a la primera.
- Cómo se cierra: Esc, click fuera, botón.
- Qué se muestra además de la imagen: el momento (`01:23:45`), «3 de 12», nada.
- Las miniaturas ganan foco de teclado y Enter para abrir, o solo mouse.
- Si suma acciones (saltar a ese momento en el reproductor, borrar) o quedan fuera.
