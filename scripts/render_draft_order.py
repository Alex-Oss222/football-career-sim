#!/usr/bin/env python3
"""Render career/2014/draft/draft_order.md from closed receipts (runtime.draft_order).

  python scripts/render_draft_order.py [--check]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "career" / "2014" / "draft" / "draft_order.md"
GROUP_LABEL = {"non-playoff": "Non-playoff", "wild_card": "Lost Wild Card", "divisional": "Lost Divisional",
               "conference": "Lost conference championship", "super_bowl_loser": "Lost Super Bowl",
               "champion": "Won Super Bowl"}


def choices(values):
    return " or ".join(str(value) for value in values)


def overall(row, counts=None):
    if counts is not None:
        return choices([b + sum(counts[str(r)] for r in row["compensatory_after_rounds"])
                        for b in row["base_overall_options"]])
    base = choices(row["base_overall_options"])
    offset = " + ".join(f"C{rnd}" for rnd in row["compensatory_after_rounds"])
    return (f"({base})" if offset and len(row["base_overall_options"]) > 1 else base) + (" + " + offset if offset else "")


def render():
    from runtime.draft_order import load_ownership, seven_rounds
    register = load_ownership()
    # A final order is published only from the recorded branch awards, never
    # from an invented default zero.
    comp = register["compensatory"]
    counts, awards = None, None
    if comp["status"] == "announced":
        awards = json.loads((OUT.parent / comp["awards"]).read_text(encoding="utf-8"))
        counts = comp["round_counts"]
        if awards["round_counts"] != counts or len(awards["picks"]) != 32:
            raise ValueError("compensatory register and awards disagree")
    elif comp["status"] != "pending" or comp["round_counts"] is not None:
        raise ValueError("unknown compensatory status")
    rows = seven_rounds(register=register)
    ov = lambda row: overall(row, counts)
    lines = [
        "# 2014 NFL Draft: all seven rounds (branch)", "",
        ("**As of:** May 11, 2014; ledger Entry 108 (Jacksonville's nine selections recorded). **Draft:** May 8–10, 2014." if register.get("selections_2014") else
         "**As of:** March 24, 2014; ledger Entry 100 (compensatory awards announced). **Draft:** May 8–10, 2014." if awards else
         "**As of:** February 2, 2014; ledger Entry 81. **Draft:** May 8–10, 2014."),
        "**Generated** by `python scripts/render_draft_order.py` from closed branch receipts and [pick_ownership.json](pick_ownership.json). Edit the underlying dated records, then regenerate; do not edit these tables by hand.",
        ("**Coverage:** all **256 selections**: 224 ordinary picks, with original club and recorded owner shown separately, and the 32 branch compensatory picks announced March 24. Overall numbers are exact." if awards else
         "**Coverage:** all **224 ordinary selections**, with original club and recorded owner shown separately. Compensatory selections are still pending; this is not a final 256-pick execution list."),
        "**Rules and sources:** [verification](../../../library/2014_draft_order_verification.md), [league rules §4](../../../library/2014_league_calendar_and_financial_rules.md#4-2014-draft-order-rules-applied-to-the-branchs-2013-season). Clubs tied on winning percentage rotate within their elimination group: first goes to last, the others move up. No real 2014 order or selection is imported.", "",
        "## Jacksonville's current draft capital", "",
        "**Corrected Cousins deal:** Jacksonville received Kirk Cousins **and Washington's original 2014 first**; Washington received Jacksonville's original **2014 and 2015 seconds**. Jacksonville retains its own first. [Completed trade](../../2013/trades/trades.md); [controlling correction, Entry 80](../../2013/ledger.md#entry-80-cousins-trade-and-draft-capital-reconciled).",
        "**Historical exception:** real Washington had previously conveyed its 2014 first to St. Louis. The user expressly corrected this branch asset to Jacksonville after that conflict was disclosed. St. Louis does not also own No. 13; no compensating Rams deal is invented.", "",
        "**Inherited asset restored (Entry 81):** Detroit's original fifth belongs to Jacksonville from the 2012 Mike Thomas trade. [League ownership audit](ownership_audit.md).", "",
        "| Round | Original club | Slot in round | Overall pick | Current owner |",
        "|---:|---|---|---|---|",
    ]
    for row in rows:
        if row["owner"] == "Jacksonville Jaguars" or row["club"] == "Jacksonville Jaguars":
            lines.append(f'| {row["round"]} | {row["club"]} | {choices(row["slot_options"])} | {ov(row)} | **{row["owner"]}** |')
    owned = [r for r in rows if r["owner"] == "Jacksonville Jaguars"]
    owned_labels = "; ".join(f"**{ov(row)}**" for row in owned)
    comp_note = ""
    if awards:
        mine = [p for p in awards["picks"] if p["club"] == "Jacksonville Jaguars"]
        comp_note = (f" Jacksonville received **{len(mine)} compensatory picks**" + (": " + ", ".join(str(p["overall"]) for p in mine) if mine else "") + "; see [Compensatory selections](#compensatory-selections).")
    selections = register.get("selections_2014")
    if selections:
        lines += ["", f"Jacksonville owned **{len(owned)} ordinary 2014 picks**: {owned_labels}.{comp_note}", "",
                  f"**Selections ({selections['status']}):** recorded in [{selections['source'].split('/')[-1]}](../../../{selections['source']}); this table repeats the register only.", "",
                  "| Overall | Round | Original club | Date | Selection | Status |", "|---:|---:|---|---|---|---|"]
        for pick in selections["picks"]:
            lines.append(f'| {pick["overall"]} | {pick["round"]} | {pick["original_club"]} | {pick["date"]} | {pick["player"]}, {pick["position"]}, {pick["school"]} | {pick["status"]} |')
        lines += [""]
    else:
        lines += ["", f"Jacksonville currently owns **{len(owned)} ordinary 2014 picks**: {owned_labels}.{comp_note} No prospect is selected by this inventory.", ""]
    lines += [
              "| Future pick transferred | Current owner | Overall pick | Authority |",
              "|---|---|---|---|"]
    for asset in register["transfers"]:
        if asset["draft_year"] > 2014:
            lines.append(f'| {asset["draft_year"]} Round {asset["round"]}, {asset["original_club"]} original | {asset["owner"]} | Unknown; future branch season | {asset["basis"]} |')
    lines += ["", "## How to read the order" if awards else "## How to read pending fields", "",
              "- **Coin flip resolved:** one RANDOM.ORG draw returned tails at 2026-09-29 01:42:47 UTC. The preassigned mapping gives **Indianapolis 14, Green Bay 15** in Round 1. That result is applied to every later rotation. [Receipt](coin_flip.json); [saved website result](coin_flip_2026-09-29.jpg).",
              ("- **Overall numbers:** each round's compensatory picks follow its ordinary picks, so every later overall number includes the earlier rounds' compensatory counts (Round 3: {c[3]}, Round 4: {c[4]}, Round 5: {c[5]}, Round 6: {c[6]}, Round 7: {c[7]}).".format(c={int(k): v for k, v in counts.items()}) if awards else
               "- **Overall offsets:** C3, C4, C5 and C6 are the unknown numbers of compensatory picks appended to those rounds. An expression is not an exact overall number. Round 3 ordinary picks precede that round's compensatory additions."),
              "- **Ownership audited:** all 224 ordinary assets have a current allocation. A **conditional hold** identifies a specific outstanding claim, not a second owner. Revis affects one of Tampa Bay's third/fourth; Benn is one claim against an undisclosed Philadelphia round; Rosario affects Chicago's seventh. [Terms, sources and branch exclusions](ownership_audit.md).",
              ("- **Execution gate:** resolve any conditional hold before spending that asset. `require_clear_ownership` rejects held or unaudited assets. Compensatory picks cannot be traded in 2014. Reconcile any newly recorded forfeiture. The branch currently records no forfeited selection." if awards else
               "- **Execution gate:** resolve any conditional hold before spending that asset. `require_clear_ownership` rejects held or unaudited assets. Resolve compensatory numbering before executing affected selections, and reconcile any newly recorded forfeiture. The branch currently records no forfeited selection."),
              ""]
    for rnd in range(1, 8):
        lines += [f"## Round {rnd}", "",
                  "| Slot in round | Overall pick | Original club | Recorded owner | 2013 record | Note |",
                  "|---|---|---|---|---|---|"]
        for row in (r for r in rows if r["round"] == rnd):
            owner = row["owner"] + (" **conditional hold**" if row["ownership_status"] == "encumbered" else "")
            notes = ["Coin flip pending"] if row["coin_flip_pending"] else []
            if row["ownership_status"] in ("recorded", "encumbered"):
                notes.append(row["basis"])
            elif row["ownership_status"] == "retained":
                notes.append("Retained original pick")
            if rnd == 1:
                notes.extend([GROUP_LABEL[row["group"]], f'SOS {row["sos"]:.3f}'])
            note = "; ".join(notes)
            lines.append(f'| {choices(row["slot_options"])} | {ov(row)} | {row["club"]} | {owner} | {row["record"]} | {note} |')
        if rnd >= 3 and awards:
            lines += ["", f"**Compensatory picks after Round {rnd}:**", "",
                      "| Overall pick | Club | Basis | Note |", "|---|---|---|---|"]
            for pick in (p for p in awards["picks"] if p["round"] == rnd):
                basis = (f'Net loss of {pick["for_player"]}' if pick["kind"] == "formula"
                         else "Fill pick to reach 32")
                lines.append(f'| {pick["overall"]} | {pick["club"]} | {basis} | Not tradeable |')
        elif rnd >= 3:
            lines += ["", f"**After Round {rnd}:** compensatory selections pending the March 24 announcement and branch awards reconciliation; no recipients or count for this round assigned."]
        lines.append("")
    if awards:
        lines += ["## Compensatory selections", "",
                  "Announced **March 24, 2014**. The 32 picks rest on each club's qualifying **2013** free-agent losses and signings in the branch. The NFL formula's weights are unpublished, so the branch applies its own [adopted method](compensatory/method.json) to [recorded inputs](compensatory/inputs.json); no real award list is imported. [Announcement and club-by-club detail](compensatory/announcement.md); [awards receipt](compensatory/awards.json).", "",
                  "| Round | Picks | Overall numbers |", "|---|---:|---|"]
        for rnd in range(3, 8):
            nums = [p["overall"] for p in awards["picks"] if p["round"] == rnd]
            lines.append(f"| {rnd} | {len(nums)} | {min(nums)}-{max(nums)} |" if nums else f"| {rnd} | 0 | None |")
        lines += ["", "Compensatory picks cannot be traded in the 2014 draft. The ownership audit records the three specific open claims on ordinary picks; there is no blanket outside-club ownership gap.", ""]
        return "\n".join(lines)
    lines += ["## Pending compensatory selections", "",
              "The 2014 awards depend on qualifying **2013 free-agent losses and signings**, not the upcoming 2014 market. The announcement gate is **March 24, 2014**. Resolve branch eligibility and awards without importing the real recipients; the private formula's exact weights are not supplied by this generator. In 2014 these picks cannot be traded.", "",
              "| Appended after | Count | Owner / overall numbering |",
              "|---|---|---|"]
    for rnd in range(3, 8):
        lines.append(f"| Round {rnd} | C{rnd}: pending | Pending; no real award list imported |")
    lines += ["", "The league's 32 supplemental choices are additional to the 224 ordinary allocations. Until their round distribution is reconciled, later overall pick expressions must retain their offsets. The ownership audit records the three specific open claims; there is no blanket outside-club ownership gap.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("DRAFT ORDER STALE: run python scripts/render_draft_order.py")
            return 1
        print("DRAFT ORDER CURRENT")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
