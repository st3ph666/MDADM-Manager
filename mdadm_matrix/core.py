"""RAID discovery, SMART analysis, and safety helpers."""

import math
import re
import shutil
from pathlib import Path

from .system import run

# =============================================================================


# Reads /proc/mdstat and returns the mdadm arrays that are currently assembled.
def get_md_arrays():

    arrays = []
    mdstat = Path("/proc/mdstat")
    if not mdstat.exists():
        return arrays
    text = mdstat.read_text(errors="replace")
    for line in text.splitlines():
        m = re.match(r"^(md\d+)\s*:\s*(\w+)\s+(\S+)\s+(.*)$", line)
        if m:
            name, state, level, rest = m.groups()
            arrays.append({
                "name": name,
                "path": f"/dev/{name}",
                "state": state,
                "level": level,
                "members": rest.strip(),
            })
    return arrays



# Uses lsblk JSON output to inventory disks, partitions, sizes, models, UUIDs, and mounts.
def get_block_devices():

    cmd = [
        "lsblk", "-J", "-b",
        "-o", "NAME,PATH,TYPE,SIZE,MODEL,SERIAL,FSTYPE,LABEL,UUID,MOUNTPOINTS"
    ]
    rc, out = run(cmd)
    if rc != 0:
        return []
    import json
    try:
        data = json.loads(out)
    except Exception:
        return []

    result = []

    
    # Recursively walks the lsblk JSON tree so no child partition/device is missed.
    def walk(nodes):
        for n in nodes:
            result.append(n)
            if n.get("children"):
                walk(n["children"])

    walk(data.get("blockdevices", []))
    return result






# Builds a reliable physical-disk -> RAID-member map from arrays that are actually assembled.
def get_raid_membership_map():

    """
    Construit une carte fiable des disques physiques -> membres mdadm.

    Exemple :
      /dev/sda -> [
        {
          array: /dev/md10,
          member: /dev/sda1,
          state: active sync set-A,
          slot: 0
        }
      ]

    Cette méthode ne dépend PAS du champ FSTYPE=linux_raid_member.
    Elle interroge les arrays mdadm réellement assemblés.
    """
    mapping = {}

    for array in get_md_arrays():
        array_path = array.get("path", "")
        if not array_path:
            continue

        members, _detail = parse_mdadm_members(array_path)

        for m in members:
            member = clean_device_path(m.get("device", ""))
            if not member:
                continue

            physical = member

            
            rc, parent = run(["lsblk", "-ndo", "PKNAME", member], timeout=8)
            parent = parent.strip().splitlines()[0].strip() if rc == 0 and parent.strip() else ""

            if parent:
                physical = parent if parent.startswith("/dev/") else f"/dev/{parent}"

            physical = clean_device_path(physical)
            if not physical:
                continue

            mapping.setdefault(physical, []).append({
                "array": array_path,
                "member": member,
                "state": m.get("state", "unknown"),
                "slot": m.get("slot", "?"),
                "problem": bool(m.get("problem")),
                "warning": bool(m.get("warning")),
            })

    return mapping



# Extracts a real /dev/... path from display text that may contain extra information.
def clean_device_path(value):




    value = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    m = re.search(r"(/dev/[A-Za-z0-9._+\-]+)", value)
    return m.group(1) if m else ""



# =============================================================================

# =============================================================================


# Resolves the physical disk behind a RAID member before calling smartctl.
def resolve_smart_device(member_path):




    member = clean_device_path(member_path)
    if not member:
        return "", "Chemin de périphérique invalide."

    if not Path(member).exists():
        return "", f"Le membre RAID {member} n'existe pas."

    
    rc, out = run(["lsblk", "-ndo", "PKNAME", member], timeout=8)
    parent = out.strip().splitlines()[0].strip() if rc == 0 and out.strip() else ""

    if parent:
        physical = clean_device_path(parent if parent.startswith("/dev/") else f"/dev/{parent}")
    else:
        
        rc2, typ = run(["lsblk", "-ndo", "TYPE", member], timeout=8)
        physical = member if rc2 == 0 and typ.strip() == "disk" else ""

    if not physical:
        return "", f"Impossible de déterminer le disque physique de {member}."

    if not Path(physical).exists():
        return "", f"Le disque physique {physical} n'existe pas."

    return physical, ""





