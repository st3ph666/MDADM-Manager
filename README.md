# MDADM Manager

**MDADM Manager** is a graphical RAID management and monitoring application for Linux built around `mdadm`.

It provides a Matrix-style graphical interface for RAID creation, monitoring, disk health inspection, SMART diagnostics, and common RAID maintenance tasks.

> ⚠️ **BETA SOFTWARE**
>
> This project performs privileged disk and RAID operations. Always keep verified backups of important data and carefully review operations before confirming destructive actions.

---

## Current Version

### **v1.58**

MDADM Manager v1.58 adds safer RAID member replacement and previous-member reintegration.

When a RAID slot is missing, the replacement assistant can identify a returning previous member using the array UUID and previous RAID slot. It also displays the RAID and disk event counters before reintegration.

For an exact previous-member match, the program preserves the existing mdadm superblock and attempts `mdadm --re-add` before offering a normal `--add`. A disk from the same array but a different previous slot, or a disk containing metadata from another array, is blocked from automatic reintegration.

---

## Modular Architecture

MDADM Manager uses a modular source layout with a small versioned compatibility launcher:

```text
mdadm_manager_v1.58.py      # Compatibility launcher
mdadm_matrix/
├── __init__.py             # Application version metadata
├── i18n.py                 # French / English interface translations
├── system.py               # System commands and privilege escalation
├── core.py                 # RAID discovery, SMART and safety checks
├── gui_common.py           # Shared Tkinter helpers
├── wizard.py               # RAID creation wizard
├── replacement.py          # RAID member replacement / reintegration
├── app.py                  # Main Tkinter application and RAID workflows
└── main.py                 # Application startup
```

---

## Main Features

- Graphical management of Linux `mdadm` RAID arrays
- RAID creation wizard
- RAID member detection and status display
- Safe previous-member reintegration with `--re-add`
- Array UUID and previous-slot validation before reintegration
- RAID/disk Events comparison
- Normal replacement workflow for new disks
- Protection against automatically using a member from the wrong RAID slot
- Disk and RAID health monitoring
- SMART monitoring for HDD, SATA SSD, and NVMe drives
- Disk temperature display
- SMART error and sector monitoring
- HDD statistical risk indicator
- SSD/NVMe wear and endurance information
- RAID member safety checks
- `/etc/fstab` protection checks
- RAID superblock protection checks
- French / English interface
- Progressive startup and background SMART scanning
- Matrix-style interface

---

## Installation and deployment with uv

### Debian / Ubuntu requirements

```bash
sudo apt update
sudo apt install -y python3 python3-tk mdadm smartmontools util-linux git curl
```

For KDE Plasma, the graphical privilege helper is recommended:

```bash
sudo apt install -y kde-cli-tools
```

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and initialize the project:

```bash
git clone https://github.com/st3ph666/MDADM-Manager.git
cd MDADM-Manager
uv sync
```

Run the current version:

```bash
uv run python mdadm_manager_v1.58.py
```

Do not run `uv sync` with `sudo`.

### Updating an existing installation

```bash
git pull
uv sync
uv run python mdadm_manager_v1.58.py
```

### Traditional launch without uv

```bash
python3 mdadm_manager_v1.58.py
```

---

## RAID member reintegration in v1.58

When a RAID contains a `removed` member and the original disk becomes visible again, MDADM Manager analyzes candidate devices with `mdadm --examine`.

An exact previous member requires:

- matching Array UUID;
- matching previous RAID device slot;
- readable mdadm metadata.

The interface displays the physical disk, model, serial number, previous role, disk Events, RAID Events, and the Events difference.

For an exact match, the first command attempted is:

```bash
mdadm --manage /dev/mdX --re-add /dev/sdXN
```

The existing superblock is preserved. If `--re-add` fails, the program shows the mdadm error and requires explicit confirmation before a normal `--add` is attempted.

A candidate belonging to the same array but to a different previous slot is blocked from automatic reintegration. Metadata belonging to another array is also protected from automatic overwrite.

---

## Safety

MDADM Manager performs operations on physical disks and RAID arrays. Incorrect RAID operations can cause permanent data loss.

The application includes RAID membership checks, filesystem/mount checks, `/etc/fstab` protection, mdadm superblock checks, and confirmations before sensitive operations. These protections do not replace verified backups.

---

## Development

MDADM Manager is actively developed and tested on Linux. Bug reports and testing feedback are welcome, especially RAID level, disk models, kernel/distribution version, error output, screenshots, and reproducible steps.

**Current release: v1.58**
