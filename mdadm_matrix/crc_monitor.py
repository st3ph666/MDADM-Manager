"""Persistent SMART CRC trend tracking."""

import json
import time
from pathlib import Path

CRC_WINDOW_SECONDS = 600
CRC_WARNING_DELTA = 3
CRC_CRITICAL_DELTA = 10


def _path():
    base = Path.home() / ".config" / "mdadm-manager"
    base.mkdir(parents=True, exist_ok=True)
    return base / "crc_history.json"


def _load():
    try:
        value = json.loads(_path().read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _save(value):
    try:
        _path().write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass


def evaluate_crc(identity, current_count):
    """Return OK for stable historical counts and warn only on a fast increase."""
    result = {"status": "ok", "label": "OK", "delta": 0, "rate_10min": 0.0}
    if not isinstance(current_count, int) or current_count < 0:
        return {"status": "unknown", "label": "", "delta": 0, "rate_10min": 0.0}

    now = time.time()
    history = _load()
    previous = history.get(identity) if isinstance(history.get(identity), dict) else None

    if previous:
        try:
            old_count = int(previous.get("count", current_count))
            old_time = float(previous.get("time", now))
            elapsed = max(1.0, now - old_time)
            delta = max(0, current_count - old_count)
            result["delta"] = delta
            result["rate_10min"] = delta * (CRC_WINDOW_SECONDS / elapsed)
            if elapsed <= CRC_WINDOW_SECONDS and delta >= CRC_CRITICAL_DELTA:
                result.update(status="critical", label="CRC EN HAUSSE RAPIDE")
            elif elapsed <= CRC_WINDOW_SECONDS and delta >= CRC_WARNING_DELTA:
                result.update(status="warning", label="CRC À SURVEILLER — HAUSSE RAPIDE")
        except Exception:
            pass

    history[identity] = {"count": current_count, "time": now}
    _save(history)
    return result
