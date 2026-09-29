"""Standings, division ranks and playoff seeding from closed-game receipts.

Tiebreakers follow the 2013 order in Document 2 section 5.3 (NFL Record &
Fact Book). Procedural details that section summarizes, including restart
rules, the head-to-head sweep condition and shared combined-ranking places,
follow the NFL tiebreaking-procedure text. A step that cannot separate the
clubs passes to the next step; the final step, a coin toss, is never
simulated: the clubs stay ordered alphabetically and are reported as an
unbroken tie.

Receipts of one season are passed in (career/{season}/stats/game_receipts);
the 2013 order is the one verified here, and a later season's standings
page says so until its own procedure is verified.
"""
from dataclasses import dataclass, field

from .league import (
    CONFERENCES, DIVISION_OF, DIVISIONS, PLAYOFF_CLUBS_PER_CONFERENCE, TEAMS,
    conference_divisions, conference_of,
)


@dataclass(frozen=True)
class Game:
    week: int
    home: str
    away: str
    home_points: int
    away_points: int
    home_touchdowns: int
    away_touchdowns: int

    def teams(self):
        return (self.home, self.away)

    def opponent(self, team):
        return self.away if team == self.home else self.home

    def points(self, team):
        return self.home_points if team == self.home else self.away_points

    def touchdowns(self, team):
        return self.home_touchdowns if team == self.home else self.away_touchdowns

    def result(self, team):
        """1 win, 0.5 tie, 0 loss."""
        mine, theirs = self.points(team), self.points(self.opponent(team))
        return 1.0 if mine > theirs else 0.5 if mine == theirs else 0.0


def games_from_receipts(receipts):
    games = []
    for receipt in receipts:
        home, away = receipt["home"], receipt["away"]
        if receipt.get("game_type") == "preseason":
            # Preseason receipts live in preseason_receipts and never count.
            raise ValueError("preseason receipt %s cannot enter standings" % receipt.get("event_id"))
        for team in (home, away):
            if team not in DIVISION_OF:
                raise ValueError("unknown club in receipt %s: %s" % (receipt.get("event_id"), team))
        score = receipt["final_score"]
        stats = receipt["team_stats"]
        games.append(Game(
            week=int(receipt["week"]), home=home, away=away,
            home_points=int(score[home]), away_points=int(score[away]),
            home_touchdowns=int(stats[home].get("touchdowns", 0)),
            away_touchdowns=int(stats[away].get("touchdowns", 0)),
        ))
    games.sort(key=lambda g: (g.week, g.away, g.home))
    return games


@dataclass
class Record:
    wins: int = 0
    losses: int = 0
    ties: int = 0

    def add(self, result):
        if result == 1.0:
            self.wins += 1
        elif result == 0.0:
            self.losses += 1
        else:
            self.ties += 1

    @property
    def games(self):
        return self.wins + self.losses + self.ties

    @property
    def pct(self):
        return (self.wins + 0.5 * self.ties) / self.games if self.games else 0.0

    def text(self):
        return "%d-%d-%d" % (self.wins, self.losses, self.ties)


@dataclass
class TeamLine:
    team: str
    overall: Record = field(default_factory=Record)
    home: Record = field(default_factory=Record)
    away: Record = field(default_factory=Record)
    division: Record = field(default_factory=Record)
    conference: Record = field(default_factory=Record)
    points_for: int = 0
    points_against: int = 0
    streak: str = "-"


def pct_text(value):
    text = "%.3f" % value
    return text[1:] if text.startswith("0") else text


