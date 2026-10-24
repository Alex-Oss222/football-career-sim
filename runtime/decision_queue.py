"""The decision queue: open decisions that code enforces (state/decision_queue.json).

An OPEN item names the events it holds (BLOCK_KINDS). The scripts that would
commit such an event refuse while it is open: building a week's inputs,
closing a week, freezing a part of a call sheet into the inputs, staging or
opening a season. The queue is an index; the question's evidence and the
decision itself live in the linked records. Validation never treats an open
item as an error on its own (it runs inside game readiness); it reports an
item that is inconsistent with the record or that a closed event has passed.
Nothing that resolves a game reads this module (docs/career_layer.md).

An item may carry an in-season event (``event``, rebuild step 5; runtime/open_events.py): it holds
that event's resolution (``event_resolution``), and the hold follows the event, never the clock. It
may also hold the inputs and the close of a week only when its answer is needed to play that week,
which is an injury replacement whose facts record that the active roster cannot dress a legal team
for that game: a trade call never holds the game, whatever its due time. The bye's adjustments item
holds only the bye's own close (``bye_close``), so the other clubs' games of the bye week close
while Stone's bye answers are open. An item past its due time is overdue (``overdue_items``), never
resolved and never an error by itself.
"""
from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re

from . import current_job
from .seasons import SeasonPaths

QUEUE = Path("state/decision_queue.json")
STATUSES = ("OPEN", "RESOLVED", "WITHDRAWN")
UNRESOLVED = frozenset({"OPEN"})
BLOCK_KINDS = {"week_inputs": ("season", "week"), "week_close": ("season", "week"),
               "call_sheet_part": ("season", "week", "part"),
               "season_stage": ("season",), "season_opening": ("season",),
               # Rebuild step 5: an in-season event's resolution, and the bye week's own close.
               "event_resolution": ("season", "event"), "bye_close": ("season", "week")}
IMPLIES = {"week_inputs": ("week_close",), "season_stage": ("season_opening",)}
SHEET_PARTS = ("offensive_call_sheet", "decisions.two_point", "decisions.kickoff",
               "decisions.fourth_down", "defensive_call_sheet")
# The club's TeamInput field each frozen part becomes in a week's package
# (runtime.week_inputs.jacksonville_input; scoring_decisions.POLICY_FIELDS).
INPUT_PARTS = {"offensive_call_sheet": "offensive_call_sheet", "defensive_call_sheet": "defensive_call_sheet",
               "try_policy": "decisions.two_point", "kickoff_policy": "decisions.kickoff",
               "fourth_down_policy": "decisions.fourth_down"}
RAISED_BY = ("user", "workflow", "staff", "organization", "medical")
RESOLVED_BY = ("user", "standing_instruction", "organization", "medical", "staff")
WEEK_KINDS = frozenset({"week_inputs", "week_close", "call_sheet_part"})
# The week blocks an event's item may carry, under the hold rule (``_event_block_errors``).
GAME_KINDS = frozenset({"week_inputs", "week_close"})
# The classes that may hold a game only through an event under the hold rule (rebuild step 5): an
# item of one of them without an event keeps the rules it had before, which hold no week.
EVENT_GAME_CLASSES = frozenset({"personnel_recommendation", "quarterback_consultation", "personnel_transaction"})
# The holder's part in a decision that lets it reach him (validation rule 3).
HOLDER_PARTS = frozenset({"decides", "decides_part", "recommends", "consulted", "responds"})
ITEM_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ITEM_KEYS = frozenset({"id", "title", "class", "subject", "owner", "owner_note", "owner_basis", "advisers",
                       "authority_rows", "question", "raised", "status", "waits_on", "deadline", "blocks",
                       "standing_not_applied", "fallback", "can_continue", "record", "sources",
                       "migrated_from", "resolution", "event"})
REQUIRED_KEYS = ("id", "title", "class", "owner", "question", "raised", "status", "blocks", "record")


@dataclass(frozen=True)
class DecisionClass:
    default_owner: str            # a party id, or "holder" (job["holder"])
    rows: tuple[str, ...]
    may_block: frozenset[str]
    closable_by_standing: bool
    raised_only_by_user: bool = False


