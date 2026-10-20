#!/usr/bin/env python3
"""Check Stone's Game Plan before anything runs (rebuild step 4).

  python scripts/check_game_plan.py WEEK --season YEAR [--file PATH] [--root PATH]

A postseason week (18 to 21) is a playoff round: its game is found in the
bracket (runtime/game_weeks.py), never before the bracket sets it, and its page
is in the round's folder under the postseason folder.

Reads the week's Game Plan page (runtime/game_plan.py) and says exactly what
is missing or invalid, in football words, for example "Inactives: 6 named, 7
needed", "Red zone: 'Flood Sail' is not in the active playbook" or
"Inactives: Ace Sanders is not on the roster". It exits 1 until the page is
complete, and 0 when it is. With --file, an uploaded .md or .txt file with
the same headings becomes the week's Game Plan page first (the page stays as
the record of his decision); nothing else is written, and an upload for a
week that is played, paused or already built for the game is refused before
anything is written.

What it checks:

- the week is open for a plan: not played, not paused, and its game not
  already built from an applied plan (the inputs or results of the week);
- every heading is present and has something under it (a choice, None,
  Same as Week N or, for the three decision rules and the inactives,
  Standing rule), and no section other than the offense and the defense
  carries a subheading;
- the inactives: the right number, every one on the active roster, every
  player out for the game among them (his medical instruction, or a closed
  game's injury inside its projected return, as the game reads them; an
  availability note the staff cannot read is a problem), and no healthy
  player when more are out than the count; "Standing rule" applies his
  standing inactive rule to the week, and "Same as Week N" carries that
  week's applied list;
- the depth chart changes: a group's new order holds exactly the players now
  in that group; a game role goes to a player of its group (the starter a
  quarterback, the kicker a kicker, the punter a punter, the nickel and the
  outside reserve corner defensive backs), the starter, kicker and punter go
  to the head of their group, and the defensive-back seats stay valid;
- the offense: every word of every call is the active offensive playbook's
  (its concept, personnel, formation, motion, protection, name and tags;
  runtime/offensive_words.py, read through the playbook lock), every
  situation a call names is one of the call sheet's;
- the decision rules: "Same as Week N" carries a rule that week froze (the
  two-point and kickoff rules are required for the game), and with Stone's
  standing fourth-down rule in force a week that froze none is not carried
  silently;
- the call sheet the page would freeze, under the existing validators
  (runtime/call_families.sheet_errors, runtime/scoring_decisions.sheet_errors
  and input_policies, runtime/defensive_calls.sheet_errors and
  source_errors), so a page that passes here applies and builds cleanly;
- the page is clean (runtime/clean_pages.py);
- the Game Week Briefing is current (a briefing the situation has overtaken
  is re-issued first; the settlement of the week's own items by this page is
  not a change of situation).

Open items with other people that hold the week, and medical exams still to
come (each once), are listed as notes; they do not fail the check, and a
complete page is applied once no exam its items wait on is still to come
(scripts/apply_game_plan.waiting). A page that has changed since it was
applied passes as complete but is reported "not yet set" (exit 1) until it
is applied again. Nothing here moves time or creates
an event. scripts/apply_game_plan.py applies a page that passes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import call_families, call_situations as cs, current_job, game_plan, offensive_words  # noqa: E402
from runtime import roster as roster_record  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

JAX = "Jacksonville Jaguars"
STATUS_WORDS = {"two_point": "Two-point tries", "kickoff": "Kickoffs", "fourth_down": "Fourth downs"}
# The situations a call may name (the page's list, as call_situations keys them).
KNOWN_MENUS = frozenset(cs.menu_key(m) for m in game_plan.CALL_SITUATIONS)
MENU_WORDS = {cs.HIGH_RED: "Red zone", cs.LOW_RED: "Red zone", cs.GOAL_LINE: "Red zone", "red-zone": "Red zone",
              cs.NORMAL: "Normal downs", cs.SECOND_LONG: "Second and long", cs.THIRD_SHORT: "Third down",
              cs.THIRD_MEDIUM: "Third down", cs.THIRD_LONG: "Third down", cs.BACKED_UP: "Backed up",
              cs.TWO_MINUTE: "Two-minute", cs.PRESS: "PRESS sequence", cs.FOUR_MINUTE: "Four-minute",
              cs.SUDDEN_CHANGE: "Sudden change", cs.OPENING: "Opening sequence", cs.TWO_POINT: "Two-point tries",
              "final-play-of-half": "Final play of the half", "empty": "Empty"}
# The page's own headings a Situations cell may borrow, and the situations each stands for.
HEADING_HINTS = {"third-down": "third and short, third and medium or third and long",
                 "final-play-of-the-half": "final play of half", "receiver-arrangement": "the situation the "
                 "arrangement is for", "normal-downs": "normal down"}
CHECK_WORDS = ((re.compile(r"system words?: (\w+)"), "'%s' is not a football word"),
               (re.compile(r"internal code: (\S+)"), "'%s' reads as an internal code"),
               (re.compile(r"internal identifier: (\S+)"), "'%s' reads as an internal identifier"),
               (re.compile(r"player identifier: (\S+)"), "'%s' reads as a player identifier"),
               (re.compile(r"system name: (\S+)"), "'%s' reads as a system name"),
               (re.compile(r"script or module name: (\S+)"), "'%s' names a script or module"),
               (re.compile(r"link to a system file: (\S+)"), "the link to %s points into the system files"),
               (re.compile(r"version label: (.+)"), "'%s' reads as a version label"),
               (re.compile(r"policy note or disclaimer: (.+)"), "'%s' reads as a disclaimer, not football"),
               (re.compile(r"entry number: (.+)"), "'%s' reads as a record number"),
               (re.compile(r"digest: (\S+)"), "'%s' reads as a file digest"),
               (re.compile(r"markup: (.+)"), "%s is markup"),
               (re.compile(r"code span"), "a code span (`) is not football writing"))
# A game role and the position group it belongs to; the starter, kicker and punter head that group.
ROLE_GROUP = {"passer": "QB", "placekicker": "K", "punt": "P", "nickel": "DB", "outside_reserve": "DB"}
HEAD_ROLES = ("passer", "placekicker", "punt")
ROLE_WORDS = {v: k for k, v in game_plan.ROLES.items()}
# Stone's standing inactive rule names five healthy players (state/current_job.json, the
# instruction on the inactives: "each of the five largest healthy position groups").
RULE_GROUPS = 5


def page_digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Plan:
    """A week's Game Plan and what checking it reads."""

    def __init__(self, root, season, week):
        self.root = Path(root).resolve()
        self.season, self.week = season, week
        self.paths = SeasonPaths(season, self.root)
        self.master = master_date(self.root)
        self.job = current_job.load(self.root)
        # A playoff game is found in the bracket (runtime/game_weeks.py), never before it is set.
        from runtime import game_weeks
        self.postseason = game_weeks.is_postseason(self.paths, week)
        self.unset = None
        try:
            self.game = game_weeks.club_game(self.paths, week, JAX)
        except game_weeks.NotSet as exc:
            self.game, self.unset = None, str(exc)
        self.pages = week_pages(season, week, self.root, postseason=self.postseason)
        self.roster = roster_record.load(self.paths.roster)
        self.chart = json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))
        self.text = self.pages.plan.read_text(encoding="utf-8") if self.pages.plan.is_file() else None
        self.choices, self.problems = (game_plan.parse(self.text) if self.text is not None else ({}, []))
        self.applied = applied_record(self.season, self.week, self.root)
        self.notes = []
        self.changed_since_applied = None
        self._outs = None

    def rel(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def label(self):
        """The game's name: "Week 6", or its playoff round ("Wild Card")."""
        from runtime import game_weeks
        return game_weeks.round_name(self.week) if self.postseason else "Week %d" % self.week

    def active(self):
        return [p["name"] for p in roster_record.players(self.roster, ("active",))]

    def needed(self):
        from runtime.rules import RULES
        return len(self.active()) - RULES.active_limit

    def carried(self):
        """{week: frozen sheet} for every "Same as Week N" the page writes."""
        out = {}
        for key, value in self.choices.items():
            if isinstance(value, dict) and "same_as" in value:
                path = week_pages(self.season, value["same_as"], self.root).call_sheet
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
        part = "postseason %s" % self.label() if self.postseason else "regular season Week %d" % self.week
        return "%d %s, %s at %s, %s %d, %d" % (
            self.season, part, place(g["away"]), place(g["home"]), d.strftime("%B"), d.day, d.year)

    def frame(self):
        from runtime.defensive_calls import active_defensive_book
        page = self.rel(self.pages.plan)
        today = self.master.isoformat()
        provenance = ("Stone's %s Game Plan (%s), checked by scripts/check_game_plan.py and applied by "
                      "scripts/apply_game_plan.py on %s: the calls, the situation menus, the decision rules and the "
                      "defensive sheet as the page writes them, each defensive row citing the page's own line."
                      % (self.label(), page, today))
        return game_plan.page_frame(page, self.event(), "%s, from Stone's %s Game Plan after its check passed; "
                                    "before any draw" % (today, self.label()), provenance, JAX,
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

    def receipts_before(self):
        """The closed games before this week (the game path's injury window reads them)."""
        from scripts.render_season_stats import load_receipts
        out = []
        for folder in (self.paths.receipts, self.paths.postseason_receipts):
            if folder.is_dir():
                out += [r for r in load_receipts(folder) if int(r["week"]) < self.week]
        return out

    def outs(self):
        """({player: why}, problems): every active player out for the game as the game reads it
        (runtime.week_inputs.jacksonville_input): his roster availability does not clear him for game
        day, or a closed game's injury holds him inside its projected return. A note the staff cannot
        read is a problem, never a clearance."""
        if self._outs is None:
            from runtime.week_inputs import injured_out, roster_available
            game_day = date.fromisoformat(self.game["date"])
            injured = injured_out(self.receipts_before(), game_day, self.season)
            out, problems = {}, []
            for p in roster_record.players(self.roster, ("active",)):
                note = p.get("availability") or ""
                try:
                    cleared = roster_available(note, game_day, self.season)
                except ValueError:
                    problems.append("Inactives: %s's medical status (%r) is not recorded in a form the staff can "
                                    "read; the medical staff restates it before the plan is set" % (p["name"], note))
                    continue
                if not cleared:
                    out[p["name"]] = "out on his medical instruction for the game"
                elif p["name"] in injured:
                    out[p["name"]] = "out for the game inside his projected return from a game injury"
            self._outs = (out, problems)
        return self._outs

    def inactives(self):
        """The players the page lists inactive: named, carried from Week N's applied list, or
        Stone's standing rule applied to the week; None when they cannot be set."""
        value = self.choices.get("inactives")
        if isinstance(value, dict) and "same_as" in value:
            return carried_inactives(self, value["same_as"])
        if isinstance(value, dict) and value.get("standing"):
            players, _ = standing_inactives(self)
            return players
        return list(value["players"]) if isinstance(value, dict) else None


def applied_record(season, week, root):
    """The week's applied Game Plan record, or None."""
    return game_plan.applied_record(week_pages(season, week, root).applied)


def carried_inactives(plan, week):
    """Week ``week``'s inactives as set: the week's inactives record (runtime/decisions.WeekPages.
    inactives), else the chart's latest list when it is that week's."""
    record = game_plan.applied_record(week_pages(plan.season, week, plan.root).inactives)
    if record is not None:
        return list(record.get("players") or [])
    listed = plan.chart.get("game_day_inactives") or {}
    return list(listed.get("players") or []) if listed.get("week") == week else None


def inactive_rule(plan):
    """Stone's standing inactive rule in force, or None."""
    return next((i for i in current_job.instructions(plan.job) if i.get("subject") == "inactives"), None)


def standing_inactives(plan):
    """(players, problems): Stone's standing inactive rule for the week: every player out for the game,
    and the deepest healthy reserve on the chart in each of the five largest healthy position groups,
    never below a legal game-day unit. When the week sits more healthy players than five, the page
    names the others below Standing rule, and they follow the rule's five. Where its words do not
    settle the week (fewer than five healthy places, a tie for the fifth-largest group, a group left
    short) or the page names the wrong number besides it, it says so."""
    if inactive_rule(plan) is None:
        return None, ["Inactives: no standing inactive rule is in force; name the players"]
    value = plan.choices.get("inactives")
    named = list(value.get("players") or []) if isinstance(value, dict) else []
    outs, _ = plan.outs()
    needed = plan.needed()
    healthy_needed = needed - len(outs)
    if healthy_needed < RULE_GROUPS:
        return None, ["Inactives: your standing rule sits %d healthy players, but this week %d sit with %d out "
                      "for the game, so %d healthy; name the players" % (RULE_GROUPS, max(needed, len(outs)),
                                                                       len(outs), max(healthy_needed, 0))]
    others = healthy_needed - RULE_GROUPS
    if len(named) != others:
        if not others:
            return None, ["Inactives: your standing rule makes the %d this week (%d out for the game and its %d "
                          "healthy players); write Standing rule alone, without the %d named"
                          % (needed, len(outs), RULE_GROUPS, len(named))]
        return None, ["Inactives: your standing rule sits %d healthy players, but this week %d sit with %d out for "
                      "the game, so %d healthy; name the other %d in the table below Standing rule (%d named)"
                      % (RULE_GROUPS, needed, len(outs), healthy_needed, others, len(named))]
    active = set(plan.active())
    groups = []
    for group, order in (plan.chart.get("depth") or {}).items():
        healthy = [p for p in order if p in active and p not in outs]
        if healthy:
            groups.append((group, healthy))
    groups.sort(key=lambda g: -len(g[1]))
    if len(groups) > RULE_GROUPS and len(groups[RULE_GROUPS - 1][1]) == len(groups[RULE_GROUPS][1]):
        return None, ["Inactives: your standing rule's five largest healthy groups are not settled this week (%s "
                      "and %s both have %d healthy players); name the players"
                      % (groups[RULE_GROUPS - 1][0], groups[RULE_GROUPS][0], len(groups[RULE_GROUPS][1]))]
    picks = [healthy[-1] for _, healthy in groups[:RULE_GROUPS]]
    already = [p for p in named if p in picks]
    if already:
        return None, ["Inactives: %s already sits by your standing rule; name another" % p for p in already]
    from runtime.usage import lineup_errors
    positions = plan.chart.get("positions") or {}
    dressed = [p for p in plan.active() if p not in outs and p not in picks and p not in named]
    short = lineup_errors([type("Row", (), {"position": positions.get(p)})() for p in dressed])
    if short:
        return None, ["Inactives: your standing rule would leave the game-day unit short (%s); name the players"
                      % "; ".join(short)]
    return [p for p in plan.active() if p in outs] + picks + named, []


def inactive_ask(plan):
    """What the week's inactives ask of Stone, in football words: how many sit, how many are out for
    the game on the medical staff's projections, and what his standing rule leaves to him; None
    when a medical note cannot be read (the briefing then asks only who does not dress)."""
    outs, problems = plan.outs()
    if problems:
        return None
    needed, active = plan.needed(), len(plan.active())
    out = ("on the medical staff's projections no one is out for the game" if not outs else
           "on the medical staff's projections %d %s out for the game" % (len(outs), "is" if len(outs) == 1 else "are"))
    head = "who does not dress: %d of the %d; %s" % (needed, active, out)
    if len(outs) >= needed:
        return head + ", so the list is %s" % ("those players" if len(outs) > 1 else "that player")
    if inactive_rule(plan) is None:
        return head + ", so you name %d healthy players" % (needed - len(outs))
    healthy = needed - len(outs)
    if healthy == RULE_GROUPS:
        return head + ", so your standing rule sits the other five and settles the list"
    if healthy > RULE_GROUPS:
        return head + ", so your standing rule sits five healthy players and leaves %d for you to name" % (
            healthy - RULE_GROUPS)
    return head + (", so %d healthy players sit, fewer than the five your standing rule sits, and you name them"
                   % healthy)


# ---------------------------------------------------------------- the checks
def section_of(text, line):
    """The heading a page line sits under."""
    current = "The page"
    for number, raw in enumerate(text.splitlines(), 1):
        if number > line:
            break
        if raw.startswith("## "):
            current = raw[3:].strip()
        elif raw.startswith("### ") and current.split(",")[0] in game_plan.WITH_SUBSECTIONS:
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
                out.append("Inactives: none named, %d needed" % plan.needed())
                continue
            hint = {"Offense": "write the calls and situations",
                    "Defense": "write who calls it and the calls by situation, or None",
                    "Fourth downs": "write your rules, Standing rule or None for your live call",
                    "Two-point tries": "write your rules or Standing rule",
                    "Kickoffs": "write your rules or Standing rule"}.get(name, "write it, or None")
            out.append("%s: nothing written; %s" % (name, hint))
    carried = plan.carried()
    for key, value in plan.choices.items():
        if isinstance(value, dict) and "same_as" in value:
            week = value["same_as"]
            name = next(n for n, k in game_plan.SECTION_KEYS.items() if k == key)
            if week >= plan.week:
                out.append("%s: Same as Week %d names a week that has not come before this one" % (name, week))
            elif key in ("offense", "fourth_down", "two_point", "kickoff", "defense", "notes") \
                    and week not in carried:
                out.append("%s: Week %d has no frozen call sheet to carry" % (name, week))
            elif key in ("two_point", "kickoff") and key not in (carried[week].get("decisions") or {}):
                out.append("%s: Week %d set no %s rule, and the game needs one; write your rules with Otherwise, "
                           "or Standing rule" % (name, week, "two-point" if key == "two_point" else "kickoff"))
            elif key == "fourth_down" and key not in (carried[week].get("decisions") or {}) \
                    and "fourth_down" in plan.standing():
                out.append("Fourth downs: Week %d froze no fourth-down rule, so Same as Week %d would leave every "
                           "fourth down to your live call although your standing rule is in force; write Standing "
                           "rule, None for your live call, or your rules" % (week, week))
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
    active = plan.active()
    needed = plan.needed()
    outs, out = plan.outs()
    out = list(out)
    if isinstance(value, dict) and value.get("standing"):
        players, found = standing_inactives(plan)
        if players is None:
            return out + found
    else:
        players = plan.inactives()
    if players is None:
        return out + ["Inactives: Week %d's list is no longer on file; name the %d" % (value["same_as"], needed)]
    want = max(needed, len(outs))
    if len(players) != want:
        if len(outs) > needed:
            out.append("Inactives: %d named; %d are out for the game, more than the %d inactive places, so the "
                       "list is those %d" % (len(players), len(outs), needed, len(outs)))
        else:
            out.append("Inactives: %d named, %d needed" % (len(players), needed))
    for name in sorted({p for p in players if players.count(p) > 1}):
        out.append("Inactives: %s is named twice" % name)
    on_lists = {p["name"]: p for p in roster_record.players(plan.roster)}
    for name in players:
        if name not in on_lists:
            out.append("Inactives: %s is not on the roster" % name)
        elif name not in active:
            out.append("Inactives: %s is not on the active roster (%s)" % (name, on_lists[name]["status"]))
    for name in active:
        if name in outs and name not in players:
            out.append("Inactives: %s is %s and must be among them" % (name, outs[name]))
    if len(outs) >= needed:
        for name in players:
            if name in active and name not in outs:
                out.append("Inactives: %s is healthy; with %d out for the game, no healthy player sits"
                           % (name, len(outs)))
    return out


def changed_chart(chart, depth):
    """(chart, changes): a copy of the game chart with the page's depth changes made, and each change in
    football words. A starter, kicker or punter goes to the head of his group's order."""
    chart = copy.deepcopy(chart)
    changes = []
    depth = depth if isinstance(depth, dict) and "same_as" not in depth else {}
    orders = {g: list(o) for g, o in (depth.get("orders") or {}).items()}
    for role, player in (depth.get("roles") or {}).items():
        group = ROLE_GROUP.get(role)
        if role in HEAD_ROLES and group in (chart.get("depth") or {}) and group not in orders \
                and player in chart["depth"][group]:
            orders[group] = [player] + [p for p in chart["depth"][group] if p != player]
    for group, order in orders.items():
        if chart.get("depth", {}).get(group) != order:
            chart["depth"][group] = list(order)
            changes.append("%s order: %s" % (group, ", ".join(order)))
    for role, player in (depth.get("roles") or {}).items():
        roles = chart.setdefault("roles", {})
        holders = [p for p, r in roles.items() if role in (r or ())]
        if holders != [player]:
            for p in holders:
                roles[p] = [r for r in roles[p] if r != role]
                if not roles[p]:
                    del roles[p]
            roles.setdefault(player, []).append(role)
            changes.append("%s: %s" % (ROLE_WORDS.get(role, role), player))
    return chart, changes


def db_words(error):
    """runtime.week_inputs.db_role_errors in the page's words."""
    words = {"nickel": "Nickel", "outside_reserve": "Outside reserve corner"}
    m = re.match(r"the (\w+) role names (.+), who is not on the chart's defensive-back list", error)
    if m:
        return "the %s goes to a defensive back; %s is not one" % (words.get(m[1], m[1]), m[2])
    m = re.match(r"the outside_reserve role names (.+), who is not a corner", error)
    if m:
        return "the Outside reserve corner goes to a corner; %s is not one" % m[1]
    m = re.match(r"the nickel and outside_reserve roles name the same player \((.+)\)", error)
    if m:
        return "%s cannot take both the Nickel and the Outside reserve corner seats" % m[1]
    m = re.match(r"the game depth chart names no (\w+) role", error)
    if m:
        return "the chart needs a %s" % words.get(m[1], m[1])
    m = re.match(r"the game depth chart names \d+ (\w+) roles \((.+)\)", error)
    if m:
        return "one player takes the %s seat, not %s" % (words.get(m[1], m[1]), m[2])
    return error.replace("_", " ")


def depth_problems(plan):
    value = plan.choices.get("depth")
    if not isinstance(value, dict) or "same_as" in value:
        return []
    out = []
    depth = plan.chart.get("depth") or {}
    orders = value.get("orders") or {}
    for group, order in orders.items():
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
        group = ROLE_GROUP.get(role)
        if role not in game_plan.ROLES.values():
            out.append("Depth chart changes: %r is not a game role (%s)" % (role, ", ".join(game_plan.ROLES)))
        elif name not in placed:
            out.append("Depth chart changes: %s is not on the chart for the %s role" % (name, ROLE_WORDS[role]))
        elif group is not None and name not in depth.get(group, ()):
            out.append("Depth chart changes: the %s role goes to a player of the %s group; %s is not one"
                       % (ROLE_WORDS[role], group, name))
        elif role in HEAD_ROLES and group in orders and orders[group] and orders[group][0] != name:
            out.append("Depth chart changes: the %s role gives %s, but your %s order puts %s first"
                       % (ROLE_WORDS[role], name, group, orders[group][0]))
    if not out:
        from runtime.week_inputs import db_role_errors
        trial, _ = changed_chart(plan.chart, value)
        before = set(db_role_errors(plan.chart))
        out += ["Depth chart changes: %s" % db_words(e) for e in db_role_errors(trial) if e not in before]
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
    players = [p["name"] for p in roster_record.players(plan.roster)]
    for call in calls:
        menus = [cs.menu_key(m) for m in call.get("menus") or ()]
        place = next((MENU_WORDS[m] for m in menus if m in MENU_WORDS), "Offense, Calls")
        family = call.get("family")
        if not family:
            out.append("%s: %r names no concept" % (place, call["name"]))
        elif offensive_words.concept(family) is None:
            out.append("%s: %r is not in the active playbook" % (place, family))
        for problem in offensive_words.call_errors(dict(call, family=None), players):
            out.append("%s, %r: %s" % (place, call["name"], problem))
        for raw, key in zip(call.get("menus") or (), menus):
            if key not in KNOWN_MENUS:
                hint = HEADING_HINTS.get(key)
                out.append("Offense, Calls, %r: %r is not a situation of the call sheet%s" % (
                    call["name"], raw, "; write %s" % hint if hint else " (%s)" % ", ".join(game_plan.CALL_SITUATIONS)))
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
    faults = scoring_decisions.sheet_errors(sheet.get("decisions"), names)
    for error in faults:
        kind = next((k for k in STATUS_WORDS if "decisions.%s" % k in error), None)
        out.append("%s: %s" % (STATUS_WORDS.get(kind, "Decision rules"), error))
    if not faults:
        # What the build reads (runtime.week_inputs.jacksonville_input): every kind the game decides
        # needs its block.
        try:
            scoring_decisions.input_policies(sheet.get("decisions"), scoring_decisions.live_kinds(), names)
        except ValueError as exc:
            missing = [k for k in scoring_decisions.live_kinds() if k not in (sheet.get("decisions") or {})
                       and k in STATUS_WORDS]
            out += ["%s: the game needs a rule (your rules with Otherwise, or Standing rule)" % STATUS_WORDS[k]
                    for k in missing] or ["Decision rules: %s" % exc]
    ds = sheet.get("defensive_call_sheet")
    if ds is not None:
        faults = defensive_calls.sheet_errors(ds)
        if not faults:
            faults = defensive_calls.source_errors(ds, plan.root, plan.season)
        out += ["Defense%s" % defensive_words(e, ds) for e in faults]
    return out, sheet


DEF_KINDS = {"package": "package", "front": "front", "coverage": "coverage", "pressure": "pressure", "tag": "tag",
             "strength": "strength"}


def defensive_words(error, sheet=None):
    """runtime.defensive_calls' sheet and source problems in the page's words (", <where>: <what>")."""
    from runtime import defensive_calls
    rows = {r.get("id"): r for r in (sheet or {}).get("rows") or () if isinstance(r, dict)}

    def where(rid):
        row = rows.get(rid) or {}
        label = game_plan.DEF_MENU_WORDS.get(row.get("menu")) or (row.get("source") or {}).get("text") or rid
        return ", Calls by situation, %s" % label
    m = re.match(r"row (\S+): (\w+) '([^']+)' is not a word of the active defensive book", error)
    if m:
        return "%s: '%s' is not a %s in the active defensive playbook" % (where(m[1]), m[3], m[2])
    m = re.match(r"row (\S+): (\w+) '([^']+)' is not on the practiced menu", error)
    if m:
        return "%s: '%s' was not practiced this week (add it to Practiced this week)" % (where(m[1]), m[3])
    m = re.match(r"practiced\.(\w+): '([^']+)' is not a word of the active defensive book", error)
    if m:
        return ", Practiced this week: '%s' is not one of the active defensive playbook's %s" % (m[2], m[1])
    m = re.match(r"practiced\.(\w+): '([^']+)' is on none of the practiced menu's cited lines", error)
    if m:
        return ", Practiced this week: '%s' is not written on the menu's lines" % m[2]
    if error.startswith("rush_rule.rule must read"):
        return ", Rush rule: write '%s'" % game_plan.RUSH_CHOICE
    if error.startswith("rush_rule"):
        return ", Rush rule: write the rush rule ('%s')" % game_plan.RUSH_CHOICE
    if error.startswith("practiced"):
        return ", Practiced this week: write the menu practiced this week, one row per list"
    if error.startswith("caller") or error == "caller must be a nonempty string":
        return ": write who calls it (Who calls it: name)"
    if error.startswith("rows must be a nonempty list"):
        return ", Calls by situation: write at least one call"
    m = re.match(r"row (\S+): a situation row needs a menu key", error)
    if m:
        return "%s: a Situation row needs its situation (%s)" % (where(m[1]),
                                                                ", ".join(game_plan.DEF_MENU_WORDS.values()))
    m = re.match(r"row (\S+): menu (\S+) already labels row (\S+)", error)
    if m:
        return ", Calls by situation: %s has two Situation rows; one call per situation" % (
            game_plan.DEF_MENU_WORDS.get(m[2], m[2]))
    m = re.match(r"row (\S+): a situation row needs its call", error)
    if m:
        return "%s: the row names no package, front, coverage or pressure" % where(m[1])
    m = re.match(r"row (\S+): a (\w+) row never labels and takes no menu", error)
    if m:
        return "%s: a %s row has no situation; leave Situation empty" % (where(m[1]),
                                                                        game_plan.KIND_WORDS.get(m[2], m[2]))
    m = re.match(r"row (\S+): call names no package, front, coverage or pressure", error)
    if m:
        return "%s: the row names no package, front, coverage or pressure" % where(m[1])
    m = re.match(r"row (\S+): a strength declaration needs its front", error)
    if m:
        return "%s: a strength goes with its front" % where(m[1])
    m = re.match(r"row (\S+): the (\S+) tag belongs to the replace family", error)
    if m:
        return "%s: the %s tag goes with the %s pressure" % (where(m[1]), m[2],
                                                           defensive_calls.PRESSURE_FAMILIES["replace"])
    m = re.match(r"row (\S+): an interior mug is encoded", error)
    if m:
        return "%s: a row that names the mug takes the %s pressure and the mug tag" % (
            where(m[1]), defensive_calls.PRESSURE_FAMILIES["replace"])
    m = re.match(r"row (\S+): (\w+) '([^']+)' is not on its cited line", error)
    if m:
        return "%s: '%s' is in the row's call but not in its words" % (where(m[1]), m[3])
    m = re.match(r"row (\S+): (.+)", error)
    if m:
        return "%s: %s" % (where(m[1]), m[2].replace("_", " "))
    return ": %s" % error.replace("_", " ")


def closed_for_changes(root, season, week):
    """Why the week's Game Plan can no longer change, or None: the week is played, a game is
    paused (nothing that a game reads changes during a pause), or the week's game has been built
    from the applied plan (its inputs or results are on file)."""
    paths = SeasonPaths(season, root)
    from runtime import game_weeks
    name = game_weeks.round_name(week) if game_weeks.is_postseason(paths, week) else "Week %d" % week
    played = [p for folder in (paths.receipts, paths.postseason_receipts) if folder.is_dir()
              for p in folder.glob("week_%02d_*.json" % week)]
    if any(JAX in json.loads(p.read_text(encoding="utf-8"))["matchup"] for p in played):
        return "%s has been played; its plan stays as it was set" % name
    from scripts.render_career_views import paused_games
    if paused_games(root):
        return "A game is paused; the plan stays as it was set until the game is finished"
    if any(paths.cache(week, kind).exists() for kind in ("inputs", "results")):
        return ("%s: the game has been built from the applied plan; the plan stays as it was set unless the "
                "staff withdraws that build" % name)
    return None


def check(root, season, week):
    """(problems, notes, plan): what is missing or invalid, and what is still to come."""
    plan = Plan(root, season, week)
    if plan.game is None:
        if plan.unset:
            return ["%s: Jacksonville's game is not set yet: %s" % (plan.label(), plan.unset)], [], plan
        return ["%s: Jacksonville has no game %s" % (plan.label(), "in this round" if plan.postseason
                                                     else "this week")], [], plan
    refused = closed_for_changes(plan.root, season, week)
    if refused:
        return [refused], [], plan
    if plan.text is None:
        return ["%s: no Game Plan page (%s)" % (plan.label(), plan.rel(plan.pages.plan))], [], plan
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
        if wk.pages.briefing.is_file() and render_game_week.overtaken(wk, wk.pages.briefing.read_text(encoding="utf-8")):
            problems.append("Game Week Briefing: the situation has changed since it went out; the staff issues "
                            "a new one before the plan is set")
    except ValueError as exc:
        problems.append("Game Week Briefing: %s" % exc)
    if plan.applied is not None and plan.applied.get("page_sha256") != page_digest(plan.text):
        when = date.fromisoformat(plan.applied["applied"])
        plan.changed_since_applied = "%s %d, %d" % (when.strftime("%B"), when.day, when.year)
    from runtime import decision_queue
    from runtime.decisions import waits_ahead
    holder = plan.job.get("holder")
    queue = decision_queue.load(plan.root)
    for item in decision_queue.unresolved(queue):
        held = [b for b in item.get("blocks") or () if b.get("season") == season and b.get("week") == week]
        if held and item.get("owner") != holder:
            plan.notes.append("Still open with %s: %s" % (current_job.party_name(plan.job, item["owner"]),
                                                          item["title"]))
        for wait in waits_ahead(item, plan.master) if held else ():
            when = date.fromisoformat(wait["date"]) if wait.get("date") else None
            note = "Still to come: %s%s" % (wait["what"].split(";")[0],
                                            " (%s %d)" % (when.strftime("%B"), when.day) if when else "")
            if note not in plan.notes:
                plan.notes.append(note)
    if not problems:
        from scripts.apply_game_plan import waiting
        if waiting(plan):
            # Complete, and set from the page once the exams his items wait on are held (the apply waits).
            plan.notes.append("The page is complete; it is set for the game once the exams still to come are "
                              "held, when the staff applies it")
    return problems, plan.notes, plan


def place_upload(root, season, week, source):
    """An uploaded .md or .txt file with the Game Plan's headings becomes the week's page; refused,
    with nothing written, for a week whose plan can no longer change."""
    source = Path(source)
    if source.suffix.lower() not in (".md", ".txt"):
        raise ValueError("an uploaded Game Plan is a .md or .txt file")
    refused = closed_for_changes(Path(root).resolve(), season, week)
    if refused:
        raise ValueError(refused)
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
    problems, notes, plan = check(args.root, args.season, args.week)
    if problems:
        print("GAME PLAN: NOT COMPLETE")
        for problem in problems:
            print("- " + problem)
    elif plan.changed_since_applied:
        print("GAME PLAN: COMPLETE, NOT YET SET  %s, %d" % (plan.label(), args.season))
        print("- The page has changed since it was applied on %s; apply it again to set the game from it"
              % plan.changed_since_applied)
    else:
        print("GAME PLAN: COMPLETE  %s, %d" % (plan.label(), args.season))
    for note in notes:
        print("  note: " + note)
    return 1 if problems or plan.changed_since_applied else 0


if __name__ == "__main__":
    raise SystemExit(main())
