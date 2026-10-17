#!/usr/bin/env python3
"""The kernel 2014.6 pre-build specification: its pinned digest and frozen rules.

library/2014_6_pre_build_specification.md fixes every selection rule, threshold,
band-row status and acceptance seed block of the 2014.6 build before anything is
built. It is never edited: FROZEN_SHA256 pins it, and every 2014.6 artifact header
records that digest.

  python scripts/research/pre_build_specification.py           prints the digest
  python scripts/research/pre_build_specification.py --check   verifies the pin and the block

Builders import ``digest()`` for their headers and ``frozen_rules()`` for the
constants. Stdlib only; read-only.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "library/2014_6_pre_build_specification.md"
FROZEN_SHA256 = "ca028ba38009d1b84e5c887ea86ce8d697edf1705bcd9b755f60aede9d6f8446"
TITLE = "# Kernel 2014.6 pre-build specification, written after the results it cites were seen"
BLOCK = re.compile(r"<!-- frozen-rules:begin -->\s*```json\n(.*?)\n```\s*<!-- frozen-rules:end -->", re.S)
REQUIRED = ("specification", "written", "blind", "data_window", "weighting", "structural_filters", "thresholds",
            "end_of_half", "scoring", "emphasis_2014", "yardage", "context", "credit_concentration",
            "player_state", "strength_v4", "seeds")


def digest(path=SPEC):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_rules(path=SPEC):
    """The machine-readable block of the specification, parsed."""
    text = Path(path).read_text(encoding="utf-8")
    found = BLOCK.findall(text)
    if len(found) != 1:
        raise ValueError("expected exactly one frozen-rules block, found %d" % len(found))
    return json.loads(found[0])


def _contiguous(edges, low, high):
    return (bool(edges) and edges[0][0] == low and edges[-1][1] == high
            and all(a[1] + 1 == b[0] for a, b in zip(edges, edges[1:])) and all(a <= b for a, b in edges))


def rule_errors(rules):
    """Internal consistency of the block (never a statement about results)."""
    errors = [key + " missing" for key in REQUIRED if key not in rules]
    if errors:
        return errors
    window = rules["data_window"]
    cut = window["cut_2014"]
    if sum(cut["games_by_week"]) != cut["games"] or len(cut["games_by_week"]) != cut["max_week"]:
        errors.append("2014 cut: games by week do not add to the cut")
    if window["seasons"] != list(range(2010, 2015)):
        errors.append("data window must be 2010-2014")
    if not window["public_from"] > cut["max_game_date"] or not window["frozen_at"]["date"] >= window["public_from"]:
        errors.append("information gate dates out of order")
    if rules["blind"] is not False:
        errors.append("the specification is not blind and must say so")
    eoh = rules["end_of_half"]
    if not _contiguous(eoh["H1_LATE_EDGES"], 0, eoh["H1_LATE_SECONDS"]):
        errors.append("h1_late edges must cover 0 to H1_LATE_SECONDS without gaps")
    if not _contiguous(sorted(eoh["LATE_TIME_BUCKETS"].values()), 0, eoh["NEUTRAL_OVER_SECONDS"]):
        errors.append("late time buckets must cover 0 to the neutral boundary without gaps")
    if not _contiguous(sorted(eoh["NEEDS"].values()), -999, 999) or len(eoh["NEEDS"]) != 8:
        errors.append("needs must partition the score difference into eight buckets")
    if eoh["TIME_MATCH_FALLBACK_SECONDS"] <= eoh["TIME_MATCH_SECONDS"]:
        errors.append("the time-match fallback must be wider than the match")
    if not _contiguous(sorted(eoh["DECISION_ZONES"].values()), 1, 99):
        errors.append("decision zones must cover the field 1-99")
    if not _contiguous(rules["scoring"]["return_td_los_bins"], 1, 99):
        errors.append("return-touchdown LOS bins must cover 1-99")
    emphasis = rules["emphasis_2014"]
    if len(emphasis["types"]) != 5 or any(t[2] not in ("dropbacks", "snaps") for t in emphasis["types"]):
        errors.append("the emphasis set is five type-sides, each with a dropback or snap exposure")
    if emphasis["completion_tilt"] is not False:
        errors.append("U2 as decided: no completion tilt")
    if "postseason" in emphasis["game_types_on"] and emphasis["persist_through_week"] <= 17:
        errors.append("U2 covers Weeks 5-17: the emphasis cannot be on in the postseason (weeks 18-21)")
    kinds = [set(emphasis[k]) for k in ("game_types_on", "game_types_undecided", "game_types_off")]
    if any(a & b for i, a in enumerate(kinds) for b in kinds[i + 1:]):
        errors.append("emphasis game types must be on, undecided or off, never two of them")
    scoring = rules["scoring"]
    if not {"live", "league"} <= set(scoring["basis_values"]):
        errors.append("decision basis must include a live-pause answer and the league chart (U6)")
    controlled = set(scoring["controlled_club_basis"])
    if not controlled <= set(scoring["basis_values"]) or "league" in controlled or "live" not in controlled:
        errors.append("the controlled club's basis is Stone's rule, delegation or live answer, never the bare chart")
    pins = window["nflscrapr_reg_pbp_fetch_sha256"]
    if sorted(int(k) for k in pins) != window["seasons"]:
        errors.append("one nflscrapR fetch pin per season of the window")
    state = rules["player_state"]
    if state["u5"] != "accepted":
        fallback = state.get("u5_fallback") or {}
        if not (state.get("u5_conditional") and fallback.get("aging") and fallback.get("draft_slope") == 0):
            errors.append("U5 unanswered: the conditional rules and their fallback must be named")
    for kind, edges in rules["credit_concentration"]["role_bins"].items():
        if edges != sorted(edges) or not all(0 < e < 1 for e in edges):
            errors.append("role bins for %s must be increasing shares" % kind)
    seeds = rules["seeds"]
    sweep = seeds["sweep"]
    if sweep["per_fixture"] * sweep["fixtures"] != sweep["games"]:
        errors.append("sweep labels do not add to the sweep size")
    if len(sweep.get("fixture_tokens") or {}) != sweep["fixtures"]:
        errors.append("each sweep fixture must be named")
    prefixes = [seeds[k]["prefix"] for k in ("acceptance", "extended", "latent_references")]
    if len(set(prefixes)) != len(prefixes):
        errors.append("seed blocks must not share a prefix")
    return errors


def check(path=SPEC):
    errors = []
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith(TITLE + "\n"):
        errors.append("the title must state that the specification was written after its results were seen")
    if digest(path) != FROZEN_SHA256:
        errors.append("specification digest %s differs from the frozen pin %s; the file is never edited, "
                      "a rule change needs a new dated specification" % (digest(path), FROZEN_SHA256))
    try:
        errors.extend(rule_errors(frozen_rules(path)))
    except (ValueError, KeyError, TypeError) as exc:
        errors.append("frozen rules unreadable: %s" % exc)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify the pin and the frozen-rules block")
    args = parser.parse_args(argv)
    if args.check:
        errors = check()
        for error in errors:
            print("ERROR: " + error)
        if errors:
            return 1
        print("PASS: pre-build specification %s" % FROZEN_SHA256)
        return 0
    print(digest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
