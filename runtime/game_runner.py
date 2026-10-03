"""Only production game entry point for every club and narration mode."""
from dataclasses import asdict
import hashlib
import inspect
import re

from . import KERNEL_VERSION
from .kernel import TeamInput, resolve_game, validate_result
from .packets import canonical
from .private_client import Client
from .player_evidence import normalize_players, serialize_roster
from . import player_state
from .strength import PLAYER_STATE_MODEL
from .play_detail import canonical_call_sheet
from .rotation import plan_errors
from .usage import lineup_errors
from .call_families import sheet_errors
from .rules import GAME_TYPES, active_limit

ENTROPY_DOMAIN = b"football-career-sim/event-entropy/v1\0"


def _team_packet(team):
    data = asdict(team)
    if data.get("strength") is None:
        data.pop("strength", None)  # legacy packets unchanged (kernel 2014.4 E1)
    # Availability and rotation are football inputs; protagonist labels are not.
    data["roster"] = serialize_roster(normalize_players(team))
    data["offensive_call_sheet"] = canonical_call_sheet(team)
    return data


def build_game_packet(event_id, snapshot, home, away, *, venue="home", weather="normal",
                      game_type="regular", management_mode="autonomous", game_date=None):
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("canonical event_id required")
    if game_type not in GAME_TYPES:
        raise ValueError("unknown game type")
    if game_date is not None and (not isinstance(game_date, str) or len(game_date) != 10):
        raise ValueError("game_date must be an ISO date string")
    if not isinstance(snapshot, str) or len(snapshot) < 8:
        raise ValueError("current snapshot digest required")
    if home.team_id == away.team_id:
        raise ValueError("game teams must differ")
    for team in (home, away):
        # Kernel 2014.6 (B7): a player-state record commits its public states
        # plus the league year's bound manifest digest, commitment and latent
        # keys; the manifest must be the pinned one and the binding present.
        record = team.strength
        if record and record.get("model") == PLAYER_STATE_MODEL:
            for field in ("league_year", "manifest_sha256", "commitment", "latent_keys"):
                if field not in record:
                    raise ValueError(f"{team.team_id} player-state record lacks {field}")
            bound = player_state.require_binding(record["league_year"])
            if record["manifest_sha256"] != bound["manifest_sha256"] or record["commitment"] != bound["commitment"]:
                raise ValueError(f"{team.team_id} player-state record names another binding than the committed one")
            if any("latent_value" in p for p in record.get("players", {}).values()):
                raise ValueError(f"{team.team_id} TeamInput carries drawn values before closure")
    if not normalize_players(home) or not normalize_players(away):
        raise ValueError("each club requires an available, roster-bound participant")
    for team in (home, away):
        # 2013 game-day rule: at most 46 active players (the other seven of
        # the 53 are declared inactive); a preseason game may dress the whole
        # roster (runtime.rules.active_limit). Fail closed before the private
        # event is journaled; which players are inactive is a football
        # decision made upstream (Stone for Jacksonville, depth order for others).
        actives = len(normalize_players(team))
        limit = active_limit(game_type)
        if actives > limit:
            raise ValueError(
                f"{team.team_id} TeamInput has {actives} game-day actives; the {game_type} limit is {limit}"
            )
        missing = lineup_errors(normalize_players(team))
        if missing:
            raise ValueError(
                f"{team.team_id} TeamInput is not a legal game-day unit: " + "; ".join(missing)
            )
        # Kernel 2013.7+ labels follow the ball carrier: every call must name
        # who it can describe (explicitly or through the 2013 family map).
        # Fail closed here, before the private event is journaled.
        undeclared = sheet_errors(getattr(team, "offensive_call_sheet", ()) or ())
        if undeclared:
            raise ValueError(f"{team.team_id} call sheet cannot be labelled: " + "; ".join(undeclared))
        # Preseason unit rotation (runtime/rotation.py): a plan naming a player
        # off the game-day unit or an unknown group, or any rotation block in
        # a non-preseason game, fails closed before the private event is journaled.
        rotation_faults = plan_errors(team, normalize_players(team), game_type)
        if rotation_faults:
            raise ValueError(f"{team.team_id} rotation plan: " + "; ".join(rotation_faults))
    packet = {
        "procedure": KERNEL_VERSION, "event_id": event_id, "snapshot": snapshot,
        "home": _team_packet(home), "away": _team_packet(away), "venue": venue,
        "weather": weather, "game_type": game_type,
        "management_mode": management_mode,
    }
    if game_date is not None:
        # Preseason only (the try rule is dated); absent from every other packet.
        packet["game_date"] = game_date
    return packet


def _entropy_from_ref(result_ref):
    if not isinstance(result_ref, str) or len(result_ref) != 64:
        raise ValueError("private runtime returned invalid opaque event reference")
    try: raw = bytes.fromhex(result_ref)
    except ValueError as exc: raise ValueError("private runtime returned invalid opaque event reference") from exc
    return hashlib.sha256(ENTROPY_DOMAIN + raw).digest()


