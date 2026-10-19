"""The coach records and the pages built from them (rebuild step 3, the coach side).

Every expectation is worked out from the stored facts (the coach records, the
job record, the closed games and the master date), never typed, so the tests
hold at any later clock. Mutations run on one throwaway copy of the checkout;
each test restores the files it changed.
"""
from datetime import timedelta
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

    def test_every_history_item_and_fact_names_an_existing_source(self):
        for slug, record in self.records.items():
            for key in coaches.HISTORY_KEYS:
                for item in record.get(key) or ():
                    with self.subTest(coach=slug, item=item):
                        self.assertTrue((ROOT / item["source"]).is_file())
        stone = next(r for r in self.records.values() if r.get("party") == self.job["holder"])
        broken = json.loads(json.dumps(stone))
        broken["education"][0].pop("source")
        self.assertTrue(any("education item" in e for e in coaches.record_errors("test", broken, ROOT)))

    def test_entry_keys_are_closed_and_salary_is_required(self):
        slug, record = next((s, r) for s, r in self.records.items() if r.get("party") != self.job["holder"]
                            and coaches.on_staff(r, self.club, self.today))
        broken = json.loads(json.dumps(record))
        signed = coaches.entries(broken, "contract_signed")[-1]
        signed["salaries"] = signed.pop("salary")
        errors = coaches.record_errors(slug, broken, ROOT)
        self.assertTrue(any("missing salary" in e and "unknown salaries" in e for e in errors), errors)
        # A signed contract may state no salary, but the key must be there.
        signed["salary"] = None
        signed.pop("salaries")
        self.assertEqual(coaches.record_errors(slug, broken, ROOT), [])

    def test_amendments_apply_in_in_world_order(self):
        stone = json.loads(json.dumps(next(r for r in self.records.values() if r.get("party") == self.job["holder"])))
        signed = coaches.entries(stone, "contract_signed")[0]
        reconstruction = next(e for e in coaches.entries(stone, "contract_amended") if e.get("reconstruction"))
        self.assertLess(coaches.day(reconstruction["in_world"]), coaches.day(reconstruction["recorded"]))
        last = max(signed["seasons"])
        raise_from = last - 1
        extension = {"in_world": "%d-06-01" % raise_from, "recorded": reconstruction["recorded"],
                     "kind": "contract_amended", "contract": signed["contract"], "source": signed["source"],
                     "terms": {"seasons": signed["seasons"] + [last + 1, last + 2],
                               "salary": {str(s): 5000000 for s in (raise_from, last, last + 1, last + 2)},
                               "end": {"date": "%d-01-31" % (last + 3), "text": "After the %d season" % (last + 2)}}}
        # Written before the reconstruction in the list, the extension still applies after it.
        stone["entries"].insert(stone["entries"].index(reconstruction), extension)
        terms = coaches.contract(stone, signed["contract"])
        self.assertEqual([a["in_world"] for a in terms["amended"]],
                         sorted(a["in_world"] for a in terms["amended"]))
        self.assertEqual(coaches.through_season(terms), last + 2)
        self.assertEqual(coaches.end_date(terms), "%d-01-31" % (last + 3))
        first = min(signed["seasons"])
        self.assertEqual(coaches.scheduled(terms)[first], reconstruction["terms"]["salary"]["value"][str(first)])
        self.assertEqual(coaches.scheduled(terms)[last + 2], 5000000)
        self.assertNotIn("end", terms["reconstructed"])          # the signed extension replaced it
        self.assertIn("salary", terms["reconstructed"])          # the earlier seasons are still completed
        self.assertIn("entries must be in date order", " ".join(coaches.record_errors("test", stone, ROOT)))
        stone["entries"].remove(extension)
        stone["entries"].append(extension)
        self.assertEqual(coaches.record_errors("test", stone, ROOT), [])

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


class PayrollTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / PLAYER_FINANCES).read_text())
        self.years = [str(y) for y in range(self.data["start_year"], self.data["end_year"] + 1)]

    def payroll(self, root=ROOT):
        from scripts.render_jaguars_cap_tracker import render_organization
        return render_organization(self.data, self.years, root)

    def test_dated_by_the_latest_contract_change(self):
        staff = organization_staff(ROOT, self.years)
        entries = [e for r, _, _ in staff for e in coaches.entries(r) if e["kind"].startswith("contract_")]
        latest = max(entries, key=lambda e: coaches.day(coaches.when(e)))
        self.assertIn("latest contract change, %s." % coaches.date_text(latest), self.payroll())

    def test_guarantee_sentence_names_every_open_season(self):
        text = self.payroll()
        for record, terms, _ in organization_staff(ROOT, self.years):
            if terms.get("job") != "Head coach" and coaches.open_seasons(terms):
                self.assertIn("%s's %s salary" % (record["name"], coaches.years_text(coaches.open_seasons(terms))), text)

    def test_completed_terms_name_each_basis(self):
        text = self.payroll()
        for record, terms, _ in organization_staff(ROOT, self.years):
            for source, _ in coaches.completed(terms):
                self.assertIn("from %s" % source, text)


