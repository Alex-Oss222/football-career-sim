#!/usr/bin/env python3
"""Resolve an event inside a week or phase and write its one result page (rebuild step 5, A4;
docs/event_inserts.md, section A.5 and the per-event result contract;
foundation/templates/event_inserts/event_result_template.md).

  python scripts/resolve_event.py ID --season YEAR --outcome OUTCOME --by PARTY --at DATETIME
         --decision TEXT [--criteria N] [--result PAGE] [--closure] [--check]
  python scripts/resolve_event.py --season YEAR --check

One resolved event, one dated result page, in the event's owner folder (runtime/decisions.event_folder),
named by runtime/decisions.result_file (Trade_Result_2014-10-14_Tennessee_Titans.md; a second result
of the same kind, date and subject takes _2, then _3), written when the event resolves, not at the
weekly close. The page carries the template's fields, every one from the event's record: when it
was raised and resolved, who it involves, what happened (the summary of whoever brought it and its
dated process), Stone's answer as he gave it on My Responses (or that none was required, or that
none was given before the question ended), the decision of the party with the authority and the
criteria it applies, the outcome, the changes (none, for every outcome this script writes), and the
source pages. It carries one event-record line with the event's id, so the year's Record.md lists
it; ``--closure`` gives that line its closure, so the runner's mid-week record moves Document 5's
checkpoint to it. The store then records the resolution, and Record.md and the open period's index
(its "Other business this week") are rebuilt at once.

OUTCOME is one of executed, no_move, accepted, rejected, declined, withdrawn, lapsed and
ended_without_agreement; PARTY a party of the job record, or other_club for the other club's own act;
DATETIME an ISO time with its ET offset (2014-10-14T15:00:00-04:00); N the index of the deciding
party's criteria entry in the event's process (by default its latest criteria entry). An outcome
that changes the roster, a contract or a staff (executed, accepted) and a news event's result are the
page of the builder that makes that change (a Transaction page, a head-coach change page), adopted
with ``--result PAGE``, which must carry the event's event-record line; every other outcome's page is
built here, from the record, and takes no ``--result``.

Refused, with nothing written: an unknown or resolved event; a time after the master date/time; a
game paused; ``executed`` or ``accepted`` on a trade call ("Executing a trade is not built yet; the
agreed terms stay on the event and the decision is put to the user"); a decision by a party other
than Stone without its criteria entry recorded before his response; a decision text that is not in
football words; ``lapsed`` without his explicit permission on his page; and anything while the
event's resolution is held by an open item. Two acts of others end his own item instead, and this
script records them: the other side ending the question (a sourced process entry of the event, of
the kind withdrawn by the other side, the other side's deadline passed or a medical entry: his item
is withdrawn by the organization, or by the medical staff for a medical entry, and the event resolves
withdrawn, ended without agreement or no move), and an injury replacement whose due time passed
with his recommendation unanswered (the general manager decides; his item is withdrawn by the
organization, "decided at the due time with no recommendation on file", and the page says no
recommendation was given). Silence is never yes or no: nothing here resolves an event on its own.

``--check`` with an ID makes every check of that resolution and writes nothing. ``--check`` alone
holds every result page this script built to its event's record (it writes nothing and exits 1 on
a stale or missing page).
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import current_job, decision_queue, decisions, event_inserts, open_events  # noqa: E402
from runtime.clean_pages import text_errors  # noqa: E402
from runtime.events import EVENT_META, load_events, render_record, annual_record_path, closures  # noqa: E402

# The outcomes whose page is the page of the change itself, adopted with --result.
ADOPTED = frozenset({"executed", "accepted"})
# The outcomes a trade call cannot reach in step 5 (docs/rebuild_plan.md step 5, "Not built").
TRADE_NOT_BUILT = ("Executing a trade is not built yet; the agreed terms stay on the event and the decision is put "
                   "to the user")
NO_CHANGE = "No contract, roster, staff or employment change."
# Stone's answer, by what it committed to (runtime/responses.compile_substance).
ANSWER_WORDS = {"support": "Supported it", "oppose": "Opposed it", "lapse": "Let it lapse at its due time"}
# His part, as the page names him among those involved.
PART_WORDS = {"recommends": "who recommends", "consulted": "who is consulted", "decides": "who decides"}


class Refused(ValueError):
    """A resolution this script refuses, in words for the runner (nothing was written)."""


# ------------------------------------------------------------------ words and links
def long_at(at):
    """"Tuesday, October 14, 2014, 3 p.m. ET"."""
    text = open_events.at_text(at)              # "Tuesday, October 14, 3 p.m. ET"
    head, clock = text.rsplit(", ", 1)
    return "%s, %d, %s" % (head, at.year, clock)


def _link(page_rel, target_rel, label, anchor=""):
    path = os.path.relpath(target_rel, os.path.dirname(page_rel)).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, path.replace(" ", "%20"), "#" + anchor if anchor else "")


def _page(record):
    """A {path, anchor?} source that is a football page (career/, .md), or None (a data file is never
    linked)."""
    if isinstance(record, dict) and str(record.get("path", "")).startswith("career/") and \
            str(record["path"]).endswith(".md"):
        return record
    return None


def _heading(root, path):
    try:
        for line in (Path(root) / path).read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return "The record"


def built_here(record):
    """Whether the event's result page is built by this script from its record: every outcome but
    the adopted ones (``ADOPTED``) of an event that is not news."""
    res = record.get("resolution") or {}
    return record["kind"] not in decisions.NEWS_KIND and res.get("outcome") not in ADOPTED


# ------------------------------------------------------------------ the page
def answer_text(record, page_rel, job):
    """The page's "Stone's answer" line, from the event's record only."""
    part = record["stone_part"]
    holder = job.get("holder", "stone")
    if isinstance(part, str) and part.startswith("standing:"):
        rule = next((i for i in current_job.instructions(job, None) if i.get("id") == part[len("standing:"):]), None)
        text = "Answered by his standing instruction"
        if rule and rule.get("summary"):
            text += ": " + str(rule["summary"]).rstrip(".")
        link = _page((rule or {}).get("record"))
        return text + (" (%s)." % _link(page_rel, link["path"], "the instruction", link.get("anchor") or "")
                       if link else ".")
    if part == "none" or holder not in (record.get("known_to") or ()):
        return "No response required."
    response = record.get("response")
    if response is not None:
        substance = response["substance"]
        kind = substance["kind"]
        if kind == "recommend":
            words = "Recommended %s" % substance.get("option")
        elif kind == "condition":
            words = "Supported it on a condition: %s" % str(substance.get("condition", "")).rstrip(".")
        else:
            words = ANSWER_WORDS[kind]
        when = dt.date.fromisoformat(response["date"])
        anchor = event_inserts.slug(response["heading"])
        return "%s (answered %s %d on %s)." % (words, when.strftime("%B"), when.day,
                                              _link(page_rel, response["page"], "My Responses", anchor))
    res = record["resolution"]
    ended = [e for e in record["process"] if e.get("kind") in open_events.OTHER_SIDE_ENDINGS]
    if ended and res["outcome"] in open_events.ENDED:
        return "No answer was given; the question ended before he answered."
    if record["kind"] == "injury_replacement":
        return "No recommendation was given; the general manager decided at the due time with none on file."
    return "No answer was given."