def fetch_latent(client, event_id, home, away):
    """(home, away) with their drawn player states applied, fetched from the
    private service for a journaled event; unchanged, with no service call,
    when neither club carries a player-state record."""
    keys = player_state.keys_of_inputs(home, away)
    if not keys:
        return home, away
    records = [t.strength for t in (home, away) if t.strength and t.strength.get("model") == PLAYER_STATE_MODEL]
    years = {int(r["league_year"]) for r in records}
    commitments = {r["commitment"] for r in records}
    if len(years) != 1 or len(commitments) != 1:
        raise ValueError("the two clubs' player-state records name different bindings")
    data = client.latent_draws(event_id, next(iter(years)), keys, player_state.roster_sha256(keys))
    if data.get("commitment") != next(iter(commitments)):
        raise ValueError("private runtime served draws under another commitment than the packet's")
    return player_state.apply_latent(home, data["draws"]), player_state.apply_latent(away, data["draws"])


def run_game(home: TeamInput, away: TeamInput, *, event_id, snapshot,
             venue="home", weather="normal", game_type="regular",
             management_mode="autonomous", controlled_team=None, continuation=None,
             client=None, game_date=None):
    """Freeze canonical inputs privately, then and only then invoke the kernel.

    There is deliberately no seed parameter.  The authenticated service returns
    only an immutable opaque event reference, which is domain-separated into the
    kernel entropy bytes.

    Kernel 2014.4 (E2): a user-controlled game may return a partial result
    (``terminated`` False) at a consequential in-game substitution. Resume it
    by calling run_game again with the same inputs and a ``continuation``
    holding the decisions; the packet is unchanged, so the idempotent private
    closure returns the same event reference and the prefix reproduces. The
    continuation is validated by the kernel against the digest of the partial
    state it answers, so it needs no place in the packet.
    """
    match = re.match(r'^(\d{4})-', event_id)
    if match:
        from .seasons import preseason_scope, require_game_release
        require_game_release(int(match[1]), preseason=preseason_scope(event_id))
    client = client or Client(snapshot=snapshot)
    if client.snapshot != snapshot:
        raise ValueError("client and game snapshot differ")
    packet = build_game_packet(event_id, snapshot, home, away, venue=venue,
                               weather=weather, game_type=game_type,
                               management_mode=management_mode, game_date=game_date)
    result_ref = client.close_event(packet)  # durable closure precedes draw
    entropy = _entropy_from_ref(result_ref)
    # Kernel 2014.6 (B7): the player-state draws are fetched only after the
    # event is journaled, applied to deep copies of the inputs, and never
    # enter the packet. Inputs without a player-state record make no call.
    home, away = fetch_latent(client, event_id, home, away)
    result = resolve_game(home, away, seed=entropy, event_id=event_id, venue=venue,
                          weather=weather, game_type=game_type,
                          management_mode=management_mode, controlled_team=controlled_team,
                          continuation=continuation, game_date=game_date)
    if not result.get("terminated"):
        # A genuine partial result: completed events only, no final score.
        if "final_score" in result or "team_stats" in result:
            raise RuntimeError("kernel invariant failure: a paused result exposes final totals")
        return result
    errors = validate_result(result)
    if errors:
        raise RuntimeError("kernel invariant failure: " + "; ".join(errors))
    return result


# Narration callers differ only after this identical production function returns.
resolve_protagonist_game = run_game
resolve_background_game = run_game


def architecture_errors():
    params = inspect.signature(run_game).parameters
    errors = []
    if "seed" in params: errors.append("production runner accepts caller-supplied seed")
    if resolve_protagonist_game is not run_game or resolve_background_game is not run_game:
        errors.append("game paths do not share the production runner")
    if Client.close_event.__name__ not in inspect.getsource(run_game):
        # Keep the check explicit even if a wrapper is later introduced.
        if ".close_event(" not in inspect.getsource(run_game):
            errors.append("production runner does not close a private event")
    source = inspect.getsource(run_game)
    if source.find("close_event(") > source.find("resolve_game("):
        errors.append("kernel can run before private event closure")
    # Kernel 2014.6 plumbing (batch B1): production resolves only with the
    # profile of runtime.KERNEL_VERSION. The kernel's private test hooks
    # (_test_onsets, _test_profile, any later _test_*) are for tests and
    # acceptance scripts; the production runner may neither accept nor pass one.
    hooks = sorted(name for name in params if name.startswith("_test"))
    if hooks:
        errors.append("production runner accepts a test hook (%s)" % ", ".join(hooks))
    if "_test_" in source:
        errors.append("production runner passes a test hook to the kernel")
    return errors
