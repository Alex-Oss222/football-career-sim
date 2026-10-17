#!/usr/bin/env python3
"""Per-season extraction shared by the kernel 2014.6 league builders (plan batch B3).

Not a command. ``build_2010_2014_league_base.py``, ``build_2010_2014_scoring_decisions.py``
and ``build_2014_conditions_calibration.py`` read league play-by-play only through
``season(...)`` here, which reads only through ``sources_2010_2014`` (the information
gate of batch B2: 2014 cut at Weeks 1-4 and games through September 29, 2014; digests
verified against the committed sources manifest; every row re-gated on read).

Drive grouping, offensive-snap test, result classifier, start-kind rule, kick and punt
outcome parses and the transition-record definitions are the committed 2012 builders'
own functions (``build_2012_drive_model``, ``build_2012_field_position_model``),
imported, never edited: ``fp.extract`` runs unchanged on the gated rows, and the
transition records rebuilt here are asserted equal to the ones it returns. What this
module adds is measured on the same drive dicts, then the rows are dropped, so the
returned season holds no club, game, player or date value: club and player identifiers
are used only to classify (offense or defence side, position group, the returner), and
every compact record is anonymous.

Stdlib only; deterministic (file order).
"""
from __future__ import annotations

import collections
import math
import re
import statistics
import sys
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_2012_drive_model as dm  # noqa: E402
import build_2012_field_position_model as fp  # noqa: E402
import pre_build_specification  # noqa: E402
import sources_2010_2014 as sources  # noqa: E402

RULES = pre_build_specification.frozen_rules()
EOH = RULES["end_of_half"]
SEASONS = tuple(RULES["data_window"]["seasons"])
CUT_SEASON = 2014
TAG = {s: ("%dw4" % s if s == CUT_SEASON else str(s)) for s in SEASONS}
SOURCES = ("nflverse", "nflscrapr")

# ---- source names -------------------------------------------------------------------


def pbp_name(season, source):
    if source == "nflverse":
        return "play_by_play_2014w4.csv" if season == CUT_SEASON else "play_by_play_%d.csv.gz" % season
    return "reg_pbp_2014w4.csv" if season == CUT_SEASON else "reg_pbp_%d.csv" % season


def roster_name(season):
    """Position source: that season's own roster (2014: the cut weekly roster)."""
    return "roster_weekly_2014w4.csv" if season == CUT_SEASON else "roster_%d.csv" % season


# ---- loading -------------------------------------------------------------------------

# Columns projected beyond the committed builder's (fp.STR_COLS, NUM_COLS, FLAG_COLS).
EXTRA_STR = (
    "season_type", "week", "game_date", "home_team", "away_team", "penalty_team", "penalty_type",
    "fumbled_1_team", "fumbled_1_player_id", "fumble_recovery_1_team", "fumble_recovery_1_player_id",
    "fumble_recovery_2_team", "forced_fumble_player_1_team", "forced_fumble_player_1_player_id",
    "return_team", "receiver_player_id", "passer_player_id", "interception_player_id", "replay_or_challenge_result",
    "roof", "surface", "stadium_id", "game_stadium", "stadium", "weather", "drive", "time",
    "own_kickoff_recovery_player_id", "kicker_player_id", "punter_player_id",
)
EXTRA_NUM = ("game_seconds_remaining", "penalty_yards", "air_yards", "temp", "wind", "season", "fumble_recovery_1_yards",
             "passing_yards", "rushing_yards", "receiving_yards", "home_timeouts_remaining",
             "away_timeouts_remaining", "score_differential", "total_home_score", "total_away_score")
EXTRA_FLAG = ("penalty", "fumble", "fumble_forced", "fumble_not_forced", "fumble_out_of_bounds", "complete_pass",
              "incomplete_pass", "out_of_bounds", "qb_dropback", "own_kickoff_recovery", "own_kickoff_recovery_td",
              "aborted_play", "return_touchdown", "extra_point_attempt", "field_goal_attempt", "punt_attempt",
              "rush_attempt", "pass_attempt", "qb_hit", "tackled_for_loss", "lateral_reception", "lateral_rush",
              "defensive_two_point_attempt")


