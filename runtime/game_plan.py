"""Stone's Game Plan page: its fixed headings, how it is read, and how it
becomes the records the game path already reads (docs/rebuild_plan.md, "How
a decision works").

The page is the head coach's own page for a game week. It has fixed headings
(``SECTIONS``) and each section begins with one line, a blockquote, naming the
legal choices. Stone fills it in place or uploads a .md or .txt file with the
same headings. Under any heading "Same as Week N" carries that week's frozen
choices exactly, and "None" means no change (or nothing to add).

Three functions carry the page:

- ``render`` writes a page from its choices (``blank`` with none, or
  ``choices_from_sheet`` for a frozen week's call sheet and inactives);
- ``parse`` reads a page back into its choices, with every problem of form
  named in football words;
- ``build_sheet`` turns the choices into the call sheet, exactly in the
  shape the weekly build reads (runtime/week_inputs), with its frame: the
  record's own fields that are not football choices (its event, when and from
  what it was frozen, the ids of its decision blocks and the packet lines its
  defensive rows cite). From a page, ``page_frame`` writes the frame, and
  every defensive row cites the page's own line; for a sheet frozen before
  the Game Plan existed, ``frame_from_sheet`` reads it back, which is how the
  Week 5 round trip is proved (tests/test_game_plan.py).

The game-day inactives and any depth-chart order or role change go to the
game depth chart (scripts/apply_game_plan.py writes them with their update-log
entry). Practice and special-teams instructions stay on the page, which is the
record of his decision. Nothing here reads the current-job record or the
decision queue (tests/test_career_layer_isolation.py); the scripts that check
and apply a page do.
"""
from __future__ import annotations

import json
import re

SECTIONS = ("Inactives", "Depth chart changes", "Practice", "Offense", "Fourth downs", "Two-point tries",
            "Kickoffs", "Defense", "Special teams", "Notes to the staff")
DECISION_SECTIONS = {"Fourth downs": "fourth_down", "Two-point tries": "two_point", "Kickoffs": "kickoff"}
# The call sheet's situation menus (its top-level ``menus``), in the sheet's own order; the page
# shows each in football words. The fourth-down and two-point menus sit in their own sections.
MENU_ORDER = ("opening_sequence", "normal_down", "second_and_long", "third_down", "backed_up", "fourth_down",
              "red_zone", "two_point", "two_minute", "PRESS_sequence", "four_minute", "sudden_change",
              "final_play_of_half", "empty_rule", "receiver_arrangement")
OFFENSE_MENUS = (("opening_sequence", "Opening sequence"), ("normal_down", "Normal downs"),
                 ("second_and_long", "Second and long"), ("third_down", "Third down"),
                 ("backed_up", "Backed up"), ("red_zone", "Red zone"), ("two_minute", "Two-minute"),
                 ("PRESS_sequence", "PRESS sequence"), ("four_minute", "Four-minute"),
                 ("sudden_change", "Sudden change"), ("final_play_of_half", "Final play of the half"),
                 ("empty_rule", "Empty"), ("receiver_arrangement", "Receiver arrangement"))
SECTION_MENU = {"fourth_down": "How we call it", "two_point": "Calls"}
# The situations a call may name in its Situations cell, as the page spells them (each is one of the
# call sheet's menus under runtime/call_situations.menu_key).
CALL_SITUATIONS = ("normal down", "second and long", "third and short", "third and medium", "third and long",
                   "backed up", "high red zone", "low red zone", "goal line", "red zone", "two-minute",
                   "PRESS sequence", "four-minute", "sudden change", "opening sequence", "two-point",
                   "final play of half", "empty")
CALLS = "Calls"
LOOKING = "What I am looking at"
# The call table: (column, call field). A call's fields are written in CALL_KEYS order.
CALL_COLUMNS = (("Call", "name"), ("Family", "family"), ("Type", "type"), ("Personnel", "personnel"),
                ("Formation", "formation"), ("Motion", "motion"), ("Protection", "protection"),
                ("Target", "target"), ("Carrier", "carrier"), ("Tags", "tags"), ("Opener", "opener"),
                ("Returns", "opener_returns"), ("Situations", "menus"))
CALL_KEYS = ("name", "family", "type", "personnel", "formation", "motion", "protection", "target", "carrier",
             "tags", "opener", "opener_returns", "menus", "what_stone_is_looking_at")
ALWAYS_LISTS = ("tags", "menus")
GROUP_VALUES = ("any", "unspecified")
TOP_KEYS = ("schema_version", "team", "event", "status", "frozen", "provenance")
STATUS = "EX_ANTE_CALL_SHEET_FROZEN"

# Decision rules: the columns of each kind's table, (column, when key or field).
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
QUARTERS = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", "OT": "OT"}
STANDING = "Standing rule"

# The defense: the practiced menu's lists and the row table.
PRACTICED = (("Packages", "packages"), ("Fronts", "fronts"), ("Coverages", "coverages"),
             ("Pressures", "pressures"), ("Tags", "tags"))
ROW_COLUMNS = (("Row", "id"), ("Use", "kind"), ("Situation", "menu"), ("Package", "package"),
               ("Front", "front"), ("Strength", "strength"), ("Coverage", "coverage"), ("Pressure", "pressure"),
               ("Tags", "tags"), ("As written", "text"))
CALL_FIELDS = ("package", "front", "strength", "coverage", "pressure", "tags")
KIND_WORDS = {"situation": "Situation", "presentation": "Presentation", "counter": "Counter",
              "conditional": "Conditional"}
DEF_MENU_WORDS = {"normal-down": "Normal downs", "second-and-long": "Second and long",
                  "third-and-short": "Third and short", "third-and-medium": "Third and medium",
                  "third-and-long": "Third and long", "two-point": "Two-point try", "goal-line": "Goal line",
                  "low-red-zone": "Low red zone", "high-red-zone": "High red zone", "red-zone": "Red zone",
                  "backed-up": "Backed up", "two-minute": "Two-minute", "four-minute": "Four-minute",
                  "lead-late": "Late lead"}
