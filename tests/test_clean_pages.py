"""The split rule of the page history (rebuild step 5, part B2; runtime/clean_pages.py).

A page written before 2014 Week 6 may be split into one page per part and nothing else about its
bytes changes. These tests audit the one split on record (the trade offer log into one page per
call) by rebuilding its pinned bytes from the parts, and check the rule on synthetic splits in
throwaway roots and copies. The real repository is never written.
"""
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from release_staging import copied_root  # noqa: E402
import support_page_history as sph  # noqa: E402
from runtime import clean_pages  # noqa: E402
from runtime.season_layout import PAGE_HISTORY  # noqa: E402
from scripts import split_history_page as splitter  # noqa: E402

SPLITS = clean_pages.splits(ROOT)


def plan_of(original, entry, data):
    """The splitter's plan that made ``entry`` from the original's ``data`` (byte ranges as lines)."""
    starts = {0: 1}
    at = 0
    for n, line in enumerate(data.splitlines(keepends=True), 1):
        at += len(line)
        starts[at] = n + 1
    lines = lambda ranges: [[starts[s], starts[e] - 1] for s, e in ranges]  # noqa: E731
    folder = Path(original).parent.as_posix() + "/"
    return {"original": original, "why": entry["why"],
            "parts": [{"name": p["path"][len(folder):], "title": p["title"], "lines": lines(p["ranges"])}
                      for p in entry["parts"]],
            "moved": [{"lines": lines([m["range"]])[0], "to": m["to"], "what": m["what"]} for m in entry["moved"]]}


def unsplit(root, original):
    """Put a split page back as it was written before Week 6, in the copy at ``root`` only: the
    original rebuilt at its path, its digest and length back in "pages", the split and its parts
    gone. Returns (the plan that made the split, its recorded date)."""
    root = Path(root).resolve()
    if root == ROOT.resolve():
        raise ValueError("the real page history is never changed")
    history = json.loads((root / PAGE_HISTORY).read_text(encoding="utf-8"))
    entry = history["splits"].pop(original)
    if not history["splits"]:
        history.pop("splits")
    data = clean_pages.rebuilt_original(original, root)
    history["pages"][original] = entry["sha256"]
    history["lengths"][original] = entry["length"]
    for part in entry["parts"]:
        (root / part["path"]).unlink()
    (root / original).write_bytes(data)
    (root / PAGE_HISTORY).write_text(json.dumps(history, indent=1) + "\n", encoding="utf-8")
    return plan_of(original, entry, data), entry["recorded"]


class RecordedSplitTests(unittest.TestCase):
    """The splits on record: each rebuilds its pinned original."""

    def test_a_split_is_on_record_and_passes(self):
        self.assertTrue(SPLITS)
        self.assertEqual(clean_pages.split_errors(ROOT), [])
        self.assertEqual(clean_pages.history_pin_errors(ROOT), [])

    def test_the_parts_rebuild_each_pinned_original(self):
        for original, entry in SPLITS.items():
            with self.subTest(original=original):
                rebuilt = clean_pages.rebuilt_original(original, ROOT)
                self.assertIsNotNone(rebuilt)
                self.assertEqual((clean_pages.digest(rebuilt), len(rebuilt)), (entry["sha256"], entry["length"]))
                # The original's entry left "pages" for the split.
                self.assertNotIn(original, clean_pages.history(ROOT))
                self.assertNotIn(original, clean_pages.history_lengths(ROOT))
                # Each part is its title line, a blank line and its ranges of the original, in order.
                for part in entry["parts"]:
                    body = clean_pages.part_prefix(part["title"]) + b"".join(rebuilt[s:e] for s, e in part["ranges"])
                    self.assertEqual((ROOT / part["path"]).read_bytes(), body, part["path"])
                    self.assertEqual(Path(part["path"]).parent, Path(original).parent)
                # Every byte is in a part or a moved section.
                covered = set()
                for span in [r for p in entry["parts"] for r in p["ranges"]] + [m["range"] for m in entry["moved"]]:
                    covered |= set(range(*span))
                self.assertEqual(covered, set(range(entry["length"])))

    def test_each_part_keeps_its_exemption_and_its_title_line_is_checked(self):
        checked = {}
        for rel, text, first in clean_pages.checked_parts(ROOT):
            checked.setdefault(rel, []).append((text, first))
        for original, entry in SPLITS.items():
            for part in entry["parts"]:
                with self.subTest(part=part["path"]):
                    self.assertEqual(checked[part["path"]], [(part["title"] + "\n", 1)])
                    self.assertEqual(clean_pages.page_errors(part["path"], part["title"] + "\n", root=ROOT), [])
                    self.assertEqual(clean_pages.text_errors(part["path"], (ROOT / part["path"]).read_text(), ROOT), [])
        # The exemption matters: the history bytes are not clean by today's rule.
        unclean = [p["path"] for e in SPLITS.values() for p in e["parts"]
                   if clean_pages.page_errors(p["path"], (ROOT / p["path"]).read_text(), root=ROOT)]
        self.assertTrue(unclean)

    def test_the_splitter_reproduces_the_recorded_split(self):
        for original, entry in SPLITS.items():
            with self.subTest(original=original):
                plan = plan_of(original, entry, clean_pages.rebuilt_original(original, ROOT))
                self.assertEqual(splitter.check(ROOT, plan, entry["recorded"]), [])


