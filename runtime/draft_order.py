"""The 2014 draft's selection order, from closed branch receipts only.

Rules (library/2014_league_calendar_and_financial_rules.md, section D):
- the 20 non-playoff clubs select 1-20 in order of regular-season winning
  percentage, lowest first;
- the 12 playoff clubs select 21-32 by round of elimination: Wild Card losers
  21-24, Divisional losers 25-28, conference-championship losers 29-30, the
  Super Bowl loser 31 and the winner 32; within a group, lowest winning
  percentage first;
- ties in winning percentage go to the club with the lower strength of
  schedule. A tie that survives strength of schedule needs the division or
  conference tiebreakers and then a coin flip. A validated recorded website
  draw resolves its named pair; no new randomness is generated here.

Later rounds rotate equal-record segments within their elimination group.
Any still-unresolved coin flip remains a set of possible slots. Ownership is joined by (draft year, round, original club), so a
rotation cannot move a traded asset to the wrong owner.
"""
import json
import hashlib
from itertools import groupby
from pathlib import Path

from .league import TEAMS
from .standings import Season, games_from_receipts
from . import postseason

ROOT = Path(__file__).resolve().parents[1]
GROUPS = (("non-playoff", 1), ("wild_card", 21), ("divisional", 25),
          ("conference", 29), ("super_bowl_loser", 31), ("champion", 32))
OWNERSHIP = ROOT / "career/2014/draft/pick_ownership.json"
COIN_FLIP = ROOT / "career/2014/draft/coin_flip.json"
_RECORDED_DRAW = object()


def _load(directory):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.json"))]


def elimination(post_receipts):
    """{club: group} for the 12 playoff clubs, from the closed postseason receipts."""
    loser_group = {18: "wild_card", 19: "divisional", 20: "conference", 21: "super_bowl_loser"}
    out = {}
    for receipt in post_receipts:
        week = int(receipt["week"])
        won = postseason.winner(receipt)
        lost = next(t for t in receipt["final_score"] if t != won)
        out[lost] = loser_group[week]
        if week == 21:
            out[won] = "champion"
    return out


def _break(season, tied, division_ranks):
    """[(club, how)] earliest pick first for clubs tied on percentage and SOS.

    Same division or same conference: the club that would win the standings
    tiebreaker picks later. Clubs in different conferences, or clubs still
    level, await a coin flip that is never simulated here.
    """
    if len(tied) == 1:
        return [(tied[0], None)]
    from .league import DIVISION_OF, conference_of
    if len({conference_of(c) for c in tied}) > 1:
        return [(c, "coin flip pending: " + ", ".join(o for o in tied if o != c)) for c in tied]
    step = "division" if len({DIVISION_OF[c] for c in tied}) == 1 else "conference"
    remaining, later = list(tied), []
    while len(remaining) > 1:
        # Standings has an alphabetical last-resort display fallback. It is
        # not authority to resolve a draft coin flip, including within a
        # conference. Inspect its notes without changing the standings log.
        was_recording, before = season.recording, len(season.notes)
        season.recording = True
        try:
            winner = season.best_of(remaining, "2014 draft order", division_ranks)
            unresolved = any(note["step"] is None for note in season.notes[before:])
        finally:
            season.recording = was_recording
            del season.notes[before:]
        if unresolved:
            pending = [(c, "coin flip pending: " + ", ".join(o for o in remaining if o != c))
                       for c in sorted(remaining)]
            return pending + [(c, step + " tiebreaker") for c in later]
        later.insert(0, winner)
        remaining.remove(winner)
    earliest_first = remaining + later
    return [(c, step + " tiebreaker with " + ", ".join(o for o in tied if o != c)) for c in earliest_first]


