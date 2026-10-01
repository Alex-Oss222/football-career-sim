#!/usr/bin/env python3
"""The 2014 Pro Bowl: need players, draft and game.

  python scripts/pro_bowl.py draft            # dry run: both first-pick outcomes
  python scripts/pro_bowl.py draft --close    # coin toss, draft and need players
  python scripts/pro_bowl.py game             # dry run: the two TeamInputs
  python scripts/pro_bowl.py game --close     # play the game (private service)
  python scripts/pro_bowl.py render           # rewrite career/2013/pro_bowl/README.md

Method: career/2013/pro_bowl/method.json, fixed before any draw. The game is
an exhibition: its receipt stays in career/2013/pro_bowl/ and counts toward no
statistic, standing, award or band.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.packets import canonical
from runtime.usage import group

DIR = ROOT / "career/2013/pro_bowl"
METHOD = DIR / "method.json"
DRAFT = DIR / "draft.json"
GAME = DIR / "game.json"
RECEIPT = DIR / "receipt.json"
PAGE = DIR / "README.md"
HONOURS = ROOT / "career/2013/awards/season_honours_results.json"
TEAMS = ("Team One", "Team Two")
EVENT_ID = "2013-pro-bowl"
UNIT = {"QB": "offense", "RB": "offense", "FB": "offense", "WR": "offense", "TE": "offense", "OL": "offense",
        "DL": "defense", "LB": "defense", "DB": "defense", "K": "special_teams", "P": "special_teams",
        "LS": "special_teams"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def playing(honours):
    """{slot: [player row, ...]} for the selections who play, by vote rank."""
    out = {}
    for slot, entries in honours["pro_bowl"]["selections"].items():
        rows = []
        for entry in entries:
            player = entry["replaced_by"] if entry["reason"] else entry
            if player:
                rows.append({k: player[k] for k in ("player", "team", "position", "score")})
        out[slot] = sorted(rows, key=lambda r: (-r["score"], r["player"]))
    return out


def captain_groups(honours, pool):
    caps = honours["pro_bowl"]["captains"]
    slot_of = {row["player"]: slot for slot, rows in pool.items() for row in rows}

    def seat(entry):
        return {"player": entry["player"], "team": entry["team"], "slot": slot_of[entry["player"]]}
    return ([seat(caps["offense"][0]), seat(caps["defense"][1])],
            [seat(caps["defense"][0]), seat(caps["offense"][1])])


def run_draft(m, honours, first):
    """Deterministic draft given which team (0 or 1) picks first."""
    pool = playing(honours)
    quota = {slot: n for day in ("tuesday", "wednesday") for slot, n in m["draft"][day]}
    groups = captain_groups(honours, pool)
    rosters = {team: [] for team in TEAMS}
    taken = set()
    for team, members in zip(TEAMS, groups):
        for c in members:
            row = next(r for r in pool[c["slot"]] if r["player"] == c["player"])
            rosters[team].append(dict(row, slot=c["slot"], how="captain"))
            taken.add(c["player"])
    log = []
    for day in ("tuesday", "wednesday"):
        turn = first
        for slot, n in m["draft"][day]:
            left = [r for r in pool[slot] if r["player"] not in taken]
            while left:
                counts = [sum(1 for r in rosters[t] if r["slot"] == slot) for t in TEAMS]
                full = [counts[i] >= n for i in (0, 1)]
                if all(full):
                    raise ValueError("more %s players than both quotas" % slot)
                if full[0] or full[1]:
                    team = TEAMS[1 if full[0] else 0]
                    how = "assigned"
                else:
                    team, how = TEAMS[turn], "pick"
                    turn = 1 - turn
                row = left.pop(0)
                taken.add(row["player"])
                rosters[team].append(dict(row, slot=slot, how=how))
                log.append({"day": day, "slot": slot, "team": team, "player": row["player"],
                            "club": row["team"], "how": how})
    for team in TEAMS:
        for slot, n in quota.items():
            have = sum(1 for r in rosters[team] if r["slot"] == slot)
            if have != n:
                raise ValueError("%s has %d at %s, quota %d" % (team, have, slot, n))
    return rosters, log


def need_player(club):
    """The long snapper in the club's latest closed receipt."""
    from scripts.render_season_stats import load_receipts
    receipts = list(load_receipts(ROOT / "career/2013/stats/game_receipts")) + list(
        load_receipts(ROOT / "career/2013/stats/postseason_receipts"))
    latest = max((r for r in receipts if club in r["team_stats"]), key=lambda r: int(r["week"]))
    snappers = [n for n, p in latest["team_stats"][club]["players"].items() if p.get("position") == "LS"]
    if len(snappers) != 1:
        raise ValueError("%s: %d long snappers in its latest receipt" % (club, len(snappers)))
    return {"player": snappers[0], "team": club, "position": "LS", "slot": "LS", "how": "need player"}


