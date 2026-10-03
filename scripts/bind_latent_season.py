#!/usr/bin/env python3
"""Bind a league year's player states in the private Engine State service.

  python scripts/bind_latent_season.py YEAR [--check]

Kernel 2014.6 (batch B7). Run from merged main only (plan B18 step 5): the
service draws and records z for every row of the committed public table
(library/data/YEAR_player_state_public.json, pinned by its manifest) under
its season reference, which never leaves the service, and returns the public
commitment over the drawn rows. The reply is written to
library/data/YEAR_player_state_binding.json, which the runtime requires before
any game on the player-state model and which every weekly package commits
(manifest digest, commitment, latent keys). Binding twice with the same
manifest is idempotent; the service refuses a second manifest. --check only
compares the service's binding with the committed file and writes nothing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import player_state  # noqa: E402
from runtime.private_client import Client, PrivateRuntimeUnavailable  # noqa: E402


def binding_record(reply):
    return {"schema": player_state.BINDING_SCHEMA, "league_year": int(reply["league_year"]),
            "manifest_sha256": reply["manifest_sha256"], "public_table_sha256": reply["public_table_sha256"],
            "commitment": reply["commitment"], "rows": int(reply["rows"]),
            "derivation": player_state.DERIVATION,
            "note": "Public commitment over the private service's drawn rows (runtime/player_state.py); "
                    "the season reference and the draws stay in the service."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("year", type=int)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.year != player_state.league_year():
        print("BIND: BLOCKED\n- no committed public player-state table for %d" % args.year)
        return 1
    manifest = player_state.manifest_sha256()
    path = player_state.binding_path(args.year, ROOT)
    if args.check:
        # Read-only: the service's /ready lists its bound years; nothing is bound here.
        try:
            bound = (Client()._request("/ready").get("latent_bound") or {}).get(str(args.year))
        except PrivateRuntimeUnavailable as exc:
            print("BIND: BLOCKED\n- %s" % exc)
            return 1
        current = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if bound is None or current is None or (current["manifest_sha256"], current["commitment"]) != (
                bound["manifest_sha256"], bound["commitment"]):
            print("BIND: DIFFERS\n- the committed binding is not the service's (service %s, committed %s)"
                  % ("unbound" if bound is None else bound["commitment"][:16],
                     "absent" if current is None else current["commitment"][:16]))
            return 1
        print("BIND: OK  commitment %s" % current["commitment"][:16])
        return 0
    try:
        reply = Client().bind_latent(args.year, manifest)
    except (PrivateRuntimeUnavailable, ValueError) as exc:
        print("BIND: BLOCKED\n- %s" % exc)
        return 1
    record = binding_record(reply)
    if path.is_file():
        current = json.loads(path.read_text(encoding="utf-8"))
        if current != record:
            print("BIND: BLOCKED\n- a different binding is already committed at %s" % path.relative_to(ROOT))
            return 1
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("BIND: BOUND  %d rows, manifest %s, commitment %s%s" % (
        record["rows"], manifest[:16], record["commitment"][:16],
        " (already bound)" if reply.get("idempotent") else ""))
    print("Written: %s (commit it from merged main)" % path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
