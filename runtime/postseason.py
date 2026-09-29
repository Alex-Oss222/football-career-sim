"""The 2013 postseason bracket, built from closed receipts only.

- Field: the final regular-season standings (`runtime.standings.compute`):
  per conference, the four division winners are seeds 1-4 and the two best
  remaining clubs are seeds 5-6.
- Wild Card (week 18): 3 hosts 6 and 4 hosts 5; seeds 1-2 have a bye.
- Divisional (week 19): reseeded. The 1 seed hosts the lowest remaining
  seed; the 2 seed hosts the other.
- Conference championships (week 20): the higher remaining seed hosts.
- Super Bowl (week 21): the two champions at a neutral site; the designated
  home conference follows `library/data/2013_postseason_slots.json`.

Dates, kickoff times and sites are the real 2013-14 slots, assigned to the
branch's games by seed matchup (the slots file). That rule is fixed before
any postseason draw and never looks at a result. A round is built only when
every game of the round before it has a closed receipt; postseason games
never end tied, so every closed receipt has a winner.
"""
import json
from pathlib import Path

from .league import conference_of
from .seasons import SeasonPaths, require_receipt_season

ROOT = Path(__file__).resolve().parents[1]
SLOTS = ROOT / "library" / "data" / "2013_postseason_slots.json"
REGULAR_RECEIPTS = ROOT / "career" / "2013" / "stats" / "game_receipts"
POSTSEASON_RECEIPTS = ROOT / "career" / "2013" / "stats" / "postseason_receipts"
ROUNDS = {18: "wild_card", 19: "divisional", 20: "conference", 21: "super_bowl"}
ROUND_TITLES = {"wild_card": "Wild Card", "divisional": "Divisional",
                "conference": "Conference Championship", "super_bowl": "Super Bowl XLVIII"}
CONFERENCES = ("AFC", "NFC")


def is_postseason(week):
    return int(week) in ROUNDS


def _load(directory):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.json"))]


def seeds(regular_receipts):
    """{conference: [team seeded 1, ..., team seeded 6]} from the final standings."""
    from .standings import compute
    result = compute(regular_receipts)
    field = {}
    for conference in CONFERENCES:
        entry = result["conferences"][conference]
        order = list(entry["division_winners"]) + list(entry["others"])
        field[conference] = order[:4 + result["wild_cards"]]
    return field


def winner(receipt):
    score = receipt["final_score"]
    (a, pa), (b, pb) = score.items()
    if pa == pb:
        raise ValueError("postseason receipt %s is tied" % receipt.get("event_id"))
    return a if pa > pb else b


def _slot(slots, week, conference, matchup):
    rounds = {r["week"]: r for r in slots["rounds"]}
    for slot in rounds[week]["slots"]:
        if slot["conference"] == conference and slot["matchup"] == matchup:
            return slot
    raise ValueError("no 2013 slot for week %d %s %s" % (week, conference, matchup))


def _game(week, conference, matchup, away, home, seed_of, slot):
    return {
        "week": week, "round": ROUNDS[week], "conference": conference, "matchup": matchup,
        "away": away, "home": home, "away_seed": seed_of.get(away), "home_seed": seed_of.get(home),
        "date": slot["date"], "kickoff_et": slot.get("kickoff_et"), "network": slot.get("network"),
        "site": slot.get("site", "home"), "venue": slot.get("venue"), "game_type": "postseason",
    }


def _round_winners(week, post_receipts, expected):
    closed = [r for r in post_receipts if int(r["week"]) == week]
    if len(closed) != expected:
        raise ValueError("postseason week %d has %d of %d closed games; the next round cannot be built"
                         % (week, len(closed), expected))
    return [winner(r) for r in closed]


def schedule(week, regular_receipts=None, post_receipts=None, slots=None, season=2013):
    """The games of one postseason week, in slot order."""
    week = int(week)
    if week not in ROUNDS:
        raise ValueError("week %d is not a postseason round" % week)
    paths = SeasonPaths(season, ROOT)
    regular_receipts = _load(paths.receipts) if regular_receipts is None else regular_receipts
    post_receipts = _load(paths.postseason_receipts) if post_receipts is None else post_receipts
    slots = json.loads(paths.postseason_slots.read_text(encoding="utf-8")) if slots is None else slots
    require_receipt_season(regular_receipts + post_receipts, season)
    field = seeds(regular_receipts)
    seed_of = {team: (conf, n) for conf in CONFERENCES for n, team in enumerate(field[conf], 1)}
    number = {team: n for team, (_, n) in seed_of.items()}
    games = []
    if week == 18:
        for conf in CONFERENCES:
            s = field[conf]
            games.append(_game(week, conf, "6@3", s[5], s[2], number, _slot(slots, week, conf, "6@3")))
            games.append(_game(week, conf, "5@4", s[4], s[3], number, _slot(slots, week, conf, "5@4")))
    elif week == 19:
        alive = set(_round_winners(18, post_receipts, 4))
        for conf in CONFERENCES:
            s = field[conf]
            remaining = sorted((t for t in s[2:] if t in alive), key=lambda t: number[t])
            low, other = remaining[-1], remaining[0]
            games.append(_game(week, conf, "low@1", low, s[0], number, _slot(slots, week, conf, "low@1")))
            games.append(_game(week, conf, "other@2", other, s[1], number, _slot(slots, week, conf, "other@2")))
    elif week == 20:
        alive = set(_round_winners(19, post_receipts, 4))
        for conf in CONFERENCES:
            left = sorted((t for t in field[conf] if t in alive), key=lambda t: number[t])
            games.append(_game(week, conf, "lower@higher", left[1], left[0], number,
                               _slot(slots, week, conf, "lower@higher")))
    else:
        champions = {conference_of(t): t for t in _round_winners(20, post_receipts, 2)}
        slot = _slot(slots, week, "NFL", slots["super_bowl_matchup"])
        home_conf = slots["designated_home_conference"]
        away_conf = "NFC" if home_conf == "AFC" else "AFC"
        games.append(_game(week, "NFL", slots["super_bowl_matchup"], champions[away_conf],
                           champions[home_conf], number, slot))
    return sorted(games, key=lambda g: (g["date"], g.get("kickoff_et") or ""))