CLASSES = {
 "weekly_game_plan":        DecisionClass("holder", ("9","10","11","12","13","14"), frozenset({"week_inputs","week_close"}), False),
 "game_day_inactives":      DecisionClass("holder", ("8",), frozenset({"week_inputs","week_close"}), True),
 "depth_and_roles":         DecisionClass("holder", ("9","10"), frozenset({"week_inputs","week_close","season_stage","season_opening","event_resolution"}), True),
 "game_management_rule":    DecisionClass("holder", ("12","13","14"), frozenset({"call_sheet_part"}), True),
 "play_calling_delegation": DecisionClass("holder", ("12","13","14"), frozenset(), True, raised_only_by_user=True),
 "emergency_succession":    DecisionClass("holder", ("2","12","13","14"), frozenset(), True, raised_only_by_user=True),
 "staff_appointment":       DecisionClass("holder", ("2","6","22"), frozenset({"season_stage","season_opening"}), False),
 "practice_plan":           DecisionClass("holder", ("11",), frozenset(), True),
 "discipline":              DecisionClass("holder", ("18",), frozenset(), False),
 "media_statement":         DecisionClass("holder", ("19",), frozenset(), False),
 "personnel_recommendation":DecisionClass("holder", ("3","4","7","20"), frozenset({"event_resolution","week_inputs","week_close"}), False),
 "quarterback_consultation":DecisionClass("holder", ("3a",), frozenset({"event_resolution","week_inputs","week_close"}), False),
 "employment_response":     DecisionClass("holder", ("1",), frozenset(), False),   # schema only: no employment event is wired
 "outside_job_approach":    DecisionClass("holder", ("1a",), frozenset(), True),   # the holder's own answer; no approach event is wired yet
 "staff_permission":        DecisionClass("holder", ("2",), frozenset({"event_resolution"}), True),    # an assistant's interview elsewhere; no request event is wired yet
 # Stone's My Adjustments in the bye week (rebuild step 5, builder C): it holds only the bye's own close.
 "bye_adjustments":         DecisionClass("holder", ("9","10","11"), frozenset({"bye_close"}), False),
 "personnel_transaction":   DecisionClass("caldwell", ("3","5","7","20"), frozenset({"event_resolution","week_inputs","week_close"}), False),
 "medical_status":          DecisionClass("medical_staff", ("15","16","17"), frozenset(), False),
 "staff_work":              DecisionClass("coaching_staff", (), frozenset(), False),
}
PART_LABEL = {"decisions.fourth_down": "a fourth-down rule", "decisions.two_point": "a two-point rule",
              "decisions.kickoff": "a kickoff rule", "defensive_call_sheet": "the defensive sheet",
              "offensive_call_sheet": "the offensive calls"}
# Not runtime.postseason.ROUND_TITLES: it names the 2013 Super Bowl.
ROUND_LABEL = {18: "Wild Card", 19: "Divisional", 20: "Conference Championship", 21: "Super Bowl"}


def event(kind, season, week=None, part=None, event=None):
    """An event a script is about to commit, in the form a block names it; ``event`` is the id of
    the in-season event an ``event_resolution`` settles (runtime/open_events.py)."""
    if kind not in BLOCK_KINDS:
        raise ValueError("unknown decision-queue event kind: %r" % (kind,))
    values = {"season": season, "week": week, "part": part, "event": event}
    ev = {"kind": kind}
    for key in BLOCK_KINDS[kind]:
        if values[key] is None:
            raise ValueError("%s needs %s" % (kind, key))
        ev[key] = values[key]
    extra = [k for k, v in values.items() if v is not None and k not in BLOCK_KINDS[kind]]
    if extra:
        raise ValueError("%s takes no %s" % (kind, ", ".join(extra)))
    return ev


def save(root, queue):
    """Write the queue in the layout the file already has (its indent and whether it escapes
    non-ASCII), so a change shows only what changed."""
    path = Path(root) / QUEUE
    raw = path.read_text(encoding="utf-8") if path.is_file() else ""
    try:
        old = json.loads(raw)
    except ValueError:
        old = None
    layout = next(((i, a) for i in (1, 2) for a in (False, True)
                   if old is not None and json.dumps(old, indent=i, ensure_ascii=a) + "\n" == raw), (1, False))
    path.write_text(json.dumps(queue, indent=layout[0], ensure_ascii=layout[1]) + "\n", encoding="utf-8")
    return path


def overdue_items(queue, at):
    """The OPEN items whose due time (``deadline.at``) is before ``at``, the clock's floor
    (runtime/open_events.master_at). Overdue is reported, never resolved and never an error by
    itself; an overdue trade item still holds nothing but its event."""
    from .open_events import parse_at
    out = []
    for item in unresolved(queue):
        due = (item.get("deadline") or {}).get("at")
        if due:
            try:
                if parse_at(due) < at:
                    out.append(item)
            except ValueError:
                continue
    return out


