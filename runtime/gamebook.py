"""Gamebook layout for 2014-onward box scores, rendered from a closed-game receipt.

This is the "Full stats for the game" block of the weekly game turn template
(foundation/templates/regular_season_output_template.md): scoring summary, team stats,
eleven individual tables per club, drive chart and snap counts. The 2013 box
score keeps its own layout in scripts/render_box_score.py; nothing here changes
a 2013 output.

Every number is read or added from receipt fields: the ``team_stats`` counters,
the per-player dictionaries, the ``drives`` rows (field order in
runtime.play_detail.DRIVE_SUMMARY_FIELDS) and the snap ``play_ledger`` of a full
receipt. Nothing is estimated. A row, column, table or line the receipt cannot
support is left out. Compact receipts (no ledger) lose every ledger-derived
item listed below.

Team stats rows and their sources
---------------------------------
Final score: final_score. Time of possession, drives: team_stats. Average drive
start: drives.start_spot. Points per drive: drives.points of the club's
touchdown and field-goal drives over its drives, kneel-only drives
(kneels >= scrimmage_plays) excluded. Total first downs: team_stats; by rushing
and by passing: ledger run/pass rows flagged first_down (scrambles count as
runs); by penalty: drives.chains[1] (the walked penalty first downs). Third
down: team_stats. Fourth down: ledger run/pass rows on down 4, converted when
first_down or touchdown. Total net yards = rushing yards + gross passing yards -
sack yards (team_stats and player sack_yards). Plays = rushing attempts +
pass attempts + sacks. Success rate: ledger rows with down and ydstogo, kneels
and spikes excluded, a turnover never successful. Explosive plays: ledger runs
of 10+ and completions of 20+. Tackled for loss: ledger run rows (not kneels)
with negative yards. Passing, rushing, punting, return, fumble and interception
counts: player counters. Kickoffs and touchbacks: ledger kickoff/free-kick rows.
Net punting average: ledger punt rows, gross minus return yards minus 20 per
touchback. Penalties: team_stats. Touchdowns: team_stats; the
rushing-passing-returns split: ledger touchdown rows. Extra points and field
goals: team_stats. Safeties: team_stats. Red zone: drives with a scrimmage snap
at the 20 or closer; goal to go: drives with a goal_to_go snap; both over the
drives that ended in a touchdown.

Omitted team stats rows (field not generated): punts had blocked, field goals
and extra points had blocked, two-point conversions.

Individual tables and their sources
-----------------------------------
Passing: counters, LNG from ledger completions. Rushing and receiving:
counters. Interceptions: counters, LNG and TD from ledger interception rows
(the row's tackler is the interceptor). Fumbles: FUM, LOST, OPP REC
(fumble_recoveries), FORCED; OWN REC omitted, since every generated fumble is
lost to the defense. Defense: TOT, SOLO, AST, SCK-YDS (sack yards from the
ledger's sack rows by tackler), TFL, PD, INT, FF, FR; QB HITS omitted (not
generated). Special teams defense: TOT (special_teams_tackles) only; SOLO,
AST, FF, FR and BLK are not generated for coverage. Kicking: counters, LNG and
the attempts line from ledger field-goal rows. Punting: counters, NET from the
ledger's punt rows. Punt returns: RET, YDS, AVG, LNG, TD (LNG and TD from the
ledger); FC omitted, since a fair catch is not attributed to a returner.
Kickoff returns: RET, YDS, AVG, LNG, TD.

Drive chart: drives rows (number, half/start_clock, start_kind, start_spot,
scrimmage_plays, net_yards, own_seconds, category). Snap counts: the kernel
2014.4 participation counters; the unit's snaps are the ledger's scrimmage rows
for that side (kick rows for special teams), or the largest counter when the
receipt has no ledger.

Checks raised as GamebookError: the scoring summary adds to the final score,
player passing and rushing yards add to the team counters, the first-down
split adds to the total, and the touchdown split adds to the team total.
"""
from __future__ import annotations

from .play_detail import DRIVE_SUMMARY_FIELDS, _period_clock
from .stat_tables import avg, combine, g, numeric, passer_rating, pct, thrown, time_text

SCRIMMAGE = ("run", "pass")
KICKOFFS = ("kickoff", "free_kick")
KICK_ROWS = KICKOFFS + ("punt", "field_goal", "extra_point")
UNATTRIBUTED = "Team / unattributed"
DASH = "—"

