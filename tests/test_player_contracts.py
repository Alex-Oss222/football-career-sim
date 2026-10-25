"""The permanent player contract records and the pages built from them (rebuild step 5, part B1).

Conversion proofs: ``rows()`` on the conversion day reproduces the contract inputs' players block as
it stood (pinned by its digest), the dead-money table is the old 24 rows in their order, and the
cap views come out byte-identical. Then the records' own rules: the in-season terms method,
renegotiation (F4), validation, the built players block, the contract and cap pages, the prefix
rule on the dated cap changes and the history pages' digests and anchors. A test that changes a
record works in a throwaway copy of the checkout; every synthetic entry there is test data.
"""
import copy
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import player_contracts as pc  # noqa: E402
from runtime import clean_pages  # noqa: E402
from runtime.season_layout import PLAYER_FINANCES  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from scripts import render_contract_pages as pages  # noqa: E402
from scripts import render_jaguars_cap_tracker as cap  # noqa: E402

YEAR = 2014
# The players block as it stood when the records were converted from it (the contract inputs at the
# step 5 base commit, as of September 8, 2014): its digest in canonical form, and the dead-money
# table's. The conversion is proved against these, so a later contract entry never breaks the proof.
CONVERTED_ON = date(2014, 9, 8)
PLAYERS_SHA256 = "7e53341fcd261d3e59714e4bd55f29abad4b2453d13c047485149c92f6540f41"
DEAD_MONEY_SHA256 = "e566d6a45b6ab77bc2d4fe0f0b5ef37df630bdaf90afe531c052e927f66272d7"
# The five player cap views at the base commit (the coaching payroll is built from the coach
# records and checked against its committed page by tests/test_club_pages.py).
PAGE_SHA256 = {
    "career/finances/salary_cap/cap_tracker.md": "bb5a48dc0c72e26abda4df866480a52b911505b79a061eab01244a6bf50079e2",
    "career/finances/player_contracts/contract_details.md": "989ea702f895a9b8ce9fac671fcd72d6cabd1fc30b7fc9bb8db33faa8ccb482e",
    "career/finances/upcoming_decisions/player_decisions.md": "2ee3385b917221224f73e869fa75fd2aad94fe2c6da5b1c5857f5e3271bacbe7",
    "career/finances/future_commitments/commitments.md": "f320192ed1670a5a0382869233df51e195e2e37d49f9eddb9bc269e924a39e6e",
    "career/finances/history/dead_money.md": "1afd7412cabeace3d42f61d7b48ed1fe6aabf24416c007f76d979581eb4e94ff",
}
# The three dead-money rows that belong to no player record, exactly as the inputs held them.
CLUB_ROWS = [
    {"player": "Brandon Marshall", "year": 2014, "amount": 0, "status": "reconstructed",
     "basis": "The original 2012 rookie contract ended on a 2012 waiver, before divergence. Future bonus accelerated "
              "into 2013, not 2014. Replacement active-roster deal modeled without a new bonus."},
    {"player": "Austen Lane", "year": 2014, "amount": 0, "status": "reconstructed",
     "basis": "Original four-year 2010 contract ends in 2013. The branch August 2013 waiver leaves no 2014 bonus year."},
    {"player": "Isaiah Stanback", "year": 2014, "amount": 0, "status": "simulation",
     "basis": "December 2012 practice-squad promotion modeled as a short minimum contract with no new bonus. August "
              "2013 waiver leaves no future bonus charge."},
]
IGNORED = (".git", ".sim_cache", "__pycache__", ".pytest_cache")


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def jax_games():
    return [g for g in SeasonPaths(YEAR, ROOT).regular_games() if pc.CLUB in (g["home"], g["away"])]


def copied_root(test):
    tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
    test.addClassCleanup(tmp.cleanup)
    root = Path(tmp.name) / "repo"
    root.mkdir()
    for part in ("career", "data", "library", "state", "docs"):
        shutil.copytree(ROOT / part, root / part, ignore=shutil.ignore_patterns(*IGNORED), symlinks=True)
    return root


