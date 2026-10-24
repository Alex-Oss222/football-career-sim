"""Dated practice and rest records (rebuild step 5, C1; runtime/practices.py).

The closed weeks' records are transcriptions of what their closed pages say:
participation not recorded session by session (a player not named is unknown,
never full), the players the pages name transcribed with their anchors, and the
padded count the Week 5 record and the defect register give (nine through
Week 5: two in each of Weeks 1 to 4, the first the one lawful double week, one
in Week 5). Stone's standing practice instruction builds each later week's
schedule, checked against the 2011 agreement's limits before any session and
again when what was held is recorded: eleven padded practices in the first
eleven weeks (the bye inside them), three in the last six, two in one week
only once and only in the first eleven, the bye's four consecutive days off
with no required player work in them but an injured player's treatment, and
the days off counted by month from the first game, bye days not counted.

Weeks and dates are derived from the fixtures, the closed records and the
standing instruction, never from today's date. Synthetic records live in memory
or in a temporary copy; the real repository is never written.
"""
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import current_job, practices  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

SEASON = 2014
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
PAD, HELMETS = practices.PADDED, "helmets"


def instruction():
    return current_job.practice_instruction(current_job.load(ROOT), SEASON)


def club_weeks():
    return practices.club_games(SEASON, ROOT)


def bye_week():
    ours = club_weeks()
    return next(w for w in range(min(ours), max(ours)) if w not in ours)


def other_day_week():
    """The first Jacksonville game, after the instruction applies, not on the instruction's game day."""
    rule = instruction()["schedule"]
    return next(w for w, g in sorted(club_weeks().items())
                if w >= rule["from_week"] and g["weekday"] != rule["week"]["game_day"])


def held(schedule_sessions, participation_recorded=True):
    return [dict(s, status="held", pad_exceptions=[], participation_recorded=participation_recorded,
                 participation=[]) for s in schedule_sessions]


def recorded(week, sessions, days_off, schedule=None, kind="game"):
    return {"schema": practices.SCHEMA, "season": SEASON, "week": week, "kind": kind, "basis": "recorded",
            "schedule": {"source": (schedule or {}).get("source") or {"instruction": "test"},
                         "sha256": (schedule or {}).get("sha256") or "0" * 64},
            "source": {"page": SeasonPaths(SEASON, ROOT).week_folder(week).joinpath("README.md")
                       .relative_to(ROOT).as_posix()},
            "sessions": sessions, "days_off": days_off, "gaps": []}


def from_instruction(week):
    return practices.schedule_from_instruction(instruction(), SEASON, week, ROOT)


def bye_schedule(week, padded=False, extra=()):
    """A synthetic bye schedule: field work on the days before the break, the players off for the
    first legal break window and to the end of the bye week."""
    first, last = practices.week_span(SEASON, week, ROOT)
    start, end = practices.bye_break_windows(SEASON, week, ROOT)[0]
    sessions = []
    day = first
    while day < start:
        sessions.append({"date": day.isoformat(), "type": "practice", "required": True, "attendees": "team",
                         "equipment": PAD if padded and not sessions else HELMETS})
        day += dt.timedelta(days=1)
    off = []
    day = start
    while day <= last:
        off.append({"date": day.isoformat(), "scope": "players", "players": "all", "exceptions": []})
        day += dt.timedelta(days=1)
    return sessions + list(extra), off


