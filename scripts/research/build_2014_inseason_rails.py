#!/usr/bin/env python3
"""Build the 2014 in-season roster rails for the 31 background clubs.

Research tool only; the runtime never downloads anything. Fetch the inputs
into SOURCE_DIR first (a transient workspace, never committed):

  research/inseason_moves.csv     the merged two-pass research list (NFL.com
                                  wire, ESPN team logs, second-pass web sources)
  research/sources_manifest.json  its page hashes
  wire/nfl_rows_*.json            NFL.com transaction wire rows, with
  wire/nfl_manifest_*.json        their cursor-checked page manifests
                                  (https://www.nfl.com/transactions/league/{category}/2014/{month})
  espn/espn_rows.json             ESPN team transaction logs, 32 clubs, and
  espn/espn_manifest.json         their page hashes
                                  (https://www.espn.com/nfl/team/transactions/_/name/{team}/season/2014)
  nflverse/players.csv            identity (gsis id, birth date, position)
  nflverse/roster_weekly_2014.csv Week 1 club membership only (status ignored)

Usage:
  python scripts/research/build_2014_inseason_rails.py SOURCE_DIR --through YYYY-MM-DD
  python scripts/research/build_2014_inseason_rails.py SOURCE_DIR --through YYYY-MM-DD --check

Every input's sha256 is recorded in the manifest; `--check` rebuilds and
compares without writing, and fails when an input hash differs from its pin.

Gate and append-only rules (library/2014_inseason_rails.md):
- `--through` may not be later than Document 5's master date, and no row
  with a gate date after it is written.
- A committed row is never edited or renumbered. New rows are numbered from
  the current maximum upward in (gate date, player id) order, and take the
  first open week as their effective week (engineering review B5). The base
  is written once, by the first build.
- Real injuries, suspensions and availability, and every Jacksonville or
  real-Jaguars row, are committed without player identity or entry text
  (rules review C6). A retirement is the exception: it applies league-wide,
  Jacksonville included, whoever filed it (rails rule 5), so its row keeps
  its identity.
- Every committed row carries at least one source-page hash; the builder
  stops on the position guard (`position_problems`) and on any error of the
  replay the weekly build runs (`replay_states`).
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime import rails, player_bios  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.usage import group  # noqa: E402

SEASON = 2014
OUT = rails.data_dir(SEASON, ROOT)
LIBRARY = "library/data/2014_week1_depth_charts.json"
NICK = {"Cardinals": "ARI", "Falcons": "ATL", "Ravens": "BAL", "Bills": "BUF", "Panthers": "CAR",
        "Bears": "CHI", "Bengals": "CIN", "Browns": "CLE", "Cowboys": "DAL", "Broncos": "DEN",
        "Lions": "DET", "Packers": "GB", "Texans": "HOU", "Colts": "IND", "Jaguars": "JAX",
        "Chiefs": "KC", "Dolphins": "MIA", "Vikings": "MIN", "Patriots": "NE", "Saints": "NO",
        "Giants": "NYG", "Jets": "NYJ", "Raiders": "OAK", "Eagles": "PHI", "Steelers": "PIT",
        "Chargers": "SD", "Seahawks": "SEA", "Niners": "SF", "49ers": "SF", "Rams": "STL",
        "Buccaneers": "TB", "Titans": "TEN", "Redskins": "WAS"}
WEEKLY_CODE = {"ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "SL": "STL"}
ESPN_SLUG = {"ari": "ARI", "atl": "ATL", "bal": "BAL", "buf": "BUF", "car": "CAR", "chi": "CHI",
             "cin": "CIN", "cle": "CLE", "dal": "DAL", "den": "DEN", "det": "DET", "gb": "GB",
             "hou": "HOU", "ind": "IND", "jax": "JAX", "kc": "KC", "lv": "OAK", "lac": "SD",
             "lar": "STL", "mia": "MIA", "min": "MIN", "ne": "NE", "no": "NO", "nyg": "NYG",
             "nyj": "NYJ", "phi": "PHI", "pit": "PIT", "sf": "SF", "sea": "SEA", "tb": "TB",
             "ten": "TEN", "wsh": "WAS"}

# ---- reviewed corrections (each cites the review item it applies) ---------------

# Name variants of one player across the wire and ESPN (rules B4, engineering B4).
ALIASES = {"cameronhenderson": "camhenderson", "daxtonswanson": "daxswanson",
           "charleshughlett": "charleyhughlett", "davepaulson": "davidpaulson",
           "jonathanabraham": "johnabraham", "trevorgraham": "tjgraham",
           "daveddrewbutler": "drewbutler", "cbkdannygorrer": "dannygorrer", "joshuabellamy": "joshbellamy",
           "dionlewi": "dionlewis"}
# Identity fixes by research id (rules B4): the research field held two
# candidates, or a namesake of another position group that the position
# guard (`position_problems`) stops on. A fix for a row gated after the
# committed window names no player here (rules C5); it takes effect only
# when the window reaches the row.
IDENTITY = {"R14-0008": "00-0030113", "R14-0579": "JON157260"}
# Rows logged twice under two spellings of one name: merged into the first id (rules B4).
MERGE = {"R14-0184": "R14-0183", "R14-0350": "R14-0349"}
# Outcome and kind corrections by research id.
OUTCOME = {
    "R14-0340": ("suspension", "NOT_APPLIED_SUSPENSION", "an activation after his suspension (rules C1)"),
    "R14-0105": (None, "NOT_APPLIED_REAL_JAGUARS", "a real Jaguars move (rules C1)"),
    "R14-0520": (None, "APPLY", "an inferred promotion, on the same evidence rule as the other inferred "
                               "promotions (rules C10)"),
    "R14-0454": ("released", "APPLY", "released from the injured reserve list: an ordinary release, a no-op "
                                       "unless he is on the club (rules C1)"),
    # Applied when the window reaches them: the wire and ESPN disagree on
    # the kind of one move, so both rows wait for a resolution (rules C10).
    "R14-0616": (None, "REVIEW_SOURCE_CONFLICT", "the wire and ESPN disagree on the kind of move (rules C10)"),
    "R14-0617": (None, "REVIEW_SOURCE_CONFLICT", "the wire and ESPN disagree on the kind of move (rules C10)"),
}
# Harrison retired as a free agent (rules C9): his retirement frees no place.
CLUB = {"R14-0107": "FA"}
# Second-pass citations whose page title names a real injury are recorded
# without the URL (rules C6); the URL stays in the pinned research list.
OTHER_SOURCE = {"R14-0107": "Steelers.com news release of September 23, 2014, stating the September 5 announcement "
                            "(URL withheld: its title names a real injury, rules review C6)"}
# Missing from the research list (rules B4): the wire's Baltimore waiver.
ADDED = [{"key": "wire:BAL:deontethompson:2014-09-24", "date": "2014-09-24", "club": "BAL", "name": "Deonte Thompson",
          "match": ("09/24", "Ravens", "Waived, No Recall"), "kind": "waived",
          "reason": "missing from the research list; the wire's Baltimore waiver (rules B4)"}]
ADMIN = {("PIT", "jeromebettis"), ("PIT", "fernandobryant"), ("PIT", "jeffhartings"), ("PIT", "johnjackson"),
         ("PIT", "rashadbutler")}
# Suspensions in force at Week 1 announced before the August 30 reduction,
# second pass (rules C2): two outside sources each.
EARLY_SUSPENSIONS = [
    {"name": "Daryl Washington", "club": "ARI", "gsis": None, "announced": "2014-05-30",
     "sources": ["https://profootballtalk.nbcsports.com/2014/05/30/report-daryl-washington-will-miss-entire-2014-season",
                 "http://arizonasports.com/story/8262/arizona-cardinals-lb-daryl-washington-suspended-for-entire-2014-season/"]},
    {"name": "Josh Gordon", "club": "CLE", "gsis": None, "announced": "2014-08-27",
     "sources": ["https://www.washingtonpost.com/news/early-lead/wp/2014/08/27/browns-wide-receiver-josh-gordon-loses-appeal-suspended-one-year-by-nfl/",
                 "https://www.si.com/nfl/2014/08/27/josh-gordon-suspension-upheld-cleveland-browns"]},
]
OUTSIDE_SUSPENSION_SOURCE = {
    "Aldon Smith": "https://www.nfl.com/news/niners-aldon-smith-suspended-for-nine-games-0ap3000000385995"}

KIND_MAP = {
    "ps_signing": "ps_signing", "waived": "waived", "fa_signing": "fa_signing", "ps_release": "ps_release",
    "injured_reserve": "injury_reserve", "ir_designated_return": "injury_reserve", "ps_injured": "injury_reserve",
    "ps_promotion": "ps_promotion", "released": "released", "suspension_lifted": "suspension",
    "reserve_suspended": "suspension", "exempt_commissioner_permission": "suspension",
    "activated_from_suspension": "suspension", "waived_injury_settlement": "injury_release",
    "injury_settlement": "injury_release", "waived_injured": "injury_release", "re_signing": "re_signing",
    "ps_poach": "ps_poach", "waiver_claim": "waiver_claim", "extension": "contract",
    "released_unspecified": "released_unspecified", "reserve_nfi": "availability", "retirement": "retirement",
    "left_team_exemption": "availability", "activated": "injury_activation",
}
INERT_OUTCOME = {"injury_reserve": "NOT_APPLIED_INJURY", "injury_release": "NOT_APPLIED_INJURY",
                 "injury_activation": "NOT_APPLIED_INJURY", "suspension": "NOT_APPLIED_SUSPENSION",
                 "availability": "NOT_APPLIED_AVAILABILITY", "contract": "NO_ROSTER_EFFECT",
                 "administrative": "NO_ROSTER_EFFECT"}
INJURY_TEXT = re.compile(r"injury settlement|waived/injured|waived, injur|released/injured", re.I)
IR_RELEASE_TEXT = re.compile(r"from the injured reserve", re.I)


def norm(name):
    return re.sub(r"[^a-z]", "", re.sub(r"\s*\(.*?\)", "", str(name)).lower())


def _active_2014(row):
    try:
        first, last = int(row["rookie_season"] or 0), int(row["last_season"] or 0)
    except ValueError:
        return False
    return (not first or first <= SEASON + 1) and (not last or last >= SEASON)


def similar(a, b):
    """Two spellings of one name in one club's log (rules B4): equal after
    the alias table, or the same surname with first names sharing three
    letters, or within two edits of each other."""
    a, b = anorm(re.sub(r"\b(?:jr|sr|ii|iii|iv)\b\.?", "", a, flags=re.I)), anorm(re.sub(r"\b(?:jr|sr|ii|iii|iv)\b\.?", "", b, flags=re.I))
    if a == b:
        return True
    if a[:1] != b[:1]:
        return False
    if _edits(a, b) <= 2:
        return True
    return False


def similar_names(x, y):
    """`similar`, or the same surname with one first name a prefix of the
    other (Will and William, Dan and Danny)."""
    if similar(x, y):
        return True
    px, py = re.sub(r"\b(?:Jr|Sr|II|III|IV)\b\.?", "", x).split(), re.sub(r"\b(?:Jr|Sr|II|III|IV)\b\.?", "", y).split()
    if len(px) < 2 or len(py) < 2 or norm(px[-1]) != norm(py[-1]):
        return False
    a, b = norm(px[0]), norm(py[0])
    return a.startswith(b) or b.startswith(a)


def _edits(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def anorm(name):
    n = norm(name)
    return ALIASES.get(n, n)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def d(value):
    return date.fromisoformat(value)


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


# ---- inputs ----------------------------------------------------------------------

class Sources:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.files = sorted(p for p in self.folder.rglob("*") if p.is_file())
        self.hashes = {str(p.relative_to(self.folder)): sha256(p) for p in self.files}
        self.research = load_csv(self.folder / "research/inseason_moves.csv")
        self.wire = []
        self.wire_pages = {}
        seen = set()
        for path in sorted((self.folder / "wire").glob("nfl_rows_*.json")):
            for row in json.loads(path.read_text()):
                key = (row["category"], row["date"], row["from"], row["to"], row["name"], row["transaction"])
                if key not in seen:  # the waiver pages were captured in two runs
                    seen.add(key)
                    self.wire.append(row)
        for path in sorted((self.folder / "wire").glob("nfl_manifest_*.json")):
            for page in json.loads(path.read_text()):
                self.wire_pages[page["url"]] = page["sha256"]
        research_manifest = json.loads((self.folder / "research/sources_manifest.json").read_text())
        for page in research_manifest.get("nfl_wire_pages", ()):
            self.wire_pages.setdefault(page["url"], page["sha256"])
        self.espn = json.loads((self.folder / "espn/espn_rows.json").read_text())
        self.espn_pages = {ESPN_SLUG[p["url"].split("/name/")[1].split("/")[0]]: p["sha256"]
                           for p in json.loads((self.folder / "espn/espn_manifest.json").read_text())}
        self.players = load_csv(self.folder / "nflverse/players.csv")
        self.weekly = load_csv(self.folder / "nflverse/roster_weekly_2014.csv")
        self.injuries = load_csv(self.folder / "nflverse/injuries_2014.csv")
        self.depth = load_csv(self.folder / "nflverse/depth_charts_2014.csv")
        for row in self.wire:
            mm, dd = row["date"].split("/")
            row["iso"] = "2014-%s-%s" % (mm, dd)


# ---- identity ----------------------------------------------------------------------

class Identity:
    """gsis -> player id, from every registry the repository already keeps
    (engineering review B4): the Week 1 library, the birth-date registry, the
    2014 receipts and the league database; new ids never collide."""

    def __init__(self, library, sources):
        self.library = {}
        for club in library["clubs"].values():
            for p in club["players"]:
                self.library[p["gsis_id"]] = p
        self.registry = player_bios.load(ROOT)
        self.by_gsis = collections.defaultdict(list)
        for name, row in self.registry.items():
            self.by_gsis[row["gsis_id"]].append(name)
        league = json.loads((SeasonPaths(SEASON, ROOT).record("league/personnel/league_players.json"))
                            .read_text(encoding="utf-8"))
        self.league = {p["player_id"]: p for p in league["players"]}
        self.receipt_ids = set()
        for path in sorted(SeasonPaths(SEASON, ROOT).receipts.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for team in data.get("team_stats", {}).values():
                self.receipt_ids.update(team.get("players", {}))
        self.names = collections.defaultdict(set)  # norm name -> gsis ids
        for gsis, p in self.library.items():
            self.names[norm(p["player_id"])].add(gsis)
        for name, row in self.registry.items():
            self.names[norm(name)].add(row["gsis_id"])
        for gsis, p in self.league.items():
            self.names[norm(p["name"])].add(gsis)
        self.players = {}
        self.by_name = collections.defaultdict(list)
        for r in sources.players:
            self.players[r["gsis_id"]] = r
            try:
                first, last = int(r["rookie_season"] or 0), int(r["last_season"] or 0)
            except ValueError:
                first = last = 0
            # A rookie season of 2015 does not rule out a 2014 camp body; a
            # later one does (a 2024 entrant is never a 2014 player).
            if first and first > SEASON + 1:
                continue
            if last and last < SEASON - 1:
                continue
            self.by_name[anorm(r["display_name"])].append(r)
            if r.get("football_name") and r.get("last_name"):
                self.by_name[anorm(r["football_name"] + " " + r["last_name"])].append(r)
        self.weekly_pos = {}
        self.weekly_team = collections.defaultdict(set)
        for r in sorted(sources.weekly, key=lambda r: int(r["week"])):
            self.weekly_pos.setdefault(r["gsis_id"], r["position"])
            self.weekly_team[r["gsis_id"]].add(WEEKLY_CODE.get(r["team"], r["team"]))
        self.assigned = {}
        self.research_ids = {}
        for r in sources.research:
            g = r["gsis_id"]
            if g and "|" not in g:
                for club in (r["club"], r["counterparty_club"]):
                    if club:
                        self.research_ids.setdefault((anorm(re.sub(r"\s*\(NFL wire: .*?\)", "", r["player"])), club), g)

    def resolve(self, name, gsis_field, clubs):
        """(uid or None, basis): the research gsis when single; else one
        players.csv identity by name (preferring players active in 2014),
        else by name and club (2014 weekly roster, then the research list)."""
        if gsis_field and "|" not in gsis_field:
            return gsis_field, "research"
        cands = {r["gsis_id"]: r for r in self.by_name.get(anorm(name), [])}
        if len(cands) == 1:
            return next(iter(cands)), "players_csv_name"
        active = {g: r for g, r in cands.items() if _active_2014(r)}
        if len(active) == 1:
            return next(iter(active)), "players_csv_name_active_2014"
        seen = [g for g in cands if self.weekly_team.get(g, set()) & set(clubs)]
        if len(seen) == 1:
            return seen[0], "players_csv_name_and_club"
        for club in clubs:
            g = self.research_ids.get((anorm(name), club))
            if g:
                return g, "research_name_and_club"
        return None, "unresolved" if not cands else "ambiguous"

    def player_id(self, uid, name, club):
        if uid in self.assigned:
            return self.assigned[uid]
        pid = None
        if uid in self.library:
            pid = self.library[uid]["player_id"]
        elif self.by_gsis.get(uid):
            names = sorted(self.by_gsis[uid], key=lambda n: (n not in self.receipt_ids, "(" not in n, n))
            pid = names[0]
        else:
            base = (self.league[uid]["name"] if uid in self.league else
                    (self.players.get(uid) or {}).get("display_name") or re.sub(r"\s*\(.*?\)", "", name).strip())
            clash = self.names.get(norm(base), set()) - {uid}
            clash |= {g for g, p in self.assigned.items() if norm(p) == norm(base) and g != uid}
            pid = base if not clash else "%s (%s)" % (base, club)
        self.assigned[uid] = pid
        self.names[norm(pid)].add(uid)
        return pid

    def position(self, uid, fallback=""):
        """The library position; else the 2014 weekly roster's; else the
        position the 2014 source states (`fallback`: the research list or
        ESPN's token); only then nflverse players.csv, which can carry a
        later-career position."""
        if uid in self.library:
            return self.library[uid]["position"]
        weekly, later = self.weekly_pos.get(uid), (self.players.get(uid) or {}).get("position")
        if weekly and group(weekly):
            return weekly
        if fallback and group(fallback):
            # The 2014 source wins when it names another group or a more
            # specific label; a generic label of the same group ("OL", "DB")
            # keeps players.csv's specific one.
            if not (later and group(later)) or group(later) != group(fallback) or fallback != group(fallback):
                return fallback
        for pos in (later,):
            if pos and group(pos):
                return pos
        pg = (self.players.get(uid) or {}).get("position_group")
        return pg if group(pg) else None

    def birth_date(self, uid):
        if uid in self.library and self.library[uid].get("birth_date"):
            return self.library[uid]["birth_date"]
        return (self.players.get(uid) or {}).get("birth_date") or None


# ---- dates and classification --------------------------------------------------

def gate(row):
    """(real date, gate date, date basis): the later of the two source dates;
    an ESPN-only row one day after its ESPN date (rules C11); a second-pass
    row its own date."""
    wire, espn = row["nfl_wire_date"], row["espn_date"]
    if wire and espn:
        real, later = min(wire, espn), max(wire, espn)
        return real, later, "two_sources_same_day" if wire == espn else "two_sources_later_date"
    if wire:
        return wire, wire, "wire_only"
    if espn:
        return espn, (d(espn) + timedelta(days=1)).isoformat(), "espn_only_plus_one"
    return row["move_date"], row["move_date"], "second_pass_single"


def classify(row, kind, pre_reserve=False):
    """(kind, outcome, reason) from both sources' text (rules C1). An
    activation of a player on a real reserve list before Week 1 is a return
    (decision D6): he was on no Week 1 chart, so his activation adds him,
    as the Week 1 library's starting-availability convention does; an
    in-season injury activation stays inert."""
    text = " ".join(row[k] for k in ("nfl_wire_entry", "espn_entry", "other_source"))
    if kind == "injury_activation" and pre_reserve:
        return "activation_return", "APPLY", ("an activation from a reserve list he was on before Week 1: a return "
                                              "to his club (decision D6)")
    if kind in ("ps_release", "waived", "released", "released_unspecified") and INJURY_TEXT.search(text):
        return "injury_release", "NOT_APPLIED_INJURY", "an injury-driven release (rules C1)"
    if kind in INERT_OUTCOME:
        return kind, INERT_OUTCOME[kind], {"NOT_APPLIED_INJURY": "a real injury placement (rails rule 2)",
                                           "NOT_APPLIED_SUSPENSION": "a suspension or its lifting (rails rule 2)",
                                           "NOT_APPLIED_AVAILABILITY": "an availability list (rails rule 2)",
                                           "NO_ROSTER_EFFECT": "no roster movement"}[INERT_OUTCOME[kind]]
    return kind, "APPLY", "a real player movement of a background club (rails rule 1)"


def page_hashes(src, row):
    """The wire and ESPN page hashes behind a row; a row found only by the
    second-pass web search carries the pinned research list's hash, so every
    committed row has provenance (rules review C6)."""
    out = []
    if row["nfl_wire_entry"]:
        name = norm(re.sub(r"\s*\(NFL wire: (.*?)\)", "", row["player"]))
        wire_name = re.search(r"\(NFL wire: (.*?)\)", row["player"])
        names = {name, norm(wire_name.group(1))} if wire_name else {name}
        for w in src.wire:
            if w["iso"] == row["nfl_wire_date"] and norm(w["name"]) in names and w["page_url"] in src.wire_pages:
                out.append(src.wire_pages[w["page_url"]])
    if row["espn_entry"] and row["club"] in src.espn_pages:
        out.append(src.espn_pages[row["club"]])
    return sorted(set(out)) or [src.hashes["research/inseason_moves.csv"]]


# ---- rows ----------------------------------------------------------------------------

def pre_week1_reserve(src, library):
    """{(name, club)}: real reserve-list placements (injured, physically
    unable to perform, non-football, retired; never a suspension, whose
    players the base restores) dated on or before the club's base date, from
    the wire's reserve-list pages: the players the Week 1 library left off
    every chart for a real reserve list."""
    dates = base_dates(library)
    out = set()
    for w in src.wire:
        code = NICK.get(w["from"]) or NICK.get(w["to"])
        if w["category"] != "reserve-list" or "Suspended" in w["transaction"] or code not in dates:
            continue
        if w["iso"] <= dates[code]["active"]:
            out.add((anorm(w["name"]), code))
    return out


ADDITION_KINDS = {k for k, (action, _) in rails.KINDS.items() if action == "add"}


def research_rows(src, ident, control, pre_reserve):
    rows, problems = [], []
    by_id = {r["move_id"]: dict(r) for r in src.research}
    for dup, keep in MERGE.items():
        a, b = by_id[keep], by_id.pop(dup)
        for k in ("nfl_wire_date", "nfl_wire_entry", "nfl_wire_url", "espn_date", "espn_entry", "espn_url"):
            if not a[k] and b[k]:
                a[k] = b[k]
        a["verification"] = "two_sources" if a["nfl_wire_entry"] and a["espn_entry"] else a["verification"]
    for rid, r in sorted(by_id.items()):
        raw = r["kind"].split(" ")[0]
        inferred = "inferred" in r["kind"]
        club = CLUB.get(rid, r["club"])
        player = re.sub(r"\s*\(NFL wire: .*?\)", "", r["player"]).strip()
        kind = KIND_MAP[raw]
        admin = (club, norm(player)) in ADMIN
        if admin:
            kind = "administrative"
        kind, outcome, reason = classify(r, kind, (anorm(player), club) in pre_reserve)
        if rid in OUTCOME:
            new_kind, outcome, reason = OUTCOME[rid]
            kind = new_kind or kind
        if r["rails_outcome"] in ("EXCLUDED_SOURCE_ERROR", "EXCLUDED_SOURCE_CONFLICT", "REVIEW_SOURCE_CONFLICT") \
                and rid not in OUTCOME:
            outcome, reason = r["rails_outcome"], r["outcome_reason"]
        retirement = kind == "retirement" and outcome == "APPLY"
        if r["rails_outcome"] == "REVIEW_UNPLACED" and outcome == "APPLY" and not retirement:
            outcome, reason = "REVIEW_UNPLACED", "an unplaced former Jaguar; the rule for his later moves is the user's (rules C4)"
        real, gate_date, basis = gate(r)
        if rid == "R14-0107":
            basis = "espn_only_plus_one"  # the Steelers release confirms the fact, not the day (rules C9)
            real, gate_date = r["espn_date"], (d(r["espn_date"]) + timedelta(days=1)).isoformat()
        clubs = [c for c in (club, r["counterparty_club"]) if c and c != "FA"]
        if admin:
            # A wire entry for a long-retired player (no roster effect): no
            # identity is resolved, so no namesake can be frozen into a row.
            uid, basis_id = None, "administrative"
        elif rid in IDENTITY:
            uid, basis_id = IDENTITY[rid], "review_fix"
        else:
            uid, basis_id = ident.resolve(player, r["gsis_id"], clubs)
        # Precedence (rules C1): a retirement first (the player's own choice,
        # league-wide, Jacksonville included: rails rule 5); then real
        # Jaguars, then Jacksonville control.
        if retirement:
            reason = "a real retirement: the player's own choice, applied league-wide, Jacksonville included (rails rule 5)"
        elif club == "JAX" or r["counterparty_club"] == "JAX":
            outcome, reason = "NOT_APPLIED_REAL_JAGUARS", "a real Jaguars move the branch never made (rails rule 4)"
        elif uid and control.controlled(uid, gate_date):
            outcome, reason = "NOT_APPLIED_JAX_CONTROL", "Jacksonville-controlled on its date (rails rule 4)"
        elif r["rails_outcome"] == "NOT_APPLIED_JAX_CONTROL":
            # Research matched him by name; control is by gsis and date.
            problems.append("%s: research said Jacksonville control, gsis %s is not controlled on %s"
                            % (rid, uid, gate_date))
        if outcome == "APPLY" and kind in ("fa_signing", "re_signing", "ps_promotion", "ps_poach", "waiver_claim",
                                           "ps_signing", "waived", "released", "ps_release", "activation_return",
                                           "released_unspecified", "retirement") and not uid:
            outcome, reason = "REVIEW_IDENTITY", "no resolvable player identity (engineering B4)"
        row = {"research_ref": rid, "real_date": real, "gate_date": gate_date, "date_basis": basis,
               "club": club, "kind": kind,
               "kind_basis": "inferred from an earlier practice-squad signing with the club" if inferred else "source",
               "counterparty": r["counterparty_club"] or None, "player": player, "uid": uid,
               "identity_basis": basis_id, "outcome": outcome, "reason": reason,
               "verification": "second_pass" if r["verification"].startswith("second_pass") else
               ("two_sources" if r["verification"].startswith("two_sources") else r["verification"]),
               "sources": {k: v for k, v in (
                   ("nfl_wire", {"date": r["nfl_wire_date"], "entry": r["nfl_wire_entry"], "page": r["nfl_wire_url"]}
                    if r["nfl_wire_entry"] else None),
                   ("espn", {"date": r["espn_date"], "entry": r["espn_entry"], "page": r["espn_url"]}
                    if r["espn_entry"] else None),
                   ("other", OTHER_SOURCE.get(rid, r["other_source"]) or None)) if v},
               "source_pages": page_hashes(src, r),
               # Working fields, never committed: the 2014 position the
               # sources state, and how the research list matched the name.
               "src_pos": source_position(r), "gsis_match": r["gsis_match"]}
        rows.append(row)
    for add in ADDED:
        mmdd, nick, tx = add["match"]
        hits = [w for w in src.wire if w["date"] == mmdd and w["from"] == nick and w["transaction"] == tx
                and norm(w["name"]) == norm(add["name"])]
        if len(hits) != 1:
            raise SystemExit("added row %s not found once on the wire" % add["key"])
        w = hits[0]
        uid, basis_id = ident.resolve(add["name"], "", [add["club"]])
        rows.append({"research_ref": add["key"], "real_date": add["date"], "gate_date": add["date"],
                     "date_basis": "wire_only", "club": add["club"], "kind": add["kind"], "kind_basis": "source",
                     "counterparty": None, "player": add["name"], "uid": uid, "identity_basis": basis_id,
                     "outcome": "APPLY", "reason": add["reason"], "verification": "nfl_wire_only",
                     "sources": {"nfl_wire": {"date": add["date"], "entry": "%s (%s -> %s)" % (tx, w["from"], w["to"]),
                                              "page": w["page_url"]}},
                     "source_pages": [src.wire_pages[w["page_url"]]] if w["page_url"] in src.wire_pages
                     else [src.hashes["research/inseason_moves.csv"]],
                     "src_pos": "", "gsis_match": "added"})
    return rows, problems


def source_position(r):
    """The 2014 position a source states for the row's player: the research
    list's, else ESPN's token in front of his name."""
    if r["pos"] and group(r["pos"].split("/")[0].split("-")[0]):
        return r["pos"].split("/")[0].split("-")[0]
    name = re.sub(r"\s*\(NFL wire: .*?\)", "", r["player"]).strip()
    m = re.search(r"\b([A-Z]{1,4})\s+" + re.escape(name), r["espn_entry"] or "")
    return m.group(1) if m and group(m.group(1)) else ""


def mark_after_real_jaguars(rows):
    """Mark the row after a real Jaguars acquisition of the same player
    (`after_real_jaguars`): in reality he left his previous squad only
    through that move, which the branch never made, so a later real
    practice-squad signing implies no release by his branch club (rails
    rule 4). Rows are in gate-date order; the Jaguars row itself stays
    stripped."""
    last = {}
    for r in rows:
        uid = r["uid"]
        if not uid:
            continue
        prev = last.get(uid)
        if prev is not None and prev["outcome"] == "NOT_APPLIED_REAL_JAGUARS" and prev["club"] == "JAX" \
                and prev["kind"] in ADDITION_KINDS and r["outcome"] not in rails.STRIPPED_OUTCOMES:
            r["after_real_jaguars"] = True
        last[uid] = r
    return rows


def finish(row, ident):
    """Committed form of one row: identity fields, or the stripped form."""
    if row["outcome"] in rails.STRIPPED_OUTCOMES:
        return {k: row[k] for k in rails.STRIPPED_FIELDS}
    out = dict(row)
    uid = out["uid"]
    if uid:
        out["player_id"] = ident.player_id(uid, out["player"], out["club"])
        out["gsis_id"] = uid if re.match(r"^\d{2}-\d{7}$", uid) else None
        out["position"] = ident.position(uid, row.get("src_pos", ""))
        out["kernel_group"] = group(out["position"]) if out["position"] else None
        out["birth_date"] = ident.birth_date(uid)
    order = ("id", "effective_from_week", "gate_date", "real_date", "date_basis", "club", "kind", "kind_basis",
             "counterparty", "player", "player_id", "uid", "gsis_id", "position", "kernel_group", "birth_date",
             "identity_basis", "outcome", "reason", "verification", "sources", "source_pages", "research_ref",
             "after_real_jaguars")
    return {k: out[k] for k in order if k in out}


# ---- base ------------------------------------------------------------------------------

def schedule_week1():
    from runtime.week_inputs import schedule
    return schedule(1, SEASON)


def base_dates(library):
    """Per club: the day before its Week 1 game (active layer) and September
    1, the practice-squad formation date (engineering review B3)."""
    games = schedule_week1()
    out = {}
    for name, club in library["clubs"].items():
        game = next(g for g in games if name in (g["away"], g["home"]))
        out[club["code"]] = {"active": (d(game["date"]) - timedelta(days=1)).isoformat(),
                             "practice_squad": "2014-09-01"}
    return out


def exclusions(library, control, ident):
    """uid -> reason for every player the real-53 fill may not add
    (engineering review B3): Jacksonville control at any status, players the
    Week 1 build removed or left unplaced, departures, draft swaps and branch
    trades (any player the library carries at another club)."""
    out = {}
    for uid, name in control.names.items():
        out[uid] = "Jacksonville-controlled"
    named = {}
    for club, names in library["removed_by_club"].items():
        for n in names:
            named[norm(n)] = "removed from %s by the Week 1 build (Jacksonville control or a branch disposition)" % club
    for entry in library["unplaced_branch_players"] + library["branch_departures"]:
        n = entry.split(" (")[0]
        named[norm(n)] = "unplaced in the branch: " + entry.split(": ", 1)[-1][:120]
    for entry in library["draft_swaps_without_week1_chart"]:
        named[norm(entry.split(":")[0])] = "draft pairing without a branch club"
    return out, named


BRANCH_FORMER = re.compile(r"left Jacksonville control|not tendered|claimed on waivers August 31, 2013|"
                           r"2013 practice squad, not offered|retired")


def unplaced_uids(library, ident, control, w1):
    """gsis ids of the branch's unplaced former Jaguars: players who left
    Jacksonville control without a same-kind, same-window real move (method
    section 3), matched by name to the Week 1 membership or the identity
    registry. Real-Jaguars-only players (on the real Jaguars, never on the
    branch's) are free agents: the real Jaguars' moves never happen and other
    clubs' later moves apply, as the Week 1 library let them stand (rules
    review C4). Jeremy Cain followed his real move."""
    out = {}
    entries = [e for e in library["unplaced_branch_players"] if BRANCH_FORMER.search(e)]
    entries += library["branch_departures"]
    for entry in entries:
        name = entry.split(" (")[0]
        if name == "Jeremy Cain" or ("Signed by" in entry and "under the rails" in entry):
            continue
        cands = set()
        for club, members in w1.items():
            for g, row in members.items():
                if norm(row["full_name"]) == norm(name):
                    cands.add(g)
        if not cands and name in ident.registry:
            cands = {ident.registry[name]["gsis_id"]}
        if not cands:
            uid, _ = ident.resolve(name, "", [])
            cands = {uid} if uid else set()
        if len(cands) == 1:
            out[cands.pop()] = name
        elif cands:
            raise SystemExit("unplaced former Jaguar %s: %d identities" % (name, len(cands)))
    for uid, name in list(out.items()):
        if control.controlled(uid, date(SEASON, 9, 2)):
            out.pop(uid)  # re-signed by Jacksonville (Alan Ball)
    return out


def week1_membership(src):
    w1 = collections.defaultdict(dict)
    for r in src.weekly:
        if r["week"] == "1" and r["game_type"] == "REG":
            w1[WEEKLY_CODE.get(r["team"], r["team"])][r["gsis_id"]] = r
    return w1


def week1_availability(src):
    """The Week 1 library's adopted availability convention, for fill
    players: the Week 1 pre-game report (Out or Doubtful is unavailable) and,
    for those players only, the first later week reported Questionable or
    Probable or charted (scripts/research/build_2014_week1_depth_charts.py,
    pre_existing_return)."""
    from scripts.research.build_2014_week1_depth_charts import UNAVAILABLE_REPORT, pre_existing_return
    week1 = {(r["team"], r["gsis_id"]): r["report_status"] for r in src.injuries
             if r["week"] == "1" and r["game_type"] == "REG"}
    later = collections.defaultdict(dict)
    for r in src.injuries:
        if r["game_type"] == "REG" and r["week"] != "1" and r["report_status"]:
            later[(r["team"], r["gsis_id"])][int(r["week"])] = r["report_status"]
    charts = {(r["club_code"], r["gsis_id"], int(r["week"])) for r in src.depth
              if r["game_type"] == "REG" and r["week"] not in ("", "1")}

    def status(code, gsis):
        report = week1.get((code, gsis)) or None
        if report not in UNAVAILABLE_REPORT:
            return True, None, report
        back = pre_existing_return(later.get((code, gsis), {}), lambda week: (code, gsis, week) in charts)
        return False, back, report
    return status


def _first_after_base(rows, dates):
    """{(uid, club): earliest applied row with that club after the club's
    base date}: by real date, so a game-day move the weekly roster already
    shows is still a move after the base."""
    out = {}
    for r in sorted((r for r in rows if r.get("outcome") == "APPLY" and r.get("uid")),
                    key=lambda r: (r["real_date"], r["id"])):
        code = r["club"]
        if code in dates and r["real_date"] > dates[code]["active"]:
            out.setdefault((r["uid"], code), r)
    return out


def joined_after_base(fill, restorations, rows, dates):
    """A fill or restoration player whose first move with his club after its
    base date is an addition was not on that club at the base: a build
    problem (the fill leaves such players out; a restoration must not
    contradict a dated row)."""
    first = _first_after_base(rows, dates)
    out = []
    for code, players in fill.items():
        for p in players:
            r = first.get((p["uid"], code))
            if r and r["kind"] in ADDITION_KINDS:
                out.append("fill %s %s joined after the base (%s, %s)" % (code, p["player_id"], r["id"], r["real_date"]))
    for p in restorations:
        r = first.get((p["uid"], p["club"]))
        if r and r["kind"] in ADDITION_KINDS:
            out.append("restoration %s %s joined after the base (%s, %s)" % (p["club"], p["player_id"], r["id"],
                                                                             r["real_date"]))
    return out


def build_fill(library, w1, control, ident, unplaced, availability=None, rows=(), dates=None):
    """The real Week 1 53 (nflverse weekly roster, membership only) minus the
    Week 1 library and every excluded player: the real-53 fill (R21 base).
    A player whose first applied move with the club after its base date is
    an addition joined after the base (a game-day signing the weekly roster
    already shows): he is left out, and that row adds him. Fill players join
    the bottom of their group by jersey, then name, with the Week 1 library's
    availability convention."""
    first = _first_after_base(rows, dates or {})
    lib = {}
    for club in library["clubs"].values():
        for p in club["players"]:
            lib[p["gsis_id"]] = club["code"]
    _, named = exclusions(library, control, ident)
    fill, excluded = collections.defaultdict(list), collections.defaultdict(list)
    for code in sorted(w1):
        if code == "JAX":
            continue
        for g, r in sorted(w1[code].items()):
            if lib.get(g) == code:
                continue
            reason = None
            if g in control.names:
                reason = "Jacksonville-controlled"
            elif g in unplaced:
                reason = "unplaced in the branch"
            elif g in lib:
                reason = "the branch has him at %s" % lib[g]
            elif norm(r["full_name"]) in named:
                reason = named[norm(r["full_name"])]
            elif (g, code) in first and first[(g, code)]["kind"] in ADDITION_KINDS:
                later = first[(g, code)]
                reason = "joined after the base date %s (%s, %s)" % (dates[code]["active"], later["id"],
                                                                     later["real_date"])
            if reason:
                excluded[code].append({"uid": g, "reason": reason})
                continue
            pos = ident.position(g, r["position"])
            if not pos:
                raise SystemExit("fill %s %s: no kernel position" % (code, r["full_name"]))
            available, back, report = availability(code, g) if availability else (True, None, None)
            fill[code].append({"uid": g, "player_id": ident.player_id(g, r["full_name"], code), "position": pos,
                               "jersey": r["jersey_number"], "birth_date": ident.birth_date(g),
                               "available": available, "return_week": back, "injury_report": report,
                               "basis": "nflverse weekly roster, Week 1 membership (status not read)"})
    for code in fill:
        fill[code].sort(key=lambda p: (int(p["jersey"]) if str(p["jersey"]).isdigit() else 999, p["player_id"]))
    return fill, excluded


# ESPN sentences (the research pass's parser, reduced to the moves the base needs).
def espn_sentences(desc):
    text = desc.replace("St. Louis", "St Louis")
    text = re.sub(r"\bJr\.(?=\s+(and|to|from|off|on|,))", "Jr", text)
    text = re.sub(r",\s+(?=(?:Waived|Signed|Released|Placed|Claimed|Activated|Terminated|Re-signed)\b)", ". ", text)
    text = re.sub(r"\s+and\s+(?=(?:waived|signed|released|placed|claimed|activated|terminated|re-signed)\b)", ". ", text)
    parts = re.split(r"(?<=[a-z0-9\)])\.\s+(?=[A-Z])|(?<=[a-z0-9\)])\.$|;\s+", text)
    return [p.strip(" .") for p in parts if p and p.strip(" .")]


def espn_names(chunk, positions=False):
    """The player names in an ESPN sentence fragment; with `positions`,
    (position token, name) pairs (the token ESPN puts in front of a name,
    or "")."""
    out = []
    for item in re.split(r",\s*(?:and\s+)?|\s+and\s+", chunk.strip()):
        item = re.sub(r"^(?:rookie|veteran|free agent)\s+", "", item.strip().strip("."), flags=re.I)
        m = re.match(r"^((?:[A-Z]{1,4}(?:[/-][A-Z]{1,4})*|CBk)\s+)?(.+)$", item)
        name = re.sub(r"\s+(?:to|from|off|on|with)\b.*$", "", m.group(2).strip()) if m else ""
        if len(name.split()) >= 2:
            token = (m.group(1) or "").strip().split("/")[0].split("-")[0] if m else ""
            out.append((token, name) if positions else name)
    return out


def espn_ps(src, lo, hi, positions=None):
    """{code: {norm name: (name, date)}} ESPN practice-squad signings minus
    releases, lo..hi; `positions`, when a dict, collects each signing's
    position token by (code, norm name)."""
    out = collections.defaultdict(dict)
    for r in sorted(src.espn, key=lambda r: r["date"]):
        if not lo <= r["date"] <= hi:
            continue
        code = ESPN_SLUG[r["espn"]]
        for s in espn_sentences(r["description"]):
            m = re.match(r"^(?:signed|re-signed|agreed to terms with)\s+(.*?)\s+to (?:the |their |a )?practice squad", s, re.I)
            if m:
                for token, n in espn_names(m.group(1), positions=True):
                    out[code][anorm(n)] = (n, r["date"])
                    if positions is not None and token:
                        positions[(code, anorm(n))] = token
                continue
            m = re.match(r"^(?:waived|released|terminated)\s+(.*?)\s+from (?:the |their )?practice squad", s, re.I)
            if m:
                for n in espn_names(m.group(1)):
                    out[code].pop(anorm(n), None)
    return out


def build_ps_base(src, ident, control, unplaced, lib_codes):
    """Practice squads as of September 1, the formation (engineering B3).

    Pass 1 is the wire's practice-squad signings dated on or before
    September 1; pass 2 is ESPN's team logs of August 30 to September 1,
    net of their practice-squad releases. Entries are matched across the
    two sources by club and spelling (`similar`) with any date from August 30
    to September 4. An ESPN entry whose wire counterpart is dated September 2
    to 4 is a dated row, not base. An entry in one source only enters the
    base unverified. A club's base is verified only when every entry has both
    sources and no name is unresolved; only then is its 10-player limit
    enforced (engineering review, minor items)."""
    wire_all = collections.defaultdict(list)
    for w in src.wire:
        if w["category"] == "signings" and w["transaction"] == "Practice Squad" and "2014-08-30" <= w["iso"] <= "2014-09-04":
            wire_all[NICK.get(w["to"])].append((w["name"], w["iso"]))
    tokens = {}
    espn = espn_ps(src, "2014-08-30", "2014-09-04", tokens)  # position tokens only, from the wider window
    espn = espn_ps(src, "2014-08-30", "2014-09-01")
    base, verified, notes = {}, {}, {}
    for code in sorted(set(lib_codes)):
        entries, ok, note = [], True, collections.defaultdict(list)
        espn_left = dict(espn.get(code, {}))
        for name, when in sorted(wire_all.get(code, ()), key=lambda x: (x[1], x[0])):
            match = next((k for k, (n, _) in espn_left.items() if similar_names(n, name)), None)
            espn_entry = espn_left.pop(match) if match else None
            if when > "2014-09-01":
                continue  # a dated row from September 2
            entries.append((name, when, ["nfl_wire"] + (["espn"] if espn_entry else []),
                            tokens.get((code, match)) if match else tokens.get((code, anorm(name)))))
        for key, (name, when) in sorted(espn_left.items()):
            entries.append((name, when, ["espn"], tokens.get((code, key))))
        rows = []
        for name, when, sources, stated in entries:
            uid, how = ident.resolve(name, "", [code])
            if not uid:
                note["unresolved"].append(name)
                ok = False
                continue
            if uid in control.names or uid in unplaced:
                continue  # never on a background squad in the branch
            if len(sources) < 2:
                note[sources[0] + "_only"].append(name)
                ok = False
            pos = ident.position(uid, stated or "")
            if not pos:
                note["no_position"].append(name)
                ok = False
                continue
            rows.append({"uid": uid, "player_id": ident.player_id(uid, name, code), "position": pos,
                         "since": when, "birth_date": ident.birth_date(uid), "sources": sources})
        base[code] = rows
        verified[code] = ok and bool(rows)
        if note:
            notes[code] = {k: sorted(v) for k, v in note.items()}
    return base, verified, notes


def build_restorations(src, ident, control, w1, lib_codes, fill, through):
    """Players suspended or on an exempt list at Week 1 and so on no Week 1
    chart (rules review C2): restored to their real clubs at the bottom of
    their groups, available (rails rule 2). The systematic pass is the
    wire's reserve/suspended and exempt placements dated on or before
    September 6 (every suspended player had to be placed at the August 30
    reduction); ESPN logs and outside sources are the second pass."""
    placements = collections.OrderedDict()
    for w in sorted(src.wire, key=lambda w: w["iso"]):
        tx = w["transaction"]
        if w["iso"] > "2014-09-06" or not ("Reserve/Suspended" in tx or "Exempt/Commissioner" in tx):
            continue
        placements.setdefault(norm(w["name"]), {"name": w["name"], "club": NICK.get(w["from"]), "date": w["iso"],
                                                "wire": "%s (%s)" % (tx, w["iso"]),
                                                "page": src.wire_pages.get(w["page_url"])})
    for e in EARLY_SUSPENSIONS:
        placements.setdefault(norm(e["name"]), {"name": e["name"], "club": e["club"], "date": e["announced"],
                                                "wire": None, "page": None, "outside": e["sources"]})
    reserve_ir = {norm(w["name"]) for w in src.wire if w["category"] == "reserve-list" and w["iso"] <= "2014-09-06"
                  and "Injured" in w["transaction"]}
    released = collections.defaultdict(list)
    for w in src.wire:
        if w["category"] in ("waivers", "terminations") and w["transaction"].startswith(("Waived", "Terminated")):
            released[norm(w["name"])].append((w["iso"], NICK.get(w["from"])))
    espn_text = collections.defaultdict(list)
    for r in src.espn:
        if r["date"] <= "2014-09-06":
            for sentence in espn_sentences(r["description"]):
                espn_text[ESPN_SLUG[r["espn"]]].append((r["date"], sentence))
    lifted = collections.defaultdict(list)
    for w in src.wire:
        if w["transaction"].startswith("Suspension Lifted") and w["iso"] <= through:
            lifted[norm(w["name"])].append(w["iso"])
    fill_uids = {p["uid"] for rows in fill.values() for p in rows}
    out, skipped = [], []
    for key, p in placements.items():
        code = p["club"]
        uid, how = ident.resolve(p["name"], "", [code])
        reason = None
        if code not in lib_codes:
            reason = "no background club"
        elif uid is None:
            reason = "identity unresolved"
        elif uid in control.names:
            reason = "Jacksonville-controlled"
        elif uid in ident.library:
            reason = "already on a Week 1 chart"
        elif uid in fill_uids or uid in w1.get(code, {}):
            reason = "on the real Week 1 roster (in the real-53 fill)"
        elif key in reserve_ir:
            reason = "on the real reserve/injured list before Week 1 (a pre-Week 1 injury stays real)"
        elif any(when <= "2014-09-06" and c == code for when, c in released.get(key, ())):
            reason = "released by his club before Week 1, so a free agent at Week 1"

        if reason:
            if reason in ("Jacksonville-controlled", "no background club"):
                # A Jacksonville or real-Jaguars suspension is never named (rules C6).
                skipped.append({"reason": reason})
            else:
                skipped.append({"player": p["name"], "club": code, "reason": reason})
            continue
        espn = sorted({day for day, t in espn_text.get(code, ()) if p["name"] in t and re.search(r"suspen|exempt", t, re.I)})
        second = ["ESPN team log, %s" % day for day in espn]
        second += ["NFL.com wire, Suspension Lifted by Commissioner, %s" % day for day in sorted(set(lifted.get(key, ())))]
        second += (p.get("outside") or []) + (
            [OUTSIDE_SUSPENSION_SOURCE[p["name"]]] if p["name"] in OUTSIDE_SUSPENSION_SOURCE else [])
        pos = ident.position(uid, "")
        out.append({"uid": uid, "player_id": ident.player_id(uid, p["name"], code), "position": pos,
                    "club": code, "date": p["date"], "birth_date": ident.birth_date(uid),
                    "first_pass": p.get("wire") or "outside sources (announcement %s)" % p["date"],
                    "second_pass": second or ["nflverse Week 1 membership: not on the 53 (one publisher)"],
                    "available": True})
    return out, skipped


def window_corrections(library, base_clubs, fill, restorations, ps_base, rows, control, codes):
    """Explicit dated base corrections (engineering B3, rules B1): a row
    inside a club's base window whose final effect the base contradicts."""
    on = collections.defaultdict(set)
    for club in library["clubs"].values():
        for p in club["players"]:
            on[club["code"]].add(p["gsis_id"])
    for code, players in fill.items():
        on[code].update(p["uid"] for p in players)
    for r in restorations:
        on[r["club"]].add(r["uid"])
    last = {}
    order = lambda r: (r["gate_date"], 0 if rails.KINDS[r["kind"]][0] in ("depart", "retire") else 1,
                       rails.ADD_RANK.get(r["kind"], 0), r["id"])
    for r in sorted((r for r in rows if r["outcome"] == "APPLY"), key=order):
        action, layer = rails.KINDS[r["kind"]]
        code = r["club"]
        if code not in base_clubs or r["gate_date"] > base_clubs[code]["base_as_of"]["active"]:
            continue
        if action == "add" and layer == "active":
            last[(r["uid"], code)] = ("in", r)
        elif action == "depart" and layer in ("active", "any"):
            last[(r["uid"], code)] = ("out", r)
        elif action == "retire":
            for c in codes:
                if r["uid"] in on[c]:
                    last[(r["uid"], c)] = ("out", r)
    corrections = []
    for (uid, code), (state, r) in sorted(last.items(), key=lambda kv: (kv[1][1]["gate_date"], kv[1][1]["id"])):
        present = uid in on[code]
        elsewhere = [c for c in codes if c != code and uid in on[c]]
        if state == "in" and not present:
            if elsewhere:
                corrections.append({"action": "remove", "club": elsewhere[0], "uid": uid, "player_id": r["player_id"],
                                    "position": r["position"], "date": r["gate_date"], "evidence": [r["id"]],
                                    "reason": "moved to %s inside the base window" % code})
            corrections.append({"action": "add", "club": code, "uid": uid, "player_id": r["player_id"],
                                "position": r["position"], "date": r["gate_date"], "evidence": [r["id"]],
                                "reason": "a real addition inside the base window that the Week 1 base lacks"})
        elif state == "out" and present:
            corrections.append({"action": "remove", "club": code, "uid": uid, "player_id": r["player_id"],
                                "position": r["position"], "date": r["gate_date"], "evidence": [r["id"]],
                                "reason": "a real departure inside the base window that the Week 1 base still lists"})
    for i, c in enumerate(corrections, 1):
        c["id"] = "BC14-%04d" % i
    return corrections


# ---- main -----------------------------------------------------------------------------

def context(source_dir):
    src = Sources(source_dir)
    library = json.loads((ROOT / LIBRARY).read_text(encoding="utf-8"))
    ident = Identity(library, src)
    control = rails.jacksonville_control(SEASON, ROOT)
    w1 = week1_membership(src)
    unplaced = unplaced_uids(library, ident, control, w1)
    src.pre_reserve = pre_week1_reserve(src, library)
    return src, library, ident, control, w1, unplaced


def candidates(src, ident, control, pre_reserve, through):
    rows, problems = research_rows(src, ident, control, pre_reserve)
    rows.sort(key=lambda r: (r["gate_date"], r["uid"] or "", r["research_ref"]))
    mark_after_real_jaguars(rows)
    rows = [r for r in rows if r["gate_date"] <= through]
    return rows, problems


# Position groups one player is listed under by different sources for scheme
# reasons (an edge rusher as end or linebacker, a fullback as back or end):
# not evidence of a namesake.
ADJACENT_GROUPS = {frozenset({"DL", "LB"}), frozenset({"RB", "FB"}), frozenset({"TE", "FB"})}


def _same_role(a, b):
    return a == b or frozenset({a, b}) in ADJACENT_GROUPS


def position_problems(row, committed, ident):
    """The identity guard (rules review B4): an applied row whose source
    states a 2014 position group (a) that differs from the base player's
    when the gsis is on a Week 1 chart, or (b) for a name-only match, that a
    namesake in nflverse players.csv fits while the chosen identity does
    not. Either stops the build until an IDENTITY fix names the player."""
    if committed.get("outcome") != "APPLY" or not committed.get("uid"):
        return []
    stated = group(row.get("src_pos") or "")
    if not stated:
        return []
    uid = committed["uid"]
    if uid in ident.library:
        base = group(ident.library[uid]["position"])
        if not _same_role(base, stated):
            return ["%s: gsis %s is a base %s, the source says %s (%s)" % (
                committed["id"], uid, base, row["src_pos"], row["research_ref"])]
        return []
    if row.get("identity_basis") == "review_fix":
        return []
    name_only = row.get("identity_basis", "").startswith("players_csv_name") or "name" in row.get("gsis_match", "")
    if not name_only:
        return []
    chosen = group(ident.weekly_pos.get(uid) or (ident.players.get(uid) or {}).get("position") or "")
    if _same_role(chosen, stated):
        return []
    namesakes = [g for g, p in ident.players.items() if g != uid and anorm(p["display_name"]) == anorm(row["player"])
                 and _same_role(group(p.get("position") or ""), stated)]
    if namesakes:
        return ["%s: %s matched by name to %s (%s), the source says %s; namesake %s fits (%s)" % (
            committed["id"], row["player"], uid, chosen, row["src_pos"], ", ".join(sorted(namesakes)),
            row["research_ref"])]
    return []


def number(rows, first, efw, ident, problems):
    """Committed rows numbered from `first` in (gate date, player id) order."""
    for i, r in enumerate(rows, first):
        r["id"] = "R14-%04d" % i
        r["effective_from_week"] = efw
    committed = [finish(r, ident) for r in rows]
    for r, c in zip(rows, committed):
        if c.get("outcome") == "APPLY" and c.get("uid") and not c.get("position"):
            problems.append("%s: no kernel position for %s" % (c["id"], c["player"]))
        problems.extend(position_problems(r, c, ident))
    return committed


def build(source_dir, through):
    src, library, ident, control, w1, unplaced = context(source_dir)
    codes = sorted(c["code"] for c in library["clubs"].values())
    rows, problems = candidates(src, ident, control, src.pre_reserve, through)
    efw = last_closed_week() + 1
    committed = number(rows, 1, efw, ident, problems)
    dates = base_dates(library)
    fill, excluded = build_fill(library, w1, control, ident, unplaced, week1_availability(src), committed, dates)
    ps_base, ps_verified, ps_notes = build_ps_base(src, ident, control, unplaced, codes)
    restorations, restoration_skips = build_restorations(src, ident, control, w1, codes, fill, through)
    problems += joined_after_base(fill, restorations, committed, dates)
    base_clubs = {code: {"base_as_of": dates[code]} for code in codes}
    corrections = window_corrections(library, base_clubs, fill, restorations, ps_base, committed, control, codes)
    # Fill, restorations and window corrections are one ordered list.
    base_corr = []
    for code in codes:
        for p in fill.get(code, ()):
            base_corr.append({"action": "add", "club": code, "uid": p["uid"], "player_id": p["player_id"],
                              "position": p["position"], "date": dates[code]["active"],
                              "reason": "real Week 1 roster, not on the Week 1 chart (real-53 fill)",
                              "kind": "fill", "birth_date": p["birth_date"]})
            if not p["available"]:
                base_corr[-1].update({"available": False, "return_week": p["return_week"],
                                      "injury_report": p["injury_report"]})
    for r in sorted(restorations, key=lambda r: (r["club"], r["date"], r["uid"])):
        base_corr.append({"action": "add", "club": r["club"], "uid": r["uid"], "player_id": r["player_id"],
                          "position": r["position"], "date": dates[r["club"]]["active"],
                          "reason": "on a league suspension or exempt list at Week 1; restored, available (rails rule 2)",
                          "kind": "restoration", "birth_date": r["birth_date"],
                          "first_pass": r["first_pass"], "second_pass": r["second_pass"]})
    n = 0
    for c in base_corr:
        n += 1
        c["id"] = "BF14-%04d" % n
    for c in corrections:
        c["kind"] = "window"
    base_corr += corrections
    base = {"schema_version": 1, "season": SEASON, "effective_from_week": efw,
            "library": LIBRARY, "library_clubs_sha256": rails.clubs_block_sha256(library),
            "clubs": {code: {"base_as_of": dates[code], "ps_base_verified": ps_verified[code],
                             "practice_squad": ps_base.get(code, []),
                             "ps_base_notes": ps_notes.get(code, {}),
                             "fill_excluded": excluded.get(code, [])} for code in codes},
            "corrections": base_corr,
            "restoration_sweep_skipped": restoration_skips,
            "unplaced_former_jaguars": sorted(unplaced)}
    return src, library, base, committed, problems


def replay_states(manifest, base, rows, library, labels, control):
    """The states the weekly build will compute for the open week, through
    the same path (runtime.week_inputs.rails_slate: every scheduled week's
    last cutoff, the C6 placements from the closed receipts, emergency
    promotions and the slate deferral), plus one at the as-of date when it
    is later than the week's last cutoff. Returns (states, errors)."""
    from runtime import week_inputs
    from scripts.render_season_stats import load_receipts
    data = rails.from_parts(manifest, base, rows, library, ROOT, labels)
    week = int(manifest["shards"][-1]["week"])
    receipts = [r for r in load_receipts(SeasonPaths(SEASON, ROOT).receipts) if int(r["week"]) < week]
    slate = week_inputs.rails_slate(week, SEASON, receipts, data=data, control=control, strict=False)
    states, errors = list(slate["states"].values()), list(slate["errors"])
    as_of = d(manifest["as_of"])
    if as_of > max(slate["states"]):
        st = rails.league_state(data, as_of, slate["branch"], slate["last_cutoffs"])
        states.append(st)
        errors += st.errors
    return states, sorted(set(errors))


def label_noops(src, library, manifest, base, rows, control, labels):
    """Run the replay the weekly build will run (`replay_states`) and label
    each no-op departure of a player the base never carried (closed-list
    reason never_in_branch), with its evidence: on the real reserve list
    before Week 1 (a pre-Week 1 injury stays real), or no signing with that
    club in either source. Labels go into the shard that adds them; any
    other replay error stops the build. Returns (errors, new labels by
    club)."""
    def run(extra):
        merged = {code: list(labels.get(code, [])) + extra.get(code, []) for code in set(labels) | set(extra)}
        return replay_states(manifest, base, rows, library, merged, control)
    new = {}
    _, errors = run(new)
    pending = [e for e in errors if e.startswith("unexplained no-op")]
    if not pending:
        return errors, new
    by_id = {r["id"]: r for r in rows}
    reserve = {(norm(w["name"]), NICK.get(w["from"])) for w in src.wire
               if w["category"] == "reserve-list" and w["iso"] <= "2014-09-06"}
    for err in pending:
        r = by_id[err.split()[2]]
        evidence = ("on the real reserve list before Week 1 (wire reserve-list); a pre-Week 1 injury stays real"
                    if (norm(r["player"]), r["club"]) in reserve else
                    "no signing with this club in either source before the departure")
        new.setdefault(r["club"], []).append({"uid": r["uid"], "player_id": r["player_id"], "row": r["id"],
                                              "evidence": evidence})
    _, errors = run(new)
    return errors, new


def last_closed_week():
    weeks = [json.loads(p.read_text())["week"] for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")]
    return max(weeks) if weeks else 0


def dumps(value):
    """Stable JSON with one list item per line for the long lists (rows,
    corrections, squads): compact, diff-friendly and append-only."""
    def item(v):
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))

    def block(v, indent):
        pad = " " * indent
        if isinstance(v, dict):
            if not v:
                return "{}"
            inner = ",\n".join("%s %s: %s" % (pad, json.dumps(k), block(x, indent + 1)) for k, x in v.items())
            return "{\n%s\n%s}" % (inner, pad)
        if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
            return "[\n%s\n%s]" % (",\n".join(pad + " " + item(x) for x in v), pad)
        return item(v)
    return block(value, 0) + "\n"


