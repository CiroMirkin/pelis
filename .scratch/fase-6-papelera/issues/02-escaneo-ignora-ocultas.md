# El escaneo ignora carpetas que empiezan con punto

Status: ready-for-agent

Hoy `escaneo.py` toma toda subcarpeta de la raíz como película (`self.biblioteca.iterdir()` con `is_dir()`), así que `.papelera/` se importaría. Ignorar cualquier carpeta que empiece con `.`, tanto en el escaneo como en la importación al abrir.

## Criterio de terminado
- [ ] Test: una carpeta `.papelera/` (u otra oculta) en la raíz no se importa ni aparece en el informe de problemas
