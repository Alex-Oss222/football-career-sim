"""Stone's Game Plan page (game week version 2, docs/game_week_v2.md sections 4
and 8): its fixed headings, how it is read, and how it compiles into the
records the game path already reads.

The page is the head coach's decision for a game week, in football language,
on the layout of foundation/templates/game_week/game_plan_template.md: a
header (head coach, game, the briefing he answers and his baseline) and seven
numbered sections. Every entry is one labelled line (``**Label:** value``) or
a row of one of the page's tables; a page has no Opener, Returns, Family,
Type or Tags column and no row id. He fills it in place or uploads a .md or
.txt file with the same headings.

Three answers are different (section 4.3): **No change** keeps the last legal
instruction set; **None** means intentionally nothing; a line left empty is
**unanswered**, and an unanswered line never approves anything. "Carry Week
NN" reads that week's call sheet as set (its applied plan for a week set on a
Game Plan).

What compiles, and what does not. ``compile_sheet`` turns the page into the
existing ``call_sheet.json`` exactly in the shape the weekly build reads
(runtime/week_inputs), deterministically, with a source map from every
emitted call, defensive row and decision block to the page line or the
carried frozen item it came from:

- the calls: the baseline week's calls, the Primary calls table (a call as
  the active book and the earlier frozen sheets name it, its situations in
  "When I want it", and any explicit variation in parentheses, "(Kelce
  receiving Y)" or "(without Kelce receiving Y)"), less the calls not
  available and the special plays removed or kept for practice. A call's
  personnel, formation, motion, protection and tags are resolved from the
  frozen form when exactly one form matches what he wrote; when more than one
  does, the check asks which (never a guess); a call no earlier Jacksonville
  sheet carries is a new install, read from its name, and must be named as
  this week's install in section 6;
- the opening sequence: "Opening calls, in order" (a call repeated is a
  return to it), or "Carry Week NN opening"; a call on it that is not a
  normal-down call is on the opening sequence's list. The tags the opening
  list and the two-point list imply ("opener", "two-point folder") follow
  them;
- the defensive responses table, in the active defensive book's words: a
  first cell naming a situation the defense keys (normal downs, third and
  long, the red zone, late lead and the rest) is that situation's row, one
  beginning "If" or "When" a conditional row, "Counter" a counter, any other
  a presentation; the response cell is read word by word (Nickel Even Cover
  6, passing strength; Dime, Replace Field), and each row cites its own page
  line;
- the rush rule, the defensive caller, and the fourth-down, two-point and
  kickoff decisions (Standing rule, Carry Week NN, No change, None, or "My
  rules, otherwise ..." above a rule table).

Everything else is author intent: what he wants the game to look like, each
call's football reason and stop condition, the situational lines, the
contingencies, the practice table (besides its installs) and the staff
directions. Intent is stored and shown (the page is its record, and the
applied plan record keeps it with its line and date), and it never changes
the compiled sheet: the same choices with reworded reasons compile to the
same bytes (tests/test_game_plan.py). Nothing here reads the current-job
record or the decision queue (tests/test_career_layer_isolation.py); the
scripts that check and apply a page do.
"""
from __future__ import annotations

import copy
import json
import re

# ---------------------------------------------------------------- the page's fixed parts
HEADINGS = ("1. What I want this game to look like", "2. Game-day availability and personnel",
            "3. Offense: what we are calling and why", "4. Defense: what we are showing and answering",
            "5. Special teams and game decisions", "6. What we will practice",
            "7. Directions to the staff and public position")
SECTIONS = HEADINGS
CALLS_SUB = "Primary calls"
SITUATIONS_SUB = "Situational changes from the standing / previous menu"
SUBHEADINGS = {3: (CALLS_SUB, SITUATIONS_SUB)}
CONTINGENCY = re.compile(r"^If .+ cannot dress$")
CONTINGENCY_LABEL = "If a pending player cannot dress"

# (key, section (0 is the header), label, kind), in the page's order. Kinds: fact (written by the
# builder), briefing, baseline, intent (stored, never compiled), inactives, depth, caller, opening,
# situational (intent; "Carry Week NN" is held to the baseline), special, removals, rush, decision.
FIELDS = (
    ("head_coach", 0, "Head coach", "fact"),
    ("game", 0, "Game", "fact"),
    ("briefing", 0, "Briefing used", "briefing"),
    ("baseline", 0, "Baseline", "baseline"),
    ("attack", 1, "The matchup I am attacking", "intent"),
    ("protect", 1, "What I must not give them", "intent"),
    ("change_course", 1, "What would make me change course", "intent"),
    ("inactives", 2, "Inactives", "inactives"),
    ("depth", 2, "Depth/role changes", "depth"),
    ("contingency", 2, CONTINGENCY_LABEL, "intent"),
    ("coverage_units", 2, "Special coverage and substitution consequences", "intent"),
    ("offense_caller", 3, "Caller", "caller"),
    ("base_personnel", 3, "Base personnel and roles", "intent"),
    ("learn", 3, "The first things I want to learn", "intent"),
    ("opening_approach", 3, "Opening approach", "intent"),
    ("opening", 3, "Opening calls, in order", "opening"),
    ("third_down", 3, "Third down", "situational"),
    ("backed_up", 3, "Backed up", "situational"),
    ("red_zone", 3, "High red zone, low red zone, goal line", "situational"),
    ("two_minute", 3, "Two-minute / hurry-up", "situational"),
    ("four_minute", 3, "Four-minute / protect a lead", "situational"),
    ("sudden_change", 3, "Sudden change / shot opportunities", "situational"),
    ("special_plays", 3, "Special plays", "special"),
    ("not_available", 3, "Calls not available this week", "removals"),
    ("defense_caller", 4, "Caller", "caller"),
    ("front", 4, "Base front and run fits", "intent"),
    ("coverage", 4, "Coverage and rush approach", "intent"),
    ("rush", 4, "Rush rule", "rush"),
    ("discover", 4, "What we need to discover early", "intent"),
    ("matchups", 4, "Individual matchups / roles changed", "intent"),
    ("kicking_caller", 5, "Kicking-game caller", "caller"),
    ("kicking", 5, "Return, coverage and operation instructions", "intent"),
    ("fourth_down", 5, "Fourth downs", "decision"),
    ("two_point", 5, "Two-point tries", "decision"),
    ("kickoff", 5, "Kickoffs and onside situations", "decision"),
    ("endgame", 5, "Timeouts, challenges and endgame", "intent"),
    ("participation", 6, "If a medical assessment changes participation", "intent"),
    ("tradeoff", 6, "What leaves the practice menu to make room", "intent"),
    ("staff", 7, "Staff instructions", "intent"),
    ("public", 7, "Public position, if I am adding one", "intent"),
    ("open_decisions", 7, "Other open decisions", "intent"),
    ("ready", 7, "Ready to lock after", "intent"),
)
FIELD = {key: (section, label, kind) for key, section, label, kind in FIELDS}
# The kinds whose answer may run on below its label (further lines or bullets): his own direction,
# kept as written and never compiled. Every other answer is read from its label's line alone.
CONTINUED_KINDS = ("intent", "situational")
# The labelled lines of each subsection of section 3 (the rest of section 3 sits above them).
SITUATIONAL_KEYS = ("third_down", "backed_up", "red_zone", "two_minute", "four_minute", "sudden_change",
                    "special_plays", "not_available")
DECISION_KEYS = ("fourth_down", "two_point", "kickoff")
DECISION_SECTIONS = {"Fourth downs": "fourth_down", "Two-point tries": "two_point",
                     "Kickoffs and onside situations": "kickoff"}

# The page's tables: the section, the subsection (or None) and the columns.
CALL_COLUMNS = ("Call / concept as named in the active book", "When I want it", "Football reason and key read",
                "Protection, personnel or stop condition")
RESPONSE_COLUMNS = ("Offensive situation / presentation", "Prepared front, coverage or pressure response",
                    "Football reason", "Counter / when to get out of it")
PRACTICE_COLUMNS = ("Priority", "Responsible coach and players", "Football situation to rehearse",
                    "What shows it is ready")
TABLES = {"calls": (3, CALLS_SUB, CALL_COLUMNS), "responses": (4, None, RESPONSE_COLUMNS),
          "practice": (6, None, PRACTICE_COLUMNS)}

TOP_KEYS = ("schema_version", "team", "event", "status", "frozen", "provenance")
STATUS = "EX_ANTE_CALL_SHEET_FROZEN"
CALL_KEYS = ("name", "family", "type", "personnel", "formation", "motion", "protection", "target", "carrier",
             "tags", "opener", "opener_returns", "menus", "what_stone_is_looking_at")
FORM_KEYS = ("family", "type", "personnel", "formation", "motion", "protection", "target", "carrier")
# Tags the page's own lists imply, re-derived on every compile.
OPENER_TAG, TWO_POINT_TAG = "opener", "two-point folder"
DERIVED_TAGS = (OPENER_TAG, TWO_POINT_TAG)
DEFENSE_KEYS = ("schema_version", "team", "caller", "book", "packet", "notes", "rush_rule", "practiced", "rows")
PRACTICED_KEYS = ("packages", "fronts", "coverages", "pressures", "tags")

