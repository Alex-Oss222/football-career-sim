#!/usr/bin/env python3
"""League awards: formula shortlist, then an audited panel draw.

  python scripts/league_awards.py week N --season YEAR            # dry run: shortlists
  python scripts/league_awards.py week N --season YEAR --close    # draw and record
  python scripts/league_awards.py month NAME --season YEAR [--close]
  python scripts/league_awards.py render --season YEAR # rewrite the award pages

The method is fixed in career/2013/awards/methodology.json before any
winner is drawn: one scoring formula per category, applied identically to
every player from the closed receipts; the top three in each conference form
the shortlist; the private service supplies the entropy for a weighted panel
pick among them, exactly as it does for a game. No real-world award result is
read anywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.game_runner import _entropy_from_ref
from runtime.league import conference_of
from runtime.packets import canonical
from runtime.seasons import SeasonPaths, require_game_release, require_receipt_season
from scripts.render_season_stats import load_receipts

AWARDS = ROOT / "career/2013/awards"
METHOD = AWARDS / "methodology.json"
RESULTS = AWARDS / "results.json"


def method_path(season=2013):
    return SeasonPaths(season, ROOT).awards / 'methodology.json'


def method(season=2013):
    path = method_path(season)
    if not path.is_file():
        raise FileNotFoundError(
            "No %d awards methodology: freeze %s from the %d schedule before any award is drawn "
            "(see career/2013/awards/methodology.json for the form)" % (season, path.relative_to(ROOT), season))
    return json.loads(path.read_text(encoding="utf-8"))


def score(category, player, m):
    f = m["formulas"][category]
    position = player.get("position")
    total = 0.0
    for part in f["parts"]:
        if part.get("positions") and position not in part["positions"]:
            continue
        for stat, weight in part["weights"].items():
            if stat == "fg_missed":
                value = player.get("field_goals_attempted", 0) - player.get("field_goals_made", 0)
            elif stat == "xp_missed":
                value = player.get("extra_points_attempted", 0) - player.get("extra_points_made", 0)
            elif stat == "punt_yards_over_45":
                value = player.get("punt_yards", 0) - 45 * player.get("punts", 0)
            else:
                value = player.get(stat, 0)
            total += weight * value
    return round(total, 2)


def eligible(category, player, m):
    f = m["formulas"][category]
    return not f.get("positions") or player.get("position") in f["positions"]


def period_weeks(kind, key, m):
    return [int(key)] if kind == "week" else m["months"][key]["weeks"]


def shortlists(kind, key, m, season=2013):
    weeks = set(period_weeks(kind, key, m))
    totals = {}
    receipts = load_receipts(SeasonPaths(season, ROOT).receipts)
    require_receipt_season(receipts, season)
    for receipt in receipts:
        if int(receipt["week"]) not in weeks:
            continue
        for team, stats in receipt["team_stats"].items():
            for name, player in stats["players"].items():
                for category in m["categories"]:
                    if not eligible(category, player, m):
                        continue
                    row = totals.setdefault((conference_of(team), category, name, team),
                                            {"score": 0.0, "games": 0})
                    row["score"] = round(row["score"] + score(category, player, m), 2)
                    row["games"] += 1
    lists = {}
    for conference in ("AFC", "NFC"):
        for category in m["categories"]:
            rows = [(v["score"], name, team) for (c, cat, name, team), v in totals.items()
                    if c == conference and cat == category]
            rows.sort(key=lambda r: (-r[0], r[1], r[2]))
            lists["%s-%s" % (conference, category)] = [
                {"player": n, "team": t, "score": s} for s, n, t in rows[:m["shortlist_size"]]]
    return lists


def event_id(kind, key, award, m, season=2013):
    tag = "week%02d" % int(key) if kind == "week" else key.lower()
    return "%d-award-%s-%s-%s" % (season, tag, award.lower(), m["procedure_tag"])


def packet(kind, key, award, shortlist, m, snapshot, season=2013):
    return {"procedure": m["procedure"], "event_id": event_id(kind, key, award, m, season),
            "snapshot": snapshot, "period": {"kind": kind, "key": str(key)}, "award": award,
            "shortlist": shortlist, "panel_weights": m["panel_weights"][:len(shortlist)],
            "method_sha256": hashlib.sha256((SeasonPaths(season, ROOT).awards / 'methodology.json').read_bytes()).hexdigest()}


def pick(result_ref, pkt):
    entropy = _entropy_from_ref(result_ref)
    rng = random.Random(int.from_bytes(hashlib.sha256(entropy + canonical(pkt)).digest(), "big"))
    weights = pkt["panel_weights"]
    u = rng.random() * sum(weights)
    for index, w in enumerate(weights):
        if u < w:
            return index
        u -= w
    return len(weights) - 1


def load_results(season=2013):
    path = SeasonPaths(season, ROOT).awards / 'results.json'
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def render(season=2013):
    if season >= 2014:
        from scripts.render_award_pages import render_pages
        from runtime.events import preserve_event_comments
        results = load_results(season)
        pages = render_pages(season, results, method(season) if results or method_path(season).is_file() else None)
        for relative, text in pages.items():
            path = SeasonPaths(season, ROOT).awards / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            previous = path.read_text(encoding='utf-8') if path.exists() else ''
            path.write_text(preserve_event_comments(text, previous), encoding='utf-8')
        return
    m, results = method(season), load_results(season)
    lines = ["# %d league awards: weekly and monthly" % season, "",
             "Generated by `scripts/league_awards.py render` from `results.json`. Method: [methodology.json](methodology.json); see [README.md](README.md).", ""]
    for kind, title in (("month", "Monthly awards"), ("week", "Weekly awards")):
        periods = [k for k, v in results.items() if v["kind"] == kind]
        if not periods:
            continue
        lines += ["## " + title, ""]
        for period in sorted(periods, key=lambda p: results[p]["order"]):
            entry = results[period]
            lines += ["### " + entry["label"], "",
                      "| Award | Winner | Team | Score | Shortlist (score) |", "|---|---|---|--:|---|"]
            for award in entry["awards"]:
                a = entry["awards"][award]
                w = a["shortlist"][a["winner_index"]]
                short = "; ".join("%s, %s (%.1f)" % (s["player"], s["team"], s["score"]) for s in a["shortlist"])
                lines.append("| %s | %s | %s | %.1f | %s |" % (m["award_names"][award], w["player"], w["team"], w["score"], short))
            lines += ["", entry.get("note", ""), ""]
    (SeasonPaths(season, ROOT).awards / 'weekly_and_monthly.md').write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=("week", "month", "render"))
    parser.add_argument("key", nargs="?")
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--note", default="")
    parser.add_argument("--season", type=int, required=True)
    args = parser.parse_args()
    paths = SeasonPaths(args.season, ROOT)
    if args.kind == "render":
        render(args.season)
        return 0
    if args.season != 2013:
        try:
            require_game_release(args.season, ROOT)
        except ValueError as exc:
            print("AWARDS: BLOCKED\n- " + str(exc))
            return 1
    try:
        m = method(args.season)
    except FileNotFoundError as exc:
        print("AWARDS: BLOCKED\n- " + str(exc))
        return 1
    if args.kind == "month" and args.key not in m.get("months", {}):
        print("AWARDS: no month %r in the %d methodology" % (args.key, args.season))
        return 1
    weeks = set(period_weeks(args.kind, args.key, m))
    closed = {int(r["week"]) for r in load_receipts(paths.receipts)}
    if not weeks & closed:
        print("AWARDS: BLOCKED\n- no closed %d receipt for %s %s; the award needs the period's closed games "
              "(scripts/close_week.py) before a shortlist exists" % (args.season, args.kind, args.key))
        return 1
    lists = shortlists(args.kind, args.key, m, args.season)
    for award, rows in lists.items():
        print(award, "; ".join("%s (%s) %.2f" % (r["player"], r["team"], r["score"]) for r in rows))
    if not args.close:
        return 0
    results = load_results(args.season)
    period = "%s-%s" % (args.kind, args.key)
    if period in results:
        print("AWARDS: %s already drawn" % period)
        return 1
    from runtime.private_client import Client
    client = Client()
    snapshot = client.current_snapshot()
    entry = {"kind": args.kind, "key": str(args.key),
             "label": ("Week %d" % int(args.key)) if args.kind == "week" else m["months"][args.key]["label"],
             "order": (int(args.key) if args.kind == "week" else 100 + m["months"][args.key]["order"]),
             "note": args.note, "awards": {}}
    for award, rows in lists.items():
        pkt = packet(args.kind, args.key, award, rows, m, snapshot, args.season)
        ref = client.close_event(pkt)
        entry["awards"][award] = {"event_id": pkt["event_id"], "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(),
                                  "result_ref": ref, "shortlist": rows, "winner_index": pick(ref, pkt)}
    results[period] = entry
    (paths.awards / 'results.json').write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    render(args.season)
    return 0


if __name__ == "__main__":
    sys.exit(main())
