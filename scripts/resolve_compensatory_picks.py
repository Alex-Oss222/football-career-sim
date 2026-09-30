#!/usr/bin/env python3
"""Resolve the branch 2014 compensatory picks (March 24, 2014 announcement).

  python scripts/resolve_compensatory_picks.py [--check]

Inputs: career/2014/04_draft/compensatory/method.json (adopted before this run),
inputs.json (built by scripts/research/build_2014_compensatory_inputs.py),
the branch 2013 regular-season and postseason receipts, the branch 2013
season honours and the branch 2014 first-round order. No real award list is
read. The result is deterministic; there is no random draw.
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DIR = ROOT / "career" / "2014" / "04_draft" / "compensatory"
METHOD, INPUTS, OUT = DIR / "method.json", DIR / "inputs.json", DIR / "awards.json"
PAGE = DIR / "announcement.md"
RECEIPTS = [ROOT / "career/2013/stats/game_receipts", ROOT / "career/2013/stats/postseason_receipts"]
HONOURS = ROOT / "career/2013/awards/season_honours_results.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def club_names():
    week1 = json.loads((ROOT / "library/data/2013_week1_depth_charts.json").read_text())
    names = {club["code"]: name for name, club in week1["clubs"].items()}
    names["JAX"] = "Jacksonville Jaguars"
    return names


def branch_games():
    games, club_games = defaultdict(int), defaultdict(int)
    for folder in RECEIPTS:
        for path in sorted(folder.glob("*.json")):
            receipt = json.loads(path.read_text())
            for team, stats in receipt.get("team_stats", {}).items():
                club_games[team] += 1
                for player, line in stats.get("players", {}).items():
                    games[(team, player)] += int(line.get("games", 0))
    return games, club_games


def honours_points(weights):
    data = json.loads(HONOURS.read_text())
    points = defaultdict(int)
    for key, rows in (("first_team_all_pro", data["all_pro"]["first"]), ("second_team_all_pro", data["all_pro"]["second"]),
                      ("pro_bowl", data["pro_bowl"]["selections"])):
        for group in rows.values():
            for r in group:
                points[(r["team"], r["player"])] = max(points[(r["team"], r["player"])], weights[key])
    return points


def value_round(points, thresholds):
    for band in thresholds:
        if points >= band["min_points"]:
            return band["round"]
    return None


def resolve():
    from runtime.draft_order import order
    method, inputs = json.loads(METHOD.read_text()), json.loads(INPUTS.read_text())
    val, names = method["valuation"], club_names()
    slot = {row["club"]: row["slot"] for row in order()}
    games, club_games = branch_games()
    honours = honours_points(val["honours"])
    floor = method["qualification"]["minimum_value_points"]
    valued, below_floor = [], []
    for c in inputs["candidates"]:
        new_club = names[c["new_club"]]
        g = games[(new_club, c["player"])]
        share = g / club_games[new_club]
        pt = next(a["points"] for a in val["playing_time"]["adjustments"] if share >= a["min_share"])
        hp = honours[(new_club, c["player"])]
        points = round(c["salary_percentile"] + pt + hp, 2)
        if points < floor:
            below_floor.append(c["player"])
            continue
        valued.append({**c, "old_club_name": names[c["old_club"]], "new_club_name": new_club,
                       "branch_games_2013": g, "club_games_2013": club_games[new_club],
                       "playing_time_points": pt, "honours_points": hp, "value_points": points,
                       "value_round": value_round(points, val["round_thresholds"])})
    key = lambda r: (r["value_round"], -r["value_points"], -r["apy"], r["player"])
    losses, gains = defaultdict(list), defaultdict(list)
    for r in valued:
        losses[r["old_club_name"]].append(r)
        gains[r["new_club_name"]].append(r)
    clubs, formula = [], []
    for club in sorted(slot, key=slot.get):
        lost, got = sorted(losses[club], key=key), sorted(gains[club], key=key)
        remaining, cancelled = list(lost), []
        for gain in got:
            same = [l for l in remaining if l["value_round"] == gain["value_round"]]
            lower = [l for l in remaining if l["value_round"] > gain["value_round"]]
            higher = [l for l in remaining if l["value_round"] < gain["value_round"]]
            hit = same[0] if same else lower[0] if lower else higher[-1] if higher else None
            if hit:
                remaining.remove(hit)
            cancelled.append({"gain": gain["player"], "cancels": hit["player"] if hit else None})
        picks = remaining[:4]
        formula += [{"club": club, "round": p["value_round"], "for_player": p["player"], "apy": p["apy"], "value_points": p["value_points"],
                     "slot": slot[club], "kind": "formula"} for p in picks]
        clubs.append({"club": club, "losses": [l["player"] for l in lost], "gains": [g["player"] for g in got],
                      "cancellations": cancelled, "net_loss": len(lost) - len(got),
                      "awarded": len(picks)})
    formula.sort(key=lambda p: (p["round"], -p["value_points"], -p["apy"], p["slot"]))
    dropped = []
    target = method["league_total"]["target"]
    while len(formula) > target:
        dropped.append(formula.pop())
    fill = [{"club": club, "round": 7, "for_player": None, "apy": None, "value_points": None, "slot": slot[club], "kind": "fill"}
            for club in sorted(slot, key=slot.get)[:max(0, target - len(formula))]]
    picks = formula + fill
    base = {3: 96, 4: 128, 5: 160, 6: 192, 7: 224}
    counts = {r: sum(1 for p in picks if p["round"] == r) for r in range(3, 8)}
    for rnd in range(3, 8):
        start = base[rnd] + sum(counts[r] for r in range(3, rnd))
        for i, p in enumerate([p for p in picks if p["round"] == rnd], 1):
            p["overall"] = start + i
    for c in clubs:
        c["awarded"] = sum(1 for p in picks if p["club"] == c["club"])
    return {"schema_version": 1, "announcement_date": "2014-03-24", "qualifying_free_agency_year": 2013,
            "method_sha256": sha(METHOD), "inputs_sha256": sha(INPUTS),
            "round_counts": {str(r): counts[r] for r in range(3, 8)},
            "picks": picks, "dropped_over_32": dropped, "clubs": clubs,
            "valued_free_agents": sorted(valued, key=key), "below_floor": sorted(below_floor)}


def money(value):
    return f"${value / 1e6:.2f}M"


def announcement(result):
    inputs = json.loads(INPUTS.read_text())
    method = json.loads(METHOD.read_text())
    val = method["valuation"]
    fa = {r["player"]: r for r in result["valued_free_agents"]}
    desc = lambda n: (f'{n} ({fa[n]["old_club"]} to {fa[n]["new_club"]}, {money(fa[n]["apy"])} a year, '
                      f'{fa[n]["value_points"]:.1f} points, Round {fa[n]["value_round"]})')
    thresholds = ", ".join(f'Round {t["round"]} at {t["min_points"]}' for t in val["round_thresholds"])
    lines = ["# 2014 compensatory picks: branch announcement", "",
             "**Announced:** Monday, March 24, 2014 (ledger Entry 100). **Generated** by `python scripts/resolve_compensatory_picks.py` from [awards.json](awards.json); do not edit by hand.", "",
             "The league awarded 32 compensatory picks for the 2014 draft, placed after rounds 3 to 7. They rest on each club's qualifying unrestricted free agents lost and signed in the **2013** league year of this branch. The NFL formula's weights are unpublished, so the branch used its own [method](method.json), version 2, on [recorded inputs](inputs.json). No real 2014 award list was read. The picks cannot be traded in 2014.", "",
             "## How a free agent is valued", "",
             f'- **Salary (primary):** his new contract\'s average per year as a percentile of the 2013 league market ({inputs["salary_market"]["contracts"]} contracts in force; median {money(inputs["salary_market"]["median_apy"])}). A $12.0M deal scores about 98; a $1.0M deal about 55.',
             "- **Playing time:** branch 2013 games for his new club as a share of that club's games: 75 percent or more costs nothing, 50 to 75 percent costs 4 points, 25 to 50 percent 8, under 25 percent 12.",
             f'- **Honours:** the highest branch 2013 honour adds points: first-team All-Pro {val["honours"]["first_team_all_pro"]}, second-team {val["honours"]["second_team_all_pro"]}, Pro Bowl {val["honours"]["pro_bowl"]}.',
             f'- **Round:** {thresholds}. Below {method["qualification"]["minimum_value_points"]} points a free agent neither earns nor cancels a pick.',
             "- **Net loss:** each signing cancels a loss in the same round first, then the best lower-round loss, then the weakest higher-round loss. Remaining losses become picks, at most four per club. The league fills to 32 with Round 7 picks in 2014 draft order.", "",
             "## Jacksonville", ""]
    jax = next(c for c in result["clubs"] if c["club"] == "Jacksonville Jaguars")
    mine = [p for p in result["picks"] if p["club"] == "Jacksonville Jaguars"]
    headline = (f'**{len(mine)} compensatory pick{"s" if len(mine) != 1 else ""}:** ' + ", ".join(f'No. {p["overall"]} (Round {p["round"]})' for p in mine) + "."
                if mine else "**No compensatory pick.**")
    lines += [f'{headline} Jacksonville lost {len(jax["losses"])} qualifying free agents and signed {len(jax["gains"])}, a net {"loss" if jax["net_loss"] > 0 else "gain"} of {abs(jax["net_loss"])}.', "",
              "- **Lost:** " + ("; ".join(desc(n) for n in jax["losses"]) or "none") + ".",
              "- **Signed:** " + ("; ".join(desc(n) for n in jax["gains"]) or "none") + ".",
              "- **Cancellations:** " + ("; ".join(f'{c["gain"]} cancels {c["cancels"]}' if c["cancels"] else f'{c["gain"]} had no loss left to cancel' for c in jax["cancellations"]) or "none") + ".",
              "- Daryl Smith re-signed with Jacksonville, so he was not a loss. Rashean Mathis, Eben Britton, George Selvie and other departures have no 2013 contract value in the source and are not counted.", "",
              "## The 32 picks", "",
              "| Overall | Round | Club | Basis |", "|---:|---:|---|---|"]
    for pick in result["picks"]:
        basis = (f'Net loss of {pick["for_player"]} ({money(pick["apy"])} a year, {pick["value_points"]:.1f} points)' if pick["kind"] == "formula"
                 else "Fill pick: the formula produced fewer than 32")
        lines.append(f'| {pick["overall"]} | {pick["round"]} | {pick["club"]} | {basis} |')
    lines += ["", "## Club summary", "",
              "Only clubs with a qualifying loss or signing are listed. Net loss is losses minus signings; a negative number is a net gain.", "",
              "| Club | Qualifying losses | Qualifying signings | Net loss | Picks |", "|---|---:|---:|---:|---:|"]
    for c in result["clubs"]:
        if c["losses"] or c["gains"]:
            lines.append(f'| {c["club"]} | {len(c["losses"])} | {len(c["gains"])} | {c["net_loss"]} | {c["awarded"]} |')
    honoured = [r for r in result["valued_free_agents"] if r["honours_points"]]
    limited = [r for r in result["valued_free_agents"] if r["playing_time_points"]]
    lines += ["", "## Adjustments and limits", "",
              "- **Honours applied:** " + ("; ".join(f'{r["player"]} (+{r["honours_points"]})' for r in honoured) or "none") + ".",
              "- **Playing time applied:** " + ("; ".join(f'{r["player"]} ({r["branch_games_2013"]} of {r["club_games_2013"]} games, {r["playing_time_points"]})' for r in limited) or "none") + ".",
              f'- **Below the minimum value:** {len(result["below_floor"])} moves: ' + ", ".join(result["below_floor"]) + ".",
              f'- **Coverage:** {len(inputs["candidates"])} valued moves (including Jacksonville\'s four branch signings) and {len(inputs["excluded_movers"])} club changes that do not qualify or could not be valued. Most of the unvalued moves are near-minimum deals missing from the source.',
              "- **Not applied:** the league's post-draft signing deadline (no signing dates in the source) and the unverified real fill order (the branch fills in 2014 first-round order). Playing time is games, not snaps.",
              "- **Values:** contract APYs are Over The Cap reconstructions via nflverse, not certified league figures; Jacksonville's four signings use its branch contracts.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = resolve()
    text = json.dumps(result, indent=1) + "\n"
    page = announcement(result)
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text and PAGE.exists() and PAGE.read_text() == page
        print("COMPENSATORY AWARDS CURRENT" if ok else "COMPENSATORY AWARDS STALE")
        return 0 if ok else 1
    OUT.write_text(text)
    PAGE.write_text(page)
    print("wrote", OUT.relative_to(ROOT), "and", PAGE.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
