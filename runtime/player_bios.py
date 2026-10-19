"""Public birth dates and calendar ages, independent of outcome resolution.

Historical retirement research lives outside runtime in archive/. Neither
future retirement dates nor real-world current status determine availability.

Canon overrides (rebuild step 3a, October 19, 2026). The birth-date registry
(library/data/player_birth_dates.json) is research and is never edited for a
canon change. A change the user makes to a researched birth date lives in the
dated canon-override layer (data/people/canon_overrides.json, through the
folder map), which ``load`` applies on top of the registry, so every page, age
view and later game preparation reads the same date. Each override names the
player's gsis id and the registry date it replaces; ``load`` fails closed when
either no longer matches the registry, so a later research change can never be
silently masked. Closed game records carry no ages and are not rewritten.
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

from .season_layout import BIRTH_DATE_REGISTRY, CANON_OVERRIDES

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = BIRTH_DATE_REGISTRY
OVERRIDES = CANON_OVERRIDES
OVERRIDE_FIELDS = {"gsis_id", "birth_date", "library_birth_date", "decided", "by", "words", "record", "applies"}


def age_on(birth_date, as_of):
    """Completed birthdays, including a March 1 birthday in non-leap years
    for a February 29 birth. No wall clock or season-year approximation."""
    born = date.fromisoformat(birth_date)
    when = date.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    if when < born:
        raise ValueError("as-of date precedes birth date")
    return when.year - born.year - ((when.month, when.day) < (born.month, born.day))


def master_date(root=ROOT):
    text = (Path(root) / "state/05_Current_Season_State.md").read_text(encoding="utf-8")
    match = re.search(r"\| Master date/time \| ([A-Za-z]+ \d{1,2}, \d{4})", text)
    if not match:
        raise ValueError("Cannot parse Document 5 master date")
    return datetime.strptime(match[1], "%B %d, %Y").date()


def birth_date_overrides(root=ROOT):
    """{player name: override row} from the canon-override layer; {} when the
    layer is absent (a test fixture root). Each row is validated in full."""
    path = Path(root) / OVERRIDES
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported canon-override layer version")
    rows = data.get("birth_dates", {})
    for name, row in rows.items():
        if set(row) != OVERRIDE_FIELDS or not all(row.get(k) for k in OVERRIDE_FIELDS):
            raise ValueError("Canon birth-date override incomplete: " + name)
        date.fromisoformat(row["birth_date"])
        date.fromisoformat(row["library_birth_date"])
        date.fromisoformat(row["decided"])
    return rows


def apply_overrides(players, overrides):
    """The registry rows with each canon override applied; the registry row
    must still carry the gsis id and the birth date the override replaced."""
    players = dict(players)
    for name, row in overrides.items():
        base = players.get(name)
        if base is None or base.get("gsis_id") != row["gsis_id"]:
            raise ValueError("Canon birth-date override names no registry identity: " + name)
        if base.get("birth_date") != row["library_birth_date"]:
            raise ValueError("Canon birth-date override no longer matches the registry date it replaced: " + name)
        players[name] = dict(base, birth_date=row["birth_date"], library_birth_date=row["library_birth_date"],
                             canon_override=row["decided"])
    return players


def load(root=ROOT, overrides=True):
    """The reviewed identities by name, with the canon overrides applied
    (``overrides=False`` returns the research registry exactly as filed)."""
    data = json.loads((Path(root) / REGISTRY).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported birth-date registry version")
    for name, row in data["players"].items():
        if not row.get("gsis_id") or not row.get("sources"):
            raise ValueError("Birth-date identity/evidence missing: " + name)
        if row.get("birth_date"):
            date.fromisoformat(row["birth_date"])
    players = data["players"]
    return apply_overrides(players, birth_date_overrides(root)) if overrides else players


def biographies(names, as_of, players=None, allow_unverified=()):
    """Exact-name lookup into reviewed identities; unknowns fail preparation.

    ``allow_unverified`` names background players (never Jacksonville's) who
    may enter a package with no verified birth date: their row carries
    ``age: None`` and ``age_unverified: True`` so the receipt records the
    gap. No date is ever guessed for them.
    """
    players = load() if players is None else players
    allow_unverified = set(allow_unverified)
    result = {}
    for name in names:
        row = players.get(name)
        if row is None or not row.get("birth_date"):
            if name in allow_unverified:
                result[name] = {"gsis_id": (row or {}).get("gsis_id"), "birth_date": None,
                                "age": None, "age_unverified": True}
                continue
            raise ValueError("Verify birth date before preparing player: " + name)
        result[name] = {"gsis_id": row["gsis_id"], "birth_date": row["birth_date"],
                        "age": age_on(row["birth_date"], as_of)}
    return result


def unverified_ages(ages):
    """Sorted names flagged age_unverified in a package's player_ages sidecar."""
    return sorted(name for name, row in (ages or {}).items() if row.get("age_unverified"))
