"""Frozen kernel profiles (kernel 2014.6 plumbing, batch B1).

A Profile names everything a kernel version resolves with: its calibration
base (runtime.calibration_base), the frozen cell and need rules of that
base, the strength parameter table entry (runtime.strength) and the named
mechanism flags that later 2014.6 batches add. Every 2014.6 mechanism is
guarded by a flag of the profile passed explicitly to the kernel, never by
module or environment state.

Production (runtime.game_runner.run_game) always resolves with the profile of
runtime.KERNEL_VERSION. Tests and acceptance scripts may pass
``_test_profile=PROFILE_2014_6`` to runtime.kernel.resolve_game; the
production runner accepts no ``_test_*`` argument
(runtime.game_runner.architecture_errors refuses one).

PROFILE_2014_5 is the live kernel and must reproduce every committed result
digest (tests/test_profiles.py, tests/test_attribution.py ResultIdentityTests).
PROFILE_2014_6 is the kernel being built: its base is the 2010-2014 league
base (U1 = (b)), registered by batch B5 with these flags:

- base_2014_6: the kernel reads the base's own numbers (clock scale, extra
  point, field-goal distance model, sack base rate, gross yards per attempt,
  yards per carry, completion rate, band centres) through the schema-3
  readers; the per-play penalty counter stays the 2012 base's factor until
  R11 (batch B11, penalty_records) replaces it with the replayed records.
- regimes_v3: the schema-3 end-of-half and late-game regimes of
  runtime.field_position.FieldPositionModelV3 (R17, R7, R10, R14, W5b).
- injury_2014_6: the injury block of the bound base (it changes onsets);
  without it the 2012 base's injury parameters are used.
- usage_2014_6: the usage shares, rank shapes and top-share centres of the
  bound base (credit only); without it the 2012 base's.

Batch B6 (drive-internal records) adds three flags, each guarded by the
profile alone (the base serves the constants, the flag decides whether the
kernel reads them):

- early_fg_v2 (W3; changes results on the possession and layout streams): a
  field-goal drive kicks on fourth down unless the kick is early by the
  frozen rule (runtime.field_position.FieldPositionModelV3.early_fg_ok): the
  drive ends its window, or in regulation its kick-snap clock is at most
  EARLY_FG_SECONDS, or in overtime the kick ends the game. Otherwise a
  field-goal tuple with term_down < 4 must admit a fourth-down layout before
  it is drawn, and the layout search is held to fourth down in every tier,
  with a closable last fallback to the real down (counted
  fg_fourth_down_relaxed).
- clock_detail_v1 (W5a; records only): snap stamps on the
  public-clock-detail-v1 substream from the base's gap and kick-length
  tables, timeout rows seated after clock-running snaps and two-minute
  warning rows (runtime.play_detail). No draw reads them.
- substitution_record (W2a; records only): each in-game removal's record
  names the entrant, the vacated and entering slots, slot moves, emergency
  fills, specialist and returner changes, computed through the pure
  participation path (runtime.participation.slot_lineup); full receipts
  carry it. Credit and exposure are unchanged.

Batch B7 (player states, identity and strength v4 at runtime) switches
PROFILE_2014_6's strength entry to ``player-state-v1`` (runtime.strength
PARAMETERS, read from library/data/2014_strength_calibration_v4.json under
its pin): each lineup slot reads the player's drawn state
(runtime.player_state), honours act as floors, the v4 terms, HOME_EDGE and
PUNTER_SLOPE apply, and the kernel publishes no per-possession strength
block. PROFILE_2014_5 keeps honours-production-v3.

Batch B8 (possession sequencing) adds one flag:

- possession_sequencing: the kernel's five alternation sites (Pro Bowl
  quarters, regulation, half openers, the overtime opener and the overtime
  loop) take the next possessor from the event that ended the last one
  (``possess`` returns it; ``kicked_after`` returns the retained flag), a
  kickoff is one link of a ``kick_sequence`` (a return touchdown is
  followed by the scorer's kickoff on the same chain, a kick the kicking
  club keeps hands it the ball), the overtime history is
  runtime.rules.ot_history over possessions and kicks, and the result and
  its receipts carry the append-only kick summary fields and
  ``scoring_events``. No branch fires until batches B9 and B10 add the
  sourced mechanisms, so a game without one equals its run before B8
  apart from those records; a profile without the flag runs the 2014.5
  sequencing byte for byte.

Batch B9 (scoring decisions; result-changing) adds three flags, each needing
possession_sequencing (FLAG_REQUIRES: a profile holding one without it is
refused when it is constructed, and the kernel checks again) and a base that
pins the scoring artifact (CalibrationBase.scoring; the kernel fails closed
otherwise):

- two_point_tries (R8): every touchdown that is not a walk-off takes a try
  decision, go or kick, from the club's policy (TeamInput.try_policy), a
  live answer from the controlling coach, or the league chart; a two-point
  try succeeds on the pooled sourced rate. The try rows carry their anchor,
  scoring club, decision, basis, cell and chart p.
- return_touchdowns (R15): interceptions, lost fumbles, punts, missed field
  goals and deep kickoffs may be returned for a touchdown at the sourced
  line-of-scrimmage rates, conditioned on the replayed drive's category
  (non_offensive_score; the scorer kicks off, overtime ends).
- onside_kicks (R9): every kickoff from the 35 takes an onside decision
  (TeamInput.kickoff_policy, a live answer, or the league chart); an onside
  kick is recovered at the expected or surprise rate on a real onside
  record of the recovering side; library rule R4 in overtime.

Batch B9F (live fourth downs; result-changing) adds one flag, needing
possession_sequencing and clock_detail_v1 (FLAG_REQUIRES) and a base that pins
the fourth-down artifact (CalibrationBase.fourth_down; the kernel fails closed
otherwise):

- fourth_down_decisions: every fourth-down decision point of a laid-out drive
  (runtime.fourth_down) takes a decision, go, field goal or punt, from the
  club's block (TeamInput.fourth_down_policy), the controlling coach's live
  answer (the default for the controlled club of a user-controlled regular or
  postseason game, Stone's standing instruction) or the league chart; one
  resolution for every club follows (the sourced conversion, field-goal or
  punt outcome with the same matchup terms), and a conversion continues the
  possession with a continuation segment drawn from the new spot.

Batch B10 (ball security; W4 and R12 layers A, B and C) adds three flags, each
needing a base that pins the ball-security artifact and carries the schema-3
fumble annotations (CalibrationBase.ball_security; the kernel fails closed
otherwise):

- ball_security_credit (W4 and layer A; credit only): a muffed kick names its
  muffer by the record's role, every kept or out-of-bounds fumble of the
  replayed drive is seated on its laid-out snap with its fumbler, forcer and
  recoverer named from the side-aware on-field sets, a kick fumble's from
  the kick play's units, each with its attribution; fumbles, muffs, forced
  fumbles and recoveries are never player evidence. Outcomes and the
  per-drive exposure are unchanged.
- fumble_terminal_kind (layer B; needs ball_security_credit): a lost
  fumble's terminal snap kind comes from the tuple's own lost entry, an
  aborted snap carried by the quarterback or the centre (result-changing on
  the chain-layout stream).
- retained_kicks (layer C; needs possession_sequencing and
  ball_security_credit): the kick and punt pools hold the kicking club's
  recoveries at their real frequency; the turnover is the receiving club's,
  the next possession the kicking club's; overtime kickoffs follow library
  rule R4 and overtime punts exclude retained records, counted
  (result-changing).

Batch B11 (R11, per-play penalty records; result-changing) adds one flag,
needing possession_sequencing (the kick summaries carry their records) and a
base that pins the penalty artifact and carries the schema-3 ``pen``
annotations (CalibrationBase.penalties; the kernel fails closed otherwise):

- penalty_records: every replayed drive's own penalty clauses are replayed
  (runtime.penalties): no-play and pre-kick rows and clauses on counted snaps
  enter the chain layout (runtime.chains.walk_steps, ledger-walk-v2, on the
  chain-layout-v2 stream) and take their accepted yards out of the scrimmage
  split; the penalty-aware static gate masks a tuple whose records admit no
  legal placement on the possession stream; kick rows carry their kick
  records' clauses; each record's fouler is a group draw; team counters go
  to the fouling club. The per-play Bernoulli counter of every earlier
  kernel is gone.

Batch B13 (R16a, R16b; the yard split) adds two flags, each on a schema-3
base carrying the B3b yardage annotations (the kernel fails closed
otherwise; runtime.yard_split):

- yard_split (R16a): each replayed drive keeps its own real rushing yards,
  passing yards, completions and sack losses. The relocation delta is split
  between the kinds (the runs take round(d x |R| / (|R| + |P|))), the
  completions are fixed in every rung (a forced one counted), the sack
  losses are never redrawn; the gauss and randint draws are still taken as
  placeholders, so the possession stream is unchanged (result-changing on
  the chain-layout stream: team counters, credit and, through the laid-out
  fourth-down states, B9F's decision points).
- snap_values (R16b; needs yard_split): each drive's real run and completion
  values replace the uniform allocation, the terminal value on the terminal
  slot, the others shuffled on the layout stream, each kind's delta by the
  gains-proportional rule.

A base names the flags its readers require (CalibrationBase.requires_flags):
a profile resolving on it must hold them, and a profile holding base_2014_6
or regimes_v3 on a base that does not serve them fails closed.
"""
from __future__ import annotations

