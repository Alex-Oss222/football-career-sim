#!/usr/bin/env python3
"""Check Stone's Game Plan before anything runs (rebuild step 4).

  python scripts/check_game_plan.py WEEK --season YEAR [--file PATH] [--root PATH]

Reads the week's Game Plan page (runtime/game_plan.py) and says exactly what
is missing or invalid, in football words, for example "Inactives: 6 named, 7
needed", "Red zone: 'Flood Sail' is not in the active playbook" or
"Inactives: Ace Sanders is not on the roster". It exits 1 until the page is
complete, and 0 when it is. With --file, an uploaded .md or .txt file with
the same headings becomes the week's Game Plan page first (the page stays as
the record of his decision); nothing else is written.

What it checks:

- every heading is present and has something under it (a choice, None,
  Same as Week N or, for the three decision rules, Standing rule);
- the inactives: the right number, every one on the active roster, every
  player whose medical instruction keeps him out on game day among them;
- the depth chart changes: a group's new order holds exactly the players now
  in that group; a game role names a player on the chart;
- the offense: every call's concept is in the active offensive playbook
  (runtime/call_families.py reads the 2013 iteration the playbook lock
  allows), every situation a call names is one of the call sheet's;
- the call sheet the page would freeze, under the existing validators
  (runtime/call_families.sheet_errors, runtime/scoring_decisions.sheet_errors,
  runtime/defensive_calls.sheet_errors and source_errors), so a page that
  passes here applies cleanly;
- the page is clean (runtime/clean_pages.py);
- the week has not been played, and the Game Week Briefing is current (a
  briefing the situation has overtaken is re-issued first).

Open items with other people that hold the week, and medical exams still to
come, are listed as notes; they do not fail the check. Nothing here moves
time or creates an event. scripts/apply_game_plan.py applies a page that
passes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import call_families, call_situations as cs, current_job, game_plan  # noqa: E402
from runtime import roster as roster_record  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

JAX = "Jacksonville Jaguars"
STATUS_WORDS = {"two_point": "Two-point tries", "kickoff": "Kickoffs", "fourth_down": "Fourth downs"}
# The situations a call may name (call_situations's menus, as the sheets spell them).
KNOWN_MENUS = frozenset({cs.NORMAL, cs.SECOND_LONG, cs.THIRD_SHORT, cs.THIRD_MEDIUM, cs.THIRD_LONG, cs.BACKED_UP,
                         cs.HIGH_RED, cs.LOW_RED, cs.GOAL_LINE, cs.TWO_MINUTE, cs.PRESS, cs.FOUR_MINUTE,
                         cs.SUDDEN_CHANGE, cs.OPENING, cs.TWO_POINT, "final-play-of-half", "red-zone", "empty"})
MENU_WORDS = {cs.HIGH_RED: "Red zone", cs.LOW_RED: "Red zone", cs.GOAL_LINE: "Red zone", "red-zone": "Red zone",
              cs.NORMAL: "Normal downs", cs.SECOND_LONG: "Second and long", cs.THIRD_SHORT: "Third down",
              cs.THIRD_MEDIUM: "Third down", cs.THIRD_LONG: "Third down", cs.BACKED_UP: "Backed up",
              cs.TWO_MINUTE: "Two-minute", cs.PRESS: "PRESS sequence", cs.FOUR_MINUTE: "Four-minute",
              cs.SUDDEN_CHANGE: "Sudden change", cs.OPENING: "Opening sequence", cs.TWO_POINT: "Two-point tries",
              "final-play-of-half": "Final play of the half", "empty": "Empty"}
CHECK_WORDS = ((re.compile(r"system words?: (\w+)"), "'%s' is not a football word"),
               (re.compile(r"internal code: (\S+)"), "'%s' reads as an internal code"),
               (re.compile(r"system name: (\S+)"), "'%s' reads as a system name"),
               (re.compile(r"script or module name: (\S+)"), "'%s' names a script or module"),
               (re.compile(r"link to a system file: (\S+)"), "the link to %s points into the system files"),
               (re.compile(r"version label: (\S+)"), "'%s' reads as a version label"),
               (re.compile(r"markup: (.+)"), "%s is markup"),
               (re.compile(r"code span"), "a code span (`) is not football writing"))


class Plan:
    """A week's Game Plan and what checking it reads."""

    def __init__(self, root, season, week):
        self.root = Path(root).resolve()
        self.season, self.week = season, week
        self.paths = SeasonPaths(season, self.root)
        self.pages = week_pages(season, week, self.root)
        self.master = master_date(self.root)
        self.job = current_job.load(self.root)
        games = [g for g in self.paths.regular_games() if g["week"] == week and JAX in (g["away"], g["home"])]
        self.game = games[0] if games else None
        self.roster = roster_record.load(self.paths.roster)
        self.chart = json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))
        self.text = self.pages.plan.read_text(encoding="utf-8") if self.pages.plan.is_file() else None
        self.choices, self.problems = (game_plan.parse(self.text) if self.text is not None else ({}, []))
        self.notes = []

    def rel(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def active(self):
        return [p["name"] for p in roster_record.players(self.roster, ("active",))]

    def carried(self):
        """{week: frozen sheet} for every "Same as Week N" the page writes."""
        out = {}
        for key, value in self.choices.items():
            if isinstance(value, dict) and "same_as" in value:
                path = self.paths.call_sheet(value["same_as"])
                if path.is_file():
                    out[value["same_as"]] = json.loads(path.read_text(encoding="utf-8"))
        return out

    def standing(self):
        """{kind: block} of each standing decision rule in force: the block stored on the instruction
        (the fourth-down rule), or the frozen sheet's block its record points at (the two-point and
        kickoff rules)."""
        out = {}
        for item in current_job.instructions(self.job):
            subject, record = item.get("subject"), item.get("record") or {}
            if subject in STATUS_WORDS and isinstance(item.get("block"), dict):
                out[subject] = json.loads(json.dumps(item["block"]))
                continue
            if subject not in STATUS_WORDS or not str(record.get("path", "")).endswith(".json"):
                continue
            try:
                data = json.loads((self.root / record["path"]).read_text(encoding="utf-8"))
                for part in [p for p in str(record.get("pointer", "")).split("/") if p]:
                    data = data[part]
            except (OSError, ValueError, KeyError, TypeError):
                continue
            out[subject] = data
        return out

    def event(self):
        g = self.game
        place = lambda club: club.rsplit(" ", 1)[0]
        d = date.fromisoformat(g["date"])
        return "%d regular season Week %d, %s at %s, %s %d, %d" % (
            self.season, self.week, place(g["away"]), place(g["home"]), d.strftime("%B"), d.day, d.year)

    def frame(self):
        from runtime.defensive_calls import active_defensive_book
        page = self.rel(self.pages.plan)
        today = self.master.isoformat()
        provenance = ("Stone's Week %d Game Plan (%s), checked by scripts/check_game_plan.py and applied by "
                      "scripts/apply_game_plan.py on %s: the calls, the situation menus, the decision rules and the "
                      "defensive sheet as the page writes them, each defensive row citing the page's own line."
                      % (self.week, page, today))
        return game_plan.page_frame(page, self.event(), "%s, from Stone's Week %d Game Plan after its check passed; "
                                    "before any draw" % (today, self.week), provenance, JAX,
                                    active_defensive_book(self.root), self.week)

    def filled(self):
        """The decision kinds whose standing rule takes Tice's first call on each matching menu."""
        return {item.get("subject") for item in current_job.instructions(self.job)
                if item.get("prepared_calls") == game_plan.FIRST_ON_MENU}

    def sheet(self):
        sheet = game_plan.build_sheet(self.choices, self.frame(), self.carried(), self.standing())
        for kind in self.filled():
            entry = self.choices.get(kind)
            block = (sheet.get("decisions") or {}).get(kind)
            if isinstance(entry, dict) and entry.get("standing") and block is not None:
                prepared = game_plan.first_calls(sheet.get("offensive_call_sheet"))
                if prepared:
                    block["prepared_calls"] = prepared
        return sheet

    def inactives(self):
        """The players the page lists inactive (or Week N's list, carried)."""
        value = self.choices.get("inactives")
        if isinstance(value, dict) and "same_as" in value:
            listed = self.chart.get("game_day_inactives") or {}
            return list(listed.get("players") or []) if listed.get("week") == value["same_as"] else None
        return list(value["players"]) if isinstance(value, dict) else None


# ---------------------------------------------------------------- the checks
def section_of(text, line):
    """The heading a page line sits under."""
    current = "The page"
    for number, raw in enumerate(text.splitlines(), 1):
        if number > line:
            break
        if raw.startswith("## "):
            current = raw[3:].strip()
        elif raw.startswith("### ") and current in ("Offense", "Defense"):
            current = current.split(",")[0] + ", " + raw[4:].strip()
    return current


def clean_problems(plan):
    out = []
    for error in page_errors(plan.rel(plan.pages.plan), plan.text, root=plan.root):
        _, line, what = error.split(":", 2)
        what = what.strip()
        for pattern, words in CHECK_WORDS:
            m = pattern.search(what)
            if m:
                what = words % m.group(1) if m.groups() else words
                break
        out.append("%s: %s" % (section_of(plan.text, int(line)), what))
    return out


def required(plan):
    out = []
    for name in game_plan.SECTIONS:
        key = game_plan.SECTION_KEYS[name]
        if plan.choices.get(key) is None:
            if name == "Inactives":
                from runtime.rules import RULES
                out.append("Inactives: none named, %d needed" % (len(plan.active()) - RULES.active_limit))
                continue
            hint = {"Offense": "write the calls and situations",
                    "Defense": "write who calls it and the calls by situation, or None",
                    "Fourth downs": "write your rules, Standing rule or None for your live call",
                    "Two-point tries": "write your rules or Standing rule",
                    "Kickoffs": "write your rules or Standing rule"}.get(name, "write it, or None")
            out.append("%s: nothing written; %s" % (name, hint))
    for key, value in plan.choices.items():
        if isinstance(value, dict) and "same_as" in value:
            week = value["same_as"]
            name = next(n for n, k in game_plan.SECTION_KEYS.items() if k == key)
            if week >= plan.week:
                out.append("%s: Same as Week %d names a week that has not come before this one" % (name, week))
            elif key in ("offense", "fourth_down", "two_point", "kickoff", "defense", "notes") \
                    and week not in plan.carried():
                out.append("%s: Week %d has no frozen call sheet to carry" % (name, week))
    for kind in ("two_point", "kickoff"):
        if plan.choices.get(kind) == "none":
            out.append("%s: a rule is needed for the game (your rules with Otherwise, or Standing rule)"
                       % STATUS_WORDS[kind])
    for kind, words in STATUS_WORDS.items():
        entry = plan.choices.get(kind)
        if isinstance(entry, dict) and entry.get("standing") and kind not in plan.standing():
            out.append("%s: no standing rule is on file as rules the staff can set; write the rules here" % words)
    return out


def inactive_problems(plan):
    value = plan.choices.get("inactives")
    if value is None:
        return []
    from runtime.rules import RULES
    active = plan.active()
    needed = len(active) - RULES.active_limit
    players = plan.inactives()
    if players is None:
        return ["Inactives: Week %d's list is no longer on file; name the %d" % (value["same_as"], needed)]
    out = []
    if len(players) != needed:
        out.append("Inactives: %d named, %d needed" % (len(players), needed))
    for name in sorted({p for p in players if players.count(p) > 1}):
        out.append("Inactives: %s is named twice" % name)
    on_lists = {p["name"]: p for p in roster_record.players(plan.roster)}
    for name in players:
        if name not in on_lists:
            out.append("Inactives: %s is not on the roster" % name)
        elif name not in active:
            out.append("Inactives: %s is not on the active roster (%s)" % (name, on_lists[name]["status"]))
    from runtime.week_inputs import roster_available
    game_day = date.fromisoformat(plan.game["date"])
    for p in roster_record.players(plan.roster, ("active",)):
        try:
            cleared = roster_available(p.get("availability") or "", game_day, plan.season)
        except ValueError:
            cleared = True
        if not cleared and p["name"] not in players:
            out.append("Inactives: %s is out on his medical instruction for the game and must be among them"
                       % p["name"])
    return out


def depth_problems(plan):
    value = plan.choices.get("depth")
    if not isinstance(value, dict) or "same_as" in value:
        return []
    out = []
    depth = plan.chart.get("depth") or {}
    for group, order in (value.get("orders") or {}).items():
        if group not in depth:
            out.append("Depth chart changes: %r is not a position group on the chart" % group)
            continue
        now = depth[group]
        for name in order:
            if name not in now:
                out.append("Depth chart changes, %s: %s is not in this group" % (group, name))
        for name in now:
            if name not in order:
                out.append("Depth chart changes, %s: %s is missing from the new order" % (group, name))
        for name in sorted({p for p in order if order.count(p) > 1}):
            out.append("Depth chart changes, %s: %s is listed twice" % (group, name))
    placed = {p for players in depth.values() for p in players}
    for role, name in (value.get("roles") or {}).items():
        if role not in game_plan.ROLES.values():
            out.append("Depth chart changes: %r is not a game role (%s)" % (role, ", ".join(game_plan.ROLES)))
        elif name not in placed:
            out.append("Depth chart changes: %s is not on the chart for the %s role" % (name, role))
    return out


def offense_problems(plan):
    value = plan.choices.get("offense")
    if not isinstance(value, dict) or "same_as" in value:
        return []
    calls = value.get("calls") or []
    if not calls:
        return ["Offense, Calls: no call is written"]
    out = []
    names = [c["name"] for c in calls]
    for name in sorted({n for n in names if names.count(n) > 1}):
        out.append("Offense, Calls: %r is written twice" % name)
    openers = [c["opener"] for c in calls if "opener" in c]
    for n in sorted({o for o in openers if openers.count(o) > 1}):
        out.append("Offense, Calls: opener %d is given to two calls" % n)
    for call in calls:
        menus = [cs.menu_key(m) for m in call.get("menus") or ()]
        place = next((MENU_WORDS[m] for m in menus if m in MENU_WORDS), "Offense, Calls")
        family = call.get("family")
        if not family:
            out.append("%s: %r names no concept" % (place, call["name"]))
        elif call_families.family_entry(family)[0] is None and not call.get("target") and not call.get("carrier"):
            out.append("%s: %r is not in the active playbook" % (place, family))
        for raw, key in zip(call.get("menus") or (), menus):
            if key not in KNOWN_MENUS:
                out.append("Offense, Calls, %r: %r is not a situation of the call sheet" % (call["name"], raw))
        if str(call.get("type", "")).lower() not in ("run", "pass", "mixed", "any"):
            out.append("Offense, Calls, %r: the type must be run, pass, mixed or any" % call["name"])
    return out


def sheet_problems(plan):
    """The call sheet the page would freeze, under the existing validators."""
    try:
        sheet = plan.sheet()
    except ValueError as exc:
        return ["The page cannot be set: %s" % exc], None
    from runtime import defensive_calls, fourth_down, scoring_decisions
    out = ["Offense, Calls: %s" % e for e in call_families.sheet_errors(sheet.get("offensive_call_sheet") or [])]
    names = fourth_down.sheet_call_names(sheet.get("offensive_call_sheet") or ())
    for error in scoring_decisions.sheet_errors(sheet.get("decisions"), names):
        kind = next((k for k in STATUS_WORDS if "decisions.%s" % k in error), None)
        out.append("%s: %s" % (STATUS_WORDS.get(kind, "Decision rules"), error))
    ds = sheet.get("defensive_call_sheet")
    if ds is not None:
        faults = defensive_calls.sheet_errors(ds)
        if not faults:
            faults = defensive_calls.source_errors(ds, plan.root, plan.season)
        out += ["Defense: %s" % defensive_words(e) for e in faults]
    return out, sheet


def defensive_words(error):
    m = re.match(r"row (\S+): (\w+) '([^']+)' is not a word of the active defensive book", error)
    if m:
        return "%s: '%s' is not a %s in the active defensive playbook" % (m[1], m[3], m[2])
    m = re.match(r"row (\S+): (\w+) '([^']+)' is not on the practiced menu", error)
    if m:
        return "%s: '%s' was not practiced this week (add it to Practiced this week)" % (m[1], m[3])
    return error


def check(root, season, week):
    """(problems, notes, plan): what is missing or invalid, and what is still to come."""
    plan = Plan(root, season, week)
    if plan.game is None:
        return ["Week %d: Jacksonville has no game this week" % week], [], plan
    played = list(plan.paths.receipts.glob("week_%02d_*.json" % week)) if plan.paths.receipts.is_dir() else []
    if any(JAX in json.loads(p.read_text(encoding="utf-8"))["matchup"] for p in played):
        return ["Week %d has been played; its plan stays as it was set" % week], [], plan
    if plan.text is None:
        return ["Week %d: no Game Plan page (%s)" % (week, plan.rel(plan.pages.plan))], [], plan
    problems = list(plan.problems)
    problems += required(plan)
    problems += inactive_problems(plan)
    problems += depth_problems(plan)
    problems += offense_problems(plan)
    if not problems:
        found, _ = sheet_problems(plan)
        problems += found
    problems += clean_problems(plan)
    from scripts import render_game_week
    try:
        wk = render_game_week.Week(plan.root, week)
        if wk.pages.briefing.is_file():
            old = wk.pages.briefing.read_text(encoding="utf-8")
            if render_game_week.undated(old) != render_game_week.undated(render_game_week.briefing(wk)):
                problems.append("Game Week Briefing: the situation has changed since it went out; the staff issues "
                                "a new one before the plan is set")
    except ValueError as exc:
        problems.append("Game Week Briefing: %s" % exc)
    from runtime import decision_queue
    holder = plan.job.get("holder")
    for item in decision_queue.unresolved(decision_queue.load(plan.root)):
        held = [b for b in item.get("blocks") or () if b.get("season") == season and b.get("week") == week]
        if held and item.get("owner") != holder:
            plan.notes.append("Still open with %s: %s" % (current_job.party_name(plan.job, item["owner"]),
                                                          item["title"]))
        for wait in item.get("waits_on") or () if held else ():
            if wait.get("date") and wait["date"] >= plan.master.isoformat():
                when = date.fromisoformat(wait["date"])
                plan.notes.append("Still to come: %s (%s %d)" % (wait["what"].split(";")[0], when.strftime("%B"),
                                                                 when.day))
    return problems, plan.notes, plan


def place_upload(root, season, week, source):
    """An uploaded .md or .txt file with the Game Plan's headings becomes the week's page."""
    source = Path(source)
    if source.suffix.lower() not in (".md", ".txt"):
        raise ValueError("an uploaded Game Plan is a .md or .txt file")
    text = source.read_text(encoding="utf-8")
    _, problems = game_plan.split(text)
    missing = [p for p in problems if p.endswith("the heading is missing")]
    if len(missing) == len(game_plan.SECTIONS):
        raise ValueError("the uploaded file has none of the Game Plan's headings")
    page = week_pages(season, week, root).plan
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    return page


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("week", type=int)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.file is not None:
        try:
            place_upload(args.root, args.season, args.week, args.file)
        except (OSError, ValueError) as exc:
            print("GAME PLAN: NOT COMPLETE\n- %s" % exc)
            return 1
    problems, notes, _ = check(args.root, args.season, args.week)
    if problems:
        print("GAME PLAN: NOT COMPLETE")
        for problem in problems:
            print("- " + problem)
    else:
        print("GAME PLAN: COMPLETE  Week %d, %d" % (args.week, args.season))
    for note in notes:
        print("  note: " + note)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
