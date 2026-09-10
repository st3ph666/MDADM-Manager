"""RAID discovery, SMART analysis, and safety helpers."""

import math
import re
import shutil
from pathlib import Path

from .system import run

#   get_md_arrays, get_block_devices, get_raid_membership_map,
#   clean_device_path, physical_disk_info, block_device_info,
#   parse_mdadm_members, get_candidate_replacement_devices,
#   get_array_mount_info
#

#   resolve_smart_device, detect_disk_kind, hdd_risk_index,
#   samsung_870_evo_tbw_rating, total_lbas_written_to_tb,
#   smart_usage_metrics
#

#   resolve_fstab_source, get_fstab_entries, device_family_paths,
#   fstab_protection_entries, protected_fstab_message,
#   raid_protection_memberships, protected_raid_message,
#   mdadm_examine_superblock, candidate_member_paths_for_cleanup,
#   safe_orphan_superblocks
#