def bits(result_ref, pkt):
    from runtime.game_runner import _entropy_from_ref
    digest = hashlib.sha256(_entropy_from_ref(result_ref) + canonical(pkt)).digest()
    return digest[0] & 1, (digest[0] >> 1) & 1


def team_input(team, roster):
    from runtime.kernel import TeamInput
    from runtime.player_evidence import PlayerInput
    players, rank = [], {}
    for row in sorted(roster, key=lambda r: (-r.get("score", 0), r["player"])):
        key = row["slot"]
        rank[key] = rank.get(key, 0) + 1
        roles = {"RS": ("kick_return", "punt_return"), "K": ("placekicker",), "P": ("punt",),
                 "LS": ("long_snap",)}.get(key, ())
        position = row["position"] if key not in ("K", "P", "LS") else key
        players.append(PlayerInput(row["player"], position, unit=UNIT.get(group(position), "offense"),
                                   roles=roles, depth=rank[key]))
    return TeamInput(team, tuple(p.player_id for p in players), roster=tuple(players))


def draft(args):
    m, honours = load(METHOD), load(HONOURS)
    if not args.close:
        for first in (0, 1):
            rosters, _ = run_draft(m, honours, first)
            print("If %s picks first:" % TEAMS[first])
            for team in TEAMS:
                print("  %s (%d): %s" % (team, len(rosters[team]), ", ".join(r["player"] for r in rosters[team][:8]) + ", ..."))
        return 0
    if DRAFT.exists():
        print("PRO BOWL DRAFT: already drawn")
        return 1
    from runtime.private_client import Client
    client = Client()
    snapshot = client.current_snapshot()
    coaches = honours["pro_bowl"]["coaches"]
    pkt = {"procedure": m["procedure"], "event_id": "2013-pro-bowl-draft-%s" % m["procedure_tag"],
           "snapshot": snapshot, "teams": list(TEAMS),
           "captain_groups": [[c["player"] for c in g] for g in captain_groups(honours, playing(honours))],
           "coaches": coaches,
           "method_sha256": hashlib.sha256(METHOD.read_bytes()).hexdigest(),
           "honours_sha256": hashlib.sha256(HONOURS.read_bytes()).hexdigest()}
    ref = client.close_event(pkt)
    first, pairing = bits(ref, pkt)
    rosters, log = run_draft(m, honours, first)
    staffs = [coaches["AFC"], coaches["NFC"]]
    if pairing:
        staffs.reverse()
    for team, staff in zip(TEAMS, staffs):
        rosters[team].append(need_player(staff["club"]))
    record = {"procedure": m["procedure"], "ledger_entry": args.entry, "snapshot": snapshot,
              "event_id": pkt["event_id"], "packet_sha256": hashlib.sha256(canonical(pkt)).hexdigest(),
              "result_ref": ref, "first_pick": TEAMS[first],
              "coaches": {team: staff for team, staff in zip(TEAMS, staffs)},
              "rosters": rosters, "picks": log}
    DRAFT.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print("First pick: %s; coaches %s" % (TEAMS[first], record["coaches"]))
    return 0


