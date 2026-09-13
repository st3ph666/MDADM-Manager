"""Point d'entrée modulaire de MDADM Manager v1.75."""

import os
import tkinter as tk
from tkinter import messagebox

from . import APP_VERSION
from .full_engine import load_engine


def main():
    moteur = load_engine()

    if os.geteuid() != 0:
        launched, _method = moteur.relaunch_as_root()
        if launched:
            raise SystemExit(0)

        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Élévation ROOT impossible",
                f"MDADM Manager v{APP_VERSION} n'a trouvé ni kdesu ni pkexec.\n\n"
                "Installe au besoin :\n"
                "sudo apt install kde-cli-tools pkexec",
            )
            root.destroy()
        except Exception:
            print("Impossible d'obtenir les privilèges root : kdesu/pkexec introuvable.")
        raise SystemExit(1)

    missing = moteur.dependency_check()

    try:
        app = moteur.MdadmManager()
    except Exception as exc:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Erreur au démarrage",
                f"MDADM Manager v{APP_VERSION} n'a pas pu démarrer.\n\n{exc}",
            )
            root.destroy()
        except Exception:
            print(f"ERREUR AU DÉMARRAGE : {exc}")
        raise

    if missing:
        app.after(
            250,
            lambda: messagebox.showwarning(
                "Dépendances",
                "Commandes manquantes : " + ", ".join(missing),
            ),
        )

    app.mainloop()


if __name__ == "__main__":
    main()