def _pages(src, through):
    """Page hashes for the wire months the committed rows can reach (never a
    month after `through`) and the 32 ESPN season logs."""
    month = int(through[5:7])
    return {"nfl_wire": {url: h for url, h in sorted(src.wire_pages.items())
                         if int(re.search(r"/2014/(\d+)", url).group(1)) <= month},
            "espn": {code: h for code, h in sorted(src.espn_pages.items())}}


def _write(outputs, check):
    if check:
        stale = [n for n, t in outputs.items() if not (OUT / n).is_file() or (OUT / n).read_text() != t]
        return stale
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in outputs.items():
        (OUT / name).write_text(text, encoding="utf-8")
    return []


def first_build(args):
    src, library, base, rows, problems = build(args.source_dir, args.through)
    if problems:
        print("STOPPED:\n- " + "\n- ".join(problems))
        return 1
    efw = base["effective_from_week"]
    shard_name = "week_%02d.json" % efw
    manifest = {
        "schema_version": rails.SCHEMA_VERSION, "season": SEASON, "as_of": args.through,
        "status": "PREPARED, GATED", "effective_from_week": efw,
        "builder": "scripts/research/build_2014_inseason_rails.py",
        "base": {"path": "base.json", "library": LIBRARY, "library_clubs_sha256": base["library_clubs_sha256"]},
        "shards": [{"week": efw, "path": shard_name, "through": args.through}],
        "builds": [{"through": args.through, "rows": [rows[0]["id"], rows[-1]["id"]], "inputs": src.hashes}],
        "sources": "sources.json", "amendments": [],
        "decisions": "library/2014_inseason_rails.md#decisions",
    }
    errors, labels = label_noops(src, library, manifest, base, rows, rails.jacksonville_control(SEASON, ROOT), {})
    if errors:
        print("STOPPED:\n- " + "\n- ".join(errors))
        return 1
    shard = {"schema_version": 1, "season": SEASON, "effective_from_week": efw, "rows": rows,
             "noop_labels": {code: labels[code] for code in sorted(labels)}}
    outputs = {"base.json": dumps(base), shard_name: dumps(shard), "sources.json": dumps(_pages(src, args.through))}
    manifest["base"]["sha256"] = hashlib.sha256(outputs["base.json"].encode()).hexdigest()
    manifest["shards"][0]["sha256"] = hashlib.sha256(outputs[shard_name].encode()).hexdigest()
    manifest["shards"][0]["rows"] = len(rows)
    outputs["manifest.json"] = dumps(manifest)
    stale = _write(outputs, args.check)
    if stale:
        print("STALE: " + ", ".join(stale))
        return 1
    counts = collections.Counter(r["outcome"] for r in rows)
    print("IN-SEASON RAILS: %s %d rows through %s; %s" % ("CURRENT" if args.check else "WRITTEN", len(rows),
                                                        args.through, dict(sorted(counts.items()))))
    return 0