START_KIND = {
    "kickoff": "Kickoff", "kickoff_touchback": "Kickoff", "free_kick": "Free kick", "punt": "Punt",
    "interception": "Interception", "fumble_lost": "Fumble", "downs": "Downs", "missed_fg": "Missed field goal",
    "period_change": "Period change", "placement": "Placement",
}
END_KIND = {
    "touchdown": "Touchdown", "punt": "Punt", "interception": "Interception", "fumble_lost": "Fumble",
    "downs": "Downs", "safety": "Safety", "end_of_half": "End of half", "end_of_game": "End of game",
    "end_of_overtime": "End of overtime", "end_of_quarter": "End of quarter", "clock": "Clock expired",
}


class GamebookError(ValueError):
    """A generated table does not reconcile with its receipt."""


def nickname(club):
    return str(club).split()[-1]


def drives_of(receipt):
    return [dict(zip(DRIVE_SUMMARY_FIELDS, row)) for row in receipt.get("drives", ())]


def ledger_of(receipt):
    return sorted(receipt.get("play_ledger") or (), key=lambda r: r.get("sequence", 0))


def spot_text(spot):
    if spot is None:
        return DASH
    if spot == 50:
        return "50"
    return "Own %d" % (100 - spot) if spot > 50 else "Opp %d" % spot


def drive_clock(drive, game_type):
    """(period label, clock text) at which the drive began."""
    half, seconds = drive["half"], int(drive["start_clock"])
    if half == "OT":
        if game_type == "postseason":
            from .rules import RULES
            return _period_clock(seconds, overtime=("OT", RULES.postseason_ot_period_bound, RULES.postseason_ot_seconds))
        return "OT", "%d:%02d" % divmod(seconds, 60)
    if half == 1:
        quarter, left = (1, seconds - 2700) if seconds > 2700 else (2, seconds - 1800)
    else:
        quarter, left = (3, seconds - 900) if seconds > 900 else (4, seconds)
    return str(quarter), "%d:%02d" % divmod(max(left, 0), 60)


def _name(player_id):
    return UNATTRIBUTED if str(player_id).startswith("__") else str(player_id)


def _ratio(made, attempts):
    return "%d-%d, %s%%" % (made, attempts, "%.0f" % (100.0 * made / attempts)) if attempts else "%d-%d" % (made, attempts)


