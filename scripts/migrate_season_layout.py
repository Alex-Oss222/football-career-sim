#!/usr/bin/env python3
"""Preview or apply the 2014+ folder migration, preserving frozen file bytes.

This command does not split reports, delete ledgers, change event identities,
refresh evidence receipts, or rewrite JSON. Complete the owner migrations first.
It refuses collisions before any move. Markdown link rebasing is a separate,
explicit option so a coordinated migration cannot interrupt active file edits.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.season_layout import readable_relative, rebase_markdown


def plan(root, years):
    root = Path(root).resolve()
    moves = {}
    destinations = {}
    for year in years:
        if not 2014 <= year <= 2100:
            raise ValueError('Only seasons from 2014 onward can be reorganized')
        folder = root/'career'/str(year)
        for source in sorted(folder.rglob('*')):
            if source.is_symlink():
                raise ValueError('Season migration does not follow symlinks: '+str(source))
            if not source.is_file():
                continue
            old = source.relative_to(folder).as_posix()
            if old == 'ledger.md':
                raise ValueError('Migrate ledger facts to their owners before moving season folders')
            target = folder/readable_relative(year, old)
            if source == target:
                continue
            if target.exists() or target in destinations:
                raise ValueError('Migration destination already exists: '+str(target.relative_to(root)))
            moves[source] = target
            destinations[target] = source
    return moves


def markdown_sources(root, moves):
    """Inspect active public Markdown only, never archived/future playbooks."""
    mapping = json.loads((root/'docs/repository_map.json').read_text())
    books = set(mapping.get('active_playbooks', [])) | {'career/playbook/README.md'}
    changes = {}
    for source in root.rglob('*.md'):
        relative = source.relative_to(root).as_posix()
        if any(part in ('.git', '__pycache__', '.sim_cache', 'archive') for part in source.relative_to(root).parts):
            continue
        if relative.startswith('career/playbook/') and relative not in books:
            continue
        if source.is_symlink():
            continue
        target = moves.get(source, source)
        content = source.read_text()
        revised = rebase_markdown(content, relative, target.relative_to(root).as_posix(),
                                  aliases=mapping.get('path_aliases', {}))
        if revised != content:
            changes[target] = revised
    return changes


def migrate(root, years, *, write=False, rewrite_links=False):
    root = Path(root).resolve()
    moves = plan(root, years)
    revisions = markdown_sources(root, moves) if rewrite_links else {}
    # All collision and text preflight work is complete before writing.
    if write:
        for source, target in moves.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)
        for target, content in revisions.items():
            target.write_text(content)
        for year in years:
            folder = root/'career'/str(year)
            for directory in sorted((p for p in folder.rglob('*') if p.is_dir()),
                                    key=lambda p: len(p.parts), reverse=True):
                if not any(directory.iterdir()):
                    directory.rmdir()
    return {'moves': {a.relative_to(root).as_posix(): b.relative_to(root).as_posix()
                      for a, b in moves.items()},
            'markdown_revisions': [p.relative_to(root).as_posix() for p in revisions]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('years', type=int, nargs='+')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--rewrite-links', action='store_true')
    args = parser.parse_args()
    result = migrate(ROOT, args.years, write=args.write, rewrite_links=args.rewrite_links)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
