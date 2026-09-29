#!/usr/bin/env python3
"""Rebuild the public season-stat views from closed-game stat receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.bands import (
    KERNEL_2013_6_LABEL, KNOWN_DETECTION_BOUND, LEGACY_LABEL, audit, audit_drive_model, audit_field_position,
    coherence, cohorts, current_cohorts, known_detections, known_status,
)
from runtime.stat_tables import (
    POSITION_GROUPS, avg, combine, g, pct, position_sections, rating_value,
    time_text,
)
from runtime.statbook import aggregate_receipts, leaders

# NFL passing qualifier: 14 attempts per team game (Wikipedia, "Passer
# rating"; NFL leaderboard minimum). Rushing and receiving average
# qualifiers are not applied until verified from a dated source.
PASSING_ATTEMPTS_PER_TEAM_GAME = 14


def load_receipts(directory):
    receipts = []
    for path in sorted(directory.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            receipts.append(json.load(handle))
    return receipts


def through_line(book):
    if not book.get("receipt_count"):
        return "**Through:** no regular-season game has closed."
    return "**Through:** Week %d." % book["through_week"]


def coverage_line(book, team_id=None):
    if not book.get("receipt_count"):
        return "**Coverage:** no closed-game receipts yet; every table is empty."
    if not book["coverage_complete"]:
        return (
            "**Coverage:** PARTIAL. One or more games lack a complete stat receipt. "
            "Tables show only preserved statistics and are not complete league rankings."
        )
    if team_id is not None:
        if not book.get("team_player_attribution_complete", {}).get(team_id, True):
            return (
                "**Coverage:** team totals complete; player attribution PARTIAL for this "
                "club because a branch-roster correction left exact attribution unknowable."
            )
        return "**Coverage:** complete for this club's closed games."
    if not book.get("player_attribution_complete", True):
        return (
            "**Coverage:** team totals complete; player attribution PARTIAL for one or "
            "more clubs. Known player lines are shown; formal league rankings are withheld."
        )
    return "**Coverage:** complete for every closed game."


def header(title, version, book, team_id=None, intro=None):
    lines = ["# " + title, "", "**Version:** `%s`" % version, through_line(book),
             coverage_line(book, team_id), ""]
    if intro:
        lines += [intro, ""]
    return lines


def no_games(book):
    return [] if book.get("receipt_count") else ["No regular-season game has closed.", ""]


# ---- player views ------------------------------------------------------------

def team_markdown(year, team_id, book):
    lines = header(
        "%s %s player statistics" % (year, team_id),
        "%s-W%02d-TEAM-PLAYER-STATS" % (year, book["through_week"]), book, team_id,
        "By position, then player. G counts games on the game-day active list.",
    ) + no_games(book)
    team = book["teams"].get(team_id)
    if team:
        lines += position_sections(team["players"], with_team=False)
    return "\n".join(lines)


def league_markdown(year, book):
    lines = header(
        "%s NFL player statistics by position" % year,
        "%s-W%02d-LEAGUE-PLAYER-STATS" % (year, book["through_week"]), book, None,
        "Every club's players, one league-wide table per position, each sorted by "
        "that position's primary production. G counts games on the game-day active list.",
    ) + no_games(book)
    return "\n".join(lines + position_sections(book.get("players", {}), with_team=True))


def all_players_markdown(year, book):
    lines = header(
        "%s NFL rosters and player statistics" % year,
        "%s-W%02d-ALL-PLAYER-STATS" % (year, book["through_week"]), book, None,
        "Club by club, then position, then player: every player who has been on a "
        "game-day active list, with his position's statistics. G counts games active.",
    ) + no_games(book)
    for team_id in sorted(book.get("teams", {})):
        sections = position_sections(book["teams"][team_id].get("players", {}), with_team=False, level="###")
        if sections:
            lines += ["## " + team_id, ""] + sections
    return "\n".join(lines)


# ---- leaders -----------------------------------------------------------------

LEADER_GROUPS = (
    ("Quarterbacks", (("Passing yards", "passing_yards"), ("Passing touchdowns", "passing_touchdowns"),
                      ("Completions", "completions"))),
    ("Running backs", (("Rushing yards", "rushing_yards"), ("Rushing touchdowns", "rushing_touchdowns"),
                       ("Receiving yards", "receiving_yards"))),
    ("Wide receivers", (("Receptions", "receptions"), ("Receiving yards", "receiving_yards"),
                        ("Receiving touchdowns", "receiving_touchdowns"))),
    ("Tight ends", (("Receptions", "receptions"), ("Receiving yards", "receiving_yards"),
                    ("Receiving touchdowns", "receiving_touchdowns"))),
    ("Defensive line", (("Sacks", "sacks"), ("Tackles for loss", "tackles_for_loss"),
                        ("Tackles", "tackles"))),
    ("Linebackers", (("Tackles", "tackles"), ("Sacks", "sacks"),
                     ("Tackles for loss", "tackles_for_loss"))),
    ("Defensive backs", (("Interceptions", "defensive_interceptions"),
                         ("Passes defended", "passes_defended"), ("Tackles", "tackles"))),
    ("Kickers", (("Field goals made", "field_goals_made"), ("Extra points made", "extra_points_made"))),
    ("Punters", (("Punt yards", "punt_yards"), ("Punts inside the 20", "punts_inside_20"))),
)
OVERALL_LEADERS = (
    ("Passing yards", "passing_yards"), ("Rushing yards", "rushing_yards"),
    ("Receiving yards", "receiving_yards"), ("Tackles", "tackles"),
    ("Sacks", "sacks"), ("Interceptions", "defensive_interceptions"),
)


def ranked(rows, value, limit=10):
    """Rank rows (player, line) by value; equal values share a place."""
    rows = sorted(rows, key=lambda item: (-value(item[1]), item[0]))[:limit]
    out, place = [], 0
    for index, (player_id, line) in enumerate(rows, 1):
        if index == 1 or value(line) != value(rows[index - 2][1]):
            place = index
        out.append((place, player_id, line))
    return out


def leader_table(title, rows, fmt, *, with_pos=False, level="###"):
    lines = [level + " " + title, "",
             "| Rank | Player | Team |" + (" Pos |" if with_pos else "") + " Total |",
             "|---:|---|---|" + ("---|" if with_pos else "") + "---:|"]
    for place, player_id, line in rows:
        pos = (" %s |" % line.get("position", "")) if with_pos else ""
        lines.append("| %d | %s | %s |%s %s |" % (
            place, player_id, ", ".join(line.get("teams", ())), pos, fmt(line)))
    lines.append("")
    return lines


def team_games(book, line):
    return max((book["teams"].get(t, {}).get("games", 0) for t in line.get("teams", ())), default=0)


def leaders_markdown(year, book):
    lines = header(
        "%s NFL statistical leaders" % year,
        "%s-W%02d-LEADERS" % (year, book["through_week"]), book,
    )
    if not book.get("receipt_count"):
        return "\n".join(lines + ["No regular-season game has closed, so no leader exists yet.", ""])
    if not book["coverage_complete"] or not book.get("player_attribution_complete", True):
        return "\n".join(lines + [
            "League rankings are withheld while player attribution is incomplete. "
            "Known lines remain in `league_player_stats.md`.", ""])

    players = {p: l for p, l in book.get("players", {}).items() if not str(p).startswith("__")}
    lines += ["By position, then category; each list ranks only players at that position. "
              "Passer-rate leaders and overall leaders follow.", ""]
    for group_title, categories in LEADER_GROUPS:
        positions = next(p for title, p, _, _ in POSITION_GROUPS if title == group_title)
        pool = [(p, l) for p, l in players.items() if l.get("position", "") in positions]
        lines += ["## " + group_title, ""]
        for title, field in categories:
            rows = ranked([(p, l) for p, l in pool if g(l, field)], lambda l, f=field: g(l, f))
            lines += leader_table(title, rows, lambda l, f=field: g(l, f))

    qualified = [(p, l) for p, l in players.items()
                 if g(l, "pass_attempts") and
                 g(l, "pass_attempts") >= PASSING_ATTEMPTS_PER_TEAM_GAME * team_games(book, l)]
    lines += ["## Passer rate leaders", "",
              "Qualified passers: at least %d attempts per team game." % PASSING_ATTEMPTS_PER_TEAM_GAME, ""]
    for title, value, fmt in (
        ("Passer rating", rating_value, lambda l: "%.1f" % rating_value(l)),
        ("Completion percentage", lambda l: g(l, "completions") / g(l, "pass_attempts"),
         lambda l: pct(g(l, "completions"), g(l, "pass_attempts"))),
        ("Yards per attempt", lambda l: g(l, "passing_yards") / g(l, "pass_attempts"),
         lambda l: avg(g(l, "passing_yards"), g(l, "pass_attempts"))),
    ):
        lines += leader_table(title, ranked(qualified, value), fmt)

    lines += ["## All positions", ""]
    for title, field in OVERALL_LEADERS:
        rows = [(r["player_id"], players[r["player_id"]]) for r in leaders(book, field, limit=10)]
        lines += leader_table(title, ranked(rows, lambda l, f=field: g(l, f)), lambda l, f=field: g(l, f),
                              with_pos=True)
    return "\n".join(lines)


# ---- team views --------------------------------------------------------------

def _spot_text(spot):
    """yardline_100 as a field position: 'own 25', 'opp 40' or 'midfield'."""
    if spot is None:
        return "—"
    spot = round(spot)
    if spot == 50:
        return "midfield"
    return "own %d" % (100 - spot) if spot > 50 else "opp %d" % spot


def field_position_rows(receipts):
    """Per-club field position from kernel 2013.7 receipts (drives summary)."""
    from runtime.bands import _drives
    clubs = {}
    for receipt in receipts:
        drives = [d for d in _drives(receipt) if d.get("start_spot") is not None]
        if not drives:
            continue
        teams = list(receipt.get("team_stats", {}))
        for team in teams:
            row = clubs.setdefault(team, {"games": 0, "drives": 0, "start": 0, "opp_drives": 0, "opp_start": 0,
                                          "punts": 0, "punt_net": 0, "tb": 0, "kicks": 0, "fourth": [0, 0]})
            row["games"] += 1
        for d in drives:
            own = clubs[d["team"]]
            own["drives"] += 1
            own["start"] += d["start_spot"]
            for team in teams:
                if team != d["team"]:
                    clubs[team]["opp_drives"] += 1
                    clubs[team]["opp_start"] += d["start_spot"]
            if d["category"] == "punt" and d.get("next_start") is not None:
                own["punts"] += 1
                own["punt_net"] += d["end_spot"] - (100 - d["next_start"])
            if d.get("chains"):
                own["fourth"][0] += d["chains"][4]
                own["fourth"][1] += d["chains"][5]
    return clubs


def team_stats_markdown(year, book, receipts=()):
    lines = header(
        "%s NFL team statistics" % year,
        "%s-W%02d-TEAM-STATS" % (year, book["through_week"]), book, None,
        "Per-game team statistics from closed-game receipts. Plays are rushing "
        "attempts plus dropbacks. Records and tiebreakers live in `../standings.md`.",
    ) + no_games(book)
    clubs = [(t, d) for t, d in book.get("teams", {}).items() if d.get("games")]
    if not clubs:
        return "\n".join(lines)

    def per(value, games):
        return "%.1f" % (value / games)

    def third(stats):
        return "%d/%d" % (stats["third_down_conversions"], stats["third_down_attempts"])

    def third_pct(stats):
        return pct(stats["third_down_conversions"], stats["third_down_attempts"])

    lines += ["## Offense", "",
              "| Team | G | PTS/G | YDS/G | PLAYS/G | Y/P | PASS/G | RUSH/G | 1D/G | 3RD | 3RD% | GIVE | SCK | PEN/G | PEN YDS/G | TOP/G |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    offense = []
    for team_id, data in clubs:
        n, t = data["games"], data["team_stats"]
        yards = t["passing_yards"] + t["rushing_yards"]
        offense.append((-yards / n, team_id, (
            team_id, n, per(t["points"], n), per(yards, n), per(data["plays"], n),
            avg(yards, data["plays"]), per(t["passing_yards"], n), per(t["rushing_yards"], n),
            per(t["first_downs"], n), third(t), third_pct(t), t["turnovers"], t["sacks_allowed"],
            per(t["penalties"], n), per(t["penalty_yards"], n), time_text(t["time_of_possession"] / n))))
    for _, _, row in sorted(offense):
        lines.append("| " + " | ".join(str(v) for v in row) + " |")

    lines += ["", "## Defense", "",
              "Opponent production per game. SCK counts sacks by the defense; TAKE counts takeaways.", "",
              "| Team | G | PTS/G | YDS/G | PLAYS/G | Y/P | PASS/G | RUSH/G | 1D/G | 3RD | 3RD% | TAKE | SCK | TO +/- |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    defense = []
    for team_id, data in clubs:
        n, o, t = data["games"], data["opponent_stats"], data["team_stats"]
        yards = o["passing_yards"] + o["rushing_yards"]
        margin = o["turnovers"] - t["turnovers"]
        defense.append((yards / n, team_id, (
            team_id, n, per(o["points"], n), per(yards, n), per(data["opponent_plays"], n),
            avg(yards, data["opponent_plays"]), per(o["passing_yards"], n), per(o["rushing_yards"], n),
            per(o["first_downs"], n), third(o), third_pct(o), o["turnovers"], o["sacks_allowed"],
            "%+d" % margin if margin else "0")))
    for _, _, row in sorted(defense):
        lines.append("| " + " | ".join(str(v) for v in row) + " |")

    lines += ["", "## Special teams", "",
              "| Team | G | FGM | FGA | FG% | XPM | XPA | PUNTS | PUNT AVG | IN20 | KR | KR AVG | PR | PR AVG |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for team_id, data in sorted(clubs):
        s = combine(data.get("players", {}).values())
        lines.append("| " + " | ".join(str(v) for v in (
            team_id, data["games"], g(s, "field_goals_made"), g(s, "field_goals_attempted"),
            pct(g(s, "field_goals_made"), g(s, "field_goals_attempted")),
            g(s, "extra_points_made"), g(s, "extra_points_attempted"), g(s, "punts"),
            avg(g(s, "punt_yards"), g(s, "punts")), g(s, "punts_inside_20"),
            g(s, "kick_returns"), avg(g(s, "kick_return_yards"), g(s, "kick_returns")),
            g(s, "punt_returns"), avg(g(s, "punt_return_yards"), g(s, "punt_returns")))) + " |")
    lines.append("")

    drive_clubs = [(t, d) for t, d in clubs if d.get("drive_model_games")]
    if drive_clubs:
        lines += ["## Drives and kicking — Week 4 onward (kernels 2013.6-2013.7)", "",
                  "Counted only from games closed under kernel 2013.6 or later; Weeks 1-3 receipts "
                  "(kernels 2013.4/2013.5) do not carry these counters and are not included. "
                  "G counts those games only. From kernel 2013.7 (after Week 8) a punt return is a "
                  "punt whose 2012 play-by-play record was returned (not a fair catch, "
                  "downed, out-of-bounds or touchback punt).", "",
                  "| Team | G | DRIVES | FGA | XPA | XPM | SAF | DOWNS | CLOCK | KO |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for team_id, data in sorted(drive_clubs):
            t = data["team_stats"]
            lines.append("| " + " | ".join(str(v) for v in (
                team_id, data["drive_model_games"], t.get("drives", 0), t.get("field_goal_attempts", 0),
                t.get("extra_point_attempts", 0), t.get("extra_points_made", 0), t.get("safeties", 0),
                t.get("turnovers_on_downs", 0), t.get("clock_expired_drives", 0),
                t.get("kickoffs", 0))) + " |")
        lines.append("")

    spots = field_position_rows(receipts)
    if spots:
        lines += ["## Field position — kernel 2013.7 games (after Week 8)", "",
                  "Kernel 2013.7 games only: average drive start for the club and for its "
                  "opponents, realized punt net (line of scrimmage to the receiving start, "
                  "returns and enforcement included) and fourth-down attempts and conversions "
                  "inside drives (from the real 2012 drive chains; a failed attempt ending a "
                  "drive is a turnover on downs). G counts those games only.", "",
                  "| Team | G | DRIVES | AVG START | OPP AVG START | PUNTS | NET PUNT | 4TH ATT | 4TH CONV |",
                  "|---|---:|---:|---|---|---:|---:|---:|---:|"]
        for team_id, row in sorted(spots.items()):
            lines.append("| " + " | ".join(str(v) for v in (
                team_id, row["games"], row["drives"],
                _spot_text(row["start"] / row["drives"]) if row["drives"] else "—",
                _spot_text(row["opp_start"] / row["opp_drives"]) if row["opp_drives"] else "—",
                row["punts"], avg(row["punt_net"], row["punts"]), row["fourth"][0], row["fourth"][1])) + " |")
        lines.append("")
    return "\n".join(lines)


def play_calls_markdown(year, team_id, book):
    lines = header(
        "%s %s descriptive call labels" % (year, team_id),
        "%s-W%02d-PLAY-CALL-STATS" % (year, book["through_week"]), book, team_id,
        "Descriptive labels on the generated snaps, from the snap ledger. From kernel "
        "2013.7 (after Week 8) each label fits that snap's ball carrier or target: it is drawn "
        "after the carrier or target is fixed, from the weekly sheet's calls whose "
        "declared (or 2013 family-map) groups include him. A label is not Stone's call "
        "selection or frequency, and per-label yardage is not evidence of a concept's "
        "effectiveness. Generic, kneel, spike and scramble labels are separate rows; a "
        "quarterback scramble is counted under the pass label it carries. Kernels "
        "2013.4-2013.6 drew each snap's label at random from the sheet's calls of that "
        "run or pass type, independent of the ball carrier (ledger Entry 41), so Weeks "
        "1-8 rows show label assignment only. Y/P is yards per snap; 20+ counts gains "
        "of 20 yards or more; NEG counts snaps that lost yardage.",
    ) + no_games(book)
    calls = book.get("play_calls", {}).get(team_id, {})
    if not calls:
        return "\n".join(lines)
    lines += ["| Call | Family | SNAPS | RUNS | DB | CMP | ATT | CMP% | YDS | Y/P | 20+ | NEG | TD | TO | SCK |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, line in sorted(calls.items(), key=lambda item: (-g(item[1], "snaps"), item[0])):
        lines.append("| " + " | ".join(str(v) for v in (
            name, line.get("family", name), g(line, "snaps"), g(line, "runs"), g(line, "dropbacks"),
            g(line, "completions"), g(line, "pass_attempts"),
            pct(g(line, "completions"), g(line, "pass_attempts")), g(line, "yards"),
            avg(g(line, "yards"), g(line, "snaps")), g(line, "explosive_plays"),
            g(line, "negative_plays"), g(line, "touchdowns"), g(line, "turnovers"),
            g(line, "sacks"))) + " |")
    lines.append("")
    return "\n".join(lines)


POINTS_NOTE = (
    "Points: non-offensive touchdowns, their tries and two-point tries are not "
    "modelled by design (about 1.7-2.0 points per team game below the 2012 centre); "
    "the ±5.0 tolerance is deliberately not tightened. Yards per team game are net "
    "of sack yards, as the 2012 centre is (corrected in Entry 55; earlier audits "
    "compared gross passing yards and read about 14 yards high)."
)


def _band_table(rows, cohort=None):
    """A band table; a cohort's known detections (runtime.bands) are labelled."""
    fmt = lambda v: "—" if v is None else ("%.3f" % v if abs(v) < 2 else "%.1f" % v)
    lines = ["| Metric | Observed | 2012 band centre | Tolerance | Status |",
             "|---|---:|---:|---:|---|"]
    for row in rows:
        metric, observed, band, tolerance, _ = row
        spread = "—" if tolerance is None else "±" + fmt(tolerance)
        lines.append("| %s | %s | %s | %s | %s |" % (metric, fmt(observed), fmt(band), spread,
                                                     known_status(row, cohort)))
    return lines


