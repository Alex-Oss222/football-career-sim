#!/usr/bin/env python3
"""Render the user's team stat tracker from closed-game receipts.

  python scripts/render_team_tracker.py YEAR [--team "Jacksonville Jaguars"] [--check]

Writes career/YEAR/stats/team_tracker/: README.md (team info, depth chart,
game index, season and postseason totals, advanced totals, awards) and one
file per game under games/ with that game's tables plus the running totals
through it. Every number is arithmetic on the stored receipt counters; nothing
is typed or estimated. It is a reader view for the user and is never an input
to the simulation, an evaluation or a decision.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.stat_tables import avg, g, passer_rating, pct, thrown, time_text  # noqa: E402
from runtime.seasons import SeasonPaths
from runtime.season_layout import rebase_markdown

ROUNDS = {18: "Wild Card", 19: "Divisional", 20: "Conference Championship", 21: "Super Bowl"}
COACH = {"Jacksonville Jaguars": "Alex Stone"}
NOT_RECORDED = ("The receipts do not record the longest completion, the longest field goal, "
                "or return and defensive touchdowns, so those template columns are left out rather than guessed.")


def tracker_dir(root, year):
    return SeasonPaths(year, root).stats / 'team_tracker'


def load_games(root, year, team):
    games = []
    for folder, kind in (("game_receipts", "regular"), ("postseason_receipts", "postseason")):
        for path in sorted((SeasonPaths(year, root).stats / folder).glob("*.json")):
            receipt = json.loads(path.read_text(encoding="utf-8"))
            if team not in receipt.get("team_stats", {}):
                continue
            opponent = next(t for t in receipt["team_stats"] if t != team)
            score = receipt["final_score"]
            games.append({
                "kind": kind,
                "week": int(receipt["week"]),
                "opponent": opponent,
                "home": receipt.get("home") == team,
                "points": score[team], "opp_points": score[opponent],
                "team": receipt["team_stats"][team],
                "opp": receipt["team_stats"][opponent],
                "event_id": receipt.get("event_id", path.stem),
            })
    games.sort(key=lambda x: (x["kind"] != "regular", x["week"]))
    return games


def label(game):
    return f'Week {game["week"]}' if game["kind"] == "regular" else ROUNDS.get(game["week"], f'Postseason week {game["week"]}')


def slug(game):
    if game["kind"] == "regular":
        return "week_%02d.md" % game["week"]
    return "postseason_" + label(game).lower().replace(" ", "_") + ".md"


def result(game):
    a, b = game["points"], game["opp_points"]
    return ("W" if a > b else "L" if a < b else "T") + f" {a}-{b}"


def combine(lines):
    out = {}
    for line in lines:
        for key, value in line.items():
            if key == "position":
                out.setdefault("position", value)
            elif key.startswith("long_"):
                out[key] = max(out.get(key, 0), g(line, key))
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                out[key] = out.get(key, 0) + value
    return out


def totals(games):
    players = {}
    for game in games:
        for name, line in game["team"]["players"].items():
            players.setdefault(name, []).append(line)
    return {name: combine(lines) for name, lines in players.items()}


def table(headers, rows):
    if not rows:
        return "None recorded.\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out) + "\n"


def any_of(line, *fields):
    return any(g(line, f) for f in fields)


def sections(players, with_games):
    """Template position tables for a set of player lines."""
    G = (lambda l: [g(l, "games")]) if with_games else (lambda l: [])
    gh = ["G"] if with_games else []
    by = lambda fields: sorted(((n, l) for n, l in players.items() if any_of(l, *fields)),
                               key=lambda x: -g(x[1], fields[0]))
    out = []
    qbs = by(["pass_attempts"])
    out += ["### Quarterbacks", "", table(["Player"] + gh + ["Cmp", "Att", "Cmp%", "Yds", "Y/A", "TD", "Int", "Sck", "Rate", "Rush Att", "Rush Yds", "Rush TD", "Fum"],
        [[n] + G(l) + [g(l, "completions"), g(l, "pass_attempts"), pct(g(l, "completions"), g(l, "pass_attempts")), g(l, "passing_yards"),
          avg(g(l, "passing_yards"), g(l, "pass_attempts")), g(l, "passing_touchdowns"), thrown(l), g(l, "sacks_taken"), passer_rating(l),
          g(l, "rushing_attempts"), g(l, "rushing_yards"), g(l, "rushing_touchdowns"), g(l, "fumbles_lost")] for n, l in qbs])]
    qb_names = {n for n, _ in qbs}
    rushers = [(n, l) for n, l in by(["rushing_attempts", "targets", "receptions"])
               if n not in qb_names and (l.get("position") in ("RB", "FB") or g(l, "rushing_attempts"))]
    out += ["### Running backs and other rushers", "", table(["Player", "Pos"] + gh + ["Att", "Yds", "Y/A", "TD", "Lng", "Tgt", "Rec", "Rec Yds", "Rec TD", "Fum"],
        [[n, l.get("position", "")] + G(l) + [g(l, "rushing_attempts"), g(l, "rushing_yards"), avg(g(l, "rushing_yards"), g(l, "rushing_attempts")),
          g(l, "rushing_touchdowns"), g(l, "long_rush"), g(l, "targets"), g(l, "receptions"), g(l, "receiving_yards"), g(l, "receiving_touchdowns"),
          g(l, "fumbles_lost")] for n, l in rushers])]
    rush_names = {n for n, _ in rushers}
    catchers = [(n, l) for n, l in by(["targets", "receptions"]) if n not in rush_names and n not in qb_names]
    out += ["### Wide receivers and tight ends", "", table(["Player", "Pos"] + gh + ["Tgt", "Rec", "Yds", "Y/R", "TD", "Lng", "Fum"],
        [[n, l.get("position", "")] + G(l) + [g(l, "targets"), g(l, "receptions"), g(l, "receiving_yards"), avg(g(l, "receiving_yards"), g(l, "receptions")),
          g(l, "receiving_touchdowns"), g(l, "long_reception"), g(l, "fumbles_lost")] for n, l in catchers])]
    defenders = by(["tackles", "sacks", "defensive_interceptions", "passes_defended", "forced_fumbles", "fumble_recoveries", "tackles_for_loss", "pressures"])
    out += ["### Defense", "", table(["Player", "Pos"] + gh + ["Tkl", "Solo", "TFL", "Sck", "Press", "Int", "PD", "FF", "FR"],
        [[n, l.get("position", "")] + G(l) + [g(l, "tackles"), g(l, "solo_tackles"), g(l, "tackles_for_loss"), g(l, "sacks"), g(l, "pressures"),
          g(l, "defensive_interceptions"), g(l, "passes_defended"), g(l, "forced_fumbles"), g(l, "fumble_recoveries")] for n, l in defenders])]
    kickers = by(["field_goals_attempted", "extra_points_attempted"])
    out += ["### Kicking", "", table(["Player"] + gh + ["FGM", "FGA", "FG%", "XPM", "XPA", "Pts"],
        [[n] + G(l) + [g(l, "field_goals_made"), g(l, "field_goals_attempted"), pct(g(l, "field_goals_made"), g(l, "field_goals_attempted")),
          g(l, "extra_points_made"), g(l, "extra_points_attempted"), 3 * g(l, "field_goals_made") + g(l, "extra_points_made")] for n, l in kickers])]
    punters = by(["punts"])
    out += ["### Punting", "", table(["Player"] + gh + ["Punts", "Yds", "Avg", "In20", "TB", "Lng"],
        [[n] + G(l) + [g(l, "punts"), g(l, "punt_yards"), avg(g(l, "punt_yards"), g(l, "punts")), g(l, "punts_inside_20"),
          g(l, "punt_touchbacks"), g(l, "long_punt")] for n, l in punters])]
    returners = by(["kick_returns", "punt_returns"])
    out += ["### Returns", "", table(["Player"] + gh + ["KR", "KR Yds", "KR Avg", "PR", "PR Yds", "PR Avg"],
        [[n] + G(l) + [g(l, "kick_returns"), g(l, "kick_return_yards"), avg(g(l, "kick_return_yards"), g(l, "kick_returns")),
          g(l, "punt_returns"), g(l, "punt_return_yards"), avg(g(l, "punt_return_yards"), g(l, "punt_returns"))] for n, l in returners])]
    return out


def advanced(players, team_lines):
    """Rate stats computed from stored counters only (no play-by-play model)."""
    out = ["### Advanced", ""]
    qbs = sorted(((n, l) for n, l in players.items() if g(l, "pass_attempts")), key=lambda x: -g(x[1], "pass_attempts"))
    rows = []
    for n, l in qbs:
        att, sk = g(l, "pass_attempts"), g(l, "sacks_taken")
        net = g(l, "passing_yards") - g(l, "sack_yards")
        anya = (net + 20 * g(l, "passing_touchdowns") - 45 * thrown(l)) / (att + sk) if att + sk else None
        rows.append([n, avg(net, att + sk), "—" if anya is None else "%.2f" % anya, pct(sk, att + sk),
                     pct(g(l, "passing_touchdowns"), att), pct(thrown(l), att)])
    out += ["**Passing.** NY/A = (yards minus sack yards) per dropback; ANY/A adds 20 per TD and subtracts 45 per interception.", "",
            table(["Player", "NY/A", "ANY/A", "Sack%", "TD%", "Int%"], rows)]
    rec = sorted(((n, l) for n, l in players.items() if g(l, "targets")), key=lambda x: -g(x[1], "targets"))
    out += ["**Receiving.**", "", table(["Player", "Pos", "Tgt", "Catch%", "Y/Tgt"],
            [[n, l.get("position", ""), g(l, "targets"), pct(g(l, "receptions"), g(l, "targets")), avg(g(l, "receiving_yards"), g(l, "targets"))] for n, l in rec])]
    t = combine(team_lines)
    out += ["**Team.**", "", table(["Points", "First downs", "3rd down", "3rd %", "Turnovers", "Sacks allowed", "Penalties", "Time of possession"],
            [[g(t, "points"), g(t, "first_downs"), f'{g(t, "third_down_conversions")}/{g(t, "third_down_attempts")}',
              pct(g(t, "third_down_conversions"), g(t, "third_down_attempts")), g(t, "turnovers"), g(t, "sacks_allowed"),
              f'{g(t, "penalties")}-{g(t, "penalty_yards")}', time_text(g(t, "time_of_possession")) if g(t, "time_of_possession") else "—"]])]
    return out


def team_line(game):
    t = game["team"]
    return {k: v for k, v in t.items() if k != "players"} | {"points": game["points"]}


def game_page(team, year, game, regular_before):
    lines = [f"# {team} {year}: {label(game)} {'vs.' if game['home'] else 'at'} {game['opponent']}", "",
             f"**Result:** {result(game)}. **Generated** by `python scripts/render_team_tracker.py {year}` from receipt `{game['event_id']}`; do not edit by hand.", "",
             "Reader view for the user only. It is not an input to the simulation or to any evaluation.", "",
             "## This game", ""]
    lines += sections(game["team"]["players"], with_games=False)
    lines += advanced(game["team"]["players"], [team_line(game)])
    if game["kind"] == "regular":
        through = regular_before + [game]
        lines += ["", f"## Season totals through {label(game)}", "",
                  f"Record through {label(game)}: {record(through)}. Rate stats are recalculated from the totals, never averaged across games.", ""]
        lines += [s.replace("### ", "#### ") for s in sections(totals(through), with_games=True)]
    lines.append(NOT_RECORDED)
    return "\n".join(lines) + "\n"


def record(games):
    w = sum(g_["points"] > g_["opp_points"] for g_ in games)
    l = sum(g_["points"] < g_["opp_points"] for g_ in games)
    t = len(games) - w - l
    return f"{w}-{l}" + (f"-{t}" if t else "")


def depth_lines(root, year):
    paths = SeasonPaths(year, root)
    final = paths.depth_chart
    working = paths.record('offseason/depth_chart_working.json')
    path = final if final.exists() else working if working.exists() else None
    if not path:
        return ["No depth chart is recorded for this season yet.", ""]
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = [[pos, " / ".join(names) if names else "Open"] for pos, names in data["depth"].items()]
    note = data.get("effective") or data.get("as_of") or ""
    return [f"From [{path.relative_to(root / 'career' / str(year)).as_posix()}](../../{path.relative_to(root / 'career' / str(year)).as_posix()}){', ' + note if note else ''}. Order is first listed first; Stone owns it.", "",
            table(["Group", "Order"], rows)]


def award_rows(root, year, team):
    base = SeasonPaths(year, root).awards
    rows = []
    results = base / "results.json"
    if results.exists():
        for entry in json.loads(results.read_text(encoding="utf-8")).values():
            for key, award in entry.get("awards", {}).items():
                short = award.get("shortlist") or []
                idx = award.get("winner_index")
                if idx is not None and idx < len(short) and short[idx].get("team") == team:
                    w = short[idx]
                    rows.append([entry.get("kind", ""), entry.get("label", ""), key.replace("_", " ").replace("-", " ") + " player", w["player"], w.get("position", "")])
    honours = base / "season_honours_results.json"
    if honours.exists():
        data = json.loads(honours.read_text(encoding="utf-8"))
        for name, award in data.get("ap_awards", {}).items():
            short, idx = award.get("shortlist") or [], award.get("winner_index")
            if idx is not None and idx < len(short) and short[idx].get("team") == team:
                rows.append(["season", "AP", name, short[idx]["player"], short[idx].get("position", "")])
        for tier in ("first", "second"):
            for group in data.get("all_pro", {}).get(tier, {}).values():
                rows += [["season", "All-Pro", f"{tier.title()}-team All-Pro", r["player"], r.get("position", "")] for r in group if r.get("team") == team]
        for group in data.get("pro_bowl", {}).get("selections", {}).values():
            rows += [["season", "Pro Bowl", "Pro Bowl selection", r["player"], r.get("position", "")] for r in group if r.get("team") == team]
    return rows


def readme(root, year, team, games):
    regular = [x for x in games if x["kind"] == "regular"]
    post = [x for x in games if x["kind"] != "regular"]
    lines = [f"# {team} {year} stat tracker", "",
             f"**Generated** by `python scripts/render_team_tracker.py {year}` from the closed-game receipts; do not edit by hand. It updates every time a game closes.", "",
             "**Reader view for the user only.** It is not an input to the simulation, the engine, player evaluation or any decision. The receipts under `stats/game_receipts/` and `stats/postseason_receipts/` remain the source.", "",
             "## Team info", "",
             table(["Field", "Value"], [["Team", team], ["Season", year], ["Head coach", COACH.get(team, "Not recorded")],
                   ["Regular-season record", record(regular) if regular else "No game closed"],
                   ["Postseason", ", ".join(f"{label(x)}: {result(x)}" for x in post) if post else "None"]]),
             "## Depth chart", ""] + depth_lines(root, year) + [
             "## Games", "", table(["Game", "Opponent", "Result", "Page"],
                   [[label(x), ("vs. " if x["home"] else "at ") + x["opponent"], result(x), f"[{slug(x)}](games/{slug(x)})"] for x in games]),
             "## Regular-season totals", "",
             (f"Through {label(regular[-1])}, {record(regular)}." if regular else "No regular-season game has closed.") + " Rate stats are recalculated from the totals.", ""]
    if regular:
        lines += [s.replace("### ", "#### ") for s in sections(totals(regular), with_games=True)]
        lines += [s.replace("### ", "#### ") for s in advanced(totals(regular), [team_line(x) for x in regular])]
    lines += ["## Postseason totals", ""]
    if post:
        lines += [s.replace("### ", "#### ") for s in sections(totals(post), with_games=True)]
    else:
        lines += ["No postseason game.", ""]
    lines += ["## Awards", "", table(["Type", "When", "Award", "Player", "Pos"], award_rows(root, year, team)), NOT_RECORDED]
    return "\n".join(lines) + "\n"


def render(root, year, team):
    games = load_games(root, year, team)
    out = {"README.md": readme(root, year, team, games)}
    regular = []
    for game in games:
        out["games/" + slug(game)] = game_page(team, year, game, list(regular))
        if game["kind"] == "regular":
            regular.append(game)
    return {name: rebase_markdown(text, f'career/{year}/stats/team_tracker/{name}',
                                  (tracker_dir(root, year) / name).relative_to(root))
            for name, text in out.items()}


def check(root, year, team="Jacksonville Jaguars"):
    base = tracker_dir(root, year)
    if not base.exists():
        return []
    expected = render(root, year, team)
    errors = [f"Team tracker stale: {rel}" for rel, text in expected.items()
              if not (base / rel).exists() or (base / rel).read_text(encoding="utf-8") != text]
    actual = {p.relative_to(base).as_posix() for p in base.rglob("*.md")}
    errors += [f"Team tracker has an unexpected page: {rel}" for rel in sorted(actual - set(expected))]
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("--team", default="Jacksonville Jaguars")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = check(ROOT, args.year, args.team)
        print("\n".join(errors) if errors else "TEAM TRACKER CURRENT")
        return 1 if errors else 0
    base = tracker_dir(ROOT, args.year)
    for rel, text in render(ROOT, args.year, args.team).items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print("wrote", base.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
