#!/usr/bin/env python3
"""Render one week's in-season rails record from the committed rails data.

  python scripts/render_inseason_rails.py --season 2014 --week N            # print
  python scripts/render_inseason_rails.py --season 2014 --week N --write    # write the page
  python scripts/render_inseason_rails.py --season 2014 --check             # every existing page current

The page is `career/YEAR/League/personnel/in_season/week_NN.md` (the record
owner in docs/repository_map.json). It is written by the week's batch only
once the master clock has passed every move it lists; nothing here advances
the clock, writes Record.md or changes Document 4 or 5. Its generated block
carries the files' sha256 and a digest of the league state at each of the
week's cutoffs, which validate_repository recomputes for every closed week
(engineering review B5).

Sections (library/2014_inseason_rails.md, "The weekly record"):
1. window, cutoff per game, sources and the two-pass summary;
2. by club: additions applied, departures applied, held, filled from hold,
   not applied (counts);
3. applied moves (Real date | Club | Move | Player | Detail | Source | Applied
   in the branch);
4. held additions;
5. not applied: real injuries, suspensions, availability and Jacksonville
   rows as per-club counts only (rules review C6); other reasons listed;
6. corrections and decisions (base corrections the week applies first);
7. the event-record comment, which the batch supplies with --event.
"""
from __future__ import annotations

import argparse
import collections
import json
from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import rails  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

BEGIN, END = "<!-- BEGIN GENERATED IN-SEASON RAILS -->", "<!-- END GENERATED IN-SEASON RAILS -->"
KIND_TEXT = {"waived": "Waived", "released": "Released", "trade_out": "Traded away", "ps_release": "Practice-squad release",
             "released_unspecified": "Released (layer unspecified)", "retirement": "Retired",
             "ps_promotion": "Promoted from the practice squad", "waiver_claim": "Waiver claim", "trade_in": "Trade",
             "fa_signing": "Free-agent signing", "re_signing": "Re-signing", "activation_return": "Activated (pre-Week 1 list)",
             "ps_poach": "Signed off another club's practice squad", "ps_signing": "Practice-squad signing"}
ACTION_TEXT = {"added_active": "Applied: on the 53", "added_practice_squad": "Applied: practice squad",
               "removed_active": "Applied: off the 53", "removed_practice_squad": "Applied: off the practice squad",
               "removed_reserve": "Applied: off the reserve list", "filled_active": "Applied from hold: on the 53",
               "filled_practice_squad": "Applied from hold: practice squad", "held_active": "Held: no place on the 53",
               "held_practice_squad": "Held: no practice-squad place", "hold_lapsed": "Hold lapsed",
               "retired": "Applied: retired", "retired_jacksonville": "Applied: retired (Jacksonville's retirement record)",
               "already_there": "Already in the base", "in_base": "Reflected in the base",
               "noop": "No-op", "not_applied": "Not applied", "implied_ps_release": "Applied: released from another squad"}


def page_path(season, week, root=ROOT):
    return SeasonPaths(season, root).record("league/personnel/in_season/week_%02d.md" % week)


def _fmt(day):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    return day.strftime("%B %-d, %Y")


def week_record(season, week, root=ROOT, receipts=None):
    """(slate, window start, window end) for the week; receipts default to
    every closed receipt before the week."""
    from runtime import week_inputs
    from scripts.render_season_stats import load_receipts
    paths = SeasonPaths(season, root)
    if receipts is None:
        receipts = [r for r in load_receipts(paths.receipts) if int(r["week"]) < week]
    slate = week_inputs.rails_slate(week, season, receipts, root=root)
    if slate is None:
        raise ValueError("Week %d of %d is before the in-season rails' effective week" % (week, season))
    lasts = slate["last_cutoffs"]
    start = lasts[week - 1] + timedelta(days=1) if week - 1 in lasts else None
    end = max(slate["cutoffs"].values())
    return slate, start, end


def _in_window(item, lasts, start, end, first_week):
    """Whether a row or branch event replays inside the week's window: on or
    before its last cutoff and, after the first week, after the previous
    week's (a later shard's row can never enter a closed week's page)."""
    when = rails.replay_date(item, lasts)
    return when <= end and (first_week or when >= start)


