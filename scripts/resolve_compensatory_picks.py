#!/usr/bin/env python3
"""Resolve the branch 2014 compensatory picks (March 24, 2014 announcement).

  python scripts/resolve_compensatory_picks.py [--check]

Inputs: career/2014/draft/compensatory/method.json (adopted before this run),
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
DIR = ROOT / "career" / "2014" / "draft" / "compensatory"
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
    games = defaultdict(int)
    for folder in RECEIPTS:
        for path in sorted(folder.glob("*.json")):
            receipt = json.loads(path.read_text())
            for team, stats in receipt.get("team_stats", {}).items():
                for player, line in stats.get("players", {}).items():
                    games[(team, player)] += int(line.get("games", 0))
    return games


def honoured():
    data = json.loads(HONOURS.read_text())
    names = set()
    for team in ("first", "second"):
        for rows in data["all_pro"][team].values():
            names.update((r["team"], r["player"]) for r in rows)
    for rows in data["pro_bowl"]["selections"].values():
        names.update((r["team"], r["player"]) for r in rows)
    return names


def base_round(apy, bands):
    for band in bands:
        if apy >= band["min_apy"]:
            return band["round"]
    return None


def resolve():
    from runtime.draft_order import order
    method, inputs = json.loads(METHOD.read_text()), json.loads(INPUTS.read_text())
    val, names = method["valuation"], club_names()
    slot = {row["club"]: row["slot"] for row in order()}
    games, honours = branch_games(), honoured()
    floor = method["qualification"]["valuation_floor_apy"]
    valued, below_floor = [], []
    for c in inputs["candidates"]:
        new_club = names[c["new_club"]]
        if c["apy"] < floor:
            below_floor.append(c["player"])
            continue
        rnd = base_round(c["apy"], val["apy_round_bands"])
        g = games[(new_club, c["player"])]
        honour = (new_club, c["player"]) in honours
        adjusted = max(3, rnd - 1) if honour else rnd
        if g < 8:
            adjusted = min(7, adjusted + 1)
        valued.append({**c, "old_club_name": names[c["old_club"]], "new_club_name": new_club,
                       "apy_round": rnd, "branch_games_2013": g, "branch_honour_2013": honour,
                       "value_round": adjusted})
    key = lambda r: (r["value_round"], -r["apy"], r["player"])
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
        formula += [{"club": club, "round": p["value_round"], "for_player": p["player"], "apy": p["apy"],
                     "slot": slot[club], "kind": "formula"} for p in picks]
        clubs.append({"club": club, "losses": [l["player"] for l in lost], "gains": [g["player"] for g in got],
                      "cancellations": cancelled, "net_loss": len(lost) - len(got),
                      "awarded": len(picks)})
    formula.sort(key=lambda p: (p["round"], -p["apy"], p["slot"]))
    dropped = []
    target = method["league_total"]["target"]
    while len(formula) > target:
        dropped.append(formula.pop())
    fill = [{"club": club, "round": 7, "for_player": None, "apy": None, "slot": slot[club], "kind": "fill"}
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
    lines = ["# 2014 compensatory picks: branch announcement", "",
             "**Announced:** Monday, March 24, 2014 (ledger Entry 100). **Generated** by `python scripts/resolve_compensatory_picks.py` from [awards.json](awards.json); do not edit by hand.", "",
             "The league awarded 32 compensatory picks for the 2014 draft, placed after rounds 3 to 7. They rest on each club's qualifying unrestricted free agents lost and signed in the **2013** league year of this branch. The NFL formula's weights are unpublished, so the branch used its own [method](method.json), adopted before the result was computed, on [recorded inputs](inputs.json). No real 2014 award list was read. The picks cannot be traded in 2014.", "",
             "## Jacksonville", ""]
    jax = next(c for c in result["clubs"] if c["club"] == "Jacksonville Jaguars")
    fa = {r["player"]: r for r in result["valued_free_agents"]}
    desc = lambda n: f'{n} ({fa[n]["old_club"]} to {fa[n]["new_club"]}, {money(fa[n]["apy"])} a year, Round {fa[n]["value_round"]} value)'
    lines += [f'**No compensatory pick.** Jacksonville lost {len(jax["losses"])} valued qualifying free agents and signed {len(jax["gains"])}, a net gain of {len(jax["gains"]) - len(jax["losses"])}.', "",
              "- **Lost:** " + "; ".join(desc(n) for n in jax["losses"]) + ".",
              "- **Signed:** " + "; ".join(desc(n) for n in jax["gains"]) + ".",
              "- **Cancellations:** " + "; ".join(f'{c["gain"]} cancels {c["cancels"]}' if c["cancels"] else f'{c["gain"]} had no loss left to cancel' for c in jax["cancellations"]) + ".",
              "- Daryl Smith re-signed with Jacksonville, so he was not a loss. Rashean Mathis, Eben Britton, George Selvie and other departures have no 2013 contract value in the source and are not counted; Rashad Jennings's $0.63M deal is below the $1.0M floor.", "",
              "Jacksonville's own picks keep their slots; their overall numbers move to include the awards: No. 134 (Round 4), 157 and 172 (Round 5), 210 (Round 6) and 247 (Round 7).", "",
              "## The 32 picks", "",
              "| Overall | Round | Club | Basis |", "|---:|---:|---|---|"]
    for pick in result["picks"]:
        basis = (f'Net loss of {pick["for_player"]} ({money(pick["apy"])} a year)' if pick["kind"] == "formula"
                 else "Fill pick: the formula produced fewer than 32")
        lines.append(f'| {pick["overall"]} | {pick["round"]} | {pick["club"]} | {basis} |')
    lines += ["", "## Club summary", "",
              "Only clubs with a valued qualifying loss or signing are listed.", "",
              "| Club | Valued losses | Valued signings | Net loss | Picks |", "|---|---:|---:|---:|---:|"]
    for c in result["clubs"]:
        if c["losses"] or c["gains"]:
            lines.append(f'| {c["club"]} | {len(c["losses"])} | {len(c["gains"])} | {c["net_loss"]} | {c["awarded"]} |')
    adjusted = [r for r in result["valued_free_agents"] if r["value_round"] != r["apy_round"]]
    lines += ["", "## Adjustments and limits", "",
              "- **Honours:** a branch 2013 Pro Bowl or All-Pro selection raised these players one round: " + "; ".join(f'{r["player"]} (Round {r["apy_round"]} to {r["value_round"]})' for r in adjusted if r["branch_honour_2013"]) + ".",
              ("- **Playing time:** fewer than 8 branch games for the new club lowered: " + "; ".join(f'{r["player"]} ({r["branch_games_2013"]} games)' for r in result["valued_free_agents"] if r["branch_games_2013"] < 8) + "."
               if any(r["branch_games_2013"] < 8 for r in result["valued_free_agents"])
               else "- **Playing time:** every valued player had at least 8 branch games for his new club, so none was lowered."),
              f'- **Coverage:** {len(inputs["candidates"])} valued moves (including Jacksonville\'s four branch signings) and {len(inputs["excluded_movers"])} club changes that do not qualify or could not be valued. Most of the unvalued moves are near-minimum deals missing from the source.',
              "- **Not applied:** the league's post-draft signing deadline (no signing dates in the source) and the unverified real fill order (the branch fills in 2014 first-round order).",
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
