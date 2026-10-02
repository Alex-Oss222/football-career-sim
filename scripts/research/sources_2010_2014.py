#!/usr/bin/env python3
"""Sources and the information gate for every kernel 2014.6 builder (plan batch B2; data only).

  python scripts/research/sources_2010_2014.py --fetch --dest DIR [--only NAME ...]
  python scripts/research/sources_2010_2014.py --fetch --dest DIR --write-manifest [--repin]
  python scripts/research/sources_2010_2014.py --check [--dest DIR]

Every 2014.6 builder reads its league data through this module and nothing else:
``source_path(name, dest)`` returns a verified local file and ``rows(name, dest)``
yields its rows after the information gate has been applied again. Nothing in
runtime/ imports it.

What it fetches (``ASSETS``): nflverse play-by-play 2010-2014, seasonal rosters
2010-2013, weekly rosters 2010-2014, injuries 2010-2014, snap counts 2013-2014,
depth charts 2010-2014, weekly player statistics 2010-2014, draft picks and the
player database; nflscrapR regular-season play-by-play 2010-2014; the NFL.com
offensive passing and rushing team tables 2010-2013.

The gate (library/2014_6_pre_build_specification.md, section 1):
- 2014 is cut at fetch: ``season_type``/``game_type`` REG, ``week <= 4`` and every
  date on the row on or before 2014-09-29. The full-season 2014 file is hashed in
  memory, checked against its pin, cut, and only the cut file is written.
- Refused: any ``stats_player_reg_*`` file, any season after 2014, any 2014 row
  beyond the cut, the seasonal 2014 roster (an end-of-season snapshot with no
  date to cut on; the weekly roster is used instead) and any path under career/.
- Column allowlists: the player database keeps gsis_id, birth_date, the draft
  fields, pff_id and pfr_id; draft picks keep season, round, pick, team, gsis_id
  and position. Weekly player statistics drop the current database's position
  labels (positions come from that season's own roster). Rows of the player
  database and draft picks for later draft classes are dropped.

Pins. Every asset's full 64-hex sha256 is recorded as fetched (provenance) and,
separately, the sha256 of the file written (the cut). A mismatch fails closed.
The play-by-play pins are anchored to the committed records named by the
specification (2010-2012 library/data/2010_2012_production_evidence.json,
2013-2014 library/data/passer_interception_persistence.json, nflscrapR from the
specification block and library/data/2012_nfl_field_position_model.json). A
``rolling`` asset (the player database, draft picks, weekly player statistics,
the NFL.com pages) is republished by its publisher without notice; its fetched
digest is provenance, and its written cut must match the pin.

Raw data stays out of the repository: the destination must be outside it. The
committed manifest, library/data/2010_2014_sources_manifest.json, holds only
digests, byte and row counts and the 2014 cut summary.

Attribution: nflverse data (https://github.com/nflverse/nflverse-data) is
published under CC BY 4.0; nflscrapR-data by Ron Yurko
(https://github.com/ryurko/nflscrapR-data); team tables from NFL.com. Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import html
import io
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_build_specification  # noqa: E402

MANIFEST = ROOT / "library/data/2010_2014_sources_manifest.json"
SCHEMA_VERSION = 1
CAREER = ROOT / "career"
SEASONS = (2010, 2011, 2012, 2013, 2014)
LAST_SEASON = 2014
CUT_SEASON = 2014
_RULES = pre_build_specification.frozen_rules()["data_window"]
CUT = _RULES["cut_2014"]
MAX_WEEK = CUT["max_week"]
MAX_DATE = CUT["max_game_date"]
NFLVERSE = "https://github.com/nflverse/nflverse-data/releases/download/"
SCRAPR = "https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/"
NFLCOM = "https://www.nfl.com/stats/team-stats/offense/%s/%d/reg/all"
USER_AGENT = "curl/8.5.0"
ATTRIBUTION = {
    "nflverse": "nflverse-data, https://github.com/nflverse/nflverse-data, licensed CC BY 4.0",
    "nflscrapR": "nflscrapR-data by Ron Yurko, https://github.com/ryurko/nflscrapR-data",
    "NFL.com": "NFL.com team statistics pages; only digests and counts are committed",
}

PLAYERS_COLUMNS = ("gsis_id", "birth_date", "draft_year", "draft_round", "draft_pick", "draft_team",
                   "pff_id", "pfr_id")
PLAYERS_NEVER = ("rookie_season", "last_season", "status", "years_of_experience")
DRAFT_PICKS_COLUMNS = ("season", "round", "pick", "team", "gsis_id", "position")
DRAFT_PICKS_NEVER = ("to", "allpro", "probowls", "seasons_started", "w_av", "car_av", "dr_av", "games")
# Weekly player statistics carry the current player database's position labels.
STATS_WEEK_DROPPED = ("position", "position_group", "headshot_url")

TYPE_COLUMNS = ("season_type", "game_type")
DATE_COLUMNS = ("game_date", "date_modified", "gameday")


class SourceRefused(ValueError):
    """A read or fetch the information gate does not allow."""


class SourceMismatch(ValueError):
    """A digest, count or invariant that differs from its pin."""


@dataclass(frozen=True)
class Asset:
    name: str            # the file written under the destination
    url: str
    publisher: str       # nflverse, nflscrapR or NFL.com
    kind: str
    season: int | None   # None for the whole-database files
    rolling: bool = False
    fetched_as: str = field(default="")

    @property
    def cut(self):
        """True when the written file differs from the fetched bytes."""
        return (self.season == CUT_SEASON or self.kind in ("players", "draft_picks", "stats_player_week")
                or self.publisher == "NFL.com")


def _assets():
    out = []
    for s in SEASONS:
        pbp = "play_by_play_%d.csv.gz" % s
        out.append(Asset("play_by_play_2014w4.csv" if s == CUT_SEASON else pbp, NFLVERSE + "pbp/" + pbp,
                         "nflverse", "pbp", s, fetched_as=pbp))
    for s in SEASONS:
        name = "reg_pbp_%d.csv" % s
        out.append(Asset("reg_pbp_2014w4.csv" if s == CUT_SEASON else name, SCRAPR + name, "nflscrapR",
                         "reg_pbp", s, fetched_as=name))
    for s in SEASONS[:-1]:
        name = "roster_%d.csv" % s
        out.append(Asset(name, NFLVERSE + "rosters/" + name, "nflverse", "roster", s, fetched_as=name))
    for kind, folder, stem, seasons in (
            ("roster_weekly", "weekly_rosters", "roster_weekly", SEASONS),
            ("injuries", "injuries", "injuries", SEASONS),
            ("snap_counts", "snap_counts", "snap_counts", (2013, 2014)),
            ("depth_charts", "depth_charts", "depth_charts", SEASONS)):
        for s in seasons:
            name = "%s_%d.csv" % (stem, s)
            out.append(Asset("%s_%dw4.csv" % (stem, s) if s == CUT_SEASON else name,
                             NFLVERSE + folder + "/" + name, "nflverse", kind, s, fetched_as=name))
    for s in SEASONS:
        name = "stats_player_week_%d.csv" % s
        out.append(Asset("stats_player_week_2014w4.csv" if s == CUT_SEASON else name,
                         NFLVERSE + "stats_player/" + name, "nflverse", "stats_player_week", s, rolling=True,
                         fetched_as=name))
    out.append(Asset("draft_picks.csv", NFLVERSE + "draft_picks/draft_picks.csv", "nflverse", "draft_picks",
                     None, rolling=True, fetched_as="draft_picks.csv"))
    out.append(Asset("players.csv", NFLVERSE + "players/players.csv", "nflverse", "players", None,
                     rolling=True, fetched_as="players.csv"))
    for table in ("passing", "rushing"):
        for s in SEASONS[:-1]:
            out.append(Asset("nflcom_offense_%s_%d.csv" % (table, s), NFLCOM % (table, s), "NFL.com",
                             "nflcom_" + table, s, rolling=True, fetched_as="%s_%d.html" % (table, s)))
    return tuple(out)


ASSETS = _assets()
BY_NAME = {a.name: a for a in ASSETS}
# Players need the dated roster ids, so rosters are fetched first.
FETCH_ORDER = sorted(ASSETS, key=lambda a: a.kind == "players")

REFUSED = (
    (re.compile(r"stats_player_reg"), "season-aggregate player statistics are refused (strength targets are "
                                      "recomputed from play-by-play)"),
    (re.compile(r"(?<!\d)(201[5-9]|20[2-9]\d)(?!\d)"), "no season after 2014 is read"),
    (re.compile(r"^roster_2014\.csv$"), "the seasonal 2014 roster is an end-of-season snapshot with no date to cut "
                                        "on; the weekly roster is cut instead"),
    (re.compile(r"_2014\.csv(\.gz)?$|^play_by_play_2014\.csv\.gz$"), "a full-season 2014 file is never written or read; "
                                                                    "only its cut (…_2014w4) is"),
)


# ------------------------------------------------------------------ the gate
def refuse_name(name):
    """Raise SourceRefused for a file name the gate refuses or the manifest does not hold."""
    base = Path(name).name
    for pattern, why in REFUSED:
        if pattern.search(base):
            raise SourceRefused("%s: %s" % (base, why))
    if base not in BY_NAME:
        raise SourceRefused("%s is not a 2010-2014 source asset (see ASSETS)" % base)
    return BY_NAME[base]


def guard_path(path):
    """Refuse any path under career/ (branch records are never a source)."""
    resolved = Path(path).resolve()
    career = CAREER.resolve()
    if resolved == career or career in resolved.parents:
        raise SourceRefused("%s is under career/: branch records are never league source data" % path)
    return resolved


def guard_dest(dest):
    """The destination must be outside the repository (raw data is never committed)."""
    resolved = guard_path(dest)
    root = ROOT.resolve()
    if resolved == root or root in resolved.parents:
        raise SourceRefused("%s is inside the repository: raw source data stays out of it" % dest)
    return resolved


def _int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def row_errors(row, season):
    """Why a row is outside the information gate (empty when admissible)."""
    errors = []
    row_season = _int(row.get("season"))
    if row_season is not None and row_season > LAST_SEASON:
        errors.append("season %s after 2014" % row_season)
    if season == CUT_SEASON or row_season == CUT_SEASON:
        for column in TYPE_COLUMNS:
            if column in row and row[column] != "REG":
                errors.append("%s %s is not REG" % (column, row[column]))
        week = _int(row.get("week"))
        if "week" in row and (week is None or week > MAX_WEEK):
            errors.append("week %s after week %d" % (row.get("week"), MAX_WEEK))
        for column in DATE_COLUMNS:
            value = (row.get(column) or "")[:10]
            if value and value > MAX_DATE:
                errors.append("%s %s after %s" % (column, value, MAX_DATE))
        if not ("week" in row or any(c in row for c in DATE_COLUMNS)):
            errors.append("a 2014 row with neither a week nor a date cannot be cut")
    return errors


def assert_rows_admissible(rows, season):
    for i, row in enumerate(rows):
        errors = row_errors(row, season)
        if errors:
            raise SourceRefused("row %d: %s" % (i, "; ".join(errors)))


# ------------------------------------------------------------- projections
def kept_columns(kind, header):
    """The columns written for an asset kind (allowlists are exact, never extended)."""
    if kind == "players":
        missing = [c for c in PLAYERS_COLUMNS if c not in header]
        if missing:
            raise SourceMismatch("players.csv lacks allowlisted columns %s" % missing)
        return list(PLAYERS_COLUMNS)
    if kind == "draft_picks":
        missing = [c for c in DRAFT_PICKS_COLUMNS if c not in header]
        if missing:
            raise SourceMismatch("draft_picks.csv lacks allowlisted columns %s" % missing)
        return list(DRAFT_PICKS_COLUMNS)
    if kind == "stats_player_week":
        return [c for c in header if c not in STATS_WEEK_DROPPED]
    return list(header)


def _decode(asset, raw):
    data = gzip.decompress(raw) if asset.fetched_as.endswith(".gz") else raw
    return data.decode("utf-8")


def _write_csv(header, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow([row.get(c, "") for c in header])
    return buffer.getvalue().encode("utf-8")


def _draft_year_ok(value):
    year = _int(value)
    return year is not None and year <= LAST_SEASON


def cut_table(asset, text, known_ids=None):
    """Apply the gate and the allowlist to a CSV text. Returns (bytes, rows_in, rows_out, header)."""
    reader = csv.DictReader(io.StringIO(text, newline=""))
    header = kept_columns(asset.kind, reader.fieldnames or [])
    rows_in = 0
    kept = []
    for row in reader:
        rows_in += 1
        if asset.kind == "players":
            if not (_draft_year_ok(row.get("draft_year")) or (known_ids is not None and row["gsis_id"] in known_ids)):
                continue
        elif asset.kind == "draft_picks":
            if not _draft_year_ok(row.get("season")):
                continue
        elif row_errors(row, asset.season):
            continue
        kept.append(row)
    return _write_csv(header, kept), rows_in, len(kept), header


_CELL = re.compile(r"<t[hd][^>]*>(.*?)</t[hd]>", re.S)
_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)


def _cell_text(cell):
    words = html.unescape(re.sub(r"<[^>]+>", " ", cell)).split()
    half = len(words) // 2
    if words and len(words) % 2 == 0 and words[:half] == words[half:]:
        words = words[:half]  # the team cell repeats its name (wide and narrow layouts)
    return " ".join(words)


def parse_nflcom_table(page):
    """The single statistics table of an NFL.com team-stats page, as (header, rows)."""
    tables = re.findall(r"<table[^>]*>.*?</table>", page, re.S)
    if len(tables) != 1:
        raise SourceMismatch("expected one table on the NFL.com page, found %d" % len(tables))
    rows = [[_cell_text(c) for c in _CELL.findall(r)] for r in _ROW.findall(tables[0])]
    rows = [r for r in rows if r]
    header, body = rows[0], rows[1:]
    if any(len(r) != len(header) for r in body):
        raise SourceMismatch("ragged NFL.com table")
    return header, body


def cut_nflcom(asset, raw):
    header, body = parse_nflcom_table(raw.decode("utf-8"))
    if len(body) != 32:
        raise SourceMismatch("%s: %d team rows, expected 32" % (asset.name, len(body)))
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["season"] + header)
    for row in body:
        writer.writerow([asset.season] + row)
    return buffer.getvalue().encode("utf-8"), len(body), len(body), ["season"] + header


def produce(asset, raw, known_ids=None):
    """The bytes written for an asset from its fetched bytes, with counts."""
    if asset.publisher == "NFL.com":
        return cut_nflcom(asset, raw)
    if not asset.cut:
        return raw, None, None, None
    return cut_table(asset, _decode(asset, raw), known_ids)


# ----------------------------------------------------------------- pins
def sha256(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def anchor_pins():
    """Fetched-asset digests fixed by committed records before B2 (the specification names them)."""
    pins = {}
    production = json.loads((ROOT / "library/data/2010_2012_production_evidence.json").read_text())["sources"]
    persistence = json.loads((ROOT / "library/data/passer_interception_persistence.json").read_text())["sources"]
    field_position = json.loads((ROOT / "library/data/2012_nfl_field_position_model.json").read_text())["sources"]
    for s in (2010, 2011, 2012):
        pins["play_by_play_%d.csv.gz" % s] = production["play_by_play_%d.csv.gz" % s]["sha256"]
        pins["depth_charts_%d.csv" % s] = production["depth_charts_%d.csv" % s]["sha256"]
    for s in (2013, 2014):
        pins["play_by_play_%d.csv.gz" % s] = persistence["play_by_play_%d.csv.gz" % s]["sha256"]
    for s, pin in _RULES["nflscrapr_reg_pbp_fetch_sha256"].items():
        pins["reg_pbp_%s.csv" % s] = pin
    if field_position["nflscrapr"]["sha256"] != pins["reg_pbp_2012.csv"]:
        raise SourceMismatch("the specification's nflscrapR 2012 pin differs from the field-position model's")
    return pins


def load_manifest(path=MANIFEST):
    if not Path(path).exists():
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _fetch(url, attempts=5):
    """The complete body of a URL; a truncated or failed transfer is retried, never kept."""
    import http.client
    import time
    import urllib.error
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=300) as response:
                body = response.read()
                length = response.headers.get("Content-Length")
                if length is not None and int(length) != len(body):
                    raise http.client.IncompleteRead(body, int(length) - len(body))
                return body
        except (http.client.IncompleteRead, urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))


def verify_fetched(asset, raw_sha, manifest, anchors):
    """Fail closed on a fetched digest that differs from its pin (rolling assets: provenance only)."""
    anchor = anchors.get(asset.fetched_as)
    if anchor is not None and raw_sha != anchor:
        raise SourceMismatch("%s fetched %s, committed pin %s" % (asset.fetched_as, raw_sha, anchor))
    record = (manifest or {}).get("assets", {}).get(asset.name)
    if record and not asset.rolling and raw_sha != record["fetched_sha256"]:
        raise SourceMismatch("%s fetched %s, manifest pin %s" % (asset.fetched_as, raw_sha,
                                                                 record["fetched_sha256"]))


def verify_written(asset, written_sha, manifest):
    record = (manifest or {}).get("assets", {}).get(asset.name)
    if record and written_sha != record["sha256"]:
        raise SourceMismatch("%s written %s, manifest pin %s%s" % (
            asset.name, written_sha, record["sha256"],
            " (a rolling asset whose allowlisted content changed: re-pin with a dated note)" if asset.rolling else ""))


def _roster_ids(dest):
    ids = set()
    for asset in ASSETS:
        if asset.kind in ("roster", "roster_weekly"):
            with open(Path(dest) / asset.name, newline="", encoding="utf-8") as f:
                ids.update(r["gsis_id"] for r in csv.DictReader(f) if r.get("gsis_id"))
    return ids


def fetch(dest, only=None, manifest=None, fetcher=_fetch, log=print):
    """Download, verify, cut and write each asset; returns the per-asset records."""
    dest = guard_dest(dest)
    dest.mkdir(parents=True, exist_ok=True)
    anchors = anchor_pins()
    records = {}
    for asset in FETCH_ORDER:
        if only and asset.name not in only:
            continue
        raw = fetcher(asset.url)
        raw_sha = sha256(raw)
        verify_fetched(asset, raw_sha, manifest, anchors)
        known = _roster_ids(dest) if asset.kind == "players" else None
        data, rows_in, rows_out, header = produce(asset, raw, known)
        written_sha = sha256(data)
        verify_written(asset, written_sha, manifest)
        tmp = dest / (asset.name + ".part")
        tmp.write_bytes(data)
        tmp.replace(dest / asset.name)
        record = {"url": asset.url, "publisher": asset.publisher, "kind": asset.kind, "season": asset.season,
                  "rolling": asset.rolling, "fetched_as": asset.fetched_as, "fetched_sha256": raw_sha,
                  "fetched_bytes": len(raw), "cut": asset.cut, "sha256": written_sha, "bytes": len(data)}
        if rows_in is not None:
            record.update(rows_fetched=rows_in, rows_written=rows_out)
        if asset.kind == "stats_player_week":
            record["columns_dropped"] = list(STATS_WEEK_DROPPED)
        if asset.kind in ("players", "draft_picks"):
            record["columns"] = header
        records[asset.name] = record
        log("%-34s fetched %s  written %s" % (asset.name, raw_sha[:12], written_sha[:12]))
    return records


# ---------------------------------------------------------- the 2014 cut
def cut_summary(dest):
    """Games, rows and the latest date of the written 2014 cut files (re-gated on read)."""
    dest = Path(dest)
    summary = {}
    with open(dest / "play_by_play_2014w4.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert_rows_admissible(rows, CUT_SEASON)
    games = {}
    for r in rows:
        games.setdefault(r["game_id"], (int(r["week"]), r["game_date"]))
    by_week = [sum(1 for w, _ in games.values() if w == k) for k in range(1, MAX_WEEK + 1)]
    summary["nflverse"] = {"rows": len(rows), "games": len(games), "games_by_week": by_week,
                           "latest_game_date": max(d for _, d in games.values())}
    with open(dest / "reg_pbp_2014w4.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert_rows_admissible(rows, CUT_SEASON)
    dates = {r["game_id"]: r["game_date"] for r in rows}
    summary["nflscrapR"] = {"rows": len(rows), "games": len(dates), "latest_game_date": max(dates.values())}
    for asset in ASSETS:
        if asset.season == CUT_SEASON and asset.kind not in ("pbp", "reg_pbp"):
            with open(dest / asset.name, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            assert_rows_admissible(rows, CUT_SEASON)
            weeks = sorted({int(r["week"]) for r in rows if r.get("week")})
            summary[asset.name] = {"rows": len(rows), "weeks": weeks}
    return summary


def cut_errors(summary):
    errors = []
    nflverse, scrapr = summary["nflverse"], summary["nflscrapR"]
    if nflverse["games"] != CUT["games"] or nflverse["games_by_week"] != CUT["games_by_week"]:
        errors.append("nflverse 2014 cut: %s games by week %s, specification %s %s" % (
            nflverse["games"], nflverse["games_by_week"], CUT["games"], CUT["games_by_week"]))
    if nflverse["rows"] != CUT["rows_nflverse"]:
        errors.append("nflverse 2014 cut: %d rows, specification %d" % (nflverse["rows"], CUT["rows_nflverse"]))
    if scrapr["games"] != CUT["games"] or scrapr["rows"] != CUT["rows_nflscrapr"]:
        errors.append("nflscrapR 2014 cut: %d games, %d rows, specification %d, %d" % (
            scrapr["games"], scrapr["rows"], CUT["games"], CUT["rows_nflscrapr"]))
    for part in (nflverse, scrapr):
        if part["latest_game_date"] != MAX_DATE:
            errors.append("2014 cut latest game date %s, specification %s" % (part["latest_game_date"], MAX_DATE))
    return errors


# ------------------------------------------------------------- manifest
def build_manifest(records, summary):
    return {
        "schema_version": SCHEMA_VERSION,
        "built_by": "scripts/research/sources_2010_2014.py",
        "specification_sha256": pre_build_specification.digest(),
        "fetch_date": date.today().isoformat(),
        "status": "research only; read by the kernel 2014.6 builders, never by runtime/",
        "attribution": ATTRIBUTION,
        "gate": {"seasons": list(SEASONS), "cut_2014": {"season_type": "REG", "max_week": MAX_WEEK,
                                                         "max_date": MAX_DATE},
                 "refused": [why for _, why in REFUSED] + ["any path under career/"],
                 "players_columns": list(PLAYERS_COLUMNS), "draft_picks_columns": list(DRAFT_PICKS_COLUMNS),
                 "stats_player_week_columns_dropped": list(STATS_WEEK_DROPPED),
                 "players_rows": "draft_year <= 2014, or an undrafted gsis_id on a written 2010-2014 roster file",
                 "draft_picks_rows": "season <= 2014"},
        "pins": "fetched_sha256 is the full fetched asset (2014: verified in memory before the cut); sha256 is "
                "the written file. A rolling asset's fetched digest is provenance only; its written file is pinned.",
        "cut_2014": summary,
        "assets": records,
    }


def manifest_errors(manifest):
    """The committed manifest against the committed anchors, the specification and the asset table."""
    errors = []
    if manifest is None:
        return ["manifest %s missing" % MANIFEST.relative_to(ROOT)]
    if manifest.get("specification_sha256") != pre_build_specification.FROZEN_SHA256:
        errors.append("manifest specification digest differs from the frozen pin")
    anchors = anchor_pins()
    assets = manifest.get("assets", {})
    if sorted(assets) != sorted(BY_NAME):
        errors.append("manifest assets differ from ASSETS: missing %s, extra %s" % (
            sorted(set(BY_NAME) - set(assets)), sorted(set(assets) - set(BY_NAME))))
    for name, record in assets.items():
        try:
            refuse_name(name)
        except SourceRefused as exc:
            errors.append(str(exc))
            continue
        asset = BY_NAME[name]
        for key in ("fetched_sha256", "sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", record.get(key, "")):
                errors.append("%s: %s is not a full sha256" % (name, key))
        anchor = anchors.get(asset.fetched_as)
        if anchor is not None and record.get("fetched_sha256") != anchor:
            errors.append("%s: fetched pin %s differs from the committed pin %s" % (
                name, record.get("fetched_sha256"), anchor))
        if not asset.cut and record.get("sha256") != record.get("fetched_sha256"):
            errors.append("%s is written as fetched, so both digests must agree" % name)
        if record.get("rolling") != asset.rolling or record.get("url") != asset.url:
            errors.append("%s: url or rolling flag differs from ASSETS" % name)
        if asset.kind == "players" and record.get("columns") != list(PLAYERS_COLUMNS):
            errors.append("players.csv columns are not the allowlist")
        if asset.kind == "draft_picks" and record.get("columns") != list(DRAFT_PICKS_COLUMNS):
            errors.append("draft_picks.csv columns are not the allowlist")
    if "cut_2014" in manifest:
        errors.extend(cut_errors(manifest["cut_2014"]))
    else:
        errors.append("manifest lacks the 2014 cut summary")
    return errors


# ------------------------------------------------------------ builder API
def source_path(name, dest, manifest=None):
    """A verified local source file: refused names fail, and its digest must equal the manifest pin."""
    asset = refuse_name(name)
    path = guard_path(Path(dest) / asset.name)
    manifest = manifest if manifest is not None else load_manifest()
    if manifest is None:
        raise SourceMismatch("no sources manifest; run --fetch --write-manifest first")
    pin = manifest["assets"][asset.name]["sha256"]
    actual = sha256_file(path)
    if actual != pin:
        raise SourceMismatch("%s is %s, manifest pin %s" % (path, actual, pin))
    return path


def rows(name, dest, manifest=None):
    """The rows of a verified source, re-gated: a row outside the gate raises."""
    path = source_path(name, dest, manifest)
    asset = BY_NAME[Path(name).name]
    opener = gzip.open if path.name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            errors = row_errors(row, asset.season) if asset.kind not in ("players", "draft_picks") else []
            if errors:
                raise SourceRefused("%s row %d: %s" % (asset.name, i, "; ".join(errors)))
            yield row


def check(dest=None, manifest=None):
    """Manifest consistency always; file digests and the 2014 cut when the sources are present."""
    manifest = manifest if manifest is not None else load_manifest()
    errors = manifest_errors(manifest)
    if errors or dest is None:
        return errors, False
    dest = Path(dest)
    present = [a for a in ASSETS if (dest / a.name).exists()]
    if len(present) != len(ASSETS):
        return errors, False
    for asset in ASSETS:
        actual = sha256_file(dest / asset.name)
        if actual != manifest["assets"][asset.name]["sha256"]:
            errors.append("%s: %s, manifest pin %s" % (asset.name, actual, manifest["assets"][asset.name]["sha256"]))
    if not errors:
        summary = cut_summary(dest)
        errors.extend(cut_errors(summary))
        if summary != manifest["cut_2014"]:
            errors.append("the 2014 cut summary differs from the manifest")
    return errors, True


def default_dest():
    value = os.environ.get("SOURCES_2010_2014_DIR")
    return Path(value) if value else None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fetch", action="store_true", help="download, verify, cut and write the sources")
    parser.add_argument("--check", action="store_true", help="verify the manifest, and the files when present")
    parser.add_argument("--dest", type=Path, default=default_dest(),
                        help="source directory outside the repository (default $SOURCES_2010_2014_DIR)")
    parser.add_argument("--only", nargs="*", help="limit --fetch to these asset names")
    parser.add_argument("--write-manifest", action="store_true", help="write the committed manifest from a full fetch")
    parser.add_argument("--repin", action="store_true", help="allow --write-manifest to replace different pins")
    args = parser.parse_args(argv)
    manifest = load_manifest()
    if args.fetch:
        if args.dest is None:
            parser.error("--fetch needs --dest or $SOURCES_2010_2014_DIR")
        if args.write_manifest and args.only:
            parser.error("--write-manifest needs a full fetch")
        records = fetch(args.dest, set(args.only or ()), None if args.repin else manifest)
        if args.write_manifest:
            new = build_manifest(records, cut_summary(args.dest))
            errors = manifest_errors(new)
            if errors:
                for error in errors:
                    print("ERROR: " + error)
                return 1
            if manifest is not None and not args.repin and {k: v["sha256"] for k, v in manifest["assets"].items()} \
                    != {k: v["sha256"] for k, v in new["assets"].items()}:
                print("ERROR: pins differ from the committed manifest; --repin with a dated note to replace them")
                return 1
            if manifest is not None and not args.repin:
                new["fetch_date"] = manifest["fetch_date"]
            MANIFEST.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            print("wrote %s" % MANIFEST.relative_to(ROOT))
    if args.check or not args.fetch:
        errors, files = check(args.dest)
        for error in errors:
            print("ERROR: " + error)
        if errors:
            return 1
        print("sources manifest OK" + ("; every file and the 2014 cut verified" if files
                                       else "; source files not present, file checks skipped"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
