"""League player cards (runtime/player_cards.py, scripts/render_player_cards.py).

The committed career/league_players folder must equal a fresh render of the
committed game records; every SVG is a static image GitHub can show; the
numbers on a card and a page equal the statbook's totals; a field the records
do not hold reads N/A; and every link resolves.
"""
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime import player_cards  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.statbook import aggregate_receipts  # noqa: E402
from runtime.stat_tables import rating_value, thrown  # noqa: E402
from scripts import render_player_cards  # noqa: E402

FOLDER = ROOT / player_cards.FOLDER
SVG = "{http://www.w3.org/2000/svg}"
_RENDER = None
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        _DATA = player_cards.card_data(ROOT)
        player_cards.assign_slugs(_DATA["players"])
    return _DATA


def rendered():
    global _RENDER
    if _RENDER is None:
        _RENDER = player_cards.render(ROOT)
    return _RENDER


def book(year, kind="regular"):
    paths = SeasonPaths(year, ROOT)
    folder = paths.receipts if kind == "regular" else paths.postseason_receipts
    return aggregate_receipts([json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))])


def page_rows(rel, heading="### Regular season"):
    """{season or 'Career': {column: cell}} from a player page's table under heading."""
    text = (ROOT / rel).read_text(encoding="utf-8")
    body = text.split(heading, 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
    lines = [l for l in body.splitlines() if l.startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    out = {}
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        out[cells[0].strip("*")] = dict(zip(head, cells))
    return out


def player(name, club):
    return next(p for p in data()["players"] if p["name"] == name and p["team"] == club)


def svg_tiles(path):
    """[(label, value)] in document order for each stat block of a card."""
    root = ET.fromstring(path.read_bytes())
    blocks = []
    for g in root.iter(SVG + "g"):
        if g.get("class") not in ("p", "c"):
            continue
        texts = [(t.get("class"), t.text) for t in g.iter(SVG + "text")]
        values = [v for c, v in texts if c == "v"]
        labels = [v for c, v in texts if c == "l"]
        title = next(v for c, v in texts if c == "bt")
        blocks.append((title, list(zip(labels, values))))
    return blocks


class CommittedFolderTests(unittest.TestCase):
    def test_committed_folder_is_current(self):
        self.assertEqual(player_cards.check(ROOT, rendered()), [])

    def test_script_check_passes_on_the_committed_state(self):
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(render_player_cards.main(["--check"]), 0)
        self.assertIn("CURRENT", out.getvalue())

    def test_render_is_deterministic(self):
        again = player_cards.render(ROOT)
        self.assertEqual(list(again), list(rendered()))
        self.assertEqual(again, rendered())

    def test_check_fails_on_a_stale_missing_or_extra_file_in_a_copy(self):
        expected = rendered()
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp)
            shutil.copytree(FOLDER, copy / player_cards.FOLDER)
            self.assertEqual(player_cards.check(copy, expected), [])
            page = copy / player_cards.FOLDER / "jacksonville_jaguars" / "kirk_cousins.md"
            page.write_text(page.read_text(encoding="utf-8").replace("| 2014 |", "| 2015 |"), encoding="utf-8")
            (copy / player_cards.FOLDER / "jacksonville_jaguars" / "README.md").unlink()
            (copy / player_cards.FOLDER / "jacksonville_jaguars" / "someone_else.md").write_text("x", encoding="utf-8")
            errors = player_cards.check(copy, expected)
            self.assertIn("League player cards stale: %s/jacksonville_jaguars/kirk_cousins.md" % player_cards.FOLDER, errors)
            self.assertIn("League player cards missing: %s/jacksonville_jaguars/README.md" % player_cards.FOLDER, errors)
            self.assertIn("League player cards has an unexpected file: %s/jacksonville_jaguars/someone_else.md"
                          % player_cards.FOLDER, errors)
            self.assertEqual(len(errors), 3)

    def test_counts_and_one_page_and_card_per_player(self):
        files = rendered()
        players = data()["players"]
        pages = [r for r in files if r.endswith(".md") and not r.endswith("README.md")]
        svgs = [r for r in files if r.endswith(".svg")]
        clubs = [r for r in files if r.endswith("/README.md") and r.count("/") == 3]
        self.assertEqual(len(pages), len(players))
        self.assertEqual(len(svgs), len(players))
        self.assertEqual(len(clubs), 32)
        self.assertEqual(len({p["key"] for p in players}), len(players))
        self.assertEqual(data()["unmatched_awards"], [])


class SvgTests(unittest.TestCase):
    def test_every_card_is_a_static_svg(self):
        svgs = sorted(FOLDER.rglob("*.svg"))
        self.assertEqual(len(svgs), sum(1 for r in rendered() if r.endswith(".svg")))
        for path in svgs:
            data = path.read_bytes()
            root = ET.fromstring(data)  # well-formed XML, text escaped
            self.assertEqual(root.tag, SVG + "svg", path)
            self.assertEqual((root.get("width"), root.get("height")), ("1280", "888"), path)
            self.assertEqual(root.get("viewBox"), "0 0 1280 888", path)
            tags = {el.tag.split("}")[-1] for el in root.iter()}
            self.assertFalse(tags & {"script", "foreignObject", "image", "a", "iframe", "use"}, path)
            self.assertEqual(sum(1 for el in root.iter(SVG + "style")), 1, path)
            for el in root.iter():
                for attr, value in el.attrib.items():
                    self.assertNotIn("href", attr, path)
                    self.assertFalse(attr.startswith("on"), path)
                    self.assertNotIn("url(", value, path)
            self.assertNotIn(b"@import", data)
            self.assertNotIn(b"http", data.replace(b'xmlns="http://www.w3.org/2000/svg"', b""), path)
            self.assertLess(len(data), 9000, path)

    def test_reader_words_stay_out_of_the_cards(self):
        banned = re.compile(r"\b(simulation|kernel|receipts?|engine|ledger|snapshot|checkpoint)\b", re.I)
        for rel, text in rendered().items():
            if rel.endswith(".svg"):
                body = re.sub(r"<style>.*?</style>", "", text, flags=re.S)
                self.assertIsNone(banned.search(body), rel)
                self.assertNotIn("—", text, rel)
            else:
                self.assertIsNone(banned.search(text), rel)
                self.assertNotIn("—", text, rel)


class ValueTests(unittest.TestCase):
    def test_jaguars_quarterback_equals_the_statbook(self):
        p = player("Kirk Cousins", "Jacksonville Jaguars")
        rel = "%s/jacksonville_jaguars/%s.md" % (player_cards.FOLDER, "kirk_cousins")
        rows = page_rows(rel)
        lines = {y: book(y)["players"]["Kirk Cousins"] for y in (2013, 2014)}
        for y, line in lines.items():
            row = rows[str(y)]
            self.assertEqual(row["G"], str(line["games"]))
            self.assertEqual(row["CMP-ATT"], "{:,}-{:,}".format(line["completions"], line["pass_attempts"]))
            self.assertEqual(row["YDS"], "{:,}".format(line["passing_yards"]))
            self.assertEqual(row["TD"], str(line["passing_touchdowns"]))
            self.assertEqual(row["INT"], str(thrown(line)))
            self.assertEqual(row["RATE"], "%.1f" % rating_value(line))
        both = {f: lines[2013].get(f, 0) + lines[2014].get(f, 0)
                for f in ("passing_yards", "passing_touchdowns", "completions", "pass_attempts", "games")}
        self.assertEqual(rows["Career"]["YDS"], "{:,}".format(both["passing_yards"]))
        self.assertEqual(rows["Career"]["G"], str(both["games"]))
        blocks = dict(svg_tiles(FOLDER / "jacksonville_jaguars" / "assets" / "kirk_cousins.svg"))
        self.assertEqual(dict(blocks["CAREER REGULAR SEASON"])["YDS"], "{:,}".format(both["passing_yards"]))
        self.assertEqual(dict(blocks["2014 REGULAR SEASON"])["TD"], str(lines[2014]["passing_touchdowns"]))
        self.assertEqual(p["career"]["regular"]["games"], both["games"])
        playoffs = book(2013, "playoffs")["players"]["Kirk Cousins"]
        self.assertEqual(page_rows(rel, "### Playoffs")["2013"]["YDS"], "{:,}".format(playoffs["passing_yards"]))
        self.assertEqual(dict(blocks["CAREER PLAYOFFS"])["YDS"], "{:,}".format(playoffs["passing_yards"]))

    def test_background_receiver_equals_the_statbook(self):
        rows = page_rows("%s/cincinnati_bengals/a_j_green.md" % player_cards.FOLDER)
        total = {"receptions": 0, "receiving_yards": 0, "targets": 0, "receiving_touchdowns": 0}
        for y in (2013, 2014):
            line = book(y)["players"]["A.J. Green"]
            self.assertEqual(rows[str(y)]["REC"], str(line["receptions"]))
            self.assertEqual(rows[str(y)]["YDS"], "{:,}".format(line["receiving_yards"]))
            self.assertEqual(rows[str(y)]["TGT"], str(line["targets"]))
            self.assertEqual(rows[str(y)]["LONG"], str(line["long_reception"]))
            for f in total:
                total[f] += line[f]
        self.assertEqual(rows["Career"]["YDS"], "{:,}".format(total["receiving_yards"]))
        self.assertEqual(rows["Career"]["TD"], str(total["receiving_touchdowns"]))

    def test_background_defender_equals_the_statbook(self):
        rows = page_rows("%s/houston_texans/j_j_watt.md" % player_cards.FOLDER)
        tackles = sacks = 0
        for y in (2013, 2014):
            line = book(y)["players"]["J.J. Watt"]
            self.assertEqual(rows[str(y)]["TKL"], str(line["tackles"]))
            self.assertEqual(float(rows[str(y)]["SACK"]), float(line["sacks"]))
            self.assertEqual(rows[str(y)]["PD"], str(line["passes_defended"]))
            tackles += line["tackles"]
            sacks += line["sacks"]
        self.assertEqual(rows["Career"]["TKL"], str(tackles))
        self.assertEqual(float(rows["Career"]["SACK"]), float(sacks))

    def test_every_player_season_total_equals_the_statbook(self):
        from runtime.statbook import BOOK_FIELDS
        rec = player_cards.collect(ROOT)
        mismatches = []
        for year, kinds in rec["receipts"].items():
            for kind, receipts in kinds.items():
                if not receipts:
                    continue
                statbook = aggregate_receipts(receipts)["players"]
                mine = {}
                for r in rec["games"]:
                    if r["year"] == year and r["type"] == kind:
                        mine.setdefault(r["pid"], []).append(r)
                self.assertEqual(set(statbook), set(mine), (year, kind))
                for pid, line in statbook.items():
                    t = player_cards.total(mine[pid])
                    mismatches += [(year, kind, pid, f) for f in BOOK_FIELDS if line.get(f, 0) != t.get(f, 0)]
        self.assertEqual(mismatches, [])

    def test_games_on_record_follow_his_clubs_while_he_was_theirs(self):
        club_games = {(2014, "regular", "A"): ["2014-09-07", "2014-09-14", "2014-09-21"],
                      (2014, "regular", "B"): ["2014-09-08", "2014-09-15", "2014-09-22", "2014-09-29"]}
        rows = [{"team": t, "date": d, "week": w} for t, d, w in
                (("A", "2014-09-07", 1), ("A", "2014-09-14", 2), ("B", "2014-09-22", 3), ("B", "2014-09-29", 4))]
        self.assertEqual(player_cards.window_games(club_games, 2014, "regular", rows), 5)
        self.assertEqual(player_cards.window_games(club_games, 2014, "regular", rows[:2]), 3)

    def test_fields_the_records_do_not_hold_read_na(self):
        # Line starts and snap counts exist only in 2014 game records: an offensive
        # lineman's 2013 row and career row say N/A for them, his 2014 row has numbers.
        rows = page_rows("%s/philadelphia_eagles/luke_joeckel.md" % player_cards.FOLDER)
        self.assertEqual(rows["2013"]["STARTS"], "N/A")
        self.assertEqual(rows["2013"]["OFF SNAPS"], "N/A")
        self.assertEqual(rows["Career"]["STARTS"], "N/A")
        self.assertEqual(rows["2014"]["STARTS"], str(book(2014)["players"]["Luke Joeckel"]["line_starts"]))
        # A ratio with no denominator is N/A, not 0.
        tiles = dict(player_cards.tiles_for("QB", [{"line": {"position": "QB"}, "nums": (), "kernel": (2014, 5), "fg": []}], {}))
        self.assertEqual(tiles["CMP%"], "N/A")
        self.assertEqual(tiles["Y/A"], "N/A")
        # Identity the sources do not list: N/A on the card, never a guess.
        players = data()["players"]
        no_college = next(p for p in players if p["college"] is None)
        no_number = next(p for p in players if p["number"] is None)
        for p, label in ((no_college, "COLLEGE"), (no_number, "NO.")):
            path = FOLDER / player_cards.club_slug(p["team"]) / "assets" / ("%s.svg" % p["slug"])
            texts = [t.text for t in ET.fromstring(path.read_bytes()).iter(SVG + "text")]
            self.assertEqual(texts[texts.index(label) + 1], "N/A", path)

    def test_jacksonville_numbers_follow_the_rule(self):
        jax = [p for p in data()["players"] if p["team"] == "Jacksonville Jaguars"]
        shown = [p["number"] for p in jax if p["number"] is not None]
        real = [p for p in jax if p["number_note"] == "his 2014 Jaguars roster listing"]
        borrowed = [p for p in jax if p["number_note"] and "Jacksonville has not recorded one" in p["number_note"]]
        self.assertEqual(len(real) + len(borrowed), len(shown))
        # A number borrowed from another club is never shared with another current Jaguar.
        for p in borrowed:
            self.assertEqual(shown.count(p["number"]), 1, p["name"])


class LinkTests(unittest.TestCase):
    def test_club_and_index_pages_link_only_to_existing_pages(self):
        link = re.compile(r"\]\(([^)\s]+)\)")
        index = (FOLDER / "README.md").read_text(encoding="utf-8")
        clubs = link.findall(index)
        self.assertEqual(len(clubs), 32)
        for target in clubs:
            self.assertTrue((FOLDER / target).is_file(), target)
        for club in sorted(FOLDER.glob("*/README.md")):
            for target in link.findall(club.read_text(encoding="utf-8")):
                path = (club.parent / target).resolve()
                self.assertTrue(path.is_file(), "%s -> %s" % (club, target))
                self.assertTrue(path.is_relative_to(FOLDER.resolve()), target)
        for page in sorted(FOLDER.glob("*/*.md")):
            for target in link.findall(page.read_text(encoding="utf-8")):
                self.assertTrue((page.parent / target).resolve().is_file(), "%s -> %s" % (page, target))

    def test_jacksonville_players_link_their_working_card(self):
        text = (FOLDER / "jacksonville_jaguars" / "kirk_cousins.md").read_text(encoding="utf-8")
        target = SeasonPaths(2014, ROOT).record("player_profiles") / "kirk_cousins.md"
        self.assertIn("[Jacksonville player card](%s)" % os.path.relpath(target, FOLDER / "jacksonville_jaguars"), text)


@unittest.skipUnless(os.environ.get("LISTED_IDENTITY_SOURCES"), "pinned nflverse sources not present")
class IdentityBuilderTests(unittest.TestCase):
    def test_committed_identity_rebuilds_from_the_pinned_sources(self):
        from scripts.research import build_2014_listed_player_identity as builder
        with redirect_stdout(io.StringIO()):
            self.assertEqual(builder.main([os.environ["LISTED_IDENTITY_SOURCES"], "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
