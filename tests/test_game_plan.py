"""Stone's Game Plan page, version 2 (runtime/game_plan.py), its check and its apply.

The proof (docs/game_week_v2.md section 4): Week 5's actual choices, written as
a version 2 Game Plan (tests/fixtures/game_plan_v2_week_05.md: carrying Week 4
where Week 5 did and naming the rest), compile to a call sheet byte-identical
to Week 5's frozen call_sheet.json, and applied in a temporary copy give the
same sheet and the same inactives. Week 5's sheet was transcribed from a
packet, so it holds author text and packet citations a version 2 page keeps
out of the sheet or derives itself: each call's "what I am looking at", the
situation prose and the notes, and the defensive record's packet, notes,
rush-rule citation, practiced menu and row ids and citations. Those come back
from the frozen sheet as its frame (frame_from_sheet), as the event and the
provenance did in step 4; a second test proves that every executable byte
(each call's name, form, tags, opening places and situations, the decisions,
the defensive caller, rush rule and each row's use, situation and call) comes
from the page alone.

Then: rewording every reason compiles to the same bytes (paraphrase
invariance); silence approves nothing; No change, None and a blank differ;
the compiler asks rather than guesses; any call of the active book may be
named for any situation, practiced or not (the user's ruling of October 20,
2026), and nothing waits on a practice record; and the step-4 guards hold
under the new page (the playbook lock, the refusals while paused, built or played, the
page digest tie, roles by position group, the standing inactives rule, the
standing decision rules and the event of the apply).

The check and apply tests work out the open week from the stored facts (the
next Jacksonville game not yet closed), never from a date.
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import game_plan  # noqa: E402
from runtime import roster as roster_record  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.rules import RULES  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

SEASON = 2014
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "game_plan_v2_week_05.md"


def week_inactives(week, root=ROOT):
    """A week's inactives as set, from the week's inactives record (the chart holds only the latest)."""
    return json.loads(week_pages(SEASON, week, root).inactives.read_text(encoding="utf-8"))["players"]


WEEK5_INACTIVES = week_inactives(5)


def copy_repo(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    return root


def week5():
    path = SeasonPaths(SEASON, ROOT).call_sheet(5)
    return path.read_bytes(), json.loads(path.read_text(encoding="utf-8"))


def earlier(week, root=ROOT):
    paths = SeasonPaths(SEASON, root)
    return {w: json.loads(paths.call_sheet(w).read_text(encoding="utf-8")) for w in range(1, week)
            if paths.call_sheet(w).is_file()}


def standing_week5():
    """The standing two-point and kickoff rules, as their instructions point at Week 5's frozen blocks."""
    from runtime import current_job
    out = {}
    for item in current_job.instructions(current_job.load(ROOT)):
        record = item.get("record") or {}
        if item.get("subject") in ("two_point", "kickoff") and str(record.get("path", "")).endswith(".json"):
            data = json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
            for part in [p for p in record["pointer"].split("/") if p]:
                data = data[part]
            out[item["subject"]] = data
    return out


def compile_week5(text, frame=None):
    _, sheet = week5()
    choices, problems = game_plan.parse(text)
    built, source, found = game_plan.compile_sheet(choices, frame or game_plan.frame_from_sheet(sheet), earlier(5),
                                                   standing_week5(), {"defense": "Alex Stone"})
    return choices, problems + found, built, source


def executable(sheet):
    """The football choices of a sheet: every call without its 'what I am looking at' text, the
    decisions, and the defensive caller, rush rule and each row's use, situation and call."""
    ds = sheet.get("defensive_call_sheet") or {}
    return {"calls": [{k: v for k, v in c.items() if k != "what_stone_is_looking_at"}
                      for c in sheet["offensive_call_sheet"]],
            "decisions": sheet.get("decisions"),
            "defense": {"caller": ds.get("caller"), "rush": (ds.get("rush_rule") or {}).get("rule"),
                        "rows": [{k: r[k] for k in ("kind", "menu", "call") if k in r} for r in ds.get("rows") or ()]}}


def reworded(text):
    """The page with every reason, intent line and stop condition reworded (the choices unchanged)."""
    out = []
    for line in text.splitlines():
        m = game_plan.LABELLED.match(line.strip())
        if m:
            key = game_plan._label_key(current_section(out), m[1].strip())
            kind = game_plan.FIELD[key][2] if key else None
            if kind in ("intent", "situational") and m[2].strip() not in ("No change", "None"):
                line = "**%s:** In other words, and at greater length than before: %s Said again." % (
                    m[1], m[2].strip().rstrip("  "))
        elif line.startswith("| ") and not set(line) <= set("|-: "):
            cells = game_plan.cells(line)
            head = header_of(out)
            if head in (game_plan.CALL_COLUMNS, game_plan.RESPONSE_COLUMNS, game_plan.PRACTICE_COLUMNS) and \
                    cells != list(head):
                keep = 2 if head != game_plan.PRACTICE_COLUMNS else (1 if cells[0].lower().startswith("install") else 0)
                cells = cells[:keep] + ["Put differently, %s, which is the same idea" % c.lower() if c else
                                        "A reason added" for c in cells[keep:]]
                line = "| " + " | ".join(cells) + " |"
        out.append(line)
    return "\n".join(out) + "\n"


def current_section(lines):
    for line in reversed(lines):
        if line.startswith("## "):
            name = line[3:].strip()
            return game_plan.HEADINGS.index(name) + 1 if name in game_plan.HEADINGS else -1
    return 0


def header_of(lines):
    for line in reversed(lines):
        if not line.startswith("|"):
            return None
        cells = tuple(game_plan.cells(line))
        if cells in (game_plan.CALL_COLUMNS, game_plan.RESPONSE_COLUMNS, game_plan.PRACTICE_COLUMNS):
            return cells
    return None


