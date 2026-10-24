"""My Responses: Stone's one answer page for a week's or a phase's inserted events (rebuild step 5,
A3; foundation/templates/event_inserts/my_responses_template.md; docs/event_inserts.md, A.4).

The page is his record. It is created when its first block is needed (an ACTION event first routed
by a brief, builder C1's practice ask or builder C2's game-day change) and grows only by blocks
appended at its end (``append_block``, the one writer), so the earlier bytes stay an exact prefix.
Each block is a ``##`` heading with the notice's title and the template's four lines (My answer, My
football or professional reason, Conditions or instructions, Date answered). The page shows names
only; the binding of each heading to its event or queue item is in the period's data record
(``responses.json``), with each applied block's digest. The reserved headings (Depth and inactives
change, Practice week: runtime/decisions.RESERVED_HEADINGS) are builder C's own and are skipped here.

``check`` holds a page to the template's validation rules in football words; ``apply`` records each
answered block: it fills the empty "Date answered" line with the master date (the runner's only
edit to his page), freezes the block by its digest, compiles what the answer commits to
(``substance``: support, oppose, recommend with the named option, a condition in his words, or his
permission to let it lapse), settles the queue item by the user with the block as its record, and
stores the response on the event with a dated response entry. A recommendation is never an
execution: the person with the authority decides, from the criteria and the substance. An applied
block is frozen; a change is a new block headed "Revised: <title>". Silence is never yes or no: an
empty answer leaves the question open, and "Leave this open until <date>" keeps it open until then.

The career layer (tests/test_career_layer_isolation.py, LAYER): nothing that resolves a game
imports this module.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

from . import current_job, decision_queue, decisions, open_events
from .events import repository_map

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("My answer", "My football or professional reason", "Conditions or instructions", "Date answered")
FIELD = re.compile(r"^\*\*(%s):\*\*[ \t]*(.*)$" % "|".join(re.escape(f) for f in FIELDS))
HEADING = re.compile(r"^## (.+?)\s*$")
REVISED = "Revised: "
RECORD_ABOUT = ("The binding of each heading on the period's My Responses page to its event or queue item (the "
                "page shows names only), and each applied block's digest, date and what it commits to. Written "
                "only by runtime/responses.py; validation holds every applied block to its digest.")
LEAVE_OPEN = re.compile(r"^leave (?:this|it) open until (.+?)\.?$", re.I)
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_TEXT = re.compile(r"\b(%s) (\d{1,2})(?:, (\d{4}))?\b" % MONTHS)
# What an answer commits to, read from its words (``compile_substance``): his reasons stay on his page.
LAPSE = re.compile(r"\b(let (?:it|the deadline|the offer|the call|the question) (?:lapse|pass)|"
                   r"permit (?:it|the deadline) to (?:lapse|pass)|it may lapse)\b", re.I)
CONDITION = re.compile(r"\b(?:only if|only when|provided that|provided|on condition that|on the condition that|"
                       r"as long as|so long as|if|unless)\b\s+(.+)", re.I)
OPPOSE = re.compile(r"\b(oppose[sd]?|against|reject|decline|do not support|don't support|not support)\b", re.I)
NOT_OPPOSED = re.compile(r"\b(?:do not|don't|not) oppose\b", re.I)
SUPPORT = re.compile(r"\b(support|in favor|in favour|accept|approve|yes|recommend|agree)\b", re.I)


# ------------------------------------------------------------------ the period's pages
def period_of(season, week, root=ROOT):
    """The period a week number names: the bye while that week is a bye of the club (no Jacksonville
    game), otherwise the game week."""
    games = {int(g["week"]) for g in open_events.club_fixtures(season, root)}
    return {"week": int(week)} if int(week) in games or int(week) > max(games) else {"bye": int(week)}


def pages_of(season, period, root=ROOT):
    """The period's pages (decisions.WeekPages or ByeWeekPages)."""
    (kind, week), = period.items()
    if kind == "week":
        return decisions.week_pages(season, week, root)
    if kind == "bye":
        return decisions.bye_pages(season, week, root)
    raise ValueError("a phase's My Responses page is not built in step 5: %r" % (period,))


