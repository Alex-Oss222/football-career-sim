"""Rebuild step 5, acceptance test 5: a synthetic Week 11 bye close, in a temporary copy.

The copy is the real checkout while its season has not closed the week before the bye. From then the
real bye's review, answers and close are history and the season has no other bye, so the copy's season
records and state are those of PRE_BYE, the merge that closed Week 7, read from the checkout's git
history under the checkout's own code, tests and docs (a checkout without that history, as in the engine
image's verification stage, has no such state to start from, and the test says so and is skipped).
The copy is brought to the evening of Jacksonville's game before the bye by relabelled week closes
(tests/test_week_close_pages.py's model), one week at a time from the copy's open week: each week's
games are an earlier closed week's games moved onto its fixtures (Jacksonville's on Jacksonville's,
the same scores and statistics, a fake result for the copy only), every other club's lines given to
that club's own players at the game (its in-season rails entry for the slate), so the rails' closed-week
invariant holds; the evening's clock and medical instructions; the practice week as Stone's standing
instruction sets it (its pads on the Wednesdays of Weeks 7 and 9 use the last of the eleven); the
Game Report; the week's decisions settled; the week's and the month's awards and the weekly
head-coach check drawn through the local test service (tests/local_private_service.py; the copy's
rate table zeroed, so no change is drawn); then the one page rebuild.

The bye, then, in the runner's order, at mid-week records of the clock (docs/run_week.md, steps 4a
and "The bye week from 2014"), every page check passing at each commit point (the page rebuild's
check, nothing re-recorded as history, and repository validation of the copy, the clean-page check
among it, adding nothing to the real checkout's):

1. At Week 10's close the bye is the open period: the Bye Week Review is issued from stored facts, the
   blank My Adjustments written and the one bye item opened, holding only the bye's close; Week 12's
   briefing and items are not issued and nothing holds the week's slate.
2. Monday: a test roster question (an injury replacement, Caldwell's to decide on Stone's
   recommendation) issues the review again for its answer, the earlier copy kept and the bye's My
   Responses opened; he answers; Caldwell decides it from his criteria (one result page on the bye's
   index). Stone's first drafts of My Adjustments are refused: required film on the break's Saturday,
   and pads with none of the eleven left.
3. Tuesday: the staff's stored assessment issues the review again (rule b), Monday's result under FOR
   YOUR INFORMATION there.
4. Thursday, the slate's first game day, with the bye item still open: scripts/build_week_inputs.py
   and scripts/close_week.py --close for the bye week run in the copy as the runner runs them (the
   readiness check among them) and close the other clubs' games; no Jacksonville input, receipt,
   score or box score; the week's awards and head-coach check follow; the bye cannot close.
5. Thursday, later: his final My Adjustments ("No change" on offense and special teams, a correction
   on defense, the four-day break and the staff's work of section 6) is checked and applied.
6. Friday: a second test roster question issues the review again; it is answered and decided after
   the bye's last issue.
7. Sunday: the bye's practice and rest record with the legal break; the staff's Bye Week Report held
   to the records (a box score, a wrong record and a pasted result each refused); the bye closes.
8. Week 12 opens: its items and its first brief, whose FOR YOUR INFORMATION window counts from the
   bye's last review (Friday's result there, Monday's not); neither result on its index; the club's
   record as it entered the bye.

Every event is test data (its source a test page the copy alone holds, its summary saying so). The one
gate the copy's build and close pass by is the in-season rails coverage (the other clubs' real moves
through the slate's cutoff, a separate data commit researched in two passes when the clock reaches
it); the copy's player-state binding record is the test store's, written from its bind reply as
scripts/bind_latent_season.py writes the deployed one's. Weeks and dates come from the fixtures and
receipts, never from today's date; the only service contacted is the local test service, and nothing
is written to the real repository. The engine is not touched.
"""
import contextlib
import hashlib
import io
import json
from datetime import date, timedelta
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "scripts"))      # scripts/check_game_readiness.py imports its neighbours bare

from runtime import bye_week, clean_pages, events, open_events, practices, rails, week_pages  # noqa: E402
from runtime.seasons import GAME_REPORT, SeasonPaths  # noqa: E402
from runtime.week_inputs import event_id, receipt_name  # noqa: E402
import support_events as se  # noqa: E402
from local_private_service import TOKEN, local_service  # noqa: E402
from test_game_report import template_report  # noqa: E402
from test_week_close_pages import check_head_coaches, ours_first, record_practice, relabel  # noqa: E402

JAX = se.CLUB
SEASON = se.SEASON
BYE = bye_week.byes(SEASON, ROOT)[0]
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
WEEK_BOUND = ("defensive_calls", "defensive_call_stats", "decision_policies")
# The one gate the copy's build and close pass by (Rehearsal.slate_close): the in-season rails coverage.
RAILS_GATE = "In-season rails: the moves are committed through"
# The copy's start once the real season has closed the week before the bye: the season's records and state
# as the merge that closed Week 7 left them (pull request #265, on main; CI checks out the full history).
# The in-season rails data is dated by the clock (rails.data_errors), so it goes back with the state, and
# with it its two dependants: the DB-family table pins its manifest's digest and the library record links
# its weekly shards.
PRE_BYE = "60767eb165029b7e49a8e1fe7d73a90d662b6001"
PRE_BYE_PATHS = ("career", "data", "state", "library/data/2014_inseason_rails", "library/data/2014_db_families.json",
                 "library/2014_inseason_rails.md")
SLATE = """
import sys
sys.path.insert(0, '.')
from runtime import rails
real = rails.week_cutoff_coverage_error
def coverage(*args):
    gate = real(*args)
    assert gate is None or gate.startswith(%(rails)r), gate
    return None
rails.week_cutoff_coverage_error = coverage
from scripts import %(script)s as script
sys.argv = ['%(script)s.py', '%(week)d', '--season', '%(season)d'%(close)s]
sys.exit(script.main())
"""


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = call(*args, **kwargs)
    return result, out.getvalue()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def players_by_weight(stats):
    """A side's players, the most involved first (snaps), so starters take starters' lines."""
    return sorted(stats["players"].items(), key=lambda kv: (-sum(v for k, v in kv[1].items() if k.endswith("_snaps")
                                                                 and isinstance(v, int)), kv[0]))


