"""Only production game entry point for every club and narration mode."""
from dataclasses import asdict
import hashlib
import inspect

from . import KERNEL_VERSION
from .kernel import TeamInput, resolve_game, validate_result
from .packets import canonical
from .private_client import Client
from .player_evidence import normalize_players, serialize_roster
from .play_detail import canonical_call_sheet

ENTROPY_DOMAIN = b"football-career-sim/event-entropy/v1\0"


def _team_packet(team):
    data = asdict(team)
    # Availability and rotation are football inputs; protagonist labels are not.
    data["roster"] = serialize_roster(normalize_players(team))
    data["offensive_call_sheet"] = canonical_call_sheet(team)
    return data


def build_game_packet(event_id, snapshot, home, away, *, venue="home", weather="normal",
                      game_type="regular", management_mode="autonomous"):
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("canonical event_id required")
    if not isinstance(snapshot, str) or len(snapshot) < 8:
        raise ValueError("current snapshot digest required")
    if home.team_id == away.team_id:
        raise ValueError("game teams must differ")
    if not normalize_players(home) or not normalize_players(away):
        raise ValueError("each club requires an available, roster-bound participant")
    return {
        "procedure": KERNEL_VERSION, "event_id": event_id, "snapshot": snapshot,
        "home": _team_packet(home), "away": _team_packet(away), "venue": venue,
        "weather": weather, "game_type": game_type,
        "management_mode": management_mode,
    }


def _entropy_from_ref(result_ref):
    if not isinstance(result_ref, str) or len(result_ref) != 64:
        raise ValueError("private runtime returned invalid opaque event reference")
    try: raw = bytes.fromhex(result_ref)
    except ValueError as exc: raise ValueError("private runtime returned invalid opaque event reference") from exc
    return hashlib.sha256(ENTROPY_DOMAIN + raw).digest()


def run_game(home: TeamInput, away: TeamInput, *, event_id, snapshot,
             venue="home", weather="normal", game_type="regular",
             management_mode="autonomous", resume=None, client=None):
    """Freeze canonical inputs privately, then and only then invoke the kernel.

    There is deliberately no seed parameter.  The authenticated service returns
    only an immutable opaque event reference, which is domain-separated into the
    kernel entropy bytes.
    """
    client = client or Client(snapshot=snapshot)
    if client.snapshot != snapshot:
        raise ValueError("client and game snapshot differ")
    packet = build_game_packet(event_id, snapshot, home, away, venue=venue,
                               weather=weather, game_type=game_type,
                               management_mode=management_mode)
    result_ref = client.close_event(packet)  # durable closure precedes draw
    entropy = _entropy_from_ref(result_ref)
    result = resolve_game(home, away, seed=entropy, event_id=event_id, venue=venue,
                          weather=weather, game_type=game_type,
                          management_mode=management_mode, resume=resume)
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
    return errors
