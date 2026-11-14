## Agent skills

### Issue tracker

Issues y specs como archivos markdown locales en `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Etiquetas por defecto (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix), registradas en la línea `Status:` de cada issue. See `docs/agents/triage-labels.md`.

### Domain docs

Un solo contexto: `GLOSSARY.md` y `docs/adr/` en la raíz. See `docs/agents/domain.md`.

## Comentarios

Al tocar código corro siempre la skill `tool:review-comments` sobre lo que cambié y aplico todos sus cambios sin esperar aprobación, salvo los que requieren una decisión del usuario (por ejemplo un hueco cuyo motivo no se encuentra, o dividir un archivo por una sección). Esos los dejo listados.
