"""RAID creation wizard for MDADM Manager."""

import re
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from . import APP_VERSION
from .i18n import tr, ui_text
from .system import run, shell_join
from .core import *  # noqa: F403,F401
from .gui_common import ConfirmDialog

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
