"""Permanent coach records (rebuild step 3, the coach side; stored-facts rules 1 and 2).

Each coach has one record, ``data/people/coaches/<slug>.json`` (the folder
map's COACH_RECORDS), stored once and never copied into a season. It grows by
dated ``entries``:

- ``hired``: the club, the job, the unit and, for the head coach, the
  appointment of the current-job record it opened (``appointment``);
- ``role_changed``: a new job at the same club;
- ``calling_changed``: the day a phase's game-day calling changed for him
  (``phase``). Who calls what is owned by the delegation of the current-job
  record; this entry only dates the change in his history, and repository
  validation checks it against that delegation;
- ``contract_signed``: the contract as signed (``contract`` names it): the
  seasons, the salary by season where it was stated, the seasons guaranteed,
  the offset, any signing bonus and the other signed terms;
- ``contract_amended``: terms completed or changed later, applied from
  ``in_world``. A term completed from comparable contracts of the time, not
  signed, is a ``reconstruction`` with the basis it was taken from;
- ``departed``: the day he left, where he went and the last season his
  contract paid.

A date is as precise as its source (YYYY-MM-DD, YYYY-MM or YYYY), with
``label`` carrying a window the source gives without an exact day. Every
entry names its ``source``. A coach's history before Jacksonville (Stone's
playing career, earlier jobs and earlier head-coaching seasons) sits beside
the entries with its source, and ``contacts`` lists every approach from
another club (a rumor, a call, a permission or interview request, an
interview, an offer, an accepted job) with its stage and any deadline.

The appointment, its authority, the delegation of who calls each phase and
the standing instructions stay in the current-job record, which reads its
term and contract from here. Nothing that resolves a game reads this module.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .season_layout import COACH_RECORDS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
KINDS = ("hired", "role_changed", "calling_changed", "contract_signed", "contract_amended", "departed")
UNITS = ("team", "offense", "defense", "special_teams")
PHASES = ("offense", "defense", "special_teams")
CONTACT_STAGES = ("rumor", "call", "permission_request", "interview_request", "interview", "offer",
                  "accepted_job", "declined")
STAGE_NAMES = {"rumor": "Rumor", "call": "Call", "permission_request": "Permission request",
               "interview_request": "Interview request", "interview": "Interview", "offer": "Offer",
               "accepted_job": "Accepted job", "declined": "Declined"}
RECORD_KEYS = ("schema_version", "name", "entries")
OPTIONAL_KEYS = ("party", "full_name", "born", "education", "playing", "playing_record", "coaching_history",
                 "head_coaching_before", "contacts")
# The terms an amendment may complete, in the order a contract page shows them.
TERMS = ("end", "salary", "guaranteed", "offset", "dismissal", "signing_bonus", "options")
DATE_FORM = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def folder(root=ROOT):
    return Path(root) / COACH_RECORDS


def dump(record):
    return json.dumps(record, indent=1, ensure_ascii=False) + "\n"


def load_all(root=ROOT):
    """{slug: record} for every coach record."""
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder(root).glob("*.json"))}


def load(slug, root=ROOT):
    path = folder(root) / ("%s.json" % slug)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("coach record %s unreadable: %s" % (slug, exc)) from None


def day(value):
    """The first day a dated entry can mean (a month or a year counts from its start)."""
    value = str(value)
    return date.fromisoformat((value + "-01-01")[:10] if len(value) == 4 else (value + "-01")[:10])


def date_text(entry):
    """The date as a page shows it: the source's window, a full date, a month or a year."""
    if entry.get("label"):
        return entry["label"]
    value = entry["date"]
    if len(value) == 4:
        return value
    when = day(value)
    if len(value) == 7:
        return "%s %d" % (when.strftime("%B"), when.year)
    return "%s %d, %d" % (when.strftime("%B"), when.day, when.year)


def entries(record, kind=None):
    return [e for e in record.get("entries") or () if kind is None or e.get("kind") == kind]


def hired(record, club=None):
    """The latest hire (at ``club``), or None."""
    found = [e for e in entries(record, "hired") if club is None or e.get("club") == club]
    return found[-1] if found else None


