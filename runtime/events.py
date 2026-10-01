"""Dated events live with their football records, never in a central ledger.

The annual record is a generated index. Compatibility aliases carry no event
facts: they only resolve old identifiers and frozen source paths to owners.
"""
from dataclasses import dataclass
from datetime import date
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVENT_META = re.compile(r'<!-- event-record:\s*(\{.*?\})\s*-->', re.S)
EVENT_ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def repository_map(root=ROOT):
    return json.loads((Path(root) / 'docs/repository_map.json').read_text())


def resolve_path(root, relative, mapping=None):
    """Resolve an unchanged historical path without changing receipt bytes."""
    root = Path(root).resolve()
    mapping = (repository_map(root) if (root / 'docs/repository_map.json').exists() else {}) if mapping is None else mapping
    aliases = mapping.get('path_aliases', {})
    relative = str(relative)
    seen = set()
    while relative in aliases:
        if relative in seen:
            raise ValueError('Cyclic repository path alias: ' + relative)
        seen.add(relative)
        relative = aliases[relative]
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise ValueError('Event source path leaves repository: ' + relative)
    if not target.exists():
        from .season_layout import repository_relative
        target = (root / repository_relative(relative)).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Event source path leaves repository: ' + relative)
    return target


@dataclass(frozen=True)
class Event:
    owner: str
    data: dict

    @property
    def id(self):
        return self.data['id']

    @property
    def through(self):
        return self.data.get('date_end', self.data['date'])

    @property
    def season(self):
        return self.data.get('season', int(self.data['date'][:4]))


def validate_event(data, owner):
    if not isinstance(data, dict):
        raise ValueError(owner + ': event record must be an object')
    if not {'id', 'date', 'summary', 'status'} <= data.keys():
        raise ValueError(owner + ': event lacks id, date, summary or status')
    if not isinstance(data['id'], str) or not EVENT_ID.fullmatch(data['id']):
        raise ValueError(owner + ': invalid descriptive event id')
    start = date.fromisoformat(data['date'])
    end = date.fromisoformat(data.get('date_end', data['date']))
    if end < start:
        raise ValueError(owner + ': event ends before it starts')
    if data['status'] != 'closed':
        raise ValueError(owner + ': event records contain completed events only')
    if data.get('kind', 'football') not in {'football', 'technical'}:
        raise ValueError(owner + ': invalid event kind')
    summary = data['summary']
    if not isinstance(summary, str) or not summary.strip() or '\n' in summary:
        raise ValueError(owner + ': event summary must be one nonempty line')
    if 'season' in data and (type(data['season']) is not int or not 2013 <= data['season'] <= 2100):
        raise ValueError(owner + ': invalid event season')
    if 'date_label' in data and (not isinstance(data['date_label'], str)
                                 or not data['date_label'].strip() or '\n' in data['date_label']):
        raise ValueError(owner + ': date label must be one nonempty line')
    if 'closure' in data:
        closure = data['closure']
        if not isinstance(closure, dict) or not {'checkpoint', 'through', 'sequence'} <= closure.keys():
            raise ValueError(owner + ': incomplete event closure')
        if not isinstance(closure['checkpoint'], str) or not closure['checkpoint'].strip():
            raise ValueError(owner + ': empty checkpoint')
        date.fromisoformat(closure['through'])
        if type(closure['sequence']) is not int or closure['sequence'] < 1:
            raise ValueError(owner + ': invalid closure sequence')


