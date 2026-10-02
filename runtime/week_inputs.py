"""Weekly TeamInput package for any regular-season week.

- Slate: `library/data/2013_schedule.json` (schedule rails only).
- Background clubs: the sourced Week 1 units (`runtime.depth_library`),
  carried forward. Later real depth charts are not read: they reflect real
  games' injuries and results, which the branch never had. A player already
  out before Week 1 returns at the library's `return_week`. From the
  in-season rails' effective week (2014: Week 5) each background unit is
  the club's active list in the in-season rails replay at the game's cutoff
  (`runtime.rails`, library/2014_inseason_rails.md): the other clubs' real
  roster moves, held to 53 and never invented.
- Availability: every injury in a closed receipt keeps its player out until
  the injury date plus its projected return days; Jacksonville's own medical
  holds come from `career/2013/roster.md`.
- Jacksonville: the controlled active roster, `career/2013/depth_chart.json`
  (order, roles, inactives) and the week's structured call sheet.

Unit anchors are passed in explicitly (Document 7 section 2.2). From the
2014 season each TeamInput also carries its dated honours strength record
(kernel 2014.4 E1, runtime/strength.py), built by one rule for every club.
"""
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from . import call_families, depth_library, player_bios, rails, strength
from .usage import group, lineup_errors
from .seasons import SeasonPaths, require_receipt_season

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "library" / "data" / "2013_schedule.json"
ROSTER = ROOT / "career" / "2013" / "roster.md"
DEPTH_CHART = ROOT / "career" / "2013" / "depth_chart.json"
PROTAGONIST = "Jacksonville Jaguars"
AVAILABLE_TEXT = "No communicated restriction"
GAME_DAY_ACTIVES = 46
LIMITED_TEXT = "Limited, no projected absence"
UNIT = depth_library.UNIT


def slug(team, sep):
    return re.sub(r"[^a-z0-9]+", sep, team.lower()).strip(sep)


def schedule(week, season=2013):
    from . import postseason
    if postseason.is_postseason(week):
        # Weeks 18-21: the bracket built from closed receipts (runtime.postseason).
        return postseason.schedule(week, season=season)
    games = [g for g in SeasonPaths(season, ROOT).regular_games() if g["week"] == week]
    if not games:
        raise ValueError("no %d schedule for week %s" % (season, week))
    return games


GENERATIONS = ROOT / "career/2013/migrations/event_generations.json"


def event_generation(week, season=2013):
    """The current event generation for a week: 1 unless a user-authorized
    void in career/2013/migrations/event_generations.json replaced it."""
    generations = SeasonPaths(season, ROOT).generations
    if not generations.exists():
        return 1
    weeks = json.loads(generations.read_text(encoding="utf-8")).get("weeks", {})
    return int(weeks.get(str(int(week)), {}).get("current_generation", 1))


def event_id(game, generation=None, season=2013):
    generation = event_generation(game["week"], season) if generation is None else generation
    base = "%d-week%02d-%s-at-%s" % (season, game["week"], slug(game["away"], "-"), slug(game["home"], "-"))
    return base if generation == 1 else "%s-g%d" % (base, generation)


def receipt_name(game):
    return "week_%02d_%s_at_%s.json" % (game["week"], slug(game["away"], "_"), slug(game["home"], "_"))


def _game_dates(season=2013):
    from . import postseason
    games = SeasonPaths(season, ROOT).regular_games()
    dates = {(g["week"], g["away"], g["home"]): date.fromisoformat(g["date"]) for g in games}
    # Closed postseason rounds: their games can always be rebuilt from receipts.
    for week in sorted(postseason.ROUNDS):
        try:
            rows = postseason.schedule(week, season=season)
        except (ValueError, FileNotFoundError, KeyError):
            break
        dates.update({(g["week"], g["away"], g["home"]): date.fromisoformat(g["date"]) for g in rows})
    return dates


