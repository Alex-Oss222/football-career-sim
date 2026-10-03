"""Versioned calibration bases (kernel 2014.6 plumbing, batch B1).

A calibration base is the frozen set of league artifacts one kernel draws
from and audits against: the aggregate baseline, the drive and
field-position models, the position-usage baseline, the injury calibration,
the attribution tilt and the field-goal distance logistic. Every artifact is
pinned by its sha256 and every base pins the partition counts it must hold
(counted from the pools and count tables themselves, never read from an
artifact's own reconciliation block). A base verifies both before its data
is used and fails closed on any difference.

`base_for_kernel` is an explicit table from kernel version to base: every
kernel up to 2014.5 draws from (and its closed receipts are audited against)
the 2012 base; kernel 2014.6 maps to the 2010-2014 league base the user chose
on October 2, 2026 (U1 = (b), runtime/2014_engine_decisions.md). That base is
built by batch B3 (data only) and pinned with its schema-3 readers by batch
B5 (BASE_2010_2014W4). An unknown version raises.

A CalibrationBase owns its loaded data and every memoised helper built on
it (runtime.field_position.FieldPositionModel, runtime.drive_model.DriveModel,
the injury parameters, the usage and tilt tables, the band centres), so two
bases can be used in one process in either order without one's caches
reaching the other. Nothing here reads a club identity or which side is the
protagonist.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CalibrationBaseError(ValueError):
    """A base that cannot be used: unknown, not built, mixed, or failing a pin."""


@dataclass(frozen=True)
class Pin:
    path: str
    sha256: str


# Every kernel version this repository has released or is building, and the
# base its games draw from. Closed receipts are audited against the base of
# their own kernel_version, never a later one.
KERNEL_BASES = {
    "2013.4": "2012", "2013.5": "2012", "2013.6": "2012", "2013.7": "2012",
    "2013.8": "2012", "2013.9": "2012", "2013.10": "2012", "2013.11": "2012",
    "2014.1": "2012", "2014.2": "2012", "2014.3": "2012", "2014.4": "2012",
    "2014.5": "2012",
    "2014.6": "2010_2014w4",
}

# Bases named by KERNEL_BASES that no runtime reader serves yet (none since
# batch B5 registered the 2010-2014 base).
PENDING_BASES = {}


def _field_position_v2_partitions(data):
    counts = {
        "neutral": sum(sum(row) for row in data["neutral_counts"]),
        "h1_final": sum(sum(cells.values()) for cells in data["h1_final_counts"].values()),
        "late": sum(sum(cells.values()) for cells in data["late_counts"].values()),
        "ot": sum(data["ot_counts"].values()),
    }
    out = {"field_position." + k: v for k, v in counts.items()}
    out["field_position.drives"] = sum(counts.values())
    for pool in ("kickoff_pool", "free_kick_pool", "punt_pool", "interception_pool", "fumble_pool"):
        out["field_position." + pool] = len(data[pool])
    return out


def _drive_model_v1_partitions(data):
    interior = data["pools"]["interior"]
    return {
        "drive_model.drives": sum(data["category_counts"].values()),
        "drive_model.interior": sum(len(interior.get(c, [])) for c in data["categories"]),
        "drive_model.half_final": sum(sum(cells.values()) for cells in data["half_final_counts"].values()),
    }


def _field_position_v3_partitions(data):
    """Schema 3 (kernel 2014.6, batch B5): the end-of-half partition of the
    pre-build specification (neutral over 600 s, h1_late, late, ot_first,
    ot_sudden and the counted, unpooled ot_untied), counted from its count
    tables; the pools and the transition pools by length. The retained kick
    records (kicking-team recoveries, B3b) are counted in their own pools."""
    counts = {
        "neutral": sum(sum(row) for row in data["neutral_counts"]),
        "h1_late": sum(sum(cells.values()) for cells in data["h1_late_counts"].values()),
        "late": sum(sum(cells.values()) for cells in data["late_counts"].values()),
        "ot_first": sum(data["ot_first_counts"].values()),
        "ot_sudden": sum(data["ot_sudden_counts"].values()),
        "ot_untied": sum(data["ot_untied_counts"].values()),
    }
    out = {"field_position." + k: v for k, v in counts.items()}
    out["field_position.drives"] = sum(counts.values())
    pools = data["pools"]
    out["field_position.pooled_tuples"] = (
        sum(len(c) for row in pools["neutral"] for c in row)
        + sum(len(t) for kind in ("h1_late", "late") for cell in pools[kind].values() for t in cell.values())
        + sum(len(t) for kind in ("ot_first", "ot_sudden") for t in pools[kind].values()))
    for pool in ("kickoff_pool", "free_kick_pool", "punt_pool", "interception_pool", "fumble_pool"):
        out["field_position." + pool] = len(data[pool])
    for kind, records in sorted(data["retained_kick_pools"].items()):
        out["field_position.retained_%s_pool" % kind] = len(records)
    return out


def _drive_model_v2_partitions(data):
    return {
        "drive_model.drives": sum(data["category_counts"].values()),
        "drive_model.games": sum(data["games"].values()),
        "drive_model.team_games": sum(data["team_games"].values()),
        "drive_model.field_goal_attempts": data["field_goal_distance"]["attempts"],
    }


# Partition counters by artifact schema. A schema without a counter cannot
# be pinned, so a base naming one fails closed.
PARTITION_COUNTERS = {
    ("field_position", "2012-nfl-field-position-model-v2"): _field_position_v2_partitions,
    ("drive_model", "2012-nfl-drive-model-v1"): _drive_model_v1_partitions,
    ("field_position", "2010-2014w4-nfl-field-position-model-v3"): _field_position_v3_partitions,
    ("drive_model", "2010-2014w4-nfl-drive-model-v2"): _drive_model_v2_partitions,
}

# Artifact roles that are not JSON (read as text, sha256 pinned like the rest).
TEXT_ROLES = ("specification",)


@dataclass(frozen=True, eq=False)
class CalibrationBase:
    """One frozen calibration base. Identity-hashed: its memo is its own."""

    name: str
    cell_rules: str
    files: tuple
    partitions: tuple
    root: Path = ROOT
    # The one season-weight table ((season index, weight), ...): empty is
    # equal weight per event, the adopted default (decisions 1B.1); a
    # recency weighting would be switched on here and would also need
    # weighted draws (B5). Part of the manifest when not empty.
    season_weights: tuple = ()
    # The profile flags a kernel must hold to resolve on this base (kernel
    # 2014.6, batch B5): a base whose readers are a later schema names the
    # flags of the mechanisms built on that schema, and a profile without
    # them (or holding one this base does not serve) fails closed.
    requires_flags: frozenset = frozenset()
    _memo: dict = field(default_factory=dict, init=False, repr=False, compare=False)

    # ---- pins ----------------------------------------------------------------

    def pin(self, role):
        for name, pin in self.files:
            if name == role:
                return pin
        raise CalibrationBaseError("calibration base %s has no %s artifact" % (self.name, role))

    def roles(self):
        return tuple(name for name, _ in self.files)

    def at(self, root):
        """The same base read from another checkout (a fresh memo)."""
        from dataclasses import replace
        return replace(self, root=Path(root))

    def path(self, role):
        return Path(self.root) / self.pin(role).path

    def manifest(self):
        """(role, path, sha256) for every pinned artifact, sorted by role."""
        return tuple(sorted((role, pin.path, pin.sha256) for role, pin in self.files))

    def manifest_sha256(self):
        text = "".join("%s %s %s\n" % row for row in self.manifest())
        if self.season_weights:
            text += "season_weights %s\n" % json.dumps(list(self.season_weights))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _read(self, role):
        path = self.path(role)
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise CalibrationBaseError("calibration base %s: %s is unreadable (%s)"
                                       % (self.name, self.pin(role).path, exc)) from exc
        digest = hashlib.sha256(data).hexdigest()
        if digest != self.pin(role).sha256:
            raise CalibrationBaseError("calibration base %s: %s sha256 %s differs from its pin %s"
                                       % (self.name, self.pin(role).path, digest, self.pin(role).sha256))
        return data

    # ---- memoised data ---------------------------------------------------------

    def memo(self, key, factory):
        """factory() once per base and key; the value is this base's alone."""
        try:
            return self._memo[key]
        except KeyError:
            value = self._memo[key] = factory()
            return value

    def raw(self, role):
        """The parsed artifact, verified against its sha256 pin; shared by
        every helper of this base, so treat it as read-only. A text role
        (TEXT_ROLES) reads as its decoded text."""
        if role in TEXT_ROLES:
            return self.memo(("raw", role), lambda: self._read(role).decode("utf-8"))
        return self.memo(("raw", role), lambda: json.loads(self._read(role)))

    def schema(self, role):
        data = self.raw(role)
        return data.get("schema") if isinstance(data, dict) else None

    def specification_rules(self):
        """The frozen machine-readable rules of the pinned pre-build
        specification (library/2014_6_pre_build_specification.md, section
        8); a base without a pinned specification raises."""
        def build():
            import re
            text = self.raw("specification")
            found = re.findall(r"<!-- frozen-rules:begin -->\s*```json\n(.*?)\n```\s*<!-- frozen-rules:end -->",
                               text, re.S)
            if len(found) != 1:
                raise CalibrationBaseError("calibration base %s: the specification has %d frozen-rules blocks"
                                           % (self.name, len(found)))
            return json.loads(found[0])
        return self.memo(("specification_rules",), build)

    def legacy_2012(self):
        """True for a base read by the 2012-schema readers (the frozen
        kernel 2013.7 rules)."""
        return self.schema("field_position") == "2012-nfl-field-position-model-v2"

    def fresh(self, role):
        """A new parsed copy of the artifact, verified against its pin (for
        callers that may modify what they read)."""
        return json.loads(self._read(role))

    def partition_counts(self):
        """Counted from the loaded pools and count tables (never from an
        artifact's own reconciliation block)."""
        out = {}
        for role, _ in self.files:
            if role in TEXT_ROLES:
                continue
            data = self.raw(role)
            counter = PARTITION_COUNTERS.get((role, data.get("schema"))) if isinstance(data, dict) else None
            if counter is not None:
                out.update(counter(data))
        return out

    def verify(self):
        """Errors (fresh read of every file): sha256 pins and partition counts."""
        errors = []
        for role, pin in self.files:
            try:
                data = self._read(role)
            except CalibrationBaseError as exc:
                errors.append(str(exc))
                continue
            if role in ("field_position", "drive_model"):
                schema = json.loads(data).get("schema")
                if (role, schema) not in PARTITION_COUNTERS:
                    errors.append("calibration base %s: %s schema %s has no partition counter"
                                  % (self.name, role, schema))
        if errors:
            return errors
        counted = self.partition_counts()
        expected = dict(self.partitions)
        for key in sorted(set(expected) | set(counted)):
            if counted.get(key) != expected.get(key):
                errors.append("calibration base %s: partition %s counts %s, pinned %s"
                              % (self.name, key, counted.get(key), expected.get(key)))
        return errors

    def require(self):
        """Verify once per base object; raise on any failed pin."""
        def check():
            errors = self.verify()
            if errors:
                raise CalibrationBaseError("; ".join(errors))
            return True
        return self.memo(("verified",), check)

    # ---- models ----------------------------------------------------------------

    def drive_model(self):
        from .drive_model import model_class
        return self.memo(("model", "drive_model"), lambda: model_class(self.schema("drive_model"))(self))

    def field_position(self):
        from .field_position import model_class
        return self.memo(("model", "field_position"), lambda: model_class(self.schema("field_position"))(self))

    def aggregate(self):
        """The validated aggregate baseline (runtime.calibration)."""
        def build():
            from . import calibration
            data = self.raw("aggregate")
            errors = calibration.validate(data, base=self)
            if errors:
                raise CalibrationBaseError("calibration base %s aggregate baseline invalid: %s"
                                           % (self.name, "; ".join(errors)))
            return data
        return self.memo(("aggregate",), build)

    def usage(self):
        """The validated position-usage baseline (runtime.usage)."""
        def build():
            from . import usage
            data = self.raw("usage")
            errors = usage.validate(data)
            if errors:
                raise CalibrationBaseError("calibration base %s usage baseline invalid: %s"
                                           % (self.name, "; ".join(errors)))
            return data
        return self.memo(("usage",), build)

    def tilt_factors(self):
        from .usage import tilt_factors_from
        return self.memo(("tilt_factors",), lambda: tilt_factors_from(self.raw("usage_tilt")))

    def top_share_centres(self):
        """The per team-game top-share band centres (runtime.bands, item 19):
        the usage baseline's own when it carries them (the 2010-2014 base),
        else the tilt file's 2012 centres."""
        usage = self.raw("usage")
        if "team_game_top_shares" in usage:
            return usage["team_game_top_shares"]
        return self.raw("usage_tilt")["team_game_top_shares_2012"]

    def injury_parameters(self):
        from .injury_model import parameters_from
        return self.memo(("injury_parameters",), lambda: parameters_from(self.raw("injury")))