def _key(row):
    if row["outcome"] in rails.STRIPPED_OUTCOMES:
        return ("stripped", row["gate_date"], row["club"], row["outcome"])
    return ("full", row["gate_date"], row["club"], row["kind"], row.get("uid") or row.get("player"))


def extend(args, manifest):
    """Append the rows gated after the committed as-of date through
    `--through`, plus any late-found row dated earlier, numbered from the
    current maximum; never edit a committed row or the base. New rows take
    the first open week as their effective week and go to that week's shard;
    a closed week's shard is never touched (engineering review B5)."""
    src, library, ident, control, w1, unplaced = context(args.source_dir)
    base = json.loads((OUT / manifest["base"]["path"]).read_text(encoding="utf-8"))
    shards = {s["path"]: json.loads((OUT / s["path"]).read_text(encoding="utf-8")) for s in manifest["shards"]}
    existing = [r for s in manifest["shards"] for r in shards[s["path"]]["rows"]]
    labels = {}
    for s in manifest["shards"]:
        for code, entries in shards[s["path"]].get("noop_labels", {}).items():
            labels.setdefault(code, []).extend(entries)
    for r in existing:  # the identity assignments already committed stay frozen
        if r.get("uid") and r.get("player_id"):
            ident.assigned[r["uid"]] = r["player_id"]
    rows, problems = candidates(src, ident, control, src.pre_reserve, args.through)
    left = collections.Counter(_key(r) for r in existing)
    new = []
    for r in rows:
        probe = finish(dict(r, id="R14-0000", effective_from_week=0), ident)
        key = _key(probe)
        if left[key]:
            left[key] -= 1
            continue
        new.append(r)
    if problems:
        print("STOPPED:\n- " + "\n- ".join(problems))
        return 1
    if not new:
        print("IN-SEASON RAILS: nothing to append through %s" % args.through)
        return 0
    efw = last_closed_week() + 1
    first = int(existing[-1]["id"].split("-")[1]) + 1 if existing else 1
    added = number(new, first, efw, ident, problems)
    if problems:
        print("STOPPED:\n- " + "\n- ".join(problems))
        return 1
    late = [r["id"] for r in added if r["gate_date"] <= manifest["as_of"]]
    shard_name = "week_%02d.json" % efw
    if shard_name not in shards:
        shards[shard_name] = {"schema_version": 1, "season": SEASON, "effective_from_week": efw, "rows": [],
                              "noop_labels": {}}
        manifest["shards"].append({"week": efw, "path": shard_name})
    shards[shard_name]["rows"].extend(added)
    manifest["as_of"] = args.through
    manifest["builds"].append({"through": args.through, "rows": [added[0]["id"], added[-1]["id"]],
                               "late_found": late, "inputs": src.hashes})
    all_rows = existing + added
    errors, new_labels = label_noops(src, library, manifest, base, all_rows, control, labels)
    if errors:
        print("STOPPED:\n- " + "\n- ".join(errors))
        return 1
    for code, entries in new_labels.items():
        shards[shard_name]["noop_labels"].setdefault(code, []).extend(entries)
    pages = json.loads((OUT / "sources.json").read_text(encoding="utf-8"))
    for kind, mapping in _pages(src, args.through).items():
        pages.setdefault(kind, {}).update({k: v for k, v in mapping.items() if k not in pages[kind]})
    outputs = {shard_name: dumps(shards[shard_name]), "sources.json": dumps(pages)}
    for s in manifest["shards"]:
        if s["path"] == shard_name:
            s.update({"through": args.through, "sha256": hashlib.sha256(outputs[shard_name].encode()).hexdigest(),
                      "rows": len(shards[shard_name]["rows"])})
    outputs["manifest.json"] = dumps(manifest)
    _write(outputs, False)
    print("IN-SEASON RAILS: APPENDED %d rows (%s to %s) through %s%s" % (
        len(added), added[0]["id"], added[-1]["id"], args.through,
        "; late-found: " + ", ".join(late) if late else ""))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--through", required=True)
    parser.add_argument("--check", action="store_true", help="rebuild the first build and compare (no write)")
    parser.add_argument("--extend", action="store_true", help="append rows after the committed as-of date")
    args = parser.parse_args()
    master = player_bios.master_date(ROOT)
    if d(args.through) > master:
        print("REFUSED: --through %s is after the master date %s (information gate)" % (args.through, master))
        return 1
    manifest_path = OUT / "manifest.json"
    existing = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    if args.extend:
        if not existing:
            print("REFUSED: nothing committed to extend")
            return 1
        if args.through < existing["as_of"]:
            print("REFUSED: --through %s is before the committed as-of date %s" % (args.through, existing["as_of"]))
            return 1
        return extend(args, existing)
    if existing and not args.check:
        print("REFUSED: the first build is committed and its rows are never edited; append with --extend "
              "(rows after %s)" % existing["as_of"])
        return 1
    return first_build(args)


if __name__ == "__main__":
    sys.exit(main())
