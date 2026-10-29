# Subir el repositorio y cerrar las decisiones abiertas

Status: ready-for-agent

Las decisiones están cerradas (grilling del 29/10/2026, ver la spec). Queda subir el repo.

## Criterio de terminado
- [x] Público o privado: público, las Releases se leen sin token
- [x] `.gitignore` revisado: `dev/`, `Peliculas/`, `.venv*/`, `build/`, `dist/` quedan afuera; `.scratch/` se versiona
- [x] Esquema de versiones: semver con `-rcN`, versión única en `src/pelis/__init__.py`, la sube `tools/version.py` (issue 05)
- [x] Firma del `.exe`: no se firma, se acepta el aviso de SmartScreen
- [ ] Revisado que el historial no tenga claves de OMDb ni TMDb
- [ ] `main` pusheada a `origin` (`CiroMirkin/pelis`), con la confirmación del usuario