# The record of builder C2's game-day change item: a block on the week's My Responses page headed
# "Depth and inactives change" (a second that week "Depth and inactives change 2", and so on).
RESPONSES_PAGE = "My_Responses.md"
GAME_DAY_ANCHOR = re.compile(r"^depth-and-inactives-change(?:-[2-9]|-[1-9][0-9]+)?$")


def game_day_item(item, holder=None):
    """Whether ``item`` is the week's game-day depth or inactives change (builder C2): a
    ``depth_and_roles`` item of the holder, bound to no event, whose record is that change's block on
    the week's My Responses page. It is an insert (ACTION REQUIRED), not a routine ask of the week."""
    record = item.get("record") or {}
    return (item.get("class") == "depth_and_roles" and item.get("event") is None
            and (holder is None or item.get("owner") == holder)
            and str(record.get("path", "")).endswith("/" + RESPONSES_PAGE)
            and bool(GAME_DAY_ANCHOR.match(str(record.get("anchor") or ""))))


# The record of builder C1's practice ask: the "Practice week" block on the week's My Responses page.
PRACTICE_ANCHOR = "practice-week"


def practice_item(item, holder=None):
    """Whether ``item`` is the week's practice week asked on My Responses (builder C1, while no
    standing practice instruction is in force): a ``practice_plan`` item of the holder, bound to no
    event, whose record is that block. It is a routine ask of the week (the briefing's section 8),
    not an insert."""
    record = item.get("record") or {}
    return (item.get("class") == "practice_plan" and item.get("event") is None
            and (holder is None or item.get("owner") == holder)
            and str(record.get("path", "")).endswith("/" + RESPONSES_PAGE)
            and record.get("anchor") == PRACTICE_ANCHOR)


def _bye_closed(season, week, root):
    """Whether the bye week's own close is recorded (runtime/bye_week.bye_closed)."""
    from . import bye_week
    return bool(bye_week.bye_closed(SeasonPaths(season, root), root, week=int(week)))


def _withdrawal_problem(item, resolution, root, holder):
    """None when the holder's event item may be WITHDRAWN by the organization or the medical staff:
    the other side ended the question (a sourced process entry of the event, of a kind that ends it,
    stamped before the withdrawal, which the item's record names and whose summary says the question
    ended without his answer), or an injury replacement's due time passed with his recommendation
    unanswered (Caldwell decides under rows 3, 5 and 7; the summary says so). Otherwise the reason."""
    from . import open_events
    if item.get("status") != "WITHDRAWN" or resolution.get("by") not in ("organization", "medical") \
            or item.get("event") is None or item.get("owner") != holder:
        return ""
    season = next((b.get("season") for b in item.get("blocks") or () if b.get("kind") == "event_resolution"), None)
    record = open_events.get(season, item["event"], root) if type(season) is int else None
    if record is None:
        return " (its event %s has no record)" % item["event"]
    summary = str(resolution.get("summary") or "")
    if summary == open_events.DUE_TIME_SUMMARY:
        due = (item.get("deadline") or {}).get("date")
        if (record.get("kind") != "injury_replacement" or item.get("class") != "personnel_recommendation"
                or resolution["by"] != "organization" or record.get("response") is not None
                or any(e.get("kind") == "response" for e in record.get("process") or ())
                or not due or str(resolution.get("date")) < due):
            return (" (the due-time withdrawal is only an injury replacement's recommendation, unanswered, "
                    "withdrawn by the organization on or after its due date)")
        return None
    pointer = str((resolution.get("record") or {}).get("pointer") or "")
    found = re.fullmatch(r"/process/(\d+)", pointer)
    entries = record.get("process") or []
    entry = entries[int(found[1])] if found and int(found[1]) < len(entries) else None
    path = (resolution.get("record") or {}).get("path")
    own = open_events.path_of(record, Path(root).resolve()).relative_to(Path(root).resolve()).as_posix()
    if entry is None or path != own:
        return " (the other side's act is a process entry of the event, which the resolution record names)"
    if entry.get("kind") not in open_events.OTHER_SIDE_ENDINGS or not entry.get("source"):
        return " (the entry it names is not a sourced act of the other side that ends the question)"
    try:
        if open_events.parse_at(entry["at"]).date().isoformat() > str(resolution.get("date")):
            return " (the other side's act is recorded after the withdrawal)"
    except (KeyError, ValueError):
        return " (the other side's act has no valid time)"
    if open_events.OTHER_SIDE_SUMMARY.lower() not in summary.lower():
        return " (its summary must say the question ended without his answer)"
    return None


