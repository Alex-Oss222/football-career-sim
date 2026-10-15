"""Kernel 2014.6 batch B9: scoring decisions (R8 two-point tries, R15
defensive and return touchdowns, R9 onside kicks).

Every number comes from the bound calibration base's scoring artifact
(library/data/2010_2014w4_scoring_decisions.json, built by
scripts/research/build_2010_2014_scoring_decisions.py with a --check mode and
pinned as the base's ``scoring`` role): the league try and onside decision
charts, the pooled two-point success rate, the expected and surprise onside
recovery rates and the real onside spot records from the 35, the
line-of-scrimmage-binned return-touchdown rates of interceptions, lost
fumbles and punts, the blocked-kick rate per missed field goal, the deep
kickoff return-touchdown rate and the feasibility-filtered real return
records. The extra point is the league base drive model's own rate (one
source; the kernel passes it).

Protagonist-blind by construction. No function here takes a club identity:
the decision functions read (policy, state, uniform), the probabilities read
the state alone, and the keyed substreams the kernel draws them on carry no
team id (an AST test confirms the module never reads ``team_id`` or
``controlled_team``). A policy is an ordinary TeamInput field any club may
carry; the same policy given to either side is the same function of state.
A policy never shifts a draw: the decision uniform is drawn in every case.

The no-percentage rule (AGENTS.md): a policy states football decisions (go
or kick, onside or deep) by situation. A probability, share, rate or
weight key anywhere in it is rejected, so a coach's block can never become
a frequency the engine samples.

E1 sockets (slope 0). No admissible evidence moves any of them
(library/2010_2014_scoring_decisions_calibration.md; the 2014.4 phase 2
study found no returner or coverage skill). Each returns the base rate
exactly at slope 0 and moves the declared way only when a test patches its
slope. The kernel passes each its input at the call site:

- two-point success: the scoring drive's matchup edge (0 on a
  non-offensive try);
- returner: the receiving club's returner's tier value (the existing
  returner term's) on punt and deep-kick returns;
- coverage: the defence's coverage composite of the drive's lineup, less its
  strength term's centre, on interception and fumble returns;
- blocked-kick protection and rush: the kicking club's protection and the
  defence's rush composites, each less its term's centre, on a missed field
  goal;
- onside kicking and hands units: no input. Strength v4 defines no
  special-teams unit composite, so the kernel passes 0 and these two are
  named terms only, inert by construction as well as by slope, until such a
  composite is specified.
"""
from __future__ import annotations

import copy

# Keyed substream tags (runtime.play_detail._stream). None carries a team id.
TRY_TAG = "scoring-try-v1"            # the try decision (and a non-offensive try's result)
KICK_TAG = "scoring-kick-v1"          # the onside decision, recovery, spot record; the deep return test
RETURN_TAG = "scoring-return-v1"      # a turnover, punt or missed field goal returned for a touchdown
TRY_DETAIL_TAG = "public-try-detail-v1"  # a two-point try's play type and credit (credit only)

# The frozen basis values (library/2014_6_pre_build_specification.md, section
# 8, scoring.basis_values): a rule of the club's policy (its index; the
# policy's ``otherwise`` decision is the implicit last rule, index
# len(rules)), the policy's explicit delegation to the league chart, a live
# answer from the controlling coach, or the league chart with no policy.
BASIS_LEAGUE = "league"
BASIS_DELEGATED = "delegated:league"
BASIS_LIVE = "live"
BASIS_POLICY = "policy:%d"
# The chart's p is drawn against for "league" and "delegated:league" only.
CHART_BASES = (BASIS_LEAGUE, BASIS_DELEGATED)

TRY_DECISIONS = ("go", "kick")
KICKOFF_DECISIONS = ("onside", "deep")
OTHERWISE = {"two_point": ("league", "ask") + TRY_DECISIONS, "kickoff": ("league", "ask") + KICKOFF_DECISIONS}
WHEN_KEYS = {"two_point": ("period", "diff_after_td", "game_seconds_min", "game_seconds_max"),
             "kickoff": ("period", "diff_after_score", "game_seconds_min", "game_seconds_max", "opening_kick")}