def page_text(record, root, job=None):
    """The result page of a resolved event, from its record (the template's fields and its one
    event-record line). ``record`` holds its resolution (at, outcome, by, decision, result_page)."""
    root = Path(root)
    job = current_job.load(root) if job is None else job
    kind = decisions.event_kind(record["kind"])
    res = record["resolution"]
    page_rel = res["result_page"]
    raised = open_events.parse_at(record["raised"]["at"])
    at = open_events.parse_at(res["at"])
    who = event_inserts.decider(record, job)
    holder = job.get("holder", "stone")
    involving = [record["subject"]]
    deciding = record["authority"]["decides"]
    if deciding != open_events.OTHER_CLUB:
        involving.append("%s, who decides" % current_job.party_name(job, deciding))
    part = record["stone_part"]
    if holder in (record.get("known_to") or ()) and part in PART_WORDS and deciding != holder:
        involving.append("%s, %s" % (current_job.party_name(job, holder), PART_WORDS[part]))
    out = ["# %s: %s" % (kind.result, record["subject"]), "",
           "**Event date:** %s" % long_at(raised), "",
           "**Resolved on:** %s" % long_at(at), "",
           "**Involving:** %s." % "; ".join(involving), "",
           "**What happened:** %s" % record["summary"]["text"].rstrip(), ""]
    steps = [e for e in record["process"] if e.get("kind") != "response"]
    if steps:
        out += ["| When | What | From |", "|---|---|---|"]
        for entry in steps:
            out.append("| %s | %s | %s |" % (open_events.at_text(open_events.parse_at(entry["at"])),
                                             str(entry["what"]).rstrip().replace("|", "/"),
                                             event_inserts.decider(record, job, entry["by"])))
        out += [""]
    out += ["**Stone's answer:** %s" % answer_text(record, page_rel, job), ""]
    decision = res["decision"]
    lead = "%s, who decides" % who if res["by"] == deciding and res["by"] != open_events.OTHER_CLUB else who
    final = "%s: %s" % (lead, decision["text"].rstrip())
    if not final.endswith("."):
        final += "."
    criteria = decision.get("criteria")
    if type(criteria) is int and 0 <= criteria < len(record["process"]):
        entry = record["process"][criteria]
        final += " The decision applies the criteria %s recorded on %s." % (
            event_inserts.decider(record, job, entry["by"]), open_events.at_text(open_events.parse_at(entry["at"])))
    out += ["**Final decision:** %s" % final, "",
            "**Outcome:** %s." % event_inserts.OUTCOME_WORDS[res["outcome"]].capitalize(), "",
            "**Changes effective:** %s" % NO_CHANGE, "",
            "**Outstanding issue:** None.", ""]
    sources, seen = [], set()
    wanted = [record["raised"]["source"]] + [e.get("source") for e in record["process"]]
    if record.get("response"):
        wanted.append({"path": record["response"]["page"], "anchor": event_inserts.slug(record["response"]["heading"])})
    for source in wanted:
        page = _page(source)
        if page is None or page["path"] == page_rel:
            continue
        key = (page["path"], page.get("anchor") or "")
        if key in seen:
            continue
        seen.add(key)
        label = "My Responses" if Path(page["path"]).name == decisions.file_name(decisions.RESPONSES) \
            else _heading(root, page["path"])
        sources.append(_link(page_rel, page["path"], label, page.get("anchor") or ""))
    out += ["**Source records:** %s" % ("; ".join(sources) + "." if sources else
                                        "On file with %s." % current_job.party_name(job, record["raised"]["by"])), ""]
    out += [event_line(record, job)]
    return "\n".join(out) + "\n"


