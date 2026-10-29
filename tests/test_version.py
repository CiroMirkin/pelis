import pytest

from version import Negativa, armar_notas, siguiente


@pytest.mark.parametrize("actual, nivel, rc, esperado", [
    ("0.1.0", "patch", False, "0.1.1"),
    ("0.1.3", "minor", False, "0.2.0"),
    ("0.4.2", "major", False, "1.0.0"),
    ("0.1.0", "minor", True, "0.2.0-rc1"),
    ("0.2.0-rc1", None, True, "0.2.0-rc2"),
    ("0.2.0-rc9", None, True, "0.2.0-rc10"),
    ("0.2.0-rc2", "final", False, "0.2.0"),
    ("0.2.0-rc1", "minor", True, "0.3.0-rc1"),
])
def test_siguiente(actual, nivel, rc, esperado):
    assert siguiente(actual, nivel, rc) == esperado


@pytest.mark.parametrize("actual, nivel, rc", [
    ("0.2.0-rc1", "patch", False),  # RC abierta: primero final
    ("0.2.0-rc1", "minor", False),
    ("0.2.0", "final", False),      # nada que cerrar
    ("0.2.0-rc1", "final", True),
    ("0.2.0", None, True),          # --rc solo, sin RC abierta
    ("0.2.0", None, False),
    ("0.2", "patch", False),
])
def test_siguiente_se_niega(actual, nivel, rc):
    with pytest.raises(Negativa):
        siguiente(actual, nivel, rc)


def test_notas_agrupan_feat_y_fix():
    asuntos = [
        "feat(capturas): tomar captura con la tecla punto",
        "fix: reconocer capturas de 100 horas o más",
        "docs: agregar casos de uso",
        "refactor(poster): crear poster.py",
        "feat: buscar actualización",
        "chore: versión v0.1.0",
    ]
    assert armar_notas(asuntos) == (
        "## Nuevo\n\n"
        "- Tomar captura con la tecla punto\n"
        "- Buscar actualización\n\n"
        "## Arreglos\n\n"
        "- Reconocer capturas de 100 horas o más"
    )


def test_notas_sin_feat_ni_fix():
    assert armar_notas(["docs: algo", "chore: otra"]) == "Sin cambios visibles."
    assert armar_notas([]) == "Sin cambios visibles."