GROUPS = {"Quarterbacks": "QB", "Running backs": "RB", "Fullback": "FB", "Fullbacks": "FB", "Wide receivers": "WR",
          "Tight ends": "TE", "Offensive line": "OL", "Defensive line": "DL", "Linebackers": "LB",
          "Defensive backs": "DB", "Kicker": "K", "Punter": "P", "Long snapper": "LS"}
ROLES = {"Starter": "passer", "Kicker": "placekicker", "Punter": "punt", "Kick returner": "kick_return",
         "Punt returner": "punt_return", "Nickel": "nickel", "Outside reserve corner": "outside_reserve"}

STANDING = "Standing rule"
CARRY = re.compile(r"^carry week (\d{1,2})\b\s*(.*)$", re.I)
NONE = re.compile(r"^none\.?$", re.I)
NO_CHANGE = re.compile(r"^no change\.?$", re.I)
NEW_PLAN = re.compile(r"^new plan\.?$", re.I)
MY_RULES = re.compile(r"^my rules(?: below)?[,;.:]?\s*otherwise\s+(.+?)\.?$", re.I)
LABELLED = re.compile(r"^\*\*([^*]+?):\*\*\s*(.*)$")
DATE = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) "
                  r"(\d{1,2}), (\d{4})(?:,? revision (\d{1,2}))?\.?$", re.I)

# The active defensive book has one rush rule (runtime/defensive_calls.RUSH_RULE), accepted in his
# voice or the staff's; the line he writes is kept as written.
RUSH_CHOICE = "Four unless I call the five-man counter"
RUSH_WORDS = frozenset({"four unless stone calls the five man counter", "four unless i call the five man counter"})


def rush_words(text):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split())


# ---------------------------------------------------------------- tables and values
def cell(value):
    return str(value).replace("|", "\\|")


def table(head, rows):
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    return lines + ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]


def cells(line):
    """The cells of a table row, its escaped bars restored."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", body)]


def is_rule_row(line):
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells(line) if c)


def read_table(lines, columns, where, problems, strict=True):
    """[(line number, {column: value})] of one table (its header row first). ``strict`` requires
    exactly the page's columns in order; otherwise every header must be one of ``columns``."""
    if not lines:
        return []
    head = cells(lines[0][1])
    if strict and tuple(head) != tuple(columns):
        problems.append("%s: the table's columns are %s; keep the page's columns (%s)"
                        % (where, ", ".join(head), ", ".join(columns)))
        return []
    unknown = [h for h in head if h not in columns]
    if unknown:
        problems.append("%s: the table has the column%s %s, not one of %s" % (
            where, "s" if len(unknown) > 1 else "", ", ".join(repr(u) for u in unknown), ", ".join(columns)))
        return []
    out = []
    for n, t in lines[1:]:
        if is_rule_row(t):
            continue
        values = cells(t)
        if len(values) != len(head):
            problems.append("%s: a row has %d cells, the header %d: %s" % (where, len(values), len(head), t))
            continue
        if not any(values):
            continue
        out.append((n, dict(zip(head, values))))
    return out


def items(text, separator=";"):
    """The items of a list written on one line, separated by ``separator``."""
    return [v.strip() for v in str(text or "").split(separator) if v.strip()]


def listed(text):
    return [v.strip() for v in re.split(r"[,;]", text or "") if v.strip()]


def norm(text):
    """A call or a phrase as words: lowercase, every mark but + a space."""
    return " ".join(re.sub(r"[^a-z0-9+]+", " ", str(text or "").lower()).split())


def clock(seconds):
    return "%d:%02d" % divmod(int(seconds), 60)


def seconds(text):
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", text.strip())
    if not m:
        raise ValueError("%r is not a clock time like 2:00" % text)
    return int(m[1]) * 60 + int(m[2])


def margin_text(value):
    return "tied" if value == 0 else ("up %d" % value if value > 0 else "down %d" % -value)


def margin_value(text):
    text = text.strip().lower()
    if text == "tied":
        return 0
    m = re.fullmatch(r"(up|down) (\d{1,2})", text)
    if not m:
        raise ValueError("%r is not a score like down 5, tied or up 1" % text)
    return int(m[2]) * (1 if m[1] == "up" else -1)


def range_text(value, item, better="or more", worse="or less"):
    if isinstance(value, list):
        return ", ".join(item(v) for v in value)
    if "min" in value and "max" in value:
        return "%s to %s" % (item(value["min"]), item(value["max"]))
    if "min" in value:
        return "%s %s" % (item(value["min"]), better)
    return "%s %s" % (item(value["max"]), worse)


def range_value(text, item, better="or more", worse="or less"):
    text = text.strip()
    for word, key in ((better, "min"), (worse, "max")):
        if text.endswith(" " + word):
            return {key: item(text[:-len(word) - 1])}
    if " to " in text:
        low, high = text.split(" to ", 1)
        return {"min": item(low), "max": item(high)}
    return [item(v) for v in listed(text)]


def number(text):
    if not re.fullmatch(r"\d{1,2}", text.strip()):
        raise ValueError("%r is not a number of yards" % text)
    return int(text)


QUARTERS = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", "OT": "OT"}


def quarter_value(text):
    names = {v.lower(): k for k, v in QUARTERS.items()}
    out = []
    for item in listed(text):
        key = item.lower()
        if key in names:
            out.append(names[key])
        elif key.isdigit() and int(key) in QUARTERS:
            out.append(int(key))
        else:
            raise ValueError("%r is not a quarter (1st, 2nd, 3rd, 4th or OT)" % item)
    return out


def yes_no(text):
    if text.strip().lower() in ("yes", "no"):
        return text.strip().lower() == "yes"
    raise ValueError("%r is not Yes or No" % text)


def long_date(value):
    return "%s %d, %d" % (value.strftime("%B"), value.day, value.year)


# ---------------------------------------------------------------- decision rules
RULE_COLUMNS = {
    "two_point": (("Quarter", "period"), ("Score after the touchdown", "diff_after_td"), ("Clock", "clock"),
                  ("Decision", "decision")),
    "kickoff": (("Quarter", "period"), ("Score after our score", "diff_after_score"), ("Clock", "clock"),
                ("Opening kick", "opening_kick"), ("Decision", "decision")),
    "fourth_down": (("Quarter", "period"), ("Score", "margin"), ("Clock", "clock"), ("Distance", "ydstogo"),
                    ("Yards to the goal line", "los"), ("Goal to go", "goal_to_go"), ("Decision", "decision"),
                    ("Call", "call")),
}
WHEN_ORDER = {"two_point": ("period", "diff_after_td", "game_seconds_min", "game_seconds_max"),
              "kickoff": ("period", "diff_after_score", "game_seconds_min", "game_seconds_max", "opening_kick"),
              "fourth_down": ("period", "margin", "ydstogo", "los", "goal_to_go", "game_seconds_min",
                              "game_seconds_max")}
DECISION_WORDS = {"two_point": {"go": "Go for two", "kick": "Kick"},
                  "kickoff": {"onside": "Onside", "deep": "Deep"},
                  "fourth_down": {"go": "Go", "field_goal": "Field goal", "punt": "Punt"}}
OTHERWISE_WORDS = {"league": "League practice", "ask": "Ask me"}


def decision_word(kind, value):
    return DECISION_WORDS[kind].get(value) or OTHERWISE_WORDS.get(value) or str(value)


def rule_cell(kind, key, rule):
    when = rule.get("when") or {}
    if key == "decision":
        return decision_word(kind, rule.get("decision"))
    if key == "call":
        return rule.get("call") or ""
    if key == "clock":
        parts = []
        if "game_seconds_max" in when:
            parts.append("%s or less left" % clock(when["game_seconds_max"]))
        if "game_seconds_min" in when:
            parts.append("%s or more left" % clock(when["game_seconds_min"]))
        return ", ".join(parts)
    if key not in when:
        return ""
    value = when[key]
    if key == "period":
        return ", ".join(QUARTERS[p] for p in value)
    if key in ("diff_after_td", "diff_after_score", "margin"):
        return range_text(value, margin_text, "or better", "or worse")
    if key in ("ydstogo", "los"):
        return range_text(value, str)
    if key in ("goal_to_go", "opening_kick"):
        return "Yes" if value else "No"
    return str(value)


def rule_from_row(kind, row, where, problems):
    when, rule = {}, {}
    words = {v.lower(): k for k, v in DECISION_WORDS[kind].items()}
    try:
        for column, value in row.items():
            key = dict(RULE_COLUMNS[kind]).get(column)
            if not value or key is None:
                continue
            if key == "period":
                when["period"] = quarter_value(value)
            elif key in ("diff_after_td", "diff_after_score", "margin"):
                when[key] = range_value(value, margin_value, "or better", "or worse")
            elif key in ("ydstogo", "los"):
                when[key] = range_value(value, number)
            elif key == "clock":
                for part in listed(value):
                    m = re.fullmatch(r"(\d{1,2}:\d{2}) or (less|more) left", part)
                    if not m:
                        raise ValueError("%r is not a clock like 2:00 or less left" % part)
                    when["game_seconds_max" if m[2] == "less" else "game_seconds_min"] = seconds(m[1])
            elif key in ("goal_to_go", "opening_kick"):
                when[key] = yes_no(value)
            elif key == "decision":
                if value.lower() not in words:
                    raise ValueError("%r is not one of %s" % (value, ", ".join(DECISION_WORDS[kind].values())))
                rule["decision"] = words[value.lower()]
            elif key == "call":
                rule["call"] = value
    except ValueError as exc:
        problems.append("%s: %s" % (where, exc))
        return None
    if not when:
        problems.append("%s: a rule needs at least one condition (%s)" % (where, ", ".join(
            c for c, k in RULE_COLUMNS[kind] if k not in ("decision", "call"))))
        return None
    if "decision" not in rule:
        problems.append("%s: a rule needs its decision" % where)
        return None
    ordered = {k: when[k] for k in WHEN_ORDER[kind] if k in when}
    return {"when": ordered, "decision": rule["decision"], **({"call": rule["call"]} if "call" in rule else {})}


