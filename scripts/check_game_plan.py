#!/usr/bin/env python3
"""Check Stone's Game Plan before anything runs (game week version 2).

  python scripts/check_game_plan.py WEEK --season YEAR [--file PATH] [--root PATH]

A postseason week (18 to 21) is a playoff round: its game is found in the
bracket (runtime/game_weeks.py), never before the bracket sets it, and its page
is in the round's folder under the postseason folder.

Reads the week's Game Plan page (runtime/game_plan.py, the layout of
foundation/templates/game_week/game_plan_template.md) and says exactly what
is missing or invalid, in football words, for example "Inactives: 6 named, 7
needed", "Offense, Primary calls: Y-Cross could be 12 Trey, Y-Cross, SOLID or
12 Trey, Y-Cross, HALF; name the one you want" or "Inactives: Ace Sanders is
not on the roster". It exits 1 until the page is complete, and 0 when it is.
With --file, an uploaded .md or .txt file with the same headings becomes the
week's Game Plan page first (the page stays as the record of his decision);
nothing else is written, and an upload for a week that is played, paused or
already built for the game is refused before anything is written.

What it checks:

- the week is open for a plan: not played, not paused, and its game not
  already built from an applied plan (the inputs or results of the week);
- every heading and every line is present and answered: a line left empty is
  unanswered (No change and None are answers; silence never is), the Primary
  calls table holds a call unless the baseline carries a week, and no section
  carries a heading of its own the page does not have (the practice table is
  information for the staff and never a condition on the plan);
- the briefing he answers is the current one (its date on "Briefing used",
  and from the second issue of a day its revision, as the issue record
  numbers them), and the briefing has not been overtaken by the situation (a
  briefing the situation has overtaken is re-issued first; the settlement of
  the week's own items by this page is not a change of situation);
- each caller line names who calls that phase on the staff page (a change of
  caller is recorded with the staff first);
- the inactives: the right number, every one on the active roster, every
  player out for the game among them (his medical instruction, or a closed
  game's injury inside its projected return, as the game reads them; an
  availability note the staff cannot read is a problem), and no healthy
  player when more are out than the count; "Standing rule" applies his
  standing inactive rule to the week (with the others he names after it),
  and "Carry Week N" carries that week's list as set; the standing rule reads
  the chart as the page's own depth changes leave it;
- the depth and role changes: a group's new order holds exactly the players
  now in that group; a game role goes to a player of its group (the starter a
  quarterback, the kicker a kicker, the punter a punter, the nickel and the
  outside reserve corner defensive backs), the starter, kicker and punter go
  to the head of their group, the defensive-back seats stay valid, and every
  role holder, new or carried on the chart, dresses (``role_problems``);
- the offense: the page compiles (runtime/game_plan.compile_sheet): each call
  is named by its full name (a shorter one is asked about, never resolved to
  a longer call) or is a new call read from its own words; any call of the
  active book may be named for any situation, whether or not the week's
  practice covered it (the user's ruling of October 20, 2026); a call kept as
  a special play is not also not available; every word of every call on the
  sheet is the active offensive playbook's (its concept, personnel,
  formation, motion, protection, name and tags; runtime/offensive_words.py,
  read through the playbook lock, which refuses a book whose range starts
  after the season); every call's personnel grouping can be fielded by the
  players who dress, and a variation naming a player needs him dressed;
- the decisions: "Carry Week N" or No change carries a rule that week froze
  (the two-point and kickoff rules are required for the game), and with
  Stone's standing fourth-down rule in force a week that froze none is not
  carried silently;
- the call sheet the page compiles to, under the existing validators
  (runtime/call_families.sheet_errors, runtime/scoring_decisions.sheet_errors
  and input_policies, runtime/defensive_calls.sheet_errors and
  source_errors), so a page that passes here applies and builds cleanly;
- the page is clean (runtime/clean_pages.py).

Open items with other people that hold the week, and medical exams still to
come (each once), are listed as notes; they do not fail the check, and a
complete page is applied once no exam its items wait on is still to come
(scripts/apply_game_plan.waiting). A page that has changed since it was
applied passes as complete but is reported "not yet set" (exit 1) until it
is applied again. A complete page shows back its opening calls in order and
the calls on each situation's list. Nothing here moves time or creates an
event.
scripts/apply_game_plan.py applies a page that passes.
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

from runtime import call_families, current_job, game_plan, offensive_words  # noqa: E402
from runtime import roster as roster_record  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.decisions import week_pages  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402

JAX = "Jacksonville Jaguars"
STATUS_WORDS = {"two_point": "Two-point tries", "kickoff": "Kickoffs and onside situations",
                "fourth_down": "Fourth downs"}
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
CALLER_PHASES = {"offense_caller": "offense", "defense_caller": "defense", "kicking_caller": "special_teams"}
# What a personnel grouping puts on the field (the active book's section 3): backs, tight ends,
# receivers by the grouping's two digits; 6OL a sixth lineman.
GROUP_NAMES = {"backs": "backs", "TE": "tight ends", "WR": "receivers", "OL": "offensive linemen"}


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
        self._compiled = None

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

    def earlier(self):
        """{week: frozen call sheet} of every earlier Jacksonville week whose plan is set."""
        out = {}
        for w in range(1, self.week):
            path = week_pages(self.season, w, self.root).call_sheet
            if path.is_file():
                out[w] = json.loads(path.read_text(encoding="utf-8"))
        return out

    carried = earlier

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

    def arrangement(self):
        """{phase: the name of who calls it} on the master date, from the current-job record."""
        out = {}
        for phase in current_job.PHASES:
            interval = current_job.interval_on(self.job, phase, self.master)
            if interval and interval.get("caller"):
                out[phase] = current_job.party_name(self.job, interval["caller"])
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
                      "scripts/apply_game_plan.py on %s: the calls, their situations and the opening calls, the "
                      "decision rules and the prepared defensive responses as the page writes them, each defensive "
                      "row citing the page's own line; the page's reasons are kept as his intent in the applied "
                      "plan record, not here." % (self.label(), page, today))
        return game_plan.page_frame(page, self.event(), "%s, from Stone's %s Game Plan after its check passed; "
                                    "before any draw" % (today, self.label()), provenance, JAX,
                                    active_defensive_book(self.root), self.week)

    def filled(self):
        """The decision kinds whose standing rule takes Tice's first call on each matching menu."""
        return {item.get("subject") for item in current_job.instructions(self.job)
                if item.get("prepared_calls") == game_plan.FIRST_ON_MENU}

    def compiled(self, frame=None):
        """(sheet or None, source map, problems) of the page (runtime/game_plan.compile_sheet), with
        Tice's first call on each matching menu filled into a standing fourth-down rule that takes them."""
        if self._compiled is None or frame is not None:
            sheet, source, problems = game_plan.compile_sheet(
                self.choices, frame or self.frame(), self.earlier(), self.standing(), self.arrangement())
            if sheet is not None:
                for kind in self.filled():
                    entry = self.choices.get(kind)
                    block = (sheet.get("decisions") or {}).get(kind)
                    if isinstance(entry, dict) and entry.get("standing") and block is not None:
                        prepared = game_plan.first_calls(sheet.get("offensive_call_sheet"))
                        if prepared:
                            block["prepared_calls"] = prepared
            if frame is not None:
                return sheet, source, problems
            self._compiled = (sheet, source, problems)
        return self._compiled

    def sheet(self):
        sheet, _, problems = self.compiled()
        if sheet is None:
            raise ValueError("; ".join(problems) or "the page does not compile")
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
        """The players the page lists inactive: named, carried from Week N's list as set, or Stone's
        standing rule applied to the week; None when they cannot be set."""
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
    never below a legal game-day unit, on the chart as the page's own depth changes leave it. When the
    week sits more healthy players than five, the page names the others after Standing rule, and they
    follow the rule's five. Where its words do not
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
                      "the game, so %d healthy; name the other %d after Standing rule on the Inactives line, with "
                      "commas between them (%d named)"
                      % (RULE_GROUPS, needed, len(outs), healthy_needed, others, len(named))]
    active = set(plan.active())
    groups = []
    # The chart as the page leaves it: a group he reorders on this page sits its new deepest reserve.
    chart, _ = changed_chart(plan.chart, plan.choices.get("depth"))
    for group, order in (chart.get("depth") or {}).items():
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
    positions = chart.get("positions") or {}
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
    """The heading (and subheading) a page line sits under."""
    current, top = "The page's header", None
    for number, raw in enumerate(text.splitlines(), 1):
        if number > line:
            break
        if raw.startswith("## "):
            top = current = raw[3:].strip().split(". ", 1)[-1]
        elif raw.startswith("### ") and top:
            current = top + ", " + raw[4:].strip()
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