def _event_block_errors(item, blocks, root, say):
    """The hold follows the event, never the clock (rebuild step 5, A1): an item with an event holds
    that event's resolution, and a week's inputs and close only when its answer is needed to play
    that week (its deadline is before the week's inputs) and its event is an injury replacement whose
    facts record that the active roster cannot dress a legal team for that game. A trade call never
    holds the game, whatever its due time."""
    ev_id = item.get("event")
    kinds = [b.get("kind") for b in blocks]
    if ev_id is None:
        if "event_resolution" in kinds:
            say("holds an event's resolution but names no event")
        return
    from .events import EVENT_ID
    if not isinstance(ev_id, str) or not EVENT_ID.fullmatch(ev_id):
        say("names an invalid event id %r" % (ev_id,))
        return
    own = [b for b in blocks if b.get("kind") == "event_resolution"]
    if not any(b.get("event") == ev_id for b in own):
        say("carries event %s but does not hold its resolution" % ev_id)
    if any(b.get("event") != ev_id for b in own):
        say("holds the resolution of an event it does not carry")
    if any(k not in GAME_KINDS and k != "event_resolution" for k in kinds):
        say("carries event %s and may hold only its resolution and, under the hold rule, a game" % ev_id)
    games = [b for b in blocks if b.get("kind") in GAME_KINDS]
    if not games:
        return
    from . import open_events
    season = next((b.get("season") for b in own if type(b.get("season")) is int), games[0].get("season"))
    record = open_events.get(season, ev_id, root) if type(season) is int else None
    before = (item.get("deadline") or {}).get("before")
    for block in games:
        needed = before == {"kind": "week_inputs", "season": block.get("season"), "week": block.get("week")}
        if record is None:
            say("holds the Week %s game for event %s, which has no record" % (block.get("week"), ev_id))
        elif record.get("kind") == "trade_talks":
            say("is a trade call's item; a trade call never holds the game, whatever its due time (it holds "
                "only its own event)")
        elif not (needed and open_events.cannot_dress(record) and open_events.held_week(record, root) == block.get("week")):
            say("holds the Week %s game, but its answer is not needed to play it: only an injury replacement whose "
                "facts record that the active roster cannot dress a legal team for that game, due before it, holds "
                "the game" % block.get("week"))


def load(root):
    path = Path(root) / QUEUE
    try:
        queue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("%s: %s" % (QUEUE.as_posix(), exc)) from None
    if not isinstance(queue, dict) or queue.get("schema_version") != 1:
        raise ValueError("%s: schema_version must be 1" % QUEUE.as_posix())
    items = queue.get("items")
    if not isinstance(items, list) or not all(
            isinstance(i, dict) and isinstance(i.get("blocks"), list) and all(isinstance(b, dict) for b in i["blocks"])
            for i in items):
        raise ValueError("%s: items must be a list of items, each with a list of blocks" % QUEUE.as_posix())
    return queue


def expand(ev):
    """The event and the events it implies (building a week's inputs
    implies closing it; staging a season implies opening it)."""
    return [ev] + [dict(ev, kind=kind) for kind in IMPLIES.get(ev.get("kind"), ())]


def holds(item, ev):
    return item.get("status") in UNRESOLVED and any(ev == held for block in item.get("blocks") or ()
                                                    for held in expand(block))


def blocking_items(queue, events):
    """(item, the first event it holds), one per held item."""
    found = []
    for item in queue["items"]:
        ev = next((e for e in events if holds(item, e)), None)
        if ev is not None:
            found.append((item, ev))
    return found


def sheet_parts(sheet):
    parts = [key for key in ("offensive_call_sheet", "defensive_call_sheet") if key in sheet]
    return parts + ["decisions." + key for key in sheet.get("decisions") or {}]


def package_parts(package, club):
    """The call-sheet parts a frozen week package carries in ``club``'s
    inputs, so a close is held by what it would draw as well as by the
    committed sheet."""
    parts = []
    for game in package.get("games") or ():
        for side in ("home", "away"):
            data = game.get(side + "_input") or {}
            if club in (game.get(side), data.get("team_id")):
                parts += [part for key, part in INPUT_PARTS.items()
                          if data.get(key) is not None and part not in parts]
    return parts