def apply_coin_flip(rows, result):
    """Apply a recorded draw only to its actual unresolved pair; never draw here."""
    if not result or result.get("status") != "resolved":
        return rows
    mapping = {"heads": "Green Bay Packers", "tails": "Indianapolis Colts"}
    if (result.get("schema_version") != 1 or result.get("mapping") != mapping
            or result.get("flip_count") != 1 or result.get("rerolls_permitted") is not False
            or result.get("winner_slot") != 14 or result.get("loser_slot") != 15
            or result.get("branch_checkpoint") != "2014-02-02"
            or result.get("result") not in mapping
            or result.get("winner") != mapping.get(result.get("result"))
            or {result.get("winner"), result.get("loser")} != set(mapping.values())
            or not result.get("observed_at") or not result.get("protocol_commit")):
        raise ValueError("invalid recorded draft coin flip")
    screenshot = (ROOT / result["screenshot"]).resolve()
    if (not screenshot.is_relative_to(ROOT)
            or hashlib.sha256(screenshot.read_bytes()).hexdigest() != result["screenshot_sha256"]):
        raise ValueError("draft coin flip evidence checksum mismatch")
    pair = rows[13:15]
    if ({r["club"] for r in pair} != set(mapping.values())
            or any(not (r["tie"] or "").startswith("coin flip pending") for r in pair)
            or len({(r["group"], r["pct"], round(r["sos"], 6)) for r in pair}) != 1):
        raise ValueError("recorded draw does not match this draft tie")
    pair.sort(key=lambda row: row["club"] != result["winner"])
    for slot, row in enumerate(pair, 14):
        row["slot"] = slot
        row["tie"] = f"Recorded website coin flip: {result['result']}; {result['winner']} first (Entry 81)"
    rows[13:15] = pair
    return rows


def order(regular_receipts=None, post_receipts=None, coin_flip=_RECORDED_DRAW):
    """[{slot, club, group, record, pct, sos, tie}] for slots 1-32."""
    regular = _load(postseason.REGULAR_RECEIPTS) if regular_receipts is None else regular_receipts
    post = _load(postseason.POSTSEASON_RECEIPTS) if post_receipts is None else post_receipts
    if sum(1 for r in post if int(r["week"]) == 21) != 1:
        raise ValueError("the Super Bowl has not closed; the draft order is not final")
    season = Season(games_from_receipts(regular))
    sos = season.strength_of_schedule(list(TEAMS))
    group_of = elimination(post)
    for club in TEAMS:
        group_of.setdefault(club, "non-playoff")
    division_ranks = season.division_ranks()
    season.recording = False
    rows = []
    for group, first in GROUPS:
        clubs = [c for c in TEAMS if group_of[c] == group]
        key = lambda c: (season.pct(c), round(sos[c], 6))
        ordered = []
        for value in sorted({key(c) for c in clubs}):
            tied = sorted(c for c in clubs if key(c) == value)
            ordered.extend((club, how) for club, how in _break(season, tied, division_ranks))
        for i, (club, how) in enumerate(ordered):
            line = season.lines[club].overall
            rows.append({"slot": first + i, "club": club, "group": group,
                         "record": line.text(), "pct": season.pct(club), "sos": sos[club],
                         "tie": how})
    assert [r["slot"] for r in rows] == list(range(1, 33))
    if coin_flip is _RECORDED_DRAW:
        coin_flip = json.loads(COIN_FLIP.read_text(encoding="utf-8"))
    return apply_coin_flip(rows, coin_flip)


