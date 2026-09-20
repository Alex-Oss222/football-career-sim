#!/usr/bin/env python3
"""Idempotently mark the stranded Week 1 reset-v1 events as technically aborted."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from runtime.private_client import Client, PrivateRuntimeUnavailable

EVENT_IDS=tuple(f"2013-week01-reset-v1-{i:02d}" for i in range(1,17))
REASON=(
    "technical abort: Codex diff extraction exceeded size after private closure; "
    "no public reset commit or PR landed"
)

def main():
    client=Client()
    try:
        for event_id in EVENT_IDS:
            client.record_correction(event_id,REASON)
    except PrivateRuntimeUnavailable as exc:
        print(f"WEEK1_V1_ABORT_MARK_FAILED: {exc}",file=sys.stderr)
        return 1
    print("WEEK1_V1_ABORT_MARKED: 16 events")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
