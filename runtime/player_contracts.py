"""Permanent player contract records, one per player (rebuild step 5, part B1; docs/rebuild_plan.md, step 5).

Each player Jacksonville holds or has held a contract for has one record,
``data/people/contracts/<id>.json`` (the folder map's PLAYER_CONTRACTS), named by the id of his
permanent player record (``data/people/players/<id>.json``), stored once and never copied into a
season. Modelled on the coach contract entries (runtime/coaches.py), a record is
``{schema_version, name, player, listed, position, roster_position, entries}``, with an optional
``draft_pick`` (as the register writes it) and ``converted`` (where the conversion took it from).
``listed`` is his line in the contract register, the order every contract view lists players in
(a new record takes the next line); ``position`` is his cap accounting group (POSITIONS).

The ``entries`` are dated, in date order, each naming its ``source`` and holding only the keys its
kind allows (ENTRY_KEYS). A date is as precise as its source (YYYY-MM-DD, YYYY-MM or YYYY), with
``label`` carrying a window the source gives without an exact day.

- ``contract_signed``: a contract as signed (``contract`` names it, ``club`` signed it): its last
  league year (``through``, null when no owner fixes it); its cap schedule by league year
  (``years``: {YYYY: {status, cap, base, proration, other_cap, cash, guaranteed_base, ...}}, the
  committed years only, in the contract inputs' row form: a year outside the term is not stored
  and reads as not committed; null when no owner holds the schedule); the bonus (``bonus``
  {text, amount}; its proration by year is each year's ``proration``); the register's texts as
  written (``type``, ``signed_text``, ``term_text``, ``value_text``, ``guarantee_text``,
  ``guarantee_basis``, ``exposure_text``, ``notes``, ``sources``); the schedule's ``basis``
  {text, source} (null when none is recorded); ``rookie`` ("drafted" or "undrafted") on a
  player's first contract; and ``method`` on a contract whose terms the in-season method computed.
- ``practice_squad``: a weekly practice-squad contract, its ``weekly_rate`` and ``weeks``; the
  season's working estimate is computed (rate times weeks), never typed.
- ``tender``: an unsigned tender, its ``years`` the tender amount's league year.
- ``contract_amended``: ``years`` of a contract changed from its date (``text`` says what).
- ``contract_ended``: how a contract ended (``how``, one of HOW; ``text`` in words; ``to`` the club
  a trade sent him to); the dead money it leaves (``dead_money`` [{year, amount, status, basis,
  line}]: ``line`` is the charge's line in the club's dead-money table, the order the charges were
  recorded); the register's ``notes`` and ``sources`` as rewritten at the ending; ``as_written``
  keeps a legacy source path the record cites no longer (never rendered).
- ``register``: the contract status register's line for him on that date, as written
  (``status``, ``availability``, ``plan``, ``credited_seasons``, ``accrued_seasons``).

A labelled reconstruction stays labelled in its own words; an unknown figure is not stored, never
filled. ``rows(root, on)`` builds the player rows the cap views and the player pages read, in the
shape the contract inputs' ``players`` block has always had; until the readers switch to
``rows()``, that block is a built copy (``write_players_block``) that nobody edits by hand, and
``errors`` fails when it differs. The club-level facts (league caps, team years, draft picks, the
financial policy, the year span, the in-season terms method and the three dead-money rows that
belong to no player record) stay in the contract inputs.

The in-season terms method (``in_season_terms`` in the contract inputs) is stored once and its
terms are computed, never typed: the league minimum by credited seasons, the weekly proration over
the pay weeks left on the fixtures, the practice-squad weekly rate and the promotion structure used
for Adrian Phillips on September 8, 2014, each labelled as the reconstruction it is.
``renegotiable_on`` applies Article 7 section 3(k).

The module stays outside the career layer (tests/test_career_layer_isolation.py): it imports
nothing from runtime.current_job, runtime.decision_queue, scripts.render_career_views or any module
in that test's LAYER, at module level or inside a function, and takes what it needs as arguments.
Nothing that resolves a game reads it.
"""
from __future__ import annotations

