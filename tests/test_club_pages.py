"""Rebuild step 3b, the club side: the roster record, its readers, the club pages, the player cap
views and the append-only history pages. Every expectation is worked out from the stored facts;
no test names today's date or the current week."""
import copy
import json
import re
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

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
            rows = tables(self.chart_text, "#### " + club_pages.GROUP_NAMES[group])
            self.assertEqual([name_of(r[1]) for r in rows], players, group)
            self.assertEqual([int(r[0]) for r in rows], list(range(1, len(players) + 1)))
        self.assertIn("## Captains, %s" % chart["captains"]["date"], self.chart_text.splitlines())
        self.assertIn("## First-unit offense", self.chart_text.splitlines())
        self.assertIn("## Situational defensive roles", self.chart_text.splitlines())
        from scripts.validate_repository import anchors
        self.assertIn("captains-august-31-2014", anchors(self.chart_text))
        history_rel = self.ctx.paths.career / "Team_Operations/Team/Depth_Chart/Changes.md"
        history = history_rel.read_text(encoding="utf-8")
        log = tables(history, "## Update log")
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


class ClubPageDatingTests(unittest.TestCase):
    """The club pages follow the master date and the closed games; the roster record and the
    update log are held to their form (rebuild step 3b review fixes)."""

    def later_week(self):
        """The fixture of Jacksonville's next game after the master date and a closed result for it
        under a regenerated event id, with the master date moved to its day."""
        from runtime.player_bios import master_date
        from scripts.render_season_stats import load_receipts
        today = master_date(ROOT)
        fixture = min((g for g in PATHS.regular_games() if club_pages.JAX in (g["away"], g["home"])
                       and g["date"] > today.isoformat()), key=lambda g: g["date"])
        receipt = {"week": fixture["week"], "away": fixture["away"], "home": fixture["home"],
                   "event_id": "a-regenerated-event-id", "final_score": {fixture["away"]: 20, fixture["home"]: 13},
                   "team_stats": {fixture["away"]: {}, fixture["home"]: {}}}
        receipts = load_receipts(PATHS.receipts) + [receipt]
        patches = (mock.patch.object(club_pages, "master_date", return_value=date.fromisoformat(fixture["date"])),
                   mock.patch("scripts.render_season_stats.load_receipts", return_value=receipts))
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        return fixture, receipt

    def test_the_pages_are_dated_by_the_master_date(self):
        from runtime.player_bios import master_date
        ctx = club_pages.Context(ROOT)
        self.assertEqual(ctx.as_of, master_date(ROOT))
        self.assertTrue(all(date.fromisoformat(ctx.fixture(r)["date"]) <= ctx.as_of for r in ctx.receipts))

    def test_the_team_page_moves_when_a_later_week_closes(self):
        before = club_pages.team_page(club_pages.Context(ROOT))[1]
        fixture, receipt = self.later_week()
        ctx = club_pages.Context(ROOT)
        _, text = club_pages.team_page(ctx)
        self.assertNotEqual(text, before)
        rows = tables(text, "## Results, %d" % YEAR)
        self.assertEqual(int(rows[-1][0]), fixture["week"])
        self.assertIn("after the Week %d game" % fixture["week"], text.splitlines()[2])
        upcoming = ctx.next_game()
        if upcoming:
            self.assertIn("Next: %s." % club_pages.fixture_line(upcoming), text)
        # The roster record has not been brought up to that game, so the check fails until it is.
        self.assertTrue(any("before Jacksonville's last closed game" in e for e in club_pages.record_errors(ctx)))
        ctx.roster = dict(ctx.roster, as_of={"date": fixture["date"], "event": "after the game"})
        self.assertEqual(club_pages.record_errors(ctx), [])

    def test_the_committed_roster_record_is_not_behind_the_closed_games(self):
        self.assertEqual(club_pages.record_errors(club_pages.Context(ROOT)), [])

    def test_the_update_log_is_held_to_its_form(self):
        log = json.loads(PATHS.record("team/depth_chart/update_log.json").read_text())
        self.assertEqual(club_pages.log_errors(log, ROOT), [])
        for breaks, expected in (
                (lambda e: e.update(recorded="2014-13-01"), "ISO date"),
                (lambda e: e.update(extra="x"), "keys must be"),
                (lambda e: e.pop("sources"), "keys must be"),
                (lambda e: e.update(sources=[{"label": "x", "page": "data/a.json"}]), "under career/"),
                (lambda e: e.update(sources=[{"label": "x", "page": "career/no_such_page.md"}]), "under career/")):
            broken = copy.deepcopy(log)
            breaks(broken["entries"][-1])
            self.assertTrue(any(expected in e for e in club_pages.log_errors(broken, ROOT)), expected)
        broken = copy.deepcopy(log)
        broken["entries"][0], broken["entries"][-1] = broken["entries"][-1], broken["entries"][0]
        self.assertTrue(any("earlier than the entry before" in e for e in club_pages.log_errors(broken, ROOT)))
        broken = copy.deepcopy(log)
        broken["notes"] = "x"
        self.assertTrue(club_pages.log_errors(broken, ROOT))

    def test_the_update_log_dates_and_sources_hold(self):
        from datetime import timedelta
        from runtime.player_bios import master_date
        log = json.loads(PATHS.record("team/depth_chart/update_log.json").read_text())
        last = log["entries"][-1]
        recorded = date.fromisoformat(last["recorded"])
        later = master_date(ROOT) + timedelta(days=1)
        shown = club_pages.long_date(recorded)
        # Every shown date is built from its recorded day.
        for e in log["entries"]:
            self.assertEqual(club_pages.shown_recorded(e["date"]), date.fromisoformat(e["recorded"]), e["date"])
        for breaks, expected in (
                (lambda e: e.update(date=club_pages.long_date(recorded + timedelta(days=1))), "long form of recorded"),
                (lambda e: e.update(date="Week %s" % recorded.day), "long form of recorded"),
                (lambda e: e.update(recorded=later.isoformat(), date=club_pages.long_date(later)), "after the master date"),
                (lambda e: e.update(sources=[{"label": "x", "page": "career/../AGENTS.md"}]), "under career/"),
                (lambda e: e.update(sources=[{"label": "x", "page": "career/../../outside.md"}]), "under career/")):
            broken = copy.deepcopy(log)
            breaks(broken["entries"][-1])
            self.assertTrue(any(expected in e for e in club_pages.log_errors(broken, ROOT)), expected)
        # The long form of the recorded day, a window ending on it and a source that normalizes into
        # career/ all hold.
        window = "%s 1 to %d, %d" % (recorded.strftime("%B"), recorded.day, recorded.year)
        for change in ({"date": shown}, {"date": window if recorded.day > 1 else shown},
                       {"sources": [{"label": "x", "page": "career/%d/../%d/Record.md" % (YEAR, YEAR)}]}):
            fine = copy.deepcopy(log)
            fine["entries"][-1].update(change)
            self.assertEqual(club_pages.log_errors(fine, ROOT), [], change)

    def test_reworded_entries_keep_their_original_words(self):
        for e in json.loads(PATHS.record("team/depth_chart/update_log.json").read_text())["entries"]:
            if "as_written" in e:
                self.assertNotEqual((e["date"], e["event"], e["change"]),
                                    tuple(e["as_written"][k] for k in ("date", "event", "change")))
        rows = [p for p in roster_record.load(PATHS.roster)["players"] + roster_record.load(PATHS.roster)["departures"]
                if "as_written" in p]
        for row in rows:
            self.assertTrue(all(row[k] != v for k, v in row["as_written"].items()))

    def test_the_team_page_speaks_plain_football(self):
        _, text = club_pages.team_page(club_pages.Context(ROOT))
        for phrase in ("Not set", "recruiting", "Professional trades", "team and program budget", "(open)", "N/A"):
            self.assertNotIn(phrase, text)
        self.assertIn("Supplies information", " ".join(" ".join(r) for r in tables(text, "## Who decides what")))
        self.assertIn("Employed by the Jacksonville Jaguars; employment decided by", text)
        _, roster = club_pages.roster_page(club_pages.Context(ROOT))
        self.assertNotIn("N/A", roster)

    def test_group_names_take_a_small_letter_inside_a_phrase(self):
        ctx = club_pages.Context(ROOT)
        parties = ctx.job.get("parties") or {}
        _, text = club_pages.team_page(ctx)
        rows = {r[0]: r[1] for r in tables(text, "## Who decides what")}
        checked = 0
        current = club_pages.current_job.appointment(ctx.job) or {}
        for d in (current.get("authority") or {}).get("domains", ()):
            label = club_pages.DECISIONS.get(d["domain"])
            if label not in rows:
                continue
            for pid in d["final"][1:]:
                if (parties.get(pid) or {}).get("kind") == "group":
                    name = parties[pid]["name"]
                    self.assertIn(name[:1].lower() + name[1:], rows[label])
                    self.assertNotIn(" and " + name, rows[label])
                    checked += 1
        self.assertTrue(checked)


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

    def test_an_appended_entry_keeps_its_event_record_line(self):
        from runtime.events import EVENT_META
        marker = ('<!-- event-record: {"date": "2014-10-06", "id": "2014-10-06-christian-jones-cleared", '
                  '"status": "closed", "summary": "Christian Jones was reassessed October 6 and cleared on his '
                  'projected date; the engine generated no new restriction."} -->')
        self.assertTrue(EVENT_META.fullmatch(marker))
        entry = "\n%s\n\n## October 6: Christian Jones cleared\n\nJones cleared on his projected date.\n" % marker
        root, _ = self.copy_with(self.OLD, self.OLD + entry)
        self.assertEqual(clean_pages.clean_errors(root), [])
        # Only a whole line is the invisible marker; one inside a line of text is markup.
        root, _ = self.copy_with(self.OLD, self.OLD + "\nJones cleared. " + marker + "\n")
        self.assertTrue(any("markup" in e for e in clean_pages.clean_errors(root)))

    def test_titled_links_and_reference_definitions_to_system_files_fail(self):
        rel = "career/2014/Team_Operations/Medical/medical_history.md"
        for line in ('[the inputs](../../../../data/2014/x.json "Inputs")', "[inputs]: ../../../../data/2014/x.json",
                     "[runner]: ../../../../scripts/close_week.py 'Runner'", "[a](../x.csv (title))"):
            self.assertTrue(any("link to a system file" in e for e in clean_pages.page_errors(rel, line, root=ROOT)), line)
        self.assertEqual(clean_pages.page_errors(rel, '[the record](medical_history.md "The record")', root=ROOT), [])
        # The repository's link check sees the same forms.
        from scripts.validate_repository import link_destinations
        self.assertEqual(sorted(link_destinations('[a](one.md "t")\n[b]: two.md "T"\n[c](three.md)\n[^1]: Note.\n')),
                         ["one.md", "three.md", "two.md"])

    def test_a_marker_line_holds_exactly_one_marker(self):
        marker = '<!-- event-record: {"date": "2014-10-06", "id": "2014-10-06-a-test-event", "status": "closed"} -->'
        rel = "career/2014/Team_Operations/Medical/medical_history.md"
        self.assertEqual(clean_pages.page_errors(rel, marker, root=ROOT), [])
        for line in (marker + " The engine closed it. " + marker, marker + " " + marker, marker + " Jones cleared."):
            errors = clean_pages.page_errors(rel, line, root=ROOT)
            self.assertTrue(any("markup" in e for e in errors), line)
        root, _ = self.copy_with(self.OLD, self.OLD + "\n%s Jones cleared. %s\n" % (marker, marker))
        self.assertTrue(any("markup" in e for e in clean_pages.clean_errors(root)))

    def test_angle_and_spaced_link_destinations_to_system_files_fail(self):
        rel = "career/2014/Team_Operations/Medical/medical_history.md"
        for line in ("[the inputs](<../../../../data/2014/x.json>)", "[the inputs]( ../../../../data/2014/x.json )",
                     '[the inputs](<../../../../data/2014/a file.json> "Inputs")', "[runner]: <../../../../scripts/a.py>",
                     "[inputs]: <../../../../data/2014/a file.json> 'Inputs'", "[x](  ../x.csv  )"):
            self.assertTrue(any("link to a system file" in e for e in clean_pages.page_errors(rel, line, root=ROOT)), line)
        for line in ("[the record](<medical_history.md>)", "[the record]( medical_history.md )"):
            self.assertEqual(clean_pages.page_errors(rel, line, root=ROOT), [], line)
        # The repository's link check reads the same destinations, without the brackets and spaces.
        from scripts.validate_repository import link_destinations
        self.assertEqual(sorted(link_destinations("[a](<one two.md>)\n[b]( three.md )\n[c]: <four.md> 'T'\n"
                                                  "[d](<five.md> \"t\")\n")),
                         ["five.md", "four.md", "one two.md", "three.md"])

    def test_the_page_history_map_is_pinned(self):
        from runtime.season_layout import PAGE_HISTORY_SHA256
        self.assertEqual(clean_pages.history_pin_errors(ROOT), [])
        self.assertEqual(clean_pages.digest((ROOT / PAGE_HISTORY).read_bytes()), PAGE_HISTORY_SHA256)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = json.loads((ROOT / PAGE_HISTORY).read_text())
            data["pages"]["career/2014/a_new_page.md"] = clean_pages.digest(b"x")
            (root / PAGE_HISTORY).parent.mkdir(parents=True)
            (root / PAGE_HISTORY).write_text(json.dumps(data))
            self.assertTrue(any("changed without its pin" in e for e in clean_pages.history_pin_errors(root)))
            (root / PAGE_HISTORY).write_bytes((ROOT / PAGE_HISTORY).read_bytes())
            self.assertEqual(clean_pages.history_pin_errors(root), [])


class BuiltRosterPageRefusalTests(unittest.TestCase):
    def test_every_markdown_roster_reader_refuses_the_built_page(self):
        from scripts.check_week_input_exclusivity import controlled_players_from_roster
        from runtime import rails
        page = PATHS.roster_page
        for read in (lambda: week_inputs.controlled_active(YEAR, roster_path=page),
                     lambda: controlled_players_from_roster(page), lambda: rails._roster_tables(page)):
            with self.assertRaisesRegex(ValueError, "no plain player rows"):
                read()


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

    def test_the_contract_pages_name_their_research_in_plain_words(self):
        from scripts import render_jaguars_cap_tracker as cap
        note = "pick 13 in the nflverse/OTC historical contracts file, $10,136,500 total"
        out = cap.reader_words(note)
        self.assertEqual(out, "pick 13 in the historical contract records, $10,136,500 total")
        data = json.loads((ROOT / cap.INPUT).read_text())
        for path, text in cap.render(data, ROOT).items():
            self.assertNotIn("nflverse", text, path)
        readme = (ROOT / "career/finances/README.md").read_text(encoding="utf-8")
        self.assertNotRegex(readme, r"(?i)\bmaintenance\b")


if __name__ == "__main__":
    unittest.main()