def season_records(stop=None, other_day=None):
    """The closed records plus every later week recorded as the instruction (or, for the bye, the
    synthetic bye schedule) sets it, in order, through Week ``stop``. The week the instruction does not
    set is recorded as ``other_day`` gives it: None for not set, or a helmets-only week of practices."""
    found = practices.records(SEASON, ROOT)
    rule = instruction()["schedule"]
    last = stop or practices.REGULAR_WEEKS
    for week in range(rule["from_week"], last + 1):
        if week == bye_week():
            sessions, off = bye_schedule(week)
            found[week] = recorded(week, held(sessions), off, kind="bye")
        elif week == other_day_week():
            if other_day is None:
                found[week] = practices.not_set_record(SEASON, week, {"page": "x"}, ROOT)
            else:
                first, end = practices.week_span(SEASON, week, ROOT)
                sessions = [{"date": end.isoformat(), "type": "walkthrough", "required": True, "attendees": "team",
                             "equipment": HELMETS}]
                found[week] = recorded(week, held(sessions), [])
        else:
            schedule = from_instruction(week)
            found[week] = recorded(week, held(schedule["sessions"]), schedule["days_off"], schedule)
    return found


def bye_message(start):
    """A failure message of docs/bye_week.md section 6, by its opening words."""
    text = (ROOT / "docs/bye_week.md").read_text(encoding="utf-8").split("## 6.", 1)[1].split("## 7.", 1)[0]
    return next(m for m in re.findall(r"^- `(.+)`$", text, re.M) if m.startswith(start))


class ClosedRecordTests(unittest.TestCase):
    def setUp(self):
        self.found = practices.records(SEASON, ROOT)
        self.start = practices.log_start(SEASON, ROOT, self.found)

    def test_every_closed_week_has_its_record_transcribed(self):
        closed = range(1, self.start)
        self.assertEqual(sorted(w for w, r in self.found.items() if r["basis"] == "closed_record"), list(closed))
        for week in closed:
            record = self.found[week]
            self.assertEqual(record["source"]["page"],
                             SeasonPaths(SEASON, ROOT).game_report(week).relative_to(ROOT).as_posix())
            # Participation was not recorded session by session in any closed week.
            self.assertTrue(all(not s["participation_recorded"] for s in record["sessions"]))
            self.assertTrue(record["gaps"])
            for session in record["sessions"]:
                for entry in session["participation"]:
                    self.assertEqual(entry["source"], record["source"])
        # The players the closed pages name, transcribed (Week 2 and Week 3, for example).
        padded = lambda week: [s for s in self.found[week]["sessions"] if s["equipment"] == PAD]
        for session in padded(2):
            out = {e["player"] for e in session["participation"] if e["status"] == "did_not_participate"}
            self.assertEqual(out, {"Maurice Jones-Drew", "Hakeem Nicks", "Gator Hoskins"})
        self.assertTrue(all(any(e["player"] == "Julian Stanford" and e["status"] == "did_not_participate"
                                for e in s["participation"]) for s in padded(3)))

    def test_nine_padded_used_two_left_and_three_for_the_last_six(self):
        status = practices.padded_status(SEASON, self.start - 1, ROOT, self.found)
        self.assertEqual((status["first"]["used"], status["first"]["left"]), (9, 2))
        self.assertEqual((status["last"]["used"], status["last"]["left"]), (0, 3))
        self.assertEqual((status["double_week"], status["double_week_used"]), (1, True))
        self.assertEqual([o["week"] for o in status["over"]], [2, 3, 4])
        self.assertEqual(status["by_week"], {1: 2, 2: 2, 3: 2, 4: 2, 5: 1})

    def test_the_first_month_has_four_counted_days_off(self):
        months = practices.days_off(SEASON, ROOT, self.found)
        first = months["months"][0]
        self.assertEqual(first["first"], club_weeks()[1]["date"])
        self.assertEqual((first["count"], first["complete"]), (4, True))
        self.assertEqual(months["warnings"], [])

    def test_an_unlisted_player_is_unknown_in_a_closed_record(self):
        for week in range(1, self.start):
            for session in self.found[week]["sessions"]:
                self.assertIsNone(practices.participation_status(session, "Kirk Cousins"))
                for entry in session["participation"]:
                    self.assertEqual(practices.participation_status(session, entry["player"]), entry["status"])
        recorded_session = dict(self.found[1]["sessions"][0], participation_recorded=True)
        self.assertEqual(practices.participation_status(recorded_session, "Kirk Cousins"), "full")

    def test_the_repository_records_validate_and_a_closed_week_shows_no_table(self):
        self.assertEqual(practices.validation_errors(SEASON, ROOT), [])
        for week in range(1, self.start):
            self.assertEqual(practices.render_table(self.found[week]), "")
        self.assertEqual(practices.render_table(practices.not_set_record(SEASON, self.start, {"page": "x"}, ROOT)), "")


