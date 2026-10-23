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
  keeps the text it carried). Each assessment may carry ``short``: the
  two-to-four-sentence staff assessment a player page shows, the latest
  assessment's on his page (the user's player card template of October 20,
  2026). It is a dated summary of the
  full assessment it names in ``summarizes``, not a third assessment; its
  words never change automatically, and each current figure in it is a token
  (``TOKEN``) the page resolves from the closed games at build time. The
  grades stay here and are never rendered.
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
    "game_depth_chart": "Jacksonville's game depth chart and Stone's dated role decisions on the working chart "
                        "(runtime/assignments.py)",
    "week1_depth_charts": "the other clubs' Week 1 depth charts for the season (library/data/2014_week1_depth_charts.json), "
                          "less branch placements, applied in-season moves and branch reserve placements",
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
    "current_assignment": ("roster", "game_depth_chart", "week1_depth_charts"),
    "position_statistic": ("game_records",),
    "staff_assessment": ("record", "game_records"),
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
# The staff assessment a page shows (``short``) and its season-figure tokens:
# {{YEAR.KIND.MEASURE}} or {{YEAR.KIND.MEASURE:words}} / {{...:Words}} (runtime/player_pages
# resolves them from the closed games).
SHORT_KEYS = ("text", "date", "recorded", "by", "summarizes", "source")
SHORT_REQUIRED = ("text", "date", "recorded", "by", "summarizes")
TOKEN = re.compile(r"\{\{(\d{4})\.(regular|playoffs)\.([a-z_]+)(?::(words|Words))?\}\}")
RATES = ("passer_rating", "completion_percentage", "yards_per_attempt", "yards_per_carry", "yards_per_catch",
         "yards_per_target", "catch_rate", "field_goal_percentage", "extra_point_percentage", "punting_average",
         "net_punting_average")
# Ambiguous names a token may not use: "interceptions" (thrown or made).
AMBIGUOUS = {"interceptions": "interceptions_thrown or defensive_interceptions"}
# Grade and rating language: the page shows no grade (a statistic's name, passer rating, is not one).
GRADE_WORDS = re.compile(r"/\s*10\b|\bgrad(?:e|es|ed|ing)\b|(?<!passer )\bratings?\b|\brated\b", re.I)
# Statements about what the records hold, which a staff assessment never makes (the template: no
# evidence-limit or process wording; plain football judgments only).
RECORD_WORDS = re.compile(
    r"\bon record\b|\brecords?\s+(?:named|names|shows?|showed|holds?|held|charged|charges|credit(?:s|ed)?)\b"
    r"|\bcharged (?:to )?(?:him|his)\b|\bnothing charged\b|\bindividually (?:evaluated|classified|graded|assessed)\b"
    r"|\bmeasurements?\b[^.]*\bconflict|\bconflicting measurements?\b", re.I)
# A full stop after a single capital letter or one of these is not a sentence end (C.J., Leno Jr., No. 8).
ABBREVIATIONS = re.compile(r"(?:(?<![A-Za-z])[A-Z]|\bJr|\bSr|\bNo|\bSt)$")


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
            if (not {"season", "stage", "owner"} <= set(a) <= {"season", "stage", "owner", "short"}
                    or not (Path(root) / a["owner"]).is_file()):
                errors.append("%s: assessment pointer %s does not resolve" % (label, a.get("owner")))
            elif "short" in a:
                errors += short_errors(label, a, record, root)
        elif not (a.get("date") and a.get("by") and a.get("grades") and a.get("read")):
            errors.append("%s: a transcribed assessment needs its date, whose view, grades and read" % label)
        elif "short" in a:
            errors += short_errors(label, a, record, root)
    for t in record["transactions"]:
        if (not DATE_FORM.match(str(t.get("date", ""))) or t.get("kind") not in TRANSACTION_KINDS
                or not t.get("text") or not t.get("source")):
            errors.append("%s: transaction needs a date, a kind, a text and a source: %s" % (label, t))
        elif not (Path(root) / t["source"]).is_file():
            errors.append("%s: transaction source missing: %s" % (label, t["source"]))
    if record["transactions"] != sorted(record["transactions"], key=sort_key):
        errors.append("%s: transactions must be in date order" % label)
    return errors