DIFF_KEY = {"two_point": "diff_after_td", "kickoff": "diff_after_score"}
DECISIONS = {"two_point": TRY_DECISIONS, "kickoff": KICKOFF_DECISIONS}
# Text kept with the frozen sheet only, never in the outcome packet.
TEXT_KEYS = ("id", "source")
# Any key naming a frequency (the no-percentage rule) is refused outright.
FREQUENCY_WORDS = ("prob", "percent", "pct", "share", "rate", "weight", "odds", "chance", "frequency")
POLICY_KINDS = ("two_point", "kickoff")

# E1 sockets, every one at slope 0 (no admissible evidence; module docstring).
SOCKETS = {
    "two_point_edge": 0.0,          # the scoring drive's matchup edge on two-point success
    "returner": 0.0,                # the returner on punt and kick return touchdowns
    "coverage": 0.0,                # the defence's coverage composite on interception and fumble returns
    "onside_kicking_unit": 0.0,     # the kicking unit on an onside recovery
    "onside_hands_unit": 0.0,       # the receiving hands unit on an onside recovery
    "blocked_kick_protection": 0.0,  # the kicking club's protection on a blocked punt or field goal
    "blocked_kick_rush": 0.0,       # the defence's rush on a blocked punt or field goal
}
TIME_2PT = (("Q1-Q3", 901, 10 ** 6), ("Q4 900-601", 601, 900), ("Q4 600-301", 301, 600),
            ("Q4 300-121", 121, 300), ("Q4 120-0", 0, 120))
TIME_ONS = (("Q1-Q3", 901, 10 ** 6), ("Q4 900-301", 301, 900), ("Q4 300-121", 121, 300), ("Q4 120-0", 0, 120))
DIFF_ONS = (("lead 1+", 1, 999), ("tied", 0, 0), ("trail 1-3", -3, -1), ("trail 4-8", -8, -4),
            ("trail 9-16", -16, -9), ("trail 17+", -999, -17))
EXPECTED_SECONDS = 300
# Onside kick record outcomes and the start kinds they give.
ONSIDE_RECOVERED = "onside_recovered"
ONSIDE_LOST = "onside_lost"
ONSIDE_START = {ONSIDE_RECOVERED: "onside_recovery", ONSIDE_LOST: "onside_lost"}
# Non-offensive touchdown sources (non_offensive_score.source) and their team counter.
SOURCES = {"interception": "defensive_touchdowns", "fumble": "defensive_touchdowns",
           "punt_return": "special_teams_touchdowns", "blocked_punt": "special_teams_touchdowns",
           "blocked_field_goal": "special_teams_touchdowns", "kickoff_return": "special_teams_touchdowns"}
# The player credit field of each source (credit only; "attribution" marks
# the group-drawn blocked-kick credit, never player evidence).
PLAYER_TD_FIELD = {"interception": "interception_return_touchdowns", "fumble": "fumble_return_touchdowns",
                   "punt_return": "punt_return_touchdowns", "blocked_punt": "blocked_kick_touchdowns",
                   "blocked_field_goal": "blocked_kick_touchdowns", "kickoff_return": "kick_return_touchdowns"}
TWO_POINT_FIELDS = ("passing_two_point_conversions", "receiving_two_point_conversions",
                    "rushing_two_point_conversions")
GROUP_DRAW = "group_draw"


class ScoringModelError(ValueError):
    """A scoring artifact the runtime cannot read."""


def _fraction(pair):
    k, n = int(pair[0]), int(pair[1])
    if n <= 0 or not 0 <= k <= n:
        raise ScoringModelError("invalid count pair %r" % (pair,))
    return k, n


def los_bin(value, bins):
    """The artifact's line-of-scrimmage bin label ('61-80') of a yardline_100."""
    for lo, hi in bins:
        if lo <= value <= hi:
            return "%d-%d" % (lo, hi)
    raise ScoringModelError("line of scrimmage %r outside the bins" % (value,))


def try_seconds(period, game_clock):
    """Game seconds left at a try row's own stamp (period 1-4, 'mm:ss')."""
    minutes, seconds = str(game_clock).split(":")
    return (4 - int(period)) * 900 + int(minutes) * 60 + int(seconds)