def projected_returns(receipts, season=2013):
    """Every injury in a closed receipt with its projected return date, in
    receipt order: the one projection `injured_out` and the in-season
    rails' branch reserve rule (C6) both read (engineering review S6)."""
    require_receipt_season(receipts, season)
    dates = _game_dates(season)
    out = []
    for receipt in receipts:
        played = dates[(int(receipt["week"]), receipt["away"], receipt["home"])]
        for injury in receipt.get("injuries", ()):
            days = injury.get("return_days") or 0
            if injury.get("restriction") == "limited" and not days:
                continue
            out.append({"player": injury["player"], "team": injury.get("team"), "played": played,
                        "back": played + timedelta(days=days), "restriction": injury.get("restriction"),
                        "injury_class": injury.get("injury_class"), "week": int(receipt["week"])})
    return out


def injured_out(receipts, game_day, season=2013):
    """{player_id: reason} for players still inside their projected return window."""
    out = {}
    for r in projected_returns(receipts, season):
        if game_day < r["back"]:
            out[r["player"]] = "%s (%s), projected return %s" % (
                r["restriction"], r["injury_class"], r["back"].isoformat())
    return out


def _out_until(receipts, game_day, season):
    out = {}
    for r in projected_returns(receipts, season):
        if game_day < r["back"]:
            out[r["player"]] = r["back"]
    return out


def last_regular_date(season):
    return max(date.fromisoformat(g["date"]) for g in SeasonPaths(season, ROOT).regular_games())


def season_last_cutoffs(season):
    """{week: its last cutoff} for every scheduled week of the season: the
    regular season and every postseason round whose games can be built
    (runtime.rails.slate_cutoffs). Cutoffs come only from the schedule, so
    this reads nothing a closed week could not have known; a row found late
    or a branch event from a later week can never replay inside an earlier
    week's state (engineering review B5)."""
    from . import postseason
    out = {}
    regular = sorted({g["week"] for g in SeasonPaths(season, ROOT).regular_games()})
    for w in regular + sorted(postseason.ROUNDS):
        try:
            out[w] = max(rails.slate_cutoffs(schedule(w, season)).values())
        except (ValueError, FileNotFoundError, KeyError):
            break
    return out


def _kickoff_order(games, season):
    return sorted(games, key=lambda g: (g["date"], g.get("kickoff_et") or "", event_id(g, season=season)))


def rails_slate(week, season, receipts, games=None, root=ROOT, data=None, control=None, strict=True):
    """The in-season rails for one weekly slate, or None before the rails'
    effective week (closed Weeks 1 to 4 keep the Week 1 library entries).

    One league state per distinct cutoff in the slate, replaying the
    committed moves, the branch reserve placements from closed receipts (C6)
    and any emergency promotion (engineering review S5) recomputed week by
    week from the receipts that existed then. Cutoffs are taken in order and
    each cutoff's games in kickoff order: a player already in an earlier
    game's TeamInput that week is left out of every later game's TeamInput
    (engineering review B1), and the emergency check sees each club without
    those players. Raises on any replay error unless `strict` is False
    (the builder's no-op labelling reads the errors instead)."""
    data = data if data is not None else rails.load(season, root)
    if data is None or int(week) < data.effective_from_week:
        return None
    games = games if games is not None else schedule(week, season)
    lasts = season_last_cutoffs(season)
    control = control if control is not None else rails.jacksonville_control(season, root)
    c6 = rails.c6_events(projected_returns(receipts, season), last_regular_date(season), lasts,
                         lambda r: r["week"], data.effective_from_week)
    emergencies, states, computed = [], {}, []
    entries, deferred = {}, []
    for w in range(data.effective_from_week, int(week) + 1):
        wgames = games if w == int(week) else schedule(w, season)
        wcut = rails.slate_cutoffs(wgames)
        prior = [r for r in receipts if int(r["week"]) < w]
        used = {}  # player id -> the earlier game's event id this week
        for cutoff in sorted(set(wcut.values())):
            at = [g for g in _kickoff_order(wgames, season) if wcut[rails.game_key(g)] == cutoff]
            while True:
                branch = rails.Branch(control, tuple(c6 + emergencies))
                state = rails.league_state(data, cutoff, branch, lasts)
                known = {e["id"] for e in emergencies}
                new = []
                for g in at:
                    out = _out_until(prior, date.fromisoformat(g["date"]), season)
                    for side in ("away", "home"):
                        if g[side] == PROTAGONIST:
                            continue
                        new += [e for e in rails.emergency_events(state, data.codes[g[side]], w, out, cutoff,
                                                                  depth_library.available, excluded=used)
                                if e["id"] not in known]
                if not new:
                    break
                emergencies += new
            computed.append(state)
            for g in at:
                for side in ("away", "home"):
                    team = g[side]
                    if team == PROTAGONIST:
                        continue
                    club = state.club_entry(data.codes[team])
                    keep = []
                    for p in club["players"]:
                        if p["player_id"] in used:
                            if w == int(week):
                                deferred.append({"player_id": p["player_id"], "club": team,
                                                 "event_id": event_id(g, season=season),
                                                 "earlier_event_id": used[p["player_id"]]})
                            continue
                        keep.append(p)
                    if w == int(week):
                        entries[(rails.game_key(g), team)] = dict(club, players=keep)
                    for p in keep:
                        used[p["player_id"]] = event_id(g, season=season)
            if w == int(week):
                states[cutoff] = state
    errors = sorted({e for s in computed for e in s.errors})
    if errors and strict:
        raise ValueError("in-season rails: " + "; ".join(errors[:10]))
    return {"data": data, "states": states, "cutoffs": rails.slate_cutoffs(games), "c6": c6,
            "emergencies": emergencies, "last_cutoffs": lasts, "entries": entries, "deferred": deferred,
            "errors": errors, "branch": rails.Branch(control, tuple(c6 + emergencies))}


