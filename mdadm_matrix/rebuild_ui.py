"""Interface de suivi en direct des reconstructions mdadm."""

import tkinter as tk
from tkinter import ttk

from .rebuild_monitor import lire_progression_rebuild, texte_progression_rebuild


def installer_progression_rebuild(manager_class):
    original_build_manage = getattr(manager_class, "_build_manage", None)
    if not original_build_manage or getattr(manager_class, "_rebuild_progress_installed", False):
        return

    def build_manage_with_rebuild(self):
        original_build_manage(self)
        try:
            frame = ttk.LabelFrame(self.tab_manage, text="SPARE / REBUILD — PROGRESSION")
            frame.grid(row=6, column=0, sticky="ew", padx=6, pady=(0, 6))
            frame.columnconfigure(0, weight=1)

            self.rebuild_status_var = tk.StringVar(value="Aucune reconstruction en cours")
            self.rebuild_detail_var = tk.StringVar(value="")
            self.rebuild_progress_var = tk.DoubleVar(value=0.0)

            ttk.Label(frame, textvariable=self.rebuild_status_var, font=("TkFixedFont", 10, "bold")).grid(
                row=0, column=0, sticky="ew", padx=8, pady=(6, 2)
            )
            ttk.Progressbar(
                frame,
                maximum=100.0,
                variable=self.rebuild_progress_var,
                mode="determinate",
            ).grid(row=1, column=0, sticky="ew", padx=8, pady=4)
            ttk.Label(frame, textvariable=self.rebuild_detail_var, font=("TkFixedFont", 9)).grid(
                row=2, column=0, sticky="w", padx=8, pady=(2, 6)
            )

            def refresh_progress():
                try:
                    array_path = self.manage_array.get().strip() if hasattr(self, "manage_array") else ""
                    if not array_path and hasattr(self, "selected_array"):
                        array_path = self.selected_array.get().strip()
                    info = lire_progression_rebuild(array_path) if array_path else {"active": False}

                    if info.get("active"):
                        pct = float(info.get("percent") or 0.0)
                        self.rebuild_progress_var.set(max(0.0, min(100.0, pct)))
                        self.rebuild_status_var.set(texte_progression_rebuild(info))
                        done = info.get("done_blocks")
                        total = info.get("total_blocks")
                        if isinstance(done, int) and isinstance(total, int) and total > 0:
                            self.rebuild_detail_var.set(f"Blocs : {done:,} / {total:,}")
                        else:
                            self.rebuild_detail_var.set("")
                    else:
                        self.rebuild_progress_var.set(0.0)
                        self.rebuild_status_var.set("Aucune reconstruction en cours")
                        self.rebuild_detail_var.set("")
                except Exception:
                    pass
                self.after(1000, refresh_progress)

            self.after(500, refresh_progress)
        except Exception:
            pass

    manager_class._build_manage = build_manage_with_rebuild
    manager_class._rebuild_progress_installed = True
