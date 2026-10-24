"""The inserts at the top of the active brief and the one reissue rule (rebuild step 5, A2;
docs/event_inserts.md, sections A.3, A.6 and C; the layout of
foundation/templates/event_inserts/brief_action_inserts_template.md).

``render`` turns a brief's route (runtime/open_events.route: ACTION REQUIRED, FOR YOUR
INFORMATION, COMING UP) into its insert sections, each left out when empty, so a brief with no
inserts keeps its bytes exactly. Every line comes from the stored record: the facts and options as
recorded (names, positions, dates and sourced terms, never a grade), the staff's position and the
football consequence as their authors stored them ("Not yet supplied" and "To come" when absent),
the times in ET where they are known and "not set" otherwise, and the fixed wording of why the
answer is his and what happens with no answer, derived only from his part, the authority and the
due time. No event id, file path or system word is printed; the answer and the records are links.

``reissue_reason`` is the one rule for every brief (docs/event_inserts.md A.6): a new issue only
for (a) an answer the current issue does not show, (b) a dated finding recorded after it that
changes a choice still pending, or (c) an answer due before the next scheduled issue that the
current issue does not show. A change only to FOR YOUR INFORMATION or COMING UP waits for the next
scheduled issue, and Stone's own answers are never a change of situation. ``plan_issue_problems``
lets a Game Plan written against an earlier issue stand when the reissue only added or changed
inserts.

The career layer (tests/test_career_layer_isolation.py, LAYER): nothing that resolves a game
imports this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re

from . import current_job, decisions, open_events

SECTIONS = ("ACTION REQUIRED", "FOR YOUR INFORMATION", "COMING UP")
HEADINGS = tuple("## " + s for s in SECTIONS)
NUMBERS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine",
           10: "Ten"}
# The one reissue rule, as the block that carries ACTION REQUIRED states it to him.
ONE_RULE = ("**When this briefing is issued again:** when a new matter needs your answer, when a recorded finding "
            "changes a choice still open, or when an answer falls due before the next scheduled briefing; each "
            "earlier issue is kept as you saw it.")
NOT_SUPPLIED = "Not yet supplied."
TO_COME = "To come."
OUTCOME_WORDS = {"executed": "completed", "no_move": "no move made", "accepted": "accepted", "rejected": "rejected",
                 "declined": "declined", "withdrawn": "withdrawn", "lapsed": "lapsed",
                 "ended_without_agreement": "ended without agreement"}
# Why the answer is his, from his part in the decision (``stone_part``) and who decides it.
WHY = {"recommends": "Your football recommendation to %s; %s decides.",
       "consulted": "%s consults you before deciding; %s decides.",
       "decides": "Your decision as head coach."}
CHOICES = {"recommends": "Support it, oppose it, or support it on a condition you name.",
           "consulted": "Support it, oppose it, or support it on a condition you name.",
           "decides": "Your decision, in your words."}
NOTE = "the briefing has been reissued with new notices at the top; your answers stand"


# ------------------------------------------------------------------ small helpers
def _link(page_rel, target_rel, label, anchor=""):
    path = os.path.relpath(target_rel, os.path.dirname(page_rel)).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, path.replace(" ", "%20"), "#" + anchor if anchor else "")


def slug(heading):
    """A heading's anchor, as repository validation finds it (scripts/validate_repository.anchors)."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def _title_of(path):
    """A page's first heading, or None."""
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        return None
    return None


def _day(value):
    when = value if isinstance(value, dt.date) else dt.date.fromisoformat(value)
    return "%s, %s %d" % (when.strftime("%A"), when.strftime("%B"), when.day)


def _by(entry):
    when = dt.date.fromisoformat(entry["date"])
    return " (%s, %s %d)" % (entry["author"], when.strftime("%B"), when.day)


def _authored(entry, missing):
    return "%s%s" % (entry["text"].rstrip(), _by(entry)) if entry else missing


def _due_words(at):
    """"4 p.m. ET on Wednesday, October 15"."""
    clock = open_events.at_text(at).split(", ")[-1]
    return "%s on %s" % (clock, _day(at.date()))


def _quote(lines):
    out = []
    for line in lines:
        out.append(">" if line == "" else "> " + line)
    return out