from dataclasses import dataclass

from .calibration_base import CalibrationBase, base_for_kernel, get_base


@dataclass(frozen=True)
class Profile:
    kernel_version: str
    base: object  # a base name (runtime.calibration_base.BASES) or, in tests, a CalibrationBase
    cell_rules: str
    strength: str
    flags: frozenset = frozenset()
    # Kernel 2014.6 onward: results and receipts record the calibration base,
    # its manifest digest and its cell rules (append-only fields).
    record_base: bool = False

    def __post_init__(self):
        if not isinstance(self.flags, frozenset):
            raise TypeError("profile flags must be a frozenset")
        unknown = self.flags - FLAGS
        if unknown:
            raise ValueError("unknown profile flags %s" % sorted(unknown))
        for flag in sorted(self.flags):
            missing = FLAG_REQUIRES.get(flag, frozenset()) - self.flags
            if missing:
                raise ValueError("profile %s holds %s without %s" % (self.kernel_version, flag,
                                                                   ", ".join(sorted(missing))))

    def has(self, flag):
        return flag in self.flags

    def calibration_base(self):
        """The bound base; it must carry the profile's cell rules and its
        schema flags must be exactly the profile's (BASE_FLAGS)."""
        base = self.base if isinstance(self.base, CalibrationBase) else get_base(self.base)
        if base.cell_rules != self.cell_rules:
            raise ValueError("profile %s expects %s cell rules; base %s carries %s"
                             % (self.kernel_version, self.cell_rules, base.name, base.cell_rules))
        held = self.flags & BASE_FLAGS
        if held != base.requires_flags:
            raise ValueError("profile %s holds base flags %s; base %s requires %s"
                             % (self.kernel_version, sorted(held), base.name, sorted(base.requires_flags)))
        return base

    def injury_base(self, base):
        """The base whose injury parameters this profile draws onsets with:
        the bound base under injury_2014_6 or when it is read by the 2012
        readers (every kernel up to 2014.5), else the 2012 base."""
        return base if self.has("injury_2014_6") or base.legacy_2012() else _legacy_base()

    def usage_base(self, base):
        """The base whose usage shares and centres this profile credits with
        (the same rule, flag usage_2014_6)."""
        return base if self.has("usage_2014_6") or base.legacy_2012() else _legacy_base()