class ScoringModel:
    """The scoring artifact as the kernel reads it (one per base)."""

    def __init__(self, data, *, kick_chain_bound=None):
        if not isinstance(data, dict) or data.get("schema") != "2010-2014w4-nfl-scoring-decisions-v1":
            raise ScoringModelError("unknown scoring artifact schema %r" % (data.get("schema") if isinstance(data, dict)
                                                                           else None))
        self.data = data
        t = data["try"]
        self.try_chart = {cell: (int(v["go"]), int(v["tries"])) for cell, v in t["decision_chart"].items()}
        self.try_cell_map = dict(t["decision_cell_map"])
        for raw, cell in self.try_cell_map.items():
            if cell not in self.try_chart:
                raise ScoringModelError("try cell map names a missing cell %s" % cell)
        success = data["two_point_success"]
        if success.get("adopted_splits"):
            raise ScoringModelError("the runtime reads one pooled two-point rate; splits %s were adopted"
                                    % success["adopted_splits"])
        self.two_point = _fraction(success["pooled"])
        types = success["type_counts"]
        self.pass_share = (int(types.get("pass", 0)), int(types.get("pass", 0)) + int(types.get("run", 0)))
        o = data["onside"]
        self.onside_chart = {cell: _fraction(v) for cell, v in o["decision_chart"].items()}
        self.recovery = {label: _fraction(v) for label, v in o["recovery"].items()}
        fields = o["spot_record_fields"]
        self.spot_records = {side: [dict(zip(fields, r)) for r in rows]
                             for side, rows in o["spot_records_from_35"].items()}
        if not self.spot_records.get("kicking") or not self.spot_records.get("receiving"):
            raise ScoringModelError("onside spot records missing a side")
        n = data["non_offensive"]
        # The line-of-scrimmage bins (the specification's return_td_los_bins),
        # read from the artifact's own interception bin labels.
        self.bin_edges = sorted([int(x) for x in label.split("-")] for label in n["interception"]["los_bins"])
        self.rates = {}
        for unit in ("interception", "fumble_lost", "punt"):
            entry = n[unit]
            if entry.get("bins_adopted"):
                # An adopted unit's bins partition its pooled units: a bin key
                # that drops units (a fumble spot off the field, say) would
                # read a rate counted on another state variable.
                bins = {label: _fraction(v) for label, v in entry["los_bins"].items()}
                total = (sum(k for k, _ in bins.values()), sum(n_ for _, n_ in bins.values()))
                if total != _fraction(entry["pooled"]):
                    raise ScoringModelError("%s line-of-scrimmage bins add up to %d/%d, not the pooled %d/%d"
                                            % ((unit,) + total + tuple(entry["pooled"])))
                self.rates[unit] = bins
            else:
                self.rates[unit] = {"*": _fraction(entry["pooled"])}
        self.missed_fg = _fraction(n["missed_field_goal"]["pooled"])
        self.kickoff = _fraction(n["kickoff"]["pooled"])
        self.safety_free_kick = _fraction(n["safety_free_kick"]["pooled"])
        records = n["records"]
        rf = records["fields"]
        self.records = {kind: [dict(zip(rf[kind], r)) for r in records[kind]] for kind in rf}
        self.kick_chain_cap = int(records["kick_return_chain_cap"])
        if kick_chain_bound is not None and self.kick_chain_cap != kick_chain_bound:
            raise ScoringModelError("artifact kick-return chain cap %s differs from the engine bound %s"
                                    % (self.kick_chain_cap, kick_chain_bound))
        if not self.records.get("kickoff_return_td"):
            raise ScoringModelError("no kickoff return touchdown records")

    # ---- R8 tries --------------------------------------------------------------------

    def try_cell(self, seconds_left, diff):
        """The chart cell of a try: game seconds left at the try row's stamp
        and the scoring club's margin after the touchdown (before the try)."""
        label = next(label for label, lo, hi in TIME_2PT if lo <= seconds_left <= hi)
        low, high = -15, 15
        d = "<=%d" % (low - 1) if diff < low else ">=%d" % (high + 1) if diff > high else "%+d" % diff
        key = "%s|%s" % (label, d)
        try:
            return self.try_cell_map[key]
        except KeyError:
            raise ScoringModelError("no try cell for %s" % key) from None

    def p_go(self, cell):
        return self.try_chart[cell]

    def two_point_success(self, edge=0.0):
        """The pooled two-point success probability; the slope-0 socket on the
        drive's matchup edge reads 0 on a non-offensive try."""
        k, n = self.two_point
        return min(1.0, max(0.0, k / n + SOCKETS["two_point_edge"] * float(edge or 0.0)))

    # ---- R9 onside -------------------------------------------------------------------

    def onside_cell(self, *, seconds_left, period, overtime, opening, diff):
        """The onside chart cell. ``opening``: a half's or overtime's opening
        kick (chain 1, after no possession); ``period`` 1-4 in regulation."""
        margin = next(label for label, lo, hi in DIFF_ONS if lo <= diff <= hi)
        if opening:
            time = "opening"
        elif overtime:
            time = "OT"
        else:
            time = next(label for label, lo, hi in TIME_ONS if lo <= seconds_left <= hi)
        cell = "%s|%s" % (time, margin)
        if cell not in self.onside_chart:
            raise ScoringModelError("no onside cell %s" % cell)
        return cell

    def p_onside(self, cell):
        return self.onside_chart[cell]

    @staticmethod
    def recovery_class(*, seconds_left, period, overtime, diff):
        """Expected iff the kicking club trails in the fourth quarter with
        300 s or less left (the preregistered split); surprise otherwise."""
        if not overtime and period == 4 and seconds_left <= EXPECTED_SECONDS and diff < 0:
            return "expected"
        return "surprise"

    def p_recover(self, label, kicking_unit=0.0, hands_unit=0.0):
        k, n = self.recovery[label]
        return min(1.0, max(0.0, k / n + SOCKETS["onside_kicking_unit"] * kicking_unit
                            - SOCKETS["onside_hands_unit"] * hands_unit))

    # ---- R15 returns -----------------------------------------------------------------

    def _bins(self):
        return self.bin_edges

    def return_rate(self, unit, los):
        """(touchdowns, units) of a turnover or punt from its line of
        scrimmage bin; a punt from 1-20 takes the 21-40 counts (no punt
        record lies inside the 20)."""
        rates = self.rates[unit]
        if "*" in rates:
            return rates["*"]
        label = los_bin(int(los), self._bins())
        if label not in rates and unit == "punt" and label == "1-20":
            label = "21-40"
        return rates[label]

    @staticmethod
    def p_return(pair, returner=0.0, coverage=0.0):
        k, n = pair
        return min(1.0, max(0.0, k / n + SOCKETS["returner"] * returner - SOCKETS["coverage"] * coverage))

    @staticmethod
    def p_blocked(pair, protection=0.0, rush=0.0):
        k, n = pair
        return min(1.0, max(0.0, k / n - SOCKETS["blocked_kick_protection"] * protection
                            + SOCKETS["blocked_kick_rush"] * rush))

    def interception_records(self, los):
        """The bin's real pick-six records feasible from this line of
        scrimmage (air yards at most LOS + 9); the whole bin when none is."""
        label = los_bin(int(los), self._bins())
        rows = [r for r in self.records["interception_return_td"] if r["los_bin"] == label]
        feasible = [r for r in rows if r["air_yards"] <= int(los) + 9]
        return feasible or rows

    def punt_records(self, los):
        """The punt bin's real return or blocked touchdown records feasible
        from this line of scrimmage (a returned punt's gross at most LOS + 9)."""
        label = los_bin(int(los), self._bins())
        if label == "1-20":
            label = "21-40"
        rows = [r for r in self.records["punt_return_or_block_td"]
                if los_bin(int(r["los"]), self._bins()) == label]
        return [r for r in rows if r["blocked"] or r["gross"] <= int(los) + 9]


