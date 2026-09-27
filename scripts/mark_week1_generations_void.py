#!/usr/bin/env python3
"""Idempotently mark every superseded Week 1 event generation in the private journal.

Generation 1 was a technical abort; generation 2 was voided by ledger Entry 34
for the kernel 2013.4 restart. Run this before closing any generation-3 event.
Void results are never shown, compared or selected among.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.private_client import Client, PrivateRuntimeUnavailable

GENERATIONS = {
    1: "technical abort: Codex diff extraction exceeded size after private closure; "
       "no public reset commit or PR landed",
    2: "void: ledger Entry 34 superseded generation 2 after verified kernel 2013.3 "
       "attribution/volume defects; replayed as generation 3 under kernel 2013.4",
}


def event_ids(generation):
    return tuple(f"2013-week01-reset-v{generation}-{i:02d}" for i in range(1, 17))


def main():
    client = Client()
    marked = 0
    try:
        for generation, reason in GENERATIONS.items():
            for event_id in event_ids(generation):
                client.record_correction(event_id, reason)
                marked += 1
    except PrivateRuntimeUnavailable as exc:
        print(f"WEEK1_GENERATION_VOID_MARK_FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"WEEK1_GENERATIONS_MARKED: {marked} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