import copy
import json
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from .season_layout import PAGE_HISTORY, PLAYER_CONTRACTS, PLAYER_FINANCES, PLAYER_RECORDS, repository_relative

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
CLUB = "Jacksonville Jaguars"
POSITIONS = ("QB", "RB", "FB", "WR", "TE", "OT", "OG", "C", "EDGE", "IDL", "LB", "CB", "S", "K", "P", "LS")
RECORD_KEYS = ("schema_version", "name", "player", "listed", "position", "roster_position", "entries")
RECORD_OPTIONAL = ("draft_pick", "converted")
START_KINDS = ("contract_signed", "practice_squad", "tender")
CONTRACT_KINDS = START_KINDS + ("contract_amended", "contract_ended")
KINDS = CONTRACT_KINDS + ("register",)
HOW = ("released", "waived", "traded", "expired", "retired", "promoted", "tender_withdrawn")
# A deal Jacksonville ended: it no longer runs to its last league year at Jacksonville, and what is
# left of its guaranteed salary (none, here) is Jacksonville's (a traded deal runs on elsewhere).
TERMINATED = ("released", "waived", "tender_withdrawn")
CONTROL_AFTER = {"released": "released", "waived": "waived", "traded": "traded", "expired": "pending",
                 "retired": "retired", "tender_withdrawn": "pending"}
CONTROL_WHILE = {"contract_signed": "signed", "practice_squad": "signed", "tender": "tender"}
STATUS_WHILE = {"contract_signed": "Under contract", "practice_squad": "Practice squad", "tender": "Unsigned tender"}
CHARGED = ("known", "approximate", "tender")
YEAR_STATUSES = CHARGED + ("option_unexercised",)
NOT_COMMITTED = {"status": "not_committed", "cap": None, "base": None, "proration": None, "cash": None}
NOT_SIGNED = {"status": "not_signed", "cap": None, "base": None, "proration": None, "cash": None}
TEXTS = ("type", "signed_text", "term_text", "value_text", "bonus", "guarantee_text", "guarantee_basis", "basis",
         "exposure_text", "notes", "sources")
DATED = ("kind", "date", "source")
ENTRY_KEYS = {
    "contract_signed": (DATED + ("contract", "club", "through", "years"),
                        ("label",) + TEXTS + ("rookie", "method", "schedule_from")),
    "practice_squad": (DATED + ("contract", "club", "weekly_rate", "weeks"),
                       ("label",) + TEXTS + ("estimate_note", "schedule_from")),
    "tender": (DATED + ("contract", "club", "through", "years"), ("label",) + TEXTS + ("schedule_from",)),
    "contract_amended": (DATED + ("contract", "years", "text"), ("label", "basis", "notes", "sources")),
    "contract_ended": (DATED + ("contract", "how", "text"),
                       ("label", "to", "dead_money", "basis", "notes", "sources", "as_written")),
    "register": (DATED, ("label", "status", "availability", "plan", "credited_seasons", "accrued_seasons")),
}
DEAD_KEYS = ("year", "amount", "status", "basis", "line")
DATE_FORM = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
METHODS = ("in_season_minimum", "promotion")


# ------------------------------------------------------------------ storage
def folder(root=ROOT):
    return Path(root) / PLAYER_CONTRACTS


def record_path(root, player_id):
    return folder(root) / ("%s.json" % player_id)


def dump(record):
    return json.dumps(record, indent=1, ensure_ascii=False) + "\n"


def load(player_id, root=ROOT):
    path = record_path(root, player_id)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("contract record %s unreadable: %s" % (player_id, exc)) from None


def load_all(root=ROOT):
    """{player record id: contract record} for every contract record."""
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder(root).glob("*.json"))}


def inputs(root=ROOT):
    """The contract inputs (data/finances/financial_inputs.json): the club-level facts, the in-season
    terms method and, until the readers switch, the built ``players`` block."""
    return json.loads((Path(root) / PLAYER_FINANCES).read_text(encoding="utf-8"))


def horizon(data):
    return [str(y) for y in range(int(data["start_year"]), int(data["end_year"]) + 1)]


# ------------------------------------------------------------------ dates
def day(value):
    """The first day a dated entry can mean (a month or a year counts from its start)."""
    value = str(value)
    return date.fromisoformat((value + "-01-01")[:10] if len(value) == 4 else (value + "-01")[:10])


def as_day(value):
    if value is None or isinstance(value, date):
        return value
    return day(value)


def league_year(value):
    """The league year a dated signing falls in (it opens in March): the usual reading of a contract
    year (the U6 reading of the practice and renegotiation research, unverified)."""
    text = str(value)
    if len(text) == 4:
        return int(text)
    d = day(text)
    return d.year if d.month >= 3 else d.year - 1


def date_words(value):
    """``value`` as a page shows it: September 8, 2014; March 2012; 2012."""
    text = str(value)
    if len(text) == 4:
        return text
    if len(text) == 7:
        return day(text).strftime("%B %Y")
    d = day(text)
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


# ------------------------------------------------------------------ reading a record
def entries(record, kind=None, on=None):
    """The record's entries in force on day ``on`` (None: all), of ``kind`` when given."""
    on = as_day(on)
    return [e for e in record.get("entries", ()) if (kind is None or e.get("kind") == kind)
            and (on is None or day(e["date"]) <= on)]


