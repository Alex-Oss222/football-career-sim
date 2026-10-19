"""The current-job record: who employs the coach, in what role, with what
authority, and who calls each phase (state/current_job.json).

The record owns these facts; Document 5, the staff page and the desk
render from it (docs/career_layer.md). The appointment's contract and term
are not stored here: ``contract_record`` names the coach's permanent record
and the contract in it (runtime/coaches.py), and ``contract_terms`` and
``term`` read them there. Document 3 section 5 keeps the row
taxonomy and points here for the values; ``f3_parity_errors`` keeps the rows
on that taxonomy, accepts only the exact pointer forms and compares any
Document 3 cell written back in value form.
Nothing that resolves a game reads this module.
"""
from datetime import date
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
JOB = Path("state/current_job.json")
F3 = Path("foundation/03_Head_Coach_Organization_and_Authority_Canon.md")
STATUSES = ("EMPLOYED", "BETWEEN_JOBS")
ROLES = ("head_coach", "interim_head_coach", "coordinator", "position_coach", "assistant")
STONE_ACTIONS = ("decides", "decides_part", "recommends", "consulted", "responds", "informs",
                 "none", "unset", "not_applicable")
AUTHORITY_ROWS = ("1", "2", "3", "3a") + tuple(str(n) for n in range(4, 23))
PHASES = ("offense", "defense", "special_teams")
INSTRUCTION_STATUSES = ("IN_FORCE", "RECORDED", "SUPERSEDED", "WITHDRAWN")
DESK_FOR_ROLE = {"head_coach": "head_coach", "interim_head_coach": "head_coach",
                 "coordinator": "coordinator", "position_coach": "position_coach",
                 "assistant": "position_coach"}           # BETWEEN_JOBS -> "between_jobs"
BUILT_DESKS = frozenset({"head_coach"})
ROLE_SECTIONS = {   # the desk's sections for each role; only BUILT_DESKS render
    "head_coach": ("Team", "Staff", "Weekly plan", "Personnel partnership", "Ownership", "Career"),
    "coordinator": ("Unit", "Staff", "Installation", "Opponent", "Personnel recommendations", "Career"),
    "position_coach": ("My room", "Teaching", "Weekly assignment", "Evaluations", "Career"),
    "between_jobs": ("Career", "Vacancies", "Contacts", "Offers")}
MECHANISMS = ("live", "sheet_rule", "not_live", "not_modelled")
# The subjects a standing instruction or a decision-queue item may name: the
# calling arrangement, the inactives and each retained game decision by its
# delegation.game_management id, so the vocabularies cannot drift apart.
SUBJECTS = ("play_calling", "inactives", "fourth_down", "two_point", "kickoff", "timeouts_and_clock",
            "replay_challenge")
REQUEST_STATUSES = ("OPEN", "MET", "WITHDRAWN")
RECORD_KEYS = frozenset({"path", "anchor", "pointer"})
# Keys holding ISO dates. A past-only key may never pass the master date; a
# scheduled key may, when its entry was instructed (or given) by then.
PAST_KEYS = ("date", "instructed", "in_world")
SCHEDULED_KEYS = ("from", "to", "effective", "start", "end")
DATE_KEYS = PAST_KEYS + SCHEDULED_KEYS + ("end_date", "user_date")
DELEGATED = re.compile(r"^delegation\.play_calling\.([a-z_]+)$")
PARITY = "Document 3 and the job record disagree; correct the record that is wrong (Document 3 §11.2), then rerun."
# The only pointer forms Document 3 may use: a section 5 row is exactly
# | N | domain | ROW_POINTER % N |, and a section 3.1 cell is exactly
# CONTRACT_POINTER % the current appointment's id.
ROW_POINTER = "[job record](../state/current_job.json) row %s"
CONTRACT_POINTER = "[Current job record](../state/current_job.json), appointment `%s`"