# Determines whether the device is NVMe, SSD, or HDD using its name and lsblk.
def detect_disk_kind(device_path):




    device = clean_device_path(device_path)
    if not device:
        return "INCONNU"

    if "/dev/nvme" in device.lower():
        return "NVMe"

    rc, rota = run(["lsblk", "-ndo", "ROTA", device], timeout=8)
    if rc == 0:
        rota = rota.strip()
        if rota == "0":
            return "SSD"
        if rota == "1":
            return "HDD"

    return "INCONNU"



# Computes an HDD risk index from age and SMART counters; it is not remaining lifetime.
def hdd_risk_index(power_hours, reallocated=None, pending=None,
                   uncorrectable=None, health="INCONNU"):













    score = 0.0

    
    
    if isinstance(power_hours, int) and power_hours >= 0:
        years = power_hours / 8760.0

        if years < 3:
            age_score = years * 2.0                 # 0 -> 6
        elif years < 5:
            age_score = 6.0 + (years - 3.0) * 7.0 # 6 -> 20
        elif years < 7:
            age_score = 20.0 + (years - 5.0) * 10.0 # 20 -> 40
        elif years < 9:
            age_score = 40.0 + (years - 7.0) * 12.5 # 40 -> 65
        else:
            age_score = 65.0 + (years - 9.0) * 5.0  # progression lente
        score += min(age_score, 80.0)

    
    # Small internal helper: checks whether a value is a strictly positive integer.
    def positive_int(v):
        return isinstance(v, int) and v > 0

    
    if positive_int(reallocated):
        score += min(22.0, 7.0 + 5.0 * math.log10(reallocated + 1))

    if positive_int(pending):
        score += min(35.0, 22.0 + 6.0 * math.log10(pending + 1))

    if positive_int(uncorrectable):
        score += min(40.0, 28.0 + 6.0 * math.log10(uncorrectable + 1))

    h = (health or "").upper()
    if "ÉCHEC" in h or "FAIL" in h:
        return 100.0
    if "ATTENTION" in h or "WARN" in h:
        score += 20.0

    return max(0.0, min(100.0, score))





# Returns the official TBW endurance rating matching a Samsung 870 EVO capacity.
def samsung_870_evo_tbw_rating(model, size_bytes):








    model_u = (model or "").upper()
    if "SAMSUNG" not in model_u or "870 EVO" not in model_u:
        return None

    try:
        gb = int(round(int(size_bytes) / 1_000_000_000))
    except Exception:
        return None

    ratings = {
        250: 150,
        500: 300,
        1000: 600,
        2000: 1200,
        4000: 2400,
    }

    
    nearest = min(ratings.keys(), key=lambda x: abs(x - gb))
    if abs(nearest - gb) <= max(20, nearest * 0.08):
        return ratings[nearest]
    return None



# Converts a SMART Total_LBAs_Written counter into decimal terabytes written.
def total_lbas_written_to_tb(raw_value, sector_size=512):




    try:
        raw = int(raw_value)
        if raw < 0:
            return None
        return (raw * sector_size) / 1_000_000_000_000
    except Exception:
        return None