class GameView:
    """One receipt, indexed by club."""

    def __init__(self, receipt, lead_team):
        clubs = [receipt["away"], receipt["home"]]
        if lead_team not in clubs:
            raise ValueError("%s did not play in %s" % (lead_team, receipt["event_id"]))
        self.receipt = receipt
        self.clubs = [lead_team] + [c for c in clubs if c != lead_team]
        self.away, self.home = receipt["away"], receipt["home"]
        self.game_type = receipt.get("game_type", "regular")
        self.stats = {c: receipt["team_stats"][c] for c in self.clubs}
        self.players = {c: self.stats[c].get("players", {}) for c in self.clubs}
        self.totals = {c: combine(self.players[c].values()) for c in self.clubs}
        self.ledger = ledger_of(receipt)
        self.has_ledger = bool(self.ledger)
        self.drives = drives_of(receipt)
        self.club_drives = {c: [d for d in self.drives if d["team"] == c] for c in self.clubs}
        self.scrim = {c: [r for r in self.ledger if r["play_type"] in SCRIMMAGE and r["offense"] == c] for c in self.clubs}
        self.events = self.scoring_events() if self.has_ledger else []

    def other(self, club):
        return next(c for c in self.clubs if c != club)

    # ---- scoring --------------------------------------------------------

    def scoring_events(self):
        """Every score in game order: dicts with period, clock, club, play, drive, points."""
        rows = self.ledger
        by_number = {d["number"]: d for d in self.drives}
        events = []

        def drive_text(number):
            d = by_number.get(number)
            if d is None:
                return ""
            seconds = d.get("own_seconds")
            if seconds is None:
                seconds = int(d["start_clock"]) - int(d["end_clock"])
            return "%d-%d, %s" % (d["scrimmage_plays"], d["net_yards"], time_text(seconds))

        def try_after(index, club):
            for row in rows[index + 1:index + 3]:
                if row["play_type"] == "extra_point" and row["offense"] == club:
                    return row
            return None

        for index, row in enumerate(rows):
            kind = row["play_type"]
            touchdown = bool(row.get("touchdown"))
            if kind in SCRIMMAGE and touchdown and not row.get("turnover"):
                club, yards = row["offense"], row["result_yards"]
                if kind == "pass" and row.get("completion"):
                    play = "%s %d yd pass from %s" % (_name(row["target"]), yards, _name(row["passer"]))
                else:
                    play = "%s %d yd run" % (_name(row["runner"]), yards)
                drive = drive_text(row["drive"])
            elif touchdown and (kind in KICKOFFS or kind == "punt" or row.get("turnover")):
                club = row["defense"]
                carrier = row.get("returner") if kind in KICKOFFS + ("punt",) else row.get("tackler")
                label = {"kickoff": "kickoff", "free_kick": "free kick", "punt": "punt"}.get(
                    kind, row.get("turnover_type") or "turnover")
                play = "%s %d yd %s return" % (_name(carrier), row.get("return_yards") or 0, label)
                drive = ""
            elif kind == "field_goal" and row.get("made"):
                events.append({"seq": index, "period": row["period"], "clock": row["game_clock"], "club": row["offense"],
                               "play": "%s %d yd field goal" % (_name(row["kicker"]), row["distance"]),
                               "drive": drive_text(row["drive"]), "points": 3})
                continue
            else:
                continue
            points = 6
            xp = try_after(index, club)
            if xp is not None:
                if xp.get("made"):
                    play += " (%s kick)" % _name(xp["kicker"])
                    points += 1
                else:
                    play += " (kick failed)"
            events.append({"seq": index, "period": row["period"], "clock": row["game_clock"], "club": club,
                           "play": play, "drive": drive, "points": points})
        for d in self.drives:
            if d["category"] != "safety":
                continue
            snaps = [(i, r) for i, r in enumerate(rows) if r["drive"] == d["number"] and r["play_type"] in SCRIMMAGE]
            if not snaps:
                continue
            index, row = snaps[-1]
            carrier = row.get("passer") if row.get("sack") else (row.get("runner") or row.get("target") or row.get("passer"))
            play = "Safety, %s tackled in end zone" % _name(carrier)
            if row.get("tackler"):
                play += " by %s" % _name(row["tackler"])
            events.append({"seq": index, "period": row["period"], "clock": row["game_clock"], "club": row["defense"],
                           "play": play, "drive": "", "points": 2})
        events.sort(key=lambda e: e["seq"])
        running = {c: 0 for c in self.clubs}
        for event in events:
            running[event["club"]] += event["points"]
            event["score"] = dict(running)
        final = self.receipt["final_score"]
        if any(running[c] != final[c] for c in self.clubs):
            raise GamebookError("scoring summary %s does not add to the final score %s" % (running, final))
        return events

    def line_score(self):
        """Points by period, in game order, as [(label, {club: points})]."""
        periods = ["1", "2", "3", "4"]
        for event in self.events:
            label = str(event["period"])
            if label not in periods:
                periods.append(label)
        points = {label: {c: 0 for c in self.clubs} for label in periods}
        for event in self.events:
            points[str(event["period"])][event["club"]] += event["points"]
        return [(label, points[label]) for label in periods]

    # ---- ledger helpers ---------------------------------------------------

    def offensive_points(self, club):
        return sum(d["points"] for d in self.club_drives[club] if d["category"] in ("touchdown", "field_goal_attempt"))

    def counted_drives(self, club):
        return [d for d in self.club_drives[club] if not (d.get("kneels") and d["kneels"] >= d["scrimmage_plays"])]

    def first_down_split(self, club):
        rows = self.scrim[club]
        rushing = sum(1 for r in rows if r["play_type"] == "run" and r.get("first_down"))
        passing = sum(1 for r in rows if r["play_type"] == "pass" and r.get("first_down"))
        penalty = sum((d.get("chains") or [0, 0])[1] for d in self.club_drives[club])
        total = self.stats[club]["first_downs"]
        if rushing + passing + penalty != total:
            raise GamebookError("%s first downs %d-%d-%d do not add to %d" % (club, rushing, passing, penalty, total))
        return rushing, passing, penalty

    def fourth_down(self, club):
        rows = [r for r in self.scrim[club] if r.get("down") == 4]
        return sum(1 for r in rows if r.get("first_down") or r.get("touchdown")), len(rows)

    def success_rate(self, club):
        rows = [r for r in self.scrim[club] if r.get("down") and r.get("ydstogo") is not None
                and not r.get("kneel") and not r.get("spike")]
        if not rows:
            return None
        good = 0
        for r in rows:
            need = {1: 0.45, 2: 0.60}.get(r["down"], 1.0) * r["ydstogo"]
            good += int(not r.get("turnover") and r["result_yards"] >= need)
        return "%.0f%%" % (100.0 * good / len(rows))

    def explosive(self, club):
        rows = self.scrim[club]
        return (sum(1 for r in rows if r["play_type"] == "run" and not r.get("kneel") and r["rushing_yards"] >= 10)
                + sum(1 for r in rows if r["play_type"] == "pass" and r.get("completion") and r["passing_yards"] >= 20))

    def tackled_for_loss(self, club):
        rows = [r for r in self.scrim[club] if r["play_type"] == "run" and not r.get("kneel") and r["result_yards"] < 0]
        return len(rows), -sum(r["result_yards"] for r in rows)

    def kickoffs(self, club):
        rows = [r for r in self.ledger if r["play_type"] in KICKOFFS and r["offense"] == club]
        return len(rows), sum(1 for r in rows if r.get("touchback"))

    def punt_rows(self, club, punter=None):
        return [r for r in self.ledger if r["play_type"] == "punt" and r["offense"] == club
                and (punter is None or r.get("punter") == punter)]

    def net_punting(self, rows):
        if not rows:
            return None
        net = sum((r.get("gross") or 0) - (r.get("return_yards") or 0) - (20 if r.get("touchback") else 0) for r in rows)
        return "%.1f" % (net / len(rows))

    def touchdown_split(self, club):
        rows = [r for r in self.ledger if r.get("touchdown")]
        rushing = sum(1 for r in rows if r["play_type"] == "run" and r["offense"] == club and not r.get("turnover"))
        passing = sum(1 for r in rows if r["play_type"] == "pass" and r["offense"] == club and not r.get("turnover"))
        returns = sum(1 for r in rows if r["defense"] == club and (r["play_type"] not in SCRIMMAGE or r.get("turnover")))
        total = self.stats[club]["touchdowns"]
        if rushing + passing + returns != total:
            raise GamebookError("%s touchdowns %d-%d-%d do not add to %d" % (club, rushing, passing, returns, total))
        return rushing, passing, returns

    def zone_trips(self, club, goal_to_go):
        trips = scores = 0
        for d in self.club_drives[club]:
            snaps = [r for r in self.scrim[club] if r["drive"] == d["number"]]
            inside = any(r.get("goal_to_go") if goal_to_go else (r.get("yardline") is not None and r["yardline"] <= 20)
                         for r in snaps)
            if inside:
                trips += 1
                scores += int(d["category"] == "touchdown")
        return scores, trips

    def long_completion(self, passer):
        return max((r["passing_yards"] for r in self.ledger if r["play_type"] == "pass" and r.get("completion")
                    and r.get("passer") == passer), default=0)

    def sack_yards_by(self, defender):
        return -sum(r["result_yards"] for r in self.ledger if r["play_type"] == "pass" and r.get("sack")
                    and r.get("tackler") == defender)

    def interception_rows(self, defender):
        return [r for r in self.ledger if r.get("turnover_type") == "interception" and r.get("tackler") == defender]

    def return_rows(self, kinds, returner):
        return [r for r in self.ledger if r["play_type"] in kinds and r.get("returner") == returner]

    def field_goal_rows(self, kicker):
        return [r for r in self.ledger if r["play_type"] == "field_goal" and r.get("kicker") == kicker]

    def unit_snaps(self, club, side):
        field = {"offense": "offensive_snaps", "defense": "defensive_snaps", "special_teams": "special_teams_snaps"}[side]
        if self.has_ledger:
            if side == "offense":
                return len(self.scrim[club])
            if side == "defense":
                return len(self.scrim[self.other(club)])
            return sum(1 for r in self.ledger if r["play_type"] in KICK_ROWS)
        return max((g(line, field) for line in self.players[club].values()), default=0)


