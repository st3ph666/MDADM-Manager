"""Suivi de progression des reconstructions mdadm."""

import re
from pathlib import Path


def lire_progression_rebuild(array_path):
    """Lit /proc/mdstat et retourne la progression recovery/resync/reshape/check."""
    nom = str(array_path or "").split("/")[-1]
    resultat = {
        "active": False,
        "action": "",
        "percent": None,
        "done_blocks": None,
        "total_blocks": None,
        "speed_kbs": None,
        "finish_minutes": None,
        "line": "",
    }
    try:
        texte = Path("/proc/mdstat").read_text(errors="replace")
    except Exception:
        return resultat

    lignes = texte.splitlines()
    debut = None
    for i, ligne in enumerate(lignes):
        if re.match(rf"^{re.escape(nom)}\s*:", ligne):
            debut = i
            break
    if debut is None:
        return resultat

    bloc = []
    for ligne in lignes[debut:]:
        if bloc and re.match(r"^md\d+\s*:", ligne):
            break
        bloc.append(ligne)
    brut = "\n".join(bloc)

    m = re.search(r"\b(recovery|resync|reshape|check|repair)\s*=\s*([0-9.]+)%\s*\((\d+)/(\d+)\)", brut, re.I)
    if not m:
        return resultat

    resultat["active"] = True
    resultat["action"] = m.group(1).lower()
    resultat["percent"] = float(m.group(2))
    resultat["done_blocks"] = int(m.group(3))
    resultat["total_blocks"] = int(m.group(4))
    resultat["line"] = m.group(0)

    vitesse = re.search(r"speed=([0-9.]+)([KMG])?/sec", brut, re.I)
    if vitesse:
        valeur = float(vitesse.group(1))
        unite = (vitesse.group(2) or "K").upper()
        facteur = {"K": 1.0, "M": 1024.0, "G": 1024.0 * 1024.0}.get(unite, 1.0)
        resultat["speed_kbs"] = valeur * facteur

    fin = re.search(r"finish=([0-9.]+)min", brut, re.I)
    if fin:
        resultat["finish_minutes"] = float(fin.group(1))
    return resultat


def texte_progression_rebuild(info):
    if not info or not info.get("active"):
        return "Aucune reconstruction en cours"
    pct = info.get("percent")
    action = str(info.get("action") or "rebuild").upper()
    vitesse = info.get("speed_kbs")
    fin = info.get("finish_minutes")
    morceaux = [f"{action} : {pct:.1f}%" if isinstance(pct, (int, float)) else action]
    if isinstance(vitesse, (int, float)):
        morceaux.append(f"{vitesse / 1024.0:.1f} MB/s")
    if isinstance(fin, (int, float)):
        heures = int(fin // 60)
        minutes = int(round(fin % 60))
        morceaux.append(f"reste ~{heures} h {minutes:02d} min" if heures else f"reste ~{minutes} min")
    return "  |  ".join(morceaux)
