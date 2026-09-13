"""Chargement contrôlé du moteur complet v1.75.

Ce module garantit que le lanceur modulaire utilise exactement les fonctions
présentes dans le script FULL pendant la migration progressive vers des modules
indépendants. Il évite qu'une fonction ajoutée entre v1.61 et v1.75 disparaisse.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


_ENGINE: ModuleType | None = None


def engine_path() -> Path:
    return Path(__file__).resolve().parent.parent / "mdadm_manager_v1.75_full.py"


def load_engine() -> ModuleType:
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    path = engine_path()
    if not path.exists():
        raise FileNotFoundError(f"Moteur v1.75 introuvable : {path}")

    spec = importlib.util.spec_from_file_location("mdadm_manager_v175_full_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger le moteur v1.75 : {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _ENGINE = module
    return module


def get_symbol(name: str):
    module = load_engine()
    try:
        return getattr(module, name)
    except AttributeError as exc:
        raise ImportError(f"Symbole v1.75 introuvable : {name}") from exc