def render(season, week, root=ROOT, receipts=None, event=None):
    """The week's page from the data effective for that week only: the base
    and the shards of weeks up to `week`, and rows and branch events that
    replay inside the week's window. Later shards never change it."""
    from runtime.week_inputs import event_id, schedule
    slate, start, end = week_record(season, week, root, receipts)
    data = slate["data"]
    lasts = slate["last_cutoffs"]
    last = slate["states"][max(slate["states"])]
    first_week = week == data.effective_from_week
    rows = {r["id"]: r for r in data.rows}
    shards = [s for s in data.manifest["shards"] if int(s["week"]) <= week]
    as_of = max(date.fromisoformat(s["through"]) for s in shards)
    in_week = [e for e in last.log if (first_week or (start and date.fromisoformat(e["date"]) >= start))
               and e["ref"] in rows]
    games = schedule(week, season)
    lines = [BEGIN, "# In-season rails: Week %d, %d" % (week, season), ""]
    meta = {"season": season, "week": week, "as_of": as_of.isoformat(),
            "files": {s["path"]: s["sha256"] for s in shards} | {
                data.manifest["base"]["path"]: data.manifest["base"]["sha256"]},
            "state_digests": {c.isoformat(): s.digest() for c, s in sorted(slate["states"].items())}}
    lines += ["<!-- rails-week: %s -->" % json.dumps(meta, sort_keys=True), ""]
    window = ("every committed move gated on or before %s (the backlog since the Week 1 base enters as one dated "
              "batch, each move in its real order)" % _fmt(end)) if first_week else \
        "moves gated %s to %s" % (_fmt(start), _fmt(end))
    lines += ["**Window:** %s. **Committed through:** %s. **Method and sources:** [in-season rails record]"
              "(../../../../../library/%d_inseason_rails.md)." % (window, _fmt(as_of), season), ""]
    lines += ["| Game | Date | Cutoff |", "|---|---|---|"]
    for g in sorted(games, key=lambda g: (g["date"], g.get("kickoff_et") or "", event_id(g, season=season))):
        lines.append("| %s at %s | %s | %s |" % (g["away"], g["home"], _fmt(g["date"]),
                                                _fmt(slate["cutoffs"][rails.game_key(g)])))
    lines.append("")
    # 2. by club
    counts = collections.defaultdict(collections.Counter)
    for e in in_week:
        counts[e["club"]][e["action"]] += 1
    stripped = collections.defaultdict(collections.Counter)
    for r in data.rows:
        if r["outcome"] in rails.STRIPPED_OUTCOMES and _in_window(r, lasts, start, end, first_week):
            stripped[r["club"]][r["outcome"]] += 1
    lines += ["## By club", "", "| Club | Additions applied | Departures applied | Held at the last cutoff | "
              "Filled from hold | Not applied |", "|---|---|---|---|---|---|"]
    for code in sorted(last.clubs):
        c = counts[code]
        held = len(last.held[code]["active"]) + len(last.held[code]["practice_squad"])
        not_applied = sum(stripped[code].values()) + c["not_applied"]
        lines.append("| %s | %d | %d | %d | %d | %d |" % (
            code, c["added_active"] + c["added_practice_squad"],
            c["removed_active"] + c["removed_practice_squad"] + c["removed_reserve"] + c["retired"],
            held, c["filled_active"] + c["filled_practice_squad"], not_applied))
    lines.append("")
    # 3. applied
    lines += ["## Applied moves", "", "| Real date | Club | Move | Player | Detail | Source | Applied in the branch |",
              "|---|---|---|---|---|---|---|"]
    for e in in_week:
        if e["action"] not in ("added_active", "added_practice_squad", "removed_active", "removed_practice_squad",
                               "removed_reserve", "filled_active", "filled_practice_squad", "retired",
                               "retired_jacksonville", "implied_ps_release"):
            continue
        r = rows[e["ref"]]
        src = "; ".join("%s %s" % ({"nfl_wire": "NFL.com wire", "espn": "ESPN team log"}.get(k, k), v["date"])
                        for k, v in r.get("sources", {}).items() if isinstance(v, dict))
        lines.append("| %s | %s | %s | %s | %s | %s | %s (%s) |" % (
            _fmt(r["real_date"]), r["club"], KIND_TEXT.get(r["kind"], r["kind"]), r["player_id"],
            r["date_basis"].replace("_", " "), src or r["verification"], ACTION_TEXT[e["action"]], _fmt(e["date"])))
    lines.append("")
    # 4. held
    lines += ["## Held additions", "", "| Club | Player | Real move | Held since | Waiting for |", "|---|---|---|---|---|"]
    for code in sorted(last.held):
        for layer in ("active", "practice_squad"):
            for h in last.held[code][layer]:
                r = rows.get(h["ref"], {})
                lines.append("| %s | %s | %s | %s | a place on the %s |" % (
                    code, h["info"]["player_id"], KIND_TEXT.get(r.get("kind"), r.get("kind", "")),
                    _fmt(h["since"]), "53" if layer == "active" else "practice squad"))
    lines.append("")
    # 5. not applied
    lines += ["## Not applied", "",
              "Real injuries, suspensions, availability lists and every Jacksonville or real-Jaguars row are counted "
              "by club only; they never touch membership (rails rules 2 and 4).", "",
              "| Club | Injury | Suspension | Availability | Jacksonville control | Real Jaguars |", "|---|---|---|---|---|---|"]
    for code in sorted(stripped):
        s = stripped[code]
        lines.append("| %s | %d | %d | %d | %d | %d |" % (code, s["NOT_APPLIED_INJURY"], s["NOT_APPLIED_SUSPENSION"],
                                                       s["NOT_APPLIED_AVAILABILITY"], s["NOT_APPLIED_JAX_CONTROL"],
                                                       s["NOT_APPLIED_REAL_JAGUARS"]))
    lines += ["", "| Club | Player | Real move | Why not applied |", "|---|---|---|---|"]
    for e in in_week:
        if e["action"] in ("not_applied", "noop"):
            r = rows[e["ref"]]
            reason = rails.NOOP_REASONS.get(e["reason"], e["reason"])
            lines.append("| %s | %s | %s | %s |" % (r["club"], r.get("player_id") or "", KIND_TEXT.get(r["kind"], r["kind"]),
                                                   reason))
    for r in data.rows:
        if r["outcome"] not in ("APPLY",) and r["outcome"] not in rails.STRIPPED_OUTCOMES and \
                _in_window(r, lasts, start, end, first_week):
            lines.append("| %s | %s | %s | %s |" % (r["club"], r.get("player_id") or r.get("player", ""),
                                                   KIND_TEXT.get(r["kind"], r["kind"]), r["reason"]))
    lines.append("")
    # 6. corrections
    lines += ["## Corrections and decisions", ""]
    if first_week:
        corr = collections.Counter(c["kind"] for c in data.base["corrections"])
        lines += ["The base enters first: the real Week 1 roster players the Week 1 chart left out (%d), the players "
                  "on a league suspension or exempt list at Week 1 restored to their clubs, available (%d), and %d "
                  "dated window correction(s); practice squads as of September 1, verified for %d of %d clubs. "
                  "Details: [in-season rails record](../../../../../library/%d_inseason_rails.md#the-base)." % (
                      corr["fill"], corr["restoration"], corr["window"],
                      sum(1 for c in data.base["clubs"].values() if c["ps_base_verified"]), len(data.base["clubs"]),
                      season), ""]
    c6 = sum(1 for e in slate["c6"] if _in_window(e, lasts, start, end, first_week))
    emergencies = sum(1 for e in slate["emergencies"] if int(e["effective_from_week"]) == week)
    if c6 or emergencies:
        lines += ["Branch events: %d branch reserve placement(s) (C6) and %d emergency promotion(s)." % (
            c6, emergencies), ""]
    lines.append(END)
    text = "\n".join(lines) + "\n"
    if event:
        text += "\n<!-- event-record: %s -->\n" % json.dumps(event, sort_keys=True)
    return text


