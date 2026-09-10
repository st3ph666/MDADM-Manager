#!/usr/bin/env python3
"""One-time refactoring utility for MDADM Manager v1.49."""

from __future__ import annotations

import ast
import io
import re
import tokenize
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mdadm_manager_v1.48.py"
PACKAGE = ROOT / "mdadm_matrix"
README = ROOT / "README.md"
PYPROJECT = ROOT / "pyproject.toml"
NEW_LAUNCHER = ROOT / "mdadm_manager_v1.49.py"

FRENCH_HINTS = re.compile(
    r"[àâçéèêëîïôûùüÿœ]|\b("
    r"affiche|ajoute|analyse|ancien|ancienne|aucun|avec|avant|barre|cache|"
    r"chemin|choix|commande|construit|couleur|création|crée|dans|défaut|"
    r"démarrage|détect|disque|données|efface|enregistre|entrée|étape|"
    r"exécute|fenêtre|fichier|garde|interface|langue|lecture|ligne|membre|"
    r"modèle|montage|nouveau|permet|périphérique|pour|protège|rafraîch|"
    r"remplacement|retourne|sauvegarde|sélection|sécur|système|utilise|"
    r"vérifie|valeur|vrai|vraie|uniquement|lorsque|pendant|reste|"
    r"plusieurs|petit|petite|même|peut|doit|sont|est|les|des|une|un|du|de|la|le)\b",
    re.IGNORECASE,
)