BASE_2012 = CalibrationBase(
    name="2012",
    cell_rules="2013.7",
    files=(
        ("aggregate", Pin("library/data/2012_nfl_aggregate_baseline.json",
                          "e9326388b1fbab473664fdb83d885b488dd9c3017779c7d6b5cf31b79d1964be")),
        ("drive_model", Pin("library/data/2012_nfl_drive_model.json",
                            "e0365f2365529154f954223a448e23c0a674671ccfc17ca3ee10f942666f1adc")),
        ("field_position", Pin("library/data/2012_nfl_field_position_model.json",
                               "fbfc0f42aa08df23226686beeddb4698403ed8ff436160476913dea08f1118a5")),
        ("usage", Pin("library/data/2012_nfl_position_usage_baseline.json",
                      "2bab464eb76f87917d18e23ecc210bd0ffc39e8bb40a50c1169fd13a6bc8e523")),
        ("injury", Pin("library/data/2012_nfl_injury_calibration.json",
                       "4ba3c34f77126c62f0bddf8f9d919d4f42ec0e8b874b5f7d58098d56e90efcfe")),
        # The attribution tilt factors and the top-share band centres
        # (runtime/usage.py TILT_SOURCE, kernel 2014.4 item 19).
        ("usage_tilt", Pin("library/data/2014_strength_calibration_v2.json",
                           "244eb8b9a2ca7a2ee611dc6c342aac9002d5ff8ec9ad7d19727990ad2824c01f")),
        # The field-goal distance logistic (kernel 2014.4 phase 2, item 18).
        ("fg_distance", Pin("library/data/2014_strength_calibration_v3.json",
                            "48ed2b9116b65c5b0a84059036548c24bcd18627cd4a7661d97b56b408d7e38a")),
    ),
    # Counted from the committed 2012 artifacts on October 2, 2026 (the
    # field-position total is the 5,984 regular-season drives of the
    # artifact's own partition check).
    partitions=(
        ("field_position.drives", 5984), ("field_position.neutral", 4632),
        ("field_position.h1_final", 256), ("field_position.late", 1035), ("field_position.ot", 61),
        ("field_position.kickoff_pool", 2444), ("field_position.free_kick_pool", 13),
        ("field_position.punt_pool", 2405), ("field_position.interception_pool", 386),
        ("field_position.fumble_pool", 251),
        ("drive_model.drives", 5984), ("drive_model.interior", 5472), ("drive_model.half_final", 512),
    ),
)

