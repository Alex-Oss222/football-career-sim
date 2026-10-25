"""A synthetic Week 6 close in a temporary copy (rebuild step 4).

The whole result side of a game week's close, the way the weekly workflow
runs it: the week's games close, the Game Report is written in the Game
Report template's layout with its generated box score, the week's awards are
drawn, and then one command, scripts/rebuild_pages.py, names the report's box
score and fills it last, and rebuilds every built
page in order (the standings, the statistics, the team tracker, the award
pages, the player, club and coach pages, the cap views, the game-week pages,
the Games and league-results pages, the injury report, the medical history's
game entry and the incident records, the in-season roster moves page, the
desk and the calendar, and the annual record). Every page must then pass the
clean-page check and repository validation of the copy must add no error to
the real checkout's; no rewritten page is re-recorded as history.

The fake result: the copy's open game week (Jacksonville's first game not
yet closed, while it is the open period; while the bye is open, once the open
game is a playoff game and once no game is left there is no game week to close
here and the test says so) is closed by relabelling closed games onto that
week's fixtures, game for game: Jacksonville's last closed game onto
Jacksonville's, the other fixtures from the latest closed week with as many
other games: the same scores and statistics, now in the new week. Jacksonville's
injuries, each a player on the active roster (a game that logged fewer gets
test injuries to active players who played in it), are recorded as a
multi-week and a long-term injury, the severities whose names the game records
with an underscore. The master date and the roster record move to the new game
day, as the week's close moves them, with each newly injured player's medical
instruction; the week's awards are drawn with each month's whose weeks have all
closed before it. The rebuild then opens the next period: the next game week's
briefing and Game Plan, or the bye's review and My Adjustments with the next
game's briefing waiting for the bye's close, or nothing once the season's last
game has closed. No game is played and the real repository is never touched.
"""
import contextlib
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import bye_week, clean_pages, events, game_weeks, open_events, postseason, week_pages  # noqa: E402
from runtime.seasons import GAME_REPORT, GAME_REPORT_FROM, SeasonPaths  # noqa: E402
from runtime.statbook import INJURY_FIELDS, INJURY_ONSET_FIELDS  # noqa: E402
from runtime.week_inputs import event_id, receipt_name  # noqa: E402
from scripts import league_awards, rebuild_pages, render_box_score, render_week_pages  # noqa: E402
from scripts.validate_repository import validate  # noqa: E402
from local_private_service import local_service  # noqa: E402
from test_game_report import template_report  # noqa: E402

JAX = "Jacksonville Jaguars"
SEASON, FIRST_REPORT_WEEK = GAME_REPORT_FROM


def open_report_week(root=ROOT):
    """(week, why not): the week this test closes in its copy, Jacksonville's open game week in the real
    checkout (the open period, runtime/open_events.open_period), a regular-season Game Report week; or
    None and the reason there is none: the bye is the open period (the next game week opens at its close,
    tests/test_step5_rehearsal_r5.py), the open game is a playoff game (tests/test_postseason_game_week.py)
    or no Jacksonville game is left."""
    period = open_events.open_period(SEASON, root)
    if period is None:
        return None, "no Jacksonville game is left to close"
    if "bye" in period:
        return None, "the Week %d bye is the open period; the next game week opens at its close" % period["bye"]
    week = int(period["week"])
    if game_weeks.is_postseason(SeasonPaths(SEASON, root), week) or week < FIRST_REPORT_WEEK:
        return None, "Jacksonville's open game (Week %d) is not a regular-season Game Report week" % week
    return week, None


IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
# The receipt fields tied to the week a game was played under: the defensive call record names that
# week's committed sheet, and the decision policies its standing rules.
WEEK_BOUND = ("defensive_calls", "defensive_call_stats", "decision_policies")
# Jacksonville's fake injuries, in the game's own severity names, with days to return.
SEVERITIES = (("multi_week", 24), ("long_term", 70))
# The positions a test injury is never given to: the quarterbacks and the kicking specialists.
SPECIALISTS = ("QB", "K", "P", "LS")
# A test injury's lines when the game logged none to copy them from: the game's form, its onset the
# first drive's end.
INJURY = {"team": JAX, "injury_class": "lower_extremity", "severity": "minor", "restriction": "out",
          "return_days": 1, "reassessment_days": 1, "onset": "end_of_drive", "drive": 1, "period": 1,
          "clock": "10:00", "removed": True}
# The number the head-coach check draws in the rehearsal: above every chance in the rate table.
NO_CHANGE = 0.999999


