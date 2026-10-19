"""The coach records and the pages built from them (rebuild step 3, the coach side).

Every expectation is worked out from the stored facts (the coach records, the
job record, the closed games and the master date), never typed, so the tests
hold at any later clock. Mutations run on one throwaway copy of the checkout;
each test restores the files it changed.
"""
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root
from runtime import coaches, current_job
from runtime.clean_pages import page_errors
from runtime.events import repository_map
from runtime.player_bios import master_date
from runtime.season_layout import PLAYER_FINANCES
from runtime.seasons import SeasonPaths
from scripts import render_coach_pages as pages
from scripts.render_jaguars_cap_tracker import render as render_finances, organization_staff


class CoachRecordTests(unittest.TestCase):
    def setUp(self):
        self.records = coaches.load_all(ROOT)
        self.job = current_job.load(ROOT)
        self.club = current_job.appointment(self.job)["employer"]["club"]
        self.today = master_date(ROOT)

    def test_records_are_well_formed(self):
        self.assertEqual(coaches.all_errors(ROOT), [])

    def test_every_staff_coach_has_a_hire_and_a_contract(self):
        staff = [r for r in self.records.values() if coaches.on_staff(r, self.club, self.today)]
        self.assertTrue(staff)
        for record in staff:
            with self.subTest(coach=record["name"]):
                self.assertIsNotNone(coaches.hired(record, self.club))
                terms = coaches.current_contract(record, self.club)
                self.assertIsNotNone(terms)
                self.assertTrue(terms["seasons"])

    def test_the_holder_is_the_head_coach_with_a_dated_term(self):
        holder = next(r for r in self.records.values() if r.get("party") == self.job["holder"])
        terms = current_job.contract_terms(self.job, ROOT)
        self.assertEqual(coaches.job(holder, self.club)[0], current_job.appointment(self.job)["title"])
        self.assertIsNotNone(coaches.end_date(terms))
        # Every completed term names its basis; every salary season lies inside the contract.
        for key, basis in terms["reconstructed"].items():
            self.assertTrue(basis["text"] and (ROOT / basis["source"]).is_file(), key)
        self.assertLessEqual(set(coaches.scheduled(terms)), set(terms["seasons"]))

    def test_a_departure_ends_the_scheduled_salary(self):
        for record in self.records.values():
            for leave in coaches.entries(record, "departed"):
                terms = coaches.current_contract(record, leave["club"])
                self.assertTrue(all(s <= leave["last_season"] for s in coaches.scheduled(terms)))
                self.assertFalse(coaches.on_staff(record, leave["club"], self.today))

    def test_schema_errors_are_named(self):
        record = json.loads(json.dumps(next(iter(self.records.values()))))
        record["entries"].append({"date": "2014-03", "kind": "departed", "club": self.club, "source": "nowhere.md"})
        errors = coaches.record_errors("test", record, ROOT)
        self.assertTrue(any("source missing" in e for e in errors), errors)
        self.assertTrue(any("last season his contract paid" in e for e in errors), errors)
        stone = json.loads(json.dumps(next(r for r in self.records.values() if r.get("party") == self.job["holder"])))
        amendment = next(e for e in stone["entries"] if e["kind"] == "contract_amended")
        next(iter(amendment["terms"].values()))["basis"] = {}
        self.assertTrue(any("needs its basis" in e for e in coaches.record_errors("test", stone, ROOT)))

    def test_payroll_totals_are_the_records_sums(self):
        data = json.loads((ROOT / PLAYER_FINANCES).read_text())
        years = [str(y) for y in range(data["start_year"], data["end_year"] + 1)]
        staff = organization_staff(ROOT, years)
        payroll = next(text for path, text in render_finances(data).items() if path.name == "coaching_payroll.md")
        first = years[0]
        assistants = sum(s.get(first, 0) for _, t, s in staff if t.get("job") != "Head coach")
        total = sum(s.get(first, 0) for _, _, s in staff)
        self.assertIn("| Assistant coaches | $%s |" % format(assistants, ","), payroll)
        self.assertIn("| Total | $%s |" % format(total, ","), payroll)
        self.assertEqual(page_errors("career/finances/coaching_and_organization/coaching_payroll.md", payroll,
                                     (), ROOT), [])


class CoachPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup)).resolve()
        cls.season = int(repository_map(cls.root)["active_season"])
        cls.paths = SeasonPaths(cls.season, cls.root)

    def write(self, relative, text):
        path = self.root / relative
        before = path.read_bytes() if path.exists() else None
        self.addCleanup(lambda: path.write_bytes(before) if before is not None else path.unlink(missing_ok=True))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_repository_pages_are_current_and_clean(self):
        self.assertEqual(pages.check(ROOT), [])

    def test_write_then_check_is_clean(self):
        pages.write(self.root)
        self.assertEqual(pages.check(self.root), [])

    def test_every_page_is_clean_and_its_links_resolve(self):
        for page, text in pages.build(self.root).items():
            with self.subTest(page=page):
                self.assertEqual(page_errors(page, text, (), self.root), [])
                for dest in re.findall(r"\]\(([^\s)#]+)", text):
                    if "://" not in dest:
                        self.assertTrue(((self.root / page).parent / unquote(dest)).exists(), dest)

    def test_record_by_season_matches_the_closed_games(self):
        ctx = pages.context(self.root)
        record = ctx.records[ctx.holder]
        rows = pages.season_rows(ctx, record)
        first = coaches.day(coaches.hired(record, ctx.club)["date"]).year
        lines = [pages.club_season(self.root, s, ctx.club) for s in range(ctx.season, first - 1, -1)]
        lines = [l for l in lines if l is not None]
        wins = sum(l["record"].wins for l in lines) + sum(b["regular"]["wins"] for b in record["head_coaching_before"])
        losses = sum(l["record"].losses for l in lines) + sum(b["regular"]["losses"]
                                                             for b in record["head_coaching_before"])
        self.assertEqual(rows[-1][0], "Career")
        self.assertTrue(rows[-1][3].startswith("%d-%d" % (wins, losses)))
        current = next(r for r in rows if r[0].startswith(str(ctx.season)))
        self.assertEqual(current[3], pages.record_text(lines[0]["record"]))

    def test_owed_from_today_is_the_remaining_salary(self):
        ctx = pages.context(self.root)
        terms = current_job.contract_terms(ctx.job, self.root)
        owed = sum(v for s, v in coaches.scheduled(terms).items() if s >= ctx.season)
        text = pages.build(self.root)[pages.CONTRACT_PAGE]
        section = text.split("## Owed from today", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| Total | $%s |" % format(owed, ","), section)
        if not ctx.records[ctx.holder].get("contacts"):
            self.assertIn("None recorded", text.split("## Contacts from other clubs", 1)[1])

    def test_a_changed_record_makes_the_staff_page_stale(self):
        ctx = pages.context(self.root)
        slug, record = next((s, r) for s, r in ctx.records.items()
                            if s != ctx.holder and coaches.on_staff(r, ctx.club, ctx.today))
        changed = json.loads(json.dumps(record))
        signed = coaches.entries(changed, "contract_signed")[-1]
        extra = max(signed["seasons"]) + 1
        signed["seasons"].append(extra)
        signed["salary"][str(extra)] = max(signed["salary"].values())
        self.write((coaches.folder(self.root) / ("%s.json" % slug)).relative_to(self.root).as_posix(),
                   coaches.dump(changed))
        staff = self.paths.staff_page.relative_to(self.root).as_posix()
        self.assertTrue(any(staff in e for e in pages.check(self.root)))
        self.assertIn("Through %d" % extra, pages.build(self.root)[staff])

    def test_a_departure_without_a_successor_is_an_open_job(self):
        ctx = pages.context(self.root)
        slug, record = next((s, r) for s, r in ctx.records.items()
                            if s != ctx.holder and coaches.on_staff(r, ctx.club, ctx.today)
                            and "coordinator" not in coaches.job(r, ctx.club)[0].lower())
        title = coaches.job(record, ctx.club)[0]
        changed = json.loads(json.dumps(record))
        changed["entries"].append({"date": ctx.today.isoformat(), "kind": "departed", "club": ctx.club,
                                   "to": "Released", "last_season": ctx.season,
                                   "source": changed["entries"][0]["source"]})
        self.write((coaches.folder(self.root) / ("%s.json" % slug)).relative_to(self.root).as_posix(),
                   coaches.dump(changed))
        text = pages.build(self.root)[self.paths.staff_page.relative_to(self.root).as_posix()]
        self.assertIn("- %s" % title, text.split("## Open jobs", 1)[1].split("\n## ", 1)[0])
        self.assertNotIn("| %s |" % record["name"], text.split("## Who coaches what", 1)[1].split("\n## ", 1)[0])

    def test_a_contact_appears_with_its_stage(self):
        ctx = pages.context(self.root)
        record = json.loads(json.dumps(ctx.records[ctx.holder]))
        record["contacts"] = [{"date": ctx.today.isoformat(), "club": "A test club", "job": "Head coach",
                               "stage": "permission_request", "source": record["entries"][0]["source"]}]
        self.write((coaches.folder(self.root) / ("%s.json" % ctx.holder)).relative_to(self.root).as_posix(),
                   coaches.dump(record))
        built = pages.build(self.root)
        self.assertIn("| A test club | Head coach | Permission request |", built[pages.CONTRACT_PAGE])
        self.assertIn("A test club, Head coach (Permission request)", built[pages.COACH_PAGE])


if __name__ == "__main__":
    unittest.main()
