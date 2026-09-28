#!/usr/bin/env python3
"""The January 2014 coaching carousel and Jacksonville's staff exposure.

  python scripts/coaching_carousel.py            # dry run: inputs and per-club probabilities
  python scripts/coaching_carousel.py --close    # one private draw; write results and the page
  python scripts/coaching_carousel.py render     # rewrite requests_and_outcomes.md

Method: career/2014/offseason/staff_changes/carousel_method.json, fixed and
committed before the draw. Rules: library/2014_coaching_hiring_and_anti_tampering_rules.md.
Every probability reads only the job, the coach's role and record, the clubs'
branch records and the calendar, never which club is the protagonist's.
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
from runtime.week_inputs import schedule
from scripts.render_season_stats import load_receipts
from scripts.research.build_2013_week1_depth_charts import CLUBS

DIR = ROOT / "career/2014/offseason/staff_changes"
METHOD = DIR / "carousel_method.json"
RESULTS = DIR / "carousel_results.json"
PAGE = DIR / "requests_and_outcomes.md"
RATES = ROOT / "library/data/2012_hc_change_base_rates.json"
JAX = "Jacksonville Jaguars"
NAME_OF = {**CLUBS, "JAX": JAX}
BRANCH_DATE = date(2014, 2, 2)
SEASON_END = date(2013, 12, 29)
ELIMINATED_JAX = date(2014, 1, 11)
HC_WINDOW_OPENS = date(2014, 1, 6)       # the evening of January 5 (rule W5), counted from the 6th
HIRE_DAYS_2013 = (3, 6, 7, 9, 14, 15, 15, 16)   # days from each vacancy opening (rules file 7.3)
TENURE_OVERRIDE = {"NO": 7}                     # Payton: 2006-2011 and 2013 (the 2012 suspension season is not his)
HC_CANDIDATES = ("Romeo Crennel", "Mike Tice", "Alan Lowry")

# Jacksonville's twelve assistants (career/2013/coaching_staff.md).
STAFF = {
    "Romeo Crennel": {"job": "defensive coordinator", "side": "defense", "calls_plays": True, "coordinator": True},
    "Mike Tice": {"job": "offensive coordinator", "side": "offense", "calls_plays": False, "coordinator": True},
    "Alan Lowry": {"job": "special teams coordinator", "side": "special teams", "calls_plays": True, "coordinator": True},
    "Frank Bush": {"job": "linebackers", "side": "defense"},
    "George Yarno": {"job": "offensive line / run game", "side": "offense"},
    "Jeremy Bates": {"job": "quarterbacks", "side": "offense"},
    "Darryl Drake": {"job": "wide receivers", "side": "offense"},
    "Tim Spencer": {"job": "running backs", "side": "offense"},
    "Tony Oden": {"job": "defensive backs", "side": "defense"},
    "Anthony Pleasant": {"job": "defensive line", "side": "defense"},
    "John Zernhelt": {"job": "tight ends", "side": "offense"},
    "Charlie Skalaski": {"job": "offensive assistant / assistant quarterbacks", "side": "offense"},
}
COORD_FACTOR = {  # method stage 3, coordinator_requests.coach_factor
    ("Jeremy Bates", "offensive coordinator"): 8.0, ("Frank Bush", "defensive coordinator"): 6.0,
    ("George Yarno", "offensive coordinator"): 1.5, ("Tony Oden", "defensive coordinator"): 1.5,
    ("Anthony Pleasant", "defensive coordinator"): 1.0, ("Darryl Drake", "offensive coordinator"): 1.0,
    ("Tim Spencer", "offensive coordinator"): 1.0, ("John Zernhelt", "offensive coordinator"): 1.0,
    ("Romeo Crennel", "defensive coordinator"): 1.6, ("Mike Tice", "offensive coordinator"): 1.6,
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def game_dates():
    dates = {}
    for week in range(1, 22):
        for g in schedule(week):
            dates[(week, g["away"], g["home"])] = date.fromisoformat(g["date"])
    return dates


def inputs():
    """Every club's branch 2013 record, postseason exit and coach cell (committed data only)."""
    rates = load(RATES)
    dates = game_dates()
    clubs = {}
    for r in load_receipts(ROOT / "career/2013/stats/game_receipts"):
        for team, other in ((r["away"], r["home"]), (r["home"], r["away"])):
            c = clubs.setdefault(team, {"wins": 0.0, "points_for": 0, "points_against": 0, "playoffs": False,
                                        "last_game": SEASON_END.isoformat()})
            us, them = r["final_score"][team], r["final_score"][other]
            c["wins"] += 1.0 if us > them else 0.5 if us == them else 0.0
            c["points_for"] += us
            c["points_against"] += them
    for r in load_receipts(ROOT / "career/2013/stats/postseason_receipts"):
        when = dates[(int(r["week"]), r["away"], r["home"])]
        for team in (r["away"], r["home"]):
            clubs[team]["playoffs"] = True
            clubs[team]["last_game"] = max(clubs[team]["last_game"], when.isoformat())
    for side, key, reverse in (("offense", "points_for", True), ("defense", "points_against", False)):
        order = sorted(clubs, key=lambda t: (-clubs[t][key] if reverse else clubs[t][key], t))
        for rank, team in enumerate(order, 1):
            clubs[team]["rank_" + side] = rank
    for code, info in rates["tenure_2013"].items():
        team = NAME_OF[code]
        clubs[team]["coach"] = info["coach"] if team != JAX else "Alex Stone"
        clubs[team]["tenure"] = TENURE_OVERRIDE.get(code, info["tenure"])
        clubs[team]["recent_playoffs"] = info["playoffs_2011_or_2012"]
        clubs[team]["code"] = code
    for team, c in clubs.items():
        c["cell"] = cell(c)
        c["p_change"] = rates["cells"][c["cell"]]["rate"] if team != JAX else None
        c["vacancy_opens"] = (date.fromisoformat(c["last_game"]) + timedelta(days=1)).isoformat()
        c["deferred"] = team != JAX and date.fromisoformat(c["vacancy_opens"]) > BRANCH_DATE
    return clubs


