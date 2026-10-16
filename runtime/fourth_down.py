"""Kernel 2014.6 batch B9F: fourth-down decisions (go, field goal or punt).

Every number comes from the bound calibration base's fourth-down artifact
(library/data/2010_2014w4_fourth_down_decisions.json, built by
scripts/research/build_2010_2014_fourth_down_decisions.py with a --check mode
under the frozen rules of library/2014_6_fourth_down_specification.md and its
disclosed amendments F1 and F2, pinned as the base's ``fourth_down`` role): the league
decision chart by distance bin, field zone and game state with the cell of
every reachable key, the conversion pairs by distance bin and goal to go, the
anonymous real fourth-down attempt records and the field-goal snap offset.

One resolution for every club (Stone's one-resolution rule, recorded with his
standing instruction "Fourth downs remain my call"). A decision comes from its
source (a club's block, the controlling coach's live answer or the chart);
its outcome comes from the same sourced rates for every club, with the same
matchup terms. The decision source is an input, never a probability shift.

Protagonist-blind by construction. No function here takes a club identity: the
decision reads (policy, state, uniform, chart counts), the probabilities read
the state alone, and the keyed substream the kernel draws them on carries the
event, the drive, the segment and the decision index, never a team id (an AST
test confirms the module never reads ``team_id`` or ``controlled_team``). A
fourth-down block is an ordinary TeamInput field any club may carry.

The no-percentage rule (AGENTS.md): a block states football decisions (go,
field goal or punt) by situation and may name Tice's prepared conversion
calls by menu. A probability, share, rate or weight key anywhere in it is
rejected, so a coach's block can never become a frequency the engine samples.
A named call fixes the snap's family (run or pass records) and its label; it
never moves the conversion probability.

E1 socket (slope 0): ``conversion_edge``, the drive's matchup edge on the
conversion probability. No admissible evidence moves it in 2014.6; it returns
the sourced rate exactly and moves the declared way only when a test patches
its slope.
"""
from __future__ import annotations

import copy

from .scoring_decisions import (BASIS_DELEGATED, BASIS_LEAGUE, BASIS_LIVE, BASIS_POLICY, CHART_BASES,
                                FREQUENCY_WORDS, TEXT_KEYS)

SCHEMA = "2010-2014w4-nfl-fourth-down-decisions-v1"
FOURTH_TAG = "fourth-down-v1"           # the decision, conversion and record uniforms (no team id)
ACTIONS = ("go", "field_goal", "punt")
GO, FIELD_GOAL, PUNT = ACTIONS
OTHERWISE = ("league", "ask") + ACTIONS
WHEN_KEYS = ("period", "margin", "ydstogo", "los", "goal_to_go", "game_seconds_min", "game_seconds_max")
BLOCK_KEYS = ("rules", "otherwise", "prepared_calls")
RULE_KEYS = ("when", "decision", "call")
TIMINGS = ("before_third_down", "at_fourth_down")
BEFORE_THIRD, AT_FOURTH = TIMINGS
# The replay's own action at a decision point (the drawn drive's).
REPLAY_ACTION = {"punt": PUNT, "field_goal_attempt": FIELD_GOAL}
RESOLUTIONS = ("replayed", "model")
# Record kinds and the layout kind a resolved go snap takes (runtime.chains).
RUN_KINDS = ("run", "fumble_run")
PASS_KINDS = ("complete", "incomplete", "sack", "interception", "fumble_catch", "fumble_sack")
SOCKETS = {"conversion_edge": 0.0}
# The kernel's decision-source label of the published fourth-down record
# (W5a decision_source): the chart is the league model, a block or a live
# answer is the head coach's.
DECISION_SOURCE = {BASIS_LEAGUE: "league_model", BASIS_DELEGATED: "league_model"}
HEAD_COACH = "head_coach"


class FourthDownModelError(ValueError):
    """A fourth-down artifact the runtime cannot read."""


def _fraction(pair):
    k, n = int(pair[0]), int(pair[1])
    if n <= 0 or not 0 <= k <= n:
        raise FourthDownModelError("invalid count pair %r" % (pair,))
    return k, n