# ---------------------------------------------------------------- the situations a call belongs to
from . import call_situations as cs  # noqa: E402

FINAL_PLAY = "final-play-of-half"
# Each offensive situation a call may name, as the frozen sheets spell it.
SITUATION_TEXT = {cs.NORMAL: "normal down", cs.SECOND_LONG: "2nd-and-long", cs.THIRD_SHORT: "third-and-short",
                  cs.THIRD_MEDIUM: "third-and-medium", cs.THIRD_LONG: "third-and-long", cs.BACKED_UP: "backed up",
                  cs.HIGH_RED: "high red zone", cs.LOW_RED: "low red zone", cs.GOAL_LINE: "goal line",
                  cs.TWO_MINUTE: "two-minute", cs.PRESS: "PRESS sequence", cs.FOUR_MINUTE: "four minute",
                  cs.SUDDEN_CHANGE: "sudden change", cs.TWO_POINT: "two-point", FINAL_PLAY: "final play of half",
                  cs.OPENING: "opening sequence"}
SITUATION_WORDS = ("normal downs", "second and long", "third and short", "third and medium", "third and long",
                   "backed up", "high red zone", "low red zone", "goal line", "two-minute", "PRESS sequence",
                   "four-minute", "sudden change", "two-point tries", "final play of the half")
_SITUATION_ALIASES = {"two-point-tries": cs.TWO_POINT, "two-point-try": cs.TWO_POINT,
                      "two-point-conversions": cs.TWO_POINT, "final-play-of-the-half": FINAL_PLAY,
                      "final-play-of-a-half": FINAL_PLAY, "press-sequences": cs.PRESS, "two-minute-offense": cs.TWO_MINUTE,
                      "four-minute-offense": cs.FOUR_MINUTE, "2nd-and-long": cs.SECOND_LONG}
ASK_WHICH = {"third-down": "third and short, third and medium or third and long",
             "third-downs": "third and short, third and medium or third and long",
             "red-zone": "high red zone, low red zone or goal line"}


def situation_key(phrase):
    """(menu key, problem) for one situation a call names."""
    key = cs.menu_key(phrase)
    key = _SITUATION_ALIASES.get(key, key)
    if key in ASK_WHICH:
        return None, "%r: say which: %s" % (phrase, ASK_WHICH[key])
    if key == cs.OPENING:
        return None, "%r: the opening calls line puts a call in the opening sequence" % phrase
    if key not in SITUATION_TEXT:
        return None, "%r is not a situation of the call sheet (%s)" % (phrase, ", ".join(SITUATION_WORDS))
    return key, None


# ---------------------------------------------------------------- the defensive response words
def _defense_terms():
    from .defensive_calls import COVERAGES, COVERAGE_FAMILIES, FRONTS, PRESSURE_FAMILIES, STRENGTHS
    strengths = "|".join(s.lower() for s in STRENGTHS)
    coverages = sorted((c for c in COVERAGES if not c.isdigit()), key=len, reverse=True)
    numbered = sorted(COVERAGES, key=len, reverse=True)
    front_pattern = "|".join(re.escape(f.lower()) for f in sorted(FRONTS, key=len, reverse=True))
    terms = [
        (r"big nickel", lambda m: {"package": "Big Nickel"}),
        (r"(%s)(?: (%s))?(?! strength)\b" % (front_pattern, strengths),
         lambda m: {"front": next(f for f in FRONTS if f.lower() == m[1]),
                    **({"strength": next(s for s in STRENGTHS if s.lower() == m[2])} if m[2] else {})}),
        (r"(%s) strength" % strengths, lambda m: {"strength": next(s for s in STRENGTHS if s.lower() == m[1])}),
        (r"nickel", lambda m: {"package": "Nickel"}),
        (r"dime", lambda m: {"package": "Dime"}),
        (r"base (?:4|four)(?:[- ]man)?(?: rush)?|four[- ]man rush|four rush",
         lambda m: {"pressure": "base-4"}),
        (r"base", lambda m: {"package": "Base"}),
        (r"cover (%s)" % "|".join(re.escape(c.lower()) for c in numbered),
         lambda m: {"coverage": [next(c for c in COVERAGES if c.lower() == m[1])]}),
        (r"(%s)" % "|".join(re.escape(c.lower()) for c in coverages),
         lambda m: {"coverage": [next(c for c in COVERAGES if c.lower() == m[1])]}),
        (r"replace (field|boundary)", lambda m: {"pressure": "replace", "tags": [m[1]]}),
        (r"replace(?: change-up)?|replacement pressure", lambda m: {"pressure": "replace"}),
        (r"(?:interior )?mug", lambda m: {"pressure": "replace", "tags": ["mug"]}),
    ]
    for key, words in PRESSURE_FAMILIES.items():
        if key in ("base-4", "replace"):
            continue
        spelled = re.escape(words.lower()).replace("/", "[/ ]").replace(r"\-", "[- ]")
        terms.append((spelled, lambda m, key=key: {"pressure": key}))
    for family in COVERAGE_FAMILIES:
        terms.append((r"%s(?: coverage)?" % re.escape(family.lower()), lambda m, f=family: {"coverage": [f]}))
    return [(re.compile(r"(?:%s)(?![0-9a-z])" % pattern), build) for pattern, build in terms]


FILLERS = ("or", "and", "with", "then", "plus", "the", "a", "first")
_TERMS = None


def response_call(text):
    """(call, problems) of one prepared response, read word by word in the active defensive book's
    words; (None, []) for an empty response. A response names at most one package, front, strength
    and pressure; its coverages are the alternatives, in the order written."""
    global _TERMS
    if _TERMS is None:
        _TERMS = _defense_terms()
    low = " ".join(str(text or "").lower().replace(",", " , ").replace(";", " ; ").split())
    if not low:
        return None, []
    found, problems, pos = {}, [], 0
    while pos < len(low):
        if low[pos] in " ,;./":
            pos += 1
            continue
        for pattern, build in _TERMS:
            m = pattern.match(low, pos)
            if m:
                for key, value in build(m).items():
                    if key in ("coverage", "tags"):
                        found.setdefault(key, [])
                        found[key] += [v for v in value if v not in found[key]]
                    elif key in found and found[key] != value:
                        problems.append("%r names two %ss (%s and %s); write one per response, each on its own row"
                                        % (text, key, found[key], value))
                    else:
                        found[key] = value
                pos = m.end()
                break
        else:
            filler = re.compile(r"(?:%s)(?![0-9a-z])" % "|".join(FILLERS)).match(low, pos)
            if filler:
                pos = filler.end()
                continue
            word = re.match(r"[^ ,;]+", low[pos:])[0]
            problems.append("%r is not a word of the active defensive playbook (in %r); write the response in the "
                            "book's words and the reason in its own column" % (word, text))
            pos += len(word)
    order = ("package", "front", "strength", "coverage", "pressure", "tags")
    return {k: found[k] for k in order if k in found}, problems


def response_words(call):
    """[(practiced list, word)] of a defensive call: its package, front, coverages, pressure and tags."""
    out = []
    for key, practiced in (("package", "packages"), ("front", "fronts"), ("pressure", "pressures")):
        if call.get(key):
            out.append((practiced, call[key]))
    out += [("coverages", c) for c in call.get("coverage") or ()]
    out += [("tags", t) for t in call.get("tags") or ()]
    return out


# The defensive situation menus a first cell may name (runtime/defensive_calls.MENUS).
DEF_MENU_WORDS = {"normal-down": "Normal downs", "second-and-long": "Second and long",
                  "third-and-short": "Third and short", "third-and-medium": "Third and medium",
                  "third-and-long": "Third and long", "two-point": "Two-point try", "goal-line": "Goal line",
                  "low-red-zone": "Low red zone", "high-red-zone": "High red zone", "red-zone": "Red zone",
                  "backed-up": "Backed up", "two-minute": "Two-minute", "four-minute": "Four-minute",
                  "lead-late": "Late lead"}
_DEF_ALIASES = {"normal-downs": "normal-down", "two-point-tries": "two-point", "two-point-try": "two-point",
                "late-lead": "lead-late", "a-late-lead": "lead-late"}
KIND_WORDS = {"situation": "Situation", "presentation": "Presentation", "counter": "Counter",
              "conditional": "Conditional"}


def response_kind(text):
    """(kind, menu) of a defensive row from its first cell: a situation the defense keys is that
    situation's row; a cell beginning If or When a conditional row, Counter a counter; any other a
    presentation."""
    key = cs.menu_key(text)
    key = _DEF_ALIASES.get(key, key)
    if key in DEF_MENU_WORDS:
        return "situation", key
    first = (str(text).strip().split() or [""])[0].lower().rstrip(":,")
    if first in ("if", "when"):
        return "conditional", None
    if first == "counter":
        return "counter", None
    return "presentation", None