def relabel(value, names):
    """``value`` with every string equal to a key of ``names`` (a club) replaced, at any depth."""
    if isinstance(value, dict):
        return {relabel(k, names): relabel(v, names) for k, v in value.items()}
    if isinstance(value, list):
        return [relabel(v, names) for v in value]
    if isinstance(value, str):
        return names.get(value, value)
    return value


def ours_first(games):
    return sorted(games, key=lambda g: (JAX not in (g["away"], g["home"]), g["away"]))


def active_injuries(receipt, data):
    """``receipt``'s Jacksonville injuries kept for players still on the active roster (the roster record
    ``data``; one placed on reserve or gone since the game is dropped), then test injuries in the
    receipt's own form until there are ``len(SEVERITIES)``: each copied from an injury the game logged
    (the lines the game records: its class, restriction and when), given to an active player who played
    in it, in the roster record's order, a specialist never. Returns Jacksonville's injuries."""
    active = [p for p in data["players"] if p.get("list") == "active"]
    names = {p["name"] for p in active}
    others = [i for i in receipt["injuries"] if i.get("team") != JAX]
    ours = [i for i in receipt["injuries"] if i.get("team") == JAX and i["player"] in names]
    template = dict(INJURY, **next(iter(ours + others), {}))
    played = receipt["team_stats"][JAX]["players"]
    spare = [p["name"] for p in active if p["name"] in played and p["position"] not in SPECIALISTS
             and p["name"] not in {i["player"] for i in ours}
             and any(v for k, v in played[p["name"]].items() if k.endswith("_snaps"))]
    for name in spare[:max(0, len(SEVERITIES) - len(ours))]:
        ours.append({k: v for k, v in dict(template, team=JAX, player=name).items()
                     if k in INJURY_FIELDS + INJURY_ONSET_FIELDS})
    receipt["injuries"] = others + ours
    return ours


def answer_practice_week(test, root, week):
    """Stone's "Practice week" answer on the week's My Responses page, where the week's opening asks a
    week the standing practice instruction does not set (a Thursday game's): test data, given before the
    practice week. One line a day from the Tuesday of a Sunday game's week (otherwise the week's first
    day) to the day before the game, helmets only so no padded practice is spent, the Tuesday before a
    Sunday game the players' day off and the day before the game a walkthrough
    (tests/test_step5_rehearsal_r3.py's answer); read, checked and frozen by
    scripts/record_practice_week.py with the master date the evening before the week (or the day the
    week asked it), then the clock put back as it was."""
    from runtime import decisions, practices
    from scripts import record_practice_week as rpw
    game = next(g for g in open_events.club_fixtures(SEASON, root) if int(g["week"]) == week)
    day = date.fromisoformat(game["date"])
    first, _ = practices.week_span(SEASON, week, root)
    start = max(first, day - timedelta(days=5)) if day.weekday() == 6 else first
    lines = []
    for n in range((day - start).days):
        on = start + timedelta(days=n)
        work = ("walkthrough in helmets" if on == day - timedelta(days=1) else
                "day off" if day.weekday() == 6 and on.weekday() == 1 else "practice in helmets")
        lines.append("%s, %s %d: %s" % (on.strftime("%A"), on.strftime("%B"), on.day, work))
    page = decisions.week_pages(SEASON, week, root).responses
    block = rpw.read_block(root, SEASON, {"week": week}, decisions.PRACTICE_WEEK)
    test.assertIsNotNone(block, "the Week %d practice week is not asked on My Responses" % week)
    if not block.answer:
        page.write_text(page.read_text(encoding="utf-8").replace(block.text, block.text.replace(
            "**My answer:**\n", "**My answer:** %s\n" % "; ".join(lines), 1), 1), encoding="utf-8")
    raised = date.fromisoformat(rpw.practice_item(root, SEASON, week)["raised"]["date"])
    eve = max(first - timedelta(days=1), raised)
    state = root / "state/05_Current_Season_State.md"
    clock = state.read_bytes()
    state.write_text(re.sub(r"^\| Master date/time \| .+? \|\s*$", "| Master date/time | %s, after the 11:59 p.m. ET "
                            "record of the Week %d preparation (a test record) |" % (week_pages.long_date(eve), week),
                            clock.decode("utf-8"), count=1, flags=re.M), encoding="utf-8")
    try:
        status, problems, _, _ = rpw.answer(root, SEASON, week)
    finally:
        state.write_bytes(clock)
    test.assertEqual((status, problems), ("SET", []))