def model_from(data, kick_chain_bound=None):
    return ScoringModel(data, kick_chain_bound=kick_chain_bound)


# ---- policies -------------------------------------------------------------------------------

def _frequency_key(key):
    lowered = str(key).lower()
    return any(word in lowered for word in FREQUENCY_WORDS)


def policy_errors(block, kind):
    """Problems with one decision block (``decisions.two_point`` or
    ``decisions.kickoff`` of a frozen call sheet); [] when it is valid."""
    errors = []
    if kind not in POLICY_KINDS:
        return ["unknown decision block %r" % (kind,)]
    where = "decisions.%s" % kind
    if not isinstance(block, dict) or not block:
        return ["%s must be a nonempty object (an empty policy is rejected)" % where]
    for key in block:
        if _frequency_key(key):
            errors.append("%s.%s: a probability, share or rate is not a football decision (no-percentage rule)"
                          % (where, key))
        elif key not in ("rules", "otherwise") + TEXT_KEYS:
            errors.append("%s: unknown key %r" % (where, key))
    if "otherwise" not in block:
        errors.append("%s: 'otherwise' is required (%s)" % (where, ", ".join(OTHERWISE[kind])))
    elif block["otherwise"] not in OTHERWISE[kind]:
        errors.append("%s.otherwise must be one of %s" % (where, ", ".join(OTHERWISE[kind])))
    for key in TEXT_KEYS:
        if key in block and not isinstance(block[key], str):
            errors.append("%s.%s must be text" % (where, key))
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
            elif key not in ("when", "decision") + TEXT_KEYS:
                errors.append("%s: unknown key %r" % (at, key))
        if rule.get("decision") not in DECISIONS[kind]:
            errors.append("%s.decision must be one of %s" % (at, ", ".join(DECISIONS[kind])))
        when = rule.get("when")
        if not isinstance(when, dict) or not when:
            errors.append("%s.when must be a nonempty object" % at)
            continue
        for key, value in when.items():
            if _frequency_key(key):
                errors.append("%s.when.%s: a probability, share or rate is not a football decision" % (at, key))
            elif key not in WHEN_KEYS[kind]:
                errors.append("%s.when: unknown key %r" % (at, key))
            elif key == "period":
                allowed = (1, 2, 3, 4) + (("OT",) if kind == "kickoff" else ())
                if not isinstance(value, list) or not value or any(
                        isinstance(p, bool) or p not in allowed for p in value):
                    errors.append("%s.when.period must be a nonempty list of %s" % (at, list(allowed)))
            elif key == DIFF_KEY[kind]:
                if isinstance(value, list):
                    if not value or any(not isinstance(d, int) or isinstance(d, bool) for d in value):
                        errors.append("%s.when.%s must list whole margins" % (at, key))
                elif isinstance(value, dict):
                    if set(value) - {"min", "max"} or not value or any(
                            not isinstance(v, int) or isinstance(v, bool) for v in value.values()):
                        errors.append("%s.when.%s range takes whole min/max" % (at, key))
                else:
                    errors.append("%s.when.%s must be a list or a {min, max} range" % (at, key))
            elif key in ("game_seconds_min", "game_seconds_max"):
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    errors.append("%s.when.%s must be whole seconds" % (at, key))
            elif key == "opening_kick":
                if not isinstance(value, bool):
                    errors.append("%s.when.opening_kick must be true or false" % at)
    return errors