def record_of(season, period, root=ROOT):
    """The period's binding and apply record ({about, period, blocks})."""
    path = pages_of(season, period, root).responses_record
    if not path.is_file():
        return {"about": RECORD_ABOUT, "period": dict(period), "blocks": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_record(season, period, root, record):
    path = pages_of(season, period, root).responses_record
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def title(season, period):
    (kind, week), = period.items()
    return "# Week %d My Responses" % week if kind == "week" else "# Week %d bye My Responses" % week


def intro(season, period, root):
    pages = pages_of(season, period, root)
    brief = pages.briefing if hasattr(pages, "briefing") else pages.review
    name = "Game Week Briefing" if hasattr(pages, "briefing") else "Bye Week Review"
    return ("Your answers to the notices at the top of the %s, one block each, under the notice's own "
            "heading. Fill in a block's lines in place, or upload a .md or .txt file with the same headings; "
            "the staff checks it and tells you what is missing before anything is recorded. An empty answer "
            "leaves the question open; no answer is never a yes or a no. [%s](%s)" % (name, name, brief.name))


def block_text(heading):
    """A blank block: the heading and the template's four lines."""
    return "\n".join(["## %s" % heading, ""] + sum((["**%s:**" % f, ""] for f in FIELDS), [])) + "\n"


def event_heading(record, existing):
    """The heading for an event's block: its notice title, numbered " (2)", " (3)" when the page
    already has it."""
    base = open_events.title(record)
    heading, n = base, 1
    while heading in existing:
        n += 1
        heading = "%s (%d)" % (base, n)
    return heading


# ------------------------------------------------------------------ parsing
@dataclass
class Block:
    heading: str
    text: str                               # the block's bytes, its heading line to the next heading
    fields: dict = field(default_factory=dict)
    line: int = 0                           # the heading's line on the page (1-based)

    @property
    def answer(self):
        return self.fields.get("My answer", "").strip()

    @property
    def sha256(self):
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def parse(text):
    """[Block] of a My Responses page, in order: each ``##`` heading, its bytes and its four lines
    (a line's text runs on in the lines below its label until the next label)."""
    lines = text.split("\n")
    starts = [n for n, line in enumerate(lines) if HEADING.match(line)]
    out = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(lines)
        chunk = lines[start:end]
        body = "\n".join(chunk)
        if i + 1 < len(starts) or text.endswith("\n"):
            body += "\n" if i + 1 < len(starts) else ""
        fields, current = {}, None
        for line in chunk[1:]:
            m = FIELD.match(line)
            if m:
                current = m[1]
                fields[current] = m[2].strip()
            elif current and line.strip():
                fields[current] = (fields[current] + "\n" + line.strip()).strip()
        out.append(Block(HEADING.match(lines[start])[1], body, fields, start + 1))
    return out


def blocks_of(text):
    return {b.heading: b for b in parse(text)}


# ------------------------------------------------------------------ the one writer
def append_block(period, heading, item, root=ROOT, season=None):
    """Append a blank block headed ``heading`` to the period's My Responses page, bound to ``item``
    (the queue item that carries the answer, and its event when it has one; None for a reserved
    heading's block before its item exists), creating the page with its title and intro when it
    has none. The earlier bytes stay an exact prefix. Refused for a heading already on the page."""
    root = Path(root).resolve()
    season = int(repository_map(root)["active_season"]) if season is None else season
    pages = pages_of(season, period, root)
    page = pages.responses
    text = page.read_text(encoding="utf-8") if page.is_file() else ""
    if heading in blocks_of(text):
        raise ValueError("My Responses already has a block headed %r" % heading)
    if not text:
        text = "%s\n\n%s\n\n" % (title(season, period), intro(season, period, root))
    elif not text.endswith("\n\n"):
        text += "\n" if text.endswith("\n") else "\n\n"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text + block_text(heading), encoding="utf-8")
    record = record_of(season, period, root)
    entry = {"heading": heading, "item": (item or {}).get("id"), "event": (item or {}).get("event"),
             "reserved": decisions.reserved_heading(heading), "applied": None}
    record["blocks"] = list(record.get("blocks") or []) + [entry]
    _save_record(season, period, root, record)
    return page


def ensure_blocks(route, root=ROOT):
    """The blocks a brief's route needs: one for each ACTION event first routed, bound to its item
    (C2's game-day change and C1's practice ask append their own reserved blocks). Returns the
    headings appended."""
    if route.period is None or "phase" in route.period:
        return []
    record = record_of(route.season, route.period, root)
    bound = {b.get("event") for b in record.get("blocks") or ()} | {b.get("item") for b in record.get("blocks") or ()}
    page = pages_of(route.season, route.period, root).responses
    existing = set(blocks_of(page.read_text(encoding="utf-8")) if page.is_file() else {})
    added = []
    for notice in route.action:
        if notice.record is None or notice.key in bound or notice.item is None:
            continue
        heading = event_heading(notice.record, existing)
        append_block(route.period, heading, notice.item, root, route.season)
        existing.add(heading)
        added.append(heading)
    return added