# Centralizes SATA/NVMe SMART analysis and returns health, errors, temperature, hours, and wear/risk.
def smart_usage_metrics(device_path):



    result = {
        "reallocated": None,
        "pending": None,
        "uncorrectable": None,
        "media_errors": None,
        "bad_total": None,
        "power_hours": None,
        "power_days": None,
        "health": "INCONNU",
         "temperature": None,
        "temperature_min": None,
        "temperature_max": None,
        "percentage_used": None,
        "power_cycle_count": None,
        "start_stop_count": None,
        "load_cycle_count": None,
        "spin_retry_count": None,
        "reported_uncorrectable": None,
        "command_timeout": None,
        "udma_crc_errors": None,
        "total_lbas_written": None,
        "total_lbas_read": None,
        "wear_percent": None,
        "wear_source": "",
        "index_kind": "wear",
        "disk_kind": "",
        "tb_written": None,
        "tbw_rating": None,
        "tbw_used_percent": None,
        "tbw_remaining_percent": None,
        "available": False,
    }

    device = clean_device_path(device_path)
    if not device or not Path(device).exists() or not shutil.which("smartctl"):
        return result

    result["disk_kind"] = detect_disk_kind(device)

    rc_lsblk, lsblk_out = run(
        ["lsblk", "-dnbo", "MODEL,SIZE", device],
        timeout=8
    )
    model = ""
    size_bytes = None
    if rc_lsblk == 0 and lsblk_out.strip():
        line = lsblk_out.strip().splitlines()[0].strip()
        m = re.match(r"^(.*\S)\s+(\d+)$", line)
        if m:
            model = m.group(1).strip()
            try:
                size_bytes = int(m.group(2))
            except Exception:
                size_bytes = None

    rc, out = run(["smartctl", "-a", device], timeout=25)
    if not out or out == "TIMEOUT":
        return result

    low_out = out.lower()
    is_nvme = (
        "/dev/nvme" in device.lower()
        or "nvme version" in low_out
        or "smart/health information (nvme log" in low_out
    )

    if is_nvme:
        critical_warning = None
        m = re.search(r"Critical Warning:\s*(0x[0-9a-fA-F]+|\d+)", out, re.I)
        if m:
            try:
                critical_warning = int(m.group(1), 0)
            except Exception:
                pass

        if critical_warning == 0:
            result["health"] = "OK"
        elif critical_warning is not None:
            result["health"] = "ATTENTION"

        def nvme_int(label):
            m = re.search(rf"^{re.escape(label)}:\s*(.+)$", out, re.I | re.M)
            if not m:
                return None
            raw = m.group(1).replace(",", "").replace(" ", "")
            m2 = re.search(r"-?\d+", raw)
            if not m2:
                return None
            try:
                return int(m2.group(0))
            except ValueError:
                return None

        result["power_hours"] = nvme_int("Power On Hours")
        result["media_errors"] = nvme_int("Media and Data Integrity Errors")
        result["percentage_used"] = nvme_int("Percentage Used")
        result["power_cycle_count"] = nvme_int("Power Cycles")

        
        
        
        # NVMe commonly exposes "Data Units Written". Per NVMe, one unit is
        #      1000 × 512-byte blocks = 512,000 bytes, so written TB can be shown
        #      even when the manufacturer's TBW rating is unknown.
        data_units_written = nvme_int("Data Units Written")
        if isinstance(data_units_written, int):
            result["tb_written"] = (
                data_units_written * 512_000
            ) / 1_000_000_000_000
        if isinstance(result["percentage_used"], int):
            result["wear_percent"] = max(0.0, min(100.0, float(result["percentage_used"])))
            result["wear_source"] = "SMART NVMe Percentage Used"
            result["index_kind"] = "wear"

        m = re.search(r"^Temperature:\s*([+-]?\d+)", out, re.I | re.M)
        if m:
            try:
                result["temperature"] = int(m.group(1))
            except ValueError:
                pass

        if isinstance(result["media_errors"], int):
            result["bad_total"] = result["media_errors"]

        if isinstance(result["power_hours"], int):
            result["power_days"] = result["power_hours"] / 24.0

        if isinstance(result["media_errors"], int) and result["media_errors"] > 0:
            if result["health"] == "OK":
                result["health"] = "ATTENTION"


        result["available"] = True
        return result

    # ATA / SATA
    if "smart overall-health self-assessment test result: passed" in low_out:
        result["health"] = "OK"
    elif "smart health status: ok" in low_out:
        result["health"] = "OK"
    elif "passed" in low_out and "smart" in low_out:
        result["health"] = "OK"
    elif "failed" in low_out or "failing_now" in low_out:
        result["health"] = "ÉCHEC"

    values = {}
    for line in out.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        parts = stripped.split()
        if len(parts) >= 10 and parts[0].isdigit():
            name = parts[1]
            raw = " ".join(parts[9:])
            m = re.search(r"-?\d+", raw)
            if m:
                try:
                    values[name] = int(m.group(0))
                except ValueError:
                    pass

    
    # Internal helper returning the first available SMART attribute among several possible names.
    def first_value(*names):
        for name in names:
            if name in values:
                return values[name]
        return None

    result["reallocated"] = first_value("Reallocated_Sector_Ct", "Reallocated_Event_Count")
    result["pending"] = first_value("Current_Pending_Sector", "Current_Pending_Sector_Ct")
    result["uncorrectable"] = first_value("Offline_Uncorrectable", "Reported_Uncorrect")
    result["power_hours"] = first_value("Power_On_Hours", "Power_On_Hours_and_Msec")
    result["temperature"] = first_value("Temperature_Celsius", "Airflow_Temperature_Cel")
    result["power_cycle_count"] = first_value("Power_Cycle_Count")
    result["start_stop_count"] = first_value("Start_Stop_Count")
    result["load_cycle_count"] = first_value("Load_Cycle_Count", "Load_Unload_Cycle_Count")
    result["spin_retry_count"] = first_value("Spin_Retry_Count")
    result["reported_uncorrectable"] = first_value("Reported_Uncorrect", "Reported_Uncorrectable")
    result["command_timeout"] = first_value("Command_Timeout")
    result["udma_crc_errors"] = first_value("UDMA_CRC_Error_Count")
    result["total_lbas_written"] = first_value("Total_LBAs_Written", "Total_LBA_Written")
    result["total_lbas_read"] = first_value("Total_LBAs_Read", "Total_LBA_Read")

    
    tm = re.search(r"(?:Temperature_Celsius|Airflow_Temperature_Cel).*?\b(\d+)\s+\(Min/Max\s+(\d+)/(\d+)\)", out, re.I)
    if tm:
        result["temperature_min"] = int(tm.group(2))
        result["temperature_max"] = int(tm.group(3))

    
    if isinstance(result["total_lbas_written"], int):
        result["tb_written"] = total_lbas_written_to_tb(result["total_lbas_written"])

    
    if result.get("disk_kind") == "SSD":
        lbas_written = first_value(
            "Total_LBAs_Written",
            "Total_LBA_Written",
        )
        host_writes_32mib = first_value("Host_Writes_32MiB")

        tb_written = None
        if isinstance(lbas_written, int):
            tb_written = total_lbas_written_to_tb(lbas_written)
        elif isinstance(host_writes_32mib, int):
            tb_written = (
                host_writes_32mib * 32 * 1024 * 1024
            ) / 1_000_000_000_000

        if tb_written is not None:
            result["tb_written"] = tb_written

        
        
        rating = samsung_870_evo_tbw_rating(model, size_bytes)

        if rating is not None and tb_written is not None:
            used = max(0.0, (tb_written / float(rating)) * 100.0)
            remaining = max(0.0, 100.0 - used)

            result["tb_written"] = tb_written
            result["tbw_rating"] = float(rating)
            result["tbw_used_percent"] = used
            result["tbw_remaining_percent"] = remaining
            result["wear_percent"] = min(100.0, used)
            result["wear_source"] = (
                f"Samsung 870 EVO : {tb_written:.2f} TB écrits / "
                f"{rating:.0f} TBW"
            )
            result["index_kind"] = "wear"

    
    if result.get("disk_kind") == "SSD":
        life_left = first_value(
            "SSD_Life_Left",
            "Percent_Lifetime_Remain",
            "Remaining_Lifetime_Perc"
        )
        percent_used = first_value(
            "Percentage_Used_Endurance_Indicator",
            "Media_Wearout_Indicator"
        )

        if result.get("wear_percent") is None and isinstance(life_left, int):
            
            result["wear_percent"] = max(0.0, min(100.0, 100.0 - float(life_left)))
            result["wear_source"] = "SMART SSD Life Left"
            result["index_kind"] = "wear"
        elif result.get("wear_percent") is None and isinstance(percent_used, int):
            
            result["wear_percent"] = max(0.0, min(100.0, float(percent_used)))
            result["wear_source"] = "SMART SSD Wear"
            result["index_kind"] = "wear"

    bad_parts = [
        v for v in (
            result["reallocated"],
            result["pending"],
            result["uncorrectable"],
        )
        if isinstance(v, int)
    ]
    if bad_parts:
        result["bad_total"] = sum(bad_parts)

    if isinstance(result["power_hours"], int):
        result["power_days"] = result["power_hours"] / 24.0

    
    if result.get("disk_kind") == "HDD":
        result["wear_percent"] = hdd_risk_index(
            result.get("power_hours"),
            result.get("reallocated"),
            result.get("pending"),
            result.get("uncorrectable"),
            result.get("health"),
        )
        result["wear_source"] = (
            "Indice de risque HDD : âge + SMART "
            "(réalloués/pending/non corrigibles)"
        )
        result["index_kind"] = "risk"


    result["available"] = bool(values)
    return result



