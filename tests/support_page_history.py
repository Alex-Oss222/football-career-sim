"""Page history in a copy of the repository (docs/rebuild_plan.md, rule 1).

A test that replays pre-Week-6 work on a copy (a synthetic Week 1 closure, a
re-rendered desk with a test item) rewrites pages written before 2014 Week 6.
Those rewrites are pre-Week-6 work, so ``keep_as_history`` records the copy's
new bytes of each such page in the copy's page history, as rebuild step 3a
recorded the real ones. A rewrite of a real page from Week 6 on has no such
step: its digest no longer matches and the clean-page check reads it. The
real repository's history is never changed here.
"""
import json
from pathlib import Path

from runtime import clean_pages
from runtime.season_layout import PAGE_HISTORY

ROOT = Path(__file__).resolve().parents[1]


def keep_as_history(root, rels=None):
    """Record, in the copy at ``root`` only, the current digest of each history page in ``rels``
    (by default every history page whose bytes the test changed). Returns the paths recorded."""
    root = Path(root).resolve()
    if root == ROOT.resolve():
        raise ValueError("the real page history is never re-recorded")
    path = root / PAGE_HISTORY
    if path.resolve() != path:
        raise ValueError("the copy's page history must be a real file of its own, not a link")
    data = json.loads(path.read_text(encoding="utf-8"))
    pages = data["pages"]
    names = sorted(pages) if rels is None else sorted(rels)
    changed = []
    for rel in names:
        if rel not in pages:
            raise ValueError("not a page written before Week 6: " + rel)
        page = root / rel
        if page.is_file():
            now = clean_pages.digest(page.read_bytes())
            if now != pages[rel]:
                pages[rel] = now
                changed.append(rel)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return changed