# What an unanswered line asks for, by its kind.
HINTS = {"fact": "the staff writes it; restore it", "briefing": "write the date of the briefing you answer",
         "baseline": "write Carry Week N or New plan", "intent": "write your direction, or None",
         "inactives": "write Standing rule, the players by name or Carry Week N",
         "depth": "write No change, None or the changes", "caller": "write who calls it, or No change",
         "opening": "write the opening calls in order, Carry Week N opening, No change or None",
         "situational": "write how you want it called, Carry Week N or No change",
         "special": "write each call with Keep, Remove or Practice only, No change or None",
         "removals": "write the calls, No change or None",
         "rush": "write the rush rule (%s), No change or Carry Week N" % game_plan.RUSH_CHOICE,
         "decision": "write Standing rule, Carry Week N, No change, None or My rules"}


def required(plan):
    """Every line answered, and the tables and carried weeks the answers need."""
    out = []
    for key in plan.choices.get("unanswered") or ():
        section, label, kind = game_plan.FIELD[key]
        if key not in (plan.choices.get("fields") or {}):
            continue          # a missing line is a problem of form, already named
        if key == "inactives":
            out.append("Inactives: unanswered; %d needed (%s)" % (plan.needed(), HINTS[kind]))
            continue
        label = plan.choices["fields"][key].get("label")
        out.append("%s: unanswered; %s" % (game_plan.where_of(key, label), HINTS[kind]))
    baseline = plan.choices.get("baseline") or {}
    earlier = plan.earlier()
    if "carry" in baseline and baseline["carry"] >= plan.week:
        out.append("Baseline: Carry Week %d names a week that has not come before this one" % baseline["carry"])
    if not plan.choices.get("calls") and "carry" not in baseline and plan.choices.get("baseline") is not None:
        out.append("Offense, Primary calls: a new plan needs its calls in the table")
    for key in game_plan.SITUATIONAL_KEYS:
        value = plan.choices.get(key)
        if isinstance(value, dict) and value.get("carry") is not None and value["carry"] != baseline.get("carry"):
            out.append("%s: Carry Week %d, but the plan's baseline %s; carry the same week or write how you want it "
                       "called" % (game_plan.where_of(key), value["carry"],
                                   "carries Week %d" % baseline["carry"] if "carry" in baseline else "is a new plan"))
    for kind, words in STATUS_WORDS.items():
        entry = plan.choices.get(kind)
        if kind in ("two_point", "kickoff") and entry == "none":
            out.append("%s: a rule is needed for the game (Standing rule, Carry Week N, No change or My rules)"
                       % words)
        if isinstance(entry, dict) and entry.get("standing") and kind not in plan.standing():
            out.append("%s: no standing rule is on file as rules the staff can set; write your rules" % words)
        if isinstance(entry, dict) and ("same_as" in entry or entry.get("no_change")):
            week = entry.get("same_as") if "same_as" in entry else max(earlier, default=None)
            how = "Carry Week %d" % week if "same_as" in entry else "No change"
            if week is None or week not in earlier:
                out.append("%s: %s names no week with a call sheet as set" % (words, how))
            elif week >= plan.week:
                out.append("%s: %s names a week that has not come before this one" % (words, how))
            elif kind in ("two_point", "kickoff") and kind not in (earlier[week].get("decisions") or {}):
                out.append("%s: Week %d set no %s rule, and the game needs one; write Standing rule or your rules"
                           % (words, week, "two-point" if kind == "two_point" else "kickoff"))
            elif kind == "fourth_down" and kind not in (earlier[week].get("decisions") or {}) \
                    and "fourth_down" in plan.standing():
                out.append("Fourth downs: Week %d froze no fourth-down rule, so %s would leave every fourth down to "
                           "your live call although your standing rule is in force; write Standing rule, None for "
                           "your live call, or your rules" % (week, how))
    return out


