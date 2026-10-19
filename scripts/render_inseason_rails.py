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

Rebuild step 4 (docs/rebuild_plan.md, rule 4): from Week 6 the page is the
week's league transactions, football words only: each move's date, club,
move, player and roster status. The window's cutoffs, the counts by club, the
real dates and sources, the held additions, the moves not applied and the
corrections are the rails data's and the library method's; ``--detail``
prints them for the staff who keep the data (the sections listed above, the
computation unchanged) and nothing writes them to a page. The week's record of
the files it was built from and the league state digests at each cutoff
(engineering review B5) is stored beside it in the data area (``meta_path``),
the only record ``check`` reads. A page written before Week 6 keeps its own
bytes and its embedded record (rule 1): ``check`` holds the stored record to
the recomputed digests, requires the page's embedded record to be the same,
and leaves its text, which the page history pins, as written.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import rails  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

BEGIN, END = "<!-- BEGIN GENERATED IN-SEASON RAILS -->", "<!-- END GENERATED IN-SEASON RAILS -->"
# The record of the files and league states a page written before rebuild step 4 embeds.
EMBEDDED_META = re.compile(r"<!-- rails-week: (\{.*?\}) -->")
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


# The page's words for the moves, reasons and sources the rails data names (clean pages).
CLEAN_KIND_TEXT = {"released_unspecified": "Released (roster or practice squad not stated)"}
CLEAN_NOOP_REASONS = {
    "excluded_from_base": "on the real Week 1 roster but not on this club's roster (with Jacksonville, without a "
                          "club, or placed with another club)",
    "earlier_addition_not_applied": "his earlier addition to this club was held, not applied or failed its "
                                    "precondition",
    "ps_base_unverified": "the club's Week 1 practice squad is not verified, so its practice-squad moves are "
                          "incomplete",
    "already_departed": "already off this list",
    "branch_placed_elsewhere": "he is with another club",
    "never_in_branch": "a real departure of a player this club's roster never carried (listed in the Week 1 "
                       "evidence)",
}
CLEAN_OUTCOME_REASONS = {
    "NO_ROSTER_EFFECT": "no roster movement",
    "REVIEW_UNPLACED": "a former Jaguar without a club; his later moves wait for a ruling",
    "REVIEW_IDENTITY": "the player could not be identified from the sources",
    "REVIEW_SOURCE_CONFLICT": "the NFL.com wire and ESPN disagree on the kind of move",
    "EXCLUDED_SOURCE_ERROR": "a source error; the move is carried by the correct record",
    "EXCLUDED_SOURCE_CONFLICT": "the sources conflict; the move is carried by the record they agree on",
}
VERIFICATION_TEXT = {"two_sources": "two sources", "nfl_wire_only": "NFL.com wire only", "espn_only": "ESPN team log only"}


def page_path(season, week, root=ROOT):
    return SeasonPaths(season, root).record("league/personnel/in_season/week_%02d.md" % week)


def meta_path(season, week, root=ROOT):
    """The week's record of the files and league states its page was built from: the page's twin
    in the data area."""
    page = page_path(season, week, root)
    return SeasonPaths(season, root).file_in(page.parent, page.stem + ".json")


def _clean_text(text, fallback):
    """Stored research wording when it is already football words, else the fallback."""
    from runtime.clean_pages import page_errors
    text = str(text or "").strip()
    return text if text and not page_errors("league/page.md", text) else fallback


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


# The league transactions page's words for each move (the briefing's opponent moves use them too).
MOVE_WORDS = {"ps_signing": "Signed to the practice squad", "waived": "Waived", "fa_signing": "Signed as a free agent",
              "ps_promotion": "Promoted from the practice squad", "ps_release": "Released from the practice squad",
              "released": "Released", "released_unspecified": "Released", "re_signing": "Re-signed",
              "ps_poach": "Signed from another club's practice squad", "waiver_claim": "Claimed off waivers",
              "retirement": "Retired", "trade_in": "Acquired in a trade", "trade_out": "Traded away",
              "reserve_injured": "Placed on reserve/injured", "suspension": "Suspended",
              "activation_return": "Activated from the reserve list"}
