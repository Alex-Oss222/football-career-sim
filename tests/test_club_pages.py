"""Rebuild step 3b, the club side: the roster record, its readers, the club pages, the player cap
views and the append-only history pages. Every expectation is worked out from the stored facts;
no test names today's date or the current week."""
import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import clean_pages, roster as roster_record, week_inputs  # noqa: E402
from scripts import render_club_pages as club_pages  # noqa: E402
from runtime.season_layout import PAGE_HISTORY, PLAYER_FINANCES  # noqa: E402
from runtime.seasons import SeasonPaths, active_season, current_record  # noqa: E402

YEAR = active_season(ROOT)
PATHS = SeasonPaths(YEAR, ROOT)


def tables(text, heading):
    """The rows (lists of cells) of the first table under ``heading`` (a "## " or "### " line)."""
    lines = text.splitlines()
    start = lines.index(heading)
    rows, seen = [], False
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        if line.startswith("|"):
            seen = True
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif seen:
            break
    return rows[2:]


def name_of(cell):
    m = re.match(r"\[([^\]]+)\]\(", cell)
    return m.group(1) if m else cell


class RosterRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = roster_record.load(PATHS.roster)

    def test_the_record_is_the_season_owner_and_the_page_is_built_from_it(self):
        self.assertEqual(PATHS.roster.suffix, ".json")
        self.assertTrue(PATHS.roster.is_relative_to(PATHS.data))
        self.assertEqual(PATHS.roster_page.suffix, ".md")
        self.assertEqual(current_record("roster", ROOT), PATHS.roster)
        self.assertEqual(roster_record.errors(self.data), [])

    def test_every_reader_reads_the_record(self):
        from scripts.build_player_progression_roster import parse_current_roster
        from scripts.check_week_input_exclusivity import controlled_players_from_roster
        from runtime import player_pages, rails
        names = [p["name"] for p in self.data["players"]]
        self.assertEqual(controlled_players_from_roster(PATHS.roster), set(names))
        active = [(p["name"], p["availability"]) for p in roster_record.players(self.data, ("active",))
                  if p["status"].startswith("Active 53")]
        self.assertEqual(week_inputs.controlled_active(YEAR), active)
        _, count, players = parse_current_roster(PATHS.roster)
        self.assertEqual(count, len(roster_record.controlled(self.data)))
        self.assertEqual([p.player for p in players], [p["name"] for p in roster_record.controlled(self.data)])
        self.assertEqual(set(player_pages.roster_rows(PATHS.roster)), set(names))
        control = rails.jacksonville_control(YEAR, ROOT)
        self.assertEqual(set(control.names.values()) & set(names), set(names))

    def test_a_broken_record_fails_closed(self):
        data = copy.deepcopy(self.data)
        data["players"].append(copy.deepcopy(data["players"][0]))
        self.assertTrue(any("listed twice" in e for e in roster_record.errors(data)))
        data = copy.deepcopy(self.data)
        data["players"][0]["status"] = "Practice squad"
        self.assertTrue(any("does not belong" in e for e in roster_record.errors(data)))
        data = copy.deepcopy(self.data)
        data["players"][0]["sources"] = {}
        self.assertTrue(any("needs its source" in e for e in roster_record.errors(data)))
        data = copy.deepcopy(self.data)
        data["departures"][0].pop("year")
        self.assertTrue(roster_record.errors(data))

    def test_counts_are_worked_out_from_the_rows(self):
        n = roster_record.counts(self.data)
        self.assertEqual(n["controlled"], n["active"] + n["reserve"])
        self.assertEqual(n["active"] + n["open_active"], self.data["active_limit"])
        self.assertEqual(n["practice_squad"] + n["open_practice_squad"], self.data["practice_squad_places"])


class ClubPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = club_pages.Context(ROOT)
        cls.pages = dict(builder(cls.ctx) for builder in (club_pages.roster_page, club_pages.depth_chart_page,
                                                          club_pages.team_page))
        cls.roster_text = cls.pages[PATHS.roster_page.relative_to(ROOT).as_posix()]
        cls.chart_text = cls.pages[PATHS.record("depth_chart.md").relative_to(ROOT).as_posix()]
        cls.team_text = cls.pages[PATHS.record("team/README.md").relative_to(ROOT).as_posix()]

    def test_the_committed_pages_are_current_and_clean(self):
        self.assertEqual(club_pages.check(ROOT), [])
        for rel, text in self.pages.items():
            self.assertEqual(clean_pages.page_errors(rel, text, root=ROOT), [], rel)

    def test_the_roster_page_shows_every_player_once_in_his_group(self):
        data = self.ctx.roster
        shown = []
        groups = list(dict.fromkeys(p["group"] for p in roster_record.players(data, ("active",))))
        for group in groups:
            rows = tables(self.roster_text, "## " + group)
            self.assertEqual([name_of(r[0]) for r in rows],
                             [p["name"] for p in roster_record.players(data, ("active",)) if p["group"] == group])
            shown += rows
        for heading, lst in (("## Reserve lists", "reserve"), ("## Practice squad", "practice_squad")):
            if roster_record.players(data, (lst,)):
                shown += tables(self.roster_text, heading)
        self.assertEqual(sorted(name_of(r[0]) for r in shown), sorted(p["name"] for p in data["players"]))
        head = [l for l in self.roster_text.splitlines() if l.startswith("| Player")][0]
        self.assertEqual(head, "| Player | # | Pos | Age | Status | Availability |")
        self.assertNotIn("Role", head)

    def test_the_roster_page_follows_the_record(self):
        ctx = copy.copy(self.ctx)
        ctx.roster = copy.deepcopy(self.ctx.roster)
        gone = roster_record.players(ctx.roster, ("active",))[-1]["name"]
        ctx.roster["players"] = [p for p in ctx.roster["players"] if p["name"] != gone]
        _, text = club_pages.roster_page(ctx)
        self.assertNotIn("[%s]" % gone, text)
        n = roster_record.counts(ctx.roster)
        self.assertIn("| %d of %d |" % (n["active"], ctx.roster["active_limit"]), text)

    def test_the_depth_chart_keeps_the_game_chart_order(self):
        chart = self.ctx.chart
        for group, players in chart["depth"].items():
            if group not in club_pages.GROUP_NAMES:
                continue
            rows = tables(self.chart_text, "### " + club_pages.GROUP_NAMES[group])
            self.assertEqual([name_of(r[1]) for r in rows], players, group)
            self.assertEqual([int(r[0]) for r in rows], list(range(1, len(players) + 1)))
        heading = "## Captains, %s" % chart["captains"]["date"]
        self.assertIn(heading, self.chart_text.splitlines())
        from scripts.validate_repository import anchors
        self.assertIn("captains-august-31-2014", anchors(self.chart_text))
        log = tables(self.chart_text, "## Update log")
        self.assertEqual(len(log), len(self.ctx.log["entries"]))
        self.assertEqual([r[0] for r in log], [e["date"] for e in self.ctx.log["entries"]])

    def test_the_update_log_is_dated_and_sourced(self):
        entries = self.ctx.log["entries"]
        self.assertEqual([e["recorded"] for e in entries], sorted(e["recorded"] for e in entries))
        for e in entries:
            self.assertTrue(e["event"] and e["change"])
            for s in e["sources"]:
                self.assertTrue((ROOT / s["page"].split("#")[0]).is_file(), s)

    def test_the_team_page_is_built_from_the_game_records_and_the_job_record(self):
        games = self.ctx.games
        rows = tables(self.team_text, "## Results, %d" % YEAR)
        self.assertEqual([int(r[0]) for r in rows], [int(g["week"]) for g in games])
        wins = sum(g["final_score"][club_pages.JAX] > max(v for k, v in g["final_score"].items() if k != club_pages.JAX)
                   for g in games)
        if rows:
            self.assertTrue(rows[-1][4].startswith("%d-" % wins))
        self.assertIn("../Staff/README.md", self.team_text)
        authority = tables(self.team_text, "## Who decides what")
        self.assertTrue(authority)
        self.assertFalse(any(re.search(r"\brow\b|\b\d+a\b", " ".join(r)) for r in authority))