def _label(edge):
    lo, hi = edge
    return str(lo) if lo == hi else "%d-%d" % (lo, hi)


def _find(edges, value):
    for edge in edges:
        if edge[0] <= value <= edge[1]:
            return edge
    raise FourthDownModelError("%r outside %r" % (value, edges))


class FourthDownModel:
    """The fourth-down artifact as the kernel reads it (one per base)."""

    def __init__(self, data):
        if not isinstance(data, dict) or data.get("schema") != SCHEMA:
            raise FourthDownModelError("unknown fourth-down artifact schema %r"
                                       % (data.get("schema") if isinstance(data, dict) else None))
        self.data = data
        rules = data["rules"]
        self.distance_bins = [tuple(b) for b in rules["distance_bins"]]
        self.zones = [tuple(z) for z in rules["zones"]]
        states = rules["states"]
        self.h1_seconds = int(states["h1_seconds"])
        self.q4_seconds = int(states["q4_seconds"])
        self.ot_margins = {k: tuple(v) for k, v in states["ot_margins"].items()}
        self.late_buckets = {k: tuple(v) for k, v in states["late_time_buckets"].items()}
        self.needs = {k: tuple(v) for k, v in states["needs"].items()}
        if list(data["chart"]["fields"]) != list(ACTIONS):
            raise FourthDownModelError("the chart's fields are not %s" % (ACTIONS,))
        self.chart = {cell: tuple(int(v) for v in counts) for cell, counts in data["chart"]["cells"].items()}
        for cell, counts in self.chart.items():
            if len(counts) != 3 or sum(counts) <= 0 or min(counts) < 0:
                raise FourthDownModelError("invalid chart cell %s %r" % (cell, counts))
        self.cell_map = dict(data["chart"]["cell_map"])
        for key, cell in self.cell_map.items():
            if cell not in self.chart:
                raise FourthDownModelError("cell map names a missing cell %s" % cell)
        conv = data["conversion"]
        self.pairs = {key: _fraction(pair) for key, pair in conv["pairs"].items() if pair[1]}
        self.conversion_map = dict(conv["map"])
        for key, target in self.conversion_map.items():
            if target not in self.pairs:
                raise FourthDownModelError("conversion map names a missing pair %s" % target)
        fields = data["records"]["fields"]
        self.records = {label: [dict(zip(fields, r)) for r in rows]
                        for label, rows in data["records"]["by_distance_bin"].items()}
        self.fg_offset = int(data["field_goal_offset"]["modal"])
        if self.fg_offset not in (17, 18, 19):
            raise FourthDownModelError("field-goal offset %s outside 17-19" % self.fg_offset)
        for dbin in self.distance_bins:
            rows = self.records.get(_label(dbin))
            if not rows or not any(r["converted"] for r in rows) or not any(not r["converted"] for r in rows):
                raise FourthDownModelError("distance bin %s lacks converted or failed records" % _label(dbin))
        # Amendment F2: the chart's masks (R14: a trailing overtime offense's
        # punt share moves to go), read from the artifact.
        self.masks = []
        for m in rules.get("masks", ()):
            if m.get("from") not in ACTIONS or m.get("to") not in ACTIONS or not m.get("state"):
                raise FourthDownModelError("invalid chart mask %r" % (m,))
            self.masks.append((m["state"], ACTIONS.index(m["from"]), ACTIONS.index(m["to"])))
        # Band centres as (count, denominator); a per-team-game rate may exceed 1.
        self.centres = {k: (int(v[0]), int(v[1])) for k, v in data["centres"].items() if int(v[1]) > 0}

    # ---- the state ----------------------------------------------------------------------

    def state(self, *, overtime, game_seconds_left, diff):
        """The chart's game state of a decision: ``game_seconds_left`` is the
        regulation countdown (3600 at kickoff, a Pro Bowl's included) in
        regulation, ignored in overtime; ``diff`` the offense's margin."""
        if overtime:
            return "ot|%s" % next(k for k, (lo, hi) in self.ot_margins.items() if lo <= diff <= hi)
        left = int(game_seconds_left)
        if left <= self.q4_seconds:
            bucket = next(k for k, (lo, hi) in self.late_buckets.items() if lo <= left <= hi)
            need = next(k for k, (lo, hi) in self.needs.items() if lo <= diff <= hi)
            return "q4|%s|%s" % (bucket, need)
        if 1800 < left <= 1800 + self.h1_seconds:
            return "h1_le%d" % self.h1_seconds
        return "neutral"

    def key(self, distance, los, state):
        return "%s|%s|%s" % (_label(_find(self.distance_bins, int(distance))), _label(_find(self.zones, int(los))),
                             state)

    def cell(self, distance, los, state):
        key = self.key(distance, los, state)
        try:
            return self.cell_map[key]
        except KeyError:
            raise FourthDownModelError("no fourth-down cell for %s" % key) from None

    def counts(self, cell):
        return self.chart[cell]

    def chart_counts(self, cell, state):
        """A decision's chart counts: its cell's, with the artifact's masks
        for its game state applied (amendment F2; R14)."""
        counts = list(self.chart[cell])
        for masked_state, i, j in self.masks:
            if state == masked_state:
                counts[j] += counts[i]
                counts[i] = 0
        return tuple(counts)

    # ---- the outcome ----------------------------------------------------------------------

    def conversion_pair(self, distance, goal_to_go):
        dbin = _label(_find(self.distance_bins, int(distance)))
        return self.pairs[self.conversion_map["%s|%s" % (dbin, "goal" if goal_to_go else "field")]]

    @staticmethod
    def p_convert(pair, edge=0.0):
        k, n = pair
        return min(1.0, max(0.0, k / n + SOCKETS["conversion_edge"] * float(edge or 0.0)))

    def attempt_records(self, distance, los, converted, family=None):
        """The real attempt records a resolved go may replay at distance d and line L: a
        converted record of d's bin with yards at least d; a failed record whose ball stays
        inside the field (L - yards from 1 to 99) and, unless it is an interception or a
        lost fumble, with yards under d. ``family`` (run or pass) keeps a named call's
        kinds only."""
        d, line = int(distance), int(los)
        rows = self.records[_label(_find(self.distance_bins, d))]
        kinds = RUN_KINDS if family == "run" else PASS_KINDS if family == "pass" else None
        out = []
        for r in rows:
            if bool(r["converted"]) != bool(converted) or (kinds is not None and r["kind"] not in kinds):
                continue
            yards = int(r["yards"])
            if converted:
                if yards < d:
                    continue
            else:
                turnover = r["kind"] == "interception" or r["kind"].startswith("fumble_")
                if not turnover and yards >= d:
                    continue
                if not 1 <= line - yards <= 99:
                    continue
            out.append(r)
        return out