def _pages(route):
    """The period's pages: a game week's (WeekPages) or the bye's (ByeWeekPages), or None for a phase."""
    (kind, week), = route.period.items()
    if kind == "week":
        return decisions.week_pages(route.season, week, route.root)
    if kind == "bye":
        return decisions.bye_pages(route.season, week, route.root)
    return None


def responses_page(route):
    """The period's My Responses page (a game week's or the bye's)."""
    pages = _pages(route)
    return pages.responses if pages is not None else None


def answer_heading(route, key, default):
    """The heading of a notice's block on the period's My Responses page: as its record binds it
    (runtime/responses.py: ``blocks``, each with its heading and its event or item), or the notice's
    title before the block is written."""
    pages = _pages(route)
    if pages is None:
        return default
    try:
        blocks = json.loads(pages.responses_record.read_text(encoding="utf-8")).get("blocks") or []
    except (OSError, ValueError, AttributeError):
        return default
    found = next((b for b in blocks if key in (b.get("event"), b.get("item"))), None)
    return found["heading"] if found else default


def _record_link(page_rel, root, record, label=None):
    """A link to a football page a record names, or None when it names a data file (never linked)."""
    if not isinstance(record, dict) or not str(record.get("path", "")).startswith("career/") \
            or not str(record["path"]).endswith(".md"):
        return None
    target = Path(root) / record["path"]
    return _link(page_rel, record["path"], label or _title_of(target) or "The record", record.get("anchor") or "")


# ------------------------------------------------------------------ the notices
def action_lines(notice, route, page_rel, job):
    """One ACTION REQUIRED notice, in the template's layout."""
    record, item = notice.record, notice.item
    root = Path(route.root)
    due = open_events.at_text(notice.due) if notice.due else "not set"
    answers = responses_page(route)
    if record is None:
        # Builder C2's game-day depth or inactives change: an item of his own, with no event record.
        heading = answer_heading(route, item["id"], item["title"])
        received = _day(item["raised"]["date"])
        lines = ["**%s** | Received: %s | **Response due: %s**" % (item["title"].rstrip("."), received, due), "",
                 "**From:** %s" % current_job.party_name(job, "medical_staff" if item["raised"].get("by") == "medical"
                                                         else "coaching_staff"), "",
                 "**What happened:** %s" % item["question"], "",
                 "**Why it needs you:** %s" % WHY["decides"], "",
                 "**If no agreement is reached:** %s" % (
                     "Kickoff is at %s; no answer is never a yes or a no." % _due_words(notice.due) if notice.due
                     else "No deadline is set; no answer is never a yes or a no."), ""]
        if answers is not None:
            lines += ["**Your answer:** %s" % _link(page_rel, answers.relative_to(root).as_posix(), heading,
                                                     slug(heading)), ""]
        lines += ["**Individual event result:** Pending"]
        return lines
    title = open_events.title(record)
    heading = answer_heading(route, record["id"], title)
    decides = current_job.party_name(job, record["authority"]["decides"])
    part = record["stone_part"]
    pronoun = "he" if ((job.get("parties") or {}).get(record["authority"]["decides"]) or {}).get("kind") == "person" \
        else "they"
    why = WHY[part] % ((decides, pronoun) if part != "decides" else ())
    lines = ["**%s** | Received: %s | **Response due: %s**" % (
        title, open_events.at_text(open_events.parse_at(record["raised"]["at"])), due), "",
        "**From:** %s" % current_job.party_name(job, record["raised"]["by"]), "",
        "**What happened:** %s" % record["summary"]["text"].rstrip(), ""]
    if record.get("facts"):
        lines += ["| Fact | Detail |", "|---|---|"]
        lines += ["| %s | %s |" % (f["label"], str(f["value"]).replace("|", "/")) for f in record["facts"]]
        lines += [""]
    lines += ["**Why it needs you:** %s" % why, ""]
    if record.get("options"):
        choices = "; ".join("%s, %s (%s)" % (o["name"], o["position"], o["basis"]) for o in record["options"])
    else:
        choices = CHOICES[part]
    lines += ["**The choices:** %s" % choices, "",
              "**Staff position:** %s" % _authored(record.get("staff_position"), NOT_SUPPLIED), ""]
    if record.get("deadline"):
        label = record["deadline"]["label"].rstrip(".")
        nothing = "%s passes at %s; no answer is never a yes or a no." % (label, _due_words(notice.due))
    else:
        nothing = "No deadline is set; no answer is never a yes or a no."
    lines += ["**If no agreement is reached:** %s" % nothing, ""]
    if answers is not None:
        lines += ["**Your answer:** %s" % _link(page_rel, answers.relative_to(root).as_posix(), heading, slug(heading)),
                  ""]
    source = _record_link(page_rel, root, record["raised"]["source"])
    lines += ["**Supporting record:** %s" % (source or "On file with %s" % current_job.party_name(
        job, record["raised"]["by"])), ""]
    result = (record.get("resolution") or {}).get("result_page")
    lines += ["**Individual event result:** %s" % (_record_link(page_rel, root, {"path": result}) if result else "Pending")]
    return lines


