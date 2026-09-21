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

    # Season statistics are generated artifacts. Rebuild them from the durable
    # closed-game receipts so stale caches or hand-edited views fail closed.
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from runtime.statbook import aggregate_receipts
        from scripts.render_season_stats import (
            all_players_markdown,
            compact_book_for_storage,
            leaders_markdown,
            league_markdown,
            play_calls_markdown,
            team_markdown,
        )

        stats_dir = root/'career/2013/stats'
        receipt_paths = sorted((stats_dir/'game_receipts').glob('*.json'))
        require(bool(receipt_paths), 'Statbook has no closed-game receipts')
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

        book = aggregate_receipts(receipts)
        expected_cache = (
            json.dumps(
                compact_book_for_storage(book),
                sort_keys=True,
                separators=(',', ':'),
            ) + '\n'
        )
        require(
            (stats_dir/'season_totals.json').read_text() == expected_cache,
            'season_totals.json is stale; rebuild season stats from receipts',
        )
        expected_views = {
            'team_player_stats.md': team_markdown(2013, 'Jacksonville Jaguars', book),
            'league_player_stats.md': league_markdown(2013, book),
            'all_player_stats.md': all_players_markdown(2013, book),
            'league_leaders.md': leaders_markdown(2013, book),
            'play_call_stats.md': play_calls_markdown(2013, 'Jacksonville Jaguars', book),
        }
        for name, expected in expected_views.items():
            actual = (stats_dir/name).read_text()
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