# Kernel 2014.6 (batch B5): the 2010-2014 league base the user chose on
# October 2, 2026 (U1 = (b)): NFL regular seasons 2010-2013 and 2014 Weeks
# 1-4 (games through September 29, 2014), usable from September 30, 2014 and
# frozen at the first 2014 Week 5 event for the rest of the 2014 season. Its
# artifacts are built by the B3 builders (scripts/research/
# build_2010_2014_league_base.py, build_2010_2014_usage_baseline.py,
# build_2010_2014_injury_calibration.py), each with a --check mode. The
# field-goal distance logistic lives in its drive model (no separate pin);
# the attribution tilt factors stay the v2 file's (plan section 3). The
# pre-build specification is pinned so its frozen rules (the end-of-half
# constants) are read, never typed.
BASE_2010_2014W4 = CalibrationBase(
    name="2010_2014w4",
    cell_rules="2014.6",
    files=(
        ("aggregate", Pin("library/data/2010_2014w4_nfl_aggregate_baseline.json",
                          "8b3647cb9a4d6e1e71a732b8b0794da3c35f9b2ceb3ee3933f8789d53d473b1d")),
        ("drive_model", Pin("library/data/2010_2014w4_nfl_drive_model.json",
                            "ea586db47de6083556d147ca7ab3612fd20fd8a1a46fce8074835ddefa41675f")),
        ("field_position", Pin("library/data/2010_2014w4_nfl_field_position_model.json",
                               "b7af8c0412ef4ee7ecfdc497dbd072a58bf9171a5c3d1cee0bf5afdb0415c126")),
        ("usage", Pin("library/data/2010_2014w4_nfl_position_usage_baseline.json",
                      "312aa79ef43fea9a6ef8f14a6d5abbd049c919d6b4879433f21ce3abfe0f8108")),
        ("injury", Pin("library/data/2010_2014w4_nfl_injury_calibration.json",
                       "ef32ef3798fe383768f357d949a64c7c23ef066141f18fc0a3c91636ee1c5169")),
        ("usage_tilt", Pin("library/data/2014_strength_calibration_v2.json",
                           "244eb8b9a2ca7a2ee611dc6c342aac9002d5ff8ec9ad7d19727990ad2824c01f")),
        ("specification", Pin("library/2014_6_pre_build_specification.md",
                              "ca028ba38009d1b84e5c887ea86ce8d697edf1705bcd9b755f60aede9d6f8446")),
    ),
    # Counted from the committed 2010-2014 artifacts on October 3, 2026 (the
    # field-position total is the pooled partition, 25,468 drives: the
    # drive model's 25,556 less the 88 excluded 2010-2011 overtime drives).
    partitions=(
        ("field_position.drives", 25468), ("field_position.neutral", 16287),
        ("field_position.h1_late", 4577), ("field_position.late", 4493),
        ("field_position.ot_first", 41), ("field_position.ot_sudden", 64), ("field_position.ot_untied", 6),
        ("field_position.pooled_tuples", 25431),
        ("field_position.kickoff_pool", 7944), ("field_position.free_kick_pool", 65),
        ("field_position.punt_pool", 10348), ("field_position.interception_pool", 1790),
        ("field_position.fumble_pool", 1044),
        ("field_position.retained_free_kick_pool", 0), ("field_position.retained_kickoff_pool", 41),
        ("field_position.retained_punt_pool", 105),
        ("drive_model.drives", 25556), ("drive_model.games", 1085), ("drive_model.team_games", 2170),
        ("drive_model.field_goal_attempts", 4225),
    ),
    requires_flags=frozenset({"base_2014_6", "regimes_v3"}),
)