def cast(donor_stats, tiers):
    """{donor player: the new club's player}: each line of the donor side given to one of the new
    club's own players at the game (``tiers``, his available players first, then the rest of the
    club), the same position first, then the same group, then any, so every player in the moved
    receipt plays for his own club."""
    from runtime.rails import group
    out = {}
    donors = players_by_weight(donor_stats)
    for pool in tiers:
        free = [p for p in pool if p["player_id"] not in {q["player_id"] for q in out.values()}]
        for match in (lambda d, p: d["position"] == p["position"],
                      lambda d, p: group(d["position"]) == group(p["position"]), lambda d, p: True):
            for name, row in donors:
                if name in out:
                    continue
                found = next((p for p in free if match(row, p)), None)
                if found is not None:
                    out[name] = found
                    free.remove(found)
    missing = [name for name, _ in donors if name not in out]
    if missing:
        raise ValueError("the club has too few players for the moved lines: %s" % ", ".join(missing))
    return out


def moved(receipt, before, after, pools=None):
    """A closed game's receipt relabelled onto another fixture: the clubs renamed (Jacksonville stays
    Jacksonville), each other club's lines given to that club's own players at the game (``pools``,
    {club: (its available players at the game, the rest of the club)}), the week and the event the new
    fixture's; the scores and statistics stay with their sides (a fake result, for the copy only)."""
    if JAX in (before["away"], before["home"]):
        other = before["home"] if before["away"] == JAX else before["away"]
        names = {other: after["home"] if after["away"] == JAX else after["away"]}
    else:
        names = {before["away"]: after["away"], before["home"]: after["home"]}
    positions = {}
    for old, new in list(names.items()):
        if pools is None or new == JAX:
            continue
        for name, player in cast(receipt["team_stats"][old], pools[new]).items():
            names[name] = player["player_id"]
            positions[player["player_id"]] = player["position"]
    receipt = relabel(receipt, names)
    for side in (after["away"], after["home"]):
        for name, row in receipt["team_stats"][side]["players"].items():
            if name in positions:
                row["position"] = positions[name]
    for key in WEEK_BOUND:
        receipt.pop(key, None)
    receipt.update({"week": int(after["week"]), "away": after["away"], "home": after["home"],
                    "matchup": "%s at %s" % (after["away"], after["home"]), "event_id": event_id(after, season=SEASON)})
    return receipt


class SlateMemo:
    """runtime/week_inputs.rails_slate for this test process, memoized on every input it reads: the week,
    the closed games it is given, the copy's root, its committed rails data (the manifest's digest) and
    Jacksonville's dated control there (rails.jacksonville_control). The page rebuild and repository
    validation replay each closed week's slate from the rails' effective week several times over, and
    in a copy ten weeks into the season one pass costs minutes; the result is the function's own, so no
    check reads a stale slate. A call that passes its own data or control is not memoized."""

    def __init__(self, real):
        self.real, self.cache = real, {}

    def __call__(self, week, season, receipts, games=None, root=None, data=None, control=None, strict=True):
        from runtime import week_inputs
        root = week_inputs.ROOT if root is None else root
        if data is not None or control is not None:
            return self.real(week, season, receipts, games, root, data, control, strict)
        manifest = rails.data_dir(season, root) / "manifest.json"
        key = (int(week), int(season), str(Path(root).resolve()), bool(strict),
               hashlib.sha256(json.dumps(receipts, sort_keys=True).encode("utf-8")).hexdigest(),
               json.dumps(games, sort_keys=True), digest(manifest) if manifest.is_file() else None,
               hashlib.sha256(repr(rails.jacksonville_control(season, root)).encode("utf-8")).hexdigest())
        if key not in self.cache:
            self.cache[key] = self.real(week, season, receipts, games, root, data, control, strict)
        return self.cache[key]