def briefing_problems(plan):
    """The briefing his page answers is the current one: its date and, from the second issue of a day,
    its revision, as the issue record numbers them (a plan written against an earlier issue the same
    day does not answer the current one)."""
    when = plan.choices.get("briefing")
    if when is None:
        return []
    from scripts import render_game_week
    try:
        current = render_game_week.current_issue(render_game_week.Week(plan.root, plan.week))
    except (OSError, ValueError):
        return []
    if current is not None and (when["date"], when["revision"]) != current:
        return ["Briefing used: your page answers the briefing of %s; the current briefing is %s; read it and "
                "write it as its status line names it (your answers may stand)"
                % (game_plan.issue_label(when["date"], when["revision"]), game_plan.issue_label(*current))]
    return []


def caller_problems(plan):
    """Each caller line names who calls that phase on the staff page."""
    out, arranged = [], plan.arrangement()
    for key, phase in CALLER_PHASES.items():
        value = plan.choices.get(key)
        if not isinstance(value, dict) or value.get("no_change"):
            continue
        on_file = arranged.get(phase)
        if on_file is None or game_plan.norm(value["name"]) != game_plan.norm(on_file):
            out.append("%s: %s calls it on the staff page; a change of caller is recorded with the staff before the "
                       "plan is set (or write No change)" % (game_plan.where_of(key), on_file or "no one"))
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
        return out + ["Inactives: Week %d's list is not on file; name the %d" % (value["same_as"], needed)]
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
            out.append("Depth/role changes: %r is not a position group on the chart" % group)
            continue
        now = depth[group]
        for name in order:
            if name not in now:
                out.append("Depth/role changes, %s: %s is not in this group" % (group, name))
        for name in now:
            if name not in order:
                out.append("Depth/role changes, %s: %s is missing from the new order" % (group, name))
        for name in sorted({p for p in order if order.count(p) > 1}):
            out.append("Depth/role changes, %s: %s is listed twice" % (group, name))
    placed = {p for players in depth.values() for p in players}
    for role, name in (value.get("roles") or {}).items():
        group = ROLE_GROUP.get(role)
        if role not in game_plan.ROLES.values():
            out.append("Depth/role changes: %r is not a game role (%s)" % (role, ", ".join(game_plan.ROLES)))
        elif name not in placed:
            out.append("Depth/role changes: %s is not on the chart for the %s role" % (name, ROLE_WORDS[role]))
        elif group is not None and name not in depth.get(group, ()):
            out.append("Depth/role changes: the %s role goes to a player of the %s group; %s is not one"
                       % (ROLE_WORDS[role], group, name))
        elif role in HEAD_ROLES and group in orders and orders[group] and orders[group][0] != name:
            out.append("Depth/role changes: the %s role gives %s, but your %s order puts %s first"
                       % (ROLE_WORDS[role], name, group, orders[group][0]))
    if not out:
        from runtime.week_inputs import db_role_errors
        trial, _ = changed_chart(plan.chart, value)
        before = set(db_role_errors(plan.chart))
        out += ["Depth/role changes: %s" % db_words(e) for e in db_role_errors(trial) if e not in before]
    return out


