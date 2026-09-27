"""Column definitions and Markdown tables shared by every public stat view.

Season views file players position first (quarterbacks, running backs, ...)
and give each position the statistics it is measured by. Game box scores use
the category layout of a standard NFL box score (passing, rushing, receiving,
defense, special teams). Every derived column is arithmetic on stored
counters; nothing is estimated.
"""
from .statbook import LONG_FIELDS

# ---- values ----------------------------------------------------------------

def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def g(line, field):
    value = line.get(field, 0)
    return value if numeric(value) else 0


def avg(yards, opportunities):
    return "%.1f" % (yards / opportunities) if opportunities else "—"


def pct(made, attempts):
    return "%.1f" % (100.0 * made / attempts) if attempts else "—"


def thrown(line):
    return line["interceptions_thrown"] if "interceptions_thrown" in line else g(line, "interceptions")


def rating_value(line):
    """Official NFL passer rating; None without an attempt."""
    attempts = g(line, "pass_attempts")
    if not attempts:
        return None
    clamp = lambda value: max(0.0, min(2.375, value))
    a = clamp((g(line, "completions") / attempts - 0.3) * 5)
    b = clamp((g(line, "passing_yards") / attempts - 3) * 0.25)
    c = clamp(g(line, "passing_touchdowns") / attempts * 20)
    d = clamp(2.375 - thrown(line) / attempts * 25)
    return (a + b + c + d) / 6 * 100


def passer_rating(line):
    value = rating_value(line)
    return "—" if value is None else "%.1f" % value


def kicking_points(line):
    return 3 * g(line, "field_goals_made") + g(line, "extra_points_made")


