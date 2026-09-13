# MDADM Manager

**MDADM Manager** is a graphical RAID management and monitoring application for Linux built around `mdadm`.

> ⚠️ **BETA SOFTWARE** — RAID operations can cause permanent data loss. Keep verified backups and review every destructive action before confirming it.

---

## Current Version

### **v1.61**

Version 1.61 fixes and improves the live rebuild display introduced in v1.60.

### v1.61 — Rebuild progress fix

- fixes `/proc/mdstat` rebuild percentage detection;
- shows rebuild percentage directly with a rebuilding member when available;
- keeps the dedicated REBUILD / RESYNC progress panel;
- displays current percentage, reconstructed blocks, speed and estimated remaining time;
- refreshes progress continuously while the operation is active;
- detects recovery, resync, reshape, check and repair operations.

Example:

```text
/dev/sdd1   slot 1   spare rebuilding — 42.7%

REBUILD / RESYNC — PROGRESSION
RECOVERY : 42.7 %
Blocs : 417 000 000 / 976 620 544   |   Vitesse : 128.6 MB/s   |   Temps restant : ~54 min
```

---

## Recent improvements

### v1.60 — Rebuild monitoring

Introduced the live Spare / Rebuild progress monitor based on `/proc/mdstat`.

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
mdadm_manager_v1.61.py
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
uv run python mdadm_manager_v1.61.py
```

### Run with system Python

```bash
python3 mdadm_manager_v1.61.py
```

### Update an existing installation

```bash
git pull
uv sync
uv run python mdadm_manager_v1.61.py
```

---

## Safety

MDADM Manager includes RAID membership checks, filesystem/mount checks, `/etc/fstab` protections, mdadm superblock checks, and confirmation dialogs before sensitive operations. These protections do not replace backups.

**Current release: v1.61**