def check(season=2014, root=ROOT):
    """Errors for every existing weekly page that differs from its render,
    and for every closed week at or after the effective week with no page."""
    from scripts.render_season_stats import load_receipts
    data = rails.load(season, root)
    if data is None:
        return []
    errors = []
    receipts = load_receipts(SeasonPaths(season, root).receipts)
    closed = sorted({int(r["week"]) for r in receipts})
    folder = page_path(season, data.effective_from_week, root).parent
    weeks = set(w for w in closed if w >= data.effective_from_week)
    if folder.is_dir():
        weeks |= {int(p.stem.split("_")[1]) for p in folder.glob("week_*.md")}
    for week in sorted(weeks):
        path = page_path(season, week, root)
        if not path.is_file():
            errors.append("closed Week %d has no in-season rails record: %s" % (week, path.relative_to(root)))
            continue
        current = path.read_text(encoding="utf-8")
        generated = render(season, week, root, [r for r in receipts if int(r["week"]) < week])
        block = current.split(END)[0] + END + "\n" if END in current else current
        if block != generated.split(END)[0] + END + "\n":
            errors.append("in-season rails record stale: %s" % path.relative_to(root))
    later = [w for w in closed if w >= data.effective_from_week]
    if later:
        from runtime import week_inputs
        week = max(later)
        slate, _, _ = week_record(season, week, root, [r for r in receipts if int(r["week"]) < week])
        last = slate["states"][max(slate["states"])]
        dates = {(g["week"], g["away"], g["home"]): g["date"] for g in SeasonPaths(season, root).regular_games()}
        errors += rails.receipt_departure_errors(last, [r for r in receipts if int(r["week"]) < week], dates,
                                                 data.codes, data.effective_from_week)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--week", type=int)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--event", help="event-record JSON for the batch that applies the week")
    args = parser.parse_args()
    if args.check:
        errors = check(args.season)
        print("\n".join(errors) if errors else "IN-SEASON RAILS RECORDS: CURRENT")
        return 1 if errors else 0
    if args.week is None:
        parser.error("--week is required unless --check")
    text = render(args.season, args.week, event=json.loads(args.event) if args.event else None)
    if args.write:
        path = page_path(args.season, args.week)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print("Written: %s" % path.relative_to(ROOT))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
