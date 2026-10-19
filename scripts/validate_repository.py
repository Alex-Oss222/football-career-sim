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
    # Compare without writing: the validated root's own method and results
    # build the expected page, and neither tree is changed.
    if season_honours.render_text(awards_dir.parents[2]) != before:
        errors.append('season_honours.md is stale; run scripts/season_honours.py render')
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


def _git(root, *args):
    """(returncode, stdout) of a git command in ``root``, or None when git
    or the checkout's history is not available."""
    import shutil
    import subprocess
    if shutil.which('git') is None or not (Path(root) / '.git').exists():
        return None
    p = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def _pure_move_source(root, commit, rel):
    """The earlier path of ``rel`` when ``commit`` only moved it (an exact,
    100% rename), else None. Rebuild step 2b moved every 2014 call sheet and
    receipt into the data area without changing a byte; a pure move neither
    freezes a sheet nor closes a receipt."""
    out = _git(root, 'show', '-M', '--name-status', '--format=', commit)
    for line in (out[1] if out and out[0] == 0 else '').splitlines():
        parts = line.split('\t')
        if len(parts) == 3 and parts[0] == 'R100' and parts[2] == rel:
            return parts[1]
    return None


def _freeze_commit(root, rel):
    """The last commit that changed the file, looking through pure moves."""
    rev = 'HEAD'
    while True:
        out = _git(root, 'log', '-1', '--format=%H', rev, '--', rel)
        commit = out[1] if out and out[0] == 0 else ''
        source = _pure_move_source(root, commit, rel) if commit else None
        if source is None:
            return commit
        rel, rev = source, commit + '^'


def _added_commits(root, rel):
    """The commits that added the file (newest first), looking through pure moves."""
    rev = 'HEAD'
    while True:
        out = _git(root, 'log', '--diff-filter=A', '--format=%H', rev, '--', rel)
        added = (out[1] if out and out[0] == 0 else '').split()
        source = _pure_move_source(root, added[-1], rel) if added else None
        if source is None:
            return added
        rel, rev = source, added[-1] + '^'


def freeze_order_errors(root, sheet_rel, receipt_rel):
    """Kernel 2014.6 W1a: the call sheet's freeze commit (the last commit
    that changed it, with no uncommitted change since) precedes the commit
    that added the receipt (its closure commit), or the receipt is not
    committed yet (a closure in progress, after the freeze). Skipped, with
    no error, where git or the full history is unavailable (a shallow
    checkout or the engine image's copy)."""
    shallow = _git(root, 'rev-parse', '--is-shallow-repository')
    if shallow is None or shallow[0] != 0 or shallow[1] == 'true':
        return []
    freeze = _freeze_commit(root, sheet_rel)
    if not freeze:
        return [f'{sheet_rel}: the call sheet is not committed, so its freeze cannot precede the closure']
    if _git(root, 'diff', '--quiet', 'HEAD', '--', sheet_rel)[0] != 0:
        return [f'{sheet_rel}: the call sheet changed after its freeze commit {freeze[:12]}']
    added = _added_commits(root, receipt_rel)
    if not added:
        return []
    closure = added[-1]
    if closure == freeze or _git(root, 'merge-base', '--is-ancestor', freeze, closure)[0] != 0:
        return [f'{receipt_rel}: closed in {closure[:12]}, which does not follow the call sheet\'s freeze '
                f'commit {freeze[:12]}']
    return []


