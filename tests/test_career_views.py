"""The career views rendered from the job record and the decision queue.

Mutations run on one throwaway copy of the checkout, with any paused-game
record removed so a live pause cannot decide a test; each test restores the
files it changed. Weeks come from the fixtures and receipts (the first
unplayed Jacksonville week, then the first unplayed postseason round) and
dates from the master date, so the tests hold at any later clock. The desk
is the whole of the active season's README, a clean page.
"""
from datetime import date
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
        self.assertNotIn("alex_stone_performance_review", self.desk())

    def test_classes_block_lists_every_class(self):
        text = self.rendered("docs/career_layer.md")
        for name in decision_queue.CLASSES:
            self.assertIn("| `%s` |" % name, text)


if __name__ == "__main__":
    unittest.main()