# From a disk or partition, retrieves the physical disk, size, model, and serial number.
def physical_disk_info(path):





    result = {
        "member_path": path,
        "physical_path": path,
        "size": 0,
        "model": "",
        "serial": "",
    }

    if not path or not path.startswith("/dev/"):
        return result

    
    rc, out = run([
        "lsblk", "-J", "-b",
        "-o", "PATH,PKNAME,TYPE,SIZE,MODEL,SERIAL",
        path
    ], timeout=10)

    if rc == 0:
        import json
        try:
            data = json.loads(out)
            nodes = data.get("blockdevices", [])
            if nodes:
                n = nodes[0]
                result["size"] = int(n.get("size") or 0)
                result["model"] = (n.get("model") or "").strip()
                result["serial"] = (n.get("serial") or "").strip()

                pkname = (n.get("pkname") or "").strip()
                ntype = (n.get("type") or "").strip()

                if ntype == "part" and pkname:
                    parent = f"/dev/{pkname}"
                    result["physical_path"] = parent

                    rc2, out2 = run([
                        "lsblk", "-dn", "-b",
                        "-o", "SIZE,MODEL,SERIAL",
                        parent
                    ], timeout=10)
                    if rc2 == 0 and out2.strip():
                        
                        rcj, outj = run([
                            "lsblk", "-J", "-dn", "-b",
                            "-o", "PATH,SIZE,MODEL,SERIAL",
                            parent
                        ], timeout=10)
                        if rcj == 0:
                            try:
                                d2 = json.loads(outj).get("blockdevices", [])[0]
                                result["size"] = int(d2.get("size") or result["size"] or 0)
                                result["model"] = (d2.get("model") or result["model"] or "").strip()
                                result["serial"] = (d2.get("serial") or result["serial"] or "").strip()
                            except Exception:
                                pass
        except Exception:
            pass

    
    physical = result["physical_path"]
    if shutil.which("udevadm") and physical:
        rc, props = run(["udevadm", "info", "--query=property", "--name", physical], timeout=10)
        if rc == 0:
            p = {}
            for line in props.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    p[k.strip()] = v.strip()

            if not result["model"]:
                result["model"] = (
                    p.get("ID_MODEL_FROM_DATABASE")
                    or p.get("ID_MODEL")
                    or p.get("ID_SCSI_MODEL")
                    or ""
                ).replace("\\x20", " ").replace("_", " ").strip()

            if not result["serial"]:
                result["serial"] = (
                    p.get("ID_SERIAL_SHORT")
                    or p.get("ID_SCSI_SERIAL")
                    or p.get("ID_SERIAL")
                    or ""
                ).strip()

    # Dernier fallback : smartctl -i.
    if shutil.which("smartctl") and physical and (not result["model"] or not result["serial"]):
        rc, smart = run(["smartctl", "-i", physical], timeout=15)
        if rc in (0, 2):  
            for line in smart.splitlines():
                low = line.lower()
                if not result["model"] and (
                    low.startswith("device model:")
                    or low.startswith("model number:")
                    or low.startswith("product:")
                ):
                    result["model"] = line.split(":", 1)[1].strip()
                if not result["serial"] and low.startswith("serial number:"):
                    result["serial"] = line.split(":", 1)[1].strip()

    return result



