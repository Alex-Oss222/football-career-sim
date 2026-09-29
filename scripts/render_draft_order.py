#!/usr/bin/env python3
"""Render career/2014/draft/draft_order.md from closed receipts (runtime.draft_order).

  python scripts/render_draft_order.py [--check]
"""
import argparse
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


def overall(row):
    base = choices(row["base_overall_options"])
    offset = " + ".join(f"C{rnd}" for rnd in row["compensatory_after_rounds"])
    return (f"({base})" if offset and len(row["base_overall_options"]) > 1 else base) + (" + " + offset if offset else "")


def render():
    from runtime.draft_order import load_ownership, seven_rounds
    register = load_ownership()
    # This renderer intentionally cannot publish a final order from an invented
    # default zero. A later awards event must add the actual branch selections.
    if (register["compensatory"]["status"] != "pending"
            or register["compensatory"]["round_counts"] is not None):
        raise ValueError("compensatory awards require an explicit final-order implementation")
    rows = seven_rounds(register=register)
    lines = [
        "# 2014 NFL Draft: all seven rounds (branch)", "",
        "**As of:** February 2, 2014; ledger Entry 81. **Draft:** May 8–10, 2014.",
        "**Generated** by `python scripts/render_draft_order.py` from closed branch receipts and [pick_ownership.json](pick_ownership.json). Edit the underlying dated records, then regenerate; do not edit these tables by hand.",
        "**Coverage:** all **224 ordinary selections**, with original club and recorded owner shown separately. Compensatory selections are still pending; this is not a final 256-pick execution list.",
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
            lines.append(f'| {row["round"]} | {row["club"]} | {choices(row["slot_options"])} | {overall(row)} | **{row["owner"]}** |')
    owned = [r for r in rows if r["owner"] == "Jacksonville Jaguars"]
    owned_labels = "; ".join(f"**{overall(row)}**" for row in owned)
    lines += ["", f"Jacksonville currently owns **{len(owned)} ordinary 2014 picks**: {owned_labels}. No prospect is selected by this inventory.", "",
              "| Future asset already conveyed | Current owner | Overall pick | Authority |",
              "|---|---|---|---|"]
    for asset in register["transfers"]:
        if asset["draft_year"] > 2014:
            lines.append(f'| {asset["draft_year"]} Round {asset["round"]}, {asset["original_club"]} original | {asset["owner"]} | Unknown; future branch season | {asset["basis"]} |')
    lines += ["", "## How to read pending fields", "",
              "- **Coin flip resolved:** one RANDOM.ORG draw returned tails at 2026-09-29 01:42:47 UTC. The preassigned mapping gives **Indianapolis 14, Green Bay 15** in Round 1. That result is applied to every later rotation. [Receipt](coin_flip.json); [saved website result](coin_flip_2026-09-29.jpg).",
              "- **Overall offsets:** C3, C4, C5 and C6 are the unknown numbers of compensatory picks appended to those rounds. An expression is not an exact overall number. Round 3 ordinary picks precede that round's compensatory additions.",
              "- **Ownership audited:** all 224 ordinary assets have a current allocation. A **conditional hold** identifies a specific outstanding claim, not a second owner. Revis affects one of Tampa Bay's third/fourth; Benn is one claim against an undisclosed Philadelphia round; Rosario affects Chicago's seventh. [Terms, sources and branch exclusions](ownership_audit.md).",
              "- **Execution gate:** resolve any conditional hold before spending that asset. `require_clear_ownership` rejects held or unaudited assets. Resolve compensatory numbering before executing affected selections, and reconcile any newly recorded forfeiture. The branch currently records no forfeited selection.",
              "- **Existing package A:** the verified rotation puts Seattle's original second at No. 36; Stone's frozen memo also calls it No. 37. Reconcile that intended asset before executing the offer. No Seattle trade or amended offer is recorded here.", ""]
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
            lines.append(f'| {choices(row["slot_options"])} | {overall(row)} | {row["club"]} | {owner} | {row["record"]} | {note} |')
        if rnd >= 3:
            lines += ["", f"**After Round {rnd}:** compensatory selections pending the March 24 announcement and branch awards reconciliation; no recipients or count for this round assigned."]
        lines.append("")
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