def model_from(data):
    return FourthDownModel(data)


def choose(u, counts):
    """The chart decision of one uniform: go below go/n, field goal below
    (go + field goal)/n, punt otherwise."""
    go, fg, punt = counts
    n = go + fg + punt
    if u < go / n:
        return GO
    if u < (go + fg) / n:
        return FIELD_GOAL
    return PUNT


def chart_probabilities(counts):
    n = sum(counts)
    return [c / n for c in counts]


# ---- blocks ---------------------------------------------------------------------------------------

def _frequency_key(key):
    lowered = str(key).lower()
    return any(word in lowered for word in FREQUENCY_WORDS)


def _range_errors(at, key, value, whole=True):
    if isinstance(value, list):
        if not value or any(not isinstance(v, int) or isinstance(v, bool) for v in value):
            return ["%s.when.%s must list whole values" % (at, key)]
        return []
    if isinstance(value, dict):
        if set(value) - {"min", "max"} or not value or any(
                not isinstance(v, int) or isinstance(v, bool) for v in value.values()):
            return ["%s.when.%s range takes whole min/max" % (at, key)]
        return []
    return ["%s.when.%s must be a list or a {min, max} range" % (at, key)]


def policy_errors(block, call_names=None):
    """Problems with one ``decisions.fourth_down`` block of a frozen call sheet;
    [] when it is valid. ``call_names`` (the sheet's call names), when given,
    checks every named call."""
    where = "decisions.fourth_down"
    if not isinstance(block, dict) or not block:
        return ["%s must be a nonempty object (an empty policy is rejected)" % where]
    errors = []
    for key in block:
        if _frequency_key(key):
            errors.append("%s.%s: a probability, share or rate is not a football decision (no-percentage rule)"
                          % (where, key))
        elif key not in BLOCK_KEYS + TEXT_KEYS:
            errors.append("%s: unknown key %r" % (where, key))
    if "otherwise" not in block:
        errors.append("%s: 'otherwise' is required (%s)" % (where, ", ".join(OTHERWISE)))
    elif block["otherwise"] not in OTHERWISE:
        errors.append("%s.otherwise must be one of %s" % (where, ", ".join(OTHERWISE)))
    for key in TEXT_KEYS:
        if key in block and not isinstance(block[key], str):
            errors.append("%s.%s must be text" % (where, key))
    prepared = block.get("prepared_calls", {})
    if not isinstance(prepared, dict):
        errors.append("%s.prepared_calls must map a menu to a call name" % where)
    else:
        for menu, name in prepared.items():
            if _frequency_key(menu) or not isinstance(name, str) or not name:
                errors.append("%s.prepared_calls.%s must name one call" % (where, menu))
            elif call_names is not None and name not in call_names:
                errors.append("%s.prepared_calls.%s names %r, not a call of the sheet" % (where, menu, name))
    rules = block.get("rules", [])
    if not isinstance(rules, list):
        return errors + ["%s.rules must be a list" % where]
    for i, rule in enumerate(rules):
        at = "%s.rules[%d]" % (where, i)
        if not isinstance(rule, dict):
            errors.append("%s must be an object" % at)
            continue
        for key in rule:
            if _frequency_key(key):
                errors.append("%s.%s: a probability, share or rate is not a football decision" % (at, key))
            elif key not in RULE_KEYS + TEXT_KEYS:
                errors.append("%s: unknown key %r" % (at, key))
        if rule.get("decision") not in ACTIONS:
            errors.append("%s.decision must be one of %s" % (at, ", ".join(ACTIONS)))
        if "call" in rule:
            if rule.get("decision") != GO or not isinstance(rule["call"], str) or not rule["call"]:
                errors.append("%s.call names one call, with decision go only" % at)
            elif call_names is not None and rule["call"] not in call_names:
                errors.append("%s.call names %r, not a call of the sheet" % (at, rule["call"]))
        when = rule.get("when")
        if not isinstance(when, dict) or not when:
            errors.append("%s.when must be a nonempty object" % at)
            continue
        for key, value in when.items():
            if _frequency_key(key):
                errors.append("%s.when.%s: a probability, share or rate is not a football decision" % (at, key))
            elif key not in WHEN_KEYS:
                errors.append("%s.when: unknown key %r" % (at, key))
            elif key == "period":
                allowed = (1, 2, 3, 4, "OT")
                if not isinstance(value, list) or not value or any(
                        isinstance(p, bool) or p not in allowed for p in value):
                    errors.append("%s.when.period must be a nonempty list of %s" % (at, list(allowed)))
            elif key in ("margin", "ydstogo", "los"):
                errors += _range_errors(at, key, value)
            elif key == "goal_to_go":
                if not isinstance(value, bool):
                    errors.append("%s.when.goal_to_go must be true or false" % at)
            elif key in ("game_seconds_min", "game_seconds_max"):
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    errors.append("%s.when.%s must be whole seconds" % (at, key))
    return errors