DEFENSE_KEYS = ("schema_version", "team", "caller", "book", "packet", "notes", "rush_rule", "practiced", "rows")
# The active defensive book has one rush rule (runtime/defensive_calls.RUSH_RULE): the page offers it
# in his own voice and accepts it in either voice; the line he writes is kept as written.
RUSH_CHOICE = "Four unless I call the five-man counter"
RUSH_WORDS = frozenset({"four unless stone calls the five man counter", "four unless i call the five man counter"})


def rush_words(text):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split())


def row_id(kind, menu, seen):
    """A defensive row's id when the page gives none: its situation for a situation row (one row
    per situation), else its use and a count ("counter-2")."""
    if kind == "situation" and menu:
        return menu
    n = 1
    while "%s-%d" % (kind, n) in seen:
        n += 1
    return "%s-%d" % (kind, n)


def derived_ids(rows):
    """The ids ``row_id`` gives a list of defensive rows, in order."""
    seen, out = set(), []
    for r in rows:
        rid = row_id(r["kind"], r.get("menu"), seen)
        seen.add(rid)
        out.append(rid)
    return out

GROUPS = {"Quarterbacks": "QB", "Running backs": "RB", "Fullback": "FB", "Wide receivers": "WR",
          "Tight ends": "TE", "Offensive line": "OL", "Defensive line": "DL", "Linebackers": "LB",
          "Defensive backs": "DB", "Kicker": "K", "Punter": "P", "Long snapper": "LS"}
ROLES = {"Starter": "passer", "Kicker": "placekicker", "Punter": "punt", "Kick returner": "kick_return",
         "Punt returner": "punt_return", "Nickel": "nickel", "Outside reserve corner": "outside_reserve"}

SAME = re.compile(r"^same as week (\d{1,2})\.?$", re.I)
NONE = re.compile(r"^none\.?$", re.I)
# A labelled line, bold as the page writes it ("**Rush rule:** ...") or plain ("Rush rule: ...").
LABELLED = re.compile(r"^(?:\*\*([^*]+?):\*\*|([A-Z][A-Za-z' -]*?):(?!\S))\s*(.*)$")
# The sections that hold subsections of their own; under any other heading a "###" subheading is
# a problem of form (the readers read the section's own lines only).
WITH_SUBSECTIONS = ("Offense", "Defense")
LOOK = re.compile(r"^[-*]\s+\*\*(.+?):\*\*\s*(.*)$")
BULLET = re.compile(r"^[-*]\s+(.*)$")


def labelled(text):
    """(label, value) of a labelled line, bold or plain, or None."""
    m = LABELLED.match(text)
    if not m:
        return None
    return (m[1] if m[1] is not None else m[2]).strip(), m[3]


class Section:
    """One section of the page: its content lines (line number, text) without blank lines and
    the one-line explanation, and its subsections."""

    def __init__(self, name, line):
        self.name, self.line, self.lines, self.subs, self.sub_lines = name, line, [], {}, {}

    def written(self):
        """What is written in the section: its lines and its subsections' lines, without the
        empty tables a blank page carries (a header and its rule, no row)."""
        return data_lines(self.lines) + [t for sub in self.subs.values() for t in data_lines(sub)]

    def same_as(self):
        lines = self.written()
        if len(lines) == 1 and SAME.match(lines[0]):
            return int(SAME.match(lines[0])[1])
        return None

    def none(self):
        lines = self.written()
        return len(lines) == 1 and bool(NONE.match(lines[0]))

    def empty(self):
        return not self.written()


def data_lines(lines):
    """The texts of ``lines`` without a table that has no row (its header and rule only)."""
    out, group = [], []
    for _, text in list(lines) + [(None, "")]:
        if text.startswith("|"):
            group.append(text)
            continue
        if group:
            rows = [g for g in group[1:] if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells(g) if c)]
            if rows:
                out += group
            group = []
        if text and not _empty_label(text):
            out.append(text)
    return out


def _empty_label(text):
    """A label line the blank page carries with nothing after it ("**Rush rule:**")."""
    found = labelled(text)
    return found is not None and text.startswith("**") and not found[1].strip()


def split(text):
    """{heading: Section} of a page and the problems of its headings."""
    found, problems, current, sub = {}, [], None, None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if raw.startswith("## "):
            name = raw[3:].strip()
            if name not in SECTIONS:
                problems.append("The page has a heading %r that is not one of the Game Plan's headings (%s)"
                                % (name, ", ".join(SECTIONS)))
                current = None
                continue
            if name in found:
                problems.append("%s: the heading appears twice" % name)
            current, sub = Section(name, number), None
            found[name] = current
        elif raw.startswith("### ") and current is not None:
            sub = raw[4:].strip()
            if current.name not in WITH_SUBSECTIONS:
                problems.append("%s: write under the heading itself, not under a subheading (%r)"
                                % (current.name, sub))
            current.subs.setdefault(sub, [])
            current.sub_lines[sub] = number
        elif current is None or not line or line.startswith(">") or raw.startswith("# "):
            continue
        elif sub is not None:
            current.subs[sub].append((number, line))
        else:
            current.lines.append((number, line))
    for name in SECTIONS:
        if name not in found:
            problems.append("%s: the heading is missing" % name)
    return found, problems


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


