#!/usr/bin/env python3
"""Fail-closed preflight. Exit 0 ready, 1 blocked, 2 invalid configuration."""
import json
from pathlib import Path
from validate_repository import ROOT, validate

REQUIRED = {'calibration', 'playing_rules', 'injury_model', 'football_kernel', 'private_runtime'}


def check(root=ROOT):
    root = Path(root)
    errors = validate(root)
    blockers = ['Repository continuity: '+error for error in errors]
    manifest = json.loads((root/'runtime/readiness.json').read_text())
    requirements = manifest['requirements']
    if {item['id'] for item in requirements} != REQUIRED or len(requirements) != len(REQUIRED):
        raise ValueError('Readiness manifest must contain each required gate exactly once')
    for item in requirements:
        if item['status'] not in {'BLOCKED', 'PARTIAL', 'VERIFIED'}:
            raise ValueError('Unknown readiness status')
        if item['status'] != 'VERIFIED':
            blockers.append(f"{item['label']}: {item['remaining']}")
        for evidence in item.get('evidence', []):
            target = (root/evidence).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                raise ValueError('Readiness evidence path is invalid')
        if item['status'] == 'VERIFIED' and not item.get('evidence'):
            blockers.append(f"{item['label']}: no verification evidence")
    # Intentionally not configurable by a status flag. Replace only when the
    # executable kernel and authenticated private-service probe are implemented.
    blockers.append('Execution integration: no full football-kernel entry point or live private-service probe is implemented.')
    return blockers


def main():
    try:
        blockers = check()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'INVALID READINESS CONFIGURATION: {exc}')
        return 2
    if blockers:
        print('GAME READINESS: BLOCKED')
        for blocker in blockers:
            print('- '+blocker)
        return 1
    print('GAME READINESS: READY')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