class InstructionTests(unittest.TestCase):
    def test_the_instruction_builds_each_week_it_sets(self):
        rule = instruction()["schedule"]
        pads = {(p["week"], p["day"]) for p in rule["equipment"]["pads"]}
        for week, game in sorted(club_weeks().items()):
            if week < rule["from_week"] or game["weekday"] != rule["week"]["game_day"]:
                continue
            schedule = from_instruction(week)
            got = [(dt.date.fromisoformat(s["date"]).strftime("%A"), s["type"], s["equipment"])
                   for s in schedule["sessions"]]
            want = [(s["day"], s["type"], PAD if (week, s["day"]) in pads else rule["equipment"]["otherwise"])
                    for s in rule["week"]["sessions"]]
            self.assertEqual(got, want, week)
            days = [dt.date.fromisoformat(d["date"]) for d in schedule["days_off"]]
            self.assertTrue(all(d < dt.date.fromisoformat(game["date"]) for d in days))
            added = [a["on"] for a in rule["added_days_off"]]
            self.assertEqual(sorted(d.isoformat() for d in days if d.strftime("%A") not in
                                    {o["day"] for o in rule["week"]["days_off"]}),
                             sorted(a for a in added if practices.week_span(SEASON, week, ROOT)[0].isoformat() <= a
                                    <= practices.week_span(SEASON, week, ROOT)[1].isoformat()))
        for week in (bye_week(), other_day_week()):
            with self.assertRaises(practices.NotCovered):
                from_instruction(week)

    def test_the_season_under_the_instruction_keeps_the_limits(self):
        found = season_records(other_day="helmets")
        for week, record in sorted(found.items()):
            if record["basis"] == "recorded":
                earlier = {w: r for w, r in found.items() if w < week}
                self.assertEqual(practices.check_schedule(SEASON, week, record["sessions"], record["days_off"], ROOT,
                                                          earlier), [], week)
        status = practices.padded_status(SEASON, practices.REGULAR_WEEKS, ROOT, found)
        self.assertEqual((status["first"]["used"], status["first"]["left"]), (11, 0))
        self.assertEqual((status["last"]["used"], status["last"]["left"]), (3, 0))
        # The month of the bye holds the four days off with the added day, the bye's days not counted.
        months = {m["month"]: m for m in practices.days_off(SEASON, ROOT, found)["months"]}
        first, last = practices.week_span(SEASON, bye_week(), ROOT)
        month = months[first.strftime("%Y-%m")]
        self.assertEqual(month["count"], 4)
        self.assertFalse(any(first.isoformat() <= d <= last.isoformat() for d in month["days"]))

    def test_a_week_left_unset_makes_the_next_pads_unknown(self):
        found = season_records(other_day=None)
        later = max(w for w in club_weeks() if w > other_day_week())
        schedule = from_instruction(later)
        earlier = {w: r for w, r in found.items() if w < later}
        problems = practices.check_schedule(SEASON, later, schedule["sessions"], schedule["days_off"], ROOT, earlier)
        if any(s["equipment"] == PAD for s in schedule["sessions"]):
            self.assertTrue(problems and "not all on record" in problems[0], problems)
        self.assertIsNone(practices.padded_status(SEASON, later - 1, ROOT, earlier)["last"]["used"])