def read_table(lines, columns, where, problems):
    """[(line number, {column: value})] of the first table in ``lines``; ``columns`` the allowed
    headers. A header row, a rule row, then the rows."""
    rows = [(n, t) for n, t in lines if t.startswith("|")]
    if not rows:
        return []
    head = cells(rows[0][1])
    unknown = [h for h in head if h not in columns]
    if unknown:
        problems.append("%s: the table has the column%s %s, not one of %s" % (
            where, "s" if len(unknown) > 1 else "", ", ".join(repr(u) for u in unknown), ", ".join(columns)))
    out = []
    for n, t in rows[1:]:
        values = cells(t)
        if all(re.fullmatch(r":?-{3,}:?", v) for v in values if v):
            continue
        if len(values) != len(head):
            problems.append("%s: a row has %d cells, the header %d: %s" % (where, len(values), len(head), t))
            continue
        out.append((n, dict(zip(head, values))))
    return out


def listed(text):
    return [v.strip() for v in text.split(",") if v.strip()] if text else []


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


# ---------------------------------------------------------------- choices from a frozen sheet
def choices_from_sheet(sheet, inactives=None):
    """The page's choices for a frozen call sheet and its game-day inactives (the round trip)."""
    menus = sheet.get("menus") or {}
    choices = {"inactives": {"players": list((inactives or {}).get("players") or [])},
               "depth": "none", "practice": "none", "special_teams": "none",
               "offense": {"menus": {k: v for k, v in menus.items() if k not in ("fourth_down", "two_point")},
                           "calls": [dict(c) for c in sheet.get("offensive_call_sheet") or ()]},
               "notes": list(sheet["notes"]) if "notes" in sheet else "none"}
    decisions = sheet.get("decisions") or {}
    for kind in DECISION_SECTIONS.values():
        block = decisions.get(kind)
        entry = {"menu": menus.get(kind)} if menus.get(kind) is not None else {}
        if block is not None:
            entry.update({"rules": [{k: v for k, v in r.items() if k in ("when", "decision", "call")}
                                    for r in block.get("rules") or ()],
                          "otherwise": block.get("otherwise")})
            if "prepared_calls" in block:
                entry["prepared"] = dict(block["prepared_calls"])
        choices[kind] = entry or "none"
    ds = sheet.get("defensive_call_sheet")
    if ds is None:
        choices["defense"] = "none"
    else:
        practiced = ds.get("practiced") or {}
        choices["defense"] = {
            "caller": ds.get("caller"), "rush": ds["rush_rule"]["rule"],
            "rush_text": ds["rush_rule"]["source"]["text"],
            "practiced": {key: list(practiced[key]) for _, key in PRACTICED if key in practiced},
            "practice_lines": [s["text"] for s in practiced.get("sources") or ()],
            "rows": [{"id": r["id"], "kind": r["kind"], **({"menu": r["menu"]} if "menu" in r else {}),
                      **({"call": dict(r["call"])} if "call" in r else {}), "text": r["source"]["text"]}
                     for r in ds.get("rows") or ()],
        }
        if "notes" in ds:
            choices["defense"]["notes"] = list(ds["notes"])
    return choices


# ---------------------------------------------------------------- the page
def legal_lines(inactive_count=7, special_teams_caller=None, previous_week=None, standing=None):
    """The one line under each heading naming the legal choices; ``standing`` maps a decision kind
    to the wording of the standing rule in force, which "Standing rule" means."""
    same = "; or Same as Week %d" % previous_week if previous_week else ""
    standing = standing or {}

    def rule(kind):
        text = standing.get(kind)
        if not text:
            return "; or Standing rule"
        return "; or Standing rule, which means your rule in force: %s" % (text[:1].lower() + text[1:]).rstrip(".")
    inactive_rule = ("; or Standing rule, which means every player out on a medical instruction on game day and "
                     "the healthy players your rule in force sits: %s; when the week needs more than that, write "
                     "Standing rule above the table and name the others in it"
                     % (standing["inactives"][:1].lower() + standing["inactives"][1:]).rstrip(".")
                     if standing.get("inactives") else "")
    return {
        "Inactives": "%d players from the active roster, one per row, among them every player out on a medical "
                     "instruction on game day (when more are out, those players only)%s%s."
                     % (inactive_count, inactive_rule, same),
        "Depth chart changes": "A position group's full new order from the players now in it, first listed first, "
                               "or a game role and its player; or None.",
        "Practice": "Who takes which work this week, for example a limited player's reps; or None.",
        "Offense": "Each situation in your words, and the calls from the active offensive playbook (its concepts, "
                   "personnel groupings, formations, motions and protections) with the situations each belongs "
                   "to, from %s%s." % (", ".join(CALL_SITUATIONS), same),
        "Fourth downs": "Rules by distance, yards to the goal line, quarter, score and clock, each Go, Field goal "
                        "or Punt, and what happens otherwise (Go, Field goal, Punt or Ask me)%s; or None for "
                        "your call on each one%s." % (rule("fourth_down"), same),
        "Two-point tries": "Rules by quarter, score after the touchdown and clock, each Go for two or Kick, and "
                           "what happens otherwise (Kick, Go for two or Ask me)%s%s." % (rule("two_point"), same),
        "Kickoffs": "Rules by quarter, score after our score and clock, each Onside or Deep, and what happens "
                    "otherwise (Deep, Onside or Ask me)%s%s." % (rule("kickoff"), same),
        "Defense": "Who calls it; the rush rule, which in the active defensive playbook is %s; the menu "
                   "practiced this week; and the calls by situation, each with its use (%s), in the active "
                   "defensive playbook's words%s." % (RUSH_CHOICE[:1].lower() + RUSH_CHOICE[1:], ", ".join(KIND_WORDS.values()),
                                                       same),
        "Special teams": "%s; your instructions for the kicking game, or None." % (
            "%s calls the kicking game" % special_teams_caller if special_teams_caller else "The kicking game"),
        "Notes to the staff": "Anything else the staff should know, one note per line, or None.",
    }


