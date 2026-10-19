"""Permanent coach records (rebuild step 3, the coach side; stored-facts rules 1 and 2).

Each coach has one record, ``data/people/coaches/<slug>.json`` (the folder
map's COACH_RECORDS), stored once and never copied into a season, and listed
in the repository map's required files. It grows by dated ``entries``, each
with only the keys its kind allows (ENTRY_KEYS):

- ``hired``: the club, the job, the unit and, for the head coach, the
  appointment of the current-job record it opened (``appointment``);
- ``role_changed``: a new job at the same club;
- ``calling_changed``: the day a phase's game-day calling changed for him
  (``phase``). Who calls what is owned by the delegation of the current-job
  record; this entry only dates the change in his history, and repository
  validation checks it against that delegation;
- ``contract_signed``: the contract as signed (``contract`` names it): the
  seasons, the salary by season (``salary`` is always present: null when the
  signed contract stated none, otherwise a salary for every season of the
  term, so a dropped season fails), the seasons guaranteed, the offset, any
  signing bonus and the other signed terms;
- ``contract_amended``: terms completed or changed later. Its date is
  ``in_world``, the day within the career it applies from; amendments are
  ordered and applied by it, and the contract on a given day holds only the
  amendments in force on it (``in_world`` on or before that day), so a page
  built for a day never shows a later one. Repository validation refuses an
  amendment dated after the master date. ``recorded`` keeps the real-world
  day the amendment was written. The contract as amended still needs a
  salary for every season of its term once any salary is stated. A term
  completed from comparable contracts of the time, not signed, is a
  ``reconstruction``; each such term names its ``basis``: the ``text``, the
  ``source`` and ``from``, the plain words the pages use for where it came
  from;
- ``departed``: the day he left, where he went and the last season his
  contract paid.

A date is as precise as its source (YYYY-MM-DD, YYYY-MM or YYYY), with
``label`` carrying a window the source gives without an exact day. Every
entry names its ``source``. A coach's history before Jacksonville (his
education, playing career, earlier jobs and earlier head-coaching seasons)
sits beside the entries, every item with its source (a ``position_source``
when the position comes from another page), and ``contacts`` lists every
approach from another club (a rumor, a call, a permission or interview
request, an interview, an offer, an accepted job) with its stage and any
deadline.

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
# The terms a contract holds and an amendment may set, in the order a contract page names them.
TERMS = ("seasons", "end", "salary", "guaranteed", "offset", "dismissal", "signing_bonus", "options")
# The keys each entry kind may carry: (required, optional). Everything else is refused, so a
# renamed key fails instead of silently dropping a fact.
DATED = ("date", "kind", "source")
ENTRY_KEYS = {
    "hired": (DATED + ("club", "job", "unit"), ("label", "appointment")),
    "role_changed": (DATED + ("club", "job", "unit"), ("label",)),
    "calling_changed": (DATED + ("phase",), ("label",)),
    "contract_signed": (DATED + ("contract", "club", "job", "seasons", "salary", "guaranteed"),
                        ("label", "offset", "dismissal", "signing_bonus", "options", "end", "terms")),
    "contract_amended": (("in_world", "recorded", "kind", "source", "contract", "terms"),
                         ("label", "reconstruction", "delegation")),
    "departed": (DATED + ("club", "to", "last_season"), ("label",)),
}
BASIS_KEYS = frozenset({"text", "from", "rows", "source"})
# The items of a coach's earlier career: (required, optional) keys, every item with its source.
HISTORY_KEYS = {
    "education": (("year", "degree", "school", "source"), ()),
    "playing": (("years", "team", "position", "source"), ("note", "position_source")),
    "coaching_history": (("years", "club", "job", "source"), ("work",)),
    "head_coaching_before": (("season", "club", "job", "regular", "source"), ("postseason", "finish", "playoffs")),
    "contacts": (("date", "club", "stage", "source"), ("label", "job", "deadline")),
}
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


def when(entry):
    """The entry's date within the career: an amendment's ``in_world``, any other entry's ``date``."""
    return entry.get("in_world") if entry.get("kind") == "contract_amended" else entry.get("date")


def date_text(entry):
    """The date as a page shows it: the source's window, a full date, a month or a year."""
    if entry.get("label"):
        return entry["label"]
    value = when(entry)
    if len(value) == 4:
        return value
    on = day(value)
    if len(value) == 7:
        return "%s %d" % (on.strftime("%B"), on.year)
    return "%s %d, %d" % (on.strftime("%B"), on.day, on.year)


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


def employed(record, club):
    """Whether his latest hire at ``club`` has no later departure (whatever the date)."""
    hire = hired(record, club)
    gone = departed(record, club)
    return hire is not None and (gone is None or day(gone["date"]) < day(hire["date"]))


