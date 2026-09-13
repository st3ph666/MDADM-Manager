# MDADM Manager

**MDADM Manager** is a graphical RAID management and monitoring application for Linux built around `mdadm`.

> ⚠️ **BETA SOFTWARE** — RAID operations can cause permanent data loss. Keep verified backups and review every destructive action before confirming it.

---

## Current Version

### **v1.60**

Version 1.60 adds a live **Spare / Rebuild progress panel** to the RAID management screen.

The application now reads `/proc/mdstat` while a RAID operation is active and displays:

- rebuild/recovery/resync/reshape/check/repair state;
- live percentage;
- progress bar;
- reconstructed blocks versus total blocks;
- current rebuild speed;
- estimated remaining time when mdadm provides it.

The panel refreshes every second and automatically detects a rebuild that was already running before MDADM Manager was opened.

---

## Recent improvements

### v1.60 — Rebuild monitoring

During a rebuild, the Manage RAID screen can now show information such as:

```text
RECOVERY : 63.4%  |  142.7 MB/s  |  reste ~42 min
Blocs : 619200000 / 976620544
```

When no operation is active, the panel displays:

```text
Aucune reconstruction en cours
```

### v1.59 — CRC and maintenance assistant

- SMART CRC values are tracked over time instead of warning on a single historical value.
- A stable historical CRC count remains normal.
- CRC warnings are based on increases over time.
- The maintenance assistant provides guided cable/connection diagnostics and access to RAID disk replacement workflows.

### v1.58 — RAID member reintegration

- Detects a returning previous member using Array UUID and previous RAID slot.
- Compares disk Events with RAID Events.
- Attempts `mdadm --re-add` first for an exact previous-member match.
- Blocks automatic reintegration of a member belonging to a different slot or another array.

---

## Modular architecture

```text
mdadm_manager_v1.60.py
mdadm_matrix/
├── app.py
├── assistant.py
├── core.py
├── crc_assistant.py
├── crc_monitor.py
├── gui_common.py
├── i18n.py
├── main.py
├── rebuild_monitor.py
├── rebuild_ui.py
├── replacement.py
├── system.py
└── wizard.py
```

---

## Installation

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-tk mdadm smartmontools util-linux git curl
```

For KDE Plasma:

```bash
sudo apt install -y kde-cli-tools
```

Clone the repository:

```bash
git clone https://github.com/st3ph666/MDADM-Manager.git
cd MDADM-Manager
```

### Run with uv

```bash
uv sync
uv run python mdadm_manager_v1.60.py
```

### Run with system Python

```bash
python3 mdadm_manager_v1.60.py
```

### Update an existing installation

```bash
git pull
uv sync
uv run python mdadm_manager_v1.60.py
```

---

## Safety

MDADM Manager includes RAID membership checks, filesystem/mount checks, `/etc/fstab` protections, mdadm superblock checks, and confirmation dialogs before sensitive operations. These protections do not replace backups.

**Current release: v1.60**