def load_rows(season, source, dest):
    """The committed loader's projection (fp.load) of the gated rows, plus EXTRA_* columns.

    nflverse rows keep REG only (the committed reader's filter); every row is
    re-gated by sources.rows and its file digest checked against the manifest."""
    name = pbp_name(season, source)
    key = fp.INPUTS[source]["drive_key"]
    out = []
    for raw in sources.rows(name, dest):
        if source == "nflverse" and raw.get("season_type") != "REG":
            continue
        r = {k: ("" if v == "NA" else v) for k, v in raw.items()}
        row = {k: r.get(k, "") for k in fp.STR_COLS + fp.RAW_COLS}
        for k in fp.NUM_COLS:
            row[k] = fp._num(r.get(k, ""))
        for k in fp.FLAG_COLS:
            row[k] = fp._flag(r.get(k, ""))
        row["drive_key"] = r.get(key, "") or ""
        if "out_of_bounds" in r:
            row["out_of_bounds_flag"] = fp._flag(r["out_of_bounds"]) == 1
        for k in EXTRA_STR:
            if k not in row:
                row[k] = r.get(k, "")
        for k in EXTRA_NUM:
            row[k] = fp._num(r.get(k, ""))
        for k in EXTRA_FLAG:
            if k not in row:
                row[k] = fp._flag(r.get(k, ""))
        out.append(row)
    return out


def positions(season, dest):
    """gsis id -> most common position on that season's roster file (committed rule)."""
    path = sources.source_path(roster_name(season), dest)
    return fp.positions_map(path)


@contextmanager
def _committed_load(all_rows):
    """Run fp.extract on rows already loaded through the gate (its own reader is bypassed)."""
    original = fp.load
    fp.load = lambda path, source: all_rows
    try:
        yield
    finally:
        fp.load = original


# ---- small helpers -------------------------------------------------------------------

GROUP = {"QB": "QB", "RB": "RB", "FB": "RB", "HB": "RB", "WR": "WR", "TE": "TE", "T": "OL", "G": "OL", "C": "OL",
         "OL": "OL", "OT": "OL", "OG": "OL", "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL", "LB": "LB", "OLB": "LB",
         "ILB": "LB", "MLB": "LB", "CB": "DB", "S": "DB", "SS": "DB", "FS": "DB", "DB": "DB", "SAF": "DB", "K": "K",
         "P": "P", "LS": "LS"}


def group_of(pos_map, pid):
    if not pid:
        return None
    position = pos_map.get(pid)
    if position is None:
        return "unknown"
    return GROUP.get(position, "other")


def clock_of(r):
    """Game clock of a snap in its own period frame: half seconds in regulation, the
    quarter clock in overtime."""
    if (r.get("qtr") or 0) >= 5:
        return r.get("quarter_seconds_remaining")
    return r.get("half_seconds_remaining")


def same_club(a, b):
    return bool(a) and bool(b) and fp.alias(a) == fp.alias(b)


def is_try_row(r):
    d = (r.get("desc") or "").upper()
    return bool(r.get("extra_point_result") or r.get("two_point_conv_result") or fp.flag(r, "two_point_attempt")
                or r.get("play_type") == "extra_point" or "TWO-POINT CONVERSION" in d or "EXTRA POINT" in d
                or r.get("extra_point_attempt") == 1)


REVERSED = re.compile(r"REVERSED\.", re.I)


def counted_text(desc):
    """The part of a description that counted: the text after the last REVERSED."""
    parts = REVERSED.split(desc or "")
    return parts[-1] if len(parts) > 1 else (desc or "")


def host_kind(r):
    pt = r.get("play_type") or ""
    if pt == "pass":
        if r.get("sack") == 1:
            return "sack"
        return "complete" if r.get("complete_pass") == 1 else (
            "interception" if fp.flag(r, "interception") else "incomplete")
    if pt in ("run", "qb_kneel", "qb_spike", "punt", "field_goal", "no_play", "kickoff"):
        return pt
    return pt or "other"


# ---- penalties (parsed clauses) ------------------------------------------------------------

CLAUSE = re.compile(
    r"(PENALTY|Penalty) on ([A-Z]{2,3})(?:-[^,]*?)?, "
    r"((?:[^,(]|\([^)]*\))+?), "
    r"(?:(declined)|(offsetting)|(-?\d+) yards?)")
CLAUSE_START = re.compile(r"(?:PENALTY|Penalty) on ")
HALF_DISTANCE = re.compile(r"half the distance", re.I)


def norm_type(text):
    return re.sub(r"\s*\(\d+ Yards\)", "", text).strip()


def clauses(r):
    """Parsed penalty clauses of a row: (team, type, status A/D/X, yards or None), and the
    number of 'Penalty on' openings the parse could not read."""
    text = counted_text(r.get("desc") or "")
    found = list(CLAUSE.finditer(text))
    out = []
    for m in found:
        _, team, kind, declined, offsetting, yards = m.groups()
        status = "D" if declined else ("X" if offsetting else "A")
        out.append((fp.alias(team), norm_type(kind), status, None if yards is None else abs(int(yards))))
    unparsed = len(CLAUSE_START.findall(text)) - len(found)
    return out, max(0, unparsed)


# ---- statistics (stdlib) ---------------------------------------------------------------