def _decision_lines(kind, entry):
    if entry == "none" or entry is None:
        return []
    if isinstance(entry, dict) and "same_as" in entry:
        return ["Same as Week %d" % entry["same_as"]]
    out = []
    if entry.get("menu") is not None:
        out += ["**%s:** %s" % (SECTION_MENU.get(kind, "Calls"), entry["menu"]), ""]
    if entry.get("standing"):
        out += [STANDING, ""]
    if entry.get("rules") is not None:
        columns = RULE_COLUMNS[kind]
        rows = [[rule_cell(kind, key, rule) for _, key in columns] for rule in entry["rules"]]
        out += table([c for c, _ in columns], rows) + [""]
    if entry.get("otherwise") is not None:
        out += ["**Otherwise:** %s" % decision_word(kind, entry["otherwise"]), ""]
    if entry.get("prepared") is not None:
        out += ["**Prepared calls:**", ""] + table(["Situation", "Call"], [[m, c] for m, c in entry["prepared"].items()]) + [""]
    return out


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


def _call_rows(calls):
    used = [(c, k) for c, k in CALL_COLUMNS if k not in ("carrier",) or any(k in call for call in calls)]
    rows = []
    for call in calls:
        row = []
        for _, key in used:
            value = call.get(key)
            if value is None:
                row.append("")
            elif key in ("tags", "menus", "opener_returns") or (key in ("target", "carrier") and isinstance(value, list)):
                row.append(", ".join(str(v) for v in value))
            else:
                row.append(str(value))
        rows.append(row)
    return [c for c, _ in used], rows


def render(title, intro, choices, legal):
    """The page, from its choices; ``legal`` is the one-line explanation of each section."""
    out = ["# " + title, "", intro, ""]
    for name in SECTIONS:
        out += ["## " + name, "", "> " + legal[name], ""]
        key = SECTION_KEYS[name]
        value = choices.get(key)
        if isinstance(value, dict) and "same_as" in value:
            out += ["Same as Week %d" % value["same_as"], ""]
            continue
        if value == "none":
            out += ["None", ""]
            continue
        if name == "Inactives" and isinstance(value, dict) and value.get("standing"):
            out += [STANDING, ""]
            if value.get("players"):
                reasons = value.get("reasons") or {}
                out += table(["Player", "Pos", "Reason"],
                             [[p, (value.get("positions") or {}).get(p, ""), reasons.get(p, "")]
                              for p in value["players"]]) + [""]
        elif name == "Inactives":
            if value is not None:
                reasons = value.get("reasons") or {}
                out += table(["Player", "Pos", "Reason"],
                             [[p, (value.get("positions") or {}).get(p, ""), reasons.get(p, "")]
                              for p in value["players"]]) + [""]
            else:
                out += table(["Player", "Pos", "Reason"], []) + [""]
        elif name == "Depth chart changes":
            if value is not None:
                if value.get("orders"):
                    out += table(["Group", "Order"], [[g, ", ".join(p)] for g, p in value["orders"].items()]) + [""]
                if value.get("roles"):
                    out += table(["Role", "Player"], [[r, p] for r, p in value["roles"].items()]) + [""]
        elif name in ("Practice", "Special teams"):
            out += [line for line in (value or [])] + ([""] if value else [])
        elif name == "Notes to the staff":
            out += ["- " + n for n in (value or [])] + ([""] if value else [])
        elif name == "Offense":
            value = value or {}
            menus = value.get("menus") or {}
            for key_, label in OFFENSE_MENUS:
                out += ["### " + label, ""] + ([menus[key_], ""] if menus.get(key_) is not None else [])
            head, rows = _call_rows(value.get("calls") or [])
            out += ["### " + CALLS, ""] + table(head, rows) + [""]
            looked = [c for c in value.get("calls") or () if c.get("what_stone_is_looking_at") is not None]
            out += ["### " + LOOKING, ""]
            out += ["- **%s:** %s" % (c["name"], c["what_stone_is_looking_at"]) for c in looked]
            out += [""] if looked else []
        elif name in DECISION_SECTIONS:
            out += _decision_lines(DECISION_SECTIONS[name], value)
        elif name == "Defense":
            out += _defense_lines(value or {})
    return "\n".join(out).rstrip("\n") + "\n"


def _defense_lines(value):
    out = ["**Who calls it:** %s" % (value.get("caller") or ""), "", "**Rush rule:** %s" % (value.get("rush") or ""), ""]
    out = [line.rstrip() for line in out]
    if value.get("rush_text") is not None and value.get("rush_text") != value.get("rush"):
        out += ["**As written:** %s" % value["rush_text"], ""]
    from .defensive_calls import PRESSURE_FAMILIES
    practiced = value.get("practiced") or {}
    rows = []
    for label, key in PRACTICED:
        if key in practiced:
            words = [PRESSURE_FAMILIES.get(w, w) if key == "pressures" else w for w in practiced[key]]
            rows.append([label, ", ".join(words)])
    out += ["### Practiced this week", ""] + table(["Menu", "Words"], rows) + [""]
    if value.get("practice_lines"):
        out += ["**Practice lines:**", ""] + ["- " + t for t in value["practice_lines"]] + [""]
    rows = []
    given = value.get("rows") or ()
    # The Row column only when a row's name is not the one the page would give it.
    columns = ROW_COLUMNS if [r["id"] for r in given] != derived_ids(given) else ROW_COLUMNS[1:]
    for r in given:
        call = r.get("call") or {}
        row = []
        for _, key in columns:
            if key == "id":
                row.append(r["id"])
            elif key == "kind":
                row.append(KIND_WORDS.get(r["kind"], r["kind"]))
            elif key == "menu":
                row.append(DEF_MENU_WORDS.get(r.get("menu"), r.get("menu") or ""))
            elif key == "text":
                row.append(r.get("text") or "")
            elif key in ("coverage", "tags"):
                row.append(", ".join(call[key]) if key in call else "")
            elif key == "pressure":
                row.append(PRESSURE_FAMILIES.get(call[key], call[key]) if key in call else "")
            else:
                row.append(call.get(key, ""))
        rows.append(row)
    out += ["### Calls by situation", ""] + table([c for c, _ in columns], rows) + [""]
    if value.get("notes"):
        out += ["### Notes", ""] + ["- " + n for n in value["notes"]] + [""]
    return out


