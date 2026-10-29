# Comando y skill para publicar una versión

Status: ready-for-agent
Blocked by: 01

Ver "Repositorio y versión" y "Comando de versión" en la spec.

- `__version__ = "0.1.0"` en `src/pelis/__init__.py`; `pyproject.toml` la toma como versión dinámica
- `tools/version.py patch|minor|major|final [--rc]`, sin dependencias fuera de la biblioteca estándar
- Se niega con cambios sin commitear o fuera de `main`; `git pull --ff-only` al empezar (se niega si divergió) y otra vez antes del push (aborta si trae algo)
- Notas: `feat` y `fix` desde la última versión final, en «Nuevo» y «Arreglos», editables en `$EDITOR` / Bloc de notas
- Sube `__version__`, commitea `chore: versión vX.Y.Z`, crea el tag anotado con las notas, muestra el resumen y pide `s/N` antes de pushear commit y tag; con `N` explica cómo pushear o deshacer
- RC: `<nivel> --rc` → `-rc1`, `--rc` → siguiente RC, `final` → saca el sufijo; con una RC abierta, un nivel sin `--rc` se niega
- Skill de proyecto `.claude/skills/version/`: corre el script con el venv del sistema, muestra las notas y las reescribe en lenguaje de usuario si se le pide

## Criterio de terminado
- [ ] Tests del cálculo de la versión siguiente (niveles, RC, `final`, negativas) y del armado de notas, sin git real
- [ ] Las tres negativas (cambios sin commitear, fuera de `main`, divergida) cortan antes de tocar nada
- [ ] Con `N` no se pushea nada y el commit y el tag quedan locales
- [ ] `/version minor` publica `v0.2.0` de punta a punta