class LimitTests(unittest.TestCase):
    def first_pad_week(self):
        rule = instruction()["schedule"]
        return min(p["week"] for p in rule["equipment"]["pads"])

    def test_shells_count_and_helmets_alone_do_not(self):
        session = {"equipment": PAD, "status": "held", "required": True}
        self.assertTrue(practices.session_padded(session))
        self.assertFalse(practices.session_padded(dict(session, equipment=HELMETS)))
        self.assertFalse(practices.session_padded(dict(session, equipment="none")))
        # The P6 exceptions never make a helmets practice padded.
        self.assertFalse(practices.session_padded(dict(session, equipment=HELMETS, pad_exceptions=[
            {"player": "Kirk Cousins", "rule": "P6(i)"}, {"player": "Josh Scobee", "rule": "P6(iii)"}])))
        # A cancelled padded practice counts unless the sixty-minute rule takes it out.
        self.assertTrue(practices.session_padded(dict(session, status="cancelled")))
        self.assertFalse(practices.session_padded(dict(session, status="cancelled_beyond_control")))

    def test_a_second_padded_practice_in_a_week_fails_at_schedule_and_record_time(self):
        week = self.first_pad_week()
        found = season_records(stop=week - 1)
        schedule = from_instruction(week)
        sessions = [dict(s) for s in schedule["sessions"]]
        second = next(s for s in sessions if s["type"] == "practice" and s["equipment"] != PAD)
        second["equipment"] = PAD
        problems = practices.check_schedule(SEASON, week, sessions, schedule["days_off"], ROOT, found)
        self.assertTrue(any("is a second padded practice this week, and the season's one week with two padded "
                            "practices was used in Week 1" in p for p in problems), problems)
        record = recorded(week, held(sessions), schedule["days_off"], schedule)
        errors = practices.record_errors(record, ROOT, schedule=dict(schedule, sessions=sessions), records_=found)
        self.assertTrue(any("second padded practice" in e for e in errors), errors)

    def test_a_third_padded_practice_in_the_first_eleven_after_the_closed_weeks_fails(self):
        rule = instruction()["schedule"]
        pad_weeks = sorted(p["week"] for p in rule["equipment"]["pads"] if p["week"] <= practices.FIRST_WEEKS)
        later = next(w for w in sorted(club_weeks()) if w > pad_weeks[-1] and w <= practices.FIRST_WEEKS)
        found = season_records(stop=later - 1)
        schedule = from_instruction(later)
        sessions = [dict(s, equipment=PAD) if s["type"] == "practice" and i == 0 else s
                    for i, s in enumerate(schedule["sessions"])]
        message = bye_message("This practice requests pads but the earlier recorded practices")
        self.assertIn(message, practices.check_schedule(SEASON, later, sessions, schedule["days_off"], ROOT, found))
        record = recorded(later, held(sessions), schedule["days_off"], schedule)
        errors = practices.record_errors(record, ROOT, schedule=dict(schedule, sessions=sessions), records_=found)
        self.assertTrue(any(message in e for e in errors), errors)

    def test_a_not_set_week_makes_the_count_unknown_and_pads_in_the_bye_are_refused(self):
        found = practices.records(SEASON, ROOT)
        start = practices.log_start(SEASON, ROOT, found)
        found[start] = practices.not_set_record(SEASON, start, {"page": "x"}, ROOT)
        status = practices.padded_status(SEASON, start, ROOT, found)
        self.assertEqual((status["first"]["used"], status["first"]["known"]), (None, False))
        self.assertIsNone(practices.week_padded(found[start]))
        for week in range(start + 1, bye_week()):
            schedule = from_instruction(week)
            found[week] = recorded(week, held([dict(s, equipment=HELMETS) for s in schedule["sessions"]]),
                                   schedule["days_off"], schedule)
        sessions, off = bye_schedule(bye_week(), padded=True)
        problems = practices.check_schedule(SEASON, bye_week(), sessions, off, ROOT, found)
        self.assertTrue(any(p.startswith("This practice requests pads on") and "not all on record" in p
                            for p in problems), problems)