def sheet_path(season, week, root):
    """The committed call sheet's path, as build_week_inputs.call_sheet_path
    finds it (the regular-season folder, then the postseason folder)."""
    paths = SeasonPaths(season, root)
    found = [p for p in (paths.call_sheet(week), paths.call_sheet(week, postseason=True)) if p.exists()]
    return found[0] if found else None


def committed_sheet(season, week, root):
    path = sheet_path(season, week, root)
    return json.loads(path.read_text(encoding="utf-8")) if path is not None else None


def _postseason_offset(season):
    return 1 if season >= 2021 else 0


def week_label(season, week):
    name = ROUND_LABEL.get(week - _postseason_offset(season))
    return "the %s" % name if name else "the Week %d" % week


def describe(ev):
    """What a held event is, in words, one line for every kind (an unknown kind is an error)."""
    kind = ev["kind"]
    if kind == "week_inputs":
        return "%s game: nothing for it is frozen until this is settled" % week_label(ev["season"], ev["week"])
    if kind == "week_close":
        return "%s game" % week_label(ev["season"], ev["week"])
    if kind == "call_sheet_part":
        return "freezing %s in %s call sheet" % (PART_LABEL.get(ev["part"], ev["part"]),
                                                week_label(ev["season"], ev["week"]))
    if kind == "season_stage":
        return "staging the %d season" % ev["season"]
    if kind == "season_opening":
        return "opening the %d season" % ev["season"]
    if kind == "event_resolution":
        return "settling the event %s" % ev["event"]
    if kind == "bye_close":
        return "closing the Week %d bye" % ev["week"]
    raise ValueError("unknown decision-queue event kind: %r" % (kind,))


def _is_holder(item, job):
    if job is not None:
        return item.get("owner") == job.get("holder")
    cls = CLASSES.get(item.get("class"))
    return cls is not None and cls.default_owner == "holder"


def refusal_line(item, ev, job, settle=True):
    """One item's refusal. Without ``settle`` (a paused game, or a slate
    partly closed) the line names no way to settle and rerun: the caller's
    only instruction is to revert the edit that opened the item."""
    owner = current_job.party_name(job, item.get("owner")) if job is not None else str(item.get("owner"))
    if _is_holder(item, job):
        owner += " (the user): present it to the user; do not settle it in the workflow"
    deadline = item.get("deadline") or {}
    record = item.get("record") or {}
    target = str(record.get("path")) + ("#" + record["anchor"] if record.get("anchor") else "")
    line = ("Decision open: %s, %s. It holds %s. Owner: %s.%s Record: %s."
            % (item.get("id"), item.get("title"), describe(ev), owner,
               " Needed %s." % deadline["label"] if deadline.get("label") else "", target))
    if settle:
        line += (" When it is settled, mark it RESOLVED in state/decision_queue.json with its resolution record, "
                 "run python scripts/render_career_views.py, merge, advance the private snapshot from main, "
                 "then rerun.")
    return line


def blocking_errors(events, root, settle=True):
    """One refusal line per open item holding any of ``events``. An
    unreadable queue refuses everything (the gate fails closed)."""
    try:
        queue = load(root)
    except ValueError as exc:
        return ["Decision queue unreadable (%s); nothing builds, closes or stages without it." % exc]
    try:
        job = current_job.load(root)
    except ValueError:
        job = None
    return [refusal_line(item, ev, job, settle) for item, ev in blocking_items(queue, events)]


def refuse_if_blocked(events, root):
    lines = blocking_errors(events, root)
    if lines:
        raise ValueError("; ".join(lines))


def unresolved(queue, owner=None):
    return [item for item in queue["items"]
            if item.get("status") in UNRESOLVED and (owner is None or item.get("owner") == owner)]


