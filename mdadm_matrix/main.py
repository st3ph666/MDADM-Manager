"""Modular entry point for MDADM Manager v1.76."""

import os
import tkinter as tk
from tkinter import messagebox

from . import APP_VERSION
from .full_engine import load_engine


def main():
    engine = load_engine()
    if os.geteuid() != 0:
        launched, _method = engine.relaunch_as_root()
        if launched:
            raise SystemExit(0)
        try:
            root = tk.Tk(); root.withdraw()
            messagebox.showerror("ROOT elevation failed", f"MDADM Manager v{APP_VERSION} could not find kdesu or pkexec.\n\nInstall if needed:\nsudo apt install kde-cli-tools pkexec")
            root.destroy()
        except Exception:
            print("Unable to obtain root privileges: kdesu/pkexec not found.")
        raise SystemExit(1)
    missing = engine.dependency_check()
    try:
        app = engine.MdadmManager()
    except Exception as exc:
        try:
            root = tk.Tk(); root.withdraw()
            messagebox.showerror("Startup error", f"MDADM Manager v{APP_VERSION} could not start.\n\n{exc}")
            root.destroy()
        except Exception:
            print(f"STARTUP ERROR: {exc}")
        raise
    if missing:
        app.after(250, lambda: messagebox.showwarning("Dependencies", "Missing commands: " + ", ".join(missing)))
    app.mainloop()

if __name__ == "__main__":
    main()
