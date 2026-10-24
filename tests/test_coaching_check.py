"""The weekly check for head-coach changes at every club (rebuild step 5, D2).

The rate table is the sourced two-pass in-season table; the check draws every
club alike, from the closed games only, one private event per week, in week
order, the retroactive Weeks 1 to 5 first; a club's draws stop at its first
change; a change takes effect the day after the club's latest closed game and
reaches the pages and the news only once the clock reaches that day; a change
at the club the job holder coaches holds the career; the coverage check
passes on the branch as it stands and fails once a later period opens while a
closed week's check is missing. Every draw runs in a temporary copy through
the local private service; the real repository is never written. Weeks and
dates come from the fixtures, the receipts, Document 5 and the method.
"""
import builtins
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import clean_pages, league_coaches as lc, open_events  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.week_inputs import receipt_name  # noqa: E402
from scripts import coaching_check, render_coaching_changes  # noqa: E402
from scripts.research import build_hc_inseason_hazard as builder  # noqa: E402
from local_private_service import local_service  # noqa: E402

SEASON = lc._season(ROOT)
METHOD = lc.load_method(SEASON, ROOT)
MASTER = re.compile(r"\| Master date/time \| [^|]* \|")


def _rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def minimal_root(tmp):
    """A copy holding only what the check reads: the map, the state files, the fixtures, the closed
    games, the week data folders, the January changes, the method and the rate table."""
    root = Path(tmp) / "repo"
    paths = SeasonPaths(SEASON, ROOT)
    files = ["state/05_Current_Season_State.md", "state/current_job.json", "state/decision_queue.json",
             _rel(paths.schedule), METHOD["table"]["file"], _rel(lc.method_path(SEASON, ROOT))]
    files += METHOD["inputs"]["january_changes"]
    for rel in files:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, root / rel)
    for folder in (paths.receipts, paths.data_for(paths.regular_season)):
        shutil.copytree(folder, root / _rel(folder))
    mapping = json.loads((ROOT / "docs/repository_map.json").read_text(encoding="utf-8"))
    mapping.pop("legacy_event_aliases", None)       # their owners are not in the copy
    (root / "docs").mkdir()
    (root / "docs/repository_map.json").write_text(json.dumps(mapping, indent=1), encoding="utf-8")
    return root


def close_next_week(root):
    """Close the week after the latest closed one in the copy: every fixture gets a receipt (home
    20, away 17); returns the week."""
    paths = SeasonPaths(SEASON, root)
    week = max(lc.closed_weeks(SEASON, root)) + 1
    for g in (g for g in paths.regular_games() if g["week"] == week):
        receipt = {"season": SEASON, "week": week, "game_type": "regular", "away": g["away"], "home": g["home"],
                   "event_id": g["game_id"], "final_score": {g["away"]: 17, g["home"]: 20}}
        (paths.receipts / receipt_name(g)).write_text(json.dumps(receipt), encoding="utf-8")
    return week


def at_close_of(root, week):
    """Put the copy at the close of ``week``: the weeks up to it closed (a synthetic close for any not
    yet closed), the receipts and practice records of later weeks removed, and the master date on the
    day of the week's last game. The next week's brief and items stay as the copy has them."""
    paths = SeasonPaths(SEASON, root)
    while max(lc.closed_weeks(SEASON, root)) < week:
        close_next_week(root)
    for receipt in paths.receipts.glob("*.json"):
        if json.loads(receipt.read_text(encoding="utf-8")).get("week", 0) > week:
            receipt.unlink()
    for later in range(week + 1, 18):
        paths.practice_log(later).unlink(missing_ok=True)
    last = max(date.fromisoformat(g["date"]) for g in paths.regular_games() if g["week"] == week)
    set_master(root, last, "after the week's last game (test)")
    return week


def set_master(root, day, words):
    path = root / "state/05_Current_Season_State.md"
    text = path.read_text(encoding="utf-8")
    line = "| Master date/time | %s %d, %d, %s |" % (day.strftime("%B"), day.day, day.year, words)
    path.write_text(MASTER.sub(line, text, count=1), encoding="utf-8")


def set_rates(root, rates):
    """Replace cells' rates in the copy's table and re-record the table's digest in the method."""
    method = lc.load_method(SEASON, root)
    table_file = root / method["table"]["file"]
    table = json.loads(table_file.read_text(encoding="utf-8"))
    for key, rate in rates.items():
        table["rates"][key]["rate"] = rate
    table_file.write_text(json.dumps(table, indent=1) + "\n", encoding="utf-8")
    method["table"]["sha256"] = hashlib.sha256(table_file.read_bytes()).hexdigest()
    lc.method_path(SEASON, root).write_text(json.dumps(method, indent=1) + "\n", encoding="utf-8")