def canonical_policy(block):
    """The block as it enters the outcome packet: its id and source text
    removed (kept with the frozen sheet only), rule order kept (the first
    matching rule applies), the prepared calls sorted. None stays None."""
    if block is None:
        return None
    out = {"otherwise": block.get("otherwise"), "rules": [],
           "prepared_calls": {k: block["prepared_calls"][k] for k in sorted(block.get("prepared_calls") or {})}}
    for rule in block.get("rules", []) or []:
        when = copy.deepcopy(rule.get("when") or {})
        if isinstance(when.get("period"), list):
            when["period"] = sorted(set(when["period"]), key=lambda p: (isinstance(p, str), p))
        for key in ("margin", "ydstogo", "los"):
            if isinstance(when.get(key), list):
                when[key] = sorted(set(when[key]))
        entry = {"when": when, "decision": rule.get("decision")}
        if rule.get("call") is not None:
            entry["call"] = rule["call"]
        out["rules"].append(entry)
    return out


def packet_policy(block, call_sheet=()):
    """The block as it enters the outcome packet: canonical_policy with each
    named call (a rule's call, a prepared call) replaced by that call's
    football substance on the frozen sheet (runtime.play_detail
    canonical_call_sheet's fields: family, type, personnel, formation,
    motion, protection, tags), so rewording a call's display name, like its
    id or source text, cannot move a draw. A name the sheet does not carry is
    refused (the block's checks refuse it before any draw)."""
    from .play_detail import _normalize_call
    out = canonical_policy(block)
    if out is None:
        return None
    calls = {}
    for item in call_sheet or ():
        c = _normalize_call(item, "any")
        calls.setdefault(c["name"], {"family": c["family"], "type": c["type"], "personnel": c["personnel"],
                                     "formation": c["formation"], "motion": c["motion"],
                                     "protection": c["protection"], "tags": list(c["tags"])})

    def substance(name):
        if name not in calls:
            raise ValueError("decisions.fourth_down names %r, not a call of the frozen sheet" % (name,))
        return calls[name]
    out["prepared_calls"] = {menu: substance(name) for menu, name in out["prepared_calls"].items()}
    for rule in out["rules"]:
        if "call" in rule:
            rule["call"] = substance(rule["call"])
    return out


