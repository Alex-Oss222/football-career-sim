"""The career views rendered from the job record and the decision queue.

Mutations run on one throwaway copy of the checkout, with any paused-game
record removed so a live pause cannot decide a test; each test restores the
files it changed. Weeks come from the fixtures and receipts (the first
unplayed Jacksonville week, then the first unplayed postseason round) and
dates from the master date, so the tests hold at any later clock. The desk
is the whole of the active season's README, a clean page.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root
from runtime import current_job, decision_queue
from runtime.decision_queue import event
from runtime.events import repository_map
from runtime.player_bios import master_date
from runtime.clean_pages import page_errors
from runtime.season_layout import STONE_REVIEWS
from runtime.seasons import SeasonPaths
from scripts import render_career_views as views
from scripts import render_coach_pages
from scripts.validate_repository import anchors, without_code

STATE = "state/05_Current_Season_State.md"
LINK = re.compile(r"\[[^\]\n]+\]\(([^\s)]+)\)")


def club_games(root):
    club = current_job.appointment(current_job.load(root))["employer"]["club"]
    season = int(repository_map(root)["active_season"])
    return sorted((g for g in SeasonPaths(season, root).regular_games() if club in (g["away"], g["home"])),
                  key=lambda g: g["date"])


def first_unplayed_week(root):
    """The first week with a Jacksonville fixture and no receipt, then the
    first postseason round with none; None once every round has closed."""
    season = int(repository_map(root)["active_season"])
    paths = SeasonPaths(season, root)
    first = 18 + (1 if season >= 2021 else 0)
    weeks = [(g["week"], paths.receipts) for g in club_games(root)]
    weeks += [(w, paths.postseason_receipts) for w in range(first, first + 4)]
    return next((w for w, folder in weeks if not any(folder.glob("week_%02d_*.json" % w))), None)


class CareerViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.week = first_unplayed_week(ROOT)
        if cls.week is None:
            raise unittest.SkipTest("every game of the active season has closed; the view tests need an "
                                    "unplayed week")
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup)).resolve()
        # Untracked paused-game records: a live pause would refuse every write.
        for record in cls.root.glob("career/**/paused_game.json"):
            record.unlink()
        cls.season = int(repository_map(cls.root)["active_season"])
        cls.paths = SeasonPaths(cls.season, cls.root)
        cls.readme = cls.paths.career / "README.md"
        cls.master = master_date(cls.root)

    def setUp(self):
        self.job = current_job.load(self.root)
        self.queue = decision_queue.load(self.root)
        self.holder = self.job["holder"]

    def write(self, path, text):
        path = self.root / path
        before = path.read_bytes() if path.exists() else None
        created = [p for p in reversed(path.parents) if p.is_relative_to(self.root) and not p.exists()]
        self.addCleanup(lambda: [p.rmdir() for p in reversed(created) if p.exists() and not any(p.iterdir())])
        self.addCleanup(lambda: path.write_bytes(before) if before is not None else path.unlink(missing_ok=True))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def with_items(self, *items):
        queue = json.loads(json.dumps(self.queue))
        queue["items"] += list(items)
        self.write(decision_queue.QUEUE, json.dumps(queue, indent=1))

    def with_job(self, change):
        job = json.loads(json.dumps(self.job))
        change(current_job.appointment(job))
        self.write(current_job.JOB, json.dumps(job, indent=1))

    def item(self, **changes):
        """An OPEN weekly plan item for the first unplayed week, owned by the holder."""
        item = {"id": "test-view-plan", "title": "Test plan for the views", "class": "weekly_game_plan",
                "owner": self.holder, "authority_rows": ["9"], "question": "A test question.",
                "raised": {"date": self.master.isoformat(), "by": "workflow"}, "status": "OPEN", "waits_on": [],
                "deadline": None, "blocks": [event("week_inputs", self.season, self.week)], "fallback": None,
                "can_continue": None, "record": {"path": self.readme.relative_to(self.root).as_posix()},
                "sources": [], "resolution": None}
        item.update(changes)
        return item

    def rendered(self, path):
        return views.render(self.root)[self.root / path]

    def desk(self):
        return self.rendered(self.readme.relative_to(self.root))

    def section(self, heading):
        return self.desk().split("## %s\n" % heading, 1)[1].split("\n## ", 1)[0]

    def assertHas(self, text, errors):
        self.assertTrue(any(text in e for e in errors), "%r not in %r" % (text, errors))

    def test_write_then_check_is_clean(self):
        views.write(self.root)
        self.assertEqual(views.check(self.root), [])

    def test_repository_views_are_current(self):
        self.assertEqual(views.check(ROOT), [])

    def test_new_open_item_makes_state_and_desk_stale(self):
        self.with_items(self.item())
        errors = views.check(self.root)
        self.assertHas("Stale career view: %s (decision-queue, manifest)" % STATE, errors)
        self.assertHas("Stale career view: %s (desk)" % self.readme.relative_to(self.root).as_posix(), errors)
        self.assertIn("Test plan for the views", self.desk())

    def test_delegation_change_makes_the_staff_page_stale_not_the_register(self):
        def change(current):
            offense = next(r for r in current["delegation"]["play_calling"]
                           if r["phase"] == "offense" and r["to"] is None)
            offense["stone_retains"] = "A changed retained role"
        register = self.paths.staff_register.relative_to(self.root).as_posix()
        before = (self.root / register).read_bytes()
        self.with_job(change)
        page = self.paths.staff_page.relative_to(self.root).as_posix()
        self.assertHas("Coach page stale or hand-edited: %s" % page, render_coach_pages.check(self.root))
        self.assertIn("Offense: a changed retained role.", render_coach_pages.build(self.root)[page])
        self.assertNotIn(self.root / register, views.render(self.root))
        views.write(self.root)
        self.assertEqual((self.root / register).read_bytes(), before)

    def test_no_readme_carries_a_desk_block(self):
        other = next(p for p in sorted(self.root.glob("career/*/README.md")) if p != self.readme)
        rel = other.relative_to(self.root).as_posix()
        self.write(rel, other.read_text(encoding="utf-8")
                   + "\n<!-- desk:begin role=head_coach season=1 -->\n## A stray desk\n<!-- desk:end -->\n")
        errors = views.check(self.root)
        self.assertHas("Career view desk block found: %s has 1; the desk is the whole of %s"
                       % (rel, self.readme.relative_to(self.root).as_posix()), errors)
        self.assertHas("Stale career view: %s (desk-block)" % rel, errors)
        views.write(self.root)
        self.assertNotIn("desk:begin", (self.root / rel).read_text(encoding="utf-8"))
        self.assertEqual(views.check(self.root), [])

    def test_write_rebuilds_the_whole_desk(self):
        rel = self.readme.relative_to(self.root).as_posix()
        text = self.readme.read_text(encoding="utf-8")
        self.write(rel, text + "\nA line added by hand.\n")
        self.assertHas("Stale career view: %s (desk)" % rel, views.check(self.root))
        views.write(self.root)
        self.assertEqual(self.readme.read_text(encoding="utf-8"), text)
        self.assertNotIn("<!--", text)

    def test_desk_is_a_clean_page_in_its_fixed_order(self):
        desk = self.desk()
        self.assertEqual(page_errors(self.readme.relative_to(self.root).as_posix(), desk, (), self.root), [])
        order = ["## Waiting on you", "## Next event", "## Coming up", "## With others", "## Standing instructions",
                 "## Who calls what", "## Records", "## Season folders"]
        self.assertEqual(sorted(order, key=desk.index), order)
        self.assertLess(desk.index("[Coach page]("), desk.index("## Waiting on you"))
        for word in ("frozen", "inputs", "Holds", "gate", "row ", "Document "):
            self.assertNotIn(word, self.section("Waiting on you") + self.section("Coming up"))
        self.assertNotIn(".json", desk)

    def test_desk_links_are_labelled_and_never_coded(self):
        desk = self.desk()
        labels = re.findall(r"\[([^\]]+)\]\(([^)]*)\)", desk)
        self.assertTrue(labels)
        self.assertNotIn("Record", [label for label, _ in labels if not _.endswith("Record.md")])
        for label, dest in labels:
            anchor = urlsplit(dest).fragment
            self.assertEqual(render_coach_pages.football_anchor(anchor, self.master), anchor or None, dest)
        if any(i.get("subject") == "play_calling" for i in current_job.instructions(self.job)):
            line = next(l for l in self.section("Standing instructions").splitlines() if "Calling arrangement" in l)
            staff = self.paths.staff_page.relative_to(self.paths.career).as_posix()
            self.assertIn("](%s#%s)" % (staff, views.CALLING_SECTION), line)
            self.assertIn(views.CALLING_SECTION, anchors(without_code(self.paths.staff_page.read_text(encoding="utf-8"))))

    def test_document_5_speaks_of_the_head_coach_and_the_desk_to_him(self):
        item = next((i for i in current_job.instructions(self.job) if i.get("subject") == "play_calling"), None)
        if item is None:
            self.skipTest("no calling arrangement in force")
        holder = views.short(SimpleNamespace(job=self.job), self.holder)
        # The record words the instruction about him, and Document 5 shows it as recorded.
        self.assertTrue(item["summary"].startswith(holder + " "), item["summary"])
        row = next(l for l in self.rendered(STATE).splitlines() if l.startswith("| Standing instructions |"))
        self.assertIn(item["summary"], row)
        self.assertNotRegex(row, r"\b[Yy]ou(?:r)?\b")
        # Only the desk speaks to him.
        line = next(l for l in self.section("Standing instructions").splitlines() if "Calling arrangement" in l)
        self.assertIn(":** You ", line)
        self.assertNotIn(item["summary"], line)

        def change(current):
            rule = next(i for i in current["standing_instructions"] if i["id"] == item["id"])
            rule["summary"] = "%s watches, decides or takes over any phase; he has his say until he changes it" % holder
        self.with_job(change)
        line = next(l for l in self.section("Standing instructions").splitlines() if "Calling arrangement" in l)
        self.assertIn(":** You watch, decide or take over any phase; you have your say until you change it.", line)
        row = next(l for l in self.rendered(STATE).splitlines() if l.startswith("| Standing instructions |"))
        self.assertIn("%s watches, decides or takes over any phase; he has his say" % holder, row)

    def test_waiting_items_name_the_game_they_are_due_for(self):
        self.with_items(self.item(question="The test plan: the opening script for the week."))
        game = next(g for g in club_games(self.root) if g["week"] == self.week)
        line = next(l for l in self.section("Waiting on you").splitlines() if "Test plan for the views" in l)
        self.assertIn("To settle: the opening script for the week.", line)
        self.assertIn("Due before kickoff, %s, %s" % (game["weekday"], views.day(game["date"], False)), line)

    def test_missing_marker_is_reported(self):
        state = (self.root / STATE).read_text(encoding="utf-8")
        self.write(STATE, re.sub(r"<!-- decision-queue:begin -->.*?<!-- decision-queue:end -->", "", state, flags=re.S))
        self.assertHas("Career view markers missing or duplicated: %s decision-queue" % STATE, views.check(self.root))
        with self.assertRaisesRegex(ValueError, "markers missing"):
            views.write(self.root)

    def test_banned_word_in_a_title_stops_the_render(self):
        self.with_items(self.item(title="Engine check before the game"))
        message = r"Banned word 'Engine' in desk text from decision_queue\.test-view-plan\.title"
        with self.assertRaisesRegex(ValueError, message):
            views.render(self.root)
        self.assertHas("Career views cannot render: Banned word 'Engine'", views.check(self.root))

    def test_next_game_follows_the_clock(self):
        games = club_games(self.root)
        played, following = games[1], games[2]
        when = date.fromisoformat(played["date"])
        state = (self.root / STATE).read_text(encoding="utf-8")
        for clock, expected in (("after the Week %d game against a test opponent" % played["week"], following),
                                ("game day before kickoff", played)):
            with self.subTest(clock=clock):
                cell = "| Master date/time | %s %d, %d, %s |" % (when.strftime("%B"), when.day, when.year, clock)
                self.write(STATE, re.sub(r"^\| Master date/time \| .*$", lambda _: cell, state, count=1, flags=re.M))
                self.assertIn("**Next game:** Week %d," % expected["week"], self.desk())

    def test_a_pause_refuses_write_but_not_check(self):
        records = [self.paths.paused_game(self.week), self.paths.paused_game(1, preseason=True)]
        for record in records:
            with self.subTest(record=record.relative_to(self.root).as_posix()):
                self.write(record.relative_to(self.root), json.dumps({"status": "paused"}))
                with self.assertRaisesRegex(views.Paused, "A Jacksonville game is paused"):
                    views.write(self.root)
                self.assertEqual(views.check(self.root), [])
                self.write(record.relative_to(self.root), json.dumps({"status": "closed"}))
                self.assertEqual(views.write(self.root), [])

    def test_other_clubs_receipts_never_change_the_views(self):
        before = views.render(self.root)
        fake = self.paths.receipts / ("week_%02d_fake-at-test.json" % self.week)
        self.write(fake.relative_to(self.root), json.dumps({"week": self.week, "home": "A", "away": "B"}))
        self.assertEqual(views.render(self.root), before)

    def test_every_rendered_link_resolves(self):
        texts = views.render(self.root)
        blocks = re.compile(r"<!-- ([a-z-]+):begin[^>]*-->.*?<!-- \1:end -->", re.S)
        checked = 0
        for path, text in texts.items():
            parts = [text] if path == self.readme else [b[0] for b in blocks.finditer(text)]
            for block in parts:
                for dest in LINK.findall(block):
                    parts = urlsplit(dest)
                    target = (path.parent / unquote(parts.path)).resolve()
                    self.assertTrue(target.is_file(), "%s: %s" % (path.relative_to(self.root), dest))
                    if parts.fragment:
                        self.assertIn(parts.fragment, anchors(without_code(target.read_text(encoding="utf-8"))), dest)
                    checked += 1
        self.assertGreater(checked, 40)

    def test_unbuilt_role_is_reported_not_raised(self):
        self.with_job(lambda current: current.update(role="coordinator"))
        with self.assertRaisesRegex(NotImplementedError, "desk for role coordinator is defined"):
            views.render(self.root)
        errors = views.check(self.root)
        self.assertHas("Career views cannot render: desk for role coordinator is defined (ROLE_SECTIONS) but not built",
                       errors)

    def test_desk_says_which_game_decisions_are_not_live_calls(self):
        decisions = current_job.appointment(self.job)["delegation"]["game_management"]["decisions"]
        alias = (self.job["parties"][self.holder].get("aliases") or [self.job["parties"][self.holder]["name"]])[0]
        line = next(l for l in self.rendered(STATE).splitlines() if "Not %s's live calls: " % alias in l)
        segment = line.split("Not %s's live calls: " % alias, 1)[1]
        for decision in decisions:
            label = views.DECISION_LABEL[decision["id"]]
            if decision["mechanism"] in ("not_live", "not_modelled"):
                self.assertIn(label + " (", segment)
            else:
                self.assertNotIn(label + " (", segment)

    def test_postseason_rounds_are_named_without_a_numeral(self):
        first = 18 + (1 if self.season >= 2021 else 0)
        rounds = ("Wild Card", "Divisional", "Conference Championship", "Super Bowl")
        self.with_items(*[self.item(id="test-round-%d" % n, blocks=[event("week_inputs", self.season, first + n)])
                          for n in range(4)])
        block = re.search(r"<!-- decision-queue:begin -->.*?<!-- decision-queue:end -->", self.rendered(STATE), re.S)[0]
        for name in rounds:
            self.assertIn("| the %s game |" % name, block)
        self.assertEqual(self.section("Waiting on you").count("Test plan for the views"), 4)
        self.assertIsNone(re.search(r"Super Bowl [IVXLC]+\b", block + self.desk()))

    def test_manifest_binds_both_files(self):
        self.with_items(self.item())
        state = self.rendered(STATE)
        for label, path, _ in views.MANIFEST_ROWS:
            blob = views.git_blob((self.root / path).read_bytes())
            self.assertIn("| %s | `%s` |" % (label, blob), state)
        manifest = state.split("## Effective source-version manifest", 1)[1].split("\n## ", 1)[0]
        rows = [l.split(" | ")[0] for l in manifest.splitlines() if l.startswith("| ")]
        at = rows.index("| Document 4")
        self.assertEqual(rows[at + 1:at + 3], ["| Current job record", "| Decision queue"])

    def test_partly_decided_rows_name_their_final_authority(self):
        row = next(l for l in self.rendered(STATE).splitlines() if l.startswith("| Final authority |"))
        current = current_job.appointment(self.job)
        for domain in current["authority"]["domains"]:
            if domain["stone_action"] == "decides_part" and domain["final"] != [self.holder]:
                parties = views.join(current_job.party_name(self.job, p) for p in domain["final"])
                clause = next(c for c in row.split("; ") if "row %s (" % domain["row"] in c)
                self.assertIn(parties.lower(), clause.lower())
                self.assertIn("decides %s)" % domain["scope"], clause)

    def test_desk_links_no_uncommunicated_review(self):
        self.assertNotIn(Path(STONE_REVIEWS).name, self.desk())

    def test_classes_block_lists_every_class(self):
        text = self.rendered("docs/career_layer.md")
        for name in decision_queue.CLASSES:
            self.assertIn("| `%s` |" % name, text)

    # ---- rebuild step 5, A6: every pending answer, whatever the phase
    def event_item(self, ident, due, **changes):
        """An OPEN event item of the holder (a trade answer), due at ``due`` (a datetime)."""
        from runtime import open_events
        event_id = "%s-%s" % (self.master.isoformat(), ident)
        item = self.item(id=event_id, title="Test trade call")
        item.update({"class": "personnel_recommendation", "authority_rows": ["3"], "event": event_id,
                     "question": "Your football answer on a test trade call.",
                     "deadline": {"date": due.date().isoformat(), "at": open_events.iso(due),
                                  "label": "The other club's deadline"},
                     "blocks": [event("event_resolution", self.season, event=event_id)]})
        item.update(changes)
        return item

    def test_an_answer_due_on_tuesday_is_not_due_before_kickoff(self):
        from runtime import open_events
        game = next(g for g in club_games(self.root) if g["week"] == self.week)
        due = open_events.et(date.fromisoformat(game["date"]), 16) + timedelta(days=2)
        self.with_items(self.event_item("test-desk-call", due))
        line = next(l for l in self.section("Waiting on you").splitlines() if "Test trade call" in l)
        self.assertIn("Due %s." % open_events.at_text(due), line)
        self.assertNotIn("before kickoff", line)
        self.assertNotIn("Overdue", line)
        self.assertEqual(page_errors(self.readme.relative_to(self.root).as_posix(), self.desk(), (), self.root), [])

    def test_an_overdue_item_says_so(self):
        from runtime import open_events
        due = open_events.master_at(self.root) - timedelta(hours=1)
        self.with_items(self.event_item("test-desk-overdue", due))
        line = next(l for l in self.section("Waiting on you").splitlines() if "Test trade call" in l)
        self.assertIn("Overdue since %s." % open_events.at_text(due), line)
        # Overdue is said, never settled: the item is still open.
        self.assertEqual(next(i for i in decision_queue.load(self.root)["items"] if i["id"].endswith("overdue"))["status"],
                         "OPEN")

    def test_a_bye_item_is_listed_with_its_pages(self):
        from runtime import decisions
        played = {g["week"] for g in club_games(self.root)}
        bye = next((w for w in range(self.week, 18) if w not in played), None)
        if bye is None:
            self.skipTest("no bye remains")
        pages = decisions.bye_pages(self.season, bye, self.root)
        self.write(pages.adjustments.relative_to(self.root), "# Week %d bye My Adjustments\n" % bye)
        self.write(pages.review.relative_to(self.root), "# Week %d Bye Week Review\n" % bye)
        self.with_items(self.item(id="test-desk-bye", title="Test bye adjustments", **{
            "class": "bye_adjustments", "authority_rows": ["9"], "question": "Your adjustments for the bye.",
            "blocks": [event("bye_close", self.season, bye)],
            "record": {"path": pages.adjustments.relative_to(self.root).as_posix()}}))
        line = next(l for l in self.section("Waiting on you").splitlines() if "Test bye adjustments" in l)
        self.assertIn("[My Adjustments](", line)
        self.assertIn("[Bye Week Review](", line)
        self.assertNotIn("before kickoff", line)

    def test_windows_are_coming_up_never_waiting(self):
        from runtime import deadlines, open_events
        windows = deadlines.coming_up(self.season, open_events.master_at(self.root), self.root)
        if not windows:
            self.skipTest("no window is coming up at the clock")
        waiting, coming = self.section("Waiting on you"), self.section("Coming up")
        for window in windows:
            self.assertNotIn(window["title"], waiting)
        # A window the schedule does not name is added on its day; one it names is not shown twice.
        state = (self.root / STATE).read_text(encoding="utf-8")
        surnames = {w["title"].split("'")[0].split()[-1] for w in windows if not w["key"].endswith("deadline")}
        kept = "\n".join(l for l in state.splitlines()
                         if not (l.startswith("| ") and any(n in l for n in surnames) and "Scheduled" in l))
        self.write(STATE, kept)
        coming = self.section("Coming up")
        for window in windows:
            if not window["key"].endswith("deadline"):
                self.assertEqual(coming.count(window["title"]), 1, coming)
        self.assertEqual(page_errors(self.readme.relative_to(self.root).as_posix(), self.desk(), (), self.root), [])


class DeskEventTests(unittest.TestCase):
    """An event's item links its My Responses block and its brief; a notice that needs no answer is
    never waiting. Events are test data in a throwaway copy (support_events)."""

    def setUp(self):
        import shutil
        import tempfile
        from release_staging import IGNORED
        import support_events as se
        self.se = se
        tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
        for record in self.root.glob("career/**/paused_game.json"):
            record.unlink()
        self.game = se.open_game(self.root)
        if self.game is None:
            self.skipTest("every regular-season game has closed")
        self.tuesday = se.tuesday_before(self.game)
        se.midweek(self.root, self.tuesday, 10, 30, int(self.game["week"]))
        self.season = se.SEASON

    def test_an_event_item_links_its_block_and_its_brief(self):
        import contextlib
        import io
        from runtime import open_events
        from scripts import render_game_week
        se = self.se
        due = open_events.et(self.tuesday + timedelta(days=1), 16)
        record = se.trade_call(self.root, "test-desk-event", open_events.et(self.tuesday, 9), due)
        open_events.raise_event(record, self.root)
        news_source = se.source_page(self.root, "head_coach_change")
        news = {"schema": open_events.SCHEMA, "id": "%s-test-desk-news" % self.tuesday.isoformat(),
                "kind": "head_coach_change", "season": self.season, "subject": "Other Test Club",
                "raised": {"at": open_events.iso(open_events.et(self.tuesday, 9, 30)), "by": "communications_staff",
                           "source": {"path": news_source}},
                "known_to": ["stone"], "authority": {"rows": ["1"], "decides": open_events.OTHER_CLUB},
                "stone_part": "none", "summary": {"text": "A test notice of another club's coaching change.",
                                                  "author": "Team communications staff",
                                                  "date": self.tuesday.isoformat()},
                "staff_position": None, "consequence": None, "facts": [], "options": [], "deadline": None,
                "state": "open", "process": [], "queue_item": None, "response": None, "resolution": None}
        open_events.raise_event(news, self.root)
        with contextlib.redirect_stdout(io.StringIO()):
            render_game_week.write(self.root)
        desk = views.render(self.root)[SeasonPaths(self.season, self.root).desk]
        waiting = desk.split("## Waiting on you\n", 1)[1].split("\n## ", 1)[0]
        line = next(l for l in waiting.splitlines() if "Trade call from Test Club" in l)
        self.assertIn("Due %s." % open_events.at_text(due), line)
        self.assertNotIn("before kickoff", line)
        self.assertIn("[My Responses](Regular_Season/Games/Week_%02d/My_Responses.md#trade-call-from-test-club)"
                      % int(self.game["week"]), line)
        self.assertIn("[Game Week Briefing](Regular_Season/Games/Week_%02d/Game_Week_Briefing.md)"
                      % int(self.game["week"]), line)
        # The news needs no answer: it is never waiting on him.
        self.assertNotIn("Other Test Club", waiting)
        self.assertNotIn(record["id"], desk)
        self.assertEqual(page_errors(SeasonPaths(self.season, self.root).desk.relative_to(self.root).as_posix(), desk,
                                     (), self.root), [])


if __name__ == "__main__":
    unittest.main()
