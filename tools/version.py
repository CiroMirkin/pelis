"""Publica una versión: sube `__version__`, commitea, crea el tag anotado con las notas y pushea.

Uso: python tools/version.py patch|minor|major|final [--rc]
     python tools/version.py --rc                  siguiente RC de la versión actual

Reglas en .scratch/fase-7-publicacion/spec.md («Comando de versión»). Solo biblioteca estándar.
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INIT = RAIZ / "src" / "pelis" / "__init__.py"
RE_VERSION = re.compile(r'^__version__ = "([^"]+)"$', re.MULTILINE)
RE_SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?")
RE_COMMIT = re.compile(r"(feat|fix)(?:\([^)]*\))?!?: (.+)")


class Negativa(Exception):
    """El comando no puede seguir; el mensaje dice por qué."""


def parsear(version):
    """'0.2.0-rc1' -> (0, 2, 0, 1). Sin RC, el último es None."""
    m = RE_SEMVER.fullmatch(version)
    if not m:
        raise Negativa(f"versión inválida: {version}")
    mayor, menor, parche, rc = m.groups()
    return int(mayor), int(menor), int(parche), int(rc) if rc else None


def formatear(mayor, menor, parche, rc=None):
    return f"{mayor}.{menor}.{parche}" + (f"-rc{rc}" if rc else "")


def siguiente(actual, nivel, rc=False):
    """Versión que sigue a `actual`. `nivel` es patch, minor, major, final o None (solo `--rc`).

    Con una RC abierta, un nivel sin `--rc` se niega: primero se cierra con `final`. Un nivel con
    `--rc` sobre una RC abierta parte de su número base (0.2.0-rc1 + minor --rc -> 0.3.0-rc1).
    """
    mayor, menor, parche, rc_actual = parsear(actual)
    if nivel == "final":
        if rc:
            raise Negativa("final no lleva --rc")
        if rc_actual is None:
            raise Negativa(f"{actual} no es una RC: no hay nada que cerrar con final")
        return formatear(mayor, menor, parche)
    if nivel is None:
        if not rc:
            raise Negativa("falta el nivel: patch, minor, major o final")
        if rc_actual is None:
            raise Negativa(f"{actual} no es una RC: para abrir una usá patch, minor o major con --rc")
        return formatear(mayor, menor, parche, rc_actual + 1)
    if rc_actual is not None and not rc:
        raise Negativa(f"hay una RC abierta ({actual}): cerrala con final o seguí con --rc")
    mayor, menor, parche = {
        "major": (mayor + 1, 0, 0),
        "minor": (mayor, menor + 1, 0),
        "patch": (mayor, menor, parche + 1),
    }[nivel]
    return formatear(mayor, menor, parche, 1 if rc else None)


def armar_notas(asuntos):
    """Notas de la Release con los asuntos de commit `feat` y `fix`, en «Nuevo» y «Arreglos»."""
    grupos = {"feat": [], "fix": []}
    for asunto in asuntos:
        if m := RE_COMMIT.fullmatch(asunto.strip()):
            texto = m.group(2)
            grupos[m.group(1)].append(texto[:1].upper() + texto[1:])
    secciones = [
        f"## {titulo}\n\n" + "\n".join(f"- {linea}" for linea in grupos[tipo])
        for tipo, titulo in (("feat", "Nuevo"), ("fix", "Arreglos"))
        if grupos[tipo]
    ]
    return "\n\n".join(secciones) or "Sin cambios visibles."


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise Negativa(f"git {' '.join(args)} falló:\n{r.stderr.strip()}")
    return r


def leer_version():
    m = RE_VERSION.search(INIT.read_text(encoding="utf-8"))
    if not m:
        raise Negativa(f"no encuentro __version__ en {INIT}")
    return m.group(1)


def escribir_version(version):
    texto = INIT.read_text(encoding="utf-8")
    INIT.write_text(RE_VERSION.sub(f'__version__ = "{version}"', texto), encoding="utf-8")


def ultima_final():
    """Último tag de una versión final (sin -rc), o None si no hay ninguno."""
    r = git("describe", "--tags", "--abbrev=0", "--match", "v*", "--exclude", "*-rc*", check=False)
    return r.stdout.strip() or None


def chequear_repo():
    """Las tres negativas: cambios sin commitear, fuera de main, main divergida de origin/main."""
    if git("status", "--porcelain").stdout.strip():
        raise Negativa("hay cambios sin commitear")
    rama = git("branch", "--show-current").stdout.strip()
    if rama != "main":
        raise Negativa(f"estás en {rama or 'un HEAD suelto'}: las versiones salen de main")
    r = git("pull", "--ff-only", "-q", check=False)
    if r.returncode != 0:
        raise Negativa(f"no se pudo traer origin/main sin merge (¿divergió?):\n{r.stderr.strip()}")


def editar(notas):
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    comando = shlex.split(editor) if editor else ["notepad" if sys.platform == "win32" else "nano"]
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(notas)
    try:
        subprocess.run([*comando, f.name], check=True)
        return Path(f.name).read_text(encoding="utf-8").strip()
    finally:
        os.unlink(f.name)


def preguntar(notas):
    """Pregunta s/e/N hasta tener una respuesta; devuelve (pushear, notas)."""
    while True:
        try:
            r = input("¿Publicar? [s = sí, e = editar notas, N = no]: ").strip().lower()
        except EOFError:
            r = "n"
        if r == "e":
            notas = editar(notas)
            print(f"\n{notas}\n")
        else:
            return r == "s", notas


def main():
    parser = argparse.ArgumentParser(prog="version", description="Publica una versión de Pelis.")
    parser.add_argument("nivel", nargs="?", choices=["patch", "minor", "major", "final"])
    parser.add_argument("--rc", action="store_true", help="publicar como pre-release (-rcN)")
    parser.add_argument("--ver", action="store_true", help="solo mostrar la versión nueva y las notas")
    parser.add_argument("--notas", type=Path, help="archivo con las notas, en vez de armarlas")
    parser.add_argument("--si", action="store_true", help="publicar sin preguntar")
    args = parser.parse_args()

    chequear_repo()
    actual = leer_version()
    if git("tag", "-l", f"v{actual}").stdout.strip() and not git("ls-remote", "--tags", "origin", f"v{actual}").stdout.strip():
        raise Negativa(f"v{actual} quedó sin publicar (¿falló el push?). Publicala con: "
                       f"git push --atomic origin main v{actual}")
    nueva = siguiente(actual, args.nivel, args.rc)
    tag = f"v{nueva}"
    if git("tag", "-l", tag).stdout.strip():
        raise Negativa(f"el tag {tag} ya existe")
    desde = ultima_final()
    asuntos = git("log", "--format=%s", f"{desde}..HEAD" if desde else "HEAD").stdout.splitlines()
    notas = args.notas.read_text(encoding="utf-8").strip() if args.notas else armar_notas(asuntos)

    print(f"{actual} -> {nueva}{'  (pre-release)' if args.rc else ''}")
    print(f"Notas, desde {desde or 'el primer commit'}:\n\n{notas}\n")
    if args.ver:
        return
    pushear, notas = (True, notas) if args.si else preguntar(notas)

    escribir_version(nueva)
    git("commit", "-q", "-m", f"chore: versión {tag}", "--", str(INIT.relative_to(RAIZ)))
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(notas + "\n")
    try:
        git("tag", "-a", tag, "--cleanup=verbatim", "-F", f.name)
    finally:
        os.unlink(f.name)

    deshacer = f"Para deshacerlos: git tag -d {tag} && git reset --hard HEAD~1"
    if not pushear:
        print(f"El commit y el tag {tag} quedaron locales.")
        print(f"Para publicarlos: git push --atomic origin main {tag}")
        print(deshacer)
        return
    git("fetch", "-q", "origin")
    if git("rev-list", "--count", "HEAD..origin/main").stdout.strip() != "0":
        print("origin/main cambió mientras confirmabas: no se pusheó nada y las notas quedarían incompletas.")
        print(deshacer + " y volvé a correr el comando.")
        sys.exit(1)
    try:
        git("push", "-q", "--atomic", "origin", "main", tag)
    except Negativa as e:
        # No volver a correr el comando: subiría otra vez la versión
        print(f"{e}\nEl commit y el tag {tag} quedaron locales.")
        print(f"Para publicarlos: git push --atomic origin main {tag}")
        print(deshacer)
        sys.exit(1)
    print(f"Publicado {tag}: el workflow arma la Release.")


if __name__ == "__main__":
    try:
        main()
    except Negativa as e:
        sys.exit(f"No se puede: {e}")
    except KeyboardInterrupt:
        sys.exit(1)
