"""Public birth dates and calendar ages, independent of outcome resolution.

Historical retirement research lives outside runtime in archive/. Neither
future retirement dates nor real-world current status determine availability.
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "library/data/player_birth_dates.json"


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


def load(root=ROOT):
    data = json.loads((Path(root) / REGISTRY).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported birth-date registry version")
    for name, row in data["players"].items():
        if not row.get("gsis_id") or not row.get("sources"):
            raise ValueError("Birth-date identity/evidence missing: " + name)
        if row.get("birth_date"):
            date.fromisoformat(row["birth_date"])
    return data["players"]


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