def summary_line(record, job):
    """The result's one line in Record.md."""
    return event_inserts.outcome_sentence(record, job)


def event_line(record, job, closure=None):
    """The page's event-record line: the event's id, the resolution date, its summary and, with
    ``closure``, its closure ({checkpoint, through, sequence})."""
    res = record["resolution"]
    day = open_events.parse_at(res["at"]).date().isoformat()
    data = {"id": record["id"], "date": day, "summary": summary_line(record, job), "status": "closed",
            "season": record["season"]}
    closure = closure if closure is not None else record.get("_closure")
    if closure is not None:
        data["closure"] = closure
    return "<!-- event-record: %s -->" % json.dumps(data, ensure_ascii=False)


def _closure_of(page_text_):
    """The closure on a page's event-record line, or None."""
    found = EVENT_META.findall(page_text_)
    return json.loads(found[0]).get("closure") if found else None


def next_closure(record, job, root):
    """The closure a mid-week record gives the result's event line: the next sequence after every
    closed event, through the resolution date, its checkpoint named for the result."""
    sequences = [item["sequence"] for _, _, item in closures(load_events(root))]
    on = open_events.parse_at(record["resolution"]["at"]).date()
    return {"checkpoint": "Canonical update - %s %d, %d - %s" % (
                on.strftime("%B"), on.day, on.year, summary_line(record, job).rstrip(".")),
            "through": on.isoformat(), "sequence": max(sequences, default=0) + 1}


# ------------------------------------------------------------------ the resolution
@dataclass
class Plan:
    """A resolution ready to write: the record as it will stand (resolution without its stamps), the
    queue with Stone's item withdrawn when another side ended the question, the page to write (None
    when adopted) and its path."""
    record: dict
    resolution: dict
    queue: dict
    page: Path
    text: str | None
    withdrawn: str | None = None
    notes: list = field(default_factory=list)