class ConversionTests(unittest.TestCase):
    """The records reproduce what the contract inputs held, byte for byte where pages are built."""

    def test_rows_on_the_conversion_day_reproduce_the_players_block(self):
        self.assertEqual(canonical(pc.rows(ROOT, CONVERTED_ON)), PLAYERS_SHA256)

    def test_the_dead_money_table_keeps_its_rows_and_order(self):
        self.assertEqual(canonical(pc.dead_money(ROOT, on=CONVERTED_ON)), DEAD_MONEY_SHA256)
        self.assertEqual(len(pc.dead_money(ROOT, on=CONVERTED_ON)), 24)

    def test_the_three_club_level_rows_stay_as_written(self):
        self.assertEqual(pc.inputs(ROOT)["dead_money"], CLUB_ROWS)
        names = {r["name"] for r in pc.load_all(ROOT).values()}
        self.assertFalse({row["player"] for row in CLUB_ROWS} & names)

    def test_the_cap_views_come_out_byte_identical(self):
        records = pc.load_all(ROOT)
        if any(pc.day(e["date"]) > CONVERTED_ON for r in records.values() for e in r["entries"]):
            self.skipTest("a contract entry after the conversion day changes the cap views by design")
        data = json.loads((ROOT / cap.INPUT).read_text(encoding="utf-8"))
        built = {str(path): text for path, text in cap.render(data, ROOT).items()}
        for rel, digest in PAGE_SHA256.items():
            self.assertEqual(hashlib.sha256(built[rel].encode("utf-8")).hexdigest(), digest, rel)

    def test_every_player_entry_and_amendment_became_record_entries(self):
        # The records converted from the inputs (each carries ``converted`` and begins by the conversion
        # day). A player signed later (an injury replacement, a practice-squad signing, a waiver claim)
        # gets a new record without it on the next register line, so he never counts here.
        records = {rid: r for rid, r in pc.load_all(ROOT).items() if r.get("converted")}
        self.assertEqual(len(records), 90)
        self.assertEqual(sorted(r["listed"] for r in records.values()), list(range(1, 91)))
        for rid, r in records.items():
            self.assertLessEqual(min(pc.day(e["date"]) for e in r["entries"]), CONVERTED_ON, rid)
        by_name = {r["name"]: r for r in records.values()}
        # The sixteen amendments of the old inputs, by the dated entries that now carry each one's
        # player facts (the March 31 pick exchange moved no player contract).
        amendments = {
            "2014-03-11": ["Cameron Bradfield", "Toney Clemons", "Mike Brown", "Austin Pasztor", "Eugene Monroe",
                           "Sen'Derrick Marks", "Alterraun Verner", "Aqib Talib", "Brad Meester", "Brent Grimes"],
            "2014-03-14": ["Hakeem Nicks"], "2014-03-18": ["Andrew Hawkins", "Daniel Te'o-Nesheim"],
            "2014-03-19": ["Jeremy Cain"], "2014-03-20": ["Uche Nwaneri"],
            "2014-03-31": ["Cecil Shorts", "Justin Blackmon"], "2014-04-04": ["Chad Henne"],
            "2014-04-07": ["Russell Allen"], "2014-05-10": ["Andrew Norwell", "Matt Feiler"],
            "2014-05-11": ["Aaron Donald", "Joel Bitonio", "Malcolm Butler"], "2014-05-12": ["Will Rackley"],
            "2014-08-30": ["Lavar Edwards", "Jeremy Cain", "C.J. Wilson", "Cameron Bradfield", "Tyler Larsen"],
            "2014-08-31": ["Tyler Bray", "Richard Murphy", "Adrian Phillips"],
            "2014-09-08": ["Alan Ball", "Adrian Phillips"]}
        for day_, names in amendments.items():
            for name in names:
                self.assertTrue([e for e in by_name[name]["entries"]
                                 if e["date"] == day_ and e["kind"] in pc.CONTRACT_KINDS], (day_, name))
        # The two-year futures, the adopted completion terms, keep their basis (the February 28 adoption).
        basis = {(e.get("basis") or {}).get("source") for r in records.values() for e in r["entries"]}
        self.assertIn("library/2014_jaguars_contract_completion.md", basis)

    def test_the_inputs_hold_only_the_club_level_facts(self):
        # The records are the one owner of the players' contracts: the inputs keep no copy of them.
        data = pc.inputs(ROOT)
        for key in ("players", "as_of", "amendments"):
            self.assertNotIn(key, data)
        self.assertEqual(json.loads((ROOT / PLAYER_FINANCES).read_text(encoding="utf-8")), data)

    def test_the_records_validate(self):
        self.assertEqual(pc.errors(ROOT), [])


