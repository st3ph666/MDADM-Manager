"""Tkinter GUI for MDADM Manager."""

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

#   install_tk_translation_hooks, ConfirmDialog
#

#   RaidCreationWizard
#

#   MdadmManager
#