def _known_detection_lines(cohort):
    known = known_detections(cohort)
    if not known:
        return []
    lines = ["Known detections (`runtime/bands.py` `KNOWN_DETECTIONS`): graded rows with a "
             "documented design cause, accepted rather than tuned. Each stays graded; OUTSIDE "
             "within %dx its tolerance is the documented detection, and beyond that it is "
             "investigated. No centre, tolerance, coefficient or pool was changed." % KNOWN_DETECTION_BOUND, ""]
    lines += ["- %s: %s." % (metric, note) for metric, note in known.items()]
    return lines + [""]


def _week_span(receipts, empty):
    weeks = sorted({int(r["week"]) for r in receipts if str(r.get("week", "")).isdigit()})
    if not weeks:
        return empty
    return "Week %d" % weeks[0] if weeks[0] == weeks[-1] else "Weeks %d-%d" % (weeks[0], weeks[-1])


def _coherence_lines(checked, counts):
    lines = ["| Class | Count | Status |", "|---|---:|---|"]
    for cls, count, measurable in counts:
        if not checked or not measurable:
            lines.append("| %s | — | not measurable |" % cls.replace("_", " "))
        else:
            lines.append("| %s | %d | %s |" % (cls.replace("_", " "), count, "OUTSIDE" if count else "WITHIN"))
    return lines