def game(args):
    record = load(DRAFT)
    home, away = (team_input(team, record["rosters"][team]) for team in TEAMS)
    if not args.close:
        from runtime.usage import lineup_errors
        from runtime.player_evidence import normalize_players
        for t in (home, away):
            print(t.team_id, len(t.roster), lineup_errors(normalize_players(t)) or "legal unit")
        return 0
    if GAME.exists():
        print("PRO BOWL: already played")
        return 1
    from runtime.game_runner import run_game
    from runtime.private_client import Client
    from runtime.statbook import make_receipt
    snapshot = hashlib.sha256((ROOT / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
    client = Client(snapshot=snapshot)
    result = run_game(home, away, event_id=EVENT_ID, snapshot=snapshot, client=client,
                      venue="neutral", game_type="pro_bowl")
    result = json.loads(json.dumps(result, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o)))
    receipt = make_receipt(result, week=20, matchup="%s at %s" % (TEAMS[1], TEAMS[0]), detail="full")
    RECEIPT.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    GAME.write_text(json.dumps({"event_id": EVENT_ID, "ledger_entry": args.entry, "snapshot": snapshot,
                                "kernel_version": result["kernel_version"],
                                "final_score": result["final_score"],
                                "receipt_sha256": hashlib.sha256(RECEIPT.read_bytes()).hexdigest()},
                               indent=1) + "\n", encoding="utf-8")
    print(result["final_score"])
    return 0


def render(_args):
    from scripts.render_box_score import comparison, team_box
    from runtime.events import preserve_event_comments
    m, record = load(METHOD), load(DRAFT)
    lines = ["# 2014 Pro Bowl (Aloha Stadium, January 26, 2014)", "",
             "Generated by `scripts/pro_bowl.py render`. Method: [method.json](method.json). Drawn retroactively "
             "on the branch date of February 2, 2014. An exhibition: it changes no standing, statistic, "
             "award or roster fact.", "", "## Draft (January 21-22)", "",
             "The private service's coin toss gave **%s** the first pick on both days." % record["first_pick"], ""]
    for team in TEAMS:
        staff = record["coaches"][team]
        roster = record["rosters"][team]
        caps = [r["player"] for r in roster if r["how"] == "captain"]
        need = next(r for r in roster if r["how"] == "need player")
        lines += ["### %s" % team, "",
                  "Coaches: %s's %s staff. Active captains: %s. Need player: %s (%s long snapper, appointed by the coaches)." % (
                      staff["head_coach"], staff["club"], " and ".join(caps), need["player"], need["team"]), "",
                  "| Position | Players |", "|---|---|"]
        slots = [s for day in ("tuesday", "wednesday") for s, _ in m["draft"][day]]
        for slot in sorted(set(slots), key=slots.index):
            names = ["%s, %s%s" % (r["player"], r["team"], " (captain)" if r["how"] == "captain" else
                                   " (assigned)" if r["how"] == "assigned" else "")
                     for r in roster if r["slot"] == slot]
            lines.append("| %s | %s |" % (slot, "; ".join(names)))
        lines.append("")
    lines += ["Picks alternate straight from the first-pick team each day, the highest vote-rank player at the "
              "segment's position going first; a team with its quota filled has the rest assigned to it. Each "
              "team has 42 voted players and its need player (43 dress): the special teamer slots are not generated.", ""]
    if RECEIPT.exists():
        receipt = load(RECEIPT)
        score = receipt["final_score"]
        lines += ["## Game (January 26)", "",
                  "**%s %d, %s %d.** No kickoffs; the ball at the 25 to start every quarter and after every "
                  "score; possession alternates at each quarter. Drives are real 2012 drives; the exhibition's "
                  "play-level rules are not modelled (method.json)." % (TEAMS[0], score[TEAMS[0]], TEAMS[1], score[TEAMS[1]]), ""]
        lines += comparison(receipt, list(TEAMS))
        for team in TEAMS:
            lines += team_box(team, receipt["team_stats"][team]["players"])
    generated = "\n".join(lines).rstrip() + "\n"
    previous = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ''
    PAGE.write_text(preserve_event_comments(generated, previous), encoding="utf-8")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("draft", "game", "render"))
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--entry", default="")
    args = parser.parse_args()
    return {"draft": draft, "game": game, "render": render}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