# ------------------------------------------------------------------ what an answer commits to
def _normal(text):
    return re.sub(r"\s+", " ", text.strip().rstrip(".!")).strip()


def compile_substance(answer, conditions, record):
    """What the answer commits to, from its words only (never from how long or how sure it sounds):
    {"kind": "lapse"}; {"kind": "condition", "condition": his words} (with the "option" he names, if
    one); {"kind": "recommend", "option": the named option}; {"kind": "oppose"}; {"kind": "support"};
    None when it says none of them. A condition written under "Conditions or instructions" makes his
    support conditional; it does not change an opposition or a named recommendation."""
    text = _normal(answer)
    if LAPSE.search(text):
        return {"kind": "lapse"}
    options = [o["name"] for o in (record or {}).get("options") or ()]
    named = [o for o in options if o.lower() in text.lower()]
    condition = CONDITION.search(text)
    if condition:
        out = {"kind": "condition", "condition": _normal(condition[1])}
        if len(named) == 1:
            out["option"] = named[0]
        return out
    if len(named) == 1:
        return {"kind": "recommend", "option": named[0]}
    if OPPOSE.search(text) and not NOT_OPPOSED.search(text):
        return {"kind": "oppose"}
    if SUPPORT.search(text) or NOT_OPPOSED.search(text):
        extra = _normal(conditions or "")
        if extra.lower() not in ("", "none", "none additional", "no"):
            return {"kind": "condition", "condition": extra}
        return {"kind": "support"}
    return None


# ------------------------------------------------------------------ the check
@dataclass
class Checked:
    """A page checked: ``problems`` in football words, ``notes``, and the blocks ready to apply."""
    problems: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    ready: list = field(default_factory=list)       # (Block, binding, event record, substance)


def _known_names(season, root):
    """Every player, coach and party name the page may name, and the clubs."""
    from . import roster as roster_record
    from .seasons import SeasonPaths
    paths = SeasonPaths(season, root)
    names = {p["name"] for p in roster_record.load(paths.roster).get("players") or ()}
    for record in (Path(root) / "data/people/coaches").glob("*.json"):
        try:
            names.add(json.loads(record.read_text(encoding="utf-8"))["name"])
        except (OSError, ValueError, KeyError):
            continue
    job = current_job.load(root)
    names |= {p.get("name") for p in (job.get("parties") or {}).values() if p.get("name")}
    for game in paths.regular_games():
        names |= {game["away"], game["home"], game["away"].rsplit(" ", 1)[0], game["home"].rsplit(" ", 1)[0]}
    return {n for n in names if n}


# A run of capitalized words (a name like "A.J. Bouye" keeps its initials; a sentence's full stop ends it).
WORD = r"[A-Z](?:(?:\.[A-Z])+\.|[a-zA-Z'-]*)"
NAME_RUN = re.compile(r"\b%s(?: %s)+" % (WORD, WORD))
NOT_NAMES = set(MONTHS.split("|")) | {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
                                      "ET", "I", "We", "My", "Our", "The", "If", "Only", "Keep", "Recommend",
                                      "Support", "Oppose", "Leave", "Let", "Week", "Revised", "None"}


def _unknown_names(text, known, record):
    extra = {o["name"] for o in (record or {}).get("options") or ()} | {(record or {}).get("subject", "")}
    out = []
    for run in NAME_RUN.findall(text):
        words = run.split()
        while words and words[0] in NOT_NAMES:
            words = words[1:]
        while words and words[-1] in NOT_NAMES:
            words = words[:-1]
        if len(words) < 2:
            continue
        name = " ".join(words)
        if not any(name == k or name in k or k in name for k in known | extra if k):
            out.append(name)
    return out


def _dates(text, year):
    out = []
    for m in DATE_TEXT.finditer(text):
        try:
            out.append(dt.datetime.strptime("%s %s %s" % (m[1], m[2], m[3] or year), "%B %d %Y").date())
        except ValueError:
            continue
    return out


