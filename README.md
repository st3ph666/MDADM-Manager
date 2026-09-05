# MDADM Manager

**MDADM Manager** is a graphical RAID management and monitoring application for Linux built around `mdadm`.

> **⚠️ BETA SOFTWARE**
>
> This project performs privileged disk and RAID operations. Always keep verified backups of important data and carefully review the generated commands before confirming destructive operations.

## Current Beta

**v1.29-beta**

The project is currently in public beta. Features and interface elements may change, and additional testing on different Linux distributions and storage configurations is welcome.

## Features

- Graphical Matrix-style interface
- RAID monitoring and management
- Guided RAID creation wizard
- RAID 0, RAID 1, RAID 5, RAID 6 and RAID 10
- Physical disk and RAID member information
- HDD, SATA SSD and NVMe SMART information
- HDD monitoring risk index based on age and relevant SMART attributes
- SSD/NVMe wear information when exposed by SMART
- Samsung 870 EVO TBW usage calculation when supported
- RAID member replacement workflow
- Array mount information
- `/etc/mdadm/mdadm.conf` viewing and management
- RAID level information and diagrams
- French and English interface
- Automatic graphical privilege elevation
- Existing RAID member protection
- Active `/etc/fstab` protection
- Safe detection of old mdadm superblocks
- Confirmation before destructive metadata cleanup
- Disk availability analysis before RAID creation

## Safety Protections

MDADM Manager includes several safeguards intended to reduce accidental data loss.

A disk is protected from destructive RAID creation or metadata cleanup when it is detected as belonging to an active RAID or when the disk or one of its partitions is referenced by an active `/etc/fstab` entry.

Commented `/etc/fstab` entries beginning with `#` or `##` are ignored.

Before removing an old mdadm superblock, the application examines the selected device, checks RAID and FSTAB protection again, displays the detected metadata, and requests confirmation.

These safeguards **do not replace backups**.

## Requirements

MDADM Manager is currently developed and tested primarily for Debian-based Linux systems.

### Debian 13 / Debian-based systems

```bash
sudo apt update
sudo apt install mdadm smartmontools python3-tk polkitd pkexec kde-cli-tools
```

Main requirements:

- Python 3
- Tkinter
- `mdadm`
- `smartmontools`
- `lsblk`
- `blkid`
- `udevadm`
- `pkexec` or KDE `kdesu` for graphical privilege elevation

No external Python packages installed through `pip` are currently required.

## Installation

Download or clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/MDADM-Manager.git
cd MDADM-Manager
```

Make the program executable:

```bash
chmod +x mdadm_manager_v1.29.py
```

Run it:

```bash
./mdadm_manager_v1.29.py
```

The application will attempt to request administrator privileges graphically when required.

You can also start it from a terminal:

```bash
python3 mdadm_manager_v1.29.py
```

## Language

The interface supports:

- English
- Français

The selected language is stored locally in:

```text
~/.config/mdadm-manager/language.conf
```

Some translations may still be refined during the beta period.

## SMART Monitoring

MDADM Manager can display SMART information for HDDs, SATA SSDs and NVMe drives when supported by the hardware and `smartctl`.

For HDDs, the displayed risk percentage is a **monitoring index**, not a prediction of remaining drive life. It combines power-on age with selected SMART warning indicators such as reallocated, pending and uncorrectable sectors.

For SSDs and NVMe devices, the application prefers actual wear/endurance values reported by SMART rather than estimating remaining life from power-on hours.

## RAID Creation Wizard

The RAID creation assistant guides the user through:

1. RAID level selection
2. Disk selection
3. RAID options
4. Final command review and confirmation

The wizard calculates an estimated usable capacity from the smallest selected member and prevents selection of protected RAID/FSTAB disks.

## Supported RAID Levels

| Level | Minimum disks | General purpose |
|---|---:|---|
| RAID 0 | 2 | Performance/capacity, no redundancy |
| RAID 1 | 2 | Mirroring |
| RAID 5 | 3 | Single-parity redundancy |
| RAID 6 | 4 | Dual-parity redundancy |
| RAID 10 | 4 recommended | Mirroring + striping |

RAID suitability depends on workload, hardware, backup strategy and failure requirements.

## Important Warning

Operations such as RAID creation, member replacement and superblock removal can cause permanent data loss when used incorrectly.

Before using destructive operations:

- Verify the selected device names.
- Verify that important data is backed up.
- Confirm that the disk does not contain data you need.
- Review the exact `mdadm` command displayed by the application.

## Bug Reports and Feature Requests

This is a beta release. Bug reports, hardware compatibility feedback and feature suggestions are welcome through GitHub Issues.

When reporting a problem, please include:

- Linux distribution and version
- MDADM Manager version
- `mdadm --version`
- Relevant RAID level
- Number/type of drives
- Error message or screenshot
- Steps needed to reproduce the issue

**Do not post sensitive disk contents, passwords, private keys or other confidential information.**

## Roadmap

Planned beta improvements include broader English translation coverage, additional validation and safety checks, UI refinements, testing on more Linux distributions, and continued SMART/RAID monitoring improvements.

## License

A license file will be added to the repository. Until a license is selected and published, normal copyright rules apply.

## Disclaimer

MDADM Manager is an independent open-source project and is not affiliated with the Linux kernel project, the `mdadm` maintainers, drive manufacturers, or Linux distribution vendors.

Use this software at your own risk. RAID is not a backup.
