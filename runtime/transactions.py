"""Injury replacement in season, end to end (rebuild step 5, D1; docs/rebuild_plan.md, step 5).

An injury replacement is an ``injury_replacement`` event (runtime/open_events.py): brought by the
general manager with the medical staff, known to Stone, the general manager and the medical staff,
decided by the general manager under Document 3 rows 3, 5 and 7, with Stone's football
recommendation asked. It opens for a Jacksonville active-roster player whose instruction from a
closed game is long term (the game's ``long_term`` severity), or when the players out for the next
game leave the active roster short of the game-day minimum (``usage.MINIMUM_GAME_DAY`` through
``usage.lineup_errors``); a shorter injury opens nothing. A designated-for-return player whose
windows have passed and whose clearance is recorded raises one when he needs a place on the 53.
One event per player whose list question is open.

The event's facts and options come from stored facts only, each with its source and never a grade:
the medical communication, whether a place on the 53 is open, whether the active roster can dress a
legal team for the next game (with the date the check was made), his place on the chart and the
contract facts; the options are the moves that can be made before the next game: the practice
squad, a designated-for-return player whose windows have passed and who is cleared, Jacksonville's
former players still unplaced under the rails (method section 9), and the players other clubs have
put on waivers whose claim period ends before the game (library/2014_playing_and_roster_rules.md,
W1 to W4). Free agents another club released during the season are listed as a fact, players
Jacksonville may pursue under method section 4, whose draw is made at the date the player signs with
a club, against that contract, so none can fill the place before then. No option names a later real
move: every rails row read is gated on or before the date.

The general manager's criteria (the need, the legal options on the date, the contract facts) are
the event's first process entry, recorded when it is raised, so they come before Stone's answer
(Document 1 sections 9.1 and 9.4). His decision is a transaction record (``transaction-v1``) in the
roster's data folder (``SeasonPaths.transactions``): the criteria it applies, Stone's answer reduced
to its substance (never his words), the basis, and the moves. ``scripts/apply_transaction.py`` is
the single writer of everything the decision changes. A waiver claim is decided when its claim
period ends, by this career's own waiver order (``waiver_order``) against the club that really
claimed the player, read only once the claim's public date has passed; a claim against a club ahead
of Jacksonville in the order is lost. A section 4 pursuit is decided by one private draw at the
player's real signing date against the contract he really signed; a player who has signed with no
club has no contract to compare and cannot be drawn.

The career layer: this module reads the job record, the decision queue and the event store, so it
is in tests/test_career_layer_isolation.py's LAYER, and nothing that resolves a game imports it.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from types import SimpleNamespace

from . import current_job, decision_queue, decisions, open_events, people, player_bios, player_contracts
from . import roster as roster_record
from .events import EVENT_ID
from .seasons import SeasonPaths
from .usage import group as kernel_group, lineup_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "transaction-v1"
KIND = "injury_replacement"
AUTHORITY_ROWS = ("3", "5", "7")
# The moves the tool makes: (the list a player leaves, the list he joins). "none" is outside the club.
MOVES = {"reserve": ("active", "reserve"), "promoted": ("practice_squad", "active"),
         "reinstated": ("reserve", "active"), "signed": ("none", "active"), "claimed": ("none", "active"),
         "practice_squad": ("none", "practice_squad")}
# The ways a player comes to the 53 from outside the club.
VIA = {"signed": ("former_player", "section_4"), "claimed": ("waiver_claim",),
       "practice_squad": ("former_player",)}
NOT_BUILT = ("A release, a waiver or a trade to open a place is not built for the in-season roster moves yet: the "
             "salary a player has earned this season and the bonus that accelerates when he leaves need a contract "
             "rule the records do not hold. The move is put to the user.")
STATUSES = ("decided", "applied", "claim_lost", "pursuit_lost")
RESERVE_STATUS = {"ordinary": "Reserve/Injured", "designated": "Reserve/Injured, designated for return"}
# The roster page's position groups, by roster position.
GROUP_WORDS = {"QB": "Quarterbacks", "RB": "Running backs", "FB": "Fullbacks", "WR": "Wide receivers",
               "TE": "Tight ends", "OT": "Offensive line", "G": "Offensive line", "C": "Offensive line",
               "DE": "Defensive line", "DT": "Defensive line", "LB": "Linebackers", "CB": "Defensive backs",
               "S": "Defensive backs", "DB": "Defensive backs", "K": "Specialists", "P": "Specialists",
               "LS": "Specialists"}
# The game-day groups (runtime/usage.MINIMUM_GAME_DAY) in football words.
KERNEL_WORDS = {"QB": "Quarterbacks", "RB": "Running backs", "FB": "Fullbacks", "WR": "Wide receivers",
                "TE": "Tight ends", "OL": "Offensive linemen", "DL": "Defensive linemen", "LB": "Linebackers",
                "DB": "Defensive backs", "K": "Kicker", "P": "Punter", "LS": "Long snapper"}
# A league position on the transaction record, as the roster writes it.
ROSTER_POSITION = {"T": "OT", "OT": "OT", "G": "G", "OG": "G", "C": "C", "OLB": "LB", "ILB": "LB", "MLB": "LB",
                   "LB": "LB", "SS": "S", "FS": "S", "S": "S", "NT": "DT", "DT": "DT", "DE": "DE", "CB": "CB",
                   "QB": "QB", "RB": "RB", "FB": "FB", "WR": "WR", "TE": "TE", "K": "K", "P": "P", "LS": "LS",
                   "DB": "DB"}
# The cap accounting group of a roster position (the contract records' pairs; DB has none of its own).
CAP_POSITION = {"QB": "QB", "RB": "RB", "FB": "FB", "WR": "WR", "TE": "TE", "OT": "OT", "G": "OG", "C": "C",
                "DE": "EDGE", "DT": "IDL", "LB": "LB", "CB": "CB", "S": "S", "K": "K", "P": "P", "LS": "LS"}
# Rails moves that take a player off a club, and the ones that put him on one.
DEPARTING = ("waived", "released", "ps_release", "released_unspecified")
JOINING = ("fa_signing", "re_signing", "ps_signing", "ps_promotion", "waiver_claim", "ps_poach", "trade_in",
           "activation_return")
PURSUIT_PROCEDURE = "inseason-fa-pursuit-2014-v1"
CHANCE_TABLE = ((0.80, 0.0), (1.00, 0.50), (1.25, 0.90))


class Refused(ValueError):
    """A step this module refuses, in football words (nothing was written)."""


# ------------------------------------------------------------------ small helpers
def _rel(root, path):
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()


def _day(value):
    return value if isinstance(value, dt.date) and not isinstance(value, dt.datetime) else dt.date.fromisoformat(
        str(value)[:10])


def long_date(day):
    day = _day(day)
    return "%s %d, %d" % (day.strftime("%B"), day.day, day.year)


def weekday_date(day):
    day = _day(day)
    return "%s, %s" % (day.strftime("%A"), long_date(day))


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", people.slugify(text).replace("_", "-")).strip("-")


def _json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def paths(season, root=ROOT):
    return SeasonPaths(int(season), Path(root))


def roster(season, root=ROOT):
    return roster_record.load(paths(season, root).roster)


def roster_rel(season, root=ROOT):
    return _rel(root, paths(season, root).roster)


def strip_links(text):
    """A roster value without its Markdown links (the fact table shows words; links go to pages)."""
    text = re.sub(r"\s*\(\[[^\]]*\]\([^)]*\)\)", "", str(text))
    text = re.sub(r";?\s*\[[^\]]*\]\([^)]*\)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def decider(root=ROOT, job=None):
    """The party Document 3 rows 3, 5 and 7 give the final word (the job record's authority map)."""
    job = current_job.load(root) if job is None else job
    domains = {d["row"]: d for d in (current_job.appointment(job) or {}).get("authority", {}).get("domains", ())}
    finals = {tuple(domains.get(r, {}).get("final") or ()) for r in AUTHORITY_ROWS}
    if len(finals) != 1 or len(next(iter(finals))) != 1:
        raise Refused("Document 3 rows 3, 5 and 7 do not name one party with the final word on a roster move")
    return next(iter(finals))[0]


def club_codes(season, root=ROOT):
    """{club name: code} from the in-season rails library, or {} when the season has none."""
    from . import rails
    data = rails.load(int(season), root)
    return dict(data.codes) if data is not None else {}


def club_name(season, code, root=ROOT):
    return {c: n for n, c in club_codes(season, root).items()}.get(code, code)


# ------------------------------------------------------------------ games and availability
def fixtures(season, root=ROOT):
    return open_events.club_fixtures(int(season), root)


def receipts(season, root=ROOT, before_week=None):
    """The closed games of the season (regular season, then the postseason), before ``before_week``."""
    p = paths(season, root)
    out = []
    for folder in (p.receipts, p.postseason_receipts):
        if folder.is_dir():
            for path in sorted(folder.glob("*.json")):
                if path.name == "README.md":
                    continue
                r = _json(path)
                if before_week is None or int(r["week"]) < int(before_week):
                    out.append(r)
    return out


def closed(season, game, root=ROOT):
    from .week_inputs import receipt_name
    return (paths(season, root).receipts / receipt_name(game)).is_file()


def jacksonville_receipt(season, week, root=ROOT):
    """The closed Jacksonville game of ``week``, or None."""
    from .week_inputs import receipt_name
    game = next((g for g in fixtures(season, root) if int(g["week"]) == int(week)), None)
    if game is None:
        return None, None
    path = paths(season, root).receipts / receipt_name(game)
    return game, (_json(path) if path.is_file() else None)


def next_game(season, root=ROOT, after=None):
    """Jacksonville's next game not yet closed (after ``after``, a date, when given), or None."""
    for game in fixtures(season, root):
        if after is not None and _day(game["date"]) <= _day(after):
            continue
        if not closed(season, game, root):
            return game
    return None


def game_name(game, club=open_events.CLUB):
    """"the Week 7 game against the Cleveland Browns"."""
    other = game["home"] if game["away"] == club else game["away"]
    return "the Week %d game %s the %s" % (int(game["week"]), "at" if game["away"] == club else "against", other)


def game_words(game, club=open_events.CLUB):
    """"Week 7 game against the Cleveland Browns, Sunday, October 19, 1 p.m. ET"."""
    return "%s, %s" % (game_name(game, club)[len("the "):], open_events.at_text(open_events.kickoff(game)))


def fixture_source(season, game, root=ROOT):
    p = paths(season, root)
    games = _json(p.schedule)["games"]
    index = next(n for n, g in enumerate(games) if g["game_id"] == game["game_id"])
    return {"path": _rel(root, p.schedule), "pointer": "/games/%d" % index}


def outs_for(season, game, data, root=ROOT):
    """{active player: why} out for ``game`` as the game reads it (runtime/week_inputs): his roster
    availability does not clear him for game day, or a closed game's injury holds him inside its
    projected return. A note the staff cannot read is out, never cleared."""
    from .week_inputs import injured_out, roster_available
    game_day = _day(game["date"])
    held = injured_out(receipts(season, root, before_week=int(game["week"])), game_day, int(season))
    out = {}
    for row in roster_record.players(data, ("active",)):
        note = row.get("availability") or ""
        try:
            cleared = roster_available(note, game_day, int(season))
        except ValueError:
            out[row["name"]] = "his medical status is not recorded in a form the staff can read"
            continue
        if not cleared:
            out[row["name"]] = "out on his medical instruction"
        elif row["name"] in held:
            out[row["name"]] = "inside his projected return"
    return out


def lineup(data, outs):
    """usage.lineup_errors over the active players not out: the groups short of the game-day minimum."""
    players = [SimpleNamespace(position=row["position"]) for row in roster_record.players(data, ("active",))
               if row["name"] not in outs]
    return lineup_errors(players)


def legal_team_fact(season, game, data, outs, on, root=ROOT):
    """The event's fact on whether the active roster can dress a legal team for ``game``."""
    errors = lineup(data, outs)
    when = long_date(on)
    if errors:
        value = "No: %s for %s, as of %s" % ("; ".join(
            "%s %s" % (KERNEL_WORDS.get(e.split(":")[0], e.split(":")[0]), e.split(": ", 1)[1]) for e in errors),
            game_name(game), when)
    else:
        value = "Yes: every position group can dress its game-day minimum for %s, as of %s" % (
            game_name(game), when)
    return {"label": open_events.LEGAL_TEAM_FACT, "value": value,
            "source": {"path": roster_rel(season, root), "pointer": "/players"}}, errors


# ------------------------------------------------------------------ the waiver rules (library W1 to W5)
def claim_period_end(requested):
    """When the claiming period of a waiver requested on day ``requested`` expires (library W1): 4
    p.m. ET the next day for a request made Monday to Thursday, 4 p.m. ET the following Monday for one
    made on a Friday or Saturday. A Sunday request has no stated period (W6): None."""
    day = _day(requested)
    if day.weekday() == 6:
        return None
    nxt = day + dt.timedelta(days=3 if day.weekday() == 4 else 2 if day.weekday() == 5 else 1)
    return open_events.et(nxt, 16)


def veteran_waivers_from(season, root=ROOT):
    """The first day a released vested veteran is subject to waivers (library W5;
    runtime/deadlines.waivers_from, read from the season's league dates)."""
    from . import deadlines
    found = deadlines.waivers_from(int(season), root)
    return _day(found) if found else None


def _records(season, root, on):
    """{club: (wins, losses, ties)} from the closed games played before day ``on``, every club."""
    from .standings import DIVISION_OF
    out = {club: [0, 0, 0] for club in DIVISION_OF}
    games = []
    for r in receipts(season, root):
        if r.get("game_type", "regular") != "regular":
            continue
        game = next((g for g in paths(season, root).regular_games()
                     if g["away"] == r["away"] and g["home"] == r["home"] and int(g["week"]) == int(r["week"])), None)
        if game is None or _day(game["date"]) >= _day(on):
            continue
        games.append((r["away"], r["home"], r["final_score"]))
        a, h = int(r["final_score"][r["away"]]), int(r["final_score"][r["home"]])
        for club, mine, theirs in ((r["away"], a, h), (r["home"], h, a)):
            out[club][0 if mine > theirs else 1 if mine < theirs else 2] += 1
    return {c: tuple(v) for c, v in out.items()}, games


def _pct(record):
    w, l, t = record
    n = w + l + t
    return (w + 0.5 * t) / n if n else 0.0


def _combined(records, opponents):
    wins = games = 0.0
    for club in opponents:
        w, l, t = records[club]
        wins += w + 0.5 * t
        games += w + l + t
    return wins / games if games else 0.0


def waiver_order(season, on, root=ROOT):
    """This career's waiver order on day ``on`` (library W2 and W3): the inverse of the current
    season's standings from the Tuesday after the third weekend, from the games closed before the day.
    Each club with its record and its strength of schedule under both readings W3 leaves open (the
    opponents played so far; every scheduled opponent at its current record); [(club, record, sos
    played, sos scheduled)] worst first, ties in winning percentage in the order of the played
    reading. Before the change (W2: the draft order) nothing is built and it is refused."""
    records, games = _records(season, root, on)
    weeks = sorted({int(g["week"]) for g in paths(season, root).regular_games()})
    third = max((_day(g["date"]) for g in paths(season, root).regular_games() if int(g["week"]) == weeks[2]))
    change = third + dt.timedelta(days=(1 - third.weekday()) % 7 or 7)
    if _day(on) < change:
        raise Refused("Before %s the waiver order is the draft order (library W2), which the in-season roster "
                      "moves do not read" % long_date(change))
    played = {c: [] for c in records}
    for away, home, _ in games:
        played[away].append(home)
        played[home].append(away)
    scheduled = {c: [] for c in records}
    for g in paths(season, root).regular_games():
        scheduled[g["away"]].append(g["home"])
        scheduled[g["home"]].append(g["away"])
    rows = [(c, records[c], _combined(records, played[c]), _combined(records, scheduled[c])) for c in records]
    return sorted(rows, key=lambda r: (_pct(r[1]), round(r[2], 9), r[0]))


def claim_priority(season, on, first, second, root=ROOT):
    """(the club ahead in the waiver order, why) between clubs ``first`` and ``second`` on day ``on``;
    the club None when a tie the sourced rule does not settle remains (W3, W6): the strength of
    schedule decides it only when both readings agree."""
    rows = {r[0]: r for r in waiver_order(season, on, root)}
    a, b = rows[first], rows[second]
    if _pct(a[1]) != _pct(b[1]):
        ahead = first if _pct(a[1]) < _pct(b[1]) else second
        return ahead, "the worse record claims first"
    played = (round(a[2], 9), round(b[2], 9))
    sched = (round(a[3], 9), round(b[3], 9))
    if played[0] == played[1] or sched[0] == sched[1] or (played[0] < played[1]) != (sched[0] < sched[1]):
        return None, ("the two clubs have the same record and the strength of schedule does not settle the order "
                      "under the sourced rule")
    return (first if played[0] < played[1] else second), "the same record; the weaker schedule claims first"


# ------------------------------------------------------------------ the rails, read on a date
def rails_rows(season, on, root=ROOT):
    """The in-season rails rows with a player identity whose public date is on or before ``on`` and
    that are applied league moves (never a later row, never a stripped Jacksonville row)."""
    from . import rails
    data = rails.load(int(season), root)
    if data is None:
        return []
    on = _day(on)
    return [r for r in data.rows if r.get("uid") and r.get("gate_date") and _day(r["gate_date"]) <= on
            and r.get("outcome") == "APPLY"]


def rails_as_of(season, root=ROOT):
    from . import rails
    data = rails.load(int(season), root)
    return data.as_of if data is not None else None


def _rails_source(season, row, root):
    from . import rails
    data = rails.load(int(season), root)
    folder = rails.data_dir(int(season), root)
    for shard in data.manifest["shards"]:
        rows = _json(folder / shard["path"])["rows"]
        for n, r in enumerate(rows):
            if r.get("id") == row["id"]:
                return {"path": _rel(root, folder / shard["path"]), "pointer": "/rows/%d" % n}
    raise Refused("the league record holds no row %s" % row["id"])


def waiver_candidates(season, at, root=ROOT, groups=None):
    """Players other clubs put on waivers whose claim period is still open at ``at`` (a datetime):
    [(row, claim period end)], each read only from a row public on or before the date. From the
    veteran waiver date a vested veteran's release goes through waivers too (W5)."""
    veterans = veteran_waivers_from(season, root)
    out = []
    for row in rails_rows(season, at.date(), root):
        if row["kind"] == "waived" or (row["kind"] == "released" and veterans and _day(row["real_date"]) >= veterans):
            end = claim_period_end(row["real_date"])
            if end is None or end <= at:
                continue
            if groups and kernel_group(ROSTER_POSITION.get(row.get("position"), row.get("position"))) not in groups:
                continue
            out.append((row, end))
    return out


def free_agents(season, on, root=ROOT, groups=None):
    """Players another club released during the season who have not signed with a club by ``on``
    (rows public by then): [(release row)]. A released vested veteran from the veteran waiver date is
    on waivers, not free (W5)."""
    veterans = veteran_waivers_from(season, root)
    rows = rails_rows(season, on, root)
    last = {}
    for row in sorted(rows, key=lambda r: (r["gate_date"], r["id"])):
        last.setdefault(row["uid"], []).append(row)
    out = []
    for uid, moves in last.items():
        final = moves[-1]
        if final["kind"] in DEPARTING and final["kind"] != "waived" and not (
                final["kind"] == "released" and veterans and _day(final["real_date"]) >= veterans):
            if groups and kernel_group(ROSTER_POSITION.get(final.get("position"), final.get("position"))) not in groups:
                continue
            out.append(final)
        elif final["kind"] == "waived":
            end = claim_period_end(final["real_date"])
            if end is not None and end.date() < _day(on):
                # Cleared waivers with no later move on the record by the date: a free agent.
                if groups and kernel_group(ROSTER_POSITION.get(final.get("position"), final.get("position"))) not in groups:
                    continue
                out.append(final)
    return sorted(out, key=lambda r: (r.get("player") or "", r["id"]))


def real_signing(season, uid, after, on, root=ROOT):
    """The first row public by ``on`` that puts player ``uid`` on another club on or after day
    ``after`` (his real signing), or None."""
    found = [r for r in rails_rows(season, on, root) if r["uid"] == uid and r["kind"] in JOINING
             and _day(r["real_date"]) >= _day(after)]
    return min(found, key=lambda r: (r["real_date"], r["gate_date"], r["id"])) if found else None


def real_claim(season, uid, requested, on, root=ROOT):
    """The real claim of a player waived on day ``requested`` (a waiver claim row public by ``on``
    dated inside his claim period), or None."""
    end = claim_period_end(requested)
    if end is None:
        return None
    found = [r for r in rails_rows(season, on, root) if r["uid"] == uid and r["kind"] == "waiver_claim"
             and _day(requested) <= _day(r["real_date"]) <= end.date()]
    return min(found, key=lambda r: (r["real_date"], r["id"])) if found else None


# ------------------------------------------------------------------ the event
def _availability_pointer(season, data, name, root):
    index = next(n for n, row in enumerate(data["players"]) if row["name"] == name)
    return {"path": roster_rel(season, root), "pointer": "/players/%d/availability" % index}


def _row_pointer(season, data, name, root, key="players"):
    index = next(n for n, row in enumerate(data[key]) if row["name"] == name)
    return {"path": roster_rel(season, root), "pointer": "/%s/%d" % (key, index)}


def place_fact(season, data, root):
    n = roster_record.counts(data)
    if n["open_active"] > 0:
        value = "%d of %d on the active roster: %s open" % (n["active"], data["active_limit"],
                                                          "one place" if n["open_active"] == 1 else
                                                          "%d places" % n["open_active"])
    else:
        value = ("%d of %d on the active roster: a place opens only when a player leaves it, as a reserve "
                 "placement does" % (n["active"], data["active_limit"]))
    return {"label": "A place on the 53", "value": value, "source": {"path": roster_rel(season, root), "pointer": "/players"}}


def chart_fact(season, name, root):
    p = paths(season, root)
    chart = _json(p.depth_chart)
    for grp, order in (chart.get("depth") or {}).items():
        if name in order:
            roles = (chart.get("roles") or {}).get(name) or []
            words = "%s, %d of %d on the depth chart" % (KERNEL_WORDS.get(grp, grp), order.index(name) + 1, len(order))
            if roles:
                words += "; he holds the %s role%s" % (", ".join(r.replace("_", " ") for r in roles),
                                                       "s" if len(roles) > 1 else "")
            return {"label": "His place on the chart", "value": words,
                    "source": {"path": _rel(root, p.depth_chart), "pointer": "/depth/%s" % grp}}
    return {"label": "His place on the chart", "value": "Not on the depth chart",
            "source": {"path": _rel(root, p.depth_chart)}}


def contract_fact(season, name, root):
    records = player_contracts.load_all(root)
    rid = next((k for k, r in records.items() if r["name"] == name), None)
    if rid is None:
        return {"label": "His contract", "value": "Not on the contract records", "source": None}
    current = player_contracts.contract_on(records[rid], None, root)
    year = (current or {}).get("years", {}).get(str(season)) if current else None
    path = {"path": _rel(root, player_contracts.record_path(root, rid))}
    if not year or year.get("cap") is None:
        return {"label": "His contract", "value": "The %d charge is not on the record" % int(season), "source": path}
    return {"label": "His contract", "value": "%d charge $%s; a reserve placement leaves the contract and the charge "
                                              "as they are" % (int(season), "{:,}".format(year["cap"])), "source": path}


def options(season, at, data, groups, root=ROOT, game=None):
    """The moves that can be made before ``game``, from stored facts only: [{name, position, basis,
    source}], never a grade."""
    out = []
    for row in roster_record.players(data, ("practice_squad",)):
        out.append({"name": row["name"], "position": row["position"],
                    "basis": "Practice squad (%s): a promotion to the 53 can be made before the game" % (
                        row["status"].split("(", 1)[1].rstrip(")") if "(" in row["status"] else "on the squad"),
                    "source": _row_pointer(season, data, row["name"], root)})
    for row in roster_record.players(data, ("reserve",)):
        window = return_window(row)
        back = window[1] if window else None
        if back is None or game is None or back > _day(game["date"]):
            continue
        from .week_inputs import roster_available
        try:
            if not roster_available(row.get("availability") or "", _day(game["date"]), int(season)):
                continue
        except ValueError:
            continue
        out.append({"name": row["name"], "position": row["position"],
                    "basis": "Designated for return: back to the 53 from %s with the medical staff's clearance" % (
                        long_date(back)), "source": _row_pointer(season, data, row["name"], root)})
    on_roster = {r["name"] for r in data["players"]}
    for n, row in enumerate(data["departures"]):
        disposition = str(row.get("disposition") or "")
        if not disposition.lower().startswith("unplaced") or row["name"] in on_roster:
            continue
        out.append({"name": row["name"], "position": row["position"],
                    "basis": "A former Jacksonville player, unplaced since he left the club: a signing can be made "
                             "before the game",
                    "source": {"path": roster_rel(season, root), "pointer": "/departures/%d" % n}})
    if game is not None:
        kick = open_events.kickoff(game)
        for row, end in waiver_candidates(season, at, root, groups):
            if end >= kick:
                continue
            out.append({"name": row["player"], "position": ROSTER_POSITION.get(row.get("position"), row.get("position")),
                        "basis": "On waivers from the %s since %s; claims close at %s, and the waiver order decides "
                                 "the award" % (club_name(season, row["club"], root), long_date(row["real_date"]),
                                                open_events.at_text(end)),
                        "source": _rails_source(season, row, root)})
    return out


def free_agent_fact(season, on, groups, root=ROOT):
    """The fact listing the free agents another club released in season, players Jacksonville may
    pursue under method section 4 (none can fill the place before he signs with a club)."""
    found = free_agents(season, on, root, groups)
    if not found:
        return None
    names = "; ".join("%s, %s, let go by the %s %s" % (r["player"], ROSTER_POSITION.get(r.get("position"),
                      r.get("position")), club_name(season, r["club"], root), long_date(r["real_date"])) for r in found)
    from . import rails
    return {"label": "Free agents Jacksonville may pursue",
            "value": ("%s. The league method decides a pursuit at the date the player signs with a club, against "
                      "that contract, so none can fill this place before then" % names),
            "source": {"path": _rel(root, rails.data_dir(int(season), root) / "manifest.json")}}


def return_window(row):
    """(practice from, active list from) of a designated-for-return player: six and eight weeks from
    his placement (library R6), read from the dated placement in his roster status."""
    placed = re.search(r"\(placed ([A-Z][a-z]+ \d{1,2}, \d{4})", row.get("status") or "")
    if "designated for return" not in (row.get("status") or "").lower() or not placed:
        return None
    day = dt.datetime.strptime(placed[1], "%B %d, %Y").date()
    return day + dt.timedelta(weeks=6), day + dt.timedelta(weeks=8)


def event_id_for(raised, subject):
    return "%s-roster-place-%s" % (raised.date().isoformat(), slug(subject))


def open_for(season, subject, root=ROOT):
    """The open injury replacement for ``subject``, or None."""
    return next((r for r in open_events.load(int(season), root) if r["kind"] == KIND and r["subject"] == subject
                 and r["state"] != "resolved"), None)


def build_event(season, subject, why, at, data, game, groups, root=ROOT, medical=None, source=None, by=None):
    """An injury replacement event (open-event-v1), its criteria entry first (the need, the legal options
    on the date and the contract facts, each with its source in the facts and options)."""
    job = current_job.load(root)
    deciding = decider(root, job)
    outs = outs_for(season, game, data, root)
    legal, _ = legal_team_fact(season, game, data, outs, at.date(), root)
    facts = []
    if medical is not None:
        facts.append(medical)
    facts += [{"label": "Next game", "value": game_words(game), "source": fixture_source(season, game, root)},
              place_fact(season, data, root), legal]
    if subject in {r["name"] for r in data["players"]}:
        facts.append(chart_fact(season, subject, root))
        contract = contract_fact(season, subject, root)
        if contract["source"] is not None:
            facts.append(contract)
    fa = free_agent_fact(season, at.date(), groups, root)
    if fa is not None:
        facts.append(fa)
    opts = options(season, at, data, groups, root, game)
    names = ", ".join("%s (%s)" % (o["name"], o["position"]) for o in opts) or "none on the record"
    criteria = {"at": open_events.iso(at), "kind": "criteria", "by": deciding,
                "what": ("The need: %s. The legal moves before %s: %s. The contract facts: %s." % (
                    why.rstrip("."), game_name(game), names,
                    next((f["value"] for f in facts if f["label"] == "His contract"), "none on the record"))),
                "source": {"path": roster_rel(season, root), "pointer": "/players"}}
    raised_source = source or {"path": roster_rel(season, root)}
    return {
        "schema": open_events.SCHEMA, "id": event_id_for(at, subject), "kind": KIND, "season": int(season),
        "subject": subject,
        "raised": {"at": open_events.iso(at), "by": by or deciding, "source": raised_source},
        "known_to": sorted({"stone", deciding, "medical_staff"} & set((job.get("parties") or {}))),
        "authority": {"rows": list(AUTHORITY_ROWS), "decides": deciding}, "stone_part": "recommends",
        "summary": {"text": why, "author": current_job.party_name(job, deciding), "date": at.date().isoformat()},
        "staff_position": None, "consequence": None, "facts": facts, "options": opts,
        "deadline": {"at": open_events.iso(open_events.kickoff(game)),
                     "label": "Kickoff of %s" % game_name(game),
                     "source": fixture_source(season, game, root)},
        "state": "open", "process": [criteria], "queue_item": None, "response": None, "resolution": None}


def injury_events(season, week, root=ROOT, at=None):
    """The injury replacement events Week ``week``'s closed Jacksonville game opens: one for each
    active player whose instruction from the game is long term, and one for each game-day group the
    players out for the next game leave short of its minimum that no such event covers. Returns
    ([event], [note]); raises Refused when the close has not recorded the medical communications."""
    from . import week_pages
    root = Path(root).resolve()
    game, receipt = jacksonville_receipt(season, week, root)
    if receipt is None:
        raise Refused("Week %d's Jacksonville game is not closed" % int(week))
    at = open_events.master_at(root) if at is None else at
    data = roster(season, root)
    nxt = next_game(season, root)
    notes, events = [], []
    if nxt is None:
        return [], ["No Jacksonville game is left to play; no roster place is open"]
    wp = week_pages.Season(root, int(season))
    rows = {r["name"]: r for r in data["players"]}
    long_term = []
    for injury in week_pages.ours_injured(receipt):
        row = rows.get(injury["player"])
        if row is None or row["list"] != "active":
            continue
        text, source = week_pages.availability_entry(wp, receipt, injury)
        if row.get("availability") != text or (row.get("sources") or {}).get("availability") != source:
            raise Refused("The close has not recorded %s's medical communication on the roster record yet; it "
                          "comes first" % injury["player"])
        if injury.get("severity") != "long_term":
            notes.append("%s: %s, not long term; no roster question opens" % (injury["player"],
                                                                              week_pages.severity_words(injury)))
            continue
        long_term.append((injury, row, source))
    outs = outs_for(season, nxt, data, root)
    short = lineup(data, outs)
    short_groups = [e.split(":")[0] for e in short]
    covered = set()
    for injury, row, source in long_term:
        if open_for(season, row["name"], root) is not None:
            notes.append("%s: his roster question is already open" % row["name"])
            continue
        grp = kernel_group(row["position"])
        covered.add(grp)
        medical = {"label": "Medical communication", "value": "%s (from the medical staff)" % strip_links(row["availability"]),
                   "source": _availability_pointer(season, data, row["name"], root)}
        why = ("%s is out long term after the Week %d game; his place on the 53 is the club's decision before the "
               "next game" % (row["name"], int(week)))
        events.append(build_event(season, row["name"], why, at, data, nxt, {grp}, root, medical,
                                  {"path": source}))
    for grp in short_groups:
        if grp in covered:
            continue
        subject = KERNEL_WORDS.get(grp, grp)
        if open_for(season, subject, root) is not None:
            notes.append("%s: the shortfall's roster question is already open" % subject)
            continue
        out = sorted(n for n in outs if kernel_group(rows[n]["position"]) == grp)
        why = ("The players out for %s leave the club short of its game-day minimum at %s (%s out)" % (
            game_name(nxt), subject.lower(), ", ".join(out) or "none listed"))
        events.append(build_event(season, subject, why, at, data, nxt, {grp}, root))
    if not events and not notes:
        notes.append("No Jacksonville player's instruction from the Week %d game is long term, and the active roster "
                     "can dress a legal team for the next game; no roster question opens" % int(week))
    return events, notes


def return_event(season, name, root=ROOT, at=None):
    """The event a designated-for-return player's clearance raises when he needs a place on the 53."""
    root = Path(root).resolve()
    at = open_events.master_at(root) if at is None else at
    data = roster(season, root)
    row = next((r for r in data["players"] if r["name"] == name), None)
    if row is None or row["list"] != "reserve" or "designated for return" not in row["status"].lower():
        raise Refused("%s is not on reserve/injured designated for return" % name)
    window = return_window(row)
    if window is None:
        raise Refused("%s's reserve placement date is not on the roster record" % name)
    back = window[1]
    if at.date() < back:
        raise Refused("%s may not return to the active list before %s" % (name, long_date(back)))
    nxt = next_game(season, root, after=at.date())
    from .week_inputs import roster_available
    try:
        cleared = nxt is not None and roster_available(row.get("availability") or "", _day(nxt["date"]), int(season))
    except ValueError:
        cleared = False
    if not cleared:
        raise Refused("%s's medical clearance is not on the roster record; the medical staff's clearance comes "
                      "first" % name)
    if nxt is None:
        raise Refused("No Jacksonville game is left to play")
    if open_for(season, name, root) is not None:
        raise Refused("%s's roster question is already open" % name)
    medical = {"label": "Medical communication", "value": "%s (from the medical staff)" % strip_links(row["availability"]),
               "source": _availability_pointer(season, data, name, root)}
    why = ("%s is cleared to return from reserve/injured; his return needs a place on the 53 before the next game"
           % name)
    return build_event(season, name, why, at, data, nxt, {kernel_group(row["position"])}, root, medical,
                       {"path": row["sources"]["availability"]} if (row.get("sources") or {}).get("availability")
                       else None)


def recommendation_event(season, name, source, root=ROOT, at=None):
    """The event Stone raises by a recommendation on an active player's place (his own page names it,
    ``source``): brought by him, decided by the general manager, his recommendation asked on the
    period's My Responses page like any other."""
    root = Path(root).resolve()
    at = open_events.master_at(root) if at is None else at
    data = roster(season, root)
    row = next((r for r in data["players"] if r["name"] == name), None)
    if row is None or row["list"] != "active":
        raise Refused("%s is not on Jacksonville's active roster" % name)
    if not str((source or {}).get("path", "")).startswith("career/") or not (root / source["path"]).is_file():
        raise Refused("Stone's recommendation is raised from his own page, which names it")
    nxt = next_game(season, root)
    if nxt is None:
        raise Refused("No Jacksonville game is left to play")
    if open_for(season, name, root) is not None:
        raise Refused("%s's roster question is already open" % name)
    job = current_job.load(root)
    holder = job.get("holder", "stone")
    medical = {"label": "Medical communication", "value": "%s (from the medical staff)" % strip_links(
        row.get("availability") or "None on file"), "source": _availability_pointer(season, data, name, root)}
    why = "Stone raises %s's place on the 53 before the next game" % name
    event = build_event(season, name, why, at, data, nxt, {kernel_group(row["position"])}, root, medical, source,
                        by=holder)
    event["summary"]["author"] = current_job.party_name(job, holder)
    return event


# ------------------------------------------------------------------ the transaction record
def store(season, root=ROOT):
    return paths(season, root).transactions


def record_path(season, tid, root=ROOT):
    return store(season, root) / ("%s.json" % tid)


def load(season, root=ROOT):
    folder = store(season, root)
    return [_json(p) for p in sorted(folder.glob("*.json"))] if folder.is_dir() else []


def get(season, tid, root=ROOT):
    path = record_path(season, tid, root)
    return _json(path) if path.is_file() else None


def write(record, root=ROOT):
    path = record_path(record["season"], record["id"], root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


RECORD_KEYS = ("schema", "id", "season", "event", "date", "at", "decided_by", "criteria", "recommendation", "basis",
               "moves", "source", "status")
OPTIONAL_KEYS = ("applied", "award", "draw")
MOVE_KEYS = ("player", "kind", "from_list", "to_list")
MOVE_OPTIONAL = ("via", "position", "designation", "availability", "contract", "waived_by", "waived_on", "offer",
                 "comparison")


def recommendation_of(event):
    """Stone's answer as the record keeps it: his substance, or "none on file"."""
    response = event.get("response")
    return copy.deepcopy(response["substance"]) if response else "none on file"


def criteria_errors(event, index, by):
    """Why a decision may not apply criteria entry ``index`` of ``event``, or []."""
    process = event.get("process") or []
    if type(index) is not int or not 0 <= index < len(process) or process[index].get("kind") != "criteria":
        return ["the decision names no criteria entry of the event (the criteria come first)"]
    if process[index].get("by") != by:
        return ["the criteria the decision applies are not %s's" % by]
    responses = [n for n, e in enumerate(process) if e.get("kind") == "response"]
    if responses and index > responses[0]:
        return ["the criteria were recorded after Stone's answer; criteria come before the case"]
    return []


def record_errors(record, root=ROOT, event=None, mapping=None):
    """Every rule one transaction record must satisfy, as lines."""
    root = Path(root)
    tid = record.get("id") if isinstance(record, dict) else None
    out = []
    say = lambda text: out.append("Transaction %s: %s" % (tid, text))
    if not isinstance(record, dict) or not set(RECORD_KEYS) <= set(record) or \
            set(record) - set(RECORD_KEYS) - set(OPTIONAL_KEYS):
        return ["Transaction %s: must hold %s" % (tid, ", ".join(RECORD_KEYS))]
    if record["schema"] != SCHEMA:
        say("schema must be %s" % SCHEMA)
    if not isinstance(tid, str) or not EVENT_ID.fullmatch(tid):
        say("the id is lowercase words joined by hyphens")
    if record["status"] not in STATUSES:
        say("status must be one of %s" % ", ".join(STATUSES))
    event = open_events.get(record["season"], record["event"], root) if event is None else event
    if event is None or event.get("kind") != KIND:
        return out + ["Transaction %s: names no injury replacement event %s" % (tid, record["event"])]
    if record["decided_by"] != event["authority"]["decides"]:
        say("is decided by %s, but the event's decision is %s's" % (record["decided_by"], event["authority"]["decides"]))
    out += ["Transaction %s: %s" % (tid, e) for e in criteria_errors(event, record["criteria"], record["decided_by"])]
    if record["recommendation"] != recommendation_of(event):
        say("its recommendation must be Stone's answer as the event keeps it (his substance, or none on file)")
    try:
        at = open_events.parse_at(record["at"])
        if record["date"] != at.date().isoformat():
            say("its date must be the day of its time")
        if at < open_events.parse_at(event["raised"]["at"]):
            say("is decided before its event was raised")
        if not open_events.master_clock(root).allows(at):
            say("is decided at %s, after the master date/time" % record["at"])
    except ValueError as exc:
        say("at: %s" % exc)
    basis = record["basis"]
    if not isinstance(basis, dict) or set(basis) != {"text", "source"} or not str(basis.get("text", "")).strip():
        say("basis must be {text, source}")
    else:
        problem = current_job.record_error(root, mapping or open_events.repository_map(root), basis["source"])
        if problem:
            say("basis source: %s" % problem)
        from .clean_pages import page_errors
        rel = (decisions.event_folder(KIND, record["season"], root) / "README.md").relative_to(root.resolve()).as_posix()
        for problem in page_errors(rel, basis["text"], root=root):
            say("the basis is not in football words (%s)" % problem.split(": ", 1)[-1])
    problem = current_job.record_error(root, mapping or open_events.repository_map(root), record["source"])
    if problem:
        say("source: %s" % problem)
    if not isinstance(record["moves"], list) or not record["moves"]:
        say("needs its moves")
        return out
    for n, move in enumerate(record["moves"], 1):
        if not isinstance(move, dict) or not set(MOVE_KEYS) <= set(move) or \
                set(move) - set(MOVE_KEYS) - set(MOVE_OPTIONAL):
            say("move %d must hold %s" % (n, ", ".join(MOVE_KEYS)))
            continue
        if move["kind"] in ("released", "waived", "traded"):
            say("move %d: %s" % (n, NOT_BUILT))
            continue
        if move["kind"] not in MOVES:
            say("move %d: kind must be one of %s" % (n, ", ".join(MOVES)))
            continue
        if (move["from_list"], move["to_list"]) != MOVES[move["kind"]]:
            say("move %d: a %s move goes from %s to %s" % ((n, move["kind"]) + MOVES[move["kind"]]))
        if move["kind"] in VIA and move.get("via") not in VIA[move["kind"]]:
            say("move %d: a %s move names how he comes (%s)" % (n, move["kind"], ", ".join(VIA[move["kind"]])))
    return out


# ------------------------------------------------------------------ the market draw (method section 4)
def chance(m):
    """The method's chance from the money index (career/2014/League/personnel/method.md section 4)."""
    if m < 0.80:
        return 0.0
    if m <= 1.00:
        return 0.5 * (m - 0.80) / 0.20
    if m <= 1.25:
        return 0.5 + 0.4 * (m - 1.00) / 0.25
    return 0.90


def money_index(jax_apy, jax_gtd, real_apy, real_gtd):
    """m = 0.5 x (Jacksonville's average per year / the real one) + 0.5 x (the guarantees), or the
    average per year alone when the real contract had no guarantee."""
    apy = jax_apy / real_apy
    if not real_gtd:
        return apy
    return 0.5 * apy + 0.5 * jax_gtd / real_gtd


def draw_inputs(offer, comparison, offer_date, signing_date):
    """The draw's inputs: the two contracts and the dates only (the label swap: no name, no club)."""
    return {"jacksonville": {"apy": int(offer["apy"]), "guarantee": int(offer.get("guarantee") or 0)},
            "real": {"apy": int(comparison["apy"]), "guarantee": int(comparison.get("guarantee") or 0)},
            "offer_date": _day(offer_date).isoformat(), "signing_date": _day(signing_date).isoformat()}


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    from .packets import canonical as _canonical
    return _canonical(value)


# ------------------------------------------------------------------ the result page
def result_name(season, event, day, root=ROOT):
    return decisions.result_file(KIND, _day(day), event["subject"], root, season=int(season))


MOVE_WORDS = {"reserve": "placed on %s", "promoted": "promoted from the practice squad to the 53",
              "reinstated": "returned from reserve/injured to the 53", "signed": "signed to the 53",
              "claimed": "claimed on waivers to the 53", "practice_squad": "signed to the practice squad"}


def move_words(move):
    if move["kind"] == "reserve":
        return MOVE_WORDS["reserve"] % ("reserve/injured, designated for return"
                                        if move.get("designation") == "designated" else "reserve/injured")
    words = MOVE_WORDS[move["kind"]]
    if move["kind"] == "claimed" and move.get("waived_by"):
        words = "claimed on waivers from the %s to the 53" % move["waived_by"]
    return words


def _link(page_rel, target_rel, label, anchor=""):
    import os
    path = os.path.relpath(target_rel, os.path.dirname(page_rel)).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, path.replace(" ", "%20"), "#" + anchor if anchor else "")


def answer_line(event, page_rel, job):
    response = event.get("response")
    if response is None:
        return "No recommendation was given before the due time; the general manager decided under his authority."
    substance = response["substance"]
    kind = substance["kind"]
    words = {"recommend": "Recommended %s" % substance.get("option"), "support": "Supported the move",
             "oppose": "Opposed the move", "lapse": "Let it pass at its due time",
             "condition": "Supported it on a condition: %s" % str(substance.get("condition", "")).rstrip(".")}[kind]
    from .event_inserts import slug as heading_slug
    return "%s (%s, on %s)." % (words, long_date(response["date"]),
                                _link(page_rel, response["page"], "My Responses", heading_slug(response["heading"])))


def page_text(record, event, root=ROOT):
    """The Transaction page: the event's one result, built from the applied transaction record (its
    ``applied`` part holds the effective date, the page, each player's contract words and the signing
    records) and the event record."""
    root = Path(root).resolve()
    job = current_job.load(root)
    applied = record.get("applied") or {}
    changes = applied.get("changes") or {}
    signing_pages = applied.get("signings") or {}
    page_rel = applied.get("page") or _rel(root, result_name(record["season"], event, record["date"], root))
    players = [m["player"] for m in record["moves"]]
    moved = "; ".join("%s %s" % (m["player"], move_words(m)) for m in record["moves"])
    title = moved if event["subject"] in players else "%s: %s" % (event["subject"], moved)
    raised = open_events.parse_at(event["raised"]["at"])
    at = open_events.parse_at(applied.get("at") or record["at"])
    meta = {"date": at.date().isoformat(), "id": event["id"], "status": "closed",
            "summary": "%s, on %s's decision." % ("; ".join("%s %s" % (m["player"], move_words(m))
                                                           for m in record["moves"]),
                                                 current_job.party_name(job, record["decided_by"]))}
    lines = ["# Transaction: %s" % title, "",
             "<!-- event-record: %s -->" % json.dumps(meta, sort_keys=True), "",
             "**Event date:** %s" % open_events.at_text(raised), "",
             "**Resolved on:** %s" % open_events.at_text(at), "",
             "**Involving:** %s; %s, who decides; Alex Stone, who recommends; the medical staff" % (
                 ", ".join(dict.fromkeys([event["subject"]] + players)), current_job.party_name(job, record["decided_by"])),
             "", "**What happened:** %s." % event["summary"]["text"].rstrip("."), ""]
    lines += ["| Fact | Detail |", "|---|---|"]
    lines += ["| %s | %s |" % (f["label"], str(f["value"]).replace("|", "/")) for f in event["facts"]
              if f["label"] != "Free agents Jacksonville may pursue"]
    lines += ["", "**Stone's answer:** %s" % answer_line(event, page_rel, job), "",
              "**Final decision:** %s (Document 3 rows %s): %s" % (
                  current_job.party_name(job, record["decided_by"]), ", ".join(event["authority"]["rows"][:-1]) +
                  " and " + event["authority"]["rows"][-1], record["basis"]["text"].rstrip(".") + "."), "",
             "**Outcome:** Executed", "", "**Changes effective:**", "",
             "| Player | Move | Effective | Contract |", "|---|---|---|---|"]
    for m in record["moves"]:
        when = (changes or {}).get(m["player"], {}).get("effective") or record["date"]
        contract = (changes or {}).get(m["player"], {}).get("contract") or "Unchanged"
        lines.append("| %s | %s | %s | %s |" % (m["player"], move_words(m)[0].upper() + move_words(m)[1:],
                                                long_date(when), contract))
    lines += ["", "**Outstanding issue:** None", "", "**Source records:** %s" % " · ".join(
        [_link(page_rel, _rel(root, paths(record["season"], root).roster_page), "Roster"),
         _link(page_rel, _rel(root, paths(record["season"], root).record("depth_chart.md")), "Depth chart")] +
        [_link(page_rel, p, "Signing record: %s" % n) for n, p in (signing_pages or {}).items()] +
        ([_link(page_rel, event["raised"]["source"]["path"], "Medical record")]
         if str(event["raised"]["source"].get("path", "")).startswith("career/") else [])), ""]
    return "\n".join(lines)


def claim_words(award):
    """A waiver claim's market line, from the stored award only: the one club that really claimed him,
    or none (the claims that failed are not on the record, library W6)."""
    end = award.get("at")
    when = long_date(open_events.parse_at(end).date()) if end else "the end of the claim period"
    if not award.get("claimed_by"):
        return "Claimed on waivers: no other club claimed him before the claim period ended %s." % when
    return ("Claimed on waivers: Jacksonville stood ahead of the %s, the club that claimed him, in the waiver order on "
            "%s (%s)." % (award["claimed_by"], when, str(award.get("order") or "").rstrip(".")))


def signing_text(record, move, root):
    """The signing record of a player Jacksonville signs from outside the club (no event line), built
    from the applied transaction record."""
    root = Path(root).resolve()
    job = current_job.load(root)
    applied = record["applied"]
    page_rel = applied["signings"][move["player"]]
    result_rel = applied["page"]
    contract_words = (applied.get("changes") or {}).get(move["player"], {}).get("contract") or "On the contract record"
    at = open_events.parse_at(applied.get("at") or record["at"])
    how = {"former_player": ("A former Jacksonville player, unplaced since he left the club under the league method "
                             "(section 3): no other club's history signs him, so there is no competing contract "
                             "and no market draw."),
           "section_4": "Pursued under the league method (section 4): the draw was made at the date he signed with a "
                        "club, against that contract, and Jacksonville's offer won it.",
           "waiver_claim": None}[move["via"]]
    if move["via"] == "waiver_claim":
        how = claim_words(record.get("award") or {})
    lines = ["# %s: signed %s" % (move["player"], long_date(at.date())), "",
             "**Decision.** %s decided the signing (Document 3 rows 3 and 5); the roster move is the %s." % (
                 current_job.party_name(job, record["decided_by"]), _link(page_rel, result_rel, "transaction")),
             "", "**Market.** %s" % how, "",
             "**Medical.** %s" % (strip_links((move.get("availability") or {}).get("text") or
                                              "None needed for the practice squad") + "."), "",
             "**Terms.** %s." % contract_words.rstrip("."), ""]
    return "\n".join(lines)


# ------------------------------------------------------------------ validation
def built_pages(season, root=ROOT):
    """{path: text} of every page an applied transaction built: its Transaction page and its signing
    records, each rebuilt from the records."""
    root = Path(root).resolve()
    out = {}
    for record in load(season, root):
        if record.get("status") != "applied":
            continue
        event = open_events.get(season, record["event"], root)
        if event is None:
            continue
        out[root / record["applied"]["page"]] = page_text(record, event, root)
        for move in record["moves"]:
            if move["player"] in (record["applied"].get("signings") or {}):
                out[root / record["applied"]["signings"][move["player"]]] = signing_text(record, move, root)
    return out


def validation_errors(root=ROOT):
    """Every transaction record of the active season against its event and its pages (the lead wires
    this into scripts/validate_repository.py): each record's rules; an applied record's event resolved
    with its Transaction page; every page it built present, clean and equal to its build; a lost claim
    with its award and a lost draw with its draw."""
    from .clean_pages import text_errors
    root = Path(root).resolve()
    season = int(open_events.repository_map(root)["active_season"])
    errors = []
    folder = store(season, root)
    for path in sorted(folder.glob("*")) if folder.is_dir() else ():
        rel = _rel(root, path)
        if path.suffix != ".json":
            errors.append("Transactions: %s is not a transaction record" % rel)
            continue
        try:
            record = _json(path)
        except ValueError as exc:
            errors.append("Transactions: %s: %s" % (rel, exc))
            continue
        if path.name != "%s.json" % record.get("id"):
            errors.append("Transactions: %s is not named by its id" % rel)
        event = open_events.get(season, record.get("event"), root) if isinstance(record, dict) else None
        found = record_errors(record, root, event)
        errors += found
        if found or event is None:
            continue
        status = record["status"]
        if status == "applied":
            res = event.get("resolution") or {}
            if res.get("result_page") != record["applied"]["page"] or res.get("outcome") != "executed":
                errors.append("Transaction %s: its event is not resolved with its Transaction page" % record["id"])
        elif status == "claim_lost" and not record.get("award"):
            errors.append("Transaction %s: a lost claim keeps its award" % record["id"])
        elif status == "pursuit_lost" and not record.get("draw"):
            errors.append("Transaction %s: a lost pursuit keeps its draw" % record["id"])
    try:
        pages = built_pages(season, root)
    except (OSError, ValueError, KeyError) as exc:
        return errors + ["Transactions: the pages cannot be built: %s" % exc]
    for path, text in pages.items():
        rel = _rel(root, path)
        if not path.is_file():
            errors.append("Transactions: %s is missing" % rel)
        elif path.read_text(encoding="utf-8") != text:
            errors.append("Transactions: %s differs from its records" % rel)
        errors += ["Transactions: %s" % e for e in text_errors(rel, text, root)]
    return errors
