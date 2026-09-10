"""Application entry point for MDADM Manager."""

import os
import shutil
import tkinter as tk
from tkinter import messagebox

from . import APP_VERSION
from .system import relaunch_as_root
from .gui import MdadmManager

#   dependency_check + bloc __main__
#



#
# =============================================================================



# =============================================================================

# =============================================================================
#

# ----------------------------



#    elles lisent Linux, mdadm, lsblk, SMART, fstab, etc.









#
# HOW TO READ THIS FILE
# --------------------------
# 1) The program intentionally lives in ONE Python file, but it is split into
#    9 clearly identified logical modules.
# 2) Functions located before the classes are mostly HELPERS: they read Linux,
#    mdadm, lsblk, SMART, fstab, and related system information.
# 3) RaidCreationWizard builds the guided RAID creation window.
# 4) MdadmManager is the application's main window.
# 5) Methods beginning with "_build_" only construct Tkinter GUI sections.
# 6) Methods beginning with "refresh_" reread system state and update the GUI.
# 7) "manage_*" methods perform mdadm operations on an array.
# 8) Every destructive command must go through RAID/FSTAB safety checks.
#    DO NOT bypass those checks when modifying the program.
#
# MINI GLOSSAIRE / MINI GLOSSARY
# ------------------------------








#

#   function        = reusable code block called with name(...)
#   method          = function owned by a class (self is the current object)
#   class           = blueprint used to build a window/object
#   dictionary      = key -> value structure, e.g. {"state": "clean"}
#   list            = ordered collection, e.g. ["/dev/sda", "/dev/sdb"]
#   callback        = function called by Tkinter after a click/event
#   thread          = parallel work used to keep the GUI responsive
#
# CONSEIL / TIP:


#   To trace an action, start from the button text in "_build_*", find its
#   command=... parameter, then follow the referenced method.
#
# =============================================================================

# =============================================================================
# MODULE 1 — INTERNATIONALIZATION
# =============================================================================

LANGUAGES = {
    "fr": "Français",
    "en": "English",
}

I18N = {
    "fr": {
        "language": "Langue",
        "french": "Français",
        "english": "English",
        "language_changed": "Langue modifiée",
        "language_restart": (
            "La langue a été enregistrée.\n\n"
            "Elle sera appliquée complètement au prochain démarrage de l'application."
        ),
        "dashboard": "Tableau de bord",
        "create_raid": "Créer un RAID",
        "manage_raid": "Gérer un RAID",
        "disks": "Disques",
        "configuration": "Configuration mdadm",
        "raid_info": "Info RAID",
        "raid_wizard": "Assistant de création RAID",
        "wizard_launch": "▶ LANCER L'ASSISTANT DE CRÉATION RAID",
        "refresh": "Rafraîchir",
        "cancel": "Annuler",
        "next": "Suivant ▶",
        "previous": "◀ Précédent",
        "create": "CRÉER LE RAID",
        "protected": "PROTÉGÉ",
        "available": "DISPONIBLE",
    },
    "en": {
        "language": "Language",
        "french": "French",
        "english": "English",
        "language_changed": "Language changed",
        "language_restart": (
            "The language setting has been saved.\n\n"
            "It will be fully applied the next time the application starts."
        ),
        "dashboard": "Dashboard",
        "create_raid": "Create RAID",
        "manage_raid": "Manage RAID",
        "disks": "Disks",
        "configuration": "mdadm Configuration",
        "raid_info": "RAID Info",
        "raid_wizard": "RAID Creation Wizard",
        "wizard_launch": "▶ START RAID CREATION WIZARD",
        "refresh": "Refresh",
        "cancel": "Cancel",
        "next": "Next ▶",
        "previous": "◀ Previous",
        "create": "CREATE RAID",
        "protected": "PROTECTED",
        "available": "AVAILABLE",
    },
}



FR_EN_TEXT = {
    "Température": "Temperature",
    "TEMPÉRATURE": "TEMPERATURE",
    "Tableau de bord": "Dashboard", "Créer un RAID": "Create RAID",
    "Gérer un RAID": "Manage RAID", "Disques": "Disks",
    "Configuration mdadm": "mdadm Configuration", "Info RAID": "RAID Info",
    "Rafraîchir": "Refresh", "Actualiser": "Refresh", "Annuler": "Cancel",
    "Fermer": "Close", "Suivant": "Next", "Précédent": "Previous",
    "Créer": "Create", "Supprimer": "Delete", "Remplacer": "Replace",
    "Arrêter": "Stop", "Démarrer": "Start", "Assembler": "Assemble",
    "Détails": "Details", "État": "State", "Taille": "Size",
    "Modèle": "Model", "Série": "Serial", "Montage": "Mount",
    "Point de montage": "Mount point", "Système de fichiers": "Filesystem",
    "Membre": "Member", "Membres": "Members", "Disponible": "Available",
    "Protégé": "Protected", "Protection": "Protection",
    "Sélection": "Selection", "Commande": "Command", "Résultat": "Result",
    "Erreur": "Error", "Attention": "Warning", "Confirmation": "Confirmation",
    "Analyse": "Analysis", "Analyse…": "Analyzing…", "À analyser": "To analyze",
    "Aucun": "None", "Aucune": "None", "Oui": "Yes", "Non": "No",
    "INCONNU": "UNKNOWN", "ÉCHEC": "FAIL", "Usure estimée": "Estimated wear",
    "Usure / Risque": "Wear / Risk", "Risque": "Risk",
    "Heures": "Hours", "Jours": "Days",
    "Assistant de création RAID": "RAID Creation Wizard",
    "Type de RAID": "RAID type", "Sélection des disques": "Disk selection",
    "Options": "Options", "Résumé": "Summary",
    "Capacité estimée": "Estimated capacity",
    "Disques sélectionnés": "Selected disks",
    "Disques physiques": "Physical disks", "RAID protégés": "Protected RAID",
    "FSTAB protégés": "Protected FSTAB",
    "FS/montage occupés": "FS/mount in use", "DISPONIBLES": "AVAILABLE",
    "SMART : analysé à l'étape suivante": "SMART: analyzed in the next step",
    "Possible": "Possible", "Impossible": "Impossible", "manque": "missing",
    "disque libre": "free disk", "disques libres": "free disks",
    "Niveau RAID": "RAID level", "Tolérance aux pannes": "Fault tolerance",
    "Nombre minimum de disques": "Minimum number of disks",
    "Mode avancé": "Advanced mode",
    "Afficher les disques occupés": "Show disks in use",
    "Métadonnées": "Metadata", "Bitmap": "Bitmap", "Nom du RAID": "RAID name",
    "Vérification finale": "Final verification",
    "Configuration chargée": "Configuration loaded",
    "Configuration sauvegardée": "Configuration saved",
    "Charger": "Load", "Sauvegarder": "Save", "Enregistrer sous": "Save As",
    "Membre actif": "Active member", "Membre défaillant": "Failed member",
    "Dégradé": "Degraded", "Actif": "Active", "Inactif": "Inactive",
    "Synchronisation": "Synchronization", "Progression": "Progress",
    "Vitesse": "Speed", "Temps restant": "Time remaining",
    "Périphérique": "Device", "Partition membre": "Member partition",
    "État RAID": "RAID state", "Erreurs": "Errors", "Utilisation": "Usage",
    "Santé SMART": "SMART health", "Informations SMART": "SMART information",
    "INDICE DE RISQUE HDD": "HDD RISK INDEX", "USURE SMART": "SMART WEAR",
    "Indice statistique de surveillance, pas une durée de vie restante.":
        "Statistical monitoring index, not remaining drive life.",
    "PROTECTION RAID ACTIVE": "ACTIVE RAID PROTECTION",
    "PROTECTION FSTAB ACTIVE": "ACTIVE FSTAB PROTECTION",
    "L'opération destructive est bloquée.": "The destructive operation is blocked.",
    "Aucun RAID détecté.": "No RAID detected.",
    "Aucun disque détecté.": "No disk detected.",
    
    "GUIDE VISUEL DES TYPES DE RAID": "VISUAL GUIDE TO RAID TYPES",
    "Le RAID combine plusieurs disques pour obtenir plus de vitesse, plus de capacité ou de la redondance. IMPORTANT : un RAID ne remplace jamais une sauvegarde.": "RAID combines multiple disks to provide more speed, capacity, or redundancy. IMPORTANT: RAID never replaces a backup.",
    "RAPIDE, MAIS AUCUNE PROTECTION": "FAST, BUT NO PROTECTION",
    "MIROIR + PERFORMANCE": "MIRROR + PERFORMANCE",
    "DOUBLE PARITÉ": "DUAL PARITY",
    "1 DISQUE DE PARITÉ": "1 PARITY DISK",
    "Minimum :": "Minimum:",
    "Tolérance aux pannes :": "Fault tolerance:",
    "Tolérance :": "Tolerance:",
    "Capacité utile :": "Usable capacity:",
    "Usage :": "Use:",
    "Avantage :": "Advantage:",
    "Risque :": "Risk:",
    "AUCUNE": "NONE",
    "disques": "disks",
    "disque": "disk",
    "de la capacité totale": "of total capacity",
    "avec 2 disques": "with 2 disks",
    "taille du plus petit disque": "size of the smallest disk",
    "environ": "about",
    "fichiers temporaires, gros débit, données non critiques": "temporary files, high throughput, non-critical data",
    "système et données importantes": "system and important data",
    "stockage général": "general storage",
    "gros ensembles RAID et données importantes": "large RAID arrays and important data",
    "serveur, VM, bases de données, gros débit": "server, VMs, databases, high throughput",
    "performances maximales": "maximum performance",
    "simple et sécuritaire": "simple and secure",
    "bon compromis capacité/protection": "good capacity/protection compromise",
    "peut survivre à 2 pannes": "can survive 2 failures",
    "très bonnes performances + redondance": "very good performance + redundancy",
    "1 seul disque en panne = RAID complet perdu": "1 disk failure = entire RAID lost",
    "capacité divisée par deux": "capacity divided by two",
    "reconstruction plus lourde sur gros volumes": "heavier rebuild on large volumes",
    "écritures/reconstruction plus lourdes": "heavier writes/rebuild",
    "nécessite davantage de disques": "requires more disks",
    "dépend de quels disques tombent en panne": "depends on which disks fail",
    "DONNÉES": "DATA", "DISQUE": "DISK", "MIROIR": "MIRROR",
    "PARITÉ": "PARITY",
    "CHOIX RAPIDE": "QUICK GUIDE",
    "vitesse maximale, aucune protection": "maximum speed, no protection",
    "simple et sécuritaire avec 2 disques": "simple and secure with 2 disks",
    "bon compromis capacité/protection, 1 panne tolérée": "good capacity/protection compromise, tolerates 1 failure",
    "meilleur choix quand 2 pannes doivent être tolérées": "best choice when 2 failures must be tolerated",
    "excellent mélange performance/redondance": "excellent performance/redundancy mix",
    "Plus le RAID contient de disques et plus sa reconstruction est longue, plus RAID 6 ou RAID 10 devient intéressant pour des données importantes.": "The more disks a RAID contains, the longer its rebuild takes; RAID 6 or RAID 10 therefore becomes more attractive for important data.",
    "DISQUES MEMBRES DU RAID": "RAID MEMBER DISKS",
    "N° série": "Serial No.", "Erreurs / secteurs": "Errors / sectors",
    "Aucun disque sélectionné": "No disk selected",
    "Marquer FAULTY": "Mark FAULTY", "Retirer": "Remove",
    "REMPLACER LE DISQUE": "REPLACE DISK",
    "Ce que l'assistant vérifie": "What the wizard checks",
    "Repères rapides": "Quick reference",
    "sélectionne directement le disque sur lequel agir": "select the disk to act on directly",
    "Retirer sélection": "Remove selected", "Faulty sélection": "Mark selected FAULTY",
    "Remplacer sélection": "Replace selected",
    "SMART du disque sélectionné": "SMART for selected disk",
    "Fichier actuellement chargé :": "Currently loaded file:",
    "Charger mdadm.conf": "Load mdadm.conf", "Scanner les arrays": "Scan arrays",
    "Sauvegarder mdadm.conf": "Save mdadm.conf", "Sauvegarder une copie": "Save a copy",
    "Sélectionne un array.": "Select an array.",
    "Montage :": "Mount:",
    "ÉTAT :": "STATE:", "TAILLE :": "SIZE:", "ACTIFS :": "ACTIVE:",
    "SANTÉ :": "HEALTH:", "MONTAGE :": "MOUNT:", "ESPACE :": "SPACE:",
    "LIBRE :": "FREE:", "utilisés": "used", "utilisé": "used",
    "INFORMATIONS DE MONTAGE": "MOUNT INFORMATION",
    "Rafraîchissement": "Refresh", "Prêt": "Ready",
    "Disque sélectionné :": "Selected disk:",

    
    "ASSISTANT DE CRÉATION RAID": "RAID CREATION WIZARD",
    "Création guidée en 4 étapes : choix du niveau RAID, analyse et sélection des disques, paramètres, puis vérification finale.":
        "Guided creation in 4 steps: choose the RAID level, analyze and select disks, set parameters, then perform the final verification.",
    "Modèle, numéro de série, taille et type HDD / SSD / NVMe":
        "Model, serial number, size and HDD / SSD / NVMe type",
    "État SMART, heures de fonctionnement et usure / risque":
        "SMART status, power-on hours and wear / risk",
    "RAID actuel, partitions, systèmes de fichiers et points de montage":
        "Current RAID, partitions, filesystems and mount points",
    "Capacité utile estimée selon RAID 0 / 1 / 5 / 6 / 10":
        "Estimated usable capacity for RAID 0 / 1 / 5 / 6 / 10",
    "Comptage rapide des disques libres sans attendre SMART":
        "Quick count of free disks without waiting for SMART",
    "SMART détaillé à la demande, sans bloquer l'assistant":
        "Detailed SMART on demand, without blocking the wizard",
    "Niveaux RAID impossibles automatiquement grisés":
        "Unavailable RAID levels are automatically grayed out",
    "Tolérance aux pannes et nombre minimal de disques":
        "Fault tolerance and minimum number of disks",
    "Protection ABSOLUE des disques déjà membres d'un RAID existant":
        "ABSOLUTE protection for disks already belonging to an existing RAID",
    "Protection ABSOLUE des disques/partitions référencés dans /etc/fstab":
        "ABSOLUTE protection for disks/partitions referenced in /etc/fstab",
    "Détection fstab par /dev, UUID, PARTUUID, LABEL et PARTLABEL":
        "fstab detection by /dev, UUID, PARTUUID, LABEL and PARTLABEL",
    "Analyse mdadm --examine des anciennes métadonnées RAID":
        "mdadm --examine analysis of old RAID metadata",
    "--zero-superblock proposé seulement pour un ancien RAID orphelin":
        "--zero-superblock offered only for an orphaned old RAID",
    "Le mode avancé ne peut jamais contourner RAID ou FSTAB":
        "Advanced mode can never bypass RAID or FSTAB protection",
    "Vérification finale de la commande mdadm avant écriture":
        "Final verification of the mdadm command before writing",
    "Interface Français / English sélectionnable et mémorisée":
        "Selectable French / English interface with saved preference",
    "performances / capacité, aucune protection":
        "performance / capacity, no protection",
    "miroir simple, très facile à comprendre et reconstruire":
        "simple mirror, very easy to understand and rebuild",
    "1 disque de parité, tolère 1 panne":
        "1 parity disk, tolerates 1 failure",
    "2 disques de parité, tolère 2 pannes":
        "2 parity disks, tolerates 2 failures",
    "miroir + performances, excellent choix avec plusieurs disques":
        "mirror + performance, excellent choice with multiple disks",
    "La capacité réelle est limitée par le plus petit disque de l'ensemble.":
        "Actual capacity is limited by the smallest disk in the array.",
    "Ajouter membre": "Add member",
    "Exécuter :": "Execute:",

    # v1.33 — assistant RAID complet
    "Analyse des disques disponibles…": "Analyzing available disks…",
    "Choisis le type de RAID selon ton objectif": "Choose the RAID type based on your goal",
    "Performance maximale": "Maximum performance",
    "Aucune tolérance de panne": "No fault tolerance",
    "Miroir": "Mirror",
    "Tolère au moins 1 panne avec 2 disques": "Tolerates at least 1 disk failure with 2 disks",
    "Capacité + protection": "Capacity + protection",
    "Tolère la panne de 1 disque": "Tolerates 1 disk failure",
    "Double parité": "Dual parity",
    "Tolère la panne de 2 disques": "Tolerates 2 disk failures",
    "Performance + miroir": "Performance + mirror",
    "Tolérance dépend des disques en panne et des paires": "Fault tolerance depends on which disks fail and on mirror pairs",
    "Minimum :": "Minimum:",
    "disques": "disks",
    "disque": "disk",
    "Explication": "Explanation",
    "Impossible — manque": "Impossible — missing",
    "Possible —": "Possible —",
    "Aucun niveau RAID proposé ne peut être créé avec les disques actuellement considérés libres. Libère ou ajoute des disques.": "None of the proposed RAID levels can be created with the disks currently considered free. Free up or add disks.",
    "Pas assez de disques libres pour créer un RAID avec les niveaux proposés.": "Not enough free disks to create a RAID with the proposed levels.",
    "Tolérance :": "Fault tolerance:",
    "Étape 2 — Choix des disques": "Step 2 — Disk selection",
    "Étape 3 — Paramètres": "Step 3 — Settings",
    "Étape 4 — Vérification et création": "Step 4 — Review and creation",
    "Assistant RAID": "RAID Wizard",
    "Étape": "Step",
    "sur": "of",
    "Les données sont réparties sur tous les disques. Très rapide, mais la panne d'un seul disque détruit l'ensemble du RAID.": "Data is striped across all disks. Very fast, but a single disk failure destroys the entire RAID.",
    "Chaque donnée est copiée sur tous les membres. Très sécurisant, mais la capacité utile correspond au plus petit disque.": "Each piece of data is copied to all members. Very safe, but usable capacity is limited to the smallest disk.",
    "Parité distribuée. Bon compromis capacité/protection, mais une reconstruction peut être longue sur de gros HDD.": "Distributed parity. Good capacity/protection compromise, but rebuilding can take a long time on large HDDs.",
    "Deux parités distribuées. Plus sécuritaire que RAID 5 pour les grands ensembles, au prix de deux disques de capacité.": "Dual distributed parity. Safer than RAID 5 for large arrays, at the cost of two disks of capacity.",
    "Combine mirroring et striping. Très bonnes performances et reconstruction généralement plus simple. Un nombre pair de disques est recommandé.": "Combines mirroring and striping. Very good performance and generally simpler rebuilding. An even number of disks is recommended.",
}


# Translates an already-built UI string from French to English when the active language is English.
def ui_text(value):
    if CURRENT_LANGUAGE != "en" or not isinstance(value, str):
        return value
    result = FR_EN_TEXT.get(value, value)
    for fr, en in sorted(FR_EN_TEXT.items(), key=lambda x: len(x[0]), reverse=True):
        result = result.replace(fr, en)
    extra = (
        ("Étape 1 — Type de RAID", "Step 1 — RAID type"),
        ("Étape 2 — Sélection des disques", "Step 2 — Disk selection"),
        ("Étape 3 — Options", "Step 3 — Options"),
        ("Étape 4 — Vérification finale", "Step 4 — Final review"),
        ("Analyse impossible", "Analysis failed"),
        ("ERREUR D'ANALYSE", "ANALYSIS ERROR"),
        ("disque(s) libre(s)", "free disk(s)"),
        ("Libère ou ajoute des disques.", "Free up or add disks."),
        ("L'analyse des disques a échoué.", "Disk analysis failed."),
    )
    for fr, en in extra:
        result = result.replace(fr, en)
    return result



# Returns the path of the small file that remembers the user's selected language.
def language_config_path():
    base = Path.home() / ".config" / "mdadm-manager"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return base / "language.conf"



# Reads the saved language; on error or unknown value, French is used as the default.
def load_language():
    try:
        value = language_config_path().read_text(encoding="utf-8").strip().lower()
        if value in LANGUAGES:
            return value
    except Exception:
        pass
    return "fr"



# Saves the language code in the user's configuration directory.
def save_language(code):
    if code not in LANGUAGES:
        return False
    try:
        language_config_path().write_text(code + "\n", encoding="utf-8")
        return True
    except Exception:
        return False


CURRENT_LANGUAGE = load_language()



# Main key-based translation entry point. Use tr(...) for fixed GUI text.
def tr(key):
    value = I18N.get(CURRENT_LANGUAGE, I18N["fr"]).get(
        key,
        I18N["fr"].get(key, key)
    )
    return ui_text(value)

MDADM_CONF = "/etc/mdadm/mdadm.conf"



# =============================================================================
# MODULE 2 — SYSTEM COMMANDS AND PRIVILEGES
# =============================================================================


# Runs a system command without a shell, captures stdout/stderr, and protects the app with a timeout.
def run(cmd, timeout=20):
    try:
        p = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False
        )
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except Exception as exc:
        return 1, str(exc)



# Turns an argument list into a safely quoted readable command, mainly for kdesu.
def shell_join(cmd):
    return " ".join(shlex.quote(str(x)) for x in cmd)



# Central hook intended to prepare a command that requires root privileges.
def privileged_cmd(cmd):
    return list(cmd)




