# MDADM Manager

**MDADM Manager** is a graphical RAID management and monitoring application for Linux built around `mdadm`.

> ⚠️ **BETA SOFTWARE** — RAID operations can cause permanent data loss. Keep verified backups and review every destructive action before confirming it.

---

## Current Version

### **v1.75 FULL**

The current release is the full MDADM Manager build with the latest RAID management, monitoring, SMART diagnostics, member reintegration, rebuild tracking, maintenance tools and interface improvements.

Main script:

```text
mdadm_manager_v1.75_full.py
```

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

- RAID array detection and monitoring;
- member status and slot tracking;
- SMART disk information and diagnostics;
- CRC monitoring and maintenance assistance;
- guided disk replacement workflows;
- previous RAID member reintegration with Array UUID validation;
- live rebuild / recovery / resync / reshape progress;
- RAID creation and management tools;
- filesystem, mount and `/etc/fstab` safety checks;
- confirmation dialogs before sensitive operations;
- modular `mdadm_matrix` architecture;
- Debian / Ubuntu support;
- `uv` and system Python launch methods.

---

## Modular architecture

```text
mdadm_manager_v1.75_full.py
mdadm_matrix/
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
uv run python mdadm_manager_v1.75_full.py
```

### Run with system Python

```bash
python3 mdadm_manager_v1.75_full.py
```

### Update an existing installation

```bash
git pull
uv sync
uv run python mdadm_manager_v1.75_full.py
```

---

## Safety

MDADM Manager includes RAID membership checks, filesystem and mount checks, `/etc/fstab` protections, mdadm superblock checks, and confirmation dialogs before sensitive operations. These protections do not replace verified backups.

**Current release: v1.75 FULL**