def _current_cohort_lines(version, members, empty):
    """One field-position-era cohort (kernel 2013.7, 2013.8, ...) of the audit."""
    team_games, rows = audit(members)
    drive_games, drive_rows = audit_drive_model(members)
    fp_games, fp_rows = audit_field_position(members)
    checked, counts = coherence(members)
    lines = [
        "## Kernel %s cohort (%s)" % (version, _week_span(members, empty)), "",
        "**Team-games audited:** %d. Carry shares exclude kneels, as in the 2012 "
        "baseline." % team_games, "",
    ] + _band_table(rows) + ["", POINTS_NOTE, "",
        "### Drive model rows", "",
        "Centres from the 2012 drive model (nflverse drive definition) and period totals; "
        "tolerance is three standard errors at the observed sample.", "",
    ] + _band_table(drive_rows, version) + [""] + _known_detection_lines(version) + [
        "### Field-position rows", "",
        "Centres from the 2012 field-position model's band_centres. Rates use "
        "3*sqrt(p(1-p)/n) and means 3*sd/sqrt(n) with the 2012 sd; a row reads "
        "INSUFFICIENT SAMPLE below 30 events. INFORMATIONAL rows are shapes, not grades.", "",
    ] + _band_table(fp_rows) + [
        "",
        "### Ledger coherence", "",
        "Zero-tolerance counts from `runtime.play_detail.check_ledger` (15 original and "
        "17 kernel 2013.7 spot and label classes). Games checked: %d. The kick-row and "
        "label classes need the full snap ledger." % checked, "",
    ] + _coherence_lines(checked, counts) + [""]
    return lines