class RecordTimeTests(unittest.TestCase):
    def setUp(self):
        self.week = practices.log_start(SEASON, ROOT)
        self.schedule = from_instruction(self.week)
        self.found = practices.records(SEASON, ROOT)
        self.roster = json.loads(SeasonPaths(SEASON, ROOT).roster.read_text(encoding="utf-8"))
        self.names = [p["name"] for p in self.roster["players"]] + [d["name"] for d in self.roster["departures"]]
        self.player = next(p["name"] for p in self.roster["players"] if p["list"] == "active")

    def errors(self, record, **kw):
        kw.setdefault("schedule", self.schedule)
        return practices.record_errors(record, ROOT, players=self.names, records_=self.found, **kw)

    def record(self, sessions=None, days_off=None):
        return recorded(self.week, sessions or held(self.schedule["sessions"]),
                        self.schedule["days_off"] if days_off is None else days_off, self.schedule)

    def test_the_week_as_scheduled_records_clean(self):
        self.assertEqual(self.errors(self.record()), [])
        table = practices.render_table(self.record())
        page = SeasonPaths(SEASON, ROOT).week_folder(self.week).joinpath("README.md").relative_to(ROOT).as_posix()
        self.assertEqual(page_errors(page, table, root=ROOT), [])
        self.assertEqual(table.count("\n| "), len(self.schedule["sessions"]) + len(self.schedule["days_off"]) + 1)

    def test_a_player_out_recorded_full_fails(self):
        out_on = lambda player, day: "out" if player == self.player else None
        # Not listed in a team session whose participation is recorded: full by the record, a contradiction.
        self.assertTrue(any("%s is out on his medical instruction" % self.player in e
                            for e in self.errors(self.record(), out_on=out_on)))
        entry = {"player": self.player, "status": "full", "basis": None, "medical": None,
                 "source": self.record()["source"]}
        sessions = held(self.schedule["sessions"])
        sessions[0]["participation"] = [entry]
        self.assertTrue(any("he is recorded full" in e for e in self.errors(self.record(sessions), out_on=out_on)))
        medical = {"page": "career/2014/Team_Operations/Medical/medical_history.md"}
        for session in sessions:
            session["participation"] = [dict(entry, status="did_not_participate", basis="medical_instruction",
                                             medical=medical)]
        self.assertEqual(self.errors(self.record(sessions), out_on=out_on), [])

    def test_a_session_after_the_master_date_fails(self):
        last = self.schedule["sessions"][-1]["date"]
        master = dt.date.fromisoformat(last) - dt.timedelta(days=1)
        self.assertTrue(any("after the master date" in e for e in self.errors(self.record(), master=master)))
        self.assertEqual(self.errors(self.record(), master=dt.date.fromisoformat(last)), [])

    def test_treatment_on_a_day_off_is_allowed_and_practice_is_not(self):
        off = self.schedule["days_off"][0]["date"]
        treatment = {"date": off, "type": "treatment", "required": True, "attendees": "injured", "equipment": "none"}
        practice = dict(treatment, type="practice", attendees="team", equipment=HELMETS)
        sessions = self.schedule["sessions"]
        self.assertEqual(practices.check_schedule(SEASON, self.week, sessions + [treatment], self.schedule["days_off"],
                                                  ROOT, self.found), [])
        problems = practices.check_schedule(SEASON, self.week, sessions + [practice], self.schedule["days_off"], ROOT,
                                            self.found)
        self.assertTrue(problems and "the players' day off" in problems[0], problems)

    def test_a_session_the_schedule_does_not_name_needs_its_change(self):
        extra = dict(self.schedule["sessions"][0], type="film", equipment="none")
        sessions = held(sorted(self.schedule["sessions"] + [extra], key=lambda s: (s["date"], s["type"])))
        self.assertTrue(any("the schedule names no film that day" in e for e in self.errors(self.record(sessions))))
        for session in sessions:
            if session["type"] == "film":
                session["change"] = {"basis": "Added by Stone for the week's opponent review",
                                     "source": self.record()["source"]}
        self.assertEqual(self.errors(self.record(sessions)), [])
        dropped = held(self.schedule["sessions"][1:])
        self.assertTrue(any("is not recorded; record it held or cancelled" in e for e in self.errors(self.record(dropped))))


