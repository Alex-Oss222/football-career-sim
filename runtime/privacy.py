"""Kernel 2014.6 (batch B7): the player-state privacy check.

Under strength model player-state-v1 each player's value is a private draw.
The kernel publishes no per-possession strength block, so no public record of
a kernel 2014.6 or later game may carry one: receipts (regular, postseason,
preseason), paused records (paused_game.json) and weekly results caches
(.sim_cache). No `attribution_tier` may appear outside library/data (the
honours-production rule's tier travels only inside the private TeamInput
record). Scoped so the model and evidence files under library/data are never
rejected. Audits of earlier kernels are untouched: their receipts never held
the block either, and their TeamInputs are not committed.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HIDDEN_FROM = (2014, 6)


def _kernel(version):
    try:
        return tuple(int(p) for p in str(version).split("."))
    except (TypeError, ValueError):
        return ()


def _strength_blocks(obj, path=""):
    """Paths of every 'strength' key inside possession-like rows."""
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "strength" and isinstance(value, dict) and ("units" in value or "edge" in value):
                found.append(path + "/" + key)
            found += _strength_blocks(value, path + "/" + str(key))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            found += _strength_blocks(value, path + "/%d" % i)
    return found


def _has_key(obj, name):
    if isinstance(obj, dict):
        return any(k == name or _has_key(v, name) for k, v in obj.items())
    if isinstance(obj, list):
        return any(_has_key(v, name) for v in obj)
    return False


def candidate_files(root=ROOT):
    root = Path(root)
    files = []
    for folder in ("career", "state", ".sim_cache"):
        base = root / folder
        if base.is_dir():
            files += sorted(p for p in base.rglob("*.json") if p.is_file())
    return files


def privacy_errors(root=ROOT):
    """Errors for every public JSON record that leaks a hidden player state."""
    errors = []
    for path in candidate_files(root):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rel = path.relative_to(root)
        records = []
        if isinstance(data, dict) and "kernel_version" in data:
            records.append(data)
        elif isinstance(data, dict) and all(isinstance(v, dict) and "kernel_version" in v for v in data.values()) \
                and data:
            records += list(data.values())  # a weekly results cache {event_id: result}
        for record in records:
            if _kernel(record.get("kernel_version")) >= HIDDEN_FROM:
                blocks = _strength_blocks(record)
                if blocks:
                    errors.append("%s publishes a possession strength block under kernel %s (%s)"
                                  % (rel, record.get("kernel_version"), blocks[0]))
        if _has_key(data, "attribution_tier"):
            errors.append("%s carries an attribution tier outside library/data" % rel)
    return errors