def fyi_lines(notice, route, page_rel, job):
    """One FOR YOUR INFORMATION notice: an event resolved since the issue before this one."""
    record = notice.record
    res = record["resolution"]
    root = Path(route.root)
    who = record["subject"] if res["by"] == open_events.OTHER_CLUB else current_job.party_name(job, res["by"])
    lines = ["**%s: %s** | %s" % (open_events.title(record), OUTCOME_WORDS[res["outcome"]],
                                  _day(open_events.parse_at(res["at"]).date())), "",
             "**Known fact:** %s Decided by %s." % (res["decision"]["text"].rstrip(), who), "",
             "**Football consequence:** %s" % _authored(record.get("consequence"), TO_COME), ""]
    page = _record_link(page_rel, root, {"path": res["result_page"]})
    lines += ["**Record:** %s" % (page or "On file")]
    return lines


def coming_up_lines(notice, route, page_rel, job):
    """One COMING UP window (runtime/deadlines.coming_up)."""
    w = notice.window
    when = open_events.at_text(open_events.parse_at(w["at"])) if w.get("at") else "Date not set"
    return ["**%s** | %s" % (w["title"], when), "",
            "**Why it matters:** %s" % w["why"], "",
            "**Current state:** %s" % w["state"], "",
            "**Action now:** %s" % w["action"]]


BUILDERS = {"action": action_lines, "fyi": fyi_lines, "coming_up": coming_up_lines}


# ------------------------------------------------------------------ results and the period's index
# What an event is called inside a sentence (the result's one line in Record.md and the index).
NOUNS = {"trade_talks": "the trade call from %s", "injury_replacement": "the roster question for %s",
         "head_coach_change": "the head-coach change at %s"}
# The sentence of a resolution, by its outcome: who decided it, or what happened to it.
OUTCOME_SENTENCE = {"executed": "{who} completed {noun}", "no_move": "{who} made no move on {noun}",
                    "accepted": "{who} accepted {noun}", "rejected": "{who} rejected {noun}",
                    "declined": "{who} declined {noun}", "withdrawn": "{Noun} was withdrawn",
                    "lapsed": "{Noun} lapsed at its due time",
                    "ended_without_agreement": "{Noun} ended without agreement"}
OTHER_BUSINESS = "## Other business this week"


def decider(record, job, party=None):
    """The name of who decided (or decides) an event: the club for a decision outside Jacksonville."""
    pid = party if party is not None else (record.get("resolution") or {}).get("by") or record["authority"]["decides"]
    return record["subject"] if pid == open_events.OTHER_CLUB else current_job.party_name(job, pid)


def noun(record):
    return NOUNS.get(record["kind"], "the matter of %s") % record["subject"]


def outcome_sentence(record, job):
    """The one sentence of a resolved event ("David Caldwell declined the trade call from the Test
    Club."), as Record.md and the period's index say it."""
    res = record["resolution"]
    thing = noun(record)
    text = OUTCOME_SENTENCE[res["outcome"]].format(who=decider(record, job), noun=thing,
                                                   Noun=thing[:1].upper() + thing[1:])
    return text[:1].upper() + text[1:] + "."


