#!/usr/bin/env python3
"""Read-only continuity checks. No future playbook or archive content is read."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
META = re.compile(r'<!-- sim-meta: (\{[^\n]+\}) -->')
STATUSES = {'NOT_STARTED', 'IN_PROGRESS', 'COMPLETE'}


def metadata(text):
    matches = META.findall(text)
    if len(matches) != 1:
        raise ValueError('expected exactly one sim-meta record')
    return json.loads(matches[0])


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def anchors(text):
    found, counts = set(), {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        found.add(slug if n == 0 else f'{slug}-{n}')
    found.update(re.findall(r'<a\s+(?:name|id)="([^"]+)"', text))
    return found


def without_code(text):
    text = re.sub(r'^```.*?^```\s*$', '', text, flags=re.M | re.S)
    return re.sub(r'`[^`\n]*`', '', text)


def award_coverage_errors(receipts, awards_dir):
    """Every closed week has its awards; every month whose weeks are all closed
    and whose following week has closed has its monthly awards."""
    method_path, results_path = awards_dir / 'methodology.json', awards_dir / 'results.json'
    if not method_path.exists():
        return []
    method = json.loads(method_path.read_text(encoding='utf-8'))
    results = json.loads(results_path.read_text(encoding='utf-8')) if results_path.exists() else {}
    closed = sorted({int(r['week']) for r in receipts if str(r.get('week', '')).isdigit()})
    errors = [f'league awards missing for week {w} (scripts/league_awards.py week {w} --close)'
              for w in closed if f'week-{w}' not in results]
    last = closed[-1] if closed else 0
    for name, month in method.get('months', {}).items():
        if max(month['weeks']) < last and f'month-{name}' not in results:
            errors.append(f'league awards missing for {name} (scripts/league_awards.py month {name} --close)')
    return errors


def season_honours_errors(awards_dir):
    """A drawn season-honours record must match its method, evidence and page."""
    results_path = awards_dir / 'season_honours_results.json'
    if not results_path.exists():
        return []
    import hashlib
    results = json.loads(results_path.read_text(encoding='utf-8'))
    errors = []
    for key, name in (('method_sha256', 'season_honours_method.json'), ('evidence_sha256', 'season_honours_evidence.json')):
        if hashlib.sha256((awards_dir / name).read_bytes()).hexdigest() != results.get(key):
            errors.append(f'{name} changed after the season honours were drawn')
    page = awards_dir / 'season_honours.md'
    before = page.read_text(encoding='utf-8') if page.exists() else None
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scripts import season_honours
    season_honours.render()
    if page.read_text(encoding='utf-8') != before:
        errors.append('season_honours.md was stale; regenerated with scripts/season_honours.py render')
    return errors


def receipt_coverage_errors(receipts, scheduled=None, season=2013, root=None):
    """One receipt per scheduled game in every regular-season week that has any.

    `scheduled(week)` returns that week's scheduled games and raises ValueError
    for a week with none (runtime.week_inputs.schedule for `season`, e.g.
    library/data/2013_schedule.json). A week outside the regular-season
    schedule, such as a postseason round, is skipped here. A season whose
    schedule file does not exist is an error, never a silent skip.
    """
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from runtime.season import SeasonDataMissing
    if scheduled is None:
        from runtime.week_inputs import schedule
        scheduled = lambda week: schedule(week, season, root)
    counts = {}
    for receipt in receipts:
        week = receipt.get('week')
        if isinstance(week, int) and not isinstance(week, bool):
            counts[week] = counts.get(week, 0) + 1
    errors = []
    for week in sorted(counts):
        try:
            games = len(scheduled(week))
        except json.JSONDecodeError:
            raise
        except SeasonDataMissing as exc:
            errors.append(f'{season} receipts cannot be checked against a schedule: {exc}')
            break
        except ValueError:
            continue
        if counts[week] != games:
            errors.append(f'Week {week}: {counts[week]} game receipt(s) for {games} scheduled games; '
                          'receipt coverage must match the schedule before the week reads complete')
    return errors


CLOSED_SEASON = 2013
GAME_DIRS = ('regular_season', 'postseason', 'preseason')
RECEIPT_DIRS = ('game_receipts', 'postseason_receipts', 'preseason_receipts')


def game_seasons(root=ROOT):
    """2013 (the closed season, always checked) plus every other career/<year>
    folder that holds receipts, call sheets or weekly outputs. A season with
    no game data yet needs none."""
    seasons = {CLOSED_SEASON}
    career = Path(root)/'career'
    for folder in sorted(career.iterdir()) if career.is_dir() else ():
        if not (folder.is_dir() and re.fullmatch(r'\d{4}', folder.name)):
            continue
        if any(any((folder/'stats'/d).glob('*.json')) for d in RECEIPT_DIRS) or any(
                any((folder/d).glob('*/call_sheet.json')) or any((folder/d).glob('*/output.md'))
                for d in GAME_DIRS):
            seasons.add(int(folder.name))
    return sorted(seasons)


def _stale_view_message(name, actual, expected):
    actual_lines = actual.splitlines()
    expected_lines = expected.splitlines()
    mismatch = next(
        (
            index
            for index, (left, right) in enumerate(
                zip(actual_lines, expected_lines), 1
            )
            if left != right
        ),
        min(len(actual_lines), len(expected_lines)) + 1,
    )
    actual_line = (
        actual_lines[mismatch - 1]
        if mismatch <= len(actual_lines)
        else '<EOF>'
    )
    expected_line = (
        expected_lines[mismatch - 1]
        if mismatch <= len(expected_lines)
        else '<EOF>'
    )
    return (f'{name}: stale generated stat view at line {mismatch}; '
            f'actual={actual_line!r}; expected={expected_line!r}; '
            'run render_season_stats.py')


def season_stat_errors(root, season):
    """Receipts, statbook views, awards and standings of one season."""
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    label = '' if season == CLOSED_SEASON else f'{season}: '
    # Season statistics are generated artifacts. Rebuild them from the durable
    # closed-game receipts so stale caches or hand-edited views fail closed.
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from scripts.render_season_stats import render_views

        stats_dir = root/f'career/{season}/stats'
        receipt_paths = sorted((stats_dir/'game_receipts').glob('*.json'))
        # Zero receipts is legitimate before the first regular-season game.
        receipts = []
        for receipt_path in receipt_paths:
            receipt = json.loads(receipt_path.read_text())
            receipts.append(receipt)
            event_id = receipt.get('event_id', receipt_path.name)
            require(str(event_id).startswith(f'{season}-week'),
                    f'{event_id}: event id does not belong to season {season}')
            require(receipt.get('game_type', 'regular') == 'regular',
                    f'{event_id}: only regular-season receipts belong in game_receipts')
            team_stats = receipt.get('team_stats')
            final_score = receipt.get('final_score')
            require(
                isinstance(team_stats, dict) and len(team_stats) == 2,
                f'{event_id}: receipt must contain exactly two team-stat rows',
            )
            require(
                isinstance(final_score, dict)
                and isinstance(team_stats, dict)
                and set(final_score) == set(team_stats),
                f'{event_id}: final-score teams differ from team-stat teams',
            )
            if isinstance(team_stats, dict) and isinstance(final_score, dict):
                for team_id, game in team_stats.items():
                    if isinstance(game, dict):
                        require(
                            game.get('points') == final_score.get(team_id),
                            f'{event_id}: {team_id} receipt points differ from final score',
                        )
        for directory in ('postseason_receipts', 'preseason_receipts'):
            for receipt_path in sorted((stats_dir/directory).glob('*.json')):
                event_id = json.loads(receipt_path.read_text()).get('event_id', receipt_path.name)
                require(str(event_id).startswith(f'{season}-week'),
                        f'{event_id}: event id does not belong to season {season}')

        if season != CLOSED_SEASON and not receipts:
            return errors
        errors.extend(receipt_coverage_errors(receipts, season=season, root=root))
        errors.extend(award_coverage_errors(receipts, root / f'career/{season}/awards'))
        if season == CLOSED_SEASON:
            errors.extend(season_honours_errors(root / 'career/2013/awards'))

        expected_views = render_views(season, 'Jacksonville Jaguars', receipts)
        for name, expected in expected_views.items():
            actual = (stats_dir/name).read_text()
            if name == 'season_totals.json':
                require(actual == expected,
                        f'{label}season_totals.json is stale; rebuild season stats from receipts')
                continue
            if actual != expected:
                require(False, label + _stale_view_message(name, actual, expected))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'{label}Malformed season statbook: {exc}')

    # Standings and weekly box scores are generated from the same receipts.
    try:
        from scripts.render_standings import render as render_standings
        standings = (root/f'career/{season}/standings.md').read_text()
        require(standings == render_standings(season, receipts),
                f'{label}standings.md is stale; run render_standings.py')
    except (OSError, ValueError, KeyError, TypeError, NameError) as exc:
        errors.append(f'{label}Standings cannot be rebuilt from receipts: {exc}')
    return errors


def season_output_errors(root, season):
    """Weekly box scores and call sheets of one season."""
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    try:
        from scripts.render_box_score import stale_blocks
        receipt_dir = root/f'career/{season}/stats/game_receipts'
        outputs = []
        for directory in GAME_DIRS:
            if season == CLOSED_SEASON and directory == 'preseason':
                continue  # 2013 preseason was a bulk narrative turn with no receipts
            outputs += sorted((root/f'career/{season}/{directory}').glob('*/output.md'))
        for output in outputs:
            directory = receipt_dir
            if output.parent.parent.name == 'preseason':
                directory = root/f'career/{season}/stats/preseason_receipts'
            for event_id in stale_blocks(output, directory):
                require(False, f'{output.relative_to(root)}: box score for {event_id} '
                               'differs from its receipt; run render_box_score.py --write')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Box score cannot be rebuilt from its receipt: {exc}')

    # Every committed weekly call sheet must be labellable by kernel 2013.7:
    # each call names who it can describe, explicitly or through the family map.
    try:
        from runtime.call_families import sheet_errors
        sheets = []
        for directory in GAME_DIRS:
            sheets += sorted((root/f'career/{season}/{directory}').glob('*/call_sheet.json'))
        for sheet_path in sheets:
            sheet = json.loads(sheet_path.read_text()).get('offensive_call_sheet', [])
            for problem in sheet_errors(sheet):
                require(False, f'{sheet_path.relative_to(root)}: {problem}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Call sheets cannot be checked: {exc}')
    return errors


def validate(root=ROOT):
    root = Path(root).resolve()
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    try:
        mapping = json.loads((root/'docs/repository_map.json').read_text())
        state = (root/'state/05_Current_Season_State.md').read_text()
        register = (root/'state/04_Roster_and_Staff_Register.md').read_text()
        ledger = (root/'career/2013/ledger.md').read_text()
        roster = (root/'career/2013/roster.md').read_text()
    except (OSError, ValueError) as exc:
        return [f'Cannot read required continuity input: {exc}']
    for path in mapping['required_files']:
        require((root/path).is_file(), f'Missing required file: {path}')

    entries = {int(n) for n in re.findall(r'^## Entry (\d+)\b', ledger, re.M)}
    master = re.search(r'\| Master date/time \| (.*?) \|', state)
    from datetime import datetime, date
    try:
        current_date = datetime.strptime(master[1].split(', after')[0], '%B %d, %Y').date()
    except (TypeError, ValueError):
        errors.append('Cannot parse master date/time in Document 5')
        current_date = date.min

    for name, paths in mapping['phases'].items():
        try:
            output_bytes = (root/paths['output']).read_bytes()
            output = metadata(output_bytes.decode())
            summary = metadata((root/paths['standouts']).read_text())
            for record, label in [(output, 'output'), (summary, 'summary')]:
                require({'kind', 'status', 'through', 'event_entry'} <= record.keys(),
                        f'{name}: {label} lacks required metadata fields')
            require(output.get('kind') == 'phase_output', f'{name}: incorrect output kind')
            require(summary.get('kind') == 'evidence_summary', f'{name}: incorrect summary kind')
            require(output.get('status') in STATUSES, f'{name}: invalid phase status')
            for field in ('status', 'through', 'event_entry'):
                require(summary.get(field) == output.get(field), f'{name}: stale summary {field}')
            require(summary.get('source') == paths['output'], f'{name}: summary points at wrong source')
            require(summary.get('source_sha256') == hashlib.sha256(output_bytes).hexdigest(),
                    f'{name}: output changed; review standouts and refresh receipt')
            if output.get('status') == 'NOT_STARTED':
                require(output.get('through') is None and output.get('event_entry') is None,
                        f'{name}: future phase has completed evidence metadata')
            else:
                through = date.fromisoformat(output['through'])
                require(through <= current_date, f'{name}: evidence exceeds master clock')
                require(output.get('event_entry') in entries, f'{name}: unknown ledger entry')
            plan = (root/paths['plan']).read_text()
            require('](output.md)' in plan and '](standouts.md)' in plan,
                    f'{name}: plan must point to execution records')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'{name}: invalid/missing phase evidence: {exc}')

    try:
        checkpoint = re.search(r'^\*\*Global package checkpoint:\*\* `([^`]+)`', state, re.M)[1]
        closed = re.findall(r'^\*\*Commit closed [—-] (.*?) [—-] canonical through ', ledger, re.M)
        require(bool(closed) and closed[-1] == checkpoint, 'State checkpoint differs from latest closed ledger entry')
        version = re.search(r'\| Document 4 register version \| `([^`]+)`', register)[1]
        require(f'| Document 4 | `{version}`' in state, 'Document 5 names a stale Document 4 version')
        register_checkpoint = re.search(r'\| Last content-changing checkpoint \| `([^`]+)`', register)[1]
        require(register_checkpoint in closed, 'Document 4 checkpoint is not a closed ledger event')
        for n, path in mapping['foundation_sources'].items():
            require(f'| Document {n} | `{git_blob((root/path).read_bytes())}`' in state,
                    f'Document {n}: stale source-version hash in Document 5')
        index = register.split('### Current player index', 1)[1].split('### Players no longer', 1)[0]
        register_names = re.findall(r'^\| ([^|]+?) \| JAX-', index, re.M)
        body = roster.split('## 3. Current controlled players', 1)[1].split('\n## 4.', 1)[0]
        roster_names = [m.strip() for m in re.findall(r'^\| ([^|]+?) \|', body, re.M)
                        if m.strip() != 'Player' and not m.strip().startswith('-')]
        require(len(register_names) == len(set(register_names)), 'Duplicate player in register')
        require(len(roster_names) == len(set(roster_names)), 'Duplicate player in readable roster')
        require(set(register_names) == set(roster_names), 'Controlled-player membership differs between roster and register')
        count = int(re.search(r'\| Current controlled players \| \*\*(\d+)\*\*', register)[1])
        require(len(register_names) == count, 'Register controlled count does not match player rows')
        require(f'**Canonical controlled-player count:** **{count}**' in roster, 'Roster header count is stale')
        state_counts = re.findall(r'\| \*\*Current [^|]*controlled roster\*\* \| \*\*(\d+)\*\*', state)
        require(len(state_counts) == 1 and int(state_counts[0]) == count, 'Document 5 controlled count is stale')
    except (OSError, IndexError, TypeError, ValueError) as exc:
        errors.append(f'Malformed canonical state: {exc}')

    # Age views must advance with the canonical calendar, including birthdays
    # during a season and January postseason dates in the next calendar year.
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from scripts.render_player_ages import check as check_player_ages
        errors.extend(check_player_ages(root))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f'Invalid player birth-date/age evidence: {exc}')

    # Season statistics, standings, box scores and call sheets are checked by
    # the same rules for every season folder that has game data: 2013 always
    # (the closed season), any later season once its receipts, call sheets
    # or box-score outputs exist. No later-season data is required now.
    for season in game_seasons(root):
        errors.extend(season_stat_errors(root, season))
    # The 2014 draft order is generated from the 2013 receipts once the
    # Super Bowl has closed (runtime.draft_order stays pinned to 2013).
    draft_order = root/'career/2014/draft/draft_order.md'
    if draft_order.exists():
        try:
            from scripts.render_draft_order import render as render_draft_order
            require(draft_order.read_text() == render_draft_order(),
                    'career/2014/draft/draft_order.md is stale; run render_draft_order.py')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'Draft order cannot be rebuilt from receipts: {exc}')
    # The opponent inventory is deliberately undated; validate it without
    # substituting the historical standings or opening the schedule gate.
    if (root/'career/2014/schedule/rotation_2014.json').exists():
        try:
            from runtime.schedule_2014 import check as check_2014_opponents
            errors.extend(check_2014_opponents(root))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'2014 opponent matrix cannot be rebuilt: {exc}')
    for season in game_seasons(root):
        errors.extend(season_output_errors(root, season))

    allowed_books = set(mapping['active_playbooks']) | {'career/playbook/README.md'}
    def readable(path):
        rel = path.relative_to(root).as_posix()
        return not rel.startswith('archive/') and (not rel.startswith('career/playbook/') or rel in allowed_books)
    for path in sorted(root.rglob('*.md')):
        if '.git' in path.parts or not readable(path):
            continue
        content = without_code(path.read_text())
        for dest in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^\s)]+)\)', content):
            parts = urlsplit(dest)
            if parts.scheme or parts.netloc:
                continue
            target = (path.parent/unquote(parts.path)).resolve() if parts.path else path
            if not target.is_relative_to(root):
                errors.append(f'{path.relative_to(root)}: link leaves repository: {dest}')
            elif not target.exists():
                errors.append(f'{path.relative_to(root)}: missing link target: {dest}')
            elif parts.fragment and target.suffix == '.md' and readable(target):
                require(unquote(parts.fragment) in anchors(without_code(target.read_text())),
                        f'{path.relative_to(root)}: missing heading: {dest}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        print('\n'.join('ERROR: ' + error for error in errors))
        return 1
    print('PASS: repository paths, phase evidence, current-state sources, checkpoint and roster agree.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