def _years_of(entry, root=ROOT):
    """A contract entry's committed years as the inputs' rows: a practice-squad contract's season is
    computed from its weekly rate and weeks; a contract without a carried schedule has none."""
    if entry["kind"] == "practice_squad":
        season = str(league_year(entry["date"]))
        total = int(entry["weekly_rate"]) * int(entry["weeks"])
        row = {"status": "approximate", "cap": None, "base": total, "proration": 0, "other_cap": 0, "cash": total,
               "approximate_cap": total, "guaranteed_base": 0}
        if entry.get("estimate_note") is not None:
            row["estimate_note"] = entry["estimate_note"]
        return {season: row}
    return copy.deepcopy(entry.get("years") or {})


def through(entry):
    if entry["kind"] == "practice_squad":
        return league_year(entry["date"])
    return entry.get("through")


def contracts(record, on=None):
    """[(start entry, ending or None, amendments)] of every contract in force by ``on``, in order."""
    found = entries(record, on=on)
    out = []
    for e in found:
        if e["kind"] in START_KINDS:
            out.append([e, None, []])
    by_id = {c[0]["contract"]: c for c in out}
    for e in found:
        c = by_id.get(e.get("contract"))
        if c is None:
            continue
        if e["kind"] == "contract_ended":
            c[1] = e
        elif e["kind"] == "contract_amended":
            c[2].append(e)
    return [tuple(c) for c in out]


def schedule(start, amendments, root=ROOT):
    """A contract's years with its amendments applied in order (an amendment's years replace the
    years it names)."""
    years = _years_of(start, root)
    for amended in amendments:
        for y, row in (amended.get("years") or {}).items():
            years[y] = copy.deepcopy(row)
    return years


def contract_on(record, on=None, root=ROOT):
    """The contract in force on day ``on`` (None: as the record stands), or None when none is:
    {"contract", "kind", "start", "years", "through", "amendments"}."""
    chain = contracts(record, on)
    if not chain or chain[-1][1] is not None:
        return None
    start, _, amendments = chain[-1]
    return {"contract": start["contract"], "kind": start["kind"], "start": start,
            "years": schedule(start, amendments, root), "through": through(start), "amendments": amendments}


def _source(entry):
    return (entry.get("as_written") or {}).get("source") or entry["source"]


# ------------------------------------------------------------------ the rows
def row(record, years, on=None, root=ROOT):
    """The player row the cap views read for one record on day ``on`` (None when no contract is in
    force by then), in the contract inputs' ``players`` shape."""
    chain = contracts(record, on)
    if not chain:
        return None
    start, ended, amendments = chain[-1]
    committed = schedule(start, amendments, root)
    endings = [c[1] for c in chain if c[1] is not None]
    former = ended is not None
    out = {"name": record["name"], "position": record["position"], "roster_position": record["roster_position"],
           "control": CONTROL_AFTER.get(ended["how"], ended["how"]) if former else CONTROL_WHILE[start["kind"]]}
    # The register line in force, unless a later contract entry changed his status.
    registers = entries(record, "register", on)
    line = registers[-1] if registers else {}
    latest = max((e for e in entries(record, on=on) if e["kind"] in CONTRACT_KINDS), key=lambda e: day(e["date"]))
    if line and day(line["date"]) >= day(latest["date"]):
        out["status"] = line.get("status")
    else:
        out["status"] = ended["text"] if former else STATUS_WHILE[start["kind"]]
    out.update(contract_type=start.get("type"), signed=start.get("signed_text"), term=start.get("term_text"),
               contract_ends=None if former and ended["how"] in TERMINATED else through(start),
               value=start.get("value_text"), bonus_terms=(start.get("bonus") or {}).get("text"),
               guarantees=start.get("guarantee_text"), dead_money_2014=start.get("exposure_text"))
    shown = {}
    for y in years:
        stored = committed.get(y)
        if stored is not None and (not former or stored["status"] not in CHARGED):
            shown[y] = copy.deepcopy(stored)
        elif (former and ended["how"] == "expired" and through(start) is not None
              and int(y) == int(through(start)) + 1):
            shown[y] = dict(NOT_SIGNED)
        else:
            shown[y] = dict(NOT_COMMITTED)
    signed_deal = start["kind"] != "tender" and (not former or ended["how"] in TERMINATED)
    out["remaining_guarantees"] = (sum(r.get("guaranteed_base") or 0 for r in shown.values())
                                   if signed_deal else None)
    out.update(availability=line.get("availability"), plan=line.get("plan"),
               source_note=(ended or {}).get("notes", start.get("notes")),
               sources=list((ended or {}).get("sources", start.get("sources") or [])),
               credited_seasons=line.get("credited_seasons"), accrued_seasons=line.get("accrued_seasons"))
    if record.get("draft_pick"):
        out["draft_pick"] = record["draft_pick"]
    if start.get("guarantee_basis") is not None:
        out["guarantee_basis"] = start["guarantee_basis"]
    out["years"] = shown
    if start.get("basis"):
        out["schedule_basis"] = start["basis"]["text"]
    waivers = [(c[0], c[1]) for c in chain if c[1] is not None and c[1]["how"] in ("released", "waived")]
    if waivers:
        earlier, how = waivers[-1]
        out["prior_contract"] = {"type": earlier.get("type"), "term": earlier.get("term_text"),
                                 "contract_ends": through(earlier), "ended": how["text"]}
    if former:
        out.update(former_player=True, departure_date=ended["date"], departure_source=_source(ended))
    elif endings and endings[-1]["how"] == "expired":
        # He left control as a free agent and signed again: his row keeps where that is recorded.
        out["departure_source"] = _source(endings[-1])
    return out


