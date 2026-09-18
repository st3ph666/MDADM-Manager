# Version History

## v1.76 — 2026-09-17

- promoted v1.76 as the current FULL / MODULAR release;
- improved RAID recovery after SATA cable or connection maintenance;
- strengthened the workflow for reconnecting and re-adding the same physical disk;
- added remembered RAID slot / disk identity handling so reintegration does not rely only on a changing `/dev/sdX` name;
- added read-only RAID re-add diagnostics before modification;
- improved previous-member candidate detection and controlled `mdadm --re-add` handling;
- expanded the cable / SATA & hot-swap assistant;
- added hot-swap safety analysis and explicit confirmation that the exact bay, port or backplane supports SATA hot-swap;
- retained CRC trend monitoring and live RAID recovery/rebuild/resync/reshape monitoring;
- updated the modular compatibility bridge to use the v1.76 engine;
- synchronized package metadata and documentation with v1.76;
- removed the obsolete v1.75 root scripts while preserving their history in Git.

This file preserves the visible release history of MDADM Manager. Older versions are no longer kept as active scripts at the repository root, but their changes remain documented here and in the Git history.

## v1.75 FULL — 2026-09-13

- consolidated the current FULL release;
- complete RAID management with safeguards before sensitive operations;
- reintegration of previous RAID members;
- RAID slot tracking, missing-member detection, and physical disk identity tracking;
- SMART tools and disk diagnostics;
- cable/SATA and hot-swap assistant;
- CRC monitoring;
- rebuild/recovery/resync/reshape progress monitoring;
- interface and maintenance improvements;
- new screenshot series;
- updated the modular architecture to use the v1.75 engine as its reference;
- synchronized `uv` metadata with v1.75.

## v1.62 to v1.74 — Intermediate Development Releases

These version numbers correspond to intermediate development stages that led to the v1.75 FULL script. Not all of them were published separately in the GitHub repository with an identifiable release commit. Their changes are therefore preserved in the consolidated FULL release rather than being artificially documented version by version.

This section can be expanded if the corresponding older scripts or release notes are later added to the repository.

## v1.61 — 2026-09-13

- fixed rebuild percentage detection from `/proc/mdstat`;
- displayed the rebuild percentage directly on the rebuilding member;
- added a dedicated REBUILD / RESYNC panel;
- displayed rebuilt blocks, speed, and estimated remaining time;
- added detection for recovery, resync, reshape, check, and repair operations.

## v1.60 — 2026-09-13

- added real-time RAID rebuild monitoring;
- added `/proc/mdstat` parsing;
- added a rebuild/resync progress panel.

## v1.59 — 2026-09-13

- added CRC trend monitoring;
- distinguished between an old stable CRC value and an actively increasing CRC count;
- added the CRC before/after assistant;
- added maintenance and replacement assistance.

## v1.58 — 2026-09-13

- added safe reintegration of a previous RAID member;
- added Array UUID validation;
- added previous RAID slot verification;
- added Events counter comparison;
- added `mdadm --re-add` attempts when a previous member matches exactly;
- added replacement candidate detection.

## v1.56 — 2026-09-13

- enabled the RAID member reintegration mechanism;
- integrated safe reintegration of previous members;
- updated the current launcher.

## v1.49 — 2026-09-10

- introduced the first major refactoring into `mdadm_matrix/`;
- separated major application components into modules;
- improved module-boundary detection;
- separated several GUI components;
- added `uv` configuration and deployment documentation.

## v1.48 RC1 — 2026-09-06

- published the RC1 release;
- established the RAID management, SMART, disk information, and Matrix interface foundation used by later releases.

## v1.29 — 2026-09-05

- first public beta release;
- RAID management and monitoring;
- RAID creation wizard;
- SMART information;
- RAID/FSTAB safeguards;
- safe removal of old superblocks with confirmation prompts.

---

## Policy for Future Releases

Starting with v1.75, every newly published version must add an entry to this file before or as part of the release commit. The repository may keep only the current script/launcher active, but the version history must never be removed.
