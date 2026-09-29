"""Season isolation for the closure, input, receipt, stat and standings paths.

The acceptance test for the 2014 closure prerequisite (runtime/defect_register.md):
a synthetic 2014 closure writes only to its isolated 2014 test workspace; the
2013 canon remains byte-identical; no career game runs in a test.

The synthetic workspace is a temporary directory with a two-game 2014 slate,
fake clubs, a fake Jacksonville roster, depth chart and call sheet. Its games
close through the production runner with a fake private client (the real
service is never contacted: constructing the real client fails the test).
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from runtime import depth_library, postseason, week_inputs
from runtime.season import SeasonDataMissing, season_of_event, season_paths
from runtime.usage import group
from scripts import build_week_inputs, close_week
from scripts.render_season_stats import load_receipts, render_views
from scripts.render_standings import render as render_standings
from scripts.validate_repository import season_output_errors, season_stat_errors

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_game_readiness import season_blockers  # noqa: E402  (imports validate_repository by name)

JAX = "Jacksonville Jaguars"
GAMES = (("Tennessee Titans", JAX), ("Buffalo Bills", "Houston Texans"))
LAYOUT = (("QB", 2), ("RB", 3), ("FB", 1), ("WR", 5), ("TE", 3), ("OT", 4), ("OG", 3), ("C", 2),
          ("DE", 4), ("DT", 3), ("LB", 5), ("CB", 5), ("S", 4), ("K", 1), ("P", 1), ("LS", 1))
ROLES = {"QB1": ["passer"], "K1": ["placekicker"], "P1": ["punt"], "WR3": ["kick_return", "punt_return"]}
# Jacksonville's week-6 families (from the synthetic kernel sample): every call is labellable.
SHEET = [
    {"name": "12 Ace Right, Power R", "family": "Power", "type": "run", "personnel": "12", "formation": "12 Ace Right"},
    {"name": "12 Trey Right, Stick, H Chip-Release", "family": "Stick", "type": "pass", "personnel": "12", "formation": "12 Trey Right"},
    {"name": "11 Bunch Right, Return, Mesh", "family": "Mesh", "type": "pass", "personnel": "11", "formation": "11 Bunch Right"},
    {"name": "12 Wing Right, Split L", "family": "Split Zone", "type": "run", "personnel": "12", "formation": "12 Wing Right"},
]


def tree_digest(path):
    digest = hashlib.sha256()
    for item in sorted(p for p in Path(path).rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode() + b"\0" + item.read_bytes())
    return digest.hexdigest()


def players(club):
    code = "".join(word[0] for word in club.split())
    return [("%s %s%d" % (code, pos, n), pos, n) for pos, count in LAYOUT for n in range(1, count + 1)]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if isinstance(text, str) else json.dumps(text, indent=1), encoding="utf-8")


def build_workspace(root):
    """A synthetic 2014 workspace: nothing in it is real or career data."""
    write(root / "state/05_Current_Season_State.md", "| Master date/time | September 1, 2014 |\n")
    write(root / "library/data/2014_schedule.json", {
        "season": 2014, "source": "synthetic test slate",
        "games": [{"week": 1, "date": "2014-09-07", "weekday": "Sunday", "kickoff_et": "1:00 PM",
                   "away": away, "home": home, "site": "home", "stadium": "Test Stadium"}
                  for away, home in GAMES]})
    clubs = {}
    for club in {team for game in GAMES for team in game} - {JAX}:
        clubs[club] = {"code": club, "players": [
            {"player_id": name, "position": pos, "depth": n,
             **({"roles": ROLES["%s%d" % (pos, n)]} if "%s%d" % (pos, n) in ROLES else {})}
            for name, pos, n in players(club)]}
    write(root / "library/data/2014_week1_depth_charts.json", {"season": 2014, "clubs": clubs})
    everyone = [name for club in set(t for g in GAMES for t in g) for name, _, _ in players(club)]
    write(root / "library/data/player_birth_dates.json", {"schema_version": 1, "players": {
        name: {"gsis_id": "TEST-%04d" % i, "birth_date": "1990-01-01", "sources": ["synthetic"]}
        for i, name in enumerate(sorted(everyone))}})
    jax = players(JAX)
    rows = ["| Player | Pos | Status | Availability |", "| --- | --- | --- | --- |"]
    rows += ["| %s | %s | Active 53 | No communicated restriction |" % (name, pos) for name, pos, _ in jax]
    write(root / "career/2014/roster.md", "# Synthetic roster\n\n" + "\n".join(rows) + "\n")
    depth = {}
    for name, pos, n in jax:
        depth.setdefault(group(pos), []).append(name)
    write(root / "career/2014/depth_chart.json", {
        "depth": depth, "positions": {name: pos for name, pos, _ in jax},
        "roles": {name: ROLES["%s%d" % (pos, n)] for name, pos, n in jax if "%s%d" % (pos, n) in ROLES},
        "game_day_inactives": {"players": ["JJ S4"]}})
    week = root / "career/2014/regular_season/week_01_tennessee_at_jacksonville"
    write(week / "call_sheet.json", {"offensive_call_sheet": SHEET})
    write(week / "output.md", "# Week 1\n\n<!-- box-score event=2014-week01-tennessee-titans-at-"
                              "jacksonville-jaguars team=Jacksonville Jaguars -->\n<!-- /box-score -->\n")


class FakeClient:
    """Stands in for the private service: a stable opaque reference per event."""

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.closed = []

    def close_event(self, packet):
        self.closed.append(packet["event_id"])
        return hashlib.sha256(("synthetic:" + packet["event_id"]).encode()).hexdigest()


def quiet(function, *args, **kwargs):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = function(*args, **kwargs)
    return code, out.getvalue()


class SyntheticSeasonClosureTests(unittest.TestCase):
    def test_2014_closure_writes_only_to_its_isolated_workspace(self):
        canon_before = tree_digest(ROOT / "career/2013")
        library_before = tree_digest(ROOT / "library/data")
        cache_before = tree_digest(ROOT / ".sim_cache") if (ROOT / ".sim_cache").exists() else None
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build_workspace(root)
            before = {p for p in root.rglob("*") if p.is_file()}

            code, text = quiet(build_week_inputs.build, 1, 2014, root)
            self.assertEqual(code, 0, text)
            package_path = root / ".sim_cache/2014/week_01_inputs.json"
            package = json.loads(package_path.read_text())
            self.assertEqual(package["season"], 2014)
            event_ids = [g["event_id"] for g in package["games"]]
            self.assertEqual(len(event_ids), 2)
            self.assertTrue(all(e.startswith("2014-week01-") for e in event_ids), event_ids)

            snapshot = hashlib.sha256((root / "state/05_Current_Season_State.md").read_bytes()).hexdigest()
            client = FakeClient(snapshot)
            with mock.patch("runtime.private_client.Client", side_effect=AssertionError("real service")):
                code, text = quiet(close_week.close_week, 1, season=2014, root=root, close=True,
                                   client=client, readiness=lambda season: season == 2014)
            self.assertEqual(code, 0, text)
            self.assertEqual(sorted(client.closed), sorted(event_ids))

            receipts = load_receipts(root / "career/2014/stats/game_receipts")
            self.assertEqual(sorted(r["event_id"] for r in receipts), sorted(event_ids))
            self.assertTrue(all(season_of_event(r["event_id"]) == 2014 for r in receipts))
            standings = (root / "career/2014/standings.md").read_text()
            self.assertTrue(standings.startswith("# 2014 NFL standings"))
            self.assertIn("not yet re-verified for 2014", standings)
            audit = (root / "career/2014/stats/calibration_audit.md").read_text()
            self.assertNotIn("Legacy cohort", audit)
            self.assertNotIn("Kernel 2013", audit)

            output = root / "career/2014/regular_season/week_01_tennessee_at_jacksonville/output.md"
            subprocess.run([sys.executable, str(ROOT / "scripts/render_box_score.py"), "--write",
                            str(output), "--root", str(root)], check=True, capture_output=True)
            self.assertIn("Tennessee Titans", output.read_text())

            # The same validation rules the 2013 season passes now read 2014.
            self.assertEqual(season_stat_errors(root, 2014), [])
            self.assertEqual(season_output_errors(root, 2014), [])

            # A replay reuses only this season's cached results: nothing redraws.
            client.closed.clear()
            code, text = quiet(close_week.close_week, 1, season=2014, root=root, close=True,
                               client=client, readiness=lambda season: True)
            self.assertEqual((code, client.closed), (0, []), text)

            # A cached result from another season is never reused.
            results = root / ".sim_cache/2014/week_01_results.json"
            data = json.loads(results.read_text())
            data["2013-week01-tennessee-titans-at-jacksonville-jaguars"] = {}
            results.write_text(json.dumps(data))
            code, text = quiet(close_week.close_week, 1, season=2014, root=root, close=True,
                               client=client, readiness=lambda season: True)
            self.assertEqual(code, 1)
            self.assertIn("another season", text)

            written = {p for p in root.rglob("*") if p.is_file()} - before
            for path in written:
                rel = path.relative_to(root).as_posix()
                self.assertTrue(rel.startswith(("career/2014/", ".sim_cache/2014/")), rel)
            self.assertFalse((root / "career/2013").exists())
        self.assertEqual(tree_digest(ROOT / "career/2013"), canon_before)
        self.assertEqual(tree_digest(ROOT / "library/data"), library_before)
        if cache_before is not None:
            self.assertEqual(tree_digest(ROOT / ".sim_cache"), cache_before)

    def test_isolated_workspace_cannot_bind_the_real_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, text = quiet(close_week.close_week, 1, season=2014, root=tmp, close=True)
        self.assertEqual(code, 1)
        self.assertIn("not this checkout", text)

    def test_package_from_another_season_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            build_workspace(root)
            self.assertEqual(quiet(build_week_inputs.build, 1, 2014, root)[0], 0)
            path = root / ".sim_cache/2014/week_01_inputs.json"
            package = json.loads(path.read_text())
            package["games"][0]["event_id"] = package["games"][0]["event_id"].replace("2014-", "2013-", 1)
            path.write_text(json.dumps(package))
            client = FakeClient("x")
            code, text = quiet(close_week.close_week, 1, season=2014, root=root, close=True,
                               client=client, readiness=lambda season: True)
        self.assertEqual((code, client.closed), (1, []))
        self.assertIn("is not a 2014 Week 1 event", text)


class RealRepository2014FailsClosedTests(unittest.TestCase):
    """The real checkout has no 2014 slate, library, roster or depth chart yet."""

    def test_missing_2014_prerequisites_raise_and_name_them(self):
        with self.assertRaisesRegex(SeasonDataMissing, "April 23, 2014 schedule gate"):
            week_inputs.schedule(1, 2014)
        with self.assertRaisesRegex(SeasonDataMissing, "depth library"):
            depth_library.team_input("Tennessee Titans", offense_anchor=2.0, defense_anchor=2.0,
                                     special_teams_anchor=2.0, season=2014)
        with self.assertRaisesRegex(SeasonDataMissing, "roster owner.*never feeds a 2014 game input"):
            week_inputs.controlled_active(2014)
        with self.assertRaisesRegex(SeasonDataMissing, "postseason slots"):
            postseason.schedule(18, season=2014)
        for error in (SeasonDataMissing,):
            self.assertTrue(issubclass(error, ValueError))

    def test_2014_build_and_close_are_blocked_without_writing(self):
        cache = ROOT / ".sim_cache/2014"
        existed = cache.exists()
        code, text = quiet(build_week_inputs.build, 1, 2014)
        self.assertEqual(code, 1)
        self.assertIn("never falls back to 2013", text)
        with mock.patch("runtime.private_client.Client", side_effect=AssertionError("real service")):
            code, text = quiet(close_week.close_week, 1, season=2014, close=True)
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED", text)
        self.assertEqual(cache.exists(), existed)

    def test_2014_readiness_is_blocked_on_rules_and_data(self):
        details = " ".join(b["detail"] for b in season_blockers(ROOT, 2014))
        self.assertIn("no verified 2014 playing rules", details)
        self.assertIn("no 2014 schedule", details)
        self.assertEqual(season_blockers(ROOT, 2013), [])

    def test_unverified_season_is_refused(self):
        with self.assertRaises(ValueError):
            season_paths(2015)


class SeasonKeyTests(unittest.TestCase):
    def test_event_ids_and_voids_are_per_season(self):
        game = {"week": 14, "away": "Houston Texans", "home": JAX}
        self.assertEqual(week_inputs.event_id(game), "2013-week14-houston-texans-at-jacksonville-jaguars-g2")
        # 2013's Week 14 void does not follow the week number into 2014.
        self.assertEqual(week_inputs.event_generation(14, 2014), 1)
        self.assertEqual(week_inputs.event_id(game, season=2014),
                         "2014-week14-houston-texans-at-jacksonville-jaguars")

    def test_cache_is_namespaced_by_season(self):
        self.assertEqual(season_paths(2013).inputs_cache(11), ROOT / ".sim_cache/week_11_inputs.json")
        self.assertEqual(season_paths(2014).results_cache(11), ROOT / ".sim_cache/2014/week_11_results.json")

    def test_dated_return_without_a_year_is_read_in_the_season(self):
        note = "Out, lower extremity; projected return August 20"
        from datetime import date
        self.assertFalse(week_inputs.roster_available(note, date(2014, 8, 14), 2014))
        self.assertTrue(week_inputs.roster_available(note, date(2014, 8, 22), 2014))

    def test_super_bowl_title_follows_the_season(self):
        self.assertEqual(postseason.round_titles(2013)["super_bowl"], "Super Bowl XLVIII")
        self.assertEqual(postseason.round_titles(2014)["super_bowl"], "Super Bowl XLIX")

    def test_draft_order_stays_on_2013_receipts(self):
        from runtime import draft_order
        self.assertEqual(draft_order.REGULAR_RECEIPTS, ROOT / "career/2013/stats/game_receipts")
        self.assertEqual(draft_order.POSTSEASON_RECEIPTS, ROOT / "career/2013/stats/postseason_receipts")


class Closed2013ViewsAreByteIdenticalTests(unittest.TestCase):
    """2013 defaults reproduce the committed generated views exactly."""

    # calibration_audit.md is left to validate_repository: it is regenerated
    # at the kernel release that adds its new coherence classes.
    SKIP = {"calibration_audit.md"}

    def test_in_process_renderers_match_committed_views(self):
        stats = ROOT / "career/2013/stats"
        receipts = load_receipts(stats / "game_receipts")
        for name, text in render_views(2013, JAX, receipts).items():
            if name not in self.SKIP:
                self.assertEqual((stats / name).read_text(encoding="utf-8"), text, name)
        self.assertEqual((ROOT / "career/2013/standings.md").read_text(encoding="utf-8"),
                         render_standings(2013, receipts))

    def test_command_line_renderers_match_committed_views(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy = root / "career/2013/stats/game_receipts"
            copy.mkdir(parents=True)
            for path in (ROOT / "career/2013/stats/game_receipts").glob("*.json"):
                (copy / path.name).write_bytes(path.read_bytes())
            subprocess.run([sys.executable, str(ROOT / "scripts/render_season_stats.py"), "2013",
                            "--team", JAX, "--root", str(root)], check=True, capture_output=True)
            subprocess.run([sys.executable, str(ROOT / "scripts/render_standings.py"), "2013",
                            "--root", str(root)], check=True, capture_output=True)
            for path in sorted((root / "career/2013/stats").glob("*.*")):
                if path.name not in self.SKIP:
                    self.assertEqual(path.read_bytes(), (ROOT / "career/2013/stats" / path.name).read_bytes(),
                                     path.name)
            self.assertEqual((root / "career/2013/standings.md").read_bytes(),
                             (ROOT / "career/2013/standings.md").read_bytes())

    def test_box_scores_match_their_receipts(self):
        errors = season_output_errors(ROOT, 2013)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
