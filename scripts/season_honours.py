#!/usr/bin/env python3
"""2013 season honours: AP awards, AP All-Pro teams and the Pro Bowl.

  python scripts/season_honours.py            # dry run: every ranking and shortlist
  python scripts/season_honours.py --close    # draw the AP awards and record everything
  python scripts/season_honours.py render     # rewrite season_honours.md

The method is fixed in career/2013/awards/season_honours_method.json before
any draw. All-Pro and Pro Bowl selections are formula ranks from the closed
regular-season receipts; each AP award is drawn from a three-name shortlist
with the private service's entropy, exactly as the weekly awards are.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.packets import canonical
from runtime.week_inputs import schedule
from scripts.league_awards import method as weekly_method, pick, score as formula_score
from scripts.render_season_stats import load_receipts

AWARDS = ROOT / "career/2013/awards"
METHOD = AWARDS / "season_honours_method.json"
EVIDENCE = AWARDS / "season_honours_evidence.json"
RESULTS = AWARDS / "season_honours_results.json"
PAGE = AWARDS / "season_honours.md"
PRO_BOWL_DATE = date(2014, 1, 26)
OFFENSE_GROUPS = ("QB", "RB", "FB", "WR", "TE")
DEFENSE_GROUPS = ("DE", "DT", "OLB", "ILB", "CB", "S")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def regular_receipts():
    return [r for r in load_receipts(ROOT / "career/2013/stats/game_receipts") if int(r["week"]) <= 17]


def postseason_receipts():
    return list(load_receipts(ROOT / "career/2013/stats/postseason_receipts"))


def group_of(position, m):
    for group, labels in m["position_groups"].items():
        if position in labels:
            return group
    return None


def season_rows(receipts, first, last, m, evidence):
    """Per-player season scores over Weeks first..last."""
    weekly = weekly_method()
    line = m["extra_formulas"]["line"]["per_start"]
    starts = {name: set(row["weeks"]) for name, row in evidence["line_starts"].items()}
    rows = {}
    for receipt in sorted(receipts, key=lambda r: (int(r["week"]), r["event_id"])):
        week = int(receipt["week"])
        if not first <= week <= last:
            continue
        for team, stats in receipt["team_stats"].items():
            for name, player in stats["players"].items():
                row = rows.setdefault(name, {"player": name, "team": team, "labels": {}, "offense": 0.0,
                                             "defense": 0.0, "kicker": 0.0, "punter": 0.0, "line": 0.0,
                                             "kick_returner": 0.0, "return_specialist": 0.0, "starts": 0})
                row["team"] = team
                label = player.get("position")
                row["labels"].setdefault(label, [0, week])[0] += 1
                row["offense"] += formula_score("offense", player, weekly)
                row["defense"] += formula_score("defense", player, weekly)
                special = formula_score("special_teams", player, weekly)
                if label == "K":
                    row["kicker"] += special
                elif label == "P":
                    row["punter"] += special
                row["kick_returner"] += 0.1 * player.get("kick_return_yards", 0)
                row["return_specialist"] += 0.1 * (player.get("kick_return_yards", 0) + player.get("punt_return_yards", 0))
                if week in starts.get(name, ()):
                    row["starts"] += 1
                    row["line"] += (line["constant"] + line["team_rushing_yards"] * stats.get("rushing_yards", 0)
                                    + line["team_passing_yards"] * stats.get("passing_yards", 0)
                                    + line["team_sacks_allowed"] * stats.get("sacks_allowed", 0))
    for row in rows.values():
        label = sorted(row["labels"].items(), key=lambda item: (-item[1][0], item[1][1]))[0][0]
        row["position"] = label
        row["group"] = group_of(label, m)
        del row["labels"]
        for key in ("offense", "defense", "kicker", "punter", "line", "kick_returner", "return_specialist"):
            row[key] = round(row[key], 2)
    return rows


def group_score(row, m):
    kind = m["group_scores"].get(row["group"])
    return row[kind] if kind else None


def ranked(rows, group, m, key=None):
    if key:
        pool = [(r[key], r) for r in rows.values() if r[key] > 0]
    else:
        pool = [(group_score(r, m), r) for r in rows.values() if r["group"] == group]
    pool.sort(key=lambda item: (-item[0], -item[1]["starts"], item[1]["player"]))
    if m["group_scores"].get(group) == "line":
        # Teammates share one line score, so a club places one lineman per position.
        seen, kept = set(), []
        for s, r in pool:
            if r["team"] not in seen:
                seen.add(r["team"])
                kept.append((s, r))
        pool = kept
    return [{"player": r["player"], "team": r["team"], "position": r["position"], "score": round(s, 2)} for s, r in pool]


def slot_ranking(rows, slot, m):
    if slot == "KR":
        return ranked(rows, None, m, key="kick_returner")
    if slot == "RS":
        return ranked(rows, None, m, key="return_specialist")
    return ranked(rows, slot, m)


def all_pro(rows, m):
    teams = {"first": {}, "second": {}}
    for slot, n in m["all_pro"]["slots"].items():
        order = slot_ranking(rows, slot, m)
        teams["first"][slot] = order[:n]
        teams["second"][slot] = order[n:2 * n]
    return teams


def team_records(receipts):
    records = {}
    for receipt in receipts:
        score = receipt["final_score"]
        for team, other in ((receipt["away"], receipt["home"]), (receipt["home"], receipt["away"])):
            row = records.setdefault(team, {"wins": 0.0, "points_for": 0, "points_against": 0})
            row["points_for"] += score[team]
            row["points_against"] += score[other]
            row["wins"] += 1.0 if score[team] > score[other] else 0.5 if score[team] == score[other] else 0.0
    return records


def game_dates():
    dates = {}
    for week in range(1, 22):
        for game in schedule(week):
            dates[(week, game["away"], game["home"])] = date.fromisoformat(game["date"])
    return dates


def unavailable_for_pro_bowl(receipts, super_bowl_clubs):
    """Players whose latest recorded injury projects a return after the game."""
    dates, latest = game_dates(), {}
    for receipt in receipts:
        when = dates[(int(receipt["week"]), receipt["away"], receipt["home"])]
        for injury in receipt.get("injuries", []):
            back = when + timedelta(days=int(injury["return_days"]))
            if injury["player"] not in latest or when >= latest[injury["player"]][0]:
                latest[injury["player"]] = (when, back)
    return {name for name, (_, back) in latest.items() if back > PRO_BOWL_DATE}


def conference_round_clubs():
    clubs = set()
    for receipt in postseason_receipts():
        if int(receipt["week"]) == 20:
            clubs.update((receipt["away"], receipt["home"]))
    return clubs


def super_bowl_clubs():
    return {team for r in postseason_receipts() if int(r["week"]) == 21 for team in (r["away"], r["home"])}


def pro_bowl(rows, m, all_receipts):
    sb, injured = super_bowl_clubs(), None
    injured = unavailable_for_pro_bowl(all_receipts, sb)
    out, alternates = {}, {}
    for slot, n in m["pro_bowl"]["slots"].items():
        order = slot_ranking(rows, slot, m)
        chosen = order[:n]
        pool = order[n:]
        alternates[slot] = pool[:3]
        entries, used = [], set()
        for sel in chosen:
            reason = ("club in Super Bowl XLVIII" if sel["team"] in sb
                      else "injury: projected return after January 26" if sel["player"] in injured else None)
            entry = dict(sel, replaced_by=None, reason=reason)
            if reason:
                for alt in pool:
                    if alt["player"] in used or alt["team"] in sb or alt["player"] in injured:
                        continue
                    used.add(alt["player"])
                    entry["replaced_by"] = alt
                    break
            entries.append(entry)
        out[slot] = entries
    last_four = conference_round_clubs()
    captains = {}
    for side, groups, key in (("offense", OFFENSE_GROUPS, "offense"), ("defense", DEFENSE_GROUPS, "defense")):
        pool = [(rows[e["player"]][key], e) for g in groups for e in out[g] if e["team"] not in last_four]
        pool.sort(key=lambda item: (-item[0], item[1]["player"]))
        captains[side] = [{"player": e["player"], "team": e["team"], "score": round(s, 2)} for s, e in pool[:2]]
    return {"selections": out, "alternates": alternates, "captains": captains,
            "super_bowl_clubs": sorted(sb)}


def pro_bowl_coaches(evidence):
    readme = (ROOT / "career/2013/postseason/README.md").read_text(encoding="utf-8")
    seeds = {}
    for line in readme.splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == 3 and cells[0].isdigit():
            seeds[cells[1]] = ("AFC", int(cells[0]))
            seeds[cells[2]] = ("NFC", int(cells[0]))
    losers = {}
    for receipt in postseason_receipts():
        if int(receipt["week"]) == 19:
            score = receipt["final_score"]
            loser = min((receipt["away"], receipt["home"]), key=lambda t: score[t])
            conference, seed = seeds[loser]
            if conference not in losers or seed < losers[conference][1]:
                losers[conference] = (loser, seed)
    return {c: {"club": t, "seed": s, "head_coach": evidence["head_coaches"][t]["coach"]} for c, (t, s) in sorted(losers.items())}


def award_shortlists(rows, m, evidence, receipts):
    spec, records = m["ap_awards"], team_records(receipts)
    rookies, comeback = set(evidence["rookies"]), set(evidence["comeback_eligible"])
    lists = {}
    for award, rule in spec["awards"].items():
        if award == "COY":
            pool = []
            for team, coach in evidence["head_coaches"].items():
                before = coach["record_2012"]["wins"] + 0.5 * coach["record_2012"]["ties"]
                now = records[team]["wins"]
                diff = records[team]["points_for"] - records[team]["points_against"]
                pool.append({"coach": coach["coach"], "team": team, "score": round(now - before, 1),
                             "wins_2013": now, "wins_2012": before, "point_differential": diff})
            pool.sort(key=lambda r: (-r["score"], -r["wins_2013"], -r["point_differential"], r["coach"]))
            lists[award] = pool[:spec["shortlist_size"]]
            continue
        eligible = {"rookies": rookies, "comeback_eligible": comeback}.get(rule.get("eligibility"))
        pool = []
        for row in rows.values():
            if eligible is not None and row["player"] not in eligible:
                continue
            for kind in rule["pool"]:
                groups = OFFENSE_GROUPS if kind == "offense" else DEFENSE_GROUPS
                if row["group"] in groups:
                    value = row[kind] + rule.get("team_wins_weight", 0) * records[row["team"]]["wins"]
                    pool.append({"player": row["player"], "team": row["team"], "position": row["position"],
                                 "score": round(value, 2)})
        pool.sort(key=lambda r: (-r["score"], r["player"]))
        lists[award] = pool[:spec["shortlist_size"]]
    return lists


def build():
    m, evidence = load(METHOD), load(EVIDENCE)
    receipts = regular_receipts()
    season = season_rows(receipts, *m["evidence"]["windows"]["ap_awards"], m, evidence)
    through_16 = season_rows(receipts, *m["evidence"]["windows"]["pro_bowl"], m, evidence)
    return m, evidence, receipts, {
        "all_pro": all_pro(season, m),
        "pro_bowl": dict(pro_bowl(through_16, m, receipts + postseason_receipts()),
                         coaches=pro_bowl_coaches(evidence)),
        "shortlists": award_shortlists(season, m, evidence, receipts),
    }


def packet(award, shortlist, snapshot, m):
    return {"procedure": m["procedure"], "event_id": "2013-honours-%s-%s" % (award.lower(), m["procedure_tag"]),
            "snapshot": snapshot, "award": award, "shortlist": shortlist,
            "panel_weights": m["ap_awards"]["panel_weights"][:len(shortlist)],
            "method_sha256": hashlib.sha256(METHOD.read_bytes()).hexdigest(),
            "evidence_sha256": hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()}


def name_of(entry):
    return entry.get("player") or entry.get("coach")


def render():
    m, results = load(METHOD), load(RESULTS)
    lines = ["# 2013 season honours", "",
             "Generated by `scripts/season_honours.py render` from `season_honours_results.json`. "
             "Method: [season_honours_method.json](season_honours_method.json); evidence: "
             "[season_honours_evidence.json](season_honours_evidence.json). Drawn retroactively on the branch "
             "date of February 2, 2014 (%s); no game result or statistic changed." % results["ledger_entry"], "",
             "## AP awards", "", "Regular season only (Weeks 1-17). Winner drawn 6:3:1 from the shortlist by the private service.", "",
             "| Award | Winner | Club | Score | Shortlist (score) |", "|---|---|---|--:|---|"]
    for award, a in results["ap_awards"].items():
        w = a["shortlist"][a["winner_index"]]
        short = "; ".join("%s, %s (%s)" % (name_of(s), s["team"], s["score"]) for s in a["shortlist"])
        lines.append("| %s | %s | %s | %s | %s |" % (m["ap_awards"]["names"][award], name_of(w), w["team"], w["score"], short))
    lines += ["", "Coach of the Year score is 2013 wins minus 2012 wins.", "",
              "## AP All-Pro teams", "", "Weeks 1-17; formula rank per position.", "",
              "| Position | First team | Second team |", "|---|---|---|"]
    ap = results["all_pro"]
    for slot in m["all_pro"]["slots"]:
        fmt = lambda xs: "; ".join("%s, %s" % (x["player"], x["team"]) for x in xs) or "none"
        lines.append("| %s | %s | %s |" % (slot, fmt(ap["first"][slot]), fmt(ap["second"][slot])))
    pb = results["pro_bowl"]
    lines += ["", "## Pro Bowl (Honolulu, January 26, 2014)", "",
              "Weeks 1-16 (the vote closed December 26); formula rank per position. Players from the Super Bowl clubs "
              "(%s) and players projected injured on January 26 are replaced by the next available alternate." % ", ".join(pb["super_bowl_clubs"]), "",
              "| Position | Selections | Replacements | Next alternates |", "|---|---|---|---|"]
    for slot in m["pro_bowl"]["slots"]:
        sel = "; ".join("%s, %s" % (e["player"], e["team"]) for e in pb["selections"][slot])
        rep = "; ".join("%s for %s (%s)" % (e["replaced_by"]["player"] if e["replaced_by"] else "no eligible alternate",
                                            e["player"], e["reason"]) for e in pb["selections"][slot] if e["reason"]) or "none"
        alt = "; ".join("%s, %s" % (a["player"], a["team"]) for a in pb["alternates"][slot])
        lines.append("| %s | %s | %s | %s |" % (slot, sel, rep, alt))
    lines += ["", "Captains (clubs outside the conference round): offense %s; defense %s." % (
        " and ".join("%s (%s)" % (c["player"], c["team"]) for c in pb["captains"]["offense"]),
        " and ".join("%s (%s)" % (c["player"], c["team"]) for c in pb["captains"]["defense"])),
        "", "Coaches (highest-seeded Divisional-round loser in each conference): " + "; ".join(
            "%s, %s staff (%s seed %d)" % (v["head_coach"], v["club"], c, v["seed"]) for c, v in pb["coaches"].items()) + ".",
        "", "Not generated: the two special teamer slots (no coverage-unit evidence in the receipts), the two coach-appointed need players, the January 21-22 draft and the game itself."]
    PAGE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", nargs="?", choices=("render",))
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    if args.action == "render":
        render()
        return 0
    m, _, _, built = build()
    for award, rows in built["shortlists"].items():
        print(award, "; ".join("%s (%s) %s" % (name_of(r), r["team"], r["score"]) for r in rows))
    if not args.close:
        print(json.dumps(built["all_pro"]["first"], indent=None)[:3000])
        return 0
    if RESULTS.exists():
        print("HONOURS: already drawn")
        return 1
    from runtime.private_client import Client
    client = Client()
    snapshot = client.current_snapshot()
    drawn = {}
    for award, shortlist in built["shortlists"].items():
        pkt = packet(award, shortlist, snapshot, m)
        ref = client.close_event(pkt)
        drawn[award] = {"event_id": pkt["event_id"], "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(),
                        "result_ref": ref, "shortlist": shortlist, "winner_index": pick(ref, pkt)}
    results = {"procedure": m["procedure"], "ledger_entry": args.entry, "snapshot": snapshot,
               "method_sha256": hashlib.sha256(METHOD.read_bytes()).hexdigest(),
               "evidence_sha256": hashlib.sha256(EVIDENCE.read_bytes()).hexdigest(),
               "ap_awards": drawn, "all_pro": built["all_pro"], "pro_bowl": built["pro_bowl"]}
    RESULTS.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    render()
    return 0


if __name__ == "__main__":
    sys.exit(main())