def role_problems(plan):
    """Every game role, the page's new ones and those the chart carries, held by a player who dresses:
    a role holder on the inactives, or out for the game, would leave the game to a fallback player in
    place of the one named."""
    players = plan.inactives()
    if players is None:
        return []
    value = plan.choices.get("depth")
    chart, _ = changed_chart(plan.chart, value)
    outs, _ = plan.outs()
    named = (value.get("roles") or {}) if isinstance(value, dict) else {}
    out = []
    for label, role in game_plan.ROLES.items():
        for player in [p for p, held in (chart.get("roles") or {}).items() if role in (held or ())]:
            if player not in players and player not in outs:
                continue
            why = "he is on the inactives" if player in players else "he is out for the game"
            if named.get(role) == player:
                out.append("Depth/role changes: the %s role goes to %s, who does not dress (%s); the role needs a "
                           "player who dresses" % (label, player, why))
            else:
                out.append("Depth/role changes: %s holds the %s role on the depth chart and does not dress (%s); "
                           "give the role to a player who dresses (%s: his name)" % (player, label, why, label))
    return out


def dressing(plan):
    """The players who dress on the page's inactives (active, not inactive), or None before the list
    can be set."""
    players = plan.inactives()
    if players is None:
        return None
    return [p for p in plan.active() if p not in players]


def grouping_needs(personnel):
    """{group: players} a personnel grouping puts on the field, or {} for one the book does not count."""
    text = str(personnel or "").upper()
    if text == "6OL":
        return {"OL": 6}
    if re.fullmatch(r"\d\d", text):
        backs, ends = int(text[0]), int(text[1])
        return {"backs": backs, "TE": ends, "WR": 5 - backs - ends}
    return {}