def row_id(kind, menu, seen):
    """A defensive row's id: its situation for a situation row, else its use and a count."""
    if kind == "situation" and menu:
        return menu
    n = 1
    while "%s-%d" % (kind, n) in seen:
        n += 1
    return "%s-%d" % (kind, n)


# ---------------------------------------------------------------- reading a page
class Field:
    def __init__(self, key, line, text, label):
        self.key, self.line, self.text, self.label = key, line, text, label


def _label_key(section, label):
    if section == 2 and CONTINGENCY.match(label):
        return "contingency"
    for key, s, l, _ in FIELDS:
        if s == section and l == label:
            return key
    return None


def split(text):
    """({key: Field}, {table: [(line, text)]}, {decision key: [(line, text)]}, problems) of a page."""
    fields, tables, rules, problems = {}, {"calls": [], "responses": [], "practice": []}, {}, []
    section, sub, current, found = 0, None, None, set()
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if raw.startswith("## "):
            name = raw[3:].strip()
            if name not in HEADINGS:
                problems.append("The page has a heading %r that is not one of the Game Plan's headings" % name)
                section, sub, current = -1, None, None
                continue
            section, sub, current = HEADINGS.index(name) + 1, None, None
            if section in found:
                problems.append("%s: the heading appears twice" % name)
            found.add(section)
            continue
        if raw.startswith("### "):
            name = raw[4:].strip()
            if name not in SUBHEADINGS.get(section, ()):
                problems.append("%s: %r is not one of its headings; write under the section's own lines"
                                % (heading(section), name))
            sub, current = name, None
            continue
        if section < 0 or not line or line.startswith(">") or raw.startswith("# "):
            continue
        m = LABELLED.match(line)
        if m:
            label, value = m[1].strip(), m[2].strip()
            key = _label_key(section, label)
            if key is None:
                problems.append("%s: %r is not one of its lines" % (heading(section), label))
                current = None
                continue
            if key in fields:
                problems.append("%s: the line %r appears twice" % (heading(section), label))
            fields[key] = Field(key, number, value, label)
            current = key
            continue
        if line.startswith("|"):
            if section == 5 and current in DECISION_KEYS:
                rules.setdefault(current, []).append((number, line))
                continue
            current = None          # a line after a table answers no label above it
            name = next((t for t, (s, subname, _) in TABLES.items() if s == section and subname in (None, sub)
                         and (subname is not None or section != 3)), None)
            if name is None:
                problems.append("%s: a table sits where the page has none (%s)" % (heading(section), line[:60]))
                continue
            tables[name].append((number, line))
            continue
        where = heading(section) if section else "The page's header"
        if current is not None and FIELD[current][2] in CONTINUED_KINDS:
            # A further line or a bullet under a label of his own direction is part of that answer: it
            # is author intent, kept as written, and never compiles.
            f = fields[current]
            f.text = (f.text + "\n" + line) if f.text else line
            continue
        if current is not None:
            problems.append("%s: %r continues the line %r, which is read as one answer; write it on that line, "
                            "the items separated by semicolons" % (where, line[:80], fields[current].label))
            continue
        problems.append("%s: %r is not on a line of its own label; write it after the label it answers"
                        % (where, line[:80]))
    for n, name in enumerate(HEADINGS, 1):
        if n not in found:
            problems.append("%s: the heading is missing" % name)
    for key, section_, label, _ in FIELDS:
        if key not in fields and (section_ == 0 or section_ in found):
            problems.append("%s: the line %r is missing" % (heading(section_) if section_ else "The page's header",
                                                             label))
    return fields, tables, rules, problems


def heading(section):
    return HEADINGS[section - 1] if section else "The page's header"


def where_of(key, label=None):
    """Where a line sits, in the page's words: "Offense, Caller"; a header line by its label."""
    section, fixed, _ = FIELD[key]
    label = label or fixed
    return label if section == 0 else "%s, %s" % (heading(section).split(". ", 1)[-1].split(":")[0], label)


def parse(text):
    """(choices, problems): the page's answers, read into their meanings, and every problem of form
    in football words. ``choices["unanswered"]`` lists the lines left empty."""
    fields, tables, rules, problems = split(text)
    choices = {"fields": {k: {"line": f.line, "text": f.text, "label": f.label} for k, f in fields.items()},
               "unanswered": []}
    for key, _, _, kind in FIELDS:
        f = fields.get(key)
        if f is None or not f.text:
            choices["unanswered"].append(key)
            choices[key] = None
            continue
        reader = READERS.get(kind)
        choices[key] = reader(key, f, problems) if reader else f.text
    for key in DECISION_KEYS:
        value = choices.get(key)
        if isinstance(value, dict) and "otherwise" in value and "rules" in value:
            value["rules"] = []
            rows = read_table(rules.get(key, []), tuple(c for c, _ in RULE_COLUMNS[key]), where_of(key), problems,
                              strict=False)
            for n, row in rows:
                rule = rule_from_row(key, row, where_of(key), problems)
                if rule is not None:
                    value["rules"].append(rule)
            if not value["rules"]:
                problems.append("%s: My rules needs the rule table below the line" % where_of(key))
        elif rules.get(key):
            problems.append("%s: a rule table goes with My rules, otherwise ..." % where_of(key))
    choices["calls"] = [_call_row(n, row, problems) for n, row in
                        read_table(tables["calls"], CALL_COLUMNS, "Offense, Primary calls", problems)]
    choices["responses"] = [_response_row(n, row, problems) for n, row in
                            read_table(tables["responses"], RESPONSE_COLUMNS, "Defense, prepared responses", problems)]
    practice = read_table(tables["practice"], PRACTICE_COLUMNS, "What we will practice", problems)
    choices["practice"] = [{"line": n, **{k: row[c] for k, c in zip(("priority", "who", "situation", "ready"),
                                                                    PRACTICE_COLUMNS)}} for n, row in practice]
    choices["installs"] = []
    for row in choices["practice"]:
        m = re.match(r"^install\b[:\s]*(.*)$", row["priority"], re.I)
        if m:
            choices["installs"] += [{"text": item, "line": row["line"]} for item in items(m[1])]
    return choices, problems


def _carry(text):
    m = CARRY.match(text)
    return int(m[1]) if m else None


def issue_label(day, revision=1):
    """A briefing's issue as the page names it: its date, and from the second issue of a day its
    revision ("October 5, 2014, revision 2")."""
    return long_date(day) + (", revision %d" % revision if revision and revision > 1 else "")


def _date(key, f, problems):
    """{date, revision} of the briefing he answers: its date, and its revision when the day had more
    than one issue (an unnumbered date is the day's first)."""
    m = DATE.match(f.text)
    if not m:
        problems.append("%s: write the briefing you answer as its status line names it, like October 5, 2014, or "
                        "October 5, 2014, revision 2 for a later issue that day" % where_of(key))
        return None
    from datetime import datetime
    when = datetime.strptime("%s %s %s" % (m[1].capitalize(), m[2], m[3]), "%B %d %Y").date()
    return {"date": when, "revision": int(m[4]) if m[4] else 1}


def _baseline(key, f, problems):
    week = _carry(f.text)
    if week is not None and not CARRY.match(f.text)[2].strip(" .,"):
        return {"carry": week}
    if NEW_PLAN.match(f.text):
        return {"new": True}
    problems.append("Baseline: write Carry Week N or New plan (%r)" % f.text)
    return None


def _names(text):
    """[(name, reason)] of a list of players: commas or semicolons between them, a reason in
    parentheses after a name."""
    out = []
    # Commas, semicolons and "and" separate the names; a reason in parentheses keeps its own.
    masked = re.sub(r"\([^()]*\)", lambda m: m[0].replace(",", "\0").replace(";", "\1").replace(" and ", "\2"), text)
    for item in re.split(r"[;,]|\s+and\s+", masked):
        item = item.replace("\0", ",").replace("\1", ";").replace("\2", " and ")
        item = item.strip()
        if not item:
            continue
        m = re.match(r"^(.*?)\s*\((.*)\)\s*$", item)
        out.append((m[1].strip(), m[2].strip()) if m else (item, ""))
    return out


def _inactives(key, f, problems):
    text = f.text
    week = _carry(text)
    if week is not None:
        return {"same_as": week}
    if NONE.match(text) or NO_CHANGE.match(text):
        problems.append("Inactives: write Standing rule, Standing rule with the others you name, the players by "
                        "name, or Carry Week N")
        return None
    standing = text.lower().startswith(STANDING.lower())
    rest = text[len(STANDING):] if standing else text
    rest = re.sub(r"^[\s,;:.]*(?:with|and|plus|also|naming)?\b[\s,;:]*", "", rest, flags=re.I) if standing else rest
    named = _names(rest)
    value = {"players": [n for n, _ in named], "reasons": {n: r for n, r in named if r}}
    return dict({"standing": True}, **value) if standing else value


def _depth(key, f, problems):
    if NONE.match(f.text) or NO_CHANGE.match(f.text):
        return "none"
    orders, roles = {}, {}
    for item in items(f.text):
        label, _, rest = item.partition(":")
        label, rest = label.strip(), rest.strip().rstrip(".")
        group = re.match(r"^(.*?)\s+order$", label, re.I)
        if group and (group[1] in GROUPS or group[1] in GROUPS.values()):
            orders[GROUPS.get(group[1], group[1])] = listed(rest)
        elif label in ROLES and rest:
            roles[ROLES[label]] = rest
        else:
            problems.append("Depth/role changes: %r is not a change the chart takes; write No change, None, a role "
                            "and its player (%s: name) or a group's new order (Wide receivers order: names), "
                            "separated by semicolons" % (item, ", ".join(ROLES)))
    return {"orders": orders, "roles": roles}