def add_item(root, item):
    path = root / "state/decision_queue.json"
    queue = json.loads(path.read_text(encoding="utf-8"))
    queue["items"].append(item)
    path.write_text(json.dumps(queue, indent=1) + "\n", encoding="utf-8")


def tree_digest(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(folder).rglob("*")) if p.is_file()}


class HazardTableTests(unittest.TestCase):
    def test_the_method_names_the_sourced_two_pass_table(self):
        table = lc.load_table(METHOD, ROOT)
        january = json.loads((ROOT / "library/data/2012_hc_change_base_rates.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256((ROOT / METHOD["table"]["file"]).read_bytes()).hexdigest(),
                         METHOD["table"]["sha256"])
        self.assertEqual(table["source"]["sha256"], january["source"]["sha256"])
        self.assertIn(table["source"]["commit"], table["source"]["url"])
        self.assertEqual(METHOD["table"]["source"]["url"], table["source"]["url"])
        self.assertTrue((ROOT / METHOD["table"]["builder"]).is_file() and (ROOT / METHOD["table"]["verifier"]).is_file())
        self.assertTrue((ROOT / METHOD["table"]["record"]).is_file())
        # The outcome rows stop at 2012, New Orleans 2012 is left out, and the cells cover games 1 to 15.
        self.assertTrue(table["changes"] and all(c["season"] <= 2012 for c in table["changes"]))
        self.assertNotIn(("NO", 2012), {(c["club"], c["season"]) for c in table["changes"]})
        self.assertEqual(table["games_at_risk"], {"first": 1, "last": 15})
        self.assertEqual(sum(r["changes"] for r in table["rates"].values()), len(table["changes"]))
        for key, row in table["rates"].items():
            w, p = table["prior_weight"], table["overall"]["rate"]
            self.assertAlmostEqual(row["rate"], (row["changes"] + w * p) / (row["club_games"] + w), places=6)

    def test_the_event_definition_on_synthetic_seasons(self):
        rows = ["season,game_type,week,home_team,away_team,home_coach,away_coach,home_score,away_score"]

        def season(year, home_coaches, away_coaches, home_wins=True):
            for week in range(1, 17):
                hs, as_ = (20, 10) if home_wins else (10, 20)
                rows.append("%d,REG,%d,AAA,BBB,%s,%s,%d,%d" % (year, week, home_coaches(week), away_coaches(week), hs, as_))
        # 2001 is read only to count seasons back; 2002: AAA's coach is replaced after game 5 and the
        # interim finishes; BBB's coach misses games 4 to 15 and returns for game 16 (a stand-in).
        season(2001, lambda w: "Al", lambda w: "Bo")
        season(2002, lambda w: "Al" if w <= 5 else "Interim", lambda w: "Bo" if w <= 3 or w == 16 else "Fill",
               home_wins=False)
        season(2013, lambda w: "Late", lambda w: "Late")       # a later season: never kept
        data = ("\n".join(rows) + "\n").encode()
        games = builder.club_games(data)
        self.assertFalse(any(s > 2012 for _, s in games))
        cells, changes, counted = builder.hazard(games)
        self.assertEqual(counted, 2)
        self.assertEqual([(c["club"], c["season"], c["game"], c["successor"]) for c in changes],
                         [("AAA", 2002, 5, "Interim")])
        self.assertEqual(changes[0]["cell"], "5 or more|later season")    # 0-5, Al's second season
        # AAA is at risk after games 1 to 5 only; BBB (no change) after games 1 to 15.
        self.assertEqual(sum(n for _, n in cells.values()), 5 + 15)
        with self.assertRaises(ValueError):
            builder.hazard({("AAA", 2013): []})

    def test_a_mismatched_input_digest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "games.csv"
            path.write_bytes(b"season,game_type\n2002,REG\n")
            with self.assertRaises(ValueError) as caught:
                builder.read_source(path)
            self.assertIn("refused", str(caught.exception))

    def test_nothing_at_run_time_opens_games_csv(self):
        for module in (lc, coaching_check, render_coaching_changes):
            text = Path(module.__file__).read_text(encoding="utf-8")
            self.assertNotIn("games.csv", text)
            self.assertNotIn("nfldata", text)
        real_open = builtins.open

        def guarded(file, *args, **kwargs):
            if "games.csv" in str(file):
                raise AssertionError("games.csv opened at run time")
            return real_open(file, *args, **kwargs)
        with patch("builtins.open", guarded), patch("io.open", guarded):
            method, weeks = coaching_check.plan(SEASON, max(lc.closed_weeks(SEASON, ROOT)), ROOT)
        self.assertTrue(weeks)


class BranchAsItStandsTests(unittest.TestCase):
    def test_adopted_with_the_users_words_and_the_checks_made_in_order(self):
        log = (ROOT / "docs/rebuild_plan.md").read_text(encoding="utf-8")
        self.assertEqual(METHOD["status"], "adopted")
        self.assertIn('"%s"' % METHOD["adopted"]["user_words"], log)
        self.assertIn('"%s"' % METHOD["retroactive"]["user_words"], log)
        self.assertIn("%s:" % date.fromisoformat(METHOD["adopted"]["user_date"]).strftime("%B %d, %Y").replace(" 0", " "),
                      log)
        # The retroactive weeks come first, before the check of the week they precede; the checks
        # recorded on the branch and the weeks still due are the closed weeks at risk, in week order,
        # the recorded ones first. Before the first check nothing is drawn, written or published.
        retro = METHOD["retroactive"]
        self.assertEqual(retro["due_before_check_of_week"], max(retro["weeks"]) + 1)
        done, due = sorted(lc.checks(SEASON, ROOT)), lc.due_weeks(SEASON, ROOT)
        at_risk = lc.at_risk_weeks(SEASON, ROOT)
        self.assertEqual(done + due, at_risk)
        self.assertEqual(at_risk[:len(retro["weeks"])], retro["weeks"])
        if not done:
            self.assertFalse(lc.folder(SEASON, ROOT).exists())
            self.assertFalse(lc.stored_news(SEASON, ROOT))

    def test_validation_and_coverage_pass(self):
        self.assertEqual(lc.validation_errors(ROOT), [])
        self.assertEqual(lc.coverage_errors(ROOT, SEASON), [])
        self.assertIsNone(lc.career_hold(SEASON, ROOT))
        self.assertEqual(render_coaching_changes.check(ROOT, SEASON), [])

    def test_every_club_has_its_january_record(self):
        clubs = {g[side] for g in SeasonPaths(SEASON, ROOT).regular_games() for side in ("away", "home")}
        self.assertEqual(set(lc.tenures(METHOD, ROOT)), clubs)
        self.assertEqual(len(clubs), 32)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = minimal_root(self.tmp.name)
        self.store, self.client = local_service(self, Path(self.tmp.name), "coaching-check")

    def run_close(self, week, root=None):
        lines = []
        code = coaching_check.close(SEASON, week, root or self.root, self.client, lines.append)
        return code, lines

    def closed_events(self):
        with self.store.connect() as c:
            return [r[0] for r in c.execute("SELECT event_id FROM events ORDER BY rowid")]

    def test_the_retroactive_weeks_are_drawn_once_in_order_one_event_each(self):
        retro = lc.load_method(SEASON, self.root)["retroactive"]
        at_close_of(self.root, retro["due_before_check_of_week"])
        due = lc.due_weeks(SEASON, self.root)
        self.assertEqual(due, retro["weeks"] + [retro["due_before_check_of_week"]])
        before = tree_digest(SeasonPaths(SEASON, self.root).receipts)
        code, _ = self.run_close(max(due))
        self.assertEqual(code, 0)
        records = lc.checks(SEASON, self.root)
        self.assertEqual(sorted(records), due)
        self.assertEqual([records[w]["order"] for w in due], list(range(1, len(due) + 1)))
        # Weeks 1 to 5 are the retroactive draws; the week they precede is checked after them, its own.
        self.assertEqual([w for w in due if records[w]["retroactive"]], retro["weeks"])
        self.assertEqual(self.closed_events(), [lc.event_id(SEASON, w) for w in due])
        self.assertEqual(len({records[w]["result_ref"] for w in due}), len(due))
        # A second run is refused and draws nothing; no closed game was rewritten.
        with self.assertRaises(coaching_check.Refused):
            self.run_close(max(due))
        self.assertEqual(len(self.closed_events()), len(due))
        self.assertEqual(tree_digest(SeasonPaths(SEASON, self.root).receipts), before)
        self.assertEqual(lc.validation_errors(self.root), [])
        # The next week's check comes after them, on its own event.
        week = close_next_week(self.root)
        code, _ = self.run_close(week)
        self.assertEqual(code, 0)
        self.assertEqual(lc.checks(SEASON, self.root)[week]["order"], len(due) + 1)
        self.assertFalse(lc.checks(SEASON, self.root)[week]["retroactive"])
        self.assertEqual(lc.validation_errors(self.root), [])

    def test_a_week_not_closed_or_with_the_method_awaiting_draws_nothing(self):
        with self.assertRaises(coaching_check.Refused):
            self.run_close(max(lc.closed_weeks(SEASON, self.root)) + 1)
        method = lc.load_method(SEASON, self.root)
        method["status"] = "awaiting the user's answer"
        lc.method_path(SEASON, self.root).write_text(json.dumps(method, indent=1), encoding="utf-8")
        self.assertEqual(lc.due_weeks(SEASON, self.root), [])
        with self.assertRaises(coaching_check.Refused):
            self.run_close(max(lc.closed_weeks(SEASON, self.root)))
        week = close_next_week(self.root)
        add_item(self.root, {"id": "%d-w%02d-game-plan" % (SEASON, week + 1), "blocks": []})
        self.assertEqual(lc.validation_errors(self.root), [])
        self.assertEqual(self.closed_events(), [])

    def test_coverage_fails_once_a_later_period_opens_while_a_check_is_missing(self):
        retro = lc.load_method(SEASON, self.root)["retroactive"]
        week = at_close_of(self.root, retro["due_before_check_of_week"])
        paths = SeasonPaths(SEASON, self.root)
        self.assertEqual(lc.coverage_errors(self.root, SEASON), [])        # nothing after the week is open
        missing = lc.due_weeks(SEASON, self.root)
        self.assertEqual(missing, retro["weeks"] + [week])
        # The next week's items and brief open at the close, before the check: they do not count.
        add_item(self.root, {"id": "%d-w%02d-game-plan" % (SEASON, week + 1), "class": "weekly_game_plan",
                             "blocks": [{"kind": "week_inputs", "season": SEASON, "week": week + 1}]})
        brief = paths.week_data(week + 1) / "briefings.json"
        if not brief.is_file():
            brief.parent.mkdir(parents=True, exist_ok=True)
            brief.write_text('{"issues": []}\n', encoding="utf-8")
        self.assertIn(week + 1, lc.opened_periods(SEASON, self.root))
        self.assertEqual(lc.coverage_errors(self.root, SEASON), [])
        self.assertEqual(lc.validation_errors(self.root), [])
        # Its practice record does: every missing week, the retroactive ones included, fails.
        practice = paths.practice_log(week + 1)
        practice.parent.mkdir(parents=True, exist_ok=True)
        practice.write_text("{}", encoding="utf-8")
        errors = lc.coverage_errors(self.root, SEASON)
        self.assertEqual([int(re.match(r"Week (\d+)", e)[1]) for e in errors], missing)
        self.assertTrue(lc.validation_errors(self.root))
        # So does the master date passing the day of its first practice, with no record written.
        practice.unlink()
        self.assertEqual(lc.coverage_errors(self.root, SEASON), [])
        first = lc.first_practice_day(SEASON, week + 1, self.root)
        set_master(self.root, first, "after the 9 a.m. ET record of the Week %d preparation (test)" % (week + 1))
        self.assertEqual(lc.coverage_errors(self.root, SEASON), [])          # that day is not yet past
        set_master(self.root, first + timedelta(days=1), "after the 9 a.m. ET record of the Week %d preparation "
                                                         "(test)" % (week + 1))
        self.assertEqual(len(lc.coverage_errors(self.root, SEASON)), len(missing))
        # And the practice-week commit: the record written and the clock moved to game day.
        game_day = min(date.fromisoformat(g["date"]) for g in paths.regular_games() if g["week"] == week + 1)
        practice.write_text("{}", encoding="utf-8")
        set_master(self.root, game_day, "game day, before kickoff (test)")
        self.assertEqual(len(lc.coverage_errors(self.root, SEASON)), len(missing))
        # Once every check is made, in order, the open period passes.
        self.assertEqual(self.run_close(week)[0], 0)
        self.assertEqual(lc.coverage_errors(self.root, SEASON), [])
        self.assertEqual(lc.validation_errors(self.root), [])

    def test_changes_take_effect_after_the_latest_closed_game_and_reach_the_pages_with_the_clock(self):
        set_rates(self.root, {"1 to 2|first season": 1.0})
        games = lc.closed_games(SEASON, self.root)
        first_week = min(lc.due_weeks(SEASON, self.root))
        expected = sorted(c for c, t in lc.tenures(lc.load_method(SEASON, self.root), self.root).items()
                          if t == "first season" and any(g.week == first_week for g in games[c])
                          and 1 <= lc.record_after(games[c], first_week)[2] - lc.record_after(games[c], first_week)[1] <= 2)
        self.assertTrue(expected)
        due = lc.due_weeks(SEASON, self.root)
        before_pages = tree_digest(SeasonPaths(SEASON, self.root).receipts)
        self.assertEqual(self.run_close(max(due))[0], 0)
        records = lc.checks(SEASON, self.root)
        changed = sorted(r["club"] for r in records[first_week]["clubs"] if r["changed"])
        self.assertEqual(changed, expected)
        latest = max(lc.closed_weeks(SEASON, self.root))
        for row in (r for r in records[first_week]["clubs"] if r["changed"]):
            last_game = max(date.fromisoformat(g.date) for g in games[row["club"]] if g.week <= latest)
            self.assertEqual(row["effective"], (last_game + timedelta(days=1)).isoformat())
            for later in (w for w in records if w > first_week):
                self.assertNotIn(row["club"], [r["club"] for r in records[later]["clubs"]])
                if any(g.week == later for g in games[row["club"]]):
                    self.assertIn({"club": row["club"], "reason": "changed earlier this season"},
                                  records[later]["not_drawn"])
        # Only the changes the clock has reached have pages and news.
        today = master_date(self.root)
        reached = {r["club"] for rec in records.values() for r in rec["clubs"]
                   if r["changed"] and date.fromisoformat(r["effective"]) <= today}
        pages = {p.name for p in lc.folder(SEASON, self.root).glob("Head_Coach_Change_*.md")}
        self.assertEqual(len(pages), len(reached))
        self.assertEqual(len(lc.stored_news(SEASON, self.root)), len(reached))
        self.assertEqual(lc.validation_errors(self.root), [])
        later_day = max(date.fromisoformat(r["effective"]) for rec in records.values() for r in rec["clubs"]
                        if r["changed"])
        set_master(self.root, later_day, "after the game-day clock advance (test)")
        self.assertTrue(lc.validation_errors(self.root))          # the pages are now due
        out = []
        self.assertEqual(coaching_check.main(["--season", str(SEASON), "--effective"], root=self.root, out=out.append), 0)
        self.assertEqual(lc.validation_errors(self.root), [])
        everyone = sorted(r["club"] for rec in records.values() for r in rec["clubs"] if r["changed"])
        self.assertEqual(len(list(lc.folder(SEASON, self.root).glob("Head_Coach_Change_*.md"))), len(everyone))
        news = lc.stored_news(SEASON, self.root)
        self.assertEqual(sorted(e["subject"] for e in news.values()), everyone)
        for event in news.values():
            self.assertEqual((event["kind"], event["state"], event["stone_part"]), ("head_coach_change", "resolved", "none"))
            self.assertEqual(event["authority"]["decides"], "other_club")
            self.assertEqual(event["raised"]["by"], "communications_staff")
            self.assertEqual(event["process"][0]["kind"], "criteria")
            self.assertEqual(event["resolution"]["decision"]["criteria"], 0)
            self.assertIsNone(event["queue_item"])
            # Raised and resolved through the event store's own writers, stamped with the open period.
            self.assertEqual(event["period"], open_events.open_period(SEASON, self.root))
            self.assertEqual(event["resolution"]["period"], event["period"])
        self.assertEqual(open_events.validation_errors(self.root), [])
        record_md = (SeasonPaths(SEASON, self.root).annual_record).read_text(encoding="utf-8")
        for club in everyone:
            self.assertIn("The %s made a change at head coach" % club, record_md)
        for path in lc.folder(SEASON, self.root).glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(clean_pages.page_errors(_rel_in(self.root, path), text, root=ROOT), [], path.name)
        self.assertEqual(render_coaching_changes.check(self.root, SEASON), [])
        self.assertEqual(tree_digest(SeasonPaths(SEASON, self.root).receipts), before_pages)
        # The head coach of a changed club is an interim from the day of the change.
        row = next(r for r in records[first_week]["clubs"] if r["changed"])
        day = date.fromisoformat(row["effective"])
        self.assertFalse(lc.head_coach(row["club"], day - timedelta(days=1), SEASON, self.root)["interim"])
        self.assertTrue(lc.head_coach(row["club"], day, SEASON, self.root)["interim"])
        with self.assertRaises(ValueError):
            lc.head_coach(row["club"], master_date(self.root) + timedelta(days=1), SEASON, self.root)

    def test_a_change_at_the_job_holders_club_holds_the_career(self):
        set_rates(self.root, {key: 1.0 for key in lc.load_table(lc.load_method(SEASON, self.root), self.root)["rates"]})
        due = lc.due_weeks(SEASON, self.root)
        code, lines = self.run_close(max(due))
        self.assertEqual(code, coaching_check.HELD)
        records = lc.checks(SEASON, self.root)
        self.assertEqual(sorted(records), due[:1])          # every club changed in the first week; then the hold
        club = lc.holder_club(self.root)
        held = next(r for r in records[due[0]]["clubs"] if r["club"] == club)
        self.assertTrue(held["changed"])
        message = lc.career_hold(SEASON, self.root)
        self.assertIn("Khan", message)
        self.assertIn("step 6", message)
        self.assertEqual(lines[-1], message)
        # Nothing further: another run and the clock-move step are refused; the club gets no page or news.
        with self.assertRaises(coaching_check.Refused):
            self.run_close(max(due))
        self.assertEqual(coaching_check.main(["--season", str(SEASON), "--effective"], root=self.root,
                                             out=lambda *_: None), coaching_check.HELD)
        self.assertNotIn(club, [e["subject"] for e in lc.stored_news(SEASON, self.root).values()])
        self.assertFalse(list(lc.folder(SEASON, self.root).glob("*%s*" % club.split()[-1])))
        # The record itself validates; a later period opening, or the clock moving, fails on the hold.
        self.assertEqual(lc.hold_errors(self.root, SEASON), [])
        add_item(self.root, {"id": "%d-w%02d-game-plan" % (SEASON, records[due[0]]["opened_through"] + 1), "blocks": []})
        self.assertEqual(lc.hold_errors(self.root, SEASON), [message])

    def test_the_hold_does_not_lift_when_step_6_flags_the_season_end(self):
        """A drawn change at the job holder's club stays held, with no page or news, when the season-end
        decision is marked built: it is the Club Decision's, never an ordinary other club's change."""
        import dataclasses
        from runtime import decisions
        set_rates(self.root, {key: 1.0 for key in lc.load_table(lc.load_method(SEASON, self.root), self.root)["rates"]})
        due = lc.due_weeks(SEASON, self.root)
        code, _ = self.run_close(max(due))
        self.assertEqual(code, coaching_check.HELD)
        club = lc.holder_club(self.root)
        message = lc.career_hold(SEASON, self.root)
        flag = decisions.BY_KIND["season_end"]
        with patch.dict(decisions.BY_KIND, {"season_end": dataclasses.replace(flag, implemented=True)}):
            self.assertEqual([r["club"] for _, r in lc.held_changes(SEASON, self.root)], [club])
            self.assertEqual(lc.career_hold(SEASON, self.root), message)
            far = date(SEASON + 1, 3, 1)
            self.assertNotIn(club, [r["club"] for _, r in lc.effective_changes(SEASON, self.root, far)])
            self.assertFalse([p for p in lc.pages(SEASON, self.root, far) if club.split()[-1] in p.name])

    def test_the_label_swap(self):
        method = lc.load_method(SEASON, self.root)
        week = max(lc.closed_weeks(SEASON, self.root))
        inputs = lc.week_inputs(SEASON, week, self.root, method)
        pkt = lc.packet(method, inputs, "snapshot", self.root, "code")
        # Relabelling the protagonist: the job record names another club as his employer.
        job_path = self.root / "state/current_job.json"
        job = json.loads(job_path.read_text(encoding="utf-8"))
        club = lc.holder_club(self.root)
        other = next(r["club"] for r in inputs["clubs"] if r["club"] != club)
        for appt in job["appointments"]:
            if appt["id"] == job["current_appointment"]:
                appt["employer"]["club"] = other
        job_path.write_text(json.dumps(job, indent=1), encoding="utf-8")
        self.assertEqual(lc.holder_club(self.root), other)
        again = lc.week_inputs(SEASON, week, self.root, method)
        self.assertEqual(again, inputs)
        self.assertEqual(lc.packet(method, again, "snapshot", self.root, "code"), pkt)
        # Swapping two clubs' facts swaps their chances, and nothing else moves.
        table = lc.load_table(method, self.root)
        a, b = club, other
        swap = {a: b, b: a}
        paths = SeasonPaths(SEASON, self.root)
        for path in paths.receipts.glob("*.json"):
            r = json.loads(path.read_text(encoding="utf-8"))
            r["away"], r["home"] = swap.get(r["away"], r["away"]), swap.get(r["home"], r["home"])
            r["final_score"] = {swap.get(k, k): v for k, v in r["final_score"].items()}
            path.write_text(json.dumps(r), encoding="utf-8")
        fixtures = json.loads(paths.schedule.read_text(encoding="utf-8"))
        for g in fixtures["games"]:
            g["away"], g["home"] = swap.get(g["away"], g["away"]), swap.get(g["home"], g["home"])
        paths.schedule.write_text(json.dumps(fixtures), encoding="utf-8")
        tenure = lc.tenures(method, self.root)
        if tenure[a] != tenure[b]:
            self.skipTest("the two clubs differ in January; the record swap alone is checked below")
        swapped = {r["club"]: table["rates"][lc.cell(r)]["rate"] for r in lc.week_inputs(SEASON, week, self.root, method)["clubs"]}
        chances = {r["club"]: table["rates"][lc.cell(r)]["rate"] for r in inputs["clubs"]}
        self.assertEqual(swapped[a], chances[b])
        self.assertEqual(swapped[b], chances[a])
        self.assertEqual({k: v for k, v in swapped.items() if k not in swap}, {k: v for k, v in chances.items() if k not in swap})

    def test_a_real_later_firing_planted_in_the_rails_or_the_library_changes_no_input(self):
        method = lc.load_method(SEASON, self.root)
        week = max(lc.closed_weeks(SEASON, self.root))
        digest = lc.inputs_digest(lc.week_inputs(SEASON, week, self.root, method))
        for rel in ("library/2014_planted_firing.md", "library/data/2014_inseason_rails/planted_firing.json"):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text('{"club": "any", "head_coach_fired": true}\n', encoding="utf-8")
        self.assertEqual(lc.inputs_digest(lc.week_inputs(SEASON, week, self.root, method)), digest)

    def test_a_fixed_reference_gives_a_fixed_result(self):
        stream = coaching_check.stream("ab" * 32, {"event_id": "pin"})
        self.assertEqual((stream.random(), stream.random()), (0.6652916429885176, 0.6756820366345362))
        method = lc.load_method(SEASON, self.root)
        table = lc.load_table(method, self.root)
        inputs = lc.week_inputs(SEASON, max(lc.closed_weeks(SEASON, self.root)), self.root, method)
        pkt = lc.packet(method, inputs, "snapshot", self.root, "code")
        first = lc.draw(inputs, table, coaching_check.stream("cd" * 32, pkt).random)
        self.assertEqual(lc.draw(inputs, table, coaching_check.stream("cd" * 32, pkt).random), first)
        self.assertNotEqual(lc.draw(inputs, table, coaching_check.stream("ef" * 32, pkt).random), first)

    def test_a_club_on_its_bye_has_no_line(self):
        paths = SeasonPaths(SEASON, self.root)
        counts = {}
        for g in paths.regular_games():
            counts.setdefault(g["week"], set()).update((g["away"], g["home"]))
        week = next(w for w in lc.closed_weeks(SEASON, self.root) if len(counts[w]) < 32)
        inputs = lc.week_inputs(SEASON, week, self.root)
        listed = {r["club"] for r in inputs["clubs"]} | {r["club"] for r in inputs["not_drawn"]}
        self.assertEqual(listed, counts[week])
        self.assertLess(len(listed), 32)

    def test_a_tampered_record_or_a_changed_method_fails(self):
        due = lc.due_weeks(SEASON, self.root)
        self.assertEqual(self.run_close(max(due))[0], 0)
        path = lc.week_path(SEASON, due[0], self.root)
        record = json.loads(path.read_text(encoding="utf-8"))
        record["clubs"][0]["changed"] = not record["clubs"][0]["changed"]
        path.write_text(json.dumps(record, indent=1), encoding="utf-8")
        self.assertTrue(any("result differs" in e for e in lc.validation_errors(self.root)))
        record["clubs"][0]["changed"] = not record["clubs"][0]["changed"]
        path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        self.assertEqual(lc.validation_errors(self.root), [])
        method = lc.load_method(SEASON, self.root)
        method["modelling_choice"]["rule"] += " "
        lc.method_path(SEASON, self.root).write_text(json.dumps(method, indent=1), encoding="utf-8")
        self.assertTrue(any("the method changed after the draw" in e for e in lc.validation_errors(self.root)))


class AnnualRecordHistoryTests(unittest.TestCase):
    """In a full copy: the annual record keeps its lines written before Week 6 as an exact prefix,
    so a change dated among them cannot be listed, and the step refuses before any page, news or
    record line is written (the draw itself is kept)."""

    def test_a_page_that_would_break_the_annual_records_history_writes_nothing(self):
        tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "repo"
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".sim_cache", "__pycache__"), symlinks=True)
        store, client = local_service(self, Path(tmp.name), "annual-record")
        paths = SeasonPaths(SEASON, root)
        record_md = paths.annual_record.read_bytes()
        set_rates(root, {key: 1.0 for key in lc.load_table(lc.load_method(SEASON, root), root)["rates"]})
        # At the close of the last retroactive week, a club on its bye that week has its latest game
        # among the weeks whose record lines were written before Week 6.
        at_close_of(root, max(lc.load_method(SEASON, root)["retroactive"]["weeks"]))
        job = json.loads((root / "state/current_job.json").read_text(encoding="utf-8"))
        job["status"] = "BETWEEN_JOBS"               # no hold, so every club's change is published
        (root / "state/current_job.json").write_text(json.dumps(job, indent=1), encoding="utf-8")
        games = lc.closed_games(SEASON, root)
        latest = max(lc.closed_weeks(SEASON, root))
        today = master_date(root)
        if not any(date.fromisoformat(lc.record_after(g, latest)[4]) < today - timedelta(days=1) for g in games.values()):
            self.skipTest("no club's change would be dated before the master date")
        with self.assertRaises(coaching_check.Refused) as caught:
            coaching_check.close(SEASON, max(lc.due_weeks(SEASON, root)), root, client, lambda *_: None)
        self.assertIn("nothing was written", str(caught.exception))
        self.assertTrue(lc.checks(SEASON, root))
        self.assertFalse(list(lc.folder(SEASON, root).glob("*.md")))
        self.assertFalse(lc.stored_news(SEASON, root))
        self.assertEqual(paths.annual_record.read_bytes(), record_md)


