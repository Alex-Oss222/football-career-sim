#!/usr/bin/env python3
"""Split a page written before 2014 Week 6 into one page per part, under the split rule
(runtime/clean_pages.py, "The split rule"; docs/rebuild_plan.md, "Pages written before Week 6").

    python3 scripts/split_history_page.py PLAN.json --recorded YYYY-MM-DD [--check]

PLAN.json names:

- ``original``: the page's repository path. It must still hold its bytes as written before Week 6
  (its digest in the page history map).
- ``why``: one line on why it is split.
- ``parts``: for each part, ``name`` (its file name, in the original's folder so its relative links
  still resolve), ``title`` (its one title line, "# " and its words, clean) and ``lines`` (the
  original's line ranges it is made of, each [first, last], counted from 1, in order).
- ``moved``: for each section that goes elsewhere, ``lines`` ([first, last]), ``to`` (its
  destination's repository path) and ``what`` (what it is).

Every line of the original goes into at least one part or one moved section. A part is its title
line, a blank line, then its lines exactly as written; nothing is reworded. The script writes the
parts, records the split in the page history map (the original's digest and length leave "pages"
for the split entry, with each part's byte ranges, digest and length and each moved section's bytes,
so the original can always be rebuilt), re-pins the map (runtime/season_layout.PAGE_HISTORY_SHA256,
the one line of the folder map this step changes) and removes the original. A replacement at the
original's path (the trade offer log's index) is written afterwards by that page's own builder.

--check writes nothing: it builds the parts and the entry from the plan and reports what differs
from the repository (an applied split reports nothing).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime import clean_pages, season_layout  # noqa: E402
from runtime.season_layout import PAGE_HISTORY  # noqa: E402

PIN = re.compile(r"^PAGE_HISTORY_SHA256 = '[0-9a-f]{64}'$", re.M)


class Refused(ValueError):
    """A split the rule refuses (nothing was written)."""


def _line_offsets(data):
    """The byte offset at which each line of ``data`` starts, and the end."""
    offsets = [0]
    for line in data.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _ranges(lines, offsets, what):
    """The byte ranges of 1-based [first, last] line ranges, adjacent ones joined."""
    count = len(offsets) - 1
    out = []
    for pair in lines:
        if (not isinstance(pair, list) or len(pair) != 2 or any(type(v) is not int for v in pair)
                or not 1 <= pair[0] <= pair[1] <= count):
            raise Refused("%s: %r is not a [first, last] range of the original's %d lines" % (what, pair, count))
        start, end = offsets[pair[0] - 1], offsets[pair[1]]
        if out and start < out[-1][1]:
            raise Refused("%s: its line ranges are not in order" % what)
        if out and start == out[-1][1]:
            out[-1][1] = end
        else:
            out.append([start, end])
    if not out:
        raise Refused("%s: no lines" % what)
    return out


def build(root, plan, recorded):
    """(the parts {path: bytes}, the history map as it would be after the split). Refused for an
    original no longer as written before Week 6, an unclean or missing title, a part outside the
    original's folder, or a line in no part and no moved section."""
    root = Path(root)
    original = plan.get("original")
    if not isinstance(original, str) or not original.endswith(".md"):
        raise Refused("the plan names no original page")
    history = json.loads((root / PAGE_HISTORY).read_text(encoding="utf-8"))
    recorded_digest = history.get("pages", {}).get(original)
    path = root / original
    if recorded_digest is None:
        raise Refused("%s is not a page written before Week 6 in the page history map" % original)
    if not path.is_file() or clean_pages.digest(path.read_bytes()) != recorded_digest:
        raise Refused("%s no longer holds its bytes as written before Week 6; only such a page is split" % original)
    if not isinstance(plan.get("why"), str) or not plan["why"].strip():
        raise Refused("the plan gives no reason for the split")
    dt.date.fromisoformat(recorded)
    data = path.read_bytes()
    offsets = _line_offsets(data)
    folder = PurePosixPath(original).parent
    covered = [False] * (len(offsets) - 1)
    parts, entry_parts = {}, []
    for n, part in enumerate(plan.get("parts") or (), 1):
        name, title = part.get("name"), part.get("title")
        if not isinstance(name, str) or "/" in name or not name.endswith(".md"):
            raise Refused("part %d: its name is a file name in the original's folder" % n)
        rel = (folder / name).as_posix()
        if rel == original or rel in parts:
            raise Refused("part %d: %s is the original or another part" % (n, rel))
        if not isinstance(title, str) or not clean_pages.SPLIT_TITLE.fullmatch(title):
            raise Refused("%s: its title is one line beginning with a heading mark" % rel)
        unclean = clean_pages.page_errors(rel, title + "\n", root=root)
        if unclean:
            raise Refused("%s: its title is not clean: %s" % (rel, "; ".join(unclean)))
        ranges = _ranges(part.get("lines"), offsets, rel)
        for first, last in part["lines"]:
            covered[first - 1:last] = [True] * (last - first + 1)
        body = clean_pages.part_prefix(title) + b"".join(data[s:e] for s, e in ranges)
        parts[rel] = body
        entry_parts.append({"path": rel, "title": title, "ranges": ranges,
                            "sha256": clean_pages.digest(body), "length": len(body)})
    if not parts:
        raise Refused("the plan names no parts")
    moved = []
    for n, section in enumerate(plan.get("moved") or (), 1):
        to, what = section.get("to"), section.get("what")
        if not isinstance(to, str) or not to or not isinstance(what, str) or not what.strip():
            raise Refused("moved section %d: it needs its destination and what it is" % n)
        (span,) = _ranges([section.get("lines")], offsets, "moved section %d" % n)
        first, last = section["lines"]
        covered[first - 1:last] = [True] * (last - first + 1)
        moved.append({"range": span, "to": to, "what": what, "text": data[span[0]:span[1]].decode("utf-8")})
    missing = [n for n, done in enumerate(covered, 1) if not done]
    if missing:
        raise Refused("lines %s of %s are in no part and no moved section" % (
            ", ".join(map(str, missing[:10])), original))
    pages = dict(history.get("pages", {}))
    lengths = dict(history.get("lengths", {}))
    pages.pop(original)
    lengths.pop(original, None)
    after = dict(history, pages=pages, lengths=lengths)
    split = dict(history.get("splits", {}))
    split[original] = {"sha256": recorded_digest, "length": len(data), "recorded": recorded,
                       "why": plan["why"].strip(), "parts": entry_parts, "moved": moved}
    after["splits"] = dict(sorted(split.items()))
    return parts, after


