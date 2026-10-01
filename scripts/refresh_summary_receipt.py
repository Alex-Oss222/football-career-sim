#!/usr/bin/env python3
"""Acknowledge a reviewed phase summary; never generate football observations."""
import argparse
import hashlib
import json
from validate_repository import ROOT, META, metadata


def main():
    mapping = json.loads((ROOT/'docs/repository_map.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=sorted(mapping['phases']))
    parser.add_argument('--reviewed', action='store_true', help='Confirm the actual summary was reviewed against the output')
    args = parser.parse_args()
    if not args.reviewed:
        parser.error('Review and update the summary first, then pass --reviewed.')
    paths = mapping['phases'][args.phase]
    if 'standouts' not in paths:
        parser.error('This phase keeps its assessment in the training report; no separate summary receipt exists.')
    source = (ROOT/paths['output']).read_bytes()
    output = metadata(source.decode())
    dest = ROOT/paths['standouts']
    text = dest.read_text()
    receipt = metadata(text)
    receipt.update({key: output[key] for key in ('status', 'through')})
    for key in ('event_ref', 'event_entry'):
        receipt.pop(key, None)
        if key in output:
            receipt[key] = output[key]
    receipt.update(source=paths['output'], source_sha256=hashlib.sha256(source).hexdigest())
    dest.write_text(META.sub(lambda _: '<!-- sim-meta: '+json.dumps(receipt, sort_keys=True)+' -->', text))
    print(f'Review receipt updated: {paths["standouts"]}')


if __name__ == '__main__':
    main()