def canonical_policy(block):
    """The policy as it enters the outcome packet: its id and source text
    removed (kept with the frozen sheet only), so rewording them cannot move
    a draw; rule order kept (the first matching rule applies). None stays
    None. The one stripper both packet builders use (runtime.kernel and
    runtime.game_runner)."""
    if block is None:
        return None
    out = {"otherwise": block.get("otherwise"), "rules": []}
    for rule in block.get("rules", []) or []:
        when = copy.deepcopy(rule.get("when") or {})
        if isinstance(when.get("period"), list):
            when["period"] = sorted(set(when["period"]), key=lambda p: (isinstance(p, str), p))
        for key in ("diff_after_td", "diff_after_score"):
            if isinstance(when.get(key), list):
                when[key] = sorted(set(when[key]))
        out["rules"].append({"when": when, "decision": rule.get("decision")})
    return out


# The TeamInput field and the profile flag of each decision kind.
POLICY_FIELDS = {"two_point": "try_policy", "kickoff": "kickoff_policy"}
POLICY_FLAGS = {"two_point": "two_point_tries", "kickoff": "onside_kicks"}


def profile_kinds(profile):
    """The decision kinds a kernel profile resolves (its B9 flags)."""
    return tuple(kind for kind in POLICY_KINDS if profile.has(POLICY_FLAGS[kind]))