def record_practice(test, root, week):
    """The week's practice and rest record, as the practice-week commit writes it once the master date
    is at game day (docs/run_week.md, step 5): the schedule Stone's standing practice instruction sets
    for the week (a week it does not set, his answer on My Responses, answer_practice_week), held as
    set, its participation not recorded session by session (test data only)."""
    from runtime import decisions, practices
    from scripts import record_practice_week
    schedule, why = record_practice_week.applied_schedule(root, SEASON, week)
    if schedule is None and record_practice_week.practice_item(root, SEASON, week) is not None:
        answer_practice_week(test, root, week)
        schedule, why = record_practice_week.applied_schedule(root, SEASON, week)
    test.assertIsNotNone(schedule, why)
    page = decisions.week_pages(SEASON, week, root).briefing
    held = {"source": {"page": page.relative_to(root).as_posix()},
            "sessions": [dict(s, participation_recorded=False) for s in schedule["sessions"]],
            "days_off": schedule["days_off"]}
    record = record_practice_week.held_record(SEASON, week, held, schedule, root)
    test.assertEqual(practices.record_errors(record, root, schedule=schedule), [])
    practices.write(record, root)


def check_head_coaches(test, root, week, client):
    """The weekly head-coach check, as the close runs it after the week's slate closes and before the
    rebuild that opens the next week (docs/run_week.md, step 8): every week still due through
    ``week``, the retroactive Weeks 1 to 5 first, each drawn through the local test service. Test data:
    the close's random stream is replaced by a number no chance in the table reaches, so no change is
    drawn and the pages never depend on the draw. The copy's method and rate table stay as recorded:
    the season's checks already drawn are verified against them at every close, so a zeroed table in
    the copy would refuse them (runtime/league_coaches.record_errors). A week whose every game is a
    club's last (Week 17) is the season-end draw's: nothing is due for it, and the close draws only the
    weeks still due before it."""
    from runtime import league_coaches
    from scripts import coaching_check

    class NoChange:
        def random(self):
            return NO_CHANGE

    method = league_coaches.load_method(SEASON, root)
    table = league_coaches.load_table(method, root)
    test.assertLess(max(row["rate"] for row in table["rates"].values()), NO_CHANGE)
    due = league_coaches.due_weeks(SEASON, root, week)
    drawn = set(league_coaches.checks(SEASON, root))
    test.assertEqual(week in due, week in league_coaches.at_risk_weeks(SEASON, root, method))
    with patch.object(coaching_check, "stream", lambda ref, pkt: NoChange()):
        test.assertEqual(coaching_check.close(SEASON, week, root, client, lambda *_: None), 0)
    test.assertEqual(set(league_coaches.checks(SEASON, root)), drawn | set(due))
    test.assertEqual(league_coaches.due_weeks(SEASON, root, week), [])
    test.assertEqual(league_coaches.coverage_errors(root, SEASON), [])