class SplitRuleTests(unittest.TestCase):
    """The rule on copies: a changed part, an appended entry, a lost byte, a re-run of the splitter."""

    @classmethod
    def setUpClass(cls):
        cls.root = copied_root(SimpleNamespace(addCleanup=cls.addClassCleanup))
        cls.original, cls.entry = next(iter(sorted(SPLITS.items())))

    def setUp(self):
        saved = {}
        for rel in [PAGE_HISTORY, self.original, "runtime/season_layout.py"] + [p["path"] for p in self.entry["parts"]]:
            path = self.root / rel
            saved[rel] = path.read_bytes() if path.is_file() else None
        self.addCleanup(self._restore, saved)

    def _restore(self, saved):
        for rel, data in saved.items():
            path = self.root / rel
            if data is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_bytes(data)

    def unclean_part(self):
        return next(p for p in self.entry["parts"]
                    if clean_pages.page_errors(p["path"], (self.root / p["path"]).read_text(), root=self.root))

    def test_a_changed_part_loses_its_exemption(self):
        part = self.unclean_part()
        path = self.root / part["path"]
        data = path.read_bytes()
        at = len(clean_pages.part_prefix(part["title"])) + 3
        path.write_bytes(data[:at] + (b"X" if data[at:at + 1] != b"X" else b"Y") + data[at + 1:])
        self.assertTrue(any(part["path"] in e and "no longer begins" in e for e in clean_pages.split_errors(self.root)))
        # The whole page is checked once one recorded byte changed.
        self.assertTrue([e for e in clean_pages.clean_errors(self.root) if e.startswith(part["path"] + ":")])

    def test_an_appended_entry_is_checked_on_its_own_lines(self):
        part = self.unclean_part()
        path = self.root / part["path"]
        before = path.read_text(encoding="utf-8")
        path.write_text(before + "\nThe kernel note added later.\n", encoding="utf-8")
        self.assertEqual(clean_pages.split_errors(self.root), [])
        errors = [e for e in clean_pages.clean_errors(self.root) if e.startswith(part["path"] + ":")]
        self.assertEqual(errors, ["%s:%d: system word: kernel" % (part["path"], before.count("\n") + 2)])

    def test_an_unclean_title_fails(self):
        history = json.loads((self.root / PAGE_HISTORY).read_text(encoding="utf-8"))
        part = history["splits"][self.original]["parts"][0]
        part["title"] = "# The kernel's call"
        body = clean_pages.part_prefix(part["title"]) + (self.root / part["path"]).read_bytes()[
            len(clean_pages.part_prefix(self.entry["parts"][0]["title"])):]
        part["sha256"], part["length"] = clean_pages.digest(body), len(body)
        (self.root / part["path"]).write_bytes(body)
        (self.root / PAGE_HISTORY).write_text(json.dumps(history, indent=1) + "\n", encoding="utf-8")
        self.assertIn("%s:1: system word: kernel" % part["path"], clean_pages.split_errors(self.root))
        with sph.pinned_copy(self.root):
            self.assertIn("%s:1: system word: kernel" % part["path"], clean_pages.clean_errors(self.root))

    def test_a_byte_in_no_part_fails(self):
        history = json.loads((self.root / PAGE_HISTORY).read_text(encoding="utf-8"))
        entry = history["splits"][self.original]
        # Drop the moved sections: their bytes are now in no part.
        entry["moved"] = []
        (self.root / PAGE_HISTORY).write_text(json.dumps(history, indent=1) + "\n", encoding="utf-8")
        self.assertTrue(any("are in no part and no moved section" in e for e in clean_pages.split_errors(self.root)))
        self.assertIsNone(clean_pages.rebuilt_original(self.original, self.root))

    def test_the_splitter_round_trip(self):
        plan, recorded = unsplit(self.root, self.original)
        self.assertEqual(clean_pages.digest((self.root / self.original).read_bytes()), self.entry["sha256"])
        # Refused: an unclean title; a line in no part; nothing is written.
        bad = json.loads(json.dumps(plan))
        bad["parts"][0]["title"] = "# The kernel's call"
        with self.assertRaisesRegex(splitter.Refused, "not clean"):
            splitter.apply(self.root, bad, recorded)
        bad = json.loads(json.dumps(plan))
        bad["moved"] = bad["moved"][1:]
        with self.assertRaisesRegex(splitter.Refused, "in no part and no moved section"):
            splitter.apply(self.root, bad, recorded)
        self.assertFalse(any((self.root / p["path"]).exists() for p in self.entry["parts"]))
        # Applied, it makes the recorded parts and entry byte for byte, and re-pins the copy's map.
        splitter.apply(self.root, plan, recorded)
        for part in self.entry["parts"]:
            self.assertEqual((self.root / part["path"]).read_bytes(), (ROOT / part["path"]).read_bytes())
        self.assertEqual(clean_pages.splits(self.root)[self.original], self.entry)
        self.assertFalse((self.root / self.original).exists())
        pin = clean_pages.digest((self.root / PAGE_HISTORY).read_bytes())
        self.assertIn("PAGE_HISTORY_SHA256 = '%s'" % pin, (self.root / "runtime/season_layout.py").read_text())
        # An original no longer as written before Week 6 is refused.
        plan2, _ = unsplit(self.root, self.original)
        path = self.root / self.original
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(splitter.Refused, "no longer holds its bytes"):
            splitter.apply(self.root, plan2, recorded)


