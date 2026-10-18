"""The current-job record: validation, callers by date and Document 3 parity.

Mutations run on one throwaway copy of the checkout per class; each test
restores the files it changed. Dates are the record's own or relative to the
master date and the committed sheets, never a fixed future week, and every
sheet a test writes goes into the active season's folders. The parity test
writes its own value-form Document 3 rows, so it holds whether Document 3
carries the values or pointers to the job record.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root
from runtime import current_job, decision_queue
from runtime.events import load_events, repository_map
from runtime.player_bios import master_date
from runtime.seasons import SeasonPaths

F3 = "foundation/03_Head_Coach_Organization_and_Authority_Canon.md"
# A sample sheet's content only; it is written into the active season's folders.
W5_SHEET = "career/2014/05_Regular_Season/Games/Week_05/call_sheet.json"


class CurrentJobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = repository_map(ROOT)
        cls.season = int(cls.mapping["active_season"])
        cls.events = load_events(ROOT, cls.mapping)
        cls.master = master_date(ROOT)
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup))

    def setUp(self):
        self.job = current_job.load(self.root)

    def write(self, relative, text):
        path = self.root / relative
        before = path.read_bytes() if path.exists() else None
        self.addCleanup(lambda: path.write_bytes(before) if before is not None else path.unlink(missing_ok=True))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def replace(self, relative, old, new):
        text = (self.root / relative).read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, old)
        self.write(relative, text.replace(old, new))

    def errors_with(self, job):
        self.write(str(current_job.JOB), json.dumps(job, indent=1, ensure_ascii=False))
        return current_job.validation_errors(self.root, self.mapping, self.events, self.master)

    def current(self, job):
        return current_job.appointment(job)

    def with_row(self, number, changes=None):
        """Document 3 with authority row ``number`` written in value form from
        the job record's own transcription, then ``changes`` ({column: text})
        applied; the copy's other rows are left as they are."""
        row = next(r for r in self.current(self.job)["authority"]["domains"] if r["row"] == number)
        cells = [number, row["domain"], row["final_text"], row["permitted"], row["consultation"], row["limits"],
                 row["provenance"]]
        for column, text in (changes or {}).items():
            cells[column - 1] = text
        text = (self.root / F3).read_text(encoding="utf-8")
        head, rest = text.split("## 5. Authority map", 1)
        section, tail = rest.split("### 5.1", 1)
        line = next(l for l in section.splitlines() if l.startswith("| %s |" % number))
        self.write(F3, head + "## 5. Authority map" + section.replace(line, "| " + " | ".join(cells) + " |", 1)
                   + "### 5.1" + tail)
        return current_job.f3_parity_errors(self.job, self.root)

    def club_week(self):
        """The active season's first Jacksonville week and its game date."""
        club = self.current(self.job)["employer"]["club"]
        week = min(g["week"] for g in SeasonPaths(self.season, self.root).regular_games()
                   if club in (g["away"], g["home"]))
        return week, current_job._game_date(self.job, self.season, week, self.root)

    def latest_sheet_date(self):
        """The latest game date of a committed call sheet in the active season."""
        dates = []
        for week in range(1, 22):
            if decision_queue.sheet_path(self.season, week, self.root) is not None:
                try:
                    dates.append(current_job._game_date(self.job, self.season, week, self.root))
                except (OSError, ValueError):
                    pass
        return max(dates, default=self.master)

    def test_repository_job_is_valid(self):
        self.assertEqual(current_job.validation_errors(ROOT, self.mapping, self.events, self.master), [])

    def test_callers_by_date(self):
        job = current_job.load(ROOT)
        self.assertEqual(current_job.caller_on(job, "defense", date(2014, 9, 21)), "crennel")
        self.assertEqual(current_job.caller_on(job, "defense", date(2014, 9, 28)), "stone")
        self.assertEqual(current_job.caller_on(job, "special_teams", date(2014, 2, 1)), "stone")
        self.assertEqual(current_job.caller_on(job, "special_teams", date(2014, 2, 11)), "westhoff")
        self.assertEqual(current_job.caller_on(job, "offense", date(2013, 9, 8)), "stone")
        self.assertEqual(current_job.party_name(job, "crennel"), "Romeo Crennel")
        self.assertEqual(current_job.desk_profile(job), "head_coach")

    def test_authority_rows_cover_document_3(self):
        rows = [r["row"] for r in self.current(self.job)["authority"]["domains"]]
        self.assertEqual(tuple(rows), current_job.AUTHORITY_ROWS)
        self.assertEqual(len(current_job.AUTHORITY_ROWS), 23)
        dropped = json.loads(json.dumps(self.job))
        domains = self.current(dropped)["authority"]["domains"]
        domains[:] = [r for r in domains if r["row"] != "3a"]
        self.assertTrue(any("missing 3a" in e for e in self.errors_with(dropped)))
        doubled = json.loads(json.dumps(self.job))
        domains = self.current(doubled)["authority"]["domains"]
        domains.append(dict(next(r for r in domains if r["row"] == "8")))
        self.assertTrue(any("duplicated 8" in e for e in self.errors_with(doubled)))

    def test_delegation_intervals_overlap_and_gap(self):
        overlap = json.loads(json.dumps(self.job))
        calls = self.current(overlap)["delegation"]["play_calling"]
        calls.append({"phase": "defense", "caller": "crennel", "prepares": "crennel",
                      "from": "2014-09-21", "to": "2014-10-01"})
        self.assertTrue(any("defense delegation intervals overlap or leave a gap" in e
                            for e in self.errors_with(overlap)))
        gap = json.loads(json.dumps(self.job))
        crennel = next(r for r in self.current(gap)["delegation"]["play_calling"]
                       if r["phase"] == "defense" and r["caller"] == "crennel")
        crennel["to"] = (date.fromisoformat(crennel["to"]) - timedelta(days=1)).isoformat()
        self.assertTrue(any("defense delegation intervals overlap or leave a gap" in e for e in self.errors_with(gap)))

    def test_document_3_parity(self):
        self.assertEqual(current_job.f3_parity_errors(self.job, self.root), [])
        self.assertFalse(any("authority row 8:" in e for e in self.with_row("8")))
        self.doCleanups()
        self.assertTrue(any("authority row 8:" in e and "Document 3 and the job record disagree" in e
                            for e in self.with_row("8", {3: "Caldwell"})))
        self.doCleanups()
        # A pointer inside a value-form row is not the pointer form.
        self.assertTrue(any("authority row 8: a Document 3 pointer row is exactly" in e for e in self.with_row(
            "8", {3: "[current job record](../state/current_job.json)"})))
        self.doCleanups()
        self.assertTrue(any("authority row 8: the decision domain differs" in e
                            for e in self.with_row("8", {2: "Game-day active status and inactives"})))
        self.doCleanups()
        # Column parity: a consultation right appearing in row 5's column 4
        # cannot drift from the record's normalized stone_action.
        self.assertTrue(any("authority row 5: permitted differs from Document 3 column 4" in e
                            for e in self.with_row("5", {4: "Stone is consulted."})))

    def test_document_3_points_every_row_to_the_job_record(self):
        # Each Document 3 section 5 row is one pointer cell naming its own
        # job-record row, and the pointers alone pass the parity check.
        text = (self.root / F3).read_text(encoding="utf-8")
        section = text.split("## 5. Authority map", 1)[1].split("### 5.1", 1)[0]
        rows = [l for l in section.splitlines() if re.match(r"\| \d+[a-z]? \|", l)]
        self.assertEqual([l.split(" | ", 1)[0][2:] for l in rows], list(current_job.AUTHORITY_ROWS))
        for line in rows:
            number = line.split(" | ", 1)[0][2:]
            self.assertEqual(line.count("|"), 4, line)
            self.assertTrue(line.endswith(" | %s |" % (current_job.ROW_POINTER % number)), line)
        self.assertEqual(current_job.f3_parity_errors(self.job, self.root), [])
        # Row 7 written back in its old six-cell value form, the
        # required-consultation cell missing, is caught: the record holds no
        # consultation, so the limit sits in the consultation column.
        row = next(r for r in self.current(self.job)["authority"]["domains"] if r["row"] == "7")
        self.assertIsNone(row["consultation"])
        short = "| " + " | ".join(["7", row["domain"], row["final_text"], row["permitted"], row["limits"],
                                   row["provenance"]]) + " |"
        self.replace(F3, next(l for l in rows if l.startswith("| 7 |")), short)
        self.assertTrue(any("authority row 7: consultation differs from Document 3 column 5" in e
                            for e in current_job.f3_parity_errors(self.job, self.root)))

    def test_document_3_pointers_are_exact(self):
        # Only the exact pointer forms pass. A value beside a pointer, a
        # pointer to another row, extra cells, a row or lettered subrow the
        # job record lacks, a repeated row and a section 3.1 value beside the
        # pointer each fail validation.
        text = (self.root / F3).read_text(encoding="utf-8")
        section = text.split("## 5. Authority map", 1)[1].split("### 5.1", 1)[0]
        line = next(l for l in section.splitlines() if l.startswith("| 13 |"))
        subrow = next(l for l in section.splitlines() if l.startswith("| 3a |"))
        pointer = current_job.ROW_POINTER % "13"
        contract = current_job.CONTRACT_POINTER % self.current(self.job)["id"]

        def errors(old, new):
            self.replace(F3, old, new)
            found = current_job.f3_parity_errors(self.job, self.root)
            self.doCleanups()
            return found

        exact = "authority row 13: a Document 3 pointer row is exactly"
        for changed in (line.replace(pointer, "Romeo Crennel (%s)" % pointer),
                        line.replace(pointer, "Romeo Crennel; " + pointer),
                        line.replace("row 13 |", "row 5 |"),
                        line + " Crennel is the ordinary defensive caller | x | y | z |"):
            self.assertTrue(any(exact in e for e in errors(line, changed)), changed)
        self.assertTrue(any("Document 3 section 5 row 23 has no job-record row" in e
                            for e in errors(line, line + "\n| 23 | Another domain | Alex Stone |")))
        self.assertTrue(any("Document 3 section 5 row 3b has no job-record row" in e for e in errors(
            subrow, subrow + "\n| 3b | Quarterback veto on a first-round pick | Alex Stone | Stone may veto | x | y | z |")))
        self.assertTrue(any("Document 3 section 5 lists row 13 more than once" in e
                            for e in errors(line, line + "\n" + line)))
        self.assertTrue(any("section 3.1 Employing organization points to the job record other than exactly as" in e
                            for e in errors("| Employing organization | %s |" % contract,
                                            "| Employing organization | Tennessee Titans; %s |" % contract)))
        self.assertEqual(current_job.f3_parity_errors(self.job, self.root), [])

    def test_subjects_share_one_vocabulary(self):
        job = json.loads(json.dumps(self.job))
        current = self.current(job)
        next(i for i in current["standing_instructions"] if i["subject"] == "kickoff")["subject"] = "onside"
        self.assertTrue(any("standing instruction stone-kickoff-rule-2014-week5: subject must be one of" in e
                            for e in self.errors_with(job)))
        job = json.loads(json.dumps(self.job))
        self.current(job)["delegation"]["game_management"]["decisions"][0]["id"] = "fourth-down"
        self.assertTrue(any("game-management decision id fourth-down must be one of" in e
                            for e in self.errors_with(job)))

    def test_call_sheet_caller_parity(self):
        week, on = self.club_week()
        expected = current_job.party_name(self.job, current_job.caller_on(self.job, "defense", on))
        other = "Romeo Crennel" if expected != "Romeo Crennel" else "Alex Stone"
        sheet = json.loads((ROOT / W5_SHEET).read_text(encoding="utf-8"))
        target = SeasonPaths(self.season, self.root).week_folder(week) / "call_sheet.json"
        rel = target.relative_to(self.root).as_posix()
        sheet["defensive_call_sheet"]["caller"] = expected
        self.write(rel, json.dumps(sheet))
        self.assertFalse(any("defensive caller" in e for e in self.errors_with(self.job)))
        sheet["defensive_call_sheet"]["caller"] = other
        self.write(rel, json.dumps(sheet))
        errors = current_job.validation_errors(self.root, self.mapping, self.events, self.master)
        self.assertTrue(any("%s names %s as the defensive caller" % (rel, other) in e
                            and "%s on %s" % (expected, on.isoformat()) in e for e in errors), errors)

    def test_unbuilt_role_desk(self):
        job = json.loads(json.dumps(self.job))
        self.current(job)["role"] = "coordinator"
        self.assertIn("Current job: desk for role coordinator is defined but not built", self.errors_with(job))

    def test_scheduled_change_needs_its_instruction(self):
        # After every committed sheet's game, so caller parity holds whatever
        # has been frozen ahead of the clock.
        later = (max(self.master, self.latest_sheet_date()) + timedelta(days=7)).isoformat()
        job = json.loads(json.dumps(self.job))
        calls = self.current(job)["delegation"]["play_calling"]
        last = next(r for r in calls if r["phase"] == "defense" and r["to"] is None)
        last["to"] = later
        change = {"phase": "defense", "caller": "crennel", "prepares": "crennel",
                  "instructed": self.master.isoformat(), "from": later, "to": None,
                  "record": dict(last["record"])}
        calls.append(change)
        self.assertEqual(self.errors_with(job), [])
        self.assertEqual(current_job.caller_on(job, "defense", date.fromisoformat(later)), "crennel")
        del change["instructed"]
        self.assertTrue(any("from %s is after the master date" % later in e for e in self.errors_with(job)))

    def test_undatable_postseason_sheet_is_a_named_error(self):
        sheet = json.loads((ROOT / W5_SHEET).read_text(encoding="utf-8"))
        first = 18 + (1 if self.season >= 2021 else 0)
        folder = SeasonPaths(self.season, self.root).week_folder(first, postseason=True)
        target = (folder / "call_sheet.json").relative_to(self.root).as_posix()
        self.write(target, json.dumps(sheet))
        self.addCleanup(lambda: folder.rmdir() if folder.exists() and not any(folder.iterdir()) else None)
        # A bracket without the club, whether or not the slots file exists yet.
        with patch("runtime.postseason.schedule", return_value=[]):
            errors = current_job.validation_errors(self.root, self.mapping, self.events, self.master)
        self.assertTrue(any(target in e and "cannot be dated" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
