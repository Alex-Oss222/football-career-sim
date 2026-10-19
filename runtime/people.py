"""Permanent player records (rebuild step 3a; stored-facts rules 1 and 2).

Each player who has a page has one record, ``data/people/players/<id>.json``
(the folder map's PLAYER_RECORDS), stored once and never copied into a
season. A record holds only the facts that have no other single owner:

- ``assessments``: the Jacksonville staff's annual assessments. A 2014
  opening or entry assessment is transcribed in full from the working card it
  was written on (grades, league comparison, the staff read, who and when,
  the dated updates); an assessment that still has its own owner (a frozen
  2013 final player sheet) is a pointer, ``{"season", "stage", "owner"}``.
  An assessment stores no age: his age on the assessment date is worked out
  from his birth date (the as-written card, pinned by ``transcribed_from``,
  keeps the text it carried).
- ``transactions``: the dated moves the season records hold (drafted,
  signed, traded, released, re-signed, reserve lists), each with its source.
  A date is as precise as its source: YYYY-MM-DD, YYYY-MM or YYYY, with
  ``label`` carrying a window the source gives without an exact day.

Every other fact a page shows is read, at build time, from the owners in
``READ_THROUGH``, in the order listed there (a later owner is read only when
the earlier ones hold nothing for him). The map lives here only; a record
does not copy it. Awards are among those facts: the award results own every
decided award, and the page reads them there (runtime/player_cards.award_entries),
so a record never holds one. Nothing here reads a hidden value, and no game,
evaluation or decision reads a record.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from .season_layout import PLAYER_RECORDS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
# The owners a player page reads, by the name READ_THROUGH uses.
OWNERS = {
    "canon_overrides": "the user's canon changes to a researched fact (data/people/canon_overrides.json)",
    "birth_date_corrections": "the reviewed birth-date corrections (library/data/player_birth_date_corrections.json)",
    "birth_date_registry": "the birth-date registry (library/data/player_birth_dates.json)",
    "week1_rosters": "the 2014 Week 1 rosters (library/data/2014_week1_rosters_branch_adjusted.json)",
    "league_database": "the league player database (each season's league personnel records in the data area)",
    "listed_identity": "the listed player identity: height, weight, college and listed numbers",
    "record": "the player's permanent record (its transactions)",
    "photos": "the open-licensed photo registry",
    "number_rule": "the number rule of the league player cards (runtime/player_cards.py)",
    "game_records": "the closed game records, read through the statbook rules (runtime/player_cards.py)",
    "roster": "the current Jacksonville roster (position and status)",
    "player_contracts": "the Jacksonville contract inputs (salary by year)",
    "award_results": "the award results of each season's awards data (runtime/player_cards.award_entries)",
}
# Each fact a page shows and its owners, in the order they are read: a later owner only when the
# earlier ones hold nothing for him (runtime/player_cards.Identity.birth_date and card_data,
# runtime/player_pages.physical_line, draft_view and render).
READ_THROUGH = {
    "birth_date": ("canon_overrides", "birth_date_corrections", "birth_date_registry", "week1_rosters",
                   "league_database"),
    "height_weight": ("listed_identity",),
    "college": ("league_database", "listed_identity"),
    "draft": ("record", "league_database"),
    "photo": ("photos",),
    "number": ("number_rule",),
    "statistics": ("game_records",),
    "position_and_status": ("roster", "game_records"),
    "contract": ("player_contracts",),
    "awards": ("award_results",),
}
RECORD_KEYS = ("schema_version", "name", "gsis_id", "assessments", "transactions")
# Facts other owners hold, which an assessment never stores (his age is worked out from his birth date).
OWNED_IN_ASSESSMENT = frozenset({"age", "age_as_written", "birth_date"})
OPTIONAL_KEYS = ("game_key",)
TRANSACTION_KINDS = frozenset({
    "drafted", "signed", "resigned", "traded", "released", "waived", "claimed", "cleared", "practice_squad",
    "promoted", "reserve", "reinstated", "tendered", "tender_withdrawn", "not_tendered", "franchise_tag",
    "offer_sheet", "contract_expired", "retired",
})
DATE_FORM = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def slugify(name):
    """The repository's player slug (runtime/player_cards.slugify)."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")
    if not slug:
        raise ValueError("player name cannot produce an empty slug")
    return slug


