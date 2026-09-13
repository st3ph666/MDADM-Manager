# MDADM Manager

**MDADM Manager** is a graphical RAID management and monitoring application for Linux built around `mdadm`.

It provides a Matrix-style graphical interface for RAID creation, monitoring, SMART diagnostics, disk health, and RAID maintenance.

> ⚠️ **BETA SOFTWARE**
>
> This project performs privileged disk and RAID operations. Always keep verified backups and review sensitive operations before confirming them.

---

## Current Version

### **v1.59**

MDADM Manager v1.59 adds intelligent SATA CRC trend monitoring and a guided maintenance assistant, while keeping the safer RAID reintegration workflow introduced in v1.58.

### CRC monitoring changes

A non-zero historical `UDMA_CRC_Error_Count` is no longer treated as an alert by itself.

The application now stores CRC history by disk identity and compares readings over time:

- stable historical CRC count → `OK`;
- isolated old value such as `1` → `OK`;
- +3 CRC errors or more within 10 minutes → `CRC À SURVEILLER — HAUSSE RAPIDE`;
- +10 CRC errors or more within 10 minutes → `CRC EN HAUSSE RAPIDE`.

The history is stored under the user's configuration directory in `~/.config/mdadm-manager/crc_history.json`.

### Guided diagnostic / maintenance assistant

The Manage RAID screen now includes an assistant entry point with two modes:

1. **Cable SATA / CRC / connection**
   - select a physical disk;
   - capture a reference CRC value;
   - capture a new value later;
   - compare the delta and elapsed time;
   - report whether the CRC count is stable or increasing rapidly.

2. **RAID disk**
   - reuses the existing safe RAID member replacement / reintegration workflow;
   - recognizes a returning previous member using Array UUID and previous slot;
   - shows disk/RAID Events before reintegration;
   - prefers `--re-add` for an exact previous-member match;
   - keeps normal replacement for a genuinely new disk.

---

## Modular Architecture

```text
mdadm_manager_v1.59.py      # Compatibility launcher
mdadm_matrix/
├── __init__.py             # Application version metadata
├── i18n.py                 # French / English interface translations
├── system.py               # System commands and privilege handling
├── core.py                 # RAID discovery, SMART and safety checks
├── gui_common.py           # Shared Tkinter helpers
├── wizard.py               # RAID creation wizard
├── replacement.py          # RAID member replacement / reintegration
├── crc_monitor.py          # Persistent CRC history and trend detection
├── crc_assistant.py        # Before/after CRC comparison assistant
├── assistant.py            # Diagnostic assistant selector
├── app.py                  # Main Tkinter application
└── main.py                 # Startup and feature installation
```

---

## Main Features

- Graphical management of Linux `mdadm` RAID arrays
- RAID creation wizard
- RAID member detection and status display
- Previous-member reintegration with `--re-add`
- Array UUID and previous-slot validation
- RAID/disk Events comparison
- Normal replacement workflow for new disks
- SMART monitoring for HDD, SATA SSD, and NVMe
- Disk temperature display
- Persistent CRC trend monitoring
- Guided CRC before/after comparison
- HDD statistical risk indicator
- SSD/NVMe wear and endurance information
- RAID member safety checks
- `/etc/fstab` and superblock protection checks
- French / English interface
- Progressive startup and background SMART scanning
- Matrix-style interface

---

## Installation with uv

### Debian / Ubuntu requirements

```bash
sudo apt update
sudo apt install -y python3 python3-tk mdadm smartmontools util-linux git curl
```

For KDE Plasma:

```bash
sudo apt install -y kde-cli-tools
```

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and initialize:

```bash
git clone https://github.com/st3ph666/MDADM-Manager.git
cd MDADM-Manager
uv sync
```

Run the current version:

```bash
uv run python mdadm_manager_v1.59.py
```

Do not run `uv sync` with `sudo`.

### Update an existing installation

```bash
git pull
uv sync
uv run python mdadm_manager_v1.59.py
```

### Traditional launch

```bash
python3 mdadm_manager_v1.59.py
```

---

## RAID member reintegration

When a RAID contains a `removed` member and the original disk becomes visible again, MDADM Manager analyzes candidate devices with `mdadm --examine`.

An exact previous member requires matching Array UUID, matching previous RAID slot, and readable mdadm metadata. The assistant shows model, serial, previous role, disk Events, RAID Events, and the Events difference before reintegration.

A candidate belonging to the same array but to a different previous slot is blocked from automatic reintegration. Metadata from another array is also protected from automatic overwrite.

---

## Safety

Incorrect RAID operations can cause permanent data loss. The application includes RAID membership checks, filesystem/mount checks, `/etc/fstab` protection, mdadm superblock checks, and confirmations before sensitive operations. These protections do not replace verified backups.

---

## Development

MDADM Manager is actively developed and tested on Linux. Bug reports and testing feedback are welcome.

**Current release: v1.59**