# ---- tables ------------------------------------------------------------------

def _table(headers, rows, align_first=True):
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "---|" * (1 if align_first else 0) + "---:|" * (len(headers) - (1 if align_first else 0))]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return lines + [""]


def scoring_summary(view):
    if not view.events:
        return []
    away, home = nickname(view.away), nickname(view.home)
    rows = [(e["period"], e["clock"], nickname(e["club"]), e["play"], e["drive"] or DASH,
             e["score"][view.away], e["score"][view.home]) for e in view.events]
    lines = ["#### Scoring summary", "",
             "| Qtr | Time | Team | Scoring play | Drive | %s | %s |" % (away, home),
             "|---|---|---|---|---|---:|---:|"]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return lines + [""]


def team_stats(view):
    s, t = view.stats, view.totals
    L = view.has_ledger
    final = view.receipt["final_score"]

    def pass_net(c):
        return s[c]["passing_yards"] - g(t[c], "sack_yards")

    def plays(c):
        return g(t[c], "rushing_attempts") + g(t[c], "pass_attempts") + g(t[c], "sacks_taken")

    def net_yards(c):
        return s[c]["rushing_yards"] + pass_net(c)

    def pair(a, b):
        return lambda c: "%d-%d" % (a(c), b(c))

    def drive_start(c):
        spots = [d["start_spot"] for d in view.club_drives[c] if d.get("start_spot") is not None]
        return spot_text(int(round(100 - sum(100 - x for x in spots) / len(spots)))) if spots else None

    def points_per_drive(c):
        drives = view.counted_drives(c)
        return "%.2f" % (view.offensive_points(c) / len(drives)) if drives else None

    def optional(field):
        return lambda c: s[c][field] if field in s[c] else None

    rows = [
        ("Score", "Final score", lambda c: final[c]),
        ("Possession", "Time of possession", lambda c: time_text(s[c]["time_of_possession"])),
        ("", "Drives", optional("drives")),
        ("", "Average drive start", drive_start if view.drives else None),
        ("", "Points per drive", points_per_drive if view.drives else None),
        ("First downs", "Total first downs", lambda c: s[c]["first_downs"]),
        ("", "By rushing", (lambda c: view.first_down_split(c)[0]) if L else None),
        ("", "By passing", (lambda c: view.first_down_split(c)[1]) if L else None),
        ("", "By penalty", (lambda c: view.first_down_split(c)[2]) if L else None),
        ("Downs", "Third down efficiency", lambda c: _ratio(s[c]["third_down_conversions"], s[c]["third_down_attempts"])),
        ("", "Fourth down efficiency", (lambda c: _ratio(*view.fourth_down(c))) if L else None),
        ("Total offense", "Total net yards", net_yards),
        ("", "Total offensive plays", plays),
        ("", "Average gain per play", lambda c: avg(net_yards(c), plays(c))),
        ("", "Success rate", view.success_rate if L else None),
        ("", "Explosive plays", view.explosive if L else None),
        ("Rushing", "Net yards rushing", lambda c: s[c]["rushing_yards"]),
        ("", "Rushing plays", lambda c: g(t[c], "rushing_attempts")),
        ("", "Average gain per rush", lambda c: avg(s[c]["rushing_yards"], g(t[c], "rushing_attempts"))),
        ("", "Tackled for loss, number and yards", (lambda c: "%d-%d" % view.tackled_for_loss(c)) if L else None),
        ("Passing", "Net yards passing", pass_net),
        ("", "Gross yards passing", lambda c: s[c]["passing_yards"]),
        ("", "Sacked, number and yards lost", pair(lambda c: g(t[c], "sacks_taken"), lambda c: g(t[c], "sack_yards"))),
        ("", "Attempts-completions-intercepted",
         lambda c: "%d-%d-%d" % (g(t[c], "pass_attempts"), g(t[c], "completions"), thrown(t[c]))),
        ("", "Average gain per pass play", lambda c: avg(pass_net(c), g(t[c], "pass_attempts") + g(t[c], "sacks_taken"))),
        ("Kicking game", "Kickoffs, number and touchbacks", (lambda c: "%d-%d" % view.kickoffs(c)) if L else None),
        ("", "Punts, number and average", lambda c: "%d-%s" % (g(t[c], "punts"), avg(g(t[c], "punt_yards"), g(t[c], "punts")))),
        ("", "Net punting average", (lambda c: view.net_punting(view.punt_rows(c))) if L else None),
        ("Returns", "Total return yardage", lambda c: g(t[c], "punt_return_yards") + g(t[c], "interception_return_yards")),
        ("", "Punt returns, number and yards", pair(lambda c: g(t[c], "punt_returns"), lambda c: g(t[c], "punt_return_yards"))),
        ("", "Kickoff returns, number and yards", pair(lambda c: g(t[c], "kick_returns"), lambda c: g(t[c], "kick_return_yards"))),
        ("", "Interception returns, number and yards",
         pair(lambda c: g(t[c], "defensive_interceptions"), lambda c: g(t[c], "interception_return_yards"))),
        ("Penalties", "Penalties, number and yards", pair(lambda c: s[c]["penalties"], lambda c: s[c]["penalty_yards"])),
        ("Ball security", "Turnovers", lambda c: s[c]["turnovers"]),
        ("", "Interceptions thrown", lambda c: thrown(t[c])),
        ("", "Fumbles, number and lost", pair(lambda c: g(t[c], "fumbles"), lambda c: g(t[c], "fumbles_lost"))),
        ("Scoring", "Touchdowns", lambda c: s[c]["touchdowns"]),
        ("", "Rushing-passing-returns", (lambda c: "%d-%d-%d" % view.touchdown_split(c)) if L else None),
        ("", "Extra points, made-attempts",
         (lambda c: "%d-%d" % (s[c]["extra_points_made"], s[c]["extra_point_attempts"]))
         if all("extra_point_attempts" in s[c] for c in view.clubs) else None),
        ("", "Field goals, made-attempts",
         (lambda c: "%d-%d" % (s[c]["field_goals"], s[c]["field_goal_attempts"]))
         if all("field_goal_attempts" in s[c] for c in view.clubs) else None),
        ("", "Safeties", optional("safeties")),
        ("Scoring chances", "Red zone efficiency", (lambda c: _ratio(*view.zone_trips(c, False))) if L else None),
        ("", "Goal to go efficiency", (lambda c: _ratio(*view.zone_trips(c, True))) if L else None),
    ]
    for c in view.clubs:
        if g(view.totals[c], "passing_yards") != s[c]["passing_yards"] or g(view.totals[c], "rushing_yards") != s[c]["rushing_yards"]:
            raise GamebookError("%s player yards do not add to the team counters" % c)

    lines = ["#### Team stats for the game", "",
             "| Group | Statistic | %s | %s |" % tuple(nickname(c) for c in view.clubs),
             "|---|---|---:|---:|"]
    group_shown = None
    for group, label, fn in rows:
        if fn is None:
            continue
        values = [fn(c) for c in view.clubs]
        if any(v is None for v in values):
            continue
        shown = group if group and group != group_shown else ""
        if group:
            group_shown = group
        lines.append("| %s | %s | %s | %s |" % (shown, label, values[0], values[1]))
    return lines + [""]