def folder(root=ROOT):
    return Path(root) / PLAYER_RECORDS


def dump(record):
    return json.dumps(record, indent=1, ensure_ascii=False) + "\n"


def load_all(root=ROOT):
    """{record id: record} for every permanent player record."""
    out = {}
    for path in sorted(folder(root).glob("*.json")):
        out[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return out


def new_record(name, gsis_id, game_key=None):
    """An identity-only record for a player who has just reached a page."""
    record = {"schema_version": SCHEMA_VERSION, "name": name, "gsis_id": gsis_id}
    if game_key and not gsis_id:
        record["game_key"] = game_key
    record.update({"assessments": [], "transactions": []})
    return record


def record_id(record, taken, group=None):
    """A unique file name: the player's slug, widened by position group, then by identity."""
    base = slugify(record["name"])
    for candidate in (base, "%s_%s" % (base, (group or "").lower()),
                      "%s_%s" % (base, slugify(record.get("gsis_id") or record.get("game_key") or "x"))):
        if candidate.strip("_") and candidate not in taken:
            return candidate
    raise ValueError("no unique record id for " + record["name"])


def sort_key(entry):
    """Transactions sort by their date, a year or month before the days inside it, and on the
    same date a draft selection before the contract that follows it."""
    return (entry["date"] + "-00-00")[:10], 0 if entry["kind"] == "drafted" else 1


def transaction_date_text(entry):
    """The date as the page shows it: the source's window, a full date, a month or a year."""
    if entry.get("label"):
        return entry["label"]
    value = entry["date"]
    if len(value) == 4:
        return value
    if len(value) == 7:
        return date(int(value[:4]), int(value[5:7]), 1).strftime("%B %Y")
    d = date.fromisoformat(value)
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def record_errors(rid, record, root=ROOT):
    """Schema errors for one record; empty when it is well formed."""
    errors = []
    label = "%s/%s.json" % (PLAYER_RECORDS, rid)
    keys = set(record)
    if not set(RECORD_KEYS) <= keys or keys - set(RECORD_KEYS) - set(OPTIONAL_KEYS):
        return ["%s: record keys must be %s" % (label, ", ".join(RECORD_KEYS))]
    if record["schema_version"] != SCHEMA_VERSION:
        errors.append("%s: unsupported schema version" % label)
    if not record["name"] or (not record["gsis_id"] and not record.get("game_key")):
        errors.append("%s: a record needs a name and a gsis id or game key" % label)
    for a in record["assessments"]:
        if OWNED_IN_ASSESSMENT & set(a):
            errors.append("%s: an assessment stores no %s; it is worked out from its owner"
                          % (label, ", ".join(sorted(OWNED_IN_ASSESSMENT & set(a)))))
        if not isinstance(a.get("season"), int) or a.get("stage") not in ("opening", "entry", "final"):
            errors.append("%s: an assessment needs a season and a stage" % label)
        elif "owner" in a:
            if set(a) != {"season", "stage", "owner"} or not (Path(root) / a["owner"]).is_file():
                errors.append("%s: assessment pointer %s does not resolve" % (label, a.get("owner")))
        elif not (a.get("date") and a.get("by") and a.get("grades") and a.get("read")):
            errors.append("%s: a transcribed assessment needs its date, whose view, grades and read" % label)
    for t in record["transactions"]:
        if (not DATE_FORM.match(str(t.get("date", ""))) or t.get("kind") not in TRANSACTION_KINDS
                or not t.get("text") or not t.get("source")):
            errors.append("%s: transaction needs a date, a kind, a text and a source: %s" % (label, t))
        elif not (Path(root) / t["source"]).is_file():
            errors.append("%s: transaction source missing: %s" % (label, t["source"]))
    if record["transactions"] != sorted(record["transactions"], key=sort_key):
        errors.append("%s: transactions must be in date order" % label)
    return errors