SECTION_KEYS = {"Inactives": "inactives", "Depth chart changes": "depth", "Practice": "practice",
                "Offense": "offense", "Fourth downs": "fourth_down", "Two-point tries": "two_point",
                "Kickoffs": "kickoff", "Defense": "defense", "Special teams": "special_teams",
                "Notes to the staff": "notes"}


def blank(title, intro, legal):
    """A blank Game Plan: every heading with its explanation and the empty tables."""
    return render(title, intro, {}, legal)


# ---------------------------------------------------------------- reading a page
def parse(text):
    """(choices, problems): the page's choices by section key, None where a section is empty,
    and every problem of form in football words."""
    found, problems = split(text)
    choices = {}
    for name in SECTIONS:
        section = found.get(name)
        key = SECTION_KEYS[name]
        if section is None or section.empty():
            choices[key] = None
            continue
        week = section.same_as()
        if week is not None:
            choices[key] = {"same_as": week}
            continue
        if section.none():
            choices[key] = "none"
            continue
        reader = READERS[name]
        choices[key] = reader(section, problems)
    return choices, problems


def _is_standing(text):
    return text.lower().rstrip(".") == STANDING.lower()


def _inactives(section, problems):
    """The inactives as written: a table of players; Standing rule alone; or Standing rule above a
    table of the others he names when the week needs more than his rule sits ({"standing": True,
    "players": ...})."""
    texts = data_lines(section.lines)
    standing = any(_is_standing(t) for t in texts)
    if standing and not any(t.startswith("|") for t in texts):
        if len([t for t in texts if _is_standing(t)]) == len(texts):
            return {"standing": True}
    rows = read_table(section.lines, ("Player", "Pos", "Reason"), "Inactives", problems)
    players, reasons, positions, lines = [], {}, {}, {}
    for n, row in rows:
        name = row.get("Player", "")
        if not name:
            continue
        players.append(name)
        lines[name] = n
        if row.get("Reason"):
            reasons[name] = row["Reason"]
        if row.get("Pos"):
            positions[name] = row["Pos"]
    stray = [t for _, t in section.lines if not t.startswith("|") and not (standing and _is_standing(t))]
    if stray:
        problems.append("Inactives: write one player per table row, Standing rule alone, or Standing rule above "
                        "a table of the others you name (%r is outside the table)" % stray[0])
    value = {"players": players, "reasons": reasons, "positions": positions, "lines": lines}
    return dict({"standing": True}, **value) if standing else value


def _depth(section, problems):
    orders, roles = {}, {}
    tables, current = [], []
    rule = lambda t: all(re.fullmatch(r":?-{3,}:?", c) for c in cells(t) if c)
    lines = list(section.lines)
    for i, (n, t) in enumerate(lines):
        # A table starts at a header row (the row a rule row follows); blank lines are not kept, so two
        # tables one after the other are told apart by their headers.
        header = t.startswith("|") and i + 1 < len(lines) and lines[i + 1][1].startswith("|") \
            and rule(lines[i + 1][1]) and not rule(t)
        if t.startswith("|") and not (header and current):
            current.append((n, t))
        elif t.startswith("|"):
            tables.append(current)
            current = [(n, t)]
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    for rows in tables:
        head = cells(rows[0][1])
        if head and head[0] == "Group":
            for _, row in read_table(rows, ("Group", "Order"), "Depth chart changes", problems):
                group = GROUPS.get(row["Group"], row["Group"])
                orders[group] = listed(row["Order"])
        elif head and head[0] == "Role":
            for _, row in read_table(rows, ("Role", "Player"), "Depth chart changes", problems):
                roles[ROLES.get(row["Role"], row["Role"])] = row["Player"]
        else:
            problems.append("Depth chart changes: a table needs Group and Order, or Role and Player, columns")
    if not tables:
        problems.append("Depth chart changes: write a Group and Order table, a Role and Player table, or None")
    return {"orders": orders, "roles": roles}


def _text(section, problems):
    return [t for _, t in section.lines]


def _notes(section, problems):
    out = []
    for _, t in section.lines:
        m = BULLET.match(t)
        out.append(m[1] if m else t)
    return out


def _offense(section, problems):
    menus, calls, looked = {}, [], {}
    labels = dict((label, key) for key, label in OFFENSE_MENUS)
    for sub, lines in section.subs.items():
        if sub in labels:
            if lines:
                menus[labels[sub]] = " ".join(t for _, t in lines)
        elif sub == CALLS:
            continue
        elif sub == LOOKING:
            for n, t in lines:
                m = LOOK.match(t)
                if not m:
                    problems.append("Offense, %s: write each as '- **Call name:** what you are looking at' (%r)"
                                    % (LOOKING, t))
                    continue
                looked[m[1]] = (n, m[2])
        else:
            problems.append("Offense: %r is not a situation of the call sheet (%s)"
                            % (sub, ", ".join(label for _, label in OFFENSE_MENUS)))
    if section.lines:
        problems.append("Offense: write under a situation heading (%r sits under none)" % section.lines[0][1])
    columns = tuple(c for c, _ in CALL_COLUMNS)
    fields = dict(CALL_COLUMNS)
    for n, row in read_table(section.subs.get(CALLS, []), columns, "Offense, Calls", problems):
        call = {}
        for column, value in row.items():
            key = fields.get(column)
            if key is None:
                continue
            try:
                parsed = call_value(key, value)
            except ValueError as exc:
                problems.append("Offense, Calls, %r: %s" % (row.get("Call", ""), exc))
                continue
            if parsed is not None:
                call[key] = parsed
        if not call.get("name"):
            problems.append("Offense, Calls: a row (line %d) names no call" % n)
            continue
        call["_line"] = n
        calls.append(call)
    names = {c["name"] for c in calls}
    for name, (n, text) in looked.items():
        if name not in names:
            problems.append("Offense, %s: %r is not a call in the Calls table" % (LOOKING, name))
    for call in calls:
        if call["name"] in looked:
            call["what_stone_is_looking_at"] = looked[call["name"]][1]
    ordered = []
    for call in calls:
        ordered.append({k: call[k] for k in CALL_KEYS if k in call} | {"_line": call["_line"]})
    return {"menus": menus, "calls": ordered}


