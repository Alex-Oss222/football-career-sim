#!/usr/bin/env python3
"""February 2014: the carousel's deferred procedure and retained-club coordinator openings.

  python scripts/coaching_carousel_deferred.py            # dry run: probabilities
  python scripts/coaching_carousel_deferred.py --close    # one private draw; write results and page
  python scripts/coaching_carousel_deferred.py render     # rewrite the page section

Method: career/2014/01_early_offseason/staff_changes/carousel_deferred_method.json, committed
before the draw. It reuses Entry 75's inputs and request models
(scripts/coaching_carousel.py). Every probability reads only the job, the coach's
role and record, the clubs' records and the calendar.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.packets import canonical
from scripts import coaching_carousel as cc

DIR = cc.DIR
METHOD = DIR / "carousel_deferred_method.json"
RESULTS = DIR / "carousel_deferred_results.json"
PAGE = cc.PAGE
END = date(2014, 2, 17)                     # the advance date
OPENS_D1 = date(2014, 2, 3)                 # the day after Super Bowl XLVIII
FIRST_REQUEST = cc.ELIMINATED_JAX + timedelta(days=1)
DEFERRED = ("Buffalo Bills", "Minnesota Vikings")
CHANGED_ENTRY_75 = ("Atlanta Falcons", "Cincinnati Bengals", "Denver Broncos",
                    "Indianapolis Colts", "San Francisco 49ers")
GONE = {"Alan Lowry"}                       # left January 12 (Entry 75)
HC_CANDIDATES = tuple(n for n in cc.HC_CANDIDATES if n not in GONE)
OPEN_P = {"offensive coordinator": 5 / 24, "defensive coordinator": 4 / 24}
DECISION_DATES = (date(2014, 1, 11), date(2014, 1, 17), date(2014, 1, 17), date(2014, 1, 18),
                  date(2014, 1, 18), date(2014, 1, 18), date(2014, 1, 18), date(2014, 2, 9),
                  date(2014, 2, 12))
RETAINED_OFFER = 0.25 * (2 / 17) / 0.5      # method stage D2 "offer"
REQUEST_LEAD = timedelta(days=3)


def resolve(rng, m, clubs, m75):
    """Every draw in the method's fixed order. Returns (changes, events, departed, pending)."""
    s3 = m75["stage_3_requests_for_jacksonville_assistants"]
    hc, cr = s3["head_coach_requests"], s3["coordinator_requests"]
    club_f = cc.club_factor(m75, clubs, cc.JAX)
    changes, events, pending, queue = [], [], [], []
    departed, filled = {}, {}
    order = 0

    def log(day, club, coach, job, kind, detail=""):
        events.append({"date": day.isoformat(), "club": club, "coach": coach, "job": job,
                       "event": kind, "detail": detail})

    def add(when, club, coach, job, kind, p_req, u_req, close, p_off, u_off):
        nonlocal order
        queue.append({"when": when, "order": order, "club": club, "coach": coach, "job": job, "kind": kind,
                      "p_req": p_req, "u_req": u_req, "close": close, "p_off": p_off, "u_off": u_off})
        order += 1

    # Stage D1: the Super Bowl clubs.
    for team in DEFERRED:
        c = clubs[team]
        u = rng.random()
        changed = u < c["p_change"]
        hire = OPENS_D1 + timedelta(days=rng.choice(cc.HIRE_DAYS_2013))
        row = {"club": team, "coach": c["coach"], "record_wins": c["wins"], "cell": c["cell"],
               "p_change": c["p_change"], "draw": round(u, 4), "changed": changed}
        if changed:
            row.update({"vacancy_opens": OPENS_D1.isoformat(), "hire_day": hire.isoformat(), "hired_from": "external"})
        changes.append(row)
        hc_draws = [(rng.random(), rng.random()) for _ in HC_CANDIDATES]
        jobs = [(rng.random(), rng.randint(2, 10), [(rng.random(), rng.random()) for _ in cc.COORD_FACTOR])
                for _ in ("offensive coordinator", "defensive coordinator")]
        pos = [rng.random() for _ in s3["position_requests"]["coaches"]]
        if not changed:
            continue
        for name, (u_req, u_off) in zip(HC_CANDIDATES, hc_draws):
            add(OPENS_D1, team, name, "head coach", "head coach",
                hc["base_probability"] * cc.hc_weight(name, m75, clubs), u_req, hire, hc["offer_probability"], u_off)
        for job, (u_open, offset, draws) in zip(("offensive coordinator", "defensive coordinator"), jobs):
            if u_open >= m75["stage_2_openings_below_head_coach"]["open_probability"][job]:
                continue
            for ((name, target), factor), (u_req, u_off) in zip(cc.COORD_FACTOR.items(), draws):
                if target == job and name not in GONE:
                    add(hire, team, name, job, "lateral coordinator" if cc.STAFF[name].get("coordinator") else "coordinator",
                        cr["base_probability"] * factor * club_f, u_req, hire + timedelta(days=offset),
                        cr["offer_probability"], u_off)
        for name, u_req in zip(s3["position_requests"]["coaches"], pos):
            if name not in GONE:
                add(hire, team, name, cc.STAFF[name]["job"], "same position",
                    s3["position_requests"]["probability"], u_req, hire, 0.0, 1.0)

    # Stage D2: coordinator openings at clubs that kept their head coach.
    retained = sorted(t for t in clubs if t != cc.JAX and t not in CHANGED_ENTRY_75
                      and not any(r["club"] == t and r["changed"] for r in changes))
    openings = []
    for team in retained:
        for job in ("offensive coordinator", "defensive coordinator"):
            u_open = rng.random()
            decided = rng.choice(DECISION_DATES)
            draws = [(rng.random(), rng.random()) for _ in cc.COORD_FACTOR]
            opened = u_open < OPEN_P[job]
            if opened:
                openings.append({"club": team, "job": job, "decision_date": decided.isoformat(),
                                 "reaches_jacksonville": decided >= FIRST_REQUEST})
            if not opened or decided < FIRST_REQUEST:
                continue
            when = max(FIRST_REQUEST, decided - REQUEST_LEAD)
            for ((name, target), factor), (u_req, u_off) in zip(cc.COORD_FACTOR.items(), draws):
                if target == job and name not in GONE:
                    lateral = cc.STAFF[name].get("coordinator", False)
                    add(when, team, name, job, "lateral coordinator" if lateral else "coordinator",
                        cr["base_probability"] * factor * club_f, u_req, decided, RETAINED_OFFER, u_off)

    # Apply in date order (Entry 75 rules): permissions, interviews, offers, one hire per club job.
    offers = []
    queue.sort(key=lambda o: (o["when"], o["order"]))
    i = 0
    while i < len(queue) or offers:
        offers.sort(key=lambda o: (o["when"], o["order"]))
        if offers and (i >= len(queue) or offers[0]["when"] <= queue[i]["when"]):
            o = offers.pop(0)
            if o["coach"] in departed or (o["club"], o["job"]) in filled:
                continue
            log(o["when"], o["club"], o["coach"], o["job"], "offer")
            log(o["when"], o["club"], o["coach"], o["job"], "hired", "accepted (Entry 75 stage 5)")
            departed[o["coach"]] = {"club": o["club"], "job": o["job"], "date": o["when"].isoformat()}
            filled[(o["club"], o["job"])] = o["when"]
            continue
        o = queue[i]
        i += 1
        if o["when"] > END or o["u_req"] >= o["p_req"] or o["coach"] in departed:
            continue
        if (o["club"], o["job"]) in filled and filled[(o["club"], o["job"])] <= o["when"]:
            continue
        log(o["when"], o["club"], o["coach"], o["job"], "request", "probability %.4f" % o["p_req"])
        if o["kind"] == "head coach":
            log(o["when"], o["club"], o["coach"], o["job"], "permission granted",
                "a head-coach interview cannot be refused once the employer's season is over (rule T2)")
        elif o["kind"] == "coordinator":
            log(o["when"], o["club"], o["coach"], o["job"], "permission granted",
                "lateral under the 2013 rules (T3) but a step up in title; Jacksonville's default policy grants it")
        else:
            log(o["when"], o["club"], o["coach"], o["job"], "permission refused",
                "lateral (rule T3); Jacksonville's default policy refuses a move to the same job elsewhere")
            continue
        log(o["when"], o["club"], o["coach"], o["job"], "interview")
        if o["close"] > END:
            pending.append({"club": o["club"], "coach": o["coach"], "job": o["job"],
                            "interviewed": o["when"].isoformat(), "decision_after": END.isoformat()})
        elif o["u_off"] < o["p_off"]:
            offers.append({"when": o["close"], "order": o["order"], "club": o["club"], "coach": o["coach"], "job": o["job"]})
    pending = [p for p in pending if p["coach"] not in departed]
    events.sort(key=lambda e: (e["date"], e["club"], e["coach"]))
    return changes, openings, events, departed, pending