def _map_bytes(history):
    return (json.dumps(history, indent=1) + "\n").encode("utf-8")


def check(root, plan, recorded):
    """What applying the plan would change (an applied split: nothing)."""
    root = Path(root)
    entry = clean_pages.splits(root).get(plan.get("original"))
    if entry is None:
        return ["%s is not split yet" % plan.get("original")]
    history = json.loads((root / PAGE_HISTORY).read_text(encoding="utf-8"))
    rebuilt = clean_pages.rebuilt_original(plan["original"], root)
    if rebuilt is None:
        return clean_pages.split_errors(root) or ["%s cannot be rebuilt from its parts" % plan["original"]]
    # Rebuild the state before the split in memory and apply the plan to it.
    before = dict(history, pages=dict(history["pages"], **{plan["original"]: entry["sha256"]}),
                  lengths=dict(history.get("lengths", {}), **{plan["original"]: entry["length"]}))
    splits = dict(history.get("splits", {}))
    splits.pop(plan["original"])
    before["splits"] = splits
    if not splits:
        before.pop("splits")
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        (scratch / PAGE_HISTORY).parent.mkdir(parents=True)
        (scratch / PAGE_HISTORY).write_bytes(_map_bytes(before))
        (scratch / plan["original"]).parent.mkdir(parents=True)
        (scratch / plan["original"]).write_bytes(rebuilt)
        parts, after = build(scratch, plan, recorded)
    for rel, body in parts.items():
        if not (root / rel).is_file() or (root / rel).read_bytes() != body:
            problems.append("%s differs from the plan" % rel)
    if after["splits"].get(plan["original"]) != entry:
        problems.append("the split entry of %s differs from the plan" % plan["original"])
    return problems


def apply(root, plan, recorded):
    """Write the parts and the split entry, re-pin the map and remove the original; returns the
    paths written or removed."""
    root = Path(root)
    parts, after = build(root, plan, recorded)
    for rel in parts:
        if (root / rel).exists():
            raise Refused("%s already exists; a part is a new page" % rel)
    written = []
    for rel, body in parts.items():
        (root / rel).write_bytes(body)
        written.append(rel)
    data = _map_bytes(after)
    (root / PAGE_HISTORY).write_bytes(data)
    layout = root / Path(season_layout.__file__).relative_to(ROOT)
    text = layout.read_text(encoding="utf-8")
    if len(PIN.findall(text)) != 1:
        raise Refused("the folder map's page history pin line was not found")
    layout.write_text(PIN.sub("PAGE_HISTORY_SHA256 = '%s'" % clean_pages.digest(data), text), encoding="utf-8")
    (root / plan["original"]).unlink()
    written += [PAGE_HISTORY, layout.relative_to(root).as_posix(), plan["original"] + " (removed)"]
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--recorded", required=True, help="the date the split is recorded (YYYY-MM-DD)")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    try:
        if args.check:
            problems = check(ROOT, plan, args.recorded)
            print("\n".join(problems) if problems else "SPLIT CURRENT: %s" % plan["original"])
            return 1 if problems else 0
        for line in apply(ROOT, plan, args.recorded):
            print(line)
        print("Split recorded; write the page that replaces the original with its own builder.")
        return 0
    except Refused as exc:
        print("Refused: %s" % exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