def other_business(season, period, page_rel, root, open_now=True, job=None):
    """The period index's "Other business this week" (rebuild step 5, A4), left out when empty: each
    result whose resolution's period is ``period`` (open_events.period_events), one link each, by its
    resolution time; and, while the period is the open one (``open_now``), every event still open
    that is known to Stone, with its due time. A closed period lists its results only, so its index
    never changes once the period has closed; an open period's index changes only when an event is
    raised or resolved. Only events known to Stone reach his pages."""
    root = Path(root)
    job = current_job.load(root) if job is None else job
    results, _ = open_events.period_events(season, period, root)
    results = [r for r in results if open_events.known_to_stone(r, job)]
    still = []
    if open_now:
        order = open_events.period_order(period)
        still = [r for r in open_events.load(season, root) if r.get("resolution") is None
                 and open_events.known_to_stone(r, job) and open_events.period_order(r["period"]) <= order]
        still.sort(key=lambda r: (r.get("deadline") is None, (r.get("deadline") or {}).get("at") or "", r["id"]))
    if not results and not still:
        return []
    rows = []
    for record in results:
        res = record["resolution"]
        page = _record_link(page_rel, root, {"path": res["result_page"]}, open_events.title(record))
        rows.append([page or open_events.title(record), outcome_sentence(record, job).rstrip("."),
                     "Resolved %s" % open_events.at_text(open_events.parse_at(res["at"]))])
    route = open_events.Route(season=season, period=dict(period), root=root)
    answers = responses_page(route)
    for record in still:
        label = open_events.title(record)
        heading = answer_heading(route, record["id"], None)
        if heading is not None and answers is not None and answers.is_file():
            label = _link(page_rel, answers.relative_to(root).as_posix(), label, slug(heading))
        # Its row stands from its raising to its resolution: its process and his answer are on the brief
        # and on My Responses, so a recorded entry never makes the index stale.
        due = record.get("deadline")
        rows.append([label, "Open", "Due %s" % open_events.at_text(open_events.parse_at(due["at"])) if due
                     else "No due time is set"])
    lines = [OTHER_BUSINESS, "", "| Matter | Where it stands | When |", "|---|---|---|"]
    lines += ["| %s |" % " | ".join(str(c).replace("|", "/") for c in row) for row in rows]
    return lines + [""]


def notice_lines(notice, route, page_rel, job=None):
    job = current_job.load(route.root) if job is None else job
    return _quote(BUILDERS[notice.section](notice, route, page_rel, job))


def notice_sha256(lines):
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def render(route, page_rel, issued_at):
    """The insert sections of a brief issued at ``issued_at`` (its lines, each section followed by a
    blank line), in the order ACTION REQUIRED, FOR YOUR INFORMATION, COMING UP; each section is left
    out when it is empty, and with no inserts nothing is added. ACTION REQUIRED is led by its index
    line in words, and the block that carries it ends with the one reissue rule."""
    if not route.notices():
        return []
    job = current_job.load(route.root)
    out = []
    for heading, notices in zip(HEADINGS, (route.action, route.fyi, route.coming_up)):
        if not notices:
            continue
        out += [heading, ""]
        if notices is route.action:
            n = len(notices)
            out += ["**%s %s your answer.**" % (NUMBERS.get(n, str(n)), "decision needs" if n == 1 else
                                                "decisions need"), ""]
        for notice in notices:
            out += notice_lines(notice, route, page_rel, job) + [""]
    if route.action:
        out += [ONE_RULE, ""]
    return out


def issue_inserts(route, page_rel):
    """The issue record's ``inserts``: one entry per notice the issue shows, with its section, the
    sha256 of its lines and, for an answer, the due time it showed (null: not set)."""
    if not route.notices():
        return []
    job = current_job.load(route.root)
    out = []
    for notice in route.notices():
        entry = {"item" if notice.record is None and notice.section == "action" else
                 "window" if notice.section == "coming_up" else "event": notice.key,
                 "section": notice.section, "sha256": notice_sha256(notice_lines(notice, route, page_rel, job))}
        if notice.section == "action":
            entry["due"] = open_events.iso(notice.due) if notice.due else None
        out.append(entry)
    return out


# ------------------------------------------------------------------ the brief's own sections
def strip_inserts(text):
    """A brief without its insert block (from the first insert heading to its first own section)."""
    lines = text.split("\n")
    start = next((n for n, line in enumerate(lines) if line in HEADINGS), None)
    if start is None:
        return text
    end = next((n for n in range(start, len(lines)) if lines[n].startswith("## ") and lines[n] not in HEADINGS),
               len(lines))
    return "\n".join(lines[:start] + lines[end:])


def own_sections(text):
    """A brief's own sections (1 to 8 of a Game Week Briefing, and what follows them), without its
    header and its inserts."""
    lines = strip_inserts(text).split("\n")
    start = next((n for n, line in enumerate(lines) if line.startswith("## ")), len(lines))
    return "\n".join(lines[start:])


