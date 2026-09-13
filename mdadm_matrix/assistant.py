"""Maintenance assistant selector."""

import tkinter as tk
from tkinter import ttk


def open_assistant(app):
    win = tk.Toplevel(app)
    win.title("Assistant diagnostic")
    win.geometry("640x300")
    win.transient(app)
    win.grab_set()

    frame = ttk.Frame(win)
    frame.pack(fill="both", expand=True, padx=18, pady=18)

    ttk.Label(frame, text="ASSISTANT DIAGNOSTIC", font=("TkFixedFont", 14, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Choisis le type d'intervention à effectuer.", wraplength=600).pack(anchor="w", pady=(8, 16))

    ttk.Button(frame, text="CÂBLE SATA / CRC / CONNEXION", command=lambda: app.open_crc_assistant()).pack(fill="x", pady=6)
    ttk.Button(frame, text="DISQUE RAID", command=lambda: app.replace_selected_member()).pack(fill="x", pady=6)
    ttk.Button(frame, text="Fermer", command=win.destroy).pack(anchor="e", pady=(18, 0))