def contract(record, contract_id, on=None):
    """The contract as it stands on day ``on`` (a date; None: with every amendment): the signed
    terms with each amendment in force on that day (``in_world`` on or before it) applied in
    in-world order, plus ``reconstructed`` ({term: basis} of the terms still completed from
    comparable contracts), ``amended`` (the amendment entries applied, in in-world order) and
    ``last_season`` after a departure. An amendment's salary sets the seasons it names and keeps
    the others."""
    signed = next((e for e in entries(record, "contract_signed") if e.get("contract") == contract_id), None)
    if signed is None:
        raise ValueError("%s has no contract %s" % (record.get("name"), contract_id))
    terms = {key: signed.get(key) for key in TERMS + ("club", "job", "terms")}
    terms.update(id=contract_id, signed=signed, reconstructed={}, amended=[], last_season=None)
    completed_seasons = set()
    amendments = [e for e in entries(record, "contract_amended") if e.get("contract") == contract_id
                  and (on is None or day(e["in_world"]) <= on)]
    for amendment in sorted(amendments, key=lambda e: day(e["in_world"])):
        terms["amended"].append(amendment)
        for key, given in (amendment.get("terms") or {}).items():
            value = given.get("value") if isinstance(given, dict) and "value" in given else given
            if key == "salary":
                value = dict(terms.get("salary") or {}, **(value or {}))
                completed_seasons = (completed_seasons | set(given_value(given))) if amendment.get("reconstruction") \
                    else completed_seasons - set(given_value(given))
            terms[key] = value
            if amendment.get("reconstruction"):
                terms["reconstructed"][key] = given.get("basis") if isinstance(given, dict) else None
            elif key != "salary" or not completed_seasons:
                terms["reconstructed"].pop(key, None)
    gone = departed(record, signed.get("club"))
    if gone is not None and day(gone["date"]) >= day(signed["date"]):
        terms["last_season"] = gone.get("last_season")
    return terms


def given_value(given):
    """The value an amendment gives a term (its ``value`` when it carries a basis)."""
    return (given.get("value") if isinstance(given, dict) and "value" in given else given) or {}


def completed(terms):
    """[(where it came from, [term, ...])] of the terms completed from other contracts, grouped
    by their basis's ``from`` in the order the terms are listed."""
    groups = {}
    for key in TERMS:
        if key in terms["reconstructed"]:
            basis = terms["reconstructed"][key] or {}
            groups.setdefault(basis.get("from") or "comparable contracts of the time", []).append(key)
    return list(groups.items())


def completed_sources(terms):
    """The research pages the completed terms cite, in order, each once."""
    return list(dict.fromkeys((b or {}).get("source") for b in terms["reconstructed"].values()
                              if (b or {}).get("source")))


def scheduled(terms):
    """{season: salary} the contract still schedules: every season with a stated salary up to
    the last season it paid (all of them when he has not left)."""
    salary = terms.get("salary") or {}
    last = terms.get("last_season")
    return {int(s): v for s, v in sorted(salary.items()) if v is not None and (last is None or int(s) <= last)}


def current_contract(record, club=None, on=None):
    """The latest contract he signed (with ``club``), as it stands on day ``on`` (``contract``),
    or None."""
    signed = [e for e in entries(record, "contract_signed") if club is None or e.get("club") == club]
    return contract(record, signed[-1]["contract"], on) if signed else None


def end_date(terms):
    """The earliest day the contract can end, from its ``end`` term, or None."""
    end = terms.get("end") or {}
    return end.get("date")


def through_season(terms):
    """The last season the contract covers (after a departure, the last one it paid)."""
    if terms.get("last_season") is not None:
        return terms["last_season"]
    return max(terms.get("seasons") or [0]) or None


def open_seasons(terms):
    """The covered seasons that are not guaranteed."""
    seasons = [s for s in terms.get("seasons") or () if terms.get("last_season") is None or s <= terms["last_season"]]
    return [s for s in seasons if s not in (terms.get("guaranteed") or ())]


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
    return "%s guaranteed; %s not" % (years_text(guaranteed), years_text(open_seasons(terms)))


def years_text(seasons):
    seasons = [str(s) for s in seasons]
    return seasons[0] if len(seasons) == 1 else ", ".join(seasons[:-1]) + " and " + seasons[-1]


def salary_error(salary, seasons):
    """Why a salary does not give every season of a contract its salary, or None: a stated salary
    maps each season of the term, and only those, to a whole number of dollars."""
    if not isinstance(salary, dict) or not all(isinstance(k, str) and k.isdigit() for k in salary):
        return "a season-by-season mapping"
    given = sorted(int(k) for k in salary)
    if given != sorted(seasons):
        missing = sorted(set(seasons) - set(given))
        outside = sorted(set(given) - set(seasons))
        return "a salary for every season of the term (%s)" % "; ".join(
            x for x in ("missing %s" % ", ".join(map(str, missing)) if missing else "",
                        "outside the term %s" % ", ".join(map(str, outside)) if outside else "") if x)
    if not all(type(v) is int and v >= 0 for v in salary.values()):
        return "a whole number of dollars for each season"
    return None


def _sourced(root, value):
    return isinstance(value, str) and bool(value) and (Path(root) / value).is_file()