def departed(record, club=None):
    found = [e for e in entries(record, "departed") if club is None or e.get("club") == club]
    return found[-1] if found else None


def job(record, club=None):
    """(job, unit) he holds or last held at ``club``: the hire, then any role change."""
    hire = hired(record, club)
    if hire is None:
        return None, None
    title, unit = hire["job"], hire.get("unit")
    for change in entries(record, "role_changed"):
        if change.get("club") == hire.get("club") and day(change["date"]) >= day(hire["date"]):
            title, unit = change["job"], change.get("unit", unit)
    return title, unit


def on_staff(record, club, on):
    """Whether he is on ``club``'s staff on day ``on``."""
    hire = hired(record, club)
    if hire is None or day(hire["date"]) > on:
        return False
    gone = departed(record, club)
    return gone is None or day(gone["date"]) > on or day(gone["date"]) < day(hire["date"])


def contract(record, contract_id):
    """The contract as it stands: the signed terms with every amendment applied, plus
    ``reconstructed`` (the terms completed from comparable contracts, each with its basis),
    ``amended`` (the amendment entries) and ``last_season`` after a departure."""
    signed = next((e for e in entries(record, "contract_signed") if e.get("contract") == contract_id), None)
    if signed is None:
        raise ValueError("%s has no contract %s" % (record.get("name"), contract_id))
    terms = {key: signed.get(key) for key in ("club", "job", "seasons", "salary", "guaranteed", "offset",
                                              "signing_bonus", "options", "dismissal", "end", "terms")}
    terms.update(id=contract_id, signed=signed, reconstructed={}, amended=[], last_season=None)
    for amendment in entries(record, "contract_amended"):
        if amendment.get("contract") != contract_id:
            continue
        terms["amended"].append(amendment)
        for key, value in (amendment.get("terms") or {}).items():
            terms[key] = value.get("value") if isinstance(value, dict) and "value" in value else value
            if amendment.get("reconstruction"):
                terms["reconstructed"][key] = value.get("basis") if isinstance(value, dict) else None
    gone = departed(record, signed.get("club"))
    if gone is not None and day(gone["date"]) >= day(signed["date"]):
        terms["last_season"] = gone.get("last_season")
    return terms


def scheduled(terms):
    """{season: salary} the contract still schedules: every season with a stated salary up to
    the last season it paid (all of them when he has not left)."""
    salary = terms.get("salary") or {}
    last = terms.get("last_season")
    return {int(s): v for s, v in sorted(salary.items()) if v is not None and (last is None or int(s) <= last)}


def current_contract(record, club=None):
    """The latest contract he signed (with ``club``), as it stands, or None."""
    signed = [e for e in entries(record, "contract_signed") if club is None or e.get("club") == club]
    return contract(record, signed[-1]["contract"]) if signed else None


def end_date(terms):
    """The earliest day the contract can end, from its ``end`` term, or None."""
    end = terms.get("end") or {}
    return end.get("date")


def through_season(terms):
    """The last season the contract covers (after a departure, the last one it paid)."""
    if terms.get("last_season") is not None:
        return terms["last_season"]
    return max(terms.get("seasons") or [0]) or None


def guarantee_text(terms):
    """Plain words for which of the covered seasons are guaranteed."""
    seasons = [s for s in terms.get("seasons") or () if terms.get("last_season") is None or s <= terms["last_season"]]
    guaranteed = [s for s in terms.get("guaranteed") or () if s in seasons]
    if not seasons:
        return "Not recorded"
    if guaranteed == seasons:
        return "Guaranteed"
    if not guaranteed:
        return "Not guaranteed"
    open_seasons = [s for s in seasons if s not in guaranteed]
    return "%s guaranteed; %s not" % (_years(guaranteed), _years(open_seasons))


def _years(seasons):
    seasons = [str(s) for s in seasons]
    return seasons[0] if len(seasons) == 1 else ", ".join(seasons[:-1]) + " and " + seasons[-1]


