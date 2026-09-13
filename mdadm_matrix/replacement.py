"""Mécanisme sécurisé de réintégration et de remplacement des membres RAID."""

import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .core import (
    get_candidate_replacement_devices,
    parse_mdadm_members,
    physical_disk_info,
)
from .system import run, shell_join


def _valeur_champ(texte, nom):
    motif = rf"^\s*{re.escape(nom)}\s*:\s*(.+?)\s*$"
    trouve = re.search(motif, texte or "", re.MULTILINE | re.IGNORECASE)
    return trouve.group(1).strip() if trouve else ""


def _entier_champ(texte, nom):
    valeur = _valeur_champ(texte, nom)
    trouve = re.search(r"-?\d+", valeur)
    if not trouve:
        return None
    try:
        return int(trouve.group(0))
    except ValueError:
        return None


def _identite_array(array_path):
    rc, sortie = run(["mdadm", "--detail", array_path], timeout=15)
    return {
        "ok": rc == 0,
        "uuid": _valeur_champ(sortie, "UUID"),
        "events": _entier_champ(sortie, "Events"),
        "nom": _valeur_champ(sortie, "Name"),
        "sortie": sortie,
    }


def _examiner_membre(device):
    rc, sortie = run(["mdadm", "--examine", device], timeout=15)
    role = _valeur_champ(sortie, "Device Role")
    slot = None
    trouve = re.search(r"Active\s+device\s+(\d+)", role, re.IGNORECASE)
    if trouve:
        slot = trouve.group(1)

    return {
        "ok": rc == 0 and bool(_valeur_champ(sortie, "Array UUID")),
        "uuid": _valeur_champ(sortie, "Array UUID"),
        "device_uuid": _valeur_champ(sortie, "Device UUID"),
        "role": role,
        "slot": slot,
        "events": _entier_champ(sortie, "Events"),
        "etat": _valeur_champ(sortie, "State"),
        "nom": _valeur_champ(sortie, "Name"),
        "sortie": sortie,
    }


def _ecart_events(events_array, events_disque):
    if not isinstance(events_array, int) or not isinstance(events_disque, int):
        return None
    return events_array - events_disque


def _decrire_candidat(candidat, identite, slot_attendu):
    chemin = candidat["path"]
    examen = _examiner_membre(chemin)
    physique = physical_disk_info(chemin) or {}

    meme_uuid = bool(examen["uuid"] and examen["uuid"] == identite["uuid"])
    meme_slot = bool(slot_attendu not in ("", "?") and examen["slot"] == str(slot_attendu))
    ancien_exact = bool(meme_uuid and meme_slot)

    if ancien_exact:
        statut = "ANCIEN MEMBRE RETROUVÉ — réintégration possible"
        categorie = "ancien"
    elif meme_uuid:
        statut = f"Même RAID — ancien rôle {examen['role'] or 'inconnu'}"
        categorie = "meme_array"
    elif examen["ok"]:
        statut = "Métadonnées mdadm d'un autre RAID"
        categorie = "autre_array"
    elif candidat.get("mounted"):
        statut = "MONTÉ — opération bloquée"
        categorie = "bloque"
    elif candidat.get("fstype"):
        statut = f"FS={candidat['fstype']} — nouveau remplacement"
        categorie = "nouveau"
    else:
        statut = "Libre — nouveau remplacement"
        categorie = "nouveau"

    return {
        **candidat,
        "examen": examen,
        "physique": physique,
        "meme_uuid": meme_uuid,
        "meme_slot": meme_slot,
        "ancien_exact": ancien_exact,
        "categorie": categorie,
        "statut": statut,
        "ecart_events": _ecart_events(identite.get("events"), examen.get("events")),
    }


