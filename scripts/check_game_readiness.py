#!/usr/bin/env python3
"""Fail-closed game preflight: validate evidence, implementation and live state."""
import argparse, json, os, sys
from pathlib import Path
from validate_repository import ROOT, validate
sys.path.insert(0,str(ROOT))
from runtime.calibration import load, validate as validate_calibration
from runtime.kernel import resolve_background_game, resolve_protagonist_game
from runtime.private_client import Client, PrivateRuntimeUnavailable
from runtime.rules import RULES

REQUIRED={'calibration','playing_rules','injury_model','football_kernel','private_runtime'}

def assess(root=ROOT):
    root=Path(root); blockers=[]
    blockers += [dict(id='repository_continuity',label='Repository continuity',detail=e) for e in validate(root)]
    manifest=json.loads((root/'runtime/readiness.json').read_text()); reqs=manifest['requirements']
    if {x['id'] for x in reqs} != REQUIRED or len(reqs)!=len(REQUIRED): raise ValueError('Readiness manifest must contain each required gate exactly once')
    for item in reqs:
        if item['status'] not in {'BLOCKED','PARTIAL','VERIFIED'}: raise ValueError('Unknown readiness status')
        if not isinstance(item.get('remaining'),str) or not item['remaining'].strip(): raise ValueError('Each readiness gate requires a nonempty disposition')
        for evidence in item.get('evidence',[]):
            target=(root/evidence).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file(): raise ValueError('Readiness evidence path is invalid')
        if item['status']!='VERIFIED': blockers.append(dict(id=item['id'],label=item['label'],detail=item['remaining']))
    try:
        errors=validate_calibration(json.loads((root/'library/data/2012_nfl_aggregate_baseline.json').read_text()))
        if errors: blockers.append(dict(id='calibration_probe',label='Calibration probe',detail='; '.join(errors)))
    except Exception as e: blockers.append(dict(id='calibration_probe',label='Calibration probe',detail=str(e)))
    rule_doc=(root/'foundation/02_League_Era_and_Sourcebook.md').read_text()
    if RULES.active_limit!=46 or '2013 playing rules, verified' not in rule_doc: blockers.append(dict(id='rules_probe',label='Rules probe',detail='2013 executable/source rules mismatch'))
    if resolve_background_game is not resolve_protagonist_game: blockers.append(dict(id='kernel_probe',label='Kernel probe',detail='game paths do not share one kernel'))
    # Only the canonical checkout may bind to the deployed branch snapshot.
    if root.resolve()!=ROOT.resolve(): blockers.append(dict(id='private_probe',label='Private runtime probe',detail='noncanonical checkout is not snapshot-bound'))
    else:
        if not os.getenv('ENGINE_RUNTIME_URL'):
            blockers.append(dict(id='private_probe',label='Private runtime probe',detail='ENGINE_RUNTIME_URL is not set'))
        if not os.getenv('ENGINE_API_TOKEN'):
            blockers.append(dict(id='private_probe',label='Private runtime probe',detail='ENGINE_API_TOKEN is not set'))
        if blockers and any(x['id']=='private_probe' for x in blockers):
            return {'ready':False,'blockers':blockers}
        try: Client().readiness()
        except PrivateRuntimeUnavailable as e: blockers.append(dict(id='private_probe',label='Private runtime probe',detail=str(e)))
    return {'ready':not blockers,'blockers':blockers}

def check(root=ROOT): return [f"{x['label']}: {x['detail']}" for x in assess(root)['blockers']]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--json',action='store_true'); a=p.parse_args()
    try: result=assess()
    except (OSError,ValueError,KeyError,TypeError) as e:
        if a.json: print(json.dumps({'ready':False,'configuration_error':str(e)},sort_keys=True)); return 2
        print(f'INVALID READINESS CONFIGURATION: {e}'); return 2
    if a.json: print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print('GAME READINESS: READY' if result['ready'] else 'GAME READINESS: BLOCKED')
        for b in result['blockers']: print(f"- {b['label']}: {b['detail']}")
    return 0 if result['ready'] else 1
if __name__=='__main__': raise SystemExit(main())