def packet(m, snapshot, in_digest):
    return {"procedure": m["procedure"], "event_id": m["event_id"], "snapshot": snapshot,
            "method_sha256": cc.digest(METHOD), "code_sha256": cc.digest(Path(__file__).resolve()),
            "entry75_code_sha256": cc.digest(Path(cc.__file__).resolve()),
            "rates_sha256": cc.digest(cc.RATES), "inputs_sha256": in_digest}


def render():
    res = cc.load(RESULTS)
    text = PAGE.read_text(encoding="utf-8")
    marker = "\n## February 2014: the deferred procedure"
    text = text.split(marker)[0].rstrip() + "\n"
    lines = [marker.strip(), "",
             "Generated from `carousel_deferred_results.json` (%s). Method: [carousel_deferred_method.json](carousel_deferred_method.json); "
             "2013 base rate: [2013_retained_club_coordinator_turnover.md](2013_retained_club_coordinator_turnover.md). "
             "Window: January 12 to February 17, 2014." % res["ledger_entry"], "",
             "### Super Bowl clubs", "", "| Club | Coach | Cell | Chance | Result | Hire |", "|---|---|---|--:|---|---|"]
    for c in res["head_coach_changes"]:
        lines.append("| %s | %s | %s | %.1f%% | %s | %s |" % (c["club"], c["coach"], c["cell"].replace("|", ", "),
                     100 * c["p_change"], "changed" if c["changed"] else "kept", c.get("hire_day", "")))
    lines += ["", "### Coordinator openings at clubs that kept their head coach", ""]
    if res["openings"]:
        lines += ["| Club | Job | Decided | Could reach Jacksonville |", "|---|---|---|---|"]
        for o in res["openings"]:
            lines.append("| %s | %s | %s | %s |" % (o["club"], o["job"], o["decision_date"],
                                                  "yes" if o["reaches_jacksonville"] else "no, decided before January 12"))
    else:
        lines.append("None opened.")
    lines += ["", "### Requests for Jacksonville's assistants", ""]
    if res["events"]:
        lines += ["| Date | Club | Coach | Job | Event | Detail |", "|---|---|---|---|---|---|"]
        for e in res["events"]:
            lines.append("| %s | %s | %s | %s | %s | %s |" % (e["date"], e["club"], e["coach"], e["job"], e["event"], e["detail"]))
    else:
        lines.append("No club asked to interview a Jacksonville assistant.")
    lines += ["", "### Departures", ""]
    if res["departed"]:
        for name, d in res["departed"].items():
            lines.append("- **%s** leaves for %s (%s), %s. The job is vacant; any replacement follows the staff plan." % (
                name, d["club"], d["job"], d["date"]))
    else:
        lines.append("No Jacksonville assistant left in this window.")
    if res["pending"]:
        lines += ["", "### Pending at February 17", ""]
        for p in res["pending"]:
            lines.append("- **%s**: %s (%s), interviewed %s." % (p["coach"], p["club"], p["job"], p["interviewed"]))
    PAGE.write_text(text + "\n" + "\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", nargs="?", choices=("render",))
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    if args.action == "render":
        render()
        return 0
    m, m75 = cc.load(METHOD), cc.load(cc.METHOD)
    clubs = cc.inputs()
    for team in DEFERRED:
        print("%-20s p_change %.4f" % (team, clubs[team]["p_change"]))
    if not args.close:
        return 0
    if RESULTS.exists():
        print("DEFERRED CAROUSEL: already drawn")
        return 1
    from runtime.game_runner import _entropy_from_ref
    from runtime.private_client import Client
    client = Client()
    snapshot = client.current_snapshot()
    in_digest = hashlib.sha256(canonical(clubs)).hexdigest()
    pkt = packet(m, snapshot, in_digest)
    ref = client.close_event(pkt)
    rng = random.Random(int.from_bytes(hashlib.sha256(_entropy_from_ref(ref) + canonical(pkt)).digest(), "big"))
    changes, openings, events, departed, pending = resolve(rng, m, clubs, m75)
    RESULTS.write_text(json.dumps({**pkt, "ledger_entry": args.entry,
                                   "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(), "result_ref": ref,
                                   "head_coach_changes": changes, "openings": openings, "events": events,
                                   "departed": departed, "pending": pending}, indent=1) + "\n", encoding="utf-8")
    render()
    print("changes:", [c["club"] for c in changes if c["changed"]], "openings:", len(openings))
    print("events:", len(events), "departed:", departed, "pending:", pending)
    return 0


if __name__ == "__main__":
    sys.exit(main())