def background_input(team, week, receipts, game_day, anchors, season=2013, club=None):
    """A background club's TeamInput: its Week 1 library entry, or, from the
    in-season rails' effective week, `club` (its rails entry at the game's
    cutoff, required then)."""
    if club is not None:
        team_input = depth_library.club_input(team, club, week=week, **anchors)
    else:
        team_input = depth_library.team_input(team, week=week, season=season, **anchors)
    out = injured_out(receipts, game_day, season)
    for player in team_input["roster"]:
        if player["player_id"] in out:
            player["available"] = False
    team_input["active_players"] = game_day_actives(team_input["roster"])
    return team_input


GAME_DAY_ACTIVE_LIMIT = 46


def game_day_actives(roster):
    """A background club's 46 game-day actives, chosen mechanically from depth.

    No club's real inactive list is imported. While more than 46 players are
    available, the deepest-ranked player in the club's depth order is made
    inactive (the larger position group first on a tie), never below a legal
    game-day unit. Jacksonville's inactives are Stone's decision instead.
    """
    rows = [p for p in roster if p["available"]]
    sizes = {}
    for p in rows:
        sizes[group(p["position"])] = sizes.get(group(p["position"]), 0) + 1
    def deepest_first(item):
        index, p = item
        depth = p.get("depth") if isinstance(p.get("depth"), int) else 99
        return (-depth, -sizes.get(group(p["position"]), 0), -index)
    order = [p for _, p in sorted(enumerate(rows), key=deepest_first)]
    active = list(rows)
    for candidate in order:
        if len(active) <= GAME_DAY_ACTIVE_LIMIT:
            break
        trial = [p for p in active if p is not candidate]
        if not lineup_errors([_Row(p) for p in trial]):
            active = trial
    return [p["player_id"] for p in active]


class _Row:
    def __init__(self, row):
        self.position = row["position"]


def controlled_active(season=2013, roster_path=None):
    """(player, availability text) for every Jacksonville active-53 player."""
    rows = []
    status_col = avail_col = None
    path = roster_path or SeasonPaths(season, ROOT).roster
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            status_col = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Player" in cells:
            status_col = cells.index("Status") if "Status" in cells else None
            avail_col = cells.index("Availability") if "Availability" in cells else None
            continue
        if status_col is None or set(cells[0]) <= {"-", ":"}:
            continue
        # "Active 53" alone or with a dated parenthetical ("Active 53 (signed August 31, 2014)").
        if re.match(r"Active 53(?:\s*\(|$)", cells[status_col]):
            rows.append((cells[0], cells[avail_col] if avail_col is not None else AVAILABLE_TEXT))
    return rows


HOLD_NOTE = re.compile(r"\b(Out|hold|Suspended|Reserve|Non-football|Exempt)\b", re.IGNORECASE)
PROJECTED_RETURN = re.compile(r"projected return ([A-Z][a-z]+ \d{1,2}(?:, \d{4})?)")