# ------------------------------------------------------------------ the one rule
@dataclass
class PeriodState:
    """What the one rule reads of a period besides its route: its brief's own sections rebuilt now
    differ from the issue (``own_changed``), whether its own items are open (``items_open``), and
    when the next scheduled issue is (``next_issue_at``: the next period's opening, None when not
    known)."""
    season: int
    period: dict
    root: Path
    own_changed: bool = False
    items_open: bool = False
    next_issue_at: dt.datetime | None = None


def _shown(entry):
    return {(i.get("event") or i.get("item")): i for i in entry.get("inserts") or () if i.get("section") == "action"}


def reissue_reason(period, current_issue, route_now):
    """Why the period's brief must be issued again now, or None (docs/event_inserts.md A.6):

    (a) an ACTION answer the current issue does not show (a new ACTION event, or C2's game-day item);
    (b) a dated finding recorded after the issue that changes a choice still pending: an ACTION
        event's state, terms or deadline changed by a process entry (a call, terms, a counter, a
        medical entry), or the brief's own sections rebuilt now differ from the issue while the
        period's own items are open (a recorded medical entry, a transaction, a decision settled by
        someone else, a staff text); the passing of an exam's date with no recorded entry is not one;
    (c) an ACTION answer due before the next scheduled issue whose due time the current issue does
        not show.

    ``current_issue`` is the issue record's entry of the current brief (an entry written before step
    5 reads as showing no insert). A change only to FOR YOUR INFORMATION or COMING UP, and Stone's own
    answers, are never a reason."""
    if current_issue is None:
        return None
    shown = _shown(current_issue)
    new = [n for n in route_now.action if n.key not in shown]
    if new:
        return "a: %s" % "; ".join(open_events.title(n.record) if n.record else n.item["title"] for n in new)
    issues_ = open_events.Issues(period.season, period.root)
    index = issues_.index(open_events.issue_identity(period.period, current_issue))
    key = open_events.period_order(period.period) + (index,)
    for notice in route_now.action:
        was = shown[notice.key]
        due = open_events.iso(notice.due) if notice.due else None
        if was.get("due", due) != due:
            return "b: the due time of %s changed" % notice.key
        if notice.record is not None:
            for n, entry in enumerate(notice.record.get("process") or ()):
                if entry.get("kind") in open_events.CHANGES and open_events.stamp_key(notice.record, issues_, n) >= key:
                    return "b: %s recorded for %s" % (entry["kind"], notice.key)
    if period.own_changed and period.items_open:
        return "b: the briefing's own sections changed while the week's decisions are open"
    for notice in route_now.action:
        if notice.due and period.next_issue_at and notice.due < period.next_issue_at \
                and shown[notice.key].get("due") != open_events.iso(notice.due):
            return "c: %s falls due before the next scheduled briefing" % notice.key
    return None


def plan_issue_problems(wk, answered):
    """(problems, notes) of a Game Plan's "Briefing used" (scripts/check_game_plan.briefing_problems
    calls this; ``answered`` is {date, revision}): none when it names the current issue, or an earlier
    one whose own sections equal the current issue's (the reissue only added or changed inserts),
    which gives a note that his answers stand; otherwise the plan check's message, so a reissue whose
    own sections changed still needs "Briefing used" updated."""
    from scripts import render_game_week as rgw
    from .game_plan import issue_label
    current = rgw.current_issue(wk)
    if current is None or answered is None:
        return [], []
    mine = (answered["date"], answered["revision"])
    if mine == current:
        return [], []
    entries = rgw.issues(wk)
    earlier = next((e for e in entries if rgw.issue_of(e) == mine), None)
    if earlier is not None and wk.pages.briefing.is_file():
        try:
            then = (wk.pages.folder / earlier["file"]).read_text(encoding="utf-8")
            now = wk.pages.briefing.read_text(encoding="utf-8")
        except OSError:
            then = now = None
        if then is not None and own_sections(then) == own_sections(now):
            return [], [NOTE[:1].upper() + NOTE[1:]]
    return ["Briefing used: your page answers the briefing of %s; the current briefing is %s; read it and write it "
            "as its status line names it (your answers may stand)" % (issue_label(*mine), issue_label(*current))], []