class MethodTests(unittest.TestCase):
    """The in-season terms method, stored once and computed."""

    def setUp(self):
        self.records = pc.load_all(ROOT)

    def entry(self, rid, kind="contract_signed"):
        return [e for e in self.records[rid]["entries"] if e["kind"] == kind][-1]

    def test_the_pay_weeks_come_from_the_fixtures(self):
        first = min(jax_games(), key=lambda g: g["date"])
        after = date.fromisoformat(first["date"]) + timedelta(days=1)
        weeks = len({g["week"] for g in SeasonPaths(YEAR, ROOT).regular_games()})
        self.assertEqual(pc.pay_weeks_left(YEAR, after, ROOT), (weeks - 1, weeks))
        self.assertEqual(pc.pay_weeks_left(YEAR, first["date"], ROOT), (weeks, weeks))

    def test_ball_and_phillips_hold_the_methods_terms(self):
        ball, phillips = self.entry("alan_ball"), self.entry("adrian_phillips")
        self.assertEqual(pc.computed_years(ball, ROOT), ball["years"])
        self.assertEqual(pc.computed_years(phillips, ROOT), phillips["years"])
        self.assertEqual(ball["years"]["2014"]["cap"], 804706)
        self.assertEqual(phillips["years"]["2014"]["base"], 395294)
        self.assertEqual(phillips["years"]["2014"]["cap"], 401594)
        self.assertEqual([phillips["years"][y]["cap"] for y in ("2015", "2016")], [510000, 600000])

    def test_the_minimum_and_the_practice_squad_rate_are_the_librarys(self):
        self.assertEqual(pc.minimum_salary(YEAR, 7, ROOT), 855000)
        self.assertEqual(pc.minimum_salary(YEAR, 0, ROOT), 420000)
        self.assertEqual(pc.minimum_salary(YEAR, 12, ROOT), 955000)
        self.assertEqual(pc.practice_squad_rate(YEAR, ROOT), 6300)
        squad = self.entry("tyler_bray", "practice_squad")
        self.assertEqual(pc.schedule(squad, [], ROOT)["2014"]["approximate_cap"], 107100)
        with self.assertRaisesRegex(ValueError, "no in-season terms"):
            pc.minimum_salary(YEAR + 1, 0, ROOT)


class RenegotiationTests(unittest.TestCase):
    """Article 7 section 3(k), the library's R1 and R2 (F4)."""

    def setUp(self):
        self.records = pc.load_all(ROOT)
        self.last = max(date.fromisoformat(g["date"]) for g in SeasonPaths(YEAR, ROOT).regular_games())

    def test_a_2014_drafted_rookie_is_not_renegotiable_in_october_2014(self):
        october = min(date.fromisoformat(g["date"]) for g in jax_games() if g["date"][5:7] == "10")
        answer, reason = pc.renegotiable_on(self.records["aaron_donald"], october, ROOT)
        self.assertIs(answer, False)
        self.assertIn("2016", reason)
        self.assertIs(pc.renegotiable_on(self.records["aaron_donald"], self.last + timedelta(days=1), ROOT)[0], False)

    def test_an_undrafted_rookie_after_his_second_contract_year(self):
        thielen = self.records["adam_thielen"]          # undrafted, signed with the 2013 class
        self.assertIs(pc.renegotiable_on(thielen, self.last, ROOT)[0], False)
        self.assertIs(pc.renegotiable_on(thielen, self.last + timedelta(days=1), ROOT)[0], True)

    def test_a_veteran_needs_verification_never_a_plain_yes(self):
        self.assertEqual(pc.renegotiable_on(self.records["paul_posluszny"], self.last, ROOT)[0], "needs verification")

    def test_an_ended_contract_is_not_in_force(self):
        self.assertIs(pc.renegotiable_on(self.records["lavar_edwards"], self.last, ROOT)[0], False)