def _caller(key, f, problems):
    if NO_CHANGE.match(f.text):
        return {"no_change": True}
    return {"name": f.text.rstrip(".")}


def _opening(key, f, problems):
    week = _carry(f.text)
    if week is not None:
        return {"carry": week}
    if NO_CHANGE.match(f.text):
        return {"no_change": True}
    if NONE.match(f.text):
        return "none"
    return {"items": items(f.text)}


def _situational(key, f, problems):
    week = _carry(f.text)
    return {"carry": week, "text": f.text} if week is not None else {"text": f.text}


SPECIAL = re.compile(r"^(.*?):\s*(keep|remove|practice only)\b[\s,.;:-]*(.*)$", re.I)


def _special(key, f, problems):
    if NONE.match(f.text) or NO_CHANGE.match(f.text) or _carry(f.text) is not None:
        return "no_change"
    out = []
    for item in items(f.text):
        m = SPECIAL.match(item)
        if not m:
            problems.append("Special plays: write each as the call, then Keep, Remove or Practice only (%r)" % item)
            continue
        out.append({"call": m[1].strip(), "status": m[2].lower(), "reason": m[3].strip()})
    return out


def _removals(key, f, problems):
    if NONE.match(f.text) or NO_CHANGE.match(f.text):
        return []
    out = []
    for item in items(f.text):
        m = re.match(r"^(.*?)\s*\((.*)\)\s*$", item)
        out.append({"call": (m[1] if m else item).strip().rstrip("."), "reason": m[2].strip() if m else ""})
    return out


def _rush(key, f, problems):
    week = _carry(f.text)
    if week is not None:
        return {"carry": week}
    if NO_CHANGE.match(f.text):
        return {"no_change": True}
    if rush_words(f.text) not in RUSH_WORDS:
        problems.append("Defense, Rush rule: %r is not the active defensive playbook's rush rule; write '%s'"
                        % (f.text, RUSH_CHOICE))
        return None
    return {"text": f.text, "line": f.line}


def _decision(key, f, problems):
    text = f.text
    if text.lower().rstrip(".") == STANDING.lower():
        return {"standing": True}
    week = _carry(text)
    if week is not None:
        return {"same_as": week}
    if NO_CHANGE.match(text):
        return {"no_change": True}
    if NONE.match(text):
        return "none"
    m = MY_RULES.match(text)
    if m:
        words = {v.lower(): k for k, v in list(DECISION_WORDS[key].items()) + list(OTHERWISE_WORDS.items())}
        if m[1].strip().lower() not in words:
            problems.append("%s: otherwise %r is not one of %s" % (where_of(key), m[1], ", ".join(
                list(DECISION_WORDS[key].values()) + list(OTHERWISE_WORDS.values()))))
            return None
        return {"rules": [], "otherwise": words[m[1].strip().lower()]}
    problems.append("%s: write Standing rule, Carry Week N, No change, None%s or My rules, otherwise ... above a "
                    "rule table (%r)" % (where_of(key), " (your live call on each)" if key == "fourth_down" else "",
                                         text))
    return None


READERS = {"briefing": _date, "baseline": _baseline, "inactives": _inactives, "depth": _depth,
           "caller": _caller, "opening": _opening, "situational": _situational, "special": _special,
           "removals": _removals, "rush": _rush, "decision": _decision}


def _call_row(n, row, problems):
    text = row[CALL_COLUMNS[0]]
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", text)
    name, variations, without = (m[1].strip(), [], []) if m else (text.strip(), [], [])
    if m:
        for part in listed(m[2]):
            w = re.match(r"^without\s+(.+)$", part, re.I)
            (without if w else variations).append(w[1].strip() if w else part)
    menus, words = [], listed(row[CALL_COLUMNS[1]])
    for phrase in words:
        key, problem = situation_key(phrase)
        if problem:
            problems.append("Offense, Primary calls, %s: %s" % (name or "a row", problem))
        elif key not in menus:
            menus.append(key)
    if not name:
        problems.append("Offense, Primary calls: a row (line %d) names no call" % n)
    if not words:
        problems.append("Offense, Primary calls, %s: say when you want it (%s)" % (name, ", ".join(SITUATION_WORDS)))
    return {"line": n, "cell": text, "name": name, "variations": variations, "without": without, "menus": menus,
            "reason": row[CALL_COLUMNS[2]], "condition": row[CALL_COLUMNS[3]]}


def _response_row(n, row, problems):
    first, response = row[RESPONSE_COLUMNS[0]], row[RESPONSE_COLUMNS[1]]
    kind, menu = response_kind(first)
    call, found = response_call(response)
    problems += ["Defense, %s: %s" % (first or "a row", p) for p in found]
    if not first:
        problems.append("Defense, prepared responses: a row (line %d) names no situation or presentation" % n)
    if kind == "situation" and not call:
        problems.append("Defense, %s: a situation's row needs its prepared front, coverage or pressure" % first)
    return {"line": n, "first": first, "response": response, "kind": kind, "menu": menu, "call": call,
            "reason": row[RESPONSE_COLUMNS[2]], "counter": row[RESPONSE_COLUMNS[3]]}


# ---------------------------------------------------------------- writing a page
GUIDE = {
    "header": "Under each heading, answer every line. No change keeps the last legal instruction set; None means "
              "intentionally nothing; a line left empty is unanswered, and nothing is set for the game until every "
              "line is answered. Baseline: Carry Week N starts from that week's calls and defensive responses as "
              "set; New plan starts from none.",
}


def render(title, facts, answers=None):
    """A Game Plan page: ``facts`` the builder's lines (head_coach, game, briefing and the guide line of
    each section, ``guides``); ``answers`` maps a line's key to its text and each table's name to its
    rows (lists of cells), and a decision key with "My rules" to its rule rows under ``rules``.
    ``render(title, facts)`` is the blank page."""
    answers = answers or {}
    guides = facts.get("guides") or {}
    out = ["# " + title, ""]
    if facts.get("intro"):
        out += ["> " + facts["intro"], ""]

    def value(key):
        if key in answers:
            return answers[key]
        if key in ("head_coach", "game", "briefing"):
            return facts.get(key, "")
        return ""

    def lines(keys):
        rows = []
        for key in keys:
            label = facts.get("contingency_label", CONTINGENCY_LABEL) if key == "contingency" else FIELD[key][1]
            rows.append(("**%s:** %s" % (label, value(key))).rstrip())
        return [r + "  " for r in rows[:-1]] + rows[-1:]

    def rule_table(key):
        rows = (answers.get("rules") or {}).get(key)
        if not rows:
            return []
        columns = [c for c, _ in RULE_COLUMNS[key]]
        return [""] + table(columns, rows)

    out += lines(("head_coach", "game", "briefing", "baseline")) + [""]
    if guides.get("header", GUIDE["header"]):
        out += ["> " + guides.get("header", GUIDE["header"]), ""]
    for n, name in enumerate(HEADINGS, 1):
        out += ["## " + name, ""]
        if guides.get(n):
            out += ["> " + guides[n], ""]
        keys = [k for k, s, _, _ in FIELDS if s == n]
        if n == 3:
            top = [k for k in keys if k not in SITUATIONAL_KEYS]
            out += lines(top) + ["", "### " + CALLS_SUB, ""]
            if guides.get("calls"):
                out += ["> " + guides["calls"], ""]
            out += table(CALL_COLUMNS, answers.get("calls") or []) + ["", "### " + SITUATIONS_SUB, ""]
            if guides.get("situations"):
                out += ["> " + guides["situations"], ""]
            out += lines(SITUATIONAL_KEYS) + [""]
        elif n == 4:
            before = [k for k in keys if k != "matchups"]
            out += lines(before) + [""]
            if guides.get("responses"):
                out += ["> " + guides["responses"], ""]
            out += table(RESPONSE_COLUMNS, answers.get("responses") or []) + [""] + lines(["matchups"]) + [""]
        elif n == 5:
            for key in keys:
                out += lines([key]) + rule_table(key) + [""]
        elif n == 6:
            out += table(PRACTICE_COLUMNS, answers.get("practice") or []) + [""] + lines(keys) + [""]
        else:
            out += lines(keys) + [""]
    return "\n".join(out).rstrip("\n") + "\n"


def blank(title, facts):
    """A blank Game Plan: every heading and line, the builder's facts and guide lines, empty tables."""
    return render(title, facts)