def load_events(root=ROOT, mapping=None):
    root = Path(root).resolve()
    mapping = repository_map(root) if mapping is None else mapping
    patterns = mapping.get('event_record_sources', [])
    if not patterns:
        raise ValueError('No event record owners configured')
    files = set()
    for pattern in patterns:
        if Path(pattern).is_absolute() or '..' in Path(pattern).parts:
            raise ValueError('Invalid event owner pattern: ' + pattern)
        files.update(root.glob(pattern))
    events = {}
    for path in sorted(files):
        owner = path.relative_to(root).as_posix()
        if not path.is_file():
            continue
        # Broad owner patterns must not read archives or later playbook editions.
        if owner.startswith(('archive/', 'library/', 'career/playbook/')):
            continue
        content = path.read_text()
        # Documentation may demonstrate the schema in fenced code. Examples
        # are not events and cannot become an alternative source of history.
        content = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', content, flags=re.M | re.S)
        content = re.sub(r'`<!-- event-record:[^\n]*-->`', '', content)
        matches = EVENT_META.findall(content)
        if content.count('<!-- event-record:') != len(matches):
            raise ValueError(owner + ': malformed event record comment')
        for raw in matches:
            data = json.loads(raw)
            validate_event(data, owner)
            event = Event(owner, data)
            if event.id in events:
                raise ValueError('Duplicate event owner: ' + event.id)
            events[event.id] = event
    for alias, targets in mapping.get('legacy_event_aliases', {}).items():
        if not isinstance(targets, list) or not targets or len(targets) != len(set(targets)):
            raise ValueError('Invalid legacy event alias: ' + alias)
        for target in targets:
            if target not in events:
                raise ValueError('Legacy event alias points to missing owner: ' + alias + ' -> ' + target)
    closures(events)
    return events


def event_refs(metadata, mapping):
    """New phase evidence names an event; old frozen evidence may use an alias."""
    if metadata.get('event_ref') is not None:
        return [metadata['event_ref']]
    legacy = metadata.get('event_entry')
    return mapping.get('legacy_event_aliases', {}).get(str(legacy), []) if legacy is not None else []


def preserve_event_comments(rendered, existing):
    """Keep owner metadata when rebuilding its generated presentation only.

    No old prose, scores or tables survive through this helper. Generated
    football content must still match its receipts on the next validation.
    """
    current = {json.loads(match[1])['id']: match[0] for match in EVENT_META.finditer(rendered)}
    additions = []
    for match in EVENT_META.finditer(existing):
        identity = json.loads(match[1])['id']
        if identity in current:
            if current[identity] != match[0]:
                raise ValueError('Conflicting generated owner metadata: ' + identity)
            continue
        current[identity] = match[0]
        additions.append(match[0])
    if not additions:
        return rendered
    return rendered.rstrip() + '\n\n' + '\n\n'.join(additions) + '\n'


def closures(events):
    result = []
    sequences, labels = set(), set()
    for event in events.values():
        item = event.data.get('closure')
        if item is None:
            continue
        if item['sequence'] in sequences or item['checkpoint'] in labels:
            raise ValueError('Duplicate event closure: ' + item['checkpoint'])
        sequences.add(item['sequence'])
        labels.add(item['checkpoint'])
        result.append((item['sequence'], event, item))
    return sorted(result, key=lambda row: row[0])


def display_date(value):
    parsed = date.fromisoformat(value)
    return f'{parsed:%B} {parsed.day}, {parsed.year}'


def annual_record_path(root, year):
    from .seasons import SeasonPaths
    return SeasonPaths(year, root).record('record.md')


def render_record(year, events, root=ROOT):
    """One line per actual event, sorted by dates, with one authoritative owner."""
    destination = annual_record_path(root, year)
    lines = [f'# {year} record', '', 'Dated events and their full records.', '']
    selected = [event for event in events.values()
                if event.season == year and event.data.get('kind', 'football') == 'football']
    for event in sorted(selected, key=lambda item: (
            item.data['date'], item.through,
            item.data.get('closure', {}).get('sequence', 0), item.id)):
        day = event.data.get('date_label')
        if day is None:
            day = display_date(event.data['date'])
            if event.through != event.data['date']:
                day += ' to ' + display_date(event.through)
        link = Path(os.path.relpath(Path(root) / event.owner, destination.parent)).as_posix()
        lines.append(f'- {day}: {event.data["summary"].rstrip()} [Full record]({link}).')
    if not selected:
        lines.append('No completed events recorded.')
    return '\n'.join(lines) + '\n'


def record_errors(root=ROOT, mapping=None, events=None):
    mapping = repository_map(root) if mapping is None else mapping
    events = load_events(root, mapping) if events is None else events
    errors = []
    for year in mapping.get('record_years', []):
        path = annual_record_path(root, year)
        expected = render_record(year, events, root)
        if not path.exists() or path.read_text() != expected:
            errors.append(f'{year} record is missing or stale; run scripts/render_annual_record.py {year}')
    return errors
