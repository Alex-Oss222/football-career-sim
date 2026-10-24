#!/usr/bin/env python3
"""Apply the general manager's roster decision on an injury replacement (rebuild step 5, D1).

  python scripts/apply_transaction.py --file DECISION.json --season YEAR [--check]
  python scripts/apply_transaction.py ID --season YEAR [--check]

The runner records the general manager's decision as a transaction record (``transaction-v1``,
runtime/transactions.py): the event it decides, the criteria entry it applies (recorded before
Stone's answer), Stone's answer as its substance (or "none on file"), the basis with its source and
the moves. ``--file`` places a checked record in the roster's transaction store; ``ID`` applies one.
This script is the single writer of everything the decision changes, in one commit:

- the roster record (each player's list and status, the club's current medical communication for a
  player joining the 53, ``as_of``);
- the contract records through runtime/player_contracts.add_entry (a promotion's or a signing's
  contract computed by the stored in-season terms method; a claimed contract marked unresolved) and
  the contract inputs' ``players`` block rebuilt;
- each player's permanent record (a dated transaction; a new record for a player who joins);
- both depth chart copies through the chart writers (the player placed off the 53 taken off, a new
  player at the bottom of his group), one update-log entry, then the week's game-day change check
  (scripts/change_game_day.py --needed); the Game Plan and the call sheet are never touched;
- the Transaction page in the roster folder, the event's one result, with its event-record line;
  for a signing from outside the club its signing record in the free agency folder and a dated line
  in the signings page;
- the general manager's transaction item resolved, the event resolved (scripts/resolve_event.py
  --result) and the pages rebuilt.

A waiver claim is decided when its claim period ends (library W1 to W4): Jacksonville's place in this
career's own waiver order against the club that really claimed the player, read only once the
league's record of the claims is public; a claim against a club ahead of Jacksonville is lost, and
that is recorded on the event, which stays open. A section 4 pursuit is decided by one private draw
at the player's real signing date against the contract he really signed (method section 4); a
player who has signed with no club has no contract to compare and cannot be drawn, and a lost draw
is recorded on the event. Refused, with nothing written: a decision without its criteria entry; a
decision while Stone's recommendation is still due; a new player with no gsis id or birth date on
the birth-date registry; a player not legally available on the date; a release, waiver or trade
(not built yet); an active roster above 53 or a practice squad above 10; a paused game; a time after
the master date/time; a figure without a source; a promotion or signing whose in-season contract
pays below the league minimum for the credited seasons his contract record holds (the promotion
structure is the undrafted schedule, for a player with none). ``--check`` makes every check and writes nothing
(and draws nothing).
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import (current_job, decision_queue, decisions, open_events, people, player_bios,  # noqa: E402
                     player_contracts, transactions as tx)
from runtime import roster as roster_record  # noqa: E402
from runtime.clean_pages import text_errors  # noqa: E402

Refused = tx.Refused


# ------------------------------------------------------------------ the resolution (A4)
def resolve_result(root, season, event_id, by, at, decision, criteria, result):
    """Resolve the event with its Transaction page through scripts/resolve_event.py --result (A4):
    Stone's open item withdrawn by the organization when his recommendation's due time has passed
    unanswered, the event resolved through the store, Record.md and the open period's index rebuilt."""
    from scripts import resolve_event
    return resolve_event.resolve(root, season, event_id, "executed", by, at, decision, criteria=criteria,
                                 result=result)


# ------------------------------------------------------------------ files touched
def snapshot(paths, trees=()):
    """The bytes of ``paths`` and of every file under ``trees`` (None for a file not there yet), and
    the trees themselves, so ``restore`` also removes a file written into them afterwards."""
    saved = {Path(p): (Path(p).read_bytes() if Path(p).is_file() else None) for p in paths}
    for tree in trees:
        for path in Path(tree).rglob("*") if Path(tree).is_dir() else ():
            if path.is_file() and "__pycache__" not in path.parts:
                saved[path] = path.read_bytes()
    return {"files": saved, "trees": [Path(t) for t in trees]}


def restore(saved):
    files = saved["files"]
    for tree in saved["trees"]:
        for path in list(tree.rglob("*")) if tree.is_dir() else ():
            if path.is_file() and path not in files and "__pycache__" not in path.parts:
                path.unlink()
    for path, data in files.items():
        if data is None:
            if path.is_file():
                path.unlink()
        elif not path.is_file() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)


# ------------------------------------------------------------------ the plan
class Plan:
    """Everything one decision changes, worked out before anything is written."""

    def __init__(self, root, season, record):
        self.root = Path(root).resolve()
        self.season = int(season)
        self.record = copy.deepcopy(record)
        self.event = open_events.get(self.season, record["event"], self.root)
        self.job = current_job.load(self.root)
        self.paths = tx.paths(self.season, self.root)
        self.data = tx.roster(self.season, self.root)
        self.registry = player_bios.load(self.root)
        self.outcome = "applied"        # or "claim_lost", "pursuit_lost"
        self.lost = None                # (process entry, record changes) for a lost claim or draw
        self.effective = tx._day(record["date"])
        self.at = open_events.parse_at(record["at"])
        self.changes = {}               # player: {"effective", "contract"}
        self.signings = {}              # player: signing record path
        self.notes = []