def _item_withdrawal(record, outcome, by, at, item, root):
    """The resolution of Stone's open item when another side ended the question or an injury
    replacement's due time passed unanswered; None when neither holds."""
    root = Path(root).resolve()
    own = open_events.path_of(record, root).relative_to(root).as_posix()
    endings = [(n, e) for n, e in enumerate(record["process"])
               if e.get("kind") in open_events.OTHER_SIDE_ENDINGS and e.get("source")]
    if endings and outcome in open_events.ENDED:
        n, entry = endings[-1]
        return {"date": at.date().isoformat(), "by": "medical" if entry["kind"] == "medical" else "organization",
                "record": {"path": own, "pointer": "/process/%d" % n},
                "summary": "%s: %s" % (open_events.OTHER_SIDE_SUMMARY, str(entry["what"]).rstrip())}
    deadline = record.get("deadline")
    if (record["kind"] == "injury_replacement" and by == record["authority"]["decides"] and deadline
            and record.get("response") is None and item.get("class") == "personnel_recommendation"
            and at >= open_events.parse_at(deadline["at"]) and outcome in open_events.DECIDED):
        return {"date": at.date().isoformat(), "by": "organization", "record": {"path": own},
                "summary": open_events.DUE_TIME_SUMMARY}
    return None


def prepare(root, season, event_id, outcome, by, at, decision, criteria=None, result=None, closure=False):
    """Every check of a resolution, with nothing written: the Plan, or Refused."""
    root = Path(root).resolve()
    try:
        open_events._refuse_if_paused(root)
    except open_events.Refused as exc:
        raise Refused(str(exc))
    record = open_events.get(season, event_id, root)
    if record is None:
        raise Refused("no event %s is recorded in %d" % (event_id, season))
    if record["state"] == "resolved":
        raise Refused("event %s is already resolved; its result stands" % event_id)
    if outcome not in open_events.OUTCOMES:
        raise Refused("the outcome is one of %s" % ", ".join(open_events.OUTCOMES))
    if record["kind"] == "trade_talks" and outcome in ADOPTED:
        raise Refused(TRADE_NOT_BUILT)
    job = current_job.load(root)
    news = record["kind"] in decisions.NEWS_KIND
    if by != open_events.OTHER_CLUB and by not in (job.get("parties") or {}):
        raise Refused("%s is not a party of the job record (or other_club for the other club's own act)" % by)
    try:
        when = open_events.parse_at(at) if isinstance(at, str) else at
    except ValueError as exc:
        raise Refused("the time: %s" % exc)
    clock = open_events.master_clock(root)
    if not clock.allows(when):
        raise Refused("the resolution is at %s, after the master date/time; record the mid-week clock first"
                      % long_at(when))
    if when < open_events.parse_at(record["raised"]["at"]):
        raise Refused("the resolution is before the event was raised")
    text = str(decision or "").strip()
    if not text or "\n" in text:
        raise Refused("the decision is one line in football words")
    folder = decisions.event_folder(record["kind"], season, root)
    rel = (folder / "README.md").relative_to(root).as_posix()
    unclean = [e.split(": ", 1)[-1] for e in text_errors(rel, text, root)]
    if unclean:
        raise Refused("the decision is not in football words: %s" % "; ".join(unclean))
    if outcome == "lapsed" and ((record.get("response") or {}).get("substance") or {}).get("kind") != "lapse":
        raise Refused("an event lapses only with Stone's explicit permission to let it lapse on his page; no answer is "
                      "never a yes or a no")
    holder = job.get("holder")
    # The criteria: the deciding party's entry, recorded before Stone's response.
    if criteria is None and by not in (holder, open_events.OTHER_CLUB) and not news:
        found = [n for n, e in enumerate(record["process"]) if e.get("kind") == "criteria" and e.get("by") == by]
        criteria = found[-1] if found else None
    if criteria is not None and (type(criteria) is not int or not 0 <= criteria < len(record["process"])
                                 or record["process"][criteria].get("kind") != "criteria"):
        raise Refused("the criteria are the index of a criteria entry in the event's process")
    if criteria is None and by not in (holder, open_events.OTHER_CLUB) and not news and outcome in open_events.DECIDED:
        raise Refused("%s decides only from criteria recorded before Stone's answer: record the criteria entry (the "
                      "need, the legal options on the date, the cap and contract facts and the other side's terms, "
                      "each with its source) first (Document 1 sections 9.1 and 9.4)" % current_job.party_name(job, by))
    responses = [n for n, e in enumerate(record["process"]) if e.get("kind") == "response"]
    if criteria is not None and responses and criteria > responses[0]:
        raise Refused("the criteria were recorded after Stone's answer; criteria come before the case")
    # The result page: adopted, or built here.
    adopted = news or outcome in ADOPTED
    resolution = {"at": open_events.iso(when), "outcome": outcome, "by": by,
                  "decision": {"text": text, "author": event_inserts.decider(record, job, by),
                               "date": when.date().isoformat(), "criteria": criteria}}
    if adopted:
        if result is None:
            raise Refused("an outcome that makes a change (%s) and a news event's result are the page of the change "
                          "itself: pass it with --result" % ", ".join(sorted(ADOPTED)))
        page = (root / result).resolve()
        if not page.is_file():
            raise Refused("the result page %s is missing" % result)
        if page.parent != folder.resolve():
            raise Refused("the result page is not in the event's owner folder (%s)" % folder.relative_to(root).as_posix())
        ids = [json.loads(m).get("id") for m in EVENT_META.findall(page.read_text(encoding="utf-8"))]
        if ids != [event_id]:
            raise Refused("the result page must carry exactly one event-record line, with the event's id")
        if closure:
            raise Refused("an adopted page's event line is its own builder's; it takes no --closure here")
        page_text_ = None
    else:
        if result is not None:
            raise Refused("this outcome's result is built here from the event's record; it takes no --result")
        page = decisions.result_file(record["kind"], when.date(), record["subject"], root, season=season)
    resolution["result_page"] = page.relative_to(root).as_posix()
    shown = dict(record, resolution=resolution, state="resolved")
    # Who still holds the event's resolution: Stone's item ends here only by another side's act.
    queue = decision_queue.load(root)
    ev = decision_queue.event("event_resolution", season, event=event_id)
    withdrawn = None
    for item in queue["items"]:
        if not decision_queue.holds(item, ev):
            continue
        ending = None
        if item.get("owner") == holder and item.get("id") == record.get("queue_item"):
            ending = _item_withdrawal(record, outcome, by, when, item, root)
        if ending is None:
            raise Refused("the event waits on %s (%s, %s); it resolves once that is settled" % (
                item.get("title"), current_job.party_name(job, item.get("owner")),
                "due %s" % long_at(open_events.parse_at(item["deadline"]["at"]))
                if (item.get("deadline") or {}).get("at") else "no due time set"))
        item["status"], item["resolution"], withdrawn = "WITHDRAWN", ending, item["id"]
    if adopted:
        plan = Plan(record, resolution, queue, page, None, withdrawn)
    else:
        if closure:
            shown["_closure"] = next_closure(shown, job, root)
        body = page_text(shown, root, job)
        shown.pop("_closure", None)
        unclean = text_errors(resolution["result_page"], body, root)
        if unclean:
            raise Refused("the result page would not be in football words: %s" % "; ".join(unclean))
        plan = Plan(record, resolution, queue, page, body, withdrawn)
    # The record as it will stand, against the store's rules (its page, written later, aside).
    errors = open_events.record_errors(dict(shown, resolution=dict(resolution, after_issue=None,
                                                                    period=record["period"])),
                                       root, job=job, queue=queue)
    errors = [e for e in errors if "result page" not in e and "event-record line" not in e]
    if errors:
        raise Refused("; ".join(errors))
    return plan