def load(root):
    path = Path(root) / JOB
    try:
        job = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("%s unreadable: %s" % (JOB.as_posix(), exc)) from None
    if not isinstance(job, dict) or job.get("schema_version") != 1:
        raise ValueError("%s must be an object with schema_version 1" % JOB.as_posix())
    return job


def appointment(job):
    """The current appointment, None when the holder is between jobs."""
    if job.get("status") == "BETWEEN_JOBS":
        return None
    return next((a for a in job.get("appointments") or () if a.get("id") == job.get("current_appointment")), None)


def contract_terms(job, root, on=None):
    """The current appointment's contract as it stands on day ``on`` (runtime/coaches.contract:
    only the amendments in force on it; None: all of them), read from the coach record its
    ``contract_record`` names; None between jobs or without a pointer."""
    from . import coaches
    pointer = (appointment(job) or {}).get("contract_record")
    if not pointer:
        return None
    return coaches.contract(coaches.load(pointer["coach"], root), pointer["contract"], on)


def term(job, root, on=None):
    """The current appointment's term from its contract on day ``on``: ``end_date`` (the
    earliest day it can end), ``end_text`` (the whole end rule), ``seasons`` and the
    ``contract`` itself."""
    from . import coaches
    terms = contract_terms(job, root, on)
    if terms is None:
        return {"end_date": None, "end_text": None, "seasons": [], "contract": None}
    end = terms.get("end") or {}
    return {"end_date": coaches.end_date(terms), "end_text": end.get("text"),
            "seasons": list(terms.get("seasons") or ()), "contract": terms}


def party_name(job, pid):
    party = (job.get("parties") or {}).get(pid)
    return party["name"] if isinstance(party, dict) and party.get("name") else str(pid)


def _day(value, low):
    return (date.min if low else date.max) if value is None else date.fromisoformat(value)


def _intervals(job, phase):
    current = appointment(job) or {}
    rows = [r for r in (current.get("delegation") or {}).get("play_calling") or () if r.get("phase") == phase]
    return sorted(rows, key=lambda r: _day(r.get("from"), True))


def interval_on(job, phase, on):
    """The phase's delegation interval holding ``on`` (from <= on < to; a
    null from or to is open), or None."""
    return next((r for r in _intervals(job, phase)
                 if _day(r.get("from"), True) <= on < _day(r.get("to"), False)), None)


def caller_on(job, phase, on):
    interval = interval_on(job, phase, on)
    return interval["caller"] if interval else None


def desk_profile(job):
    if job.get("status") == "BETWEEN_JOBS":
        return "between_jobs"
    current = appointment(job)
    if current is None or current.get("role") not in DESK_FOR_ROLE:
        raise ValueError("no current appointment with a known role")
    return DESK_FOR_ROLE[current["role"]]


def instructions(job, status="IN_FORCE"):
    """The current appointment's standing instructions with ``status`` (all
    of them when status is None). Only IN_FORCE ones answer a pause or close
    a queue item."""
    current = appointment(job) or {}
    return [i for i in current.get("standing_instructions") or ()
            if status is None or i.get("status") == status]