class WeekClosePagesTests(unittest.TestCase):
    def setUp(self):
        self.week, why = open_report_week()
        if self.week is None:
            self.skipTest(why)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        self.paths = SeasonPaths(SEASON, self.root)
        self.real = sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json"))

    def fake_week(self):
        """Close the week in the copy from closed games, game for game: Jacksonville's last closed game
        onto Jacksonville's (a bye between them changes nothing), the other fixtures from the latest
        closed week with as many other games, each moved once; returns Jacksonville's receipt."""
        paths, week = self.paths, self.week
        fixtures = paths.regular_games()
        new = ours_first(g for g in fixtures if g["week"] == week)
        self.assertIn(JAX, (new[0]["away"], new[0]["home"]))
        closed = [g for g in fixtures if (paths.receipts / receipt_name(g)).is_file()]
        mine = max((g for g in closed if JAX in (g["away"], g["home"])), key=lambda g: g["week"])
        others = {}
        for g in closed:
            if JAX not in (g["away"], g["home"]):
                others.setdefault(g["week"], []).append(g)
        donor = next(w for w in sorted(others, reverse=True) if len(others[w]) >= len(new) - 1)
        old = [mine] + ours_first(others[donor])[:len(new) - 1]
        self.assertEqual(len(new), len(old))
        self.assertFalse(list(paths.receipts.glob("week_%02d_*.json" % week)), "the week is already closed")
        data = json.loads(paths.roster.read_text(encoding="utf-8"))
        ours = None
        for before, after in zip(old, new):
            receipt = json.loads((paths.receipts / receipt_name(before)).read_text(encoding="utf-8"))
            # The previous week's away club becomes the new away club, its home club the new home club.
            names = {before["away"]: after["away"], before["home"]: after["home"]}
            if JAX in (before["away"], before["home"]):  # Jacksonville stays Jacksonville
                other = before["home"] if before["away"] == JAX else before["away"]
                names = {other: after["home"] if after["away"] == JAX else after["away"]}
            receipt = relabel(receipt, names)
            for key in WEEK_BOUND:
                receipt.pop(key, None)
            receipt.update({"week": week, "away": after["away"], "home": after["home"],
                            "matchup": "%s at %s" % (after["away"], after["home"]),
                            "event_id": event_id(after, season=SEASON)})
            if JAX in (after["away"], after["home"]):
                # Swapping the sides: the score and statistics stay with their clubs.
                ours = receipt
                injured = active_injuries(receipt, data)
                self.assertGreaterEqual(len(injured), len(SEVERITIES))
                for injury, (severity, days) in zip(injured, SEVERITIES):
                    injury.update({"severity": severity, "return_days": days, "reassessment_days": 6})
            (paths.receipts / receipt_name(after)).write_text(json.dumps(receipt, indent=1), encoding="utf-8")
        return ours

    def move_clock(self, receipt):
        """The master date and the roster record to the game day, each new injury's instruction on it."""
        week = self.week
        played = date.fromisoformat(next(g for g in self.paths.regular_games()
                                         if g["week"] == week and JAX in (g["away"], g["home"]))["date"])
        state = self.root / "state/05_Current_Season_State.md"
        text = state.read_text(encoding="utf-8")
        text, n = re.subn(r"(\| Master date/time \| )[A-Za-z]+ \d{1,2}, \d{4}[^|]*\|",
                          r"\g<1>%s, after the Week %d game |" % (week_pages.long_date(played), week), text, count=1)
        self.assertEqual(n, 1)
        state.write_text(text, encoding="utf-8")
        roster = self.paths.roster
        data = json.loads(roster.read_text(encoding="utf-8"))
        data["as_of"] = {"date": played.isoformat(), "event": "after the Week %d game" % week}
        injured = [i for i in receipt["injuries"] if i.get("team") == JAX]
        self.assertTrue(injured, "the fake week carries no Jacksonville injury")
        # Each instruction as the close records it: written from the game's record in the one
        # medical format (runtime/week_pages.availability_entry), as render_week_pages.py
        # --availability prints it.
        season = week_pages.Season(self.root, SEASON)
        game = next(r for r in season.receipts.values() if int(r["week"]) == week and JAX in (r["away"], r["home"]))
        for injury in injured:
            row = next(p for p in data["players"] if p["name"] == injury["player"])
            row["availability"], source = week_pages.availability_entry(season, game, injury)
            row.setdefault("sources", {})["availability"] = source
        roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return played

    def write_report(self, receipt):
        """The week's Game Report in the Game Report template's layout (tests/test_game_report.py
        template_report): its sections, the event line, the header, line score and record of the game,
        and the template's markers last, unnamed: the rebuild names them and fills the box score."""
        week = self.week
        report = self.paths.game_report(week)
        self.assertEqual(report.name, GAME_REPORT)
        checkpoint = "Canonical update - %s - Week %d closed" % (week_pages.long_date(self.played), week)
        sequence = max(item["sequence"] for _, _, item in events.closures(events.load_events(self.root))) + 1
        event = {"date": self.played.isoformat(), "id": "%s-week-%d-game" % (self.played.isoformat(), week),
                 "status": "closed", "summary": "%s in the Week %d game." % (week_pages.score_line(receipt), week),
                 "closure": {"checkpoint": checkpoint, "through": self.played.isoformat(), "sequence": sequence}}
        state = self.root / "state/05_Current_Season_State.md"
        text, n = re.subn(r"^(\*\*Global package checkpoint:\*\* `)[^`]+(`)", r"\g<1>%s\g<2>" % checkpoint,
                          state.read_text(encoding="utf-8"), count=1, flags=re.M)
        self.assertEqual(n, 1)
        state.write_text(text, encoding="utf-8")
        from runtime import game_report
        game = game_weeks.club_game(self.paths, week, JAX)
        played = [r for r in game_weeks.regular_receipts(self.paths) if JAX in (r["away"], r["home"])]
        record = sorted(game_report.record_forms(played, JAX), key=len)[0]
        page = template_report(receipt, game, record, self.root)
        title, rest = page.split("\n", 1)
        # A report opened before the game (the practice-week commit's preparation and game-day
        # event lines) keeps those lines: the week index and the annual record already cite them.
        opened = report.read_text(encoding="utf-8").splitlines() if report.is_file() else []
        earlier = [line for line in opened if line.startswith("<!-- event-record: ")]
        shell = "\n".join([title, ""] + earlier
                           + ["<!-- event-record: %s -->" % json.dumps(event, sort_keys=True), rest])
        self.assertIn(game_report.EVENT_PLACEHOLDER, shell)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(shell, encoding="utf-8")
        # Its pregame sections (from Week 7 the preparation alone) as the game-day commit froze them
        # before kickoff (scripts/freeze_pregame.py; the synthetic close writes the report after the game).
        from runtime import decisions
        frozen = decisions.week_pages(SEASON, week, self.root).pregame
        frozen.parent.mkdir(parents=True, exist_ok=True)
        record = game_report.pregame_record(shell, self.played, game, self.root)
        frozen.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        return report

    def settle_week(self, report):
        """The week's open decisions, settled in the copy as Stone's Game Plan settles them."""
        path = self.root / "state/decision_queue.json"
        queue = json.loads(path.read_text(encoding="utf-8"))
        for item in queue["items"]:
            if item["status"] == "OPEN" and any(b.get("kind") == "week_inputs" and b.get("week") == self.week
                                                for b in item.get("blocks", ())):
                item["status"] = "RESOLVED"
                item["resolution"] = {"date": self.played.isoformat(), "by": "user",
                                      "record": {"path": report.relative_to(self.root).as_posix()},
                                      "summary": "Settled for the synthetic close."}
        path.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    def draw_awards(self, client):
        """The week's awards, then each month's whose weeks have all closed before it (the validator's
        rule: October's once Week 9 closes), drawn through the local test service as the weekly close
        draws them."""
        def draw(kind, key):
            with patch.object(league_awards, "ROOT", self.root), \
                    patch("runtime.private_client.Client", return_value=client), \
                    patch.object(sys, "argv", ["league_awards", kind, str(key), "--season", str(SEASON), "--close"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(league_awards.main(), 0, (kind, key))
        draw("week", self.week)
        with patch.object(league_awards, "ROOT", self.root):
            method, results = league_awards.method(SEASON), league_awards.load_results(SEASON)
        for name, month in method["months"].items():
            if max(month["weeks"]) < self.week and "month-%s" % name not in results:
                draw("month", name)

    def test_week_close_rebuilds_clean_pages_and_validates(self):
        root, paths, week = self.root, self.paths, self.week
        receipt = self.fake_week()
        self.played = self.move_clock(receipt)
        record_practice(self, self.root, week)
        report = self.write_report(receipt)
        self.settle_week(report)
        snapshot = hashlib.sha256((root / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
        _, client = local_service(self, root / "private", "week-close-pages", snapshot=snapshot)
        self.draw_awards(client)
        check_head_coaches(self, root, week, client)
        self.assertEqual(clean_pages.page_errors(report.relative_to(root).as_posix(),
                                                 report.read_text(encoding="utf-8")), [])

        # One command rebuilds every built page; a second run finds nothing to write.
        history = week_pages.medical_path(week_pages.Season(root, SEASON), "medical_history.md")
        before = history.read_bytes()
        record = events.annual_record_path(root, SEASON)
        record_before = record.read_bytes()
        written, problems = rebuild_pages.rebuild(root, SEASON)
        self.assertEqual(problems, [])
        self.assertTrue(written)
        self.assertEqual(rebuild_pages.rebuild(root, SEASON), ([], []))
        self.assertEqual(rebuild_pages.rebuild(root, SEASON, check=True), ([], []))

        # The history pages only gained entries: the medical history its one game entry, the record
        # its lines.
        self.assertTrue(history.read_bytes().startswith(before), "the medical history only gains entries")
        appended = history.read_bytes()[len(before):].decode("utf-8")
        self.assertEqual(appended.count("<!-- event-record:"), 1)
        self.assertIn("Week %d injuries" % week, appended)
        self.assertIn("multi-week", appended)
        self.assertIn("long term", appended)
        self.assertTrue(record.read_bytes().startswith(record_before))
        self.assertEqual(render_week_pages.check(root, SEASON), [])

        season = week_pages.Season(root, SEASON)
        results = week_pages.week_page_path(season, week)
        self.assertTrue(results.is_file())
        self.assertIn(week_pages.TO_COME, results.read_text(encoding="utf-8"))
        self.assertIn("SCK/YDS", report.read_text(encoding="utf-8"))
        self.assertNotIn("SCK-YDS", report.read_text(encoding="utf-8"))
        self.assertEqual(render_box_score.stale_blocks(report, paths.receipts, season=SEASON), [])
        for rel in week_pages.incidents(season):
            self.assertTrue((root / rel).is_file(), rel)
        injury_report = week_pages.medical_path(season, "current_injury_report.md").read_text(encoding="utf-8")
        self.assertIn("(multi-week)", injury_report)
        self.assertIn("(long term)", injury_report)
        # The next period opens (runtime/open_events.open_period): a game week's briefing, its blank Game
        # Plan and its index are issued; the bye's review and blank My Adjustments, the next game's
        # briefing waiting for the bye's close; after the season's last game, no brief.
        from runtime import decisions
        period = open_events.open_period(SEASON, root)
        if period is None:
            brief = None
            for later in sorted(postseason.ROUNDS):
                self.assertFalse(decisions.week_pages(SEASON, later, root).briefing.exists(), later)
        elif "bye" in period:
            bye = decisions.bye_pages(SEASON, period["bye"], root)
            self.assertTrue(bye.review.is_file() and bye.adjustments.is_file())
            _, after = bye_week.around(SEASON, period["bye"], root)
            self.assertFalse(decisions.week_pages(SEASON, int(after["week"]), root).briefing.exists())
            brief = bye.review
        else:
            following = decisions.week_pages(SEASON, period["week"], root)
            self.assertTrue(following.briefing.is_file() and following.plan.is_file())
            brief = following.briefing
        self.assertIn("Game Report", decisions.week_pages(SEASON, week, root).readme.read_text(encoding="utf-8"))

        # The next period's brief (the briefing, or the bye's review) reads each new instruction whole,
        # its exam included.
        from scripts import render_game_week
        briefing = brief.read_text(encoding="utf-8") if brief is not None else ""
        for injury in (i for i in receipt["injuries"] if brief is not None and i.get("team") == JAX
                       and i.get("reassessment_days")):
            exam = week_pages.month_day(self.played + timedelta(days=injury["reassessment_days"]))
            line = next(l for l in briefing.splitlines() if l.startswith("| ") and injury["player"] in l.split("|")[1])
            self.assertIn("| Reassessment, %s |" % exam, line)
            self.assertNotIn("; reassessment", line)      # the note is read whole, not copied as written

        # A played week's index is checked like the open week's (F4): left stale, it fails.
        played_pages = decisions.week_pages(SEASON, week, root)
        built = played_pages.readme.read_text(encoding="utf-8")
        played_pages.readme.write_text(built.replace("[Game Report](Game_Report.md)", "Game Report"), encoding="utf-8")
        self.assertTrue(any("Week %d: the week index is missing or stale" % week in e
                            for e in render_game_week.validation_errors(root)))
        self.assertTrue(render_game_week.check(root, week))
        played_pages.readme.write_text(built, encoding="utf-8")
        self.assertEqual(render_game_week.check(root, week), [])

        # The week's league-results highlights are stored text a rebuild renders (F6).
        game = next(g for g in week_pages.ordered_games(season, week) if JAX not in (g["away"], g["home"]))
        path = week_pages.highlights_path(season, week)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"games": {season.receipt(game)["event_id"]: "A stored highlight."}}),
                        encoding="utf-8")
        self.assertTrue(render_week_pages.check(root, SEASON))
        self.assertEqual(rebuild_pages.rebuild(root, SEASON)[1], [])
        self.assertIn("A stored highlight.", results.read_text(encoding="utf-8"))
        self.assertEqual(render_week_pages.check(root, SEASON), [])

        # Every page is checked as written, none re-recorded as history, and validation of the copy
        # adds nothing to the real checkout's.
        self.assertEqual(clean_pages.clean_errors(root), [])
        self.assertEqual(clean_pages.history(root), clean_pages.history(ROOT))
        baseline = set(validate(ROOT))
        self.assertEqual(sorted(set(validate(root)) - baseline), [])

        # Isolation: nothing reached the real season.
        self.assertEqual(sorted(p.name for p in SeasonPaths(SEASON, ROOT).receipts.glob("*.json")), self.real)


if __name__ == "__main__":
    unittest.main()
