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


def render():
    from runtime.draft_order import order
    rows = order()
    lines = [
        "# 2014 NFL Draft: selection order (branch)",
        "",
        "**Generated** by `python scripts/render_draft_order.py` from the closed 2013 regular-season and postseason receipts (`runtime/draft_order.py`). Do not edit by hand.",
        "**Rules:** `library/2014_league_calendar_and_financial_rules.md` section 4: non-playoff clubs 1-20 by winning percentage, playoff clubs 21-32 by round of elimination, ties to the lower strength of schedule, then the division or conference tiebreaker (the club that would win it picks later), then a coin flip. No real 2014 draft order is imported.",
        "**Draft:** May 8-10, 2014, Radio City Music Hall, New York.",
        "",
        "## Round 1 order",
        "",
        "| Slot | Club | 2013 record | Strength of schedule | Group | Tie note |",
        "|---:|---|---|---:|---|---|",
    ]
    for r in rows:
        sos = ("%.3f" % r["sos"]).lstrip("0")
        lines.append("| %d | %s | %s | %s | %s | %s |" % (r["slot"], r["club"], r["record"], sos,
                     GROUP_LABEL[r["group"]], r["tie"] or ""))
    jax = next(r for r in rows if r["club"] == "Jacksonville Jaguars")
    lines += [
        "",
        "## Rounds 2-7",
        "",
        "Each later round repeats the round-1 order. Under the league rule, clubs tied in winning percentage rotate their order from round to round; the rotation detail is **Unverified** in the library (section 6), so the round-2 to round-7 order between tied clubs is unresolved until it is sourced.",
        "",
        "## Pending before the order is final",
        "",
        "- **Coin flips:** any tie marked \"coin flip pending\" above is decided by a coin flip that the league held before the draft. It is never invented; it is resolved as a recorded branch event when that date is reached.",
        "- **Compensatory selections** (end of rounds 3-7; announced March 24, 2014, a gated date) depend on the branch's own 2014 free-agent losses and gains. No real compensatory award is imported.",
        "- **Pick ownership:** this table orders slots by club. Trades of 2014 selections by other clubs, before or after the branch divergence (January 15, 2013), are not reconciled here and are not imported from later real records.",
        "",
        "## Jacksonville's 2014 selections",
        "",
        "| Round | Slot in round | Owner | Source |",
        "|---:|---:|---|---|",
        "| 1 | %d | Jacksonville | own selection |" % jax["slot"],
        "| 2 | %d | **Washington** | the Kirk Cousins trade (`career/2013/trades/trades.md`) |" % jax["slot"],
    ]
    for rnd in range(3, 8):
        lines.append("| %d | %d | Jacksonville | own selection |" % (rnd, jax["slot"]))
    lines += ["", "Jacksonville's compensatory selections, if any, are pending the branch's 2014 free-agency cycle (see above).", ""]
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