def _snapshot(paths):
    return {p: (p.read_bytes() if p.is_file() else None) for p in paths}


def _restore(saved):
    for path, data in saved.items():
        if data is None:
            if path.is_file():
                path.unlink()
        else:
            path.write_bytes(data)


def resolve(root, season, event_id, outcome, by, at, decision, criteria=None, result=None, closure=False):
    """Resolve the event: its result page written (or adopted), Stone's item withdrawn when another
    side ended the question, the resolution recorded (stamped with the open period and its latest
    issue), Record.md and the open period's index rebuilt. All or nothing. Returns the paths written."""
    root = Path(root).resolve()
    plan = prepare(root, season, event_id, outcome, by, at, decision, criteria, result, closure)
    record_path = open_events.path_of(plan.record, root)
    annual = annual_record_path(root, season)
    touched = [record_path, root / decision_queue.QUEUE, annual, plan.page]
    from scripts import render_game_week
    index = None
    try:
        wk = render_game_week.Week(root)
        if wk.game is not None:
            index = wk.pages.readme
            touched.append(index)
    except (OSError, ValueError, KeyError):
        wk = None
    saved = _snapshot(touched)
    written = []
    try:
        if plan.text is not None:
            plan.page.parent.mkdir(parents=True, exist_ok=True)
            plan.page.write_text(plan.text, encoding="utf-8")
            written.append(plan.page)
        if plan.withdrawn is not None:
            written.append(decision_queue.save(root, plan.queue))
        written.append(open_events.resolve(season, event_id, {k: plan.resolution[k] for k in (
            "at", "outcome", "by", "decision", "result_page")}, root))
        written += rebuild(root, season)
    except Exception as exc:  # noqa: BLE001  (every failure restores what was there)
        _restore(saved)
        raise Refused(str(exc)) from exc
    return written


