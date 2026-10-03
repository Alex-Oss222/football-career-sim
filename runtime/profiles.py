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
  R11 (batch B11) owns it.
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
FLAGS = BASE_FLAGS | {"injury_2014_6", "usage_2014_6"} | B6_FLAGS


def _legacy_base():
    from .calibration_base import BASE_2012
    return BASE_2012


PROFILE_2014_5 = Profile("2014.5", base="2012", cell_rules="2013.7", strength="honours-production-v3")
PROFILE_2014_6 = Profile("2014.6", base="2010_2014w4", cell_rules="2014.6", strength="player-state-v1",
                         flags=frozenset({"base_2014_6", "regimes_v3", "injury_2014_6", "usage_2014_6",
                                          "early_fg_v2", "clock_detail_v1", "substitution_record"}),
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
