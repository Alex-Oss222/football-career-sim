"""League player cards: a simple card and career statistics for every player on record.

``scripts/render_player_cards.py`` writes ``career/league_players/`` from this
module after every closed game:

- ``README.md``: the 32 clubs by conference and division;
- ``<club>/README.md``: the players whose latest game on record was with that
  club, by position group;
- ``<club>/<player>.md``: his card image, his regular-season and playoff
  statistics by season with a career row, and his awards on record;
- ``<club>/assets/<player>.svg``: the card (header with listed identity, then
  latest-season and career blocks for playoffs and regular season).

Every statistic is arithmetic on the committed game records (the receipts the
statbook reads), with the repository's own field names, loaders and passer
rating; totals equal ``runtime.statbook.aggregate_receipts``. A value the
records do not carry is "N/A", never 0 or an estimate. Identity comes from
committed sources only: the 2014 identity map and birth-date registry, the
2014 Week 1 rosters, the league player database and the listed 2014 identity
(``library/data/2014_listed_player_identity.json``). This is a reader view: no
game, evaluation or decision reads it.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import unicodedata
from html import escape
from pathlib import Path

from runtime import postseason as post_mod
from runtime.league import DIVISIONS, DIVISION_OF
from runtime.play_detail import DRIVE_SUMMARY_FIELDS
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
# Club colours, 2014 names (primary, secondary), from the user's colour file.
COLORS = {
    "Buffalo Bills": ("#00338D", "#C60C30"), "Miami Dolphins": ("#008E97", "#FC4C02"),
    "New England Patriots": ("#002244", "#C60C30"), "New York Jets": ("#003F2D", "#FFFFFF"),
    "Baltimore Ravens": ("#241773", "#9E7C0C"), "Cincinnati Bengals": ("#FB4F14", "#000000"),
    "Cleveland Browns": ("#311D00", "#FF3C00"), "Pittsburgh Steelers": ("#101820", "#FFB612"),
    "Houston Texans": ("#03202F", "#A71930"), "Indianapolis Colts": ("#002C5F", "#A2AAAD"),
    "Jacksonville Jaguars": ("#006778", "#D7A22A"), "Tennessee Titans": ("#0C2340", "#4B92DB"),
    "Denver Broncos": ("#FB4F14", "#002244"), "Kansas City Chiefs": ("#E31837", "#FFB81C"),
    "Oakland Raiders": ("#000000", "#A5ACAF"), "San Diego Chargers": ("#002A5E", "#FFC20E"),
    "Dallas Cowboys": ("#041E42", "#869397"), "New York Giants": ("#0B2265", "#A71930"),
    "Philadelphia Eagles": ("#004C54", "#A5ACAF"), "Washington Redskins": ("#5A1414", "#FFB612"),
    "Chicago Bears": ("#0B162A", "#C83803"), "Detroit Lions": ("#0076B6", "#B0B7BC"),
    "Green Bay Packers": ("#203731", "#FFB612"), "Minnesota Vikings": ("#4F2683", "#FFC62F"),
    "Atlanta Falcons": ("#A71930", "#000000"), "Carolina Panthers": ("#0085CA", "#101820"),
    "New Orleans Saints": ("#101820", "#D3BC8D"), "Tampa Bay Buccaneers": ("#D50A0A", "#34302B"),
    "Arizona Cardinals": ("#97233F", "#FFB612"), "St. Louis Rams": ("#002244", "#B3995D"),
    "San Francisco 49ers": ("#AA0000", "#B3995D"), "Seattle Seahawks": ("#002244", "#69BE28"),
}
WHITE, INK = "#FFFFFF", "#101418"
SURFACE, SURFACE_TILE, PAGE = "#1B1E23", "#272B32", "#111317"


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


# ------------------------------------------------------------------ colours
def _lum(hex_color):
    def chan(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    h = hex_color.lstrip("#")
    r, g, b = (chan(h[i:i + 2]) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def text_on(background):
    """White or near-black, whichever reads better on the background."""
    return WHITE if contrast(WHITE, background) >= contrast(INK, background) else INK


def mix(a, b, share):
    """a blended over b at ``share`` (an opaque colour, so tiles have no seams)."""
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#%02X%02X%02X" % tuple(round(int(a[i:i + 2], 16) * share + int(b[i:i + 2], 16) * (1 - share))
                                   for i in (0, 2, 4))


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


def window_games(club_games, year, gtype, rows):
    """His clubs' games that season while he was theirs, as far as the record shows: each club
    from his first game with it (the first club from the season's start) until his first game
    with the next club."""
    order = []
    for r in sorted(rows, key=lambda r: (r["date"], r["week"])):
        if not order or order[-1][0] != r["team"]:
            if r["team"] not in [c for c, _ in order]:
                order.append((r["team"], r["date"]))
    count = 0
    for i, (club, start) in enumerate(order):
        end = order[i + 1][1] if i + 1 < len(order) else None
        dates = club_games.get((year, gtype, club), [])
        count += sum(1 for d in dates if (i == 0 or d >= start) and (end is None or d < end))
    return count


def block(group, rows, club_count, long_seen):
    if not rows:
        return None
    return {"games": len(rows), "club_games": club_count, "tiles": tiles_for(group, rows, long_seen)}


# ------------------------------------------------------------------ identity
class Identity:
    def __init__(self, root):
        root = Path(root)
        self.branch = _load(SeasonPaths(2014, root).record("league/personnel/branch_identity.json"))["by_player_id"]
        self.births = _load(root / "library/data/player_birth_dates.json")["players"]
        self.fixes = _load(root / "library/data/player_birth_date_corrections.json")["players"]
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
        self.college = {p["player_id"]: p["college"]
                        for p in _load(SeasonPaths(2014, root).record("league/personnel/league_players.json"))["players"]
                        if p.get("player_id") and p.get("college")}
        self.jax_dob = {}
        for row in SeasonPaths(2014, root).roster.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*([^|]+?)\s*\|\s*([A-Z]+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", row)
            if m:
                self.jax_dob.setdefault(m.group(1), m.group(3))

    def gsis(self, name, year):
        a = self.branch.get(name)
        b = (self.births.get(name) or {}).get("gsis_id")
        return (a or b) if year >= 2014 else (b or a)

    def birth_date(self, names, week1, latest):
        """Corrections first, then the registry, the 2014 Week 1 roster and Jacksonville's roster."""
        for name in sorted(names):
            if (self.fixes.get(name) or {}).get("birth_date"):
                return self.fixes[name]["birth_date"]
        for name in sorted(names):
            if (self.births.get(name) or {}).get("birth_date"):
                return self.births[name]["birth_date"]
        if week1 and week1.get("birth_date"):
            return week1["birth_date"]
        return self.jax_dob.get(latest)


def height_text(inches):
    return N_A if inches is None else "%d' %d\"" % (inches // 12, inches % 12)


# ------------------------------------------------------------------ awards
AWARD_KIND = {"offense": "Offensive", "defense": "Defensive", "special_teams": "Special Teams"}
AP_NAMES = {"MVP": "AP Most Valuable Player", "OPOY": "AP Offensive Player of the Year",
            "DPOY": "AP Defensive Player of the Year", "OROY": "AP Offensive Rookie of the Year",
            "DROY": "AP Defensive Rookie of the Year", "CPOY": "AP Comeback Player of the Year"}


def award_rows(root, years):
    """(record name, club, season, award text) for every award decided on record."""
    out = []
    for year in years:
        folder = SeasonPaths(year, root).awards
        results = folder / "results.json"
        if results.exists():
            for entry in _load(results).values():
                unit = "Week" if entry["kind"] == "week" else "Month"
                when = "%d, Week %s" % (year, entry["key"]) if unit == "Week" else "%d, %s" % (year, entry["key"])
                for slot, a in sorted(entry.get("awards", {}).items()):
                    if a.get("winner_index") is None:
                        continue
                    conf, kind = slot.split("-", 1)
                    w = a["shortlist"][a["winner_index"]]
                    out.append((w["player"], w["team"], year, "%s %s Player of the %s (%s)"
                                % (conf, AWARD_KIND.get(kind, kind), unit, when)))
        honours = folder / "season_honours_results.json"
        if honours.exists():
            h = _load(honours)
            for code, a in h.get("ap_awards", {}).items():
                if code in AP_NAMES and a.get("winner_index") is not None:
                    w = a["shortlist"][a["winner_index"]]
                    out.append((w["player"], w["team"], year, "%s (%d)" % (AP_NAMES[code], year)))
            for key, label in (("first", "AP First-Team All-Pro"), ("second", "AP Second-Team All-Pro")):
                for pos, lst in h.get("all_pro", {}).get(key, {}).items():
                    for w in lst:
                        out.append((w["player"], w["team"], year, "%s (%d, %s)" % (label, year, pos)))
            for pos, lst in h.get("pro_bowl", {}).get("selections", {}).items():
                for w in lst:
                    out.append((w["player"], w["team"], year, "Pro Bowl selection (%d, %s)" % (year, pos)))
                    rb = w.get("replaced_by")
                    if rb:
                        out.append((rb["player"], rb["team"], year,
                                    "Pro Bowl selection, replacement (%d, %s)" % (year, pos)))
        mvp = folder / "super_bowl_mvp.json"
        if mvp.exists():
            s = _load(mvp)
            if s.get("winner_index") is not None:
                w = s["shortlist"][s["winner_index"]]
                out.append((w["player"], w["team"], year, "Super Bowl MVP (%d season)" % year))
    return out


# ------------------------------------------------------------------ assemble
def card_data(root=ROOT):
    """All players on record, their clubs, identity, blocks and awards."""
    root = Path(root)
    rec = collect(root)
    games, long_seen, club_games = rec["games"], rec["long_seen"], rec["club_games"]
    ident = Identity(root)
    years = record_years(root)
    as_of = max(r["date"] for r in games)
    as_of_date = dt.date.fromisoformat(as_of)
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
        w1 = (ident.week1_gsis.get(gsis) if gsis else None) or ident.week1_name.get(last["pid"])
        if last["team"] != JAX:
            if w1 and w1.get("club") == last["team"] and str(w1.get("jersey") or "").isdigit():
                number, number_note = int(w1["jersey"]), "2014 Week 1 roster"
            elif listed.get("number") is not None and (listed.get("number_basis") or {}).get("club") == ident.codes.get(last["team"]):
                number = listed["number"]
                number_note = "2014 Week %d roster listing" % listed["number_basis"]["week"]
        elif listed.get("jaguars_number") is not None:
            number, number_note = listed["jaguars_number"], "jaguars"
        elif listed.get("number") is not None:
            number, number_note = listed["number"], "other:" + listed["number_basis"]["club"]
        dob = ident.birth_date({r["pid"] for r in rows}, w1, last["pid"])
        age = None
        if dob:
            b = dt.date.fromisoformat(dob)
            age = as_of_date.year - b.year - ((as_of_date.month, as_of_date.day) < (b.month, b.day))
        college = ident.college.get(gsis) if gsis else None
        college = college or listed.get("college")
        seasons, career_rows, career_clubs = {}, {"regular": [], "playoffs": []}, {"regular": 0, "playoffs": 0}
        for year in years:
            yr = [r for r in rows if r["year"] == year]
            if not yr:
                continue
            s = {"clubs": []}
            for r in yr:
                if r["team"] not in s["clubs"]:
                    s["clubs"].append(r["team"])
            for gtype in ("regular", "playoffs"):
                gr = [r for r in yr if r["type"] == gtype]
                cg = window_games(club_games, year, gtype, gr) if gr else 0
                s[gtype] = block(group, gr, cg, long_seen)
                career_rows[gtype].extend(gr)
                career_clubs[gtype] += cg
            seasons[year] = s
        players.append({
            "key": key, "gsis": gsis, "name": display(last["pid"]), "record_names": sorted({r["pid"] for r in rows}),
            "team": last["team"], "pos": pos, "group": group, "number": number, "number_note": number_note,
            "height_in": listed.get("height_in"), "weight": listed.get("weight"), "listing": listed.get("listing"),
            "birth_date": dob, "age": age, "college": college, "seasons": seasons,
            "career": {g: block(group, career_rows[g], career_clubs[g], long_seen) for g in ("regular", "playoffs")},
            "awards": awards.get(key, []),
        })
    # Jacksonville numbers: his real 2014 Jaguars number; else the number he wore in 2014 with his
    # real club when no other current Jaguar holds or claims it; else none (Jacksonville has not
    # recorded jersey numbers of its own).
    claims = {}
    for p in players:
        if p["team"] == JAX and p["number"] is not None:
            claims.setdefault(p["number"], []).append(p)
    for number, ps in claims.items():
        for p in ps:
            if p["number_note"].startswith("other:") and len(ps) > 1:
                p["number"], p["number_note"] = None, None
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


# ------------------------------------------------------------------ SVG card
W, H = 1280, 888
BW, BH = 610, 276
FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'


def _x(s):
    return escape(str(s), quote=False)


def _fit(text, base, width, em=0.6):
    return min(base, int(width / (em * max(len(text), 1))))


def _block_svg(x, y, title, b, empty, on_primary, colors):
    primary, secondary, ink = colors
    fill = primary if on_primary else SURFACE
    tile = mix(ink, primary, 0.14) if on_primary else SURFACE_TILE
    out = ['<g transform="translate(%d %d)" class="%s">' % (x, y, "p" if on_primary else "c"),
           '<rect width="%d" height="%d" rx="22" fill="%s"/>' % (BW, BH, fill)]
    if not on_primary:
        accent = secondary if contrast(secondary, SURFACE) >= 1.6 else primary
        out.append('<rect x="22" width="%d" height="4" fill="%s"/>' % (BW - 44, accent))
    out.append('<text x="24" y="42" class="bt">%s</text>' % _x(title.upper()))
    if b is None:
        out.append('<text x="%d" y="156" class="m">%s</text></g>' % (BW // 2, _x(empty)))
        return "".join(out)
    out.append('<text x="586" y="42" class="g">%d G</text>' % b["games"])
    out.append('<path d="M24 58H586" class="d"/>')
    tw, gap, th = 104, 10, 80
    path, texts = [], []
    for i, (label, value) in enumerate(b["tiles"]):
        tx, ty = 25 + (i % 5) * (tw + gap), 72 + (i // 5) * (th + 10)
        path.append("M%d %dh%dv%dh-%dz" % (tx + 4, ty + 4, tw - 8, th - 8, tw - 8))
        cx = tx + tw // 2
        vs, ls = _fit(value, 28, 96, 0.6), _fit(label, 12, 96, 0.66)
        texts.append('<text x="%d" y="%d" class="v"%s>%s</text>' % (
            cx, ty + 44, "" if vs == 28 else ' style="font-size:%dpx"' % vs, _x(value)))
        texts.append('<text x="%d" y="%d" class="l"%s>%s</text>' % (
            cx, ty + 66, "" if ls == 12 else ' style="font-size:%dpx"' % ls, _x(label)))
    out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="8" stroke-linejoin="round"/>'
               % ("".join(path), tile, tile))
    out.extend(texts)
    out.append('<text x="24" y="%d" class="f">%d of %d games on record</text></g>'
               % (BH - 12, b["games"], b["club_games"]))
    return "".join(out)


def card_svg(p, as_of):
    primary, secondary = COLORS[p["team"]]
    ink = text_on(primary)
    colors = (primary, secondary, ink)
    latest = max(p["seasons"])
    s = p["seasons"][latest]
    name = p["name"]
    name_size = 50 if len(name) <= 24 else (42 if len(name) <= 30 else 34)
    college = p["college"] or N_A
    if len(college) > 40:
        college = college[:39].rstrip() + "..."
    born = long_date(p["birth_date"]) if p["birth_date"] else N_A
    ident = [("NO.", "#%d" % p["number"] if p["number"] is not None else N_A, 52),
             ("HEIGHT", height_text(p["height_in"]), 150),
             ("WEIGHT", "%d lb" % p["weight"] if p["weight"] is not None else N_A, 270),
             ("BORN", born, 390), ("AGE", str(p["age"]) if p["age"] is not None else N_A, 640),
             ("COLLEGE", college, 730)]
    style = ("text{font-family:%s;fill:#FFF}.h text,.p text{fill:%s}.e{font-size:15px;font-weight:700;"
             "letter-spacing:2px;opacity:.8}.n{font-weight:700}.s{font-size:22px;font-weight:600}"
             ".k{font-size:13px;font-weight:700;letter-spacing:1.5px;opacity:.75}.i{font-size:22px;font-weight:600}"
             ".r{text-anchor:end}.bt{font-size:22px;font-weight:700;letter-spacing:.5px}.g{font-size:20px;"
             "font-weight:700;text-anchor:end}.v{font-size:28px;font-weight:700;text-anchor:middle}"
             ".l{font-size:12px;font-weight:700;text-anchor:middle;opacity:.8}.f{font-size:14px;opacity:.75}"
             ".m{font-size:18px;text-anchor:middle;opacity:.8}.d{stroke:%s;stroke-opacity:.2}"
             ".c .d{stroke:#FFF}.x{font-size:14px;fill:#9BA1AA}" % (FONT, ink, ink))
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" '
           'aria-labelledby="t">' % (W, H, W, H),
           '<title id="t">%s career card</title>' % _x(name),
           "<style>%s</style>" % style,
           '<rect width="%d" height="%d" rx="28" fill="%s"/>' % (W, H, PAGE),
           '<path d="M20 44a24 24 0 0 1 24-24h1192a24 24 0 0 1 24 24v200H20z" fill="%s"/>' % primary,
           '<rect x="20" y="244" width="1240" height="8" fill="%s"/>' % secondary,
           '<g class="h">',
           '<text x="52" y="64" class="e">PLAYER CAREER</text>',
           '<text x="52" y="120" class="n" style="font-size:%dpx">%s</text>' % (name_size, _x(name)),
           '<text x="52" y="156" class="s">%s · NFL · %s</text>' % (_x(p["team"]), _x(p["pos"] or N_A)),
           '<text x="1228" y="64" class="e r">RECORD THROUGH</text>',
           '<text x="1228" y="100" class="r n" style="font-size:28px">%s</text>' % _x(long_date(as_of)),
           '<path d="M52 176H1228" class="d"/>']
    for label, value, x in ident:
        out.append('<text x="%d" y="202" class="k">%s</text><text x="%d" y="230" class="i">%s</text>'
                   % (x, label, x, _x(value)))
    out.append("</g>")
    out.append(_block_svg(20, 272, "%d playoffs" % latest, s["playoffs"], "No playoff games in %d" % latest,
                          True, colors))
    out.append(_block_svg(650, 272, "Career playoffs", p["career"]["playoffs"], "No playoff games on record",
                          False, colors))
    out.append(_block_svg(20, 568, "%d regular season" % latest, s["regular"],
                          "No regular-season games in %d" % latest, True, colors))
    out.append(_block_svg(650, 568, "Career regular season", p["career"]["regular"],
                          "No regular-season games on record", False, colors))
    out.append('<text x="32" y="872" class="x">Regular season and playoffs are separate records. '
               'N/A: not on record.</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ Markdown
def _cell(v):
    return str(v).replace("|", "\\|")


def stat_table(p, gtype):
    """Rows by season (his club or clubs that season) and a career row."""
    rows = [(year, s) for year, s in sorted(p["seasons"].items()) if s[gtype]]
    if not rows:
        return None
    labels = [label for label, _ in p["career"][gtype]["tiles"] if label != "GAMES"]
    head = ["Season", "Club", "G"] + labels
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(["---", "---"] + ["---:"] * (len(head) - 2)) + "|"]

    def values(b):
        tiles = dict(b["tiles"])
        return [tiles.get(label, N_A) for label in labels]
    for year, s in rows:
        lines.append("| " + " | ".join(_cell(v) for v in [year, ", ".join(s["clubs"]), b_games(s[gtype])]
                                       + values(s[gtype])) + " |")
    c = p["career"][gtype]
    lines.append("| " + " | ".join(_cell(v) for v in ["**Career**", "", c["games"]] + values(c)) + " |")
    return "\n".join(lines)


def b_games(b):
    return b["games"] if b else 0


def player_page(p, as_of, profile_link):
    lines = ["# %s" % p["name"], "",
             "![%s career card](assets/%s.svg)" % (p["name"], p["slug"]), "",
             "## Career stats", "", "### Regular season", ""]
    reg = stat_table(p, "regular")
    lines += [reg if reg else "No regular-season games on record.", "", "### Playoffs", ""]
    post = stat_table(p, "playoffs")
    lines += [post if post else "No playoff games on record.", "", "## Awards", ""]
    lines += (["- %s" % a for a in p["awards"]] if p["awards"] else ["None on record."])
    lines.append("")
    if profile_link:
        lines += ["[Jacksonville player card](%s)" % profile_link, ""]
    if p["listing"] == "weeks_1_4":
        basis = "listed 2014 roster data, Weeks 1-4"
    elif p["listing"] == "player_file":
        basis = "the public player file's latest listing (no 2014 Weeks 1-4 roster row)"
    else:
        basis = "no listing on record"
    number = "; number: %s" % p["number_note"] if p["number"] is not None and p["number_note"] else ""
    lines.append("Records through %s. Identity: %s%s. [All %s players](README.md)."
                 % (long_date(as_of), basis, number, p["team"]))
    return "\n".join(lines) + "\n"


def club_page(team, players, years, as_of):
    lines = ["# %s players" % team, "",
             "%s · Players whose latest game on record was with the %s. G counts regular-season games with any "
             "club. Records through %s. [All clubs](../README.md)." % (DIVISION_OF[team], team, long_date(as_of)), ""]
    cols = ["%d G" % y for y in sorted(years, reverse=True)]
    for group, heading in GROUPS:
        ps = sorted((p for p in players if p["group"] == group), key=lambda p: (p["name"], p["slug"]))
        if not ps:
            continue
        lines += ["## %s" % heading, "", "| # | Player | Pos | " + " | ".join(cols) + " |",
                  "|---:|---|---|" + "|".join("---:" for _ in cols) + "|"]
        for p in ps:
            games = [b_games((p["seasons"].get(y) or {}).get("regular")) for y in sorted(years, reverse=True)]
            lines.append("| %s | [%s](%s.md) | %s | %s |" % (
                p["number"] if p["number"] is not None else N_A, _cell(p["name"]), p["slug"], p["pos"] or N_A,
                " | ".join(str(g) for g in games)))
        lines.append("")
    return "\n".join(lines)


def index_page(counts, years, as_of):
    lines = ["# League players", "",
             "Every player in the %s game records, under the club of his latest game on record. Each player page "
             "has his career card, his regular-season and playoff statistics by season and his awards." % (
                 " and ".join(str(y) for y in years)), ""]
    for conf in ("AFC", "NFC"):
        lines += ["## %s" % conf, ""]
        for division, teams in DIVISIONS.items():
            if not division.startswith(conf):
                continue
            lines += ["### %s" % division, ""]
            lines += ["- [%s](%s/README.md) (%d players)" % (t, club_slug(t), counts.get(t, 0)) for t in teams]
            lines.append("")
    lines.append("Generated by scripts/render_player_cards.py after every closed game; record through %s."
                 % long_date(as_of))
    return "\n".join(lines) + "\n"


def jacksonville_profiles(root):
    """Current Jacksonville-controlled players' working card paths, by name."""
    from scripts.build_player_progression_roster import parse_current_roster
    active = _load(root / "docs/repository_map.json")["active_season"]
    paths = SeasonPaths(active, root)
    folder = paths.record("player_profiles")
    _, _, roster = parse_current_roster(paths.roster)
    out = {}
    for r in roster:
        path = folder / (slugify(r.player) + ".md")
        if path.is_file():
            out[r.player] = path
    return out


def render(root=ROOT):
    """{path relative to the repository root: text} for the whole folder."""
    root = Path(root)
    data = card_data(root)
    if data["unmatched_awards"]:
        raise ValueError("awards with no player on record: " + "; ".join(data["unmatched_awards"][:5]))
    players, as_of, years = data["players"], data["as_of"], data["years"]
    unknown = sorted({p["team"] for p in players} - set(COLORS))
    if unknown:
        raise ValueError("no club colours for: " + ", ".join(unknown))
    assign_slugs(players)
    profiles = jacksonville_profiles(root)
    files = {}
    by_club = {}
    for p in players:
        by_club.setdefault(p["team"], []).append(p)
        base = "%s/%s" % (FOLDER, club_slug(p["team"]))
        link = None
        prof = next((profiles[n] for n in [p["name"]] + p["record_names"] if n in profiles), None)
        if prof is not None:
            link = Path(os.path.relpath(prof, root / base)).as_posix()
        files["%s/%s.md" % (base, p["slug"])] = player_page(p, as_of, link)
        files["%s/assets/%s.svg" % (base, p["slug"])] = card_svg(p, as_of)
    for team, ps in by_club.items():
        files["%s/%s/README.md" % (FOLDER, club_slug(team))] = club_page(team, ps, years, as_of)
    files["%s/README.md" % FOLDER] = index_page({t: len(ps) for t, ps in by_club.items()}, years, as_of)
    return dict(sorted(files.items()))


def check(root=ROOT, expected=None):
    root = Path(root)
    expected = render(root) if expected is None else expected
    errors = []
    for rel, text in expected.items():
        path = root / rel
        if not path.is_file():
            errors.append("League player cards missing: %s" % rel)
        elif path.read_bytes() != text.encode("utf-8"):
            errors.append("League player cards stale: %s" % rel)
    folder = root / FOLDER
    if folder.is_dir():
        for path in sorted(folder.rglob("*")):
            rel = path.relative_to(root).as_posix()
            if path.is_file() and rel not in expected:
                errors.append("League player cards has an unexpected file: %s" % rel)
    return errors


def write(root=ROOT):
    """Write the folder, removing pages of players no longer on record. Returns (written, removed)."""
    root = Path(root)
    expected = render(root)
    written = removed = 0
    for rel, text in expected.items():
        path = root / rel
        data = text.encode("utf-8")
        if not path.is_file() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            written += 1
    folder = root / FOLDER
    for path in sorted(folder.rglob("*"), reverse=True):
        rel = path.relative_to(root).as_posix()
        if path.is_file() and rel not in expected:
            path.unlink()
            removed += 1
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    return written, removed