def rebuild(root, season):
    """Record.md and the open period's index, rebuilt from the records (the bye's index by its own
    builder when the bye is the open period)."""
    from scripts import render_annual_record, render_game_week
    root = Path(root).resolve()
    written = []
    path = annual_record_path(root, season)
    expected = render_record(season, load_events(root), root)
    unclean = render_annual_record.problems(root, season, expected)
    if unclean:
        raise Refused("Record.md would not be in football words: %s" % "; ".join(unclean))
    if not path.is_file() or path.read_text(encoding="utf-8") != expected:
        path.write_text(expected, encoding="utf-8")
        written.append(path)
    wk = render_game_week.Week(root)
    if wk.game is not None:
        written += render_game_week.write_index(root)
    elif (wk.period or {}).get("bye"):
        written += bye_index(root)
    return written


def bye_index(root):
    """STUB until builder C3's bye pages land: the bye's index rebuilt by its own builder
    (scripts/render_bye_week.write_index(root)), which lists the bye's results through
    event_inserts.other_business; without it nothing is written."""
    try:
        from scripts import render_bye_week
    except ImportError:
        return []
    writer = getattr(render_bye_week, "write_index", None)
    return list(writer(root) or ()) if writer is not None else []


# ------------------------------------------------------------------ the built pages' check
def built_pages(root, season):
    """(path, text) of every result page this script builds, each from its event's record and the
    closure its event line carries (scripts/rebuild_pages.py writes those that differ)."""
    root = Path(root).resolve()
    job = current_job.load(root)
    out = []
    for record in open_events.load(season, root):
        res = record.get("resolution")
        if res is None or not built_here(record):
            continue
        page = root / res["result_page"]
        closure = _closure_of(page.read_text(encoding="utf-8")) if page.is_file() else None
        out.append((page, page_text(dict(record, _closure=closure), root, job)))
    return out


def check(root, season):
    """Every result page this script built, against its event's record (none written)."""
    root = Path(root).resolve()
    errors = []
    for page, text in built_pages(root, season):
        rel = page.relative_to(root).as_posix()
        if not page.is_file():
            errors.append("Result page missing: %s" % rel)
        elif page.read_text(encoding="utf-8") != text:
            errors.append("Result page %s differs from its event's record; a result page is rebuilt from the event, "
                          "never edited by hand (python scripts/rebuild_pages.py --season %d)" % (rel, season))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("event", nargs="?")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--outcome")
    parser.add_argument("--by")
    parser.add_argument("--at")
    parser.add_argument("--decision")
    parser.add_argument("--criteria", type=int)
    parser.add_argument("--result")
    parser.add_argument("--closure", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.event is None:
        if not args.check:
            parser.error("name the event to resolve, or pass --check alone to check the result pages")
        try:
            errors = check(root, args.season)
        except (OSError, ValueError, KeyError) as exc:
            errors = ["Result pages cannot be checked: %s" % exc]
        print("\n".join(errors) if errors else "RESULT PAGES CURRENT")
        return 1 if errors else 0
    missing = [name for name in ("outcome", "by", "at", "decision") if getattr(args, name) is None]
    if missing:
        parser.error("a resolution needs --%s" % ", --".join(missing))
    call = (root, args.season, args.event, args.outcome, args.by, args.at, args.decision, args.criteria,
            args.result, args.closure)
    try:
        if args.check:
            plan = prepare(*call)
            print("RESULT READY: %s" % plan.page.relative_to(root).as_posix())
            return 0
        written = resolve(*call)
    except (Refused, open_events.Refused, ValueError, KeyError) as exc:
        print("EVENT NOT RESOLVED: %s" % exc)
        return 1
    for path in written:
        print("wrote %s" % Path(path).resolve().relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