def binding_of(bound, heading):
    """A block's binding: its own, or for "Revised: <title>" the binding of the recorded block it
    revises (the same event and item, not yet applied)."""
    if heading in bound:
        return bound[heading]
    if heading.startswith(REVISED):
        earlier = bound.get(heading[len(REVISED):])
        if earlier is not None and earlier.get("applied"):
            return {"heading": heading, "item": earlier.get("item"), "event": earlier.get("event"),
                    "reserved": None, "applied": None}
    return None


def check(season, period, root=ROOT, text=None):
    """The page against the template's validation rules, in football words (``Checked``)."""
    from .clean_pages import page_errors
    root = Path(root).resolve()
    pages = pages_of(season, period, root)
    out = Checked()
    if text is None:
        if not pages.responses.is_file():
            out.notes.append("No My Responses page for %s: nothing waits on an answer there"
                             % open_events.period_label(period))
            return out
        text = pages.responses.read_text(encoding="utf-8")
    rel = pages.responses.relative_to(root).as_posix()
    out.problems += [e.split(": ", 1)[-1] for e in page_errors(rel, text, root=root)]
    record = record_of(season, period, root)
    bound = {b["heading"]: b for b in record.get("blocks") or ()}
    clock = open_events.master_clock(root)
    known = _known_names(season, root)
    job = current_job.load(root)
    queue = decision_queue.load(root)
    events = {r["id"]: r for r in open_events.load(season, root)}
    for block in parse(text):
        if decisions.reserved_heading(block.heading):
            continue                                    # builder C's own blocks
        say = lambda t: out.problems.append("%s: %s" % (block.heading, t))
        binding = binding_of(bound, block.heading)
        if binding is None:
            fyi = next((r for r in events.values() if open_events.title(r) == block.heading.replace(REVISED, "", 1)
                        and not open_events.needs_answer(r)), None)
            if fyi is not None:
                say("None needed: %s; to change that, write the new rule in your words" % _no_answer_why(fyi, job))
            else:
                say("this heading is not a notice of %s; answer under a notice's own heading"
                    % open_events.period_label(period))
            continue
        applied = binding.get("applied")
        if applied is not None:
            if applied.get("sha256") != block.sha256:
                say("this answer was recorded on %s and stays as written; to change it, add a new block headed "
                    "%s%s" % (_long(applied["date"]), REVISED, block.heading.replace(REVISED, "", 1)))
            continue
        event = events.get(binding.get("event")) if binding.get("event") else None
        item = next((i for i in queue["items"] if i.get("id") == binding.get("item")), None)
        if binding.get("event") and event is None:
            say("the notice it answers is not on record")
            continue
        if event is not None:
            if not open_events.known_to_stone(event, job):
                say("the notice it answers was not brought to you")
                continue
            if event["state"] == "resolved":
                if block.answer:
                    say("this question is settled (%s); your answer is not recorded"
                        % event["resolution"]["outcome"].replace("_", " "))
                continue
            if not open_events.needs_answer(event):
                say("None needed: %s; to change that, write the new rule in your words" % _no_answer_why(event, job))
                continue
        if not block.answer:
            due = (item or {}).get("deadline") or {}
            if due.get("at") and clock.overdue(open_events.parse_at(due["at"])):
                out.notes.append("%s: still open, past its due time (%s); nothing is decided without your answer"
                                 % (block.heading, open_events.at_text(open_events.parse_at(due["at"]))))
            else:
                out.notes.append("%s: still open; no answer yet" % block.heading)
            continue
        leave = LEAVE_OPEN.match(_normal(block.answer) + ".")
        due_at = open_events.parse_at(event["deadline"]["at"]) if event and event.get("deadline") else None
        year = clock.date.year
        if leave:
            until = _dates(leave[1], year)
            if not until:
                say("write the date to leave it open until, like October 15")
            elif due_at is not None and until[0] > due_at.date():
                say("it cannot be left open past its due time (%s)" % open_events.at_text(due_at))
            elif due_at is not None and clock.overdue(due_at):
                say("its due time has passed (%s)" % open_events.at_text(due_at))
            else:
                out.notes.append("%s: left open until %s, as you wrote" % (block.heading, _long(until[0].isoformat())))
            continue
        for name in _unknown_names("; ".join([block.answer, block.fields.get(FIELDS[2], "")]), known, event):
            say("%s is not on the roster or the coach records" % name)
        for when in _dates(" ".join(block.fields.get(f, "") for f in FIELDS[:3]), year):
            if due_at is not None and when > due_at.date():
                say("%s is after the question's due time (%s)" % (_long(when.isoformat()), open_events.at_text(due_at)))
        if due_at is not None and clock.overdue(due_at):
            say("its due time has passed (%s); an answer after it is not recorded" % open_events.at_text(due_at))
            continue
        substance = compile_substance(block.answer, block.fields.get(FIELDS[2], ""), event)
        if substance is None:
            say("say whether you support it, oppose it, recommend one of its options or set a condition")
            continue
        if substance["kind"] == "recommend" and event is not None and not event.get("options"):
            substance = {"kind": "support"}
        written = block.fields.get(FIELDS[3], "").strip()
        if written and written != _long(clock.date.isoformat()) and binding.get("applied") is None:
            say("Date answered is filled in by the staff when the answer is recorded; leave it empty")
            continue
        out.ready.append((block, binding, event, substance))
    return out


