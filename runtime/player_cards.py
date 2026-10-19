"""The player statistics and identity layer the player pages read (runtime/player_pages.py).

Rebuild step 3a (October 19, 2026) moved the page layout to runtime/player_pages.py, which
writes every player page from the permanent player records (runtime/people.py); the career-card
images are no longer drawn. This module keeps what the pages read through:

- ``card_data``: every player in the game records (2013 and 2014), keyed by gsis id, with the
  club of his latest game, his clubs, age on each season's opening game and number by season
  (``season_number``), and a block per season and game type (regular season, playoffs) holding
  his games, the totals of every recorded field and which later-record fields every game carries;
- ``Identity``: the committed identity sources (the identity map, the birth-date registry with
  the user's canon overrides through runtime/player_bios.py, the 2014 Week 1 rosters, the league
  player database and the listed 2014 identity); a name-keyed entry is used only when its gsis id
  is the player's;
- ``award_entries``: every award decided on record and where it was decided;
- ``jacksonville_rows``: the Season | Team | Age | # lead of the working cards before step 3a
  (scripts/update_player_cards.py keeps that format for the season-close tools).

Every statistic is arithmetic on the committed game records (the receipts the statbook reads),
with the repository's own field names, loaders and passer rating; totals equal
``runtime.statbook.aggregate_receipts``. A value the records do not carry is "N/A", never 0 or an
estimate. This is a reader view: no game, evaluation or decision reads it.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import unicodedata
from pathlib import Path

from runtime import player_bios
from runtime import postseason as post_mod
from runtime.play_detail import DRIVE_SUMMARY_FIELDS
from runtime.season_layout import BIRTH_DATE_CORRECTIONS
from runtime.seasons import SeasonPaths
from runtime.stat_tables import rating_value, thrown
from runtime.statbook import LONG_FIELDS, kernel_at_least

ROOT = Path(__file__).resolve().parents[1]
FOLDER = "career/league_players"
JAX = "Jacksonville Jaguars"
JAX_CODE = "JAX"
N_A = "N/A"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
# Fields only later game records carry (runtime/player_evidence.py STAT_FIELDS comments).
FROM_KERNEL = {"line_starts": (2014, 3), "long_snaps": (2014, 3), "special_teams_tackles": (2014, 3),
               "offensive_snaps": (2014, 4), "defensive_snaps": (2014, 4), "special_teams_snaps": (2014, 4)}
GROUP_OF = {}
for _grp, _poss in {"QB": "QB", "RB": "RB HB FB", "WR": "WR", "TE": "TE",
                    "OL": "OT OG G T C OL LT LG RG RT", "DL": "DE DT NT DL",
                    "LB": "OLB ILB MLB LB", "DB": "CB S FS SS DB", "K": "K PK", "P": "P", "LS": "LS"}.items():
    for _p in _poss.split():
        GROUP_OF[_p] = _grp
GROUPS = (("QB", "Quarterbacks"), ("RB", "Running backs"), ("WR", "Wide receivers"), ("TE", "Tight ends"),
          ("OL", "Offensive line"), ("DL", "Defensive line"), ("LB", "Linebackers"), ("DB", "Defensive backs"),
          ("K", "Kickers"), ("P", "Punters"), ("LS", "Long snappers"))
# The season whose rosters the listed identity's 2014 numbers come from (Weeks 1-4).
LISTING_SEASON = 2014


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def slugify(name):
    """The repository's player slug (scripts/build_annual_player_sheets.slugify)."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")
    if not slug:
        raise ValueError("player name cannot produce an empty slug")
    return slug


def display(name):
    """A record name without its disambiguating club suffix, e.g. 'Name (NYJ)'."""
    return re.sub(r"\s+\([A-Z]{2,3}\)$", "", name)


def long_date(iso):
    d = dt.date.fromisoformat(iso)
    return "%s %d, %d" % (MONTHS[d.month - 1], d.day, d.year)


# ------------------------------------------------------------------ records
def record_years(root):
    years = _load(root / "docs/repository_map.json")["record_years"]
    return tuple(y for y in sorted(years) if SeasonPaths(y, root).receipts.is_dir())


def _receipts(directory):
    return [_load(p) for p in sorted(Path(directory).glob("*.json"))] if Path(directory).is_dir() else []


def _kv(receipt):
    return tuple(int(x) for x in str(receipt.get("kernel_version", "0.0")).split(".")[:2])