def _rows(players, fields, sort_field):
    rows = [(_name(p), line) for p, line in players.items() if any(g(line, f) for f in fields)]
    rows.sort(key=lambda item: (item[0] == UNATTRIBUTED, -g(item[1], sort_field), item[0]))
    return rows


def _block(title, headers, rows, columns, total=False):
    """One individual table: bold title, player rows, optional team total."""
    if not rows:
        return []
    body = [[name] + [fn(name, line) for fn in columns] for name, line in rows]
    if total:
        merged = combine(line for _, line in rows)
        body.append(["Team total"] + [fn(None, merged) for fn in columns])
    return ["**%s**" % title, ""] + _table(["Player"] + headers, body)


def individual(view, club):
    L = view.has_ledger
    p = view.players[club]
    lines = ["#### %s stats for the game" % nickname(club), ""]

    def c(field):
        return lambda name, line: g(line, field)

    # Passing
    rows_cache = _rows(p, ("pass_attempts", "sacks_taken"), "passing_yards")
    headers = ["CMP/ATT", "YDS", "AVG", "TD", "INT", "SCK-YDS"] + (["LNG"] if L else []) + ["RTG"]
    columns = [lambda n, l: "%d/%d" % (g(l, "completions"), g(l, "pass_attempts")), c("passing_yards"),
               lambda n, l: avg(g(l, "passing_yards"), g(l, "pass_attempts")), c("passing_touchdowns"),
               lambda n, l: thrown(l), lambda n, l: "%d-%d" % (g(l, "sacks_taken"), g(l, "sack_yards"))]
    if L:
        columns.append(lambda n, l: view.long_completion(n))
    columns.append(lambda n, l: passer_rating(l))
    lines += _block("Passing", headers, rows_cache, columns)

    # Rushing
    rows_cache = _rows(p, ("rushing_attempts",), "rushing_yards")
    lines += _block("Rushing", ["CAR", "YDS", "AVG", "LNG", "TD"], rows_cache,
                    [c("rushing_attempts"), c("rushing_yards"),
                     lambda n, l: avg(g(l, "rushing_yards"), g(l, "rushing_attempts")), c("long_rush"),
                     c("rushing_touchdowns")], total=True)

    # Receiving
    rows_cache = _rows(p, ("targets", "receptions"), "receiving_yards")
    lines += _block("Receiving", ["TGT", "REC", "YDS", "AVG", "LNG", "TD"], rows_cache,
                    [c("targets"), c("receptions"), c("receiving_yards"),
                     lambda n, l: avg(g(l, "receiving_yards"), g(l, "receptions")), c("long_reception"),
                     c("receiving_touchdowns")], total=True)

    # Interceptions
    rows_cache = _rows(p, ("defensive_interceptions",), "interception_return_yards")
    headers = ["INT", "YDS", "AVG"] + (["LNG", "TD"] if L else [])
    columns = [c("defensive_interceptions"), c("interception_return_yards"),
               lambda n, l: avg(g(l, "interception_return_yards"), g(l, "defensive_interceptions"))]
    if L:
        columns += [lambda n, l: max((r.get("return_yards") or 0 for r in view.interception_rows(n)), default=0),
                    lambda n, l: sum(1 for r in view.interception_rows(n) if r.get("touchdown"))]
    lines += _block("Interceptions", headers, rows_cache, columns)

    # Fumbles
    rows_cache = _rows(p, ("fumbles", "forced_fumbles", "fumble_recoveries"), "fumbles")
    lines += _block("Fumbles", ["FUM", "LOST", "OPP REC", "FORCED"], rows_cache,
                    [c("fumbles"), c("fumbles_lost"), c("fumble_recoveries"), c("forced_fumbles")])

    # Defense
    rows_cache = defenders = _rows(p, ("tackles", "sacks", "tackles_for_loss", "passes_defended",
                                       "defensive_interceptions", "forced_fumbles", "fumble_recoveries"), "tackles")

    def sack_cell(name, line):
        if not L:
            return "%.1f" % g(line, "sacks")
        yards = sum(view.sack_yards_by(n) for n, _ in defenders) if name is None else view.sack_yards_by(name)
        return "%.1f-%d" % (g(line, "sacks"), yards)

    lines += _block("Defense", ["TOT", "SOLO", "AST", "SCK-YDS" if L else "SCK", "TFL", "PD", "INT", "FF", "FR"],
                    rows_cache, [c("tackles"), c("solo_tackles"), c("assisted_tackles"), sack_cell,
                                 c("tackles_for_loss"), c("passes_defended"), c("defensive_interceptions"),
                                 c("forced_fumbles"), c("fumble_recoveries")], total=True)

    # Special teams defense
    rows_cache = _rows(p, ("special_teams_tackles",), "special_teams_tackles")
    lines += _block("Special teams defense", ["TOT"], rows_cache, [c("special_teams_tackles")])

    # Kicking
    rows_cache = _rows(p, ("field_goals_attempted", "extra_points_attempted"), "field_goals_made")
    headers = ["FGM", "FGA", "FG%"] + (["LNG"] if L else []) + ["XPM", "XPA", "PTS"]
    columns = [c("field_goals_made"), c("field_goals_attempted"),
               lambda n, l: pct(g(l, "field_goals_made"), g(l, "field_goals_attempted"))]
    if L:
        columns.append(lambda n, l: max((r["distance"] for r in view.field_goal_rows(n) if r.get("made")), default=0))
    columns += [c("extra_points_made"), c("extra_points_attempted"),
                lambda n, l: 3 * g(l, "field_goals_made") + g(l, "extra_points_made")]
    lines += _block("Kicking", headers, rows_cache, columns)
    if L and rows_cache:
        attempts = []
        for name, _ in rows_cache:
            for r in view.field_goal_rows(name):
                attempts.append("%s %d yd %s" % (name, r["distance"], "good" if r.get("made") else "no good"))
        lines += ["Field goal attempts: " + ("; ".join(attempts) if attempts else "none") + ".", ""]

    # Punting
    rows_cache = _rows(p, ("punts",), "punt_yards")
    headers = ["PUNTS", "YDS", "AVG"] + (["NET"] if L else []) + ["TB", "IN20", "LNG"]
    columns = [c("punts"), c("punt_yards"), lambda n, l: avg(g(l, "punt_yards"), g(l, "punts"))]
    if L:
        columns.append(lambda n, l: view.net_punting(view.punt_rows(club, n)) or DASH)
    columns += [c("punt_touchbacks"), c("punts_inside_20"), c("long_punt")]
    lines += _block("Punting", headers, rows_cache, columns)

    # Returns
    for title, count, yards, kinds in (("Punt returns", "punt_returns", "punt_return_yards", ("punt",)),
                                       ("Kickoff returns", "kick_returns", "kick_return_yards", KICKOFFS)):
        rows_cache = _rows(p, (count,), yards)
        headers = ["RET", "YDS", "AVG"] + (["LNG", "TD"] if L else [])
        columns = [c(count), c(yards), lambda n, l, count=count, yards=yards: avg(g(l, yards), g(l, count))]
        if L:
            columns += [lambda n, l, kinds=kinds: max((r.get("return_yards") or 0 for r in view.return_rows(kinds, n)), default=0),
                        lambda n, l, kinds=kinds: sum(1 for r in view.return_rows(kinds, n) if r.get("touchdown"))]
        lines += _block(title, headers, rows_cache, columns)
    return lines