def offense_problems(plan, sheet):
    """The playbook lock on every word of every call on the sheet, each call's personnel grouping
    against the players who dress, and every variation naming a player against his dressing."""
    out = []
    players = [p["name"] for p in roster_record.players(plan.roster)]
    for call in sheet.get("offensive_call_sheet") or ():
        family = call.get("family")
        if not family:
            out.append("Offense, %s: it names no concept" % call["name"])
        elif offensive_words.concept(family) is None:
            out.append("Offense, %s: %r is not in the active playbook" % (call["name"], family))
        for problem in offensive_words.call_errors(dict(call, family=None), players):
            out.append("Offense, %s: %s" % (call["name"], problem))
    dressed = dressing(plan)
    if dressed is None:
        return out
    depth = plan.chart.get("depth") or {}
    group_of = {p: g for g, order in depth.items() for p in order}
    counts = {}
    for p in dressed:
        g = group_of.get(p)
        key = "backs" if g in ("RB", "FB") else g
        counts[key] = counts.get(key, 0) + 1
    seen = set()
    for call in sheet.get("offensive_call_sheet") or ():
        for group, need in grouping_needs(call.get("personnel")).items():
            if counts.get(group, 0) < need and (call.get("personnel"), group) not in seen:
                seen.add((call.get("personnel"), group))
                out.append("Offense, %s: %s personnel needs %d %s and %d dress" % (
                    call["name"], call["personnel"], need, GROUP_NAMES.get(group, group), counts.get(group, 0)))
    surnames = {}
    for name in players:
        surnames.setdefault(name.split()[-1].lower(), []).append(name)
    for call in sheet.get("offensive_call_sheet") or ():
        for tag in call.get("tags") or ():
            for word in re.findall(r"[A-Za-z'.-]+", tag):
                named = surnames.get(word.lower()) or []
                if len(named) == 1 and named[0] not in dressed:
                    out.append("Offense, %s: the variation %s needs %s, who does not dress; take it off (without %s)"
                               % (call["name"], tag, named[0], tag))
    return out


def sheet_problems(plan, sheet):
    """The call sheet the page compiles to, under the existing validators."""
    from runtime import defensive_calls, fourth_down, scoring_decisions
    out = ["Offense: %s" % e for e in call_families.sheet_errors(sheet.get("offensive_call_sheet") or [])]
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
            out += ["%s: the game needs a rule (Standing rule, Carry Week N or My rules)" % STATUS_WORDS[k]
                    for k in missing] or ["Decision rules: %s" % exc]
    ds = sheet.get("defensive_call_sheet")
    if ds is not None:
        faults = defensive_calls.sheet_errors(ds)
        if not faults:
            faults = defensive_calls.source_errors(ds, plan.root, plan.season)
        source = (plan.compiled()[1] or {}).get("defense")
        out += ["Defense%s" % defensive_words(e, ds, source) for e in faults]
    return out


DEF_KINDS = {"package": "package", "front": "front", "coverage": "coverage", "pressure": "pressure", "tag": "tag",
             "strength": "strength"}