class Season:
    def __init__(self, games):
        self.games = list(games)
        self.by_team = {team: [] for team in TEAMS}
        for game in self.games:
            for team in game.teams():
                self.by_team[team].append(game)
        self.lines = {team: self._line(team) for team in TEAMS}
        self.notes = []
        self.recording = True

    # ---- records -------------------------------------------------------
    def _line(self, team):
        line = TeamLine(team)
        run_kind, run_length = None, 0
        for game in self.by_team[team]:
            result = game.result(team)
            opponent = game.opponent(team)
            line.overall.add(result)
            (line.home if game.home == team else line.away).add(result)
            if DIVISION_OF[opponent] == DIVISION_OF[team]:
                line.division.add(result)
            if conference_of(opponent) == conference_of(team):
                line.conference.add(result)
            line.points_for += game.points(team)
            line.points_against += game.points(opponent)
            kind = {1.0: "W", 0.5: "T", 0.0: "L"}[result]
            run_kind, run_length = (kind, run_length + 1) if kind == run_kind else (kind, 1)
        if run_kind:
            line.streak = "%s%d" % (run_kind, run_length)
        return line

    def pct(self, team):
        return self.lines[team].overall.pct

    def record_in(self, team, games):
        record = Record()
        for game in games:
            record.add(game.result(team))
        return record

    def games_against(self, team, opponents):
        return [g for g in self.by_team[team] if g.opponent(team) in opponents]

    # ---- tiebreak measures (higher is better; None = not applicable) ----
    def head_to_head(self, group):
        values = {}
        for team in group:
            games = self.games_against(team, set(group) - {team})
            if not games:
                return None
            values[team] = self.record_in(team, games).pct
        return values

    def head_to_head_sweep(self, group):
        """Returns (winner, eliminated) under the sweep condition."""
        def swept(team, want):
            for other in group:
                if other == team:
                    continue
                games = self.games_against(team, {other})
                if not games or any(g.result(team) != want for g in games):
                    return False
            return True
        winners = [t for t in group if swept(t, 1.0)]
        if len(winners) == 1:
            return winners[0], None
        losers = [t for t in group if swept(t, 0.0)]
        if len(losers) == 1:
            return None, losers[0]
        return None, None

    def division_pct(self, group):
        return {t: self.lines[t].division.pct for t in group}

    def conference_pct(self, group):
        return {t: self.lines[t].conference.pct for t in group}

    def common_opponents(self, group):
        sets = [{g.opponent(t) for g in self.by_team[t]} - set(group) for t in group]
        return set.intersection(*sets) if sets else set()

    def common_pct(self, group, minimum=0):
        common = self.common_opponents(group)
        if not common:
            return None
        values = {}
        for team in group:
            games = self.games_against(team, common)
            if len(games) < minimum or not games:
                return None
            values[team] = self.record_in(team, games).pct
        return values

    def _combined_pct(self, opponents):
        wins = games = 0.0
        for opponent in opponents:
            record = self.lines[opponent].overall
            wins += record.wins + 0.5 * record.ties
            games += record.games
        return wins / games if games else 0.0

    def strength_of_victory(self, group):
        return {t: self._combined_pct([g.opponent(t) for g in self.by_team[t] if g.result(t) == 1.0])
                for t in group}

    def strength_of_schedule(self, group):
        return {t: self._combined_pct([g.opponent(t) for g in self.by_team[t]]) for t in group}

    def _rank(self, pool, key, descending):
        """Shared places count as held alone: 1, 1, 3."""
        values = {t: key(t) for t in pool}
        return {t: 1 + sum(1 for o in pool if (values[o] > values[t] if descending else values[o] < values[t]))
                for t in pool}

    def combined_ranking(self, group, pool):
        scored = self._rank(pool, lambda t: self.lines[t].points_for, True)
        allowed = self._rank(pool, lambda t: self.lines[t].points_against, False)
        return {t: -(scored[t] + allowed[t]) for t in group}

    def combined_ranking_conference(self, group):
        conference = conference_of(group[0])
        return self.combined_ranking(group, [t for t in TEAMS if conference_of(t) == conference])

    def combined_ranking_league(self, group):
        return self.combined_ranking(group, list(TEAMS))

    def net_points_in(self, group, games_for):
        values = {}
        for team in group:
            games = games_for(team)
            values[team] = sum(g.points(team) - g.points(g.opponent(team)) for g in games)
        return values

    def net_points_common(self, group):
        common = self.common_opponents(group)
        if not common:
            return None
        return self.net_points_in(group, lambda t: self.games_against(t, common))

    def net_points_conference(self, group):
        return self.net_points_in(group, lambda t: [
            g for g in self.by_team[t] if conference_of(g.opponent(t)) == conference_of(t)])

    def net_points_all(self, group):
        return self.net_points_in(group, lambda t: self.by_team[t])

    def net_touchdowns(self, group):
        return {t: sum(g.touchdowns(t) - g.touchdowns(g.opponent(t)) for g in self.by_team[t])
                for t in group}

    # ---- procedures ------------------------------------------------------
    def division_steps(self):
        return (
            ("head-to-head", self.head_to_head),
            ("division record", self.division_pct),
            ("record in common games", self.common_pct),
            ("conference record", self.conference_pct),
            ("strength of victory", self.strength_of_victory),
            ("strength of schedule", self.strength_of_schedule),
            ("combined conference ranking in points scored and allowed", self.combined_ranking_conference),
            ("combined league ranking in points scored and allowed", self.combined_ranking_league),
            ("net points in common games", self.net_points_common),
            ("net points in all games", self.net_points_all),
            ("net touchdowns in all games", self.net_touchdowns),
        )

    def wild_card_steps(self, three_or_more):
        head = ("head-to-head sweep", None) if three_or_more else ("head-to-head", self.head_to_head)
        return (
            head,
            ("conference record", self.conference_pct),
            ("record in common games (minimum four)", lambda g: self.common_pct(g, minimum=4)),
            ("strength of victory", self.strength_of_victory),
            ("strength of schedule", self.strength_of_schedule),
            ("combined conference ranking in points scored and allowed", self.combined_ranking_conference),
            ("combined league ranking in points scored and allowed", self.combined_ranking_league),
            ("net points in conference games", self.net_points_conference),
            ("net points in all games", self.net_points_all),
            ("net touchdowns in all games", self.net_touchdowns),
        )

    def best_of(self, group, context, division_ranks=None):
        """Return the club that wins the tie among `group` and record why."""
        group = sorted(group)
        if len(group) == 1:
            return group[0]
        same_division = len({DIVISION_OF[t] for t in group}) == 1
        if not same_division:
            reduced = self._reduce_to_division_leaders(group, division_ranks, context)
            if len(reduced) < len(group):
                return self.best_of(reduced, context, division_ranks)
        steps = self.division_steps() if same_division else self.wild_card_steps(len(group) > 2)
        for name, measure in steps:
            if measure is None:
                winner, eliminated = self.head_to_head_sweep(group)
                if winner:
                    self._note(context, winner, group, name)
                    return winner
                if eliminated:
                    return self.best_of([t for t in group if t != eliminated], context, division_ranks)
                continue
            values = measure(group)
            if values is None:
                continue
            best = max(values.values())
            leaders = [t for t in group if values[t] == best]
            if len(leaders) == 1:
                self._note(context, leaders[0], group, name)
                return leaders[0]
            if len(leaders) < len(group):
                return self.best_of(leaders, context, division_ranks)
        self._note(context, group[0], group, None)
        return group[0]

    def _reduce_to_division_leaders(self, group, division_ranks, context):
        by_division = {}
        for team in group:
            by_division.setdefault(DIVISION_OF[team], []).append(team)
        if all(len(teams) == 1 for teams in by_division.values()):
            return group
        reduced = []
        for division, teams in sorted(by_division.items()):
            if len(teams) == 1:
                reduced.append(teams[0])
            else:
                order = division_ranks[division]
                reduced.append(min(teams, key=order.index))
        return reduced

    def _note(self, context, winner, group, step):
        if not self.recording:
            return
        others = [t for t in group if t != winner]
        self.notes.append({"context": context, "winner": winner, "others": others, "step": step})

    def order(self, teams, context, division_ranks=None, noted_places=None):
        """Order clubs by percentage, breaking each tie by the procedure.

        Tiebreak notes are kept for the first `noted_places` places (all
        places when None); the order of clubs outside the playoff field is
        still decided by the procedure but not annotated.
        """
        remaining = sorted(teams)
        ordered = []
        while remaining:
            self.recording = noted_places is None or len(ordered) < noted_places
            best_pct = max(self.pct(t) for t in remaining)
            tied = [t for t in remaining if self.pct(t) == best_pct]
            winner = self.best_of(tied, context, division_ranks) if len(tied) > 1 else tied[0]
            ordered.append(winner)
            remaining.remove(winner)
        self.recording = True
        return ordered

    def division_ranks(self):
        return {division: self.order(teams, division) for division, teams in DIVISIONS.items()}

    def conference_order(self, conference, division_ranks):
        """Seeds 1-4 are division winners, 5-6 wild cards, then the rest."""
        winners = [division_ranks[d][0] for d in conference_divisions(conference)]
        seeded = self.order(winners, conference + " seeding", division_ranks)
        others = [t for t in TEAMS if conference_of(t) == conference and t not in winners]
        rest = self.order(others, conference + " wild card", division_ranks,
                          noted_places=PLAYOFF_CLUBS_PER_CONFERENCE - len(winners))
        return seeded, rest


def compute(receipts):
    """Return the full standings picture for rendering."""
    season = Season(games_from_receipts(receipts))
    played = bool(season.games)
    division_ranks = season.division_ranks() if played else {
        division: sorted(teams) for division, teams in DIVISIONS.items()}
    conferences = {}
    for conference in CONFERENCES:
        if played:
            seeded, rest = season.conference_order(conference, division_ranks)
        else:
            seeded, rest = [], sorted(t for t in TEAMS if conference_of(t) == conference)
        conferences[conference] = {"division_winners": seeded, "others": rest}
    return {
        "played": played,
        "through_week": max((g.week for g in season.games), default=0),
        "lines": season.lines,
        "division_ranks": division_ranks,
        "conferences": conferences,
        "notes": season.notes if played else [],
        "sov": season.strength_of_victory(list(TEAMS)),
        "sos": season.strength_of_schedule(list(TEAMS)),
        "wild_cards": PLAYOFF_CLUBS_PER_CONFERENCE - 4,
    }
