"""`--check` of the in-season rails builder (scripts/research/build_2014_inseason_rails.py).

The builder's IO is mocked as in tests/test_inseason_rails.py: a temporary
directory stands in for the committed data directory, a synthetic source
and identity stand in for the downloaded research, and the replay labelling
is stubbed. Every record checked here is first written by the builder
itself (a first build, then an extension), so each check compares against
what the builder writes.
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts.research import build_2014_inseason_rails as builder

WIRE = "https://www.nfl.com/transactions/league/signings/2014/%d"


def raw(gate, club, uid, name, kind="fa_signing", outcome="APPLY"):
    return {"gate_date": gate, "real_date": gate, "date_basis": "two_sources_same_day", "club": club, "kind": kind,
            "kind_basis": "wire", "counterparty": None, "player": name, "uid": uid, "identity_basis": "research",
            "outcome": outcome, "reason": "", "verification": "two sources", "sources": ["nfl_wire", "espn"],
            "source_pages": ["page-" + uid], "research_ref": "X-" + uid}


FIRST = [raw("2014-09-20", "AAA", "90-0000001", "First Player"),
         raw("2014-09-25", "BBB", "90-0000002", "Hurt Player", "injury_reserve", "NOT_APPLIED_INJURY"),
         raw("2014-09-27", "CCC", "90-0000003", "Third Player", "waived")]
OCTOBER = FIRST + [raw("2014-09-26", "AAA", "90-0000004", "Late Found"),  # gated before the first as-of date
                   raw("2014-10-01", "BBB", "90-0000005", "October Player"),
                   raw("2014-10-03", "CCC", "90-0000006", "Another Player", "waived")]
LATER = OCTOBER + [raw("2014-10-08", "AAA", "90-0000007", "Next Week")]
LATE_FOUND = OCTOBER + [raw("2014-09-29", "BBB", "90-0000008", "Found Since")]
SOURCES = {"S1": ("h1", FIRST), "S2": ("h2", OCTOBER), "S3": ("h3", LATER), "S4": ("h4", LATE_FOUND)}


class FakeIdentity:
    """The parts of builder.Identity that finish() and number() use."""

    def __init__(self):
        self.assigned, self.library = {}, {}

    def player_id(self, uid, name, club):
        return self.assigned.setdefault(uid, name)

    def position(self, uid, fallback=""):
        return "WR"

    def birth_date(self, uid):
        return None


def fake_context(source_dir):
    digest, rows = SOURCES[str(source_dir)]
    src = SimpleNamespace(hashes={"research/inseason_moves.csv": digest}, rows=rows, pre_reserve=set(),
                          wire_pages={WIRE % 9: "w9", WIRE % 10: "w10"}, espn_pages={"AAA": "e1"})
    return src, {"clubs": {}}, FakeIdentity(), None, {}, set()


def fake_candidates(src, ident, control, pre_reserve, through):
    rows = sorted((dict(r) for r in src.rows), key=lambda r: (r["gate_date"], r["uid"] or "", r["research_ref"]))
    return [r for r in rows if r["gate_date"] <= through], []


def fake_build(source_dir, through):
    src, library, ident, *_ = fake_context(source_dir)
    rows, problems = builder.candidates(src, ident, None, set(), through)
    committed = builder.number(rows, 1, 5, ident, problems)
    base = {"schema_version": 1, "season": 2014, "effective_from_week": 5, "library": builder.LIBRARY,
            "library_clubs_sha256": "synthetic", "clubs": {}, "corrections": []}
    return src, library, base, committed, problems


def snapshot(folder):
    folder = Path(folder)
    return {p.name: p.read_bytes() for p in sorted(folder.iterdir())} if folder.exists() else None


class CheckTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.out = Path(tmp.name) / "2014_inseason_rails"
        self.master = date(2014, 10, 4)
        for patch in (mock.patch.object(builder, "OUT", self.out),
                      mock.patch.object(builder, "context", fake_context),
                      mock.patch.object(builder, "candidates", fake_candidates),
                      mock.patch.object(builder, "build", fake_build),
                      mock.patch.object(builder, "label_noops", return_value=([], {})),
                      mock.patch.object(builder, "last_closed_week", return_value=4),
                      mock.patch.object(builder.rails, "jacksonville_control", return_value=None),
                      mock.patch.object(builder.player_bios, "master_date", side_effect=lambda root: self.master)):
            patch.start()
            self.addCleanup(patch.stop)

    def run_builder(self, *argv):
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["builder"] + list(argv)), contextlib.redirect_stdout(out):
            code = builder.main()
        return code, out.getvalue()

    def write_record(self, extended=True):
        code, text = self.run_builder("S1", "--through", "2014-09-28")
        self.assertEqual(code, 0, text)
        if extended:
            self.extend_record()

    def extend_record(self):
        code, text = self.run_builder("S2", "--through", "2014-10-04", "--extend")
        self.assertEqual(code, 0, text)
        self.assertIn("APPENDED 3 rows (R14-0004 to R14-0006)", text)
        self.assertIn("late-found: R14-0004", text)

    def checked(self, *argv):
        """Run one --check and assert it wrote nothing."""
        before = snapshot(self.out)
        code, text = self.run_builder(*argv)
        self.assertEqual(snapshot(self.out), before, "--check wrote: %s" % " ".join(argv))
        return code, text

    def test_check_on_an_extended_record_re_derives_its_last_extension(self):
        self.write_record()
        for argv in (("S2", "--through", "2014-10-04", "--check"),
                     ("S2", "--through", "2014-10-04", "--check", "--extend")):
            code, text = self.checked(*argv)
            self.assertEqual(code, 0, text)
            self.assertIn("CURRENT 6 rows through 2014-10-04", text)
            self.assertIn("(R14-0004 to R14-0006, through 2014-10-04) re-derived field by field", text)

    def test_a_changed_field_of_a_committed_extension_row_is_stale(self):
        self.write_record()
        shard = self.out / "week_05.json"
        text = shard.read_text(encoding="utf-8")
        changed = text.replace('"real_date":"2014-10-01"', '"real_date":"2014-09-30"')
        self.assertNotEqual(changed, text)
        shard.write_text(changed, encoding="utf-8")
        code, out = self.checked("S2", "--through", "2014-10-04", "--check")
        self.assertEqual(code, 1)
        self.assertIn('R14-0005 real_date: committed "2014-09-30", re-derived "2014-10-01"', out)
        # The identity key alone (gate date, club, kind, player) still matches.
        self.assertNotIn("not committed", out)

    def test_a_dropped_or_extra_extension_row_is_stale(self):
        self.write_record()
        shard = self.out / "week_05.json"
        data = json.loads(shard.read_text(encoding="utf-8"))
        dropped = data["rows"].pop()
        shard.write_text(builder.dumps(data), encoding="utf-8")
        code, out = self.checked("S2", "--through", "2014-10-04", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("R14-0006 is re-derived but not committed", out)
        data["rows"] += [dropped, dict(dropped, id="R14-0007")]
        shard.write_text(builder.dumps(data), encoding="utf-8")
        code, out = self.checked("S2", "--through", "2014-10-04", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("R14-0007 is committed after the last build's rows", out)

    def test_at_the_as_of_date_the_check_wants_the_pinned_source(self):
        self.write_record()
        code, out = self.checked("S1", "--through", "2014-10-04", "--check")
        self.assertEqual(code, 1)
        self.assertIn("inputs differ from the last build's pins: research/inseason_moves.csv", out)
        code, out = self.checked("S4", "--through", "2014-10-04", "--check")
        self.assertEqual(code, 1)
        self.assertIn("inputs differ", out)
        self.assertIn("1 rows through 2014-10-04 are not committed", out)  # the late-found September 29 row

    def test_a_row_through_through_the_record_lacks_is_stale(self):
        self.write_record()
        self.master = date(2014, 10, 11)
        code, out = self.checked("S3", "--through", "2014-10-11", "--check")
        self.assertEqual(code, 1)
        self.assertIn("1 rows through 2014-10-11 are not committed (append with --extend)", out)
        self.assertNotIn("inputs differ", out)  # a later date may come from a later source
        code, out = self.checked("S2", "--through", "2014-10-11", "--check")
        self.assertEqual(code, 0, out)
        self.assertIn("re-derived field by field", out)
        code, out = self.checked("S2", "--through", "2014-10-01", "--check")
        self.assertEqual(code, 1)
        self.assertIn("REFUSED", out)

    def test_check_never_writes_in_any_mode(self):
        # No record yet: the first-build comparison is stale and creates nothing.
        code, _ = self.checked("S1", "--through", "2014-09-28", "--check")
        self.assertEqual(code, 1)
        self.assertIsNone(snapshot(self.out))
        code, _ = self.checked("S1", "--through", "2014-09-28", "--check", "--extend")
        self.assertEqual(code, 1)
        self.assertIsNone(snapshot(self.out))
        # The first build alone: plain --check compares every file; with
        # --extend it re-derives that build's rows. The October source has
        # rows to append, which --check reports and never appends.
        self.write_record(extended=False)
        for argv, want in ((("S1", "--through", "2014-09-28", "--check"), 0),
                           (("S1", "--through", "2014-09-28", "--check", "--extend"), 0),
                           (("S2", "--through", "2014-09-28", "--check"), 1),
                           (("S2", "--through", "2014-10-04", "--check", "--extend"), 1)):
            self.assertEqual(self.checked(*argv)[0], want, argv)
        # The extended record, in every mode and outcome.
        self.extend_record()
        for argv, want in ((("S2", "--through", "2014-10-04", "--check"), 0),
                           (("S2", "--through", "2014-10-04", "--check", "--extend"), 0),
                           (("S1", "--through", "2014-10-04", "--check"), 1),
                           (("S4", "--through", "2014-10-04", "--check", "--extend"), 1),
                           (("S2", "--through", "2014-09-28", "--check"), 1)):
            self.assertEqual(self.checked(*argv)[0], want, argv)

    def edit_shard(self, edit, repin=True):
        """Edit week_05.json's rows; with `repin`, record the edited shard's
        sha256 and row count in the manifest too, so only the comparison
        under test can catch the edit."""
        shard = self.out / "week_05.json"
        data = json.loads(shard.read_text(encoding="utf-8"))
        edit(data["rows"])
        shard.write_text(builder.dumps(data), encoding="utf-8")
        if repin:
            path = self.out / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["shards"][0].update(sha256=builder.sha256(shard), rows=len(data["rows"]))
            path.write_text(builder.dumps(manifest), encoding="utf-8")

    def test_a_repeated_row_id_is_stale_even_with_the_genuine_row_after_it(self):
        good = {"id": "R14-0005", "real_date": "2014-10-01"}
        self.assertIn("R14-0005 is committed 2 times",
                      builder._field_diffs([dict(good, real_date="2014-01-01"), good], [good]))
        self.write_record()

        def duplicate(rows):
            at = next(i for i, r in enumerate(rows) if r["id"] == "R14-0005")
            rows.insert(at, dict(rows[at], real_date="2014-01-01", counterparty="ZZZ"))
        self.edit_shard(duplicate)
        code, out = self.checked("S2", "--through", "2014-10-04", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("R14-0005 is committed 2 times", out)
        self.assertIn("row ids do not run R14-0001 upward without a gap or repeat", out)
        self.assertNotIn("sha256 pin", out)

    def test_another_source_never_passes_after_the_as_of_date(self):
        self.write_record()
        self.master = date(2014, 10, 11)
        # The first build's source holds no row the record lacks, yet it
        # cannot vouch for the extension.
        code, out = self.checked("S1", "--through", "2014-10-05", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("NOT VERIFIED 6 rows through 2014-10-05", out)
        self.assertNotIn("CURRENT", out)
        # A source with the pinned rows under another hash, against an edited
        # extension row whose manifest pins were updated: not verified, and
        # only the pinned source finds the edit.
        self.edit_shard(lambda rows: rows[4].update(real_date="2014-09-30"))
        with mock.patch.dict(SOURCES, {"S5": ("h5", OCTOBER)}):
            for argv in (("S5", "--through", "2014-10-11", "--check"),
                         ("S5", "--through", "2014-10-11", "--check", "--extend")):
                code, out = self.checked(*argv)
                self.assertEqual(code, 1, out)
                self.assertIn("NOT VERIFIED", out)
                self.assertIn("not re-derived: this source is not the one it pins (research/inseason_moves.csv)", out)
            # At the as-of date the same source is stale.
            code, out = self.checked("S5", "--through", "2014-10-04", "--check")
            self.assertEqual(code, 1, out)
            self.assertIn("inputs differ from the last build's pins", out)
        code, out = self.checked("S2", "--through", "2014-10-11", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn('R14-0005 real_date: committed "2014-09-30", re-derived "2014-10-01"', out)
        # A later source with rows to append is stale and still not verified.
        code, out = self.checked("S3", "--through", "2014-10-11", "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("1 rows through 2014-10-11 are not committed", out)
        self.assertIn("not re-derived: this source is not the one it pins", out)

    def test_check_extend_on_a_first_build_record_compares_every_file(self):
        self.write_record(extended=False)
        base = self.out / "base.json"
        data = json.loads(base.read_text(encoding="utf-8"))
        data["corrections"].append({"action": "add", "club": "AAA", "uid": "x"})
        base.write_text(builder.dumps(data), encoding="utf-8")
        for argv in (("S1", "--through", "2014-09-28", "--check"),
                     ("S1", "--through", "2014-09-28", "--check", "--extend")):
            code, out = self.checked(*argv)
            self.assertEqual(code, 1, argv)
            self.assertIn("STALE: base.json", out)

    def test_the_bookkeeping_of_an_extended_record_is_checked(self):
        self.write_record()
        clean = snapshot(self.out)

        def tampered(name, change):
            path = self.out / name
            data = json.loads(path.read_text(encoding="utf-8"))
            change(data)
            path.write_text(builder.dumps(data), encoding="utf-8")
            code, out = self.checked("S2", "--through", "2014-10-04", "--check")
            for n, b in clean.items():
                (self.out / n).write_bytes(b)
            self.assertEqual(code, 1, name)
            return out
        out = tampered("base.json", lambda b: b["corrections"].append({"action": "add", "club": "AAA", "uid": "x"}))
        self.assertIn("base.json differs from its manifest sha256 pin", out)
        # A first-build row is not re-derived from the October source; its
        # shard's pin guards it.
        out = tampered("week_05.json", lambda s: s["rows"][0].update(real_date="2014-09-01", reason="edited"))
        self.assertIn("week_05.json differs from its manifest sha256 pin", out)
        self.assertNotIn("R14-0001", out)
        out = tampered("manifest.json", lambda m: m["shards"][0].update(sha256="0" * 64, rows=99))
        self.assertIn("week_05.json differs from its manifest sha256 pin", out)
        self.assertIn("week_05.json holds 6 rows, the manifest records 99", out)
        out = tampered("manifest.json", lambda m: m.update(as_of="2014-10-03"))
        self.assertIn("as-of date 2014-10-03 is not the last build's date 2014-10-04", out)
        out = tampered("sources.json", lambda p: p.update(nfl_wire={}))
        self.assertIn("sources.json lacks the nfl_wire page %s" % (WIRE % 10), out)
        self.assertEqual(snapshot(self.out), clean)
        self.assertEqual(self.checked("S2", "--through", "2014-10-04", "--check")[0], 0)


if __name__ == "__main__":
    unittest.main()