def defensive_words(error, sheet=None, source=None):
    """runtime.defensive_calls' sheet and source problems in the page's words (", <where>: <what>");
    ``source`` (the compile's defensive source map) names each row by its first cell on the page."""
    from runtime import defensive_calls
    rows = {r.get("id"): r for r in (sheet or {}).get("rows") or () if isinstance(r, dict)}
    plan_rows = {rid: (v.get("text") or "").split(" | ")[0] for rid, v in (source or {}).items()
                 if isinstance(v, dict) and v.get("text")}

    def where(rid):
        row = rows.get(rid) or {}
        label = plan_rows.get(rid) or game_plan.DEF_MENU_WORDS.get(row.get("menu")) or \
            (row.get("source") or {}).get("text") or rid
        return ", %s" % label
    m = re.match(r"row (\S+): (\w+) '([^']+)' is not a word of the active defensive book", error)
    if m:
        return "%s: '%s' is not a %s in the active defensive playbook" % (where(m[1]), m[3], m[2])
    m = re.match(r"row (\S+): (\w+) '([^']+)' is not on the practiced menu", error)
    if m:
        # Only a sheet carried as frozen keeps its own menu; a page's menu is its own rows' words.
        return "%s: '%s' is not among the words of the prepared responses carried" % (where(m[1]), m[3])
    m = re.match(r"practiced\.(\w+): '([^']+)' is not a word of the active defensive book", error)
    if m:
        return ": '%s' is not one of the active defensive playbook's %s" % (m[2], m[1])
    m = re.match(r"practiced\.(\w+): '([^']+)' is on none of the practiced menu's cited lines", error)
    if m:
        return ": '%s' is not written on the lines of the week's prepared responses" % m[2]
    if error.startswith("rush_rule.rule must read"):
        return ", Rush rule: write '%s'" % game_plan.RUSH_CHOICE
    if error.startswith("rush_rule"):
        return ", Rush rule: write the rush rule ('%s')" % game_plan.RUSH_CHOICE
    if error.startswith("practiced"):
        return ": write the prepared responses in the active defensive playbook's words"
    if error.startswith("caller") or error == "caller must be a nonempty string":
        return ", Caller: write who calls the defense"
    if error.startswith("rows must be a nonempty list"):
        return ": write at least one prepared response"
    m = re.match(r"row (\S+): a situation row needs a menu key", error)
    if m:
        return "%s: a Situation row needs its situation (%s)" % (where(m[1]),
                                                                ", ".join(game_plan.DEF_MENU_WORDS.values()))
    m = re.match(r"row (\S+): menu (\S+) already labels row (\S+)", error)
    if m:
        return ": %s has two rows; one prepared response per situation" % (
            game_plan.DEF_MENU_WORDS.get(m[2], m[2]))
    m = re.match(r"row (\S+): a situation row needs its call", error)
    if m:
        return "%s: the row names no package, front, coverage or pressure" % where(m[1])
    m = re.match(r"row (\S+): a (\w+) row never labels and takes no menu", error)
    if m:
        return "%s: a %s row has no situation" % (where(m[1]), game_plan.KIND_WORDS.get(m[2], m[2]).lower())
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
    sheet = None
    if not problems:
        # The compile once every line is answered (an unanswered line is named once, above).
        sheet, _, found = plan.compiled()
        problems += found
    problems += briefing_problems(plan)
    problems += caller_problems(plan)
    listed, moved = inactive_problems(plan), depth_problems(plan)
    problems += listed + moved
    if not listed and not moved:
        problems += role_problems(plan)
    if sheet is not None:
        problems += offense_problems(plan, sheet)
        if not problems:
            problems += sheet_problems(plan, sheet)
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


def situation_lists(sheet):
    """[(situation, [call names])] of a compiled sheet, in the sheet's order: what each situation's
    list holds, shown back to him when the page is complete."""
    from runtime import call_situations as cs
    order = list(game_plan.SITUATION_TEXT)
    lists = {}
    for call in sheet.get("offensive_call_sheet") or ():
        for menu in cs.menu_keys(call.get("menus")):
            lists.setdefault(menu, []).append(call["name"])
    words = dict(zip([cs.menu_key(w) for w in game_plan.SITUATION_WORDS], game_plan.SITUATION_WORDS))
    words.update({"two-point": "two-point tries", "final-play-of-half": "final play of the half",
                  "opening-sequence": "opening sequence"})
    return [(words.get(m, m), lists[m]) for m in order if m in lists]


def opening_order(sheet):
    """The compiled opening sequence in order, a return to a call named again: what the sheet sends."""
    slots = sorted((int(s), c["name"]) for c in sheet.get("offensive_call_sheet") or ()
                   for s in ([c["opener"]] if c.get("opener") is not None else []) + list(c.get("opener_returns") or ()))
    return [name for _, name in slots]


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
    problems = game_plan.split(text)[-1]
    missing = [p for p in problems if p.endswith("the heading is missing")]
    if len(missing) == len(game_plan.HEADINGS):
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
        order = opening_order(plan.sheet())
        if order:
            print("  Opening calls, in order: %s" % "; ".join(order))
        for situation, names in situation_lists(plan.sheet()):
            print("  %s: %s" % (situation[:1].upper() + situation[1:], "; ".join(names)))
    for note in notes:
        print("  note: " + note)
    return 1 if problems or plan.changed_since_applied else 0


if __name__ == "__main__":
    raise SystemExit(main())