class ValidationTests(unittest.TestCase):
    """Each rule fails on a broken record, judged on a copy of one record (no files written)."""

    def setUp(self):
        self.records = pc.load_all(ROOT)

    def errors_for(self, rid, record):
        return pc.record_errors(rid, record, ROOT)

    def test_a_charge_beyond_the_term_fails(self):
        record = copy.deepcopy(self.records["roy_miller"])
        signed = record["entries"][0]
        signed["years"]["2015"] = copy.deepcopy(signed["years"]["2014"])
        self.assertTrue(any("beyond the contract" in e for e in self.errors_for("roy_miller", record)))

    def test_cap_must_equal_its_components(self):
        record = copy.deepcopy(self.records["roy_miller"])
        record["entries"][0]["years"]["2014"]["cap"] += 1
        self.assertTrue(any("cap must equal" in e for e in self.errors_for("roy_miller", record)))

    def test_an_entry_without_a_source_or_with_one_that_does_not_resolve_fails(self):
        record = copy.deepcopy(self.records["roy_miller"])
        record["entries"][0].pop("source")
        self.assertTrue(any("needs" in e and "source" in e for e in self.errors_for("roy_miller", record)))
        record = copy.deepcopy(self.records["roy_miller"])
        record["entries"][0]["source"] = "career/2014/no_such_page.md"
        self.assertTrue(any("does not resolve" in e for e in self.errors_for("roy_miller", record)))

    def test_entries_out_of_date_order_fail(self):
        record = copy.deepcopy(self.records["tyler_bray"])
        record["entries"].reverse()
        self.assertTrue(any("date order" in e for e in self.errors_for("tyler_bray", record)))

    def test_an_amended_rookie_contract_before_it_may_be_renegotiated_fails(self):
        record = copy.deepcopy(self.records["aaron_donald"])
        signed = record["entries"][0]
        record["entries"].insert(1, {"kind": "contract_amended", "date": "2014-09-08", "source": signed["source"],
                                     "contract": signed["contract"], "years": {"2015": signed["years"]["2015"]},
                                     "text": "test amendment"})
        self.assertTrue(any("before it may be renegotiated" in e for e in self.errors_for("aaron_donald", record)))

    def test_two_open_contracts_fail(self):
        record = copy.deepcopy(self.records["roy_miller"])
        second = copy.deepcopy(record["entries"][0])
        second.update(contract="roy_miller_test", date="2014-09-08")
        record["entries"].insert(1, second)
        self.assertTrue(any("more than one open contract" in e for e in self.errors_for("roy_miller", record)))

    def test_a_method_contract_that_differs_from_the_method_fails(self):
        records = copy.deepcopy(self.records)
        ball = [e for e in records["alan_ball"]["entries"] if e.get("method")][0]
        ball["years"]["2014"]["base"] += 1
        ball["years"]["2014"]["cap"] += 1
        ball["years"]["2014"]["cash"] += 1
        self.assertTrue(any("in-season method" in e for e in pc.method_errors(records, ROOT)))

    def test_credited_seasons_are_read_from_the_register_and_unresolved_stays_unknown(self):
        self.assertEqual(pc.credited_seasons(self.records["richard_murphy"]), 1)
        self.assertEqual(pc.credited_seasons(self.records["adrian_phillips"]), 0)
        stated = {"credited_seasons": "Four to six (inferred; unverified)", "kind": "register",
                  "date": "2014-09-08", "source": "x"}
        record = {"entries": [stated]}
        self.assertIsNone(pc.credited_seasons(record))
        stated["credited_seasons"] = "Unresolved; verify Article 26 service separately from accrued seasons"
        self.assertIsNone(pc.credited_seasons(record))
        stated["credited_seasons"] = "4: Atlanta 2009, 2010 and late 2011"
        self.assertEqual(pc.credited_seasons(record), 4)

    def test_an_in_season_contract_below_his_minimum_fails(self):
        """A promotion re-signs the undrafted schedule, the minimum for no credited season: on a player
        with one credited season (Richard Murphy) it pays below his minimum and fails, as does an
        in-season minimum for fewer credited seasons than his record holds."""
        records = copy.deepcopy(self.records)
        murphy = records["richard_murphy"]
        day = "2014-10-14"
        # The practice-squad contract in force on the test's promotion day, and his record as it stood
        # then: a later release, promotion or signing on the live record changes neither (the cut is
        # made in the copy only; every other record is still checked as it stands).
        squad = pc.contract_on(murphy, date.fromisoformat(day), ROOT)
        self.assertEqual(squad["kind"], "practice_squad")
        murphy["entries"] = [e for e in murphy["entries"] if pc.day(e["date"]) <= date.fromisoformat(day)]
        weeks = sum(1 for _, paid in pc.pay_weeks(YEAR, ROOT) if date.fromisoformat(squad["start"]["date"]) <= paid
                    < date.fromisoformat(day))
        promoted = {"kind": "contract_signed", "date": day, "source": squad["start"]["source"],
                    "contract": "richard_murphy_%s" % day, "club": pc.CLUB,
                    "method": {"name": "promotion", "squad_weeks": weeks}}
        promoted["years"] = pc.computed_years(promoted, ROOT)
        promoted["through"] = max(int(y) for y in promoted["years"])
        self.assertIn("495,000", pc.minimum_problem(murphy, promoted, ROOT))
        murphy["entries"] += [{"kind": "contract_ended", "date": day, "source": squad["start"]["source"],
                               "contract": squad["contract"], "how": "promoted", "text": "test promotion"}, promoted]
        found = [e for e in pc.method_errors(records, ROOT) if "below the league minimum" in e]
        self.assertEqual(len(found), 1, found)
        # The in-season minimum for no credited season, on the same record, fails the same way.
        signed = dict(promoted, method={"name": "in_season_minimum", "credited_seasons": 0})
        self.assertIn("495,000", pc.minimum_problem(murphy, signed, ROOT))
        self.assertIsNone(pc.minimum_problem(murphy, dict(signed, method={"name": "in_season_minimum",
                                                                          "credited_seasons": 1}), ROOT))
        # Phillips (no credited season) was promoted on September 8 at the structure, which is his minimum.
        phillips = [e for e in self.records["adrian_phillips"]["entries"] if e.get("method")][0]
        self.assertIsNone(pc.minimum_problem(self.records["adrian_phillips"], phillips, ROOT))