def calibration_audit_markdown(year, receipts, book):
    legacy, kernel_2013_6, current = cohorts(receipts)
    lines = [
        "# %s statistical band audit" % year, "",
        "**Version:** `%s-W%02d-BAND-AUDIT`" % (year, book["through_week"]),
        through_line(book), "",
        "League-wide receipts compared with the sourced 2012 shapes in "
        "`library/data/2012_nfl_aggregate_baseline.json`, "
        "`library/data/2012_nfl_position_usage_baseline.json`, "
        "`library/data/2012_nfl_drive_model.json` and "
        "`library/data/2012_nfl_field_position_model.json`. This is a defect "
        "detector for engine code and TeamInputs. An OUTSIDE row is investigated; "
        "it never reruns, selects or edits a closed game. Receipts are split into "
        "cohorts by kernel version; grading starts at 16 team-games per cohort.", "",
    ]
    team_games, rows = audit(legacy)
    lines += [
        "## Legacy cohort: kernels 2013.4/2013.5",
        "",
        "**Status:** %s." % LEGACY_LABEL,
        "**Team-games audited:** %d." % team_games, "",
    ] + _band_table(rows) + [
        "",
        "Drive-model rows and ledger coherence: not measurable for this cohort "
        "(legacy receipts carry no drives summary or kicking-attempt counters).", "",
    ]
    team_games, rows = audit(kernel_2013_6)
    drive_games, drive_rows = audit_drive_model(kernel_2013_6)
    checked, counts = coherence(kernel_2013_6)
    lines += [
        "## Kernel 2013.6 cohort (%s, detection only)" % _week_span(kernel_2013_6, "Week 4 onward"), "",
        "**Status:** %s." % KERNEL_2013_6_LABEL,
        "**Team-games audited:** %d." % team_games, "",
    ] + _band_table(rows) + ["", POINTS_NOTE, "",
        "### Drive model rows", "",
        "Centres from the 2012 drive model (nflverse drive definition) and period totals; "
        "tolerance is three standard errors at the observed sample.", "",
    ] + _band_table(drive_rows, "2013.6") + [""] + _known_detection_lines("2013.6") + [
        "### Ledger coherence", "",
        "Zero-tolerance counts from `runtime.play_detail.check_ledger` over every "
        "receipt's drives summary plus the full snap ledgers. Games checked: %d. The "
        "kernel 2013.7 spot and label classes are not measurable for this cohort "
        "(its receipts carry no start spots)." % checked, "",
    ] + _coherence_lines(checked, counts) + [""]
    split = dict(current_cohorts(current))
    lines += _current_cohort_lines("2013.7", split.pop("2013.7", []), "after Week 8; no game closed yet")
    for version, members in sorted(split.items(), key=lambda item: tuple(int(v) for v in item[0].split("."))):
        lines += _current_cohort_lines(version, members, "no game closed yet")
    return "\n".join(lines)