def _iso(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _closes(instruction, item):
    return item.get("class") in (instruction.get("closes") or ()) and (
        item.get("subject") is None or item.get("subject") == instruction.get("subject"))


def _club_weeks(season, root, club):
    return {g["week"] for g in SeasonPaths(season, root).regular_games() if club in (g["away"], g["home"])}


def _is_postseason(season, week):
    return week - _postseason_offset(season) in ROUND_LABEL


def _paused(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("status") == "paused"
    except (OSError, ValueError, AttributeError):
        return False


def validation_errors(root, mapping, events, master, job):
    """Every rule the queue must satisfy (docs/career_layer.md). An OPEN or
    overdue item is never an error by itself."""
    prefix = "Decision queue: "
    try:
        queue = load(root)
    except ValueError as exc:
        return [prefix + str(exc)]
    try:
        return _validation_errors(queue, root, mapping, events, master, job, prefix)
    except (OSError, KeyError, IndexError, TypeError, ValueError, AttributeError) as exc:
        return [prefix + "malformed queue: %s" % exc]


def _validation_errors(queue, root, mapping, events, master, job, prefix):
    root = Path(root)
    errors = []
    parties = job.get("parties") or {}
    holder = job.get("holder")
    actions = {r.get("row"): r.get("stone_action")
               for r in ((current_job.appointment(job) or {}).get("authority") or {}).get("domains") or ()}
    in_force = current_job.instructions(job)
    club = ((current_job.appointment(job) or {}).get("employer") or {}).get("club")
    club_weeks = {}
    # 1. Schema.
    since = queue.get("enforced_from")
    if not isinstance(since, dict) or type(since.get("season")) is not int or type(since.get("week")) is not int:
        errors.append(prefix + "enforced_from needs an int season and week")
        since = {"season": 9999, "week": 99}
    ids = [i.get("id") for i in queue["items"]]
    for dup in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        errors.append(prefix + "duplicate item id %s" % dup)
    plans = {}
    for item in queue["items"]:
        iid = item.get("id")
        say = lambda text: errors.append(prefix + "%s %s" % (iid, text))
        if not isinstance(iid, str) or not ITEM_ID.fullmatch(iid):
            say("has an invalid id (lowercase words joined by hyphens)")
        missing = [k for k in REQUIRED_KEYS if k not in item]
        unknown = sorted(set(item) - ITEM_KEYS)
        if missing or unknown:
            say("lacks %s / has unknown keys %s" % (", ".join(missing) or "nothing", ", ".join(unknown) or "none"))
        cls = CLASSES.get(item.get("class"))
        if cls is None:
            say("has unknown class %r" % (item.get("class"),))
        status = item.get("status")
        if status not in STATUSES:
            say("status must be one of %s" % ", ".join(STATUSES))
        raised = item.get("raised") or {}
        if raised.get("by") not in RAISED_BY:
            say("raised.by must be one of %s" % ", ".join(RAISED_BY))
        named = [("owner", item.get("owner"))] + [("adviser", p) for p in item.get("advisers") or ()]
        # A wait's owner is null where its record names none.
        named += [("waits_on owner", w["owner"]) for w in item.get("waits_on") or () if w.get("owner") is not None]
        for role, pid in named:
            if pid not in parties:
                say("names %s %r, which is not a party in the job record" % (role, pid))
        if item.get("subject") is not None and item["subject"] not in current_job.ITEM_SUBJECTS:
            say("has unknown subject %r (one of %s)" % (item["subject"], ", ".join(current_job.ITEM_SUBJECTS)))
        for row in item.get("authority_rows") or ():
            if row not in current_job.AUTHORITY_ROWS:
                say("names unknown authority row %r" % (row,))
        # 2. Blocks.
        blocks = item.get("blocks") or []
        implied = [held for block in blocks for held in expand(block)]
        for block in blocks:
            kind = block.get("kind")
            if kind not in BLOCK_KINDS:
                say("blocks unknown event kind %r" % (kind,))
                continue
            if cls is not None and (kind not in cls.may_block or (
                    kind in GAME_KINDS and item.get("class") in EVENT_GAME_CLASSES and item.get("event") is None)):
                say("is a %s item, which may not block %s" % (item.get("class"), kind))
            keys = set(block) - {"kind"}
            if keys != set(BLOCK_KINDS[kind]) or any(type(block.get(k)) is not int for k in ("season", "week")
                                                     if k in BLOCK_KINDS[kind]) or (
                    kind == "event_resolution" and not isinstance(block.get("event"), str)):
                say("block %s must have exactly the keys %s (season and week ints)" % (kind, ", ".join(BLOCK_KINDS[kind])))
                continue
            if kind == "call_sheet_part" and block["part"] not in SHEET_PARTS:
                say("blocks unknown call-sheet part %r" % (block["part"],))
            if kind in WEEK_KINDS and not _is_postseason(block["season"], block["week"]):
                key = block["season"]
                if key not in club_weeks:
                    try:
                        club_weeks[key] = _club_weeks(key, root, club)
                    except (OSError, ValueError, KeyError) as exc:
                        club_weeks[key] = set()
                        say("cannot read the %d fixtures: %s" % (key, exc))
                if block["week"] not in club_weeks[key]:
                    say("holds Week %d of %d, in which %s does not play (a bye has no plan, sheet or inactives)"
                        % (block["week"], key, club or "the club"))
            if kind == "bye_close":
                # The reverse: the bye's own close is a week in which the club does not play.
                key = block["season"]
                if key not in club_weeks:
                    try:
                        club_weeks[key] = _club_weeks(key, root, club)
                    except (OSError, ValueError, KeyError) as exc:
                        club_weeks[key] = set()
                        say("cannot read the %d fixtures: %s" % (key, exc))
                if block["week"] in club_weeks[key] or _is_postseason(key, block["week"]):
                    say("holds the close of Week %d of %d as a bye, but %s plays that week; only a bye week has a "
                        "bye close" % (block["week"], key, club or "the club"))
        _event_block_errors(item, blocks, root, say)
        deadline = item.get("deadline")
        if deadline is not None:
            if _iso(deadline.get("date")) is None:
                say("deadline.date is not an ISO date")
            if deadline.get("before") is not None and deadline["before"] not in implied:
                say("deadline.before is not one of the events it holds")
            if deadline.get("at") is not None:
                from .open_events import parse_at
                try:
                    if parse_at(deadline["at"]).date().isoformat() != deadline.get("date"):
                        say("deadline.at is not on deadline.date")
                except ValueError as exc:
                    say("deadline.at: %s" % exc)
        # 3. Owner.
        default = None if cls is None else (holder if cls.default_owner == "holder" else cls.default_owner)
        if cls is not None and item.get("owner") != default and "owner_note" not in item and "owner_basis" not in item:
            say("is owned by %s, not the class default %s, with no owner_note or owner_basis"
                % (item.get("owner"), default))
        if cls is not None and item.get("owner") == holder and not any(actions.get(r) in HOLDER_PARTS for r in cls.rows):
            say("puts %s to %s, but his appointment gives him no decision or recommendation on rows %s"
                % (item.get("class"), current_job.party_name(job, holder), ", ".join(cls.rows) or "(none)"))
        # 4. Raising.
        if cls is not None and cls.raised_only_by_user and raised.get("by") != "user":
            say("is a %s item, which only the user raises" % item.get("class"))
        # 5. Standing coverage.
        not_applied = {}
        for entry in item.get("standing_not_applied") or ():
            if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
                say("standing_not_applied %s needs a reason" % entry.get("instruction"))
            if entry.get("instruction") not in {i.get("id") for i in current_job.instructions(job, None)}:
                say("standing_not_applied names unknown instruction %s" % entry.get("instruction"))
            not_applied[entry.get("instruction")] = entry
        if status == "OPEN" and cls is not None and cls.closable_by_standing:
            for instruction in in_force:
                if _closes(instruction, item) and instruction.get("id") not in not_applied:
                    say("is covered by the standing instruction %s; settle it as covered (resolution.by "
                        "standing_instruction) or record why the instruction does not apply" % instruction.get("id"))
        # 6. Records.
        resolution = item.get("resolution")
        records = [("record", item.get("record"))] + [("sources", s) for s in item.get("sources") or ()]
        if isinstance(resolution, dict) and resolution.get("record") is not None:
            records.append(("resolution.record", resolution["record"]))
        for where, record in records:
            problem = current_job.record_error(root, mapping, record)
            if problem:
                say("%s: %s" % (where, problem))
        # 7. Dates.
        raised_on = _iso(raised.get("date"))
        if raised_on is None:
            say("raised.date is not an ISO date")
        elif raised_on > master:
            say("was raised on %s, after the master date" % raised["date"])
        for wait in item.get("waits_on") or ():
            if wait.get("date") is not None and _iso(wait["date"]) is None:
                say("waits_on date %r is not an ISO date" % (wait["date"],))
        for where, ref in (("raised.event", raised.get("event")),
                           ("resolution.event", resolution.get("event") if isinstance(resolution, dict) else None)):
            if ref is not None and ref not in events:
                say("%s %s is not a closed event" % (where, ref))
        # 8. Resolution.
        if status in ("RESOLVED", "WITHDRAWN"):
            if not isinstance(resolution, dict) or any(not resolution.get(k) for k in ("date", "by", "record", "summary")):
                say("is %s without a resolution date, by, record and summary" % status)
            else:
                settled = _iso(resolution["date"])
                if settled is None or settled > master:
                    say("resolution.date %s is not an ISO date on or before the master date" % resolution["date"])
                if resolution["by"] not in RESOLVED_BY:
                    say("resolution.by must be one of %s" % ", ".join(RESOLVED_BY))
                if item.get("owner") == holder and resolution["by"] not in ("user", "standing_instruction"):
                    # Another side's act, or an injury replacement's due time (rebuild step 5, A1).
                    problem = _withdrawal_problem(item, resolution, root, holder)
                    if problem is not None:
                        say("is %s's decision and may be settled only by the user or a standing instruction, not by %s%s"
                            % (current_job.party_name(job, holder), resolution["by"], problem))
                if resolution["by"] == "standing_instruction":
                    named_rule = next((i for i in in_force if i.get("id") == resolution.get("standing_instruction")), None)
                    if cls is not None and not cls.closable_by_standing:
                        say("is settled by a standing instruction, but the class %s does not close by a standing "
                            "instruction (foundation/decision_rules.md section 4)" % item.get("class"))
                    elif named_rule is None or not _closes(named_rule, item):
                        say("is settled by a standing instruction, but %r is no IN_FORCE instruction that closes %s"
                            % (resolution.get("standing_instruction"), item.get("class")))
        elif status == "OPEN" and resolution is not None:
            say("is OPEN with a resolution")
        if status == "OPEN":
            # 9. Closed while open. A block on a call-sheet part the closed
            # week's committed sheet never froze held nothing: the closing
            # commit moves it to the next week the club plays (bookkeeping,
            # not a settlement). The holder's decision is never settled here.
            weeks = sorted({(b["season"], b["week"]) for b in blocks
                            if b.get("kind") in WEEK_KINDS and type(b.get("season")) is int and type(b.get("week")) is int})
            for season, week in weeks:
                paths = SeasonPaths(season, root)
                folder = paths.postseason_receipts if _is_postseason(season, week) else paths.receipts
                if any(folder.glob("week_%02d_*.json" % week)):
                    label = week_label(season, week)[4:]
                    held = [b for b in blocks if b.get("kind") in WEEK_KINDS
                            and (b.get("season"), b.get("week")) == (season, week)]
                    frozen = sheet_parts(committed_sheet(season, week, root) or {})
                    unfrozen = [b["part"] for b in held
                                if b["kind"] == "call_sheet_part" and b.get("part") not in frozen]
                    if len(unfrozen) == len(held):
                        say("is open, but %s of %d has closed without freezing %s in its call sheet; move the block "
                            "to the next week in which %s plays in the closing commit (bookkeeping, not a settlement)"
                            % (label, season, " or ".join(PART_LABEL.get(p, p) for p in unfrozen), club or "the club"))
                    elif item.get("owner") == holder:
                        say("is open, but %s of %d has closed; it is %s's decision, which the workflow may not "
                            "resolve or withdraw: present it to the user"
                            % (label, season, current_job.party_name(job, holder)))
                    else:
                        say("is open, but %s of %d has closed; resolve or withdraw it in the closing commit"
                            % (label, season))
                # 10. Paused.
                if any(h.get("kind") == "week_close" and h.get("week") == week for h in implied):
                    for post in (False, True):
                        if _paused(paths.paused_game(week, post)):
                            say("holds %s of %d while that game is paused; Document 5 and the queue must not "
                                "change during a pause" % (week_label(season, week)[4:], season))
            # 9b. The bye's own close: an open item on a bye that has closed.
            for held in implied:
                if held.get("kind") == "bye_close" and _bye_closed(held["season"], held["week"], root):
                    say("is open, but the Week %d bye of %d has closed" % (held["week"], held["season"]))
            # 9a. Opened or staged while held.
            for held in implied:
                if held.get("kind") == "season_opening" and int(mapping["active_season"]) >= held["season"]:
                    say("holds opening the %d season, which is already active" % held["season"])
                if (held.get("kind") == "season_stage"
                        and SeasonPaths(held["season"], root).record("opening_handoff.json").exists()):
                    say("holds staging the %d season, which is already staged" % held["season"])
        if item.get("class") == "weekly_game_plan" and status == "RESOLVED":
            for block in blocks:
                if block.get("kind") == "week_inputs":
                    plans[(block.get("season"), block.get("week"))] = True
    # 11. Plan before sheet.
    active = int(mapping["active_season"])
    if active >= since["season"]:
        first = since["week"] if active == since["season"] else 1
        last = 22 if active >= 2021 else 21
        for week in range(first, last + 1):
            if sheet_path(active, week, root) is not None and (active, week) not in plans:
                errors.append(prefix + "call sheet for %s exists without Stone's resolved weekly plan item"
                              % week_label(active, week)[4:])
    return errors