# Returns lsblk metadata for one block device as a dictionary.
def block_device_info(path):

    rc, out = run([
        "lsblk", "-J", "-b",
        "-o", "NAME,PATH,TYPE,SIZE,MODEL,SERIAL,FSTYPE,LABEL,UUID,MOUNTPOINTS",
        path
    ], timeout=10)
    if rc != 0:
        return {}
    import json
    try:
        data = json.loads(out)
        nodes = data.get("blockdevices", [])
        if not nodes:
            return {}
        n = nodes[0]
        return {
            "path": n.get("path") or path,
            "type": n.get("type") or "",
            "size": int(n.get("size") or 0),
            "model": (n.get("model") or "").strip(),
            "serial": (n.get("serial") or "").strip(),
            "fstype": n.get("fstype") or "",
            "label": n.get("label") or "",
            "uuid": n.get("uuid") or "",
            "mountpoints": n.get("mountpoints") or [],
        }
    except Exception:
        return {}



# Parses 'mdadm --detail' output to obtain slot, state, and device for each member.
def parse_mdadm_members(array_path):





    rc, detail = run(["mdadm", "--detail", array_path], timeout=15)
    if rc != 0:
        return [], detail

    members = []
    in_table = False

    for raw in detail.splitlines():
        line = raw.strip()
        if not line:
            continue

        if ("RaidDevice" in line and "State" in line) or (
            line.startswith("Number") and "State" in line
        ):
            in_table = True
            continue

        if not in_table:
            continue

        
        # 0  8  17  0  active sync set-A  /dev/sdb1
        # -  0   0  1  removed
        parts = line.split()
        if len(parts) < 5:
            continue

        
        try:
            slot = parts[3]
        except Exception:
            slot = "?"

        dev = ""
        dev_index = None
        for i, token in enumerate(parts):
            if token.startswith("/dev/"):
                dev = token
                dev_index = i
                break

        if dev_index is not None:
            state_tokens = parts[4:dev_index]
        else:
            state_tokens = parts[4:]

        state = " ".join(state_tokens).strip() or "unknown"
        low = state.lower()

        problem_words = (
            "faulty", "failed", "removed", "missing",
            "blocked", "write-mostly faulty"
        )
        warning_words = (
            "spare", "rebuild", "recover", "resync",
            "replacement", "reshape"
        )

        problem = any(w in low for w in problem_words)
        warning = (not problem) and any(w in low for w in warning_words)

        members.append({
            "device": dev,
            "slot": slot,
            "state": state,
            "problem": problem,
            "warning": warning,
        })

    
    if not members:
        mdname = Path(array_path).name
        slaves = Path(f"/sys/block/{mdname}/slaves")
        if slaves.exists():
            for slave in sorted(slaves.iterdir()):
                members.append({
                    "device": f"/dev/{slave.name}",
                    "slot": "?",
                    "state": "active",
                    "problem": False,
                    "warning": False,
                })

    return members, detail



