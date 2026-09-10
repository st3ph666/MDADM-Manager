"""Main Tkinter application for MDADM Manager."""

import re
import shlex
import shutil
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path

from . import APP_TITLE, APP_VERSION
from . import i18n
from .i18n import LANGUAGES, ui_text, save_language, tr
from .system import run, shell_join, privileged_cmd
from .core import *  # noqa: F403,F401
from .gui_common import ConfirmDialog
from .wizard import RaidCreationWizard

# =============================================================================


# Main window: builds tabs, refreshes data, and coordinates all mdadm actions.
class MdadmManager(tk.Tk):

    # -------------------------------------------------------------------------
    # APPLICATION INITIALIZATION
    # -------------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.build_language_menu()
        self.geometry("1220x780")
        self.minsize(1000, 650)

        self.configure(bg="#020802")

        # -----------------------------------------------------------------
        
        # -----------------------------------------------------------------
        
        
        
        
        #
        
        
        #
        # Classic Tk widgets (Text, Listbox, Entry...) normally start with
        #      a white background. apply_matrix_widgets() recolored them later,
        #      which caused the two visible white rectangles during startup.
        #
        #      option_add() sets their defaults before creation, so they are
        #      black/green from their very first painted frame.
        self.option_add("*Listbox.background", "#010601")
        self.option_add("*Listbox.foreground", "#00ff66")
        self.option_add("*Listbox.selectBackground", "#145214")
        self.option_add("*Listbox.selectForeground", "#ffffff")
        self.option_add("*Listbox.highlightBackground", "#0b3d0b")
        self.option_add("*Listbox.highlightColor", "#00aa44")

        self.option_add("*Text.background", "#010601")
        self.option_add("*Text.foreground", "#00ff66")
        self.option_add("*Text.insertBackground", "#00ff66")
        self.option_add("*Text.selectBackground", "#145214")
        self.option_add("*Text.selectForeground", "#ffffff")
        self.option_add("*Text.highlightBackground", "#0b3d0b")
        self.option_add("*Text.highlightColor", "#00aa44")

        self.option_add("*Entry.background", "#010601")
        self.option_add("*Entry.foreground", "#00ff66")
        self.option_add("*Entry.insertBackground", "#00ff66")
        self.option_add("*Entry.selectBackground", "#145214")
        self.option_add("*Entry.selectForeground", "#ffffff")

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background="#061006", foreground="#00dd55", fieldbackground="#020802")
        style.configure("TFrame", background="#061006")
        style.configure("TLabel", background="#061006", foreground="#00dd55")
        style.configure("TButton", background="#0b1c0b", foreground="#00ff66", padding=7)
        style.map("TButton", background=[("active", "#123812")], foreground=[("active", "#ffffff")])
        style.configure("TNotebook", background="#020802", borderwidth=0)
        style.configure("TNotebook.Tab", background="#071407", foreground="#00cc55", padding=(12, 7))
        style.map("TNotebook.Tab", background=[("selected", "#103010")], foreground=[("selected", "#00ff66")])
        style.configure("Treeview", background="#020802", fieldbackground="#020802", foreground="#00dd55", rowheight=25)
        style.configure("Treeview.Heading", background="#0a1c0a", foreground="#00ff66")
        style.map("Treeview", background=[("selected", "#145214")], foreground=[("selected", "#ffffff")])

        # -----------------------------------------------------------------
        # COMBOBOX MATRIX / MATRIX COMBOBOX
        # -----------------------------------------------------------------
        
        
        
        # On some Linux themes, a readonly Combobox may stay white even
        #      with a dark global style. Force field, text, readonly and active
        #      colors here for consistent readability.
        style.configure(
            "Matrix.TCombobox",
            foreground="#00ff66",
            fieldbackground="#010601",
            background="#0b1c0b",
            arrowcolor="#00ff66",
            bordercolor="#0b3d0b",
            lightcolor="#0b3d0b",
            darkcolor="#0b3d0b",
            padding=4,
        )
        style.map(
            "Matrix.TCombobox",
            fieldbackground=[
                ("readonly", "#010601"),
                ("focus", "#010601"),
                ("!disabled", "#010601"),
            ],
            foreground=[
                ("readonly", "#00ff66"),
                ("focus", "#00ff66"),
                ("!disabled", "#00ff66"),
            ],
            background=[
                ("readonly", "#0b1c0b"),
                ("active", "#123812"),
            ],
            arrowcolor=[
                ("readonly", "#00ff66"),
                ("active", "#ffffff"),
            ],
        )

        self.status_var = tk.StringVar(value=f"MDADM Manager v{APP_VERSION} // ROOT // Rafraîchissement 15 s // Prêt")
        self.selected_array = tk.StringVar()
        self.refresh_ms = 15000
        self.selected_member_key = None
        self.selected_manage_member_key = None
        
        
        self.smart_metrics_cache = {}
        self.smart_metrics_cache_seconds = 120

        
        
        
        # Build and display the GUI first. Slower disk/SMART probing starts
        #      immediately afterward, so the application appears much faster.
        self._smart_scan_running = False

        
        
        
        
        # A lightweight MATRIX loading screen is displayed immediately.
        #      The heavy GUI is then built tab by tab with after(), avoiding
        #      a several-second black window.
        self._build_startup_screen()
        self.after(25, self._build_ui_staged)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds the black/green MATRIX language menu.
    def build_language_menu(self):

        
        menu_bg = "#020802"
        menu_fg = "#00dd55"
        menu_active_bg = "#103010"
        menu_active_fg = "#00ff66"

        menubar = tk.Menu(
            self,
            bg=menu_bg,
            fg=menu_fg,
            activebackground=menu_active_bg,
            activeforeground=menu_active_fg,
            borderwidth=0,
            relief="flat",
        )

        language_menu = tk.Menu(
            menubar,
            tearoff=False,
            bg=menu_bg,
            fg=menu_fg,
            activebackground=menu_active_bg,
            activeforeground=menu_active_fg,
            selectcolor=menu_fg,
            borderwidth=1,
            relief="solid",
        )
        self.language_menu_var = tk.StringVar(value=i18n.CURRENT_LANGUAGE)

        language_menu.add_radiobutton(
            label="Français",
            variable=self.language_menu_var,
            value="fr",
            command=lambda: self.change_language("fr")
        )
        language_menu.add_radiobutton(
            label="English",
            variable=self.language_menu_var,
            value="en",
            command=lambda: self.change_language("en")
        )

        menubar.add_cascade(
            label="Langue / Language",
            menu=language_menu
        )
        self.config(menu=menubar)

    
    # Saves the new language and informs the user about restart behavior.
    def change_language(self, code):

        if code not in LANGUAGES:
            return

        i18n.CURRENT_LANGUAGE = code
        save_language(code)

        messagebox.showinfo(
            tr("language_changed"),
            tr("language_restart"),
            parent=self
        )


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Immediately displays a very lightweight loading screen.
    def _build_startup_screen(self):

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.startup_frame = tk.Frame(self, bg="#020802")
        self.startup_frame.grid(row=0, column=0, sticky="nsew")

        center = tk.Frame(self.startup_frame, bg="#020802")
        center.place(relx=0.5, rely=0.46, anchor="center")

        tk.Label(
            center,
            text=f"MDADM MANAGER v{APP_VERSION}",
            bg="#020802",
            fg="#00ff66",
            font=("DejaVu Sans Mono", 20, "bold"),
        ).pack(pady=(0, 12))

        tk.Label(
            center,
            text="Initialisation…" if i18n.CURRENT_LANGUAGE != "en" else "Initializing…",
            bg="#020802",
            fg="#00cc55",
            font=("DejaVu Sans Mono", 11),
        ).pack()

        self.startup_progress_var = tk.StringVar(value="[░░░░░░]")

        tk.Label(
            center,
            textvariable=self.startup_progress_var,
            bg="#020802",
            fg="#00dd55",
            font=("DejaVu Sans Mono", 13, "bold"),
        ).pack(pady=(12, 0))

        
        self.update_idletasks()


    
    # Prepares tabs and starts priority-aware progressive loading.
    def _build_ui_staged(self):













        self.nb = ttk.Notebook(self)
        self.nb.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.nb.configure(style="Matrix.TNotebook")

        self.tab_info = tk.Frame(self.nb, bg="#020802")
        self.tab_dashboard = tk.Frame(self.nb, bg="#020802")
        self.tab_create = tk.Frame(self.nb, bg="#020802")
        self.tab_manage = tk.Frame(self.nb, bg="#020802")
        self.tab_disks = tk.Frame(self.nb, bg="#020802")
        self.tab_config = tk.Frame(self.nb, bg="#020802")

        self.nb.add(self.tab_dashboard, text=tr("dashboard"))
        self.nb.add(self.tab_create, text=tr("create_raid"))
        self.nb.add(self.tab_manage, text=tr("manage_raid"))
        self.nb.add(self.tab_disks, text=tr("disks"))
        self.nb.add(self.tab_config, text=tr("configuration"))
        self.nb.add(self.tab_info, text=tr("raid_info"))

        self.status_widget = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
        )
        self.status_widget.grid(row=1, column=0, sticky="ew")

        
        # 0=Dashboard, 1=Create RAID, 2=Manage RAID, 3=Disks,
        # 4=Configuration, 5=RAID Info.
        self._startup_tab_built = set()
        self._startup_tab_building = set()
        self._startup_background_after_id = None
        self._startup_finished = False

        self._startup_tab_builders = {
            0: self._build_dashboard,
            1: self._build_create,
            2: self._build_manage,
            3: self._build_disks,
            4: self._build_config,
            5: self._build_info,
        }

        
        
        self._startup_background_order = [0, 1, 2, 3, 4, 5]

        
        for index in range(6):
            self._show_tab_loading_placeholder(index)

        
        
        self.nb.bind("<<NotebookTabChanged>>", self._on_startup_tab_changed, add="+")

        self.startup_progress_var.set("[█░░░░░] Dashboard")

        
        self.nb.select(self.tab_dashboard)
        self.after(1, lambda: self._ensure_startup_tab_built(0, user_requested=False))


    def _show_tab_loading_placeholder(self, index):

        tab = self.nb.nametowidget(self.nb.tabs()[index])

        holder = tk.Frame(tab, bg="#020802")
        holder.pack(fill="both", expand=True)

        label = tk.Label(
            holder,
            text=(
                "Chargement de cette section…\n"
                "Cliquez ici et elle devient prioritaire."
                if i18n.CURRENT_LANGUAGE != "en"
                else
                "Loading this section…\n"
                "Open it and it becomes the priority."
            ),
            bg="#020802",
            fg="#00cc55",
            font=("DejaVu Sans Mono", 11),
            justify="center",
        )
        label.place(relx=0.5, rely=0.45, anchor="center")


    def _clear_tab_before_build(self, index):

        tab = self.nb.nametowidget(self.nb.tabs()[index])
        for child in tab.winfo_children():
            child.destroy()


    def _on_startup_tab_changed(self, event=None):






        if not hasattr(self, "_startup_tab_built"):
            return

        try:
            index = self.nb.index(self.nb.select())
        except tk.TclError:
            return

        if index not in self._startup_tab_built:
            self._ensure_startup_tab_built(index, user_requested=True)


    def _ensure_startup_tab_built(self, index, user_requested=False):

        if index in self._startup_tab_built or index in self._startup_tab_building:
            return

        
        
        if user_requested and self._startup_background_after_id is not None:
            try:
                self.after_cancel(self._startup_background_after_id)
            except tk.TclError:
                pass
            self._startup_background_after_id = None

        self._startup_tab_building.add(index)

        tab_names_fr = {
            0: "Tableau de bord",
            1: "Création RAID",
            2: "Gestion RAID",
            3: "Disques",
            4: "Configuration",
            5: "Info RAID",
        }
        tab_names_en = {
            0: "Dashboard",
            1: "Create RAID",
            2: "Manage RAID",
            3: "Disks",
            4: "Configuration",
            5: "RAID Info",
        }
        tab_name = (tab_names_en if i18n.CURRENT_LANGUAGE == "en" else tab_names_fr)[index]

        if getattr(self, "startup_frame", None) is not None:
            blocks = "█" * (index + 1)
            spaces = "░" * (5 - index)
            self.startup_progress_var.set(f"[{blocks}{spaces}] {tab_name}")

        self.set_status(
            f"Chargement : {tab_name}…"
            if i18n.CURRENT_LANGUAGE != "en"
            else f"Loading: {tab_name}…"
        )

        
        self.update_idletasks()

        self._clear_tab_before_build(index)
        builder = self._startup_tab_builders[index]

        try:
            builder()
            self._startup_tab_built.add(index)
        finally:
            self._startup_tab_building.discard(index)

        
        if index == 0:
            if getattr(self, "startup_frame", None) is not None:
                self.startup_frame.destroy()
                self.startup_frame = None

            self.nb.select(self.tab_dashboard)
            self.update_idletasks()

            # Affichage RAID rapide, sans SMART bloquant.
            self.after(
                1,
                lambda: self.refresh_arrays(
                    include_manage=(2 in self._startup_tab_built),
                    allow_smart_query=False,
                ),
            )

        
        elif index == 2:
            self.after(
                1,
                lambda: self.refresh_arrays(
                    include_manage=True,
                    allow_smart_query=False,
                ),
            )

        self.update_idletasks()

        
        
        # sans donner l'impression que l'application prend son temps.
        if len(self._startup_tab_built) == len(self._startup_tab_builders):
            self._finish_progressive_startup()
        else:
            delay = 15 if user_requested else 65
            self._schedule_next_background_tab(delay)


    def _schedule_next_background_tab(self, delay=65):

        if self._startup_finished:
            return

        if self._startup_background_after_id is not None:
            try:
                self.after_cancel(self._startup_background_after_id)
            except tk.TclError:
                pass

        self._startup_background_after_id = self.after(
            delay,
            self._build_next_background_tab,
        )


    def _build_next_background_tab(self):

        self._startup_background_after_id = None

        for index in self._startup_background_order:
            if (
                index not in self._startup_tab_built
                and index not in self._startup_tab_building
            ):
                self._ensure_startup_tab_built(index, user_requested=False)
                return

        self._finish_progressive_startup()


    def _finish_progressive_startup(self):

        if self._startup_finished:
            return

        if len(self._startup_tab_built) != len(self._startup_tab_builders):
            return

        self._startup_finished = True
        self.apply_matrix_widgets()
        self.update_idletasks()

        self.set_status(
            "Interface prête — analyse système en arrière-plan…"
            if i18n.CURRENT_LANGUAGE != "en"
            else "Interface ready — background system analysis…"
        )

        
        self.after(1, self._startup_fast_refresh)
        self.after(self.refresh_ms, self.auto_refresh)


    
    
    def _build_ui(self):
        self._build_startup_screen()
        self.after(25, self._build_ui_staged)


    # -------------------------------------------------------------------------
    # ONGLET INFO RAID / RAID INFO TAB
    # -------------------------------------------------------------------------

    
    # Builds the educational RAID Info tab and its diagrams.
    def _build_info(self):
        f = self.tab_info
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)

        outer = ttk.Frame(f)
        outer.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        ttk.Label(
            outer,
            text="GUIDE VISUEL DES TYPES DE RAID",
            font=("TkFixedFont", 14, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        canvas = tk.Canvas(outer, bg="#020802", highlightthickness=0)
        canvas.grid(row=1, column=0, sticky="nsew")

        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        sb.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=sb.set)

        content = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=content, anchor="nw")

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(win_id, width=e.width)
        )

        ttk.Label(
            content,
            text=(
                "Le RAID combine plusieurs disques pour obtenir plus de vitesse, "
                "plus de capacité ou de la redondance. IMPORTANT : un RAID ne remplace "
                "jamais une sauvegarde."
            ),
            justify="left",
            wraplength=1300,
            font=("TkFixedFont", 10, "bold")
        ).pack(fill="x", pady=(0, 10))

        raids = [
            (
                "RAID 0 — RAPIDE, MAIS AUCUNE PROTECTION",
                "Minimum : 2 disques\n"
                "Tolérance aux pannes : AUCUNE\n"
                "Capacité utile : 100 % de la capacité totale\n"
                "Usage : fichiers temporaires, gros débit, données non critiques\n"
                "Avantage : performances maximales\n"
                "Risque : 1 seul disque en panne = RAID complet perdu",
                "        DONNÉES\n"
                "           │\n"
                "      ┌────┴────┐\n"
                "      │         │\n"
                "  ┌───────┐ ┌───────┐\n"
                "  │DISQUE1│ │DISQUE2│\n"
                "  │ A C E │ │ B D F │\n"
                "  └───────┘ └───────┘\n"
                "     STRIPING"
            ),
            (
                "RAID 1 — MIROIR",
                "Minimum : 2 disques\n"
                "Tolérance aux pannes : 1 disque\n"
                "Capacité utile : 50 % avec 2 disques\n"
                "Usage : système et données importantes\n"
                "Avantage : simple et sécuritaire\n"
                "Risque : capacité divisée par deux",
                "        DONNÉES\n"
                "           │\n"
                "      ┌────┴────┐\n"
                "      │         │\n"
                "  ┌───────┐ ┌───────┐\n"
                "  │DISQUE1│ │DISQUE2│\n"
                "  │ A B C │ │ A B C │\n"
                "  └───────┘ └───────┘\n"
                "       MIROIR"
            ),
            (
                "RAID 5 — 1 DISQUE DE PARITÉ",
                "Minimum : 3 disques\n"
                "Tolérance aux pannes : 1 disque\n"
                "Capacité utile : (N - 1) × taille du plus petit disque\n"
                "Usage : stockage général\n"
                "Avantage : bon compromis capacité/protection\n"
                "Risque : reconstruction plus lourde sur gros volumes",
                "          RAID 5\n"
                " ┌────────┬────────┬────────┐\n"
                " │DISQUE1 │DISQUE2 │DISQUE3 │\n"
                " ├────────┼────────┼────────┤\n"
                " │   A    │   B    │  PAB   │\n"
                " │   C    │  PCD   │   D    │\n"
                " │  PEF   │   E    │   F    │\n"
                " └────────┴────────┴────────┘\n"
                " P = PARITÉ"
            ),
            (
                "RAID 6 — DOUBLE PARITÉ",
                "Minimum : 4 disques\n"
                "Tolérance aux pannes : 2 disques\n"
                "Capacité utile : (N - 2) × taille du plus petit disque\n"
                "Usage : gros ensembles RAID et données importantes\n"
                "Avantage : peut survivre à 2 pannes\n"
                "Risque : écritures/reconstruction plus lourdes",
                "             RAID 6\n"
                " ┌────────┬────────┬────────┬────────┐\n"
                " │DISQUE1 │DISQUE2 │DISQUE3 │DISQUE4 │\n"
                " ├────────┼────────┼────────┼────────┤\n"
                " │   A    │   B    │   P    │   Q    │\n"
                " │   C    │   P    │   Q    │   D    │\n"
                " │   P    │   Q    │   E    │   F    │\n"
                " └────────┴────────┴────────┴────────┘\n"
                " P + Q = DOUBLE PARITÉ"
            ),
            (
                "RAID 10 — MIROIR + PERFORMANCE",
                "Minimum : 4 disques\n"
                "Tolérance : dépend de quels disques tombent en panne\n"
                "Capacité utile : environ 50 %\n"
                "Usage : serveur, VM, bases de données, gros débit\n"
                "Avantage : très bonnes performances + redondance\n"
                "Risque : nécessite davantage de disques",
                "                RAID 10\n"
                "         ┌────────┴────────┐\n"
                "         │                 │\n"
                "      MIROIR A          MIROIR B\n"
                "    ┌────┴────┐        ┌────┴────┐\n"
                " ┌──────┐ ┌──────┐  ┌──────┐ ┌──────┐\n"
                " │DISQ 1│ │DISQ 2│  │DISQ 3│ │DISQ 4│\n"
                " │ A C E│ │ A C E│  │ B D F│ │ B D F│\n"
                " └──────┘ └──────┘  └──────┘ └──────┘"
            ),
        ]

        for title, description, diagram in raids:
            box = ttk.LabelFrame(content, text=title)
            box.pack(fill="x", pady=6)

            box.columnconfigure(0, weight=3)
            box.columnconfigure(1, weight=2)

            ttk.Label(
                box,
                text=description,
                justify="left",
                wraplength=700,
                font=("TkFixedFont", 10)
            ).grid(row=0, column=0, sticky="nw", padx=10, pady=10)

            txt = tk.Text(
                box,
                height=10,
                width=52,
                wrap="none",
                font=("TkFixedFont", 10),
                bg="#001500",
                fg="#00ff66",
                insertbackground="#00ff66",
                relief="solid",
                borderwidth=1
            )
            txt.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
            txt.insert("1.0", ui_text(diagram))
            txt.configure(state="disabled")

        quick = ttk.LabelFrame(content, text="CHOIX RAPIDE")
        quick.pack(fill="x", pady=(10, 6))

        ttk.Label(
            quick,
            text=(
                "RAID 0  → vitesse maximale, aucune protection\n"
                "RAID 1  → simple et sécuritaire avec 2 disques\n"
                "RAID 5  → bon compromis capacité/protection, 1 panne tolérée\n"
                "RAID 6  → meilleur choix quand 2 pannes doivent être tolérées\n"
                "RAID 10 → excellent mélange performance/redondance\n\n"
                "Plus le RAID contient de disques et plus sa reconstruction est longue, "
                "plus RAID 6 ou RAID 10 devient intéressant pour des données importantes."
            ),
            justify="left",
            wraplength=1300,
            font=("TkFixedFont", 10, "bold")
        ).pack(anchor="w", padx=10, pady=10)

        def wheel(event):
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(3, "units")
            elif getattr(event, "delta", 0):
                canvas.yview_scroll(int(-event.delta / 120), "units")

        canvas.bind("<Enter>", lambda e: (
            canvas.bind_all("<MouseWheel>", wheel),
            canvas.bind_all("<Button-4>", wheel),
            canvas.bind_all("<Button-5>", wheel)
        ))
        canvas.bind("<Leave>", lambda e: (
            canvas.unbind_all("<MouseWheel>"),
            canvas.unbind_all("<Button-4>"),
            canvas.unbind_all("<Button-5>")
        ))


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds the active-array dashboard.
    def _build_dashboard(self):
        f = self.tab_dashboard
        f.columnconfigure(0, weight=0)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(0, weight=1)

        left = ttk.Frame(f)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8), pady=4)

        ttk.Label(
            left,
            text="ARRAYS MDADM",
            font=("TkFixedFont", 12, "bold")
        ).pack(anchor="w")

        self.arr_list = tk.Listbox(
            left,
            width=30,
            height=28,
            font=("TkFixedFont", 10),
            bg="#010601",
            fg="#00ff66",
            selectbackground="#145214",
            selectforeground="#ffffff",
            highlightbackground="#0b3d0b",
            highlightcolor="#00aa44",
            relief="flat",
        )
        self.arr_list.pack(fill="y", expand=True, pady=(5, 8))
        self.arr_list.bind("<<ListboxSelect>>", self.on_array_select)

        ttk.Button(left, text="⟳  Rafraîchir", command=self.refresh_all).pack(fill="x")

        right = ttk.Frame(f)
        right.grid(row=0, column=1, sticky="nsew", pady=4)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)
        right.rowconfigure(6, weight=1)

        self.summary_var = tk.StringVar(value="Sélectionne un array.")
        ttk.Label(
            right,
            textvariable=self.summary_var,
            justify="left",
            font=("TkFixedFont", 11, "bold")
        ).grid(row=0, column=0, sticky="ew", padx=4, pady=(2, 4))

        self.mount_var = tk.StringVar(value="Montage : —")
        ttk.Label(
            right,
            textvariable=self.mount_var,
            justify="left",
            font=("TkFixedFont", 10)
        ).grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 6))

        ttk.Label(
            right,
            text="DISQUES MEMBRES DU RAID",
            font=("TkFixedFont", 11, "bold")
        ).grid(row=2, column=0, sticky="w", padx=4, pady=(4, 2))

        cols = ("device", "slot", "state", "size", "model", "serial", "temp", "bad", "usage")
        self.member_tree = ttk.Treeview(right, columns=cols, show="headings", height=10)
        heads = {
            "device": "Périphérique",
            "slot": "Slot",
            "state": "État",
            "size": "Taille",
            "model": "Modèle",
            "serial": "N° série",
            "temp": "Temp",
            "bad": "Erreurs / secteurs",
            "usage": "Utilisation",
        }
        widths = {
            "device": 205,
            "slot": 60,
            "state": 190,
            "size": 100,
            "model": 200,
            "serial": 190,
            "temp": 58,
            "bad": 155,
            "usage": 175,
        }
        for col in cols:
            self.member_tree.heading(col, text=heads[col])
            self.member_tree.column(
                col,
                width=widths[col],
                anchor=("center" if col == "temp" else "w"),
                stretch=(False if col == "temp" else True),
            )

        self.member_tree.tag_configure("ok", foreground="#00ff66")
        self.member_tree.tag_configure("warning", foreground="#ffb000")
        self.member_tree.tag_configure("problem", foreground="#ff3b3b")
        self.member_tree.tag_configure("removed", foreground="#ff3b3b")

        self.member_tree.grid(row=3, column=0, sticky="nsew", padx=4, pady=(0, 4))
        self.member_tree.bind("<<TreeviewSelect>>", self.on_member_select)
        self.member_tree.bind("<Double-1>", self.member_smart)

        member_scroll = ttk.Scrollbar(right, orient="vertical", command=self.member_tree.yview)
        member_scroll.grid(row=3, column=1, sticky="ns", pady=(0, 4))
        self.member_tree.configure(yscrollcommand=member_scroll.set)

        self.selected_member_var = tk.StringVar(value="Aucun disque sélectionné")
        ttk.Label(
            right,
            textvariable=self.selected_member_var,
            font=("TkFixedFont", 10)
        ).grid(row=4, column=0, sticky="ew", padx=4, pady=(2, 4))

        diskbar = ttk.Frame(right)
        diskbar.grid(row=5, column=0, sticky="ew", padx=4, pady=(0, 6))
        for i in range(5):
            diskbar.columnconfigure(i, weight=1)

        ttk.Button(diskbar, text="SMART", command=self.member_smart).grid(row=0, column=0, padx=3, sticky="ew")
        ttk.Button(diskbar, text="Marquer FAULTY", command=self.member_faulty).grid(row=0, column=1, padx=3, sticky="ew")
        ttk.Button(diskbar, text="Retirer", command=self.member_remove).grid(row=0, column=2, padx=3, sticky="ew")
        ttk.Button(diskbar, text="REMPLACER LE DISQUE", command=self.replace_selected_member).grid(row=0, column=3, padx=3, sticky="ew")
        ttk.Button(diskbar, text="Détails RAID", command=self.dashboard_details).grid(row=0, column=4, padx=3, sticky="ew")

        self.detail_text = tk.Text(
            right,
            wrap="none",
            height=9,
            font=("TkFixedFont", 9),
            bg="#010601",
            fg="#00ff66",
            insertbackground="#00ff66",
            selectbackground="#145214",
            selectforeground="#ffffff",
            highlightbackground="#0b3d0b",
            highlightcolor="#00aa44",
            relief="flat",
        )
        self.detail_text.grid(row=6, column=0, sticky="nsew", padx=4, pady=(2, 0))

        sy = ttk.Scrollbar(right, orient="vertical", command=self.detail_text.yview)
        sy.grid(row=6, column=1, sticky="ns", pady=(2, 0))
        self.detail_text.configure(yscrollcommand=sy.set)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds the creation tab and the button that opens the wizard.
    def _build_create(self):
        f = self.tab_create
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        hero = ttk.Frame(f, padding=18)
        hero.grid(row=0, column=0, sticky="ew")
        hero.columnconfigure(0, weight=1)

        ttk.Label(
            hero,
            text="ASSISTANT DE CRÉATION RAID",
            font=("TkFixedFont", 16, "bold")
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            hero,
            text=(
                "Création guidée en 4 étapes : choix du niveau RAID, analyse et "
                "sélection des disques, paramètres, puis vérification finale."
            ),
            wraplength=1000,
            justify="left"
        ).grid(row=1, column=0, sticky="w", pady=(8, 12))

        ttk.Button(
            hero,
            text=tr("wizard_launch"),
            command=self.open_create_wizard
        ).grid(row=2, column=0, sticky="w", pady=(4, 8))

        info = ttk.LabelFrame(f, text="Ce que l'assistant vérifie")
        info.grid(row=1, column=0, sticky="ew", padx=18, pady=8)
        info.columnconfigure(0, weight=1)

        ttk.Label(
            info,
            text=(
                "• Modèle, numéro de série, taille et type HDD / SSD / NVMe\n"
                "• État SMART, heures de fonctionnement et usure / risque\n"
                "• RAID actuel, partitions, systèmes de fichiers et points de montage\n"
                "• Capacité utile estimée selon RAID 0 / 1 / 5 / 6 / 10\n"
                "• Comptage rapide des disques libres sans attendre SMART\n"
                "• SMART détaillé à la demande, sans bloquer l'assistant\n"
                "• Niveaux RAID impossibles automatiquement grisés\n"
                "• Tolérance aux pannes et nombre minimal de disques\n"
                "• Protection ABSOLUE des disques déjà membres d'un RAID existant\n"
                "• Protection ABSOLUE des disques/partitions référencés dans /etc/fstab\n"
                "• Détection fstab par /dev, UUID, PARTUUID, LABEL et PARTLABEL\n"
                "• Analyse mdadm --examine des anciennes métadonnées RAID\n"
                "• --zero-superblock proposé seulement pour un ancien RAID orphelin\n"
                "• Le mode avancé ne peut jamais contourner RAID ou FSTAB\n"
                "• Vérification finale de la commande mdadm avant écriture\n"                 "• Interface Français / English sélectionnable et mémorisée"
            ),
            justify="left",
            padding=12,
            font=("TkFixedFont", 10)
        ).grid(row=0, column=0, sticky="w")

        guide = ttk.LabelFrame(f, text="Repères rapides")
        guide.grid(row=2, column=0, sticky="nsew", padx=18, pady=(8, 18))
        guide.columnconfigure(0, weight=1)

        ttk.Label(
            guide,
            text=(
                "RAID 0  → performances / capacité, aucune protection\n"
                "RAID 1  → miroir simple, très facile à comprendre et reconstruire\n"
                "RAID 5  → 1 disque de parité, tolère 1 panne\n"
                "RAID 6  → 2 disques de parité, tolère 2 pannes\n"
                "RAID 10 → miroir + performances, excellent choix avec plusieurs disques\n\n"
                "La capacité réelle est limitée par le plus petit disque de l'ensemble."
            ),
            justify="left",
            padding=14,
            font=("TkFixedFont", 10)
        ).grid(row=0, column=0, sticky="nw")

        
        
        self.create_name = ttk.Entry(f)
        self.create_name.insert(0, "md20")
        self.create_level = ttk.Combobox(f, values=["raid0", "raid1", "raid5", "raid6", "raid10"], style="Matrix.TCombobox")
        self.create_level.set("raid10")
        self.create_chunk = ttk.Combobox(f, values=["64", "128", "256", "512", "1024"], style="Matrix.TCombobox")
        self.create_chunk.set("512")
        self.create_meta = ttk.Combobox(f, values=["1.2", "1.1", "1.0"], style="Matrix.TCombobox")
        self.create_meta.set("1.2")
        self.create_bitmap = tk.BooleanVar(value=True)
        self.create_disks = tk.Listbox(f, selectmode="extended")

    
    # Opens a new RAID creation wizard instance.
    def open_create_wizard(self):
        RaidCreationWizard(self)


    # -------------------------------------------------------------------------
    # ONGLET GESTION RAID / MANAGE RAID TAB
    # -------------------------------------------------------------------------

    
    # Builds management controls: details, stop, check, repair, members, etc.
    def _build_manage(self):
        f = self.tab_manage
        f.columnconfigure(0, weight=1)
        f.rowconfigure(4, weight=1)

        top = ttk.Frame(f)
        top.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Array :").grid(row=0, column=0, sticky="e", padx=(0, 6))
        self.manage_array = ttk.Combobox(top, state="readonly", style="Matrix.TCombobox")
        self.manage_array.grid(row=0, column=1, sticky="ew")
        self.manage_array.bind("<<ComboboxSelected>>", self.on_manage_array_select)

        actionbar = ttk.Frame(f)
        actionbar.grid(row=1, column=0, sticky="ew", padx=6, pady=4)

        actions = [
            ("Détails", self.manage_details),
            ("Assembler", self.manage_assemble),
            ("Arrêter", self.manage_stop),
            ("Check", self.manage_check),
            ("Repair", self.manage_repair),
            ("Ajouter membre", self.manage_add),
            ("Retirer sélection", self.member_remove),
            ("Faulty sélection", self.member_faulty),
            ("Remplacer sélection", self.replace_selected_member),
            ("Zero superblock", self.manage_zero_superblock),
        ]
        for i, (label, fn) in enumerate(actions):
            ttk.Button(actionbar, text=label, command=fn).grid(
                row=i // 5, column=i % 5, padx=3, pady=3, sticky="ew"
            )
            actionbar.columnconfigure(i % 5, weight=1)

        ttk.Label(
            f,
            text="Membres — sélectionne directement le disque sur lequel agir",
            font=("TkFixedFont", 10, "bold")
        ).grid(row=2, column=0, sticky="w", padx=6, pady=(6, 2))

        cols = ("device", "slot", "state", "size", "model", "serial", "temp", "bad", "usage")
        self.manage_member_tree = ttk.Treeview(f, columns=cols, show="headings", height=8)
        heads = {
            "device": "Périphérique",
            "slot": "Slot",
            "state": "État",
            "size": "Taille",
            "model": "Modèle",
            "serial": "N° série",
            "temp": "Temp",
            "bad": "Erreurs / secteurs",
            "usage": "Utilisation",
        }
        widths = {
            "device": 205, "slot": 60, "state": 180,
            "size": 100, "model": 200, "serial": 180,
            "temp": 58, "bad": 155, "usage": 175
        }
        for col in cols:
            self.manage_member_tree.heading(col, text=heads[col])
            self.manage_member_tree.column(
                col,
                width=widths[col],
                anchor=("center" if col == "temp" else "w"),
                stretch=(False if col == "temp" else True),
            )
        self.manage_member_tree.tag_configure("ok", foreground="#00ff66")
        self.manage_member_tree.tag_configure("warning", foreground="#ffb000")
        self.manage_member_tree.tag_configure("problem", foreground="#ff3b3b")
        self.manage_member_tree.tag_configure("removed", foreground="#ff3b3b")
        self.manage_member_tree.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 6))
        self.manage_member_tree.bind("<<TreeviewSelect>>", self.on_manage_member_select)

        self.manage_output = tk.Text(f, wrap="none", font=("TkFixedFont", 10))
        self.manage_output.grid(row=4, column=0, sticky="nsew", padx=6, pady=6)


    # -------------------------------------------------------------------------
    # ONGLET DISQUES / SMART / DISKS / SMART TAB
    # -------------------------------------------------------------------------

    
    # Builds the physical disk inventory with SMART/RAID columns.
    def _build_disks(self):
        f = self.tab_disks
        f.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)

        cols = (
            "path", "size", "model", "serial", "temp",
            "raid", "member", "raid_state",
            "smart", "bad", "usage", "wear",
            "fstype", "mount"
        )
        self.disk_tree = ttk.Treeview(f, columns=cols, show="headings")

        heads = {
            "path": "Périphérique",
            "size": "Taille",
            "model": "Modèle",
            "serial": "Série",
            "temp": "Temp",
            "raid": "RAID",
            "member": "Membre RAID",
            "raid_state": "État RAID",
            "smart": "SMART",
            "bad": "Erreurs / secteurs",
            "usage": "Utilisation",
            "wear": "Usure / Risque",
            "fstype": "FS",
            "mount": "Montage",
        }

        widths = {
            "path": 105,
            "size": 90,
            "model": 190,
            "serial": 165,
            "temp": 58,
            "raid": 95,
            "member": 125,
            "raid_state": 175,
            "smart": 80,
            "bad": 145,
            "usage": 170,
            "wear": 145,
            "fstype": 125,
            "mount": 190,
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

        self.disk_tree.tag_configure("ok", foreground="#00ff66")
        self.disk_tree.tag_configure("warning", foreground="#ffb000")
        self.disk_tree.tag_configure("problem", foreground="#ff3b3b")

        self.disk_tree.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        sb_y = ttk.Scrollbar(f, orient="vertical", command=self.disk_tree.yview)
        sb_y.grid(row=0, column=1, sticky="ns", pady=6)

        sb_x = ttk.Scrollbar(f, orient="horizontal", command=self.disk_tree.xview)
        sb_x.grid(row=1, column=0, sticky="ew", padx=6)

        self.disk_tree.configure(
            yscrollcommand=sb_y.set,
            xscrollcommand=sb_x.set
        )

        bar = ttk.Frame(f)
        bar.grid(row=2, column=0, sticky="ew", padx=6, pady=6)

        ttk.Button(
            bar,
            text="Rafraîchir",
            command=self.refresh_disks
        ).pack(side="left")

        ttk.Button(
            bar,
            text="SMART du disque sélectionné",
            command=self.show_smart
        ).pack(side="left", padx=8)

        ttk.Label(
            bar,
            text="RAID/Membre provient de mdadm, pas seulement de FSTYPE.",
            font=("TkFixedFont", 9)
        ).pack(side="left", padx=14)


    # -------------------------------------------------------------------------
    # ONGLET CONFIGURATION MDADM / MDADM CONFIGURATION TAB
    # -------------------------------------------------------------------------

    
    # Builds the mdadm.conf editor.
    def _build_config(self):
        f = self.tab_config
        self.config_loaded_path = "/etc/mdadm/mdadm.conf"
        self.config_file_var = tk.StringVar(
            value="Fichier actuellement chargé : /etc/mdadm/mdadm.conf"
        )
        f.rowconfigure(2, weight=1)
        f.columnconfigure(0, weight=1)

        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        ttk.Button(bar, text="Charger mdadm.conf", command=self.load_config).pack(side="left")
        ttk.Button(bar, text="Scanner les arrays", command=self.scan_config).pack(side="left", padx=8)
        ttk.Button(bar, text="Sauvegarder mdadm.conf", command=self.save_config).pack(side="left")
        ttk.Button(bar, text="Sauvegarder une copie", command=self.export_config).pack(side="left", padx=8)

        ttk.Label(
            f,
            textvariable=self.config_file_var,
            font=("TkFixedFont", 10, "bold")
        ).grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 5))

        self.config_text = tk.Text(f, wrap="none", font=("TkFixedFont", 10))
        self.config_text.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)

    
    # Applies MATRIX colors/styles to widgets needing post-creation adjustments.
    def apply_matrix_widgets(self):
        def walk(widget):
            for child in widget.winfo_children():
                try:
                    if isinstance(child, tk.Text):
                        child.configure(bg="#010601", fg="#00ff66",
                                        insertbackground="#00ff66",
                                        selectbackground="#145214",
                                        selectforeground="#ffffff",
                                        relief="flat")
                    elif isinstance(child, tk.Listbox):
                        child.configure(bg="#010601", fg="#00ff66",
                                        selectbackground="#145214",
                                        selectforeground="#ffffff",
                                        relief="flat",
                                        highlightbackground="#0b3d0b",
                                        highlightcolor="#00aa44")
                except tk.TclError:
                    pass
                walk(child)
        walk(self)

    
    # Changes the message shown in the bottom status bar.
    def set_status(self, text):
        self.status_var.set(text)
        self.update_idletasks()


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Runs slow work in a thread, then returns to Tkinter's thread to update the GUI.
    def run_async(
        self,
        cmd,
        output_widget=None,
        privileged=False,
        timeout=120,
        show_error_popup=True,
        refresh_after=True
    ):
        
        
        # Tkinter must not be blocked by slow system commands on its main thread.
        # System work therefore runs in the background, then UI updates return through after().
        def worker():
            actual = privileged_cmd(cmd) if privileged else cmd
            self.after(0, lambda: self.set_status("Exécution : " + shell_join(actual)))
            rc, out = run(actual, timeout=timeout)

            def done():
                if output_widget is not None:
                    output_widget.delete("1.0", "end")
                    output_widget.insert("end", out)

                    
                    
                    
                    if rc != 0 and not show_error_popup:
                        output_widget.insert(
                            "end",
                            f"\n\n--- Code de retour : {rc} ---\n"
                            "Note : smartctl utilise des codes de retour par bits; "
                            "un code non nul ne signifie pas nécessairement que la "
                            "lecture SMART a échoué.\n"
                        )

                self.set_status(f"Terminé (code {rc})")

                if refresh_after:
                    self.refresh_all()

                if rc != 0 and show_error_popup:
                    messagebox.showerror(
                        "Commande",
                        out[-3000:] if out else f"Code {rc}"
                    )

            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Refreshes all major views without requiring the user to switch tabs.
    def _startup_fast_refresh(self):

        
        
        # RAID/lsblk information is usually fast. SMART can take several
        #      seconds on systems containing many drives.
        self.set_status(
            f"MDADM Manager v{APP_VERSION} // ROOT // Chargement rapide…"
            if i18n.CURRENT_LANGUAGE != "en"
            else f"MDADM Manager v{APP_VERSION} // ROOT // Fast loading…"
        )
        self.refresh_arrays()
        self.refresh_disks(allow_smart_query=False)
        self.refresh_create_disks()

        if hasattr(self, "manage_array") and self.manage_array.get().strip():
            self.refresh_manage_members(self.manage_array.get().strip())

        
        self.start_smart_refresh_background()

    def start_smart_refresh_background(self):

        if getattr(self, "_smart_scan_running", False):
            return

        self._smart_scan_running = True

        def worker():
            try:
                devices = get_block_devices()
                paths = []
                for d in devices:
                    if d.get("type") != "disk":
                        continue
                    path = clean_device_path(d.get("path", ""))
                    if path:
                        paths.append(path)

                total = len(paths)

                for index, path in enumerate(paths, 1):
                    
                    data = smart_usage_metrics(path)
                    self.smart_metrics_cache[path] = {
                        "timestamp": time.time(),
                        "data": data,
                    }

                    
                    
                    self.after(
                        0,
                        lambda i=index, n=total: self.set_status(
                            f"SMART : {i}/{n}"
                        )
                    )

            finally:
                self._smart_scan_running = False

                def finish():
                    
                    
                    self.refresh_disks(allow_smart_query=False)
                    self.set_status(
                        f"MDADM Manager v{APP_VERSION} // ROOT // Rafraîchissement 15 s // Prêt"
                        if i18n.CURRENT_LANGUAGE != "en"
                        else f"MDADM Manager v{APP_VERSION} // ROOT // Refresh 15 s // Ready"
                    )

                self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def refresh_all(self):
        
        # Immediate fast refresh, followed by SMART in the background.
        if hasattr(self, "smart_metrics_cache"):
            self.smart_metrics_cache.clear()

        self.refresh_arrays()
        self.refresh_disks(allow_smart_query=False)
        self.refresh_create_disks()

        if hasattr(self, "manage_array") and self.manage_array.get().strip():
            self.refresh_manage_members(self.manage_array.get().strip())

        self.start_smart_refresh_background()

    
    # Schedules the next automatic refresh using Tkinter.after().
    def auto_refresh(self):
        self.refresh_arrays()
        self.after(self.refresh_ms, self.auto_refresh)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Rereads active arrays and updates the dashboard.
    def refresh_arrays(self, include_manage=True, allow_smart_query=True):
        arrays = get_md_arrays()

        current_path = self.selected_array.get().strip()
        if not current_path and self.arr_list.curselection():
            try:
                current_path = self.arr_list.get(self.arr_list.curselection()[0]).split()[0]
            except Exception:
                current_path = ""

        self.arr_list.delete(0, "end")
        names = []

        for a in arrays:
            names.append(a["path"])

            
            members, _ = parse_mdadm_members(a["path"])
            has_problem = any(m.get("problem") for m in members)
            has_warning = any(m.get("warning") for m in members)

            prefix = "●"
            line = f'{prefix} {a["path"]}   {a["level"]}   {a["state"]}'
            idx = self.arr_list.size()
            self.arr_list.insert("end", line)
            try:
                if has_problem:
                    self.arr_list.itemconfig(idx, fg="#ff3b3b")
                elif has_warning:
                    self.arr_list.itemconfig(idx, fg="#ffb000")
                else:
                    self.arr_list.itemconfig(idx, fg="#00ff66")
            except tk.TclError:
                pass

        
        
        # During staged startup, the Manage RAID tab may not exist yet.
        #      In that case, update only the Dashboard.
        manage_ready = (
            include_manage
            and hasattr(self, "manage_array")
            and hasattr(self, "manage_member_tree")
        )

        if manage_ready:
            self.manage_array["values"] = names

        if names:
            if manage_ready and self.manage_array.get() not in names:
                self.manage_array.set(names[0])

            target = current_path if current_path in names else names[0]
            self.selected_array.set(target)

            for i in range(self.arr_list.size()):
                if target in self.arr_list.get(i):
                    self.arr_list.selection_clear(0, "end")
                    self.arr_list.selection_set(i)
                    self.arr_list.activate(i)
                    break

            
            self.refresh_array_view(target, allow_smart_query=allow_smart_query)

            
            if manage_ready:
                self.refresh_manage_members(self.manage_array.get())
        else:
            self.selected_array.set("")
            self.summary_var.set("Aucun array mdadm actif détecté.")
            self.mount_var.set("Montage : —")
            self.member_tree.delete(*self.member_tree.get_children())

            if manage_ready:
                self.manage_member_tree.delete(
                    *self.manage_member_tree.get_children()
                )

    
    # Displays full details for the selected array and its members.
    def refresh_array_view(self, path, allow_smart_query=True):
        if not path:
            return

        members, detail = parse_mdadm_members(path)
        rc2, mdstat = run(["cat", "/proc/mdstat"], timeout=5)

        state = ""
        level = ""
        size = ""
        devices = ""
        failed = ""
        spare = ""

        for line in detail.splitlines():
            if "Raid Level" in line:
                level = line.split(":", 1)[1].strip()
            elif "State :" in line:
                state = line.split(":", 1)[1].strip()
            elif "Array Size" in line:
                size = line.split(":", 1)[1].strip()
            elif "Active Devices" in line:
                devices = line.split(":", 1)[1].strip()
            elif "Failed Devices" in line:
                failed = line.split(":", 1)[1].strip()
            elif "Spare Devices" in line:
                spare = line.split(":", 1)[1].strip()

        problems = sum(1 for m in members if m.get("problem"))
        warnings = sum(1 for m in members if m.get("warning"))
        health = "OK"
        if problems:
            health = f"PROBLÈME — {problems} disque(s)"
        elif warnings:
            health = f"ATTENTION — {warnings} disque(s)"

        self.summary_var.set(
            f"ARRAY : {path}    RAID : {level or '?'}    ÉTAT : {state or '?'}\n"
            f"TAILLE : {size or '?'}    ACTIFS : {devices or '?'}    "
            f"FAILED : {failed or '0'}    SPARE : {spare or '0'}    SANTÉ : {health}"
        )

        mount = get_array_mount_info(path)
        mountpoints = ", ".join(mount.get("mountpoints") or []) or "NON MONTÉ"
        fs = mount.get("fstype") or "—"
        label = mount.get("label") or "—"
        uuid = mount.get("uuid") or "—"
        source = mount.get("source") or path

        usage = ""
        if mount.get("size"):
            usage = (
                f"    ESPACE : {mount.get('used','?')} utilisés / "
                f"{mount.get('size','?')}    LIBRE : {mount.get('avail','?')} "
                f"({mount.get('use_percent','?')} utilisé)"
            )

        self.mount_var.set(
            f"MONTAGE : {mountpoints}    SOURCE : {source}    FS : {fs}    LABEL : {label}\n"
            f"UUID : {uuid}{usage}"
        )

        self.populate_member_tree(self.member_tree, path, members, allow_smart_query=allow_smart_query)

        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("end", detail)
        self.detail_text.insert("end", "\n\n--- INFORMATIONS DE MONTAGE ---\n")
        self.detail_text.insert("end", self.mount_var.get() + "\n")
        self.detail_text.insert("end", "\n--- /proc/mdstat ---\n")
        self.detail_text.insert("end", mdstat)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Builds a stable key from a Treeview row so selection can survive refreshes.
    def _member_key_from_values(self, values):

        if not values:
            return None

        shown = str(values[0])
        dev = shown
        if "  [/dev/" in dev:
            dev = dev.split("  [", 1)[0].strip()
        serial = str(values[5]).strip() if len(values) > 5 else ""
        slot = str(values[1]).strip() if len(values) > 1 else ""

        
        if serial and serial not in ("INCONNU", "—"):
            return ("serial", serial)
        return ("device", dev, slot)

    
    # Returns the stable key for the currently selected row.
    def _current_tree_selection_key(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        values = tree.item(sel[0], "values")
        return self._member_key_from_values(values)

    
    # Uses a small SMART cache to avoid unnecessarily rerunning smartctl on every refresh.
    def get_cached_smart_metrics(self, physical_path, allow_query=True):
        physical = clean_device_path(physical_path)
        if not physical:
            return {
                "reallocated": None,
                "pending": None,
                "uncorrectable": None,
                "media_errors": None,
                "bad_total": None,
                "power_hours": None,
                "power_days": None,
                "health": "INCONNU",
                "temperature": None,
                "percentage_used": None,
                "wear_percent": None,
                "wear_source": "",
                "index_kind": "wear",
                "disk_kind": "",
                "tb_written": None,
                "tbw_rating": None,
                "tbw_used_percent": None,
                "tbw_remaining_percent": None,
                "available": False,
            }

        now = time.time()
        cached = self.smart_metrics_cache.get(physical)

        if cached and (now - cached["timestamp"] < self.smart_metrics_cache_seconds):
            return cached["data"]

        
        
        # During fast startup, do not run smartctl here: this function is
        #      called once per disk and would otherwise block the GUI.
        if not allow_query:
            return {
                "reallocated": None,
                "pending": None,
                "uncorrectable": None,
                "media_errors": None,
                "bad_total": None,
                "power_hours": None,
                "power_days": None,
                "health": "INCONNU",
                "temperature": None,
                "percentage_used": None,
                "wear_percent": None,
                "wear_source": "",
                "index_kind": "wear",
                "disk_kind": "",
                "tb_written": None,
                "tbw_rating": None,
                "tbw_used_percent": None,
                "tbw_remaining_percent": None,
                "available": False,
            }

        data = smart_usage_metrics(physical)
        self.smart_metrics_cache[physical] = {
            "timestamp": now,
            "data": data,
        }
        return data

    
    # Fills a Treeview with array members and their hardware/SMART information.
    def populate_member_tree(self, tree, array_path, members=None, allow_smart_query=True):
        
        current_key = self._current_tree_selection_key(tree)

        if tree is self.member_tree and self.selected_member_key:
            current_key = self.selected_member_key
        elif (
            hasattr(self, "manage_member_tree")
            and tree is self.manage_member_tree
            and self.selected_manage_member_key
        ):
            current_key = self.selected_manage_member_key

        tree.delete(*tree.get_children())

        if members is None:
            members, _ = parse_mdadm_members(array_path)

        selected_item = None

        for m in members:
            dev = m.get("device") or ""
            info = physical_disk_info(dev) if dev else {}
            size = self.human_size(info.get("size", 0)) if info.get("size") else "—"
            model = info.get("model") or "INCONNU"
            serial = info.get("serial") or "INCONNU"
            physical = info.get("physical_path") or dev

            smart = self.get_cached_smart_metrics(physical, allow_query=allow_smart_query) if dev else {}
            bad_total = smart.get("bad_total")
            reallocated = smart.get("reallocated")
            pending = smart.get("pending")
            uncorrectable = smart.get("uncorrectable")
            power_hours = smart.get("power_hours")
            power_days = smart.get("power_days")

            if bad_total is None:
                bad_display = "—"
            else:
                bad_display = str(bad_total)

            if isinstance(power_hours, int) and power_days is not None:
                usage_display = f"{power_hours:,} h / {power_days:,.1f} {'d' if i18n.CURRENT_LANGUAGE == 'en' else 'j'}".replace(",", " ")
            else:
                usage_display = "—"

            display_dev = dev if dev else "(disque retiré/manquant)"
            if dev and physical and physical != dev:
                display_dev = f"{dev}  [{physical}]"

            tag = "problem" if m.get("problem") else ("warning" if m.get("warning") else "ok")

            
            if tag == "ok" and isinstance(bad_total, int) and bad_total > 0:
                tag = "warning"

            if not dev:
                tag = "removed"

            item = tree.insert(
                "", "end",
                values=(
                    display_dev,
                    m.get("slot", "?"),
                    m.get("state", "?"),
                    size,
                    model,
                    serial,
                    (f"{smart.get('temperature')} °C" if smart.get("temperature") is not None else "—"),
                    bad_display,
                    usage_display,
                ),
                tags=(tag,)
            )

            values = tree.item(item, "values")
            key = self._member_key_from_values(values)
            if current_key and key == current_key:
                selected_item = item

        
        if selected_item:
            tree.selection_set(selected_item)
            tree.focus(selected_item)
            tree.see(selected_item)

    
    # Callback when the user selects an array on the Dashboard.
    def on_array_select(self, _event=None):
        sel = self.arr_list.curselection()
        if not sel:
            return
        raw = self.arr_list.get(sel[0])
        m = re.search(r"(/dev/md\d+)", raw)
        if not m:
            return
        path = m.group(1)
        self.selected_array.set(path)

        if hasattr(self, "manage_array"):
            self.manage_array.set(path)

        self.selected_member_key = None
        if hasattr(self, "selected_manage_member_key"):
            self.selected_manage_member_key = None

        self.refresh_array_view(path)

        if hasattr(self, "manage_array") and hasattr(self, "manage_member_tree"):
            self.refresh_manage_members(path)

    
    # Callback when the user selects an array in Manage RAID.
    def on_manage_array_select(self, _event=None):
        path = self.manage_array.get().strip()
        if not path:
            return
        self.selected_array.set(path)
        self.selected_member_key = None
        self.selected_manage_member_key = None
        self.refresh_manage_members(path)

    
    # Reloads members of the array currently being managed.
    def refresh_manage_members(self, path=None):
        path = (path or self.manage_array.get()).strip()
        if not path:
            return
        members, _ = parse_mdadm_members(path)
        self.populate_member_tree(self.manage_member_tree, path, members)

    
    # Converts the selected Treeview row into usable member information.
    def selected_member_from_tree(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        values = tree.item(sel[0], "values")
        if not values:
            return None
        dev = str(values[0])
        if "  [/dev/" in dev:
            dev = dev.split("  [", 1)[0].strip()
        dev = clean_device_path(dev) if not dev.startswith("(") else ""
        return {
            "device": dev,
            "slot": str(values[1]),
            "state": str(values[2]),
            "size": str(values[3]),
            "model": str(values[4]),
            "serial": str(values[5]),
        }

    
    # Returns the member currently selected in the relevant view.
    def get_selected_member(self):
        
        member = self.selected_member_from_tree(self.manage_member_tree)
        if member:
            return member
        return self.selected_member_from_tree(self.member_tree)

    
    # Updates buttons/information when a member is selected on the Dashboard.
    def on_member_select(self, _event=None):
        member = self.selected_member_from_tree(self.member_tree)
        if not member:
            self.selected_member_var.set("Aucun disque sélectionné")
            return

        self.selected_member_key = self._current_tree_selection_key(self.member_tree)

        dev = member["device"] or "(retiré/manquant)"
        self.selected_member_var.set(
            f"Sélection : {dev}    Slot {member['slot']}    État : {member['state']}"
        )

        
        path = self.selected_array.get().strip()
        if path:
            self.manage_array.set(path)
            self.refresh_manage_members(path)

            target_key = self.selected_member_key
            for item in self.manage_member_tree.get_children():
                vals = self.manage_member_tree.item(item, "values")
                if self._member_key_from_values(vals) == target_key:
                    self.manage_member_tree.selection_set(item)
                    self.manage_member_tree.focus(item)
                    self.manage_member_tree.see(item)
                    self.selected_manage_member_key = target_key
                    break

    
    # Updates action state when a member is selected in Manage RAID.
    def on_manage_member_select(self, _event=None):
        member = self.selected_member_from_tree(self.manage_member_tree)
        if member:
            self.selected_manage_member_key = self._current_tree_selection_key(self.manage_member_tree)

            dev = member["device"] or "(retiré/manquant)"
            self.set_status(
                f"Disque sélectionné : {dev} // {member['state']} // slot {member['slot']}"
            )

    
    # Shows detailed mdadm output for the array selected on the Dashboard.
    def dashboard_details(self):
        path = self.selected_array.get().strip()
        if path:
            self.run_async(["mdadm", "--detail", path], self.detail_text)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Rebuilds the full disk inventory and updates the Disks tab.
    def refresh_disks(self, allow_smart_query=True):
        devices = get_block_devices()
        membership = get_raid_membership_map()

        
        old_selected_path = ""
        sel = self.disk_tree.selection()
        if sel:
            vals = self.disk_tree.item(sel[0], "values")
            if vals:
                old_selected_path = str(vals[0])

        self.disk_tree.delete(*self.disk_tree.get_children())
        selected_item = None

        for d in devices:
            if d.get("type") != "disk":
                continue

            path = clean_device_path(d.get("path", ""))
            if not path:
                continue

            size = d.get("size") or 0
            try:
                size_txt = self.human_size(int(size))
            except Exception:
                size_txt = str(size)

            
            raid_entries = membership.get(path, [])

            if raid_entries:
                raid_txt = ", ".join(sorted(set(x["array"] for x in raid_entries)))
                member_txt = ", ".join(sorted(set(x["member"] for x in raid_entries)))
                state_txt = " | ".join(
                    f'{x["state"]} (slot {x["slot"]})'
                    for x in raid_entries
                )
            else:
                raid_txt = "—"
                member_txt = "—"
                state_txt = "—"

            # ---------- SMART ----------
            metrics = self.get_cached_smart_metrics(path, allow_query=allow_smart_query)
            health = metrics.get("health", "INCONNU")

            bad = metrics.get("bad_total")
            bad_txt = "—" if bad is None else str(bad)

            hours = metrics.get("power_hours")
            days = metrics.get("power_days")
            if isinstance(hours, int) and days is not None:
                usage_txt = f"{hours:,} h / {days:,.1f} {'d' if i18n.CURRENT_LANGUAGE == 'en' else 'j'}".replace(",", " ")
            else:
                usage_txt = "—"

            wear = metrics.get("wear_percent")
            wear_source = metrics.get("wear_source") or ""
            index_kind = metrics.get("index_kind") or "wear"
            if wear is None:
                wear_txt = "—"
            elif index_kind == "risk":
                wear_txt = f"Risque {wear:.1f}%"
            else:
                wear_txt = f"Usure {wear:.1f}%"

            # ---------- Filesystem / mount ----------
            mounts = d.get("mountpoints") or []
            mounttxt = (
                ", ".join([m for m in mounts if m])
                if isinstance(mounts, list)
                else str(mounts or "")
            )
            fstype = d.get("fstype", "") or ""

            
            child_fs = []
            child_mounts = []
            for child in d.get("children") or []:
                cfs = child.get("fstype") or ""
                cpath = child.get("path") or child.get("name") or ""
                cmounts = child.get("mountpoints") or []

                if cfs:
                    child_fs.append(f"{cpath}:{cfs}")

                if isinstance(cmounts, list):
                    for mnt in cmounts:
                        if mnt:
                            child_mounts.append(f"{cpath}:{mnt}")

            if not fstype and child_fs:
                fstype = " | ".join(child_fs)

            if not mounttxt and child_mounts:
                mounttxt = " | ".join(child_mounts)

            
            tag = "ok"

            if any(x.get("problem") for x in raid_entries):
                tag = "problem"
            elif health == "ÉCHEC":
                tag = "problem"
            elif health == "ATTENTION":
                tag = "warning"
            elif any(x.get("warning") for x in raid_entries):
                tag = "warning"
            elif isinstance(bad, int) and bad > 0:
                tag = "warning"
            elif (
                isinstance(wear, (int, float))
                and metrics.get("index_kind") == "risk"
                and wear >= 60
            ):
                tag = "warning"
            elif (
                isinstance(wear, (int, float))
                and metrics.get("index_kind") != "risk"
                and wear >= 80
            ):
                tag = "warning"

            item = self.disk_tree.insert(
                "", "end",
                values=(
                    path,
                    size_txt,
                    d.get("model", "") or "",
                    d.get("serial", "") or "",
                    (f"{metrics.get('temperature')} °C" if metrics.get("temperature") is not None else "—"),
                    raid_txt,
                    member_txt,
                    state_txt,
                    health,
                    bad_txt,
                    usage_txt,
                    wear_txt,
                    fstype,
                    mounttxt,
                ),
                tags=(tag,)
            )

            if old_selected_path and path == old_selected_path:
                selected_item = item

        if selected_item:
            self.disk_tree.selection_set(selected_item)
            self.disk_tree.focus(selected_item)
            self.disk_tree.see(selected_item)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Refreshes disks usable by the legacy creation screen.
    def refresh_create_disks(self):
        
        if not hasattr(self, "create_disks"):
            return

        devices = get_block_devices()
        try:
            self.create_disks.delete(0, "end")
        except Exception:
            return

        membership = get_raid_membership_map()

        for d in devices:
            if d.get("type") != "disk":
                continue

            path = clean_device_path(d.get("path", ""))
            if not path:
                continue

            try:
                size = self.human_size(int(d.get("size") or 0))
            except Exception:
                size = "—"

            model = d.get("model") or ""
            serial = d.get("serial") or ""
            raids = membership.get(path, [])
            raid_txt = ",".join(sorted({x.get("array", "") for x in raids if x.get("array")}))

            flags = []
            if raid_txt:
                flags.append(f"RAID={raid_txt}")

            for child in d.get("children") or []:
                if child.get("fstype"):
                    flags.append(f"FS={child.get('fstype')}")
                mounts = child.get("mountpoints") or []
                if isinstance(mounts, list) and any(mounts):
                    flags.append("MONTÉ")

            suffix = f" [{' '.join(flags)}]" if flags else " [DISPONIBLE]"
            self.create_disks.insert(
                "end",
                f"{path:<12} {size:<10} {model:<24} {serial}{suffix}"
            )

    @staticmethod
    
    # Converts a byte count into a human-readable size (GiB/TiB).
    def human_size(n):
        units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
        x = float(n)
        for u in units:
            if x < 1024 or u == units[-1]:
                return f"{x:.1f} {u}"
            x /= 1024.0

    
    # Returns paths selected in the main creation screen.
    def selected_create_paths(self):
        paths = []
        for idx in self.create_disks.curselection():
            line = self.create_disks.get(idx)
            paths.append(line.split()[0])
        return paths

    
    # Builds the mdadm creation command from main-screen selections.
    def build_create_cmd(self):
        name = self.create_name.get().strip()
        if not re.fullmatch(r"md\d+", name):
            raise ValueError("Le nom doit être du type md20.")
        level = self.create_level.get().strip()
        disks = self.selected_create_paths()
        if len(disks) < 2:
            raise ValueError("Sélectionne au moins deux disques.")

        protected = []
        for dev in disks:
            memberships = raid_protection_memberships(dev)
            if memberships:
                arrays = ", ".join(sorted({
                    e.get("array", "") for e in memberships if e.get("array")
                }))
                protected.append(f"{dev} → {arrays or 'RAID existant'}")

        if protected:
            raise ValueError(
                "PROTECTION RAID : création bloquée.\n"
                "Les périphériques suivants appartiennent déjà à un RAID :\n"
                + "\n".join(protected)
            )

        protected_fstab = []
        for dev in disks:
            entries = fstab_protection_entries(dev)
            if entries:
                targets = ", ".join(sorted({
                    e.get("target", "") for e in entries if e.get("target")
                }))
                protected_fstab.append(
                    f"{dev} → {targets or '/etc/fstab'}"
                )

        if protected_fstab:
            raise ValueError(
                "PROTECTION FSTAB : création bloquée.\n"
                "Les périphériques suivants sont référencés dans /etc/fstab :\n"
                + "\n".join(protected_fstab)
            )

        min_by_level = {
            "raid0": 2,
            "raid1": 2,
            "raid5": 3,
            "raid6": 4,
            "raid10": 4,
        }
        if len(disks) < min_by_level.get(level, 2):
            raise ValueError(f"{level} nécessite au moins {min_by_level[level]} disques.")

        cmd = [
            "mdadm", "--create", f"/dev/{name}",
            "--verbose",
            "--level", level.replace("raid", ""),
            "--raid-devices", str(len(disks)),
            "--metadata", self.create_meta.get(),
            "--chunk", self.create_chunk.get(),
        ]
        if self.create_bitmap.get() and level != "raid0":
            cmd += ["--bitmap=internal"]
        cmd += disks
        return cmd

    
    # Shows the creation command before any write occurs.
    def preview_create(self):
        try:
            cmd = self.build_create_cmd()
        except Exception as exc:
            messagebox.showerror("Création", str(exc))
            return
        messagebox.showinfo("Commande mdadm", shell_join(cmd))

    
    # Performs final safety validation and starts array creation.
    def create_array(self):
        try:
            cmd = self.build_create_cmd()
        except Exception as exc:
            messagebox.showerror("Création", str(exc))
            return

        name = self.create_name.get().strip()
        disks = self.selected_create_paths()

        text = (
            "Cette opération va CRÉER un nouveau RAID et écrire des métadonnées "
            "sur les disques suivants :\n\n"
            + "\n".join(disks)
            + "\n\nCommande :\n"
            + shell_join(cmd)
        )

        dlg = ConfirmDialog(self, "Création RAID", text, confirm_token=name)
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(cmd, self.manage_output, privileged=True, timeout=600)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Returns the path of the array currently selected in Manage RAID.
    def current_manage_array(self):
        p = self.manage_array.get().strip() or self.selected_array.get().strip()
        if not p:
            messagebox.showerror("Gestion", "Aucun array sélectionné.")
            return None
        return p

    
    # Displays 'mdadm --detail' for the selected array.
    def manage_details(self):
        p = self.current_manage_array()
        if p:
            self.run_async(["mdadm", "--detail", p], self.manage_output)

    
    # Attempts to assemble the selected array.
    def manage_assemble(self):
        p = self.current_manage_array()
        if not p:
            return
        cmd = ["mdadm", "--assemble", "--run", p]
        if messagebox.askyesno("Assembler", f"Exécuter :\n{shell_join(cmd)} ?"):
            self.run_async(cmd, self.manage_output, privileged=True)

    
    # Stops an array safely after confirmation.
    def manage_stop(self):
        p = self.current_manage_array()
        if not p:
            return
        dlg = ConfirmDialog(
            self,
            "Arrêter l'array",
            f"Arrêter {p} ?\n\nAssure-toi qu'aucun système de fichiers n'est monté depuis cet array.",
            confirm_token=Path(p).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", "--stop", p], self.manage_output, privileged=True)

    
    # Starts an array consistency check.
    def manage_check(self):
        p = self.current_manage_array()
        if not p:
            return
        sync_action = f"/sys/block/{Path(p).name}/md/sync_action"
        cmd = ["sh", "-c", f"echo check > {shlex.quote(sync_action)}"]
        if messagebox.askyesno("Check RAID", f"Lancer une vérification sur {p} ?"):
            self.run_async(cmd, self.manage_output, privileged=True)

    
    # Starts a controlled repair/resync where supported by mdadm.
    def manage_repair(self):
        p = self.current_manage_array()
        if not p:
            return
        sync_action = f"/sys/block/{Path(p).name}/md/sync_action"
        cmd = ["sh", "-c", f"echo repair > {shlex.quote(sync_action)}"]
        dlg = ConfirmDialog(
            self,
            "Repair RAID",
            f"Lancer un repair sur {p} ?\n\nCette opération peut réécrire des blocs.",
            confirm_token=Path(p).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(cmd, self.manage_output, privileged=True)

    
    # Asks the user for a device path using a small dialog.
    def ask_device(self, title):
        value = simpledialog.askstring(title, "Périphérique (ex. /dev/sdb1 ou /dev/sdb) :", parent=self)
        if not value:
            return None
        value = value.strip()
        if not value.startswith("/dev/"):
            messagebox.showerror(title, "Le périphérique doit commencer par /dev/.")
            return None
        return value

    
    # Adds a device as member/spare after safety checks.
    def manage_add(self):
        p = self.current_manage_array()
        if not p:
            return
        dev = self.ask_device("Ajouter membre")
        if not dev:
            return
        cmd = ["mdadm", p, "--add", dev]
        if messagebox.askyesno("Ajouter membre", f"Exécuter :\n{shell_join(cmd)} ?"):
            self.run_async(cmd, self.manage_output, privileged=True, timeout=120)

    
    # Removes a member only when array state and confirmations allow it.
    def manage_remove(self):
        p = self.current_manage_array()
        if not p:
            return
        dev = self.ask_device("Retirer membre")
        if not dev:
            return
        dlg = ConfirmDialog(
            self,
            "Retirer membre",
            f"Retirer {dev} de {p} ?\n\nCommande :\nmdadm {p} --remove {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--remove", dev], self.manage_output, privileged=True)

    
    # Explicitly marks the selected member faulty after confirmation.
    def manage_faulty(self):
        p = self.current_manage_array()
        if not p:
            return
        dev = self.ask_device("Marquer faulty")
        if not dev:
            return
        dlg = ConfirmDialog(
            self,
            "Marquer faulty",
            f"Marquer {dev} comme défaillant dans {p} ?",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--fail", dev], self.manage_output, privileged=True)

    
    # Clears old mdadm metadata only after all safety checks and confirmations.
    def manage_zero_superblock(self):
        dev = self.ask_device("Zero superblock")
        if not dev:
            return

        protection = protected_raid_message(dev)
        if protection:
            messagebox.showerror(
                "PROTECTION RAID — OPÉRATION BLOQUÉE",
                protection,
                parent=self
            )
            return

        fstab_protection = protected_fstab_message(dev)
        if fstab_protection:
            messagebox.showerror(
                "PROTECTION FSTAB — OPÉRATION BLOQUÉE",
                fstab_protection,
                parent=self
            )
            return

        dlg = ConfirmDialog(
            self,
            "EFFACER SUPERBLOCK MD",
            f"Cette opération supprime les métadonnées mdadm de {dev}.\n\n"
            "Protection RAID : aucune appartenance RAID active détectée.\n\n"
            f"Commande : mdadm --zero-superblock {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            
            
            protection = protected_raid_message(dev)
            if protection:
                messagebox.showerror(
                    "PROTECTION RAID — ÉTAT MODIFIÉ",
                    protection,
                    parent=self
                )
                return

            fstab_protection = protected_fstab_message(dev)
            if fstab_protection:
                messagebox.showerror(
                    "PROTECTION FSTAB — ÉTAT MODIFIÉ",
                    fstab_protection,
                    parent=self
                )
                return

            self.run_async(
                ["mdadm", "--zero-superblock", dev],
                self.manage_output,
                privileged=True
            )

    
    # Opens SMART information for the currently selected member.
    def member_smart(self, _event=None):
        member = self.get_selected_member()
        if not member or not member.get("device"):
            messagebox.showinfo("SMART", "Sélectionne d'abord un disque membre valide.")
            return
        self.show_smart_for_path(member["device"])

    
    # Dashboard shortcut to mark the selected member faulty.
    def member_faulty(self):
        p = self.manage_array.get().strip() or self.selected_array.get().strip()
        member = self.get_selected_member()
        if not p or not member or not member.get("device"):
            messagebox.showinfo("FAULTY", "Sélectionne d'abord un disque membre du RAID.")
            return

        dev = member["device"]
        if "faulty" in member["state"].lower() or "failed" in member["state"].lower():
            messagebox.showinfo("FAULTY", f"{dev} est déjà indiqué comme défaillant.")
            return

        dlg = ConfirmDialog(
            self,
            "Marquer le disque FAULTY",
            f"Array : {p}\nDisque : {dev}\nÉtat actuel : {member['state']}\n\n"
            f"Commande :\nmdadm {p} --fail {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--fail", dev], self.manage_output, privileged=True)

    
    # Dashboard shortcut to remove the selected member.
    def member_remove(self):
        p = self.manage_array.get().strip() or self.selected_array.get().strip()
        member = self.get_selected_member()
        if not p or not member or not member.get("device"):
            messagebox.showinfo("Retirer", "Sélectionne d'abord un disque membre du RAID.")
            return

        dev = member["device"]
        low = member["state"].lower()
        if "active" in low and "faulty" not in low and "failed" not in low:
            messagebox.showwarning(
                "Retirer",
                f"{dev} semble encore ACTIF.\n\n"
                "Marque-le d'abord FAULTY avant de le retirer, sauf si tu sais exactement ce que tu fais."
            )
            return

        dlg = ConfirmDialog(
            self,
            "Retirer le disque du RAID",
            f"Array : {p}\nDisque : {dev}\nÉtat : {member['state']}\n\n"
            f"Commande :\nmdadm {p} --remove {dev}",
            confirm_token=Path(dev).name
        )
        self.wait_window(dlg)
        if dlg.result:
            self.run_async(["mdadm", p, "--remove", dev], self.manage_output, privileged=True)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Collects and displays detailed SMART information for a /dev path.
    def show_smart_for_path(self, path):
        if not shutil.which("smartctl"):
            messagebox.showerror(
                "SMART",
                "smartctl n'est pas installé.\nInstalle smartmontools."
            )
            return

        member = clean_device_path(path)
        smart_path, error = resolve_smart_device(member)

        if error:
            messagebox.showerror(
                "SMART — périphérique introuvable",
                f"Membre RAID : {member or path}\n\n{error}\n\n"
                "La liste des RAID va être rafraîchie."
            )
            self.refresh_all()
            return

        
        info = physical_disk_info(member)
        model = (info.get("model") or "INCONNU").strip()
        serial = (info.get("serial") or "INCONNU").strip()

        metrics = smart_usage_metrics(smart_path)
        bad_total = metrics.get("bad_total")
        reallocated = metrics.get("reallocated")
        pending = metrics.get("pending")
        uncorrectable = metrics.get("uncorrectable")
        media_errors = metrics.get("media_errors")
        power_hours = metrics.get("power_hours")
        power_days = metrics.get("power_days")
        temperature = metrics.get("temperature")
        percentage_used = metrics.get("percentage_used")
        wear_percent = metrics.get("wear_percent")
        wear_source = metrics.get("wear_source") or ""
        index_kind = metrics.get("index_kind") or "wear"
        disk_kind = metrics.get("disk_kind") or "INCONNU"
        tb_written = metrics.get("tb_written")
        tbw_rating = metrics.get("tbw_rating")
        tbw_used = metrics.get("tbw_used_percent")
        tbw_remaining = metrics.get("tbw_remaining_percent")
        temperature_min = metrics.get("temperature_min")
        temperature_max = metrics.get("temperature_max")
        power_cycle_count = metrics.get("power_cycle_count")
        start_stop_count = metrics.get("start_stop_count")
        load_cycle_count = metrics.get("load_cycle_count")
        spin_retry_count = metrics.get("spin_retry_count")
        reported_uncorrectable = metrics.get("reported_uncorrectable")
        command_timeout = metrics.get("command_timeout")
        udma_crc_errors = metrics.get("udma_crc_errors")
        total_lbas_written = metrics.get("total_lbas_written")
        total_lbas_read = metrics.get("total_lbas_read")
        smart_health = metrics.get("health", "INCONNU")

        def metric(v):
            return "—" if v is None else str(v)

        if isinstance(power_hours, int) and power_days is not None:
            usage_text = (f"{power_hours:,} hours / {power_days:,.1f} days" if i18n.CURRENT_LANGUAGE == "en" else f"{power_hours:,} heures / {power_days:,.1f} jours").replace(",", " ")
        else:
            usage_text = "—"

        
        
        smart_path = clean_device_path(smart_path)
        if not smart_path or not Path(smart_path).exists():
            messagebox.showerror(
                "SMART — sécurité",
                f"Le périphérique résolu n'existe pas : {smart_path or '(vide)'}"
            )
            self.refresh_all()
            return

        win = tk.Toplevel(self)
        win.title(f"SMART - {smart_path}")
        win.geometry("980x680")
        win.transient(self)
        win.lift()

        header = ttk.Frame(win)
        header.pack(fill="x", padx=8, pady=8)

        
        
        # Some fields do not apply to every drive type. Show an explanation
        #      instead of an ambiguous dash.
        
        # Bilingual SMART display strings.
        is_en = i18n.CURRENT_LANGUAGE == "en"

        if disk_kind == "HDD":
            nvme_wear_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
            tb_written_text = (
                f"{tb_written:.2f} TB"
                if tb_written is not None
                else ("Not reported by SMART on this HDD" if is_en else "Non fourni par SMART sur ce HDD")
            )
            endurance_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
            tbw_used_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
            tbw_remaining_text = "Not applicable (HDD)" if is_en else "Non applicable (HDD)"
        else:
            nvme_wear_text = (
                f"{percentage_used} %"
                if percentage_used is not None
                else (
                    "Not reported" if (is_en and disk_kind == "NVMe")
                    else "Not applicable" if is_en
                    else "Non fourni" if disk_kind == "NVMe"
                    else "Non applicable"
                )
            )
            tb_written_text = (
                f"{tb_written:.2f} TB"
                if tb_written is not None
                else ("Not reported by SMART" if is_en else "Non fourni par SMART")
            )
            endurance_text = (
                f"{tbw_rating:.0f} TBW"
                if tbw_rating is not None
                else ("Manufacturer rating unknown" if is_en else "Valeur constructeur inconnue")
            )
            tbw_used_text = (
                f"{tbw_used:.2f}%"
                if tbw_used is not None
                else (
                    "Cannot calculate without manufacturer TBW"
                    if is_en
                    else "Calcul impossible sans TBW constructeur"
                )
            )
            tbw_remaining_text = (
                f"{tbw_remaining:.2f}%"
                if tbw_remaining is not None
                else (
                    "Cannot calculate without manufacturer TBW"
                    if is_en
                    else "Calcul impossible sans TBW constructeur"
                )
            )

        
        # Additional SMART information actually reported by the drive.
        extra_lines = []

        def add_extra(fr_label, en_label, value):
            if value is not None:
                extra_lines.append(f"{en_label if is_en else fr_label}: {value}")

        add_extra("Cycles alimentation", "Power cycles", power_cycle_count)
        add_extra("Cycles démarrage/arrêt", "Start/stop cycles", start_stop_count)
        add_extra("Cycles chargement/déchargement", "Load/unload cycles", load_cycle_count)
        add_extra("Tentatives de rotation", "Spin retry count", spin_retry_count)
        add_extra("Non corrigibles signalés", "Reported uncorrectable", reported_uncorrectable)
        add_extra("Timeout commandes", "Command timeouts", command_timeout)
        add_extra("Erreurs CRC UDMA", "UDMA CRC errors", udma_crc_errors)
        add_extra("Total LBA écrits", "Total LBAs written", total_lbas_written)
        add_extra("Total LBA lus", "Total LBAs read", total_lbas_read)

        if temperature_min is not None or temperature_max is not None:
            lo = "—" if temperature_min is None else temperature_min
            hi = "—" if temperature_max is None else temperature_max
            extra_lines.append(
                f"{'Temperature min/max' if is_en else 'Température min/max'}: {lo}/{hi} °C"
            )

        extra_text = ""
        if extra_lines:
            extra_text = (
                "\n\n"
                + ("AVAILABLE SMART DETAILS" if is_en else "DÉTAILS SMART DISPONIBLES")
                + "\n"
                + "\n".join(extra_lines)
            )

        if is_en:
            smart_text = (
                f"RAID MEMBER: {member}\n"
                f"PHYSICAL DISK: {smart_path}\n"
                f"MODEL: {model}\n"
                f"SERIAL NO.: {serial}\n"
                f"SMART: {smart_health}\n"
                f"ERRORS / SECTORS: {metric(bad_total)} "
                f"(reallocated {metric(reallocated)}, pending {metric(pending)}, "
                f"uncorrectable {metric(uncorrectable)}, NVMe media {metric(media_errors)})\n"
                f"USAGE: {usage_text}\n"
                f"TEMPERATURE: {metric(temperature)} °C    "
                f"NVMe WEAR: {nvme_wear_text}\n"
                f"TYPE: {disk_kind}\n"
                f"{'HDD RISK INDEX' if index_kind == 'risk' else 'SMART WEAR'}: "
                f"{'—' if wear_percent is None else f'{wear_percent:.1f}%'}\n"
                f"SOURCE: {wear_source or 'Unavailable'}\n"
                f"TB WRITTEN: {tb_written_text}\n"
                f"ENDURANCE: {endurance_text}\n"
                f"TBW USED: {tbw_used_text}\n"
                f"TBW REMAINING: {tbw_remaining_text}\n"
                f"NOTE: "
                f"{'Statistical monitoring index, not remaining drive life.' if index_kind == 'risk' else 'SMART/manufacturer endurance value when available.'}"
                f"{extra_text}"
            )
        else:
            smart_text = (
                f"MEMBRE RAID : {member}\n"
                f"DISQUE PHYSIQUE : {smart_path}\n"
                f"MODÈLE : {model}\n"
                f"N° SÉRIE : {serial}\n"
                f"SMART : {smart_health}\n"
                f"ERREURS / SECTEURS : {metric(bad_total)} "
                f"(réalloués {metric(reallocated)}, en attente {metric(pending)}, "
                f"non corrigibles {metric(uncorrectable)}, média NVMe {metric(media_errors)})\n"
                f"UTILISATION : {usage_text}\n"
                f"TEMPÉRATURE : {metric(temperature)} °C    "
                f"USURE NVMe : {nvme_wear_text}\n"
                f"TYPE : {disk_kind}\n"
                f"{'INDICE DE RISQUE HDD' if index_kind == 'risk' else 'USURE SMART'} : "
                f"{'—' if wear_percent is None else f'{wear_percent:.1f}%'}\n"
                f"SOURCE : {wear_source or 'Non disponible'}\n"
                f"TB ÉCRITS : {tb_written_text}\n"
                f"ENDURANCE : {endurance_text}\n"
                f"TBW UTILISÉ : {tbw_used_text}\n"
                f"TBW RESTANT : {tbw_remaining_text}\n"
                f"NOTE : "
                f"{'Indice statistique de surveillance, pas une durée de vie restante.' if index_kind == 'risk' else 'Valeur SMART/endurance constructeur lorsqu’elle est disponible.'}"
                f"{extra_text}"
            )

        ttk.Label(
            header,
            text=smart_text,
            justify="left",
            font=("TkFixedFont", 10, "bold")
        ).pack(anchor="w")

        txt = tk.Text(win, wrap="none", font=("TkFixedFont", 10))
        txt.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.apply_matrix_widgets()

        
        
        self.run_async(
            ["smartctl", "-a", smart_path],
            txt,
            privileged=True,
            timeout=60,
            show_error_popup=False,
            refresh_after=False
        )


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Replacement workflow: validates old member, proposes a new disk, and prepares the mdadm sequence.
    def replace_selected_member(self):








        array_path = self.manage_array.get().strip() or self.selected_array.get().strip()
        member = self.get_selected_member()

        if not array_path:
            messagebox.showinfo("Remplacement", "Sélectionne d'abord un RAID.")
            return
        if not member:
            messagebox.showinfo("Remplacement", "Sélectionne le disque à remplacer.")
            return

        old_dev = member.get("device") or ""
        old_state = member.get("state") or "unknown"
        old_slot = member.get("slot") or "?"

        current_members, _ = parse_mdadm_members(array_path)
        member_paths = [m.get("device") for m in current_members if m.get("device")]
        candidates = get_candidate_replacement_devices(exclude=member_paths)

        if not candidates:
            messagebox.showwarning(
                "Remplacement",
                "Aucun autre disque ou partition candidat n'a été détecté."
            )
            return

        win = tk.Toplevel(self)
        win.title(f"Remplacer un disque — {array_path}")
        win.geometry("840x560")
        win.transient(self)
        win.grab_set()
        win.configure(bg="#020802")

        outer = ttk.Frame(win)
        outer.pack(fill="both", expand=True, padx=12, pady=12)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        old_label = old_dev if old_dev else f"(membre manquant, slot {old_slot})"
        ttk.Label(
            outer,
            text="ASSISTANT DE REMPLACEMENT DE DISQUE",
            font=("TkFixedFont", 13, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        ttk.Label(
            outer,
            text=(
                f"RAID : {array_path}\n"
                f"Ancien membre : {old_label}\n"
                f"Slot : {old_slot}\n"
                f"État : {old_state}"
            ),
            font=("TkFixedFont", 10)
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        ttk.Label(
            outer,
            text="Choisis le nouveau périphérique :",
            font=("TkFixedFont", 10, "bold")
        ).grid(row=2, column=0, sticky="w")

        cols = ("path", "type", "size", "model", "status")
        tree = ttk.Treeview(outer, columns=cols, show="headings")
        for col, title, width in [
            ("path", "Périphérique", 150),
            ("type", "Type", 70),
            ("size", "Taille", 100),
            ("model", "Modèle", 250),
            ("status", "Attention", 190),
        ]:
            tree.heading(col, text=title)
            tree.column(col, width=width, anchor="w")
        tree.grid(row=3, column=0, sticky="nsew", pady=8)

        for c in candidates:
            status = []
            if c["mounted"]:
                status.append("MONTÉ")
            if c["fstype"]:
                status.append(f"FS={c['fstype']}")
            if not status:
                status.append("libre/non monté")
            tag = "problem" if c["mounted"] else ("warning" if c["fstype"] else "ok")
            tree.insert(
                "", "end",
                values=(
                    c["path"],
                    c["type"],
                    self.human_size(c["size"]),
                    c["model"] or "—",
                    ", ".join(status)
                ),
                tags=(tag,)
            )
        tree.tag_configure("ok", foreground="#00ff66")
        tree.tag_configure("warning", foreground="#ffb000")
        tree.tag_configure("problem", foreground="#ff3b3b")

        info = ttk.Label(
            outer,
            text=(
                "Le nouveau périphérique doit être préparé correctement. "
                "S'il est monté ou contient un système de fichiers, l'opération sera bloquée."
            ),
            wraplength=780
        )
        info.grid(row=4, column=0, sticky="w", pady=(2, 8))

        buttons = ttk.Frame(outer)
        buttons.grid(row=5, column=0, sticky="ew")
        buttons.columnconfigure(0, weight=1)

        def execute_replace():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Remplacement", "Sélectionne le nouveau périphérique.", parent=win)
                return

            vals = tree.item(sel[0], "values")
            new_dev = str(vals[0])
            cand = next((c for c in candidates if c["path"] == new_dev), None)
            if not cand:
                return

            if cand["mounted"]:
                messagebox.showerror(
                    "Remplacement",
                    f"{new_dev} est monté. Démonte-le avant de continuer.",
                    parent=win
                )
                return

            if cand["fstype"]:
                if not messagebox.askyesno(
                    "Périphérique contenant des données",
                    f"{new_dev} contient un système de fichiers ({cand['fstype']}).\n\n"
                    "mdadm peut écraser ses métadonnées. Continuer quand même ?",
                    parent=win
                ):
                    return

            commands = []
            low = old_state.lower()

            if old_dev:
                if "faulty" not in low and "failed" not in low:
                    commands.append(["mdadm", array_path, "--fail", old_dev])
                commands.append(["mdadm", array_path, "--remove", old_dev])

            commands.append(["mdadm", array_path, "--add", new_dev])

            command_preview = "\n".join(shell_join(c) for c in commands)
            token = Path(new_dev).name

            dlg = ConfirmDialog(
                win,
                "CONFIRMER LE REMPLACEMENT",
                f"RAID : {array_path}\n"
                f"Ancien : {old_label}\n"
                f"Nouveau : {new_dev}\n\n"
                "Les commandes suivantes seront exécutées dans cet ordre :\n\n"
                f"{command_preview}\n\n"
                "Après l'ajout, mdadm devrait lancer automatiquement la reconstruction "
                "si le niveau RAID le permet.",
                confirm_token=token
            )
            win.wait_window(dlg)
            if not dlg.result:
                return

            win.destroy()
            self.run_replace_sequence(commands, array_path, old_label, new_dev)

        ttk.Button(buttons, text="Annuler", command=win.destroy).pack(side="right")
        ttk.Button(
            buttons,
            text="REMPLACER LE DISQUE",
            command=execute_replace
        ).pack(side="right", padx=(0, 8))

        self.apply_matrix_widgets()

    
    # Runs replacement commands sequentially and stops on the first failure.
    def run_replace_sequence(self, commands, array_path, old_label, new_dev):
        def worker():
            log = []
            success = True

            for cmd in commands:
                self.after(0, lambda c=cmd: self.set_status("Remplacement : " + shell_join(c)))
                rc, out = run(cmd, timeout=180)
                log.append(f"$ {shell_join(cmd)}\n{out}\n")
                if rc != 0:
                    success = False
                    break

            output = "\n".join(log)

            def done():
                self.manage_output.delete("1.0", "end")
                self.manage_output.insert("end", output)
                self.refresh_all()

                if success:
                    self.set_status(f"Remplacement lancé : {old_label} -> {new_dev}")
                    messagebox.showinfo(
                        "Remplacement",
                        f"Le nouveau disque {new_dev} a été ajouté à {array_path}.\n\n"
                        "Surveille la progression de reconstruction dans /proc/mdstat."
                    )
                else:
                    self.set_status("Erreur pendant le remplacement")
                    messagebox.showerror(
                        "Remplacement",
                        "Une commande a échoué. La séquence a été arrêtée.\n\n"
                        + output[-4000:]
                    )

            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    
    # Opens SMART information for the disk selected in Disks.
    def show_smart(self):
        sel = self.disk_tree.selection()
        if not sel:
            messagebox.showinfo("SMART", "Sélectionne un disque.")
            return
        path = self.disk_tree.item(sel[0], "values")[0]
        self.show_smart_for_path(path)


    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------

    
    # Loads /etc/mdadm/mdadm.conf into the text editor.
    def load_config(self):
        path = Path("/etc/mdadm/mdadm.conf")
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            self.config_text.delete("1.0", "end")
            self.config_text.insert("1.0", content)
            self.config_loaded_path = str(path)
            self.config_file_var.set(
                f"Fichier actuellement chargé : {path}  //  {len(content.splitlines())} lignes"
            )
            self.set_status(f"Configuration chargée : {path}")
            messagebox.showinfo(
                "mdadm.conf chargé",
                f"Configuration chargée avec succès.\n\n"
                f"Fichier : {path}\n"
                f"Nombre de lignes : {len(content.splitlines())}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Erreur de chargement",
                f"Impossible de charger {path}\n\n{exc}"
            )

    
    # Asks mdadm to scan arrays and places the result in the editor.
    def scan_config(self):
        rc, out = run(["mdadm", "--detail", "--scan"], timeout=30)
        if rc != 0:
            messagebox.showerror("Scan", out)
            return
        current = self.config_text.get("1.0", "end").strip()
        if current:
            current += "\n\n"
        self.config_text.delete("1.0", "end")
        self.config_text.insert("end", current + out.strip() + "\n")

    
    # Safely saves editor contents into mdadm.conf.
    def save_config(self):
        path = Path("/etc/mdadm/mdadm.conf")
        content = self.config_text.get("1.0", "end-1c")

        if not messagebox.askyesno(
            "Confirmer l'écriture",
            f"Le contenu affiché va être écrit dans :\n\n{path}\n\n"
            "Une copie de sécurité horodatée sera créée avant l'écriture.\n\nContinuer ?"
        ):
            return

        try:
            import datetime
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = Path(f"/etc/mdadm/mdadm.conf.backup-{stamp}")

            if path.exists():
                shutil.copy2(path, backup)

            if content and not content.endswith("\n"):
                content += "\n"
            path.write_text(content, encoding="utf-8")
            path.chmod(0o644)

            self.config_loaded_path = str(path)
            self.config_file_var.set(f"Fichier actuellement chargé : {path}")
            self.set_status(f"mdadm.conf sauvegardé : {path}")

            backup_text = str(backup) if backup.exists() else "Aucune"
            messagebox.showinfo(
                "Sauvegarde terminée",
                f"Configuration enregistrée.\n\n"
                f"Fichier : {path}\n"
                f"Copie de sécurité : {backup_text}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Erreur de sauvegarde",
                f"Impossible d'enregistrer {path}\n\n{exc}"
            )

    
    # Exports a copy of the configuration to a user-selected file.
    def export_config(self):
        content = self.config_text.get("1.0", "end-1c")

        filename = filedialog.asksaveasfilename(
            title="Sauvegarder une copie de mdadm.conf",
            initialfile="mdadm.conf",
            defaultextension=".conf",
            filetypes=[
                ("Configuration mdadm", "*.conf"),
                ("Tous les fichiers", "*.*"),
            ]
        )

        if not filename:
            self.set_status("Sauvegarde de copie annulée.")
            return

        try:
            out = Path(filename)
            if content and not content.endswith("\n"):
                content += "\n"
            out.write_text(content, encoding="utf-8")

            self.set_status(f"Copie sauvegardée : {out}")
            messagebox.showinfo(
                "Copie sauvegardée",
                f"La copie a été créée avec succès.\n\nEmplacement :\n{out}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Erreur de sauvegarde",
                f"Impossible de sauvegarder la copie.\n\n{exc}"
            )




# =============================================================================
