"""Point d'entrée de MDADM Manager."""

import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk

from . import APP_VERSION
from .system import relaunch_as_root
from .app import MdadmManager
from .replacement import installer_mecanisme_remplacement
from .assistant import open_assistant
from .crc_assistant import open_crc_assistant
from .crc_monitor import evaluate_crc
from .core import clean_device_path, physical_disk_info

# =============================================================================


# Vérifie au démarrage que les commandes système indispensables sont disponibles.
def dependency_check():
    missing = []
    for exe in ("mdadm", "lsblk"):
        if not shutil.which(exe):
            missing.append(exe)
    return missing


def installer_diagnostic(manager_class):
    """Active le suivi CRC et ajoute l'entrée de l'assistant dans Gérer un RAID."""
    manager_class.open_crc_assistant = lambda self: open_crc_assistant(self)
    manager_class.open_maintenance_assistant = lambda self: open_assistant(self)

    original_cached = getattr(manager_class, "get_cached_smart_metrics", None)
    if original_cached and not getattr(manager_class, "_crc_trend_installed", False):
        def cached_with_crc(self, physical_path, allow_query=True):
            data = original_cached(self, physical_path, allow_query=allow_query)
            if isinstance(data, dict) and allow_query and isinstance(data.get("udma_crc_errors"), int):
                info = physical_disk_info(physical_path) or {}
                identity = (info.get("serial") or clean_device_path(physical_path) or physical_path).strip()
                trend = evaluate_crc(identity, data["udma_crc_errors"])
                data["crc_trend"] = trend["status"]
                data["crc_trend_label"] = trend["label"]
                data["crc_delta"] = trend["delta"]
                data["crc_rate_10min"] = trend["rate_10min"]
            return data

        manager_class.get_cached_smart_metrics = cached_with_crc
        manager_class._crc_trend_installed = True

    original_build_manage = getattr(manager_class, "_build_manage", None)
    if original_build_manage and not getattr(manager_class, "_maintenance_button_installed", False):
        def build_manage_with_assistant(self):
            original_build_manage(self)
            try:
                bar = ttk.Frame(self.tab_manage)
                bar.grid(row=5, column=0, sticky="ew", padx=6, pady=(0, 6))
                ttk.Button(
                    bar,
                    text="ASSISTANT DIAGNOSTIC / REMPLACEMENT",
                    command=self.open_maintenance_assistant,
                ).pack(fill="x")
            except Exception:
                pass

        manager_class._build_manage = build_manage_with_assistant
        manager_class._maintenance_button_installed = True


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

        installer_mecanisme_remplacement(MdadmManager)
        installer_diagnostic(MdadmManager)

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