class ByeTests(unittest.TestCase):
    def test_the_break_windows(self):
        week = bye_week()
        first, last = practices.week_span(SEASON, week, ROOT)
        windows = practices.bye_break_windows(SEASON, week, ROOT)
        self.assertEqual(windows, [(last - dt.timedelta(days=3), last)])
        self.assertEqual([d.strftime("%A") for d in windows[0]], ["Thursday", "Sunday"])
        # A synthetic Thursday game after the bye gives Wednesday to Saturday (B3).
        games = [dict(g) for g in practices.fixtures(SEASON, ROOT)]
        after = next(g for g in games if int(g["week"]) == week + 1 and practices.JAX in (g["away"], g["home"]))
        thursday = dt.date.fromisoformat(after["date"]) - dt.timedelta(days=3)
        after.update(date=thursday.isoformat(), weekday="Thursday")
        (start, end), = practices.bye_break_windows(SEASON, week, ROOT, games)
        self.assertEqual((start.strftime("%A"), end.strftime("%A")), ("Wednesday", "Saturday"))
        self.assertEqual(end, last - dt.timedelta(days=1))

    def test_required_film_inside_the_break_fails_with_the_designs_message(self):
        week = bye_week()
        start, end = practices.bye_break_windows(SEASON, week, ROOT)[0]
        saturday = end - dt.timedelta(days=1)
        film = {"date": saturday.isoformat(), "type": "film", "required": True, "attendees": "team", "equipment": "none"}
        sessions, off = bye_schedule(week, extra=[film])
        found = season_records(stop=week - 1)
        problems = practices.check_schedule(SEASON, week, sessions, off, ROOT, found)
        self.assertEqual(problems, [bye_message("You scheduled required player film work")])
        # An injured player's treatment in the break is allowed; quarterback meetings are not.
        treatment = dict(film, type="treatment", attendees="injured")
        sessions, off = bye_schedule(week, extra=[treatment])
        self.assertEqual(practices.check_schedule(SEASON, week, sessions, off, ROOT, found), [])
        off[0]["exceptions"] = [{"kind": "quarterback_meetings", "players": "all"}]
        self.assertTrue(any("quarterback meetings" in p for p in
                            practices.check_schedule(SEASON, week, sessions, off, ROOT, found)))

    def test_a_bye_without_a_legal_break_fails(self):
        week = bye_week()
        sessions, off = bye_schedule(week)
        problems = practices.check_schedule(SEASON, week, sessions, off[1:], ROOT, season_records(stop=week - 1))
        self.assertTrue(problems and problems[0].startswith("The players' days off do not give the four consecutive "
                                                            "days the bye requires"), problems)

    def test_pads_in_the_bye_with_none_left_fail(self):
        week = bye_week()
        sessions, off = bye_schedule(week, padded=True)
        problems = practices.check_schedule(SEASON, week, sessions, off, ROOT, season_records(stop=week - 1))
        self.assertIn(bye_message("This practice requests pads but"), problems)