def rows(root=ROOT, on=None, records=None, years=None):
    """Every player row on day ``on`` (None: as the records stand), in register order: exactly the
    shape of the contract inputs' ``players`` block, so the cap views and the player page switch with
    one read change."""
    records = load_all(root) if records is None else records
    years = horizon(inputs(root)) if years is None else years
    out = []
    for _, record in sorted(records.items(), key=lambda item: (item[1]["listed"], item[0])):
        r = row(record, years, on, root)
        if r is not None:
            out.append(r)
    return out


def as_of(root=ROOT, records=None, on=None):
    """The latest dated contract or register entry (by day ``on``): the date the contract views stand at."""
    records = load_all(root) if records is None else records
    days = [e["date"] for r in records.values() for e in entries(r, on=on) if len(e["date"]) == 10]
    return max(days) if days else None


def dead_money(root=ROOT, records=None, club_rows=None, on=None):
    """The club's dead-money table in line order (by day ``on``): each charge a player record's ending
    leaves, and the club-level rows of the contract inputs (charges with no player record), which hold
    the lines the player charges leave free, in their stored order."""
    records = load_all(root) if records is None else records
    club_rows = inputs(root).get("dead_money", []) if club_rows is None else club_rows
    placed = {}
    for record in records.values():
        for e in entries(record, "contract_ended", on):
            for item in e.get("dead_money") or ():
                placed[int(item["line"])] = {"player": record["name"], "year": item["year"], "amount": item["amount"],
                                             "status": item["status"], "basis": item["basis"]}
    out, rest = [], list(club_rows)
    for line in range(1, len(placed) + len(rest) + 1):
        if line in placed:
            out.append(placed[line])
        elif rest:
            out.append(copy.deepcopy(rest.pop(0)))
    return out


def tracker_inputs(data, root=ROOT, on=None):
    """The contract inputs as the cap views read them: the club-level facts of ``data`` with the
    players, the dead-money table and the date built from the contract records (as they stood on day
    ``on``; None: as they stand)."""
    full = copy.deepcopy(data)
    records = load_all(root)
    full["players"] = rows(root, on, records, horizon(data))
    full["dead_money"] = dead_money(root, records, data.get("dead_money", []), on)
    full["as_of"] = as_of(root, records, on) or data.get("as_of")
    return full


def players_block(root=ROOT):
    """The contract inputs with their built ``players`` block and date (the text the inputs file
    should hold)."""
    data = inputs(root)
    data["as_of"] = as_of(root) or data.get("as_of")
    # A row whose content is unchanged keeps the stored dict (its key order), so a rebuild after one
    # new entry changes only that player's row in the file.
    stored = {r.get("name"): r for r in data.get("players") or ()}
    data["players"] = [stored[r["name"]] if stored.get(r["name"]) == r else r for r in rows(root, years=horizon(data))]
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


def write_players_block(root=ROOT):
    """Rebuild the ``players`` block (every writer of a contract entry calls this in the same commit).
    Returns True when the file changed."""
    path = Path(root) / PLAYER_FINANCES
    text = players_block(root)
    if path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


# ------------------------------------------------------------------ the in-season terms method
def method(root=ROOT, data=None):
    """The stored in-season terms method of the contract inputs."""
    data = inputs(root) if data is None else data
    return data["in_season_terms"]


def _season(terms, season):
    found = terms["seasons"].get(str(season))
    if found is None:
        raise ValueError("no in-season terms are recorded for %s" % season)
    return found