def remove_docstrings(source: str) -> str:
    """Remove module, class, and function docstrings while preserving line numbers."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    lines = source.splitlines(keepends=True)
    ranges: list[tuple[int, int]] = []

    def visit_body(body):
        if body and isinstance(body[0], ast.Expr):
            value = body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                ranges.append((body[0].lineno, body[0].end_lineno or body[0].lineno))
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit_body(node.body)

    visit_body(tree.body)
    for start, end in sorted(ranges, reverse=True):
        for index in range(start - 1, end):
            lines[index] = "\n" if lines[index].endswith("\n") else ""
    return "".join(lines)


def clean_comment_text(comment: str) -> str:
    """Return an English-only comment or an empty string."""
    stripped = comment.strip()
    if stripped.startswith("#!") or "coding:" in stripped:
        return comment
    if stripped.startswith("# BEGINNER: FR") or stripped.startswith("# FR"):
        return ""
    if stripped.startswith("# BEGINNER: EN"):
        text = stripped.split("EN", 1)[1].lstrip(" :—-")
        return f"# {text}" if text else ""
    if stripped.startswith("# EN"):
        text = stripped.split("EN", 1)[1].lstrip(" :—-")
        return f"# {text}" if text else ""
    if " / MODULE " in stripped:
        return "# MODULE " + stripped.split(" / MODULE ", 1)[1]
    if " / STEP " in stripped:
        return "# STEP " + stripped.split(" / STEP ", 1)[1]
    if " / APPLICATION " in stripped:
        return "# APPLICATION " + stripped.split(" / APPLICATION ", 1)[1]
    if FRENCH_HINTS.search(stripped.lstrip("#").strip()):
        return ""
    return comment


def strip_french_comments(source: str) -> str:
    """Remove French comments and keep English comments."""
    source = remove_docstrings(source)
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                token = tokenize.TokenInfo(token.type, clean_comment_text(token.string), token.start, token.end, token.line)
            tokens.append(token)
        return tokenize.untokenize(tokens)
    except (tokenize.TokenError, IndentationError):
        return source


def section(source: str, number: int) -> str:
    """Extract the real numbered code module, ignoring the architecture guide."""
    marker = re.compile(rf"^# MODULE {number}\b.*$", re.MULTILINE)
    matches = list(marker.finditer(source))
    if not matches:
        raise RuntimeError(f"Module marker {number} not found")
    match = matches[-1]
    start = source.find("\n", match.end()) + 1
    if number < 9:
        next_matches = list(re.compile(rf"^# MODULE {number + 1}\b.*$", re.MULTILINE).finditer(source))
        if not next_matches:
            raise RuntimeError(f"Next module marker after {number} not found")
        end = next_matches[-1].start()
    else:
        end = len(source)
    return source[start:end].strip("\n") + "\n"


def english_header(title: str) -> str:
    return f'"""{title}"""\n\n'


def build_i18n(parts: dict[int, str]) -> str:
    return english_header("Internationalization helpers for MDADM Manager.") + "from pathlib import Path\n\n" + strip_french_comments(parts[1])


def build_system(parts: dict[int, str]) -> str:
    return english_header("System command and privilege helpers for MDADM Manager.") + "import os\nimport sys\nimport shlex\nimport shutil\nimport subprocess\nfrom pathlib import Path\n\n" + strip_french_comments(parts[2])


def build_core(parts: dict[int, str]) -> str:
    body = "\n\n".join(strip_french_comments(parts[n]).strip() for n in (3, 4, 5)) + "\n"
    return english_header("RAID discovery, SMART analysis, and safety helpers.") + "import math\nimport re\nimport shutil\nfrom pathlib import Path\n\nfrom .system import run\n\n" + body


def build_gui_common(parts: dict[int, str]) -> str:
    return english_header("Shared Tkinter GUI infrastructure for MDADM Manager.") + "import tkinter as tk\nfrom tkinter import ttk, messagebox\n\nfrom .i18n import ui_text\n\n" + strip_french_comments(parts[6])


def build_wizard(parts: dict[int, str]) -> str:
    return english_header("RAID creation wizard for MDADM Manager.") + "import re\nimport time\nimport tkinter as tk\nfrom tkinter import ttk, messagebox\nfrom pathlib import Path\n\nfrom . import APP_VERSION\nfrom .i18n import tr, ui_text\nfrom .system import run, shell_join\nfrom .core import *  # noqa: F403,F401\nfrom .gui_common import ConfirmDialog\n\n" + strip_french_comments(parts[7])


def build_app(parts: dict[int, str]) -> str:
    body = strip_french_comments(parts[8])
    body = re.sub(r"^\s*global\s+CURRENT_LANGUAGE\s*$", "", body, flags=re.MULTILINE)
    body = re.sub(r"\bCURRENT_LANGUAGE\b", "i18n.CURRENT_LANGUAGE", body)
    return english_header("Main Tkinter application for MDADM Manager.") + "import re\nimport shlex\nimport shutil\nimport threading\nimport time\nimport tkinter as tk\nfrom tkinter import ttk, messagebox, simpledialog, filedialog\nfrom pathlib import Path\n\nfrom . import APP_TITLE, APP_VERSION\nfrom . import i18n\nfrom .i18n import LANGUAGES, ui_text, save_language, tr\nfrom .system import run, shell_join, privileged_cmd\nfrom .core import *  # noqa: F403,F401\nfrom .gui_common import ConfirmDialog\nfrom .wizard import RaidCreationWizard\n\n" + body


def build_main(parts: dict[int, str]) -> str:
    body = strip_french_comments(parts[9])
    marker = 'if __name__ == "__main__":'
    if marker not in body:
        raise RuntimeError("Legacy startup block not found")
    before, startup = body.split(marker, 1)
    indented = "\n".join("    " + line if line.strip() else "" for line in startup.lstrip("\n").splitlines())
    return english_header("Application entry point for MDADM Manager.") + "import os\nimport shutil\nimport tkinter as tk\nfrom tkinter import messagebox\n\nfrom . import APP_VERSION\nfrom .system import relaunch_as_root\nfrom .app import MdadmManager\n\n" + before.strip() + "\n\ndef main():\n" + indented + "\n\nif __name__ == \"__main__\":\n    main()\n"


def update_readme(text: str) -> str:
    text = text.replace("v1.48 RC1", "v1.49 RC1").replace("v1.48 Stable", "v1.49 Stable").replace("mdadm_manager_v1.48.py", "mdadm_manager_v1.49.py").replace("MDADM Manager v1.48", "MDADM Manager v1.49")
    architecture = '''\n## Modular Architecture\n\nStarting with **v1.49 RC1**, MDADM Manager uses a modular source layout while keeping a small versioned launcher for compatibility.\n\n```text\nmdadm_manager_v1.49.py      # Compatibility launcher\nmdadm_matrix/\n├── __init__.py             # Application version metadata\n├── i18n.py                 # French / English interface translations\n├── system.py               # System commands and privilege escalation\n├── core.py                 # RAID discovery, SMART and safety checks\n├── gui_common.py           # Shared Tkinter helpers\n├── wizard.py               # RAID creation wizard\n├── app.py                  # Main Tkinter application and RAID workflows\n└── main.py                 # Application startup\n```\n\nSource-code comments are maintained in **English only**. The graphical interface remains bilingual (French / English).\n\n---\n\n'''
    if "## Modular Architecture" in text:
        text = re.sub(r"\n## Modular Architecture\n.*?\n---\n", architecture, text, count=1, flags=re.S)
    elif "## Main Features" in text:
        text = text.replace("## Main Features", architecture + "## Main Features", 1)
    return text


def main() -> None:
    if SOURCE.exists():
        source = SOURCE.read_text(encoding="utf-8")
    else:
        revisions = subprocess.check_output(["git", "rev-list", "--all", "--", SOURCE.name], cwd=ROOT, text=True).splitlines()
        source = ""
        for revision in revisions:
            try:
                source = subprocess.check_output(["git", "show", f"{revision}:{SOURCE.name}"], cwd=ROOT, text=True)
                break
            except subprocess.CalledProcessError:
                continue
        if not source:
            raise RuntimeError("Unable to recover mdadm_manager_v1.48.py from Git history")

    parts = {n: section(source, n) for n in range(1, 10)}
    PACKAGE.mkdir(exist_ok=True)
    (PACKAGE / "__init__.py").write_text('"""MDADM Manager package."""\n\nAPP_VERSION = "1.49"\nAPP_TITLE = f"MDADM Manager v{APP_VERSION} // MATRIX ROOT"\n', encoding="utf-8")
    (PACKAGE / "i18n.py").write_text(build_i18n(parts), encoding="utf-8")
    (PACKAGE / "system.py").write_text(build_system(parts), encoding="utf-8")
    (PACKAGE / "core.py").write_text(build_core(parts), encoding="utf-8")
    (PACKAGE / "gui_common.py").write_text(build_gui_common(parts), encoding="utf-8")
    (PACKAGE / "wizard.py").write_text(build_wizard(parts), encoding="utf-8")
    (PACKAGE / "app.py").write_text(build_app(parts), encoding="utf-8")
    (PACKAGE / "main.py").write_text(build_main(parts), encoding="utf-8")
    for obsolete in (PACKAGE / "gui.py",):
        if obsolete.exists():
            obsolete.unlink()

    NEW_LAUNCHER.write_text('#!/usr/bin/env python3\n"""Compatibility launcher for MDADM Manager v1.49."""\n\nfrom mdadm_matrix.main import main\n\nif __name__ == "__main__":\n    main()\n', encoding="utf-8")
    NEW_LAUNCHER.chmod(0o755)

    if README.exists():
        README.write_text(update_readme(README.read_text(encoding="utf-8")), encoding="utf-8")
    if PYPROJECT.exists():
        pyproject = re.sub(r'^version\s*=\s*"[^"]+"', 'version = "1.49"', PYPROJECT.read_text(encoding="utf-8"), flags=re.MULTILINE)
        PYPROJECT.write_text(pyproject, encoding="utf-8")
    if SOURCE.exists():
        SOURCE.unlink()
    shutil.rmtree(ROOT / "__pycache__", ignore_errors=True)
    shutil.rmtree(PACKAGE / "__pycache__", ignore_errors=True)
    old_ignore = ROOT / "gitignore"
    proper_ignore = ROOT / ".gitignore"
    if old_ignore.exists() and not proper_ignore.exists():
        old_ignore.rename(proper_ignore)


if __name__ == "__main__":
    main()
