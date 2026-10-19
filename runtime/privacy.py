"""Kernel 2014.6 (batch B7): the player-state privacy check.

Under strength model player-state-v1 each player's value is a private draw.
The kernel publishes no per-possession strength block, so no public record of
a kernel 2014.6 or later game may carry one: receipts (regular, postseason,
preseason), paused records (paused_game.json) and weekly results caches
(.sim_cache). No `attribution_tier`, `drawn_tier` or `latent_value` may
appear outside library/data (the tiers and drawn values travel only inside
the private TeamInput record; the drawn ones only in apply_latent's copy).
The one place the public honours-production `attribution_tier` may sit is
that record itself: the frozen pre-closure weekly TeamInput packages
(`.sim_cache/YEAR/*_inputs.json`, written by build_week_inputs.py and read
by close_week.py). Those packages still refuse `drawn_tier` and
`latent_value`, since no package may hold a draw before closure (review
fix, October 16, 2026).
Scoped so the model and evidence files under library/data are never
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
    # data/ holds the season's system files from 2014 (receipts, paused
    # records, call sheets): rebuild step 2b.
    for folder in ("career", "data", "state", ".sim_cache"):
        base = root / folder
        if base.is_dir():
            files += sorted(p for p in base.rglob("*.json") if p.is_file())
    return files


def frozen_input_package(rel):
    """True for a frozen pre-closure weekly TeamInput package,
    `.sim_cache/YEAR/<name>_inputs.json` (relative to the repository root)."""
    parts = Path(rel).parts
    return len(parts) == 3 and parts[0] == ".sim_cache" and parts[2].endswith("_inputs.json")


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
        package = frozen_input_package(rel)
        for key, what in (("attribution_tier", "an attribution tier"), ("drawn_tier", "a drawn tier"),
                          ("latent_value", "a drawn player value")):
            if key == "attribution_tier" and package:
                continue  # the private TeamInput record itself (public honours-production tier)
            if _has_key(data, key):
                errors.append("%s carries %s outside library/data" % (rel, what))
    return errors
