"""System command and privilege helpers for MDADM Manager."""

import os
import sys
import shlex
import shutil
import subprocess
from pathlib import Path

#   run, shell_join, privileged_cmd, find_kdesu, relaunch_as_root
#
