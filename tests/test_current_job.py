"""The current-job record: validation, callers by date and Document 3 parity.

Mutations run on one throwaway copy of the checkout per class; each test
restores the files it changed. Dates are the record's own or relative to the
master date, never a fixed future week.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root
from runtime import current_job
from runtime.events import load_events, repository_map
from runtime.player_bios import master_date
from runtime.seasons import SeasonPaths

F3 = "foundation/03_Head_Coach_Organization_and_Authority_Canon.md"
W5_SHEET = "career/2014/05_Regular_Season/Games/Week_05/call_sheet.json"


class CurrentJobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = repository_map(ROOT)
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
        row8 = "| 8 | Game-day active status, elevations, and inactives | Stone |"
        self.assertEqual(current_job.f3_parity_errors(self.job, self.root), [])
        self.replace(F3, row8, "| 8 | Game-day active status, elevations, and inactives | Caldwell |")
        self.assertTrue(any("authority row 8:" in e and "Document 3 and the job record disagree" in e
                            for e in current_job.f3_parity_errors(self.job, self.root)))
        self.doCleanups()
        self.replace(F3, row8, "| 8 | Game-day active status, elevations, and inactives | "
                               "[current job record](../state/current_job.json) |")
        self.assertFalse(any("authority row 8:" in e for e in current_job.f3_parity_errors(self.job, self.root)))
        self.doCleanups()
        self.replace(F3, row8, "| 8 | Game-day active status and inactives | Stone |")
        self.assertTrue(any("authority row 8: the decision domain differs" in e
                            for e in current_job.f3_parity_errors(self.job, self.root)))
        self.doCleanups()
        # Column parity: a consultation right appearing in row 5's column 4
        # cannot drift from the record's normalized stone_action.
        self.replace(F3, "| 5 | Player contract negotiation and execution | Caldwell | [UNSET] |",
                     "| 5 | Player contract negotiation and execution | Caldwell | Stone is consulted. |")
        self.assertTrue(any("authority row 5: permitted differs from Document 3 column 4" in e
                            for e in current_job.f3_parity_errors(self.job, self.root)))

    def test_call_sheet_caller_parity(self):
        self.assertFalse(any("defensive caller" in e for e in self.errors_with(self.job)))
        self.replace(W5_SHEET, '"caller": "Alex Stone"', '"caller": "Romeo Crennel"')
        errors = current_job.validation_errors(self.root, self.mapping, self.events, self.master)
        self.assertTrue(any("Week_05/call_sheet.json names Romeo Crennel as the defensive caller" in e
                            and "Alex Stone on 2014-10-05" in e for e in errors))

    def test_unbuilt_role_desk(self):
        job = json.loads(json.dumps(self.job))
        self.current(job)["role"] = "coordinator"
        self.assertIn("Current job: desk for role coordinator is defined but not built", self.errors_with(job))

    def test_scheduled_change_needs_its_instruction(self):
        later = (self.master + timedelta(days=7)).isoformat()
        job = json.loads(json.dumps(self.job))
        calls = self.current(job)["delegation"]["play_calling"]
        last = next(r for r in calls if r["phase"] == "defense" and r["to"] is None)
        last["to"] = later
        change = {"phase": "defense", "caller": "crennel", "prepares": "crennel",
                  "instructed": self.master.isoformat(), "from": later, "to": None,
                  "record": dict(last["record"])}
        calls.append(change)
        self.assertEqual(self.errors_with(job), [])
        self.assertEqual(current_job.caller_on(job, "defense", self.master + timedelta(days=7)), "crennel")
        del change["instructed"]
        self.assertTrue(any("from %s is after the master date" % later in e for e in self.errors_with(job)))

    def test_undatable_postseason_sheet_is_a_named_error(self):
        sheet = json.loads((ROOT / W5_SHEET).read_text(encoding="utf-8"))
        folder = SeasonPaths(2014, self.root).week_folder(18, postseason=True)
        target = (folder / "call_sheet.json").relative_to(self.root).as_posix()
        self.write(target, json.dumps(sheet))
        self.addCleanup(lambda: folder.rmdir() if folder.exists() and not any(folder.iterdir()) else None)
        errors = current_job.validation_errors(self.root, self.mapping, self.events, self.master)
        self.assertTrue(any(target in e and "cannot be dated" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