def _no_answer_why(record, job):
    part = record.get("stone_part", "")
    if part.startswith("standing:"):
        rule = next((i for i in current_job.instructions(job, None) if i.get("id") == part.split(":", 1)[1]), {})
        return "your standing instruction answers it (%s)" % (rule.get("summary") or "on record").rstrip(".")
    return "%s decides it and it reaches you as news" % (record["subject"] if record["authority"]["decides"] ==
                                                         open_events.OTHER_CLUB else
                                                         current_job.party_name(job, record["authority"]["decides"]))


def _long(iso):
    d = dt.date.fromisoformat(iso)
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


# ------------------------------------------------------------------ the upload
def place_upload(root, season, period, source):
    """An uploaded .md or .txt file becomes the period's My Responses page; refused, with nothing
    written, for another kind of file, a ``##`` heading neither bound nor reserved, an applied block
    that differs from its recorded digest, an answer for an event that is resolved or a block for one
    that is not open (judged by the event's state). It writes only My_Responses.md, never the Game
    Plan."""
    root = Path(root).resolve()
    source = Path(source)
    if source.suffix.lower() not in (".md", ".txt"):
        raise ValueError("an uploaded My Responses page is a .md or .txt file")
    text = source.read_text(encoding="utf-8")
    text = text if text.endswith("\n") else text + "\n"
    record = record_of(season, period, root)
    bound = {b["heading"]: b for b in record.get("blocks") or ()}
    events = {r["id"]: r for r in open_events.load(season, root)}
    problems = []
    for block in parse(text):
        if decisions.reserved_heading(block.heading):
            continue
        binding = binding_of(bound, block.heading)
        if binding is None:
            problems.append("%s: this heading is not a notice of %s" % (block.heading, open_events.period_label(period)))
            continue
        if binding.get("applied") and binding["applied"].get("sha256") != block.sha256:
            problems.append("%s: this answer was recorded and stays as written" % block.heading)
            continue
        event = events.get(binding.get("event")) if binding.get("event") else None
        if event is not None and event["state"] == "resolved" and block.answer and not binding.get("applied"):
            problems.append("%s: this question is settled; an answer for it is not recorded" % block.heading)
        elif event is not None and event["state"] == "resolved":
            continue
    missing = [h for h, b in bound.items() if b.get("applied") and h not in blocks_of(text)]
    problems += ["%s: a recorded answer cannot be removed" % h for h in missing]
    if problems:
        raise ValueError("; ".join(problems))
    page = pages_of(season, period, root).responses
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text, encoding="utf-8")
    return page