def minimum_salary(season, credited, root=ROOT, terms=None):
    """The league minimum for ``credited`` credited seasons in ``season`` (the agreement's Article 26
    column the library records)."""
    terms = method(root) if terms is None else terms
    for low, high, amount in _season(terms, season)["minimum_salary"]["by_credited_seasons"]:
        if credited >= low and (high is None or credited <= high):
            return amount
    raise ValueError("no minimum salary for %s credited seasons in %s" % (credited, season))


def practice_squad_rate(season, root=ROOT, terms=None):
    terms = method(root) if terms is None else terms
    return _season(terms, season)["practice_squad_weekly"]["amount"]


def pay_weeks(season, root=ROOT, club=CLUB):
    """[(week, pay date)] of the regular season on the fixtures: the week's game for ``club``, or for
    its bye the week's last league game."""
    from .seasons import SeasonPaths
    games = SeasonPaths(int(season), Path(root)).regular_games()
    weeks = sorted({int(g["week"]) for g in games})
    out = []
    for week in weeks:
        in_week = [g for g in games if int(g["week"]) == week]
        own = [g for g in in_week if club in (g["home"], g["away"])]
        out.append((week, date.fromisoformat(max(g["date"] for g in (own or in_week)))))
    return out


def pay_weeks_left(season, on, root=ROOT, club=CLUB):
    """(weeks left, weeks in the season) for a contract signed on day ``on``: the weeks whose pay
    date is on or after it."""
    weeks = pay_weeks(season, root, club)
    on = as_day(on)
    return sum(1 for _, paid in weeks if paid >= on), len(weeks)