def collect(root=ROOT):
    """Every player-game on record, with the season context the cards need."""
    root = Path(root)
    games, long_seen, club_games, receipts_by = [], {}, {}, {}
    for year in record_years(root):
        paths = SeasonPaths(year, root)
        reg, post = _receipts(paths.receipts), _receipts(paths.postseason_receipts)
        receipts_by[year] = {"regular": reg, "playoffs": post}
        dates = {(int(g["week"]), g["away"], g["home"]): g["date"] for g in _load(paths.schedule)["games"]}
        for w in sorted({int(r["week"]) for r in post}):
            for g in post_mod.schedule(w, regular_receipts=reg, post_receipts=post, season=year):
                dates[(w, g["away"], g["home"])] = g["date"]
        for gtype, recs in (("regular", reg), ("playoffs", post)):
            for r in recs:
                week = int(r["week"])
                date = dates.get((week, r["away"], r["home"]))
                if date is None:
                    raise ValueError("no scheduled date for %s %s" % (year, r["event_id"]))
                drives = [dict(zip(DRIVE_SUMMARY_FIELDS, row)) for row in r.get("drives", ())]
                k = _kv(r)
                for team, g in r["team_stats"].items():
                    club_games.setdefault((year, gtype, team), []).append(date)
                    opp = next(t for t in r["team_stats"] if t != team)
                    opp_players = r["team_stats"][opp].get("players", {})
                    players = {p: l for p, l in g.get("players", {}).items() if not str(p).startswith("__")}
                    # Field-goal distances are credited only when one kicker took every attempt
                    # and the drive summaries agree with his attempts and makes.
                    fg_drives = [d for d in drives if d.get("team") == team and d.get("category") == "field_goal_attempt"]
                    kickers = [p for p, l in players.items() if l.get("field_goals_attempted", 0)]
                    fg_by = {}
                    if len(kickers) == 1 and drives:
                        line = players[kickers[0]]
                        ok = (len(fg_drives) == line.get("field_goals_attempted", 0)
                              and sum(1 for d in fg_drives if d.get("fg_made")) == line.get("field_goals_made", 0)
                              and all(isinstance(d.get("fg_distance"), (int, float)) for d in fg_drives))
                        fg_by[kickers[0]] = [(int(d["fg_distance"]), bool(d["fg_made"])) for d in fg_drives] if ok else None
                    else:
                        fg_by.update((p, None) for p in kickers)
                    punters = [p for p, l in players.items() if l.get("punts", 0)]
                    ret_allowed = (sum(l.get("punt_return_yards", 0) for l in opp_players.values())
                                   if len(punters) == 1 else None)
                    for pid, line in players.items():
                        long_seen.setdefault(k, set()).update(f for f in LONG_FIELDS if f in line)
                        games.append({
                            "pid": pid, "year": year, "type": gtype, "week": week, "date": date, "team": team,
                            "kernel": k, "line": line, "pos": line.get("position", ""),
                            "nums": tuple((f, v) for f, v in line.items() if f != "position"
                                          and not isinstance(v, bool) and isinstance(v, (int, float))),
                            "fg": fg_by.get(pid, []) if line.get("field_goals_attempted", 0) else [],
                            "ret_allowed": (ret_allowed if pid in punters else 0) if line.get("punts", 0) else 0,
                        })
    return {"games": games, "long_seen": long_seen, "club_games": club_games, "receipts": receipts_by}


# ------------------------------------------------------------------ totals
def total(rows):
    t = {}
    for r in rows:
        for f, v in r["nums"]:
            t[f] = max(t.get(f, 0), v) if f in LONG_FIELDS else t.get(f, 0) + v
    return t


def fi(v):
    return N_A if v is None else "{:,}".format(int(v))


def f1(v):
    return N_A if v is None else "%.1f" % v


def ratio(a, b, scale=1.0):
    return None if not b else a / b * scale


def made_att(m, a):
    return "%s-%s" % (fi(m), fi(a))


def sack_text(v):
    return f1(v) if v % 1 else fi(v)


