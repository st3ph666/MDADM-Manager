# MDADM Manager

**MDADM Manager** is a Matrix-style graphical RAID management, monitoring and recovery application for Linux built around `mdadm`.

> ⚠️ **BETA SOFTWARE** — RAID operations can cause permanent data loss. Keep verified backups and review every destructive action before confirming it.

---

## Current Version

### **v1.76 — FULL / MODULAR**

v1.76 is the current reference engine. The repository also includes the `mdadm_matrix/` modular package, whose launcher loads the v1.76 engine so the application can be refactored progressively without dropping current features or RAID safeguards.

Current engine:

```text
mdadm_manager_v1.76.py
```

Modular package:

```text
mdadm_matrix/
```

The repository keeps only the current active application at its root. Older releases remain available through Git history and are documented in [CHANGELOG.md](CHANGELOG.md).

---

## Screenshots

![MDADM Manager 1](screenshots/1.png)

![MDADM Manager 2](screenshots/2.png)

![MDADM Manager 3](screenshots/3.png)

![MDADM Manager 4](screenshots/4.png)

![MDADM Manager 5](screenshots/5.png)

![MDADM Manager 6](screenshots/6.png)

---

## Main features

- RAID array detection, monitoring and management;
- member state, RAID slot and physical disk identity tracking;
- SMART information, disk diagnostics and HDD/SSD/NVMe health data;
- CRC trend monitoring that distinguishes old stable counters from active increases;
- cable / SATA connection assistant;
- guided hot-swap workflow with safety checks and explicit hardware confirmation;
- previous RAID member reintegration;
- automatic recognition of the same reconnected disk using remembered slot/serial information instead of relying only on `/dev/sdX`;
- Array UUID and mdadm metadata validation before reintegration;
- read-only reintegration diagnostics;
- `mdadm --re-add` workflow for a valid previous member;
- live recovery / rebuild / resync / reshape / check / repair progress;
- RAID creation and management tools;
- filesystem, mount, RAID membership and `/etc/fstab` protections;
- superblock inspection and guarded cleanup;
- confirmation dialogs before sensitive operations;
- French / English interface support;
- root relaunch through KDE `kdesu`, with `pkexec` fallback;
- modular `mdadm_matrix` architecture.

---

## v1.76 recovery workflow

v1.76 strengthens the maintenance path for the common case where a RAID disk is removed because of a SATA cable or connection problem and the **same physical disk** is later reconnected.

The application records and compares RAID slot information, disk serial identity and mdadm metadata. The device name is not treated as a stable identity because Linux can assign a different `/dev/sdX` name after a disconnect or hot-swap.

The cable / SATA & hot-swap assistant performs its safety analysis before enabling hot-swap preparation. Physical removal is only presented after explicit confirmation that the exact bay, port or backplane supports SATA hot-swap.

For reintegration, the diagnostic path is read-only. When the selected disk is validated as the expected previous member, MDADM Manager can perform the controlled `mdadm --manage <array> --re-add <device>` operation.

---

## Modular architecture

```text
mdadm_manager_v1.76.py        # current complete v1.76 engine
mdadm_matrix/
├── __init__.py
├── __main__.py
├── main.py
├── full_engine.py
├── app.py
├── assistant.py
├── core.py
├── crc_assistant.py
├── crc_monitor.py
├── gui_common.py
├── i18n.py
├── rebuild_monitor.py
├── rebuild_ui.py
├── replacement.py
├── system.py
└── wizard.py
```

`full_engine.py` is the compatibility bridge to `mdadm_manager_v1.76.py`. Existing modules can be migrated progressively while the current engine remains the functional reference.

---

## Installation

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-tk mdadm smartmontools util-linux git curl policykit-1
```

For KDE Plasma root elevation:

```bash
sudo apt install -y kde-cli-tools
```

Clone the repository:

```bash
git clone https://github.com/st3ph666/MDADM-Manager.git
cd MDADM-Manager
```

### Run the current v1.76 engine

```bash
python3 mdadm_manager_v1.76.py
```

The application will request root elevation when needed.

### Run through the modular package

```bash
python3 -m mdadm_matrix
```

### Run with uv

```bash
uv sync
uv run python mdadm_manager_v1.76.py
```

or:

```bash
uv run python -m mdadm_matrix
```

### Update an existing installation

```bash
git pull
uv sync
uv run python mdadm_manager_v1.76.py
```

---

## Safety model

MDADM Manager is designed to put checks immediately before sensitive writes. Depending on the operation, these include RAID membership checks, filesystem and mount checks, `/etc/fstab` protection, mdadm superblock/UUID checks, remembered physical disk identity, candidate validation and explicit confirmation dialogs.

Hot-swap support in the software does **not** make unsupported SATA hardware hot-swappable. The exact controller, port, bay/backplane and firmware/BIOS configuration must support hot-swap before physically disconnecting a powered disk.

These protections reduce operational mistakes but do not replace verified backups.

---

## Version history

See [CHANGELOG.md](CHANGELOG.md) for published milestones and the v1.76 release notes.

**Current release: v1.76 FULL / MODULAR**
