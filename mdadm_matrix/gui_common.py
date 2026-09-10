"""Shared Tkinter GUI infrastructure for MDADM Manager."""

import tkinter as tk
from tkinter import ttk, messagebox

from .i18n import ui_text

# =============================================================================


# Installs Tkinter hooks that automatically translate many texts when widgets are created/updated.
def install_tk_translation_hooks():
    if getattr(tk, "_mdadm_i18n_installed", False):
        return
    tk._mdadm_i18n_installed = True

    
    original_stringvar_init = tk.StringVar.__init__
    
    # Intercepts StringVar creation to translate its initial value.
    def translated_stringvar_init(self, *args, **kwargs):
        if "value" in kwargs and isinstance(kwargs["value"], str):
            kwargs["value"] = ui_text(kwargs["value"])
        return original_stringvar_init(self, *args, **kwargs)
    tk.StringVar.__init__ = translated_stringvar_init

    original_stringvar_set = tk.StringVar.set
    
    # Intercepts StringVar.set() to translate dynamic display values.
    def translated_stringvar_set(self, value):
        return original_stringvar_set(self, ui_text(value) if isinstance(value, str) else value)
    tk.StringVar.set = translated_stringvar_set

    classes = [
        tk.Label, tk.Button, tk.Checkbutton, tk.Radiobutton, tk.LabelFrame,
        ttk.Label, ttk.Button, ttk.Checkbutton, ttk.Radiobutton, ttk.LabelFrame
    ]
    for cls in classes:
        original_init = cls.__init__
        def make_init(orig):
            def translated_init(self, *args, **kwargs):
                if "text" in kwargs:
                    kwargs["text"] = ui_text(kwargs["text"])
                return orig(self, *args, **kwargs)
            return translated_init
        cls.__init__ = make_init(original_init)

        original_configure = cls.configure
        def make_configure(orig):
            def translated_configure(self, cnf=None, **kwargs):
                if isinstance(cnf, dict):
                    cnf = dict(cnf)
                    if "text" in cnf:
                        cnf["text"] = ui_text(cnf["text"])
                if "text" in kwargs:
                    kwargs["text"] = ui_text(kwargs["text"])
                if cnf is None:
                    return orig(self, **kwargs)
                return orig(self, cnf, **kwargs)
            return translated_configure
        cls.configure = make_configure(original_configure)
        cls.config = cls.configure

    for name in ("showinfo", "showwarning", "showerror", "askyesno",
                 "askokcancel", "askretrycancel"):
        if hasattr(messagebox, name):
            original = getattr(messagebox, name)
            def make_msg(fn):
                def translated_msg(title, message, *args, **kwargs):
                    return fn(ui_text(title), ui_text(message), *args, **kwargs)
                return translated_msg
            setattr(messagebox, name, make_msg(original))

    original_heading = ttk.Treeview.heading
    
    # Intercepts ttk.Treeview column headings so they are translated.
    def translated_heading(self, column, option=None, **kw):
        if "text" in kw:
            kw["text"] = ui_text(kw["text"])
        return original_heading(self, column, option, **kw)
    ttk.Treeview.heading = translated_heading

    original_add = ttk.Notebook.add
    
    # Intercepts ttk.Notebook tab insertion to translate tab titles.
    def translated_add(self, child, **kw):
        if "text" in kw:
            kw["text"] = ui_text(kw["text"])
        return original_add(self, child, **kw)
    ttk.Notebook.add = translated_add

install_tk_translation_hooks()



# Reusable confirmation window for sensitive/destructive actions.
class ConfirmDialog(tk.Toplevel):
    def __init__(self, parent, title, text, confirm_token=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.result = False
        self.confirm_token = confirm_token

        self.transient(parent)
        self.grab_set()

        ttk.Label(
            self,
            text=text,
            justify="left",
            wraplength=760
        ).pack(fill="x", padx=14, pady=(14, 8))

        if confirm_token:
            ttk.Label(
                self,
                text=f"Pour confirmer, tape exactement : {confirm_token}"
            ).pack(anchor="w", padx=14, pady=(6, 2))
            self.entry = ttk.Entry(self, width=40)
            self.entry.pack(fill="x", padx=14, pady=(0, 10))
        else:
            self.entry = None

        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=14, pady=(4, 14))
        ttk.Button(frame, text="Annuler", command=self.cancel).pack(side="right")
        ttk.Button(frame, text="Confirmer", command=self.ok).pack(side="right", padx=(0, 8))

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_idletasks()
        self.geometry(f"+{parent.winfo_rootx()+100}+{parent.winfo_rooty()+100}")

    def ok(self):
        if self.confirm_token and self.entry.get().strip() != self.confirm_token:
            messagebox.showerror("Confirmation", "Le texte de confirmation ne correspond pas.", parent=self)
            return
        self.result = True
        self.destroy()

    def cancel(self):
        self.result = False
        self.destroy()




# =============================================================================
