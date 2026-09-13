#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MDADM Manager - v1.32
Interface graphique de surveillance et configuration mdadm pour Linux/Debian.

Dépendances système recommandées :
    apt install mdadm smartmontools python3-tk kde-cli-tools pkexec

L'application fonctionne en root.
Si elle est lancée par double-clic comme utilisateur normal, elle se relance
avec une fenêtre graphique d'authentification KDE (kdesu), puis utilise
pkexec en solution de secours.
"""

import os
import sys
import re
import shlex
import shutil
import subprocess
import threading
import math
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path

APP_VERSION = "1.58"
APP_TITLE = f"MDADM Manager v{APP_VERSION} // MATRIX ROOT"



from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# MDADM MANAGER — ARCHITECTURE DU SCRIPT / SCRIPT ARCHITECTURE
# =============================================================================
#
# Ce fichier reste volontairement autonome (un seul .py), mais il est organisé
# en modules logiques clairement séparés afin de faciliter le développement,
# les revues GitHub et le travail à plusieurs.
#
# MODULE 1  — INTERNATIONALISATION / I18N
#   ui_text, language_config_path, load_language, save_language, tr
#
# MODULE 2  — COMMANDES SYSTÈME ET PRIVILÈGES
#   run, shell_join, privileged_cmd, find_kdesu, relaunch_as_root
#
# MODULE 3  — DÉTECTION RAID ET PÉRIPHÉRIQUES
#   get_md_arrays, get_block_devices, get_raid_membership_map,
#   clean_device_path, physical_disk_info, block_device_info,
#   parse_mdadm_members, get_candidate_replacement_devices,
#   get_array_mount_info
#
# MODULE 4  — SMART / SANTÉ DES DISQUES
#   resolve_smart_device, detect_disk_kind, hdd_risk_index,
#   samsung_870_evo_tbw_rating, total_lbas_written_to_tb,
#   smart_usage_metrics
#
# MODULE 5  — PROTECTIONS FSTAB / RAID / SUPERBLOCK
#   resolve_fstab_source, get_fstab_entries, device_family_paths,
#   fstab_protection_entries, protected_fstab_message,
#   raid_protection_memberships, protected_raid_message,
#   mdadm_examine_superblock, candidate_member_paths_for_cleanup,
#   safe_orphan_superblocks
#
# MODULE 6  — INFRASTRUCTURE INTERFACE GRAPHIQUE
#   install_tk_translation_hooks, ConfirmDialog
#
# MODULE 7  — ASSISTANT DE CRÉATION RAID
#   RaidCreationWizard
#
# MODULE 8  — APPLICATION PRINCIPALE
#   MdadmManager
#
# MODULE 9  — DÉMARRAGE ET DÉPENDANCES
#   dependency_check + bloc __main__
#
# RÈGLE DE SÉCURITÉ:
#   Toute opération destructive doit repasser par les protections RAID/FSTAB
#   immédiatement avant l'écriture effective sur le disque.
#
# =============================================================================



# =============================================================================
# GUIDE POUR PROGRAMMEUR DÉBUTANT / BEGINNER PROGRAMMER GUIDE
# =============================================================================
#
# FR — COMMENT LIRE CE FICHIER
# ----------------------------
# 1) Le programme est volontairement contenu dans UN SEUL fichier Python.
#    Il est toutefois divisé en 9 modules logiques clairement identifiés.
# 2) Les fonctions placées avant les classes sont surtout des OUTILS :
#    elles lisent Linux, mdadm, lsblk, SMART, fstab, etc.
# 3) RaidCreationWizard construit la fenêtre de création guidée d'un RAID.
# 4) MdadmManager est la fenêtre principale de l'application.
# 5) Les méthodes qui commencent par "_build_" construisent uniquement
#    des parties de l'interface graphique Tkinter.
# 6) Les méthodes qui commencent par "refresh_" relisent l'état du système
#    et mettent l'interface à jour.
# 7) Les méthodes "manage_*" exécutent les opérations mdadm sur un RAID.
# 8) Toute commande destructive doit être précédée des protections RAID/FSTAB.
#    NE PAS contourner ces vérifications lorsqu'on modifie le programme.
#
# EN — HOW TO READ THIS FILE
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
# FR:
#   fonction       = bloc de code réutilisable appelé avec nom(...)
#   méthode         = fonction appartenant à une classe (self représente l'objet)
#   classe          = modèle servant à construire une fenêtre/objet
#   dictionnaire    = structure clé -> valeur, ex. {"state": "clean"}
#   liste           = collection ordonnée, ex. ["/dev/sda", "/dev/sdb"]
#   callback        = fonction appelée par Tkinter après un clic/événement
#   thread          = travail exécuté en parallèle pour ne pas figer l'interface
#
# EN:
#   function        = reusable code block called with name(...)
#   method          = function owned by a class (self is the current object)
#   class           = blueprint used to build a window/object
#   dictionary      = key -> value structure, e.g. {"state": "clean"}
#   list            = ordered collection, e.g. ["/dev/sda", "/dev/sdb"]
#   callback        = function called by Tkinter after a click/event
#   thread          = parallel work used to keep the GUI responsive
#
# CONSEIL / TIP:
#   Pour suivre une action, partez du texte du bouton dans "_build_*", trouvez
#   son paramètre command=..., puis suivez la méthode appelée.
#   To trace an action, start from the button text in "_build_*", find its
#   command=... parameter, then follow the referenced method.
#
# =============================================================================

# =============================================================================
# MODULE 1 — INTERNATIONALISATION / MODULE 1 — INTERNATIONALIZATION
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
    "Gérer un RAID": "Manage RAID", "Disques": "Disks", "Vitesse des liens": "Link Speeds",
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
    "Périphérique": "Device", "Port ATA": "ATA Port", "Hôte": "Host",
    "Lien SATA": "SATA Link", "Interface": "Interface",
    "Partition membre": "Member partition",
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
    # v1.31 — traductions complètes des écrans principaux
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

    # v1.32 — éléments encore visibles en français dans Create RAID / Manage RAID
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
    "Réintégrer ancien membre": "Re-add previous member",
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

# BEGINNER: FR — Traduit un texte d'interface déjà construit du français vers l'anglais lorsque la langue active est English.
# BEGINNER: EN — Translates an already-built UI string from French to English when the active language is English.
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


# BEGINNER: FR — Retourne le chemin du petit fichier qui mémorise la langue choisie par l'utilisateur.
# BEGINNER: EN — Returns the path of the small file that remembers the user's selected language.
def language_config_path():
    base = Path.home() / ".config" / "mdadm-manager"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return base / "language.conf"


# BEGINNER: FR — Lit la langue sauvegardée; en cas d'erreur ou de valeur inconnue, le français est utilisé par défaut.
# BEGINNER: EN — Reads the saved language; on error or unknown value, French is used as the default.
def load_language():
    try:
        value = language_config_path().read_text(encoding="utf-8").strip().lower()
        if value in LANGUAGES:
            return value
    except Exception:
        pass
    return "fr"


# BEGINNER: FR — Enregistre le code de langue dans le dossier de configuration de l'utilisateur.
# BEGINNER: EN — Saves the language code in the user's configuration directory.
def save_language(code):
    if code not in LANGUAGES:
        return False
    try:
        language_config_path().write_text(code + "\n", encoding="utf-8")
        return True
    except Exception:
        return False


CURRENT_LANGUAGE = load_language()


# BEGINNER: FR — Point d'entrée principal des traductions par clé. Utiliser tr(...) pour les textes fixes de l'interface.
# BEGINNER: EN — Main key-based translation entry point. Use tr(...) for fixed GUI text.
def tr(key):
    value = I18N.get(CURRENT_LANGUAGE, I18N["fr"]).get(
        key,
        I18N["fr"].get(key, key)
    )
    return ui_text(value)

MDADM_CONF = "/etc/mdadm/mdadm.conf"



# =============================================================================
# MODULE 2 — COMMANDES SYSTÈME ET PRIVILÈGES / MODULE 2 — SYSTEM COMMANDS AND PRIVILEGES
# =============================================================================

# BEGINNER: FR — Exécute une commande système sans shell, capture stdout/stderr et protège l'application avec un délai maximal.
# BEGINNER: EN — Runs a system command without a shell, captures stdout/stderr, and protects the app with a timeout.
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


# BEGINNER: FR — Transforme une liste d'arguments en commande lisible/échappée, surtout pour kdesu.
# BEGINNER: EN — Turns an argument list into a safely quoted readable command, mainly for kdesu.
def shell_join(cmd):
    return " ".join(shlex.quote(str(x)) for x in cmd)


# BEGINNER: FR — Point central prévu pour préparer une commande nécessitant les privilèges root.
# BEGINNER: EN — Central hook intended to prepare a command that requires root privileges.
def privileged_cmd(cmd):
    return list(cmd)



# BEGINNER: FR — Cherche l'exécutable kdesu dans plusieurs emplacements possibles sous KDE.
# BEGINNER: EN — Looks for the kdesu executable in several possible KDE locations.
def find_kdesu():
    """Retourne le chemin de kdesu si disponible sur KDE/Debian."""
    candidates = [
        shutil.which("kdesu"),
        shutil.which("kdesudo"),
        "/usr/lib/x86_64-linux-gnu/libexec/kf6/kdesu",
        "/usr/lib/x86_64-linux-gnu/libexec/kf5/kdesu",
        "/usr/libexec/kf6/kdesu",
        "/usr/libexec/kf5/kdesu",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return ""


# BEGINNER: FR — Relance toute l'application en root avec kdesu, puis pkexec en secours.
# BEGINNER: EN — Relaunches the whole application as root through kdesu, with pkexec as fallback.
def relaunch_as_root():
    if os.geteuid() == 0:
        return True, "déjà root"

    script = str(Path(sys.argv[0]).resolve())
    args = [sys.executable, script] + sys.argv[1:]
    kdesu = find_kdesu()

    if kdesu:
        command = shell_join(args)
        try:
            subprocess.Popen([kdesu, "-c", command])
            return True, "kdesu"
        except Exception:
            pass

    pkexec = shutil.which("pkexec")
    if pkexec:
        try:
            subprocess.Popen([pkexec] + args)
            return True, "pkexec"
        except Exception:
            pass

    return False, ""

# NOTE: content continues exactly from the validated v1.58 working file generated from the user's uploaded v1.57.