# ---------------------------------------------------------------- the frame
def frame_from_sheet(sheet):
    """The frame of a sheet frozen before version 2 (the Week 5 proof): its record fields that are not
    football choices and that version 2 keeps out of the sheet or derives itself: the event, when and
    from what it was frozen; the situation prose, the notes and each call's 'what I am looking at'
    text (author text, which a version 2 page keeps as intent, never in the sheet); and the defensive
    sheet's packet, notes, rush-rule citation, practiced menu and each row's id and packet citation (a
    version 2 page derives the ids and the practiced menu and cites its own lines)."""
    frame = {"top": {k: sheet[k] for k in TOP_KEYS if k in sheet},
             "record_text": {k: copy.deepcopy(sheet[k]) for k in ("menus", "notes") if k in sheet},
             "looking": {c["name"]: c["what_stone_is_looking_at"] for c in sheet.get("offensive_call_sheet") or ()
                         if isinstance(c, dict) and "what_stone_is_looking_at" in c},
             "decisions": {}, "defense": None}
    for kind, block in (sheet.get("decisions") or {}).items():
        frame["decisions"][kind] = {"id": block.get("id"), "source": block.get("source"),
                                    "rules": [{"id": r.get("id"), "source": r.get("source")}
                                              for r in block.get("rules") or ()]}
    ds = sheet.get("defensive_call_sheet")
    if ds is not None:
        frame["defense"] = {"head": {k: ds[k] for k in ("schema_version", "team", "book", "packet") if k in ds},
                            "notes": copy.deepcopy(ds.get("notes")) if "notes" in ds else None,
                            "rush": copy.deepcopy(ds["rush_rule"]["source"]),
                            "practiced": copy.deepcopy(ds.get("practiced")),
                            "rows": [{"id": r["id"], "source": copy.deepcopy(r["source"])} for r in ds.get("rows") or ()]}
    return frame


def page_frame(page_rel, event, frozen, provenance, team, book, week):
    """The frame a version 2 Game Plan writes when it is applied: its own decision blocks named for the
    week, and its defensive record citing the page's own lines."""
    return {"top": {"schema_version": 1, "team": team, "event": event, "status": STATUS, "frozen": frozen,
                    "provenance": provenance},
            "record_text": {}, "looking": {},
            "decisions": {kind: {"id": "stone-%s-game-plan-week-%d" % (kind.replace("_", "-"), week),
                                 "source": "Stone's Week %d Game Plan, %s" % (week, section)}
                          for section, kind in DECISION_SECTIONS.items()},
            "defense": {"head": {"schema_version": 1, "team": team, "book": book, "packet": page_rel},
                        "page": page_rel}}


# ---------------------------------------------------------------- the compiler
def tokens(text):
    return norm(text).split()


def _subsequence(short, long_):
    it = iter(long_)
    return all(any(t == u for u in it) for t in short)


def match_calls(text, names):
    """The name a call written as ``text`` stands for: only its exact name (its words, marks and case
    aside). A shorter or partial name never resolves to a longer call, which would add a route, a tag
    or a protection he did not write (docs/game_week_v2.md, section 4.5); ``near_calls`` names the
    calls it might mean, for the check to ask."""
    want = tokens(text)
    if not want:
        return []
    return [n for n in names if tokens(n) == want][:1]


def near_calls(text, names):
    """The calls whose words hold every word of ``text`` in order, the exact name aside: what a short
    or partial name might mean, for the check to ask (never to resolve)."""
    want = tokens(text)
    if not want:
        return []
    return [n for n in names if tokens(n) != want and _subsequence(want, tokens(n))]


def did_you_mean(text, near):
    return " or ".join(near) if near else ""


def base_tags(tags):
    return [t for t in tags or () if t not in DERIVED_TAGS]


def form_of(call):
    return {k: copy.deepcopy(call[k]) for k in FORM_KEYS if call.get(k) is not None}


def new_call_form(name):
    """(form, problem) of a call no earlier sheet carries, read from its name: the grouping and
    formation before the first comma, then the concept (with its direction) and the protection."""
    from . import call_families, offensive_words
    parts = [p.strip() for p in name.split(",")]
    if len(parts) < 2 or len(parts) > 3:
        return None, ("%r is not on any earlier Jacksonville call sheet; write a new call as its formation, concept "
                      "and protection, for example 11 Trips, Smash, HALF" % name)
    formation = parts[0]
    personnel = formation.split()[0] if formation.split() and formation.split()[0].upper() in \
        offensive_words.PERSONNEL else None
    concept = re.sub(r"\s+(Right|Left|R|L)$", "", parts[1])
    family, entry = call_families.family_entry(concept)
    if family is None:
        book = offensive_words.concept(concept)
        return None, ("%r: %s is a play the book gives no receiver or carrier for; it needs the staff's prepared "
                      "card before it is called" % (name, book) if book else
                      "%r: %r is not a concept of the active playbook" % (name, concept))
    kind = "mixed" if "carrier" in entry and "target" in entry else "run" if "carrier" in entry else "pass"
    form = {"family": family, "type": kind}
    if personnel:
        form["personnel"] = personnel
    form["formation"] = formation
    if len(parts) == 3:
        if parts[2].lower() not in {p.lower() for p in offensive_words.PROTECTIONS}:
            return None, "%r: %r is not a protection of the active playbook (%s)" % (
                name, parts[2], ", ".join(offensive_words.PROTECTIONS))
        form["protection"] = next(p for p in offensive_words.PROTECTIONS if p.lower() == parts[2].lower())
    return form, None


def earlier_forms(earlier, baseline=None):
    """{call name: (form with tags and menus, week, index)}: every call of the earlier frozen sheets,
    the latest week's form of each, and the baseline week's ahead of any other."""
    forms = {}
    order = sorted(earlier) + ([baseline] if baseline in earlier else [])
    for week in order:
        for i, call in enumerate(earlier[week].get("offensive_call_sheet") or ()):
            if isinstance(call, dict) and call.get("name"):
                forms[call["name"]] = (call, week, i)
    return forms


def earlier_tags(earlier):
    return {t for sheet in earlier.values() for c in sheet.get("offensive_call_sheet") or () if isinstance(c, dict)
            for t in c.get("tags") or ()}


def earlier_practiced(earlier):
    out = {}
    for sheet in earlier.values():
        practiced = (sheet.get("defensive_call_sheet") or {}).get("practiced") or {}
        for key in PRACTICED_KEYS:
            out.setdefault(key, set()).update(practiced.get(key) or ())
    return out


SPECIAL_TAG = "special play"


def is_special(name, forms, named=()):
    """Whether a call is a special play: its frozen form is tagged one, its concept is one of the
    active book's special plays and gadgets (runtime/offensive_words.BOOK_PLAYS), or the page names it
    under Special plays."""
    from . import offensive_words
    call = (forms.get(name) or ({},))[0]
    plays = {norm(p) for p in offensive_words.BOOK_PLAYS}
    return SPECIAL_TAG in (call.get("tags") or ()) or norm(call.get("family")) in plays or norm(name) in named


def special_situations(name, earlier):
    """The situations a carried call has been set for on the earlier frozen sheets (the opening
    sequence aside): a special play's installed situations."""
    out = set()
    for sheet in earlier.values():
        for call in sheet.get("offensive_call_sheet") or ():
            if isinstance(call, dict) and call.get("name") == name:
                out.update(m for m in cs.menu_keys(call.get("menus")) if m != cs.OPENING)
    return out


def situations_in(text):
    """The situations a phrase names in the page's words ("third and long and backed up", "goal line,
    two-minute"), or None when any part of it is not one."""
    forms = {}
    for words in SITUATION_WORDS + tuple(SITUATION_TEXT.values()):
        key, problem = situation_key(words)
        if key and not problem:
            forms[tuple(norm(words).split())] = key
    words, out, i = norm(text).split(), [], 0
    while i < len(words):
        if words[i] in ("and", "or"):
            i += 1
            continue
        for n in range(len(words) - i, 0, -1):
            key = forms.get(tuple(words[i:i + n]))
            if key:
                out.append(key)
                i += n
                break
        else:
            return None
    return out or None


def situation_list(keys):
    """Situations in the page's words, in the call sheet's order: "third and long and backed up"."""
    words = dict(zip((situation_key(w)[0] for w in SITUATION_WORDS), SITUATION_WORDS))
    names = [words.get(k, SITUATION_TEXT.get(k, k)) for k in SITUATION_TEXT if k in set(keys)]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1] if names else ""


def latest(earlier, test=lambda sheet: True):
    weeks = [w for w in sorted(earlier) if test(earlier[w])]
    return weeks[-1] if weeks else None