def refuse_if(problems):
    if problems:
        raise Refused("; ".join(problems))


def check_record(plan):
    root, record, event = plan.root, plan.record, plan.event
    if event is None:
        raise Refused("no injury replacement event %s is recorded" % record["event"])
    refuse_if(tx.record_errors(record, root, event))
    if record["status"] != "decided":
        raise Refused("transaction %s is %s; a decision is applied once" % (record["id"], record["status"]))
    if event["state"] == "resolved":
        raise Refused("event %s is already resolved" % event["id"])
    # Stone's recommendation is asked: the general manager decides once it is answered, or once its
    # due time has passed unanswered (open_events DUE_TIME_SUMMARY); his answer alone never applies one.
    item = next((i for i in decision_queue.load(root)["items"] if i.get("id") == event.get("queue_item")), None)
    if item is not None and item.get("status") == "OPEN" and event.get("response") is None:
        due = open_events.parse_at(item["deadline"]["at"]) if (item.get("deadline") or {}).get("at") else None
        if due is None or plan.at < due:
            raise Refused("Stone's recommendation is due %s and not yet answered; the general manager decides once it "
                          "is answered or its due time has passed" % (open_events.at_text(due) if due else "with no "
                                                                      "due time set"))


def _uid(plan, name):
    row = plan.registry.get(name)
    if not row or not row.get("gsis_id") or not row.get("birth_date"):
        raise Refused("%s has no gsis id or birth date on the birth-date registry; the league record cannot place "
                      "him, so he cannot join the roster until his identity is recorded" % name)
    return row["gsis_id"]


def decide_claim(plan, move):
    """The award of a waiver claim (library W1 to W4), or Refused while it cannot yet be decided."""
    season, root = plan.season, plan.root
    uid = _uid(plan, move["player"])
    waived_on = tx._day(move.get("waived_on") or "")
    candidates = {r["uid"]: (r, end) for r, end in tx.waiver_candidates(season, plan.at, root)}
    if uid not in candidates:
        raise Refused("%s was not on waivers with his claim period open when the decision was made" % move["player"])
    row, end = candidates[uid]
    if tx._day(row["real_date"]) != waived_on:
        raise Refused("%s's waiver request is dated %s on the league record" % (move["player"],
                                                                                 tx.long_date(row["real_date"])))
    clock = open_events.master_clock(root)
    day_after = end.date() + dt.timedelta(days=1)
    covered = tx.rails_as_of(season, root)
    if clock.date < day_after or covered is None or covered < day_after:
        raise Refused("The claim period on %s ends %s; the claim is decided once the league's record of that day's "
                      "claims is in the career" % (move["player"], open_events.at_text(end)))
    club = open_events.employer_club(root)
    real = tx.real_claim(season, uid, waived_on, clock.date, root)
    move["waived_by"] = tx.club_name(season, row["club"], root)
    if real is None:
        plan.effective, plan.at_effective = end.date(), end
        return {"claimed_by": None, "order": "no other club claimed him", "at": open_events.iso(end)}
    other = tx.club_name(season, real["club"], root)
    ahead, why = tx.claim_priority(season, end.date(), club, other, root)
    if ahead is None:
        raise Refused("The claim on %s cannot be decided: %s. It is put to the user" % (move["player"], why))
    award = {"claimed_by": other, "order": why, "at": open_events.iso(end), "jacksonville": ahead == club}
    if ahead == club:
        plan.effective, plan.at_effective = end.date(), end
        return award
    plan.outcome = "claim_lost"
    plan.lost = ({"at": open_events.iso(max(end, plan.at)), "kind": "decision", "by": open_events.OTHER_CLUB,
                  "what": ("The claim on %s was awarded to the %s, ahead of Jacksonville in the waiver order (%s)"
                           % (move["player"], other, why)),
                  "source": tx._rails_source(season, real, root)}, {"award": award})
    return award