# Lists devices that can be offered as candidates when replacing a RAID member.
def get_candidate_replacement_devices(exclude=None):

    exclude = set(exclude or [])
    devices = get_block_devices()
    candidates = []
    for d in devices:
        if d.get("type") not in ("disk", "part"):
            continue
        path = d.get("path") or ""
        if not path or path in exclude:
            continue

        mounts = d.get("mountpoints") or []
        mounted = any(bool(m) for m in mounts) if isinstance(mounts, list) else bool(mounts)
        fstype = d.get("fstype") or ""
        model = (d.get("model") or "").strip()
        size = int(d.get("size") or 0)

        candidates.append({
            "path": path,
            "type": d.get("type") or "",
            "size": size,
            "model": model,
            "fstype": fstype,
            "mounted": mounted,
        })
    return candidates



# Collects filesystem, UUID, mount, and used/free space information for an array.
def get_array_mount_info(array_path):




    info = {
        "fstype": "",
        "label": "",
        "uuid": "",
        "mountpoints": [],
        "source": array_path,
        "size": "",
        "used": "",
        "avail": "",
        "use_percent": "",
    }

    rc, out = run([
        "lsblk", "-J", "-o",
        "PATH,FSTYPE,LABEL,UUID,MOUNTPOINTS",
        array_path
    ], timeout=10)

    if rc == 0:
        import json
        try:
            data = json.loads(out)
            nodes = data.get("blockdevices", [])
            if nodes:
                n = nodes[0]
                info["fstype"] = n.get("fstype") or ""
                info["label"] = n.get("label") or ""
                info["uuid"] = n.get("uuid") or ""
                mounts = n.get("mountpoints") or []
                if isinstance(mounts, list):
                    info["mountpoints"] = [m for m in mounts if m]
                elif mounts:
                    info["mountpoints"] = [str(mounts)]
        except Exception:
            pass

    
    if not info["mountpoints"]:
        rc, out = run([
            "lsblk", "-J", "-o",
            "PATH,FSTYPE,LABEL,UUID,MOUNTPOINTS",
            array_path
        ], timeout=10)
        if rc == 0:
            import json
            try:
                data = json.loads(out)

                
                # Recursively walks the lsblk JSON tree so no child partition/device is missed.
                def walk(nodes):
                    for n in nodes:
                        mounts = n.get("mountpoints") or []
                        if isinstance(mounts, list):
                            valid = [m for m in mounts if m]
                        else:
                            valid = [str(mounts)] if mounts else []
                        if valid:
                            info["source"] = n.get("path") or array_path
                            info["fstype"] = n.get("fstype") or info["fstype"]
                            info["label"] = n.get("label") or info["label"]
                            info["uuid"] = n.get("uuid") or info["uuid"]
                            info["mountpoints"] = valid
                            return True
                        if n.get("children") and walk(n["children"]):
                            return True
                    return False

                walk(data.get("blockdevices", []))
            except Exception:
                pass

    
    if info["mountpoints"]:
        mountpoint = info["mountpoints"][0]
        rc, out = run([
            "df", "-h", "--output=source,size,used,avail,pcent,target",
            mountpoint
        ], timeout=10)
        if rc == 0:
            lines = [l for l in out.splitlines() if l.strip()]
            if len(lines) >= 2:
                parts = lines[-1].split()
                if len(parts) >= 6:
                    info["source"] = parts[0]
                    info["size"] = parts[1]
                    info["used"] = parts[2]
                    info["avail"] = parts[3]
                    info["use_percent"] = parts[4]

    return info




