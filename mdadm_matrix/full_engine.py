"""Compatibility bridge to the current MDADM Manager v1.76 engine.

The project keeps a modular launcher/package while v1.76 remains a single-file
reference engine. New components can be extracted into mdadm_matrix modules
progressively without losing current user-visible behaviour or safety checks.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

_ENGINE: ModuleType | None = None

def engine_path() -> Path:
    return Path(__file__).resolve().parent.parent / "mdadm_manager_v1.76.py"

def load_engine() -> ModuleType:
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE
    path = engine_path()
    if not path.exists():
        raise FileNotFoundError(f"MDADM Manager v1.76 engine not found: {path}")
    spec = importlib.util.spec_from_file_location("mdadm_manager_v176_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load MDADM Manager v1.76 engine: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _ENGINE = module
    return module

def get_symbol(name: str):
    module = load_engine()
    try:
        return getattr(module, name)
    except AttributeError as exc:
        raise ImportError(f"Symbol not found in v1.76 engine: {name}") from exc