def tiles_for(group, rows, long_seen):
    """The ten (label, value) tiles of a block, from that block's games."""
    t = total(rows)
    n = len(rows)

    def gv(f):
        return t.get(f, 0)

    def ok(f):
        if f in FROM_KERNEL:
            return all(kernel_at_least(".".join(map(str, r["kernel"])), FROM_KERNEL[f]) for r in rows)
        if f in LONG_FIELDS:
            return all(f in long_seen.get(r["kernel"], set()) for r in rows)
        return True

    def opt(label, f):
        return (label, fi(gv(f)) if ok(f) else N_A)

    def per_game(label, f):
        return (label, f1(ratio(gv(f), n)) if ok(f) else N_A)

    if group == "QB":
        att, cmp_, yds = gv("pass_attempts"), gv("completions"), gv("passing_yards")
        return [("CMP-ATT", made_att(cmp_, att)), ("CMP%", f1(ratio(cmp_, att, 100))), ("YDS", fi(yds)),
                ("TD", fi(gv("passing_touchdowns"))), ("INT", fi(thrown(t))), ("Y/A", f1(ratio(yds, att))),
                ("RATE", f1(rating_value(t))), ("YDS/G", f1(ratio(yds, n))),
                ("RUSH YDS", fi(gv("rushing_yards"))), ("RUSH TD", fi(gv("rushing_touchdowns")))]
    if group == "RB":
        car, ry = gv("rushing_attempts"), gv("rushing_yards")
        return [("CAR", fi(car)), ("RUSH YDS", fi(ry)), ("Y/C", f1(ratio(ry, car))),
                ("RUSH TD", fi(gv("rushing_touchdowns"))), ("YDS/G", f1(ratio(ry, n))), ("REC", fi(gv("receptions"))),
                ("REC YDS", fi(gv("receiving_yards"))), ("REC TD", fi(gv("receiving_touchdowns"))),
                ("TOUCHES", fi(car + gv("receptions"))), ("FUM LOST", fi(gv("fumbles_lost")))]
    if group in ("WR", "TE"):
        tgt, rec, yds = gv("targets"), gv("receptions"), gv("receiving_yards")
        long_tile = (("LONG", fi(gv("long_reception")) if rec else N_A) if ok("long_reception")
                     else ("REC/G", f1(ratio(rec, n))))
        return [("TGT", fi(tgt)), ("REC", fi(rec)), ("YDS", fi(yds)), ("Y/R", f1(ratio(yds, rec))),
                ("TD", fi(gv("receiving_touchdowns"))), ("YDS/G", f1(ratio(yds, n))),
                ("CATCH%", f1(ratio(rec, tgt, 100))), long_tile, ("RUSH YDS", fi(gv("rushing_yards"))),
                ("FUM LOST", fi(gv("fumbles_lost")))]
    if group in ("DL", "LB"):
        # Defensive touchdowns and safeties are not player fields in these records: PRESS and SOLO stand in.
        return [("TKL", fi(gv("tackles"))), ("SACK", sack_text(gv("sacks"))), ("TFL", fi(gv("tackles_for_loss"))),
                ("INT", fi(gv("defensive_interceptions"))), ("PD", fi(gv("passes_defended"))),
                ("FF", fi(gv("forced_fumbles"))), ("FR", fi(gv("fumble_recoveries"))), ("PRESS", fi(gv("pressures"))),
                ("TKL/G", f1(ratio(gv("tackles"), n))), ("SOLO", fi(gv("solo_tackles")))]
    if group == "DB":
        # Defensive touchdowns are not a player field in these records: TFL stands in.
        return [("TKL", fi(gv("tackles"))), ("INT", fi(gv("defensive_interceptions"))),
                ("PD", fi(gv("passes_defended"))), ("INT YDS", fi(gv("interception_return_yards"))),
                ("TFL", fi(gv("tackles_for_loss"))), ("SACK", sack_text(gv("sacks"))),
                ("FF", fi(gv("forced_fumbles"))), ("FR", fi(gv("fumble_recoveries"))),
                ("TKL/G", f1(ratio(gv("tackles"), n))),
                ("RET YDS", fi(gv("kick_return_yards") + gv("punt_return_yards")))]
    if group == "K":
        fgm, fga = gv("field_goals_made"), gv("field_goals_attempted")
        xpm, xpa = gv("extra_points_made"), gv("extra_points_attempted")
        kicks, known = [], True
        for r in rows:
            if r["fg"] is None:
                known = False
            else:
                kicks.extend(r["fg"])
        pts = 3 * fgm + xpm

        def band(label, lo, hi):
            if not known:
                return (label, N_A)
            b = [(d, m) for d, m in kicks if lo <= d <= hi]
            return (label, made_att(sum(m for _, m in b), len(b)))
        made = [d for d, m in kicks if m]
        long_ = ("LONG", (fi(max(made)) if made else N_A) if known else N_A)
        # Kickoffs and touchbacks are not player fields in these records: FG 1-39 stands in.
        return [("FGM-FGA", made_att(fgm, fga)), ("FG%", f1(ratio(fgm, fga, 100))), long_,
                ("XPM-XPA", made_att(xpm, xpa)), ("XP%", f1(ratio(xpm, xpa, 100))), ("PTS", fi(pts)),
                band("FG 40-49", 40, 49), band("FG 50+", 50, 999), band("FG 1-39", 0, 39),
                ("PTS/G", f1(ratio(pts, n)))]
    if group == "P":
        p, y, tb = gv("punts"), gv("punt_yards"), gv("punt_touchbacks")
        ret = None if any(r["ret_allowed"] is None for r in rows) else sum(r["ret_allowed"] for r in rows)
        # NET = (gross yards - punt return yards allowed - 20 x touchbacks) / punts, from the opponents'
        # punt-return lines in games where he was his club's only punter. Blocks are not recorded: IN20% stands in.
        net = None if ret is None or not p else (y - ret - 20 * tb) / p
        return [("PUNTS", fi(p)), ("YDS", fi(y)), ("AVG", f1(ratio(y, p))), ("NET", f1(net)),
                ("IN20", fi(gv("punts_inside_20"))),
                ("LONG", (fi(gv("long_punt")) if p else N_A) if ok("long_punt") else N_A), ("TB", fi(tb)),
                ("IN20%", f1(ratio(gv("punts_inside_20"), p, 100))), ("PUNTS/G", f1(ratio(p, n))),
                ("RET YDS ALLOWED", fi(ret))]
    if group == "LS":
        return [("GAMES", fi(n)), opt("LONG SNAPS", "long_snaps"), opt("ST SNAPS", "special_teams_snaps"),
                opt("ST TKL", "special_teams_tackles"), ("TKL", fi(gv("tackles"))), ("SOLO", fi(gv("solo_tackles"))),
                ("AST", fi(gv("assisted_tackles"))), ("FF", fi(gv("forced_fumbles"))),
                ("FR", fi(gv("fumble_recoveries"))), per_game("LONG SNAPS/G", "long_snaps")]
    # OL: games and the counters the records carry for linemen.
    return [("GAMES", fi(n)), opt("STARTS", "line_starts"), opt("OFF SNAPS", "offensive_snaps"),
            ("SACKS ALLOWED", fi(gv("sacks_allowed"))), opt("ST SNAPS", "special_teams_snaps"),
            ("FR", fi(gv("fumble_recoveries"))), ("TKL", fi(gv("tackles"))), ("FUM LOST", fi(gv("fumbles_lost"))),
            ("REC", fi(gv("receptions"))), per_game("OFF SNAPS/G", "offensive_snaps")]