def decide_pursuit(plan, move, client=None, check=False):
    """The method section 4 draw at the player's real signing date, or Refused while it cannot be made."""
    season, root = plan.season, plan.root
    uid = _uid(plan, move["player"])
    clock = open_events.master_clock(root)
    released = max((r for r in tx.rails_rows(season, plan.at.date(), root)
                    if r["uid"] == uid and r["kind"] in tx.DEPARTING), key=lambda r: (r["real_date"], r["id"]),
                   default=None)
    earlier = tx.real_signing(season, uid, released["real_date"], clock.date, root) if released else None
    if earlier is not None and tx._day(earlier["real_date"]) < plan.effective:
        # He really signed before Jacksonville's offer (a move public only after the offer was made):
        # an offer counts only if it was made before he signed, so he is gone (method section 4).
        plan.outcome = "pursuit_lost"
        plan.lost = ({"at": open_events.iso(max(plan.at, open_events.et(clock.date))), "kind": "decision",
                      "by": open_events.OTHER_CLUB,
                      "what": ("%s signed with the %s on %s, before Jacksonville's offer; the offer does not count"
                               % (move["player"], tx.club_name(season, earlier["club"], root),
                                  tx.long_date(earlier["real_date"]))),
                      "source": tx._rails_source(season, earlier, root)},
                     {"draw": {"jacksonville": False, "before_offer": True, "real_date": earlier["real_date"]}})
        return None
    signed = tx.real_signing(season, uid, plan.effective, clock.date, root)
    if signed is None:
        raise Refused("%s has not signed with any club on the league record through %s. The league method decides a "
                      "pursuit only at the date the player signs, against the contract he signs; a player who signs "
                      "with no club has no contract to compare an offer with and cannot be drawn, so he cannot fill "
                      "this place" % (move["player"], tx.long_date(clock.date)))
    offer = move.get("offer") or {}
    if offer.get("method") != "in_season_minimum" or type(offer.get("credited_seasons")) is not int:
        raise Refused("Jacksonville's offer to %s is the in-season minimum for his credited seasons, with their source; "
                      "another offer is not built" % move["player"])
    comparison = move.get("comparison")
    club = tx.club_name(season, signed["club"], root)
    if not isinstance(comparison, dict) or type(comparison.get("apy")) is not int or comparison["apy"] <= 0 or \
            not comparison.get("source"):
        raise Refused("The contract %s signed with the %s on %s is not on file; it is researched under the two-pass "
                      "rule and recorded with its source before the draw" % (move["player"], club,
                                                                             tx.long_date(signed["real_date"])))
    apy = player_contracts.minimum_salary(season, offer["credited_seasons"], root)
    inputs = tx.draw_inputs({"apy": apy, "guarantee": 0}, comparison, plan.effective, signed["real_date"])
    m = tx.money_index(apy, 0, comparison["apy"], comparison.get("guarantee") or 0)
    p = tx.chance(m)
    at_signing = max(plan.at, open_events.et(tx._day(signed["real_date"])))
    stored = plan.record.get("draw")
    if stored is not None:
        # Drawn once already (its record kept when a later write failed): the same draw stands and the
        # private service is not asked again under the same event.
        if not stored.get("jacksonville"):
            raise Refused("the draw for %s is recorded and went to his real contract" % move["player"])
        plan.effective, plan.at_effective = tx._day(signed["real_date"]), at_signing
        return stored
    if check:
        plan.notes.append("%s: money index %.4f, chance %.4f; the draw is made when this is applied" % (
            move["player"], m, p))
        plan.effective, plan.at_effective = tx._day(signed["real_date"]), at_signing
        return None
    from runtime.game_runner import _entropy_from_ref
    if client is None:
        from runtime.private_client import Client
        client = Client()
    method = tx.paths(season, root).record("league/personnel/method.md")
    code = hashlib.sha256()
    for path in (Path(tx.__file__).resolve(), Path(__file__).resolve()):
        code.update(path.name.encode() + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    pkt = {"procedure": tx.PURSUIT_PROCEDURE, "event_id": "%s-market-draw" % plan.record["id"],
           "snapshot": client.current_snapshot(), "method_sha256": tx.digest_bytes(method.read_bytes()),
           "code_sha256": code.hexdigest(), "inputs_sha256": tx.digest_bytes(tx.canonical(inputs))}
    ref = client.close_event(pkt)
    stream = random.Random(int.from_bytes(hashlib.sha256(_entropy_from_ref(ref) + tx.canonical(pkt)).digest(), "big"))
    u = stream.random()
    draw = {"packet": pkt, "packet_sha256": tx.digest_bytes(tx.canonical(pkt)), "result_ref": ref, "inputs": inputs,
            "m": round(m, 4), "chance": round(p, 4), "draw": round(u, 4), "jacksonville": u < p,
            "real_club": club, "real_date": signed["real_date"]}
    # The draw is kept on the decision at once, so a later failure never draws it again.
    plan.record["draw"] = draw
    tx.write(dict(tx.get(season, plan.record["id"], root), draw=draw), root)
    if u < p:
        plan.effective, plan.at_effective = tx._day(signed["real_date"]), at_signing
        return draw
    plan.outcome = "pursuit_lost"
    plan.lost = ({"at": open_events.iso(at_signing), "kind": "decision", "by": open_events.OTHER_CLUB,
                  "what": ("%s signed with the %s on %s; the draw under the league method went to that contract"
                           % (move["player"], club, tx.long_date(signed["real_date"]))),
                  "source": tx._rails_source(season, signed, root)}, {"draw": draw})
    return draw


def check_legal(plan):
    """Each move against the roster as it stands and the rules on the date."""
    data, season, root = plan.data, plan.season, plan.root
    rows = {r["name"]: r for r in data["players"]}
    controlled = set(rows)
    for move in plan.record["moves"]:
        name, kind = move["player"], move["kind"]
        row = rows.get(name)
        if kind in ("reserve", "promoted", "reinstated"):
            if row is None or row["list"] != move["from_list"]:
                raise Refused("%s is not on Jacksonville's %s list" % (name, move["from_list"].replace("_", " ")))
        else:
            if name in controlled:
                raise Refused("%s is already under Jacksonville's control" % name)
            _uid(plan, name)
        if kind == "reserve" and move.get("designation") == "designated":
            used = [r["name"] for r in data["players"] if "designated for return" in r["status"].lower()]
            for rid, record in people.load_all(root).items():
                for t in record.get("transactions") or ():
                    if t.get("kind") == "reserve" and "designated for return" in t.get("text", "") and \
                            str(t.get("date", "")).startswith(str(season)):
                        used.append(record["name"])
            if used:
                raise Refused("Jacksonville's one designation for return this season is used (%s; rules library R6)"
                              % ", ".join(sorted(set(used))))
        if kind == "reinstated":
            window = tx.return_window(row)
            if window is None:
                raise Refused("%s is not on reserve/injured designated for return with a dated placement" % name)
            if plan.effective < window[1]:
                raise Refused("%s may not return to the active list before %s (rules library R6)" % (
                    name, tx.long_date(window[1])))
        if move["to_list"] == "active":
            avail = move.get("availability")
            if not isinstance(avail, dict) or not str(avail.get("text", "")).strip() or not avail.get("source"):
                raise Refused("%s joins the 53: the medical staff's communication on his availability (his physical or "
                              "clearance), with its source, comes first" % name)
            if not (root / avail["source"]).is_file():
                raise Refused("%s's medical communication cites %s, which is not on file" % (name, avail["source"]))
        if kind in ("signed", "practice_squad") and move.get("via") == "former_player":
            dep = [r for r in data["departures"] if r["name"] == name]
            if not dep or not str(dep[-1].get("disposition") or "").lower().startswith("unplaced"):
                raise Refused("%s is not a former Jacksonville player unplaced under the league method" % name)
        if kind == "signed" and move.get("via") == "section_4":
            uid = _uid(plan, name)
            fa = {r["uid"] for r in tx.free_agents(season, plan.at.date(), root)}
            if uid not in fa:
                raise Refused("%s was not a free agent on the league record when the offer was made; a player on "
                              "waivers is claimed, and a player under contract elsewhere cannot be signed" % name)


def counts_after(plan):
    data = copy.deepcopy(plan.data)
    for move in plan.record["moves"]:
        row = next((r for r in data["players"] if r["name"] == move["player"]), None)
        if row is None:
            data["players"].append({"name": move["player"], "list": move["to_list"]})
        else:
            row["list"] = move["to_list"]
    active = sum(1 for r in data["players"] if r["list"] == "active")
    squad = sum(1 for r in data["players"] if r["list"] == "practice_squad")
    if active > plan.data["active_limit"]:
        raise Refused("the moves leave %d players on the active roster, above the %d allowed" % (
            active, plan.data["active_limit"]))
    if squad > plan.data["practice_squad_places"]:
        raise Refused("the moves leave %d players on the practice squad, above the %d allowed" % (
            squad, plan.data["practice_squad_places"]))


# ------------------------------------------------------------------ the writes
def position_of(move, plan):
    if move.get("position"):
        return tx.ROSTER_POSITION.get(move["position"], move["position"])
    row = next((r for r in plan.data["players"] if r["name"] == move["player"]), None)
    if row is not None:
        return row["position"]
    dep = [r for r in plan.data["departures"] if r["name"] == move["player"]]
    if dep:
        return dep[-1]["position"]
    raise Refused("%s's position is not on the record" % move["player"])


def status_for(move, row, day):
    when = tx.long_date(day)
    kind = move["kind"]
    if kind == "reserve":
        return "%s (placed %s)" % (tx.RESERVE_STATUS[move.get("designation") or "ordinary"], when)
    if kind == "promoted":
        inner = row["status"].split("(", 1)[1].rstrip(")") + "; " if "(" in row["status"] else ""
        return "Active 53 (%spromoted from the practice squad %s)" % (inner, when)
    if kind == "reinstated":
        return "Active 53 (returned from reserve/injured %s)" % when
    if kind == "practice_squad":
        return "Practice squad (signed %s)" % when
    return "Active 53 (%s %s)" % ("claimed" if kind == "claimed" else "signed", when)


def new_roster(plan, page_rel):
    data = copy.deepcopy(plan.data)
    day = plan.effective
    for move in plan.record["moves"]:
        name = move["player"]
        row = next((r for r in data["players"] if r["name"] == name), None)
        position = position_of(move, plan)
        status = status_for(move, row, day)
        if row is None:
            row = {"name": name, "position": position, "list": "active", "group": tx.GROUP_WORDS[position],
                   "status": status, "availability": None, "sources": {}}
            data["players"].append(row)
        row["list"] = move["to_list"]
        row["status"] = status
        row["group"] = tx.GROUP_WORDS[row["position"]] if move["to_list"] == "active" else None
        row.setdefault("sources", {})["status"] = page_rel
        if move["to_list"] == "active":
            row["availability"] = move["availability"]["text"]
            row["sources"]["availability"] = move["availability"]["source"]
        elif move["to_list"] == "practice_squad":
            row["availability"] = None
            row["sources"].pop("availability", None)
    data["as_of"] = {"date": day.isoformat(), "event": "after the roster moves of %s" % tx.long_date(day)}
    problems = roster_record.errors(data)
    if problems:
        raise Refused("the roster record would be invalid: %s" % "; ".join(problems))
    return data


def contract_entries(plan, page_rel):
    """[(player id, entry, new record fields or None, contract words)] the moves add to the contract
    records, each computed by the stored in-season terms method or marked unresolved."""
    root, season = plan.root, plan.season
    records = player_contracts.load_all(root)
    by_name = {r["name"]: rid for rid, r in records.items()}
    out = []
    day = plan.effective
    iso = day.isoformat()
    for move in plan.record["moves"]:
        name = move["player"]
        rid = by_name.get(name) or player_id(plan, name)
        record = records.get(rid)
        position = position_of(move, plan)
        fields = None
        if record is None:
            cap = tx.CAP_POSITION.get(position)
            if cap is None:
                raise Refused("%s's cap accounting group is not on file for the position %s" % (name, position))
            fields = {"position": cap, "roster_position": position}
        kind = move["kind"]
        if kind in ("reserve", "reinstated"):
            words = ("Unchanged: the contract continues on reserve/injured" if kind == "reserve" else
                     "Unchanged: the contract continues")
            out.append((rid, {"kind": "register", "date": iso, "source": page_rel,
                              "status": "Under contract; %s %s" % (
                                  "reserve/injured from" if kind == "reserve" else "back on the active roster",
                                  tx.long_date(day))}, fields, words))
            continue
        if kind == "promoted":
            current = player_contracts.contract_on(record, None, root) if record else None
            if current is None or current["kind"] != "practice_squad":
                raise Refused("%s holds no practice-squad contract to end" % name)
            start = tx._day(current["start"]["date"])
            weeks = sum(1 for _, paid in player_contracts.pay_weeks(season, root) if start <= paid < day)
            entry = {"kind": "contract_signed", "date": iso, "source": page_rel, "contract": "%s_%s" % (rid, iso),
                     "club": player_contracts.CLUB, "method": {"name": "promotion", "squad_weeks": weeks}}
            below = player_contracts.minimum_problem(record, entry, root)
            if below:
                raise Refused("%s cannot be promoted on the in-season terms method: %s" % (name, below))
            years = player_contracts.computed_years(entry, root)
            last = max(int(y) for y in years)
            entry.update(through=last, years=years, type="Promotion structure (re-signed on promotion from the "
                                                         "practice squad)",
                         signed_text=tx.long_date(day), term_text="%d / %d" % (len(years), last),
                         value_text="$%s" % "{:,}".format(sum(r["cap"] for r in years.values())),
                         bonus={"text": "$0; $0; 0", "amount": 0}, guarantee_text="$0",
                         guarantee_basis="Branch contract",
                         basis={"text": "The in-season terms method: the promotion structure, its first year earned for "
                                        "the pay weeks left; a labelled reconstruction",
                                "source": page_rel},
                         exposure_text="$0 gross exposure", sources=[page_rel],
                         notes="Promoted from the practice squad %s on the in-season promotion structure; the "
                               "first year is earned for the pay weeks left, a labelled reconstruction" % tx.long_date(day))
            out.append((rid, {"kind": "contract_ended", "date": iso, "source": page_rel,
                              "contract": current["contract"], "how": "promoted",
                              "text": "Promoted from the practice squad %s" % tx.long_date(day)}, None, None))
            out.append((rid, entry, None, "%s; %s in %d" % (entry["term_text"].replace(" / ", " years, through "),
                                                           "$" + "{:,}".format(years[str(season)]["cap"]), season)))
            continue
        if kind == "signed":
            terms = move.get("contract") if move.get("via") == "former_player" else move.get("offer")
            if not isinstance(terms, dict) or type(terms.get("credited_seasons")) is not int or not terms.get("source"):
                raise Refused("%s's credited seasons, with their source, are needed for the in-season minimum" % name)
            if not (root / str(terms["source"]).split("#")[0]).is_file():
                raise Refused("%s's credited seasons cite %s, which is not on file" % (name, terms["source"]))
            entry = {"kind": "contract_signed", "date": iso, "source": page_rel, "contract": "%s_%s" % (rid, iso),
                     "club": player_contracts.CLUB,
                     "method": {"name": "in_season_minimum", "credited_seasons": terms["credited_seasons"]}}
            below = player_contracts.minimum_problem(record, entry, root) if record else None
            if below:
                raise Refused("%s cannot be signed on the in-season terms method: %s" % (name, below))
            years = player_contracts.computed_years(entry, root)
            rate = player_contracts.minimum_salary(season, terms["credited_seasons"], root)
            entry.update(through=season, years=years, type="Veteran minimum (in-season signing, %s)" % tx.long_date(day),
                         signed_text=tx.long_date(day), term_text="1 / %d" % season,
                         value_text="$%s earned and charged (the $%s rate for the pay weeks left)" % (
                             "{:,}".format(years[str(season)]["cap"]), "{:,}".format(rate)),
                         bonus={"text": "$0; $0; 0", "amount": 0}, guarantee_text="$0",
                         guarantee_basis="Branch contract",
                         basis={"text": "The in-season terms method: the minimum for his credited seasons, earned for the "
                                        "pay weeks left; a labelled reconstruction",
                                "source": page_rel},
                         exposure_text="$0 gross exposure", sources=[page_rel],
                         notes="Signed %s at the minimum for %d credited seasons, earned for the pay weeks left, a "
                               "labelled reconstruction" % (tx.long_date(day), terms["credited_seasons"]))
            out.append((rid, entry, fields, "One year, %d: the $%s minimum for %d credited seasons, $%s earned and "
                                            "charged for the pay weeks left" % (
                                                season, "{:,}".format(rate), terms["credited_seasons"],
                                                "{:,}".format(years[str(season)]["cap"]))))
            continue
        if kind == "practice_squad":
            rate = player_contracts.practice_squad_rate(season, root)
            weeks = len(player_contracts.pay_weeks(season, root))
            entry = {"kind": "practice_squad", "date": iso, "source": page_rel, "contract": "%s_%s" % (rid, iso),
                     "club": player_contracts.CLUB, "weekly_rate": rate, "weeks": weeks,
                     "type": "Practice squad (weekly)", "signed_text": tx.long_date(day),
                     "term_text": "Weekly, through the %d season" % season,
                     "value_text": "$%s a week, the %d practice-squad minimum, for the weeks on the squad" % (
                         "{:,}".format(rate), season),
                     "bonus": {"text": "$0; $0; 0", "amount": 0}, "guarantee_text": "$0; a practice-squad contract "
                                                                                   "pays only for weeks on the squad",
                     "guarantee_basis": "Branch contract",
                     "basis": {"text": "The in-season terms method: the practice-squad weekly rate", "source": page_rel},
                     "exposure_text": "$0 gross exposure", "sources": [page_rel],
                     "notes": "Signed to the practice squad %s at the season's weekly rate; the season total is a "
                              "working estimate, charged only for the weeks on the squad" % tx.long_date(day)}
            out.append((rid, entry, fields, "Practice squad: $%s a week for the weeks on the squad" % "{:,}".format(rate)))
            continue
        if kind == "claimed":
            entry = {"kind": "contract_signed", "date": iso, "source": page_rel, "contract": "%s_%s" % (rid, iso),
                     "club": player_contracts.CLUB, "through": None, "years": None,
                     "type": "Claimed on waivers (the contract he was claimed on continues)",
                     "signed_text": tx.long_date(day), "term_text": "Unresolved",
                     "value_text": "Unresolved: the terms of the contract he was claimed on are not on the record",
                     "guarantee_text": "Unresolved", "basis": None,
                     "exposure_text": "Unresolved: the claimed contract's terms are not on the record",
                     "sources": [page_rel],
                     "notes": "Claimed on waivers %s; the contract he was claimed on continues, and its terms are "
                              "not on the record (unresolved, never filled)" % tx.long_date(day)}
            out.append((rid, entry, fields, "The contract he was claimed on continues; its terms are unresolved on the "
                                            "record"))
    return out


def add_entries(root, rid, entries, fields=None):
    """A player's contract entries of one move, through the contract records' own writer and checks
    (runtime/player_contracts.add_entries: one entry, or a promotion's pair in one write)."""
    try:
        return player_contracts.add_entries(root, rid, entries, fields)
    except ValueError as exc:
        raise Refused(str(exc)) from exc


def player_id(plan, name):
    """The permanent record id of ``name`` (an existing record, or the id a new one takes)."""
    records = people.load_all(plan.root)
    found = [rid for rid, r in records.items() if r["name"] == name]
    if len(found) == 1:
        return found[0]
    if len(found) > 1:
        uid = _uid(plan, name)
        match = [rid for rid in found if records[rid].get("gsis_id") == uid]
        if len(match) == 1:
            return match[0]
        raise Refused("%s matches more than one permanent player record" % name)
    record = people.new_record(name, _uid(plan, name))
    return people.record_id(record, set(records))


def player_records(plan, page_rel):
    """{record id: record} of the permanent player records with each move's dated transaction."""
    root = plan.root
    records = people.load_all(root)
    out = {}
    texts = {"reserve": "Placed on reserve/injured by Jacksonville", "promoted": "Promoted from the practice squad "
             "to the active roster by Jacksonville", "reinstated": "Returned from reserve/injured to the active roster",
             "signed": "Signed to the active roster by Jacksonville", "claimed": "Claimed on waivers by Jacksonville",
             "practice_squad": "Signed to the Jacksonville practice squad"}
    for move in plan.record["moves"]:
        name = move["player"]
        rid = player_id(plan, name)
        record = copy.deepcopy(records.get(rid) or out.get(rid) or people.new_record(name, _uid(plan, name)))
        text = texts[move["kind"]]
        if move["kind"] == "reserve" and move.get("designation") == "designated":
            text = "Placed on reserve/injured, designated for return, by Jacksonville"
        if move["kind"] == "claimed" and move.get("waived_by"):
            text = "Claimed on waivers from the %s by Jacksonville" % move["waived_by"]
        record["transactions"] = sorted(record["transactions"] + [
            {"date": plan.effective.isoformat(), "kind": move["kind"], "text": text, "source": page_rel}],
            key=people.sort_key)
        out[rid] = record
    return out


def chart_change(plan):
    """(leaving, joining) for the chart writers: players off the 53 and players joining it."""
    leaving = [m["player"] for m in plan.record["moves"] if m["from_list"] == "active"]
    joining = {}
    chart = json.loads(plan.paths.depth_chart.read_text(encoding="utf-8"))
    used = set((chart.get("positions") or {}).values())
    for move in plan.record["moves"]:
        if move["to_list"] != "active":
            continue
        position = position_of(move, plan)
        if position not in used:
            records = player_contracts.load_all(plan.root)
            cap = next((r["position"] for r in records.values() if r["name"] == move["player"]), None)
            position = {"OG": "G"}.get(cap, cap)
            if position not in used:
                raise Refused("%s's position on the depth chart is not one the chart uses; Stone names it on My "
                              "Responses" % move["player"])
        joining[move["player"]] = (tx.kernel_group(position), position)
    return leaving, joining


def write_signings(plan, applied, page_rel):
    """The signing records of players signed from outside the club and their lines in the signings page."""
    root = plan.root
    out = {}
    lines = []
    for move in applied["moves"]:
        if move["kind"] not in ("signed", "practice_squad"):
            continue
        rel = applied["applied"]["signings"][move["player"]]
        path = root / rel
        text = tx.signing_text(applied, move, root)
        problems = text_errors(rel, text, root)
        if problems:
            raise Refused("the signing record would not be in football words: %s" % "; ".join(problems))
        out[path] = text
        lines.append("- %s: [%s signed](%s), %s." % (tx.long_date(plan.effective), move["player"], path.name,
                                                    "a former Jacksonville player" if move.get("via") == "former_player"
                                                    else "after the market draw under the league method"))
    signings = plan.paths.record("free_agency") / "signings.md"
    if lines:
        text = signings.read_text(encoding="utf-8")
        if "\n## In-season signings\n" not in text:
            text = text.rstrip("\n") + "\n\n## In-season signings\n\n"
        text = text + "\n".join(lines) + "\n"
        problems = text_errors(tx._rel(root, signings), text, root)
        if problems:
            raise Refused("the signings page would not be in football words: %s" % "; ".join(problems))
        out[signings] = text
    return out


def apply(root, season, tid, client=None, check=False, rebuild=True, out=print):
    """Apply transaction ``tid``; returns the outcome ("applied", "claim_lost", "pursuit_lost")."""
    root = Path(root).resolve()
    try:
        open_events._refuse_if_paused(root)
    except open_events.Refused as exc:
        raise Refused(str(exc))
    record = tx.get(season, tid, root)
    if record is None:
        raise Refused("no transaction %s is recorded" % tid)
    plan = Plan(root, season, record)
    plan.at_effective = plan.at
    check_record(plan)
    mechanism = None
    for move in plan.record["moves"]:
        if move.get("via") == "waiver_claim":
            mechanism = ("award", decide_claim(plan, move))
        elif move.get("via") == "section_4":
            mechanism = ("draw", decide_pursuit(plan, move, client, check))
    if not open_events.master_clock(root).allows(plan.at_effective):
        raise Refused("the moves take effect at %s, after the master date/time" % plan.at_effective.isoformat())
    if plan.outcome != "applied":
        entry, fields = plan.lost
        if check:
            out(entry["what"])
            return plan.outcome
        saved = snapshot([tx.record_path(season, tid, root), open_events.path_of(plan.event, root)])
        try:
            open_events.add_process(season, plan.event["id"], entry, root)
            updated = dict(plan.record, status=plan.outcome, **fields)
            tx.write(updated, root)
        except Exception:
            restore(saved)
            raise
        out(entry["what"])
        return plan.outcome
    check_legal(plan)
    counts_after(plan)
    page = tx.result_name(season, plan.event, plan.effective, root)
    page_rel = tx._rel(root, page)
    roster_data = new_roster(plan, page_rel)
    entries = contract_entries(plan, page_rel)
    words = {}
    for rid, entry, fields, contract_words in entries:
        name = next(m["player"] for m in plan.record["moves"]
                    if player_id(plan, m["player"]) == rid)
        if contract_words:
            words[name] = contract_words
            plan.changes.setdefault(name, {})["contract"] = contract_words
    for move in plan.record["moves"]:
        plan.changes.setdefault(move["player"], {})["effective"] = plan.effective.isoformat()
    people_records = player_records(plan, page_rel)
    leaving, joining = chart_change(plan)
    signing_pages = {}
    for move in plan.record["moves"]:
        if move["kind"] in ("signed", "practice_squad"):
            signing_pages[move["player"]] = tx._rel(root, plan.paths.signing_record(player_id(plan, move["player"]),
                                                                                  plan.effective))
    applied = dict(plan.record, status="applied",
                   applied={"at": open_events.iso(plan.at_effective), "date": plan.effective.isoformat(),
                            "page": page_rel, "changes": plan.changes, "signings": signing_pages})
    if mechanism and mechanism[1] is not None:
        applied[mechanism[0]] = mechanism[1]
    text = tx.page_text(applied, plan.event, root)
    problems = text_errors(page_rel, text, root)
    if problems:
        raise Refused("the Transaction page would not be in football words: %s" % "; ".join(problems))
    signing_files = write_signings(plan, applied, page_rel)
    if check:
        for note in plan.notes:
            out(note)
        out("TRANSACTION READY: %s; nothing written" % page.name)
        return "ready"
    # Everything written here, or nothing.
    from scripts.apply_game_plan import log_change, write_charts
    from scripts.change_game_day import open_item, roster_move
    saved = snapshot([root / decision_queue.QUEUE], [root / "career", root / "data", root / "state"])
    try:
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(text, encoding="utf-8")
        for path, body in signing_files.items():
            path.write_text(body, encoding="utf-8")
        plan.paths.roster.write_text(json.dumps(roster_data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        folder = root / people.PLAYER_RECORDS
        for rid, prec in people_records.items():
            (folder / ("%s.json" % rid)).write_text(people.dump(prec), encoding="utf-8")
        for rid in dict.fromkeys(rid for rid, _, _, _ in entries):
            add_entries(root, rid, [e for r, e, _, _ in entries if r == rid],
                        next((f for r, _, f, _ in entries if r == rid and f), None))
        write_charts(plan.paths, lambda chart, working: roster_move(chart, leaving, joining))
        log_change(plan.paths, {
            "date": tx.long_date(plan.effective), "recorded": plan.effective.isoformat(),
            "event": "Roster moves of %s: %s" % (tx.long_date(plan.effective), plan.event["subject"]),
            "change": "; ".join(["%s off the chart (%s)" % (n, "reserve/injured") for n in leaving] +
                                ["%s placed at the bottom of the %s group" % (n, tx.KERNEL_WORDS.get(g, g).lower())
                                 for n, (g, _) in joining.items()]) +
                      ". No order change by Stone; a role or a place the move leaves is his to set.",
            "sources": [{"label": "transaction", "page": page_rel}]})
        tx.write(applied, root)
        queue = decision_queue.load(root)
        for item in queue["items"]:
            if item.get("event") == plan.event["id"] and item.get("owner") != plan.job.get("holder") \
                    and item.get("status") == "OPEN":
                item["status"] = "RESOLVED"
                item["resolution"] = {"date": plan.effective.isoformat(), "by": "organization",
                                      "record": {"path": page_rel},
                                      "summary": "The roster move is applied: %s." % "; ".join(
                                          "%s %s" % (m["player"], tx.move_words(m)) for m in plan.record["moves"])}
        decision_queue.save(root, queue)
        resolve_result(root, season, plan.event["id"], plan.record["decided_by"],
                       open_events.iso(plan.at_effective), plan.record["basis"]["text"], plan.record["criteria"],
                       page_rel)
        game = tx.next_game(season, root)
        if game is not None:
            item, message = open_item(root, season, int(game["week"]))
            out(message)
        if rebuild:
            from scripts import rebuild_pages
            _, problems = rebuild_pages.rebuild(root, season)
            if problems:
                raise Refused("a page could not be rebuilt after the roster moves: %s" % "; ".join(problems))
    except Exception:
        restore(saved)
        raise
    out("TRANSACTION APPLIED: %s" % page.name)
    return "applied"


def place(root, season, path):
    """Check a decision record and place it in the transaction store."""
    root = Path(root).resolve()
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    if record.get("season") != int(season):
        raise Refused("the decision names season %r" % record.get("season"))
    if tx.get(season, record.get("id"), root) is not None:
        raise Refused("transaction %s is already recorded" % record.get("id"))
    refuse_if(tx.record_errors(record, root))
    if record.get("status") != "decided":
        raise Refused("a new decision is recorded as decided")
    return tx.write(record, root)


def main(argv=None, root=ROOT, client=None, out=print):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("id", nargs="?")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--file")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = Path(root).resolve()
    try:
        if args.file:
            if args.id:
                raise Refused("--file takes no id")
            if args.check:
                record = json.loads(Path(args.file).read_text(encoding="utf-8"))
                refuse_if(tx.record_errors(record, root))
                out("DECISION READY: %s" % record["id"])
                return 0
            out("DECISION RECORDED: %s" % place(root, args.season, args.file).name)
            return 0
        if not args.id:
            raise Refused("name the transaction: apply_transaction.py ID --season YEAR")
        apply(root, args.season, args.id, client, args.check, out=out)
        return 0
    except (Refused, open_events.Refused, ValueError) as exc:
        out("TRANSACTION REFUSED: %s" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
