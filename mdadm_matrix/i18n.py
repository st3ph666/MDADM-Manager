"""Internationalization helpers for MDADM Manager."""

from pathlib import Path

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
