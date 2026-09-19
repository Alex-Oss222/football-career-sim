#!/usr/bin/env python3
"""Fail-closed preflight. Exit 0 ready, 1 blocked, 2 invalid configuration.

The optional JSON form is an administrative diagnostic only.  It deliberately
reports gate labels and public evidence paths, never private-service contents.
"""
import argparse
import json
from pathlib import Path
from validate_repository import ROOT, validate

REQUIRED = {'calibration', 'playing_rules', 'injury_model', 'football_kernel', 'private_runtime'}


def assess(root=ROOT):
    root = Path(root)
    errors = validate(root)
    blockers = [dict(id='repository_continuity', label='Repository continuity',
                     detail=error) for error in errors]
    manifest = json.loads((root/'runtime/readiness.json').read_text())
    requirements = manifest['requirements']
    if {item['id'] for item in requirements} != REQUIRED or len(requirements) != len(REQUIRED):
        raise ValueError('Readiness manifest must contain each required gate exactly once')
    for item in requirements:
        if item['status'] not in {'BLOCKED', 'PARTIAL', 'VERIFIED'}:
            raise ValueError('Unknown readiness status')
        if not isinstance(item.get('remaining'), str) or not item['remaining'].strip():
            raise ValueError('Each readiness gate requires a nonempty remaining-work statement')
        if item['status'] != 'VERIFIED':
            blockers.append(dict(id=item['id'], label=item['label'],
                                 detail=item['remaining']))
        for evidence in item.get('evidence', []):
            target = (root/evidence).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                raise ValueError('Readiness evidence path is invalid')
        if item['status'] == 'VERIFIED' and not item.get('evidence'):
            blockers.append(dict(id=item['id'], label=item['label'],
                                 detail='no verification evidence'))
    # Intentionally not configurable by a status flag. Replace only when the
    # executable kernel and authenticated private-service probe are implemented.
    blockers.append(dict(
        id='execution_integration', label='Execution integration',
        detail='no full football-kernel entry point or live private-service probe is implemented.'))
    return {'ready': not blockers, 'blockers': blockers}


def check(root=ROOT):
    """Backward-compatible list of human-readable blockers used by tests."""
    return [f"{item['label']}: {item['detail']}"
            for item in assess(root)['blockers']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true',
                        help='emit a machine-readable public gate assessment')
    args = parser.parse_args()
    try:
        assessment = assess()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if args.json:
            print(json.dumps({'ready': False, 'configuration_error': str(exc)},
                             sort_keys=True))
            return 2
        print(f'INVALID READINESS CONFIGURATION: {exc}')
        return 2
    if args.json:
        print(json.dumps(assessment, indent=2, sort_keys=True))
        return 0 if assessment['ready'] else 1
    if assessment['blockers']:
        print('GAME READINESS: BLOCKED')
        for blocker in assessment['blockers']:
            print(f"- {blocker['label']}: {blocker['detail']}")
        return 1
    print('GAME READINESS: READY')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