# Flags tied to a base's reader schema; injury_2014_6 and usage_2014_6 are
# switches the profile may hold on any base that carries those blocks.
BASE_FLAGS = frozenset({"base_2014_6", "regimes_v3"})
# Batch B6 mechanism flags (W3, W5a, W2a); each needs a schema-3 base for
# its constants, which the kernel checks when the flag is held.
B6_FLAGS = frozenset({"early_fg_v2", "clock_detail_v1", "substitution_record"})
# Batch B8 mechanism flag: possession sequencing (kick chains, retained
# kicks, the next possessor returned by every alternation site) with its
# append-only records (kick summary fields, scoring_events).
B8_FLAGS = frozenset({"possession_sequencing"})
# Batch B9 mechanism flags (R8, R15, R9), each requiring possession_sequencing.
B9_FLAGS = frozenset({"two_point_tries", "return_touchdowns", "onside_kicks"})
# Batch B9F mechanism flag (live fourth downs), requiring possession_sequencing
# (the possession's records) and clock_detail_v1 (the W5a stamps that time a
# decision and the segments of a continued possession).
B9F_FLAGS = frozenset({"fourth_down_decisions"})
# Batch B10 mechanism flags (W4 and R12 layers A, B and C).
B10_FLAGS = frozenset({"ball_security_credit", "fumble_terminal_kind", "retained_kicks"})
# Batch B11 mechanism flag (R11, per-play penalty records).
B11_FLAGS = frozenset({"penalty_records"})
# Batch B13 mechanism flags (R16a yard split, R16b snap values).
B13_FLAGS = frozenset({"yard_split", "snap_values"})
FLAGS = (BASE_FLAGS | {"injury_2014_6", "usage_2014_6"} | B6_FLAGS | B8_FLAGS | B9_FLAGS | B9F_FLAGS | B10_FLAGS
         | B11_FLAGS | B13_FLAGS)