class GuardTests(unittest.TestCase):
    """Each guard fails on a broken record in a throwaway copy."""

    @classmethod
    def setUpClass(cls):
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup)).resolve()

    def change(self, slug, record=None):
        path = coaches.folder(self.root) / ("%s.json" % slug)
        before = path.read_bytes()
        self.addCleanup(path.write_bytes, before)
        if record is None:
            path.unlink()
        else:
            path.write_text(coaches.dump(record), encoding="utf-8")

    def staff_coach(self, delegated):
        job = current_job.load(self.root)
        named = {r.get(k) for r in current_job.appointment(job)["delegation"]["play_calling"]
                 for k in ("caller", "prepares", "transmits")} - {None}
        return next((s, r) for s, r in coaches.load_all(self.root).items()
                    if (r.get("party") in named) == delegated and r.get("party") != job["holder"]
                    and coaches.employed(r, current_job.appointment(job)["employer"]["club"]))

    def job_errors(self):
        from runtime.events import load_events
        mapping = repository_map(self.root)
        return current_job.validation_errors(self.root, mapping, load_events(self.root, mapping),
                                             master_date(self.root))

    def test_a_renamed_salary_fails_the_payroll(self):
        slug, record = self.staff_coach(False)
        broken = json.loads(json.dumps(record))
        signed = coaches.entries(broken, "contract_signed")[-1]
        signed["salaries"] = signed.pop("salary")
        self.change(slug, broken)
        data = json.loads((self.root / PLAYER_FINANCES).read_text())
        years = [str(y) for y in range(data["start_year"], data["end_year"] + 1)]
        with self.assertRaisesRegex(ValueError, record["name"]):
            organization_staff(self.root, years)
        self.assertTrue(any("unknown salaries" in e for e in coaches.all_errors(self.root)))

    def test_a_deleted_caller_record_fails(self):
        slug, record = self.staff_coach(True)
        self.change(slug)
        self.assertTrue(any("required coach record is missing" in e for e in coaches.all_errors(self.root)))
        self.assertTrue(any("%s," % record["party"] in e and "no coach record" in e for e in self.job_errors()))

    def test_a_departed_current_caller_fails(self):
        slug, record = self.staff_coach(True)
        club = current_job.appointment(current_job.load(self.root))["employer"]["club"]
        broken = json.loads(json.dumps(record))
        hire = coaches.hired(broken, club)
        broken["entries"].append({"date": hire["date"], "kind": "departed", "club": club, "to": "Released",
                                  "last_season": coaches.day(hire["date"]).year, "source": hire["source"]})
        self.change(slug, broken)
        self.assertTrue(any("is not on the" in e for e in self.job_errors()), self.job_errors())

    def test_an_unlisted_record_fails(self):
        slug, record = self.staff_coach(False)
        extra = json.loads(json.dumps(record))
        extra.pop("party", None)
        path = coaches.folder(self.root) / "an_unlisted_coach.json"
        self.addCleanup(path.unlink, missing_ok=True)
        path.write_text(coaches.dump(extra), encoding="utf-8")
        self.assertTrue(any("an_unlisted_coach.json: a coach record not listed" in e
                            for e in coaches.all_errors(self.root)))

    def test_a_record_whose_name_is_not_its_party_fails(self):
        slug, record = self.staff_coach(True)
        broken = dict(record, name="Someone Else")
        self.change(slug, broken)
        self.assertTrue(any("coach record %s is Someone Else" % slug in e for e in self.job_errors()))


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

    def test_both_pages_carry_the_same_terms_line(self):
        ctx = pages.context(self.root)
        terms = current_job.contract_terms(ctx.job, self.root)
        built = pages.build(self.root)
        for page in (pages.COACH_PAGE, pages.CONTRACT_PAGE):
            line = pages.terms_line(ctx, terms, page)
            self.assertIn(line, built[page])
            for source, keys in coaches.completed(terms):
                self.assertIn("Completed from %s: %s." % (source, pages.join(pages.TERM_NAMES[k] for k in keys)), line)
        coach = built[pages.COACH_PAGE]
        self.assertLess(coach.index("## Job and contract"), coach.index(pages.terms_line(ctx, terms, pages.COACH_PAGE)))
        self.assertLess(coach.index(pages.terms_line(ctx, terms, pages.COACH_PAGE)), coach.index("## Record by season"))

    def test_coded_and_real_world_anchors_are_not_linked(self):
        today = master_date(self.root)
        self.assertIsNone(pages.football_anchor("entry-3-the-clubs-decision", today))
        self.assertIsNone(pages.football_anchor("august-31-2014-the-week-1-inactives-stone-document-3-row-8", today))
        self.assertIsNone(pages.football_anchor("addendum-%d-the-rule" % (today.year + 12), today))
        self.assertEqual(pages.football_anchor("who-calls-what", today), "who-calls-what")
        text = pages.build(self.root)[pages.COACH_PAGE]
        self.assertNotRegex(text, r"\]\([^)]*#[^)]*(entry|row|document)-\d")

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


