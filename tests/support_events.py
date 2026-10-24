"""Synthetic in-season events for tests, in a throwaway copy of the checkout only (rebuild step 5).

Every event built here is test data: its summary says so, its source is a test page the copy alone
holds, and nothing is written to the real repository. Weeks and dates come from the fixtures and the
receipts (the open week is the first Jacksonville game without a receipt), never from today's date,
so the tests hold at any later clock.
"""
from datetime import date, timedelta
import json
from pathlib import Path
import re

from runtime import decision_queue, decisions, open_events
from runtime.events import repository_map
from runtime.seasons import SeasonPaths
from runtime.week_inputs import receipt_name

ROOT = Path(__file__).resolve().parents[1]
SEASON = int(repository_map(ROOT)["active_season"])
CLUB = "Jacksonville Jaguars"
STATE = "state/05_Current_Season_State.md"


def open_game(root=ROOT):
    """The open week's Jacksonville fixture (the first without a receipt), or None."""
    paths = SeasonPaths(SEASON, root)
    return next((g for g in open_events.club_fixtures(SEASON, root)
                 if not (paths.receipts / receipt_name(g)).is_file()), None)


def long_date(day):
    return "%s %d, %d" % (day.strftime("%B"), day.day, day.year)


def set_clock(root, line):
    """Document 5's master date/time line in the copy at ``root`` (never the real one)."""
    root = Path(root).resolve()
    if root == ROOT.resolve():
        raise ValueError("the real master date is never moved by a test")
    path = root / STATE
    text = path.read_text(encoding="utf-8")
    path.write_text(re.sub(r"^\| Master date/time \| .+? \|\s*$", "| Master date/time | %s |" % line, text,
                           count=1, flags=re.M), encoding="utf-8")


def midweek(root, day, hour, minute=0, week=None):
    """Set the copy's clock to a mid-week record at ``hour``:``minute`` ET on ``day``."""
    clock = "%d%s %s" % (hour % 12 or 12, ":%02d" % minute if minute else "", "a.m." if hour < 12 else "p.m.")
    set_clock(root, "%s, after the %s ET record of the Week %d preparation (a test record)" % (
        long_date(day), clock, week or open_game(root)["week"]))


def source_page(root, kind, name="test_event_source.md", text="# Test source\n\nA test record.\n"):
    """A test source page in the event owner's folder of the copy; its repository path."""
    folder = decisions.event_folder(kind, SEASON, root)
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path.relative_to(Path(root).resolve()).as_posix()


def fixture_pointer(root, game):
    """The fixtures record of a game, as a {path, pointer} source."""
    paths = SeasonPaths(SEASON, root)
    games = json.loads(paths.schedule.read_text(encoding="utf-8"))["games"]
    index = next(n for n, g in enumerate(games) if g["game_id"] == game["game_id"])
    return {"path": paths.schedule.relative_to(Path(root).resolve()).as_posix(), "pointer": "/games/%d" % index}


def at(day, hour, minute=0):
    return open_events.iso(open_events.et(day, hour, minute))


def trade_call(root, ident, raised, due=None, subject="Test Club", source=None, **changes):
    """A test trade call raised at ``raised`` (a datetime), Stone's football recommendation asked,
    Caldwell deciding; ``due`` (a datetime) the other side's sourced deadline, or None."""
    source = source or source_page(root, "trade_talks")
    record = {
        "schema": open_events.SCHEMA, "id": "%s-%s" % (raised.date().isoformat(), ident), "kind": "trade_talks",
        "season": SEASON, "subject": subject,
        "raised": {"at": open_events.iso(raised), "by": "caldwell", "source": {"path": source}},
        "known_to": ["stone", "caldwell"], "authority": {"rows": ["3", "20"], "decides": "caldwell"},
        "stone_part": "recommends",
        "summary": {"text": "A test call from another club about a trade.", "author": "David Caldwell",
                    "date": raised.date().isoformat()},
        "staff_position": None, "consequence": None, "facts": [], "options": [],
        "deadline": ({"at": open_events.iso(due), "label": "The other club's deadline", "source": {"path": source}}
                     if due else None),
        "state": "open", "process": [], "queue_item": None, "response": None, "resolution": None}
    record.update(changes)
    return record


def injury_replacement(root, ident, raised, game, short=True, subject="Test Player", **changes):
    """A test injury replacement due at ``game``'s kickoff; ``short`` records that the active roster
    cannot dress a legal team for it."""
    source = source_page(root, "injury_replacement")
    facts = [{"label": "Medical communication", "value": "Out for the next game, from the medical staff",
              "source": {"path": source}}]
    if short:
        facts.append({"label": open_events.LEGAL_TEAM_FACT, "value": "No: a test shortfall at one position",
                      "source": {"path": source}})
    record = {
        "schema": open_events.SCHEMA, "id": "%s-%s" % (raised.date().isoformat(), ident),
        "kind": "injury_replacement", "season": SEASON, "subject": subject,
        "raised": {"at": open_events.iso(raised), "by": "caldwell", "source": {"path": source}},
        "known_to": ["stone", "caldwell"], "authority": {"rows": ["3", "5", "7"], "decides": "caldwell"},
        "stone_part": "recommends",
        "summary": {"text": "A test roster question after an injury.", "author": "David Caldwell",
                    "date": raised.date().isoformat()},
        "staff_position": None, "consequence": None, "facts": facts, "options": [],
        "deadline": {"at": open_events.iso(open_events.kickoff(game)), "label": "Kickoff",
                     "source": fixture_pointer(root, game)},
        "state": "open", "process": [], "queue_item": None, "response": None, "resolution": None}
    record.update(changes)
    return record


def result_page(root, record, name, when, summary="A test result."):
    """A minimal test result page for ``record`` in its owner's folder, carrying its event line."""
    folder = decisions.event_folder(record["kind"], SEASON, root)
    path = folder / name
    line = json.dumps({"id": record["id"], "date": when.isoformat(), "summary": summary, "status": "closed",
                       "season": SEASON})
    path.write_text("# Test result\n\nA test result page.\n\n<!-- event-record: %s -->\n" % line, encoding="utf-8")
    return path.relative_to(Path(root).resolve()).as_posix()


def save_queue(root, queue):
    decision_queue.save(root, queue)


def item(root, item_id):
    return next(i for i in decision_queue.load(root)["items"] if i["id"] == item_id)


def settle(root, item_id, status, resolution):
    queue = decision_queue.load(root)
    for entry in queue["items"]:
        if entry["id"] == item_id:
            entry["status"] = status
            entry["resolution"] = resolution
    save_queue(root, queue)


def tuesday_before(game):
    """The Tuesday of a Sunday game's week (five days before it)."""
    return date.fromisoformat(game["date"]) - timedelta(days=5)