# Looks for the kdesu executable in several possible KDE locations.
def find_kdesu():

    candidates = [
        shutil.which("kdesu"),
        shutil.which("kdesu5"),
        shutil.which("kdesu6"),
        "/usr/lib/x86_64-linux-gnu/libexec/kf6/kdesu",
        "/usr/lib/x86_64-linux-gnu/libexec/kf5/kdesu",
        "/usr/libexec/kf6/kdesu",
        "/usr/libexec/kf5/kdesu",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None



# Relaunches this same script with administrator rights using kdesu, then pkexec as fallback.
def relaunch_as_root():

    script = str(Path(__file__).resolve())
    python_exe = sys.executable or "/usr/bin/python3"

    
    kdesu = find_kdesu()
    if kdesu:
        command = shell_join([python_exe, script])
        try:
            subprocess.Popen([kdesu, "-c", command])
            return True, "kdesu"
        except Exception:
            pass

    # Secours PolicyKit.
    pkexec = shutil.which("pkexec")
    if pkexec:
        cmd = [pkexec, "env"]
        for var in ("DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR"):
            value = os.environ.get(var)
            if value:
                cmd.append(f"{var}={value}")
        cmd += [python_exe, script]

        try:
            subprocess.Popen(cmd)
            return True, "pkexec"
        except Exception:
            pass

    return False, None



# =============================================================================
# MODULE 3 — RAID AND DEVICE DISCOVERY
# =============================================================================


# Reads /proc/mdstat and returns the mdadm arrays that are currently assembled.
def get_md_arrays():

    arrays = []
    mdstat = Path("/proc/mdstat")
    if not mdstat.exists():
        return arrays
    text = mdstat.read_text(errors="replace")
    for line in text.splitlines():
        m = re.match(r"^(md\d+)\s*:\s*(\w+)\s+(\S+)\s+(.*)$", line)
        if m:
            name, state, level, rest = m.groups()
            arrays.append({
                "name": name,
                "path": f"/dev/{name}",
                "state": state,
                "level": level,
                "members": rest.strip(),
            })
    return arrays



# Uses lsblk JSON output to inventory disks, partitions, sizes, models, UUIDs, and mounts.
def get_block_devices():

    cmd = [
        "lsblk", "-J", "-b",
        "-o", "NAME,PATH,TYPE,SIZE,MODEL,SERIAL,FSTYPE,LABEL,UUID,MOUNTPOINTS"
    ]
    rc, out = run(cmd)
    if rc != 0:
        return []
    import json
    try:
        data = json.loads(out)
    except Exception:
        return []

    result = []

    
    # Recursively walks the lsblk JSON tree so no child partition/device is missed.
    def walk(nodes):
        for n in nodes:
            result.append(n)
            if n.get("children"):
                walk(n["children"])

    walk(data.get("blockdevices", []))
    return result






# Builds a reliable physical-disk -> RAID-member map from arrays that are actually assembled.
def get_raid_membership_map():

    """
    Construit une carte fiable des disques physiques -> membres mdadm.

    Exemple :
      /dev/sda -> [
        {
          array: /dev/md10,
          member: /dev/sda1,
          state: active sync set-A,
          slot: 0
        }
      ]

    Cette méthode ne dépend PAS du champ FSTYPE=linux_raid_member.
    Elle interroge les arrays mdadm réellement assemblés.
    """
    mapping = {}

    for array in get_md_arrays():
        array_path = array.get("path", "")
        if not array_path:
            continue

        members, _detail = parse_mdadm_members(array_path)

        for m in members:
            member = clean_device_path(m.get("device", ""))
            if not member:
                continue

            physical = member

            
            rc, parent = run(["lsblk", "-ndo", "PKNAME", member], timeout=8)
            parent = parent.strip().splitlines()[0].strip() if rc == 0 and parent.strip() else ""

            if parent:
                physical = parent if parent.startswith("/dev/") else f"/dev/{parent}"

            physical = clean_device_path(physical)
            if not physical:
                continue

            mapping.setdefault(physical, []).append({
                "array": array_path,
                "member": member,
                "state": m.get("state", "unknown"),
                "slot": m.get("slot", "?"),
                "problem": bool(m.get("problem")),
                "warning": bool(m.get("warning")),
            })

    return mapping



# Extracts a real /dev/... path from display text that may contain extra information.
def clean_device_path(value):




    value = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    m = re.search(r"(/dev/[A-Za-z0-9._+\-]+)", value)
    return m.group(1) if m else ""



# =============================================================================
# MODULE 4 — SMART AND DISK HEALTH
# =============================================================================


# Resolves the physical disk behind a RAID member before calling smartctl.
def resolve_smart_device(member_path):




    member = clean_device_path(member_path)
    if not member:
        return "", "Chemin de périphérique invalide."

    if not Path(member).exists():
        return "", f"Le membre RAID {member} n'existe pas."

    
    rc, out = run(["lsblk", "-ndo", "PKNAME", member], timeout=8)
    parent = out.strip().splitlines()[0].strip() if rc == 0 and out.strip() else ""

    if parent:
        physical = clean_device_path(parent if parent.startswith("/dev/") else f"/dev/{parent}")
    else:
        
        rc2, typ = run(["lsblk", "-ndo", "TYPE", member], timeout=8)
        physical = member if rc2 == 0 and typ.strip() == "disk" else ""

    if not physical:
        return "", f"Impossible de déterminer le disque physique de {member}."

    if not Path(physical).exists():
        return "", f"Le disque physique {physical} n'existe pas."

    return physical, ""





# Determines whether the device is NVMe, SSD, or HDD using its name and lsblk.
def detect_disk_kind(device_path):




    device = clean_device_path(device_path)
    if not device:
        return "INCONNU"

    if "/dev/nvme" in device.lower():
        return "NVMe"

    rc, rota = run(["lsblk", "-ndo", "ROTA", device], timeout=8)
    if rc == 0:
        rota = rota.strip()
        if rota == "0":
            return "SSD"
        if rota == "1":
            return "HDD"

    return "INCONNU"



# Computes an HDD risk index from age and SMART counters; it is not remaining lifetime.
def hdd_risk_index(power_hours, reallocated=None, pending=None,
                   uncorrectable=None, health="INCONNU"):













    score = 0.0

    
    
    if isinstance(power_hours, int) and power_hours >= 0:
        years = power_hours / 8760.0

        if years < 3:
            age_score = years * 2.0                 # 0 -> 6
        elif years < 5:
            age_score = 6.0 + (years - 3.0) * 7.0 # 6 -> 20
        elif years < 7:
            age_score = 20.0 + (years - 5.0) * 10.0 # 20 -> 40
        elif years < 9:
            age_score = 40.0 + (years - 7.0) * 12.5 # 40 -> 65
        else:
            age_score = 65.0 + (years - 9.0) * 5.0  # progression lente
        score += min(age_score, 80.0)

    
    # Small internal helper: checks whether a value is a strictly positive integer.
    def positive_int(v):
        return isinstance(v, int) and v > 0

    
    if positive_int(reallocated):
        score += min(22.0, 7.0 + 5.0 * math.log10(reallocated + 1))

    if positive_int(pending):
        score += min(35.0, 22.0 + 6.0 * math.log10(pending + 1))

    if positive_int(uncorrectable):
        score += min(40.0, 28.0 + 6.0 * math.log10(uncorrectable + 1))

    h = (health or "").upper()
    if "ÉCHEC" in h or "FAIL" in h:
        return 100.0
    if "ATTENTION" in h or "WARN" in h:
        score += 20.0

    return max(0.0, min(100.0, score))





# Returns the official TBW endurance rating matching a Samsung 870 EVO capacity.
def samsung_870_evo_tbw_rating(model, size_bytes):








    model_u = (model or "").upper()
    if "SAMSUNG" not in model_u or "870 EVO" not in model_u:
        return None

    try:
        gb = int(round(int(size_bytes) / 1_000_000_000))
    except Exception:
        return None

    ratings = {
        250: 150,
        500: 300,
        1000: 600,
        2000: 1200,
        4000: 2400,
    }

    
    nearest = min(ratings.keys(), key=lambda x: abs(x - gb))
    if abs(nearest - gb) <= max(20, nearest * 0.08):
        return ratings[nearest]
    return None



# Converts a SMART Total_LBAs_Written counter into decimal terabytes written.
def total_lbas_written_to_tb(raw_value, sector_size=512):




    try:
        raw = int(raw_value)
        if raw < 0:
            return None
        return (raw * sector_size) / 1_000_000_000_000
    except Exception:
        return None



# Centralizes SATA/NVMe SMART analysis and returns health, errors, temperature, hours, and wear/risk.
def smart_usage_metrics(device_path):



    result = {
        "reallocated": None,
        "pending": None,
        "uncorrectable": None,
        "media_errors": None,
        "bad_total": None,
        "power_hours": None,
        "power_days": None,
        "health": "INCONNU",
         "temperature": None,
        "temperature_min": None,
        "temperature_max": None,
        "percentage_used": None,
        "power_cycle_count": None,
        "start_stop_count": None,
        "load_cycle_count": None,
        "spin_retry_count": None,
        "reported_uncorrectable": None,
        "command_timeout": None,
        "udma_crc_errors": None,
        "total_lbas_written": None,
        "total_lbas_read": None,
        "wear_percent": None,
        "wear_source": "",
        "index_kind": "wear",
        "disk_kind": "",
        "tb_written": None,
        "tbw_rating": None,
        "tbw_used_percent": None,
        "tbw_remaining_percent": None,
        "available": False,
    }

    device = clean_device_path(device_path)
    if not device or not Path(device).exists() or not shutil.which("smartctl"):
        return result

    result["disk_kind"] = detect_disk_kind(device)

    rc_lsblk, lsblk_out = run(
        ["lsblk", "-dnbo", "MODEL,SIZE", device],
        timeout=8
    )
    model = ""
    size_bytes = None
    if rc_lsblk == 0 and lsblk_out.strip():
        line = lsblk_out.strip().splitlines()[0].strip()
        m = re.match(r"^(.*\S)\s+(\d+)$", line)
        if m:
            model = m.group(1).strip()
            try:
                size_bytes = int(m.group(2))
            except Exception:
                size_bytes = None

    rc, out = run(["smartctl", "-a", device], timeout=25)
    if not out or out == "TIMEOUT":
        return result

    low_out = out.lower()
    is_nvme = (
        "/dev/nvme" in device.lower()
        or "nvme version" in low_out
        or "smart/health information (nvme log" in low_out
    )

    if is_nvme:
        critical_warning = None
        m = re.search(r"Critical Warning:\s*(0x[0-9a-fA-F]+|\d+)", out, re.I)
        if m:
            try:
                critical_warning = int(m.group(1), 0)
            except Exception:
                pass

        if critical_warning == 0:
            result["health"] = "OK"
        elif critical_warning is not None:
            result["health"] = "ATTENTION"

        def nvme_int(label):
            m = re.search(rf"^{re.escape(label)}:\s*(.+)$", out, re.I | re.M)
            if not m:
                return None
            raw = m.group(1).replace(",", "").replace(" ", "")
            m2 = re.search(r"-?\d+", raw)
            if not m2:
                return None
            try:
                return int(m2.group(0))
            except ValueError:
                return None

        result["power_hours"] = nvme_int("Power On Hours")
        result["media_errors"] = nvme_int("Media and Data Integrity Errors")
        result["percentage_used"] = nvme_int("Percentage Used")
        result["power_cycle_count"] = nvme_int("Power Cycles")

        
        
        
        # NVMe commonly exposes "Data Units Written". Per NVMe, one unit is
        #      1000 × 512-byte blocks = 512,000 bytes, so written TB can be shown
        #      even when the manufacturer's TBW rating is unknown.
        data_units_written = nvme_int("Data Units Written")
        if isinstance(data_units_written, int):
            result["tb_written"] = (
                data_units_written * 512_000
            ) / 1_000_000_000_000
        if isinstance(result["percentage_used"], int):
            result["wear_percent"] = max(0.0, min(100.0, float(result["percentage_used"])))
            result["wear_source"] = "SMART NVMe Percentage Used"
            result["index_kind"] = "wear"

        m = re.search(r"^Temperature:\s*([+-]?\d+)", out, re.I | re.M)
        if m:
            try:
                result["temperature"] = int(m.group(1))
            except ValueError:
                pass

        if isinstance(result["media_errors"], int):
            result["bad_total"] = result["media_errors"]

        if isinstance(result["power_hours"], int):
            result["power_days"] = result["power_hours"] / 24.0

        if isinstance(result["media_errors"], int) and result["media_errors"] > 0:
            if result["health"] == "OK":
                result["health"] = "ATTENTION"


        result["available"] = True
        return result

    # ATA / SATA
    if "smart overall-health self-assessment test result: passed" in low_out:
        result["health"] = "OK"
    elif "smart health status: ok" in low_out:
        result["health"] = "OK"
    elif "passed" in low_out and "smart" in low_out:
        result["health"] = "OK"
    elif "failed" in low_out or "failing_now" in low_out:
        result["health"] = "ÉCHEC"

    values = {}
    for line in out.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        parts = stripped.split()
        if len(parts) >= 10 and parts[0].isdigit():
            name = parts[1]
            raw = " ".join(parts[9:])
            m = re.search(r"-?\d+", raw)
            if m:
                try:
                    values[name] = int(m.group(0))
                except ValueError:
                    pass

    
    # Internal helper returning the first available SMART attribute among several possible names.
    def first_value(*names):
        for name in names:
            if name in values:
                return values[name]
        return None

    result["reallocated"] = first_value("Reallocated_Sector_Ct", "Reallocated_Event_Count")
    result["pending"] = first_value("Current_Pending_Sector", "Current_Pending_Sector_Ct")
    result["uncorrectable"] = first_value("Offline_Uncorrectable", "Reported_Uncorrect")
    result["power_hours"] = first_value("Power_On_Hours", "Power_On_Hours_and_Msec")
    result["temperature"] = first_value("Temperature_Celsius", "Airflow_Temperature_Cel")
    result["power_cycle_count"] = first_value("Power_Cycle_Count")
    result["start_stop_count"] = first_value("Start_Stop_Count")
    result["load_cycle_count"] = first_value("Load_Cycle_Count", "Load_Unload_Cycle_Count")
    result["spin_retry_count"] = first_value("Spin_Retry_Count")
    result["reported_uncorrectable"] = first_value("Reported_Uncorrect", "Reported_Uncorrectable")
    result["command_timeout"] = first_value("Command_Timeout")
    result["udma_crc_errors"] = first_value("UDMA_CRC_Error_Count")
    result["total_lbas_written"] = first_value("Total_LBAs_Written", "Total_LBA_Written")
    result["total_lbas_read"] = first_value("Total_LBAs_Read", "Total_LBA_Read")

    
    tm = re.search(r"(?:Temperature_Celsius|Airflow_Temperature_Cel).*?\b(\d+)\s+\(Min/Max\s+(\d+)/(\d+)\)", out, re.I)
    if tm:
        result["temperature_min"] = int(tm.group(2))
        result["temperature_max"] = int(tm.group(3))

    
    if isinstance(result["total_lbas_written"], int):
        result["tb_written"] = total_lbas_written_to_tb(result["total_lbas_written"])

    
    if result.get("disk_kind") == "SSD":
        lbas_written = first_value(
            "Total_LBAs_Written",
            "Total_LBA_Written",
        )
        host_writes_32mib = first_value("Host_Writes_32MiB")

        tb_written = None
        if isinstance(lbas_written, int):
            tb_written = total_lbas_written_to_tb(lbas_written)
        elif isinstance(host_writes_32mib, int):
            tb_written = (
                host_writes_32mib * 32 * 1024 * 1024
            ) / 1_000_000_000_000

        if tb_written is not None:
            result["tb_written"] = tb_written

        
        
        rating = samsung_870_evo_tbw_rating(model, size_bytes)

        if rating is not None and tb_written is not None:
            used = max(0.0, (tb_written / float(rating)) * 100.0)
            remaining = max(0.0, 100.0 - used)

            result["tb_written"] = tb_written
            result["tbw_rating"] = float(rating)
            result["tbw_used_percent"] = used
            result["tbw_remaining_percent"] = remaining
            result["wear_percent"] = min(100.0, used)
            result["wear_source"] = (
                f"Samsung 870 EVO : {tb_written:.2f} TB écrits / "
                f"{rating:.0f} TBW"
            )
            result["index_kind"] = "wear"

    
    if result.get("disk_kind") == "SSD":
        life_left = first_value(
            "SSD_Life_Left",
            "Percent_Lifetime_Remain",
            "Remaining_Lifetime_Perc"
        )
        percent_used = first_value(
            "Percentage_Used_Endurance_Indicator",
            "Media_Wearout_Indicator"
        )

        if result.get("wear_percent") is None and isinstance(life_left, int):
            
            result["wear_percent"] = max(0.0, min(100.0, 100.0 - float(life_left)))
            result["wear_source"] = "SMART SSD Life Left"
            result["index_kind"] = "wear"
        elif result.get("wear_percent") is None and isinstance(percent_used, int):
            
            result["wear_percent"] = max(0.0, min(100.0, float(percent_used)))
            result["wear_source"] = "SMART SSD Wear"
            result["index_kind"] = "wear"

    bad_parts = [
        v for v in (
            result["reallocated"],
            result["pending"],
            result["uncorrectable"],
        )
        if isinstance(v, int)
    ]
    if bad_parts:
        result["bad_total"] = sum(bad_parts)

    if isinstance(result["power_hours"], int):
        result["power_days"] = result["power_hours"] / 24.0

    
    if result.get("disk_kind") == "HDD":
        result["wear_percent"] = hdd_risk_index(
            result.get("power_hours"),
            result.get("reallocated"),
            result.get("pending"),
            result.get("uncorrectable"),
            result.get("health"),
        )
        result["wear_source"] = (
            "Indice de risque HDD : âge + SMART "
            "(réalloués/pending/non corrigibles)"
        )
        result["index_kind"] = "risk"


    result["available"] = bool(values)
    return result



# From a disk or partition, retrieves the physical disk, size, model, and serial number.
def physical_disk_info(path):





    result = {
        "member_path": path,
        "physical_path": path,
        "size": 0,
        "model": "",
        "serial": "",
    }

    if not path or not path.startswith("/dev/"):
        return result

    
    rc, out = run([
        "lsblk", "-J", "-b",
        "-o", "PATH,PKNAME,TYPE,SIZE,MODEL,SERIAL",
        path
    ], timeout=10)

    if rc == 0:
        import json
        try:
            data = json.loads(out)
            nodes = data.get("blockdevices", [])
            if nodes:
                n = nodes[0]
                result["size"] = int(n.get("size") or 0)
                result["model"] = (n.get("model") or "").strip()
                result["serial"] = (n.get("serial") or "").strip()

                pkname = (n.get("pkname") or "").strip()
                ntype = (n.get("type") or "").strip()

                if ntype == "part" and pkname:
                    parent = f"/dev/{pkname}"
                    result["physical_path"] = parent

                    rc2, out2 = run([
                        "lsblk", "-dn", "-b",
                        "-o", "SIZE,MODEL,SERIAL",
                        parent
                    ], timeout=10)
                    if rc2 == 0 and out2.strip():
                        
                        rcj, outj = run([
                            "lsblk", "-J", "-dn", "-b",
                            "-o", "PATH,SIZE,MODEL,SERIAL",
                            parent
                        ], timeout=10)
                        if rcj == 0:
                            try:
                                d2 = json.loads(outj).get("blockdevices", [])[0]
                                result["size"] = int(d2.get("size") or result["size"] or 0)
                                result["model"] = (d2.get("model") or result["model"] or "").strip()
                                result["serial"] = (d2.get("serial") or result["serial"] or "").strip()
                            except Exception:
                                pass
        except Exception:
            pass

    
    physical = result["physical_path"]
    if shutil.which("udevadm") and physical:
        rc, props = run(["udevadm", "info", "--query=property", "--name", physical], timeout=10)
        if rc == 0:
            p = {}
            for line in props.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    p[k.strip()] = v.strip()

            if not result["model"]:
                result["model"] = (
                    p.get("ID_MODEL_FROM_DATABASE")
                    or p.get("ID_MODEL")
                    or p.get("ID_SCSI_MODEL")
                    or ""
                ).replace("\\x20", " ").replace("_", " ").strip()

            if not result["serial"]:
                result["serial"] = (
                    p.get("ID_SERIAL_SHORT")
                    or p.get("ID_SCSI_SERIAL")
                    or p.get("ID_SERIAL")
                    or ""
                ).strip()

    # Dernier fallback : smartctl -i.
    if shutil.which("smartctl") and physical and (not result["model"] or not result["serial"]):
        rc, smart = run(["smartctl", "-i", physical], timeout=15)
        if rc in (0, 2):  
            for line in smart.splitlines():
                low = line.lower()
                if not result["model"] and (
                    low.startswith("device model:")
                    or low.startswith("model number:")
                    or low.startswith("product:")
                ):
                    result["model"] = line.split(":", 1)[1].strip()
                if not result["serial"] and low.startswith("serial number:"):
                    result["serial"] = line.split(":", 1)[1].strip()

    return result



# Returns lsblk metadata for one block device as a dictionary.
def block_device_info(path):

    rc, out = run([
        "lsblk", "-J", "-b",
        "-o", "NAME,PATH,TYPE,SIZE,MODEL,SERIAL,FSTYPE,LABEL,UUID,MOUNTPOINTS",
        path
    ], timeout=10)
    if rc != 0:
        return {}
    import json
    try:
        data = json.loads(out)
        nodes = data.get("blockdevices", [])
        if not nodes:
            return {}
        n = nodes[0]
        return {
            "path": n.get("path") or path,
            "type": n.get("type") or "",
            "size": int(n.get("size") or 0),
            "model": (n.get("model") or "").strip(),
            "serial": (n.get("serial") or "").strip(),
            "fstype": n.get("fstype") or "",
            "label": n.get("label") or "",
            "uuid": n.get("uuid") or "",
            "mountpoints": n.get("mountpoints") or [],
        }
    except Exception:
        return {}



# Parses 'mdadm --detail' output to obtain slot, state, and device for each member.
def parse_mdadm_members(array_path):





    rc, detail = run(["mdadm", "--detail", array_path], timeout=15)
    if rc != 0:
        return [], detail

    members = []
    in_table = False

    for raw in detail.splitlines():
        line = raw.strip()
        if not line:
            continue

        if ("RaidDevice" in line and "State" in line) or (
            line.startswith("Number") and "State" in line
        ):
            in_table = True
            continue

        if not in_table:
            continue

        
        # 0  8  17  0  active sync set-A  /dev/sdb1
        # -  0   0  1  removed
        parts = line.split()
        if len(parts) < 5:
            continue

        
        try:
            slot = parts[3]
        except Exception:
            slot = "?"

        dev = ""
        dev_index = None
        for i, token in enumerate(parts):
            if token.startswith("/dev/"):
                dev = token
                dev_index = i
                break

        if dev_index is not None:
            state_tokens = parts[4:dev_index]
        else:
            state_tokens = parts[4:]

        state = " ".join(state_tokens).strip() or "unknown"
        low = state.lower()

        problem_words = (
            "faulty", "failed", "removed", "missing",
            "blocked", "write-mostly faulty"
        )
        warning_words = (
            "spare", "rebuild", "recover", "resync",
            "replacement", "reshape"
        )

        problem = any(w in low for w in problem_words)
        warning = (not problem) and any(w in low for w in warning_words)

        members.append({
            "device": dev,
            "slot": slot,
            "state": state,
            "problem": problem,
            "warning": warning,
        })

    
    if not members:
        mdname = Path(array_path).name
        slaves = Path(f"/sys/block/{mdname}/slaves")
        if slaves.exists():
            for slave in sorted(slaves.iterdir()):
                members.append({
                    "device": f"/dev/{slave.name}",
                    "slot": "?",
                    "state": "active",
                    "problem": False,
                    "warning": False,
                })

    return members, detail



# Lists devices that can be offered as candidates when replacing a RAID member.
def get_candidate_replacement_devices(exclude=None):

    exclude = set(exclude or [])
    devices = get_block_devices()
    candidates = []
    for d in devices:
        if d.get("type") not in ("disk", "part"):
            continue
        path = d.get("path") or ""
        if not path or path in exclude:
            continue

        mounts = d.get("mountpoints") or []
        mounted = any(bool(m) for m in mounts) if isinstance(mounts, list) else bool(mounts)
        fstype = d.get("fstype") or ""
        model = (d.get("model") or "").strip()
        size = int(d.get("size") or 0)

        candidates.append({
            "path": path,
            "type": d.get("type") or "",
            "size": size,
            "model": model,
            "fstype": fstype,
            "mounted": mounted,
        })
    return candidates



# Collects filesystem, UUID, mount, and used/free space information for an array.
def get_array_mount_info(array_path):




    info = {
        "fstype": "",
        "label": "",
        "uuid": "",
        "mountpoints": [],
        "source": array_path,
        "size": "",
        "used": "",
        "avail": "",
        "use_percent": "",
    }

    rc, out = run([
        "lsblk", "-J", "-o",
        "PATH,FSTYPE,LABEL,UUID,MOUNTPOINTS",
        array_path
    ], timeout=10)

    if rc == 0:
        import json
        try:
            data = json.loads(out)
            nodes = data.get("blockdevices", [])
            if nodes:
                n = nodes[0]
                info["fstype"] = n.get("fstype") or ""
                info["label"] = n.get("label") or ""
                info["uuid"] = n.get("uuid") or ""
                mounts = n.get("mountpoints") or []
                if isinstance(mounts, list):
                    info["mountpoints"] = [m for m in mounts if m]
                elif mounts:
                    info["mountpoints"] = [str(mounts)]
        except Exception:
            pass

    
    if not info["mountpoints"]:
        rc, out = run([
            "lsblk", "-J", "-o",
            "PATH,FSTYPE,LABEL,UUID,MOUNTPOINTS",
            array_path
        ], timeout=10)
        if rc == 0:
            import json
            try:
                data = json.loads(out)

                
                # Recursively walks the lsblk JSON tree so no child partition/device is missed.
                def walk(nodes):
                    for n in nodes:
                        mounts = n.get("mountpoints") or []
                        if isinstance(mounts, list):
                            valid = [m for m in mounts if m]
                        else:
                            valid = [str(mounts)] if mounts else []
                        if valid:
                            info["source"] = n.get("path") or array_path
                            info["fstype"] = n.get("fstype") or info["fstype"]
                            info["label"] = n.get("label") or info["label"]
                            info["uuid"] = n.get("uuid") or info["uuid"]
                            info["mountpoints"] = valid
                            return True
                        if n.get("children") and walk(n["children"]):
                            return True
                    return False

                walk(data.get("blockdevices", []))
            except Exception:
                pass

    
    if info["mountpoints"]:
        mountpoint = info["mountpoints"][0]
        rc, out = run([
            "df", "-h", "--output=source,size,used,avail,pcent,target",
            mountpoint
        ], timeout=10)
        if rc == 0:
            lines = [l for l in out.splitlines() if l.strip()]
            if len(lines) >= 2:
                parts = lines[-1].split()
                if len(parts) >= 6:
                    info["source"] = parts[0]
                    info["size"] = parts[1]
                    info["used"] = parts[2]
                    info["avail"] = parts[3]
                    info["use_percent"] = parts[4]

    return info




# =============================================================================
# MODULE 5 — FSTAB / RAID / SUPERBLOCK SAFETY


# IMPORTANT SAFETY: functions in this module are the main barrier
# against accidentally erasing a RAID member or an fstab-referenced disk.
# =============================================================================


# Resolves an fstab source (/dev, UUID, LABEL...) into real /dev device path(s).
def resolve_fstab_source(source):

    source = (source or "").strip()
    if not source:
        return []

    lower = source.lower()
    if (
        source.startswith("//")
        or (":" in source and not source.startswith("/dev/"))
        or lower in ("none", "tmpfs", "proc", "sysfs", "devpts")
    ):
        return []

    if source.startswith("/dev/"):
        try:
            return [str(Path(source).resolve())]
        except Exception:
            return [source]

    for prefix in ("UUID=", "PARTUUID=", "LABEL=", "PARTLABEL="):
        if source.startswith(prefix):
            rc, out = run(["blkid", "-t", source, "-o", "device"], timeout=5)
            if rc != 0:
                return []
            result = []
            for line in out.splitlines():
                dev = clean_device_path(line.strip())
                if not dev:
                    continue
                try:
                    dev = str(Path(dev).resolve())
                except Exception:
                    pass
                result.append(dev)
            return result

    return []



# Reads active /etc/fstab lines and builds a list used by safety checks.
def get_fstab_entries():




    path = Path("/etc/fstab")
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []

    entries = []
    for line_no, raw in enumerate(lines, 1):
        stripped = raw.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if "#" in stripped:
            stripped = stripped.split("#", 1)[0].strip()

        if not stripped:
            continue

        parts = re.split(r"\s+", stripped)
        if len(parts) < 2:
            continue

        source = parts[0]
        target = parts[1]
        fstype = parts[2] if len(parts) >= 3 else ""
        options = parts[3] if len(parts) >= 4 else ""

        resolved = resolve_fstab_source(source)
        for dev in resolved:
            entries.append({
                "source": source,
                "device": dev,
                "target": target,
                "fstype": fstype,
                "options": options,
                "line": line_no,
            })

    return entries



# Returns a disk and all its children so its partitions are protected as well.
def device_family_paths(device_path):




    dev = clean_device_path(device_path)
    if not dev:
        return set()

    try:
        dev = str(Path(dev).resolve())
    except Exception:
        pass

    paths = {dev}
    rc, out = run(["lsblk", "-nrpo", "PATH", dev], timeout=5)
    if rc == 0:
        for line in out.splitlines():
            p = clean_device_path(line.strip())
            if not p:
                continue
            try:
                p = str(Path(p).resolve())
            except Exception:
                pass
            paths.add(p)

    return paths



# Checks whether the disk or one of its partitions is referenced by fstab.
def fstab_protection_entries(device_path, cached_entries=None):

    family = device_family_paths(device_path)
    if not family:
        return []

    entries = cached_entries if cached_entries is not None else get_fstab_entries()
    result = []

    for entry in entries:
        dev = entry.get("device", "")
        try:
            dev = str(Path(dev).resolve())
        except Exception:
            pass
        if dev in family:
            result.append(entry)

    return result



# Builds the message explaining why a destructive operation is blocked by fstab.
def protected_fstab_message(device_path):
    entries = fstab_protection_entries(device_path)
    if not entries:
        return ""

    lines = []
    for e in entries:
        lines.append(
            f"{e.get('source', '?')} → {e.get('target', '?')} "
            f"(résolu: {e.get('device', '?')}, ligne {e.get('line', '?')})"
        )

    return (
        "PROTECTION FSTAB ACTIVE\n\n"
        "Le périphérique demandé, ou une de ses partitions, est référencé "
        "dans une ligne ACTIVE de /etc/fstab :\n\n"
        + "\n".join(lines)
        + "\n\nL'opération destructive est bloquée."
    )



# Checks whether a device already belongs to an active mdadm array.
def raid_protection_memberships(device_path):



    dev = clean_device_path(device_path)
    if not dev:
        return []

    memberships = get_raid_membership_map()
    found = []

    if dev in memberships:
        found.extend(memberships.get(dev, []))

    for physical, entries in memberships.items():
        for entry in entries:
            member = clean_device_path(entry.get("member", ""))
            if member == dev:
                found.append(entry)

    rc, parent = run(["lsblk", "-ndo", "PKNAME", dev], timeout=5)
    if rc == 0 and parent.strip():
        physical = "/dev/" + parent.strip().splitlines()[0].strip()
        found.extend(memberships.get(physical, []))

    unique = []
    seen = set()
    for e in found:
        key = (e.get("array", ""), e.get("member", ""))
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique



# Builds the blocking message when a device is already a RAID member.
def protected_raid_message(device_path):
    entries = raid_protection_memberships(device_path)
    if not entries:
        return ""

    lines = []
    for e in entries:
        arr = e.get("array") or "RAID inconnu"
        member = e.get("member") or device_path
        state = e.get("state") or ""
        lines.append(
            f"{member} → {arr}" + (f" ({state})" if state else "")
        )

    return (
        "PROTECTION RAID ACTIVE\n\n"
        "Le périphérique demandé appartient déjà à un RAID mdadm détecté :\n\n"
        + "\n".join(lines)
        + "\n\nL'opération destructive est bloquée."
    )



# Examines mdadm metadata present on a device without writing anything.
def mdadm_examine_superblock(device_path):

    dev = clean_device_path(device_path)
    if not dev:
        return False, ""

    rc, out = run(["mdadm", "--examine", dev], timeout=20)
    low = (out or "").lower()
    signatures = (
        "magic :",
        "version :",
        "array uuid",
        "raid level",
        "raid devices",
        "device role",
        "array state",
    )
    found = any(sig in low for sig in signatures)
    return found, out or ""



# Returns the raw disk and partitions that may contain an old superblock.
def candidate_member_paths_for_cleanup(disk_path):

    dev = clean_device_path(disk_path)
    if not dev:
        return []

    paths = []
    rc, out = run(["lsblk", "-nrpo", "PATH,TYPE", dev], timeout=10)
    if rc == 0:
        for line in out.splitlines():
            parts = line.split()
            if not parts:
                continue
            p = clean_device_path(parts[0])
            typ = parts[1] if len(parts) > 1 else ""
            if p and typ in ("disk", "part"):
                paths.append(p)

    if dev not in paths:
        paths.insert(0, dev)

    result = []
    seen = set()
    for p in paths:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result



# Finds only old superblocks that can be cleared without touching protected RAID/FSTAB devices.
def safe_orphan_superblocks(disk_paths):



    found = []
    protected = []

    for disk in disk_paths:
        for dev in candidate_member_paths_for_cleanup(disk):
            raid_msg = protected_raid_message(dev)
            fstab_msg = protected_fstab_message(dev)

            if raid_msg or fstab_msg:
                protected.append((dev, raid_msg or fstab_msg))
                continue

            has_sb, examine = mdadm_examine_superblock(dev)
            if has_sb:
                found.append({
                    "device": dev,
                    "examine": examine,
                })

    unique = []
    seen = set()
    for item in found:
        if item["device"] not in seen:
            seen.add(item["device"])
            unique.append(item)

    return unique, protected





# =============================================================================
# MODULE 6 — GUI INFRASTRUCTURE
# =============================================================================


# Installs Tkinter hooks that automatically translate many texts when widgets are created/updated.
def install_tk_translation_hooks():
    if getattr(tk, "_mdadm_i18n_installed", False):
        return
    tk._mdadm_i18n_installed = True

    
    original_stringvar_init = tk.StringVar.__init__
    
    # Intercepts StringVar creation to translate its initial value.
    def translated_stringvar_init(self, *args, **kwargs):
        if "value" in kwargs and isinstance(kwargs["value"], str):
            kwargs["value"] = ui_text(kwargs["value"])
        return original_stringvar_init(self, *args, **kwargs)
    tk.StringVar.__init__ = translated_stringvar_init

    original_stringvar_set = tk.StringVar.set
    
    # Intercepts StringVar.set() to translate dynamic display values.
    def translated_stringvar_set(self, value):
        return original_stringvar_set(self, ui_text(value) if isinstance(value, str) else value)
    tk.StringVar.set = translated_stringvar_set

    classes = [
        tk.Label, tk.Button, tk.Checkbutton, tk.Radiobutton, tk.LabelFrame,
        ttk.Label, ttk.Button, ttk.Checkbutton, ttk.Radiobutton, ttk.LabelFrame
    ]
    for cls in classes:
        original_init = cls.__init__
        def make_init(orig):
            def translated_init(self, *args, **kwargs):
                if "text" in kwargs:
                    kwargs["text"] = ui_text(kwargs["text"])
                return orig(self, *args, **kwargs)
            return translated_init
        cls.__init__ = make_init(original_init)

        original_configure = cls.configure
        def make_configure(orig):
            def translated_configure(self, cnf=None, **kwargs):
                if isinstance(cnf, dict):
                    cnf = dict(cnf)
                    if "text" in cnf:
                        cnf["text"] = ui_text(cnf["text"])
                if "text" in kwargs:
                    kwargs["text"] = ui_text(kwargs["text"])
                if cnf is None:
                    return orig(self, **kwargs)
                return orig(self, cnf, **kwargs)
            return translated_configure
        cls.configure = make_configure(original_configure)
        cls.config = cls.configure

    for name in ("showinfo", "showwarning", "showerror", "askyesno",
                 "askokcancel", "askretrycancel"):
        if hasattr(messagebox, name):
            original = getattr(messagebox, name)
            def make_msg(fn):
                def translated_msg(title, message, *args, **kwargs):
                    return fn(ui_text(title), ui_text(message), *args, **kwargs)
                return translated_msg
            setattr(messagebox, name, make_msg(original))

    original_heading = ttk.Treeview.heading
    
    # Intercepts ttk.Treeview column headings so they are translated.
    def translated_heading(self, column, option=None, **kw):
        if "text" in kw:
            kw["text"] = ui_text(kw["text"])
        return original_heading(self, column, option, **kw)
    ttk.Treeview.heading = translated_heading

    original_add = ttk.Notebook.add
    
    # Intercepts ttk.Notebook tab insertion to translate tab titles.
    def translated_add(self, child, **kw):
        if "text" in kw:
            kw["text"] = ui_text(kw["text"])
        return original_add(self, child, **kw)
    ttk.Notebook.add = translated_add

install_tk_translation_hooks()



# Reusable confirmation window for sensitive/destructive actions.
class ConfirmDialog(tk.Toplevel):
    def __init__(self, parent, title, text, confirm_token=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.result = False
        self.confirm_token = confirm_token

        self.transient(parent)
        self.grab_set()

        ttk.Label(
            self,
            text=text,
            justify="left",
            wraplength=760
        ).pack(fill="x", padx=14, pady=(14, 8))

        if confirm_token:
            ttk.Label(
                self,
                text=f"Pour confirmer, tape exactement : {confirm_token}"
            ).pack(anchor="w", padx=14, pady=(6, 2))
            self.entry = ttk.Entry(self, width=40)
            self.entry.pack(fill="x", padx=14, pady=(0, 10))
        else:
            self.entry = None

        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=14, pady=(4, 14))
        ttk.Button(frame, text="Annuler", command=self.cancel).pack(side="right")
        ttk.Button(frame, text="Confirmer", command=self.ok).pack(side="right", padx=(0, 8))

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()
        self.geometry(f"+{parent.winfo_rootx()+100}+{parent.winfo_rooty()+100}")

    def ok(self):
        if self.confirm_token and self.entry.get().strip() != self.confirm_token:
            messagebox.showerror("Confirmation", "Le texte de confirmation ne correspond pas.", parent=self)
            return
        self.result = True
        self.destroy()

    def cancel(self):
        self.result = False
        self.destroy()




# =============================================================================
# MODULE 7 — RAID CREATION WIZARD
# =============================================================================


# Multi-step wizard that analyzes disks, validates choices, and prepares RAID creation.
class RaidCreationWizard(tk.Toplevel):


    LEVEL_INFO = {
        "raid0": {
            "title": "RAID 0 — Performance maximale",
            "min": 2,
            "faults": "Aucune tolérance de panne",
            "desc": (
                "Les données sont réparties sur tous les disques. Très rapide, "
                "mais la panne d'un seul disque détruit l'ensemble du RAID."
            ),
        },
        "raid1": {
            "title": "RAID 1 — Miroir",
            "min": 2,
            "faults": "Tolère au moins 1 panne avec 2 disques",
            "desc": (
                "Chaque donnée est copiée sur tous les membres. Très sécurisant, "
                "mais la capacité utile correspond au plus petit disque."
            ),
        },
        "raid5": {
            "title": "RAID 5 — Capacité + protection",
            "min": 3,
            "faults": "Tolère la panne de 1 disque",
            "desc": (
                "Parité distribuée. Bon compromis capacité/protection, mais une "
                "reconstruction peut être longue sur de gros HDD."
            ),
        },
        "raid6": {
            "title": "RAID 6 — Double parité",
            "min": 4,
            "faults": "Tolère la panne de 2 disques",
            "desc": (
                "Deux parités distribuées. Plus sécuritaire que RAID 5 pour les "
                "grands ensembles, au prix de deux disques de capacité."
            ),
        },
        "raid10": {
            "title": "RAID 10 — Performance + miroir",
            "min": 4,
            "faults": "Tolérance dépend des disques en panne et des paires",
            "desc": (
                "Combine mirroring et striping. Très bonnes performances et "
                "reconstruction généralement plus simple. Un nombre pair de "
                "disques est recommandé."
            ),
        },
    }


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title(f"{tr('raid_wizard')} — MDADM Manager v{APP_VERSION}")
        self.geometry("1320x820")
        self.minsize(1080, 680)
        self.transient(parent)
        self.grab_set()

        self.step = 0
        self.disk_records = {}
        self.selected_paths = []

        self.level_var = tk.StringVar(value="raid10")
        self.name_var = tk.StringVar(value="md20")
        self.chunk_var = tk.StringVar(value="512")
        self.meta_var = tk.StringVar(value="1.2")
        self.bitmap_var = tk.BooleanVar(value=True)
        self.allow_used_var = tk.BooleanVar(value=False)
        self.availability_var = tk.StringVar(value=ui_text("Analyse des disques disponibles…"))
        self.level_status_vars = {}

        outer = ttk.Frame(self, padding=10)
        outer.pack(fill="both", expand=True)
        outer.rowconfigure(2, weight=1)
        outer.columnconfigure(0, weight=1)

        self.header_var = tk.StringVar()
        ttk.Label(
            outer,
            textvariable=self.header_var,
            font=("TkFixedFont", 14, "bold")
        ).grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.progress_var = tk.StringVar()
        ttk.Label(
            outer,
            textvariable=self.progress_var,
            font=("TkFixedFont", 10)
        ).grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.body = ttk.Frame(outer)
        self.body.grid(row=2, column=0, sticky="nsew")
        self.body.rowconfigure(0, weight=1)
        self.body.columnconfigure(0, weight=1)

        self.pages = []
        self._build_page_level()
        self._build_page_disks()
        self._build_page_options()
        self._build_page_review()

        nav = ttk.Frame(outer)
        nav.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        nav.columnconfigure(2, weight=1)

        self.back_btn = ttk.Button(nav, text=tr("previous"), command=self.prev_step)
        self.back_btn.grid(row=0, column=0, padx=(0, 6))

        self.next_btn = ttk.Button(nav, text=tr("next"), command=self.next_step)
        self.next_btn.grid(row=0, column=1)

        ttk.Button(nav, text=tr("cancel"), command=self.destroy).grid(row=0, column=3, padx=(6, 0))

        self.show_step(0)

    
    # Creates a standard empty wizard page so every step shares the same structure.
    def _new_page(self):
        page = ttk.Frame(self.body)
        page.grid(row=0, column=0, sticky="nsew")
        page.rowconfigure(0, weight=1)
        page.columnconfigure(0, weight=1)
        self.pages.append(page)
        return page


    # -------------------------------------------------------------------------
    # STEP 1 — RAID LEVEL
    # -------------------------------------------------------------------------

    
    # Builds step 1: RAID level selection and availability based on usable disks.
    def _build_page_level(self):
        page = self._new_page()

        box = ttk.Frame(page, padding=14)
        box.grid(row=0, column=0, sticky="nsew")
        box.columnconfigure(1, weight=1)

        ttk.Label(
            box,
            text=ui_text("Choisis le type de RAID selon ton objectif"),
            font=("TkFixedFont", 13, "bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        ttk.Label(
            box,
            textvariable=self.availability_var,
            font=("TkFixedFont", 10, "bold"),
            wraplength=1050,
            justify="left"
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 12))

        row = 2
        self.level_buttons = {}
        for level in ("raid0", "raid1", "raid5", "raid6", "raid10"):
            info = self.LEVEL_INFO[level]
            rb = ttk.Radiobutton(
                box,
                text=ui_text(info["title"]),
                variable=self.level_var,
                value=level,
                command=self.update_level_details
            )
            rb.grid(row=row, column=0, sticky="nw", padx=(0, 18), pady=8)
            self.level_buttons[level] = rb

            ttk.Label(
                box,
                text=ui_text(f'{info["faults"]}\nMinimum : {info["min"]} disques'),
                font=("TkFixedFont", 9)
            ).grid(row=row, column=1, sticky="nw", pady=8)

            status_var = tk.StringVar(value=ui_text("Analyse…"))
            self.level_status_vars[level] = status_var
            ttk.Label(
                box,
                textvariable=status_var,
                font=("TkFixedFont", 9, "bold")
            ).grid(row=row, column=2, sticky="nw", padx=(18, 0), pady=8)
            row += 1

        self.level_details_var = tk.StringVar()
        details = ttk.LabelFrame(box, text=ui_text("Explication"))
        details.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(18, 0))
        details.columnconfigure(0, weight=1)
        ttk.Label(
            details,
            textvariable=self.level_details_var,
            wraplength=1000,
            justify="left",
            padding=12
        ).grid(row=0, column=0, sticky="ew")

        self.update_level_details()


    # -------------------------------------------------------------------------
    # STEP 2 — DISK SELECTION
    # -------------------------------------------------------------------------

    
    # Builds step 2: disk selection table plus SMART/safety information.
    def _build_page_disks(self):
        page = self._new_page()
        page.rowconfigure(1, weight=1)
        page.columnconfigure(0, weight=1)

        top = ttk.Frame(page)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        top.columnconfigure(1, weight=1)

        ttk.Label(
            top,
            text="Sélectionne les disques qui composeront le RAID",
            font=("TkFixedFont", 12, "bold")
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            top,
            text="Rafraîchir les informations",
            command=self.load_disks
        ).grid(row=0, column=2, sticky="e")

        cols = (
            "path", "size", "type", "model", "serial", "temp",
            "smart", "age", "wear", "raid", "fs", "mount", "status"
        )
        self.disk_tree = ttk.Treeview(
            page,
            columns=cols,
            show="headings",
            selectmode="extended"
        )

        heads = {
            "path": "Disque",
            "size": "Taille",
            "type": "Type",
            "model": "Modèle",
            "serial": "N° série",
            "temp": "Temp",
            "smart": "SMART",
            "age": "Heures / âge",
            "wear": "Usure / risque",
            "raid": "RAID actuel",
            "fs": "Partitions / FS",
            "mount": "Montage",
            "status": "Disponibilité",
        }
        widths = {
            "path": 90, "size": 85, "type": 70, "model": 180,
            "serial": 155, "temp": 58, "smart": 75, "age": 135, "wear": 130,
            "raid": 115, "fs": 230, "mount": 220, "status": 150
        }
        for c in cols:
            self.disk_tree.heading(c, text=heads[c])
            self.disk_tree.column(
                c,
                width=widths[c],
                minwidth=(48 if c == "temp" else 60),
                anchor=("center" if c == "temp" else "w"),
                stretch=(False if c == "temp" else True),
            )

        self.disk_tree.tag_configure("safe", foreground="#00ff66")
        self.disk_tree.tag_configure("warning", foreground="#ffb000")
        self.disk_tree.tag_configure("danger", foreground="#ff3b3b")
        self.disk_tree.grid(row=1, column=0, sticky="nsew")

        sy = ttk.Scrollbar(page, orient="vertical", command=self.disk_tree.yview)
        sy.grid(row=1, column=1, sticky="ns")
        sx = ttk.Scrollbar(page, orient="horizontal", command=self.disk_tree.xview)
        sx.grid(row=2, column=0, sticky="ew")
        self.disk_tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        controls = ttk.Frame(page)
        controls.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        controls.columnconfigure(2, weight=1)

        ttk.Checkbutton(
            controls,
            text="Mode avancé : autoriser FS/montages ordinaires (RAID et FSTAB restent BLOQUÉS)",
            variable=self.allow_used_var,
            command=self.on_allow_used_change
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            controls,
            text="SMART du disque",
            command=self.show_selected_smart
        ).grid(row=0, column=1, padx=10)

        self.disk_summary_var = tk.StringVar(value="Aucun disque sélectionné.")
        ttk.Label(
            controls,
            textvariable=self.disk_summary_var,
            font=("TkFixedFont", 10, "bold")
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 0))

        self.disk_tree.bind("<<TreeviewSelect>>", self.on_disk_selection)
        self.disk_tree.bind("<Double-1>", lambda _e: self.show_selected_smart())


    # -------------------------------------------------------------------------
    # STEP 3 — RAID OPTIONS
    # -------------------------------------------------------------------------

    
    # Builds step 3: name, metadata, bitmap, and other creation options.
    def _build_page_options(self):
        page = self._new_page()
        box = ttk.Frame(page, padding=16)
        box.grid(row=0, column=0, sticky="nsew")
        box.columnconfigure(1, weight=1)

        ttk.Label(
            box,
            text="Paramètres du nouvel ensemble RAID",
            font=("TkFixedFont", 13, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        ttk.Label(box, text="Nom :").grid(row=1, column=0, sticky="e", padx=8, pady=8)
        ttk.Entry(box, textvariable=self.name_var, width=22).grid(row=1, column=1, sticky="w", pady=8)
        ttk.Label(box, text="Exemple : md20 → /dev/md20").grid(row=2, column=1, sticky="w")

        ttk.Label(box, text="Chunk :").grid(row=3, column=0, sticky="e", padx=8, pady=8)
        ttk.Combobox(
            box,
            textvariable=self.chunk_var,
            values=["64", "128", "256", "512", "1024"],
            state="readonly",
            width=12
        ).grid(row=3, column=1, sticky="w", pady=8)

        ttk.Label(
            box,
            text="512 KiB convient bien à beaucoup de charges séquentielles. "
                 "Le chunk n'a pas le même impact selon le niveau RAID.",
            wraplength=820,
            justify="left"
        ).grid(row=4, column=1, sticky="w")

        ttk.Label(box, text="Métadonnées :").grid(row=5, column=0, sticky="e", padx=8, pady=8)
        ttk.Combobox(
            box,
            textvariable=self.meta_var,
            values=["1.2", "1.1", "1.0"],
            state="readonly",
            width=12
        ).grid(row=5, column=1, sticky="w", pady=8)

        ttk.Label(
            box,
            text="1.2 est le format moderne recommandé dans la plupart des cas.",
            wraplength=820
        ).grid(row=6, column=1, sticky="w")

        ttk.Checkbutton(
            box,
            text="Bitmap interne (recommandé sauf RAID 0)",
            variable=self.bitmap_var
        ).grid(row=7, column=1, sticky="w", pady=(14, 4))

        self.options_summary_var = tk.StringVar()
        lf = ttk.LabelFrame(box, text="Résumé calculé")
        lf.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        ttk.Label(
            lf,
            textvariable=self.options_summary_var,
            padding=12,
            justify="left",
            font=("TkFixedFont", 10)
        ).pack(anchor="w")


    # -------------------------------------------------------------------------
    # STEP 4 — FINAL REVIEW
    # -------------------------------------------------------------------------

    
    # Builds step 4: final summary and command that will be executed.
    def _build_page_review(self):
        page = self._new_page()
        page.rowconfigure(1, weight=1)
        page.columnconfigure(0, weight=1)

        ttk.Label(
            page,
            text="Vérification finale avant écriture",
            font=("TkFixedFont", 13, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.review_text = tk.Text(
            page,
            wrap="word",
            font=("TkFixedFont", 10),
            height=28
        )
        self.review_text.grid(row=1, column=0, sticky="nsew")

        sy = ttk.Scrollbar(page, orient="vertical", command=self.review_text.yview)
        sy.grid(row=1, column=1, sticky="ns")
        self.review_text.configure(yscrollcommand=sy.set)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Analyzes system disks and classifies them as free, protected, or in use.
    def analyze_free_disks(self):







        devices = get_block_devices()
        membership = get_raid_membership_map()
        fstab_entries_cache = get_fstab_entries()

        stats = {
            "total": 0,
            "raid": 0,
            "fstab": 0,
            "filesystem": 0,
            "mounted": 0,
            "smart_bad": 0,
            "free": 0,
        }

        for d in devices:
            if d.get("type") != "disk":
                continue

            path = clean_device_path(d.get("path", ""))
            if not path:
                continue

            stats["total"] += 1
            raid_locked = bool(membership.get(path, []))
            fstab_locked = bool(
                fstab_protection_entries(
                    path,
                    cached_entries=fstab_entries_cache
                )
            )

            fs_found = bool(d.get("fstype"))
            mount_found = False
            mounts = d.get("mountpoints") or []
            if isinstance(mounts, list):
                mount_found = any(bool(x) for x in mounts)
            else:
                mount_found = bool(mounts)

            for child in d.get("children") or []:
                if child.get("fstype"):
                    fs_found = True
                cm = child.get("mountpoints") or []
                if isinstance(cm, list):
                    if any(bool(x) for x in cm):
                        mount_found = True
                elif cm:
                    mount_found = True

            # IMPORTANT : aucune interrogation SMART ici.
            
            
            
            smart_bad = False

            if raid_locked:
                stats["raid"] += 1
            if fstab_locked:
                stats["fstab"] += 1
            if fs_found:
                stats["filesystem"] += 1
            if mount_found:
                stats["mounted"] += 1
            if smart_bad:
                stats["smart_bad"] += 1

            if not (raid_locked or fstab_locked or fs_found or mount_found or smart_bad):
                stats["free"] += 1

        return stats

    
    # Enables/disables RAID levels according to the number of truly available disks.
    def refresh_level_availability(self):
        try:
            stats = self.analyze_free_disks()
        except Exception as exc:
            self.availability_var.set(
                f"ERREUR D'ANALYSE : {type(exc).__name__}: {exc}"
            )
            for level in self.LEVEL_INFO:
                self.level_status_vars[level].set(ui_text("✖ Analyse impossible"))
                self.level_buttons[level].configure(state="disabled")
            self.level_details_var.set(
                "L'analyse a échoué. Le détail de l'erreur est affiché "
                "ci-dessus au lieu de laisser « Analyse… » indéfiniment."
            )
            return

        free = stats["free"]

        self.availability_var.set(
            f"Disques physiques : {stats['total']}   |   "
            f"RAID protégés : {stats['raid']}   |   "
            f"FSTAB protégés : {stats['fstab']}   |   "
            f"FS/montage occupés : {max(stats['filesystem'], stats['mounted'])}   |   "
            f"DISPONIBLES : {free}   |   "
            "SMART : analysé à l'étape suivante"
        )

        possible = []
        for level, info in self.LEVEL_INFO.items():
            missing = max(0, info["min"] - free)
            if missing:
                self.level_status_vars[level].set(
                    ui_text(f"✖ Impossible — manque {missing} disque" + ("s" if missing > 1 else ""))
                )
                self.level_buttons[level].configure(state="disabled")
            else:
                self.level_status_vars[level].set(
                    ui_text(f"✓ Possible — {free} disque(s) libre(s)")
                )
                self.level_buttons[level].configure(state="normal")
                possible.append(level)

        current = self.level_var.get()
        if current not in possible:
            preferred = next(
                (x for x in ("raid10", "raid6", "raid5", "raid1", "raid0")
                 if x in possible),
                ""
            )
            self.level_var.set(preferred)

        if not possible:
            self.level_details_var.set(ui_text(
                "Aucun niveau RAID proposé ne peut être créé avec les disques "
                "actuellement considérés libres. Libère ou ajoute des disques."
            ))
        else:
            self.update_level_details()

    
    # Updates the explanation for the selected RAID level.
    def update_level_details(self):
        level = self.level_var.get()
        if not level or level not in self.LEVEL_INFO:
            self.level_details_var.set(ui_text(
                "Pas assez de disques libres pour créer un RAID avec les "
                "niveaux proposés."
            ))
            return
        info = self.LEVEL_INFO[level]
        self.level_details_var.set(
            ui_text(f'{info["desc"]}\n\n'
            f'Tolérance : {info["faults"]}\n'
            f'Minimum : {info["min"]} disques')
        )

    
    # Handles the advanced option that also shows disks currently in use.
    def on_allow_used_change(self):
        self.on_disk_selection()

    def load_disks(self):
        previous = set(self.selected_paths)
        self.disk_tree.delete(*self.disk_tree.get_children())
        self.disk_records = {}

        devices = get_block_devices()
        membership = get_raid_membership_map()
        fstab_entries_cache = get_fstab_entries()

        for d in devices:
            if d.get("type") != "disk":
                continue

            path = clean_device_path(d.get("path", ""))
            if not path:
                continue

            try:
                size_bytes = int(d.get("size") or 0)
            except Exception:
                size_bytes = 0
            size_txt = self.parent.human_size(size_bytes)

            
            
            
            cached = self.parent.smart_cache.get(path)
            metrics = {}
            if cached:
                try:
                    cached_time, cached_metrics = cached
                    if time.time() - cached_time <= self.parent.smart_cache_ttl:
                        metrics = cached_metrics or {}
                except Exception:
                    metrics = {}

            health = metrics.get("health", "À analyser")
            kind = metrics.get("disk_kind") or detect_disk_kind(path)

            hours = metrics.get("power_hours")
            if isinstance(hours, int):
                years = hours / 8760.0
                age_txt = f"{hours:,} h / {years:.1f} a".replace(",", " ")
            else:
                age_txt = "—"

            idx = metrics.get("wear_percent")
            idx_kind = metrics.get("index_kind") or "wear"
            if isinstance(idx, (int, float)):
                wear_txt = (
                    f"Risque {idx:.1f}%"
                    if idx_kind == "risk"
                    else f"Usure {idx:.1f}%"
                )
            else:
                wear_txt = "—"

            raid_entries = membership.get(path, [])
            raid_txt = ", ".join(sorted({x.get("array", "") for x in raid_entries if x.get("array")})) or "—"

            fs_parts = []
            mount_parts = []
            parent_fs = d.get("fstype") or ""
            parent_mounts = d.get("mountpoints") or []
            if parent_fs:
                fs_parts.append(parent_fs)
            if isinstance(parent_mounts, list):
                mount_parts.extend([m for m in parent_mounts if m])
            elif parent_mounts:
                mount_parts.append(str(parent_mounts))

            for child in d.get("children") or []:
                cpath = child.get("path") or child.get("name") or ""
                cfs = child.get("fstype") or ""
                cmounts = child.get("mountpoints") or []
                if cfs:
                    fs_parts.append(f"{Path(cpath).name}:{cfs}")
                if isinstance(cmounts, list):
                    for mnt in cmounts:
                        if mnt:
                            mount_parts.append(f"{Path(cpath).name}:{mnt}")
                elif cmounts:
                    mount_parts.append(f"{Path(cpath).name}:{cmounts}")

            fs_txt = " | ".join(fs_parts) if fs_parts else "—"
            mount_txt = " | ".join(mount_parts) if mount_parts else "—"

            raid_protected = bool(raid_entries)
            fstab_entries = fstab_protection_entries(
                path,
                cached_entries=fstab_entries_cache
            )
            fstab_protected = bool(fstab_entries)

            used_reasons = []
            if raid_entries:
                used_reasons.append("RAID PROTÉGÉ")
            if fstab_entries:
                used_reasons.append("FSTAB PROTÉGÉ")
            if fs_parts:
                used_reasons.append("FS présent")
            if mount_parts:
                used_reasons.append("monté")
            if health == "ÉCHEC":
                used_reasons.append("SMART ÉCHEC")

            if raid_protected and fstab_protected:
                status = "PROTÉGÉ — RAID EXISTANT + FSTAB"
                tag = "danger"
                blocked = True
            elif raid_protected:
                status = "PROTÉGÉ — MEMBRE D'UN RAID EXISTANT"
                tag = "danger"
                blocked = True
            elif fstab_protected:
                targets = ", ".join(sorted({
                    e.get("target", "") for e in fstab_entries if e.get("target")
                }))
                status = "PROTÉGÉ — FSTAB" + (f" ({targets})" if targets else "")
                tag = "danger"
                blocked = True
            elif health == "ÉCHEC":
                status = "À NE PAS UTILISER"
                tag = "danger"
                blocked = True
            elif used_reasons:
                status = "UTILISÉ : " + ", ".join(used_reasons)
                tag = "warning"
                blocked = True
            else:
                status = "DISPONIBLE"
                tag = "safe"
                blocked = False

            rec = {
                "path": path,
                "size_bytes": size_bytes,
                "size_txt": size_txt,
                "kind": kind,
                "model": d.get("model") or "",
                "serial": d.get("serial") or "",
                "health": health,
                "age_txt": age_txt,
                "wear_txt": wear_txt,
                "raid_txt": raid_txt,
                "fs_txt": fs_txt,
                "mount_txt": mount_txt,
                "status": status,
                "blocked": blocked,
                "raid_protected": raid_protected,
                "fstab_protected": fstab_protected,
                "fstab_entries": fstab_entries,
            }
            self.disk_records[path] = rec

            item = self.disk_tree.insert(
                "",
                "end",
                iid=path,
                values=(
                    path, size_txt, kind,
                    rec["model"], rec["serial"],
                    (f"{metrics.get('temperature')} °C" if metrics.get("temperature") is not None else "—"),
                    health,
                    age_txt, wear_txt, raid_txt,
                    fs_txt, mount_txt, status
                ),
                tags=(tag,)
            )
            if path in previous:
                self.disk_tree.selection_add(item)

        self.on_disk_selection()

    
    # Opens SMART information for the disk selected in the wizard.
    def show_selected_smart(self):
        sel = self.disk_tree.selection()
        if len(sel) != 1:
            messagebox.showinfo(
                "SMART",
                "Sélectionne exactement un disque pour afficher son SMART.",
                parent=self
            )
            return
        self.parent.show_smart_for_path(sel[0])


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Returns only /dev paths for selected disks.
    def selected_disk_paths(self):
        return [p for p in self.disk_tree.selection() if p in self.disk_records]

    def on_disk_selection(self, _event=None):
        selected = self.selected_disk_paths()

        
        
        hard_locked = [
            p for p in selected
            if (
                self.disk_records.get(p, {}).get("raid_protected")
                or self.disk_records.get(p, {}).get("fstab_protected")
            )
        ]
        for p in hard_locked:
            self.disk_tree.selection_remove(p)

        if hard_locked:
            selected = self.selected_disk_paths()

        
        
        if not self.allow_used_var.get():
            invalid = [
                p for p in selected
                if self.disk_records.get(p, {}).get("blocked")
            ]
            for p in invalid:
                self.disk_tree.selection_remove(p)
            if invalid:
                selected = self.selected_disk_paths()

        self.selected_paths = selected
        self.update_disk_summary()

    
    # Estimates usable array capacity from RAID level and the smallest disk.
    def estimated_capacity_bytes(self):
        selected = self.selected_disk_paths()
        if not selected:
            return 0

        sizes = [
            self.disk_records[p]["size_bytes"]
            for p in selected
            if p in self.disk_records
        ]
        if not sizes:
            return 0

        n = len(sizes)
        smallest = min(sizes)
        level = self.level_var.get()

        if level == "raid0":
            return smallest * n
        if level == "raid1":
            return smallest
        if level == "raid5":
            return smallest * max(0, n - 1)
        if level == "raid6":
            return smallest * max(0, n - 2)
        if level == "raid10":
            return smallest * (n // 2)
        return 0

    
    # Updates the visual summary of selected disks.
    def update_disk_summary(self):
        selected = self.selected_disk_paths()
        level = self.level_var.get()
        info = self.LEVEL_INFO[level]
        capacity = self.parent.human_size(self.estimated_capacity_bytes())

        if not selected:
            self.disk_summary_var.set(
                f"{info['title']} — sélectionne au moins {info['min']} disques."
            )
            return

        size_values = [self.disk_records[p]["size_bytes"] for p in selected]
        smallest = min(size_values) if size_values else 0
        largest = max(size_values) if size_values else 0
        mismatch = largest > smallest * 1.05 if smallest else False
        suffix = (
            "  ⚠ Capacités différentes : l'espace au-delà du plus petit disque "
            "ne sera pas utilisé par ce calcul RAID."
            if mismatch else ""
        )

        self.disk_summary_var.set(
            f"{len(selected)} disque(s) sélectionné(s) — "
            f"capacité utile estimée : {capacity} — "
            f"{info['faults']}.{suffix}"
        )

    
    # Validates disk count, state, and safety before continuing.
    def validate_disks(self):
        selected = self.selected_disk_paths()
        level = self.level_var.get()
        info = self.LEVEL_INFO[level]

        if len(selected) < info["min"]:
            messagebox.showerror(
                "Assistant RAID",
                f"{level.upper()} nécessite au moins {info['min']} disques.",
                parent=self
            )
            return False

        if level == "raid10" and len(selected) % 2:
            if not messagebox.askyesno(
                "RAID 10 avec nombre impair",
                "Linux mdadm peut créer certains RAID10 avec un nombre impair de "
                "membres, mais un nombre pair est généralement plus simple.\n\n"
                "Continuer avec ce nombre de disques ?",
                parent=self
            ):
                return False

        raid_locked = [
            p for p in selected
            if self.disk_records.get(p, {}).get("raid_protected")
        ]
        fstab_locked = [
            p for p in selected
            if self.disk_records.get(p, {}).get("fstab_protected")
        ]

        if raid_locked or fstab_locked:
            details = []
            for p in raid_locked:
                details.append(
                    f"{p} — RAID : {self.disk_records[p].get('raid_txt', 'RAID')}"
                )
            for p in fstab_locked:
                targets = ", ".join(sorted({
                    e.get("target", "")
                    for e in self.disk_records[p].get("fstab_entries", [])
                    if e.get("target")
                }))
                details.append(f"{p} — FSTAB : {targets or 'entrée détectée'}")

            messagebox.showerror(
                "PROTECTION RAID / FSTAB",
                "Création impossible : un ou plusieurs disques sont protégés.\n\n"
                + "\n".join(details)
                + "\n\nLe mode avancé ne peut pas contourner cette protection.",
                parent=self
            )
            return False

        blocked = [
            p for p in selected
            if self.disk_records.get(p, {}).get("blocked")
        ]
        if blocked and not self.allow_used_var.get():
            messagebox.showerror(
                "Disques utilisés",
                "Certains disques sélectionnés contiennent déjà des données, "
                "sont montés ou appartiennent à un RAID.",
                parent=self
            )
            return False

        if blocked:
            details = "\n".join(
                f"{p} — {self.disk_records[p]['status']}"
                for p in blocked
            )
            if not messagebox.askyesno(
                "ATTENTION — disques déjà utilisés",
                "Le mode avancé permet actuellement des disques utilisés.\n\n"
                f"{details}\n\n"
                "La création du RAID peut rendre les données existantes "
                "inaccessibles. Continuer vers l'étape suivante ?",
                parent=self
            ):
                return False

        return True

    
    # Validates creation options before the final step.
    def validate_options(self):
        name = self.name_var.get().strip()
        if not re.fullmatch(r"md\d+", name):
            messagebox.showerror(
                "Nom du RAID",
                "Le nom doit être du type md20, md30, etc.",
                parent=self
            )
            return False

        arrays = {Path(a).name for a in get_md_arrays()}
        if name in arrays or Path(f"/dev/{name}").exists():
            messagebox.showerror(
                "Nom déjà utilisé",
                f"/dev/{name} existe déjà. Choisis un autre numéro.",
                parent=self
            )
            return False
        return True


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds the mdadm --create argument list without executing it yet.
    def build_cmd(self):
        selected = self.selected_disk_paths()
        level = self.level_var.get()
        name = self.name_var.get().strip()

        cmd = [
            "mdadm", "--create", f"/dev/{name}",
            "--verbose",
            "--level", level.replace("raid", ""),
            "--raid-devices", str(len(selected)),
            "--metadata", self.meta_var.get(),
            "--chunk", self.chunk_var.get(),
        ]
        if self.bitmap_var.get() and level != "raid0":
            cmd.append("--bitmap=internal")
        cmd.extend(selected)
        return cmd

    
    # Updates the summary text for selected options.
    def update_options_summary(self):
        level = self.level_var.get()
        selected = self.selected_disk_paths()
        info = self.LEVEL_INFO[level]
        capacity = self.parent.human_size(self.estimated_capacity_bytes())

        self.options_summary_var.set(
            f"Niveau : {level.upper()}\n"
            f"Disques : {len(selected)}\n"
            f"Capacité utile estimée : {capacity}\n"
            f"Tolérance : {info['faults']}\n"
            f"Nom : /dev/{self.name_var.get().strip() or '?'}\n"
            f"Chunk : {self.chunk_var.get()} KiB\n"
            f"Métadonnées : {self.meta_var.get()}\n"
            f"Bitmap interne : {'Oui' if self.bitmap_var.get() and level != 'raid0' else 'Non'}"
        )

    
    # Prepares the wizard's final review with disks, capacity, and command.
    def populate_review(self):
        level = self.level_var.get()
        info = self.LEVEL_INFO[level]
        selected = self.selected_disk_paths()
        capacity = self.parent.human_size(self.estimated_capacity_bytes())
        cmd = self.build_cmd()

        lines = [
            "=== NOUVEAU RAID ===",
            f"Nom                 : /dev/{self.name_var.get().strip()}",
            f"Niveau              : {level.upper()}",
            f"Nombre de disques   : {len(selected)}",
            f"Capacité estimée    : {capacity}",
            f"Tolérance           : {info['faults']}",
            f"Chunk               : {self.chunk_var.get()} KiB",
            f"Métadonnées         : {self.meta_var.get()}",
            f"Bitmap interne      : {'Oui' if self.bitmap_var.get() and level != 'raid0' else 'Non'}",
            "",
            "=== DISQUES ===",
        ]

        for p in selected:
            r = self.disk_records[p]
            lines.extend([
                f"{p}",
                f"  {r['size_txt']} | {r['kind']} | {r['model']}",
                f"  Série: {r['serial'] or '—'} | SMART: {r['health']} | {r['wear_txt']}",
                f"  État actuel: {r['status']}",
            ])

        lines.extend([
            "",
            "=== COMMANDE MDADM ===",
            shell_join(cmd),
            "",
            "IMPORTANT :",
            "La création écrit des métadonnées RAID sur les périphériques sélectionnés.",
            "Vérifie particulièrement les numéros de série avant de continuer.",
            "Avant la création, mdadm --examine recherchera les anciens superblocks.",
            "Un --zero-superblock ne sera proposé que pour une métadonnée orpheline.",
            "RAID actif et /etc/fstab restent protégés et bloquent l'effacement.",
            "L'assistant ne crée pas automatiquement de système de fichiers.",
        ])

        self.review_text.delete("1.0", "end")
        self.review_text.insert("1.0", "\n".join(lines))

    
    # Shows one wizard step and hides the others.
    def show_step(self, step):
        self.step = step
        titles = [
            "Étape 1 — Type de RAID",
            "Étape 2 — Choix des disques",
            "Étape 3 — Paramètres",
            "Étape 4 — Vérification et création",
        ]
        self.header_var.set(ui_text(titles[step]))
        self.progress_var.set(ui_text(f"Assistant RAID  •  Étape {step + 1} sur 4"))

        self.pages[step].tkraise()
        self.back_btn.configure(state="disabled" if step == 0 else "normal")

        if step == 0:
            self.refresh_level_availability()
        elif step == 1:
            self.load_disks()
        elif step == 2:
            self.update_options_summary()
        elif step == 3:
            self.populate_review()

        if step == 3:
            self.next_btn.configure(text=tr("create"), command=self.finish)
        else:
            self.next_btn.configure(text=tr("next"), command=self.next_step)

    
    # Validates the current step and advances only when everything is acceptable.
    def next_step(self):
        if self.step == 0:
            level = self.level_var.get()
            if not level or level not in self.LEVEL_INFO:
                messagebox.showerror(
                    "Pas assez de disques libres",
                    "Aucun niveau RAID ne peut être créé avec les disques "
                    "actuellement disponibles.",
                    parent=self
                )
                return

            stats = self.analyze_free_disks()
            required = self.LEVEL_INFO[level]["min"]
            if stats["free"] < required:
                messagebox.showerror(
                    "Pas assez de disques libres",
                    f"{level.upper()} demande au minimum {required} disques libres.\n\n"
                    f"Disques réellement disponibles : {stats['free']}\n"
                    f"Il manque : {required - stats['free']} disque(s).",
                    parent=self
                )
                return

            self.show_step(1)
            return
        if self.step == 1:
            if not self.validate_disks():
                return
            self.show_step(2)
            return
        if self.step == 2:
            if not self.validate_options():
                return
            self.show_step(3)

    
    # Returns to the previous step without modifying disks.
    def prev_step(self):
        if self.step > 0:
            self.show_step(self.step - 1)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Safely prepares selected disks immediately before creation.
    def prepare_selected_disks(self):




        disks = self.selected_disk_paths()
        orphaned, protected = safe_orphan_superblocks(disks)

        if protected:
            
            
            devices = "\n".join(sorted({p for p, _msg in protected}))
            messagebox.showerror(
                "PROTECTION RAID / FSTAB",
                "La préparation a détecté un périphérique maintenant protégé :\n\n"
                f"{devices}\n\n"
                "La création est annulée. Rafraîchis les disques avant de recommencer.",
                parent=self
            )
            return False

        if not orphaned:
            messagebox.showinfo(
                "Préparation des disques",
                "Aucun ancien superblock mdadm orphelin n'a été détecté.\n\n"
                "Aucun --zero-superblock n'est nécessaire.",
                parent=self
            )
            return True

        details = []
        for item in orphaned:
            dev = item["device"]
            examine = item["examine"]
            uuid_match = re.search(r"Array UUID\s*:\s*(\S+)", examine, re.I)
            level_match = re.search(r"Raid Level\s*:\s*(\S+)", examine, re.I)
            uuid_txt = uuid_match.group(1) if uuid_match else "inconnu"
            level_txt = level_match.group(1) if level_match else "inconnu"
            details.append(f"{dev} — ancien RAID {level_txt}, UUID {uuid_txt}")

        msg = (
            "Anciennes métadonnées mdadm détectées sur :\n\n"
            + "\n".join(details)
            + "\n\nCes périphériques ne sont actuellement ni membres d'un RAID "
              "détecté ni protégés par /etc/fstab.\n\n"
              "Veux-tu effacer UNIQUEMENT ces anciens superblocks avec "
              "mdadm --zero-superblock ?"
        )

        if not messagebox.askyesno(
            "Préparation — anciens superblocks RAID",
            msg,
            parent=self
        ):
            
            return True

        for item in orphaned:
            dev = item["device"]

            
            raid_guard = protected_raid_message(dev)
            fstab_guard = protected_fstab_message(dev)
            if raid_guard or fstab_guard:
                messagebox.showerror(
                    "PROTECTION — ÉTAT MODIFIÉ",
                    raid_guard or fstab_guard,
                    parent=self
                )
                return False

            rc, out = run(
                ["mdadm", "--zero-superblock", dev],
                timeout=60
            )
            if rc != 0:
                messagebox.showerror(
                    "Préparation incomplète",
                    f"Impossible d'effacer l'ancien superblock sur {dev}.\n\n"
                    f"{out}\n\nLa création RAID est annulée.",
                    parent=self
                )
                return False

        messagebox.showinfo(
            "Préparation terminée",
            "Les anciens superblocks mdadm sélectionnés ont été effacés.\n\n"
            "Les protections RAID actif et /etc/fstab ont été respectées.",
            parent=self
        )
        return True


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Final step: reconfirms, executes creation, and refreshes the application.
    def finish(self):
        if not self.validate_disks() or not self.validate_options():
            return

        cmd = self.build_cmd()
        name = self.name_var.get().strip()
        disks = self.selected_disk_paths()

        warning = (
            f"Création de /dev/{name}\n\n"
            f"Niveau : {self.level_var.get().upper()}\n"
            f"Disques :\n" + "\n".join(disks) +
            "\n\nCette opération écrit des métadonnées RAID sur ces disques.\n"
            "Vérifie une dernière fois les périphériques et numéros de série.\n\n"
            f"Commande :\n{shell_join(cmd)}"
        )

        dlg = ConfirmDialog(
            self,
            "CONFIRMATION FINALE — CRÉATION RAID",
            warning,
            confirm_token=name
        )
        self.wait_window(dlg)
        if not dlg.result:
            return

        
        
        
        if not self.prepare_selected_disks():
            return

        self.grab_release()
        self.destroy()
        self.parent.run_async(
            cmd,
            self.parent.manage_output,
            privileged=True,
            timeout=600
        )



# =============================================================================
# MODULE 8 — MAIN APPLICATION
# =============================================================================


# Main window: builds tabs, refreshes data, and coordinates all mdadm actions.
class MdadmManager(tk.Tk):

    # -------------------------------------------------------------------------
    # APPLICATION INITIALIZATION
    # -------------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.build_language_menu()
        self.geometry("1220x780")
        self.minsize(1000, 650)

        self.configure(bg="#020802")

        # -----------------------------------------------------------------
        
        # -----------------------------------------------------------------
        
        
        
        
        #
        
        
        #
        # Classic Tk widgets (Text, Listbox, Entry...) normally start with
        #      a white background. apply_matrix_widgets() recolored them later,
        #      which caused the two visible white rectangles during startup.
        #
        #      option_add() sets their defaults before creation, so they are
        #      black/green from their very first painted frame.
        self.option_add("*Listbox.background", "#010601")
        self.option_add("*Listbox.foreground", "#00ff66")
        self.option_add("*Listbox.selectBackground", "#145214")
        self.option_add("*Listbox.selectForeground", "#ffffff")
        self.option_add("*Listbox.highlightBackground", "#0b3d0b")
        self.option_add("*Listbox.highlightColor", "#00aa44")

        self.option_add("*Text.background", "#010601")
        self.option_add("*Text.foreground", "#00ff66")
        self.option_add("*Text.insertBackground", "#00ff66")
        self.option_add("*Text.selectBackground", "#145214")
        self.option_add("*Text.selectForeground", "#ffffff")
        self.option_add("*Text.highlightBackground", "#0b3d0b")
        self.option_add("*Text.highlightColor", "#00aa44")

        self.option_add("*Entry.background", "#010601")
        self.option_add("*Entry.foreground", "#00ff66")
        self.option_add("*Entry.insertBackground", "#00ff66")
        self.option_add("*Entry.selectBackground", "#145214")
        self.option_add("*Entry.selectForeground", "#ffffff")

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background="#061006", foreground="#00dd55", fieldbackground="#020802")
        style.configure("TFrame", background="#061006")
        style.configure("TLabel", background="#061006", foreground="#00dd55")
        style.configure("TButton", background="#0b1c0b", foreground="#00ff66", padding=7)
        style.map("TButton", background=[("active", "#123812")], foreground=[("active", "#ffffff")])
        style.configure("TNotebook", background="#020802", borderwidth=0)
        style.configure("TNotebook.Tab", background="#071407", foreground="#00cc55", padding=(12, 7))
        style.map("TNotebook.Tab", background=[("selected", "#103010")], foreground=[("selected", "#00ff66")])
        style.configure("Treeview", background="#020802", fieldbackground="#020802", foreground="#00dd55", rowheight=25)
        style.configure("Treeview.Heading", background="#0a1c0a", foreground="#00ff66")
        style.map("Treeview", background=[("selected", "#145214")], foreground=[("selected", "#ffffff")])

        # -----------------------------------------------------------------
        # COMBOBOX MATRIX / MATRIX COMBOBOX
        # -----------------------------------------------------------------
        
        
        
        # On some Linux themes, a readonly Combobox may stay white even
        #      with a dark global style. Force field, text, readonly and active
        #      colors here for consistent readability.
        style.configure(
            "Matrix.TCombobox",
            foreground="#00ff66",
            fieldbackground="#010601",
            background="#0b1c0b",
            arrowcolor="#00ff66",
            bordercolor="#0b3d0b",
            lightcolor="#0b3d0b",
            darkcolor="#0b3d0b",
            padding=4,
        )
        style.map(
            "Matrix.TCombobox",
            fieldbackground=[
                ("readonly", "#010601"),
                ("focus", "#010601"),
                ("!disabled", "#010601"),
            ],
            foreground=[
                ("readonly", "#00ff66"),
                ("focus", "#00ff66"),
                ("!disabled", "#00ff66"),
            ],
            background=[
                ("readonly", "#0b1c0b"),
                ("active", "#123812"),
            ],
            arrowcolor=[
                ("readonly", "#00ff66"),
                ("active", "#ffffff"),
            ],
        )

        self.status_var = tk.StringVar(value=f"MDADM Manager v{APP_VERSION} // ROOT // Rafraîchissement 15 s // Prêt")
        self.selected_array = tk.StringVar()
        self.refresh_ms = 15000
        self.selected_member_key = None
        self.selected_manage_member_key = None
        
        
        self.smart_metrics_cache = {}
        self.smart_metrics_cache_seconds = 120

        
        
        
        # Build and display the GUI first. Slower disk/SMART probing starts
        #      immediately afterward, so the application appears much faster.
        self._smart_scan_running = False

        
        
        
        
        # A lightweight MATRIX loading screen is displayed immediately.
        #      The heavy GUI is then built tab by tab with after(), avoiding
        #      a several-second black window.
        self._build_startup_screen()
        self.after(25, self._build_ui_staged)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds the black/green MATRIX language menu.
    def build_language_menu(self):

        
        menu_bg = "#020802"
        menu_fg = "#00dd55"
        menu_active_bg = "#103010"
        menu_active_fg = "#00ff66"

        menubar = tk.Menu(
            self,
            bg=menu_bg,
            fg=menu_fg,
            activebackground=menu_active_bg,
            activeforeground=menu_active_fg,
            borderwidth=0,
            relief="flat",
        )

        language_menu = tk.Menu(
            menubar,
            tearoff=False,
            bg=menu_bg,
            fg=menu_fg,
            activebackground=menu_active_bg,
            activeforeground=menu_active_fg,
            selectcolor=menu_fg,
            borderwidth=1,
            relief="solid",
        )
        self.language_menu_var = tk.StringVar(value=CURRENT_LANGUAGE)

        language_menu.add_radiobutton(
            label="Français",
            variable=self.language_menu_var,
            value="fr",
            command=lambda: self.change_language("fr")
        )
        language_menu.add_radiobutton(
            label="English",
            variable=self.language_menu_var,
            value="en",
            command=lambda: self.change_language("en")
        )

        menubar.add_cascade(
            label="Langue / Language",
            menu=language_menu
        )
        self.config(menu=menubar)

    
    # Saves the new language and informs the user about restart behavior.
    def change_language(self, code):
        global CURRENT_LANGUAGE
        if code not in LANGUAGES:
            return

        CURRENT_LANGUAGE = code
        save_language(code)

        messagebox.showinfo(
            tr("language_changed"),
            tr("language_restart"),
            parent=self
        )


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Immediately displays a very lightweight loading screen.
    def _build_startup_screen(self):

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.startup_frame = tk.Frame(self, bg="#020802")
        self.startup_frame.grid(row=0, column=0, sticky="nsew")

        center = tk.Frame(self.startup_frame, bg="#020802")
        center.place(relx=0.5, rely=0.46, anchor="center")

        tk.Label(
            center,
            text=f"MDADM MANAGER v{APP_VERSION}",
            bg="#020802",
            fg="#00ff66",
            font=("DejaVu Sans Mono", 20, "bold"),
        ).pack(pady=(0, 12))

        tk.Label(
            center,
            text="Initialisation…" if CURRENT_LANGUAGE != "en" else "Initializing…",
            bg="#020802",
            fg="#00cc55",
            font=("DejaVu Sans Mono", 11),
        ).pack()

        self.startup_progress_var = tk.StringVar(value="[░░░░░░]")

        tk.Label(
            center,
            textvariable=self.startup_progress_var,
            bg="#020802",
            fg="#00dd55",
            font=("DejaVu Sans Mono", 13, "bold"),
        ).pack(pady=(12, 0))

        
        self.update_idletasks()


    
    # Prepares tabs and starts priority-aware progressive loading.
    def _build_ui_staged(self):













        self.nb = ttk.Notebook(self)
        self.nb.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.nb.configure(style="Matrix.TNotebook")

        self.tab_info = tk.Frame(self.nb, bg="#020802")
        self.tab_dashboard = tk.Frame(self.nb, bg="#020802")
        self.tab_create = tk.Frame(self.nb, bg="#020802")
        self.tab_manage = tk.Frame(self.nb, bg="#020802")
        self.tab_disks = tk.Frame(self.nb, bg="#020802")
        self.tab_config = tk.Frame(self.nb, bg="#020802")

        self.nb.add(self.tab_dashboard, text=tr("dashboard"))
        self.nb.add(self.tab_create, text=tr("create_raid"))
        self.nb.add(self.tab_manage, text=tr("manage_raid"))
        self.nb.add(self.tab_disks, text=tr("disks"))
        self.nb.add(self.tab_config, text=tr("configuration"))
        self.nb.add(self.tab_info, text=tr("raid_info"))

        self.status_widget = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
        )
        self.status_widget.grid(row=1, column=0, sticky="ew")

        
        # 0=Dashboard, 1=Create RAID, 2=Manage RAID, 3=Disks,
        # 4=Configuration, 5=RAID Info.
        self._startup_tab_built = set()
        self._startup_tab_building = set()
        self._startup_background_after_id = None
        self._startup_finished = False

        self._startup_tab_builders = {
            0: self._build_dashboard,
            1: self._build_create,
            2: self._build_manage,
            3: self._build_disks,
            4: self._build_config,
            5: self._build_info,
        }

        
        
        self._startup_background_order = [0, 1, 2, 3, 4, 5]

        
        for index in range(6):
            self._show_tab_loading_placeholder(index)

        
        
        self.nb.bind("<<NotebookTabChanged>>", self._on_startup_tab_changed, add="+")

        self.startup_progress_var.set("[█░░░░░] Dashboard")

        
        self.nb.select(self.tab_dashboard)
        self.after(1, lambda: self._ensure_startup_tab_built(0, user_requested=False))


    def _show_tab_loading_placeholder(self, index):

        tab = self.nb.nametowidget(self.nb.tabs()[index])

        holder = tk.Frame(tab, bg="#020802")
        holder.pack(fill="both", expand=True)

        label = tk.Label(
            holder,
            text=(
                "Chargement de cette section…\n"
                "Cliquez ici et elle devient prioritaire."
                if CURRENT_LANGUAGE != "en"
                else
                "Loading this section…\n"
                "Open it and it becomes the priority."
            ),
            bg="#020802",
            fg="#00cc55",
            font=("DejaVu Sans Mono", 11),
            justify="center",
        )
        label.place(relx=0.5, rely=0.45, anchor="center")


    def _clear_tab_before_build(self, index):

        tab = self.nb.nametowidget(self.nb.tabs()[index])
        for child in tab.winfo_children():
            child.destroy()


    def _on_startup_tab_changed(self, event=None):






        if not hasattr(self, "_startup_tab_built"):
            return

        try:
            index = self.nb.index(self.nb.select())
        except tk.TclError:
            return

        if index not in self._startup_tab_built:
            self._ensure_startup_tab_built(index, user_requested=True)


    def _ensure_startup_tab_built(self, index, user_requested=False):

        if index in self._startup_tab_built or index in self._startup_tab_building:
            return

        
        
        if user_requested and self._startup_background_after_id is not None:
            try:
                self.after_cancel(self._startup_background_after_id)
            except tk.TclError:
                pass
            self._startup_background_after_id = None

        self._startup_tab_building.add(index)

        tab_names_fr = {
            0: "Tableau de bord",
            1: "Création RAID",
            2: "Gestion RAID",
            3: "Disques",
            4: "Configuration",
            5: "Info RAID",
        }
        tab_names_en = {
            0: "Dashboard",
            1: "Create RAID",
            2: "Manage RAID",
            3: "Disks",
            4: "Configuration",
            5: "RAID Info",
        }
        tab_name = (tab_names_en if CURRENT_LANGUAGE == "en" else tab_names_fr)[index]

        if getattr(self, "startup_frame", None) is not None:
            blocks = "█" * (index + 1)
            spaces = "░" * (5 - index)
            self.startup_progress_var.set(f"[{blocks}{spaces}] {tab_name}")

        self.set_status(
            f"Chargement : {tab_name}…"
            if CURRENT_LANGUAGE != "en"
            else f"Loading: {tab_name}…"
        )

        
        self.update_idletasks()

        self._clear_tab_before_build(index)
        builder = self._startup_tab_builders[index]

        try:
            builder()
            self._startup_tab_built.add(index)
        finally:
            self._startup_tab_building.discard(index)

        
        if index == 0:
            if getattr(self, "startup_frame", None) is not None:
                self.startup_frame.destroy()
                self.startup_frame = None

            self.nb.select(self.tab_dashboard)
            self.update_idletasks()

            # Affichage RAID rapide, sans SMART bloquant.
            self.after(
                1,
                lambda: self.refresh_arrays(
                    include_manage=(2 in self._startup_tab_built),
                    allow_smart_query=False,
                ),
            )

        
        elif index == 2:
            self.after(
                1,
                lambda: self.refresh_arrays(
                    include_manage=True,
                    allow_smart_query=False,
                ),
            )

        self.update_idletasks()

        
        
        # sans donner l'impression que l'application prend son temps.
        if len(self._startup_tab_built) == len(self._startup_tab_builders):
            self._finish_progressive_startup()
        else:
            delay = 15 if user_requested else 65
            self._schedule_next_background_tab(delay)


    def _schedule_next_background_tab(self, delay=65):

        if self._startup_finished:
            return

        if self._startup_background_after_id is not None:
            try:
                self.after_cancel(self._startup_background_after_id)
            except tk.TclError:
                pass

        self._startup_background_after_id = self.after(
            delay,
            self._build_next_background_tab,
        )


    def _build_next_background_tab(self):

        self._startup_background_after_id = None

        for index in self._startup_background_order:
            if (
                index not in self._startup_tab_built
                and index not in self._startup_tab_building
            ):
                self._ensure_startup_tab_built(index, user_requested=False)
                return

        self._finish_progressive_startup()


    def _finish_progressive_startup(self):

        if self._startup_finished:
            return

        if len(self._startup_tab_built) != len(self._startup_tab_builders):
            return

        self._startup_finished = True
        self.apply_matrix_widgets()
        self.update_idletasks()

        self.set_status(
            "Interface prête — analyse système en arrière-plan…"
            if CURRENT_LANGUAGE != "en"
            else "Interface ready — background system analysis…"
        )

        
        self.after(1, self._startup_fast_refresh)
        self.after(self.refresh_ms, self.auto_refresh)


    
    
    def _build_ui(self):
        self._build_startup_screen()
        self.after(25, self._build_ui_staged)


    # -------------------------------------------------------------------------
    # ONGLET INFO RAID / RAID INFO TAB
    # -------------------------------------------------------------------------

    
    # Builds the educational RAID Info tab and its diagrams.
    def _build_info(self):
        f = self.tab_info
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)

        outer = ttk.Frame(f)
        outer.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        ttk.Label(
            outer,
            text="GUIDE VISUEL DES TYPES DE RAID",
            font=("TkFixedFont", 14, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        canvas = tk.Canvas(outer, bg="#020802", highlightthickness=0)
        canvas.grid(row=1, column=0, sticky="nsew")

        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        sb.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=sb.set)

        content = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=content, anchor="nw")

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(win_id, width=e.width)
        )

        ttk.Label(
            content,
            text=(
                "Le RAID combine plusieurs disques pour obtenir plus de vitesse, "
                "plus de capacité ou de la redondance. IMPORTANT : un RAID ne remplace "
                "jamais une sauvegarde."
            ),
            justify="left",
            wraplength=1300,
            font=("TkFixedFont", 10, "bold")
        ).pack(fill="x", pady=(0, 10))

        raids = [
            (
                "RAID 0 — RAPIDE, MAIS AUCUNE PROTECTION",
                "Minimum : 2 disques\n"
                "Tolérance aux pannes : AUCUNE\n"
                "Capacité utile : 100 % de la capacité totale\n"
                "Usage : fichiers temporaires, gros débit, données non critiques\n"
                "Avantage : performances maximales\n"
                "Risque : 1 seul disque en panne = RAID complet perdu",
                "        DONNÉES\n"
                "           │\n"
                "      ┌────┴────┐\n"
                "      │         │\n"
                "  ┌───────┐ ┌───────┐\n"
                "  │DISQUE1│ │DISQUE2│\n"
                "  │ A C E │ │ B D F │\n"
                "  └───────┘ └───────┘\n"
                "     STRIPING"
            ),
            (
                "RAID 1 — MIROIR",
                "Minimum : 2 disques\n"
                "Tolérance aux pannes : 1 disque\n"
                "Capacité utile : 50 % avec 2 disques\n"
                "Usage : système et données importantes\n"
                "Avantage : simple et sécuritaire\n"
                "Risque : capacité divisée par deux",
                "        DONNÉES\n"
                "           │\n"
                "      ┌────┴────┐\n"
                "      │         │\n"
                "  ┌───────┐ ┌───────┐\n"
                "  │DISQUE1│ │DISQUE2│\n"
                "  │ A B C │ │ A B C │\n"
                "  └───────┘ └───────┘\n"
                "       MIROIR"
            ),
            (
                "RAID 5 — 1 DISQUE DE PARITÉ",
                "Minimum : 3 disques\n"
                "Tolérance aux pannes : 1 disque\n"
                "Capacité utile : (N - 1) × taille du plus petit disque\n"
                "Usage : stockage général\n"
                "Avantage : bon compromis capacité/protection\n"
                "Risque : reconstruction plus lourde sur gros volumes",
                "          RAID 5\n"
                " ┌────────┬────────┬────────┐\n"
                " │DISQUE1 │DISQUE2 │DISQUE3 │\n"
                " ├────────┼────────┼────────┤\n"
                " │   A    │   B    │  PAB   │\n"
                " │   C    │  PCD   │   D    │\n"
                " │  PEF   │   E    │   F    │\n"
                " └────────┴────────┴────────┘\n"
                " P = PARITÉ"
            ),
            (
                "RAID 6 — DOUBLE PARITÉ",
                "Minimum : 4 disques\n"
                "Tolérance aux pannes : 2 disques\n"
                "Capacité utile : (N - 2) × taille du plus petit disque\n"
                "Usage : gros ensembles RAID et données importantes\n"
                "Avantage : peut survivre à 2 pannes\n"
                "Risque : écritures/reconstruction plus lourdes",
                "             RAID 6\n"
                " ┌────────┬────────┬────────┬────────┐\n"
                " │DISQUE1 │DISQUE2 │DISQUE3 │DISQUE4 │\n"
                " ├────────┼────────┼────────┼────────┤\n"
                " │   A    │   B    │   P    │   Q    │\n"
                " │   C    │   P    │   Q    │   D    │\n"
                " │   P    │   Q    │   E    │   F    │\n"
                " └────────┴────────┴────────┴────────┘\n"
                " P + Q = DOUBLE PARITÉ"
            ),
            (
                "RAID 10 — MIROIR + PERFORMANCE",
                "Minimum : 4 disques\n"
                "Tolérance : dépend de quels disques tombent en panne\n"
                "Capacité utile : environ 50 %\n"
                "Usage : serveur, VM, bases de données, gros débit\n"
                "Avantage : très bonnes performances + redondance\n"
                "Risque : nécessite davantage de disques",
                "                RAID 10\n"
                "         ┌────────┴────────┐\n"
                "         │                 │\n"
                "      MIROIR A          MIROIR B\n"
                "    ┌────┴────┐        ┌────┴────┐\n"
                " ┌──────┐ ┌──────┐  ┌──────┐ ┌──────┐\n"
                " │DISQ 1│ │DISQ 2│  │DISQ 3│ │DISQ 4│\n"
                " │ A C E│ │ A C E│  │ B D F│ │ B D F│\n"
                " └──────┘ └──────┘  └──────┘ └──────┘"
            ),
        ]

        for title, description, diagram in raids:
            box = ttk.LabelFrame(content, text=title)
            box.pack(fill="x", pady=6)

            box.columnconfigure(0, weight=3)
            box.columnconfigure(1, weight=2)

            ttk.Label(
                box,
                text=description,
                justify="left",
                wraplength=700,
                font=("TkFixedFont", 10)
            ).grid(row=0, column=0, sticky="nw", padx=10, pady=10)

            txt = tk.Text(
                box,
                height=10,
                width=52,
                wrap="none",
                font=("TkFixedFont", 10),
                bg="#001500",
                fg="#00ff66",
                insertbackground="#00ff66",
                relief="solid",
                borderwidth=1
            )
            txt.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
            txt.insert("1.0", ui_text(diagram))
            txt.configure(state="disabled")

        quick = ttk.LabelFrame(content, text="CHOIX RAPIDE")
        quick.pack(fill="x", pady=(10, 6))

        ttk.Label(
            quick,
            text=(
                "RAID 0  → vitesse maximale, aucune protection\n"
                "RAID 1  → simple et sécuritaire avec 2 disques\n"
                "RAID 5  → bon compromis capacité/protection, 1 panne tolérée\n"
                "RAID 6  → meilleur choix quand 2 pannes doivent être tolérées\n"
                "RAID 10 → excellent mélange performance/redondance\n\n"
                "Plus le RAID contient de disques et plus sa reconstruction est longue, "
                "plus RAID 6 ou RAID 10 devient intéressant pour des données importantes."
            ),
            justify="left",
            wraplength=1300,
            font=("TkFixedFont", 10, "bold")
        ).pack(anchor="w", padx=10, pady=10)

        def wheel(event):
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(3, "units")
            elif getattr(event, "delta", 0):
                canvas.yview_scroll(int(-event.delta / 120), "units")

        canvas.bind("<Enter>", lambda e: (
            canvas.bind_all("<MouseWheel>", wheel),
            canvas.bind_all("<Button-4>", wheel),
            canvas.bind_all("<Button-5>", wheel)
        ))
        canvas.bind("<Leave>", lambda e: (
            canvas.unbind_all("<MouseWheel>"),
            canvas.unbind_all("<Button-4>"),
            canvas.unbind_all("<Button-5>")
        ))


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds the active-array dashboard.
    def _build_dashboard(self):
        f = self.tab_dashboard
        f.columnconfigure(0, weight=0)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(0, weight=1)

        left = ttk.Frame(f)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8), pady=4)

        ttk.Label(
            left,
            text="ARRAYS MDADM",
            font=("TkFixedFont", 12, "bold")
        ).pack(anchor="w")

        self.arr_list = tk.Listbox(
            left,
            width=30,
            height=28,
            font=("TkFixedFont", 10),
            bg="#010601",
            fg="#00ff66",
            selectbackground="#145214",
            selectforeground="#ffffff",
            highlightbackground="#0b3d0b",
            highlightcolor="#00aa44",
            relief="flat",
        )
        self.arr_list.pack(fill="y", expand=True, pady=(5, 8))
        self.arr_list.bind("<<ListboxSelect>>", self.on_array_select)

        ttk.Button(left, text="⟳  Rafraîchir", command=self.refresh_all).pack(fill="x")

        right = ttk.Frame(f)
        right.grid(row=0, column=1, sticky="nsew", pady=4)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)
        right.rowconfigure(6, weight=1)

        self.summary_var = tk.StringVar(value="Sélectionne un array.")
        ttk.Label(
            right,
            textvariable=self.summary_var,
            justify="left",
            font=("TkFixedFont", 11, "bold")
        ).grid(row=0, column=0, sticky="ew", padx=4, pady=(2, 4))

        self.mount_var = tk.StringVar(value="Montage : —")
        ttk.Label(
            right,
            textvariable=self.mount_var,
            justify="left",
            font=("TkFixedFont", 10)
        ).grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 6))

        ttk.Label(
            right,
            text="DISQUES MEMBRES DU RAID",
            font=("TkFixedFont", 11, "bold")
        ).grid(row=2, column=0, sticky="w", padx=4, pady=(4, 2))

        cols = ("device", "slot", "state", "size", "model", "serial", "temp", "bad", "usage")
        self.member_tree = ttk.Treeview(right, columns=cols, show="headings", height=10)
        heads = {
            "device": "Périphérique",
            "slot": "Slot",
            "state": "État",
            "size": "Taille",
            "model": "Modèle",
            "serial": "N° série",
            "temp": "Temp",
            "bad": "Erreurs / secteurs",
            "usage": "Utilisation",
        }
        widths = {
            "device": 205,
            "slot": 60,
            "state": 190,
            "size": 100,
            "model": 200,
            "serial": 190,
            "temp": 58,
            "bad": 155,
            "usage": 175,
        }
        for col in cols:
            self.member_tree.heading(col, text=heads[col])
            self.member_tree.column(
                col,
                width=widths[col],
                anchor=("center" if col == "temp" else "w"),
                stretch=(False if col == "temp" else True),
            )

        self.member_tree.tag_configure("ok", foreground="#00ff66")
        self.member_tree.tag_configure("warning", foreground="#ffb000")
        self.member_tree.tag_configure("problem", foreground="#ff3b3b")
        self.member_tree.tag_configure("removed", foreground="#ff3b3b")

        self.member_tree.grid(row=3, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.member_tree.bind("<<TreeviewSelect>>", self.on_member_select)
        self.member_tree.bind("<Double-1>", self.member_smart)

        member_scroll = ttk.Scrollbar(right, orient="vertical", command=self.member_tree.yview)
        member_scroll.grid(row=3, column=1, sticky="ns", pady=(0, 4))
        self.member_tree.configure(yscrollcommand=member_scroll.set)

        self.selected_member_var = tk.StringVar(value="Aucun disque sélectionné")
        ttk.Label(
            right,
            textvariable=self.selected_member_var,
            font=("TkFixedFont", 10)
        ).grid(row=4, column=0, sticky="ew", padx=4, pady=(2, 4))

        diskbar = ttk.Frame(right)
        diskbar.grid(row=5, column=0, sticky="ew", padx=4, pady=(0, 6))
        for i in range(5):
            diskbar.columnconfigure(i, weight=1)

        ttk.Button(diskbar, text="SMART", command=self.member_smart).grid(row=0, column=0, padx=3, sticky="ew")
        ttk.Button(diskbar, text="Marquer FAULTY", command=self.member_faulty).grid(row=0, column=1, padx=3, sticky="ew")
        ttk.Button(diskbar, text="Retirer", command=self.member_remove).grid(row=0, column=2, padx=3, sticky="ew")
        ttk.Button(diskbar, text="REMPLACER LE DISQUE", command=self.replace_selected_member).grid(row=0, column=3, padx=3, sticky="ew")
        ttk.Button(diskbar, text="Détails RAID", command=self.dashboard_details).grid(row=0, column=4, padx=3, sticky="ew")

        self.detail_text = tk.Text(
            right,
            wrap="none",
            height=9,
            font=("TkFixedFont", 9),
            bg="#010601",
            fg="#00ff66",
            insertbackground="#00ff66",
            selectbackground="#145214",
            selectforeground="#ffffff",
            highlightbackground="#0b3d0b",
            highlightcolor="#00aa44",
            relief="flat",
        )
        self.detail_text.grid(row=6, column=0, sticky="nsew", padx=4, pady=(2, 0))

        sy = ttk.Scrollbar(right, orient="vertical", command=self.detail_text.yview)
        sy.grid(row=6, column=1, sticky="ns", pady=(2, 0))
        self.detail_text.configure(yscrollcommand=sy.set)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds the creation tab and the button that opens the wizard.
    def _build_create(self):
        f = self.tab_create
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        hero = ttk.Frame(f, padding=18)
        hero.grid(row=0, column=0, sticky="ew")
        hero.columnconfigure(0, weight=1)

        ttk.Label(
            hero,
            text="ASSISTANT DE CRÉATION RAID",
            font=("TkFixedFont", 16, "bold")
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            hero,
            text=(
                "Création guidée en 4 étapes : choix du niveau RAID, analyse et "
                "sélection des disques, paramètres, puis vérification finale."
            ),
            wraplength=1000,
            justify="left"
        ).grid(row=1, column=0, sticky="w", pady=(8, 12))

        ttk.Button(
            hero,
            text=tr("wizard_launch"),
            command=self.open_create_wizard
        ).grid(row=2, column=0, sticky="w", pady=(4, 8))

        info = ttk.LabelFrame(f, text="Ce que l'assistant vérifie")
        info.grid(row=1, column=0, sticky="ew", padx=18, pady=8)
        info.columnconfigure(0, weight=1)

        ttk.Label(
            info,
            text=(
                "• Modèle, numéro de série, taille et type HDD / SSD / NVMe\n"
                "• État SMART, heures de fonctionnement et usure / risque\n"
                "• RAID actuel, partitions, systèmes de fichiers et points de montage\n"
                "• Capacité utile estimée selon RAID 0 / 1 / 5 / 6 / 10\n"
                "• Comptage rapide des disques libres sans attendre SMART\n"
                "• SMART détaillé à la demande, sans bloquer l'assistant\n"
                "• Niveaux RAID impossibles automatiquement grisés\n"
                "• Tolérance aux pannes et nombre minimal de disques\n"
                "• Protection ABSOLUE des disques déjà membres d'un RAID existant\n"
                "• Protection ABSOLUE des disques/partitions référencés dans /etc/fstab\n"
                "• Détection fstab par /dev, UUID, PARTUUID, LABEL et PARTLABEL\n"
                "• Analyse mdadm --examine des anciennes métadonnées RAID\n"
                "• --zero-superblock proposé seulement pour un ancien RAID orphelin\n"
                "• Le mode avancé ne peut jamais contourner RAID ou FSTAB\n"
                "• Vérification finale de la commande mdadm avant écriture\n"                 "• Interface Français / English sélectionnable et mémorisée"
            ),
            justify="left",
            padding=12,
            font=("TkFixedFont", 10)
        ).grid(row=0, column=0, sticky="w")

        guide = ttk.LabelFrame(f, text="Repères rapides")
        guide.grid(row=2, column=0, sticky="nsew", padx=18, pady=(8, 18))
        guide.columnconfigure(0, weight=1)

        ttk.Label(
            guide,
            text=(
                "RAID 0  → performances / capacité, aucune protection\n"
                "RAID 1  → miroir simple, très facile à comprendre et reconstruire\n"
                "RAID 5  → 1 disque de parité, tolère 1 panne\n"
                "RAID 6  → 2 disques de parité, tolère 2 pannes\n"
                "RAID 10 → miroir + performances, excellent choix avec plusieurs disques\n\n"
                "La capacité réelle est limitée par le plus petit disque de l'ensemble."
            ),
            justify="left",
            padding=14,
            font=("TkFixedFont", 10)
        ).grid(row=0, column=0, sticky="nw")

        
        
        self.create_name = ttk.Entry(f)
        self.create_name.insert(0, "md20")
        self.create_level = ttk.Combobox(f, values=["raid0", "raid1", "raid5", "raid6", "raid10"], style="Matrix.TCombobox")
        self.create_level.set("raid10")
        self.create_chunk = ttk.Combobox(f, values=["64", "128", "256", "512", "1024"], style="Matrix.TCombobox")
        self.create_chunk.set("512")
        self.create_meta = ttk.Combobox(f, values=["1.2", "1.1", "1.0"], style="Matrix.TCombobox")
        self.create_meta.set("1.2")
        self.create_bitmap = tk.BooleanVar(value=True)
        self.create_disks = tk.Listbox(f, selectmode="extended")

    
    # Opens a new RAID creation wizard instance.
    def open_create_wizard(self):
        RaidCreationWizard(self)


    # -------------------------------------------------------------------------
    # ONGLET GESTION RAID / MANAGE RAID TAB
    # -------------------------------------------------------------------------

    
    # Builds management controls: details, stop, check, repair, members, etc.
    def _build_manage(self):
        f = self.tab_manage
        f.columnconfigure(0, weight=1)
        f.rowconfigure(4, weight=1)

        top = ttk.Frame(f)
        top.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Array :").grid(row=0, column=0, sticky="e", padx=(0, 6))
        self.manage_array = ttk.Combobox(top, state="readonly", style="Matrix.TCombobox")
        self.manage_array.grid(row=0, column=1, sticky="ew")
        self.manage_array.bind("<<ComboboxSelected>>", self.on_manage_array_select)

        actionbar = ttk.Frame(f)
        actionbar.grid(row=1, column=0, sticky="ew", padx=6, pady=4)

        actions = [
            ("Détails", self.manage_details),
            ("Assembler", self.manage_assemble),
            ("Arrêter", self.manage_stop),
            ("Check", self.manage_check),
            ("Repair", self.manage_repair),
            ("Ajouter membre", self.manage_add),
            ("Retirer sélection", self.member_remove),
            ("Faulty sélection", self.member_faulty),
            ("Remplacer sélection", self.replace_selected_member),
            ("Zero superblock", self.manage_zero_superblock),
        ]
        for i, (label, fn) in enumerate(actions):
            ttk.Button(actionbar, text=label, command=fn).grid(
                row=i // 5, column=i % 5, padx=3, pady=3, sticky="ew"
            )
            actionbar.columnconfigure(i % 5, weight=1)

        ttk.Label(
            f,
            text="Membres — sélectionne directement le disque sur lequel agir",
            font=("TkFixedFont", 10, "bold")
        ).grid(row=2, column=0, sticky="w", padx=6, pady=(6, 2))

        cols = ("device", "slot", "state", "size", "model", "serial", "temp", "bad", "usage")
        self.manage_member_tree = ttk.Treeview(f, columns=cols, show="headings", height=8)
        heads = {
            "device": "Périphérique",
            "slot": "Slot",
            "state": "État",
            "size": "Taille",
            "model": "Modèle",
            "serial": "N° série",
            "temp": "Temp",
            "bad": "Erreurs / secteurs",
            "usage": "Utilisation",
        }
        widths = {
            "device": 205, "slot": 60, "state": 180,
            "size": 100, "model": 200, "serial": 180,
            "temp": 58, "bad": 155, "usage": 175
        }
        for col in cols:
            self.manage_member_tree.heading(col, text=heads[col])
            self.manage_member_tree.column(
                col,
                width=widths[col],
                anchor=("center" if col == "temp" else "w"),
                stretch=(False if col == "temp" else True),
            )
        self.manage_member_tree.tag_configure("ok", foreground="#00ff66")
        self.manage_member_tree.tag_configure("warning", foreground="#ffb000")
        self.manage_member_tree.tag_configure("problem", foreground="#ff3b3b")
        self.manage_member_tree.tag_configure("removed", foreground="#ff3b3b")
        self.manage_member_tree.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 6))
        self.manage_member_tree.bind("<<TreeviewSelect>>", self.on_manage_member_select)

        self.manage_output = tk.Text(f, wrap="none", font=("TkFixedFont", 10))
        self.manage_output.grid(row=4, column=0, sticky="nsew", padx=6, pady=6)


    # -------------------------------------------------------------------------
    # ONGLET DISQUES / SMART / DISKS / SMART TAB
    # -------------------------------------------------------------------------

    
    # Builds the physical disk inventory with SMART/RAID columns.
    def _build_disks(self):
        f = self.tab_disks
        f.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)

        cols = (
            "path", "size", "model", "serial", "temp",
            "raid", "member", "raid_state",
            "smart", "bad", "usage", "wear",
            "fstype", "mount"
        )
        self.disk_tree = ttk.Treeview(f, columns=cols, show="headings")

        heads = {
            "path": "Périphérique",
            "size": "Taille",
            "model": "Modèle",
            "serial": "Série",
            "temp": "Temp",
            "raid": "RAID",
            "member": "Membre RAID",
            "raid_state": "État RAID",
            "smart": "SMART",
            "bad": "Erreurs / secteurs",
            "usage": "Utilisation",
            "wear": "Usure / Risque",
            "fstype": "FS",
            "mount": "Montage",
        }

        widths = {
            "path": 105,
            "size": 90,
            "model": 190,
            "serial": 165,
            "temp": 58,
            "raid": 95,
            "member": 125,
            "raid_state": 175,
            "smart": 80,
            "bad": 145,
            "usage": 170,
            "wear": 145,
            "fstype": 125,
            "mount": 190,
        }

        for c in cols:
            self.disk_tree.heading(c, text=heads[c])
            self.disk_tree.column(
                c,
                width=widths[c],
                minwidth=(48 if c == "temp" else 60),
                anchor=("center" if c == "temp" else "w"),
                stretch=(False if c == "temp" else True),
            )

        self.disk_tree.tag_configure("ok", foreground="#00ff66")
        self.disk_tree.tag_configure("warning", foreground="#ffb000")
        self.disk_tree.tag_configure("problem", foreground="#ff3b3b")

        self.disk_tree.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        sb_y = ttk.Scrollbar(f, orient="vertical", command=self.disk_tree.yview)
        sb_y.grid(row=0, column=1, sticky="ns", pady=6)

        sb_x = ttk.Scrollbar(f, orient="horizontal", command=self.disk_tree.xview)
        sb_x.grid(row=1, column=0, sticky="ew", padx=6)

        self.disk_tree.configure(
            yscrollcommand=sb_y.set,
            xscrollcommand=sb_x.set
        )

        bar = ttk.Frame(f)
        bar.grid(row=2, column=0, sticky="ew", padx=6, pady=6)

        ttk.Button(
            bar,
            text="Rafraîchir",
            command=self.refresh_disks
        ).pack(side="left")

        ttk.Button(
            bar,
            text="SMART du disque sélectionné",
            command=self.show_smart
        ).pack(side="left", padx=8)

        ttk.Label(
            bar,
            text="RAID/Membre provient de mdadm, pas seulement de FSTYPE.",
            font=("TkFixedFont", 9)
        ).pack(side="left", padx=14)


    # -------------------------------------------------------------------------
    # ONGLET CONFIGURATION MDADM / MDADM CONFIGURATION TAB
    # -------------------------------------------------------------------------

    
    # Builds the mdadm.conf editor.
    def _build_config(self):
        f = self.tab_config
        self.config_loaded_path = "/etc/mdadm/mdadm.conf"
        self.config_file_var = tk.StringVar(
            value="Fichier actuellement chargé : /etc/mdadm/mdadm.conf"
        )
        f.rowconfigure(2, weight=1)
        f.columnconfigure(0, weight=1)

        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        ttk.Button(bar, text="Charger mdadm.conf", command=self.load_config).pack(side="left")
        ttk.Button(bar, text="Scanner les arrays", command=self.scan_config).pack(side="left", padx=8)
        ttk.Button(bar, text="Sauvegarder mdadm.conf", command=self.save_config).pack(side="left")
        ttk.Button(bar, text="Sauvegarder une copie", command=self.export_config).pack(side="left", padx=8)

        ttk.Label(
            f,
            textvariable=self.config_file_var,
            font=("TkFixedFont", 10, "bold")
        ).grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 5))

        self.config_text = tk.Text(f, wrap="none", font=("TkFixedFont", 10))
        self.config_text.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)

    
    # Applies MATRIX colors/styles to widgets needing post-creation adjustments.
    def apply_matrix_widgets(self):
        def walk(widget):
            for child in widget.winfo_children():
                try:
                    if isinstance(child, tk.Text):
                        child.configure(bg="#010601", fg="#00ff66",
                                        insertbackground="#00ff66",
                                        selectbackground="#145214",
                                        selectforeground="#ffffff",
                                        relief="flat")
                    elif isinstance(child, tk.Listbox):
                        child.configure(bg="#010601", fg="#00ff66",
                                        selectbackground="#145214",
                                        selectforeground="#ffffff",
                                        relief="flat",
                                        highlightbackground="#0b3d0b",
                                        highlightcolor="#00aa44")
                except tk.TclError:
                    pass
                walk(child)
        walk(self)

    
    # Changes the message shown in the bottom status bar.
    def set_status(self, text):
        self.status_var.set(text)
        self.update_idletasks()


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Runs slow work in a thread, then returns to Tkinter's thread to update the GUI.
    def run_async(
        self,
        cmd,
        output_widget=None,
        privileged=False,
        timeout=120,
        show_error_popup=True,
        refresh_after=True
    ):
        
        
        # Tkinter must not be blocked by slow system commands on its main thread.
        # System work therefore runs in the background, then UI updates return through after().
        def worker():
            actual = privileged_cmd(cmd) if privileged else cmd
            self.after(0, lambda: self.set_status("Exécution : " + shell_join(actual)))
            rc, out = run(actual, timeout=timeout)

            def done():
                if output_widget is not None:
                    output_widget.delete("1.0", "end")
                    output_widget.insert("end", out)

                    
                    
                    
                    if rc != 0 and not show_error_popup:
                        output_widget.insert(
                            "end",
                            f"\n\n--- Code de retour : {rc} ---\n"
                            "Note : smartctl utilise des codes de retour par bits; "
                            "un code non nul ne signifie pas nécessairement que la "
                            "lecture SMART a échoué.\n"
                        )

                self.set_status(f"Terminé (code {rc})")

                if refresh_after:
                    self.refresh_all()

                if rc != 0 and show_error_popup:
                    messagebox.showerror(
                        "Commande",
                        out[-3000:] if out else f"Code {rc}"
                    )

            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Refreshes all major views without requiring the user to switch tabs.
    def _startup_fast_refresh(self):

        
        
        # RAID/lsblk information is usually fast. SMART can take several
        #      seconds on systems containing many drives.
        self.set_status(
            f"MDADM Manager v{APP_VERSION} // ROOT // Chargement rapide…"
            if CURRENT_LANGUAGE != "en"
            else f"MDADM Manager v{APP_VERSION} // ROOT // Fast loading…"
        )
        self.refresh_arrays()
        self.refresh_disks(allow_smart_query=False)
        self.refresh_create_disks()

        if hasattr(self, "manage_array") and self.manage_array.get().strip():
            self.refresh_manage_members(self.manage_array.get().strip())

        
        self.start_smart_refresh_background()

    def start_smart_refresh_background(self):

        if getattr(self, "_smart_scan_running", False):
            return

        self._smart_scan_running = True

        def worker():
            try:
                devices = get_block_devices()
                paths = []
                for d in devices:
                    if d.get("type") != "disk":
                        continue
                    path = clean_device_path(d.get("path", ""))
                    if path:
                        paths.append(path)

                total = len(paths)

                for index, path in enumerate(paths, 1):
                    
                    data = smart_usage_metrics(path)
                    self.smart_metrics_cache[path] = {
                        "timestamp": time.time(),
                        "data": data,
                    }

                    
                    
                    self.after(
                        0,
                        lambda i=index, n=total: self.set_status(
                            f"SMART : {i}/{n}"
                        )
                    )

            finally:
                self._smart_scan_running = False

                def finish():
                    
                    
                    self.refresh_disks(allow_smart_query=False)
                    self.set_status(
                        f"MDADM Manager v{APP_VERSION} // ROOT // Rafraîchissement 15 s // Prêt"
                        if CURRENT_LANGUAGE != "en"
                        else f"MDADM Manager v{APP_VERSION} // ROOT // Refresh 15 s // Ready"
                    )

                self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def refresh_all(self):
        
        # Immediate fast refresh, followed by SMART in the background.
        if hasattr(self, "smart_metrics_cache"):
            self.smart_metrics_cache.clear()

        self.refresh_arrays()
        self.refresh_disks(allow_smart_query=False)
        self.refresh_create_disks()

        if hasattr(self, "manage_array") and self.manage_array.get().strip():
            self.refresh_manage_members(self.manage_array.get().strip())

        self.start_smart_refresh_background()

    
    # Schedules the next automatic refresh using Tkinter.after().
    def auto_refresh(self):
        self.refresh_arrays()
        self.after(self.refresh_ms, self.auto_refresh)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Rereads active arrays and updates the dashboard.
    def refresh_arrays(self, include_manage=True, allow_smart_query=True):
        arrays = get_md_arrays()

        current_path = self.selected_array.get().strip()
        if not current_path and self.arr_list.curselection():
            try:
                current_path = self.arr_list.get(self.arr_list.curselection()[0]).split()[0]
            except Exception:
                current_path = ""

        self.arr_list.delete(0, "end")
        names = []

        for a in arrays:
            names.append(a["path"])

            
            members, _ = parse_mdadm_members(a["path"])
            has_problem = any(m.get("problem") for m in members)
            has_warning = any(m.get("warning") for m in members)

            prefix = "●"
            line = f'{prefix} {a["path"]}   {a["level"]}   {a["state"]}'
            idx = self.arr_list.size()
            self.arr_list.insert("end", line)
            try:
                if has_problem:
                    self.arr_list.itemconfig(idx, fg="#ff3b3b")
                elif has_warning:
                    self.arr_list.itemconfig(idx, fg="#ffb000")
                else:
                    self.arr_list.itemconfig(idx, fg="#00ff66")
            except tk.TclError:
                pass

        
        
        # During staged startup, the Manage RAID tab may not exist yet.
        #      In that case, update only the Dashboard.
        manage_ready = (
            include_manage
            and hasattr(self, "manage_array")
            and hasattr(self, "manage_member_tree")
        )

        if manage_ready:
            self.manage_array["values"] = names

        if names:
            if manage_ready and self.manage_array.get() not in names:
                self.manage_array.set(names[0])

            target = current_path if current_path in names else names[0]
            self.selected_array.set(target)

            for i in range(self.arr_list.size()):
                if target in self.arr_list.get(i):
                    self.arr_list.selection_clear(0, "end")
                    self.arr_list.selection_set(i)
                    self.arr_list.activate(i)
                    break

            
            self.refresh_array_view(target, allow_smart_query=allow_smart_query)

            
            if manage_ready:
                self.refresh_manage_members(self.manage_array.get())
        else:
            self.selected_array.set("")
            self.summary_var.set("Aucun array mdadm actif détecté.")
            self.mount_var.set("Montage : —")
            self.member_tree.delete(*self.member_tree.get_children())

            if manage_ready:
                self.manage_member_tree.delete(
                    *self.manage_member_tree.get_children()
                )

    
    # Displays full details for the selected array and its members.
    def refresh_array_view(self, path, allow_smart_query=True):
        if not path:
            return

        members, detail = parse_mdadm_members(path)
        rc2, mdstat = run(["cat", "/proc/mdstat"], timeout=5)

        state = ""
        level = ""
        size = ""
        devices = ""
        failed = ""
        spare = ""

        for line in detail.splitlines():
            if "Raid Level" in line:
                level = line.split(":", 1)[1].strip()
            elif "State :" in line:
                state = line.split(":", 1)[1].strip()
            elif "Array Size" in line:
                size = line.split(":", 1)[1].strip()
            elif "Active Devices" in line:
                devices = line.split(":", 1)[1].strip()
            elif "Failed Devices" in line:
                failed = line.split(":", 1)[1].strip()
            elif "Spare Devices" in line:
                spare = line.split(":", 1)[1].strip()

        problems = sum(1 for m in members if m.get("problem"))
        warnings = sum(1 for m in members if m.get("warning"))
        health = "OK"
        if problems:
            health = f"PROBLÈME — {problems} disque(s)"
        elif warnings:
            health = f"ATTENTION — {warnings} disque(s)"

        self.summary_var.set(
            f"ARRAY : {path}    RAID : {level or '?'}    ÉTAT : {state or '?'}\n"
            f"TAILLE : {size or '?'}    ACTIFS : {devices or '?'}    "
            f"FAILED : {failed or '0'}    SPARE : {spare or '0'}    SANTÉ : {health}"
        )

        mount = get_array_mount_info(path)
        mountpoints = ", ".join(mount.get("mountpoints") or []) or "NON MONTÉ"
        fs = mount.get("fstype") or "—"
        label = mount.get("label") or "—"
        uuid = mount.get("uuid") or "—"
        source = mount.get("source") or path

        usage = ""
        if mount.get("size"):
            usage = (
                f"    ESPACE : {mount.get('used','?')} utilisés / "
                f"{mount.get('size','?')}    LIBRE : {mount.get('avail','?')} "
                f"({mount.get('use_percent','?')} utilisé)"
            )

        self.mount_var.set(
            f"MONTAGE : {mountpoints}    SOURCE : {source}    FS : {fs}    LABEL : {label}\n"
            f"UUID : {uuid}{usage}"
        )

        self.populate_member_tree(self.member_tree, path, members, allow_smart_query=allow_smart_query)

        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("end", detail)
        self.detail_text.insert("end", "\n\n--- INFORMATIONS DE MONTAGE ---\n")
        self.detail_text.insert("end", self.mount_var.get() + "\n")
        self.detail_text.insert("end", "\n--- /proc/mdstat ---\n")
        self.detail_text.insert("end", mdstat)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds a stable key from a Treeview row so selection can survive refreshes.
    def _member_key_from_values(self, values):

        if not values:
            return None

        shown = str(values[0])
        dev = shown
        if "  [/dev/" in dev:
            dev = dev.split("  [", 1)[0].strip()
        serial = str(values[5]).strip() if len(values) > 5 else ""
        slot = str(values[1]).strip() if len(values) > 1 else ""

        
        if serial and serial not in ("INCONNU", "—"):
            return ("serial", serial)
        return ("device", dev, slot)

    
    # Returns the stable key for the currently selected row.
    def _current_tree_selection_key(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        values = tree.item(sel[0], "values")
        return self._member_key_from_values(values)

    
    # Uses a small SMART cache to avoid unnecessarily rerunning smartctl on every refresh.
    def get_cached_smart_metrics(self, physical_path, allow_query=True):
        physical = clean_device_path(physical_path)
        if not physical:
            return {
                "reallocated": None,
                "pending": None,
                "uncorrectable": None,
                "media_errors": None,
                "bad_total": None,
                "power_hours": None,
                "power_days": None,
                "health": "INCONNU",
                "temperature": None,
                "percentage_used": None,
                "wear_percent": None,
                "wear_source": "",
                "index_kind": "wear",
                "disk_kind": "",
                "tb_written": None,
                "tbw_rating": None,
                "tbw_used_percent": None,
                "tbw_remaining_percent": None,
                "available": False,
            }

        now = time.time()
        cached = self.smart_metrics_cache.get(physical)

        if cached and (now - cached["timestamp"] < self.smart_metrics_cache_seconds):
            return cached["data"]

        
        
        # During fast startup, do not run smartctl here: this function is
        #      called once per disk and would otherwise block the GUI.
        if not allow_query:
            return {
                "reallocated": None,
                "pending": None,
                "uncorrectable": None,
                "media_errors": None,
                "bad_total": None,
                "power_hours": None,
                "power_days": None,
                "health": "INCONNU",
                "temperature": None,
                "percentage_used": None,
                "wear_percent": None,
                "wear_source": "",
                "index_kind": "wear",
                "disk_kind": "",
                "tb_written": None,
                "tbw_rating": None,
                "tbw_used_percent": None,
                "tbw_remaining_percent": None,
                "available": False,
            }

        data = smart_usage_metrics(physical)
        self.smart_metrics_cache[physical] = {
            "timestamp": now,
            "data": data,
        }
        return data

    
    # Fills a Treeview with array members and their hardware/SMART information.
    def populate_member_tree(self, tree, array_path, members=None, allow_smart_query=True):
        
        current_key = self._current_tree_selection_key(tree)

        if tree is self.member_tree and self.selected_member_key:
            current_key = self.selected_member_key
        elif (
            hasattr(self, "manage_member_tree")
            and tree is self.manage_member_tree
            and self.selected_manage_member_key
        ):
            current_key = self.selected_manage_member_key

        tree.delete(*tree.get_children())

        if members is None:
            members, _ = parse_mdadm_members(array_path)

        selected_item = None

        for m in members:
            dev = m.get("device") or ""
            info = physical_disk_info(dev) if dev else {}
            size = self.human_size(info.get("size", 0)) if info.get("size") else "—"
            model = info.get("model") or "INCONNU"
            serial = info.get("serial") or "INCONNU"
            physical = info.get("physical_path") or dev

            smart = self.get_cached_smart_metrics(physical, allow_query=allow_smart_query) if dev else {}
            bad_total = smart.get("bad_total")
            reallocated = smart.get("reallocated")
            pending = smart.get("pending")
            uncorrectable = smart.get("uncorrectable")
            power_hours = smart.get("power_hours")
            power_days = smart.get("power_days")

            if bad_total is None:
                bad_display = "—"
            else:
                bad_display = str(bad_total)

            if isinstance(power_hours, int) and power_days is not None:
                usage_display = f"{power_hours:,} h / {power_days:,.1f} {'d' if CURRENT_LANGUAGE == 'en' else 'j'}".replace(",", " ")
            else:
                usage_display = "—"

            display_dev = dev if dev else "(disque retiré/manquant)"
            if dev and physical and physical != dev:
                display_dev = f"{dev}  [{physical}]"

            tag = "problem" if m.get("problem") else ("warning" if m.get("warning") else "ok")

            
            if tag == "ok" and isinstance(bad_total, int) and bad_total > 0:
                tag = "warning"

            if not dev:
                tag = "removed"

            item = tree.insert(
                "", "end",
                values=(
                    display_dev,
                    m.get("slot", "?"),
                    m.get("state", "?"),
                    size,
                    model,
                    serial,
                    (f"{smart.get('temperature')} °C" if smart.get("temperature") is not None else "—"),
                    bad_display,
                    usage_display,
                ),
                tags=(tag,)
            )

            values = tree.item(item, "values")
            key = self._member_key_from_values(values)
            if current_key and key == current_key:
                selected_item = item

        
        if selected_item:
            tree.selection_set(selected_item)
            tree.focus(selected_item)
            tree.see(selected_item)

    
    # Callback when the user selects an array on the Dashboard.
    def on_array_select(self, _event=None):
        sel = self.arr_list.curselection()
        if not sel:
            return
        raw = self.arr_list.get(sel[0])
        m = re.search(r"(/dev/md\d+)", raw)
        if not m:
            return
        path = m.group(1)
        self.selected_array.set(path)

        if hasattr(self, "manage_array"):
            self.manage_array.set(path)

        self.selected_member_key = None
        if hasattr(self, "selected_manage_member_key"):
            self.selected_manage_member_key = None

        self.refresh_array_view(path)

        if hasattr(self, "manage_array") and hasattr(self, "manage_member_tree"):
            self.refresh_manage_members(path)

    
    # Callback when the user selects an array in Manage RAID.
    def on_manage_array_select(self, _event=None):
        path = self.manage_array.get().strip()
        if not path:
            return
        self.selected_array.set(path)
        self.selected_member_key = None
        self.selected_manage_member_key = None
        self.refresh_manage_members(path)

    
    # Reloads members of the array currently being managed.
    def refresh_manage_members(self, path=None):
        path = (path or self.manage_array.get()).strip()
        if not path:
            return
        members, _ = parse_mdadm_members(path)
        self.populate_member_tree(self.manage_member_tree, path, members)

    
    # Converts the selected Treeview row into usable member information.
    def selected_member_from_tree(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        values = tree.item(sel[0], "values")
        if not values:
            return None
        dev = str(values[0])
        if "  [/dev/" in dev:
            dev = dev.split("  [", 1)[0].strip()
        dev = clean_device_path(dev) if not dev.startswith("(") else ""
        return {
            "device": dev,
            "slot": str(values[1]),
            "state": str(values[2]),
            "size": str(values[3]),
            "model": str(values[4]),
            "serial": str(values[5]),
        }

    
    # Returns the member currently selected in the relevant view.
    def get_selected_member(self):
        
        member = self.selected_member_from_tree(self.manage_member_tree)
        if member:
            return member
        return self.selected_member_from_tree(self.member_tree)

    
    # Updates buttons/information when a member is selected on the Dashboard.
    def on_member_select(self, _event=None):
        member = self.selected_member_from_tree(self.member_tree)
        if not member:
            self.selected_member_var.set("Aucun disque sélectionné")
            return

        self.selected_member_key = self._current_tree_selection_key(self.member_tree)

        dev = member["device"] or "(retiré/manquant)"
        self.selected_member_var.set(
            f"Sélection : {dev}    Slot {member['slot']}    État : {member['state']}"
        )

        
        path = self.selected_array.get().strip()
        if path:
            self.manage_array.set(path)
            self.refresh_manage_members(path)

            target_key = self.selected_member_key
            for item in self.manage_member_tree.get_children():
                vals = self.manage_member_tree.item(item, "values")
                if self._member_key_from_values(vals) == target_key:
                    self.manage_member_tree.selection_set(item)
                    self.manage_member_tree.focus(item)
                    self.manage_member_tree.see(item)
                    self.selected_manage_member_key = target_key
                    break

    
    # Updates action state when a member is selected in Manage RAID.
    def on_manage_member_select(self, _event=None):
        member = self.selected_member_from_tree(self.manage_member_tree)
        if member:
            self.selected_manage_member_key = self._current_tree_selection_key(self.manage_member_tree)

            dev = member["device"] or "(retiré/manquant)"
            self.set_status(
                f"Disque sélectionné : {dev} // {member['state']} // slot {member['slot']}"
            )

    
    # Shows detailed mdadm output for the array selected on the Dashboard.
    def dashboard_details(self):
        path = self.selected_array.get().strip()
        if path:
            self.run_async(["mdadm", "--detail", path], self.detail_text)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Rebuilds the full disk inventory and updates the Disks tab.
    def refresh_disks(self, allow_smart_query=True):
        devices = get_block_devices()
        membership = get_raid_membership_map()

        
        old_selected_path = ""
        sel = self.disk_tree.selection()
        if sel:
            vals = self.disk_tree.item(sel[0], "values")
            if vals:
                old_selected_path = str(vals[0])

        self.disk_tree.delete(*self.disk_tree.get_children())
        selected_item = None

        for d in devices:
            if d.get("type") != "disk":
                continue

            path = clean_device_path(d.get("path", ""))
            if not path:
                continue

            size = d.get("size") or 0
            try:
                size_txt = self.human_size(int(size))
            except Exception:
                size_txt = str(size)

            
            raid_entries = membership.get(path, [])

            if raid_entries:
                raid_txt = ", ".join(sorted(set(x["array"] for x in raid_entries)))
                member_txt = ", ".join(sorted(set(x["member"] for x in raid_entries)))
                state_txt = " | ".join(
                    f'{x["state"]} (slot {x["slot"]})'
                    for x in raid_entries
                )
            else:
                raid_txt = "—"
                member_txt = "—"
                state_txt = "—"

            # ---------- SMART ----------
            metrics = self.get_cached_smart_metrics(path, allow_query=allow_smart_query)
            health = metrics.get("health", "INCONNU")

            bad = metrics.get("bad_total")
            bad_txt = "—" if bad is None else str(bad)

            hours = metrics.get("power_hours")
            days = metrics.get("power_days")
            if isinstance(hours, int) and days is not None:
                usage_txt = f"{hours:,} h / {days:,.1f} {'d' if CURRENT_LANGUAGE == 'en' else 'j'}".replace(",", " ")
            else:
                usage_txt = "—"

            wear = metrics.get("wear_percent")
            wear_source = metrics.get("wear_source") or ""
            index_kind = metrics.get("index_kind") or "wear"
            if wear is None:
                wear_txt = "—"
            elif index_kind == "risk":
                wear_txt = f"Risque {wear:.1f}%"
            else:
                wear_txt = f"Usure {wear:.1f}%"

            # ---------- Filesystem / mount ----------
            mounts = d.get("mountpoints") or []
            mounttxt = (
                ", ".join([m for m in mounts if m])
                if isinstance(mounts, list)
                else str(mounts or "")
            )
            fstype = d.get("fstype", "") or ""

            
            child_fs = []
            child_mounts = []
            for child in d.get("children") or []:
                cfs = child.get("fstype") or ""
                cpath = child.get("path") or child.get("name") or ""
                cmounts = child.get("mountpoints") or []

                if cfs:
                    child_fs.append(f"{cpath}:{cfs}")

                if isinstance(cmounts, list):
                    for mnt in cmounts:
                        if mnt:
                            child_mounts.append(f"{cpath}:{mnt}")

            if not fstype and child_fs:
                fstype = " | ".join(child_fs)

            if not mounttxt and child_mounts:
                mounttxt = " | ".join(child_mounts)

            
            tag = "ok"

            if any(x.get("problem") for x in raid_entries):
                tag = "problem"
            elif health == "ÉCHEC":
                tag = "problem"
            elif health == "ATTENTION":
                tag = "warning"
            elif any(x.get("warning") for x in raid_entries):
                tag = "warning"
            elif isinstance(bad, int) and bad > 0:
                tag = "warning"
            elif (
                isinstance(wear, (int, float))
                and metrics.get("index_kind") == "risk"
                and wear >= 60
            ):
                tag = "warning"
            elif (
                isinstance(wear, (int, float))
                and metrics.get("index_kind") != "risk"
                and wear >= 80
            ):
                tag = "warning"

            item = self.disk_tree.insert(
                "", "end",
                values=(
                    path,
                    size_txt,
                    d.get("model", "") or "",
                    d.get("serial", "") or "",
                    (f"{metrics.get('temperature')} °C" if metrics.get("temperature") is not None else "—"),
                    raid_txt,
                    member_txt,
                    state_txt,
                    health,
                    bad_txt,
                    usage_txt,
                    wear_txt,
                    fstype,
                    mounttxt,
                ),
                tags=(tag,)
            )

            if old_selected_path and path == old_selected_path:
                selected_item = item

        if selected_item:
            self.disk_tree.selection_set(selected_item)
            self.disk_tree.focus(selected_item)
            self.disk_tree.see(selected_item)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Refreshes disks usable by the legacy creation screen.
    def refresh_create_disks(self):
        
        if not hasattr(self, "create_disks"):
            return

        devices = get_block_devices()
        try:
            self.create_disks.delete(0, "end")
        except Exception:
            return

        membership = get_raid_membership_map()

        for d in devices:
            if d.get("type") != "disk":
                continue

            path = clean_device_path(d.get("path", ""))
            if not path:
                continue

            try:
                size = self.human_size(int(d.get("size") or 0))
            except Exception:
                size = "—"

            model = d.get("model") or ""
            serial = d.get("serial") or ""
            raids = membership.get(path, [])
            raid_txt = ",".join(sorted({x.get("array", "") for x in raids if x.get("array")}))

            flags = []
            if raid_txt:
                flags.append(f"RAID={raid_txt}")

            for child in d.get("children") or []:
                if child.get("fstype"):
                    flags.append(f"FS={child.get('fstype')}")
                mounts = child.get("mountpoints") or []
                if isinstance(mounts, list) and any(mounts):
                    flags.append("MONTÉ")

            suffix = f" [{' '.join(flags)}]" if flags else " [DISPONIBLE]"
            self.create_disks.insert(
                "end",
                f"{path:<12} {size:<10} {model:<24} {serial}{suffix}"
            )

    @staticmethod
    
    # Converts a byte count into a human-readable size (GiB/TiB).
    def human_size(n):
        units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
        x = float(n)
        for u in units:
            if x < 1024 or u == units[-1]:
                return f"{x:.1f} {u}"
            x /= 1024.0

    
    # Returns paths selected in the main creation screen.
    def selected_create_paths(self):
        paths = []
        for idx in self.create_disks.curselection():
            line = self.create_disks.get(idx)
            paths.append(line.split()[0])
        return paths

    
    # Builds the mdadm creation command from main-screen selections.
    def build_create_cmd(self):
        name = self.create_name.get().strip()
        if not re.fullmatch(r"md\d+", name):
            raise ValueError("Le nom doit être du type md20.")
        level = self.create_level.get().strip()
        disks = self.selected_create_paths()
        if len(disks) < 2:
            raise ValueError("Sélectionne au moins deux disques.")

        protected = []
        for dev in disks:
            memberships = raid_protection_memberships(dev)
            if memberships:
                arrays = ", ".join(sorted({
                    e.get("array", "") for e in memberships if e.get("array")
                }))
                protected.append(f"{dev} → {arrays or 'RAID existant'}")

        if protected:
            raise ValueError(
                "PROTECTION RAID : création bloquée.\n"
                "Les périphériques suivants appartiennent déjà à un RAID :\n"
                + "\n".join(protected)
            )

        protected_fstab = []
        for dev in disks:
            entries = fstab_protection_entries(dev)
            if entries:
                targets = ", ".join(sorted({
                    e.get("target", "") for e in entries if e.get("target")
                }))
                protected_fstab.append(
                    f"{dev} → {targets or '/etc/fstab'}"
                )

        if protected_fstab:
            raise ValueError(
                "PROTECTION FSTAB : création bloquée.\n"
                "Les périphériques suivants sont référencés dans /etc/fstab :\n"
                + "\n".join(protected_fstab)
            )

        min_by_level = {
            "raid0": 2,
            "raid1": 2,
            "raid5": 3,
            "raid6": 4,
            "raid10": 4,
        }
        if len(disks) < min_by_level.get(level, 2):
            raise ValueError(f"{level} nécessite au moins {min_by_level[level]} disques.")

        cmd = [
            "mdadm", "--create", f"/dev/{name}",
            "--verbose",
            "--level", level.replace("raid", ""),
            "--raid-devices", str(len(disks)),
            "--metadata", self.create_meta.get(),
            "--chunk", self.create_chunk.get(),
        ]
        if self.create_bitmap.get() and level != "raid0":
            cmd += ["--bitmap=internal"]
        cmd += disks
        return cmd

    
    # Shows the creation command before any write occurs.
    def preview_create(self):
        try:
            cmd = self.build_create_cmd()
        except Exception as exc:
            messagebox.showerror("Création", str(exc))
            return
        messagebox.showinfo("Commande mdadm", shell_join(cmd))

    
    # Performs final safety validation and starts array creation.
    def create_array(self):
        try:
            cmd = self.build_create_cmd()
        except Exception as exc:
            messagebox.showerror("Création", str(exc))
            return

        name = self.create_name.get().strip()
        disks = self.selected_create_paths()

        text = (
            "Cette opération va CRÉER un nouveau RAID et écrire des métadonnées "
            "sur les disques suivants :\n\n"
            + "\n".join(disks)
            + "\n\nCommande :\n"
            + shell_join(cmd)
        )

        dlg = ConfirmDialog(self, "Création RAID", text, confirm_token=name)
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(cmd, self.manage_output, privileged=True, timeout=600)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Returns the path of the array currently selected in Manage RAID.
    def current_manage_array(self):
        p = self.manage_array.get().strip() or self.selected_array.get().strip()
        if not p:
            messagebox.showerror("Gestion", "Aucun array sélectionné.")
            return None
        return p

    
    # Displays 'mdadm --detail' for the selected array.
    def manage_details(self):
        p = self.current_manage_array()
        if p:
            self.run_async(["mdadm", "--detail", p], self.manage_output)

    
    # Attempts to assemble the selected array.
    def manage_assemble(self):
        p = self.current_manage_array()
        if not p:
            return
        cmd = ["mdadm", "--assemble", "--run", p]
        if messagebox.askyesno("Assembler", f"Exécuter :\n{shell_join(cmd)} ?"):
            self.run_async(cmd, self.manage_output, privileged=True)

    
    # Stops an array safely after confirmation.
    def manage_stop(self):
        p = self.current_manage_array()
        if not p:
            return
        dlg = ConfirmDialog(
            self,
            "Arrêter l'array",
            f"Arrêter {p} ?\n\nAssure-toi qu'aucun système de fichiers n'est monté depuis cet array.",
            confirm_token=Path(p).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", "--stop", p], self.manage_output, privileged=True)

    
    # Starts an array consistency check.
    def manage_check(self):
        p = self.current_manage_array()
        if not p:
            return
        sync_action = f"/sys/block/{Path(p).name}/md/sync_action"
        cmd = ["sh", "-c", f"echo check > {shlex.quote(sync_action)}"]
        if messagebox.askyesno("Check RAID", f"Lancer une vérification sur {p} ?"):
            self.run_async(cmd, self.manage_output, privileged=True)

    
    # Starts a controlled repair/resync where supported by mdadm.
    def manage_repair(self):
        p = self.current_manage_array()
        if not p:
            return
        sync_action = f"/sys/block/{Path(p).name}/md/sync_action"
        cmd = ["sh", "-c", f"echo repair > {shlex.quote(sync_action)}"]
        dlg = ConfirmDialog(
            self,
            "Repair RAID",
            f"Lancer un repair sur {p} ?\n\nCette opération peut réécrire des blocs.",
            confirm_token=Path(p).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(cmd, self.manage_output, privileged=True)

    
    # Asks the user for a device path using a small dialog.
    def ask_device(self, title):
        value = simpledialog.askstring(title, "Périphérique (ex. /dev/sdb1 ou /dev/sdb) :", parent=self)
        if not value:
            return None
        value = value.strip()
        if not value.startswith("/dev/"):
            messagebox.showerror(title, "Le périphérique doit commencer par /dev/.")
            return None
        return value

    
    # Adds a device as member/spare after safety checks.
    def manage_add(self):
        p = self.current_manage_array()
        if not p:
            return
        dev = self.ask_device("Ajouter membre")
        if not dev:
            return
        cmd = ["mdadm", p, "--add", dev]
        if messagebox.askyesno("Ajouter membre", f"Exécuter :\n{shell_join(cmd)} ?"):
            self.run_async(cmd, self.manage_output, privileged=True, timeout=120)

    
    # Removes a member only when array state and confirmations allow it.
    def manage_remove(self):
        p = self.current_manage_array()
        if not p:
            return
        dev = self.ask_device("Retirer membre")
        if not dev:
            return
        dlg = ConfirmDialog(
            self,
            "Retirer membre",
            f"Retirer {dev} de {p} ?\n\nCommande :\nmdadm {p} --remove {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--remove", dev], self.manage_output, privileged=True)

    
    # Explicitly marks the selected member faulty after confirmation.
    def manage_faulty(self):
        p = self.current_manage_array()
        if not p:
            return
        dev = self.ask_device("Marquer faulty")
        if not dev:
            return
        dlg = ConfirmDialog(
            self,
            "Marquer faulty",
            f"Marquer {dev} comme défaillant dans {p} ?",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--fail", dev], self.manage_output, privileged=True)

    
    # Clears old mdadm metadata only after all safety checks and confirmations.
    def manage_zero_superblock(self):
        dev = self.ask_device("Zero superblock")
        if not dev:
            return

        protection = protected_raid_message(dev)
        if protection:
            messagebox.showerror(
                "PROTECTION RAID — OPÉRATION BLOQUÉE",
                protection,
                parent=self
            )
            return

        fstab_protection = protected_fstab_message(dev)
        if fstab_protection:
            messagebox.showerror(
                "PROTECTION FSTAB — OPÉRATION BLOQUÉE",
                fstab_protection,
                parent=self
            )
            return

        dlg = ConfirmDialog(
            self,
            "EFFACER SUPERBLOCK MD",
            f"Cette opération supprime les métadonnées mdadm de {dev}.\n\n"
            "Protection RAID : aucune appartenance RAID active détectée.\n\n"
            f"Commande : mdadm --zero-superblock {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            
            
            protection = protected_raid_message(dev)
            if protection:
                messagebox.showerror(
                    "PROTECTION RAID — ÉTAT MODIFIÉ",
                    protection,
                    parent=self
                )
                return

            fstab_protection = protected_fstab_message(dev)
            if fstab_protection:
                messagebox.showerror(
                    "PROTECTION FSTAB — ÉTAT MODIFIÉ",
                    fstab_protection,
                    parent=self
                )
                return

            self.run_async(
                ["mdadm", "--zero-superblock", dev],
                self.manage_output,
                privileged=True
            )

    
    # Opens SMART information for the currently selected member.
    def member_smart(self, _event=None):
        member = self.get_selected_member()
        if not member or not member.get("device"):
            messagebox.showinfo("SMART", "Sélectionne d'abord un disque membre valide.")
            return
        self.show_smart_for_path(member["device"])

    
    # Dashboard shortcut to mark the selected member faulty.
    def member_faulty(self):
        p = self.manage_array.get().strip() or self.selected_array.get().strip()
        member = self.get_selected_member()
        if not p or not member or not member.get("device"):
            messagebox.showinfo("FAULTY", "Sélectionne d'abord un disque membre du RAID.")
            return

        dev = member["device"]
        if "faulty" in member["state"].lower() or "failed" in member["state"].lower():
            messagebox.showinfo("FAULTY", f"{dev} est déjà indiqué comme défaillant.")
            return

        dlg = ConfirmDialog(
            self,
            "Marquer le disque FAULTY",
            f"Array : {p}\nDisque : {dev}\nÉtat actuel : {member['state']}\n\n"
            f"Commande :\nmdadm {p} --fail {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--fail", dev], self.manage_output, privileged=True)

    
    # Dashboard shortcut to remove the selected member.
    def member_remove(self):
        p = self.manage_array.get().strip() or self.selected_array.get().strip()
        member = self.get_selected_member()
        if not p or not member or not member.get("device"):
            messagebox.showinfo("Retirer", "Sélectionne d'abord un disque membre du RAID.")
            return

        dev = member["device"]
        low = member["state"].lower()
        if "active" in low and "faulty" not in low and "failed" not in low:
            messagebox.showwarning(
                "Retirer",
                f"{dev} semble encore ACTIF.\n\n"
                "Marque-le d'abord FAULTY avant de le retirer, sauf si tu sais exactement ce que tu fais."
            )
            return

        dlg = ConfirmDialog(
            self,
            "Retirer le disque du RAID",
            f"Array : {p}\nDisque : {dev}\nÉtat : {member['state']}\n\n"
            f"Commande :\nmdadm {p} --remove {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--remove", dev], self.manage_output, privileged=True)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Collects and displays detailed SMART information for a /dev path.
    def show_smart_for_path(self, path):
        if not shutil.which("smartctl"):
            messagebox.showerror(
                "SMART",
                "smartctl n'est pas installé.\nInstalle smartmontools."
            )
            return

        member = clean_device_path(path)
        smart_path, error = resolve_smart_device(member)

        if error:
            messagebox.showerror(
                "SMART — périphérique introuvable",
                f"Membre RAID : {member or path}\n\n{error}\n\n"
                "La liste des RAID va être rafraîchie."
            )
            self.refresh_all()
            return

        
        info = physical_disk_info(member)
        model = (info.get("model") or "INCONNU").strip()
        serial = (info.get("serial") or "INCONNU").strip()

        metrics = smart_usage_metrics(smart_path)
        bad_total = metrics.get("bad_total")
        reallocated = metrics.get("reallocated")
        pending = metrics.get("pending")
        uncorrectable = metrics.get("uncorrectable")
        media_errors = metrics.get("media_errors")
        power_hours = metrics.get("power_hours")
        power_days = metrics.get("power_days")
        temperature = metrics.get("temperature")
        percentage_used = metrics.get("percentage_used")
        wear_percent = metrics.get("wear_percent")
        wear_source = metrics.get("wear_source") or ""
        index_kind = metrics.get("index_kind") or "wear"
        disk_kind = metrics.get("disk_kind") or "INCONNU"
        tb_written = metrics.get("tb_written")
        tbw_rating = metrics.get("tbw_rating")
        tbw_used = metrics.get("tbw_used_percent")
        tbw_remaining = metrics.get("tbw_remaining_percent")
        temperature_min = metrics.get("temperature_min")
        temperature_max = metrics.get("temperature_max")
        power_cycle_count = metrics.get("power_cycle_count")
        start_stop_count = metrics.get("start_stop_count")
        load_cycle_count = metrics.get("load_cycle_count")
        spin_retry_count = metrics.get("spin_retry_count")
        reported_uncorrectable = metrics.get("reported_uncorrectable")
        command_timeout = metrics.get("command_timeout")
        udma_crc_errors = metrics.get("udma_crc_errors")
        total_lbas_written = metrics.get("total_lbas_written")
        total_lbas_read = metrics.get("total_lbas_read")
        smart_health = metrics.get("health", "INCONNU")

        def metric(v):
            return "—" if v is None else str(v)

        if isinstance(power_hours, int) and power_days is not None:
            usage_text = (f"{power_hours:,} hours / {power_days:,.1f} days" if CURRENT_LANGUAGE == "en" else f"{power_hours:,} heures / {power_days:,.1f} jours").replace(",", " ")
        else:
            usage_text = "—"

        
        
        smart_path = clean_device_path(smart_path)
        if not smart_path or not Path(smart_path).exists():
            messagebox.showerror(
                "SMART — sécurité",
                f"Le périphérique résolu n'existe pas : {smart_path or '(vide)'}"
            )
            self.refresh_all()
            return

        win = tk.Toplevel(self)
        win.title(f"SMART - {smart_path}")
        win.geometry("980x680")
        win.transient(self)
        win.lift()

        header = ttk.Frame(win)
        header.pack(fill="x", padx=8, pady=8)

        
        
        # Some fields do not apply to every drive type. Show an explanation
        #      instead of an ambiguous dash.
        
        # Bilingual SMART display strings.
        is_en = CURRENT_LANGUAGE == "en"

        if disk_kind == "HDD":
            nvme_wear_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
            tb_written_text = (
                f"{tb_written:.2f} TB"
                if tb_written is not None
                else ("Not reported by SMART on this HDD" if is_en else "Non fourni par SMART sur ce HDD")
            )
            endurance_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
            tbw_used_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
            tbw_remaining_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
        else:
            nvme_wear_text = (
                f"{percentage_used} %"
                if percentage_used is not None
                else (
                    "Not reported" if (is_en and disk_kind == "NVMe")
                    else "Not applicable" if is_en
                    else "Non fourni" if disk_kind == "NVMe"
                    else "Non applicable"
                )
            )
            tb_written_text = (
                f"{tb_written:.2f} TB"
                if tb_written is not None
                else ("Not reported by SMART" if is_en else "Non fourni par SMART")
            )
            endurance_text = (
                f"{tbw_rating:.0f} TBW"
                if tbw_rating is not None
                else ("Manufacturer rating unknown" if is_en else "Valeur constructeur inconnue")
            )
            tbw_used_text = (
                f"{tbw_used:.2f}%"
                if tbw_used is not None
                else (
                    "Cannot calculate without manufacturer TBW"
                    if is_en
                    else "Calcul impossible sans TBW constructeur"
                )
            )
            tbw_remaining_text = (
                f"{tbw_remaining:.2f}%"
                if tbw_remaining is not None
                else (
                    "Cannot calculate without manufacturer TBW"
                    if is_en
                    else "Calcul impossible sans TBW constructeur"
                )
            )

        
        # Additional SMART information actually reported by the drive.
        extra_lines = []

        def add_extra(fr_label, en_label, value):
            if value is not None:
                extra_lines.append(f"{en_label if is_en else fr_label}: {value}")

        add_extra("Cycles alimentation", "Power cycles", power_cycle_count)
        add_extra("Cycles démarrage/arrêt", "Start/stop cycles", start_stop_count)
        add_extra("Cycles chargement/déchargement", "Load/unload cycles", load_cycle_count)
        add_extra("Tentatives de rotation", "Spin retry count", spin_retry_count)
        add_extra("Non corrigibles signalés", "Reported uncorrectable", reported_uncorrectable)
        add_extra("Timeout commandes", "Command timeouts", command_timeout)
        add_extra("Erreurs CRC UDMA", "UDMA CRC errors", udma_crc_errors)
        add_extra("Total LBA écrits", "Total LBAs written", total_lbas_written)
        add_extra("Total LBA lus", "Total LBAs read", total_lbas_read)

        if temperature_min is not None or temperature_max is not None:
            lo = "—" if temperature_min is None else temperature_min
            hi = "—" if temperature_max is None else temperature_max
            extra_lines.append(
                f"{'Temperature min/max' if is_en else 'Température min/max'}: {lo}/{hi} °C"
            )

        extra_text = ""
        if extra_lines:
            extra_text = (
                "\n\n"
                + ("AVAILABLE SMART DETAILS" if is_en else "DÉTAILS SMART DISPONIBLES")
                + "\n"
                + "\n".join(extra_lines)
            )

        if is_en:
            smart_text = (
                f"RAID MEMBER: {member}\n"
                f"PHYSICAL DISK: {smart_path}\n"
                f"MODEL: {model}\n"
                f"SERIAL NO.: {serial}\n"
                f"SMART: {smart_health}\n"
                f"ERRORS / SECTORS: {metric(bad_total)} "
                f"(reallocated {metric(reallocated)}, pending {metric(pending)}, "
                f"uncorrectable {metric(uncorrectable)}, NVMe media {metric(media_errors)})\n"
                f"USAGE: {usage_text}\n"
                f"TEMPERATURE: {metric(temperature)} °C    "
                f"NVMe WEAR: {nvme_wear_text}\n"
                f"TYPE: {disk_kind}\n"
                f"{'HDD RISK INDEX' if index_kind == 'risk' else 'SMART WEAR'}: "
                f"{'—' if wear_percent is None else f'{wear_percent:.1f}%'}\n"
                f"SOURCE: {wear_source or 'Unavailable'}\n"
                f"TB WRITTEN: {tb_written_text}\n"
                f"ENDURANCE: {endurance_text}\n"
                f"TBW USED: {tbw_used_text}\n"
                f"TBW REMAINING: {tbw_remaining_text}\n"
                f"NOTE: "
                f"{'Statistical monitoring index, not remaining drive life.' if index_kind == 'risk' else 'SMART/manufacturer endurance value when available.'}"
                f"{extra_text}"
            )
        else:
            smart_text = (
                f"MEMBRE RAID : {member}\n"
                f"DISQUE PHYSIQUE : {smart_path}\n"
                f"MODÈLE : {model}\n"
                f"N° SÉRIE : {serial}\n"
                f"SMART : {smart_health}\n"
                f"ERREURS / SECTEURS : {metric(bad_total)} "
                f"(réalloués {metric(reallocated)}, en attente {metric(pending)}, "
                f"non corrigibles {metric(uncorrectable)}, média NVMe {metric(media_errors)})\n"
                f"UTILISATION : {usage_text}\n"
                f"TEMPÉRATURE : {metric(temperature)} °C    "
                f"USURE NVMe : {nvme_wear_text}\n"
                f"TYPE : {disk_kind}\n"
                f"{'INDICE DE RISQUE HDD' if index_kind == 'risk' else 'USURE SMART'} : "
                f"{'—' if wear_percent is None else f'{wear_percent:.1f}%'}\n"
                f"SOURCE : {wear_source or 'Non disponible'}\n"
                f"TB ÉCRITS : {tb_written_text}\n"
                f"ENDURANCE : {endurance_text}\n"
                f"TBW UTILISÉ : {tbw_used_text}\n"
                f"TBW RESTANT : {tbw_remaining_text}\n"
                f"NOTE : "
                f"{'Indice statistique de surveillance, pas une durée de vie restante.' if index_kind == 'risk' else 'Valeur SMART/endurance constructeur lorsqu’elle est disponible.'}"
                f"{extra_text}"
            )

        ttk.Label(
            header,
            text=smart_text,
            justify="left",
            font=("TkFixedFont", 10, "bold")
        ).pack(anchor="w")

        txt = tk.Text(win, wrap="none", font=("TkFixedFont", 10))
        txt.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.apply_matrix_widgets()

        
        
        self.run_async(
            ["smartctl", "-a", smart_path],
            txt,
            privileged=True,
            timeout=60,
            show_error_popup=False,
            refresh_after=False
        )


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Replacement workflow: validates old member, proposes a new disk, and prepares the mdadm sequence.
    def replace_selected_member(self):








        array_path = self.manage_array.get().strip() or self.selected_array.get().strip()
        member = self.get_selected_member()

        if not array_path:
            messagebox.showinfo("Remplacement", "Sélectionne d'abord un RAID.")
            return
        if not member:
            messagebox.showinfo("Remplacement", "Sélectionne le disque à remplacer.")
            return

        old_dev = member.get("device") or ""
        old_state = member.get("state") or "unknown"
        old_slot = member.get("slot") or "?"

        current_members, _ = parse_mdadm_members(array_path)
        member_paths = [m.get("device") for m in current_members if m.get("device")]
        candidates = get_candidate_replacement_devices(exclude=member_paths)

        if not candidates:
            messagebox.showwarning(
                "Remplacement",
                "Aucun autre disque ou partition candidat n'a été détecté."
            )
            return

        win = tk.Toplevel(self)
        win.title(f"Remplacer un disque — {array_path}")
        win.geometry("840x560")
        win.transient(self)
        win.grab_set()
        win.configure(bg="#020802")

        outer = ttk.Frame(win)
        outer.pack(fill="both", expand=True, padx=12, pady=12)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        old_label = old_dev if old_dev else f"(membre manquant, slot {old_slot})"
        ttk.Label(
            outer,
            text="ASSISTANT DE REMPLACEMENT DE DISQUE",
            font=("TkFixedFont", 13, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        ttk.Label(
            outer,
            text=(
                f"RAID : {array_path}\n"
                f"Ancien membre : {old_label}\n"
                f"Slot : {old_slot}\n"
                f"État : {old_state}"
            ),
            font=("TkFixedFont", 10)
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        ttk.Label(
            outer,
            text="Choisis le nouveau périphérique :",
            font=("TkFixedFont", 10, "bold")
        ).grid(row=2, column=0, sticky="w")

        cols = ("path", "type", "size", "model", "status")
        tree = ttk.Treeview(outer, columns=cols, show="headings")
        for col, title, width in [
            ("path", "Périphérique", 150),
            ("type", "Type", 70),
            ("size", "Taille", 100),
            ("model", "Modèle", 250),
            ("status", "Attention", 190),
        ]:
            tree.heading(col, text=title)
            tree.column(col, width=width, anchor="w")
        tree.grid(row=3, column=0, sticky="nsew", pady=8)

        for c in candidates:
            status = []
            if c["mounted"]:
                status.append("MONTÉ")
            if c["fstype"]:
                status.append(f"FS={c['fstype']}")
            if not status:
                status.append("libre/non monté")
            tag = "problem" if c["mounted"] else ("warning" if c["fstype"] else "ok")
            tree.insert(
                "", "end",
                values=(
                    c["path"],
                    c["type"],
                    self.human_size(c["size"]),
                    c["model"] or "—",
                    ", ".join(status)
                ),
                tags=(tag,)
            )
        tree.tag_configure("ok", foreground="#00ff66")
        tree.tag_configure("warning", foreground="#ffb000")
        tree.tag_configure("problem", foreground="#ff3b3b")

        info = ttk.Label(
            outer,
            text=(
                "Le nouveau périphérique doit être préparé correctement. "
                "S'il est monté ou contient un système de fichiers, l'opération sera bloquée."
            ),
            wraplength=780
        )
        info.grid(row=4, column=0, sticky="w", pady=(2, 8))

        buttons = ttk.Frame(outer)
        buttons.grid(row=5, column=0, sticky="ew")
        buttons.columnconfigure(0, weight=1)

        def execute_replace():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Remplacement", "Sélectionne le nouveau périphérique.", parent=win)
                return

            vals = tree.item(sel[0], "values")
            new_dev = str(vals[0])
            cand = next((c for c in candidates if c["path"] == new_dev), None)
            if not cand:
                return

            if cand["mounted"]:
                messagebox.showerror(
                    "Remplacement",
                    f"{new_dev} est monté. Démonte-le avant de continuer.",
                    parent=win
                )
                return

            if cand["fstype"]:
                if not messagebox.askyesno(
                    "Périphérique contenant des données",
                    f"{new_dev} contient un système de fichiers ({cand['fstype']}).\n\n"
                    "mdadm peut écraser ses métadonnées. Continuer quand même ?",
                    parent=win
                ):
                    return

            commands = []
            low = old_state.lower()

            if old_dev:
                if "faulty" not in low and "failed" not in low:
                    commands.append(["mdadm", array_path, "--fail", old_dev])
                commands.append(["mdadm", array_path, "--remove", old_dev])

            commands.append(["mdadm", array_path, "--add", new_dev])

            command_preview = "\n".join(shell_join(c) for c in commands)
            token = Path(new_dev).name

            dlg = ConfirmDialog(
                win,
                "CONFIRMER LE REMPLACEMENT",
                f"RAID : {array_path}\n"
                f"Ancien : {old_label}\n"
                f"Nouveau : {new_dev}\n\n"
                "Les commandes suivantes seront exécutées dans cet ordre :\n\n"
                f"{command_preview}\n\n"
                "Après l'ajout, mdadm devrait lancer automatiquement la reconstruction "
                "si le niveau RAID le permet.",
                confirm_token=token
            )
            win.wait_window(dlg)
            if not dlg.result:
                return

            win.destroy()
            self.run_replace_sequence(commands, array_path, old_label, new_dev)

        ttk.Button(buttons, text="Annuler", command=win.destroy).pack(side="right")
        ttk.Button(
            buttons,
            text="REMPLACER LE DISQUE",
            command=execute_replace
        ).pack(side="right", padx=(0, 8))

        self.apply_matrix_widgets()

    
    # Runs replacement commands sequentially and stops on the first failure.
    def run_replace_sequence(self, commands, array_path, old_label, new_dev):
        def worker():
            log = []
            success = True

            for cmd in commands:
                self.after(0, lambda c=cmd: self.set_status("Remplacement : " + shell_join(c)))
                rc, out = run(cmd, timeout=180)
                log.append(f"$ {shell_join(cmd)}\n{out}\n")
                if rc != 0:
                    success = False
                    break

            output = "\n".join(log)

            def done():
                self.manage_output.delete("1.0", "end")
                self.manage_output.insert("end", output)
                self.refresh_all()

                if success:
                    self.set_status(f"Remplacement lancé : {old_label} -> {new_dev}")
                    messagebox.showinfo(
                        "Remplacement",
                        f"Le nouveau disque {new_dev} a été ajouté à {array_path}.\n\n"
                        "Surveille la progression de reconstruction dans /proc/mdstat."
                    )
                else:
                    self.set_status("Erreur pendant le remplacement")
                    messagebox.showerror(
                        "Remplacement",
                        "Une commande a échoué. La séquence a été arrêtée.\n\n"
                        + output[-4000:]
                    )

            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    
    # Opens SMART information for the disk selected in Disks.
    def show_smart(self):
        sel = self.disk_tree.selection()
        if not sel:
            messagebox.showinfo("SMART", "Sélectionne un disque.")
            return
        path = self.disk_tree.item(sel[0], "values")[0]
        self.show_smart_for_path(path)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Loads /etc/mdadm/mdadm.conf into the text editor.
    def load_config(self):
        path = Path("/etc/mdadm/mdadm.conf")
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            self.config_text.delete("1.0", "end")
            self.config_text.insert("1.0", content)
            self.config_loaded_path = str(path)
            self.config_file_var.set(
                f"Fichier actuellement chargé : {path}  //  {len(content.splitlines())} lignes"
            )
            self.set_status(f"Configuration chargée : {path}")
            messagebox.showinfo(
                "mdadm.conf chargé",
                f"Configuration chargée avec succès.\n\n"
                f"Fichier : {path}\n"
                f"Nombre de lignes : {len(content.splitlines())}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Erreur de chargement",
                f"Impossible de charger {path}\n\n{exc}"
            )

    
    # Asks mdadm to scan arrays and places the result in the editor.
    def scan_config(self):
        rc, out = run(["mdadm", "--detail", "--scan"], timeout=30)
        if rc != 0:
            messagebox.showerror("Scan", out)
            return
        current = self.config_text.get("1.0", "end").strip()
        if current:
            current += "\n\n"
        self.config_text.delete("1.0", "end")
        self.config_text.insert("end", current + out.strip() + "\n")

    
    # Safely saves editor contents into mdadm.conf.
    def save_config(self):
        path = Path("/etc/mdadm/mdadm.conf")
        content = self.config_text.get("1.0", "end-1c")

        if not messagebox.askyesno(
            "Confirmer l'écriture",
            f"Le contenu affiché va être écrit dans :\n\n{path}\n\n"
            "Une copie de sécurité horodatée sera créée avant l'écriture.\n\nContinuer ?"
        ):
            return

        try:
            import datetime
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = Path(f"/etc/mdadm/mdadm.conf.backup-{stamp}")

            if path.exists():
                shutil.copy2(path, backup)

            if content and not content.endswith("\n"):
                content += "\n"
            path.write_text(content, encoding="utf-8")
            path.chmod(0o644)

            self.config_loaded_path = str(path)
            self.config_file_var.set(f"Fichier actuellement chargé : {path}")
            self.set_status(f"mdadm.conf sauvegardé : {path}")

            backup_text = str(backup) if backup.exists() else "Aucune"
            messagebox.showinfo(
                "Sauvegarde terminée",
                f"Configuration enregistrée.\n\n"
                f"Fichier : {path}\n"
                f"Copie de sécurité : {backup_text}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Erreur de sauvegarde",
                f"Impossible d'enregistrer {path}\n\n{exc}"
            )

    
    # Exports a copy of the configuration to a user-selected file.
    def export_config(self):
        content = self.config_text.get("1.0", "end-1c")

        filename = filedialog.asksaveasfilename(
            title="Sauvegarder une copie de mdadm.conf",
            initialfile="mdadm.conf",
            defaultextension=".conf",
            filetypes=[
                ("Configuration mdadm", "*.conf"),
                ("Tous les fichiers", "*.*"),
            ]
        )

        if not filename:
            self.set_status("Sauvegarde de copie annulée.")
            return

        try:
            out = Path(filename)
            if content and not content.endswith("\n"):
                content += "\n"
            out.write_text(content, encoding="utf-8")

            self.set_status(f"Copie sauvegardée : {out}")
            messagebox.showinfo(
                "Copie sauvegardée",
                f"La copie a été créée avec succès.\n\nEmplacement :\n{out}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Erreur de sauvegarde",
                f"Impossible de sauvegarder la copie.\n\n{exc}"
            )




# =============================================================================
# MODULE 9 — STARTUP AND DEPENDENCIES
# =============================================================================


# Checks at startup that required system commands are available.
def dependency_check():

    missing = []
    for exe in ("mdadm", "lsblk"):
        if not shutil.which(exe):
            missing.append(exe)
    return missing

def main():
        if os.geteuid() != 0:
            launched, method = relaunch_as_root()
            if launched:
                raise SystemExit(0)

            try:
                r = tk.Tk()
                r.withdraw()
                messagebox.showerror(
                    "Élévation ROOT impossible",
                    f"MDADM Manager v{APP_VERSION} n'a trouvé ni kdesu ni pkexec.\n\n"
                    "Installe au besoin :\n"
                    "sudo apt install kde-cli-tools pkexec"
                )
                r.destroy()
            except Exception:
                print("Impossible d'obtenir les privilèges root : kdesu/pkexec introuvable.")
            raise SystemExit(1)

        missing = dependency_check()

        try:
            app = MdadmManager()
        except Exception as exc:

            try:
                r = tk.Tk()
                r.withdraw()
                messagebox.showerror(
                    "Erreur au démarrage",
                    f"MDADM Manager v{APP_VERSION} n'a pas pu démarrer.\n\n{exc}"
                )
                r.destroy()
            except Exception:
                print(f"ERREUR AU DÉMARRAGE : {exc}")
            raise

        if missing:
            app.after(
                250,
                lambda: messagebox.showwarning(
                    "Dépendances",
                    "Commandes manquantes : " + ", ".join(missing)
                )
            )

        app.mainloop()

if __name__ == "__main__":
    main()