def window_dates(club_games, year, gtype, rows):
    """The dates of his clubs' games that season while he was theirs, as far as the record shows:
    each club from his first game with it (the first club from the season's start) until his
    first game with the next club."""
    order = []
    for r in sorted(rows, key=lambda r: (r["date"], r["week"])):
        if not order or order[-1][0] != r["team"]:
            if r["team"] not in [c for c, _ in order]:
                order.append((r["team"], r["date"]))
    out = []
    for i, (club, start) in enumerate(order):
        end = order[i + 1][1] if i + 1 < len(order) else None
        out += [d for d in club_games.get((year, gtype, club), []) if (i == 0 or d >= start) and (end is None or d < end)]
    return sorted(out)


def window_games(club_games, year, gtype, rows):
    return len(window_dates(club_games, year, gtype, rows))


def available(rows, long_seen):
    """{field: recorded in every game of ``rows``} for the fields only later game records carry."""
    out = {}
    for f in FROM_KERNEL:
        out[f] = all(kernel_at_least(".".join(map(str, r["kernel"])), FROM_KERNEL[f]) for r in rows)
    for f in LONG_FIELDS:
        out[f] = all(f in long_seen.get(r["kernel"], set()) for r in rows)
    return out


def block(group, rows, dates, long_seen):
    """A season's (or a career's) record: games, his club's games while his, the tiles, the totals,
    which later-record fields every game carries, and the latest date covered."""
    if not rows:
        return None
    return {"games": len(rows), "club_games": len(dates), "tiles": tiles_for(group, rows, long_seen),
            "totals": total(rows), "available": available(rows, long_seen),
            "through": max(list(dates) + [r["date"] for r in rows])}


