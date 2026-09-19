#!/usr/bin/env python3
"""Explicitly advance private Engine State after a canonical progression commit."""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from runtime.private_client import Client, PrivateRuntimeUnavailable


def main():
    parser=argparse.ArgumentParser(
        description="CAS the private snapshot to the current Document 5 digest")
    parser.add_argument("checkpoint",help="canonical checkpoint/event reference")
    args=parser.parse_args()
    if not args.checkpoint.strip(): parser.error("checkpoint must be nonempty")
    next_snapshot=hashlib.sha256(
        (ROOT/"state/05_Current_Season_State.md").read_bytes()).hexdigest()
    client=Client(snapshot=next_snapshot)
    try:
        previous_snapshot=client.current_snapshot()
        if previous_snapshot!=next_snapshot:
            client.advance_snapshot(previous_snapshot,next_snapshot,args.checkpoint)
        client.readiness()
    except PrivateRuntimeUnavailable as exc:
        print(f"SNAPSHOT ADVANCE FAILED: {exc}",file=sys.stderr)
        return 1
    print(f"PRIVATE SNAPSHOT CURRENT: {next_snapshot} ({args.checkpoint})")
    return 0


if __name__=="__main__": raise SystemExit(main())