def call_value(key, value):
    if key in ALWAYS_LISTS:
        return listed(value)
    if value == "":
        return None
    if key == "opener":
        if not value.isdigit():
            raise ValueError("the opener %r is not a number" % value)
        return int(value)
    if key == "opener_returns":
        items = listed(value)
        if not all(i.isdigit() for i in items):
            raise ValueError("the returns %r are not opener numbers" % value)
        return [int(i) for i in items]
    if key in ("target", "carrier"):
        return value if value in GROUP_VALUES else listed(value)
    return value


def _decision(kind):
    def read(section, problems):
        where = next(name for name, k in DECISION_SECTIONS.items() if k == kind)
        entry, label = {}, SECTION_MENU.get(kind, "Calls")
        rule_lines = [(n, t) for n, t in section.lines if t.startswith("|")]
        prepared_at = None
        for i, (n, t) in enumerate(section.lines):
            m = labelled(t)
            if t.lower().rstrip(".") == STANDING.lower():
                entry["standing"] = True
            elif m and m[0] == label:
                entry["menu"] = m[1]
            elif m and m[0] == "Otherwise":
                words = {v.lower(): k for k, v in list(DECISION_WORDS[kind].items()) + list(OTHERWISE_WORDS.items())}
                if m[1].strip().lower() not in words:
                    problems.append("%s: otherwise %r is not one of %s" % (
                        where, m[1], ", ".join(list(DECISION_WORDS[kind].values()) + list(OTHERWISE_WORDS.values()))))
                else:
                    entry["otherwise"] = words[m[1].strip().lower()]
            elif m and m[0] == "Prepared calls":
                prepared_at = n
            elif not t.startswith("|"):
                problems.append("%s: %r is neither a rule table, Otherwise, Standing rule nor %s" % (where, t, label))
        rules_part = [(n, t) for n, t in rule_lines if prepared_at is None or n < prepared_at]
        prepared_part = [(n, t) for n, t in rule_lines if prepared_at is not None and n > prepared_at]
        columns = dict(RULE_COLUMNS[kind])
        rows = read_table(rules_part, tuple(columns), where, problems)
        if rows or rules_part:
            entry["rules"] = []
        for n, row in rows:
            rule = rule_from_row(kind, row, where, problems)
            if rule is not None:
                entry["rules"].append(rule)
        if prepared_part:
            entry["prepared"] = {r["Situation"]: r["Call"]
                                 for _, r in read_table(prepared_part, ("Situation", "Call"), where, problems)}
        if entry.get("rules") is not None and "otherwise" not in entry:
            problems.append("%s: say what happens otherwise (**Otherwise:** %s)" % (
                where, " or ".join(list(DECISION_WORDS[kind].values()) + list(OTHERWISE_WORDS.values()))))
        if entry.get("standing") and entry.get("rules") is not None:
            problems.append("%s: write Standing rule or your own rules, not both" % where)
        return entry
    return read


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