BASES = {BASE_2012.name: BASE_2012, BASE_2010_2014W4.name: BASE_2010_2014W4}
# Bases whose kernels predate the recorded calibration_base block.
RECORDLESS_BASES = frozenset({BASE_2012.name})


def get_base(name):
    """The committed base of that name; a pending or unknown name raises."""
    if isinstance(name, CalibrationBase):
        return name
    if name in BASES:
        return BASES[name]
    if name in PENDING_BASES:
        raise CalibrationBaseError("calibration base %s is not available: %s" % (name, PENDING_BASES[name]))
    raise CalibrationBaseError("unknown calibration base %r" % (name,))


def base_for_kernel(version):
    """The base name of a kernel version string (explicit table); an
    unknown version, or one that is not a string, raises."""
    if not isinstance(version, str) or version not in KERNEL_BASES:
        raise CalibrationBaseError("no calibration base is defined for kernel version %r" % (version,))
    return KERNEL_BASES[version]


def base_of_kernel(version):
    return get_base(base_for_kernel(version))


def base_for_result(result):
    """The base a result or receipt is audited against: its own kernel
    version's. A recorded calibration_base block (kernel 2014.6 onward) must
    name that same base and manifest, or the audit fails closed."""
    base = base_of_kernel(result.get("kernel_version"))
    recorded = result.get("calibration_base")
    if recorded is None and base_for_kernel(result.get("kernel_version")) not in RECORDLESS_BASES:
        # Kernel 2014.6 onward always records its base (batch B5): a result
        # or receipt without the block fails closed.
        raise CalibrationBaseError("%s (kernel %s) records no calibration base"
                                   % (result.get("event_id"), result.get("kernel_version")))
    if recorded is not None:
        if not isinstance(recorded, dict) or recorded.get("name") != base.name \
                or recorded.get("manifest_sha256") != base.manifest_sha256() \
                or recorded.get("cell_rules") != base.cell_rules:
            raise CalibrationBaseError("%s records calibration base %r, not the %s base of kernel %s"
                                       % (result.get("event_id"), recorded, base.name,
                                          result.get("kernel_version")))
    return base


def cohort_base_name(receipts):
    """The one base name every receipt of a cohort maps to; None when empty.
    A cohort whose receipts map to two bases raises (audits never mix bases)."""
    names = {base_for_kernel(r.get("kernel_version")) for r in receipts}
    if len(names) > 1:
        raise CalibrationBaseError("mixed-base cohort: receipts map to calibration bases %s"
                                   % ", ".join(sorted(names)))
    return next(iter(names)) if names else None


def cohort_base(receipts, cohort=None):
    """The base a band cohort is graded against.

    `cohort` (a kernel version) names it explicitly; every receipt must then
    map to the same base. Without one the receipts decide, and an empty
    receipt list falls back to the 2012 base (every closed cohort's)."""
    name = cohort_base_name(receipts)
    if cohort is not None:
        expected = base_for_kernel(cohort)
        if name is not None and name != expected:
            raise CalibrationBaseError("cohort %s is graded on the %s base; its receipts map to %s"
                                       % (cohort, expected, name))
        name = expected
    return get_base(name if name is not None else BASE_2012.name)


def record(base):
    """The append-only receipt block naming a base (kernel 2014.6 onward)."""
    return {"name": base.name, "manifest_sha256": base.manifest_sha256(), "cell_rules": base.cell_rules}
