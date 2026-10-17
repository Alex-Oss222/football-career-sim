"""Kernel 2014.6 batch B2: the shared sources module and its information gate
(scripts/research/sources_2010_2014.py, library/data/2010_2014_sources_manifest.json).

No network. The file checks run only when the fetched sources are present
($SOURCES_2010_2014_DIR); they are skipped otherwise, as raw data stays out of
the repository.
"""
import csv
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/research"))
import sources_2010_2014 as sources  # noqa: E402


def table(header, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


def read(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


class GateTests(unittest.TestCase):
    def test_rows_after_the_cut_are_rejected(self):
        week4 = {"season": "2014", "season_type": "REG", "week": "4", "game_date": "2014-09-29"}
        self.assertEqual(sources.row_errors(week4, 2014), [])
        for change in ({"week": "5"}, {"game_date": "2014-10-02"}, {"week": "5", "game_date": "2014-10-02"},
                       {"season_type": "POST"}, {"week": ""}):
            row = dict(week4, **change)
            self.assertTrue(sources.row_errors(row, 2014), change)
            with self.assertRaises(sources.SourceRefused):
                sources.assert_rows_admissible([week4, row], 2014)
        # An injury report modified on October 2 is outside the gate even when filed under week 4.
        report = {"season": "2014", "game_type": "REG", "week": "4", "date_modified": "2014-10-02T15:00:00Z"}
        self.assertTrue(sources.row_errors(report, 2014))
        # nflscrapR rows carry a date but no week.
        self.assertTrue(sources.row_errors({"game_id": "2014100200", "game_date": "2014-10-02"}, 2014))
        self.assertEqual(sources.row_errors({"game_id": "2014092900", "game_date": "2014-09-29"}, 2014), [])
        # A 2014 row with nothing to cut on is refused, never assumed inside the window.
        self.assertTrue(sources.row_errors({"season": "2014", "team": "MIN"}, 2014))

    def test_later_seasons_are_refused(self):
        self.assertTrue(sources.row_errors({"season": "2015", "week": "1"}, None))
        self.assertEqual(sources.row_errors({"season": "2013", "week": "17"}, 2013), [])
        for name in ("play_by_play_2015.csv.gz", "roster_weekly_2016.csv", "pbp_participation_2016.csv",
                     "ftn_charting_2022.csv"):
            with self.assertRaises(sources.SourceRefused):
                sources.refuse_name(name)

    def test_the_cut_writes_only_admissible_rows(self):
        asset = sources.BY_NAME["roster_weekly_2014w4.csv"]
        text = table(["season", "game_type", "week", "gsis_id"],
                     [["2014", "REG", "1", "a"], ["2014", "REG", "4", "b"], ["2014", "REG", "5", "c"],
                      ["2014", "POST", "18", "d"], ["2014", "REG", "17", "e"]])
        data, rows_in, rows_out, _ = sources.cut_table(asset, text)
        self.assertEqual((rows_in, rows_out), (5, 2))
        self.assertEqual([r["gsis_id"] for r in read(data)], ["a", "b"])
        pbp = sources.BY_NAME["play_by_play_2014w4.csv"]
        text = table(["game_id", "season_type", "week", "game_date"],
                     [["2014_04_NE_KC", "REG", "4", "2014-09-29"], ["2014_05_MIN_GB", "REG", "5", "2014-10-02"]])
        self.assertEqual([r["game_id"] for r in read(sources.cut_table(pbp, text)[0])], ["2014_04_NE_KC"])

    def test_stats_player_reg_is_refused(self):
        for name in ("stats_player_reg_2010.csv", "stats_player_reg_2013.csv", "stats_player_reg_2014.csv"):
            with self.assertRaises(sources.SourceRefused) as caught:
                sources.refuse_name(name)
            self.assertIn("season-aggregate", str(caught.exception))
        self.assertFalse(any("stats_player_reg" in a.url or "stats_player_reg" in a.name for a in sources.ASSETS))

    def test_full_season_2014_files_are_refused(self):
        for name in ("play_by_play_2014.csv.gz", "reg_pbp_2014.csv", "injuries_2014.csv", "roster_2014.csv",
                     "snap_counts_2014.csv", "depth_charts_2014.csv", "stats_player_week_2014.csv"):
            with self.assertRaises(sources.SourceRefused):
                sources.refuse_name(name)
        for asset in sources.ASSETS:
            if asset.season == 2014:
                self.assertTrue(asset.cut and "2014w4" in asset.name, asset.name)

    def test_career_reads_are_refused(self):
        for path in (ROOT / "career/2014/stats/game_receipts/x.json", ROOT / "career",
                     ROOT / "career/2014/../2014/roster.md"):
            with self.assertRaises(sources.SourceRefused):
                sources.guard_path(path)
        with self.assertRaises(sources.SourceRefused):
            sources.source_path("play_by_play_2012.csv.gz", ROOT / "career/2014")
        with self.assertRaises(sources.SourceRefused):
            sources.guard_dest(ROOT / "library/raw")
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(sources.guard_dest(tmp), Path(tmp).resolve())

    def test_allowlists_are_enforced(self):
        players = sources.BY_NAME["players.csv"]
        header = ["gsis_id", "display_name", "birth_date", "position", "rookie_season", "last_season", "status",
                  "years_of_experience", "pff_id", "pfr_id", "draft_year", "draft_round", "draft_pick", "draft_team",
                  "latest_team"]
        text = table(header, [
            ["00-1", "A", "1985-01-01", "QB", "2008", "2019", "RET", "11", "1", "A1", "2008", "1", "3", "BAL", "X"],
            ["00-2", "B", "1997-01-01", "QB", "2019", "2024", "ACT", "6", "2", "B1", "2019", "1", "1", "ARI", "Y"],
            ["00-3", "C", "1990-01-01", "LB", "2013", "2016", "RET", "3", "3", "C1", "", "", "", "", "Z"],
            ["00-4", "D", "1999-01-01", "LB", "2022", "2023", "ACT", "1", "4", "D1", "", "", "", "", "W"]])
        data, rows_in, rows_out, kept = sources.cut_table(players, text, known_ids={"00-3"})
        self.assertEqual(kept, list(sources.PLAYERS_COLUMNS))
        out = read(data)
        self.assertEqual([r["gsis_id"] for r in out], ["00-1", "00-3"])  # later classes and unknown ids dropped
        for forbidden in sources.PLAYERS_NEVER + ("position", "display_name", "latest_team"):
            self.assertNotIn(forbidden, out[0])
        picks = sources.BY_NAME["draft_picks.csv"]
        header = ["season", "round", "pick", "team", "gsis_id", "pfr_player_name", "position", "to", "allpro",
                  "probowls", "seasons_started", "w_av", "car_av", "games", "pass_yards"]
        text = table(header, [["2012", "1", "1", "IND", "00-9", "N", "QB", "2023", "0", "4", "90", "1", "1", "1", "9"],
                              ["2015", "1", "1", "TB", "00-8", "M", "QB", "2023", "0", "3", "90", "1", "1", "1", "9"]])
        data, _, _, kept = sources.cut_table(picks, text)
        self.assertEqual(kept, list(sources.DRAFT_PICKS_COLUMNS))
        out = read(data)
        self.assertEqual([r["season"] for r in out], ["2012"])
        for forbidden in sources.DRAFT_PICKS_NEVER + ("pass_yards", "pfr_player_name"):
            self.assertNotIn(forbidden, out[0])
        week = sources.BY_NAME["stats_player_week_2013.csv"]
        data, _, _, kept = sources.cut_table(week, table(
            ["player_id", "position", "position_group", "headshot_url", "season", "week", "carries"],
            [["00-1", "RB", "RB", "u", "2013", "1", "20"]]))
        self.assertEqual(kept, ["player_id", "season", "week", "carries"])
        with self.assertRaises(sources.SourceMismatch):
            sources.kept_columns("players", ["gsis_id", "birth_date"])

    def test_nflcom_table_parser(self):
        cells = "".join("<td><span>%s</span><span>%s</span></td>" % (t, t) if i == 0 else "<td>%s</td>" % t
                        for i, t in enumerate(["Lions", "740", "57T"]))
        page = "<html><table><thead><tr><th>Team</th><th>Att</th><th>Lng</th></tr></thead><tbody><tr>%s</tr>" \
               "</tbody></table></html>" % cells
        self.assertEqual(sources.parse_nflcom_table(page), (["Team", "Att", "Lng"], [["Lions", "740", "57T"]]))
        with self.assertRaises(sources.SourceMismatch):
            sources.parse_nflcom_table(page + page)

    def test_fetch_fails_closed_on_a_pin_mismatch(self):
        manifest = sources.load_manifest()
        asset = sources.BY_NAME["play_by_play_2012.csv.gz"]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(sources.SourceMismatch):
                sources.fetch(tmp, only={asset.name}, manifest=manifest, fetcher=lambda url: b"not the asset",
                              log=lambda *a: None)
            self.assertFalse((Path(tmp) / asset.name).exists())
            # A rolling asset may change its fetched bytes, but not its written cut.
            players = sources.BY_NAME["players.csv"]
            for kind in ("roster", "roster_weekly"):
                for a in sources.ASSETS:
                    if a.kind == kind:
                        (Path(tmp) / a.name).write_text("gsis_id\n", encoding="utf-8")
            fake = table(list(sources.PLAYERS_COLUMNS), [["00-1", "1980-01-01", "2002", "1", "1", "HOU", "", ""]])
            with self.assertRaises(sources.SourceMismatch):
                sources.fetch(tmp, only={players.name}, manifest=manifest, fetcher=lambda url: fake.encode(),
                              log=lambda *a: None)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = sources.load_manifest()

    def test_manifest_is_consistent(self):
        self.assertEqual(sources.manifest_errors(self.manifest), [])

    def test_play_by_play_pins_are_the_committed_pins(self):
        production = json.loads((ROOT / "library/data/2010_2012_production_evidence.json").read_text())["sources"]
        persistence = json.loads((ROOT / "library/data/passer_interception_persistence.json").read_text())["sources"]
        assets = self.manifest["assets"]
        for season in (2010, 2011, 2012):
            name = "play_by_play_%d.csv.gz" % season
            self.assertEqual(assets[name]["fetched_sha256"], production[name]["sha256"])
            self.assertEqual(assets[name]["sha256"], production[name]["sha256"])
        for season, name in ((2013, "play_by_play_2013.csv.gz"), (2014, "play_by_play_2014w4.csv")):
            self.assertEqual(assets[name]["fetched_sha256"],
                             persistence["play_by_play_%d.csv.gz" % season]["sha256"])
        frozen = sources.pre_build_specification.frozen_rules()["data_window"]["nflscrapr_reg_pbp_fetch_sha256"]
        for season, pin in frozen.items():
            name = "reg_pbp_%sw4.csv" % season if season == "2014" else "reg_pbp_%s.csv" % season
            self.assertEqual(assets[name]["fetched_sha256"], pin)

    def test_the_2014_cut_is_the_specification_cut(self):
        cut = self.manifest["cut_2014"]
        self.assertEqual(cut["nflverse"], {"rows": 10893, "games": 61, "games_by_week": [16, 16, 16, 13],
                                           "latest_game_date": "2014-09-29"})
        self.assertEqual(cut["nflscrapR"], {"rows": 10852, "games": 61, "latest_game_date": "2014-09-29"})
        for name, part in cut.items():
            if "weeks" in part:
                self.assertTrue(set(part["weeks"]) <= {1, 2, 3, 4}, name)

    def test_errors_are_caught(self):
        broken = json.loads(json.dumps(self.manifest))
        broken["assets"]["play_by_play_2011.csv.gz"]["fetched_sha256"] = "0" * 64
        broken["assets"]["players.csv"]["columns"].append("status")
        broken["cut_2014"]["nflverse"]["games_by_week"] = [16, 16, 16, 14]
        broken["assets"]["stats_player_reg_2013.csv"] = {}
        errors = sources.manifest_errors(broken)
        self.assertTrue(any("play_by_play_2011" in e for e in errors))
        self.assertTrue(any("players.csv columns" in e for e in errors))
        self.assertTrue(any("games by week" in e for e in errors))
        self.assertTrue(any("season-aggregate" in e for e in errors))

    def test_no_row_level_data_is_committed(self):
        def walk(value):
            if isinstance(value, dict):
                for v in value.values():
                    yield from walk(v)
            elif isinstance(value, list):
                yield value
                for v in value:
                    yield from walk(v)
        for value in walk(self.manifest):
            self.assertLess(len(value), 64)

    def test_runtime_never_imports_the_sources(self):
        for path in (ROOT / "runtime").rglob("*.py"):
            self.assertNotIn("sources_2010_2014", path.read_text(encoding="utf-8"), path)


@unittest.skipUnless(sources.default_dest() and sources.default_dest().is_dir(),
                     "fetched sources not present ($SOURCES_2010_2014_DIR)")
class PresentSourcesTests(unittest.TestCase):
    def test_check(self):
        errors, files = sources.check(sources.default_dest())
        self.assertEqual(errors, [])
        self.assertTrue(files)

    def test_rows_are_regated(self):
        rows = list(sources.rows("injuries_2014w4.csv", sources.default_dest()))
        self.assertTrue(rows)
        self.assertTrue(all(int(r["week"]) <= 4 for r in rows))


if __name__ == "__main__":
    unittest.main()