def _lancer_reintegration(self, array_path, candidat, identite, fenetre):
    device = candidat["path"]
    examen = candidat["examen"]
    physique = candidat.get("physique") or {}
    serial = physique.get("serial") or "INCONNU"
    modele = physique.get("model") or candidat.get("model") or "INCONNU"
    ecart = candidat.get("ecart_events")
    ecart_txt = "inconnu" if ecart is None else str(ecart)

    commande = ["mdadm", "--manage", array_path, "--re-add", device]
    texte = (
        f"RAID : {array_path}\n"
        f"Ancien membre : {device}\n"
        f"Disque physique : {physique.get('physical_path') or '—'}\n"
        f"Modèle : {modele}\n"
        f"N° série : {serial}\n"
        f"Array UUID : {examen.get('uuid') or '—'}\n"
        f"Ancien rôle : {examen.get('role') or '—'}\n"
        f"Events disque : {examen.get('events') if examen.get('events') is not None else '—'}\n"
        f"Events RAID : {identite.get('events') if identite.get('events') is not None else '—'}\n"
        f"Écart Events : {ecart_txt}\n\n"
        "Le superblock existant sera conservé. Le programme va d'abord tenter --re-add.\n\n"
        f"Commande :\n{shell_join(commande)}"
    )

    dlg = self.__class__.__mro__[1].__dict__.get("ConfirmDialog") if False else None
    from .gui_common import ConfirmDialog
    confirmation = ConfirmDialog(
        fenetre,
        "RÉINTÉGRER L'ANCIEN MEMBRE",
        texte,
        confirm_token=Path(device).name,
    )
    fenetre.wait_window(confirmation)
    if not confirmation.result:
        return

    fenetre.destroy()

    def travail():
        self.after(0, lambda: self.set_status("Réintégration : " + shell_join(commande)))
        rc, sortie = run(commande, timeout=180)

        def termine():
            self.manage_output.delete("1.0", "end")
            self.manage_output.insert("end", f"$ {shell_join(commande)}\n{sortie}\n")
            self.refresh_all()

            if rc == 0:
                self.set_status(f"Ancien membre réintégré : {device}")
                messagebox.showinfo(
                    "Réintégration réussie",
                    f"{device} a été réintégré dans {array_path}.\n\n"
                    "La reconstruction ou la remise à niveau des blocs peut maintenant être visible dans /proc/mdstat.",
                )
                return

            self.set_status("Échec de --re-add")
            if not messagebox.askyesno(
                "--re-add refusé",
                "mdadm a refusé la réintégration directe.\n\n"
                f"Sortie :\n{sortie[-2500:]}\n\n"
                "Le disque possède pourtant le même UUID et le même ancien slot.\n"
                "Veux-tu tenter un ajout normal (--add), ce qui peut provoquer une reconstruction complète ?",
            ):
                return

            commande_add = ["mdadm", "--manage", array_path, "--add", device]

            def travail_add():
                self.after(0, lambda: self.set_status("Ajout de secours : " + shell_join(commande_add)))
                rc2, sortie2 = run(commande_add, timeout=180)

                def termine_add():
                    self.manage_output.insert(
                        "end",
                        f"\n$ {shell_join(commande_add)}\n{sortie2}\n",
                    )
                    self.refresh_all()
                    if rc2 == 0:
                        self.set_status(f"Membre ajouté avec reconstruction : {device}")
                        messagebox.showinfo(
                            "Ajout lancé",
                            f"{device} a été ajouté à {array_path}.\n\n"
                            "Surveille la reconstruction dans /proc/mdstat.",
                        )
                    else:
                        self.set_status("Échec du remplacement")
                        messagebox.showerror(
                            "Échec du remplacement",
                            sortie2[-3500:] if sortie2 else f"Code {rc2}",
                        )

                self.after(0, termine_add)

            threading.Thread(target=travail_add, daemon=True).start()

        self.after(0, termine)

    threading.Thread(target=travail, daemon=True).start()