def compile_sheet(choices, frame, earlier, standing=None, arrangement=None):
    """(sheet, source map, problems): the call sheet the page compiles to, from its choices, the frame
    (``page_frame`` or, for the Week 5 proof, ``frame_from_sheet``), the earlier frozen Jacksonville
    sheets ({week: sheet}), the standing decision blocks ({kind: block}) and the calling arrangement
    on file ({"defense": caller's name}, which "No change" on a caller line means). Every problem is
    in football words; with any problem the sheet is None."""
    standing = standing or {}
    problems, source = [], {"calls": {}, "defense": {}, "decisions": {}}
    baseline = (choices.get("baseline") or {}).get("carry")
    if baseline is not None and baseline not in earlier:
        problems.append("Baseline: Week %d has no call sheet as set to carry" % baseline)
        baseline = None
    base = earlier.get(baseline) if baseline is not None else None
    forms = earlier_forms(earlier, baseline)
    installs = {norm(i["text"]): i for i in choices.get("installs") or ()}
    known_tags = earlier_tags(earlier)
    used = []          # the installs the sheet relies on, each confirmed taught before it is set

    def rely(item):
        if item not in used:
            used.append(item)

    # A special play's installed situations: those its frozen entries have set on an earlier sheet. An
    # install line may add one ("Install 12 Ace, Flea Flicker, MAX on third and long").
    situational = {}
    for item in choices.get("installs") or ():
        for m in re.finditer(r"\s(?:on|for)\s", item["text"], re.I):
            keys = situations_in(item["text"][m.end():])
            if keys:
                situational.setdefault(norm(item["text"][:m.start()]), {"situations": set(), "item": item})[
                    "situations"].update(keys)
                break
    special_named = {norm(i["call"]) for i in choices.get("special_plays") or () if isinstance(i, dict)}

    # The calls on the sheet: the baseline's, then the table's.
    calls, order = {}, []
    for i, call in enumerate((base or {}).get("offensive_call_sheet") or ()):
        entry = {"name": call["name"], "form": form_of(call), "tags": base_tags(call.get("tags")),
                 "menus": [cs.menu_key(m) for m in call.get("menus") or () if cs.menu_key(m) != cs.OPENING],
                 "from": [{"carried": {"week": baseline, "call": i}}]}
        calls[call["name"]] = entry
    carried_order = list(calls)
    table_order = []
    for row in choices.get("calls") or ():
        if not row["name"]:
            continue
        found = match_calls(row["name"], list(forms))
        if found:
            name = found[0]
            call, w, idx = forms[name]
            entry = calls.get(name) or {"name": name, "form": form_of(call), "tags": base_tags(call.get("tags")),
                                        "from": [{"carried": {"week": w, "call": idx}}]}
        else:
            near = near_calls(row["name"], list(forms))
            if near and norm(row["name"]) not in installs:
                # A short or partial name is asked about, never resolved to a longer call.
                problems.append("Offense, Primary calls: %s is not a call of an earlier Jacksonville sheet as written; "
                                "did you mean %s? Write the call's full name, or, for a new call, name it as this "
                                "week's install in What we will practice (Install %s)"
                                % (row["name"], did_you_mean(row["name"], near), row["name"]))
                continue
            form, problem = new_call_form(row["name"])
            if problem:
                problems.append("Offense, Primary calls: %s" % problem)
                continue
            name = row["name"]
            if norm(name) not in installs:
                problems.append("Offense, Primary calls: %s is not on an earlier Jacksonville call sheet; name it as "
                                "this week's install in What we will practice (Install %s)" % (name, name))
            else:
                rely(installs[norm(name)])
            entry = {"name": name, "form": form, "tags": [], "from": [], "new": True}
        if name in table_order:
            problems.append("Offense, Primary calls: %s is written twice" % name)
            continue
        entry = dict(entry, menus=list(row["menus"]))
        if not entry.get("new") and is_special(name, forms, special_named):
            installed = special_situations(name, earlier)
            extra = situational.get(norm(name)) or {}
            new = [m for m in row["menus"] if m not in installed]
            missing = [m for m in new if m not in extra.get("situations", ())]
            if missing:
                problems.append("Offense, Primary calls, %s: it is a special play installed for %s; %s %s not among "
                                "its installed situations. Choose an installed situation, or name the install in "
                                "What we will practice (Install %s on %s)" % (
                                    name, situation_list(installed) or "no situation yet",
                                    situation_list(missing), "is" if len(missing) == 1 else "are", name,
                                    situation_list(missing)))
            elif new:
                rely(extra["item"])
        for tag in row["without"]:
            if tag not in entry["tags"]:
                problems.append("Offense, Primary calls, %s: it carries no %s to take off" % (name, tag))
            entry["tags"] = [t for t in entry["tags"] if t != tag]
        for tag in row["variations"]:
            if tag not in known_tags and norm(tag) not in installs:
                problems.append("Offense, Primary calls, %s: %s is a new variation; name it as this week's install "
                                "in What we will practice (Install %s)" % (name, tag, tag))
            elif tag not in known_tags:
                rely(installs[norm(tag)])
            if tag not in entry["tags"]:
                entry["tags"].append(tag)
        entry["from"] = list(entry["from"]) + [{"page": row["line"], "text": row["cell"]}]
        calls[name] = entry
        table_order.append(name)

    def on_sheet(text, where):
        found = match_calls(text, list(calls))
        if found:
            return found[0]
        near = near_calls(text, list(calls))
        problems.append("%s: %s %s" % (where, text, "is not a call on this week's sheet as written; did you mean %s? "
                                       "Write the call's full name" % did_you_mean(text, near) if near
                                       else "is not a call on this week's sheet"))
        return None

    removed, kept = {}, set()
    special = choices.get("special_plays")
    for item in special if isinstance(special, list) else ():
        name = on_sheet(item["call"], "Offense, Special plays")
        if name and item["status"] in ("remove", "practice only"):
            removed[name] = item["status"]
        elif name:
            kept.add(name)
    for item in choices.get("not_available") or ():
        name = on_sheet(item["call"], "Offense, Calls not available this week")
        if name:
            if name in table_order:
                problems.append("Offense: %s is in the Primary calls table and among the calls not available; take "
                                "it out of one" % name)
            if name in kept:
                problems.append("Offense: %s is kept under Special plays and listed among the calls not available "
                                "this week; take it out of one" % name)
            removed[name] = "not available"
    for name in removed:
        calls.pop(name, None)

    # The opening sequence.
    positions = {}
    opening = choices.get("opening")
    if isinstance(opening, dict) and ("carry" in opening or opening.get("no_change")):
        week_ = opening.get("carry") if "carry" in opening else latest(
            earlier, lambda s: any(isinstance(c, dict) and c.get("opener") for c in s.get("offensive_call_sheet") or ()))
        if week_ not in earlier:
            problems.append("Offense, Opening calls: Week %s has no opening calls as set to carry" % week_)
        else:
            slots = sorted((int(s), call["name"]) for call in earlier[week_].get("offensive_call_sheet") or ()
                           for s in ([call["opener"]] if call.get("opener") is not None else [])
                           + list(call.get("opener_returns") or ()))
            dropped = []
            for _, name in slots:
                if name not in calls and name not in removed and name not in dropped:
                    problems.append("Offense, Opening calls: Week %d's opening calls include %s, which is not on this "
                                    "week's sheet; give the opening calls in order" % (week_, name))
                if name not in calls and name not in dropped:
                    dropped.append(name)
            # A call this page takes off leaves the carried opening: the calls after it move up in order.
            remaining = [name for _, name in slots if name in calls]
            renumber = bool(dropped)
            for n, (slot, name) in enumerate([(s, c) for s, c in slots if c in calls], 1):
                positions.setdefault(name, []).append(n if renumber else slot)
            for name in dict.fromkeys(remaining):
                calls[name]["from"].append({"opening": {"week": week_}})
            if dropped:
                source["opening_dropped"] = [n for n in dropped if n in removed]
    elif isinstance(opening, dict):
        line = choices["fields"]["opening"]["line"]
        for n, text in enumerate(opening["items"], 1):
            name = on_sheet(text, "Offense, Opening calls, number %d" % n)
            if name:
                positions.setdefault(name, []).append(n)
        for name in positions:
            calls[name]["from"].append({"opening": {"page": line}})

    # The order: the opening calls in order, then the table's, then the baseline's.
    first = sorted(positions, key=lambda n: positions[n][0])
    order = first + [n for n in table_order if n in calls and n not in first] + \
        [n for n in carried_order if n in calls and n not in first and n not in table_order]
    emitted = []
    for name in order:
        entry = calls[name]
        menus = [m for m in entry["menus"] if m != cs.OPENING]
        unknown = [m for m in menus if m not in SITUATION_TEXT]
        if unknown:
            problems.append("Offense: %s carries the situation %s, which the sheet no longer takes; give its "
                            "situations in the Primary calls table" % (name, ", ".join(unknown)))
            continue
        slots = positions.get(name)
        if slots and cs.NORMAL not in menus:
            menus = [cs.OPENING] + menus
        if not menus:
            problems.append("Offense: %s has no situation once it is off the opening calls; give its situations in "
                            "the Primary calls table or take it off" % name)
            continue
        tags = ([OPENER_TAG] if slots else []) + base_tags(entry["tags"]) + \
            ([TWO_POINT_TAG] if cs.TWO_POINT in menus else [])
        call = {"name": name}
        call.update({k: copy.deepcopy(entry["form"][k]) for k in FORM_KEYS if k in entry["form"]})
        call["tags"] = tags
        if slots:
            call["opener"] = slots[0]
            if slots[1:]:
                call["opener_returns"] = slots[1:]
        call["menus"] = [SITUATION_TEXT[m] for m in menus]
        if name in (frame.get("looking") or {}):
            call["what_stone_is_looking_at"] = frame["looking"][name]
        emitted.append({k: call[k] for k in CALL_KEYS if k in call})
        source["calls"][name] = entry["from"]

    # The decisions.
    decisions = {}
    for kind in ("two_point", "kickoff", "fourth_down"):
        entry = choices.get(kind)
        if isinstance(entry, dict) and entry.get("standing"):
            if kind in standing:
                decisions[kind] = copy.deepcopy(standing[kind])
                source["decisions"][kind] = {"standing": True}
        elif isinstance(entry, dict) and ("same_as" in entry or entry.get("no_change")):
            week_ = entry.get("same_as") if "same_as" in entry else latest(earlier)
            if week_ in earlier and kind in (earlier[week_].get("decisions") or {}):
                decisions[kind] = copy.deepcopy(earlier[week_]["decisions"][kind])
                source["decisions"][kind] = {"carried": {"week": week_}}
        elif isinstance(entry, dict) and entry.get("rules") is not None:
            names = (frame.get("decisions") or {}).get(kind) or {}
            block = {k: names[k] for k in ("id", "source") if names.get(k) is not None}
            rule_names = names.get("rules") or []
            block["rules"] = []
            for i, rule in enumerate(entry["rules"]):
                named = rule_names[i] if i < len(rule_names) else {}
                block["rules"].append({**{k: named[k] for k in ("id", "source") if named.get(k) is not None}, **rule})
            block["otherwise"] = entry["otherwise"]
            decisions[kind] = block
            source["decisions"][kind] = {"page": choices["fields"][kind]["line"]}

    defense = _compile_defense(choices, frame, earlier, base, baseline, installs, problems, source,
                               (arrangement or {}).get("defense"), rely)
    # The installs the sheet relies on (a new call, a new variation, a defensive word off the practiced
    # menu, a special play's new situation), each confirmed taught in the practice week before the plan
    # is set for the game (scripts/apply_game_plan.py).
    source["installs"] = [{"text": i["text"], "line": i["line"]} for i in used]
    sheet = dict(frame["top"])
    for key in ("menus", "notes"):
        if key in (frame.get("record_text") or {}):
            sheet[key] = copy.deepcopy(frame["record_text"][key])
    sheet["offensive_call_sheet"] = emitted
    if decisions:
        sheet["decisions"] = {k: decisions[k] for k in ("two_point", "kickoff", "fourth_down") if k in decisions}
    if defense is not None:
        sheet["defensive_call_sheet"] = defense
    if not emitted and not problems:
        problems.append("Offense: no call is on the sheet; carry a week or write the Primary calls")
    return (None if problems else sheet), source, problems