def cell(c):
    t = c["tenure"]
    tb = "1st season" if t == 1 else "2nd-3rd" if t <= 3 else "4th+"
    if c["playoffs"]:
        return "playoffs|" + tb
    w = c["wins"]
    wb = "0-4" if w <= 4.5 else "5-6" if w <= 6.5 else "7-8" if w <= 8.5 else "9-10" if w <= 10.5 else "11+"
    if t == 1:
        return wb + "|" + tb
    return wb + "|" + tb + "|" + ("recent playoffs" if c["recent_playoffs"] else "no recent playoffs")


def unit_factor(rank):
    return 1.5 if rank <= 8 else 1.0 if rank <= 24 else 0.6


def club_factor(m, clubs, team):
    """The playoff-club factor divided by its league mean, so it moves interest
    between clubs' staffs without raising the league total (method stage 3)."""
    f = m["stage_3_requests_for_jacksonville_assistants"]["head_coach_requests"]["club_factor"]
    raw = lambda c: f["playoff club"] if c["playoffs"] else f["other"]
    return raw(clubs[team]) / (sum(raw(c) for c in clubs.values()) / len(clubs))


def unit_mean(clubs):
    return sum(unit_factor(c["rank_offense"]) for c in clubs.values()) / len(clubs)


def hc_weight(name, m, clubs):
    s = m["stage_3_requests_for_jacksonville_assistants"]["head_coach_requests"]
    info = STAFF[name]
    w = s["role_factor"][info["job"]]
    w *= s["play_calling_factor"]["calls plays" if info["calls_plays"] else "does not call plays"]
    w *= club_factor(m, clubs, JAX)
    if info["side"] in ("offense", "defense"):
        w *= unit_factor(clubs[JAX]["rank_" + info["side"]]) / unit_mean(clubs)
    return w