class SyntheticSplitTests(unittest.TestCase):
    """A small split in a bare root: two parts that disagree on a shared byte, and a moved section's
    destination page that does not hold it."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir=ROOT.parent)
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.original = "career/test_folder/log.md"
        self.data = b"# Log\n\n## One\n\nA shared line.\n\n## Two\n\nThe second call.\n"
        (self.root / self.original).parent.mkdir(parents=True)
        (self.root / self.original).write_bytes(self.data)
        (self.root / PAGE_HISTORY).parent.mkdir(parents=True)
        history = {"pages": {self.original: clean_pages.digest(self.data)},
                   "lengths": {self.original: len(self.data)}}
        (self.root / PAGE_HISTORY).write_text(json.dumps(history, indent=1) + "\n", encoding="utf-8")
        (self.root / "runtime").mkdir()
        shutil.copy(ROOT / "runtime/season_layout.py", self.root / "runtime/season_layout.py")
        self.plan = {"original": self.original, "why": "A test split.",
                     "parts": [{"name": "one.md", "title": "# Call one", "lines": [[3, 6]]},
                               {"name": "two.md", "title": "# Call two", "lines": [[5, 6], [7, 9]]}],
                     "moved": [{"lines": [1, 2], "to": "career/test_folder/index.md", "what": "The title."}]}

    def test_a_clean_split_passes_once_its_destination_holds_the_moved_bytes(self):
        splitter.apply(self.root, self.plan, "2000-01-01")
        self.assertTrue(any("does not exist" in e for e in clean_pages.split_errors(self.root)))
        (self.root / "career/test_folder/index.md").write_text("# Index\n", encoding="utf-8")
        self.assertTrue(any("does not hold it" in e for e in clean_pages.split_errors(self.root)))
        (self.root / "career/test_folder/index.md").write_text("# Log\n\nAn index.\n", encoding="utf-8")
        self.assertEqual(clean_pages.split_errors(self.root), [])
        self.assertEqual(clean_pages.rebuilt_original(self.original, self.root), self.data)
        self.assertEqual((self.root / "career/test_folder/two.md").read_bytes(),
                         b"# Call two\n\nA shared line.\n\n## Two\n\nThe second call.\n")

    def test_parts_that_disagree_on_a_shared_byte_fail(self):
        splitter.apply(self.root, self.plan, "2000-01-01")
        (self.root / "career/test_folder/index.md").write_text("# Log\n\n", encoding="utf-8")
        history = json.loads((self.root / PAGE_HISTORY).read_text(encoding="utf-8"))
        part = history["splits"][self.original]["parts"][1]
        body = (self.root / part["path"]).read_bytes().replace(b"A shared line.", b"A shared lime.")
        (self.root / part["path"]).write_bytes(body)
        part["sha256"] = clean_pages.digest(body)
        (self.root / PAGE_HISTORY).write_text(json.dumps(history, indent=1) + "\n", encoding="utf-8")
        self.assertTrue(any("disagrees with another part" in e for e in clean_pages.split_errors(self.root)))

    def test_a_part_outside_the_original_folder_is_refused(self):
        plan = json.loads(json.dumps(self.plan))
        plan["parts"][0]["name"] = "../elsewhere.md"
        with self.assertRaisesRegex(splitter.Refused, "file name in the original's folder"):
            splitter.apply(self.root, plan, "2000-01-01")


if __name__ == "__main__":
    unittest.main()