# ---- storage -----------------------------------------------------------------

def _nonzero(line, keep):
    kept = {key: line[key] for key in keep if key in line}
    kept.update({key: value for key, value in line.items()
                 if key not in keep and isinstance(value, (int, float))
                 and not isinstance(value, bool) and value != 0})
    return kept


def compact_book_for_storage(book):
    """The aggregated book without mechanically implied zero fields."""
    compact = {key: value for key, value in book.items() if key not in {"teams", "players"}}
    compact["teams"] = {}
    for team_id, team in book.get("teams", {}).items():
        row = {key: team[key] for key in ("games", "plays", "opponent_plays", "team_stats", "opponent_stats")}
        row["players"] = {}
        for player_id, line in team.get("players", {}).items():
            kept = _nonzero(line, ("position",))
            if len(kept) > 1 or str(player_id).startswith("__"):
                row["players"][player_id] = kept
        compact["teams"][team_id] = row
    compact["players"] = {}
    for player_id, line in book.get("players", {}).items():
        kept = _nonzero({**line, "teams": list(line.get("teams", ()))}, ("position", "teams"))
        if len(kept) > 2:
            compact["players"][player_id] = kept
    return compact


def render_views(year, team, receipts):
    from runtime.seasons import require_receipt_season
    require_receipt_season(receipts, year)
    """Every generated stat file, keyed by file name, from one receipt set."""
    book = aggregate_receipts(receipts)
    return {
        "season_totals.json": json.dumps(compact_book_for_storage(book), sort_keys=True, separators=(",", ":")) + "\n",
        "team_player_stats.md": team_markdown(year, team, book),
        "league_player_stats.md": league_markdown(year, book),
        "all_player_stats.md": all_players_markdown(year, book),
        "league_leaders.md": leaders_markdown(year, book),
        "play_call_stats.md": play_calls_markdown(year, team, book),
        "team_stats.md": team_stats_markdown(year, book, receipts),
        "calibration_audit.md": calibration_audit_markdown(year, receipts, book),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("year", type=int)
    parser.add_argument("--team", required=True, help="Exact team_id used by game receipts")
    args = parser.parse_args()

    stats_dir = ROOT / "career" / str(args.year) / "stats"
    from runtime.seasons import SeasonPaths
    stats_dir = SeasonPaths(args.year, ROOT).stats
    receipts = load_receipts(stats_dir / "game_receipts")
    views = render_views(args.year, args.team, receipts)
    stats_dir.mkdir(parents=True, exist_ok=True)
    for name, text in views.items():
        (stats_dir / name).write_text(text, encoding="utf-8")
    print("rendered %d stat views from %d receipts" % (len(views), len(receipts)))


if __name__ == "__main__":
    main()