class WriterTests(unittest.TestCase):
    """add_entry and the pages in a throwaway copy (test data only)."""

    @classmethod
    def setUpClass(cls):
        cls.root = copied_root(cls)

    def restore(self, *rels):
        for rel in rels:
            path = self.root / rel
            before = path.read_bytes() if path.is_file() else None
            self.addCleanup(lambda p=path, b=before: p.write_bytes(b) if b is not None else p.unlink(missing_ok=True))

    def master(self):
        from runtime.player_bios import master_date
        return master_date(self.root)

    def test_an_entry_leaves_the_pages_stale_until_they_are_rebuilt(self):
        paths = pages.page_paths(YEAR, self.root)
        record = pc.record_path(self.root, "roy_miller").relative_to(self.root).as_posix()
        self.restore(record, PLAYER_FINANCES, *paths.values(), *cap.render(pc.inputs(self.root), self.root))
        inputs_before = (self.root / PLAYER_FINANCES).read_bytes()
        on = self.master().isoformat()
        pc.add_entry(self.root, "roy_miller", {"kind": "register", "date": on,
                                               "source": "career/2014/Team_Operations/Finances/player_contracts/contract_status.md",
                                               "plan": "Test data: a register note"})
        self.assertEqual(pc.errors(self.root), [])
        self.assertTrue(any("missing or stale" in p for p in pages.check(self.root, YEAR)))
        pages.write(self.root, YEAR)
        self.assertEqual(pages.check(self.root, YEAR), [])
        self.assertEqual(pc.as_of(self.root), on)
        # The entry reaches the rows every reader takes; the club-level inputs are untouched.
        self.assertEqual(next(r for r in pc.rows(self.root) if r["name"] == "Roy Miller")["plan"],
                         "Test data: a register note")
        self.assertEqual((self.root / PLAYER_FINANCES).read_bytes(), inputs_before)

    def test_add_entry_refuses_an_earlier_date_and_a_bad_source(self):
        with self.assertRaisesRegex(ValueError, "comes before"):
            pc.add_entry(self.root, "roy_miller", {"kind": "register", "date": "2014-01-01",
                                                   "source": "career/2014/Team_Operations/Finances/player_contracts/contract_status.md"})
        with self.assertRaisesRegex(ValueError, "does not resolve"):
            pc.add_entry(self.root, "roy_miller", {"kind": "register", "date": self.master().isoformat(),
                                                   "source": "career/2014/no_such_page.md"})

    def test_a_roster_player_without_an_open_contract_fails(self):
        rid = "roy_miller"
        self.restore(pc.record_path(self.root, rid).relative_to(self.root).as_posix())
        record = pc.load(rid, self.root)
        signed = record["entries"][0]
        record["entries"].insert(1, {"kind": "contract_ended", "date": "2014-09-08", "source": signed["source"],
                                     "contract": signed["contract"], "how": "released", "text": "Test data: released"})
        pc.record_path(self.root, rid).write_text(pc.dump(record), encoding="utf-8")
        self.assertTrue(any("Roy Miller is on the roster record without an open contract" in e
                            for e in pc.errors(self.root)))

    def test_cap_changes_keep_their_bytes_and_gain_built_entries_after_them(self):
        paths = pages.page_paths(YEAR, self.root)
        rel = paths["changes"]
        recorded = (self.root / rel).read_bytes()
        length, pinned = clean_pages.history_lengths(self.root)[rel], clean_pages.history(self.root)[rel]
        # Its pre-Week-6 bytes stay exactly as recorded: the whole page until a contract changes after the
        # history closes, then the prefix the built entries follow.
        self.assertEqual(clean_pages.digest(recorded[:length]), pinned)
        self.assertEqual(clean_pages.unchecked_prefix(recorded, pinned, length), length)
        self.assertEqual(pages.changes_page(pc.load_all(self.root), pc.inputs(self.root), YEAR, self.root, paths),
                         recorded.decode("utf-8"))
        # A test release recorded the day after every real entry appends one dated line (in the copy
        # only): from the practice squad while a contract is open there, else the first open contract.
        records = pc.load_all(self.root)
        held = [(r, pc.contract_on(r, None, self.root)) for r in sorted(records.values(), key=lambda r: r["listed"])]
        held = [(r, c) for r, c in held if c is not None]
        record, contract = next((h for h in held if h[1]["kind"] == "practice_squad"), held[0])
        rid = record["player"]
        self.restore(pc.record_path(self.root, rid).relative_to(self.root).as_posix())
        last = max([pc.history_through(self.root)]
                   + [pc.day(e["date"]) for r in records.values() for e in r["entries"]])
        on = (last + timedelta(days=1)).isoformat()
        pc.add_entry(self.root, rid, {"kind": "contract_ended", "date": on, "source": contract["start"]["source"],
                                      "contract": contract["contract"], "how": "released",
                                      "text": "Test data: released"})
        built = pages.changes_page(pc.load_all(self.root), pc.inputs(self.root), YEAR, self.root, paths)
        self.assertTrue(built.startswith(recorded.decode("utf-8")))
        tail = built[len(recorded.decode("utf-8")):]
        # The dated part follows the recorded bytes (its heading is in the tail until a real entry
        # brought it), and the tail holds one dated line: the release.
        self.assertIn("## Changes from", built.encode("utf-8")[length:].decode("utf-8"))
        lines = [line for line in tail.splitlines()
                 if line.startswith("| ") and not line.startswith("| Date and completed business |")]
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("| %s: %s:" % (pc.date_words(on).rsplit(",", 1)[0], record["name"])),
                        lines[0])
        self.assertEqual(clean_pages.text_errors(rel, built, self.root), [])