# =============================================================================

# IMPORTANT SAFETY: functions in this module are the main barrier
# against accidentally erasing a RAID member or an fstab-referenced disk.
# =============================================================================


# Resolves an fstab source (/dev, UUID, LABEL...) into real /dev device path(s).
def resolve_fstab_source(source):

    source = (source or "").strip()
    if not source:
        return []

    lower = source.lower()
    if (
        source.startswith("//")
        or (":" in source and not source.startswith("/dev/"))
        or lower in ("none", "tmpfs", "proc", "sysfs", "devpts")
    ):
        return []

    if source.startswith("/dev/"):
        try:
            return [str(Path(source).resolve())]
        except Exception:
            return [source]

    for prefix in ("UUID=", "PARTUUID=", "LABEL=", "PARTLABEL="):
        if source.startswith(prefix):
            rc, out = run(["blkid", "-t", source, "-o", "device"], timeout=5)
            if rc != 0:
                return []
            result = []
            for line in out.splitlines():
                dev = clean_device_path(line.strip())
                if not dev:
                    continue
                try:
                    dev = str(Path(dev).resolve())
                except Exception:
                    pass
                result.append(dev)
            return result

    return []



# Reads active /etc/fstab lines and builds a list used by safety checks.
def get_fstab_entries():




    path = Path("/etc/fstab")
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []

    entries = []
    for line_no, raw in enumerate(lines, 1):
        stripped = raw.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if "#" in stripped:
            stripped = stripped.split("#", 1)[0].strip()

        if not stripped:
            continue

        parts = re.split(r"\s+", stripped)
        if len(parts) < 2:
            continue

        source = parts[0]
        target = parts[1]
        fstype = parts[2] if len(parts) >= 3 else ""
        options = parts[3] if len(parts) >= 4 else ""

        resolved = resolve_fstab_source(source)
        for dev in resolved:
            entries.append({
                "source": source,
                "device": dev,
                "target": target,
                "fstype": fstype,
                "options": options,
                "line": line_no,
            })

    return entries



# Returns a disk and all its children so its partitions are protected as well.
def device_family_paths(device_path):




    dev = clean_device_path(device_path)
    if not dev:
        return set()

    try:
        dev = str(Path(dev).resolve())
    except Exception:
        pass

    paths = {dev}
    rc, out = run(["lsblk", "-nrpo", "PATH", dev], timeout=5)
    if rc == 0:
        for line in out.splitlines():
            p = clean_device_path(line.strip())
            if not p:
                continue
            try:
                p = str(Path(p).resolve())
            except Exception:
                pass
            paths.add(p)

    return paths



# Checks whether the disk or one of its partitions is referenced by fstab.
def fstab_protection_entries(device_path, cached_entries=None):

    family = device_family_paths(device_path)
    if not family:
        return []

    entries = cached_entries if cached_entries is not None else get_fstab_entries()
    result = []

    for entry in entries:
        dev = entry.get("device", "")
        try:
            dev = str(Path(dev).resolve())
        except Exception:
            pass
        if dev in family:
            result.append(entry)

    return result