class ContractDateTests(unittest.TestCase):
    """An amendment applies only from its in-world date: a page built for an earlier day never
    shows it, validation refuses one dated after the master date, and a contract's salary covers
    every season of its term (rebuild step 3b, last fixes)."""

    @classmethod
    def setUpClass(cls):
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup)).resolve()

    def setUp(self):
        self.job = current_job.load(self.root)
        self.slug, record = next((s, r) for s, r in coaches.load_all(self.root).items()
                                 if r.get("party") == self.job["holder"])
        self.stone = json.loads(json.dumps(record))
        self.signed = coaches.entries(self.stone, "contract_signed")[0]
        self.last = max(self.signed["seasons"])
        self.today = master_date(self.root)

    def extension(self, on):
        """A one-season extension at a new salary, in force from day ``on``."""
        recorded = next(e for e in coaches.entries(self.stone, "contract_amended"))["recorded"]
        return {"in_world": on.isoformat(), "recorded": recorded, "kind": "contract_amended",
                "contract": self.signed["contract"], "source": self.signed["source"],
                "terms": {"seasons": self.signed["seasons"] + [self.last + 1],
                          "salary": {str(self.last + 1): 5000000},
                          "end": {"date": "%d-01-31" % (self.last + 2), "text": "After the %d season" % (self.last + 1)}}}

    def write(self, record):
        path = coaches.folder(self.root) / ("%s.json" % self.slug)
        before = path.read_bytes()
        self.addCleanup(path.write_bytes, before)
        path.write_text(coaches.dump(record), encoding="utf-8")

    def payroll(self):
        from scripts.render_jaguars_cap_tracker import render_organization
        data = json.loads((self.root / PLAYER_FINANCES).read_text())
        years = [str(y) for y in range(data["start_year"], data["end_year"] + 1)]
        self.assertIn(str(self.last + 1), years)
        return render_organization(data, years, self.root)

    def test_a_later_amendment_does_not_apply_before_its_day(self):
        later = self.today + timedelta(days=1)
        self.stone["entries"].append(self.extension(later))
        cid = self.signed["contract"]
        self.assertEqual(coaches.through_season(coaches.contract(self.stone, cid, self.today)), self.last)
        self.assertEqual(coaches.through_season(coaches.contract(self.stone, cid, later)), self.last + 1)
        self.assertEqual(coaches.through_season(coaches.contract(self.stone, cid)), self.last + 1)
        self.write(self.stone)
        built = pages.build(self.root)
        contract = built[pages.CONTRACT_PAGE].split("## Salary by season", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("| %d |" % (self.last + 1), contract)
        staff = built[SeasonPaths(int(repository_map(self.root)["active_season"]), self.root)
                      .staff_page.relative_to(self.root).as_posix()]
        self.assertNotIn("Through %d" % (self.last + 1), staff)
        self.assertNotIn("$5,000,000", self.payroll())
        self.assertIsNone(current_job.term(self.job, self.root, self.today)["contract"]["salary"].get(str(self.last + 1)))
        # Validation refuses an amendment the career has not reached.
        self.assertTrue(any("after the master date" in e for e in coaches.all_errors(self.root)))

    def test_an_amendment_on_the_page_day_applies(self):
        self.stone["entries"].append(self.extension(self.today))
        self.write(self.stone)
        self.assertFalse(any("after the master date" in e for e in coaches.all_errors(self.root)))
        built = pages.build(self.root)
        contract = built[pages.CONTRACT_PAGE].split("## Salary by season", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| %d | $5,000,000 |" % (self.last + 1), contract)
        self.assertIn("$5,000,000", self.payroll())

    def test_a_signed_salary_covers_every_season(self):
        slug, record = next((s, r) for s, r in coaches.load_all(self.root).items()
                            if r.get("party") != self.job["holder"]
                            and (coaches.entries(r, "contract_signed")[-1].get("salary") or {}))
        broken = json.loads(json.dumps(record))
        signed = coaches.entries(broken, "contract_signed")[-1]
        dropped = str(max(signed["seasons"]))
        signed["salary"].pop(dropped)
        errors = coaches.record_errors(slug, broken, self.root)
        self.assertTrue(any("salary for every season" in e and "missing %s" % dropped in e for e in errors), errors)
        signed["salary"][dropped] = None
        self.assertTrue(any("whole number of dollars" in e for e in coaches.record_errors(slug, broken, self.root)))
        # Null stays allowed for a salary the signed contract did not state at all.
        signed["salary"] = None
        self.assertEqual(coaches.record_errors(slug, broken, self.root), [])

    def test_an_amended_salary_covers_every_season(self):
        extension = self.extension(self.today)
        extension["terms"]["salary"] = {}
        self.stone["entries"].append(extension)
        errors = coaches.record_errors(self.slug, self.stone, self.root)
        self.assertTrue(any("as amended needs a salary for every season" in e and "missing %d" % (self.last + 1) in e
                            for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