def resolve(rng, m, clubs):
    """Every draw, in the method's fixed order. Returns (changes, events, departed, pending)."""
    s3 = m["stage_3_requests_for_jacksonville_assistants"]
    hc = s3["head_coach_requests"]
    cr = s3["coordinator_requests"]
    deferred_id = m["deferred_procedure"]["event_id"]
    changes, searches, events, pending = [], [], [], []
    departed, filled = {}, {}
    row_of = {}

    def log(day, club, coach, job, kind, detail=""):
        events.append({"date": day.isoformat(), "club": club, "coach": coach, "job": job, "event": kind, "detail": detail})

    # Stage 1: head-coach changes (Jacksonville resolved by Entry 74).
    for team in sorted(clubs):
        c = clubs[team]
        if team == JAX:
            continue
        opens = date.fromisoformat(c["vacancy_opens"])
        if c["deferred"]:
            # A Super Bowl club's decision falls after the branch date: deferred, not drawn.
            changes.append({"club": team, "coach": c["coach"], "record_wins": c["wins"], "cell": c["cell"],
                            "p_change": c["p_change"], "draw": None, "changed": None, "deferred": deferred_id})
            continue
        u = rng.random()
        changed = u < c["p_change"]
        row = {"club": team, "coach": c["coach"], "record_wins": c["wins"], "cell": c["cell"],
               "p_change": c["p_change"], "draw": round(u, 4), "changed": changed}
        if changed:
            hire = opens + timedelta(days=rng.choice(HIRE_DAYS_2013))
            row.update({"vacancy_opens": opens.isoformat(), "hire_day": hire.isoformat(),
                        "resolved_by_branch_date": hire <= BRANCH_DATE, "hired_from": "external"})
            searches.append({"club": team, "opens": opens, "hire": hire})
            row_of[team] = row
        changes.append(row)

    # Every remaining draw is made first, in a fixed structural order, so the
    # result is deterministic whatever the dates; events are then applied in
    # date order, so a coach who has left is never asked again (rule 16 logging).
    hc_draws = [[(rng.random(), rng.random()) for _ in HC_CANDIDATES] for _ in searches]
    coord_draws = []
    for _ in searches:
        jobs = [(rng.random(), rng.randint(2, 10), [(rng.random(), rng.random()) for _ in COORD_FACTOR])
                for _ in ("offensive coordinator", "defensive coordinator")]
        coord_draws.append((jobs, [rng.random() for _ in s3["position_requests"]["coaches"]]))

    def run(queue):
        offers = []
        queue = sorted(queue, key=lambda o: (o["when"], o["order"]))
        i = 0
        while i < len(queue) or offers:
            offers.sort(key=lambda o: (o["when"], o["order"]))
            if offers and (i >= len(queue) or offers[0]["when"] <= queue[i]["when"]):
                o = offers.pop(0)
                if o["coach"] in departed or (o["club"], o["job"]) in filled:
                    continue
                log(o["when"], o["club"], o["coach"], o["job"], "offer")
                log(o["when"], o["club"], o["coach"], o["job"], "hired", "accepted (method stage 5)")
                departed[o["coach"]] = {"club": o["club"], "job": o["job"], "date": o["when"].isoformat()}
                filled[(o["club"], o["job"])] = o["when"]
                continue
            o = queue[i]
            i += 1
            gone = departed.get(o["coach"])
            if o["when"] > BRANCH_DATE or o["u_req"] >= o["p_req"]:
                continue
            if gone and o["when"] >= date.fromisoformat(gone["date"]):
                continue
            if (o["club"], o["job"]) in filled and filled[(o["club"], o["job"])] <= o["when"]:
                continue
            log(o["when"], o["club"], o["coach"], o["job"], "request", "probability %.3f" % o["p_req"])
            if o["kind"] == "head coach":
                if o["when"] <= ELIMINATED_JAX:
                    detail = ("inside the January 5-12 window for a Wild Card winner's assistants (rule W5); whether a playoff "
                              "club could refuse rather than schedule it is Unverified (W11), and Jacksonville's default policy grants it")
                else:
                    detail = "a head-coach interview cannot be refused once the employer's season is over (rule T2)"
                log(o["when"], o["club"], o["coach"], o["job"], "permission granted", detail)
            elif o["kind"] == "coordinator":
                log(o["when"], o["club"], o["coach"], o["job"], "permission granted",
                    "lateral under the 2013 rules (T3) but a step up in title; Jacksonville's default policy grants it")
            else:
                log(o["when"], o["club"], o["coach"], o["job"], "permission refused",
                    "lateral (rule T3); Jacksonville's default policy refuses a move to the same job elsewhere")
                continue
            log(o["when"], o["club"], o["coach"], o["job"], "interview")
            if o["close"] > BRANCH_DATE:
                pending.append({"club": o["club"], "coach": o["coach"], "job": o["job"], "interviewed": o["when"].isoformat(),
                                "decision_after": BRANCH_DATE.isoformat(), "resolved_by": deferred_id})
            elif o["u_off"] < o["p_off"]:
                offers.append({"when": o["close"], "order": o["order"], "club": o["club"], "coach": o["coach"], "job": o["job"]})

    # Stages 3-5 for head-coach jobs. Only a head-coach job can take a
    # Jacksonville coordinator (every other request for one is lateral and
    # refused), so these resolve first and fix each search's real hire date.
    queue, order = [], 0
    for srch, draws in zip(searches, hc_draws):
        if srch["hire"] < HC_WINDOW_OPENS:   # closed before Jacksonville's staff could be asked (rule W5)
            continue
        for name, (u_req, u_off) in zip(HC_CANDIDATES, draws):
            queue.append({"when": max(srch["opens"], HC_WINDOW_OPENS), "order": order, "club": srch["club"], "coach": name,
                          "job": "head coach", "kind": "head coach", "p_req": hc["base_probability"] * hc_weight(name, m, clubs),
                          "u_req": u_req, "close": max(srch["hire"], ELIMINATED_JAX + timedelta(days=1)),
                          "p_off": hc["offer_probability"], "u_off": u_off})
            order += 1
    run(queue)
    for name, d in departed.items():
        row = row_of[d["club"]]
        row.update({"hire_day": d["date"], "hired_from": "Jacksonville Jaguars (%s)" % name})
        next(x for x in searches if x["club"] == d["club"])["hire"] = date.fromisoformat(d["date"])

    # Stages 2-5 below head coach, from each search's actual hire date.
    queue = []
    club_f = club_factor(m, clubs, JAX)
    for srch, (jobs, position_draws) in zip(searches, coord_draws):
        opens = srch["hire"]
        reach = max(opens, ELIMINATED_JAX + timedelta(days=1))   # lateral requests wait for elimination (W10)
        for job, (u_open, offset, draws) in zip(("offensive coordinator", "defensive coordinator"), jobs):
            close = opens + timedelta(days=offset)
            if u_open >= m["stage_2_openings_below_head_coach"]["open_probability"][job] or reach > close:
                continue
            for ((name, target), factor), (u_req, u_off) in zip(COORD_FACTOR.items(), draws):
                if target != job:
                    continue
                queue.append({"when": reach, "order": order, "club": srch["club"], "coach": name, "job": job,
                              "kind": "lateral coordinator" if STAFF[name].get("coordinator") else "coordinator",
                              "p_req": cr["base_probability"] * factor * club_f, "u_req": u_req, "close": close,
                              "p_off": cr["offer_probability"], "u_off": u_off})
                order += 1
        for name, u_req in zip(s3["position_requests"]["coaches"], position_draws):
            queue.append({"when": reach, "order": order, "club": srch["club"], "coach": name, "job": STAFF[name]["job"],
                          "kind": "same position", "p_req": s3["position_requests"]["probability"], "u_req": u_req,
                          "close": reach, "p_off": 0.0, "u_off": 1.0})
            order += 1
    run(queue)
    pending = [p for p in pending if p["coach"] not in departed]
    events.sort(key=lambda e: (e["date"], e["club"], e["coach"]))
    return changes, events, departed, pending


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packet(m, snapshot, in_digest):
    return {"procedure": m["procedure"], "event_id": m["event_id"], "snapshot": snapshot,
            "method_sha256": digest(METHOD), "code_sha256": digest(Path(__file__).resolve()),
            "rates_sha256": digest(RATES), "inputs_sha256": in_digest}