def _within(value, spec):
    if isinstance(spec, list):
        return value in spec
    return spec.get("min", -10 ** 6) <= value <= spec.get("max", 10 ** 6)


def _matches(when, state):
    if "period" in when and state["period"] not in when["period"]:
        return False
    for key, field in (("margin", "diff"), ("ydstogo", "ydstogo"), ("los", "los")):
        if key in when and not _within(state[field], when[key]):
            return False
    if "goal_to_go" in when and bool(state["goal_to_go"]) != when["goal_to_go"]:
        return False
    if "game_seconds_min" in when and state["seconds"] < when["game_seconds_min"]:
        return False
    if "game_seconds_max" in when and state["seconds"] > when["game_seconds_max"]:
        return False
    return True


def decide(policy, state, u, counts, *, live_default=False):
    """(decision, basis, call) for one fourth down.

    ``state``: {"period", "diff", "seconds", "ydstogo", "los", "goal_to_go"}.
    A block rule that matches decides (basis policy:i, its call if it names
    one); the block's ``otherwise`` decision is rule len(rules);
    ``otherwise: ask`` returns decision None with basis live (the controlling
    coach answers); ``otherwise: league`` delegates to the chart
    (delegated:league). With no block: the controlling coach live when
    ``live_default`` (the controlled club of a user-controlled regular-season
    or postseason game, Stone's standing instruction), else the chart
    (league). The chart decision is ``choose(u, counts)``; ``u`` is drawn by
    the caller in every case. No club identity is read."""
    if policy is not None:
        rules = policy.get("rules") or []
        for i, rule in enumerate(rules):
            if _matches(rule.get("when") or {}, state):
                return rule["decision"], BASIS_POLICY % i, rule.get("call")
        otherwise = policy.get("otherwise")
        if otherwise in ACTIONS:
            return otherwise, BASIS_POLICY % len(rules), None
        if otherwise == "ask":
            return None, BASIS_LIVE, None
        return choose(u, counts), BASIS_DELEGATED, None
    if live_default:
        return None, BASIS_LIVE, None
    return choose(u, counts), BASIS_LEAGUE, None


def decision_source(basis):
    """The published fourth-down record's decision source for a basis."""
    return DECISION_SOURCE.get(basis, HEAD_COACH)


def is_chart(basis):
    return basis in CHART_BASES


def sheet_call_names(sheet):
    """The call names of a frozen offensive call sheet (strings or dicts)."""
    names = []
    for item in sheet or ():
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            name = item.get("name") or item.get("concept") or item.get("family")
            if name:
                names.append(str(name))
    return names