def drive_chart(view):
    if not view.drives or any(d.get("start_spot") is None for d in view.drives):
        return []
    lines = ["#### Drive chart", ""]
    for club in view.clubs:
        rows = []
        for number, d in enumerate(view.club_drives[club], 1):
            period, clock = drive_clock(d, view.game_type)
            seconds = d.get("own_seconds")
            if seconds is None:
                seconds = int(d["start_clock"]) - int(d["end_clock"])
            end = d["category"]
            if end == "field_goal_attempt":
                end = "Field goal" if d.get("fg_made") else "Missed field goal"
            else:
                end = END_KIND.get(end, end)
            rows.append([number, period, clock, START_KIND.get(d.get("start_kind"), d.get("start_kind") or DASH),
                         spot_text(d["start_spot"]), d["scrimmage_plays"], d["net_yards"], time_text(seconds), end])
        lines += ["**%s**" % nickname(club), ""]
        lines += ["| # | Qtr | Time received | How obtained | Began at | Plays | Net yards | Time of possession | How given up |",
                  "|---:|---|---|---|---|---:|---:|---|---|"]
        lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
        lines.append("")
    return lines


def snap_counts(view):
    fields = ("offensive_snaps", "defensive_snaps", "special_teams_snaps")
    if not any(f in line for c in view.clubs for line in view.players[c].values() for f in fields):
        return []
    lines = ["#### Snap counts", ""]
    for club in view.clubs:
        units = {f: view.unit_snaps(club, side) for f, side in zip(fields, ("offense", "defense", "special_teams"))}
        rows = [(name, line) for name, line in view.players[club].items() if any(g(line, f) for f in fields)]
        rows.sort(key=lambda item: tuple(-g(item[1], f) for f in fields) + (str(item[0]),))
        body = []
        for name, line in rows:
            cells = [_name(name), line.get("position", "")]
            for f in fields:
                snaps = g(line, f)
                cells.append("%d (%d%%)" % (snaps, round(100.0 * snaps / units[f])) if snaps and units[f] else "0")
            body.append(cells)
        lines += ["**%s**" % nickname(club), ""]
        lines += ["| Player | POS | Offense | Defense | Special teams |", "|---|---|---:|---:|---:|"]
        lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in body]
        lines.append("")
    return lines


def render(receipt, lead_team):
    view = GameView(receipt, lead_team)
    lines = scoring_summary(view) + team_stats(view)
    for club in view.clubs:
        lines += individual(view, club)
    lines += drive_chart(view) + snap_counts(view)
    text = "\n".join(lines).rstrip("\n")
    if "None" in text.split() or "nan" in text.lower().split():
        raise GamebookError("unrendered cell in the gamebook")
    return text


def line_score_table(receipt):
    """The Section 3 line score (away first) as Markdown, from the scoring summary."""
    view = GameView(receipt, receipt["home"])
    periods = view.line_score()
    header = ["Team"] + [label for label, _ in periods] + ["Final"]
    rows = []
    for club in (view.away, view.home):
        rows.append([nickname(club)] + [points[club] for _, points in periods] + [receipt["final_score"][club]])
    return "\n".join(_table(header, rows))