def defensive_record_errors(root, paths, regular, playoff):
    """Kernel 2014.6 W1a: every 2014 receipt carrying a defensive call
    record against the week's committed call sheet, the week's paused
    record's bound sheets (when that event paused) and the sheet's freeze
    commit."""
    from runtime.defensive_calls import receipt_record_errors
    errors = []
    for receipts, folder, postseason in ((regular, paths.receipts, False), (playoff, paths.postseason_receipts, True)):
        for receipt in receipts:
            if not receipt.get('defensive_calls'):
                continue
            week = int(receipt['week'])
            sheet_path = paths.call_sheet(week, postseason=postseason)
            data = json.loads(sheet_path.read_text()) if sheet_path.is_file() else None
            event = receipt.get('event_id')
            errors += [f'{event}: {problem}' for problem in receipt_record_errors(receipt, data)]
            # Overnight review fix (October 17, 2026): a paused (or closed
            # after a pause) record of this event binds the defensive sheets
            # it paused with; the receipt's record must name the same ones.
            paused_path = paths.paused_game(week, postseason=postseason)
            paused = json.loads(paused_path.read_text()) if paused_path.is_file() else None
            if paused is not None and paused.get('event_id') == event:
                bound = paused.get('defensive_sheets') or {}
                named = {team: (entry or {}).get('sheet_sha256')
                         for team, entry in (receipt['defensive_calls'].get('teams') or {}).items()}
                if bound != named:
                    errors.append(f'{event}: the paused record binds the defensive sheets '
                                  f'{json.dumps(bound, sort_keys=True)}; the receipt\'s record names '
                                  f'{json.dumps(named, sort_keys=True)}')
            matches = [p for p in sorted(Path(folder).glob('*.json'))
                       if json.loads(p.read_text()).get('event_id') == event]
            if data is not None and matches:
                errors += freeze_order_errors(root, sheet_path.relative_to(root).as_posix(),
                                              matches[0].relative_to(root).as_posix())
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
        from runtime.events import closures, event_refs, load_events, record_errors, resolve_path
        events = load_events(root, mapping)
        roster_path = current_record('roster', root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f'Cannot read required continuity input: {exc}']
    for path in mapping['required_files']:
        require((root/path).is_file(), f'Missing required file: {path}')

    try:
        from scripts.build_annual_player_sheets import repository_profile_errors
        errors.extend(repository_profile_errors(root))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('Invalid annual Player Sheets: ' + str(exc))

    try:
        from scripts.season_handoff import check as check_handoff, repository_opening_errors
        from runtime.seasons import SeasonPaths
        handoff = SeasonPaths(mapping['active_season'], root).record('closeouts/season_handoff.json')
        if handoff.exists():
            errors.extend(check_handoff(root, json.loads(handoff.read_text())))
        errors.extend(repository_opening_errors(root, mapping['active_season']))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('Invalid annual handoff: ' + str(exc))

    errors.extend(record_errors(root, mapping, events))
    master = re.search(r'\| Master date/time \| (.*?) \|', state)
    from datetime import datetime, date
    try:
        current_date = datetime.strptime(master[1].split(', after')[0], '%B %d, %Y').date()
    except (TypeError, ValueError):
        errors.append('Cannot parse master date/time in Document 5')
        current_date = date.min

    for event in events.values():
        if event.data.get('kind', 'football') == 'football':
            require(date.fromisoformat(event.through) <= current_date,
                    'Closed event exceeds master clock: ' + event.id)

    for name, paths in mapping['phases'].items():
        try:
            output_bytes = (root/paths['output']).read_bytes()
            output = metadata(output_bytes.decode())
            require({'kind', 'status', 'through'} <= output.keys()
                    and ('event_ref' in output or 'event_entry' in output),
                    f'{name}: output lacks required metadata fields')
            require(output.get('kind') == 'phase_output', f'{name}: incorrect output kind')
            require(output.get('status') in STATUSES, f'{name}: invalid phase status')
            # Historical separate summaries retain their reviewed-source digest.
            # New reports contain the assessment themselves, so no second view
            # or self-authenticating hash is manufactured for those reports.
            if 'standouts' in paths:
                summary = metadata((root/paths['standouts']).read_text())
                require({'kind', 'status', 'through'} <= summary.keys()
                        and ('event_ref' in summary or 'event_entry' in summary),
                        f'{name}: summary lacks required metadata fields')
                require(summary.get('kind') == 'evidence_summary', f'{name}: incorrect summary kind')
                for field in ('status', 'through'):
                    require(summary.get(field) == output.get(field), f'{name}: stale summary {field}')
                require(event_refs(summary, mapping) == event_refs(output, mapping),
                        f'{name}: stale summary event reference')
                require(resolve_path(root, summary.get('source', ''), mapping) == (root/paths['output']).resolve(),
                        f'{name}: summary points at wrong source')
                require(summary.get('source_sha256') == hashlib.sha256(output_bytes).hexdigest(),
                        f'{name}: output changed; review standouts and refresh receipt')
            if output.get('status') == 'NOT_STARTED':
                require(output.get('through') is None and output.get('event_ref') is None
                        and output.get('event_entry') is None,
                        f'{name}: future phase has completed evidence metadata')
            else:
                through = date.fromisoformat(output['through'])
                require(through <= current_date, f'{name}: evidence exceeds master clock')
                refs = event_refs(output, mapping)
                require(bool(refs) and all(ref in events for ref in refs), f'{name}: unknown event owner')
                owned = [events[ref] for ref in refs if ref in events and events[ref].owner == paths['output']]
                require(bool(owned), f'{name}: completed phase must own its event evidence')
                require(any(event.through == output['through'] for event in owned),
                        f'{name}: phase date differs from its event evidence')
            plan = (root/paths['plan']).read_text()
            destinations = [paths['output']] + ([paths['standouts']] if 'standouts' in paths else [])
            require(all(f']({Path(target).name})' in plan for target in destinations),
                    f'{name}: plan must point to execution records')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'{name}: invalid/missing phase evidence: {exc}')

    try:
        checkpoint = re.search(r'^\*\*Global package checkpoint:\*\* `([^`]+)`', state, re.M)[1]
        closed_records = closures(events)
        closed = [item['checkpoint'] for _, _, item in closed_records]
        require(bool(closed) and closed[-1] == checkpoint, 'State checkpoint differs from latest closed event owner')
        if closed_records:
            require(date.fromisoformat(closed_records[-1][2]['through']) == current_date,
                    'State master date differs from latest closed event owner')
        version = re.search(r'\| Document 4 register version \| `([^`]+)`', register)[1]
        require(f'| Document 4 | `{version}`' in state, 'Document 5 names a stale Document 4 version')
        register_checkpoint = re.search(r'\| Last content-changing checkpoint \| `([^`]+)`', register)[1]
        require(register_checkpoint in closed, 'Document 4 checkpoint is not a closed event owner')
        for n, path in mapping['foundation_sources'].items():
            require(f'| Document {n} | `{git_blob((root/path).read_bytes())}`' in state,
                    f'Document {n}: stale source-version hash in Document 5')
        index = register.split('### Current player index', 1)[1].split('### Players no longer', 1)[0]
        register_names = re.findall(r'^\| ([^|]+?) \| JAX-', index, re.M)
        # The roster record (runtime/roster.py) owns club control: its active roster and
        # reserve lists are the controlled players the register and Document 5 count.
        from runtime import roster as roster_record
        roster_names = [row['name'] for row in roster_record.controlled(roster_record.load(roster_path))]
        require(len(register_names) == len(set(register_names)), 'Duplicate player in register')
        require(len(roster_names) == len(set(roster_names)), 'Duplicate player in readable roster')
        require(set(register_names) == set(roster_names), 'Controlled-player membership differs between roster and register')
        count = int(re.search(r'\| Current controlled players \| \*\*(\d+)\*\*', register)[1])
        require(len(register_names) == count, 'Register controlled count does not match player rows')
        require(len(roster_names) == count, 'Roster record controlled count differs from the register')
        state_counts = re.findall(r'\| \*\*Current [^|]*controlled roster\*\* \| \*\*(\d+)\*\*', state)
        require(len(state_counts) == 1 and int(state_counts[0]) == count, 'Document 5 controlled count is stale')
    except (OSError, IndexError, TypeError, ValueError) as exc:
        errors.append(f'Malformed canonical state: {exc}')

    # The current-job record, the decision queue and their generated views
    # (docs/career_layer.md). An open decision is never an error here: this
    # runs inside game readiness.
    try:
        from runtime import current_job, decision_queue
        from scripts.render_career_views import check as check_career_views
        job = current_job.load(root)
        errors.extend(current_job.validation_errors(root, mapping, events, current_date))
        errors.extend(decision_queue.validation_errors(root, mapping, events, current_date, job))
        # The map names the files the code binds; the renderer and the gates
        # read the constants, so the two must agree.
        layer = {'job': current_job.JOB.as_posix(), 'queue': decision_queue.QUEUE.as_posix()}
        require(mapping.get('career_layer') == layer,
                f'docs/repository_map.json career_layer must be {layer}, the paths the career layer reads')
        for label, rel in (('Current job record', current_job.JOB), ('Decision queue', decision_queue.QUEUE)):
            require(f'| {label} | `{git_blob((root/rel).read_bytes())}`' in state,
                    f'Document 5 names a stale {label} version; run scripts/render_career_views.py')
        errors.extend(check_career_views(root))
    except (OSError, ValueError, KeyError, IndexError, TypeError, NotImplementedError) as exc:
        errors.append(f'Invalid current job or decision queue: {exc}')

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

    # Every player page (career/league_players and the Jacksonville player
    # folder) is built from its permanent record (data/people/players) and the
    # owners the record names: a game closed or a record changed without
    # rebuilding fails, and so does a record that breaks the schema.
    try:
        from runtime.player_pages import check as check_player_pages
        page_errors = check_player_pages(root)
        errors.extend(page_errors[:20])
        if len(page_errors) > 20:
            errors.append('Player pages: %d more stale or missing files; run '
                          'scripts/render_player_pages.py' % (len(page_errors) - 20))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f'Invalid player pages: {exc}')

    # The coach side's pages (the Coach page, Contract and jobs, the Staff
    # page) are built from the coach records (data/people/coaches) and the
    # current-job record: a changed record or a closed game without a rebuild
    # fails, and so does a coach record that breaks its schema.
    try:
        from scripts.render_coach_pages import check as check_coach_pages
        errors.extend(check_coach_pages(root))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f'Invalid coach pages: {exc}')

    # The club pages (scripts/render_club_pages.py: the team page, the roster and the depth chart) and
    # the player cap views (scripts/render_jaguars_cap_tracker.py) are built from their stored
    # owners: a changed owner without a rebuild, or a hand edit, fails.
    try:
        from scripts.render_club_pages import check as check_club_pages
        errors.extend(check_club_pages(root))
        import json as _json
        from scripts import render_jaguars_cap_tracker as cap_tracker
        cap_data = _json.loads((root / cap_tracker.INPUT).read_text())
        for cap_path, cap_text in cap_tracker.render(cap_data, root).items():
            if not (root / cap_path).is_file() or (root / cap_path).read_text() != cap_text:
                errors.append('Cap view stale or hand-edited: %s; run scripts/render_jaguars_cap_tracker.py' % cap_path)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f'Invalid club pages or cap views: {exc}')

    # The open game week's pages (scripts/render_game_week.py, rebuild step 4): once its Game Week
    # Briefing is issued, the week index is current, the Game Plan sits beside the briefing and the
    # staff read is well formed. A dated briefing the situation has overtaken is re-issued by the
    # weekly workflow (render_game_week.py --check), not failed here.
    try:
        from scripts.render_game_week import validation_errors as game_week_errors
        errors.extend(game_week_errors(root))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f'Invalid game week pages: {exc}')

    # Clean pages (docs/rebuild_plan.md, rule 4): a built page, and any page
    # written from 2014 Week 6 on, is football only. Folder map (stored-facts
    # rule 2): no script or runtime module writes a season folder or a year
    # into a path itself.
    try:
        from runtime.clean_pages import clean_errors, folder_map_errors, history_pin_errors
        for label, found in (('Clean pages', clean_errors(root)), ('Page history', history_pin_errors(root)),
                             ('Folder map', folder_map_errors(root))):
            errors.extend(found[:20])
            if len(found) > 20:
                errors.append('%s: %d more problems' % (label, len(found) - 20))
    except (OSError, ValueError, KeyError, SyntaxError, TypeError) as exc:
        errors.append(f'Clean-page or folder-map check failed: {exc}')

    # Season statistics are generated artifacts. Rebuild them from the durable
    # closed-game receipts so stale caches or hand-edited views fail closed.
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from scripts.render_season_stats import render_views
        from runtime.seasons import SeasonPaths

        stats_dir = SeasonPaths(2013, root).stats
        receipt_paths = sorted(SeasonPaths(2013, root).receipts.glob('*.json'))
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
        errors.extend(award_coverage_errors(receipts, SeasonPaths(2013, root).awards_data))
        errors.extend(season_honours_errors(SeasonPaths(2013, root).awards_data))

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
        standings = SeasonPaths(2013, root).record('standings.md').read_text()
        require(standings == render_standings(2013, receipts),
                'standings.md is stale; run render_standings.py')
    except (OSError, ValueError, KeyError, TypeError, NameError) as exc:
        errors.append(f'Standings cannot be rebuilt from receipts: {exc}')
    # The 2014 draft order is generated from the same receipts once the
    # Super Bowl has closed.
    draft_order = SeasonPaths(2014, root).record('draft/draft_order.md')
    if draft_order.exists():
        try:
            from scripts.render_draft_order import render as render_draft_order
            require(draft_order.read_text() == render_draft_order(),
                    f'{draft_order.relative_to(root).as_posix()} is stale; run render_draft_order.py')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'Draft order cannot be rebuilt from receipts: {exc}')
    # The opponent inventory is deliberately undated; validate it without
    # importing results or opening the schedule gate.
    if SeasonPaths(2014, root).record('schedule/rotation_2014.json').exists():
        try:
            from runtime.schedule_2014 import check as check_2014_opponents
            errors.extend(check_2014_opponents(root))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'2014 opponent matrix cannot be rebuilt: {exc}')
    try:
        from scripts.render_box_score import stale_blocks
        receipt_dir = SeasonPaths(2013, root).receipts
        outputs = sorted(SeasonPaths(2013, root).regular_season.glob('*/output.md'))
        outputs += sorted(SeasonPaths(2013, root).postseason.glob('*/output.md'))
        for output in outputs:
            for event_id in stale_blocks(output, receipt_dir):
                require(False, f'{output.relative_to(root)}: box score for {event_id} '
                               'differs from its receipt; run render_box_score.py --write')
        # From 2014 the filled block is the gamebook layout of the weekly game
        # turn template (runtime/gamebook.py), checked against the same receipts.
        from runtime.seasons import SeasonPaths
        for year in sorted({2014, mapping.get('active_season', 2014)}):
            paths = SeasonPaths(year, root)
            outputs = sorted(paths.regular_season.glob('*/output.md')) + sorted(paths.postseason.glob('*/output.md'))
            for output in outputs:
                for event_id in stale_blocks(output, paths.receipts, season=year):
                    require(False, f'{output.relative_to(root)}: box score for {event_id} '
                                   f'differs from its receipt; run render_box_score.py --season {year} --write')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Box score cannot be rebuilt from its receipt: {exc}')

    # Every committed weekly call sheet must be labellable by kernel 2013.7:
    # each call names who it can describe, explicitly or through the family map.
    try:
        from runtime.call_families import sheet_errors
        sheets = sorted(SeasonPaths(2013, root).regular_season.glob('*/call_sheet.json'))
        sheets += sorted(SeasonPaths(2013, root).postseason.glob('*/call_sheet.json'))
        for sheet_path in sheets:
            sheet = json.loads(sheet_path.read_text()).get('offensive_call_sheet', [])
            for problem in sheet_errors(sheet):
                require(False, f'{sheet_path.relative_to(root)}: {problem}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Call sheets cannot be checked: {exc}')

    # Kernel 2014.6 batch B9 (R8, R9; U6): a committed call sheet's decisions
    # block (Stone's standing two-point and onside rules, or a delegation)
    # must be well formed: no probability, share or rate key, no unknown key,
    # an explicit otherwise. A malformed block fails closed here and in the
    # week build (WEEK_INPUTS: BLOCKED).
    try:
        from runtime.scoring_decisions import sheet_errors as decision_errors
        # From 2014 the call sheets are system files in the data area.
        for sheet_path in sorted([*(root/'career').glob('20*/**/call_sheet.json'),
                                  *(root/'data').glob('20*/**/call_sheet.json')]):
            data = json.loads(sheet_path.read_text())
            # Batch B9F: a fourth-down block's named calls must be calls of the sheet.
            from runtime.fourth_down import sheet_call_names
            names = sheet_call_names(data.get('offensive_call_sheet') or ())
            for problem in decision_errors(data.get('decisions'), names):
                require(False, f'{sheet_path.relative_to(root)}: {problem}')
            # Kernel 2014.6 W1a: a structured defensive sheet must pass its
            # schema, quote its packet lines verbatim and use only the active
            # defensive book's words (the playbook lock).
            from runtime.defensive_calls import committed_sheet_errors
            season = int(sheet_path.relative_to(root).parts[1])
            for problem in committed_sheet_errors(data, root, season):
                require(False, f'{sheet_path.relative_to(root)}: defensive_call_sheet: {problem}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Call sheet decision blocks cannot be checked: {exc}')

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
            # Kernel 2014.6 release (Stone, October 17, 2026, "A: one PR"):
            # each committed receipt is judged by the release gates that
            # apply to the kernel that produced it, so the 2014.4 and 2014.5
            # receipts are not judged by the player_state gate that starts at
            # 2014.6. A new game still fails closed on every gate of the
            # installed kernel (require_game_release, check_game_readiness).
            for kernel in sorted({r.get('kernel_version') or '' for r in regular + playoff}):
                require(not game_release_errors(2014, root, receipt_kernel=kernel or None),
                        '2014 receipts exist before season release acceptance')
            for receipt in regular + playoff:
                for team, score in receipt['final_score'].items():
                    require(receipt['team_stats'][team]['points'] == score,
                            '2014 receipt points differ from final score')
            # Kernel 2014.6 W1a: a receipt's defensive call record must name
            # the week's committed sheet (its sha256 and the offensive
            # menus' hash), and the sheet's freeze commit must precede the
            # commit that closed the receipt.
            errors.extend(defensive_record_errors(root, paths, regular, playoff))
        if regular:
            games = paths.regular_games()
            def scheduled_2014(week):
                rows = [g for g in games if g['week'] == week]
                if not rows:
                    raise ValueError('no regular-season fixture week')
                return rows
            errors.extend(receipt_coverage_errors(regular, scheduled_2014))
            for name, expected in render_views(2014, 'Jacksonville Jaguars', regular).items():
                view = paths.file_in(paths.stats, name)
                require(view.is_file() and view.read_text() == expected,
                        '2014 generated statistics missing or stale: ' + name)
            from scripts.render_standings import render as standings_view
            standings_path = paths.record('standings.md')
            require(standings_path.is_file() and standings_path.read_text() == standings_view(2014, regular),
                    '2014 standings missing or stale')
            errors.extend(award_coverage_errors(regular, paths.awards_data))
        # Preseason receipts live apart (SeasonPaths.preseason_receipts): never
        # in standings or the regular-season statbook, but their own views and
        # box scores must be current, and none may exist before release.
        from scripts.render_preseason_stats import load_receipts as load_preseason, require_preseason, stale_views
        from scripts.render_box_score import stale_blocks
        preseason = load_preseason(paths.preseason_receipts)
        require_preseason(preseason, 2014)
        require(len({r['event_id'] for r in preseason}) == len(preseason), '2014 preseason receipts contain duplicate event identities')
        if preseason:
            for receipt in preseason:
                require(not game_release_errors(2014, root, preseason=int(receipt.get('preseason_game') or 0) or None,
                                                receipt_kernel=receipt.get('kernel_version') or None),
                        '2014 preseason receipts exist before season release acceptance')
            fixtures = {g['game_id'] for g in paths.preseason_games()}
            for receipt in preseason:
                require(receipt['event_id'] in fixtures, '2014 preseason receipt is not a dated fixture: ' + receipt['event_id'])
                for team, score in receipt['final_score'].items():
                    require(receipt['team_stats'][team]['points'] == score, '2014 preseason receipt points differ from final score')
            for name in stale_views(paths):
                require(False, '2014 preseason statistics missing or stale: %s; run render_preseason_stats.py --season 2014' % name)
            for output in sorted(p for pattern in ('Game_*/output.md', 'game_*/output.md')
                                 for p in paths.preseason_games_dir.glob(pattern)):
                for event_id in stale_blocks(output, paths.preseason_receipts, season=2014):
                    require(False, f'{output.relative_to(root)}: box score for {event_id} differs from its '
                                   'receipt; run render_box_score.py --season 2014 --preseason --write')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('2014 season records invalid: ' + str(exc))

    # Kernel 2014.6 (batch B7) privacy check: under the player-state model
    # the drawn values are hidden, so no receipt, paused record or results
    # file of kernel 2014.6 or later may carry a possession strength block,
    # and no attribution tier appears outside library/data (the model files
    # themselves are the only legitimate holders).
    try:
        from runtime.privacy import privacy_errors
        errors.extend(privacy_errors(root))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('player-state privacy check failed: ' + str(exc))

    # In-season roster rails (library/2014_inseason_rails.md): the committed
    # moves stay behind the master clock, keep their recorded hashes and
    # stripped forms, and every closed week from the effective week has a
    # current weekly record whose state digests recompute (engineering B5).
    try:
        from runtime import rails as inseason_rails
        from scripts.render_inseason_rails import check as check_inseason_pages
        errors.extend(inseason_rails.data_errors(2014, current_date, root))
        errors.extend(check_inseason_pages(2014, root))
        # Kernel 2014.6 batch B15 review fix (October 16, 2026): the
        # defensive-back family table is rebuilt whenever the rails grow.
        from runtime.depth_library import db_families_errors
        errors.extend(db_families_errors(2014, root))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('2014 in-season rails invalid: ' + str(exc))

    try:
        from scripts.render_trade_pages import check as check_trade_pages
        from scripts.render_award_pages import render_pages as award_pages
        from runtime.events import preserve_event_comments
        from runtime.seasons import SeasonPaths
        year = mapping['active_season']
        if year >= 2014:
            # Only compare prepared presentation pages; never run a draw.
            trade_source = SeasonPaths(year, root).record('trades/trades.md')
            if trade_source.exists():
                errors.extend(check_trade_pages(root, year))
            folder = SeasonPaths(year, root).awards
            data = SeasonPaths(year, root).awards_data
            if (folder/'week_01/README.md').exists():
                results = json.loads((data/'results.json').read_text()) if (data/'results.json').exists() else {}
                method = (json.loads((data/'methodology.json').read_text())
                          if results or (data/'methodology.json').is_file() else None)
                for relative, text in award_pages(year, results, method).items():
                    path = folder/relative
                    previous = path.read_text() if path.is_file() else ''
                    require(path.is_file() and previous == preserve_event_comments(text, previous),
                            'Award page missing or stale: '+relative)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('Season reading pages invalid: '+str(exc))

    allowed_books = set(mapping['active_playbooks']) | {'career/playbook/README.md'}
    def readable(path):
        rel = path.relative_to(root).as_posix()
        return not rel.startswith('archive/') and (not rel.startswith('career/playbook/') or rel in allowed_books)
    for path in sorted(root.rglob('*.md')):
        if '.git' in path.parts or not readable(path):
            continue
        content = without_code(path.read_text())
        for dest in link_destinations(content):
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


LINK_TITLE = r'(?:"[^"\n]*"|\'[^\'\n]*\'|\([^()\n]*\))'
# A destination in angle brackets (<path>, which may hold spaces) or bare; the same forms as the
# clean-page check (runtime/clean_pages.LINK and REFERENCE).
LINK_DEST = r'(<[^<>\n]*>|[^\s)<>]+)'


def link_destinations(content):
    """Every link destination of a Markdown text: inline links, with or without a title
    ([x](path "t")), in angle brackets ([x](<path>)) or with spaces around them ([x]( path )),
    and reference definitions ([x]: path, [x]: <path>). Angle brackets and the spaces around a
    destination are not part of it."""
    dests = re.findall(r'\[[^\]\n]+\]\(\s*' + LINK_DEST + r'(?:\s+' + LINK_TITLE + r')?\s*\)', content)
    dests += re.findall(r'(?m)^ {0,3}\[[^\]\n^][^\]\n]*\]:\s*(<[^<>\n]*>|[^\s<>]+)', content)
    return [d[1:-1].strip() if d.startswith('<') and d.endswith('>') else d for d in dests]


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