def _defense(section, problems):
    from .defensive_calls import PRESSURE_FAMILIES
    pressures = {v.lower(): k for k, v in PRESSURE_FAMILIES.items()} | {k: k for k in PRESSURE_FAMILIES}
    value, lines = {}, {}
    practice_at = None
    for n, t in section.lines:
        m = labelled(t)
        if m and m[0] == "Who calls it":
            if m[1].strip():
                value["caller"] = m[1].strip()
        elif m and m[0] == "Rush rule":
            if m[1].strip():
                value["rush"], lines["rush"] = m[1].strip(), n
        elif m and m[0] == "As written":
            value["rush_text"], lines["rush_text"] = m[1], n
        else:
            problems.append("Defense: %r is not Who calls it, Rush rule or As written (write them as "
                            "'Who calls it: name' and 'Rush rule: your rule')" % t)
    if "rush" in value:
        from .defensive_calls import RUSH_RULE
        if rush_words(value["rush"]) in RUSH_WORDS:
            if value["rush"] != RUSH_RULE and "rush_text" not in value:
                value["rush_text"], lines["rush_text"] = value["rush"], lines["rush"]
            value["rush"] = RUSH_RULE
        else:
            problems.append("Defense, Rush rule: %r is not the active defensive playbook's rush rule; write "
                            "'%s'" % (value["rush"], RUSH_CHOICE))
    practiced, plines = {}, {}
    sub = section.subs.get("Practiced this week", [])
    for n, row in read_table(sub, ("Menu", "Words"), "Defense, Practiced this week", problems):
        key = dict(PRACTICED).get(row["Menu"])
        if key is None:
            problems.append("Defense, Practiced this week: %r is not one of %s" % (
                row["Menu"], ", ".join(label for label, _ in PRACTICED)))
            continue
        words = listed(row["Words"])
        if key == "pressures":
            words = [pressures.get(w.lower(), w) for w in words]
        practiced[key] = words
        plines[key] = (n, row["Words"])
    value["practiced"], lines["practiced"] = practiced, plines
    for i, (n, t) in enumerate(sub):
        if labelled(t) and labelled(t)[0] == "Practice lines":
            practice_at = i
    if practice_at is not None:
        value["practice_lines"], lines["practice_lines"] = [], []
        for n, t in sub[practice_at + 1:]:
            m = BULLET.match(t)
            if m:
                value["practice_lines"].append(m[1])
                lines["practice_lines"].append(n)
    rows = []
    kinds = {v.lower(): k for k, v in KIND_WORDS.items()}
    menus = {v.lower(): k for k, v in DEF_MENU_WORDS.items()} | {k: k for k in DEF_MENU_WORDS}
    seen = set()
    for n, row in read_table(section.subs.get("Calls by situation", []), tuple(c for c, _ in ROW_COLUMNS),
                             "Defense, Calls by situation", problems):
        where = "Defense, Calls by situation, line %d" % n
        kind = kinds.get(row.get("Use", "").lower())
        if kind is None:
            problems.append("%s: the use %r is not one of %s" % (where, row.get("Use", ""),
                                                                 ", ".join(KIND_WORDS.values())))
            continue
        entry = {"kind": kind}
        if row.get("Situation"):
            menu = menus.get(row["Situation"].lower())
            if menu is None:
                problems.append("%s: %r is not a defensive situation (%s)" % (
                    where, row["Situation"], ", ".join(DEF_MENU_WORDS.values())))
            else:
                entry["menu"] = menu
        rid = re.sub(r"\s+", "-", row.get("Row", "").strip().lower()) or row_id(kind, entry.get("menu"), seen)
        seen.add(rid)
        entry = {"id": rid, **entry}
        call = {}
        for column, key in ROW_COLUMNS[3:9]:
            cell_value = row.get(column, "")
            if not cell_value:
                continue
            if key in ("coverage", "tags"):
                call[key] = listed(cell_value)
            elif key == "pressure":
                call[key] = pressures.get(cell_value.lower(), cell_value)
            else:
                call[key] = cell_value
        if call:
            entry["call"] = {k: call[k] for k in CALL_FIELDS if k in call}
        # The row's words as the page writes them, verbatim on its own line: its As written cell, or
        # else its name, its situation or its use.
        entry["text"] = (row.get("As written") or row.get("Row", "").strip() or row.get("Situation")
                         or row.get("Use"))
        entry["_line"] = n
        rows.append(entry)
    value["rows"] = rows
    notes = section.subs.get("Notes", [])
    if notes:
        value["notes"] = [BULLET.match(t)[1] if BULLET.match(t) else t for _, t in notes]
    for sub_name in section.subs:
        if sub_name not in ("Practiced this week", "Calls by situation", "Notes"):
            problems.append("Defense: %r is not one of Practiced this week, Calls by situation or Notes" % sub_name)
    value["_lines"] = lines
    return value


READERS = {"Inactives": _inactives, "Depth chart changes": _depth, "Practice": _text, "Offense": _offense,
           "Fourth downs": _decision("fourth_down"), "Two-point tries": _decision("two_point"),
           "Kickoffs": _decision("kickoff"), "Defense": _defense, "Special teams": _text,
           "Notes to the staff": _notes}


# ---------------------------------------------------------------- the frame
def frame_from_sheet(sheet):
    """The frame of a frozen sheet: its record fields that are not football choices (the event,
    when and from what it was frozen, the ids and source wording of its decision blocks, and the
    packet lines its defensive rows cite)."""
    frame = {"top": {k: sheet[k] for k in TOP_KEYS if k in sheet}, "decisions": {}, "defense": None}
    for kind, block in (sheet.get("decisions") or {}).items():
        frame["decisions"][kind] = {"id": block.get("id"), "source": block.get("source"),
                                    "rules": [{"id": r.get("id"), "source": r.get("source")}
                                              for r in block.get("rules") or ()]}
    ds = sheet.get("defensive_call_sheet")
    if ds is not None:
        where = lambda s: {"path": s["path"], "line": s["line"]}
        frame["defense"] = {"head": {k: ds[k] for k in ("schema_version", "team", "book", "packet") if k in ds},
                            "rush": where(ds["rush_rule"]["source"]),
                            "practiced": [where(s) for s in (ds.get("practiced") or {}).get("sources") or ()],
                            "rows": {r["id"]: where(r["source"]) for r in ds.get("rows") or ()}}
    return frame


def page_frame(page_rel, event, frozen, provenance, team, book, week):
    """The frame a Game Plan writes when it is applied: its decision blocks named for the week, and
    its defensive rows citing the page's own lines (no per-row entries: build_sheet uses the
    parsed line numbers)."""
    return {"top": {"schema_version": 1, "team": team, "event": event, "status": STATUS, "frozen": frozen,
                    "provenance": provenance},
            "decisions": {kind: {"id": "stone-%s-game-plan-week-%d" % (kind.replace("_", "-"), week),
                                 "source": "Stone's Week %d Game Plan, %s" % (week, section)}
                          for section, kind in DECISION_SECTIONS.items()},
            "defense": {"head": {"schema_version": 1, "team": team, "book": book, "packet": page_rel},
                        "page": page_rel}}