def prorated(amount, left, total):
    """``amount`` earned for ``left`` of ``total`` weekly installments, to the dollar (a labelled
    reconstruction: the standard player contract pays in equal weekly installments, and no league
    proration rule is on file)."""
    return int((Decimal(amount) * left / total).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _known(base, other=0):
    return {"status": "known", "cap": base + other, "base": base, "proration": 0, "other_cap": other,
            "cash": base + other, "guaranteed_base": 0}


def computed_years(entry, root=ROOT, terms=None, club=CLUB):
    """The years the in-season method gives a contract entry that names it in ``method``:
    ``in_season_minimum`` (the season's minimum for his credited seasons, earned for the pay weeks
    left) or ``promotion`` (the promotion structure: its first year prorated the same way, plus the
    practice-squad weeks he was paid)."""
    spec = entry["method"]
    terms = method(root) if terms is None else terms
    season = league_year(entry["date"])
    left, total = pay_weeks_left(season, entry["date"], root, club)
    if spec["name"] == "in_season_minimum":
        rate = minimum_salary(season, int(spec["credited_seasons"]), root, terms)
        return {str(season): _known(prorated(rate, left, total))}
    if spec["name"] == "promotion":
        structure = terms["promotion"]["schedule"]
        paid = int(spec["squad_weeks"]) * practice_squad_rate(season, root, terms)
        out = {}
        for y, base in sorted(structure.items()):
            out[y] = _known(prorated(base, left, total), paid) if int(y) == season else _known(base)
        return out
    raise ValueError("unknown in-season method %r" % spec.get("name"))


# ------------------------------------------------------------------ renegotiation
def final_regular_game(season, root=ROOT):
    """The date of the season's last regular-season game on its fixtures, or None when the fixtures
    are not released."""
    from .seasons import SeasonPaths
    try:
        games = SeasonPaths(int(season), Path(root)).regular_games()
    except (OSError, ValueError, KeyError):
        return None
    return max(date.fromisoformat(g["date"]) for g in games) if games else None


def renegotiable_on(record, on, root=ROOT):
    """(answer, reason): whether the contract in force on day ``on`` may be renegotiated, amended or
    extended. A rookie contract may not until after the final regular-season game of the player's
    third contract year (drafted) or second (undrafted) (Article 7 section 3(k), the library's R1
    and R2); a contract year is read as the league year he signed in (the U6 reading, unverified).
    Any other contract returns "needs verification", never a plain yes."""
    on = as_day(on)
    current = contract_on(record, on, root)
    if current is None:
        return False, "no Jacksonville contract is in force"
    kind = current["start"].get("rookie")
    if kind not in ("drafted", "undrafted"):
        return "needs verification", "not a rookie contract; no renegotiation rule for it is on file"
    first = league_year(current["start"]["date"])
    bar = first + (2 if kind == "drafted" else 1)
    final = final_regular_game(bar, root)
    if final is None:
        if on < date(bar + 1, 1, 1):
            return False, "a %s rookie's contract is not renegotiable before the final %d regular-season game" % (kind, bar)
        return "needs verification", "the %d fixtures are not on file" % bar
    if on > final:
        return True, "after the final %d regular-season game (%s), his %s contract year" % (
            bar, date_words(final.isoformat()), "third" if kind == "drafted" else "second")
    return False, "a %s rookie's contract is not renegotiable before the final %d regular-season game (%s)" % (
        kind, bar, date_words(final.isoformat()))


# ------------------------------------------------------------------ writing
def entry_errors(entry, label="entry"):
    """Schema problems of one entry."""
    kind = entry.get("kind")
    if kind not in ENTRY_KEYS:
        return ["%s: unknown entry kind %r" % (label, kind)]
    required, optional = ENTRY_KEYS[kind]
    errors = []
    missing = [k for k in required if k not in entry]
    extra = sorted(set(entry) - set(required) - set(optional))
    if missing:
        errors.append("%s: a %s entry needs %s" % (label, kind, ", ".join(missing)))
    if extra:
        errors.append("%s: a %s entry may not carry %s" % (label, kind, ", ".join(extra)))
    if not DATE_FORM.match(str(entry.get("date", ""))):
        errors.append("%s: date must be YYYY, YYYY-MM or YYYY-MM-DD" % label)
    if kind == "contract_ended" and entry.get("how") not in HOW:
        errors.append("%s: how must be one of %s" % (label, ", ".join(HOW)))
    if kind == "contract_signed" and entry.get("rookie") not in (None, "drafted", "undrafted"):
        errors.append("%s: rookie must be drafted or undrafted" % label)
    if kind == "contract_signed" and entry.get("method") is not None:
        if entry["method"].get("name") not in METHODS:
            errors.append("%s: method must be one of %s" % (label, ", ".join(METHODS)))
    for item in entry.get("dead_money") or ():
        if set(item) != set(DEAD_KEYS) or not isinstance(item.get("amount"), int) or item["amount"] < 0 \
                or not isinstance(item.get("line"), int) or item["line"] < 1:
            errors.append("%s: a dead-money charge needs %s, a whole-dollar amount and a line" % (label, ", ".join(DEAD_KEYS)))
    return errors


def add_entry(root, player_id, entry, record=None):
    """Append ``entry`` to his record (the one writer builder D's transactions use) and write it; a
    new player's record is created from ``record`` ({position, roster_position} and an optional
    draft_pick), its name taken from his permanent player record and its line the next in the
    register. Refuses an entry that breaks the schema, comes before the record's latest entry, or
    cites a source that does not resolve. The caller rebuilds the players block in the same commit
    (``write_players_block``). Returns the record as written."""
    root = Path(root)
    problems = entry_errors(entry, player_id)
    if problems:
        raise ValueError("; ".join(problems))
    path = record_path(root, player_id)
    if path.is_file():
        current = load(player_id, root)
    else:
        player = root / PLAYER_RECORDS / ("%s.json" % player_id)
        if not player.is_file():
            raise ValueError("no permanent player record %s; create it first" % player_id)
        if not record or not {"position", "roster_position"} <= set(record):
            raise ValueError("a new contract record needs the player's position and roster position")
        listed = max([r["listed"] for r in load_all(root).values()] or [0]) + 1
        current = {"schema_version": SCHEMA_VERSION, "name": json.loads(player.read_text(encoding="utf-8"))["name"],
                   "player": player_id, "listed": listed, "position": record["position"],
                   "roster_position": record["roster_position"], "entries": []}
        if record.get("draft_pick"):
            current["draft_pick"] = record["draft_pick"]
    if current["entries"] and day(entry["date"]) < day(current["entries"][-1]["date"]):
        raise ValueError("%s: an entry dated %s comes before his latest entry (%s)"
                         % (player_id, entry["date"], current["entries"][-1]["date"]))
    for source in _entry_sources(entry):
        if not _resolves(root, source):
            raise ValueError("%s: source %s does not resolve" % (player_id, source))
    candidate = copy.deepcopy(current)
    candidate["entries"].append(copy.deepcopy(entry))
    problems = record_errors(player_id, candidate, root)
    if problems:
        raise ValueError("; ".join(problems))
    folder(root).mkdir(parents=True, exist_ok=True)
    path.write_text(dump(candidate), encoding="utf-8")
    return candidate


# ------------------------------------------------------------------ validation
def _entry_sources(entry):
    out = [entry.get("source")] + list(entry.get("sources") or [])
    if entry.get("basis"):
        out.append(entry["basis"].get("source"))
    return [s for s in out if s]


def _resolves(root, source):
    return (Path(root) / repository_relative(str(source).split("#")[0])).is_file()


def _year_errors(label, years, end, first):
    errors = []
    for y, r in (years or {}).items():
        if not re.fullmatch(r"\d{4}", str(y)):
            errors.append("%s: year %r is not a league year" % (label, y))
            continue
        status = r.get("status")
        if status not in YEAR_STATUSES:
            errors.append("%s %s: status %r is not a committed year" % (label, y, status))
            continue
        for k in ("cap", "base", "proration", "other_cap", "cash", "guaranteed_base", "approximate_cap"):
            v = r.get(k)
            if v is not None and (type(v) is not int or v < 0):
                errors.append("%s %s: %s must be a whole-dollar amount" % (label, y, k))
        parts = [r.get("base"), r.get("proration")]
        if status in ("known", "tender"):
            if r.get("cap") is None:
                errors.append("%s %s: a %s year needs its cap charge" % (label, y, status))
            elif None not in parts and r["cap"] != parts[0] + parts[1] + (r.get("other_cap") or 0):
                errors.append("%s %s: cap must equal base plus proration plus other charges" % (label, y))
        if status == "approximate":
            if r.get("approximate_cap") is None or not r.get("estimate_note"):
                errors.append("%s %s: an estimate needs its amount and its basis" % (label, y))
            elif None not in parts and r["approximate_cap"] != parts[0] + parts[1] + (r.get("other_cap") or 0):
                errors.append("%s %s: the estimate must equal base plus proration plus other charges" % (label, y))
        if status in CHARGED and end is not None and int(y) > int(end):
            errors.append("%s %s: a charge beyond the contract's last league year (%s)" % (label, y, end))
        if status in CHARGED and first is not None and int(y) < first:
            errors.append("%s %s: a charge before the contract's first league year" % (label, y))
    return errors


def record_errors(rid, record, root=ROOT):
    """Schema, date-order, source and contract problems of one record."""
    root = Path(root)
    label = "%s/%s.json" % (PLAYER_CONTRACTS, rid)
    keys = set(record)
    if not set(RECORD_KEYS) <= keys or keys - set(RECORD_KEYS) - set(RECORD_OPTIONAL):
        return ["%s: record keys must be %s" % (label, ", ".join(RECORD_KEYS))]
    errors = []
    if record["schema_version"] != SCHEMA_VERSION:
        errors.append("%s: unsupported schema version" % label)
    if record["player"] != rid:
        errors.append("%s: the record must be named by his player record id" % label)
    player = root / PLAYER_RECORDS / ("%s.json" % rid)
    if not player.is_file():
        errors.append("%s: no permanent player record %s" % (label, rid))
    elif json.loads(player.read_text(encoding="utf-8")).get("name") != record["name"]:
        errors.append("%s: the name differs from his player record" % label)
    if record["position"] not in POSITIONS:
        errors.append("%s: unknown cap position %r" % (label, record["position"]))
    if not isinstance(record["listed"], int) or record["listed"] < 1:
        errors.append("%s: listed must be his line in the register" % label)
    previous = None
    starts = {}
    ended = set()
    for n, e in enumerate(record["entries"], 1):
        where = "%s entry %d" % (label, n)
        problems = entry_errors(e, where)
        errors += problems
        if problems:
            continue
        if previous is not None and day(e["date"]) < previous:
            errors.append("%s: entries must be in date order" % where)
        previous = day(e["date"])
        for source in _entry_sources(e):
            if not _resolves(root, source):
                errors.append("%s: source %s does not resolve" % (where, source))
        kind = e["kind"]
        if kind in START_KINDS:
            if e["contract"] in starts:
                errors.append("%s: contract %s is started twice" % (where, e["contract"]))
            starts[e["contract"]] = e
            errors += _year_errors("%s (%s)" % (where, e["contract"]), _years_of(e, root), through(e),
                                   league_year(e["date"]))
        elif kind in ("contract_ended", "contract_amended"):
            if e["contract"] not in starts:
                errors.append("%s: contract %s was never started" % (where, e["contract"]))
            elif e["contract"] in ended:
                errors.append("%s: contract %s has already ended" % (where, e["contract"]))
            elif kind == "contract_amended":
                start = starts[e["contract"]]
                errors += _year_errors("%s (%s)" % (where, e["contract"]), e["years"], through(start),
                                       league_year(start["date"]))
                if start.get("rookie"):
                    answer, _ = renegotiable_on(dict(record, entries=[x for x in record["entries"]
                                                                       if day(x["date"]) < day(e["date"])]),
                                                day(e["date"]), root)
                    if answer is not True:
                        errors.append("%s: a rookie contract amended before it may be renegotiated" % where)
            if kind == "contract_ended":
                ended.add(e["contract"])
    for n, e in enumerate(record["entries"]):
        if e.get("kind") == "contract_ended" and e.get("how") == "promoted":
            later = [x for x in record["entries"][n + 1:] if x.get("kind") in START_KINDS]
            if not later or later[0].get("date") != e.get("date"):
                errors.append("%s: a promotion ends %s only with a new contract the same day" % (label, e.get("contract")))
    open_contracts = [c for c in starts if c not in ended]
    if len(open_contracts) > 1:
        errors.append("%s: more than one open contract (%s)" % (label, ", ".join(open_contracts)))
    return errors


def method_errors(records, root=ROOT, data=None):
    """A contract the in-season method computed must hold the method's terms, and a practice-squad
    contract the season's weekly rate and pay weeks."""
    errors = []
    terms = method(root, data)
    cited = [terms.get("proration", {}).get("source"), terms.get("promotion", {}).get("source"),
             terms.get("promotion", {}).get("applied")]
    cited += [part.get("source") for season in terms.get("seasons", {}).values() for part in season.values()]
    for source in cited:
        if not source or not _resolves(root, source):
            errors.append("The in-season terms method cites %s, which does not resolve" % source)
    for rid, record in records.items():
        for e in entries(record):
            try:
                if e["kind"] == "contract_signed" and e.get("method"):
                    want = computed_years(e, root, terms)
                    if (e.get("years") or {}) != want:
                        errors.append("%s: %s does not hold the in-season method's terms" % (rid, e["contract"]))
                elif e["kind"] == "practice_squad":
                    season = league_year(e["date"])
                    if e["weekly_rate"] != practice_squad_rate(season, root, terms):
                        errors.append("%s: %s is not at the season's practice-squad weekly rate" % (rid, e["contract"]))
                    if e["weeks"] != len(pay_weeks(season, root)):
                        errors.append("%s: %s does not count the season's pay weeks" % (rid, e["contract"]))
            except (OSError, ValueError, KeyError) as exc:
                errors.append("%s: %s cannot be checked against the in-season method: %s" % (rid, e.get("contract"), exc))
    return errors


def errors(root=ROOT):
    """Every problem with the contract records (scripts/validate_repository.py wires this): each
    record's schema, dates, sources, terms and charges; one open contract for every player the
    roster record lists, and only for them; no rookie contract amended before it may be
    renegotiated; the in-season method's terms; the dead-money lines; no entry after the master
    date; and the inputs' players block and date equal to ``rows()``."""
    root = Path(root)
    out = []
    try:
        records = load_all(root)
        data = inputs(root)
    except (OSError, ValueError) as exc:
        return ["Player contract records unreadable: %s" % exc]
    if not records:
        return ["No player contract records in %s" % PLAYER_CONTRACTS]
    lines = {}
    for rid, record in records.items():
        out += record_errors(rid, record, root)
        if record.get("listed") in lines:
            out.append("%s and %s hold the same register line" % (lines[record["listed"]], rid))
        lines[record.get("listed")] = rid
    if out:
        return out
    out += method_errors(records, root, data)
    # One open contract for each player the roster record lists, and only for them.
    from . import roster as roster_record
    roster_path = root / repository_relative(data["current_roster"])
    listed = {p["name"] for p in roster_record.load(roster_path)["players"]}
    open_names = {r["name"] for r in records.values() if contract_on(r, None, root) is not None}
    for name in sorted(listed - open_names):
        out.append("%s is on the roster record without an open contract" % name)
    for name in sorted(open_names - listed):
        out.append("%s holds an open contract but is not on the roster record" % name)
    # The dead-money lines: each charge on one line; the club-level rows fill the rest.
    taken = [item["line"] for r in records.values() for e in entries(r, "contract_ended")
             for item in e.get("dead_money") or ()]
    if len(taken) != len(set(taken)):
        out.append("Two dead-money charges hold the same line")
    elif taken and max(taken) > len(taken) + len(data.get("dead_money", [])):
        out.append("The dead-money lines leave a gap the club-level rows do not fill")
    # No entry dated after the master date.
    try:
        from .player_bios import master_date
        master = master_date(root)
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        master = None
    if master is not None:
        for rid, record in records.items():
            for e in record["entries"]:
                if day(e["date"]) > master:
                    out.append("%s: an entry dated %s is after the master date" % (rid, e["date"]))
    if data.get("players") != rows(root, records=records, years=horizon(data)):
        out.append("The players block of %s differs from the contract records; rebuild it" % PLAYER_FINANCES)
    if data.get("as_of") != as_of(root, records):
        out.append("The date of %s differs from the latest contract entry; rebuild it" % PLAYER_FINANCES)
    return out


def history_through(root=ROOT):
    """The day the page history closes (data/pages/history.json "through"): entries after it are
    new business for the history pages' appended parts."""
    data = json.loads((Path(root) / PAGE_HISTORY).read_text(encoding="utf-8"))
    return day(data["through"])