# Builds the message explaining why a destructive operation is blocked by fstab.
def protected_fstab_message(device_path):
    entries = fstab_protection_entries(device_path)
    if not entries:
        return ""

    lines = []
    for e in entries:
        lines.append(
            f"{e.get('source', '?')} → {e.get('target', '?')} "
            f"(résolu: {e.get('device', '?')}, ligne {e.get('line', '?')})"
        )

    return (
        "PROTECTION FSTAB ACTIVE\n\n"
        "Le périphérique demandé, ou une de ses partitions, est référencé "
        "dans une ligne ACTIVE de /etc/fstab :\n\n"
        + "\n".join(lines)
        + "\n\nL'opération destructive est bloquée."
    )



# Checks whether a device already belongs to an active mdadm array.
def raid_protection_memberships(device_path):



    dev = clean_device_path(device_path)
    if not dev:
        return []

    memberships = get_raid_membership_map()
    found = []

    if dev in memberships:
        found.extend(memberships.get(dev, []))

    for physical, entries in memberships.items():
        for entry in entries:
            member = clean_device_path(entry.get("member", ""))
            if member == dev:
                found.append(entry)

    rc, parent = run(["lsblk", "-ndo", "PKNAME", dev], timeout=5)
    if rc == 0 and parent.strip():
        physical = "/dev/" + parent.strip().splitlines()[0].strip()
        found.extend(memberships.get(physical, []))

    unique = []
    seen = set()
    for e in found:
        key = (e.get("array", ""), e.get("member", ""))
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique



# Builds the blocking message when a device is already a RAID member.
def protected_raid_message(device_path):
    entries = raid_protection_memberships(device_path)
    if not entries:
        return ""

    lines = []
    for e in entries:
        arr = e.get("array") or "RAID inconnu"
        member = e.get("member") or device_path
        state = e.get("state") or ""
        lines.append(
            f"{member} → {arr}" + (f" ({state})" if state else "")
        )

    return (
        "PROTECTION RAID ACTIVE\n\n"
        "Le périphérique demandé appartient déjà à un RAID mdadm détecté :\n\n"
        + "\n".join(lines)
        + "\n\nL'opération destructive est bloquée."
    )



# Examines mdadm metadata present on a device without writing anything.
def mdadm_examine_superblock(device_path):

    dev = clean_device_path(device_path)
    if not dev:
        return False, ""

    rc, out = run(["mdadm", "--examine", dev], timeout=20)
    low = (out or "").lower()
    signatures = (
        "magic :",
        "version :",
        "array uuid",
        "raid level",
        "raid devices",
        "device role",
        "array state",
    )
    found = any(sig in low for sig in signatures)
    return found, out or ""



# Returns the raw disk and partitions that may contain an old superblock.
def candidate_member_paths_for_cleanup(disk_path):

    dev = clean_device_path(disk_path)
    if not dev:
        return []

    paths = []
    rc, out = run(["lsblk", "-nrpo", "PATH,TYPE", dev], timeout=10)
    if rc == 0:
        for line in out.splitlines():
            parts = line.split()
            if not parts:
                continue
            p = clean_device_path(parts[0])
            typ = parts[1] if len(parts) > 1 else ""
            if p and typ in ("disk", "part"):
                paths.append(p)

    if dev not in paths:
        paths.insert(0, dev)

    result = []
    seen = set()
    for p in paths:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result



# Finds only old superblocks that can be cleared without touching protected RAID/FSTAB devices.
def safe_orphan_superblocks(disk_paths):



    found = []
    protected = []

    for disk in disk_paths:
        for dev in candidate_member_paths_for_cleanup(disk):
            raid_msg = protected_raid_message(dev)
            fstab_msg = protected_fstab_message(dev)

            if raid_msg or fstab_msg:
                protected.append((dev, raid_msg or fstab_msg))
                continue

            has_sb, examine = mdadm_examine_superblock(dev)
            if has_sb:
                found.append({
                    "device": dev,
                    "examine": examine,
                })

    unique = []
    seen = set()
    for item in found:
        if item["device"] not in seen:
            seen.add(item["device"])
            unique.append(item)

    return unique, protected





# =============================================================================