class AppendOnlyHistoryTests(unittest.TestCase):
    def copy_with(self, original, now):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        page = root / "career/2014/Team_Operations/Medical/medical_history.md"
        page.parent.mkdir(parents=True)
        page.write_bytes(now.encode("utf-8"))
        rel = page.relative_to(root).as_posix()
        data = original.encode("utf-8")
        (root / PAGE_HISTORY).parent.mkdir(parents=True)
        (root / PAGE_HISTORY).write_text(json.dumps({"pages": {rel: clean_pages.digest(data)},
                                                     "lengths": {rel: len(data)}}))
        return root, rel

    OLD = "# Medical history\n\nThe kernel note written before Week 6 stays as history.\n"

    def test_an_untouched_history_page_is_exempt(self):
        root, _ = self.copy_with(self.OLD, self.OLD)
        self.assertEqual(clean_pages.clean_errors(root), [])

    def test_an_appended_clean_entry_passes(self):
        root, _ = self.copy_with(self.OLD, self.OLD + "\n## A later entry\n\nTrawick cleared on his date.\n")
        self.assertEqual(clean_pages.clean_errors(root), [])
        checked = clean_pages.checked_parts(root)
        self.assertEqual(len(checked), 1)
        self.assertNotIn("kernel", checked[0][1])

    def test_an_appended_dirty_entry_fails_on_its_own_line(self):
        root, rel = self.copy_with(self.OLD, self.OLD + "\nThe engine closed the week.\n")
        errors = clean_pages.clean_errors(root)
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("%s:%d:" % (rel, self.OLD.count("\n") + 2)), errors)

    def test_an_edited_old_line_makes_the_whole_page_new(self):
        root, _ = self.copy_with(self.OLD, self.OLD.replace("stays", "stayed") + "\nA clean entry.\n")
        errors = clean_pages.clean_errors(root)
        self.assertTrue(any("kernel" in e for e in errors), errors)

    def test_the_real_history_records_every_length(self):
        self.assertEqual(set(clean_pages.history_lengths(ROOT)), set(clean_pages.history(ROOT)))


class CapViewTests(unittest.TestCase):
    def test_the_inputs_live_in_the_data_area(self):
        from scripts import render_jaguars_cap_tracker as cap
        self.assertEqual(cap.INPUT.as_posix(), PLAYER_FINANCES)
        self.assertTrue(PLAYER_FINANCES.startswith("data/"))
        self.assertTrue((ROOT / PLAYER_FINANCES).is_file())

    def test_reader_words_change_no_figure_and_no_name(self):
        from scripts.render_jaguars_cap_tracker import reader_words
        text = ("Andre Branch keeps $4.475M (simulation reconstruction); the branch trade, see the dead-money "
                "ledger (career/2014/Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md).")
        out = reader_words(text)
        self.assertIn("Andre Branch", out)
        self.assertIn("$4.475 million", out)
        self.assertNotIn("simulation", out)
        self.assertNotIn("ledger", out)
        self.assertIn("[final roster cuts](", out)
        self.assertEqual(re.findall(r"\d[\d,.]*", out.split("](")[0]), re.findall(r"\d[\d,.]*", text.split("(career")[0]))

    def test_every_player_cap_view_is_current_and_clean(self):
        from scripts import render_jaguars_cap_tracker as cap
        data = json.loads((ROOT / cap.INPUT).read_text())
        for path, text in cap.render(data, ROOT).items():
            self.assertEqual((ROOT / path).read_text(), text, path)
            if path != cap.ORGANIZATION:
                self.assertEqual(clean_pages.page_errors(str(path), text, root=ROOT), [], path)


if __name__ == "__main__":
    unittest.main()