def record_errors(slug, record, root=ROOT):
    """Schema errors for one coach record; empty when it is well formed."""
    root = Path(root)
    label = "%s/%s.json" % (COACH_RECORDS, slug)
    keys = set(record)
    if not set(RECORD_KEYS) <= keys or keys - set(RECORD_KEYS) - set(OPTIONAL_KEYS):
        return ["%s: record keys must be %s, with optional %s" % (label, ", ".join(RECORD_KEYS),
                                                                 ", ".join(OPTIONAL_KEYS))]
    errors = []
    if record["schema_version"] != SCHEMA_VERSION:
        errors.append("%s: unsupported schema version" % label)
    if not record.get("name"):
        errors.append("%s: a record needs a name" % label)
    signed_ids = []
    for entry in record["entries"]:
        where = "%s: %s entry %s" % (label, entry.get("kind"), entry.get("date"))
        if entry.get("kind") not in KINDS or not DATE_FORM.match(str(entry.get("date", ""))):
            errors.append("%s: an entry needs a known kind and a date" % where)
            continue
        if not entry.get("source") or not (root / entry["source"]).is_file():
            errors.append("%s: source missing: %s" % (where, entry.get("source")))
        kind = entry["kind"]
        if kind in ("hired", "role_changed") and not (entry.get("club") and entry.get("job")
                                                      and entry.get("unit") in UNITS):
            errors.append("%s: a hire or role change needs a club, a job and a unit (%s)" % (where, ", ".join(UNITS)))
        if kind == "calling_changed" and entry.get("phase") not in PHASES:
            errors.append("%s: a calling change needs a phase (%s)" % (where, ", ".join(PHASES)))
        if kind == "contract_signed":
            signed_ids.append(entry.get("contract"))
            seasons = entry.get("seasons") or []
            if not (entry.get("contract") and entry.get("club") and seasons and seasons == sorted(seasons)):
                errors.append("%s: a signed contract needs an id, a club and its seasons in order" % where)
            for key in ("salary",):
                if entry.get(key) is not None and set(map(int, entry[key])) - set(seasons):
                    errors.append("%s: salary names a season outside the contract" % where)
            if set(entry.get("guaranteed") or ()) - set(seasons):
                errors.append("%s: a guaranteed season outside the contract" % where)
        if kind == "contract_amended":
            if entry.get("contract") not in signed_ids:
                errors.append("%s: amends no earlier signed contract" % where)
            if not DATE_FORM.match(str(entry.get("in_world", ""))):
                errors.append("%s: an amendment needs the in-world date it applies from" % where)
            bad = set(entry.get("terms") or {}) - set(TERMS)
            if bad or not entry.get("terms"):
                errors.append("%s: an amendment's terms must be among %s" % (where, ", ".join(TERMS)))
            for key, value in (entry.get("terms") or {}).items():
                basis = value.get("basis") if isinstance(value, dict) else None
                if entry.get("reconstruction") and not (basis and basis.get("text") and basis.get("source")
                                                        and (root / basis["source"]).is_file()):
                    errors.append("%s: the reconstructed term %s needs its basis and an existing source" % (where, key))
        if kind == "departed" and not isinstance(entry.get("last_season"), int):
            errors.append("%s: a departure names the last season his contract paid" % where)
    dated = [day(e["date"]) for e in record["entries"] if DATE_FORM.match(str(e.get("date", "")))]
    if dated != sorted(dated):
        errors.append("%s: entries must be in date order" % label)
    for contact in record.get("contacts") or ():
        if contact.get("stage") not in CONTACT_STAGES or not DATE_FORM.match(str(contact.get("date", ""))) \
                or not contact.get("club") or not contact.get("source") or not (root / contact["source"]).is_file():
            errors.append("%s: a contact needs a date, a club, a stage (%s) and an existing source"
                          % (label, ", ".join(CONTACT_STAGES)))
    for item in (record.get("playing") or []) + (record.get("coaching_history") or []) \
            + (record.get("head_coaching_before") or []):
        if not item.get("source") or not (root / item["source"]).is_file():
            errors.append("%s: career history needs an existing source: %s" % (label, item))
    for key in ("born", "playing_record"):
        if record.get(key) is not None and not (root / str(record[key].get("source"))).is_file():
            errors.append("%s: %s needs an existing source" % (label, key))
    return errors


def all_errors(root=ROOT):
    errors = []
    for slug, record in load_all(root).items():
        errors += record_errors(slug, record, root)
    return errors