# ------------------------------------------------------------------ identity
class Identity:
    def __init__(self, root):
        root = Path(root)
        self.branch = _load(SeasonPaths(2014, root).record("league/personnel/branch_identity.json"))["by_player_id"]
        # The birth-date registry with the user's canon overrides (runtime/player_bios.py);
        # an override outranks every other source below.
        self.births = player_bios.load(root)
        self.canon = {n: r for n, r in self.births.items() if r.get("canon_override")}
        self.fixes = _load(root / BIRTH_DATE_CORRECTIONS)["players"]
        week1 = _load(root / "library/data/2014_week1_rosters_branch_adjusted.json")["clubs"]
        self.codes = {club: v.get("code") for club, v in week1.items()}
        self.codes.setdefault(JAX, JAX_CODE)
        self.week1_name, self.week1_gsis = {}, {}
        for club in sorted(week1):
            for p in week1[club]["players"]:
                rec = dict(p, club=club)
                self.week1_name.setdefault(p["player_id"], rec)
                if p.get("gsis_id"):
                    self.week1_gsis.setdefault(p["gsis_id"], rec)
        self.listed = _load(root / "library/data/2014_listed_player_identity.json")["players"]
        league = _load(SeasonPaths(2014, root).record("league/personnel/league_players.json"))["players"]
        self.college = {p["player_id"]: p["college"] for p in league if p.get("player_id") and p.get("college")}
        self.league_dob = {p["player_id"]: p["birth_date"] for p in league if p.get("player_id") and p.get("birth_date")}
        self.jax_dob = {}
        for row in SeasonPaths(2014, root).roster.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*([^|]+?)\s*\|\s*([A-Z]+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", row)
            if m:
                self.jax_dob.setdefault(m.group(1), m.group(3))

    def gsis(self, name, year):
        a = self.branch.get(name)
        b = (self.births.get(name) or {}).get("gsis_id")
        return (a or b) if year >= 2014 else (b or a)

    def week1_row(self, gsis, name):
        """His 2014 Week 1 roster row: by gsis, else by record name when that row is not another man's."""
        row = self.week1_gsis.get(gsis) if gsis else None
        if row is None:
            row = self.week1_name.get(name)
            if row is not None and not same_person(row.get("gsis_id"), gsis):
                row = None
        return row

    def birth_date(self, names, gsis, week1, latest):
        """Corrections first, then the registry, the 2014 Week 1 roster, the league player database
        and Jacksonville's roster. A name-keyed entry counts only when it names the same gsis id
        (two players can share a record name across seasons)."""
        for source in (self.canon, self.fixes, self.births):
            for name in sorted(names):
                entry = source.get(name) or {}
                if entry.get("birth_date") and same_person(entry.get("gsis_id"), gsis):
                    return entry["birth_date"]
        if week1 and week1.get("birth_date") and same_person(week1.get("gsis_id"), gsis):
            return week1["birth_date"]
        if gsis and self.league_dob.get(gsis):
            return self.league_dob[gsis]
        if latest in self.jax_dob and same_person(self.branch.get(latest), gsis):
            return self.jax_dob[latest]
        return None


def same_person(entry_gsis, gsis):
    """A name-keyed entry is his unless both ids are known and differ."""
    return not entry_gsis or not gsis or entry_gsis == gsis


def height_text(inches):
    return N_A if inches is None else "%d' %d\"" % (inches // 12, inches % 12)


# ------------------------------------------------------------------ awards
AWARD_KIND = {"offense": "Offensive", "defense": "Defensive", "special_teams": "Special Teams"}
AP_NAMES = {"MVP": "AP Most Valuable Player", "OPOY": "AP Offensive Player of the Year",
            "DPOY": "AP Defensive Player of the Year", "OROY": "AP Offensive Rookie of the Year",
            "DROY": "AP Defensive Rookie of the Year", "CPOY": "AP Comeback Player of the Year"}


def award_entries(root, years):
    """Every award decided on record, as dicts: the winner's record name and club, the season,
    the award text the player pages show, and where the decision is held (``decided``: the
    season, the results file in that season's awards data and the entry within it)."""
    out = []
    for year in years:
        folder = SeasonPaths(year, root).awards_data

        def entry(w, text, file, key, slot=None, role="winner"):
            decided = {"season": year, "file": file, "key": key}
            if slot is not None:
                decided["slot"] = slot
            if role != "winner":
                decided["role"] = role
            out.append({"player": w["player"], "team": w["team"], "season": year, "award": text,
                        "decided": decided})
        results = folder / "results.json"
        if results.exists():
            for rkey, e in _load(results).items():
                unit = "Week" if e["kind"] == "week" else "Month"
                when = "%d, Week %s" % (year, e["key"]) if unit == "Week" else "%d, %s" % (year, e["key"])
                for slot, a in sorted(e.get("awards", {}).items()):
                    if a.get("winner_index") is None:
                        continue
                    conf, kind = slot.split("-", 1)
                    entry(a["shortlist"][a["winner_index"]], "%s %s Player of the %s (%s)"
                          % (conf, AWARD_KIND.get(kind, kind), unit, when), "results.json", rkey, slot)
        honours = folder / "season_honours_results.json"
        if honours.exists():
            h = _load(honours)
            for code, a in h.get("ap_awards", {}).items():
                if code in AP_NAMES and a.get("winner_index") is not None:
                    entry(a["shortlist"][a["winner_index"]], "%s (%d)" % (AP_NAMES[code], year),
                          "season_honours_results.json", "ap_awards", code)
            for key, label in (("first", "AP First-Team All-Pro"), ("second", "AP Second-Team All-Pro")):
                for pos, lst in h.get("all_pro", {}).get(key, {}).items():
                    for w in lst:
                        entry(w, "%s (%d, %s)" % (label, year, pos), "season_honours_results.json",
                              "all_pro." + key, pos)
            for pos, lst in h.get("pro_bowl", {}).get("selections", {}).items():
                for w in lst:
                    entry(w, "Pro Bowl selection (%d, %s)" % (year, pos), "season_honours_results.json",
                          "pro_bowl.selections", pos)
                    rb = w.get("replaced_by")
                    if rb:
                        entry(rb, "Pro Bowl selection, replacement (%d, %s)" % (year, pos),
                              "season_honours_results.json", "pro_bowl.selections", pos, role="replacement")
        mvp = folder / "super_bowl_mvp.json"
        if mvp.exists():
            m = _load(mvp)
            if m.get("winner_index") is not None:
                entry(m["shortlist"][m["winner_index"]], "Super Bowl MVP (%d season)" % year,
                      "super_bowl_mvp.json", "winner")
    return out


def award_rows(root, years):
    """(record name, club, season, award text) for every award decided on record."""
    return [(e["player"], e["team"], e["season"], e["award"]) for e in award_entries(root, years)]


# ------------------------------------------------------------------ assemble
def opening_dates(root, years):
    """{season: the date of the league's first regular-season game}, from each season's schedule."""
    return {y: min(g["date"] for g in _load(SeasonPaths(y, root).schedule)["games"]) for y in years}


def age_on(birth_date, day):
    if not birth_date:
        return None
    b, t = dt.date.fromisoformat(birth_date), dt.date.fromisoformat(day)
    return t.year - b.year - ((t.month, t.day) < (b.month, b.day))


def season_number(year, club, p, listed, w1, codes):
    """The number a career table shows for one season row, for the club he ended that season
    with. 2014: the card's own number for his latest club (the rule below, Jacksonville's
    included); for another club, his 2014 Week 1 roster number with it (not a row a
    Jacksonville trade placed there) or his Weeks 1-4 listing with it. 2013: his 2013 season
    roster number (his latest 2013 week) when that row is with the same club; for Jacksonville
    that is the real 2013 Jaguars' listing, Jacksonville having recorded no numbers. Otherwise
    None (N/A): no number is inferred."""
    code = codes.get(club)
    if year == LISTING_SEASON:
        if club == p["team"]:
            return p["number"]
        if club == JAX:
            return None
        if (w1 and w1.get("club") == club and not w1.get("branch_note")
                and str(w1.get("jersey") or "").isdigit()):
            return int(w1["jersey"])
        if listed.get("number") is not None and (listed.get("number_basis") or {}).get("club") == code:
            return listed["number"]
        return None
    if year == LISTING_SEASON - 1:
        if listed.get("number_2013") is not None and (listed.get("number_2013_basis") or {}).get("club") == code:
            return listed["number_2013"]
    return None


def card_data(root=ROOT):
    """All players on record, their clubs, identity, blocks and awards."""
    root = Path(root)
    rec = collect(root)
    games, long_seen, club_games = rec["games"], rec["long_seen"], rec["club_games"]
    ident = Identity(root)
    current_jax = jacksonville_current(root, ident)
    years = record_years(root)
    openings = opening_dates(root, years)
    as_of = max(r["date"] for r in games)
    for r in games:
        r["key"] = ident.gsis(r["pid"], r["year"]) or "%s-%s" % (slugify(display(r["pid"])), GROUP_OF.get(r["pos"], "x"))
    by_player = {}
    for r in games:
        by_player.setdefault(r["key"], []).append(r)
    name_team_key, name_keys = {}, {}
    for r in games:
        name_team_key.setdefault((r["pid"], r["team"], r["year"]), r["key"])
        name_keys.setdefault(r["pid"], set()).add(r["key"])
    awards, unmatched = {}, []
    for name, team, year, text in award_rows(root, years):
        k = name_team_key.get((name, team, year))
        if k is None and len(name_keys.get(name, ())) == 1:
            k = next(iter(name_keys[name]))
        if k is None:
            unmatched.append("%s (%s, %d): %s" % (name, team, year, text))
        else:
            awards.setdefault(k, []).append(text)
    players = []
    for key in sorted(by_player):
        rows = sorted(by_player[key], key=lambda r: (r["date"], r["week"]))
        last = rows[-1]
        pos = last["pos"]
        group = GROUP_OF.get(pos, "OL")
        gsis = ident.gsis(last["pid"], last["year"])
        listed = ident.listed.get(gsis, {}) if gsis else {}
        number, number_note = None, None
        w1 = ident.week1_row(gsis, last["pid"])
        current = is_current_jaguar(current_jax, gsis, {r["pid"] for r in rows})
        if last["team"] != JAX:
            # A Week 1 row placed with a club by a Jacksonville trade carries his real club's number.
            if (w1 and w1.get("club") == last["team"] and not w1.get("branch_note")
                    and str(w1.get("jersey") or "").isdigit()):
                number, number_note = int(w1["jersey"]), "2014 Week 1 roster"
            elif listed.get("number") is not None and (listed.get("number_basis") or {}).get("club") == ident.codes.get(last["team"]):
                number = listed["number"]
                number_note = "2014 Week %d roster listing" % listed["number_basis"]["week"]
        elif not current:
            pass  # a former Jaguar: Jacksonville has not recorded his number
        elif listed.get("jaguars_number") is not None:
            number, number_note = listed["jaguars_number"], "jaguars"
        elif listed.get("number") is not None:
            number, number_note = listed["number"], "other:" + listed["number_basis"]["club"]
        dob = ident.birth_date({r["pid"] for r in rows}, gsis, w1, last["pid"])
        college = ident.college.get(gsis) if gsis else None
        college = college or listed.get("college")
        seasons, career_rows, career_dates = {}, {"regular": [], "playoffs": []}, {"regular": [], "playoffs": []}
        for year in years:
            yr = [r for r in rows if r["year"] == year]
            if not yr:
                continue
            s = {"clubs": [], "age": age_on(dob, openings[year])}
            for r in yr:
                if r["team"] not in s["clubs"]:
                    s["clubs"].append(r["team"])
            for gtype in ("regular", "playoffs"):
                gr = [r for r in yr if r["type"] == gtype]
                dates = window_dates(club_games, year, gtype, gr) if gr else []
                s[gtype] = block(group, gr, dates, long_seen)
                career_rows[gtype].extend(gr)
                career_dates[gtype] += dates
            seasons[year] = s
        career = {g: block(group, career_rows[g], career_dates[g], long_seen) for g in ("regular", "playoffs")}
        through = max(b["through"] for b in career.values() if b)
        age = None
        if dob:
            b, t = dt.date.fromisoformat(dob), dt.date.fromisoformat(through)
            age = t.year - b.year - ((t.month, t.day) < (b.month, b.day))
        players.append({
            "key": key, "gsis": gsis, "name": display(last["pid"]), "record_names": sorted({r["pid"] for r in rows}),
            "team": last["team"], "pos": pos, "group": group, "number": number, "number_note": number_note,
            "height_in": listed.get("height_in"), "weight": listed.get("weight"), "listing": listed.get("listing"),
            "birth_date": dob, "age": age, "college": college, "seasons": seasons, "career": career,
            "through": through, "current_jaguar": current, "awards": awards.get(key, []),
            "_listed": listed, "_w1": w1,
        })
    # Jacksonville numbers, for players Jacksonville currently controls (active roster, reserve and
    # practice squad): his real 2014 Jaguars number; else the number he wore in 2014 with his real
    # club when no other current Jaguar holds or claims it; else none. A former Jaguar shows none.
    # Jacksonville has not recorded jersey numbers of its own.
    claims = {}
    for p in players:
        if p["team"] == JAX and p["current_jaguar"] and p["number"] is not None:
            claims.setdefault(p["number"], []).append(p)
    for number, ps in claims.items():
        for p in ps:
            if p["number_note"].startswith("other:") and len(ps) > 1:
                p["number"], p["number_note"] = None, None
    # His listing and Week 1 row stay on the record (``_listed``, ``_w1``) so a season's number for
    # another club than the one he ended it with (jacksonville_rows) comes from season_number too.
    for p in players:
        for year, s in p["seasons"].items():
            s["number"] = season_number(year, s["clubs"][-1], p, p["_listed"], p["_w1"], ident.codes)
    club_of_code = {code: club for club, code in ident.codes.items()}
    for p in players:
        note = p["number_note"]
        if note == "jaguars":
            p["number_note"] = "his 2014 Jaguars roster listing"
        elif note and note.startswith("other:"):
            code = note.split(":", 1)[1]
            p["number_note"] = ("the number he wore in 2014 with the %s (Jacksonville has not recorded one)"
                                % club_of_code.get(code, code))
    return {"as_of": as_of, "years": years, "players": players, "unmatched_awards": unmatched}


def jacksonville_current(root, ident):
    """(gsis ids, names without one) of the players Jacksonville controls now: every roster table
    row whose status shows club control, practice squad included (the weekly input gate's rule)."""
    from scripts.check_week_input_exclusivity import controlled_players_from_roster
    active = _load(Path(root) / "docs/repository_map.json")["active_season"]
    names = controlled_players_from_roster(SeasonPaths(active, root).roster)
    ids = {ident.branch[n] for n in names if ident.branch.get(n)}
    return ids, {n for n in names if not ident.branch.get(n)}


def is_current_jaguar(current, gsis, record_names):
    ids, unkeyed = current
    return bool(gsis and gsis in ids) or bool(unkeyed & set(record_names))


# ------------------------------------------------------------------ layout
def club_slug(team):
    return slugify(team)


def assign_slugs(players):
    """A unique file name per club folder: the player's slug, widened by group then id on a clash."""
    by_club = {}
    for p in players:
        by_club.setdefault(p["team"], []).append(p)
    for club, ps in by_club.items():
        base = {}
        for p in ps:
            base.setdefault(slugify(p["name"]), []).append(p)
        for slug, same in base.items():
            if len(same) == 1:
                same[0]["slug"] = slug
                continue
            wide = {}
            for p in same:
                wide.setdefault("%s_%s" % (slug, p["group"].lower()), []).append(p)
            for s2, same2 in wide.items():
                for p in same2:
                    p["slug"] = s2 if len(same2) == 1 else "%s_%s" % (s2, slugify(p["key"]))


# The career-card block markers of the working cards before rebuild step 3a; the built player
# pages carry none (scripts/player_photos.place_block still recognises one on a legacy card).
CARD_BEGIN, CARD_END = "<!-- player-card:begin -->", "<!-- player-card:end -->"


def season_open(root):
    """Whether the active season is still open: not yet closed by its season review
    (scripts/build_annual_player_sheets.season_is_complete)."""
    from scripts.build_annual_player_sheets import season_is_complete
    active = _load(Path(root) / "docs/repository_map.json")["active_season"]
    return not season_is_complete(active, Path(root))


def jacksonville_profiles(root):
    """Current Jacksonville-controlled players' working card paths, by name: every roster table row
    whose status shows club control, practice squad included (jacksonville_current's rule, the one
    the league card's current_jaguar follows)."""
    from scripts.check_week_input_exclusivity import controlled_players_from_roster
    active = _load(Path(root) / "docs/repository_map.json")["active_season"]
    paths = SeasonPaths(active, root)
    folder = paths.record("player_profiles")
    out = {}
    for name in sorted(controlled_players_from_roster(paths.roster)):
        path = folder / (slugify(name) + ".md")
        if path.is_file():
            out[name] = path
    return out


def profile_for(p, profiles, branch):
    """His Jacksonville working card: the roster name's gsis id must be his. A roster name with no
    id matches only an exact record name of a player whose latest game was with Jacksonville."""
    for name in sorted(profiles):
        gsis = branch.get(name)
        if gsis and p["gsis"]:
            if gsis == p["gsis"]:
                return profiles[name]
        elif name in p["record_names"] and p["team"] == JAX:
            return profiles[name]
    return None


def page_players(players, profiles, branch):
    """{page path: league player} for the named pages (``profiles``, by name), by profile_for."""
    out = {}
    for p in players:
        page = profile_for(p, profiles, branch)
        if page is None:
            continue
        if page in out:
            raise ValueError("two league players match the player page %s" % page)
        out[page] = p
    return out


# ------------------------------------------------------------------ Jacksonville player card season rows
# The regular-season and playoff tables at the bottom of each Jacksonville player card
# (scripts/update_player_cards.py) count Jacksonville's games only, so their season row leads with
# the Jacksonville Jaguars, his age on the league's opening game of that season and #. Jacksonville
# has recorded no jersey numbers of its own: # is the number his league card shows while he is a
# current Jaguar whose latest game was with Jacksonville (his real 2014 Jaguars listing, else his
# real 2014 number with his real club when no other current Jaguar claims it; the league page
# names which), and N/A for a player with no game on record, one whose latest game was with
# another club, or a former player. update_player_cards works the row out only for a current
# player while the season is open; once he has left or the season has closed, the row keeps the
# cells already written.
def jacksonville_rows(year, names, root=ROOT, data=None):
    """{card name: (team, age, number)} for the ``year`` row of each named Jacksonville player card,
    from the current state; None is N/A. A card is his league player's by the reverse link's own
    rule (profile_for): the current roster's cards exactly as their career card blocks are matched
    (page_players over jacksonville_profiles), then each other named card (a former player's) among
    the remaining players. Age is age_on his league card's birth date at the season's opening game
    (opening_dates); # is season_number for Jacksonville that season, so a current player's card
    and his league page cannot disagree. A card with no league player (no game on record) takes its
    age from the same birth-date sources (Identity.birth_date) and has no number."""
    root = Path(root)
    data = card_data(root) if data is None else data
    players = data["players"]
    ident = Identity(root)
    schedule = SeasonPaths(year, root).schedule
    opening = opening_dates(root, (year,))[year] if schedule.is_file() else None
    names = sorted(set(names))
    profiles = jacksonville_profiles(root)
    by_page = page_players(players, profiles, ident.branch)
    found = {name: by_page[page] for name, page in profiles.items() if page in by_page and name in names}
    taken = {id(p) for p in by_page.values()}
    others = {name: name for name in names if name not in profiles}
    found.update(page_players([p for p in players if id(p) not in taken], others, ident.branch))
    out = {}
    for name in names:
        p = found.get(name)
        if p is not None:
            dob = p["birth_date"]
            number = season_number(year, JAX, p, p["_listed"], p["_w1"], ident.codes)
        else:
            gsis = ident.gsis(name, year)
            dob, number = ident.birth_date({name}, gsis, ident.week1_row(gsis, name), name), None
        out[name] = (JAX, age_on(dob, opening) if opening else None, number)
    return out