def _remplacer_selection(self):
    array_path = self.manage_array.get().strip() or self.selected_array.get().strip()
    member = self.get_selected_member()

    if not array_path:
        messagebox.showinfo("Remplacement", "Sélectionne d'abord un RAID.")
        return
    if not member:
        messagebox.showinfo("Remplacement", "Sélectionne le disque ou le slot à remplacer.")
        return

    old_dev = member.get("device") or ""
    old_state = member.get("state") or "unknown"
    old_slot = str(member.get("slot") or "?")

    identite = _identite_array(array_path)
    if not identite["ok"] or not identite["uuid"]:
        messagebox.showerror(
            "Remplacement",
            f"Impossible de lire l'identité mdadm de {array_path}.",
        )
        return

    current_members, _ = parse_mdadm_members(array_path)
    member_paths = [m.get("device") for m in current_members if m.get("device")]
    bruts = get_candidate_replacement_devices(exclude=member_paths)
    candidats = [_decrire_candidat(c, identite, old_slot) for c in bruts]

    if not candidats:
        messagebox.showwarning("Remplacement", "Aucun périphérique candidat détecté.")
        return

    candidats.sort(key=lambda c: (0 if c["ancien_exact"] else 1, c["path"]))

    win = tk.Toplevel(self)
    win.title(f"Réintégrer / remplacer — {array_path}")
    win.geometry("1120x620")
    win.transient(self)
    win.grab_set()
    win.configure(bg="#020802")

    outer = ttk.Frame(win)
    outer.pack(fill="both", expand=True, padx=12, pady=12)
    outer.columnconfigure(0, weight=1)
    outer.rowconfigure(3, weight=1)

    old_label = old_dev if old_dev else f"(membre retiré/manquant, slot {old_slot})"
    ttk.Label(
        outer,
        text="RÉINTÉGRATION / REMPLACEMENT D'UN MEMBRE RAID",
        font=("TkFixedFont", 13, "bold"),
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))

    ttk.Label(
        outer,
        text=(
            f"RAID : {array_path}    UUID : {identite['uuid']}\n"
            f"Membre ciblé : {old_label}    Slot : {old_slot}    État : {old_state}    "
            f"Events RAID : {identite.get('events') if identite.get('events') is not None else '—'}"
        ),
        font=("TkFixedFont", 10),
    ).grid(row=1, column=0, sticky="w", pady=(0, 8))

    ttk.Label(
        outer,
        text=(
            "Vert = ancien membre exact retrouvé. Dans ce cas, le programme conserve ses métadonnées "
            "et tente --re-add avant toute autre action."
        ),
        wraplength=1080,
    ).grid(row=2, column=0, sticky="w")

    colonnes = ("path", "physical", "model", "serial", "role", "events", "delta", "status")
    tree = ttk.Treeview(outer, columns=colonnes, show="headings")
    definitions = [
        ("path", "Périphérique", 120),
        ("physical", "Disque", 100),
        ("model", "Modèle", 190),
        ("serial", "N° série", 150),
        ("role", "Ancien rôle", 125),
        ("events", "Events", 80),
        ("delta", "Écart", 70),
        ("status", "Compatibilité", 285),
    ]
    for col, titre, largeur in definitions:
        tree.heading(col, text=titre)
        tree.column(col, width=largeur, anchor="w")
    tree.grid(row=3, column=0, sticky="nsew", pady=8)

    for c in candidats:
        info = c.get("physique") or {}
        examen = c.get("examen") or {}
        delta = c.get("ecart_events")
        tag = "ancien" if c["ancien_exact"] else (
            "bloque" if c["categorie"] in ("bloque", "autre_array") else "normal"
        )
        tree.insert(
            "",
            "end",
            values=(
                c["path"],
                info.get("physical_path") or "—",
                info.get("model") or c.get("model") or "—",
                info.get("serial") or "—",
                examen.get("role") or "—",
                examen.get("events") if examen.get("events") is not None else "—",
                delta if delta is not None else "—",
                c["statut"],
            ),
            tags=(tag,),
        )

    tree.tag_configure("ancien", foreground="#00ff66")
    tree.tag_configure("normal", foreground="#ffb000")
    tree.tag_configure("bloque", foreground="#ff3b3b")

    anciens = [c for c in candidats if c["ancien_exact"]]
    if len(anciens) == 1:
        for item in tree.get_children():
            if tree.item(item, "values")[0] == anciens[0]["path"]:
                tree.selection_set(item)
                tree.focus(item)
                tree.see(item)
                break

    info_var = tk.StringVar(value="Sélectionne un candidat.")
    ttk.Label(outer, textvariable=info_var, wraplength=1080).grid(
        row=4, column=0, sticky="w", pady=(2, 8)
    )

    def selection_change(_event=None):
        sel = tree.selection()
        if not sel:
            return
        chemin = str(tree.item(sel[0], "values")[0])
        c = next((x for x in candidats if x["path"] == chemin), None)
        if not c:
            return
        examen = c["examen"]
        info_var.set(
            f"{c['statut']} | UUID={examen.get('uuid') or '—'} | "
            f"rôle={examen.get('role') or '—'} | Events={examen.get('events') if examen.get('events') is not None else '—'}"
        )

    tree.bind("<<TreeviewSelect>>", selection_change)
    selection_change()

    boutons = ttk.Frame(outer)
    boutons.grid(row=5, column=0, sticky="ew")

    def executer():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Remplacement", "Sélectionne un périphérique.", parent=win)
            return

        chemin = str(tree.item(sel[0], "values")[0])
        candidat = next((c for c in candidats if c["path"] == chemin), None)
        if not candidat:
            return

        if candidat["ancien_exact"]:
            _lancer_reintegration(self, array_path, candidat, identite, win)
            return

        if candidat["categorie"] == "meme_array":
            messagebox.showerror(
                "Ancien rôle différent",
                f"{chemin} appartient au même RAID, mais son ancien rôle ne correspond pas au slot {old_slot}.\n\n"
                "Réintégration automatique bloquée pour éviter de remettre le mauvais membre dans ce slot.",
                parent=win,
            )
            return

        if candidat["categorie"] == "autre_array":
            messagebox.showerror(
                "Métadonnées d'un autre RAID",
                f"{chemin} contient des métadonnées mdadm d'un autre array.\n\n"
                "Le programme refuse de les écraser automatiquement.",
                parent=win,
            )
            return

        if candidat.get("mounted"):
            messagebox.showerror(
                "Remplacement",
                f"{chemin} est monté. Démonte-le avant de continuer.",
                parent=win,
            )
            return

        if candidat.get("fstype") and not messagebox.askyesno(
            "Périphérique contenant des données",
            f"{chemin} contient un système de fichiers ({candidat['fstype']}).\n\n"
            "Un remplacement normal peut écraser ses métadonnées. Continuer ?",
            parent=win,
        ):
            return

        commandes = []
        bas = old_state.lower()
        if old_dev:
            if "faulty" not in bas and "failed" not in bas:
                commandes.append(["mdadm", array_path, "--fail", old_dev])
            commandes.append(["mdadm", array_path, "--remove", old_dev])
        commandes.append(["mdadm", "--manage", array_path, "--add", chemin])

        apercu = "\n".join(shell_join(c) for c in commandes)
        from .gui_common import ConfirmDialog
        confirmation = ConfirmDialog(
            win,
            "CONFIRMER LE REMPLACEMENT",
            f"RAID : {array_path}\nAncien : {old_label}\nNouveau : {chemin}\n\n"
            f"Commandes :\n\n{apercu}\n\n"
            "Il s'agit d'un remplacement normal. Une reconstruction complète peut être lancée.",
            confirm_token=Path(chemin).name,
        )
        win.wait_window(confirmation)
        if not confirmation.result:
            return

        win.destroy()
        self.run_replace_sequence(commandes, array_path, old_label, chemin)

    ttk.Button(boutons, text="Annuler", command=win.destroy).pack(side="right")
    ttk.Button(
        boutons,
        text="RÉINTÉGRER / REMPLACER",
        command=executer,
    ).pack(side="right", padx=(0, 8))

    self.apply_matrix_widgets()


def installer_mecanisme_remplacement(classe_gestionnaire):
    """Remplace l'ancien assistant par la version avec reconnaissance des anciens membres."""
    classe_gestionnaire.replace_selected_member = _remplacer_selection