class Rehearsal:
    """The runner's steps in the copy at ``self.root`` (a unittest.TestCase mixin)."""

    # ------------------------------------------------------------------ helpers
    @property
    def paths(self):
        return SeasonPaths(SEASON, self.root)

    def fixtures(self, week):
        return ours_first(g for g in self.paths.regular_games() if int(g["week"]) == week)

    def closed_weeks(self):
        return sorted({int(p.name[5:7]) for p in self.paths.receipts.glob("week_*.json")})

    def rebuild(self, label=""):
        from scripts import rebuild_pages
        written, problems = rebuild_pages.rebuild(self.root, SEASON)
        self.assertEqual(problems, [], label)
        return written

    def assert_pages(self, label=""):
        """Every page check passes: nothing stale or unclean, nothing re-recorded as history (the copy's
        history as it started), and validation of the copy adds nothing to the real checkout's."""
        from scripts import rebuild_pages
        from scripts.validate_repository import validate
        self.assertEqual(rebuild_pages.rebuild(self.root, SEASON, check=True), ([], []), label)
        self.assertEqual(clean_pages.history(self.root), self.history, label)
        if not hasattr(type(self), "baseline"):
            type(self).baseline = set(validate(ROOT))
        self.maxDiff = None
        self.assertEqual(sorted(set(validate(self.root)) - self.baseline), [], label)

    def clock(self, line):
        se.set_clock(self.root, line)

    def checkpoint(self, checkpoint):
        state = self.root / se.STATE
        text, n = re.subn(r"^(\*\*Global package checkpoint:\*\* `)[^`]+(`)", r"\g<1>%s\g<2>" % checkpoint,
                          state.read_text(encoding="utf-8"), count=1, flags=re.M)
        self.assertEqual(n, 1)
        state.write_text(text, encoding="utf-8")

    def next_sequence(self):
        return max(item["sequence"] for _, _, item in events.closures(events.load_events(self.root))) + 1

    def pre_bye(self):
        """The copy's season records and state put back to PRE_BYE from the checkout's git history (git
        archive of PRE_BYE_PATHS), its code, tests and docs left as the checkout's. Without git or that
        commit (the engine image's verification stage, a shallow clone) there is no state to start from
        and the test is skipped, as scripts/validate_repository.py skips its commit-order check there."""
        import subprocess

        def git(*args):
            return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True)
        if shutil.which("git") is None or not (ROOT / ".git").exists():
            self.skipTest("the pre-bye state is read from git history, which this checkout lacks (the engine image)")
        if git("cat-file", "-e", PRE_BYE + "^{commit}").returncode != 0:
            if git("rev-parse", "--is-shallow-repository").stdout.strip() == b"true":
                self.skipTest("the pre-bye commit %s is outside this shallow clone's history" % PRE_BYE[:12])
            self.fail("the pre-bye commit %s is not in the checkout's history" % PRE_BYE)
        tar = self.root.parent / "pre_bye.tar"
        done = git("archive", "--format=tar", "-o", str(tar), PRE_BYE, "--", *PRE_BYE_PATHS)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        for rel in PRE_BYE_PATHS:
            path = self.root / rel
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
        done = subprocess.run(["tar", "-xf", str(tar), "-C", str(self.root)], capture_output=True)
        tar.unlink()
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        self.assertLess(self.closed_weeks()[-1], BYE - 1, "PRE_BYE is before the week before the bye closed")

    # ------------------------------------------------------------------ a relabelled week close
    def donors(self, week):
        """(Jacksonville's donor game, the background donor games) for ``week``: the latest closed
        week's Jacksonville game, and the background games of the latest closed week with as many."""
        def background(w):
            return [g for g in self.fixtures(w) if JAX not in (g["away"], g["home"])]
        closed = list(reversed(self.closed_weeks()))
        need = len(background(week))
        ours = next(g for w in closed for g in self.fixtures(w) if JAX in (g["away"], g["home"]))
        others = next((b for b in map(background, closed) if len(b) >= need), None)
        self.assertIsNotNone(others, "no closed week has %d background games" % need)
        return ours, others[:need]

    def pools(self, week):
        """{game: {club: the club's available players at the game}}: each club's in-season rails entry
        for the week's slate (runtime/week_inputs.rails_slate, from the copy's closed games), less the
        players the closed games put out for it, as the week's build reads them."""
        from runtime import week_inputs
        from scripts.render_season_stats import load_receipts
        before = [r for r in load_receipts(self.paths.receipts) if int(r["week"]) < week]
        slate = week_inputs.rails_slate(week, SEASON, before, root=self.root)
        out = {}
        for game in self.fixtures(week):
            out_now = week_inputs.injured_out(before, date.fromisoformat(game["date"]), SEASON)
            key = rails.game_key(game)
            state = slate["states"][slate["cutoffs"][key]]
            out[key] = {}
            for club in (game["away"], game["home"]):
                if club == JAX:
                    continue
                entry = slate["entries"][(key, club)]["players"]
                ready = [p for p in entry if p.get("available") is not False and p["player_id"] not in out_now]
                rest = [p for p in entry if p not in ready]
                rest += state.clubs[slate["data"].codes[club]]["practice_squad"]
                out[key][club] = (ready, rest)
        return out

    def fake_slate(self, week):
        """Close ``week``'s games in the copy from earlier closed games; returns Jacksonville's receipt."""
        paths = self.paths
        games = self.fixtures(week)
        self.assertFalse(list(paths.receipts.glob("week_%02d_*.json" % week)), "the week is already closed")
        ours_donor, others = self.donors(week)
        ours = [g for g in games if JAX in (g["away"], g["home"])]
        pairs = list(zip(others, [g for g in games if JAX not in (g["away"], g["home"])]))
        if ours:
            pairs.insert(0, (ours_donor, ours[0]))
        pools = self.pools(week)
        receipt = None
        for before, after in pairs:
            data = json.loads((paths.receipts / receipt_name(before)).read_text(encoding="utf-8"))
            data = moved(data, before, after, pools[rails.game_key(after)])
            if JAX in (after["away"], after["home"]):
                receipt = data
            (paths.receipts / receipt_name(after)).write_text(json.dumps(data, indent=1), encoding="utf-8")
        return receipt

    def after_game(self, week, receipt):
        """The master date and the roster record to the evening of the game, each new Jacksonville
        injury's medical instruction recorded from the game's record (the close's own format)."""
        game = next(g for g in self.fixtures(week) if JAX in (g["away"], g["home"]))
        played = date.fromisoformat(game["date"])
        self.clock("%s, after the Week %d game" % (week_pages.long_date(played), week))
        roster = self.paths.roster
        data = json.loads(roster.read_text(encoding="utf-8"))
        data["as_of"] = {"date": played.isoformat(), "event": "after the Week %d game" % week}
        season = week_pages.Season(self.root, SEASON)
        closed = next(r for r in season.receipts.values() if int(r["week"]) == week and JAX in (r["away"], r["home"]))
        for injury in (i for i in receipt["injuries"] if i.get("team") == JAX):
            row = next(p for p in data["players"] if p["name"] == injury["player"])
            row["availability"], source = week_pages.availability_entry(season, closed, injury)
            row.setdefault("sources", {})["availability"] = source
        roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return played

    def write_report(self, week, receipt, played):
        """The week's Game Report in the template's layout with its closed event line, its pregame
        record frozen, and Document 5's checkpoint moved to the game (tests/test_week_close_pages.py)."""
        from runtime import decisions, game_report, game_weeks
        report = self.paths.game_report(week)
        self.assertEqual(report.name, GAME_REPORT)
        checkpoint = "Canonical update - %s - Week %d closed" % (week_pages.long_date(played), week)
        event = {"date": played.isoformat(), "id": "%s-week-%d-game" % (played.isoformat(), week),
                 "status": "closed", "summary": "%s in the Week %d game." % (week_pages.score_line(receipt), week),
                 "closure": {"checkpoint": checkpoint, "through": played.isoformat(),
                             "sequence": self.next_sequence()}}
        self.checkpoint(checkpoint)
        game = game_weeks.club_game(self.paths, week, JAX)
        mine = [r for r in game_weeks.regular_receipts(self.paths) if JAX in (r["away"], r["home"])]
        record = sorted(game_report.record_forms(mine, JAX), key=len)[0]
        title, rest = template_report(receipt, game, record, self.root).split("\n", 1)
        shell = "\n".join([title, "", "<!-- event-record: %s -->" % json.dumps(event, sort_keys=True), rest])
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(shell, encoding="utf-8")
        frozen = decisions.week_pages(SEASON, week, self.root).pregame
        frozen.parent.mkdir(parents=True, exist_ok=True)
        frozen.write_text(json.dumps(game_report.pregame_record(shell, played, game, self.root), indent=1) + "\n",
                          encoding="utf-8")
        return report

    def settle_week(self, week, report, played):
        """The week's open game decisions, settled in the copy as his applied Game Plan settles them."""
        path = self.root / "state/decision_queue.json"
        queue = json.loads(path.read_text(encoding="utf-8"))
        for item in queue["items"]:
            if item["status"] == "OPEN" and any(b.get("kind") == "week_inputs" and b.get("week") == week
                                                for b in item.get("blocks", ())):
                item["status"] = "RESOLVED"
                item["resolution"] = {"date": played.isoformat(), "by": "user",
                                      "record": {"path": report.relative_to(self.root).as_posix()},
                                      "summary": "Settled for the synthetic close (test data)."}
        path.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    def draw_awards(self, kind, key):
        """A period's league awards, drawn through the local test service as the close draws them."""
        from scripts import league_awards
        with patch.object(league_awards, "ROOT", self.root), \
                patch("runtime.private_client.Client", return_value=self.client), \
                patch.object(sys, "argv", ["league_awards", kind, str(key), "--season", str(SEASON), "--close"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(league_awards.main(), 0)

    def due_awards(self):
        """Every week and finished month without its awards (the validator's rule), drawn in order."""
        from scripts import league_awards
        with patch.object(league_awards, "ROOT", self.root):
            method, results = league_awards.method(SEASON), league_awards.load_results(SEASON)
        closed = self.closed_weeks()
        for week in closed:
            if "week-%d" % week not in results:
                self.draw_awards("week", week)
        for name, month in method["months"].items():
            if max(month["weeks"]) < closed[-1] and "month-%s" % name not in results:
                self.draw_awards("month", name)

    def close_game_week(self, week):
        """One relabelled week close, the runner's order: the slate, the evening's clock and medical
        instructions, the practice week as the standing instruction set it, the Game Report, the week's
        decisions settled, the awards, the head-coach check, then the page rebuild that opens the next
        period."""
        receipt = self.fake_slate(week)
        played = self.after_game(week, receipt)
        record_practice(self, self.root, week)
        report = self.write_report(week, receipt, played)
        self.settle_week(week, report, played)
        self.due_awards()
        check_head_coaches(self, self.root, week, self.client)
        self.rebuild("Week %d close" % week)
        return receipt

    def close_to_the_bye(self):
        """Every Jacksonville game before the bye, closed in order from the copy's open week."""
        from runtime import league_coaches
        last = self.closed_weeks()[-1]
        if league_coaches.due_weeks(SEASON, self.root, last):
            check_head_coaches(self, self.root, last, self.client)
        for week in range(last + 1, BYE):
            self.close_game_week(week)

    # ------------------------------------------------------------------ the bye's helpers
    def bye(self):
        from scripts import render_bye_week
        return render_bye_week.Bye(self.root, BYE)

    def issues(self):
        from scripts import render_bye_week
        return render_bye_week.issues(self.bye())

    def window(self):
        (start, end), = practices.bye_break_windows(SEASON, BYE, self.root)
        return start, end

    def bye_days(self):
        return bye_week.dates(SEASON, BYE, self.root)

    def midweek(self, day, hour):
        """A mid-week record of the bye at ``hour`` ET on ``day`` (docs/run_week.md, step 4a); the clock
        only moves forward."""
        at = open_events.et(day, hour)
        self.assertGreaterEqual(at, open_events.master_at(self.root), "the clock never moves back")
        self.clock("%s, after the %d %s ET record of the Week %d bye (a test record)" % (
            se.long_date(day), hour % 12 or 12, "a.m." if hour < 12 else "p.m.", BYE))
        return at

    def holds(self, kind):
        from runtime import decision_queue
        return decision_queue.blocking_errors([decision_queue.event(kind, SEASON, BYE)], self.root)

    def bye_item(self):
        from runtime import decision_queue
        return bye_week.bye_item(decision_queue.load(self.root), SEASON, BYE)

    def responses_status(self):
        """The bye index's status of My Responses."""
        row = next(l for l in self.bye().pages.readme.read_text(encoding="utf-8").splitlines()
                   if l.startswith("| [My Responses]"))
        return row.strip("| ").rsplit(" | ", 1)[-1]

    def question_subjects(self):
        """The two test roster questions' subjects: the first and the last Jacksonville player hurt in the
        game before the bye, or, when it hurt none (the injury draw allows it), the first and the last
        active player on the copy's roster record (test data either way, as the event says)."""
        names = [i["player"] for i in self.week_10["injuries"] if i.get("team") == JAX]
        if not names:
            data = json.loads(self.paths.roster.read_text(encoding="utf-8"))
            names = [p["name"] for p in data["players"] if p.get("list") == "active"]
        return names[0], names[-1]

    def roster_question(self, ident, subject, raised):
        """A test injury replacement in the bye (test data: its source is a test page the copy alone
        holds): David Caldwell brings it, Stone's recommendation is asked on the bye's My Responses, and
        Caldwell's criteria are recorded first; due at the next game's kickoff, holding nothing (the
        active roster dresses a legal team)."""
        from scripts import raise_event
        record = se.injury_replacement(self.root, ident, raised, self.bye().after, short=False, subject=subject)
        record["facts"] = [{"label": "Medical communication", "value": "A test roster question while he is out",
                            "source": record["raised"]["source"]}]
        record["summary"]["text"] = "A test roster question after an injury (test data)."
        upload = self.root.parent / ("%s.json" % ident)
        upload.write_text(json.dumps(record, indent=1), encoding="utf-8")
        code, out = quiet(raise_event.main, ["--season", str(SEASON), "--file", str(upload), "--root", str(self.root)])
        upload.unlink()
        self.assertEqual(code, 0, out)
        open_events.add_process(SEASON, record["id"], {
            "at": open_events.iso(raised + timedelta(minutes=5)), "kind": "criteria", "by": "caldwell",
            "what": "A test record of the need at the position, the legal options on the date and the contract "
                    "facts, each on file.", "source": record["raised"]["source"]}, self.root)
        event = open_events.get(SEASON, record["id"], self.root)
        self.assertEqual(event["period"], {"bye": BYE})
        return event

    def answer(self, event, words):
        """Stone's answer in his block on the bye's My Responses (test data), checked and recorded."""
        from runtime import responses
        from scripts import apply_responses, check_responses
        period = {"bye": BYE}
        record = responses.record_of(SEASON, period, self.root)
        heading = next(b["heading"] for b in record["blocks"] if b.get("event") == event["id"])
        page = responses.pages_of(SEASON, period, self.root).responses
        text = page.read_text(encoding="utf-8")
        block = responses.blocks_of(text)[heading]
        filled = block.text.replace("**My answer:**\n", "**My answer:** %s\n" % words, 1)
        filled = filled.replace("**My football or professional reason:**\n",
                                "**My football or professional reason:** He is back before the next game.\n", 1)
        filled = filled.replace("**Conditions or instructions:**\n", "**Conditions or instructions:** None.\n", 1)
        page.write_text(text.replace(block.text, filled, 1), encoding="utf-8")
        for script in (check_responses, apply_responses):
            code, out = quiet(script.main, [str(BYE), "--season", str(SEASON), "--root", str(self.root)])
            self.assertEqual(code, 0, out)
        answered = open_events.get(SEASON, event["id"], self.root)
        self.assertEqual(answered["state"], "answered")
        return answered

    def resolve(self, event, when):
        """Caldwell decides from his criteria: no move, the roster as it stands (its result page built
        from the record, its event line closing; Document 5's checkpoint moved to it)."""
        from scripts import resolve_event
        code, out = quiet(resolve_event.main, [
            event["id"], "--season", str(SEASON), "--outcome", "no_move", "--by", "caldwell",
            "--at", open_events.iso(when), "--decision", "Caldwell keeps the roster as it stands.", "--closure",
            "--root", str(self.root)])
        self.assertEqual(code, 0, out)
        self.checkpoint(events.closures(events.load_events(self.root))[-1][2]["checkpoint"])
        resolved = open_events.get(SEASON, event["id"], self.root)
        self.assertEqual(resolved["resolution"]["period"], {"bye": BYE})
        return resolved

    def adjustments(self, **answers):
        """Stone's My Adjustments in his words: each line of the blank page answered (``answers`` by the
        line's key, runtime/bye_week.sections), in place on the page."""
        from scripts import render_bye_week
        bye = self.bye()
        start, end = self.window()
        latest = render_bye_week.label_of(render_bye_week.issue_of(self.issues()[-1]))
        given = {
            "briefing": latest, "approach": "Carry current approved instructions, with the explicit changes below",
            "keep": "Current system unchanged", "correction": "The run fits against twelve personnel",
            "not_add": "No additional restriction", "ready": "No new evaluation",
            "offense": "No change", "offense_why": "Nothing on the closed games calls for it.",
            "offense_owner": "No new owner", "offense_shown": "No new requirement", "offense_fallback": "Carry current menu",
            "defense": "Correct the run fits against twelve personnel", "defense_why": "It is the first correction.",
            "defense_owner": "No new owner", "defense_check": "No new evaluation", "defense_fallback": "Carry current menu",
            "special_teams": "No change", "st_reason": "None", "st_evaluation": "No new evaluation",
            "roles": "No change", "if_not_cleared": "Bring me a new briefing", "recommendation": "No recommendation",
            "development": "None",
            "days_off": "%s to %s" % (bye_week.long_day(start), bye_week.long_day(end)),
            "staff_work": "Every closed game through the last one, the coordinators",
            "player_work": "No on-field player work during the bye", "test": "No new test", "removed": "None",
            "medical": "Follow every current staff instruction", "durable": "None", "ideas": "No change",
            "retained": "Every standing instruction", "open_issues": "None", "finished": "Yes"}
        given.update(answers)
        labels = {}
        for heading, lines in bye_week.sections(bye.job, bye.master):
            for key, label in lines:
                labels[(heading, label)] = key
        out, heading = [], None
        for line in render_bye_week.adjustments_page(bye).split("\n"):
            if line.startswith("## "):
                heading = line[3:]
            m = re.match(r"^\*\*([^*]+):\*\*\s*$", line.rstrip())
            if m:
                key = labels.get((heading, m[1])) or {label: k for k, label in bye_week.HEADER}.get(m[1])
                if key in given:
                    line = "**%s:** %s%s" % (m[1], given[key], "  " if line.endswith("  ") else "")
            out.append(line)
        bye.pages.adjustments.write_text("\n".join(out), encoding="utf-8")

    def check_adjustments(self):
        from scripts import check_bye_adjustments
        return check_bye_adjustments.check(self.root, SEASON, BYE)

    def slate_close(self):
        """scripts/build_week_inputs.py and scripts/close_week.py --close for the bye week, run in the copy
        as the runner runs them, against a local test service bound to the copy's Document 5 (no engine
        variable of the real runtime is read). The one gate the copy passes by is the in-season rails
        coverage of the build and the close (the other clubs' real moves through the slate's cutoff, a
        separate data commit researched in two passes when the clock reaches it); every other gate runs
        as written, the readiness check (repository validation of the copy among it) included."""
        import os
        import subprocess
        snapshot = digest(self.root / se.STATE)
        _, client = local_service(self, self.root / "private_slate", "step5-rehearsal-r5-slate", snapshot=snapshot)
        # The league year's player states bound in the test store, and the copy's binding record written
        # from its reply, as scripts/bind_latent_season.py binds the deployed service once and records it
        # (the test store's commitment, under its own pinned seed, is not the deployed one's).
        from runtime import player_state
        from scripts import bind_latent_season
        reply = client.bind_latent(SEASON, player_state.manifest_sha256())
        player_state.binding_path(SEASON, self.root).write_text(
            json.dumps(bind_latent_season.binding_record(reply), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in ("ENGINE_RUNTIME_URL", "ENGINE_API_TOKEN")}
        env.update({"ENGINE_RUNTIME_URL": client.url, "ENGINE_API_TOKEN": TOKEN})
        out = {}
        for script in ("build_week_inputs", "close_week"):
            code = SLATE % {"script": script, "week": BYE, "season": SEASON, "rails": RAILS_GATE,
                            "close": ", '--close'" if script == "close_week" else ""}
            done = subprocess.run([sys.executable, "-c", code], cwd=self.root, env=env, capture_output=True,
                                  text=True, timeout=3600)
            out[script] = done.stdout + done.stderr
            self.assertEqual(done.returncode, 0, out[script][-4000:])
        return out

    # ------------------------------------------------------------------ the bye, in the runner's order
    def bye_opens(self):
        """At Week 10's close: the bye is the open period, its review issued from stored facts and its
        one item open; the next game's briefing and items wait; nothing holds the week's slate."""
        from runtime import decision_queue
        from scripts import open_game_week, render_bye_week, render_game_week
        self.assertEqual(bye_week.active_bye(self.paths, self.root), BYE)
        bye = self.bye()
        self.assertEqual([(e["file"], e["reason"]) for e in self.issues()], [(bye.pages.review.name, None)])
        self.assertEqual(bye.pages.adjustments.read_text(encoding="utf-8"), render_bye_week.adjustments_page(bye))
        wk = render_game_week.Week(self.root)
        self.assertEqual((wk.game, wk.period), (None, {"bye": BYE}))
        after = render_game_week.decisions.week_pages(SEASON, int(bye.after["week"]), self.root)
        self.assertFalse(after.briefing.exists(), "the next game's briefing waits for the bye's close")
        self.assertEqual(open_game_week.missing(self.root)[0], [])
        mine = [i for i in decision_queue.load(self.root)["items"]
                if any(b.get("week") in (BYE, int(bye.after["week"])) for b in i.get("blocks") or ())]
        self.assertEqual([(i["class"], i["status"], i["blocks"], i["deadline"]) for i in mine],
                         [("bye_adjustments", "OPEN", [decision_queue.event("bye_close", SEASON, BYE)], None)])
        self.assertEqual(self.holds("week_inputs"), [])
        self.assertEqual(self.holds("week_close"), [])
        self.assertTrue(any(mine[0]["id"] in line for line in self.holds("bye_close")))
        review = bye.pages.review.read_text(encoding="utf-8")
        self.assertIn("| Current record, division position | %s." % bye_week.record_words(SEASON, BYE, self.root),
                      review)
        start, end = self.window()
        self.assertIn("%s to %s is the only window" % (bye_week.long_day(start), bye_week.long_day(end)), review)
        # The standing instruction's pads (the Wednesdays of Weeks 7 and 9) used the last of the eleven.
        self.assertEqual(practices.padded_status(SEASON, BYE - 1, self.root)["first"]["left"], 0)
        self.assertIn("all 11 of the first eleven weeks are used; no padded practice in the bye", review)
        self.assertNotIn("## ACTION REQUIRED", review)
        # The desk lists his one answer of the bye, with the page he answers it on.
        desk = (self.paths.career / "README.md").read_text(encoding="utf-8")
        waiting = desk.split("## Waiting on you", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Week %d bye adjustments" % BYE, waiting)
        self.assertIn("[My Adjustments](", waiting)
        self.record_before = bye_week.record_words(SEASON, BYE, self.root)
        self.week_10 = json.loads((self.paths.receipts / receipt_name(bye.before)).read_text(encoding="utf-8"))

    def bye_monday(self):
        """Monday: a test roster question raised for Stone's recommendation issues the review again for
        its answer (rule a), the earlier copy kept and the bye's My Responses opened; he answers;
        Caldwell decides it from his criteria (one result page, on the bye's index). Stone's first drafts
        of My Adjustments are checked: required film inside the break and pads with none left are each
        refused in the design's words; nothing is applied."""
        from scripts import render_bye_week
        monday, _ = self.bye_days()
        subject, _ = self.question_subjects()
        self.midweek(monday, 9)
        first = self.bye().pages.review.read_bytes()
        self.first_question = self.roster_question("test-roster-question-first", subject,
                                                   open_events.et(monday, 8, 30))
        self.assertTrue(render_bye_week.reissue_reason(self.bye()).startswith("a:"))
        self.rebuild("Monday's roster question")
        entries = self.issues()
        self.assertEqual([e["reason"][:2] if e["reason"] else None for e in entries], [None, "a:"])
        self.assertEqual((self.bye().pages.folder / entries[0]["file"]).read_bytes(), first)
        review = self.bye().pages.review.read_text(encoding="utf-8")
        self.assertIn("## ACTION REQUIRED", review)
        self.assertIn(open_events.title(self.first_question), review)
        self.assertNotIn(self.first_question["id"], review)
        self.assertTrue(self.bye().pages.responses.is_file())
        self.assertEqual(self.responses_status(), "Waiting on you")
        self.assertEqual(self.holds("week_close"), [])
        # His answer, then Caldwell's decision: news for the next issue, not a reissue of this one.
        self.midweek(monday, 11)
        self.answer(self.first_question, "I support keeping the roster as it stands.")
        self.first_question = self.resolve(self.first_question, open_events.et(monday, 11))
        self.assertIsNone(render_bye_week.reissue_reason(self.bye()))
        page = self.root / self.first_question["resolution"]["result_page"]
        self.assertTrue(page.is_file())
        self.rebuild("Monday's decision")
        self.assertIn(page.name, self.bye().pages.readme.read_text(encoding="utf-8"))
        self.assertEqual(self.responses_status(), "No answer waiting")
        # His first drafts, checked: refused, so nothing is applied.
        start, end = self.window()
        saturday = end - timedelta(days=1)
        self.adjustments(player_work="%s: film" % saturday.strftime("%A"))
        self.assertIn("You scheduled required player film work on %s, inside the four-day player break. Move it "
                      "before the break or make it staff-only." % practices.long_day(saturday),
                      self.check_adjustments()[0])
        tuesday = monday + timedelta(days=1)
        self.adjustments(player_work="%s: practice in helmets and shoulder pads" % tuesday.strftime("%A"))
        self.assertIn("This practice requests pads but the earlier recorded practices have used the season's "
                      "available first-eleven-week allocation. Choose helmets-only work or no field period.",
                      self.check_adjustments()[0])
        self.assertEqual(self.bye_item()["status"], "OPEN")
        self.assert_pages("the Monday of the bye")

    def bye_tuesday(self):
        """Tuesday: the staff's stored assessment changes the review's own sections while the bye's
        decisions are open; the review is issued again (rule b), Monday's result under FOR YOUR
        INFORMATION there and nowhere else."""
        from scripts import render_bye_week
        monday, _ = self.bye_days()
        tuesday = monday + timedelta(days=1)
        self.midweek(tuesday, 9)
        staff = self.bye().pages.staff_review
        staff.write_text(json.dumps({"texts": {"assessment": [{
            "author": "The coaching staff", "date": tuesday.isoformat(),
            "text": "A test assessment standing in for the staff's own; it records no film finding."}]}},
            indent=1) + "\n", encoding="utf-8")
        self.assertTrue(render_bye_week.reissue_reason(self.bye()).startswith("b:"))
        self.rebuild("Tuesday's staff assessment")
        entries = self.issues()
        self.assertEqual(len(entries), 3)
        self.assertEqual([i.get("event") for i in entries[-1]["inserts"] if i["section"] == "fyi"],
                         [self.first_question["id"]])
        review = self.bye().pages.review.read_text(encoding="utf-8")
        self.assertIn("## FOR YOUR INFORMATION", review)
        self.assertNotIn("## ACTION REQUIRED", review)
        self.assertIn("A test assessment standing in for the staff's own", review)
        self.assertIsNone(render_bye_week.reissue_reason(self.bye()))
        self.assert_pages("the Tuesday of the bye")

    def bye_thursday_slate(self):
        """Thursday, the slate's first game day: with Stone's bye item still open, the week's inputs
        build and its games close through the game path's own scripts (no Jacksonville input, receipt,
        score or box score); the week's awards and head-coach check follow; the bye cannot close."""
        from scripts import close_bye_week, render_bye_week
        games = [g for g in self.paths.regular_games() if int(g["week"]) == BYE]
        first = min(date.fromisoformat(g["date"]) for g in games)
        self.midweek(first, 9)
        self.rebuild("Thursday's record")
        self.assertEqual(self.bye_item()["status"], "OPEN")
        self.assertEqual(self.holds("week_inputs"), [])
        self.assertEqual(self.holds("week_close"), [])
        out = self.slate_close()
        self.assertIn("WEEK_INPUTS: READY  week %d, %d games" % (BYE, len(games)), out["build_week_inputs"])
        self.assertIn("Week %d closed: %d receipts written" % (BYE, len(games)), out["close_week"])
        package = json.loads(self.paths.cache(BYE, "inputs").read_text(encoding="utf-8"))
        self.assertFalse([g for g in package["games"] if JAX in (g["away"], g["home"])])
        receipts = sorted(self.paths.receipts.glob("week_%02d_*.json" % BYE))
        self.assertEqual(len(receipts), len(games))
        self.assertFalse([p for p in receipts if JAX in json.loads(p.read_text(encoding="utf-8"))["matchup"]])
        self.assertEqual(self.bye_item()["status"], "OPEN", "the slate closed with his bye answers open")
        refused = close_bye_week.refusals(self.root, SEASON, BYE)
        self.assertTrue(any("bye adjustments are not applied" in r for r in refused), refused)
        self.assertTrue(any("closes on its Sunday" in r for r in refused), refused)
        self.due_awards()
        check_head_coaches(self, self.root, BYE, self.client)
        self.rebuild("the Week %d slate closed" % BYE)
        self.assertIsNone(render_bye_week.reissue_reason(self.bye()), "a game elsewhere never reissues the review")
        self.assertEqual(bye_week.record_words(SEASON, BYE, self.root), self.record_before)
        self.assert_pages("the Week %d slate closed with the bye open" % BYE)

    def bye_thursday_apply(self):
        """Thursday, later: his final My Adjustments (no change on offense and special teams, a correction
        on defense, the break and the work of section 6) is checked and applied; the item is his,
        settled, and nothing holds the bye's close any more."""
        from runtime import decision_queue
        from scripts import apply_bye_adjustments
        games = [g for g in self.paths.regular_games() if int(g["week"]) == BYE]
        first = min(date.fromisoformat(g["date"]) for g in games)
        self.midweek(first, 11)
        self.adjustments()
        problems, notes, compiled = self.check_adjustments()
        self.assertEqual(problems, [])
        self.assertTrue(compiled["areas"]["offense"]["no_change"])
        self.assertTrue(compiled["areas"]["special_teams"]["no_change"])
        self.assertEqual([p["kind"] for p in compiled["areas"]["defense"]["parts"]], ["correct"])
        start, end = self.window()
        self.assertEqual([d["date"] for d in compiled["schedule"]["days_off"]],
                         [(start + timedelta(days=n)).isoformat() for n in range((end - start).days + 1)])
        self.assertEqual(compiled["schedule"]["sessions"], [])
        problems, notes, written = apply_bye_adjustments.apply(self.root, SEASON, BYE)
        self.assertEqual(problems, [])
        applied = bye_week.applied_record(SEASON, BYE, self.root)
        self.assertEqual(applied["date"], first.isoformat())
        item = self.bye_item()
        self.assertEqual((item["status"], item["resolution"]["by"]), ("RESOLVED", "user"))
        self.assertEqual(self.holds("bye_close"), [])
        self.assertEqual(apply_bye_adjustments.apply(self.root, SEASON, BYE)[2], [], "applied once")
        self.rebuild("My Adjustments applied")
        self.assert_pages("My Adjustments applied")

    def bye_friday(self):
        """Friday: a second test roster question issues the review a last time, for its answer (rule a);
        he answers and Caldwell decides it the same morning, after that last issue, so it is news for the
        next game week's first brief."""
        from scripts import render_bye_week
        games = [g for g in self.paths.regular_games() if int(g["week"]) == BYE]
        friday = min(date.fromisoformat(g["date"]) for g in games) + timedelta(days=1)
        _, subject = self.question_subjects()
        self.midweek(friday, 9)
        self.second_question = self.roster_question("test-roster-question-second", subject,
                                                    open_events.et(friday, 8, 30))
        self.assertTrue(render_bye_week.reissue_reason(self.bye()).startswith("a:"))
        self.rebuild("Friday's roster question")
        self.assertEqual(len(self.issues()), 4)
        self.assertEqual(self.responses_status(), "Waiting on you")
        self.midweek(friday, 11)
        self.answer(self.second_question, "I support keeping the roster as it stands.")
        self.second_question = self.resolve(self.second_question, open_events.et(friday, 11))
        self.assertIsNone(render_bye_week.reissue_reason(self.bye()))
        self.rebuild("Friday's decision")
        index = self.bye().pages.readme.read_text(encoding="utf-8")
        for question in (self.first_question, self.second_question):
            self.assertIn(Path(question["resolution"]["result_page"]).name, index)
        self.assertEqual(self.responses_status(), "No answer waiting")
        self.assert_pages("the Friday of the bye")

    def bye_sunday_close(self):
        """Sunday: the bye's practice and rest record (the legal four-day break, no required player work);
        the staff's Bye Week Report, held to the records; the bye's close, Document 5's checkpoint and
        master date moved to it, and the page rebuild that opens the next game week."""
        import os
        from scripts import close_bye_week, record_practice_week, render_bye_week
        _, sunday = self.bye_days()
        self.clock("%s, after the Week %d bye closed" % (se.long_date(sunday), BYE))
        bye = self.bye()
        schedule, why = record_practice_week.applied_schedule(self.root, SEASON, BYE)
        self.assertIsNotNone(schedule, why)
        held = self.root.parent / "held_bye.json"
        held.write_text(json.dumps({"source": {"page": bye.rel(bye.pages.readme)},
                                    "sessions": [dict(s, participation_recorded=False) for s in schedule["sessions"]],
                                    "days_off": schedule["days_off"],
                                    "gaps": ["Participation was not recorded session by session"]}), encoding="utf-8")
        problems, _, path = record_practice_week.record(self.root, SEASON, BYE, held)
        held.unlink()
        self.assertEqual(problems, [])
        log = practices.load(SEASON, BYE, self.root)
        self.assertEqual((log["kind"], log["basis"], log["sessions"]), ("bye", "recorded", []))
        start, end = self.window()
        self.assertEqual([d["date"] for d in log["days_off"]],
                         [(start + timedelta(days=n)).isoformat() for n in range((end - start).days + 1)])
        refused = close_bye_week.refusals(self.root, SEASON, BYE)
        self.assertTrue(any("the report is not written" in r for r in refused), refused)
        # The staff's report, after the work: the frame's fixed parts, its own parts written (test text).
        frame = render_bye_week.report_frame(self.bye())
        links = ", ".join("[%s](%s)" % (open_events.title(q), os.path.relpath(
            self.root / q["resolution"]["result_page"], bye.pages.folder).replace(os.sep, "/"))
            for q in (self.first_question, self.second_question))
        report = frame.replace("| To come. | To come. |", "| Adopted as applied | The next game week's film |")
        report = report.replace("## 5. League context and the next opponent\n\nTo come.",
                                "## 5. League context and the next opponent\n\n**Jacksonville:** No game this week; "
                                "record unchanged. The other business of the bye: %s." % links)
        report = report.replace("To come.", "A test entry standing in for the staff's own (test data).")
        bye.pages.report.write_text(report, encoding="utf-8")
        self.assertEqual(bye_week.report_errors(SEASON, BYE, self.root), [])
        for bad, words in ((report + "\n## Box score\n", "no box score"),
                           (report.replace("%s through" % self.record_before, "9-1 through"), "the record line"),
                           (report.replace(links, "the roster questions"), "not linked")):
            with self.subTest(words=words):
                bye.pages.report.write_text(bad, encoding="utf-8")
                self.assertTrue(any(words in e for e in bye_week.report_errors(SEASON, BYE, self.root)),
                                bye_week.report_errors(SEASON, BYE, self.root))
        bye.pages.report.write_text(report, encoding="utf-8")
        self.assertEqual(close_bye_week.refusals(self.root, SEASON, BYE), [])
        problems, written = close_bye_week.close(self.root, SEASON, BYE)
        self.assertEqual(problems, [])
        self.checkpoint(events.closures(events.load_events(self.root))[-1][2]["checkpoint"])
        self.assertTrue(bye_week.bye_closed(self.paths, self.root, BYE))
        self.assertIsNone(bye_week.active_bye(self.paths, self.root))
        self.assertIn("Week %d bye" % BYE, events.annual_record_path(self.root, SEASON).read_text(encoding="utf-8"))
        self.assertTrue(close_bye_week.refusals(self.root, SEASON, BYE)[0].startswith("The Week %d bye has closed" % BYE))
        self.rebuild("the bye closed")

    def week_12_opens(self):
        """After the bye: the club's record as it entered the bye, no Jacksonville game in the bye week,
        and the next game week open: its items and its first brief, whose notices count from the bye's
        last review (the Friday result there, the Monday result not), its index naming neither."""
        from runtime import decision_queue
        from scripts import open_game_week, render_game_week
        self.assertEqual(bye_week.record_words(SEASON, BYE, self.root), self.record_before)
        self.assertFalse([p for p in self.paths.receipts.glob("week_%02d_*.json" % BYE)
                          if JAX in json.loads(p.read_text(encoding="utf-8"))["matchup"]])
        after = int(self.bye().after["week"])
        wk = render_game_week.Week(self.root)
        self.assertEqual(int(wk.game["week"]), after)
        self.assertEqual(open_game_week.missing(self.root)[0], [])
        opened = [i["class"] for i in decision_queue.load(self.root)["items"] if i["status"] == "OPEN"
                  and any(b.get("week") == after for b in i.get("blocks") or ())]
        self.assertEqual(sorted(opened), sorted([open_game_week.PLAN, open_game_week.INACTIVES]))
        pages = render_game_week.decisions.week_pages(SEASON, after, self.root)
        self.assertTrue(pages.briefing.is_file() and pages.plan.is_file())
        first = render_game_week.issues(wk)[0]
        self.assertEqual([i.get("event") for i in first["inserts"] if i["section"] == "fyi"],
                         [self.second_question["id"]])
        brief = pages.briefing.read_text(encoding="utf-8")
        self.assertIn("## FOR YOUR INFORMATION", brief)
        self.assertIn("Jacksonville %s" % self.record_before, brief)
        index = pages.readme.read_text(encoding="utf-8")
        for question in (self.first_question, self.second_question):
            self.assertNotIn(Path(question["resolution"]["result_page"]).name, index)
        self.assertIn(Path(self.second_question["resolution"]["result_page"]).name, brief)
        self.assertNotIn(Path(self.first_question["resolution"]["result_page"]).name, brief)
        self.assert_pages("Week %d open after the bye" % after)
        # The game readiness gates hold in the copy too (the private probe aside: a copy is never bound to
        # the deployed snapshot; repository validation as the real checkout's).
        from check_game_readiness import assess
        blockers = ["%s: %s" % (b["label"], b["detail"]) for b in assess(self.root, SEASON)["blockers"]
                    if b["id"] != "private_probe" and not (b["id"] == "repository_continuity"
                                                           and b["detail"] in type(self).baseline)]
        self.assertEqual(blockers, [])


class ByeCloseRehearsal(Rehearsal, unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        if self.closed_weeks()[-1] >= BYE - 1:
            self.pre_bye()
        self.history = clean_pages.history(self.root)
        _, self.client = local_service(self, self.root / "private", "step5-rehearsal-r5", snapshot="rehearsal-r5")
        from runtime import week_inputs
        memo = patch.object(week_inputs, "rails_slate", SlateMemo(week_inputs.rails_slate))
        memo.start()
        self.addCleanup(memo.stop)

    def test_the_bye_closes_after_a_relabelled_week_10(self):
        watched = (se.STATE, "state/decision_queue.json", "state/current_job.json")
        real = {p: digest(ROOT / p) for p in watched}
        receipts = sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json"))
        self.close_to_the_bye()
        self.bye_opens()
        self.assert_pages("Week %d closed: the bye open" % (BYE - 1))
        self.bye_monday()
        self.bye_tuesday()
        self.bye_thursday_slate()
        self.bye_thursday_apply()
        self.bye_friday()
        self.bye_sunday_close()
        self.week_12_opens()
        # Nothing reached the real repository.
        self.assertEqual({p: digest(ROOT / p) for p in watched}, real)
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), receipts)


if __name__ == "__main__":
    unittest.main()