def render():
    res = load(RESULTS)
    changed = [c for c in res["head_coach_changes"] if c["changed"]]
    lines = ["# January 2014 coaching carousel: requests and outcomes", "",
             "Generated by `scripts/coaching_carousel.py render` from `carousel_results.json`. Method: "
             "[carousel_method.json](carousel_method.json); rules: `library/2014_coaching_hiring_and_anti_tampering_rules.md`. "
             "Resolved retroactively on the branch date of February 2, 2014 (%s)." % res["ledger_entry"], "",
             "## Head-coach changes around the league", "",
             "| Club | Coach | 2013 wins | Cell | Chance | Result | Hire |", "|---|---|--:|---|--:|---|---|"]
    for c in res["head_coach_changes"]:
        result = "deferred past February 2" if c.get("deferred") else "changed" if c["changed"] else "kept"
        hire = ""
        if c["changed"]:
            hire = c["hire_day"] if c["hire_day"] <= BRANCH_DATE.isoformat() else "open at February 2"
            if c["hired_from"] != "external":
                hire += ", from " + c["hired_from"]
        lines.append("| %s | %s | %s | %s | %.1f%% | %s | %s |" % (
            c["club"], c["coach"], ("%g" % c["record_wins"]), c["cell"].replace("|", ", "), 100 * c["p_change"], result, hire))
    deferred = [c["club"] for c in res["head_coach_changes"] if c.get("deferred")]
    lines += ["", "%d clubs changed head coaches. New head coaches from outside Jacksonville are recorded as external hires: "
              "the branch has no league-wide staff register to name them." % len(changed)]
    if deferred:
        lines += ["", "The Super Bowl clubs (%s) decide after February 2; they are resolved by `%s` when the clock passes "
                  "that date." % (" and ".join(deferred), res["deferred_procedure"])]
    lines += ["", "## Requests for Jacksonville's assistants", ""]
    if not res["events"]:
        lines.append("No club asked to interview a Jacksonville assistant.")
    else:
        lines += ["| Date | Club | Coach | Job | Event | Detail |", "|---|---|---|---|---|---|"]
        for e in res["events"]:
            lines.append("| %s | %s | %s | %s | %s | %s |" % (e["date"], e["club"], e["coach"], e["job"], e["event"], e["detail"]))
    lines += ["", "## Departures", ""]
    if res["departed"]:
        for name, d in res["departed"].items():
            lines.append("- **%s** leaves for %s (%s), %s. The job is vacant; any replacement awaits the user's staff plan "
                         "([staff_plan.md](staff_plan.md))." % (name, d["club"], d["job"], d["date"]))
    elif not res["pending"]:
        lines.append("No Jacksonville assistant left. Every one stays under contract for 2014.")
    else:
        lines.append("No Jacksonville assistant left by February 2.")
    pending = {(p["coach"], p["club"], p["job"]) for p in res["pending"]}
    hired = {(e["coach"], e["club"], e["job"]) for e in res["events"] if e["event"] == "hired"}
    passed = [e for e in res["events"] if e["event"] == "interview"
              and (e["coach"], e["club"], e["job"]) not in hired | pending]
    if passed:
        lines += ["", "## Interviewed, not hired", ""]
        for e in passed:
            lines.append("- **%s** interviewed with %s (%s) on %s and was not offered the job; the club hired another "
                         "candidate by February 2. He stays under contract with Jacksonville." % (
                             e["coach"], e["club"], e["job"], e["date"]))
    if res["pending"]:
        lines += ["", "## Pending at February 2", "",
                  "Interviewed, with the club's decision after the branch date. Resolved by `%s`." % res["deferred_procedure"], ""]
        for p in res["pending"]:
            lines.append("- **%s**: %s (%s), interviewed %s." % (p["coach"], p["club"], p["job"], p["interviewed"]))
    PAGE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", nargs="?", choices=("render",))
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    if args.action == "render":
        render()
        return 0
    m = load(METHOD)
    clubs = inputs()
    for team in sorted(clubs, key=lambda t: -(clubs[t]["p_change"] or 0)):
        c = clubs[team]
        print("%-24s %-18s wins %-4g %-20s p=%s" % (team, c["coach"], c["wins"], c["cell"], c["p_change"]))
    for name in HC_CANDIDATES:
        print("HC weight %s %.3f" % (name, hc_weight(name, m, clubs)))
    expected = sum(c["p_change"] for t, c in clubs.items() if t != JAX and not c["deferred"])
    print("expected head-coach changes by February 2 %.2f (deferred: %s)" % (
        expected, [t for t, c in clubs.items() if c["deferred"]]))
    if not args.close:
        return 0
    if RESULTS.exists():
        print("CAROUSEL: already drawn")
        return 1
    from runtime.game_runner import _entropy_from_ref
    from runtime.private_client import Client
    client = Client()
    snapshot = client.current_snapshot()
    in_digest = hashlib.sha256(canonical(clubs)).hexdigest()
    pkt = packet(m, snapshot, in_digest)
    ref = client.close_event(pkt)
    rng = random.Random(int.from_bytes(hashlib.sha256(_entropy_from_ref(ref) + canonical(pkt)).digest(), "big"))
    changes, events, departed, pending = resolve(rng, m, clubs)
    RESULTS.write_text(json.dumps({**{k: pkt[k] for k in ("procedure", "event_id", "snapshot", "method_sha256",
                                                            "code_sha256", "rates_sha256", "inputs_sha256")},
                                   "ledger_entry": args.entry, "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(),
                                   "result_ref": ref, "deferred_procedure": m["deferred_procedure"]["event_id"],
                                   "head_coach_changes": changes, "events": events, "departed": departed,
                                   "pending": pending}, indent=1) + "\n", encoding="utf-8")
    render()
    print("changes:", [c["club"] for c in changes if c["changed"]])
    print("events:", len(events), "departed:", departed, "pending:", pending)
    return 0


if __name__ == "__main__":
    sys.exit(main())
