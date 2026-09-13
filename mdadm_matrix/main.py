"""Point d'entrée de MDADM Manager."""

import os
import shutil
import tkinter as tk
from tkinter import messagebox

from . import APP_VERSION
from .system import relaunch_as_root
from .app import MdadmManager
from .replacement import installer_mecanisme_remplacement

# =============================================================================


# Vérifie au démarrage que les commandes système indispensables sont disponibles.
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

        # Active l'assistant de remplacement capable de reconnaître un ancien membre
        # grâce à l'UUID du RAID, son ancien rôle et son compteur Events.
        installer_mecanisme_remplacement(MdadmManager)

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