# A mechanism flag that needs another flag's records (a profile holding it
# without them is refused at construction).
FLAG_REQUIRES = {flag: B8_FLAGS for flag in B9_FLAGS}
FLAG_REQUIRES["fourth_down_decisions"] = frozenset({"possession_sequencing", "clock_detail_v1"})
FLAG_REQUIRES["fumble_terminal_kind"] = frozenset({"ball_security_credit"})
FLAG_REQUIRES["retained_kicks"] = frozenset({"possession_sequencing", "ball_security_credit"})
FLAG_REQUIRES["penalty_records"] = frozenset({"possession_sequencing"})
FLAG_REQUIRES["snap_values"] = frozenset({"yard_split"})


def _legacy_base():
    from .calibration_base import BASE_2012
    return BASE_2012


PROFILE_2014_5 = Profile("2014.5", base="2012", cell_rules="2013.7", strength="honours-production-v3")
PROFILE_2014_6 = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength="player-state-v1",
                         flags=frozenset({"base_2014_6", "regimes_v3", "injury_2014_6", "usage_2014_6",
                                          "early_fg_v2", "clock_detail_v1", "substitution_record",
                                          "possession_sequencing", "two_point_tries", "return_touchdowns",
                                          "onside_kicks", "fourth_down_decisions", "ball_security_credit",
                                          "fumble_terminal_kind", "retained_kicks", "penalty_records",
                                          "yard_split", "snap_values"}),
                         record_base=True)

PROFILES = {p.kernel_version: p for p in (PROFILE_2014_5, PROFILE_2014_6)}
for _profile in PROFILES.values():
    # A registered profile's base is the explicit table's (no drift).
    if _profile.base != base_for_kernel(_profile.kernel_version):
        raise ValueError("profile %s base differs from base_for_kernel" % _profile.kernel_version)
del _profile


def profile_for(version):
    """The registered profile of a kernel version; unknown raises."""
    try:
        return PROFILES[str(version)]
    except KeyError:
        raise ValueError("no kernel profile is registered for version %r" % (version,)) from None