def gammq(a, x):
    """Upper regularized incomplete gamma Q(a, x)."""
    if x <= 0:
        return 1.0
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(5000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return max(0.0, 1.0 - s * math.exp(-x + a * math.log(x) - math.lgamma(a)))
    b = x + 1 - a
    c = 1e300
    d = 1 / b
    h = d
    for i in range(1, 5000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = d if abs(d) > 1e-300 else 1e-300
        c = b + an / c
        c = c if abs(c) > 1e-300 else 1e-300
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_p(stat, df):
    return gammq(df / 2.0, stat / 2.0) if df > 0 else float("nan")


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 5000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c
        c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c
        c = c if abs(c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return h


def betai(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def f_p(f, df1, df2):
    """Upper tail of the F distribution."""
    if not (f > 0) or df1 <= 0 or df2 <= 0:
        return float("nan")
    return betai(df2 / 2.0, df1 / 2.0, df2 / (df2 + df1 * f))


def share_drift(pairs):
    """Homogeneity of a share across seasons: Pearson chi-square on the k x 2 table."""
    rows = [(k, n - k) for k, n in pairs if n > 0]
    if len(rows) < 2:
        return None
    total = sum(a + b for a, b in rows)
    col = [sum(r[0] for r in rows), sum(r[1] for r in rows)]
    if not all(col):
        return {"test": "chi-square", "stat": 0.0, "df": len(rows) - 1, "p": 1.0}
    stat = 0.0
    for a, b in rows:
        n = a + b
        for j, v in enumerate((a, b)):
            e = n * col[j] / total
            stat += (v - e) ** 2 / e
    df = len(rows) - 1
    return {"test": "chi-square", "stat": round(stat, 4), "df": df, "p": round(chi2_p(stat, df), 6)}


def rate_drift(pairs):
    """Homogeneity of a per-unit count rate (Poisson): chi-square of counts against exposures."""
    rows = [(k, n) for k, n in pairs if n > 0]
    if len(rows) < 2:
        return None
    rate = sum(k for k, _ in rows) / sum(n for _, n in rows)
    if rate <= 0:
        return {"test": "poisson chi-square", "stat": 0.0, "df": len(rows) - 1, "p": 1.0}
    stat = sum((k - n * rate) ** 2 / (n * rate) for k, n in rows)
    df = len(rows) - 1
    return {"test": "poisson chi-square", "stat": round(stat, 4), "df": df, "p": round(chi2_p(stat, df), 6)}


def mean_drift(moments):
    """One-way ANOVA across seasons from (n, sum, sum of squares) moments."""
    rows = [m for m in moments if m[0] > 1]
    if len(rows) < 2:
        return None
    n = sum(m[0] for m in rows)
    grand = sum(m[1] for m in rows) / n
    ssb = sum(m[0] * (m[1] / m[0] - grand) ** 2 for m in rows)
    ssw = sum(m[2] - m[1] ** 2 / m[0] for m in rows)
    df1, df2 = len(rows) - 1, n - len(rows)
    if ssw <= 0:
        return {"test": "anova F", "stat": None, "df": [df1, df2], "p": None}
    f = (ssb / df1) / (ssw / df2)
    return {"test": "anova F", "stat": round(f, 4), "df": [df1, df2], "p": round(f_p(f, df1, df2), 6)}


def moments(values):
    values = list(values)
    return [len(values), sum(values), sum(v * v for v in values)]


# ---- the season extraction -----------------------------------------------------------------

def _first_top(d):
    """R17a: the first row of the drive group carrying a drive time of possession."""
    for r in d["rows"]:
        value = fp.clock_seconds(r.get("drive_time_of_possession", ""))
        if value is not None:
            return value
    return None


def _elapsed(d):
    """Game-clock seconds from the drive's first snap to its terminal snap."""
    a, b = clock_of(d["first"]), clock_of(d["terminal"])
    if a is None or b is None:
        return None
    return int(round(a - b))


def r17a_group(d):
    if d["final"] and d["category"] == "clock":
        return "h1_clock_expiry" if d["half"] == "Half1" else "end_of_game_clock"
    return "interior"


def drive_rows(d):
    """The drive's own rows in file order, without kick rows and tries: scrimmage snaps,
    no-play rows, and the punt or field-goal row that ends it."""
    return [r for r in d["own"] if not fp.is_kick_row(r) and not is_try_row(r)]


def _ot_orders(drives):
    """Index of each overtime drive among its game's overtime drives (0 = opening)."""
    seen = collections.Counter()
    out = {}
    for i, d in enumerate(drives):
        if d["half"] == "Overtime":
            gid = d["first"]["game_id"]
            out[i] = seen[gid]
            seen[gid] += 1
    return out


def repair_split_drives(all_rows):
    """A game whose fixed_drive grouping leaves an unclassified drive (a split drive in the
    source key) is regrouped by the source's own `drive` key (specification section 2:
    explained, never repaired by hand). Returns the repaired game count's ids (not stored)."""
    fp.annotate_scores(all_rows)
    broken = {d["first"]["game_id"] for d in fp.build_drives(all_rows) if d["category"] not in fp.CATEGORIES}
    for r in all_rows:
        if r["game_id"] in broken:
            r["drive_key"] = r.get("drive") or ""
    return sorted(broken)


def season(season_year, source, dest):
    """Extract one season from one source. Returns an anonymous dict (no rows)."""
    all_rows = load_rows(season_year, source, dest)
    pos_map = positions(season_year, dest)
    path = sources.source_path(pbp_name(season_year, source), dest)
    repaired = repair_split_drives(all_rows) if source == "nflverse" else []
    with _committed_load(all_rows):
        ex = fp.extract(path, source, pos_map)
    drives = ex["drives"]
    if source == "nflverse" and any(d["category"] not in fp.CATEGORIES for d in drives):
        raise AssertionError("%s nflverse: a drive is still unclassified after the drive-key repair" % season_year)
    ot_order = _ot_orders(drives)
    out_drives = []
    for i, d in enumerate(drives):
        out_drives.append(compact_drive(d, season_year, source, ot_order.get(i), pos_map))
    pools, retained, mapping = transition_records(drives, season_year, source, ex, pos_map)
    games = fp.games(all_rows)
    play = play_level(all_rows, games, season_year, source, pos_map)
    return {
        "season": season_year, "source": source, "games": ex["games"], "team_games": 2 * ex["games"],
        "repaired_games": len(repaired),
        "drives": out_drives, "pools": pools, "retained": retained, "kick_mappings": mapping,
        "start_kinds": ex["start_kinds"], "turnover_touchbacks": ex["turnover_touchbacks"],
        "scramble": ex["scramble"], "corrections": ex["corrections"], "imputed_tries": ex["imputed_tries"],
        "play": play,
    }


def compact_drive(d, season_year, source, ot_index, pos_map):
    """Everything the builders need from one drive dict, with no identifier."""
    t, first = d["terminal"], d["first"]
    top, e = _first_top(d), _elapsed(d)
    c = {
        "season": season_year, "category": d["category"], "raw": d["raw"], "remap": d["remap"],
        "half": d["half"], "final": bool(d["final"]), "start": d["start"], "end": d["end"], "net0": d["net0"],
        "plays": d["plays"], "runs": d["runs"], "attempts": d["attempts"], "sacks": d["sacks"],
        "kneel_yards": d["kneel_yards"], "spikes": d["spikes"], "off_timeouts": d["off_timeouts"],
        "def_timeouts": d["def_timeouts"], "off_timeouts_used": d["off_timeouts_used"],
        "def_timeouts_used": d["def_timeouts_used"], "seconds_v2": d["seconds"], "t0": d["t0"],
        "score_diff": d["score_diff"], "term_bucket": d["term_bucket"], "term_down": d["term_down"],
        "term_ydstogo": d["term_ydstogo"], "chains": d["chains"], "fg": d["fg"], "safety_term": d["safety_term"],
        "td_kind": d["td_kind"], "renderable": d["renderable"], "start_kind": d["start_kind"],
        "corrected_start": d["corrected_start"], "fg_offset_corrected": d.get("fg_offset_corrected"),
        "ot_index": ot_index, "top_first": top, "elapsed": e, "r17a_group": r17a_group(d),
        "last_row_top_blank": fp.clock_seconds(d["rows"][-1].get("drive_time_of_possession", "")) is None,
        "term_qtr": t["qtr"], "term_qsr": t["quarter_seconds_remaining"], "term_clock": clock_of(t),
        "first_clock": clock_of(first), "term_sd": t.get("sd"), "first_qtr": first["qtr"],
        "term_play_type": t["play_type"],
    }
    c["points"] = _drive_points(d)
    # Spikes: the clock at the last spike (its own period frame).
    spikes = [r for r in d["offs"] if r["play_type"] == "qb_spike"]
    c["last_spike_clock"] = clock_of(spikes[-1]) if spikes else None
    c["spike_clocks"] = [clock_of(r) for r in spikes]
    # Field-goal snap clock and its down (W3).
    c["fg_snap_clock"] = clock_of(t) if t["play_type"] == "field_goal" else None
    c["fg_snap_down"] = int(t["down"]) if t["play_type"] == "field_goal" and t["down"] else None
    c["clock_sequence"] = clock_sequence(d)
    # Pre-snap ball spots of the drive's rows (the legal start range of a relocated replay).
    spots = [int(round(r["yardline_100"])) for r in drive_rows(d) if r.get("yardline_100") is not None]
    c["placement"] = [d["start"] + 1 - min(spots), d["start"] + 99 - max(spots)] if spots else [d["start"], d["start"]]
    c.update(yardage(d))
    c.update(penalties_of(d, pos_map))
    c["fumbles"] = fumbles_of(d, pos_map)
    return c


def _drive_points(d):
    category = d["category"]
    if category == "touchdown":
        t = d["terminal"]
        after = d["game_rows"][t["gi"] + 1:t["gi"] + 3]
        tries = [r for r in after if r["extra_point_result"] or r["two_point_conv_result"]]
        bonus = 0
        if tries:
            bonus = (tries[0]["extra_point_result"] == "good") + 2 * (tries[0]["two_point_conv_result"] == "success")
        return 6 + bonus
    if category == "field_goal_attempt":
        return 3 * d["fg"][1]
    return 0


# ---- W5a clock sequences ---------------------------------------------------------------------

OOB = re.compile(r"\b(?:ran|pushed|run|pushed out of bounds|ran out of bounds) ob\b|out of bounds", re.I)


def out_of_bounds(r):
    """The play ended out of bounds: nflverse's flag; nflscrapR (no such column) from the
    description, the same GSIS text the flag is derived from."""
    if "out_of_bounds_flag" in r:
        return r["out_of_bounds_flag"]
    return bool(OOB.search(counted_text(r.get("desc") or "")))


def snap_kind(r):
    """W5a previous-play kind of a snap row (None for rows that are not snaps)."""
    pt = r.get("play_type")
    oob = out_of_bounds(r)
    if pt == "run":
        return "run_oob" if oob else "run"
    if pt == "pass":
        if r.get("sack") == 1:
            return "sack"
        if r.get("complete_pass") == 1:
            return "complete_oob" if oob else "complete"
        return "incomplete"
    if pt == "qb_spike":
        return "spike"
    if pt == "qb_kneel":
        return "kneel"
    return None


def clock_sequence(d):
    """[(kind, clock, qtr, quarter clock)] of the drive's own scrimmage snaps, timeout rows
    and its kick snap, in file order (the W5a gap and kick-length tables)."""
    seq = []
    for r in d["rows"]:
        if r.get("timeout") == 1 and r.get("play_type") in ("no_play", "") and "Timeout" in (r.get("desc") or ""):
            seq.append(("timeout", clock_of(r), r.get("qtr"), r.get("quarter_seconds_remaining")))
            continue
        if r["posteam"] != d["posteam"] or not fp.is_off(r, d["posteam"]):
            continue
        kind = snap_kind(r)
        if kind is None and r["play_type"] in ("punt", "field_goal"):
            kind = r["play_type"]
        if kind is not None:
            seq.append((kind, clock_of(r), r.get("qtr"), r.get("quarter_seconds_remaining")))
    return seq


# ---- B3b annotations ------------------------------------------------------------------------

def yardage(d):
    """Real rushing and passing yards, completions and sack losses of the drive, in snap order."""
    rush = passing = completions = 0
    sack_losses, run_values, completion_values, spike_positions = [], [], [], []
    snap = 0
    terminal = d["terminal"]
    term_snap = None
    for r in d["offs"]:
        pt = r["play_type"]
        if pt not in fp.SCRIMMAGE:
            continue
        y = int(r["yards_gained"] or 0)
        if pt == "run":
            rush += y
            run_values.append(y)
        elif pt == "pass" and r["sack"] == 1:
            sack_losses.append(y)
        elif pt == "pass" and r.get("complete_pass") == 1:
            passing += y
            completions += 1
            completion_values.append(y)
        elif pt == "qb_spike":
            spike_positions.append(snap)
        if r is terminal:
            term_snap = [host_kind(r), y]
        snap += 1
    kneel = sum(d["kneel_yards"])
    other = d["net0"] - (rush + passing + sum(sack_losses) + kneel)
    return {"rush_yards": rush, "pass_yards": passing, "completions": completions, "sack_losses": sack_losses,
            "other_yards": other, "run_values": run_values, "completion_values": completion_values,
            "spike_positions": spike_positions, "term_snap": term_snap}


EMPHASIS = tuple((side, kind) for side, kind, _ in RULES["emphasis_2014"]["types"])
EMPHASIS_EXPOSURE = tuple(exposure for _, _, exposure in RULES["emphasis_2014"]["types"])


def is_dropback(r):
    """A dropback, including a no-play dropback (the pass or sack the foul nullified)."""
    if r.get("play_type") == "pass" or r.get("qb_dropback") == 1:
        return True
    if r.get("play_type") == "no_play":
        text = (r.get("desc") or "").lower()
        return " pass " in text or "sacked" in text or "scrambles" in text
    return False


def penalties_of(d, pos_map):
    """Penalty clauses on the drive's own rows (pen), the 2014 emphasis counts (emph) and
    exposures (exposure: [dropbacks including no-play dropbacks, snaps])."""
    pos = d["posteam"]
    rows = drive_rows(d)
    pen = []
    emph = [0] * len(EMPHASIS)
    unparsed = 0
    dropbacks = snaps = 0
    for index, r in enumerate(rows):
        pt = r["play_type"]
        is_snap = pt in fp.SCRIMMAGE or pt == "no_play"
        if is_snap:
            snaps += 1
            dropbacks += is_dropback(r)
        found, missing = clauses(r)
        unparsed += missing
        for team, kind, status, yards in found:
            side = "O" if same_club(team, pos) else "D"
            if pt == "no_play":
                enforce = "N"
            elif pt in ("punt", "field_goal"):
                enforce = "K"
            else:
                enforce = "S"
            signed = None
            if status == "A" and yards is not None:
                signed = yards if side == "D" else -yards
            first_down = int(status == "A" and side == "D" and r.get("first_down_penalty") == 1)
            half = int(bool(HALF_DISTANCE.search(counted_text(r.get("desc") or ""))))
            pen.append([index, kind, side, signed, status, enforce, first_down, host_kind(r), half])
            if status == "A":
                key = ("defense" if side == "D" else "offense", kind)
                if key in EMPHASIS:
                    emph[EMPHASIS.index(key)] += 1
    return {"pen": pen, "emph": emph, "exposure": [dropbacks, snaps], "pen_unparsed": unparsed}


def fumble_kind(r):
    if r.get("play_type") in ("punt", "field_goal"):
        return "kick"
    if r.get("aborted_play") == 1 or "Aborted" in (r.get("desc") or "") or "FUMBLES (Aborted)" in (r.get("desc") or ""):
        return "aborted"
    if r.get("play_type") == "pass" and r.get("sack") == 1:
        return "sack"
    if r.get("play_type") == "pass":
        return "reception"
    return "run"


def fumbles_of(d, pos_map):
    """Scrimmage fumbles of the drive: [snap order, kind, host, outcome, forced, forcer group,
    recoverer group, recoverer is forcer, recoverer is fumbler] (the fumble=1 rows; a
    nullified play carries fumble=0)."""
    pos = d["posteam"]
    out = []
    for index, r in enumerate(drive_rows(d)):
        if r.get("fumble") != 1:
            continue
        if r.get("fumble_lost") == "1" or fp.flag(r, "fumble_lost"):
            outcome = "lost"
        elif r.get("fumble_out_of_bounds") == 1:
            outcome = "oob"
        else:
            outcome = "kept"
        forcer = r.get("forced_fumble_player_1_player_id") or ""
        recoverer = r.get("fumble_recovery_1_player_id") or ""
        fumbler = r.get("fumbled_1_player_id") or ""
        out.append([index, fumble_kind(r), host_kind(r), outcome, int(r.get("fumble_forced") == 1),
                    group_of(pos_map, forcer), group_of(pos_map, recoverer),
                    int(bool(recoverer) and recoverer == forcer), int(bool(recoverer) and recoverer == fumbler)])
    return out


# ---- transition records --------------------------------------------------------------------

def _kick_penalties(r):
    """Clauses on a kick row, signed to the receiving club (positive helps the receiver)."""
    found, _ = clauses(r)
    kicking = r["defteam"] if r["play_type"] == "kickoff" or fp.is_kick_row(r) else r["posteam"]
    out = []
    for team, kind, status, yards in found:
        side = "K" if same_club(team, kicking) else "R"
        signed = None
        if status == "A" and yards is not None:
            signed = yards if side == "K" else -yards
        out.append([kind, side, signed, status])
    return out


def _kick_fumble(r, returner):
    """[kind muff|fumble, outcome kept|lost|oob, muffer role returner|other] or None."""
    text = (r.get("desc") or "").upper()
    muff = "MUFF" in text
    fumble = r.get("fumble") == 1 or "FUMBLE" in text
    if not (muff or fumble):
        return None
    if r.get("fumble_lost") == "1" or fp.flag(r, "fumble_lost"):
        outcome = "lost"
    elif r.get("fumble_out_of_bounds") == 1:
        outcome = "oob"
    else:
        outcome = "kept"
    fumbler = r.get("fumbled_1_player_id") or ""
    role = None
    if fumbler:
        role = "returner" if returner and fumbler == returner else "other"
    return ["muff" if muff else "fumble", outcome, role]


def muffer_role(fumble):
    """The muffer's role (returner or other) when the kick was muffed; None otherwise."""
    return fumble[2] if fumble and fumble[0] == "muff" else None


def transition_records(drives, season_year, source, ex, pos_map):
    """The committed transition records, rebuilt with the committed functions and asserted
    equal to fp.extract's, each followed by its annotations; plus retained kicks."""
    kick_pool, free_kicks, punts = [], [], []
    turnovers = {"interception": [], "fumble_lost": []}
    retained = {"kickoff": [], "free_kick": [], "punt": []}
    mapping = collections.Counter()
    for d in drives:
        kind, det = fp.start_type(d)
        nxt = d["start"]
        if kind in ("kickoff", "safety_free_kick"):
            k = det["kick_row"]
            outcome = fp.kickoff_outcome(k)
            spot = fp.kick_spot_own(k)
            kicks_here = [r for r in d["game_rows"][(d["prev"]["last_off_gi"] + 1 if d["prev"] else 0):d["first_gi"]]
                          if fp.is_kick_row(r)]
            if len(kicks_here) > 1:
                mapping["rekick"] += 1
            if kind == "safety_free_kick" and d["prev"] is not None and d["prev"]["category"] != "safety":
                mapping["penalty_or_other_safety_free_kick"] += 1
            returner = k.get("kickoff_returner_player_id") or ""
            pen = _kick_penalties(k)
            if det.get("recovered_by_kicking_team"):
                if outcome in ("onside", "return_td") or flag_td(k) or spot != (35 if kind == "kickoff" else 20):
                    mapping["retained_excluded"] += 1
                    continue
                kick = fp.kick_yards(k) or 0
                ret = int(k["return_yards"] or 0)
                landing = spot + kick - ret      # receiving frame
                e = nxt - (100 - landing)        # kicking frame: next start = 100 - landing + e
                record = [0, nxt, kick, ret, e, "retained", season_year, pen,
                          e - _signed_sum(pen, kicking_frame=True), _kick_fumble(k, returner), "kicking",
                          muffer_role(_kick_fumble(k, returner))]
                retained["kickoff" if kind == "kickoff" else "free_kick"].append(record)
                continue
            if outcome in ("onside", "return_td") or spot != (35 if kind == "kickoff" else 20):
                continue
            touchback = outcome == "touchback"
            kick = fp.kick_yards(k) or 0
            ret = 0 if touchback else int(k["return_yards"] or 0)
            e = nxt - 80 if touchback else nxt - (spot + kick - ret)
            fumble = _kick_fumble(k, returner)
            record = [int(touchback), nxt, kick, ret, e, outcome, season_year, pen, e - _signed_sum(pen),
                      fumble, "receiving", muffer_role(fumble)]
            (kick_pool if kind == "kickoff" else free_kicks).append(record)
        elif kind == "punt":
            t = d["prev"]["terminal"]
            los = int(round(t["yardline_100"]))
            outcome = fp.punt_outcome(t)
            gross = fp.kick_yards(t) or 0
            ret = int(t["return_yards"] or 0)
            touchback = outcome == "touchback"
            e = nxt - 80 if touchback else nxt - (100 - los + gross - ret)
            returner = t.get("punt_returner_player_id") or ""
            pen = _kick_penalties(t)
            fumble = _kick_fumble(t, returner)
            punts.append([los, outcome, gross, ret, e, nxt, int(touchback), season_year, pen, e - _signed_sum(pen),
                          fumble, "receiving", muffer_role(fumble)])
        elif kind in turnovers:
            prev = d["prev"]
            t = prev["terminal"]
            end = prev["end"]
            touchback = "TOUCHBACK" in t["desc"].upper()
            ret = int(t["return_yards"] or 0)
            turnovers[kind].append([end, nxt, ret, int(touchback), nxt - (100 - end), season_year])
        elif kind == "same_team_continuation" and d["prev"] is not None and d["prev"]["category"] == "punt":
            # The punting club kept the ball (a muffed punt it recovered): a retained punt.
            t = d["prev"]["terminal"]
            if flag_td(t):
                mapping["retained_excluded"] += 1
                continue
            los = int(round(t["yardline_100"]))
            gross = fp.kick_yards(t) or 0
            ret = int(t["return_yards"] or 0)
            landing = 100 - los + gross - ret          # receiving frame
            e = nxt - (100 - landing)                  # kicking frame
            returner = t.get("punt_returner_player_id") or ""
            pen = _kick_penalties(t)
            fumble = _kick_fumble(t, returner)
            retained["punt"].append([los, "retained", gross, ret, e, nxt, 0, season_year, pen,
                                     e - _signed_sum(pen, kicking_frame=True), fumble, "kicking",
                                     muffer_role(fumble)])
    punts.sort(key=lambda r: r[0])
    for pool in turnovers.values():
        pool.sort(key=lambda r: r[0])
    retained["punt"].sort(key=lambda r: r[0])
    pools = {"kickoff_pool": kick_pool, "free_kick_pool": free_kicks, "punt_pool": punts,
             "interception_pool": turnovers["interception"], "fumble_pool": turnovers["fumble_lost"]}
    # The committed records are the prefixes of these (core fields only).
    widths = {"kickoff_pool": 6, "free_kick_pool": 6, "punt_pool": 7, "interception_pool": 5, "fumble_pool": 5}
    for name, width in widths.items():
        committed = ex[name]
        mine = [r[:width] for r in pools[name]]
        if mine != committed:
            raise AssertionError("%s %s %s: rebuilt transition records differ from fp.extract's"
                                 % (season_year, source, name))
    return pools, retained, dict(mapping)


def flag_td(r):
    return fp.flag(r, "touchdown")


def _signed_sum(pen, kicking_frame=False):
    """The accepted penalty yards' effect on a record's enforcement e. pen yards are signed
    positive when they help the receiving club; a receiving-frame next start (its distance to
    the kicking club's goal) falls by them, a kicking-frame next start rises by them."""
    total = sum(p[2] for p in pen if p[3] == "A" and p[2] is not None)
    return total if kicking_frame else -total


# ---- play-level totals ---------------------------------------------------------------------

def play_level(all_rows, games, season_year, source, pos_map):
    """League play-level counts for the aggregate baseline, the drive-model rates and the
    pass-2 comparisons (no identifiers)."""
    c = collections.Counter()
    fg_rows = []
    pen_accepted = collections.Counter()
    pen_yards = collections.Counter()
    multi = 0
    unparsed = 0
    two_point = {"drive_model": [0, 0], "scrimmage": [0, 0]}
    for r in all_rows:
        pt = r["play_type"]
        text = r.get("desc") or ""
        if r.get("field_goal_result"):
            c["fg_attempts"] += 1
            c["fg_made"] += r["field_goal_result"] == "made"
            c["fg_blocked"] += r["field_goal_result"] == "blocked"
            if r["kick_distance"] is not None:
                fg_rows.append((int(r["kick_distance"]), int(r["field_goal_result"] == "made")))
        if r.get("extra_point_result"):
            c["xp_attempts"] += 1
            c["xp_made"] += r["extra_point_result"] == "good"
        if r.get("two_point_conv_result"):
            two_point["drive_model"][1] += 1
            two_point["drive_model"][0] += r["two_point_conv_result"] == "success"
        if r.get("two_point_conv_result") and "No Play" not in text and "(Kick formation)" not in text \
                and r.get("defensive_two_point_attempt") != 1:
            two_point["scrimmage"][1] += 1
            two_point["scrimmage"][0] += r["two_point_conv_result"] == "success"
        if fp.flag(r, "safety"):
            c["safeties"] += 1
        off = fp.is_off(r) and pt != "no_play"   # offensive snaps (two-point tries excluded)
        if off and pt == "pass" and r["sack"] != 1:
            c["pass_attempts"] += 1
            if r.get("complete_pass") == 1:
                c["completions"] += 1
                c["pass_yards"] += int(r["yards_gained"] or 0)
            if fp.flag(r, "interception"):
                c["interceptions"] += 1
            if fp.flag(r, "touchdown") and same_club(r["td_team"], r["posteam"]):
                c["pass_td"] += 1
        if off and pt == "qb_spike":
            c["spikes"] += 1
        if off and pt == "pass" and r["sack"] == 1:
            c["sacks"] += 1
            c["sack_yards"] += int(r["yards_gained"] or 0)
        if off and pt == "run":
            c["rush_attempts"] += 1
            c["rush_yards"] += int(r["yards_gained"] or 0)
            if fp.flag(r, "touchdown") and same_club(r["td_team"], r["posteam"]):
                c["rush_td"] += 1
        if off and pt == "qb_kneel":
            c["kneels"] += 1
            c["kneel_yards"] += int(r["yards_gained"] or 0)
        found, missing = clauses(r)
        unparsed += missing
        accepted = [f for f in found if f[2] == "A"]
        if len(accepted) > 1:
            multi += 1
        week = r.get("week") or ""
        for team, kind, status, yards in accepted:
            pen_accepted["all"] += 1
            pen_yards["all"] += yards or 0
            pen_accepted["week:%s" % week] += 1
        if r.get("penalty") == 1:
            c["penalty_flag_rows"] += 1
        if r.get("first_down_penalty") == 1:
            c["penalty_first_downs"] += 1
    points = 0
    for plays in games.values():
        totals = [(r.get("total_home_score") or 0) + (r.get("total_away_score") or 0) for r in plays]
        points += int(max(totals)) if totals else 0
    games_by_week = collections.Counter(plays[0].get("week") or "" for plays in games.values())
    return {"counts": dict(c), "fg_rows": fg_rows, "points": points,
            "penalties_by_week": {w: [pen_accepted["week:%s" % w], n] for w, n in sorted(games_by_week.items())}, "penalties_accepted": pen_accepted["all"],
            "penalty_yards_accepted": pen_yards["all"], "rows_with_two_accepted": multi,
            "unparsed_clauses": unparsed, "two_point": two_point, "games": len(games)}


def median_low(values):
    return statistics.median_low(values) if values else None