def time_text(seconds):
    seconds = int(round(seconds))
    return "%d:%02d" % (seconds // 60, seconds % 60)


# ---- columns ---------------------------------------------------------------

def col(header, field):
    return (header, lambda line: g(line, field), (field,))


def derived(header, fn, *fields):
    return (header, fn, fields)


GAMES = col("G", "games")
PASSING = (
    col("CMP", "completions"), col("ATT", "pass_attempts"),
    derived("CMP%", lambda l: pct(g(l, "completions"), g(l, "pass_attempts"))),
    col("YDS", "passing_yards"),
    derived("Y/A", lambda l: avg(g(l, "passing_yards"), g(l, "pass_attempts"))),
    col("TD", "passing_touchdowns"),
    derived("INT", thrown, "interceptions_thrown", "interceptions"),
    derived("RTG", passer_rating),
    col("SCK", "sacks_taken"), col("SCKY", "sack_yards"),
)
RUSHING = (
    col("CAR", "rushing_attempts"), col("YDS", "rushing_yards"),
    derived("AVG", lambda l: avg(g(l, "rushing_yards"), g(l, "rushing_attempts"))),
    col("TD", "rushing_touchdowns"), col("LNG", "long_rush"),
)
RECEIVING = (
    col("TGT", "targets"), col("REC", "receptions"), col("YDS", "receiving_yards"),
    derived("AVG", lambda l: avg(g(l, "receiving_yards"), g(l, "receptions"))),
    col("TD", "receiving_touchdowns"), col("LNG", "long_reception"),
)
FUMBLES = (col("FUM", "fumbles"), col("LOST", "fumbles_lost"))
RUSH_SECONDARY = (
    col("RUSH", "rushing_attempts"), col("RUSH YDS", "rushing_yards"), col("RUSH TD", "rushing_touchdowns"),
)
RECEIVE_SECONDARY = (
    col("TGT", "targets"), col("REC", "receptions"), col("REC YDS", "receiving_yards"),
    col("REC TD", "receiving_touchdowns"),
)
TACKLING = (
    col("TOT", "tackles"), col("SOLO", "solo_tackles"), col("AST", "assisted_tackles"),
    col("TFL", "tackles_for_loss"),
)
FRONT_DEFENSE = TACKLING + (
    col("SCK", "sacks"), col("PRESS", "pressures"), col("PD", "passes_defended"),
    col("INT", "defensive_interceptions"), col("FF", "forced_fumbles"), col("FR", "fumble_recoveries"),
)
BACK_DEFENSE = TACKLING + (
    col("INT", "defensive_interceptions"), col("INT YDS", "interception_return_yards"),
    col("PD", "passes_defended"), col("SCK", "sacks"), col("PRESS", "pressures"),
    col("FF", "forced_fumbles"), col("FR", "fumble_recoveries"),
)
BOX_DEFENSE = TACKLING + (
    col("SCK", "sacks"), col("PD", "passes_defended"), col("INT", "defensive_interceptions"),
    col("INT YDS", "interception_return_yards"), col("FF", "forced_fumbles"),
    col("FR", "fumble_recoveries"),
)
KICKING = (
    col("FGM", "field_goals_made"), col("FGA", "field_goals_attempted"),
    derived("FG%", lambda l: pct(g(l, "field_goals_made"), g(l, "field_goals_attempted"))),
    col("XPM", "extra_points_made"), col("XPA", "extra_points_attempted"),
    derived("PTS", kicking_points),
)
PUNTING = (
    col("PUNTS", "punts"), col("YDS", "punt_yards"),
    derived("AVG", lambda l: avg(g(l, "punt_yards"), g(l, "punts"))),
    col("LNG", "long_punt"), col("IN20", "punts_inside_20"), col("TB", "punt_touchbacks"),
)
RETURNS = (
    col("KR", "kick_returns"), col("KR YDS", "kick_return_yards"),
    derived("KR AVG", lambda l: avg(g(l, "kick_return_yards"), g(l, "kick_returns"))),
    col("PR", "punt_returns"), col("PR YDS", "punt_return_yards"),
    derived("PR AVG", lambda l: avg(g(l, "punt_return_yards"), g(l, "punt_returns"))),
)
OFFENSIVE_LINE = (col("SCK ALLOWED", "sacks_allowed"),)

RETURN_FIELDS = frozenset({"kick_returns", "kick_return_yards", "punt_returns", "punt_return_yards", "return_yards"})
# Implied by columns already shown: dropbacks are attempts plus sacks, and
# return yards are kick plus punt return yards.
IMPLIED_FIELDS = frozenset({"dropbacks", "return_yards"})

# (title, roster positions, stat columns, sort field)
POSITION_GROUPS = (
    ("Quarterbacks", {"QB"}, PASSING + RUSH_SECONDARY + FUMBLES, "passing_yards"),
    ("Running backs", {"RB", "HB", "FB"}, RUSHING + RECEIVE_SECONDARY + FUMBLES, "rushing_yards"),
    ("Wide receivers", {"WR"}, RECEIVING + RUSH_SECONDARY + FUMBLES, "receiving_yards"),
    ("Tight ends", {"TE"}, RECEIVING + RUSH_SECONDARY + FUMBLES, "receiving_yards"),
    ("Offensive line", {"OT", "OG", "G", "T", "C", "OL", "LT", "LG", "RG", "RT"}, OFFENSIVE_LINE, "sacks_allowed"),
    ("Defensive line", {"DE", "DT", "NT", "DL"}, FRONT_DEFENSE, "tackles"),
    ("Linebackers", {"OLB", "ILB", "MLB", "LB"}, FRONT_DEFENSE, "tackles"),
    ("Defensive backs", {"CB", "S", "FS", "SS", "DB"}, BACK_DEFENSE, "tackles"),
    ("Kickers", {"K", "PK"}, KICKING, "field_goals_made"),
    ("Punters", {"P"}, PUNTING, "punt_yards"),
    ("Long snappers", {"LS"}, (), "games"),
)

LABELS = {
    "pass_attempts": "ATT", "completions": "CMP", "passing_yards": "PASS YDS",
    "passing_touchdowns": "PASS TD", "interceptions_thrown": "INT THROWN",
    "interceptions": "INT THROWN", "sacks_taken": "SCK TAKEN", "sack_yards": "SCKY",
    "rushing_attempts": "RUSH", "rushing_yards": "RUSH YDS", "rushing_touchdowns": "RUSH TD",
    "long_rush": "RUSH LNG", "targets": "TGT", "receptions": "REC",
    "receiving_yards": "REC YDS", "receiving_touchdowns": "REC TD", "long_reception": "REC LNG",
    "fumbles": "FUM", "fumbles_lost": "LOST", "sacks_allowed": "SCK ALLOWED",
    "tackles": "TOT", "solo_tackles": "SOLO", "assisted_tackles": "AST",
    "tackles_for_loss": "TFL", "sacks": "SCK", "pressures": "PRESS",
    "passes_defended": "PD", "defensive_interceptions": "INT",
    "interception_return_yards": "INT YDS", "forced_fumbles": "FF", "fumble_recoveries": "FR",
    "field_goals_made": "FGM", "field_goals_attempted": "FGA", "extra_points_made": "XPM",
    "extra_points_attempted": "XPA", "punts": "PUNTS", "punt_yards": "PUNT YDS",
    "long_punt": "PUNT LNG", "punts_inside_20": "IN20", "punt_touchbacks": "TB",
}


def position_group(position):
    for index, (_, positions, _, _) in enumerate(POSITION_GROUPS):
        if position in positions:
            return index
    return None


def covered(columns):
    return {field for _, _, fields in columns for field in fields}


def stat_fields(line):
    return {f for f, v in line.items() if f not in {"position", "teams"} and numeric(v) and v}


def sort_key(field):
    return lambda item: (-g(item[1], field), ", ".join(item[1].get("teams", ())), item[0])


# ---- tables ----------------------------------------------------------------

def table(title, rows, columns, *, with_team=False, with_pos=False, level="##", total=None):
    lead = ["Player"] + (["Team"] if with_team else []) + (["Pos"] if with_pos else [])
    headers = lead + [header for header, _, _ in columns]
    lines = []
    if title:
        lines += [level + " " + title, ""]
    lines += ["| " + " | ".join(headers) + " |",
              "|" + "---|" * len(lead) + "---:|" * len(columns)]
    for player_id, line in rows:
        cells = [player_id]
        if with_team:
            cells.append(", ".join(line.get("teams", ())))
        if with_pos:
            cells.append(line.get("position", ""))
        cells += [str(fn(line)) for _, fn, _ in columns]
        lines.append("| " + " | ".join(cells) + " |")
    if total is not None:
        cells = ["**Team total**"] + [""] * (len(lead) - 1) + [str(fn(total)) for _, fn, _ in columns]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def combine(lines):
    """Team-total line: counters add, longest-play fields take the maximum."""
    total = {}
    for line in lines:
        for field, value in line.items():
            if not numeric(value):
                continue
            total[field] = max(total.get(field, 0), value) if field in LONG_FIELDS else total.get(field, 0) + value
    return total


def rows_with(players, fields, sort_field):
    rows = [(player_id, line) for player_id, line in players.items()
            if not str(player_id).startswith("__") and any(g(line, f) for f in fields)]
    rows.sort(key=sort_key(sort_field))
    return rows


def position_sections(players, *, with_team, level="##"):
    """Position first, then players.

    One table per position group with at least one game-active player, then
    returners, then any stored counter that falls outside a player's
    position columns (a receiver's coverage tackle, for example), so the
    readable view never drops a generated statistic.
    """
    grouped = {index: [] for index in range(len(POSITION_GROUPS))}
    extra_rows = []
    for player_id, line in players.items():
        if str(player_id).startswith("__"):
            continue
        fields = stat_fields(line)
        if not fields:
            continue
        index = position_group(line.get("position", ""))
        shown = RETURN_FIELDS | IMPLIED_FIELDS | {"games"}
        if index is None:
            extra = fields - shown
        else:
            grouped[index].append((player_id, line))
            extra = fields - shown - covered(POSITION_GROUPS[index][2])
        if extra:
            order = list(LABELS)
            extra_rows.append((player_id, line, sorted(extra, key=lambda f: order.index(f) if f in order else len(order))))

    lines = []
    for index, (title, _, columns, sort_field) in enumerate(POSITION_GROUPS):
        rows = grouped[index]
        if rows:
            rows.sort(key=sort_key(sort_field))
            lines += table(title, rows, (GAMES,) + columns, with_team=with_team, level=level)

    returners = rows_with(players, ("kick_returns", "punt_returns"), "return_yards")
    if returners:
        lines += table("Kick and punt returners", returners, (GAMES,) + RETURNS,
                       with_team=with_team, with_pos=True, level=level)

    if extra_rows:
        extra_rows.sort(key=lambda item: (", ".join(item[1].get("teams", ())), item[1].get("position", ""), item[0]))
        lines += [level + " Other statistics", "",
                  "Counters outside the player's position table, such as coverage "
                  "tackles by offensive players or statistics at a position without "
                  "its own table.", "",
                  "| Player | " + ("Team | " if with_team else "") + "Pos | Statistics |",
                  "|---|" + ("---|" if with_team else "") + "---|---|"]
        for player_id, line, extra in extra_rows:
            stats = ", ".join("%s %s" % (LABELS.get(f, f), g(line, f)) for f in extra)
            team = (", ".join(line.get("teams", ())) + " | ") if with_team else ""
            lines.append("| %s | %s%s | %s |" % (player_id, team, line.get("position", ""), stats))
        lines.append("")
    return lines
