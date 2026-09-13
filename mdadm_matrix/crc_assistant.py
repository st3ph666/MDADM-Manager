"""Guided before/after CRC comparison window."""

import time
import tkinter as tk
from tkinter import messagebox, ttk

from .core import clean_device_path, get_block_devices, physical_disk_info, smart_usage_metrics
from .crc_monitor import CRC_CRITICAL_DELTA, CRC_WARNING_DELTA, CRC_WINDOW_SECONDS


def _disks():
    result = []
    for item in get_block_devices():
        if item.get("type") != "disk":
            continue
        path = clean_device_path(item.get("path") or "")
        if path:
            result.append({
                "path": path,
                "model": (item.get("model") or "").strip(),
                "serial": (item.get("serial") or "").strip(),
            })
    return result


def open_crc_assistant(app):
    win = tk.Toplevel(app)
    win.title("Assistant CRC SATA")
    win.geometry("820x520")
    win.transient(app)
    win.grab_set()

    frame = ttk.Frame(win)
    frame.pack(fill="both", expand=True, padx=14, pady=14)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(4, weight=1)

    ttk.Label(frame, text="ASSISTANT CRC SATA", font=("TkFixedFont", 13, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(
        frame,
        text="Une valeur historique stable reste OK. L'alerte apparaît seulement lorsque le compteur augmente rapidement.",
        wraplength=770,
    ).grid(row=1, column=0, sticky="w", pady=(6, 10))

    disks = _disks()
    labels = [f"{d['path']} | {d['serial'] or 'S/N inconnu'} | {d['model'] or 'modèle inconnu'}" for d in disks]
    selected = tk.StringVar(value=labels[0] if labels else "")
    ttk.Combobox(frame, textvariable=selected, values=labels, state="readonly", style="Matrix.TCombobox").grid(row=2, column=0, sticky="ew")

    baseline = {"device": "", "crc": None, "time": None}
    output = tk.Text(frame, wrap="word", font=("TkFixedFont", 10))
    output.grid(row=4, column=0, sticky="nsew", pady=10)

    def selected_device():
        return clean_device_path(selected.get().split("|", 1)[0].strip())

    def capture_before():
        device = selected_device()
        if not device:
            return
        metrics = smart_usage_metrics(device)
        crc = metrics.get("udma_crc_errors")
        if not isinstance(crc, int):
            messagebox.showwarning("CRC", "Compteur UDMA CRC non disponible.", parent=win)
            return
        baseline.update(device=device, crc=crc, time=time.time())
        info = physical_disk_info(device) or {}
        output.delete("1.0", "end")
        output.insert(
            "end",
            f"MESURE DE RÉFÉRENCE\nDisque : {device}\nModèle : {info.get('model') or '—'}\n"
            f"N° série : {info.get('serial') or '—'}\nCRC : {crc}\n",
        )

    def capture_after():
        device = selected_device()
        if not baseline["device"]:
            messagebox.showinfo("CRC", "Prends d'abord une mesure de référence.", parent=win)
            return
        if device != baseline["device"]:
            messagebox.showwarning("CRC", "Le disque sélectionné a changé.", parent=win)
            return
        metrics = smart_usage_metrics(device)
        crc = metrics.get("udma_crc_errors")
        if not isinstance(crc, int):
            return
        elapsed = max(1.0, time.time() - baseline["time"])
        delta = crc - baseline["crc"]
        if delta <= 0:
            verdict = "OK — aucune nouvelle erreur CRC."
        elif elapsed <= CRC_WINDOW_SECONDS and delta >= CRC_CRITICAL_DELTA:
            verdict = "ALERTE — hausse CRC très rapide."
        elif elapsed <= CRC_WINDOW_SECONDS and delta >= CRC_WARNING_DELTA:
            verdict = "À SURVEILLER — hausse CRC rapide."
        else:
            verdict = "OK — le seuil de hausse rapide n'est pas atteint."
        output.insert(
            "end",
            f"\nNOUVELLE MESURE\nCRC : {crc}\nÉcart : {delta}\nTemps : {elapsed:.0f} s\nRÉSULTAT : {verdict}\n",
        )
        output.see("end")

    bar = ttk.Frame(frame)
    bar.grid(row=3, column=0, sticky="ew", pady=8)
    ttk.Button(bar, text="1 — MESURE DE RÉFÉRENCE", command=capture_before).pack(side="left")
    ttk.Button(bar, text="2 — NOUVELLE MESURE", command=capture_after).pack(side="left", padx=8)
    ttk.Button(bar, text="Fermer", command=win.destroy).pack(side="right")