class CopyTests(unittest.TestCase):
    """The runner's command and the game's inputs, in a temporary copy."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        cls.root = Path(cls.tmp.name) / "repo"
        shutil.copytree(ROOT, cls.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_runner_cannot_record_a_schedule_nobody_gave(self):
        from scripts import record_practice_week as rpw
        week = other_day_week()
        source = SeasonPaths(SEASON, self.root).week_folder(week) / "held.json"
        source.write_text(json.dumps({"source": {"page": "x"}, "sessions": [], "days_off": []}), encoding="utf-8")
        problems, _, written = rpw.record(self.root, SEASON, week, source)
        self.assertTrue(problems and "the runner cannot record a schedule nobody gave" in problems[0], problems)
        self.assertIsNone(written)
        problems, _, written = rpw.record(self.root, SEASON, week, check=True)
        self.assertEqual((problems, written), ([], None))
        problems, _, written = rpw.record(self.root, SEASON, week)
        self.assertEqual(problems, [])
        record = json.loads(written.read_text(encoding="utf-8"))
        self.assertEqual((record["basis"], record["sessions"], record["gaps"]), ("not_set", [], [practices.NOT_SET_GAP]))
        written.unlink()
        source.unlink()
        # The schedule the instruction sets is shown and checked; the weeks it does not set say so.
        problems, lines = rpw.show_schedule(self.root, SEASON, practices.log_start(SEASON, self.root))
        self.assertEqual(problems, [])
        self.assertTrue(lines)
        for week in (bye_week(), other_day_week()):
            problems, lines = rpw.show_schedule(self.root, SEASON, week)
            self.assertEqual(lines, [])
            self.assertTrue(problems)

    def test_a_weeks_inputs_are_byte_identical_with_and_without_a_record(self):
        # The last closed week's package, built in the copy as the weekly build does, its chart's inactives
        # holding every player now out so the current roster dresses a legal unit.
        paths = SeasonPaths(SEASON, self.root)
        week = practices.log_start(SEASON, self.root) - 1
        chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
        roster = json.loads(paths.roster.read_text(encoding="utf-8"))
        from runtime.week_inputs import roster_available
        game_day = dt.date.fromisoformat(club_weeks()[week]["date"])
        out = [p["name"] for p in roster["players"] if p["list"] == "active"
               and not roster_available(p["availability"], game_day, SEASON)]
        listed = chart["game_day_inactives"]["players"]
        healthy = [p for p in listed if p not in out]
        chart["game_day_inactives"]["players"] = (out + healthy)[:len(listed)]
        paths.depth_chart.write_text(json.dumps(chart, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        code = ("import hashlib, json, sys\n"
                "sys.path.insert(0, '.')\n"
                "from runtime.seasons import SeasonPaths\n"
                "from runtime.week_inputs import build_package\n"
                "from scripts.build_week_inputs import AVERAGE_ANCHORS\n"
                "from scripts.render_season_stats import load_receipts\n"
                "week, season = %d, %d\n"
                "paths = SeasonPaths(season)\n"
                "sheet = json.loads(paths.call_sheet(week).read_text())\n"
                "receipts = [r for r in load_receipts(paths.receipts) if int(r['week']) < week]\n"
                "package = build_package(week, receipts, sheet['offensive_call_sheet'], AVERAGE_ANCHORS, season,\n"
                "    decisions=sheet.get('decisions'), defensive_sheet=sheet.get('defensive_call_sheet'))\n"
                "print(hashlib.sha256(json.dumps(package, indent=1).encode()).hexdigest())\n" % (week, SEASON))

        def build():
            done = subprocess.run([sys.executable, "-c", code], cwd=self.root, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr[-2000:])
            return done.stdout.strip()
        logged = {w: paths.practice_log(w).read_bytes() for w in range(1, week + 1)}
        with_records = build()
        for w in logged:
            paths.practice_log(w).unlink()
        without = build()
        record = json.loads(logged[week])
        record.update(basis="recorded", schedule={"source": {"instruction": "test"}, "sha256": "0" * 64})
        paths.practice_log(week).write_text(json.dumps(record), encoding="utf-8")
        with_other = build()
        for w, data in logged.items():
            paths.practice_log(w).write_bytes(data)
        self.assertEqual(with_records, without)
        self.assertEqual(with_records, with_other)


if __name__ == "__main__":
    unittest.main()