def _caller_name(choices, key, arrangement=None):
    value = choices.get(key)
    if isinstance(value, dict) and value.get("no_change"):
        return arrangement
    return value.get("name") if isinstance(value, dict) else None


def _compile_defense(choices, frame, earlier, base, baseline, installs, problems, source, arranged=None,
                     rely=lambda item: None):
    fd = frame.get("defense") or {}
    page = fd.get("page")
    rows_in = choices.get("responses") or []
    caller = _caller_name(choices, "defense_caller", arranged)
    rush = choices.get("rush")
    carried = None
    if isinstance(rush, dict) and ("carry" in rush or rush.get("no_change")):
        week_ = rush.get("carry") if "carry" in rush else latest(earlier, lambda s: "defensive_call_sheet" in s)
        carried = (earlier.get(week_) or {}).get("defensive_call_sheet")
        if carried is None:
            problems.append("Defense, Rush rule: Week %s set no defensive sheet to carry" % week_)
    from .defensive_calls import RUSH_RULE
    if not rows_in:
        if base is None or "defensive_call_sheet" not in base:
            problems.append("Defense: write the prepared responses (or carry a week that set them)")
            return None
        out = copy.deepcopy(base["defensive_call_sheet"])
        # The rows keep their inherited citations (the source map records the carry); the record is this
        # page's, with no earlier week's freeze notes.
        if (fd.get("head") or {}).get("packet"):
            out["packet"] = fd["head"]["packet"]
        out["notes"] = ["Carried from Week %d as set: its prepared responses, their citations and the practiced "
                        "menu." % baseline]
        if caller:
            out["caller"] = caller
        if isinstance(rush, dict) and rush.get("text"):
            out["rush_rule"] = {"rule": RUSH_RULE, "source": {"path": page, "line": rush["line"], "text": rush["text"]}}
        elif carried is not None:
            out["rush_rule"] = copy.deepcopy(carried["rush_rule"])
        source["defense"] = {"carried": {"week": baseline}}
        return {k: out[k] for k in DEFENSE_KEYS if k in out}
    known = earlier_practiced(earlier)
    taught = {}
    for item in choices.get("installs") or ():
        call, _ = response_call(norm(item["text"]))
        for word in response_words(call or {}):
            taught.setdefault(word, item)
    fixed_rows = fd.get("rows")
    if fixed_rows is not None and len(fixed_rows) != len(rows_in):
        problems.append("Defense: the frozen sheet has %d rows and the page %d" % (len(fixed_rows), len(rows_in)))
        return None
    rows, seen, practiced = [], set(), {k: [] for k in PRACTICED_KEYS}
    practiced_sources = []
    for i, r in enumerate(rows_in):
        call = r["call"]
        for key, word in response_words(call or {}):
            if word not in known.get(key, set()) and (key, word) not in taught:
                problems.append("Defense, %s: %s has not been practiced on an earlier Jacksonville sheet; name it as "
                                "this week's install in What we will practice" % (r["first"], word))
            elif word not in known.get(key, set()):
                rely(taught[(key, word)])
            if word not in practiced[key]:
                practiced[key].append(word)
        text = r["response"] or r["first"]
        if fixed_rows is not None:
            rid, cite = fixed_rows[i]["id"], copy.deepcopy(fixed_rows[i]["source"])
        else:
            rid, cite = row_id(r["kind"], r["menu"], seen), {"path": page, "line": r["line"], "text": text}
        seen.add(rid)
        row = {"id": rid, "kind": r["kind"]}
        if r["menu"]:
            row["menu"] = r["menu"]
        if call:
            row["call"] = call
            practiced_sources.append({"path": page, "line": r["line"], "text": r["response"]})
        row["source"] = cite
        rows.append(row)
        source["defense"][rid] = {"page": r["line"], "text": r["first"] + " | " + r["response"]}
    head = fd.get("head") or {}
    out = {k: head[k] for k in ("schema_version", "team") if k in head}
    out["caller"] = caller
    out.update({k: head[k] for k in ("book", "packet") if k in head})
    if fd.get("notes") is not None:
        out["notes"] = copy.deepcopy(fd["notes"])
    if fd.get("rush") is not None:
        out["rush_rule"] = {"rule": RUSH_RULE, "source": copy.deepcopy(fd["rush"])}
    elif isinstance(rush, dict) and rush.get("text"):
        out["rush_rule"] = {"rule": RUSH_RULE, "source": {"path": page, "line": rush["line"], "text": rush["text"]}}
    elif carried is not None:
        out["rush_rule"] = copy.deepcopy(carried["rush_rule"])
    if fd.get("practiced") is not None:
        out["practiced"] = copy.deepcopy(fd["practiced"])
    else:
        out["practiced"] = {k: practiced[k] for k in PRACTICED_KEYS}
        out["practiced"]["sources"] = practiced_sources
    out["rows"] = rows
    return {k: out[k] for k in DEFENSE_KEYS if k in out}


# ---------------------------------------------------------------- intent and the source map
INTENT_KINDS = ("fact", "intent", "situational")


def intent(choices):
    """The page's author intent, as the applied record keeps it: every line that never compiles, each
    call's reason and stop condition, each defensive row's reason and counter and the practice table,
    each with its page line."""
    fields = choices.get("fields") or {}
    out = {"lines": {key: fields[key] for key, _, _, kind in FIELDS if kind in INTENT_KINDS and key in fields},
           "calls": [{"line": r["line"], "call": r["name"], "reason": r["reason"], "condition": r["condition"]}
                     for r in choices.get("calls") or ()],
           "responses": [{"line": r["line"], "reason": r["reason"], "counter": r["counter"]}
                         for r in choices.get("responses") or ()],
           "practice": list(choices.get("practice") or ())}
    for key in ("special_plays", "not_available"):
        value = choices.get(key)
        if isinstance(value, list):
            out[key] = [{"call": v["call"], "reason": v.get("reason", "")} for v in value]
    return out


# ---------------------------------------------------------------- the standing fourth-down rule's calls
# A standing fourth-down rule that names "Tice's first call on the matching menu" says so on its
# instruction (``prepared_calls``); the calls are the week's, so they are filled from its sheet.
FIRST_ON_MENU = "first-call-on-each-matching-menu"


def first_calls(calls):
    """{menu: call name}: for each menu a fourth down can match (runtime/fourth_down.py's prepared
    menus), the first call of the sheet, in sheet order, that names it; the live fourth-down
    information lists a matching menu's calls in the same order (runtime/kernel.py matching_calls)."""
    menus = (cs.THIRD_SHORT, cs.THIRD_MEDIUM, cs.THIRD_LONG, cs.GOAL_LINE, cs.LOW_RED, cs.HIGH_RED,
             cs.BACKED_UP, cs.TWO_MINUTE, cs.PRESS, cs.FOUR_MINUTE, cs.NORMAL)
    out = {}
    for menu in menus:
        first = next((c["name"] for c in calls or () if str(c.get("type", "any")).lower() in ("run", "pass", "mixed", "any")
                      and menu in cs.menu_keys(c.get("menus"))), None)
        if first is not None:
            out[menu] = first
    return out


def sheet_bytes(sheet):
    """The frozen call sheet's bytes, as every frozen sheet is written (indent 1, a final newline)."""
    return (json.dumps(sheet, indent=1) + "\n").encode("utf-8")


# ---------------------------------------------------------------- the applied record
def applied_record(path):
    """The applied Game Plan record at ``path`` (runtime/decisions.WeekPages.applied), or None."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def event_line(record):
    """The applied plan's event-record line, which the week index carries (the record is its owner)."""
    return "<!-- event-record: %s -->" % json.dumps(record["event"], sort_keys=True)