# Each move's roster status once it took effect, by the replay's action.
STATUS_TEXT = {"added_active": "On the 53", "filled_active": "On the 53", "emergency_promotion": "On the 53",
               "added_practice_squad": "Practice squad", "filled_practice_squad": "Practice squad",
               "removed_active": "Off the 53", "removed_practice_squad": "Off the practice squad",
               "implied_ps_release": "Off the practice squad", "removed_reserve": "Off the reserve list",
               "retired": "Retired", "retired_jacksonville": "Retired", "branch_reserve": "Reserve/injured"}
BRANCH_MOVES = {"branch_reserve": "Placed on reserve/injured", "emergency_promotion": "Promoted from the practice squad"}


def move_words(kind):
    return MOVE_WORDS.get(kind) or str(kind or "").replace("_", " ").capitalize()


def render(season, week, root=ROOT, receipts=None, event=None):
    """The week's league transactions page: every roster move by the other clubs that took effect
    in the week's window, with its date, club, move, player and roster status, from the data
    effective for that week only (later shards never change it). How a move is held for a roster
    place, which moves never reach a roster and how the opening rosters were set are the rails
    data's and the library method's, printed by ``detail`` (``--detail``), never on the page."""
    slate, start, end = week_record(season, week, root, receipts)
    data = slate["data"]
    last = slate["states"][max(slate["states"])]
    first_week = week == data.effective_from_week
    rows = {r["id"]: r for r in data.rows}
    shards = [s for s in data.manifest["shards"] if int(s["week"]) <= week]
    as_of = max(date.fromisoformat(s["through"]) for s in shards)
    clubs = {code: name for name, code in data.codes.items()}
    moves = []
    for e in last.log:
        if not (first_week or (start and date.fromisoformat(e["date"]) >= start)) or e["action"] not in STATUS_TEXT:
            continue
        if e["ref"] in rows:
            kind = rows[e["ref"]]["kind"]
            move = "Signed away from the practice squad" if e["action"] == "implied_ps_release" else move_words(kind)
        elif e["action"] in BRANCH_MOVES:
            move = BRANCH_MOVES[e["action"]]
        else:
            continue
        player = e.get("player_id") or (rows.get(e["ref"]) or {}).get("player_id") or ""
        # A same-named player's id carries his club's code ("Charles Johnson (CLE)"); the club column names it.
        player = re.sub(r" \((%s)\)$" % "|".join(map(re.escape, clubs)), "", player)
        moves.append([_fmt(e["date"]), clubs.get(e["club"], e["club"]), move, player, STATUS_TEXT[e["action"]]])
    window = ("every move since the opening week's rosters, through %s" % _fmt(end)) if first_week else \
        "moves from %s to %s" % (_fmt(start), _fmt(end))
    lines = ["# League transactions: Week %d, %d" % (week, season), "",
             "Roster moves by the other 31 clubs that took effect before the Week %d games: %s. Transactions on "
             "file through %s. [Sources](../../../../../library/%d_inseason_rails.md)" % (week, window, _fmt(as_of), season), ""]
    if moves:
        lines += ["| Date | Club | Move | Player | Status |", "|---|---|---|---|---|"]
        lines += ["| %s |" % " | ".join(str(c).replace("|", "/") for c in row) for row in moves]
    else:
        lines.append("No roster move took effect.")
    text = "\n".join(lines).rstrip("\n") + "\n"
    if event:
        text += "\n<!-- event-record: %s -->\n" % json.dumps(event, sort_keys=True)
    return text


