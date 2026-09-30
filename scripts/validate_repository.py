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


def receipt_coverage_errors(receipts, scheduled=None):
    """One receipt per scheduled game in every regular-season week that has any.

    `scheduled(week)` returns that week's scheduled games and raises ValueError
    for a week with none (runtime.week_inputs.schedule, library/data/2013_schedule.json).
    A week outside the regular-season schedule, such as a postseason round, is
    skipped here.
    """
    if scheduled is None:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from runtime.week_inputs import schedule as scheduled
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
        except ValueError:
            continue
        if counts[week] != games:
            errors.append(f'Week {week}: {counts[week]} game receipt(s) for {games} scheduled games; '
                          'receipt coverage must match the schedule before the week reads complete')
    return errors


def validate(root=ROOT):
    root = Path(root).resolve()
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    try:
        mapping = json.loads((root/'docs/repository_map.json').read_text())
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from runtime.seasons import current_record
        state = (root/'state/05_Current_Season_State.md').read_text()
        register = (root/'state/04_Roster_and_Staff_Register.md').read_text()
        ledger = '\n'.join((root/p).read_text() for p in mapping.get('ledger_history', [])) + '\n' + current_record('ledger', root).read_text()
        roster = current_record('roster', root).read_text()
    except (OSError, ValueError) as exc:
        return [f'Cannot read required continuity input: {exc}']
    for path in mapping['required_files']:
        require((root/path).is_file(), f'Missing required file: {path}')

    try:
        from scripts.build_annual_player_sheets import repository_profile_errors
        errors.extend(repository_profile_errors(root))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('Invalid annual Player Sheets: ' + str(exc))

    try:
        from scripts.season_handoff import check as check_handoff
        handoff = root / 'career' / str(mapping['active_season']) / 'closeouts/season_handoff.json'
        if handoff.exists():
            errors.extend(check_handoff(root, json.loads(handoff.read_text())))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('Invalid annual handoff: ' + str(exc))

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
        body = re.split(r'^## (?:3\. )?Current controlled players\s*$', roster, maxsplit=1, flags=re.M)[1]
        body = re.split(r'^## ', body, maxsplit=1, flags=re.M)[0]
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

    # The user's team stat tracker is a generated reader view. Any stale page
    # (a game closed without re-rendering) fails validation.
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from scripts.render_team_tracker import check as check_team_tracker
        for tracker_year in sorted(p.name for p in (root/'career').iterdir() if p.name.isdigit()):
            errors.extend(check_team_tracker(root, int(tracker_year)))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f'Invalid team tracker: {exc}')

    # Season statistics are generated artifacts. Rebuild them from the durable
    # closed-game receipts so stale caches or hand-edited views fail closed.
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from scripts.render_season_stats import render_views

        stats_dir = root/'career/2013/stats'
        receipt_paths = sorted((stats_dir/'game_receipts').glob('*.json'))
        # Zero receipts is legitimate before the first regular-season game.
        receipts = []
        for receipt_path in receipt_paths:
            receipt = json.loads(receipt_path.read_text())
            receipts.append(receipt)
            event_id = receipt.get('event_id', receipt_path.name)
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

        errors.extend(receipt_coverage_errors(receipts))
        errors.extend(award_coverage_errors(receipts, root / 'career/2013/awards'))
        errors.extend(season_honours_errors(root / 'career/2013/awards'))

        expected_views = render_views(2013, 'Jacksonville Jaguars', receipts)
        for name, expected in expected_views.items():
            actual = (stats_dir/name).read_text()
            if name == 'season_totals.json':
                require(actual == expected,
                        'season_totals.json is stale; rebuild season stats from receipts')
                continue
            if actual != expected:
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
                require(
                    False,
                    f'{name}: stale generated stat view at line {mismatch}; '
                    f'actual={actual_line!r}; expected={expected_line!r}; '
                    'run render_season_stats.py',
                )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Malformed season statbook: {exc}')

    # Standings and weekly box scores are generated from the same receipts.
    try:
        from scripts.render_standings import render as render_standings
        standings = (root/'career/2013/standings.md').read_text()
        require(standings == render_standings(2013, receipts),
                'standings.md is stale; run render_standings.py')
    except (OSError, ValueError, KeyError, TypeError, NameError) as exc:
        errors.append(f'Standings cannot be rebuilt from receipts: {exc}')
    # The 2014 draft order is generated from the same receipts once the
    # Super Bowl has closed.
    draft_order = root/'career/2014/draft/draft_order.md'
    if draft_order.exists():
        try:
            from scripts.render_draft_order import render as render_draft_order
            require(draft_order.read_text() == render_draft_order(),
                    'career/2014/draft/draft_order.md is stale; run render_draft_order.py')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'Draft order cannot be rebuilt from receipts: {exc}')
    # The opponent inventory is deliberately undated; validate it without
    # importing results or opening the schedule gate.
    if (root/'career/2014/schedule/rotation_2014.json').exists():
        try:
            from runtime.schedule_2014 import check as check_2014_opponents
            errors.extend(check_2014_opponents(root))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'2014 opponent matrix cannot be rebuilt: {exc}')
    try:
        from scripts.render_box_score import stale_blocks
        receipt_dir = root/'career/2013/stats/game_receipts'
        outputs = sorted((root/'career/2013/regular_season').glob('*/output.md'))
        outputs += sorted((root/'career/2013/postseason').glob('*/output.md'))
        for output in outputs:
            for event_id in stale_blocks(output, receipt_dir):
                require(False, f'{output.relative_to(root)}: box score for {event_id} '
                               'differs from its receipt; run render_box_score.py --write')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Box score cannot be rebuilt from its receipt: {exc}')

    # Every committed weekly call sheet must be labellable by kernel 2013.7:
    # each call names who it can describe, explicitly or through the family map.
    try:
        from runtime.call_families import sheet_errors
        sheets = sorted((root/'career/2013/regular_season').glob('*/call_sheet.json'))
        sheets += sorted((root/'career/2013/postseason').glob('*/call_sheet.json'))
        for sheet_path in sheets:
            sheet = json.loads(sheet_path.read_text()).get('offensive_call_sheet', [])
            for problem in sheet_errors(sheet):
                require(False, f'{sheet_path.relative_to(root)}: {problem}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Call sheets cannot be checked: {exc}')

    # Prepared 2014 storage is legitimate, but future/foreign receipts are not.
    try:
        from runtime.seasons import SeasonPaths, game_release_errors, require_receipt_season
        from scripts.render_season_stats import load_receipts, render_views
        paths = SeasonPaths(2014, root)
        regular = load_receipts(paths.receipts)
        playoff = load_receipts(paths.postseason_receipts)
        require_receipt_season(regular + playoff, 2014)
        ids = [r['event_id'] for r in regular + playoff]
        require(len(ids) == len(set(ids)), '2014 receipts contain duplicate event identities')
        if regular or playoff:
            require(not game_release_errors(2014, root), '2014 receipts exist before season release acceptance')
            for receipt in regular + playoff:
                for team, score in receipt['final_score'].items():
                    require(receipt['team_stats'][team]['points'] == score,
                            '2014 receipt points differ from final score')
        if regular:
            games = paths.regular_games()
            def scheduled_2014(week):
                rows = [g for g in games if g['week'] == week]
                if not rows:
                    raise ValueError('no regular-season fixture week')
                return rows
            errors.extend(receipt_coverage_errors(regular, scheduled_2014))
            for name, expected in render_views(2014, 'Jacksonville Jaguars', regular).items():
                require((paths.stats / name).is_file() and (paths.stats / name).read_text() == expected,
                        '2014 generated statistics missing or stale: ' + name)
            from scripts.render_standings import render as standings_view
            standings_path = paths.career / 'standings.md'
            require(standings_path.is_file() and standings_path.read_text() == standings_view(2014, regular),
                    '2014 standings missing or stale')
            errors.extend(award_coverage_errors(regular, paths.career / 'awards'))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('2014 season records invalid: ' + str(exc))

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