# ------------------------------------------------------------------ the apply
def apply(season, period, root=ROOT):
    """Record every answered block that passes the check (``check``): returns (problems, applied
    headings). With any problem nothing is recorded. Refused while a game is paused."""
    root = Path(root).resolve()
    from scripts.render_career_views import paused_games
    if paused_games(root):
        return ["A Jacksonville game is paused; nothing is recorded until it is finished"], []
    checked = check(season, period, root)
    if checked.problems:
        return checked.problems, []
    if not checked.ready:
        return [], []
    pages = pages_of(season, period, root)
    page_rel = pages.responses.relative_to(root).as_posix()
    clock = open_events.master_clock(root)
    on = _long(clock.date.isoformat())
    text = pages.responses.read_text(encoding="utf-8")
    # Fill each answered block's empty "Date answered" line: the runner's only edit to his page.
    for block, _, _, _ in checked.ready:
        if not block.fields.get(FIELDS[3], "").strip():
            filled = re.sub(r"^\*\*Date answered:\*\*[ \t]*$", "**Date answered:** %s" % on, block.text, count=1,
                            flags=re.M)
            text = text.replace(block.text, filled, 1)
    pages.responses.write_text(text, encoding="utf-8")
    now = blocks_of(text)
    record = record_of(season, period, root)
    queue = decision_queue.load(root)
    at = clock.at if clock.timed else open_events.et(clock.date)
    applied = []
    for block, binding, event, substance in checked.ready:
        frozen = now[block.heading]
        anchor = _anchor(block.heading)
        entry = next((b for b in record["blocks"] if b["heading"] == block.heading), None)
        if entry is None:                       # a revision he wrote himself: bound to the block it revises
            entry = dict(binding)
            record["blocks"].append(entry)
        entry["applied"] = {"sha256": frozen.sha256, "date": clock.date.isoformat(), "substance": substance}
        item_id = binding.get("item")
        for item in queue["items"]:
            if item.get("id") == item_id and item.get("status") == "OPEN":
                item["status"] = "RESOLVED"
                item["resolution"] = {"date": clock.date.isoformat(), "by": "user",
                                      "record": {"path": page_rel, "anchor": anchor},
                                      "summary": "Answered on My Responses: %s." % _summary(substance)}
        applied.append((block.heading, event, frozen, substance))
    _save_record(season, period, root, record)
    decision_queue.save(root, queue)
    for heading, event, frozen, substance in applied:
        if event is None:
            continue
        response = {"page": page_rel, "heading": heading, "sha256": frozen.sha256, "date": clock.date.isoformat(),
                    "substance": substance}
        _record_response(season, event["id"], response, {"path": page_rel, "anchor": _anchor(heading)}, at, root)
    return [], [h for h, _, _, _ in applied]


def _anchor(heading):
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def _summary(substance):
    kind = substance["kind"]
    if kind == "recommend":
        return "recommends %s" % substance["option"]
    if kind == "condition":
        return "supports it on a condition"
    return {"support": "supports it", "oppose": "opposes it", "lapse": "lets it lapse"}[kind]


def _record_response(season, event_id, response, source, at, root):
    """The response on the event, with its dated response entry: the event moves to answered and
    nothing is executed (the person with the authority decides)."""
    record = open_events.get(season, event_id, root)
    entry = {"at": open_events.iso(at), "kind": "response", "what": "Stone answered on My Responses: %s."
             % _summary(response["substance"]), "by": current_job.load(root).get("holder"), "source": source}
    open_events.add_process(season, event_id, entry, root, state="answered")
    record = open_events.get(season, event_id, root)
    record["response"] = response
    errors = open_events.record_errors(record, root, issues_=open_events.Issues(season, root),
                                       queue=decision_queue.load(root))
    if errors:
        raise ValueError("; ".join(errors))
    open_events._write(record, root)


# ------------------------------------------------------------------ validation
def validation_errors(root=ROOT):
    """Every applied block of the season's My Responses pages held to its recorded digest, and every
    binding to a heading on its page (the lead wires this into scripts/validate_repository.py). A game
    week's and the bye's pages share the week's folder, so each week's record is read once."""
    root = Path(root).resolve()
    season = int(repository_map(root)["active_season"])
    errors = []
    for week in range(1, 23):
        try:
            pages = decisions.week_pages(season, week, root)
        except (OSError, ValueError, KeyError):
            continue
        if not pages.responses_record.is_file():
            continue
        try:
            record = json.loads(pages.responses_record.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append("My Responses, Week %d: its record is unreadable: %s" % (week, exc))
            continue
        label = "My Responses, %s" % open_events.period_label(record.get("period") or {"week": week})
        if not pages.responses.is_file():
            errors.append("%s: the page is missing (%s)" % (label, pages.responses.relative_to(root).as_posix()))
            continue
        blocks = blocks_of(pages.responses.read_text(encoding="utf-8"))
        for entry in record.get("blocks") or ():
            block = blocks.get(entry.get("heading"))
            if block is None:
                errors.append("%s: the block %s is missing from the page" % (label, entry.get("heading")))
            elif entry.get("applied") and entry["applied"].get("sha256") != block.sha256:
                errors.append("%s: the answer under %s differs from the one recorded on %s; an applied block stays "
                              "as written" % (label, entry["heading"], entry["applied"].get("date")))
    return errors