def _walk(node, where=""):
    """Every dict in a JSON tree, with a readable location."""
    if isinstance(node, dict):
        yield where, node
        for key, value in node.items():
            yield from _walk(value, "%s.%s" % (where, key) if where else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk(value, "%s[%d]" % (where, i))


def _validate_repository():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scripts import validate_repository
    return validate_repository


def pointed(root, mapping, record):
    """The JSON value a record's ``pointer`` names (RFC 6901)."""
    from .events import resolve_path
    value = json.loads(resolve_path(root, record["path"], mapping).read_text(encoding="utf-8"))
    for token in record["pointer"].split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def record_error(root, mapping, record):
    """Why a {path, anchor?, pointer?} record does not resolve, or None."""
    from .events import resolve_path
    if not isinstance(record, dict) or not isinstance(record.get("path"), str) or not set(record) <= RECORD_KEYS:
        return "malformed record %r" % (record,)
    try:
        target = resolve_path(root, record["path"], mapping)
    except ValueError as exc:
        return str(exc)
    if not target.is_file():
        return "missing record %s" % record["path"]
    if record.get("anchor") is not None:
        repo = _validate_repository()
        if target.suffix != ".md" or record["anchor"] not in repo.anchors(repo.without_code(target.read_text())):
            return "missing heading %s#%s" % (record["path"], record["anchor"])
    if record.get("pointer") is not None:
        if target.suffix != ".json" or not str(record["pointer"]).startswith("/"):
            return "invalid JSON pointer %s %s" % (record["path"], record["pointer"])
        try:
            pointed(root, mapping, record)
        except (ValueError, KeyError, IndexError, TypeError):
            return "unresolved JSON pointer %s %s" % (record["path"], record["pointer"])
    return None


def _rows(text, start, stop):
    """The cells of each pipe-table row between two headings, in order."""
    if start not in text:
        raise ValueError("Document 3 has no heading %r" % start)
    section = text.split(start, 1)[1].split(stop, 1)[0]
    return [[c.strip() for c in line.strip()[1:-1].split("|")]
            for line in section.splitlines() if line.startswith("| ")]


def _table(text, start, stop):
    """{first cell: cells} for the pipe-table rows between two headings."""
    rows = {}
    for cells in _rows(text, start, stop):
        rows.setdefault(cells[0], cells)
    return rows


def _cell(cells, n):
    """Column n (1-based), None where the Document 3 row has fewer cells."""
    return cells[n - 1] if len(cells) >= n else None


def f3_parity_errors(job, root):
    """The authority rows and the employment facts against Document 3. Each
    Document 3 cell is either the exact pointer to the job record or the
    record's own value, compared in full; a Document 3 row with no job row,
    and a repeated row number, fail."""
    current = appointment(job)
    if current is None:
        return []
    prefix = "Current job: "
    try:
        text = (Path(root) / F3).read_text(encoding="utf-8")
        listed = [cells for cells in _rows(text, "## 5. Authority map", "### 5.1")
                  if re.fullmatch(r"\d+[a-z]?", cells[0])]
        contract = _table(text, "### 3.1 Head-coach contract", "### 3.2")
    except (OSError, ValueError) as exc:
        return [prefix + "cannot read Document 3: %s" % exc]
    errors = []
    domains = (current.get("authority") or {}).get("domains") or ()
    known = {row.get("row") for row in domains}
    numbers = [cells[0] for cells in listed]
    for number in sorted(set(numbers), key=numbers.index):
        if numbers.count(number) > 1:
            errors.append(prefix + "Document 3 section 5 lists row %s more than once. %s" % (number, PARITY))
        if number not in known:
            errors.append(prefix + "Document 3 section 5 row %s has no job-record row. %s" % (number, PARITY))
    authority = {}
    for cells in listed:
        authority.setdefault(cells[0], cells)
    parties = job.get("parties") or {}
    for row in domains:
        number = row.get("row")
        cells = authority.get(number)
        where = prefix + "authority row %s: " % number
        if cells is None:
            errors.append(where + "Document 3 section 5 has no such row. " + PARITY)
            continue
        if _cell(cells, 2) != row.get("domain"):
            errors.append(where + "the decision domain differs. " + PARITY)
        pointer = ROW_POINTER % number
        if cells[2:] == [pointer]:
            continue
        if any("current_job.json" in c for c in cells):
            errors.append(where + "a Document 3 pointer row is exactly | %s | <domain> | %s |, with no other cell. %s"
                          % (number, pointer, PARITY))
            continue
        if len(cells) != 7:
            errors.append(where + "a Document 3 value-form row has 7 cells, not %d. %s" % (len(cells), PARITY))
        final = _cell(cells, 3) or ""
        for pid in row.get("final") or ():
            party = parties.get(pid) or {}
            names = [party.get("name") or pid] + list(party.get("aliases") or ())
            if not any(n.lower() in final.lower() for n in names):
                errors.append(where + "Document 3 does not name %s as final authority. %s"
                              % (party_name(job, pid), PARITY))
        if not row.get("final") and "NOT APPLICABLE" not in final:
            errors.append(where + "Document 3 does not mark the row NOT APPLICABLE. " + PARITY)
        columns = [("final_text", 3), ("consultation", 5), ("limits", 6), ("provenance", 7)]
        if number not in ("13", "14"):
            columns.append(("permitted", 4))
        for field, n in columns:
            if row.get(field) != _cell(cells, n):
                errors.append(where + "%s differs from Document 3 column %s. %s" % (field, n, PARITY))
    start = date.fromisoformat(current["start"]) if current.get("start") else None
    expected = (("Employing organization", (current.get("employer") or {}).get("club"), False),
                ("Position title", current.get("title"), True),
                ("Effective start date", f"{start:%B} {start.day}, {start.year}" if start else None, False))
    pointer = CONTRACT_POINTER % current.get("id")
    for label, value, fold in expected:
        cells = contract.get(label)
        entry = _cell(cells, 2) if cells else None
        if entry is None:
            errors.append(prefix + "Document 3 section 3.1 has no %s row. %s" % (label, PARITY))
        elif entry == pointer:
            continue
        elif "current_job.json" in entry:
            errors.append(prefix + "Document 3 section 3.1 %s points to the job record other than exactly as %s. %s"
                          % (label, pointer, PARITY))
        elif not (value and (value.lower() in entry.lower() if fold else value in entry)):
            errors.append(prefix + "Document 3 section 3.1 %s does not match the job record. %s" % (label, PARITY))
    return errors


def _game_date(job, season, week, root):
    """The employer club's game date for a week, from the regular-season
    fixtures or, for a postseason round, the bracket built from the root's
    closed receipts."""
    from .seasons import SeasonPaths
    club = ((appointment(job) or {}).get("employer") or {}).get("club")
    paths = SeasonPaths(season, root)
    ours = [g for g in paths.regular_games() if g["week"] == week and club in (g["away"], g["home"])]
    if not ours:
        from . import postseason
        if not postseason.is_postseason(week):
            raise ValueError("no %s game in week %d" % (club, week))
        games = postseason.schedule(week, regular_receipts=postseason._load(paths.receipts),
                                    post_receipts=postseason._load(paths.postseason_receipts),
                                    slots=json.loads(paths.postseason_slots.read_text(encoding="utf-8")),
                                    season=season)
        ours = [g for g in games if club in (g["away"], g["home"])]
        if not ours:
            raise ValueError("no %s game in week %d" % (club, week))
    return date.fromisoformat(ours[0]["date"])


def _party_refs(job, current):
    """(location, party id) for every field that names a party."""
    yield "holder", job.get("holder")
    reporting = current.get("reporting") or {}
    for pid in reporting.get("employment_decided_by") or ():
        yield "reporting.employment_decided_by", pid
    for key in ("direct_supervisor", "evaluator"):
        if reporting.get(key) is not None:
            yield "reporting." + key, reporting[key]
    for row in (current.get("authority") or {}).get("domains") or ():
        for pid in row.get("final") or ():
            yield "authority row %s final" % row.get("row"), pid
        if row.get("overruled_by") is not None:
            yield "authority row %s overruled_by" % row.get("row"), row["overruled_by"]
    delegation = current.get("delegation") or {}
    for row in delegation.get("play_calling") or ():
        for key in ("caller", "prepares", "transmits", "front_declaration"):
            if row.get(key) is not None:
                yield "delegation.play_calling %s" % key, row[key]
    management = delegation.get("game_management") or {}
    if management.get("decides") is not None:
        yield "delegation.game_management.decides", management["decides"]
    for carrier in (delegation.get("relay") or {}).get("carriers") or ():
        yield "delegation.relay.carriers", carrier.get("party")
    emergency = delegation.get("emergency") or {}
    for pid in emergency.get("practice_lead") or ():
        yield "delegation.emergency.practice_lead", pid
    if emergency.get("game_day_caller") is not None:
        yield "delegation.emergency.game_day_caller", emergency["game_day_caller"]
    for request in current.get("employer_requests") or ():
        yield "employer_requests %s by" % request.get("id"), request.get("by")
    for item in current.get("evaluation") or ():
        if item.get("by") != "contract":
            yield "evaluation %s by" % item.get("id"), item.get("by")


def _interval_errors(job, prefix):
    errors = []
    phases = {r.get("phase") for r in ((appointment(job) or {}).get("delegation") or {}).get("play_calling") or ()}
    for phase in sorted(phases, key=str):
        if phase not in PHASES:
            errors.append(prefix + "unknown delegation phase %r" % (phase,))
            continue
        rows = _intervals(job, phase)
        open_ended = [r for r in rows if r.get("to") is None]
        if len(open_ended) != 1 or rows[-1].get("to") is not None:
            errors.append(prefix + "%s delegation must end with exactly one interval without an end" % phase)
        for i, row in enumerate(rows):
            if row.get("from") is not None and row.get("to") is not None and row["from"] >= row["to"]:
                errors.append(prefix + "%s delegation interval from %s does not end after it starts" % (phase, row["from"]))
            if i and rows[i - 1].get("to") != row.get("from"):
                errors.append(prefix + "%s delegation intervals overlap or leave a gap at %s"
                              % (phase, row.get("from") or "the start"))
    return errors


def validation_errors(root, mapping, events, master):
    """Every rule the job record must satisfy (docs/career_layer.md)."""
    prefix = "Current job: "
    try:
        job = load(root)
    except ValueError as exc:
        return [prefix + str(exc)]
    errors = []
    try:
        errors.extend(_validation_errors(job, root, mapping, events, master, prefix))
    except (KeyError, IndexError, TypeError, ValueError, AttributeError) as exc:
        errors.append(prefix + "malformed record: %s" % exc)
    return errors


def _validation_errors(job, root, mapping, events, master, prefix):
    from .decision_queue import CLASSES
    errors = []
    parties = job.get("parties")
    # 1. Schema.
    if job.get("status") not in STATUSES:
        errors.append(prefix + "status must be one of %s" % ", ".join(STATUSES))
    if not isinstance(parties, dict) or job.get("holder") not in parties:
        errors.append(prefix + "the holder must be a party")
        parties = parties if isinstance(parties, dict) else {}
    appointments = job.get("appointments") or []
    ids = [a.get("id") for a in appointments]
    if len(ids) != len(set(ids)):
        errors.append(prefix + "appointment ids must be unique")
    open_ended = [a.get("id") for a in appointments if a.get("end") is None]
    if job.get("status") == "EMPLOYED":
        if job.get("current_appointment") not in ids or open_ended != [job.get("current_appointment")]:
            errors.append(prefix + "an employed holder's current appointment must be the one appointment without an end")
    elif job.get("status") == "BETWEEN_JOBS":
        if job.get("current_appointment") is not None or open_ended:
            errors.append(prefix + "a holder between jobs has no current or open-ended appointment")
    current = appointment(job)
    if current is None:
        if job.get("status") == "EMPLOYED":
            return errors
        current = {}
    elif current.get("role") not in ROLES:
        errors.append(prefix + "role must be one of %s" % ", ".join(ROLES))
        return errors
    for where, pid in _party_refs(job, current):
        if pid not in parties:
            errors.append(prefix + "%s names %r, which is not a party" % (where, pid))
    # 2. Desk.
    profile = desk_profile(job)
    if profile not in BUILT_DESKS:
        errors.append(prefix + "desk for role %s is defined but not built" % profile)
    # 3. Dates and events.
    nodes = list(_walk(job))
    for where, node in nodes:
        for key in DATE_KEYS:
            if node.get(key) is None:
                continue
            try:
                when = date.fromisoformat(node[key])
            except (TypeError, ValueError):
                errors.append(prefix + "%s.%s is not an ISO date" % (where, key))
                continue
            if key in PAST_KEYS and when > master:
                errors.append(prefix + "%s.%s %s is after the master date" % (where, key, node[key]))
            elif key in SCHEDULED_KEYS and when > master and not _scheduled(job, node, key, master):
                errors.append(prefix + "%s.%s %s is after the master date and no instruction by then schedules it"
                              % (where, key, node[key]))
        if isinstance(node.get("event"), str) and node["event"] not in events:
            errors.append(prefix + "%s.event %s is not a closed event" % (where, node["event"]))
    # 4. Records.
    for where, node in nodes:
        if "path" in node:
            problem = record_error(root, mapping, node)
            if problem:
                errors.append(prefix + "%s: %s" % (where, problem))
    # 5. Authority rows.
    rows = (current.get("authority") or {}).get("domains") or []
    numbers = [r.get("row") for r in rows]
    if current:
        missing = [n for n in AUTHORITY_ROWS if n not in numbers]
        doubled = sorted({n for n in numbers if numbers.count(n) > 1}, key=str)
        if missing or doubled or [n for n in numbers if n not in AUTHORITY_ROWS]:
            errors.append(prefix + "authority rows must be exactly Document 3's rows once each "
                          "(missing %s; duplicated %s)" % (", ".join(missing) or "none", ", ".join(doubled) or "none"))
        elif tuple(numbers) != AUTHORITY_ROWS:
            errors.append(prefix + "authority rows must follow Document 3's order")
    for row in rows:
        if row.get("stone_action") not in STONE_ACTIONS:
            errors.append(prefix + "authority row %s stone_action must be one of %s" % (row.get("row"), ", ".join(STONE_ACTIONS)))
        if row.get("delegated") is not None:
            match = DELEGATED.match(str(row["delegated"]))
            if not match or not _intervals(job, match[1]):
                errors.append(prefix + "authority row %s delegated %s names no phase with intervals"
                              % (row.get("row"), row["delegated"]))
    # 6. Delegation intervals.
    errors.extend(_interval_errors(job, prefix))
    # 7. Call-sheet caller parity.
    errors.extend(_caller_parity_errors(job, root, mapping, prefix))
    # 8. Standing instructions.
    every = instructions(job, None)
    names = [i.get("id") for i in every]
    if len(names) != len(set(names)):
        errors.append(prefix + "standing instruction ids must be unique")
    queue_ids = None
    for item in every:
        label = prefix + "standing instruction %s: " % item.get("id")
        if item.get("status") not in INSTRUCTION_STATUSES:
            errors.append(label + "status must be one of %s" % ", ".join(INSTRUCTION_STATUSES))
        bad = [c for c in item.get("closes") or () if c not in CLASSES]
        if bad or not isinstance(item.get("closes"), list):
            errors.append(label + "closes must list decision classes (%s)" % ", ".join(map(str, bad)))
        if item.get("subject") is not None and item["subject"] not in SUBJECTS:
            errors.append(label + "subject must be one of %s" % ", ".join(SUBJECTS))
        if item.get("open_item") is not None:
            if queue_ids is None:
                from . import decision_queue
                try:
                    queue_ids = {i.get("id") for i in decision_queue.load(root)["items"]}
                except ValueError as exc:
                    errors.append(label + str(exc))
                    queue_ids = set()
            if item["open_item"] not in queue_ids:
                errors.append(label + "open_item %s is not a decision-queue item" % item["open_item"])
        record = item.get("record") or {}
        if record.get("pointer") is not None and record_error(root, mapping, record) is None:
            target = pointed(root, mapping, record)
            if isinstance(target, dict) and "id" in target and target["id"] != item.get("id"):
                errors.append(label + "the pointed rule's id is %s" % target["id"])
    # 8a. Game management and employer requests.
    decisions = ((current.get("delegation") or {}).get("game_management") or {}).get("decisions") or []
    seen = [d.get("id") for d in decisions]
    if len(seen) != len(set(seen)):
        errors.append(prefix + "game-management decision ids must be unique")
    for decision in decisions:
        if decision.get("mechanism") not in MECHANISMS:
            errors.append(prefix + "game-management decision %s mechanism must be one of %s"
                          % (decision.get("id"), ", ".join(MECHANISMS)))
        if decision.get("id") not in SUBJECTS:
            errors.append(prefix + "game-management decision id %s must be one of %s"
                          % (decision.get("id"), ", ".join(SUBJECTS)))
    requests = current.get("employer_requests") or []
    seen = [r.get("id") for r in requests]
    if len(seen) != len(set(seen)):
        errors.append(prefix + "employer request ids must be unique")
    for request in requests:
        if request.get("status") not in REQUEST_STATUSES:
            errors.append(prefix + "employer request %s status must be one of %s"
                          % (request.get("id"), ", ".join(REQUEST_STATUSES)))
        if "record" not in request:
            errors.append(prefix + "employer request %s has no record" % request.get("id"))
    # 9. Document 3 parity.
    errors.extend(f3_parity_errors(job, root))
    # 10. The contract and term, read from the coach record (stored there once).
    errors.extend(_contract_errors(job, current, root, prefix))
    errors.extend(_staff_errors(job, current, root, master, prefix))
    return errors


def _contract_errors(job, current, root, prefix):
    """The appointment's contract pointer resolves to a contract with the same club, job and
    start, its coach's hire names this appointment, and every dated calling change on a staff
    coach's record matches a change in the delegation."""
    from . import coaches
    if not current:
        return []
    errors = []
    if "term" in current or "contract" in current:
        errors.append(prefix + "the appointment stores its term or contract; they are read from the coach "
                      "record that contract_record names")
    pointer = current.get("contract_record")
    if not isinstance(pointer, dict) or set(pointer) != {"coach", "contract"}:
        return errors + [prefix + "contract_record must name the coach record and the contract in it"]
    try:
        record = coaches.load(pointer["coach"], root)
        terms = coaches.contract(record, pointer["contract"])
    except ValueError as exc:
        return errors + [prefix + "contract_record: %s" % exc]
    signed = terms["signed"]
    employer = (current.get("employer") or {}).get("club")
    if terms.get("club") != employer or terms.get("job") != current.get("title") or signed["date"] != current.get("start"):
        errors.append(prefix + "the contract's club, job and signing date must be the appointment's")
    if not coaches.end_date(terms):
        errors.append(prefix + "the contract records no end date")
    hire = coaches.hired(record, employer)
    if hire is None or hire.get("appointment") != current.get("id") or hire["date"] != current.get("start"):
        errors.append(prefix + "the coach record's hire must name this appointment on its start date")
    parties = job.get("parties") or {}
    for slug, other in coaches.load_all(root).items():
        pid = other.get("party")
        if pid is not None and pid not in parties:
            errors.append(prefix + "coach record %s names party %r, which is not a party" % (slug, pid))
        for entry in coaches.entries(other, "calling_changed"):
            changes = [r for r in _intervals(job, entry["phase"])
                       if entry["date"] in (r.get("from"), r.get("to"))
                       and pid in (r.get("caller"), r.get("prepares"), r.get("transmits"))]
            if not changes:
                errors.append(prefix + "coach record %s dates a %s calling change on %s that the delegation "
                              "does not hold" % (slug, entry["phase"], entry["date"]))
    return errors


def _staff_errors(job, current, root, master, prefix):
    """The delegation and the coach records agree both ways: every coach the delegation names
    (a caller, a preparer or the coach who sends in the call; a relay carrier; a practice lead or
    game-day caller if the head coach is out) is a party with a coach record of the same name, on
    the employer's staff on the master date when the arrangement is current; and every coach
    record names a party of the same name."""
    from . import coaches
    if not current:
        return []
    club = (current.get("employer") or {}).get("club")
    parties = job.get("parties") or {}
    records = {r.get("party"): (slug, r) for slug, r in coaches.load_all(root).items() if r.get("party")}
    errors = []
    for pid, (slug, record) in records.items():
        party = parties.get(pid)
        if isinstance(party, dict) and party.get("name") != record.get("name"):
            errors.append(prefix + "coach record %s is %s but party %r is %s"
                          % (slug, record.get("name"), pid, party.get("name")))
    delegation = current.get("delegation") or {}
    named = []   # (party, what, whether the arrangement is in force on the master date)
    for row in delegation.get("play_calling") or ():
        now = _day(row.get("from"), True) <= master < _day(row.get("to"), False)
        for key in ("caller", "prepares", "transmits"):
            if row.get(key):
                named.append((row[key], "the %s %s" % (row.get("phase"), key), now))
    for carrier in (delegation.get("relay") or {}).get("carriers") or ():
        named.append((carrier.get("party"), "a relay carrier", True))
    emergency = delegation.get("emergency") or {}
    for pid in list(emergency.get("practice_lead") or ()) + [emergency.get("game_day_caller")]:
        if pid:
            named.append((pid, "an emergency lead", True))
    for pid, what, now in named:
        if pid not in records:
            errors.append(prefix + "%s, %s, has no coach record (data/people/coaches)" % (pid, what))
        elif now and not coaches.on_staff(records[pid][1], club, master):
            errors.append(prefix + "%s, %s, is not on the %s staff on %s by his coach record"
                          % (pid, what, club, master.isoformat()))
    return errors


def _scheduled(job, node, key, master):
    """A future from, to, effective, start or end recorded with the
    instruction that scheduled it: the entry's own instructed (or given)
    date, or, for a delegation interval's end, the next interval's."""
    def instructed(entry):
        given = entry.get("given") if isinstance(entry.get("given"), dict) else {}
        when = entry.get("instructed") or given.get("in_world")
        return when is not None and date.fromisoformat(when) <= master
    if instructed(node):
        return True
    if key == "to" and node.get("phase") in PHASES:
        return any(instructed(r) for r in _intervals(job, node["phase"]) if r.get("from") == node["to"])
    return False


def _caller_parity_errors(job, root, mapping, prefix):
    """Each committed call sheet's defensive caller is the job record's
    defensive caller on that game's date."""
    from .seasons import SeasonPaths
    if appointment(job) is None:
        return []
    season = int(mapping["active_season"])
    paths = SeasonPaths(season, root)
    errors = []
    for week in range(1, 22):
        for postseason in (False, True):
            try:
                sheet = paths.call_sheet(week, postseason)
            except ValueError as exc:
                errors.append(prefix + "week %d: %s" % (week, exc))
                continue
            if not sheet.is_file():
                continue
            name = sheet.relative_to(paths.root).as_posix()
            try:
                caller = (json.loads(sheet.read_text(encoding="utf-8")).get("defensive_call_sheet") or {}).get("caller")
            except (ValueError, AttributeError) as exc:
                errors.append(prefix + "%s is unreadable: %s" % (name, exc))
                continue
            if caller is None:
                continue
            try:
                on = _game_date(job, season, week, root)
            except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
                errors.append(prefix + "%s names a defensive caller, but its game cannot be dated (%s)" % (name, exc))
                continue
            expected = caller_on(job, "defense", on)
            if expected is None or caller != party_name(job, expected):
                errors.append(prefix + "%s names %s as the defensive caller; the job record has %s on %s"
                              % (name, caller, party_name(job, expected) if expected else "no caller", on.isoformat()))
    return errors
