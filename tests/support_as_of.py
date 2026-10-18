"""Jacksonville's controlled roster as it stood before a closed week's game.

Tests and acceptance checks that rebuild a week's Jacksonville input after
the week has closed read the current roster, which already carries the
instructions that game produced (the Week 5 injuries to Christian Jones and
Brynden Trawick, for example). Before kickoff those instructions did not
exist. `roster_before_week` presents the roster without them: a player whose
injury is logged in a closed receipt of that week or later is read as having
no communicated restriction for the build. Real builds never use it; the
runtime reads the roster as it stands.
"""
from contextlib import contextmanager
from unittest import mock

from runtime import week_inputs
from runtime.seasons import SeasonPaths


def game_injured(week, season=2014, root=None):
    """Jacksonville players whose injury is logged in a closed receipt of
    `week` or later."""
    from scripts.render_season_stats import load_receipts
    paths = SeasonPaths(season, root) if root is not None else SeasonPaths(season)
    injured = set()
    for receipt in load_receipts(paths.receipts):
        if int(receipt["week"]) >= int(week):
            for injury in receipt.get("injuries", ()):
                if injury.get("team") == week_inputs.PROTAGONIST:
                    injured.add(injury["player"])
    return injured


@contextmanager
def roster_before_week(week, season=2014, root=None):
    """Patch `week_inputs.controlled_active` (the roster read by
    `jacksonville_input`) so the instructions from `week`'s game and later
    are not yet on it. Yields the set of players it cleared."""
    injured = game_injured(week, season, root)
    real = week_inputs.controlled_active

    def before(season_arg=season, roster_path=None):
        return [(player, week_inputs.AVAILABLE_TEXT if player in injured else availability)
                for player, availability in real(season_arg, roster_path)]

    with mock.patch.object(week_inputs, "controlled_active", before):
        yield injured