def roster_available(availability, game_day, season=2013):
    """Whether a roster availability note clears a player for `game_day`.

    A game injury recorded with a projected return clears on that date, the
    rule every background club gets; a hold without a date (a medical hold,
    a suspension) clears only when the roster entry is changed. A player
    listed as limited with no projected absence plays, as for every club.
    """
    if availability.startswith(AVAILABLE_TEXT) or availability.startswith(LIMITED_TEXT):
        return True
    match = PROJECTED_RETURN.search(availability)
    if not match:
        if not HOLD_NOTE.search(availability):
            # A note that is neither clear, limited, dated nor an explicit
            # hold is a data defect, not a hold: fail the build (Entry 57).
            raise ValueError("unrecognized availability note: %r" % availability)
        return False
    text = match.group(1)
    if season != 2013 and "," not in text:
        raise ValueError('New-season projected returns require an explicit year')
    back = datetime.strptime(text if "," in text else text + ", 2013", "%B %d, %Y").date()
    return game_day >= back


def jacksonville_input(receipts, game_day, anchors, call_sheet, season=2013):
    undeclared = call_families.sheet_errors(call_sheet)
    if undeclared:
        # Kernel 2013.7 fails closed on a call no label rule covers.
        raise ValueError("call sheet cannot be labelled: " + "; ".join(undeclared))
    chart = json.loads(SeasonPaths(season, ROOT).depth_chart.read_text(encoding="utf-8"))
    depth = {player: rank for players in chart["depth"].values() for rank, player in enumerate(players, 1)}
    injured = injured_out(receipts, game_day, season)
    inactives = set(chart["game_day_inactives"]["players"])
    roster, missing = [], []
    for player, availability in controlled_active(season):
        if player not in depth:
            missing.append(player)
            continue
        position = chart["positions"][player]
        cleared = roster_available(availability, game_day, season)
        roster.append({
            "player_id": player, "position": position,
            "available": cleared and player not in injured,
            "unit": UNIT[group(position)], "roles": chart["roles"].get(player, []),
            "depth": depth[player],
            "medical_limitation": None if cleared else availability,
        })
    if missing:
        raise ValueError("depth_chart.json does not place: " + ", ".join(missing))
    active = [p["player_id"] for p in roster if p["available"] and p["player_id"] not in inactives]
    healthy_inactive = [p["player_id"] for p in roster if p["available"] and p["player_id"] in inactives]
    if len(active) < GAME_DAY_ACTIVES and healthy_inactive:
        # 2013 clubs dress 46 while healthy players remain: an unavailable
        # player missing from Stone's inactive list is a plan gap to resolve
        # before the draw, never a silent 45-man unit (Entry 57).
        unlisted = [p["player_id"] for p in roster if not p["available"] and p["player_id"] not in inactives]
        raise ValueError("Jacksonville would dress %d, not %d: unavailable but not listed inactive: %s; "
                         "healthy inactives: %s" % (len(active), GAME_DAY_ACTIVES, ", ".join(unlisted) or "none",
                                                     ", ".join(healthy_inactive)))
    return {
        "team_id": PROTAGONIST,
        "active_players": active,
        **anchors, "roster": roster, "offensive_call_sheet": list(call_sheet),
    }


def _rails_clubs(slate, games, season):
    """{(event key, team): club entry} and the deferral log, as the slate
    assigned them in kickoff order (date, kickoff time, event id): a player
    already in an earlier game's TeamInput this week is left out of any later
    game's TeamInput (engineering review B1); he stays on his club's list and
    counts toward its 53."""
    return dict(slate["entries"]), list(slate["deferred"])


def _rails_metadata(slate, games, season, deferred):
    data = slate["data"]
    folder = rails.data_dir(season, ROOT)
    return {
        "effective_from_week": data.effective_from_week, "as_of": data.as_of.isoformat(),
        "manifest_sha256": rails.sha256_file(folder / "manifest.json"),
        "files": {s["path"]: s["sha256"] for s in data.manifest["shards"]} | {
            data.manifest["base"]["path"]: data.manifest["base"]["sha256"]},
        "cutoffs": {event_id(g, season=season): slate["cutoffs"][rails.game_key(g)].isoformat() for g in games},
        "state_digests": {c.isoformat(): s.digest() for c, s in sorted(slate["states"].items())},
        "held": {c.isoformat(): sum(len(h["active"]) + len(h["practice_squad"]) for h in s.held.values())
                 for c, s in sorted(slate["states"].items())},
        "branch_reserve": [e["id"] for e in slate["c6"]],
        "emergency": [e["id"] for e in slate["emergencies"]],
        "slate_deferred": deferred,
    }