# ---------------------------------------------------------------- the call sheet
def build_sheet(choices, frame, carried=None, standing=None):
    """The call sheet from the page's choices and the frame. ``carried`` maps a week to its frozen
    sheet for "Same as Week N"; ``standing`` maps a decision kind to the standing rule's block for
    "Standing rule". Raises ValueError on a choice it cannot place."""
    carried = carried or {}
    standing = standing or {}
    sheet = dict(frame["top"])
    menus = {}

    def week_sheet(week):
        if week not in carried:
            raise ValueError("Week %d's call sheet is not on file" % week)
        return carried[week]

    offense = choices.get("offense")
    if isinstance(offense, dict) and "same_as" in offense:
        source = week_sheet(offense["same_as"])
        menus.update({k: v for k, v in (source.get("menus") or {}).items() if k not in ("fourth_down", "two_point")})
        calls = json.loads(json.dumps(source.get("offensive_call_sheet") or []))
    else:
        offense = offense if isinstance(offense, dict) else {}
        menus.update(offense.get("menus") or {})
        calls = [{k: v for k, v in c.items() if k != "_line"} for c in offense.get("calls") or ()]
    decisions = {}
    for kind in ("two_point", "kickoff", "fourth_down"):
        entry = choices.get(kind)
        if isinstance(entry, dict) and "same_as" in entry:
            source = week_sheet(entry["same_as"])
            if (source.get("menus") or {}).get(kind) is not None:
                menus[kind] = source["menus"][kind]
            if kind in (source.get("decisions") or {}):
                decisions[kind] = json.loads(json.dumps(source["decisions"][kind]))
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("menu") is not None:
            menus[kind] = entry["menu"]
        if entry.get("standing"):
            if kind not in standing:
                raise ValueError("no standing rule is on file for %s" % kind)
            decisions[kind] = json.loads(json.dumps(standing[kind]))
        elif entry.get("rules") is not None or entry.get("otherwise") is not None:
            names = (frame.get("decisions") or {}).get(kind) or {}
            block = {}
            if names.get("id") is not None:
                block["id"] = names["id"]
            if names.get("source") is not None:
                block["source"] = names["source"]
            rule_names = names.get("rules") or []
            rules = []
            for i, rule in enumerate(entry.get("rules") or ()):
                named = rule_names[i] if i < len(rule_names) else {}
                out = {}
                if named.get("id") is not None:
                    out["id"] = named["id"]
                if named.get("source") is not None:
                    out["source"] = named["source"]
                out.update(rule)
                rules.append(out)
            block["rules"] = rules
            block["otherwise"] = entry.get("otherwise")
            if entry.get("prepared") is not None:
                block["prepared_calls"] = dict(entry["prepared"])
            decisions[kind] = block
    sheet["menus"] = {k: menus[k] for k in MENU_ORDER if k in menus}
    notes = choices.get("notes")
    if isinstance(notes, dict) and "same_as" in notes:
        source = week_sheet(notes["same_as"])
        if "notes" in source:
            sheet["notes"] = list(source["notes"])
    elif isinstance(notes, list):
        sheet["notes"] = list(notes)
    sheet["offensive_call_sheet"] = calls
    if decisions:
        sheet["decisions"] = {k: decisions[k] for k in ("two_point", "kickoff", "fourth_down") if k in decisions}
    defense = choices.get("defense")
    if isinstance(defense, dict) and "same_as" in defense:
        source = week_sheet(defense["same_as"])
        if "defensive_call_sheet" in source:
            sheet["defensive_call_sheet"] = json.loads(json.dumps(source["defensive_call_sheet"]))
    elif isinstance(defense, dict):
        sheet["defensive_call_sheet"] = _defensive_sheet(defense, frame["defense"])
    return sheet


def _defensive_sheet(value, frame):
    head = frame["head"]
    page = frame.get("page")
    lines = value.get("_lines") or {}

    def source(fixed, line, text):
        if fixed is not None:
            return {"path": fixed["path"], "line": fixed["line"], "text": text}
        return {"path": page, "line": line, "text": text}

    out = {k: head[k] for k in ("schema_version", "team") if k in head}
    out["caller"] = value.get("caller")
    out.update({k: head[k] for k in ("book", "packet") if k in head})
    if "notes" in value:
        out["notes"] = list(value["notes"])
    rush_text = value.get("rush_text") if value.get("rush_text") is not None else value.get("rush")
    rush_line = lines.get("rush_text") if value.get("rush_text") is not None else lines.get("rush")
    out["rush_rule"] = {"rule": value.get("rush"), "source": source(frame.get("rush"), rush_line, rush_text)}
    practiced = {key: list(value["practiced"][key]) for _, key in PRACTICED if key in (value.get("practiced") or {})}
    fixed = frame.get("practiced")
    if value.get("practice_lines") is not None:
        texts = list(value["practice_lines"])
        numbers = lines.get("practice_lines") or [None] * len(texts)
    else:
        found = [(lines.get("practiced") or {})[key] for _, key in PRACTICED if key in (lines.get("practiced") or {})]
        texts, numbers = [t for _, t in found], [n for n, _ in found]
    practiced["sources"] = [source(fixed[i] if fixed is not None and i < len(fixed) else None, numbers[i], texts[i])
                            for i in range(len(texts))]
    out["practiced"] = practiced
    rows = []
    for r in value.get("rows") or ():
        row = {"id": r["id"], "kind": r["kind"]}
        if "menu" in r:
            row["menu"] = r["menu"]
        if "call" in r:
            row["call"] = dict(r["call"])
        row["source"] = source((frame.get("rows") or {}).get(r["id"]), r.get("_line"), r["text"])
        rows.append(row)
    out["rows"] = rows
    return {k: out[k] for k in DEFENSE_KEYS if k in out}


# A standing fourth-down rule that names "Tice's first call on the matching menu" says so on its
# instruction (``prepared_calls``); the calls are the week's, so they are filled from its sheet.
FIRST_ON_MENU = "first-call-on-each-matching-menu"


def first_calls(calls):
    """{menu: call name}: for each menu a fourth down can match (runtime/fourth_down.py's prepared
    menus), the first call of the sheet, in sheet order, that names it; the live fourth-down
    information lists a matching menu's calls in the same order (runtime/kernel.py matching_calls)."""
    from . import call_situations as cs
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