def _keys_error(where, item, required, optional):
    keys = set(item)
    missing, unknown = set(required) - keys, keys - set(required) - set(optional)
    if missing or unknown:
        return "%s: needs %s%s; %s" % (where, ", ".join(required), (" (optional %s)" % ", ".join(optional))
                                       if optional else "", "; ".join(
            x for x in ("missing " + ", ".join(sorted(missing)) if missing else "",
                        "unknown " + ", ".join(sorted(unknown)) if unknown else "") if x))
    return None


def record_errors(slug, record, root=ROOT, master=None):
    """Schema errors for one coach record; empty when it is well formed. With ``master`` (the
    master date), an amendment dated after it fails: the career has not reached it."""
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
        kind = entry.get("kind")
        where = "%s: %s entry %s" % (label, kind, when(entry))
        if kind not in KINDS or not DATE_FORM.match(str(when(entry) or "")):
            errors.append("%s: an entry needs a known kind and a date" % where)
            continue
        problem = _keys_error(where, entry, *ENTRY_KEYS[kind])
        if problem:
            errors.append(problem)
        if not _sourced(root, entry.get("source")):
            errors.append("%s: source missing: %s" % (where, entry.get("source")))
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
            salary = entry.get("salary")
            problem = None if salary is None else salary_error(salary, seasons)
            if problem:
                errors.append("%s: salary must be null (none stated) or %s" % (where, problem))
            if set(entry.get("guaranteed") or ()) - set(seasons):
                errors.append("%s: a guaranteed season outside the contract" % where)
        if kind == "contract_amended":
            if entry.get("contract") not in signed_ids:
                errors.append("%s: amends no earlier signed contract" % where)
            if not DATE_FORM.match(str(entry.get("recorded", ""))):
                errors.append("%s: an amendment needs the real-world day it was recorded" % where)
            if master is not None and day(entry["in_world"]) > master:
                errors.append("%s: an amendment dated after the master date (%s); the career has not reached "
                              "it" % (where, master.isoformat()))
            bad = set(entry.get("terms") or {}) - set(TERMS)
            if bad or not entry.get("terms"):
                errors.append("%s: an amendment's terms must be among %s" % (where, ", ".join(TERMS)))
            for key, value in (entry.get("terms") or {}).items():
                basis = value.get("basis") if isinstance(value, dict) else None
                if entry.get("reconstruction") and not (
                        isinstance(basis, dict) and not set(basis) - BASIS_KEYS and basis.get("text")
                        and basis.get("from") and _sourced(root, basis.get("source"))):
                    errors.append("%s: the reconstructed term %s needs its basis (text, from and an existing "
                                  "source)" % (where, key))
        if kind == "departed" and not isinstance(entry.get("last_season"), int):
            errors.append("%s: a departure names the last season his contract paid" % where)
    for contract_id in signed_ids:
        try:
            amended = contract(record, contract_id)
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
        if amended["amended"] and amended.get("salary") is not None:
            problem = salary_error(amended["salary"], amended.get("seasons") or [])
            if problem:
                errors.append("%s: contract %s as amended needs %s" % (label, contract_id, problem))
    dated = [day(when(e)) for e in record["entries"] if DATE_FORM.match(str(when(e) or ""))]
    if dated != sorted(dated):
        errors.append("%s: entries must be in date order (an amendment by its in-world date)" % label)
    for key, (required, optional) in HISTORY_KEYS.items():
        for item in record.get(key) or ():
            where = "%s: %s item %s" % (label, key, item)
            problem = _keys_error(where, item, required, optional) if isinstance(item, dict) else where + ": not an item"
            if problem:
                errors.append(problem)
                continue
            if not _sourced(root, item.get("source")) or ("position_source" in item
                                                         and not _sourced(root, item["position_source"])):
                errors.append("%s: needs an existing source" % where)
            if key == "contacts" and (item.get("stage") not in CONTACT_STAGES
                                      or not DATE_FORM.match(str(item.get("date", "")))):
                errors.append("%s: a contact needs a date and a stage (%s)" % (where, ", ".join(CONTACT_STAGES)))
    for key in ("born", "playing_record"):
        if record.get(key) is not None and not _sourced(root, record[key].get("source")):
            errors.append("%s: %s needs an existing source" % (label, key))
    return errors


def repository_errors(root=ROOT):
    """Every coach record is a required file of the repository map, and every coach record the
    map requires exists, so a record cannot be added or lost silently."""
    root = Path(root)
    mapping = json.loads((root / "docs/repository_map.json").read_text(encoding="utf-8"))
    prefix = COACH_RECORDS.rstrip("/") + "/"
    required = {p for p in mapping.get("required_files") or () if p.startswith(prefix)}
    present = {(folder(root) / p.name).relative_to(root).as_posix() for p in folder(root).glob("*.json")}
    errors = ["%s: a coach record not listed in the repository map's required files" % p
              for p in sorted(present - required)]
    errors += ["%s: a required coach record is missing" % p for p in sorted(required - present)]
    return errors


def all_errors(root=ROOT):
    """Every coach record's schema errors, an amendment dated after the master date among them."""
    from .player_bios import master_date
    master = master_date(root)
    errors = repository_errors(root)
    for slug, record in load_all(root).items():
        errors += record_errors(slug, record, root, master)
    return errors
