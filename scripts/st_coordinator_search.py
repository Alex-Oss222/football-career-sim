#!/usr/bin/env python3
"""February 2014: Jacksonville's special teams coordinator search.

  python scripts/st_coordinator_search.py           # dry run: path probabilities
  python scripts/st_coordinator_search.py --close   # one private draw; write results

Method: career/2014/early_offseason/staff_changes/st_search_method.json, committed before the draw.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.packets import canonical

DIR = ROOT / "career/2014/early_offseason/staff_changes"
METHOD = DIR / "st_search_method.json"
RESULTS = DIR / "st_search_results.json"
P_APRIL_RESIGNED = 13 / 16
P_WESTHOFF_WILLING = 0.25
P_COUNTER = 0.5
TERMS = {"Bobby April": (700_000, 800_000), "Mike Westhoff": (625_000, 750_000), "Bruce DeHaven": (625_000, 750_000)}


def resolve(rng):
    u_april, u_april_counter, u_west, u_west_counter, u_dh_counter = (rng.random() for _ in range(5))
    events = []

    def ev(day, coach, event, detail=""):
        events.append({"date": "2014-02-%02d" % day, "coach": coach, "event": event, "detail": detail})

    def hire(day, coach, u_counter):
        opening, ceiling = TERMS[coach]
        counter = u_counter < P_COUNTER
        ev(day, coach, "funding confirmed", "Caldwell confirms the allocation within the plan's ceiling")
        ev(day, coach, "offer", "$%s a season, 2014-2015, common terms" % format(opening, ","))
        salary = ceiling if counter else opening
        if counter:
            ev(day, coach, "counter", "asks for the ceiling; met at $%s under Stone's instruction" % format(ceiling, ","))
        ev(day, coach, "accepted", "$%s a season" % format(salary, ","))
        return {"coach": coach, "date": "2014-02-%02d" % day, "salary": salary, "term": "2014-2015",
                "counter": counter}

    resigned = u_april < P_APRIL_RESIGNED
    draws = {"april_resigned": round(u_april, 4), "westhoff_willing": round(u_west, 4)}
    if resigned:
        ev(3, "Bobby April", "status", "re-signed by Oakland for 2014 before the approach")
        ev(3, "Bobby April", "request", "permission to interview for special teams coordinator")
        ev(4, "Bobby April", "permission refused", "lateral (rule T3); the symmetric default policy refuses it")
    else:
        ev(3, "Bobby April", "status", "Oakland deal expired after 2013; not re-signed; unattached")
        ev(5, "Bobby April", "interview")
        return {"hired": hire(6, "Bobby April", u_april_counter), "events": events, "draws": draws}
    ev(5, "Mike Westhoff", "contact", "unattached; no permission needed")
    if u_west < P_WESTHOFF_WILLING:
        ev(7, "Mike Westhoff", "willing", "agrees to interview")
        ev(10, "Mike Westhoff", "interview")
        return {"hired": hire(11, "Mike Westhoff", u_west_counter), "events": events, "draws": draws}
    ev(7, "Mike Westhoff", "declined", "prefers to stay retired")
    ev(10, "Bruce DeHaven", "request", "Carolina's permission to interview its assistant for coordinator")
    ev(11, "Bruce DeHaven", "permission granted", "a step up in title; the symmetric default policy grants it")
    ev(12, "Bruce DeHaven", "interview")
    return {"hired": hire(13, "Bruce DeHaven", u_dh_counter), "events": events, "draws": draws}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    m = json.loads(METHOD.read_text(encoding="utf-8"))
    print("April %.3f; Westhoff %.3f; DeHaven %.3f" % (
        1 - P_APRIL_RESIGNED, P_APRIL_RESIGNED * P_WESTHOFF_WILLING, P_APRIL_RESIGNED * (1 - P_WESTHOFF_WILLING)))
    if not args.close:
        return 0
    if RESULTS.exists():
        print("ST SEARCH: already drawn")
        return 1
    from runtime.game_runner import _entropy_from_ref
    from runtime.private_client import Client
    client = Client()
    pkt = {"procedure": m["procedure"], "event_id": m["event_id"], "snapshot": client.current_snapshot(),
           "method_sha256": digest(METHOD), "code_sha256": digest(Path(__file__).resolve())}
    ref = client.close_event(pkt)
    rng = random.Random(int.from_bytes(hashlib.sha256(_entropy_from_ref(ref) + canonical(pkt)).digest(), "big"))
    res = resolve(rng)
    RESULTS.write_text(json.dumps({**pkt, "ledger_entry": args.entry, "result_ref": ref,
                                   "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(), **res},
                                  indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