def strength_identities(roster, season, club=None, protagonist=False, registry=None):
    """Roster rows with their gsis id for runtime.strength, never in the
    TeamInput (PlayerInput has no gsis field). Background players take the
    rails entry's id; Jacksonville's come from the identity registry and fail
    closed when missing (engineering review B6)."""
    ids = {}
    if club is not None:
        ids = {p["player_id"]: p.get("gsis_id") for p in club["players"]}
    elif protagonist:
        registry = player_bios.load() if registry is None else registry
        missing = [r["player_id"] for r in roster if not (registry.get(r["player_id"]) or {}).get("gsis_id")]
        if missing:
            raise ValueError("strength identity: no gsis id for " + ", ".join(missing))
        ids = {r["player_id"]: registry[r["player_id"]]["gsis_id"] for r in roster}
    return [dict(r, gsis_id=ids.get(r["player_id"])) for r in roster]


def build_package(week, receipts, call_sheet, anchors, season=2013):
    games = []
    coverage = {}
    birth_dates = player_bios.load()
    slate_games = schedule(week, season)
    slate = rails_slate(week, season, receipts, slate_games) if season != 2013 else None
    clubs, deferred = _rails_clubs(slate, slate_games, season) if slate else ({}, [])
    if slate:
        # Newcomers' public birth dates (nflverse players, carried in the
        # rails rows and base) for players the registry does not hold yet.
        birth_dates = dict(rails.identities(slate["data"]), **birth_dates)
    for game in slate_games:
        game_day = date.fromisoformat(game["date"])

        def unit(team):
            club = clubs.get((rails.game_key(game), team)) if slate else None
            if team == PROTAGONIST:
                data = jacksonville_input(receipts, game_day, anchors, call_sheet, season)
            else:
                data = background_input(team, week, receipts, game_day, anchors, season, club=club)
            if season != 2013:
                # Kernel 2014.4 E1: every club, Jacksonville included, gets
                # its dated honours record by the same rule, as of the game
                # day (runtime/strength.py). The closed 2013 season is never
                # rebuilt with it. From the rails' effective week every club
                # joins by gsis id (engineering review B6).
                rows = (strength_identities(data["roster"], season, club=club, protagonist=team == PROTAGONIST)
                        if slate else data["roster"])
                data["strength"], coverage[team] = strength.team_strength(team, rows, season, game_day)
            return data

        games.append({
            "event_id": event_id(game, season=season), "receipt": receipt_name(game), "week": week,
            "date": game["date"], "away": game["away"], "home": game["home"],
            "venue": "neutral" if game["site"] == "neutral" else "home",
            "game_type": game.get("game_type", "regular"),
            **{key: game[key] for key in ("round", "conference", "matchup", "kickoff_et", "network",
                                          "away_seed", "home_seed") if key in game},
            "away_input": unit(game["away"]), "home_input": unit(game["home"]),
        })
        # Public preparation metadata, deliberately outside TeamInput and the
        # outcome packet. Birthdays cannot reroll already-frozen football.
        # A background player with no verified birth date enters with
        # age None and age_unverified (carried into the receipt, as for a
        # preseason opponent); every Jacksonville player still fails closed.
        games[-1]["player_ages"] = player_bios.biographies(
            [p["player_id"] for side in ("away_input", "home_input")
             for p in games[-1][side]["roster"]], game_day, birth_dates,
            allow_unverified=[p["player_id"] for side in ("away", "home")
                              if game[side] != PROTAGONIST
                              for p in games[-1][side + "_input"]["roster"]])
    package = {"season": season, "week": week, "games": games}
    if coverage:
        # Public preparation metadata outside TeamInput: E1 evidence coverage
        # and every Average fallback, per club.
        package["strength_coverage"] = {
            team: {k: v for k, v in c.items()} for team, c in sorted(coverage.items())}
    if slate:
        # Public preparation metadata outside TeamInput and the outcome
        # packet: the rails files, cutoffs and state digests the week used.
        package["rails"] = _rails_metadata(slate, slate_games, season, deferred)
    return package
