"""Open-licensed player photographs for cards and award pages.

The registry (library/data/player_photos.json) is identity imagery only: a
photograph carries no football information and nothing in the engine reads
it. Every rendered photo carries its credit and license line.
"""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'library/data/player_photos.json'
BIRTH_DATES = ROOT / 'library/data/player_birth_dates.json'
DEPTH_LIBRARY = ROOT / 'library/data/2014_week1_depth_charts.json'
PHOTO_START, PHOTO_END = '<!-- photo -->', '<!-- /photo -->'


def _load(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


class Photos:
    def __init__(self, root=ROOT):
        self.players = _load(root / REGISTRY.relative_to(ROOT)).get('players', {})
        self.by_name = {}
        for gsis, row in self.players.items():
            self.by_name.setdefault(row['name'], []).append(gsis)
        self.registry_ids = {name: row.get('gsis_id')
                             for name, row in _load(root / BIRTH_DATES.relative_to(ROOT)).get('players', {}).items()}
        self.club_ids = {}
        for club, entry in _load(root / DEPTH_LIBRARY.relative_to(ROOT)).get('clubs', {}).items():
            self.club_ids[club] = {p.get('gsis_id') for p in entry.get('players', [])}

    def lookup(self, name, gsis_id=None, team=None):
        """The photo row for a player, or None. A name shared by several
        players resolves through the birth-date registry or the club; an
        unresolved name gets no photo rather than a guess."""
        if gsis_id is None:
            gsis_id = self.registry_ids.get(name)
        if gsis_id is None:
            ids = self.by_name.get(name, [])
            if len(ids) > 1 and team in self.club_ids:
                ids = [g for g in ids if g in self.club_ids[team]]
            gsis_id = ids[0] if len(ids) == 1 else None
        row = self.players.get(gsis_id)
        return dict(row, gsis_id=gsis_id) if row and row['name'] == name else None


def credit_line(row):
    credit = f"Photo: {row['credit']}, " if row.get('credit') else 'Photo: '
    license_ = row.get('license') or 'license unrecorded'
    if row.get('license_url'):
        license_ = f"[{license_}]({row['license_url']})"
    source = f" ([source]({row['source_page']}))" if row.get('source_page') else ''
    return f"*{credit}{license_}{source}.*"


def credit_short(row):
    """One credit for a list: credit, linked license, source."""
    parts = [row['credit']] if row.get('credit') else []
    license_ = row.get('license') or 'license unrecorded'
    parts.append(f"[{license_}]({row['license_url']})" if row.get('license_url') else license_)
    if row.get('source_page'):
        parts.append(f"[source]({row['source_page']})")
    return ', '.join(parts)


def block(row, name, width=160):
    return '\n'.join([PHOTO_START,
                      f'<img src="{escape(row["url"], quote=True)}" alt="{escape(name, quote=True)}" width="{width}">', '',
                      credit_line(row), PHOTO_END])


def place_block(text, row, name):
    """Insert or refresh the photo block directly under the card's title
    line; remove it when the player has no photo."""
    if PHOTO_START in text:
        before, rest = text.split(PHOTO_START, 1)
        after = rest.split(PHOTO_END, 1)[1]
        text = before.rstrip('\n') + '\n\n' + after.lstrip('\n')
    if row is None:
        return text
    title, _, body = text.partition('\n')
    return title + '\n\n' + block(row, name) + '\n\n' + body.lstrip('\n')