def load_ownership(path=OWNERSHIP):
    """Load the current register and reject duplicate or malformed assets.

    This is a snapshot, not a transaction log. A later transfer replaces the
    current owner only after its dated ledger event has been recorded.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        raise ValueError("unsupported pick ownership schema")
    if (data.get("audited_year") != 2014 or data.get("as_of") != "2014-02-02"
            or len(data.get("audited_clubs", [])) != 32
            or set(data["audited_clubs"]) != set(TEAMS)):
        raise ValueError("expected complete 2014 ownership audit at the recorded checkpoint")
    seen = set()
    for row in data["transfers"]:
        key = (row["draft_year"], row["round"], row["original_club"])
        if key in seen:
            raise ValueError(f"duplicate pick ownership: {key}")
        if (type(row["draft_year"]) is not int or row["draft_year"] < 2014
                or type(row["round"]) is not int or row["round"] not in range(1, 8)
                or row["original_club"] not in TEAMS or row["owner"] not in TEAMS
                or not row.get("source") or not row.get("basis")
                or not row.get("effective_date") or row["effective_date"] > data["as_of"]):
            raise ValueError(f"invalid pick ownership: {row}")
        seen.add(key)
    claim_ids, encumbered = set(), set()
    for claim in data["conditional_claims"]:
        if (claim["id"] in claim_ids or claim["draft_year"] != 2014
                or claim["original_club"] not in TEAMS or claim["beneficiary"] not in TEAMS
                or claim["original_club"] == claim["beneficiary"]
                or not claim["round_options"]
                or len(set(claim["round_options"])) != len(claim["round_options"])
                or any(type(r) is not int or r not in range(1, 8) for r in claim["round_options"])
                or claim["effective_date"] > data["as_of"]
                or claim.get("max_picks") != 1
                or claim["status"] not in ("awaiting_date", "terms_unverified")
                or not claim.get("source") or not claim.get("basis")):
            raise ValueError("invalid conditional pick claim")
        claim_ids.add(claim["id"])
        for rnd in claim["round_options"]:
            key = (2014, rnd, claim["original_club"])
            if key in seen or key in encumbered:
                raise ValueError(f"overlapping transfer/conditional pick claim: {key}")
            encumbered.add(key)
    return data


def ownership_for(year, rnd, club, register):
    """Return legal allocation plus encumbrance, without booking both alternatives."""
    if type(year) is not int or year < 2014 or type(rnd) is not int or rnd not in range(1, 8) or club not in TEAMS:
        raise ValueError("invalid draft asset")
    for row in register["transfers"]:
        if (row["draft_year"], row["round"], row["original_club"]) == (year, rnd, club):
            return row["owner"], "recorded", row["basis"]
    for claim in register["conditional_claims"]:
        if (year == claim["draft_year"] and club == claim["original_club"]
                and rnd in claim["round_options"]):
            return club, "encumbered", claim["id"] + ": " + claim["basis"]
    if year == register["audited_year"] and club in register["audited_clubs"]:
        return club, "retained", "Audited retained original pick; ledger Entry 81"
    return club, "provisional", "Outside the completed 2014 ownership audit"


def require_clear_ownership(year, rnd, club, register=None):
    """Guard for future trade/selection callers; dates/compensatory gates are separate."""
    owner, status, _ = ownership_for(year, rnd, club, load_ownership() if register is None else register)
    if status not in ("retained", "recorded"):
        raise ValueError(f"pick ownership is {status}: {year} round {rnd}, {club}")
    return owner


def seven_rounds(first_round=None, register=None):
    """224 ordinary assets, with possible round slots and compensatory offsets.

    No real draft order, future season or compensatory award is consulted.
    The recorded branch coin result is applied before rotation. `base_overall_options` excludes compensatory picks; callers
    must retain `compensatory_after_rounds` when displaying rounds 4-7.
    The returned rows are assets, not a finalized executable selection list.
    """
    first = order() if first_round is None else first_round
    register = load_ownership() if register is None else register
    if (len(first) != 32 or {r["club"] for r in first} != set(TEAMS)
            or [r["slot"] for r in first] != list(range(1, 33))):
        raise ValueError("expected one complete, ordered 32-club first round")
    segments = [list(rows) for _, rows in groupby(first, lambda r: (r["group"], r["pct"]))]
    out = []
    for rnd in range(1, 8):
        current = []
        for segment in segments:
            start, size = segment[0]["slot"], len(segment)
            for i, row in enumerate(segment):
                pending = bool(row["tie"] and row["tie"].startswith("coin flip pending"))
                possible = [i]
                if pending:
                    possible = [j for j, candidate in enumerate(segment)
                                if candidate["tie"] and candidate["tie"].startswith("coin flip pending")
                                and round(candidate["sos"], 6) == round(row["sos"], 6)]
                slots = sorted(start + (j - rnd + 1) % size for j in possible)
                owner, status, basis = ownership_for(2014, rnd, row["club"], register)
                current.append({
                    "draft_year": 2014, "round": rnd, "club": row["club"],
                    "slot_options": slots,
                    "base_overall_options": [32 * (rnd - 1) + slot for slot in slots],
                    "compensatory_after_rounds": list(range(3, rnd)),
                    "coin_flip_pending": pending,
                    "owner": owner, "ownership_status": status, "basis": basis,
                    "record": row["record"], "group": row["group"], "sos": row["sos"],
                })
        out.extend(sorted(current, key=lambda r: (r["slot_options"][0], r["club"])))
    return out