def detail(season, week, root=ROOT, receipts=None):
    """The week's full record for the staff who keep the rails data (printed by ``--detail``,
    never a page): the cutoffs, the counts by club, every move with its real date and sources,
    the held additions, the moves not applied and the corrections. Every count, row and order is
    the computation the weekly record has always used."""
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
    lines = ["# League roster moves in detail: Week %d, %d" % (week, season), ""]
    window = ("every move dated on or before %s (the moves since the Week 1 rosters take effect together, each "
              "in its real order)" % _fmt(end)) if first_week else \
        "moves dated %s to %s" % (_fmt(start), _fmt(end))
    lines += ["The other 31 clubs' real roster moves as they take effect before this week's games.", "",
              "**Window:** %s. **Recorded through:** %s. **Sources and method:** [the league's in-season roster "
              "moves](../../../../../library/%d_inseason_rails.md)." % (window, _fmt(as_of), season), ""]
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
    lines += ["## Moves that took effect", "", "| Real date | Club | Move | Player | Basis | Source | Took effect |",
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
            _fmt(r["real_date"]), r["club"], kind_text(r["kind"]), r["player_id"],
            r["date_basis"].replace("_", " "),
            src or VERIFICATION_TEXT.get(r["verification"], str(r["verification"]).replace("_", " ")),
            ACTION_TEXT[e["action"]], _fmt(e["date"])))
    lines.append("")
    # 4. held
    lines += ["## Held additions", "", "| Club | Player | Real move | Held since | Waiting for |", "|---|---|---|---|---|"]
    for code in sorted(last.held):
        for layer in ("active", "practice_squad"):
            for h in last.held[code][layer]:
                r = rows.get(h["ref"], {})
                lines.append("| %s | %s | %s | %s | a place on the %s |" % (
                    code, h["info"]["player_id"], kind_text(r.get("kind", "")),
                    _fmt(h["since"]), "53" if layer == "active" else "practice squad"))
    lines.append("")
    # 5. not applied
    lines += ["## Not applied", "",
              "Real injuries, suspensions and availability lists, and every move involving Jacksonville's players or "
              "the real Jaguars, are counted by club only; they never change a roster.", "",
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
            reason = CLEAN_NOOP_REASONS.get(e["reason"]) or _clean_text(
                rails.NOOP_REASONS.get(e["reason"], e["reason"]), "not applied")
            lines.append("| %s | %s | %s | %s |" % (r["club"], r.get("player_id") or "", kind_text(r["kind"]),
                                                   reason))
    for r in data.rows:
        if r["outcome"] not in ("APPLY",) and r["outcome"] not in rails.STRIPPED_OUTCOMES and \
                _in_window(r, lasts, start, end, first_week):
            generic = CLEAN_OUTCOME_REASONS.get(r["outcome"], "not applied")
            reason = generic if r["outcome"].startswith("REVIEW_") else _clean_text(r["reason"], generic)
            lines.append("| %s | %s | %s | %s |" % (r["club"], r.get("player_id") or r.get("player", ""),
                                                   kind_text(r["kind"]), reason))
    lines.append("")
    # 6. corrections
    lines += ["## Corrections and decisions", ""]
    if first_week:
        corr = collections.Counter(c["kind"] for c in data.base["corrections"])
        lines += ["The Week 1 rosters take effect first: the real Week 1 roster players the Week 1 depth charts left "
                  "out (%d), the players on a league suspension or exempt list at Week 1 restored to their clubs, "
                  "available (%d), and %d dated window correction(s); practice squads as of September 1, verified "
                  "for %d of %d clubs. Details: [the league's in-season roster moves]"
                  "(../../../../../library/%d_inseason_rails.md#the-base)." % (
                      corr["fill"], corr["restoration"], corr["window"],
                      sum(1 for c in data.base["clubs"].values() if c["ps_base_verified"]), len(data.base["clubs"]),
                      season), ""]
    c6 = sum(1 for e in slate["c6"] if _in_window(e, lasts, start, end, first_week))
    emergencies = sum(1 for e in slate["emergencies"] if int(e["effective_from_week"]) == week)
    if c6 or emergencies:
        lines += ["From this season's games: %d reserve-list placement(s) after injuries and %d emergency "
                  "promotion(s) from a practice squad." % (c6, emergencies), ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def kind_text(kind):
    return CLEAN_KIND_TEXT.get(kind) or KIND_TEXT.get(kind) or str(kind or "").replace("_", " ")


def week_meta(season, week, root=ROOT, receipts=None):
    """The record of the files and league states a week's page is built from: the base's and the
    effective shards' sha256 and the state digest at each of the week's cutoffs."""
    slate, _, _ = week_record(season, week, root, receipts)
    data = slate["data"]
    shards = [s for s in data.manifest["shards"] if int(s["week"]) <= week]
    as_of = max(date.fromisoformat(s["through"]) for s in shards)
    return {"season": season, "week": week, "as_of": as_of.isoformat(),
            "files": {s["path"]: s["sha256"] for s in shards} | {
                data.manifest["base"]["path"]: data.manifest["base"]["sha256"]},
            "state_digests": {c.isoformat(): s.digest() for c, s in sorted(slate["states"].items())}}


def write(season, week, root=ROOT, receipts=None, event=None):
    """Write the week's page and its record beside it in the data area. An event-record line the
    page already carries is kept (the batch's event); a new ``event`` is added."""
    from runtime.events import preserve_event_comments
    path = page_path(season, week, root)
    previous = path.read_text(encoding="utf-8") if path.is_file() else ""
    text = preserve_event_comments(render(season, week, root, receipts, event), previous)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    meta = meta_path(season, week, root)
    meta.parent.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps(week_meta(season, week, root, receipts), indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def _history_page(rel, data, root):
    """Whether a page is kept as written before Week 6 (its bytes match the page history)."""
    from runtime import clean_pages
    return clean_pages.unchecked_prefix(data, clean_pages.history(root).get(rel),
                                        clean_pages.history_lengths(root).get(rel)) == len(data)


def _without_events(text):
    from runtime.events import EVENT_META
    return EVENT_META.sub("", text).rstrip() + "\n"


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
        before = [r for r in receipts if int(r["week"]) < week]
        rel = path.relative_to(root).as_posix()
        expected = week_meta(season, week, root, before)
        stored = meta_path(season, week, root)
        if not stored.is_file():
            errors.append("in-season rails record missing: %s (the week's record of its files and league states); "
                          "run python scripts/render_inseason_rails.py --season %d --week %d --write"
                          % (stored.relative_to(root).as_posix(), season, week))
            continue
        recorded = json.loads(stored.read_text(encoding="utf-8"))
        embedded = EMBEDDED_META.search(current)
        if embedded and json.loads(embedded.group(1)) != recorded:
            # A page written before Week 6 carries its record too; the stored record must be the same.
            errors.append("in-season rails record differs from the record its page carries: %s" % rel)
        if recorded != expected:
            errors.append("in-season rails record stale: %s" % rel)
        elif not _history_page(rel, current.encode("utf-8"), root) and \
                _without_events(current) != _without_events(render(season, week, root, before)):
            errors.append("in-season rails record stale: %s" % rel)
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
    parser.add_argument("--detail", action="store_true",
                        help="print the week's full record (counts, held additions, moves not applied); writes nothing")
    args = parser.parse_args()
    if args.check:
        errors = check(args.season)
        print("\n".join(errors) if errors else "IN-SEASON RAILS RECORDS: CURRENT")
        return 1 if errors else 0
    if args.week is None:
        parser.error("--week is required unless --check")
    event = json.loads(args.event) if args.event else None
    if args.detail:
        sys.stdout.write(detail(args.season, args.week))
        return 0
    if args.write:
        path = write(args.season, args.week, event=event)
        print("Written: %s and its record %s" % (path.relative_to(ROOT), meta_path(args.season, args.week).relative_to(ROOT)))
        return 0
    sys.stdout.write(render(args.season, args.week, event=event))
    return 0


if __name__ == "__main__":
    sys.exit(main())
