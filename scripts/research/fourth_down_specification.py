#!/usr/bin/env python3
"""The kernel 2014.6 batch B9F fourth-down specification: its pinned digest and frozen rules.

library/2014_6_fourth_down_specification.md fixes the fourth-down chart's bins, states and
collapse ladder, the conversion and record rules, the resolution, timing and pause rules and
the band rows of batch B9F before its builder counted any fourth-down row. It is never
edited: FROZEN_SHA256 pins it, and the B9F artifact header records that digest.

  python scripts/research/fourth_down_specification.py           prints the digest
  python scripts/research/fourth_down_specification.py --check   verifies the pin and the block

Stdlib only; read-only.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "library/2014_6_fourth_down_specification.md"
FROZEN_SHA256 = "fdf719b92fe022e05df2ccd85254677ff1418108db919e75cce7af82e3bae156"
TITLE = "# Kernel 2014.6 batch B9F fourth-down specification, written before its rates were counted"
BLOCK = re.compile(r"<!-- frozen-rules:begin -->\s*```json\n(.*?)\n```\s*<!-- frozen-rules:end -->", re.S)
REQUIRED = ("specification", "written", "blind", "pre_build_specification_sha256", "data", "actions",
            "distance_bins", "zones", "coarse_zones", "coarse_distances", "states", "collapse_ladder",
            "conversion", "record_kinds", "call_families", "field_goal_offset", "sockets", "bases",
            "controlled_default", "timing", "answers", "substream", "clock", "bands", "agreement", "seeds")
LADDER = ["full", "time_merged", "zone_coarse", "neutral", "distance_coarse", "zone_only"]


def digest(path=SPEC):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_rules(path=SPEC):
    """The machine-readable block of the specification, parsed."""
    text = Path(path).read_text(encoding="utf-8")
    found = BLOCK.findall(text)
    if len(found) != 1:
        raise ValueError("expected exactly one frozen-rules block, found %d" % len(found))
    return json.loads(found[0])


def _partition(edges, low, high):
    return (bool(edges) and edges[0][0] == low and edges[-1][1] == high
            and all(a[1] + 1 == b[0] for a, b in zip(edges, edges[1:])) and all(a <= b for a, b in edges))


def rule_errors(rules):
    """Internal consistency of the block (never a statement about results)."""
    errors = [key + " missing" for key in REQUIRED if key not in rules]
    if errors:
        return errors
    if rules["actions"] != ["go", "field_goal", "punt"]:
        errors.append("the actions are go, field_goal and punt")
    if not _partition(rules["distance_bins"], 1, 99) or not _partition(rules["coarse_distances"], 1, 99):
        errors.append("distance bins must cover 1-99 without gaps")
    if not _partition(rules["zones"], 1, 99) or not _partition(rules["coarse_zones"], 1, 99):
        errors.append("zones must cover the field 1-99 without gaps")
    for fine, coarse, name in ((rules["zones"], rules["coarse_zones"], "zone"),
                               (rules["distance_bins"], rules["coarse_distances"], "distance")):
        if any(not any(c[0] <= f[0] and f[1] <= c[1] for c in coarse) for f in fine):
            errors.append("every %s bin must nest in one coarse bin" % name)
    if rules["collapse_ladder"] != LADDER:
        errors.append("the collapse ladder is %s" % LADDER)
    margins = rules["states"]["ot_margins"]
    if not _partition(sorted(margins.values()), -999, 999):
        errors.append("overtime margins must partition the score difference")
    fams = rules["call_families"]
    if sorted(fams["run"] + fams["pass"]) != sorted(rules["record_kinds"]):
        errors.append("the call families must partition the record kinds")
    if any(v != 0.0 for v in rules["sockets"].values()):
        errors.append("every B9F socket is at slope 0")
    if not set(rules["field_goal_offset"]["allowed"]) <= {17, 18, 19}:
        errors.append("the field-goal offset lies in 17-19 (the audit's fg_distance_offset)")
    if not {"live", "league"} <= set(rules["bases"]):
        errors.append("the bases include a live answer and the league chart")
    if rules["timing"] != ["before_third_down", "at_fourth_down"]:
        errors.append("the timings are before_third_down and at_fourth_down")
    if rules["answers"]["fourth_down"] != rules["actions"]:
        errors.append("the answers are the actions")
    return errors


def check(path=SPEC):
    errors = []
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith(TITLE + "\n"):
        errors.append("the title must state that the specification was written before its rates were counted")
    if digest(path) != FROZEN_SHA256:
        errors.append("specification digest %s differs from the frozen pin %s; the file is never edited, "
                      "a rule change needs a new dated specification" % (digest(path), FROZEN_SHA256))
    try:
        rules = frozen_rules(path)
        errors.extend(rule_errors(rules))
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import pre_build_specification
        if rules.get("pre_build_specification_sha256") != pre_build_specification.FROZEN_SHA256:
            errors.append("the B9F specification names another pre-build specification")
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
        print("PASS: B9F fourth-down specification %s" % FROZEN_SHA256)
        return 0
    print(digest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
