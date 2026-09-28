"""One shared, cached synthetic kernel sample (2013.11) for the kernel test modules.

Resolving games is the slow part of the suite (the Railway image runs the
whole suite on every deploy), so the coherence, label and band tests share
one 250-game sample computed once per process. Synthetic seeds only; the
private service is never contacted.

Club A carries Jacksonville's Week 6 call sheet (families only: carriers and
targets come from the committed 2013 call-family map), plus five label probes:
a Jet Sweep and an RB Slow Screen from earlier weekly sheets, a Draw declared
for the quarterback, a Stick declared for tight ends only, and a run declared
'unspecified' that must never be used. Club B has no sheet (generic labels).
"""
from functools import lru_cache

from runtime.kernel import TeamInput, resolve_game
from support_rosters import game_day_roster

SEED = b"synthetic-calibration-seed-not-career-state"
SAMPLE_SIZE = 250
EVENT_PREFIX = "sample-2013-7"

WEEK6_SHEET = (
    {"name": "12 Ace Right, Power R", "family": "Power", "type": "run", "personnel": "12", "formation": "12 Ace Right"},
    {"name": "12 Trey Right, Stick, H Chip-Release", "family": "Stick", "type": "pass", "personnel": "12", "formation": "12 Trey Right"},
    {"name": "11 Bunch Right, Return, Mesh", "family": "Mesh", "type": "pass", "personnel": "11", "formation": "11 Bunch Right"},
    {"name": "12 Wing Right, Split L", "family": "Split Zone", "type": "run", "personnel": "12", "formation": "12 Wing Right"},
    {"name": "11 Doubles, Zip, Smoke", "family": "Smoke/Now", "type": "pass", "personnel": "11", "formation": "11 Doubles"},
    {"name": "12 Doubles, Drive, H Chip-Release, Solid", "family": "Drive", "type": "pass", "personnel": "12", "formation": "12 Doubles", "protection": "Solid"},
    {"name": "21 Pro Left, Counter R", "family": "Counter", "type": "run", "personnel": "21", "formation": "21 Pro Left"},
    {"name": "12 Bunch Right, Snag", "family": "Snag", "type": "pass", "personnel": "12", "formation": "12 Bunch Right"},
    {"name": "12 Wing Left, TE Delay", "family": "TE Delay", "type": "pass", "personnel": "12", "formation": "12 Wing Left"},
    {"name": "20 Doubles, Draw", "family": "Draw", "type": "run", "personnel": "20", "formation": "20 Doubles"},
    {"name": "12 Trey Right, Sprint Flood R", "family": "Sprint Flood", "type": "pass", "personnel": "12", "formation": "12 Trey Right"},
    {"name": "12 Ace, Shift Empty, Spacing", "family": "Spacing", "type": "pass", "personnel": "12", "formation": "12 Ace Shift Empty"},
    {"name": "6OL Heavy Right, Power R", "family": "Power", "type": "run", "personnel": "6OL", "formation": "6OL Heavy Right"},
    {"name": "12 Ace Right, Power Pass, Post-Cross, Max", "family": "Power Pass", "type": "pass", "personnel": "12", "formation": "12 Ace Right", "protection": "Max"},
    {"name": "11 Trips Right, Inside L, Access Bubble", "family": "Inside + Bubble", "type": "run", "personnel": "11", "formation": "11 Trips Right"},
)
LABEL_PROBES = (
    {"name": "11 Trey Right, Jet L", "family": "Jet Sweep", "type": "run", "personnel": "11", "formation": "11 Trey Right"},
    {"name": "12 Trey Right, RB Slow Screen", "family": "RB Slow Screen", "type": "pass", "personnel": "12", "formation": "12 Trey Right"},
    {"name": "QB Draw", "family": "Draw", "type": "run", "carrier": ["QB"]},
    {"name": "Stick TE", "family": "Stick", "type": "pass", "target": ["TE"]},
    {"name": "Unspecified probe", "family": "Probe", "type": "run", "carrier": "unspecified"},
)
TEAM_A_SHEET = WEEK6_SHEET + LABEL_PROBES


def team(prefix, calls=()):
    roster = game_day_roster(prefix)
    return TeamInput(prefix, tuple(p.player_id for p in roster), roster=roster,
                     offensive_call_sheet=tuple(calls))


def sample_teams():
    return team("A", TEAM_A_SHEET), team("B")


@lru_cache(maxsize=1)
def sample():
    a, b = sample_teams()
    return tuple(
        resolve_game(a, b, seed=SEED + b"-%05d" % i, event_id=f"{EVENT_PREFIX}-{i}")
        for i in range(SAMPLE_SIZE)
    )