def kernel_kinds(version):
    """The decision kinds the kernel ``version`` decided: its registered
    profile's, and none for every kernel before 2014.6 (unregistered)."""
    from .profiles import PROFILES
    profile = PROFILES.get(str(version))
    return profile_kinds(profile) if profile is not None else ()


def live_kinds():
    """The decision kinds of the installed kernel's profile."""
    from . import KERNEL_VERSION
    from .profiles import profile_for
    return profile_kinds(profile_for(KERNEL_VERSION))


def sheet_errors(decisions):
    """Problems with a frozen call sheet's ``decisions`` object (its
    ``two_point`` and ``kickoff`` blocks); [] when it is valid or absent."""
    if decisions is None:
        return []
    if not isinstance(decisions, dict) or not decisions:
        return ["decisions must be a nonempty object of two_point and kickoff blocks"]
    errors = ["decisions: unknown block %r" % key for key in decisions if key not in POLICY_KINDS]
    for kind in POLICY_KINDS:
        if kind in decisions:
            errors += policy_errors(decisions[kind], kind)
    return errors


def input_policies(decisions, kinds):
    """{TeamInput field: block} for the controlled club's user-controlled
    game, from its frozen sheet's ``decisions`` and the ``kinds`` the
    resolving kernel decides (fails closed, ValueError): a malformed block,
    a block the kernel does not resolve, or a kind the kernel resolves with
    no block (U6: Stone's standing rule, a delegation, or ``otherwise: ask``
    for a live answer). No kind, no block: nothing is added."""
    faults = sheet_errors(decisions)
    if faults:
        raise ValueError("call sheet decisions: " + "; ".join(faults))
    decisions = decisions or {}
    extra = [kind for kind in decisions if kind not in kinds]
    if extra:
        raise ValueError("call sheet carries a %s decision block the resolving kernel does not decide"
                         % " and ".join(extra))
    missing = [kind for kind in kinds if kind not in decisions]
    if missing:
        raise ValueError("U6: the call sheet has no decisions.%s block (Stone's standing rule, a dated "
                         "delegation such as otherwise: league, or otherwise: ask for a live answer); the "
                         "controlled club's inputs fail closed" % " or decisions.".join(missing))
    return {POLICY_FIELDS[kind]: copy.deepcopy(decisions[kind]) for kind in kinds}


def _matches(when, kind, state):
    period = when.get("period")
    if period is not None and state["period"] not in period:
        return False
    diff = when.get(DIFF_KEY[kind])
    if isinstance(diff, list) and state["diff"] not in diff:
        return False
    if isinstance(diff, dict) and not (diff.get("min", -10 ** 6) <= state["diff"] <= diff.get("max", 10 ** 6)):
        return False
    if "game_seconds_min" in when and state["seconds"] < when["game_seconds_min"]:
        return False
    if "game_seconds_max" in when and state["seconds"] > when["game_seconds_max"]:
        return False
    if "opening_kick" in when and bool(state.get("opening")) != when["opening_kick"]:
        return False
    return True


def decide(policy, kind, state, u, chart_pair):
    """(decision, basis) for one try or kickoff.

    ``state``: {"period", "diff", "seconds"} (and "opening" for a kickoff).
    The club's policy rule that matches the state decides (basis policy:i;
    the policy's explicit ``otherwise`` go/kick or onside/deep is rule
    len(rules)); ``otherwise: league`` delegates to the chart
    (delegated:league); ``otherwise: ask`` returns decision None with basis
    live (the controlling coach answers); with no policy the chart decides
    (league). The chart decision is go/onside iff ``u`` < k/n of
    ``chart_pair``. ``u`` is drawn by the caller in every case. No club
    identity is read."""
    yes, no = DECISIONS[kind]
    if policy is not None:
        rules = policy.get("rules") or []
        for i, rule in enumerate(rules):
            if _matches(rule.get("when") or {}, kind, state):
                return rule["decision"], BASIS_POLICY % i
        otherwise = policy.get("otherwise")
        if otherwise in DECISIONS[kind]:
            return otherwise, BASIS_POLICY % len(rules)
        if otherwise == "ask":
            return None, BASIS_LIVE
        basis = BASIS_DELEGATED
    else:
        basis = BASIS_LEAGUE
    k, n = chart_pair
    return (yes if u < k / n else no), basis
