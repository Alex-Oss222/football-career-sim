"""Explicit season routing. A missing new-season input never falls back to 2013.

Historical Python callers default to 2013 to preserve reproducible receipts;
operator commands require a season or use the map's explicit planning season.
Current record ownership is separate from the season being prepared.
"""
from dataclasses import dataclass
import json
from pathlib import Path
import re
from .season_layout import season_relative

ROOT = Path(__file__).resolve().parents[1]
RELEASE_GATES = {'tier1_engine', 'season_rules', 'season_closure', 'dated_fixtures',
                 'legal_rosters', 'financial_control'}


def active_season(root=ROOT):
    return int(json.loads((Path(root) / 'docs/repository_map.json').read_text())['active_season'])


def current_record(name, root=ROOT):
    root = Path(root).resolve()
    mapping = json.loads((root / 'docs/repository_map.json').read_text())
    target = (root / mapping['current_records'][name]).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError('Missing or invalid current record: ' + name)
    return target


@dataclass(frozen=True)
class SeasonPaths:
    year: int
    root: Path = ROOT

    def __post_init__(self):
        if type(self.year) is not int or not 2013 <= self.year <= 2100:
            raise ValueError('Unsupported season: %r' % self.year)
        object.__setattr__(self, 'root', Path(self.root).resolve())

    @property
    def career(self): return self.root / 'career' / str(self.year)

    def record(self, relative):
        return self.career / season_relative(self.year, relative)

    @property
    def calendar(self): return self.record('calendar.md')
    @property
    def annual_record(self): return self.record('record.md')
    @property
    def stats(self): return self.record('stats')
    @property
    def receipts(self): return self.stats / 'game_receipts'
    @property
    def postseason_receipts(self): return self.stats / 'postseason_receipts'
    @property
    def roster(self): return self.record('roster.md')
    @property
    def depth_chart(self): return self.record('depth_chart.json')
    @property
    def awards(self): return self.record('awards')
    @property
    def regular_season(self): return self.record('regular_season')
    @property
    def postseason(self): return self.record('postseason')
    @property
    def schedule(self):
        return (self.root / 'library/data/2013_schedule.json' if self.year == 2013
                else self.record('schedule/fixtures.json'))
    @property
    def postseason_slots(self):
        return self.root / ('library/data/%d_postseason_slots.json' % self.year)
    @property
    def background_depth(self):
        return self.root / ('library/data/%d_week1_depth_charts.json' % self.year)
    @property
    def inseason_rails(self):
        """The in-season roster rails data folder (manifest, base, weekly
        shards); runtime.rails reads it. A season without one has no rails."""
        return self.root / ('library/data/%d_inseason_rails' % self.year)
    @property
    def generations(self): return self.career / 'migrations/event_generations.json'

    def cache(self, week, kind):
        if type(week) is not int or not 1 <= week <= (21 if self.year < 2021 else 22) or kind not in ('inputs', 'results'):
            raise ValueError('Invalid weekly cache identity')
        return self.root / '.sim_cache' / str(self.year) / ('week_%02d_%s.json' % (week, kind))

    def week_folder(self, week, postseason=False):
        """The week's output folder (existing `week_NN` or `week_NN_<away>_at_<home>`)."""
        if type(week) is not int or not 1 <= week <= (21 if self.year < 2021 else 22):
            raise ValueError('Invalid week')
        parent = self.postseason if postseason else self.regular_season
        prefixes = ('week_%02d' % week, 'Week_%02d' % week)
        matches = sorted(p for prefix in prefixes for p in parent.glob(prefix+'*') if p.is_dir())
        if len(matches) > 1:
            raise ValueError('Multiple output folders for week %d' % week)
        prefix = prefixes[0] if self.year < 2014 or postseason else prefixes[1]
        return matches[0] if matches else parent / prefix

    def paused_game(self, week, postseason=False, preseason=False):
        """Kernel 2014.4 E2: the protagonist game's paused partial record.

        With ``preseason`` the week number is the preseason game number and
        the record sits in that game's folder; nothing under regular_season
        or postseason is touched.
        """
        if preseason:
            if postseason:
                raise ValueError('A game is preseason or postseason, not both')
            return self.preseason_folder(week) / 'paused_game.json'
        return self.week_folder(week, postseason) / 'paused_game.json'

    # ---- preseason (dated fixtures, separate receipts, no standings) ---------
    @property
    def preseason_games_dir(self): return self.record('preseason')
    @property
    def preseason_fixtures(self): return self.preseason_games_dir / 'fixtures.json'
    @property
    def preseason_receipts(self):
        """Preseason receipts live apart from `receipts` and
        `postseason_receipts`, so standings, the regular-season statbook,
        awards and the draft order never read them."""
        return self.preseason_games_dir / 'statistics' / 'records' / 'game_receipts'

    def preseason_folder(self, game):
        if type(game) is not int or not 1 <= game <= 5:
            raise ValueError('Invalid preseason game number')
        return self.record('preseason/game_%02d' % game)

    def preseason_cache(self, game, kind):
        if type(game) is not int or not 1 <= game <= 5 or kind not in ('inputs', 'results'):
            raise ValueError('Invalid preseason cache identity')
        return self.root / '.sim_cache' / str(self.year) / ('preseason_%02d_%s.json' % (game, kind))

    def preseason_games(self):
        """The season's dated preseason fixtures (schedule facts only)."""
        data = json.loads(self.preseason_fixtures.read_text())
        if (data.get('season') != self.year or data.get('status') != 'RELEASED'
                or data.get('game_type') != 'preseason'):
            raise ValueError('Preseason fixtures must have the requested season, RELEASED status and preseason game_type')
        games = data['games']
        numbers = [g.get('game') for g in games]
        if numbers != list(range(1, len(games) + 1)):
            raise ValueError('Preseason fixtures must be numbered 1..N in order')
        if any(not g['date'].startswith(str(self.year) + '-') for g in games):
            raise ValueError('Preseason fixture dates do not belong to the requested season')
        if any(g.get('game_id') != '%d-preseason-%02d-%s-at-%s' % (
                self.year, g['game'], _slug(g['away']), _slug(g['home'])) for g in games):
            raise ValueError('Preseason fixture game_id must follow YEAR-preseason-NN-away-at-home')
        return games

    def preseason_game(self, game):
        rows = [g for g in self.preseason_games() if g['game'] == game]
        if not rows:
            raise ValueError('No preseason game %s in the %d fixtures' % (game, self.year))
        return rows[0]

    def regular_games(self):
        data = json.loads(self.schedule.read_text())
        if self.year != 2013 and (data.get('season') != self.year or data.get('status') != 'RELEASED'):
            raise ValueError('Season fixtures must have the requested season and RELEASED status')
        games = data['games']
        if any(not (g['date'].startswith(str(self.year) + '-') or
                    g['date'].startswith(str(self.year + 1) + '-01-')) for g in games):
            raise ValueError('Fixture dates do not belong to requested regular season')
        return games