class PageTests(unittest.TestCase):
    """The built pages: clean, current, every Sep 8 reconciliation figure, the history kept."""

    @classmethod
    def setUpClass(cls):
        cls.built = pages.render(ROOT, YEAR)
        cls.paths = pages.page_paths(YEAR, ROOT)

    def test_the_pages_are_current_and_clean(self):
        self.assertEqual(pages.check(ROOT, YEAR), [])
        for rel, text in self.built.items():
            if rel.endswith(".md"):
                self.assertEqual(clean_pages.text_errors(rel, text, ROOT), [], rel)

    def test_salary_cap_reproduces_the_september_8_reconciliation(self):
        worksheet = (ROOT / self.paths["worksheet"]).read_text(encoding="utf-8")
        section = worksheet.split("## September 8, 2014 reconciliation")[1]
        text = self.built[self.paths["cap"]]
        exact = {m.rstrip(",.") for m in re.findall(r"\$\d[\d,]*", section)}
        self.assertGreater(len(exact), 20)
        # Each figure is on the page's own September 8 reconciliation (its before and after are the
        # records in force on September 7 and 8, so a later entry never changes it), or in the working
        # position and the reserve charges of Mike Harris and Dwight Lowery that the page's functions
        # build from the records as of September 8: the live position and reserve lists move with
        # every later transaction.
        dated = text.split("\n### September 8, 2014\n")[1].split("\n## ")[0]
        records, data = pc.load_all(ROOT), pc.inputs(ROOT)
        then = pages.Position(records, data, YEAR, ROOT, CONVERTED_ON)
        working = pages.table(["Component", str(YEAR)], pages.position_rows(then, data), right=(1,))
        by_name = {r["name"]: r for r in then.current}
        reserve = "\n".join(pages.money(pages.charge(by_name[name]["years"][str(YEAR)]))
                            for name in ("Mike Harris", "Dwight Lowery"))
        for figure in exact:
            self.assertIn(figure, "\n".join((dated, working, reserve)), figure)
        # "about $12.63M to $13.30M" with the carryover estimate: the estimate is approximate, so the page
        # gives it and the range built on it in the worksheet's rounded form, never to the dollar.
        self.assertIn("about $12.63M to $13.30M with it", section)
        self.assertIn("(about $5.33 million to $6.00 million), not certified | about $12.63 million to $13.30 million |",
                      working)
        self.assertNotIn("$12,631,314", working + text)
        # The live page gives its current range the same rounded way, never to the dollar.
        now = pages.Position(records, data, YEAR, ROOT)
        estimate = data["team_years"][str(YEAR)]["carryover_working_estimate"]
        low, high = now.difference() + estimate["low"], now.difference() + estimate["high"]
        self.assertIn("(about %s to %s), not certified | about %s to %s |" % (
            pages.about_millions(estimate["low"]), pages.about_millions(estimate["high"]),
            pages.about_millions(low), pages.about_millions(high)), text)
        self.assertNotIn(pages.money(low), text)
        self.assertNotIn(pages.money(high), text)

    def test_the_contract_page_lists_every_player_and_the_update_log(self):
        text = self.built[self.paths["contracts"]]
        current = [r for r in pc.rows(ROOT) if not r.get("former_player")]
        for r in current:
            self.assertIn(r["name"], text)
        self.assertIn("## Update log", text)
        self.assertIn("Promoted from the practice squad September 8, 2014", text)

    def test_the_readmes_point_to_the_current_pages_first(self):
        for key, first in (("contracts_readme", "Player_Contracts.md"), ("cap_readme", "Salary_Cap.md")):
            table = self.built[self.paths[key]].split("| Open |")[1]
            self.assertIn(first, table.split("\n")[2], key)

    def test_the_history_pages_keep_their_digests_and_every_inbound_anchor_resolves(self):
        from scripts.validate_repository import anchors, link_destinations, without_code
        from urllib.parse import unquote, urlsplit
        history = clean_pages.history(ROOT)
        kept = [self.paths[k] for k in ("contract_table", "status_register", "worksheet", "changes")]
        lengths = clean_pages.history_lengths(ROOT)
        for rel in kept:
            data = (ROOT / rel).read_bytes()
            if rel == self.paths["changes"]:
                # Append-only: after the history closes the builder adds dated entries after its recorded
                # bytes, which stay exactly as recorded.
                self.assertIsInstance(lengths.get(rel), int, rel)
                self.assertGreaterEqual(len(data), lengths[rel], rel)
                self.assertEqual(clean_pages.digest(data[:lengths[rel]]), history[rel], rel)
            else:
                # The contract table, the status register and the cap worksheet are frozen: the whole file.
                self.assertEqual(clean_pages.digest(data), history[rel], rel)
        targets = {(ROOT / rel).resolve(): anchors(without_code((ROOT / rel).read_text(encoding="utf-8"))) for rel in kept}
        found = 0
        for page in (ROOT / "career").rglob("*.md"):
            for dest in link_destinations(without_code(page.read_text(encoding="utf-8"))):
                parts = urlsplit(dest)
                if parts.scheme or not parts.fragment or not parts.path:
                    continue
                target = (page.parent / unquote(parts.path)).resolve()
                if target in targets:
                    found += 1
                    self.assertIn(unquote(parts.fragment), targets[target], "%s -> %s" % (page, dest))
        self.assertGreater(found, 0)

    def test_a_week_of_inputs_never_reads_the_contract_records(self):
        import ast
        for name in ("runtime/week_inputs.py", "scripts/build_week_inputs.py", "scripts/close_week.py"):
            tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
            imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module} | \
                       {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
            self.assertFalse({m for m in imported if m and m.endswith("player_contracts")}, name)


if __name__ == "__main__":
    unittest.main()