class FirstPracticeTests(unittest.TestCase):
    """In a full copy with no standing practice instruction: the open week is asked on My Responses, and
    once Stone's "Practice week" answer is applied its first session, not the first day of the week's
    span, is the week's first practice, so the checks due before it fail nothing until that day passes."""

    def test_a_week_asked_on_my_responses_opens_at_his_first_session(self):
        import contextlib
        import io
        from runtime import current_job, practices
        from runtime.decisions import PRACTICE_WEEK, week_pages
        from scripts import record_practice_week as rpw, render_game_week
        sys.path.insert(0, str(ROOT / "tests"))
        import support_events as se
        from test_practices import answer_text
        tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "repo"
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".sim_cache", "__pycache__"), symlinks=True)
        game = se.open_game(root)
        if game is None:
            self.skipTest("every regular-season game has closed")
        week = int(game["week"])
        path = root / current_job.JOB
        job = json.loads(path.read_text(encoding="utf-8"))
        for rule in current_job.instructions(job):
            if rule["subject"] == "practice_schedule":
                rule["status"] = "WITHDRAWN"
        path.write_text(json.dumps(job, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(root)
        if rpw.practice_item(root, SEASON, week) is None:
            self.skipTest("the open week's practice is not asked")
        span = practices.week_span(SEASON, week, root)[0]
        self.assertEqual(lc.first_practice_day(SEASON, week, root), span)
        pages = week_pages(SEASON, week, root)
        block = rpw.read_block(root, SEASON, {"week": week}, PRACTICE_WEEK)
        pages.responses.write_text(pages.responses.read_text(encoding="utf-8").replace(block.text, block.text.replace(
            "**My answer:**\n", "**My answer:** %s\n" % answer_text(week).replace("\n", "; "), 1), 1), encoding="utf-8")
        tuesday = se.tuesday_before(game)
        se.midweek(root, tuesday, 9, 0, week)
        status, problems, _, _ = rpw.answer(root, SEASON, week)
        self.assertEqual((status, problems), ("SET", []))
        schedule, _ = rpw.applied_schedule(root, SEASON, week)
        first = min(date.fromisoformat(s["date"]) for s in schedule["sessions"])
        self.assertGreater(first, span)
        self.assertEqual(lc.first_practice_day(SEASON, week, root), first)
        self.assertNotIn(week, lc.practice_weeks_opened(SEASON, root))
        set_master(root, first + timedelta(days=1), "after the 9 a.m. ET record of the Week %d preparation (test)" % week)
        self.assertIn(week, lc.practice_weeks_opened(SEASON, root))


def _rel_in(root, path):
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()


if __name__ == "__main__":
    unittest.main()
