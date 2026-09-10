"""System command and privilege helpers for MDADM Manager."""

import os
import sys
import shlex
import shutil
import subprocess
from pathlib import Path

# =============================================================================


# Runs a system command without a shell, captures stdout/stderr, and protects the app with a timeout.
def run(cmd, timeout=20):
    try:
        p = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False
        )
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except Exception as exc:
        return 1, str(exc)



# Turns an argument list into a safely quoted readable command, mainly for kdesu.
def shell_join(cmd):
    return " ".join(shlex.quote(str(x)) for x in cmd)



# Central hook intended to prepare a command that requires root privileges.
def privileged_cmd(cmd):
    return list(cmd)




# Looks for the kdesu executable in several possible KDE locations.
def find_kdesu():

    candidates = [
        shutil.which("kdesu"),
        shutil.which("kdesu5"),
        shutil.which("kdesu6"),
        "/usr/lib/x86_64-linux-gnu/libexec/kf6/kdesu",
        "/usr/lib/x86_64-linux-gnu/libexec/kf5/kdesu",
        "/usr/libexec/kf6/kdesu",
        "/usr/libexec/kf5/kdesu",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None



# Relaunches this same script with administrator rights using kdesu, then pkexec as fallback.
def relaunch_as_root():

    script = str(Path(__file__).resolve())
    python_exe = sys.executable or "/usr/bin/python3"

    
    kdesu = find_kdesu()
    if kdesu:
        command = shell_join([python_exe, script])
        try:
            subprocess.Popen([kdesu, "-c", command])
            return True, "kdesu"
        except Exception:
            pass

    # Secours PolicyKit.
    pkexec = shutil.which("pkexec")
    if pkexec:
        cmd = [pkexec, "env"]
        for var in ("DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR"):
            value = os.environ.get(var)
            if value:
                cmd.append(f"{var}={value}")
        cmd += [python_exe, script]

        try:
            subprocess.Popen(cmd)
            return True, "pkexec"
        except Exception:
            pass

    return False, None



# =============================================================================