# ------------------------------------------------------------------ the short staff assessment
def assessment_date(a, root=ROOT):
    """The ISO date of a full assessment: a transcribed entry's own date, or for a pointer to a
    frozen 2013 final sheet the date of its "Season-close checkpoint" line."""
    if "owner" not in a:
        return a["date"]
    text = (Path(root) / a["owner"]).read_text(encoding="utf-8")
    line = re.search(r"^\*\*Season-close checkpoint:\*\*\s*(.*?)\s*$", text, re.M)
    when = re.search(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", line.group(1)) if line else None
    if not when:
        raise ValueError("%s: no season-close checkpoint date" % a["owner"])
    month = ("January February March April May June July August September October November "
             "December").split().index(when.group(1)) + 1
    return date(int(when.group(3)), month, int(when.group(2))).isoformat()


def measures():
    """Every measure a token may name: games, the recorded player fields and the rates."""
    from .player_evidence import STAT_FIELDS
    return ("games",) + tuple(f for f in STAT_FIELDS if f not in AMBIGUOUS) + RATES


def token_errors(label, text, root=ROOT):
    """Static problems of the tokens in ``text``: an unknown season, kind, measure or format, a
    format on a rate, and any brace left that is not a whole token."""
    errors = []
    try:
        repo = json.loads((Path(root) / "docs/repository_map.json").read_text(encoding="utf-8"))
        years = {int(y) for y in repo.get("record_years", ())}
        active = int(repo["active_season"])
    except (OSError, ValueError, KeyError):
        return ["%s: the record years and active season cannot be read" % label]
    known = set(measures())
    for m in TOKEN.finditer(text):
        year, _kind, measure, fmt = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        if year not in years or year > active:
            errors.append("%s: token %s names a season with no game records up to %d" % (label, m.group(0), active))
        if measure in AMBIGUOUS:
            errors.append("%s: token %s is ambiguous; use %s" % (label, m.group(0), AMBIGUOUS[measure]))
        elif measure not in known:
            errors.append("%s: token %s names an unknown measure" % (label, m.group(0)))
        elif fmt and measure in RATES:
            errors.append("%s: token %s formats a rate; a rate prints with one decimal" % (label, m.group(0)))
    rest = TOKEN.sub(" ", text)
    if "{" in rest or "}" in rest:
        errors.append("%s: the staff assessment has a malformed token: %s" % (label, rest))
    return errors


def sentence_count(text):
    """Sentences in ``text``: each full stop, question or exclamation mark followed by a space or
    the end, except a full stop after a single capital letter or Jr, Sr, No or St."""
    count = 0
    for m in re.finditer(r"[.!?](?=\s|$)", text):
        if m.group(0) == "." and ABBREVIATIONS.search(text[:m.start()]) and m.end() < len(text):
            continue
        count += 1
    return count


def text_errors(label, text, root=ROOT, resolved=False):
    """The rules on the words of a staff assessment: one line, two to four sentences, no link or
    table cell, no grade or rating language, no statement about what the records hold
    (``RECORD_WORDS``), the clean-page rule and, before its tokens are resolved, every figure a
    token (a four-digit year apart)."""
    from . import clean_pages
    errors = []
    if not isinstance(text, str) or not text.strip():
        return ["%s: the staff assessment needs its text" % label]
    if "\n" in text or "|" in text or "](" in text or re.search(r"https?://", text):
        errors.append("%s: the staff assessment is one line with no link or table cell" % label)
    plain = TOKEN.sub("0", text)
    stray = [d for d in re.findall(r"\d+", TOKEN.sub(" ", text)) if not re.fullmatch(r"(?:19|20)\d\d", d)]
    if stray and not resolved:
        errors.append("%s: every figure in a staff assessment is a token (found %s); write football terms in "
                      "words" % (label, ", ".join(stray)))
    n = sentence_count(plain)
    if not 2 <= n <= 4 or not re.search(r"[.!?]$", plain.strip()):
        errors.append("%s: a staff assessment is two to four sentences (found %d)" % (label, n))
    for m in GRADE_WORDS.finditer(plain):
        errors.append("%s: no grade or rating language in a staff assessment: %s" % (label, m.group(0)))
    for m in RECORD_WORDS.finditer(plain):
        errors.append("%s: a staff assessment is a football judgment, not a statement about the records: %s"
                      % (label, m.group(0)))
    errors += ["%s: the staff assessment breaks the clean-page rule (%s)" % (label, e.split(": ", 1)[-1])
               for e in clean_pages.page_errors("short.md", plain + "\n", root=root)]
    return errors


def short_errors(label, a, record, root=ROOT):
    """Static errors of an assessment's ``short``: its keys, text and tokens, its dates (on or
    after the assessment it summarizes, no later than the master date), who wrote it, the
    assessments it summarizes (the first is the entry carrying it) and any adopted source."""
    from . import player_bios
    short = a["short"]
    label = "%s: %d %s staff assessment" % (label, a["season"], a["stage"])
    if not isinstance(short, dict):
        return ["%s must be an object" % label]
    keys = set(short)
    if not set(SHORT_REQUIRED) <= keys or keys - set(SHORT_KEYS):
        return ["%s keys must be %s, with an optional source" % (label, ", ".join(SHORT_REQUIRED))]
    errors = text_errors(label, short["text"], root) + token_errors(label, short["text"], root)
    dates = {}
    for field in ("date", "recorded"):
        try:
            dates[field] = date.fromisoformat(str(short[field]))
        except ValueError:
            errors.append("%s: %s must be an ISO date" % (label, field))
    if not isinstance(short["by"], str) or not short["by"].strip():
        errors.append("%s: by must name whose view it is" % label)
    if "date" in dates:
        try:
            if dates["date"] < date.fromisoformat(assessment_date(a, root)):
                errors.append("%s: dated %s, before the assessment it summarizes" % (label, short["date"]))
            if dates["date"] > player_bios.master_date(root):
                errors.append("%s: dated %s, after the master date" % (label, short["date"]))
        except (OSError, ValueError) as exc:
            errors.append("%s: its date cannot be checked: %s" % (label, exc))
    items = short["summarizes"]
    have = {(x.get("season"), x.get("stage")) for x in record["assessments"]}
    if (not isinstance(items, list) or not items
            or any(not isinstance(i, dict) or set(i) != {"season", "stage"} for i in items)):
        errors.append("%s: summarizes is a list of {season, stage}" % label)
    else:
        if (items[0]["season"], items[0]["stage"]) != (a["season"], a["stage"]):
            errors.append("%s: the first assessment it summarizes is the one carrying it" % label)
        for i in items:
            if (i["season"], i["stage"]) not in have:
                errors.append("%s: summarizes %s %s, which is not on the record" % (label, i["season"], i["stage"]))
    if "source" in short and not (isinstance(short["source"], str) and (Path(root) / short["source"]).is_file()):
        errors.append("%s: source %s does not exist" % (label, short.get("source")))
    return errors