def _slug(team):
    return re.sub(r'[^a-z0-9]+', '-', team.lower()).strip('-')


def require_receipt_season(receipts, season):
    """Reject foreign-season receipts; legacy 2013 ids remain byte-identical."""
    SeasonPaths(season)
    for row in receipts:
        event = str(row.get('event_id', ''))
        match = re.match(r'^(\d{4})-', event)
        if row.get('season', season) != season or (match and int(match[1]) != season):
            raise ValueError('Receipt belongs to another season: ' + event)
        if season != 2013 and (not match or int(match[1]) != season):
            raise ValueError('Receipt lacks a season-qualified event id: ' + event)


def game_release_errors(season, root=ROOT, preseason=None):
    """Public release gate, independent of credentials or legacy VERIFIED flags.

    ``preseason=N`` scopes the required-input check to preseason game N: the
    Jacksonville depth chart it needs is the game's frozen chart
    (``Game_0N/depth_chart.json``, Stone's plan), not the season input
    ``game_depth_chart.json``, which stays required for every regular-season
    or postseason closure. The release gates themselves are the same.
    """
    paths = SeasonPaths(season, root)
    if preseason is not None and (type(preseason) is not int or not 1 <= preseason <= 5):
        raise ValueError('Invalid preseason game number: %r' % (preseason,))
    if season == 2013:
        return []
    from . import KERNEL_VERSION
    data = json.loads((Path(root) / 'runtime/season_readiness.json').read_text())
    release = data['seasons'].get(str(season))
    if release is None:
        return ['No season release registered for %d; preparation does not authorize games' % season]
    if {g['id'] for g in release['gates']} != RELEASE_GATES or len(release['gates']) != len(RELEASE_GATES):
        raise ValueError('Season release must contain each required gate exactly once')
    errors = []
    if not release.get('accepted_kernel') or release['accepted_kernel'] != KERNEL_VERSION:
        errors.append('No accepted %d game release for the installed kernel' % season)
    for gate in release['gates']:
        if gate['status'] not in ('BLOCKED', 'PARTIAL', 'VERIFIED') or not gate.get('remaining'):
            raise ValueError('Invalid season release disposition: ' + gate['id'])
        for evidence in gate.get('evidence', []):
            target = (Path(root) / evidence).resolve()
            if not target.is_relative_to(paths.root) or not target.is_file():
                raise ValueError('Invalid season release evidence: ' + evidence)
        if gate['status'] != 'VERIFIED':
            errors.append(gate['id'] + ': ' + gate['remaining'])
        elif not gate.get('evidence') or any(not (Path(root) / p).is_file() for p in gate['evidence']):
            errors.append(gate['id'] + ': verified gate lacks acceptance evidence')
    inputs = {name: getattr(paths, name) for name in ('roster', 'depth_chart', 'schedule', 'background_depth')}
    if preseason is not None:
        inputs['depth_chart'] = paths.preseason_folder(preseason) / 'depth_chart.json'
    for name, path in inputs.items():
        if not path.is_file():
            errors.append('Missing %d %sinput: %s' % (season, 'preseason game %d ' % preseason if preseason else '',
                                                    path.relative_to(paths.root)))
    if paths.schedule.is_file():
        try:
            expected = 256 if season < 2021 else 272
            if len(paths.regular_games()) != expected:
                errors.append('%d regular-season fixture count must be %d' % (season, expected))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append('Invalid season fixtures: ' + str(exc))
    return errors


def preseason_scope(event_id):
    """The preseason game number an event id names (YEAR-preseason-NN-...), else None."""
    match = re.match(r'^\d{4}-preseason-(\d{2})-', str(event_id))
    return int(match[1]) if match else None


def require_game_release(season, root=ROOT, preseason=None):
    errors = game_release_errors(season, root, preseason)
    if errors:
        raise ValueError('Season %d game execution blocked: %s' % (season, '; '.join(errors)))