class ProofTests(unittest.TestCase):
    """Week 5's actual choices as a version 2 Game Plan compile to its frozen call sheet."""

    def test_the_week_5_inactives_record_is_the_list_set(self):
        self.assertEqual(len(WEEK5_INACTIVES), 7)
        report = SeasonPaths(SEASON, ROOT).game_report(5).read_text(encoding="utf-8")
        for name in WEEK5_INACTIVES:
            self.assertIn(name.split()[-1], report)

    def test_week_5_compiles_byte_identical(self):
        raw, _ = week5()
        choices, problems, built, _ = compile_week5(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(problems, [])
        self.assertEqual(choices["unanswered"], [])
        self.assertEqual(game_plan.sheet_bytes(built), raw)
        self.assertEqual(choices["inactives"]["players"], WEEK5_INACTIVES)

    def test_a_page_with_the_old_opening_label_reads_the_same(self):
        # A page written before October 20, 2026 names its opening list "Opening calls, in order".
        text = FIXTURE.read_text(encoding="utf-8")
        old = text.replace("**Opening ideas:**", "**Opening calls, in order:**")
        self.assertNotEqual(old, text)
        raw, _ = week5()
        for page in (text, old):
            _, problems, built, _ = compile_week5(page)
            self.assertEqual(problems, [])
            self.assertEqual(game_plan.sheet_bytes(built), raw)

    def test_every_executable_byte_comes_from_the_page(self):
        _, sheet = week5()
        page = game_plan.page_frame("tests/fixtures/game_plan_v2_week_05.md", "event", "frozen", "provenance",
                                    sheet["team"], sheet["defensive_call_sheet"]["book"], 5)
        _, problems, built, _ = compile_week5(FIXTURE.read_text(encoding="utf-8"), page)
        self.assertEqual(problems, [])
        self.assertEqual(executable(built), executable(sheet))
        # A version 2 sheet carries no author text: no situation prose, notes or "what I am looking at".
        self.assertNotIn("menus", built)
        self.assertNotIn("notes", built)
        self.assertFalse(any("what_stone_is_looking_at" in c for c in built["offensive_call_sheet"]))

    def test_the_frame_holds_no_football_choice(self):
        _, sheet = week5()
        frame = game_plan.frame_from_sheet(sheet)
        self.assertEqual(set(frame["top"]), set(game_plan.TOP_KEYS))
        self.assertEqual(set(frame["record_text"]), {"menus", "notes"})
        self.assertTrue(all(isinstance(v, str) for v in frame["looking"].values()))
        self.assertEqual(set(frame["defense"]), {"head", "notes", "rush", "practiced", "rows"})
        self.assertEqual(set(frame["defense"]["head"]), {"schema_version", "team", "book", "packet"})
        for row in frame["defense"]["rows"]:
            self.assertEqual(set(row), {"id", "source"})
        self.assertEqual(set(frame["defense"]["rush"]), {"path", "line", "text"})

    def test_applied_in_a_copy_the_week_5_records_are_identical(self):
        from scripts.apply_game_plan import apply_records
        from scripts.check_game_plan import Plan
        root = copy_repo(self)
        raw, sheet = week5()
        pages = week_pages(SEASON, 5, root)
        pages.plan.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
        plan = Plan(root, SEASON, 5)
        self.assertEqual(plan.problems, [])
        built, _, problems = plan.compiled(game_plan.frame_from_sheet(sheet))
        self.assertEqual(problems, [])
        apply_records(plan, built, plan.inactives(), resolve_queue=False)
        self.assertEqual(SeasonPaths(SEASON, root).call_sheet(5).read_bytes(), raw)
        chart = json.loads(SeasonPaths(SEASON, root).depth_chart.read_text(encoding="utf-8"))
        self.assertEqual((chart["game_day_inactives"]["week"], chart["game_day_inactives"]["players"]),
                         (5, WEEK5_INACTIVES))
        record = game_plan.applied_record(pages.applied)
        # The source map ties every emitted call to a page line or a carried frozen call, reversibly.
        text = pages.plan.read_text(encoding="utf-8").splitlines()
        for call in sheet["offensive_call_sheet"]:
            sources = record["source_map"]["calls"][call["name"]]
            self.assertTrue(sources)
            for source in sources:
                if "page" in source:
                    self.assertIn(source["text"], text[source["page"] - 1])
                elif "carried" in source:
                    week, index = source["carried"]["week"], source["carried"]["call"]
                    carried = json.loads(SeasonPaths(SEASON, root).call_sheet(week).read_text(encoding="utf-8"))
                    self.assertEqual(carried["offensive_call_sheet"][index]["name"], call["name"])
        # His reasons are kept as intent, with their lines and the day they were known.
        self.assertTrue(record["intent"]["calls"])
        self.assertEqual(record["intent"]["known"], plan.master.isoformat())


class ParaphraseTests(unittest.TestCase):
    """Rewording a coach's explanation without changing his choices compiles to the same bytes."""

    def test_reworded_reasons_compile_to_the_same_bytes(self):
        text = FIXTURE.read_text(encoding="utf-8")
        other = reworded(text)
        self.assertNotEqual(other, text)
        self.assertGreater(len(other), len(text))
        _, problems, first, _ = compile_week5(text)
        _, problems2, second, _ = compile_week5(other)
        self.assertEqual(problems + problems2, [])
        self.assertEqual(game_plan.sheet_bytes(first), game_plan.sheet_bytes(second))
        # And as a version 2 page writes it, citing its own lines.
        _, sheet = week5()
        page = game_plan.page_frame("tests/fixtures/game_plan_v2_week_05.md", "event", "frozen", "provenance",
                                    sheet["team"], sheet["defensive_call_sheet"]["book"], 5)
        a = compile_week5(text, page)[2]
        b = compile_week5(other, page)[2]
        self.assertEqual(game_plan.sheet_bytes(a), game_plan.sheet_bytes(b))

    def test_a_changed_choice_changes_the_sheet(self):
        text = FIXTURE.read_text(encoding="utf-8").replace(
            "| 11 Doubles, Inside Zone Right | backed up |", "| 11 Doubles, Inside Zone Right | backed up, goal line |")
        _, problems, built, _ = compile_week5(text)
        self.assertEqual(problems, [])
        raw, _ = week5()
        self.assertNotEqual(game_plan.sheet_bytes(built), raw)


class CompilerTests(unittest.TestCase):
    """The compiler's answers to the page, from the fixture with one line changed at a time."""

    def page(self, old, new):
        text = FIXTURE.read_text(encoding="utf-8")
        self.assertIn(old, text)
        return text.replace(old, new)

    def test_no_change_none_and_blank_differ(self):
        from scripts.check_game_plan import opening_order
        line = next(l for l in FIXTURE.read_text(encoding="utf-8").splitlines() if l.startswith("**Opening ideas"))
        # No change carries Week 4's opening calls; the call this week's page takes off (12 Trey, Y-Cross,
        # HALF, among the calls not available) leaves it, and the calls after it move up in order.
        _, problems, carried, source = compile_week5(self.page(line, "**Opening ideas:** No change  "))
        self.assertEqual(problems, [])
        week4 = earlier(5)[4]["offensive_call_sheet"]
        self.assertEqual(opening_order(carried), [n for n in opening_order({"offensive_call_sheet": week4})
                                                  if n != "12 Trey, Y-Cross, HALF"])
        self.assertEqual(source["opening_dropped"], ["12 Trey, Y-Cross, HALF"])
        slots = sorted(s for c in carried["offensive_call_sheet"]
                       for s in ([c["opener"]] if "opener" in c else []) + c.get("opener_returns", []))
        self.assertEqual(slots, list(range(1, len(slots) + 1)))
        text = self.page(line, "**Opening ideas:** No change  ").replace(
            "**Calls not available this week:** 12 Trey, Y-Cross, HALF (no line of the plan names it)",
            "**Calls not available this week:** None")
        _, problems, carried, _ = compile_week5(text)
        self.assertEqual(problems, [])
        week4 = earlier(5)[4]["offensive_call_sheet"]
        self.assertEqual({c["name"]: c.get("opener") for c in carried["offensive_call_sheet"] if c.get("opener")},
                         {c["name"]: c["opener"] for c in week4 if c.get("opener")})
        choices, problems, none, _ = compile_week5(self.page(line, "**Opening ideas:** None  "))
        self.assertFalse(any("opener" in c for c in none["offensive_call_sheet"]))
        choices, problems, blank, _ = compile_week5(self.page(line, "**Opening ideas:**  "))
        self.assertIn("opening", choices["unanswered"])

    def asked(self, problems, name):
        return next(p for p in problems if p.startswith("Offense, Primary calls: %s is not a call of an earlier "
                                                         "Jacksonville sheet as written; did you mean " % name))

    def test_a_short_name_is_asked_never_resolved(self):
        # Two calls hold its words: both are named.
        text = self.page("| 12 Trey, Y-Cross, SOLID (Kelce receiving Y) |", "| Y-Cross (Kelce receiving Y) |")
        _, problems, built, _ = compile_week5(text)
        self.assertIsNone(built)
        asked = self.asked(problems, "Y-Cross")
        for name in ("12 Trey, Y-Cross, SOLID", "12 Trey, Y-Cross, HALF", "11 Trey, Y-Cross, SOLID"):
            self.assertIn(name, asked.split("did you mean ", 1)[1].split("?", 1)[0])
        # One call holds them: still asked, never resolved to it.
        text = self.page("| 11 Bunch, Mesh, HALF (Kelce receiving Y) |", "| Mesh (Kelce receiving Y) |")
        _, problems, built, _ = compile_week5(text)
        self.assertIsNone(built)
        self.assertIn("did you mean 11 Bunch, Mesh, HALF?", self.asked(problems, "Mesh"))
        # A name that is itself a call of the book, held by a longer carried call that adds a route or a
        # protection: asked, never filled in with the bubble or the post-cross.
        text = self.page("| 11 Trips, Inside Zone + Bubble | third and short |", "| 11 Trips, Inside Zone | third and short |")
        _, problems, built, _ = compile_week5(text)
        self.assertIsNone(built)
        self.assertIn("did you mean 11 Trips, Inside Zone + Bubble?", self.asked(problems, "11 Trips, Inside Zone"))
        self.assertIn("or, for the call these words name, New call: 11 Trips, Inside Zone",
                      self.asked(problems, "11 Trips, Inside Zone"))
        power = self.page("| 11 Trips, Inside Zone + Bubble | third and short |",
                          "| 12 Ace, Power Pass | normal downs | x | y |\n| 11 Trips, Inside Zone + Bubble | third and short |")
        _, problems, built, _ = compile_week5(power)
        self.assertIn("did you mean 12 Ace, Power Pass / Post-Cross, MAX?", self.asked(problems, "12 Ace, Power Pass"))
        # Written as a new call, it is the call its words say, and nothing more; no install is asked for.
        text = text.replace("| 11 Trips, Inside Zone | third and short |", "| New call: 11 Trips, Inside Zone | third and short |")
        _, problems, built, source = compile_week5(text)
        self.assertEqual(problems, [])
        plain = next(c for c in built["offensive_call_sheet"] if c["name"] == "11 Trips, Inside Zone")
        self.assertNotIn("Bubble", plain["family"])
        self.assertEqual((plain["type"], plain["formation"], plain["tags"], plain["menus"]),
                         ("run", "11 Trips", [], ["third-and-short"]))
        self.assertNotIn("installs", source)
        # A reference to a call on the sheet is exact too.
        line = next(l for l in FIXTURE.read_text(encoding="utf-8").splitlines() if l.startswith("**Special plays"))
        _, problems, _, _ = compile_week5(self.page(line, "**Special plays:** Flea Flicker: Keep; 12 Wing, TE Delay: Keep"))
        self.assertIn("Offense, Special plays: Flea Flicker is not a call on this week's sheet as written; did you mean "
                      "12 Ace, Flea Flicker, MAX? Write the call's full name", problems)

    def test_keep_and_not_available_contradict(self):
        text = self.page("**Calls not available this week:** 12 Trey, Y-Cross, HALF (no line of the plan names it)",
                         "**Calls not available this week:** 12 Trey, Y-Cross, HALF (no line of the plan names it); "
                         "12 Ace, Flea Flicker, MAX")
        _, problems, built, _ = compile_week5(text)
        self.assertIsNone(built)
        self.assertIn("Offense: 12 Ace, Flea Flicker, MAX is kept under Special plays and listed among the calls not "
                      "available this week; take it out of one", problems)

    def test_a_special_play_may_be_named_for_any_situation(self):
        # Set on earlier sheets for sudden change only, it may be named for third and long and backed up
        # with no install (the user's ruling of October 20, 2026: "We can call anything from the playbook").
        row = "| 12 Ace, Flea Flicker, MAX | third and long, backed up | A shot | After the safety bites |"
        text = self.page("| 11 Trips, Inside Zone + Bubble | third and short |",
                         row + "\n| 11 Trips, Inside Zone + Bubble | third and short |")
        _, problems, built, source = compile_week5(text)
        self.assertEqual(problems, [])
        flea = next(c for c in built["offensive_call_sheet"] if c["name"] == "12 Ace, Flea Flicker, MAX")
        self.assertEqual(flea["menus"], ["opening sequence", "third-and-long", "backed up"])
        self.assertNotIn("installs", source)

    def test_any_call_of_the_book_may_be_named(self):
        # A call no earlier sheet carries, and no practice row names, is read from its words.
        smash = "| 11 Trips, Smash, HALF | normal downs, third and medium | The corner against cloud | Off if pressed |"
        text = self.page("| 11 Trips, Inside Zone + Bubble | third and short |",
                         smash + "\n| 11 Trips, Inside Zone + Bubble | third and short |")
        text = text.replace("| Install Kelce receiving Y; Nicks X relief |", "| Kelce receiving Y; Nicks X relief |")
        _, problems, built, _ = compile_week5(text)
        self.assertEqual(problems, [])
        call = next(c for c in built["offensive_call_sheet"] if c["name"] == "11 Trips, Smash, HALF")
        self.assertEqual({k: call[k] for k in ("family", "type", "personnel", "formation", "protection", "tags")},
                         {"family": "Smash", "type": "pass", "personnel": "11", "formation": "11 Trips",
                          "protection": "HALF", "tags": []})
        # A special play of the book the call-family map names no players for is set with its book type
        # and its players unspecified (no completion or carry is labelled with it), never refused for want
        # of a card: a Halfback Pass is a pass, so a fourth-down go on it resolves as a pass.
        from runtime import call_families, offensive_words
        gadget = "| 12 Ace, Halfback Pass, MAX | sudden change | A shot | After the safety bites |"
        _, problems, built, _ = compile_week5(text.replace(smash, gadget))
        self.assertEqual(problems, [])
        call = next(c for c in built["offensive_call_sheet"] if c["name"] == "12 Ace, Halfback Pass, MAX")
        self.assertEqual((call["family"], call["type"], call["carrier"], call["target"]),
                         ("Halfback Pass", "pass", "unspecified", "unspecified"))
        self.assertEqual(call_families.sheet_errors(built["offensive_call_sheet"]), [])
        # Every play of the book's sections 12.3 and 12.4 has its type: a run for the WR Reverse and the
        # Tunnel Fake Draw (the QB's draw action), a pass for the rest; never "any".
        self.assertEqual(set(offensive_words.BOOK_PLAY_TYPES), set(offensive_words.BOOK_PLAYS))
        for play in offensive_words.BOOK_PLAYS:
            form, problem = game_plan.new_call_form("12 Ace, %s, MAX" % play)
            self.assertIsNone(problem, play)
            self.assertEqual(form["type"], "run" if play in ("WR Reverse", "Tunnel Fake Draw") else "pass", play)
        # The playbook lock stays: a concept the active book does not have is refused.
        _, problems, built, _ = compile_week5(text.replace(smash, "| 11 Doubles, Flood Sail | high red zone | x | y |"))
        self.assertIsNone(built)
        self.assertTrue(any("'Flood Sail' is not a concept of the active playbook" in p for p in problems), problems)

    def test_a_new_variation_needs_no_install(self):
        text = self.page("| Install Kelce receiving Y; Nicks X relief |", "| Kelce receiving Y |")
        _, problems, built, _ = compile_week5(text)
        self.assertEqual(problems, [])
        drive = next(c for c in built["offensive_call_sheet"] if c["name"] == "11 Doubles, Drive, HALF")
        self.assertIn("Nicks X relief", drive["tags"])

    def test_any_call_of_the_book_may_be_an_opening_idea(self):
        # The user's ruling of October 20, 2026: any call in the book may be named for any situation, and
        # the opening ideas are ideas, not a fixed script. A book call no earlier sheet carries, named only
        # under Opening ideas, is added to the sheet with the opening sequence as its only situation.
        line = next(l for l in FIXTURE.read_text(encoding="utf-8").splitlines() if l.startswith("**Opening ideas"))
        forms = game_plan.earlier_forms(earlier(5), 4)
        self.assertNotIn("11 Trips, Smash, HALF", forms)
        _, problems, built, source = compile_week5(self.page(line, line.replace(
            "**Opening ideas:** ", "**Opening ideas:** 11 Trips, Smash, HALF; ")))
        self.assertEqual(problems, [])
        smash = next(c for c in built["offensive_call_sheet"] if c["name"] == "11 Trips, Smash, HALF")
        self.assertEqual({k: smash.get(k) for k in ("family", "type", "formation", "protection", "tags", "opener",
                                                     "menus")},
                         {"family": "Smash", "type": "pass", "formation": "11 Trips", "protection": "HALF",
                          "tags": ["opener"], "opener": 1, "menus": ["opening sequence"]})
        self.assertEqual(source["calls"]["11 Trips, Smash, HALF"], [{"opening": {"page": source["calls"][
            "11 Trips, Smash, HALF"][0]["opening"]["page"]}}])
        # A call an earlier sheet carries takes that sheet's form.
        self.assertIn("11 Trey, Stick", forms)
        _, problems, built, _ = compile_week5(self.page(line, line.replace(
            "**Opening ideas:** ", "**Opening ideas:** 11 Trey, Stick; ")))
        self.assertEqual(problems, [])
        stick = next(c for c in built["offensive_call_sheet"] if c["name"] == "11 Trey, Stick")
        self.assertEqual((stick["family"], stick["type"], stick["formation"], stick["menus"]),
                         (forms["11 Trey, Stick"][0]["family"], forms["11 Trey, Stick"][0]["type"],
                          forms["11 Trey, Stick"][0]["formation"], ["opening sequence"]))
        # A call the page takes off is asked about, never added back.
        _, problems, built, _ = compile_week5(self.page(line, line.replace("11 Trey, Dagger, HALF", "12 Trey, Y-Cross, HALF")))
        self.assertIsNone(built)
        self.assertIn("Offense, Opening ideas, number 27: 12 Trey, Y-Cross, HALF is among the calls not available "
                      "this week; take it out of one", problems)
        # A shorter name is asked about; written New call, the call its own words name is added.
        _, problems, built, _ = compile_week5(self.page(line, line.replace("**Opening ideas:** ",
                                                                           "**Opening ideas:** 12 Ace, Power; ")))
        self.assertIsNone(built)
        self.assertTrue(any("12 Ace, Power is not a call of this week's sheet or an earlier Jacksonville sheet as "
                            "written; did you mean 12 Ace, Power Right" in p and "New call: 12 Ace, Power" in p
                            for p in problems), problems)
        _, problems, built, _ = compile_week5(self.page(line, line.replace("**Opening ideas:** ",
                                                                           "**Opening ideas:** New call: 12 Ace, Power; ")))
        self.assertEqual(problems, [])
        self.assertIn("12 Ace, Power", [c["name"] for c in built["offensive_call_sheet"]])
        # The playbook lock stays: a concept the active book does not have is refused.
        _, problems, built, _ = compile_week5(self.page(line, line.replace("**Opening ideas:** ",
                                                                           "**Opening ideas:** 11 Doubles, Flood Sail; ")))
        self.assertIsNone(built)
        self.assertTrue(any("'Flood Sail' is not a concept of the active playbook" in p for p in problems), problems)

    def test_a_special_play_not_on_the_sheet_names_the_remedy(self):
        # Special plays sets a call's status (Keep, Remove, Practice only) and has no situation, so a book
        # call it names that the sheet does not have is not added; the check says how to call it.
        line = next(l for l in FIXTURE.read_text(encoding="utf-8").splitlines() if l.startswith("**Special plays"))
        _, problems, built, _ = compile_week5(self.page(line, line + "; 12 Ace, Halfback Pass, MAX: Keep"))
        self.assertIsNone(built)
        self.assertIn("Offense, Special plays: 12 Ace, Halfback Pass, MAX is not a call on this week's sheet; to call "
                      "it this week, add it as a row in the Primary calls table with the situations you want it for",
                      problems)

    def test_a_situation_is_named_in_the_sheets_words(self):
        text = self.page("| 11 Doubles, Inside Zone Right | backed up |", "| 11 Doubles, Inside Zone Right | red zone |")
        _, problems, built, _ = compile_week5(text)
        self.assertTrue(any("say which: high red zone, low red zone or goal line" in p for p in problems), problems)
        text = self.page("| 11 Doubles, Inside Zone Right | backed up |",
                         "| 11 Doubles, Inside Zone Right | opening sequence |")
        _, problems, _, _ = compile_week5(text)
        self.assertTrue(any("the opening ideas line puts a call in the opening sequence" in p for p in problems))

    def test_a_defensive_word_of_the_book_needs_no_earlier_practice(self):
        # Cover 2 is on no earlier Jacksonville sheet and no practice row names it: a version 2 page's
        # practiced menu is its own rows' words, so the sheet holds it and its validators pass.
        from runtime import defensive_calls
        text = self.page("| Third and long | Dime Quarters or Cover 6, base four |",
                         "| Third and long | Dime Cover 2, base four |")
        frame = game_plan.page_frame("career/2014/Regular_Season/Games/Week_05/Game_Plan.md", "Week 5", "frozen",
                                     "provenance", "Jacksonville Jaguars", defensive_calls.active_defensive_book(ROOT), 5)
        _, problems, built, _ = compile_week5(text, frame)
        self.assertEqual(problems, [])
        ds = built["defensive_call_sheet"]
        self.assertIn("2", ds["practiced"]["coverages"])
        self.assertEqual(defensive_calls.sheet_errors(ds), [])
        # A word the active defensive book does not have is refused.
        _, problems, _, _ = compile_week5(text.replace("Dime Cover 2, base four", "Dime Cover 9, base four"), frame)
        self.assertTrue(any("'9' is not a word of the active defensive playbook" in p for p in problems), problems)

    def test_the_response_is_read_in_the_books_words(self):
        call, problems = game_plan.response_call("Nickel Even Cover 6, passing strength")
        self.assertEqual((call, problems), ({"front": "Nickel Even", "strength": "Passing", "coverage": ["6"]}, []))
        self.assertEqual(game_plan.response_call("Dime, interior mug")[0],
                         {"package": "Dime", "pressure": "replace", "tags": ["mug"]})
        call, problems = game_plan.response_call("Quarters with an eight-man front")
        self.assertTrue(problems)
        self.assertEqual(game_plan.response_kind("Third and medium"), ("situation", "third-and-medium"))
        self.assertEqual(game_plan.response_kind("When tempo keeps Dime on"), ("conditional", None))
        self.assertEqual(game_plan.response_kind("Counter on third and medium"), ("counter", None))
        self.assertEqual(game_plan.response_kind("11 personnel, 3x1"), ("presentation", None))

    def test_the_page_has_no_technical_column(self):
        template = (ROOT / "foundation/templates/game_week/game_plan_template.md").read_text(encoding="utf-8")
        for words in ("Opener", "Returns", "Family", "Type", "Tags"):
            self.assertNotIn("| %s |" % words, template)
        blank = game_plan.blank("Week 6 Game Plan", {})
        for words in ("Opener", "Returns", "Family", "| Type", "Tags |", "Row"):
            self.assertNotIn(words, blank)
        for heading in game_plan.HEADINGS:
            self.assertIn("## " + heading, template)
            self.assertIn("## " + heading, blank)
        for columns in (game_plan.CALL_COLUMNS, game_plan.RESPONSE_COLUMNS, game_plan.PRACTICE_COLUMNS):
            self.assertIn("| " + " | ".join(columns) + " |", template)


def open_week(root):
    from scripts.render_game_week import Week
    return Week(root)


def needed_inactives(root, week):
    """A legal inactive list from the stored facts: every player out on game day, then the deepest
    reserve of the largest groups."""
    from runtime.week_inputs import roster_available
    from datetime import date
    paths = SeasonPaths(SEASON, root)
    roster = roster_record.load(paths.roster)
    chart = json.loads(paths.depth_chart.read_text(encoding="utf-8"))
    active = roster_record.players(roster, ("active",))
    game = next(g for g in paths.regular_games() if g["week"] == week and "Jacksonville Jaguars" in (g["away"], g["home"]))
    out = [p["name"] for p in active if not roster_available(p["availability"], date.fromisoformat(game["date"]), SEASON)]
    groups = sorted(chart["depth"].items(), key=lambda kv: -len(kv[1]))
    depth = 1
    while len(out) < len(active) - RULES.active_limit:
        for _, players in groups:
            if len(out) < len(active) - RULES.active_limit and len(players) > depth + 2:
                name = players[-depth]
                if name not in out:
                    out.append(name)
        depth += 1
    return out


def quiet(call, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = call(*args, **kwargs)
    return result, out.getvalue()


class OpenWeek(unittest.TestCase):
    """A temporary copy with the open week's pages issued, and the helpers the tests share."""

    def setUp(self):
        self.root = copy_repo(self)
        from scripts import render_game_week
        wk = open_week(self.root)
        if wk.game is None:
            self.skipTest("no Jacksonville game is open")
        # Every test here starts from the open week's blank page, whatever the real page holds:
        # writing the pages builds the blank one only where the page is missing.
        week_pages(SEASON, wk.game["week"], self.root).plan.unlink(missing_ok=True)
        quiet(render_game_week.write, self.root)
        self.week = wk.game["week"]
        self.pages = week_pages(SEASON, self.week, self.root)
        self.previous = max(w for w in range(1, self.week) if SeasonPaths(SEASON, self.root).call_sheet(w).is_file())

    def check(self):
        from scripts.check_game_plan import check
        return check(self.root, SEASON, self.week)

    def answers(self, **over):
        """A complete page for the open week: the previous week carried, the standing rules, the
        inactives named from the stored facts."""
        answers = {
            "baseline": "Carry Week %d" % self.previous, "attack": "Their linebackers in space against our tight ends.",
            "protect": "A cutback behind an overrun.", "change_course": "A safety rotating late to the second tight end.",
            "inactives": ", ".join(needed_inactives(self.root, self.week)), "depth": "No change",
            "contingency": "Reissue after the examinations.", "coverage_units": "No change",
            "offense_caller": "No change", "base_personnel": "Twelve personnel leads.",
            "learn": "Who travels with the second tight end.", "opening_approach": "As last week, with changes below.",
            "opening": "Carry Week %d opening" % self.previous, "third_down": "Carry Week %d" % self.previous,
            "backed_up": "No change", "red_zone": "No change", "two_minute": "No change", "four_minute": "No change",
            "sudden_change": "No change", "special_plays": "No change", "not_available": "None",
            "defense_caller": "No change", "front": "Force and cutback first.", "coverage": "Quarters and 6.",
            "rush": game_plan.RUSH_CHOICE, "discover": "Their protection against the replaced rusher.",
            "matchups": "No change", "kicking_caller": "No change", "kicking": "No change",
            "fourth_down": "Standing rule", "two_point": "Standing rule", "kickoff": "Standing rule",
            "endgame": "No change", "participation": "Reissue after the examination.", "tradeoff": "None",
            "staff": "None", "public": "No new statement", "open_decisions": "None", "ready": "The exams of the week.",
            "practice": [["Third down", "Tice with the offense", "Third and medium", "The Saturday walkthrough"]]}
        answers.update(over)
        return answers

    def write(self, answers):
        from scripts import render_game_week
        wk = render_game_week.Week(self.root)
        text = game_plan.render("Week %d Game Plan" % self.week, render_game_week.plan_facts(wk), answers)
        self.pages.plan.write_text(text, encoding="utf-8")
        self.answered = answers
        return text

    def apply(self):
        from scripts.apply_game_plan import apply
        problems, written = quiet(apply, self.root, SEASON, self.week)[0]
        self.assertEqual(problems, [])
        return written

    def roster(self):
        return roster_record.load(SeasonPaths(SEASON, self.root).roster)

    def chart(self):
        return json.loads(SeasonPaths(SEASON, self.root).depth_chart.read_text(encoding="utf-8"))

    def week_items(self, queue=None):
        queue = queue or json.loads((self.root / "state/decision_queue.json").read_text(encoding="utf-8"))
        return queue, [i for i in queue["items"] if i["class"] in ("weekly_game_plan", "game_day_inactives")
                       and any(b.get("week") == self.week for b in i["blocks"])]

    def exams_held(self):
        """In the copy, the exams the week's items wait on held: each dated wait moved to the day before
        today (the clock stays), and the briefing re-issued for the changed situation."""
        from datetime import timedelta
        from runtime.player_bios import master_date
        queue, items = self.week_items()
        before = (master_date(self.root) - timedelta(days=1)).isoformat()
        for item in items:
            for wait in item.get("waits_on") or ():
                if wait.get("date"):
                    wait["date"] = before
        (self.root / "state/decision_queue.json").write_text(json.dumps(queue, indent=1, ensure_ascii=False)
                                                              + "\n", encoding="utf-8")
        from scripts import render_game_week
        quiet(render_game_week.write, self.root)
        # He answers the briefing re-issued after the exams: the same choices, its issue on Briefing used.
        if getattr(self, "answered", None) is not None:
            self.write(self.answered)

    def set_availability(self, names, note, reissue=True):
        path = SeasonPaths(SEASON, self.root).roster
        data = json.loads(path.read_text(encoding="utf-8"))
        for p in data["players"]:
            if p["name"] in names:
                p["availability"] = note
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if reissue:
            from scripts import render_game_week
            quiet(render_game_week.write, self.root)

    def game_day(self):
        from datetime import date
        game = next(g for g in SeasonPaths(SEASON, self.root).regular_games()
                    if g["week"] == self.week and "Jacksonville Jaguars" in (g["away"], g["home"]))
        return date.fromisoformat(game["date"])

    def out_note(self):
        from datetime import timedelta
        back = self.game_day() + timedelta(days=30)
        return "Out, short: lower extremity; projected return %s %d, %d" % (back.strftime("%B"), back.day, back.year)


class SilenceTests(OpenWeek):
    """No user silence creates an approved decision; opening or checking a page moves nothing."""

    def test_the_blank_page_approves_nothing(self):
        from scripts import apply_game_plan
        problems, _, plan = self.check()
        for key, section, label, kind in game_plan.FIELDS:
            if kind == "fact" or key == "briefing":     # the builder writes these lines
                continue
            where = game_plan.where_of(key, plan.choices["fields"][key]["label"])
            self.assertTrue(any(p.startswith((where + ": unanswered", label + ": unanswered")) for p in problems),
                            (key, problems))
        self.assertEqual(page_errors(self.pages.plan.relative_to(self.root).as_posix(),
                                     self.pages.plan.read_text(encoding="utf-8"), root=self.root), [])
        state = (self.root / "state/05_Current_Season_State.md").read_bytes()
        queue = (self.root / "state/decision_queue.json").read_bytes()
        (problems, written), _ = quiet(apply_game_plan.apply, self.root, SEASON, self.week)
        self.assertTrue(problems)
        self.assertEqual(written, [])
        self.assertFalse(self.pages.call_sheet.exists())
        self.assertEqual((self.root / "state/05_Current_Season_State.md").read_bytes(), state)
        self.assertEqual((self.root / "state/decision_queue.json").read_bytes(), queue)

    def test_one_blank_line_holds_the_whole_plan(self):
        for key in ("two_point", "attack", "rush", "inactives"):
            self.write(self.answers(**{key: ""}))
            problems, _, _ = self.check()
            self.assertTrue(any("unanswered" in p for p in problems), (key, problems))
        # The practice table is information for the staff, never a condition on the plan.
        self.write(self.answers(practice=[]))
        self.assertFalse(any("What we will practice" in p for p in self.check()[0]))


class CheckTests(OpenWeek):
    def test_a_complete_page_checks_applies_and_validates(self):
        from scripts.validate_repository import validate
        players = needed_inactives(self.root, self.week)
        self.write(self.answers())
        problems, _, _ = self.check()
        self.assertEqual(problems, [])
        self.exams_held()
        self.apply()
        paths = SeasonPaths(SEASON, self.root)
        sheet = json.loads(paths.call_sheet(self.week).read_text(encoding="utf-8"))
        before = json.loads(paths.call_sheet(self.previous).read_text(encoding="utf-8"))
        strip = lambda calls: [{k: v for k, v in c.items() if k != "what_stone_is_looking_at"} for c in calls]
        self.assertEqual(sheet["offensive_call_sheet"], strip(before["offensive_call_sheet"]))
        self.assertEqual(sheet["defensive_call_sheet"]["rows"], before["defensive_call_sheet"]["rows"])
        self.assertEqual(sheet["decisions"]["two_point"], before["decisions"]["two_point"])
        block = sheet["decisions"]["fourth_down"]
        self.assertEqual({k: v for k, v in block.items() if k != "prepared_calls"}, standing_block(self.root))
        self.assertEqual(block["prepared_calls"], game_plan.first_calls(sheet["offensive_call_sheet"]))
        chart = self.chart()
        self.assertEqual((chart["game_day_inactives"]["week"], chart["game_day_inactives"]["players"]),
                         (self.week, players))
        _, items = self.week_items()
        self.assertTrue(items and all(i["status"] == "RESOLVED" and i["resolution"]["by"] == "user" for i in items))
        self.assertEqual(validate(self.root), [])

    def test_invalid_choices_are_named_in_football_words(self):
        roster = self.roster()
        self.assertNotIn("Ace Sanders", {p["name"] for p in roster_record.players(roster)})
        six = needed_inactives(self.root, self.week)[:5] + ["Ace Sanders"]
        self.write(self.answers(inactives=", ".join(six), staff="Kernel note.",
                                calls=[["11 Doubles, Flood Sail", "high red zone", "A shot", "None"]]))
        problems, _, _ = self.check()
        self.assertIn("Inactives: 6 named, %d needed" % len(needed_inactives(self.root, self.week)), problems)
        self.assertIn("Inactives: Ace Sanders is not on the roster", problems)
        self.assertIn("Directions to the staff and public position: 'Kernel' is not a football word", problems)
        self.write(self.answers(calls=[["11 Doubles, Flood Sail", "high red zone", "A shot", "None"]]))
        problems, _, _ = self.check()
        self.assertTrue(any("'Flood Sail' is not a concept of the active playbook" in p for p in problems), problems)

    def test_the_briefing_he_answers_is_the_current_one(self):
        self.write(self.answers(briefing="September 28, 2014"))
        problems, _, _ = self.check()
        self.assertTrue(any(p.startswith("Briefing used: your page answers the briefing of September 28, 2014")
                            for p in problems), problems)

    def test_a_caller_line_names_the_caller_on_file(self):
        self.write(self.answers(defense_caller="Romeo Crennel"))
        problems, _, _ = self.check()
        self.assertTrue(any(p.startswith("Defense, Caller: Alex Stone calls it on the staff page") for p in problems),
                        problems)

    def test_a_grouping_needs_the_players_who_dress(self):
        chart = self.chart()
        active = {p["name"] for p in roster_record.players(self.roster(), ("active",))}
        ends = [p for p in chart["depth"]["TE"] if p in active]
        needed = needed_inactives(self.root, self.week)
        if len(ends) - 1 > len(needed):
            self.skipTest("more tight ends than inactive places")
        players = ends[1:] + [p for p in needed if p not in ends][:len(needed) - len(ends) + 1]
        self.write(self.answers(inactives=", ".join(players)))
        problems, _, _ = self.check()
        self.assertTrue(any("12 personnel needs 2 tight ends and 1 dress" in p for p in problems), problems)


def standing_block(root=ROOT):
    from runtime import current_job
    job = current_job.load(root)
    rule = next(i for i in current_job.instructions(job) if i["id"] == "stone-fourth-down-rule")
    return rule["block"]


class FourthDownRuleTests(unittest.TestCase):
    """Stone's standing fourth-down rule as a decisions.fourth_down block, against its words."""

    # (yards to go, yards to the goal line, goal to go, decision, why)
    CASES = (
        (1, 70, False, "go", "4th-and-1 at the own 30"),
        (2, 99, False, "go", "4th-and-2 at the own 1"),
        (1, 2, True, "go", "4th-and-1 at the 2, as Week 5 read it"),
        (3, 45, False, "go", "4th-and-3 at the opponent's 45"),
        (4, 26, False, "go", "4th-and-4 at the 26, as Week 5 read it"),
        (4, 49, False, "go", "4th-and-4 at the opponent's 49, past midfield"),
        (3, 50, False, "punt", "4th-and-3 at midfield is not past it: a 68-yard kick"),
        (3, 55, False, "punt", "4th-and-3 at the own 45: the field-goal line, a 73-yard kick"),
        (6, 30, False, "field_goal", "4th-and-6 at the opponent's 30: a 48-yard kick"),
        (6, 34, False, "field_goal", "4th-and-6 at the opponent's 34: a 52-yard kick"),
        (6, 35, False, "punt", "4th-and-6 at the opponent's 35: a 53-yard kick"),
        (6, 40, False, "punt", "4th-and-6 at the opponent's 40: a 58-yard kick"),
        (10, 28, False, "field_goal", "4th-and-10 at the 28: Week 5's 46-yard kick"),
        (5, 37, False, "punt", "4th-and-5 at the 37: Week 5's 55-yard kick"),
        (5, 5, True, "field_goal", "4th-and-goal from the 5: a 23-yard kick"),
    )

    def test_the_block_reads_as_the_words(self):
        from runtime import fourth_down
        block = standing_block()
        for ydstogo, los, goal, expected, why in self.CASES:
            state = {"period": 2, "diff": 0, "seconds": 1800, "ydstogo": ydstogo, "los": los, "goal_to_go": goal}
            decision, basis, call = fourth_down.decide(block, state, 0.5, (1, 1, 1))
            self.assertEqual(decision, expected, why)
            self.assertTrue(basis.startswith("policy:"), why)

    def test_the_field_goal_line_is_the_library_offset(self):
        data = json.loads((ROOT / "library/data/2010_2014w4_fourth_down_decisions.json").read_text(encoding="utf-8"))
        offset = int(data["field_goal_offset"]["modal"])
        kick = next(r for r in standing_block()["rules"] if r["decision"] == "field_goal")
        self.assertEqual(kick["when"]["los"]["max"] + offset, 52)

    def test_the_block_is_valid_with_the_weeks_first_calls(self):
        from runtime import fourth_down
        _, sheet = week5()
        block = dict(standing_block(), prepared_calls=game_plan.first_calls(sheet["offensive_call_sheet"]))
        self.assertEqual(block["prepared_calls"]["third-and-short"], "12 Ace, Power Right")
        self.assertEqual(fourth_down.policy_errors(block, fourth_down.sheet_call_names(sheet["offensive_call_sheet"])),
                         [])


WEEK6_ANSWERS = {
    "briefing": "October 5, 2014", "baseline": "Carry Week 5", "attack": "The tight ends in space.",
    "protect": "A cutback behind an overrun.", "change_course": "A late safety rotation.",
    "inactives": "Standing rule", "depth": "No change", "contingency": "None", "coverage_units": "No change",
    "offense_caller": "No change", "base_personnel": "Twelve personnel leads.", "learn": "Who takes the second end.",
    "opening_approach": "As last week.", "opening": "Carry Week 5 opening", "third_down": "Carry Week 5",
    "backed_up": "No change", "red_zone": "No change", "two_minute": "No change", "four_minute": "No change",
    "sudden_change": "No change", "special_plays": "No change", "not_available": "None",
    "defense_caller": "No change", "front": "Force first.", "coverage": "Quarters and 6.", "rush": "No change",
    "discover": "Their protection.", "matchups": "No change", "kicking_caller": "No change", "kicking": "No change",
    "fourth_down": "None", "two_point": "Standing rule", "kickoff": "Standing rule", "endgame": "No change",
    "participation": "None", "tradeoff": "None", "staff": "None", "public": "No new statement",
    "open_decisions": "None", "ready": "All decisions settled",
    "practice": [["Third down", "Tice with the offense", "Third and medium", "The Saturday walkthrough"]]}
WEEK6_PAGE = "career/2014/Regular_Season/Games/Week_06/Game_Plan.md"


def compile_week6(**over):
    """A Week 6 page carrying Week 5, compiled as the check compiles it (a version 2 frame)."""
    _, sheet = week5()
    text = game_plan.render("Week 6 Game Plan", {}, dict(WEEK6_ANSWERS, **over))
    choices, problems = game_plan.parse(text)
    frame = game_plan.page_frame(WEEK6_PAGE, "event", "frozen", "provenance", sheet["team"],
                                 sheet["defensive_call_sheet"]["book"], 6)
    built, source, found = game_plan.compile_sheet(choices, frame, earlier(6), standing_week5(), {"defense": "Alex Stone"})
    return problems + found, built, source


class CarryTests(unittest.TestCase):
    """What a carried week brings, and what it does not."""

    def test_a_carried_defense_cites_this_page(self):
        problems, built, source = compile_week6()
        self.assertEqual(problems, [])
        _, sheet = week5()
        ds, before = built["defensive_call_sheet"], sheet["defensive_call_sheet"]
        # The responses and their inherited citations stand as set; the record is this page's.
        self.assertEqual(ds["rows"], before["rows"])
        self.assertEqual(ds["practiced"], before["practiced"])
        self.assertEqual(ds["packet"], WEEK6_PAGE)
        self.assertEqual(ds["notes"], ["Carried from Week 5 as set: its prepared responses, their citations and the "
                                       "practiced menu."])
        self.assertNotIn("Week_05_Pittsburgh", json.dumps({k: v for k, v in ds.items() if k not in ("rows", "practiced",
                                                                                                 "rush_rule")}))
        self.assertEqual(source["defense"], {"carried": {"week": 5}})

    def test_a_carried_opening_drops_a_call_the_page_takes_off(self):
        from scripts.check_game_plan import opening_order
        _, sheet = week5()
        for over, gone in (({"special_plays": "12 Ace, Flea Flicker, MAX: Remove, no safety trigger yet"},
                            "12 Ace, Flea Flicker, MAX"),
                           ({"special_plays": "12 Wing, TE Delay: Practice only, the rush is not credible"},
                            "12 Wing, TE Delay"),
                           ({"not_available": "12 Wing, TE Delay (Lewis is out)"}, "12 Wing, TE Delay")):
            problems, built, source = compile_week6(**over)
            self.assertEqual(problems, [], over)
            self.assertEqual(opening_order(built), [n for n in opening_order(sheet) if n != gone])
            self.assertNotIn(gone, [c["name"] for c in built["offensive_call_sheet"]])
            self.assertEqual(source["opening_dropped"], [gone])
        # Nothing taken off: the opening is Week 5's exactly, its numbers as set.
        problems, built, _ = compile_week6()
        self.assertEqual({c["name"]: (c.get("opener"), c.get("opener_returns")) for c in built["offensive_call_sheet"]},
                         {c["name"]: (c.get("opener"), c.get("opener_returns")) for c in sheet["offensive_call_sheet"]})

    def test_rewording_bullets_compiles_to_the_same_bytes(self):
        _, first, _ = compile_week6(staff="Tice relays.")
        _, second, _ = compile_week6(staff="Tice relays.\n- And at greater length.\n- Bates on protection.")
        self.assertEqual(game_plan.sheet_bytes(first), game_plan.sheet_bytes(second))


class ParseTests(unittest.TestCase):
    def test_my_rules_read_back_from_their_football_words(self):
        rows = [["4th", "down 8 to down 1", "5:00 or less left", "2 or less", "35 or less", "No", "Go",
                 "12 Ace, Power Right"]]
        text = game_plan.render("Plan", {}, {"fourth_down": "My rules, otherwise Punt", "rules": {"fourth_down": rows}})
        choices, problems = game_plan.parse(text)
        self.assertEqual(problems, [])
        self.assertEqual(choices["fourth_down"], {"rules": [{"when": {"period": [4], "margin": {"min": -8, "max": -1},
                                                                      "ydstogo": {"max": 2}, "los": {"max": 35},
                                                                      "goal_to_go": False, "game_seconds_max": 300},
                                                             "decision": "go", "call": "12 Ace, Power Right"}],
                                                  "otherwise": "punt"})

    def test_a_missing_heading_and_a_stray_line_are_named(self):
        text = game_plan.blank("Plan", {}).replace("## 5. Special teams and game decisions", "## 5. Kicking")
        _, problems = game_plan.parse(text)
        self.assertIn("5. Special teams and game decisions: the heading is missing", problems)
        heading = "## 7. Directions to the staff and public position\n"
        text = game_plan.blank("Plan", {}).replace(heading, heading + "\nA stray line.\n")
        _, problems = game_plan.parse(text)
        self.assertTrue(any("'A stray line.' is not on a line of its own label" in p for p in problems), problems)

    def test_his_direction_may_run_on_below_its_label(self):
        # Further lines and bullets under a line of his own direction are part of that answer.
        text = game_plan.blank("Plan", {}).replace("**Staff instructions:**",
                                                   "**Staff instructions:** Short.\nMore.\n- Tice: the relay.")
        choices, problems = game_plan.parse(text)
        self.assertEqual(problems, [])
        self.assertEqual(choices["staff"], "Short.\nMore.\n- Tice: the relay.")
        text = game_plan.blank("Plan", {}).replace("**Staff instructions:**", "**Staff instructions:**\n- Tice: the relay.")
        choices, _ = game_plan.parse(text)
        self.assertNotIn("staff", choices["unanswered"])
        # Under a line read as one answer, a further line is named, never read into it.
        text = game_plan.blank("Plan", {}).replace("**Inactives:**", "**Inactives:** Standing rule\n- Gator Hoskins")
        _, problems = game_plan.parse(text)
        self.assertTrue(any("'- Gator Hoskins' continues the line 'Inactives'" in p for p in problems), problems)

    def test_the_briefing_used_names_its_revision(self):
        text = game_plan.blank("Plan", {}).replace("**Briefing used:**", "**Briefing used:** October 5, 2014, revision 3")
        choices, problems = game_plan.parse(text)
        from datetime import date
        self.assertEqual(choices["briefing"], {"date": date(2014, 10, 5), "revision": 3})
        self.assertEqual(game_plan.issue_label(date(2014, 10, 5), 3), "October 5, 2014, revision 3")
        self.assertEqual(game_plan.issue_label(date(2014, 10, 5), 1), "October 5, 2014")
        text = game_plan.blank("Plan", {}).replace("**Briefing used:**", "**Briefing used:** October 5, 2014")
        self.assertEqual(game_plan.parse(text)[0]["briefing"]["revision"], 1)


# ---------------------------------------------------------------- the step-4 guards under version 2
class GuardTests(OpenWeek):
    # GP1: the playbook lock covers every word a call carries.
    def test_gp1_every_word_of_a_call_is_held_to_the_active_book(self):
        self.write(self.answers(calls=[["12 Ace, Power Right (READ Glance)", "normal downs", "x", "y"]]))
        problems, _, _ = self.check()
        self.assertTrue(any("the tag 'READ Glance' has 'READ'" in p for p in problems), problems)
        from runtime import offensive_words
        names = [p["name"] for p in roster_record.players(self.roster())]
        for week in range(1, self.week):
            path = SeasonPaths(SEASON, self.root).call_sheet(week)
            if path.is_file():
                for call in json.loads(path.read_text(encoding="utf-8"))["offensive_call_sheet"]:
                    self.assertEqual(offensive_words.call_errors(call, names), [], (week, call["name"]))

    # GP2: no plan changes while a game is paused or once the week's game is built.
    def test_gp2_a_paused_or_built_week_is_refused(self):
        from scripts.apply_game_plan import apply
        self.write(self.answers())
        paths = SeasonPaths(SEASON, self.root)
        paused = paths.paused_game(self.week)
        paused.parent.mkdir(parents=True, exist_ok=True)
        paused.write_text(json.dumps({"status": "paused"}), encoding="utf-8")
        problems, _, _ = self.check()
        self.assertEqual(problems, ["A game is paused; the plan stays as it was set until the game is finished"])
        paused.unlink()
        built = paths.cache(self.week, "inputs")
        built.parent.mkdir(parents=True, exist_ok=True)
        built.write_text("{}", encoding="utf-8")
        problems, written = apply(self.root, SEASON, self.week)
        self.assertTrue(problems and "has been built from the applied plan" in problems[0], problems)
        self.assertEqual(written, [])
        self.assertFalse(paths.call_sheet(self.week).exists())

    # GP3, F2: the applied page is tied to the sheet it froze; the apply records its event and,
    # applied again, replaces its log entry.
    def test_gp3_f2_the_applied_page_is_tied_to_its_sheet(self):
        from scripts import check_game_plan, render_game_week
        from scripts.validate_repository import validate
        self.write(self.answers())
        self.exams_held()
        self.apply()
        self.assertFalse(any("a new briefing is due" in e for e in render_game_week.check(self.root)))
        self.assertEqual(validate(self.root), [])
        self.assertIn("-week-%d-game-plan-set" % self.week, self.pages.readme.read_text(encoding="utf-8"))
        record = SeasonPaths(SEASON, self.root).record("record.md").read_text(encoding="utf-8")
        self.assertIn("Stone set his Week %d Game Plan" % self.week, record.rstrip().splitlines()[-1])
        sheet = self.pages.call_sheet.read_bytes()
        # Only a reason changed: the page is no longer the one applied, but the sheet it sets is the same.
        self.write(self.answers(staff="Keep the walkthrough short."))
        self.assertTrue(any("has changed since it was applied" in e for e in validate(self.root)))
        code, out = quiet(check_game_plan.main, [str(self.week), "--season", str(SEASON), "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("NOT YET SET", out)
        self.apply()
        self.assertEqual(validate(self.root), [])
        self.assertEqual(self.pages.call_sheet.read_bytes(), sheet)
        log = json.loads(SeasonPaths(SEASON, self.root).record("team/depth_chart/update_log.json").read_text(
            encoding="utf-8"))
        self.assertEqual(len([e for e in log["entries"] if e["event"] == "Week %d: Stone's Game Plan" % self.week]), 1)

    # GP4: a game role does what it says; an order change reaches the chart.
    def test_gp4_roles_and_orders_reach_the_game(self):
        from scripts.validate_repository import validate
        chart = self.chart()
        backup = chart["depth"]["QB"][1]
        swap = list(chart["depth"]["WR"])
        swap[2], swap[3] = swap[3], swap[2]
        self.write(self.answers(depth="Wide receivers order: %s; Starter: %s" % (", ".join(swap), backup)))
        self.assertEqual(self.check()[0], [])
        self.exams_held()
        self.apply()
        chart = self.chart()
        self.assertEqual(chart["depth"]["QB"][0], backup)
        self.assertIn("passer", chart["roles"][backup])
        self.assertEqual(chart["depth"]["WR"], swap)
        self.assertEqual(validate(self.root), [])

    def test_gp4_gp8_a_role_goes_to_a_player_of_its_group(self):
        chart = self.chart()
        receiver = chart["depth"]["WR"][-1]
        reserve = next(p for p, roles in chart["roles"].items() if "outside_reserve" in roles)
        self.write(self.answers(depth="Kicker: %s; Nickel: %s" % (receiver, receiver)))
        problems, _, _ = self.check()
        self.assertIn("Depth/role changes: the Kicker role goes to a player of the K group; %s is not one" % receiver,
                      problems)
        self.assertIn("Depth/role changes: the Nickel role goes to a player of the DB group; %s is not one" % receiver,
                      problems)
        self.write(self.answers(depth="Nickel: %s" % reserve))
        problems, _, _ = self.check()
        self.assertIn("Depth/role changes: %s cannot take both the Nickel and the Outside reserve corner seats"
                      % reserve, problems)

    # GP5: a heading the page does not have is rejected, not dropped.
    def test_gp5_a_subheading_the_page_lacks_is_rejected(self):
        text = self.write(self.answers(staff="Keep the walkthrough short."))
        text = text.replace("**Staff instructions:**", "### For Tice\n\n**Staff instructions:**")
        self.pages.plan.write_text(text, encoding="utf-8")
        problems, _, _ = self.check()
        self.assertIn("7. Directions to the staff and public position: 'For Tice' is not one of its headings; write "
                      "under the section's own lines", problems)

    # GP6, GP7: Carry Week N carries a rule only when that week froze one.
    def test_gp6_gp7_carrying_a_week_without_the_rule(self):
        sheets = earlier(self.week, self.root)
        bare = [w for w, sh in sheets.items() if "two_point" not in (sh.get("decisions") or {})]
        no_fourth = [w for w, sh in sheets.items() if "fourth_down" not in (sh.get("decisions") or {})]
        if bare:
            self.write(self.answers(two_point="Carry Week %d" % bare[-1]))
            self.assertTrue(any(p.startswith("Two-point tries: Week %d set no two-point rule" % bare[-1])
                                for p in self.check()[0]))
        if no_fourth:
            self.write(self.answers(fourth_down="Carry Week %d" % no_fourth[-1]))
            self.assertTrue(any(p.startswith("Fourth downs: Week %d froze no fourth-down rule" % no_fourth[-1])
                                for p in self.check()[0]))
            self.write(self.answers(fourth_down="No change"))
            if "fourth_down" not in (sheets[max(sheets)].get("decisions") or {}):
                self.assertTrue(any("so No change would leave every fourth down to your live call" in p
                                    for p in self.check()[0]))

    # GP9: more players out than the inactive places: the list is those players.
    def test_gp9_more_out_than_the_places(self):
        from scripts.check_game_plan import Plan, inactive_problems
        needed = len(roster_record.players(self.roster(), ("active",))) - RULES.active_limit
        chart = self.chart()
        active = {q["name"] for q in roster_record.players(self.roster(), ("active",))}
        out = [p for p in chart["depth"]["DB"] + chart["depth"]["LB"] if p in active][:needed + 1]
        self.set_availability(out, self.out_note())
        self.write(self.answers(inactives=", ".join(out)))
        self.assertEqual(inactive_problems(Plan(self.root, SEASON, self.week)), [])
        self.write(self.answers(inactives=", ".join(out[:needed])))
        problems = inactive_problems(Plan(self.root, SEASON, self.week))
        self.assertTrue(any("are out for the game, more than the %d inactive places" % needed in p for p in problems))

    # GP10: an availability note the staff cannot read fails the check, never a traceback.
    def test_gp10_an_unreadable_note_is_a_problem(self):
        from scripts.check_game_plan import Plan, check, inactive_problems
        name = self.chart()["depth"]["WR"][0]
        self.write(self.answers())
        self.set_availability([name], "Doubtful with an ankle sprain after the Friday practice", reissue=False)
        from scripts import render_game_week
        with self.assertRaises(ValueError):
            quiet(render_game_week.write, self.root)
        problems = inactive_problems(Plan(self.root, SEASON, self.week))
        self.assertTrue(any(p.startswith("Inactives: %s's medical status" % name) for p in problems), problems)
        found = check(self.root, SEASON, self.week)[0]
        self.assertTrue(any(p.startswith("Inactives: %s's medical status" % name) for p in found), found)
        self.assertTrue(any(p.startswith("Game Week Briefing: ") and "medical format" in p for p in found), found)

    # GP11: an upload for a played week is refused before anything is written.
    def test_gp11_uploads_are_refused_before_writing(self):
        from scripts import apply_game_plan, check_game_plan
        played = self.previous
        page = week_pages(SEASON, played, self.root).plan
        before = page.read_bytes() if page.is_file() else None
        upload = self.root / "upload.md"
        upload.write_text(self.pages.plan.read_text(encoding="utf-8"), encoding="utf-8")
        code, out = quiet(check_game_plan.main, [str(played), "--season", str(SEASON), "--file", str(upload),
                                                 "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("has been played", out)
        self.assertEqual(page.read_bytes() if page.is_file() else None, before)
        pdf = self.root / "upload.pdf"
        pdf.write_text("x", encoding="utf-8")
        code, out = quiet(apply_game_plan.main, [str(self.week), "--season", str(SEASON), "--file", str(pdf),
                                                 "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("GAME PLAN: NOT APPLIED", out)

    # GP12: clean-page problems are placed in their section and read in football words.
    def test_gp12_problems_name_their_place(self):
        from scripts.check_game_plan import section_of
        self.write(self.answers(staff="Run THIRD-AND-3 twice."))
        self.assertIn("Directions to the staff and public position: 'THIRD-AND-3' reads as an internal identifier",
                      self.check()[0])
        text = "## 3. Offense: what we are calling and why\n\n### Primary calls\n\nline\n"
        self.assertEqual(section_of(text, 5), "Offense: what we are calling and why, Primary calls")

    # R6, W6-10: Standing rule for the inactives, with the others he names after it.
    def test_r6_standing_rule_with_the_others_named(self):
        from scripts.check_game_plan import Plan, RULE_GROUPS, standing_inactives
        self.write(self.answers(inactives="Standing rule"))
        plan = Plan(self.root, SEASON, self.week)
        self.assertEqual(plan.choices["inactives"], {"standing": True, "players": [], "reasons": {}})
        outs, _ = plan.outs()
        healthy = plan.needed() - len(outs)
        players, problems = standing_inactives(plan)
        if healthy < RULE_GROUPS:
            self.assertIsNone(players)
            return
        if healthy == RULE_GROUPS:
            self.assertEqual(self.check()[0], [])
            return
        others = healthy - RULE_GROUPS
        self.assertIn("name the other %d after Standing rule on the Inactives line, with commas between them (0 named)"
                      % others, problems[0])
        chart, active = self.chart(), set(plan.active())
        groups = sorted(((g, [p for p in o if p in active and p not in outs]) for g, o in chart["depth"].items()),
                        key=lambda g: -len(g[1]))
        picks = [h[-1] for _, h in groups[:RULE_GROUPS] if h]
        named = [p for p in needed_inactives(self.root, self.week) if p not in picks and p not in outs][:others]
        self.write(self.answers(inactives="Standing rule, %s (coach's call), %s" % (named[0], ", ".join(named[1:]))
                                if len(named) > 1 else "Standing rule, %s (coach's call)" % named[0]))
        plan = Plan(self.root, SEASON, self.week)
        self.assertEqual(plan.problems, [])
        self.assertEqual(plan.choices["inactives"]["players"], named)
        self.assertEqual(plan.choices["inactives"]["reasons"], {named[0]: "coach's call"})
        self.assertEqual(self.check()[0], [])
        self.assertEqual(plan.inactives(), [p for p in plan.active() if p in outs] + picks + named)
        self.write(self.answers(inactives="Standing rule, " + ", ".join([picks[0]] + named[1:])))
        self.assertIn("Inactives: %s already sits by your standing rule; name another" % picks[0], self.check()[0])

    # F8: Carry Week N carries that week's list as set, whatever the chart holds now.
    def test_f8_carry_reads_the_weeks_record(self):
        from scripts.check_game_plan import Plan
        self.write(self.answers(inactives="Carry Week 5"))
        self.assertEqual(Plan(self.root, SEASON, self.week).inactives(), WEEK5_INACTIVES)

    # R7: nothing is set from the page while an exam his items wait on is still to come.
    def test_r7_the_plan_is_set_only_after_the_exams(self):
        from scripts import apply_game_plan, check_game_plan, render_game_week
        from runtime.player_bios import master_date
        queue, items = self.week_items()
        inactives = next(i for i in items if i["class"] == "game_day_inactives")
        today = master_date(self.root).isoformat()
        inactives["waits_on"] = list(inactives.get("waits_on") or []) + [
            {"what": "a test reassessment", "owner": "medical_staff", "date": today}]
        (self.root / "state/decision_queue.json").write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n",
                                                              encoding="utf-8")
        quiet(render_game_week.write, self.root)
        self.write(self.answers())
        problems, notes, _ = self.check()
        self.assertEqual(problems, [])
        self.assertTrue(any("a test reassessment" in n for n in notes))
        before = (self.root / "state/decision_queue.json").read_bytes()
        code, out = quiet(apply_game_plan.main, [str(self.week), "--season", str(SEASON), "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("GAME PLAN: COMPLETE, NOT YET SET", out)
        self.assertEqual((self.root / "state/decision_queue.json").read_bytes(), before)
        self.assertFalse(self.pages.call_sheet.exists())
        self.exams_held()
        self.apply()
        _, items = self.week_items()
        self.assertTrue(items and all(i["status"] == "RESOLVED" for i in items))
        code, out = quiet(check_game_plan.main, [str(self.week), "--season", str(SEASON), "--root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertIn("Third and short:", out)

    # Fresh: a briefing issued later shows only the exams still to come on its issue date.
    def test_still_to_come_is_as_of_the_issue_date(self):
        from datetime import timedelta
        from scripts import render_game_week
        queue, items = self.week_items()
        wk = render_game_week.Week(self.root)
        item = next(i for i in items if i["class"] == "game_day_inactives")
        item["waits_on"] = [{"what": "a past exam", "owner": "medical_staff",
                             "date": (wk.master - timedelta(days=1)).isoformat()},
                            {"what": "an exam today", "owner": "medical_staff", "date": wk.master.isoformat()}]
        (self.root / "state/decision_queue.json").write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n",
                                                              encoding="utf-8")
        wk = render_game_week.Week(self.root)
        row = next(l for l in render_game_week.briefing(wk).splitlines() if l.startswith("| Week %d inactives |" % self.week))
        self.assertIn("an exam today", row)
        self.assertNotIn("a past exam", row)
        later = render_game_week.briefing(wk, wk.master + timedelta(days=1))
        row = next(l for l in later.splitlines() if l.startswith("| Week %d inactives |" % self.week))
        self.assertTrue(row.rstrip().endswith("; nothing still to come |"), row)

    # Fresh: the week's decisions are opened by a tool, and an issued briefing needs them.
    def test_w6_6_the_weeks_items_are_opened(self):
        from scripts import open_game_week, render_career_views
        from scripts.validate_repository import validate
        path = self.root / "state/decision_queue.json"
        queue = json.loads(path.read_text(encoding="utf-8"))
        held = lambda i: any(b.get("week") == self.week and b.get("season") == SEASON for b in i.get("blocks") or ())
        queue["items"] = [i for i in queue["items"] if not (held(i) and i["class"] in
                                                            ("weekly_game_plan", "game_day_inactives"))]
        path.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        render_career_views.write(self.root)
        self.assertTrue(any("holds no game-plan item" in e for e in validate(self.root)))
        self.assertEqual(sorted(open_game_week.open_items(self.root)),
                         sorted(["%d-w%02d-game-plan" % (SEASON, self.week), "%d-w%02d-inactives" % (SEASON, self.week)]))
        self.assertEqual(open_game_week.open_items(self.root), [])

    # A variation naming a player needs him dressed.
    def test_a_variation_needs_its_player_dressed(self):
        sheet = earlier(self.week, self.root)[self.previous]
        tagged = next((c for c in sheet["offensive_call_sheet"] for t in c.get("tags") or ()
                       if "receiving" in t), None)
        if tagged is None:
            self.skipTest("no carried variation names a player")
        tag = next(t for t in tagged["tags"] if "receiving" in t)
        player = next(p["name"] for p in roster_record.players(self.roster(), ("active",))
                      if p["name"].split()[-1] == tag.split()[0])
        players = [player] + [p for p in needed_inactives(self.root, self.week) if p != player][:-1]
        self.write(self.answers(inactives=", ".join(players)))
        problems, _, _ = self.check()
        self.assertTrue(any("the variation %s needs %s, who does not dress" % (tag, player) in p for p in problems),
                        problems)


class VerifierRoundTests(OpenWeek):
    """The game week version 2 verifier round: every role holder dresses, the standing rule reads the
    page's own reorder, a new call is set with no practice record, and a same-day briefing revision is
    told apart."""

    def test_a_role_holder_must_dress(self):
        chart = self.chart()
        returner = next(p for p, roles in chart["roles"].items() if "punt_return" in roles)
        listed = needed_inactives(self.root, self.week)
        if returner in listed:
            self.skipTest("the punt returner already sits")
        named = listed[:-1] + [returner]
        self.write(self.answers(inactives=", ".join(named)))
        self.assertIn("Depth/role changes: %s holds the Punt returner role on the depth chart and does not dress (he "
                      "is on the inactives); give the role to a player who dresses (Punt returner: his name)" % returner,
                      self.check()[0])
        # A role the page gives to a player who sits is refused, never left to a fallback player.
        sitting = next(p for p in listed if any(p in order for order in chart["depth"].values()))
        self.write(self.answers(depth="Punt returner: %s" % sitting))
        self.assertIn("Depth/role changes: the Punt returner role goes to %s, who does not dress (he is on the "
                      "inactives); the role needs a player who dresses" % sitting, self.check()[0])

    def test_the_standing_rule_reads_the_pages_own_reorder(self):
        from scripts.check_game_plan import Plan, RULE_GROUPS, changed_chart, standing_inactives
        chart = self.chart()
        receivers = list(chart["depth"]["WR"])
        reordered = [receivers[0], receivers[-1]] + receivers[1:-1]
        depth = "Wide receivers order: %s" % ", ".join(reordered)
        self.write(self.answers(inactives="Standing rule", depth=depth))
        plan = Plan(self.root, SEASON, self.week)
        outs, _ = plan.outs()
        healthy = plan.needed() - len(outs)
        if healthy < RULE_GROUPS:
            self.skipTest("the standing rule does not settle this week")
        game_chart, _ = changed_chart(plan.chart, plan.choices["depth"])
        active = set(plan.active())
        groups = sorted(((g, [p for p in o if p in active and p not in outs]) for g, o in game_chart["depth"].items()),
                        key=lambda g: -len(g[1]))
        if "WR" not in [g for g, _ in groups[:RULE_GROUPS]]:
            self.skipTest("the receivers are not among the five largest healthy groups")
        picks = [h[-1] for _, h in groups[:RULE_GROUPS] if h]
        named = [p for p in needed_inactives(self.root, self.week) if p not in picks and p not in outs
                 and p not in receivers][:healthy - RULE_GROUPS]
        self.write(self.answers(inactives=", ".join(["Standing rule"] + named), depth=depth))
        players, problems = standing_inactives(Plan(self.root, SEASON, self.week))
        self.assertEqual(problems, [])
        deepest = [p for p in reordered if p in active and p not in outs][-1]
        self.assertIn(deepest, players)
        self.assertNotIn(receivers[-1], players)

    def test_a_new_call_is_set_with_no_practice_record(self):
        # The user's ruling of October 20, 2026: any call of the active book may be named; nothing waits
        # on a practice record, before game day or on it.
        from scripts import apply_game_plan
        smash = dict(calls=[["11 Trips, Smash, HALF", "third and medium", "The corner against cloud", "Off if pressed"]],
                     practice=[])
        self.write(self.answers(**smash))
        problems, notes, _ = self.check()
        self.assertEqual(problems, [])
        self.assertFalse(any("install" in n.lower() for n in notes), notes)
        self.exams_held()
        self.write(self.answers(**smash))
        self.apply()
        sheet = json.loads(self.pages.call_sheet.read_text(encoding="utf-8"))
        self.assertIn("11 Trips, Smash, HALF", [c["name"] for c in sheet["offensive_call_sheet"]])
        applied = game_plan.applied_record(self.pages.applied)
        self.assertNotIn("installs", applied["source_map"])
        self.assertFalse((self.pages.data / "practice.json").exists())
        self.assertEqual(apply_game_plan.validation_errors(self.root), [])

    def test_a_same_day_revision_is_told_apart(self):
        from scripts import render_game_week
        self.write(self.answers())
        self.assertFalse(any(p.startswith("Briefing used") for p in self.check()[0]))
        answered = render_game_week.current_issue(render_game_week.Week(self.root))
        # A staff text stored the same day changes the briefing: a new issue that day, its own revision.
        wk = render_game_week.Week(self.root)
        self.pages.staff_texts.parent.mkdir(parents=True, exist_ok=True)
        self.pages.staff_texts.write_text(json.dumps({"texts": {"central_question": {
            "author": "Mike Tice", "date": wk.master.isoformat(), "text": "Can we run the ball on the road?"}}}),
            encoding="utf-8")
        quiet(render_game_week.write, self.root)
        current = render_game_week.current_issue(render_game_week.Week(self.root))
        self.assertEqual((current[0], current[1]), (answered[0], answered[1] + 1))
        self.assertIn("Briefing used: your page answers the briefing of %s; the current briefing is %s; read it and "
                      "write it as its status line names it (your answers may stand)"
                      % (game_plan.issue_label(*answered), game_plan.issue_label(*current)), self.check()[0])
        briefing = self.pages.briefing.read_text(encoding="utf-8")
        self.assertIn("**Issued:** %s" % game_plan.issue_label(*current), briefing)
        self.assertIn("**Status:** Revised: it replaces the briefing of %s." % game_plan.issue_label(*answered), briefing)
        index = self.pages.readme.read_text(encoding="utf-8")
        self.assertIn("Issued %s" % game_plan.issue_label(*current), index)
        self.assertIn("[%s](Game_Week_Briefing_%s.md)" % (game_plan.issue_label(*answered), (
            "%s_%d" % (answered[0].strftime("%B"), answered[0].day)) + ("_%d" % answered[1] if answered[1] > 1 else "")),
            index)
        self.write(self.answers())
        self.assertFalse(any(p.startswith("Briefing used") for p in self.check()[0]))
        self.assertEqual(render_game_week.validation_errors(self.root), [])


class DocsTests(unittest.TestCase):
    def test_highlights_are_stored_in_the_data_twin(self):
        for rel in ("docs/run_week.md",):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("every rebuild keeps them", text, rel)
            self.assertIn("League_Results/week_NN.json", text, rel)
            self.assertIn("never edited by hand", text, rel)


class OffensiveWordsTests(unittest.TestCase):
    def test_every_word_is_the_active_books(self):
        from runtime import offensive_words
        mapping = json.loads((ROOT / "docs/repository_map.json").read_text(encoding="utf-8"))
        self.assertIn(offensive_words.PLAYBOOK, mapping["active_playbooks"])
        book = (ROOT / offensive_words.PLAYBOOK).read_text(encoding="utf-8")
        for label, words in offensive_words.BOOK_LISTS.items():
            for word in words:
                parts = r"[\s-]+".join(map(re.escape, word.split()))
                self.assertRegex(book, re.compile(r"(?<![0-9A-Za-z])%s(?![0-9A-Za-z])" % parts, re.I), (label, word))


class MasterDateTests(unittest.TestCase):
    """docs/run_week.md's two master-date forms read alike under every reader of the line."""

    def test_the_documented_forms_parse(self):
        from datetime import datetime
        text = (ROOT / "docs/run_week.md").read_text(encoding="utf-8")
        forms = re.findall(r"`(\| Master date/time \| [^`]+\|)`", text)
        self.assertEqual(len(forms), 2)
        for form, played in zip(forms, (False, True)):
            cell = re.search(r"\| Master date/time \| (.*?) \|", form)[1]
            by_bios = datetime.strptime(re.match(r"[A-Za-z]+ \d{1,2}, \d{4}", cell)[0], "%B %d, %Y").date()
            by_validator = datetime.strptime(cell.split(", after")[0], "%B %d, %Y").date()
            self.assertEqual(by_bios, by_validator)
            self.assertEqual(bool(re.search(r"after the Week (\d+) game", cell)), played)


if __name__ == "__main__":
    unittest.main()
