"""League player cards (runtime/player_cards.py, scripts/render_player_cards.py).

The committed career/league_players folder must equal a fresh render of the
committed game records; every SVG is a static image GitHub can show; the
numbers on a card and a page equal the statbook's totals; a field the records
do not hold reads N/A; and every link resolves. Each current Jacksonville
player's card page that his league page links back to shows his card in a
generated block directly under its H1, a former player's page shows none, and
nothing else on the page is written.
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


def built():
    """(league folder files, Jacksonville player card pages) for the committed state."""
    global _RENDER
    if _RENDER is None:
        _RENDER = player_cards._build(ROOT)
    return _RENDER


def rendered():
    return built()[0]


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


def row_items(text):
    """The items of one row element: its own text, then each tspan's."""
    return ([text.text] if text.text else []) + [t.text for t in text.iter(SVG + "tspan")]


def svg_rows(root, cls):
    return [item for t in root.iter(SVG + "text") if t.get("class") == cls for item in row_items(t)]


def svg_tiles(path):
    """[(label, value)] in document order for each stat block of a card."""
    root = ET.fromstring(path.read_bytes())
    blocks = []
    for g in root.iter(SVG + "g"):
        if g.get("class") not in ("p", "c"):
            continue
        title = next(t.text for t in g.iter(SVG + "text") if t.get("class") == "bt")
        blocks.append((title, list(zip(svg_rows(g, "l"), svg_rows(g, "v")))))
    return blocks


def svg_identity(path):
    """{label: value} of a card's header identity row."""
    root = ET.fromstring(path.read_bytes())
    return dict(zip(svg_rows(root, "k"), svg_rows(root, "i")))


def svg_text(path):
    return [t for el in ET.fromstring(path.read_bytes()).iter() for t in (el.text, el.tail) if t]


def card_path(p):
    return FOLDER / player_cards.club_slug(p["team"]) / "assets" / ("%s.svg" % p["slug"])


class CommittedFolderTests(unittest.TestCase):
    def test_committed_folder_is_current(self):
        self.assertEqual(player_cards.check(ROOT, *built()), [])

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
            self.assertLessEqual(len(data), 6144, path)  # the 6 KB budget per card

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
        no_height = next(p for p in players if p["height_in"] is None)
        for p, label in ((no_college, "COLLEGE"), (no_number, "NO."), (no_height, "HEIGHT"), (no_height, "WEIGHT")):
            self.assertEqual(svg_identity(card_path(p))[label], "N/A", card_path(p))

    def test_jacksonville_numbers_follow_the_rule(self):
        jax = [p for p in data()["players"] if p["team"] == "Jacksonville Jaguars"]
        shown = [p["number"] for p in jax if p["number"] is not None]
        real = [p for p in jax if p["number_note"] == "his 2014 Jaguars roster listing"]
        borrowed = [p for p in jax if p["number_note"] and "Jacksonville has not recorded one" in p["number_note"]]
        self.assertEqual(len(real) + len(borrowed), len(shown))
        # A number borrowed from another club is never shared with another current Jaguar.
        for p in borrowed:
            self.assertEqual(shown.count(p["number"]), 1, p["name"])
        # Only players Jacksonville controls now carry a number on a Jaguars card.
        self.assertTrue(all(p["current_jaguar"] for p in jax if p["number"] is not None))
        self.assertIsNone(player("Ryan Davis", "Jacksonville Jaguars")["number"])  # waived August 30
        self.assertIsNone(player("C.J. Wilson", "Jacksonville Jaguars")["number"])  # a Jaguar only in 2013
        jones = player("Christian Jones", "Jacksonville Jaguars")
        self.assertTrue(jones["current_jaguar"])
        self.assertEqual(jones["number"], 59)

    def test_no_club_shows_one_number_twice(self):
        seen = {}
        for p in data()["players"]:
            if p["number"] is not None:
                seen.setdefault((p["team"], p["number"]), []).append(p["name"])
        self.assertEqual({k: v for k, v in seen.items() if len(v) > 1}, {})
        # A Week 1 row placed with a club by a Jacksonville trade carries his real club's number.
        self.assertIsNone(player("Cecil Shorts", "Indianapolis Colts")["number"])
        self.assertIsNone(player("Jason Babin", "Miami Dolphins")["number"])
        self.assertEqual(player("Jack Doyle", "Indianapolis Colts")["number"], 84)

    def test_namesakes_keep_their_own_birth_dates(self):
        car = player("Jonathan Stewart", "Carolina Panthers")
        stl = player("Jonathan Stewart", "St. Louis Rams")
        self.assertNotEqual(car["gsis"], stl["gsis"])
        self.assertEqual((car["birth_date"], car["age"]), ("1987-03-21", 27))
        self.assertEqual(stl["birth_date"], "1990-11-23")
        self.assertEqual(svg_identity(card_path(car))["BORN"], "March 21, 1987")
        self.assertEqual(svg_identity(card_path(stl))["BORN"], "November 23, 1990")
        # No card takes a name-keyed birth date recorded for a different gsis id.
        registry = json.loads((ROOT / "library/data/player_birth_dates.json").read_text(encoding="utf-8"))["players"]
        for p in data()["players"]:
            for name in p["record_names"]:
                entry = registry.get(name) or {}
                if entry.get("gsis_id") and p["gsis"] and entry["gsis_id"] != p["gsis"]:
                    self.assertNotEqual(p["birth_date"], entry["birth_date"], (p["name"], p["team"]))

    def test_text_is_unescaped_once(self):
        listed = json.loads((ROOT / "library/data/2014_listed_player_identity.json").read_text(encoding="utf-8"))
        self.assertFalse([v for v in listed["players"].values() if "&amp;" in v.get("college", "")])
        for path in sorted(FOLDER.rglob("*.svg")):
            self.assertFalse([t for t in svg_text(path) if "&amp;" in t or "&#" in t], path)
        self.assertEqual(svg_identity(card_path(player("Mike Evans", "Tampa Bay Buccaneers")))["COLLEGE"], "Texas A&M")

    def test_long_college_lists_are_cut_at_a_school(self):
        long = [p for p in data()["players"] if p["college"] and len(p["college"]) > player_cards.COLLEGE_CHARS]
        self.assertTrue(long)
        for p in long:
            shown = svg_identity(card_path(p))["COLLEGE"]
            self.assertLessEqual(len(shown), player_cards.COLLEGE_CHARS, p["name"])
            self.assertNotIn("...", shown)
            self.assertTrue(shown.endswith("; …"), shown)
            self.assertTrue(p["college"].startswith(shown[:-len("; …")] + "; "), shown)
            page = (FOLDER / player_cards.club_slug(p["team"]) / ("%s.md" % p["slug"])).read_text(encoding="utf-8")
            self.assertIn("Schools listed: %s." % p["college"], page)

    def test_each_card_is_dated_by_the_games_it_covers(self):
        # A card's date is the latest game it covers (his, or his club's while he was theirs), so a
        # card whose record did not change is not rewritten; the index carries the latest date.
        as_of = data()["as_of"]
        index = (FOLDER / "README.md").read_text(encoding="utf-8")
        self.assertIn("record through %s." % player_cards.long_date(as_of), index)
        cousins = player("Kirk Cousins", "Jacksonville Jaguars")
        # He has played every Jacksonville game on record: his card runs through the club's latest.
        jacksonville = max(r["date"] for r in player_cards.collect(ROOT)["games"]
                           if r["team"] == "Jacksonville Jaguars")
        self.assertEqual(cousins["through"], jacksonville)
        self.assertGreaterEqual(cousins["through"], "2014-09-28")
        meester = player("Brad Meester", "Jacksonville Jaguars")
        self.assertEqual(max(meester["seasons"]), 2013)
        self.assertLess(meester["through"], "2014-03-01")
        text = card_path(meester).read_text(encoding="utf-8")
        self.assertIn(player_cards.long_date(meester["through"]), text)
        self.assertNotIn(player_cards.long_date(as_of), text)
        for p in data()["players"]:
            covered = [b["through"] for b in p["career"].values() if b]
            self.assertEqual(p["through"], max(covered), p["name"])

    def test_text_on_the_club_colours_meets_aa(self):
        style = re.search(r"<style>(.*?)</style>", (FOLDER / "README.md").parent.joinpath(
            "jacksonville_jaguars", "assets", "kirk_cousins.svg").read_text(encoding="utf-8")).group(1)
        # Small text is dimmed only on the dark career surface.
        for rule in re.findall(r"([^{}]+)\{(?:[^}]*;)?opacity:", style):
            self.assertTrue(all(sel.strip().startswith(".c ") for sel in rule.split(",")), rule)
        for club, (primary, secondary) in player_cards.COLORS.items():
            ink = player_cards.text_on(primary)
            self.assertGreaterEqual(player_cards.contrast(ink, primary), 4.5, club)
            self.assertGreaterEqual(player_cards.contrast(ink, player_cards.tile_colour(primary, ink)), 4.5, club)
            # The secondary shows on every card: a stripe on the page, or the rule on the band.
            ground = player_cards.PAGE if player_cards.secondary_on_page(secondary) else primary
            self.assertGreaterEqual(player_cards.contrast(secondary, ground), player_cards.ACCENT, club)


class SeasonColumnTests(unittest.TestCase):
    """Each career-table season row leads with his team, his age on the league's opening game of
    that season and the number listed for him that season; the career row leaves both blank."""

    def head(self, rel, heading="### Regular season"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        body = text.split(heading, 1)[1]
        return [c.strip() for c in next(l for l in body.splitlines() if l.startswith("|")).strip("|").split("|")]

    def test_the_columns_lead_every_table(self):
        rel = "%s/jacksonville_jaguars/kirk_cousins.md" % player_cards.FOLDER
        self.assertEqual(self.head(rel)[:5], ["Season", "Team", "Age", "#", "G"])
        self.assertEqual(self.head(rel, "### Playoffs")[:5], ["Season", "Team", "Age", "#", "G"])
        for path in sorted(FOLDER.glob("*/*.md")):
            if path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith("| Season |"):
                    self.assertTrue(line.startswith("| Season | Team | Age | # | G |"), path)

    def test_age_is_on_the_opening_game_of_each_season(self):
        self.assertEqual(player_cards.opening_dates(ROOT, (2013, 2014)), {2013: "2013-09-05", 2014: "2014-09-04"})
        self.assertEqual(player_cards.age_on("1990-09-05", "2013-09-05"), 23)  # his birthday that day
        self.assertEqual(player_cards.age_on("1990-09-06", "2013-09-05"), 22)
        self.assertIsNone(player_cards.age_on(None, "2013-09-05"))
        p = player("Kirk Cousins", "Jacksonville Jaguars")  # born August 19, 1988
        rows = page_rows("%s/jacksonville_jaguars/kirk_cousins.md" % player_cards.FOLDER)
        self.assertEqual((rows["2013"]["Age"], rows["2014"]["Age"]), ("25", "26"))
        self.assertEqual(page_rows("%s/jacksonville_jaguars/kirk_cousins.md" % player_cards.FOLDER,
                                   "### Playoffs")["2013"]["Age"], "25")
        self.assertEqual(p["seasons"][2014]["age"], player_cards.age_on(p["birth_date"], "2014-09-04"))

    def test_no_birth_date_reads_na(self):
        p = next(x for x in data()["players"] if x["birth_date"] is None and x["seasons"])
        self.assertTrue(all(s["age"] is None for s in p["seasons"].values()))
        rows = page_rows("%s/%s/%s.md" % (player_cards.FOLDER, player_cards.club_slug(p["team"]), p["slug"]))
        year = str(min(y for y, s in p["seasons"].items() if s["regular"]))
        self.assertEqual(rows[year]["Age"], "N/A")

    def test_the_number_follows_the_season_and_team(self):
        number = player_cards.season_number
        codes = {"Alpha Club": "AAA", "Beta Club": "BBB", "Jacksonville Jaguars": "JAX"}
        p = {"team": "Beta Club", "number": 11}
        listed = {"number": 22, "number_basis": {"club": "AAA", "week": 2},
                  "number_2013": 33, "number_2013_basis": {"club": "AAA", "week": 17}}
        w1 = {"club": "Alpha Club", "jersey": "44"}
        self.assertEqual(number(2014, "Beta Club", p, listed, w1, codes), 11)  # his latest team: the card's number
        self.assertEqual(number(2014, "Alpha Club", p, listed, w1, codes), 44)  # another 2014 team: Week 1 roster
        self.assertEqual(number(2014, "Alpha Club", p, listed, dict(w1, branch_note="trade"), codes), 22)
        self.assertIsNone(number(2014, "Alpha Club", p, dict(listed, number_basis={"club": "BBB"}), None, codes))
        self.assertIsNone(number(2014, "Jacksonville Jaguars", p, listed, w1, codes))  # not his latest team
        self.assertEqual(number(2013, "Alpha Club", p, listed, w1, codes), 33)  # the 2013 roster, same team
        self.assertIsNone(number(2013, "Beta Club", p, listed, w1, codes))  # listed with another team
        jax = dict(listed, number_2013_basis={"club": "JAX", "week": 17})
        self.assertEqual(number(2013, "Jacksonville Jaguars", p, jax, w1, codes), 33)  # the real 2013 Jaguars
        self.assertIsNone(number(2015, "Beta Club", p, listed, w1, codes))  # no listing for a later season
        # Committed pages: a Jaguar the real 2013 Jaguars did not list reads N/A for 2013.
        rows = page_rows("%s/jacksonville_jaguars/kirk_cousins.md" % player_cards.FOLDER)
        cousins = player("Kirk Cousins", "Jacksonville Jaguars")
        self.assertEqual(rows["2013"]["#"], "N/A")
        self.assertEqual(rows["2014"]["#"], str(cousins["number"]))
        doyle = player("Jack Doyle", "Indianapolis Colts")
        self.assertEqual({y: s["number"] for y, s in doyle["seasons"].items()}, {2013: 84, 2014: 84})
        # Every season number is the card's own for the latest 2014 team.
        for x in data()["players"]:
            s = x["seasons"].get(2014)
            if s and s["clubs"][-1] == x["team"]:
                self.assertEqual(s["number"], x["number"], x["name"])

    def test_the_career_row_leaves_age_and_number_blank(self):
        rows = page_rows("%s/jacksonville_jaguars/kirk_cousins.md" % player_cards.FOLDER)
        self.assertEqual((rows["Career"]["Team"], rows["Career"]["Age"], rows["Career"]["#"]), ("", "", ""))


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

    def test_only_the_same_player_links_a_jacksonville_card(self):
        for rel in ("baltimore_ravens/c_j_mosley.md", "san_diego_chargers/mike_harris.md"):
            self.assertNotIn("Jacksonville player card", (FOLDER / rel).read_text(encoding="utf-8"), rel)
        profiles = player_cards.jacksonville_profiles(ROOT)
        branch = player_cards.Identity(ROOT).branch
        by_path = {path: name for name, path in profiles.items()}
        linked = 0
        for p in data()["players"]:
            page = (FOLDER / player_cards.club_slug(p["team"]) / ("%s.md" % p["slug"])).read_text(encoding="utf-8")
            prof = player_cards.profile_for(p, profiles, branch)
            self.assertEqual(prof is not None, "Jacksonville player card" in page, p["name"])
            if prof is None:
                continue
            linked += 1
            name = by_path[prof]
            self.assertIn(name, p["record_names"], p["name"])
            if branch.get(name):
                self.assertEqual(branch[name], p["gsis"], p["name"])
            self.assertTrue(p["current_jaguar"], p["name"])
        self.assertGreater(linked, 40)

    def test_jacksonville_players_link_their_working_card(self):
        text = (FOLDER / "jacksonville_jaguars" / "kirk_cousins.md").read_text(encoding="utf-8")
        target = SeasonPaths(2014, ROOT).record("player_profiles") / "kirk_cousins.md"
        self.assertIn("[Jacksonville player card](%s)" % os.path.relpath(target, FOLDER / "jacksonville_jaguars"), text)


PROFILES = SeasonPaths(2014, ROOT).record("player_profiles")


def page_block(text):
    """The text from the begin marker through the end marker, or None."""
    if player_cards.CARD_BEGIN not in text:
        return None
    return player_cards.CARD_BEGIN + text.split(player_cards.CARD_BEGIN, 1)[1].split(player_cards.CARD_END, 1)[0] \
        + player_cards.CARD_END


def without_block(text):
    """The page as its own owners wrote it: the block and its framing blank line removed."""
    return player_cards.with_card_block(text, None)


class JacksonvillePageTests(unittest.TestCase):
    def matched(self):
        pages = player_cards.profile_pages(ROOT)
        return pages, player_cards.page_players(data()["players"], player_cards.jacksonville_profiles(ROOT),
                                                player_cards.Identity(ROOT).branch)

    def test_kirk_cousins_page_shows_his_current_card_under_the_title(self):
        page = PROFILES / "kirk_cousins.md"
        text = page.read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertEqual(lines[0], "# Kirk Cousins — 2014 Player Profile")
        self.assertEqual(lines[1], "")
        self.assertEqual(lines[2], player_cards.CARD_BEGIN)
        block = page_block(text)
        self.assertEqual(text.count(player_cards.CARD_BEGIN), 1)
        # Matched by gsis id: his league page is the Jaguars quarterback's.
        branch = player_cards.Identity(ROOT).branch
        cousins = player("Kirk Cousins", "Jacksonville Jaguars")
        self.assertEqual(cousins["gsis"], branch["Kirk Cousins"])
        self.assertIs(self.matched()[1][page], cousins)
        self.assertEqual(block, player_cards.card_block(page, cousins, ROOT))
        self.assertEqual(built()[1][page.relative_to(ROOT).as_posix()], text)
        image = re.search(r"!\[Kirk Cousins career card\]\(([^)\s]+)\)", block).group(1)
        stats = re.search(r"\[Career statistics\]\(([^)\s]+)\)", block).group(1)
        self.assertEqual(image, "../../../../league_players/jacksonville_jaguars/assets/kirk_cousins.svg")
        self.assertEqual((page.parent / image).resolve(), (FOLDER / "jacksonville_jaguars/assets/kirk_cousins.svg").resolve())
        self.assertTrue((page.parent / image).resolve().is_file())
        self.assertEqual((page.parent / stats).resolve(), (FOLDER / "jacksonville_jaguars/kirk_cousins.md").resolve())
        self.assertTrue((page.parent / stats).resolve().is_file())
        # The photo follows the card, and the photo refresh keeps that order.
        from scripts.player_photos import Photos, place_block
        self.assertEqual(place_block(text, Photos(ROOT).lookup("Kirk Cousins"), "Kirk Cousins"), text)
        self.assertLess(text.index(player_cards.CARD_END), text.index("<!-- photo -->"))

    def test_a_page_has_a_block_exactly_when_his_league_page_links_back_to_it(self):
        pages, matched = self.matched()
        self.assertEqual(set(pages), {p for p in PROFILES.glob("*.md") if p.name not in ("README.md", "TEMPLATE.md")})
        current = set(player_cards.jacksonville_profiles(ROOT).values())
        self.assertLessEqual(set(matched), current)
        ids = {p["gsis"] for p in data()["players"] if p["gsis"]}
        jaguar_names = {n for p in data()["players"] if p["team"] == player_cards.JAX for n in p["record_names"]}
        branch = player_cards.Identity(ROOT).branch
        for path, name in pages.items():
            text = path.read_text(encoding="utf-8")
            if path in matched:
                p = matched[path]
                self.assertEqual(page_block(text), player_cards.card_block(path, p, ROOT), name)
                self.assertTrue(text.startswith(text.partition("\n")[0] + "\n\n" + player_cards.CARD_BEGIN), name)
                self.assertTrue(player_cards.block_under_title(text), name)
                if branch.get(name) and p["gsis"]:
                    self.assertEqual(branch[name], p["gsis"], name)
                for target in re.findall(r"\]\(([^)\s]+)\)", page_block(text)):
                    self.assertTrue((path.parent / target).resolve().is_file(), "%s -> %s" % (name, target))
                # His league page links back to this page: the two links are one pair.
                league = (path.parent / re.search(r"\[Career statistics\]\(([^)\s]+)\)", page_block(text)).group(1))
                back = re.search(r"\[Jacksonville player card\]\(([^)\s]+)\)", league.read_text(encoding="utf-8"))
                self.assertIsNotNone(back, name)
                self.assertEqual((league.parent / back.group(1)).resolve(), path.resolve(), name)
            elif path in current:
                # A current player no league player is: none carries his gsis id, or, when the page
                # name has none, none whose latest game was with Jacksonville carries the name.
                self.assertNotIn("player-card:", text, name)
                self.assertNotIn(branch[name], ids, name) if branch.get(name) else self.assertNotIn(
                    name, jaguar_names, name)
            else:
                # A former player's page is history through his departure: no block, whatever club
                # his latest game on record was with.
                self.assertNotIn("player-card:", text, name)
        self.assertGreater(len(matched), 40)

    def test_practice_squad_cards_are_matched_like_the_rest_of_the_roster(self):
        """Blocks and links back are matched over every player Jacksonville controls, practice squad
        included: the same set the league card's current_jaguar reads (jacksonville_current)."""
        from scripts.check_week_input_exclusivity import controlled_players_from_roster
        controlled = controlled_players_from_roster(SeasonPaths(2014, ROOT).roster)
        profiles = player_cards.jacksonville_profiles(ROOT)
        self.assertEqual(profiles, {n: PROFILES / ("%s.md" % player_cards.slugify(n)) for n in sorted(controlled)
                                    if (PROFILES / ("%s.md" % player_cards.slugify(n))).is_file()})
        for name in ("Tyler Bray", "Richard Murphy", "Matt Feiler", "Tyler Shatley", "Jackson Jeffcoat",
                     "Jerome Long", "Jemea Thomas"):
            self.assertIn(name, profiles)
        self.assertEqual(len(profiles), 64)

    def test_former_players_pages_do_not_follow_them_to_new_clubs(self):
        current = set(player_cards.jacksonville_profiles(ROOT).values())
        for slug, name, club in (("jeremy_cain", "Jeremy Cain", "Chicago Bears"),
                                 ("cecil_shorts", "Cecil Shorts", "Indianapolis Colts"),
                                 ("justin_blackmon", "Justin Blackmon", "Indianapolis Colts")):
            page = PROFILES / ("%s.md" % slug)
            self.assertNotIn(page, current, name)
            self.assertEqual(player(name, club)["team"], club)
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("player-card:", text, name)
            self.assertNotIn("league_players/", text, name)
            self.assertEqual(built()[1][page.relative_to(ROOT).as_posix()], text, name)

    def test_rerun_is_idempotent_and_replaces_only_the_block(self):
        page = PROFILES / "kirk_cousins.md"
        text = page.read_text(encoding="utf-8")
        block = page_block(text)
        self.assertEqual(player_cards.with_card_block(text, block), text)
        stale = text.replace("kirk_cousins.svg", "someone_else.svg")
        self.assertNotEqual(stale, text)
        self.assertEqual(player_cards.with_card_block(stale, block), text)
        original = without_block(text)
        self.assertNotIn("player-card:", original)
        self.assertEqual(original, text.replace("\n" + block + "\n", "", 1))
        self.assertEqual(player_cards.with_card_block(original, block), text)
        self.assertEqual(player_cards.with_card_block(player_cards.with_card_block(original, block), block), text)
        # Content outside the markers is byte-identical.
        edited = text.replace("**Season:** 2014", "**Season:** 2014 ", 1)
        replaced = player_cards.with_card_block(edited.replace(block, "%s\nold\n%s" % (
            player_cards.CARD_BEGIN, player_cards.CARD_END)), block)
        self.assertEqual(replaced, edited)
        # A block that has moved, below the photo or down the page, goes back directly under the title.
        bare = without_block(text)
        below_photo = bare.replace("<!-- /photo -->", "<!-- /photo -->\n\n" + block, 1)
        down_page = bare.replace("\n## ", "\n" + block + "\n\n## ", 1)
        for moved in (below_photo, down_page):
            self.assertNotEqual(moved, text)
            self.assertFalse(player_cards.block_under_title(moved))
            self.assertEqual(player_cards.with_card_block(moved, block), text)
        with self.assertRaises(ValueError):
            player_cards.with_card_block(text + "\n" + player_cards.CARD_BEGIN + "\n", block)
        # The committed pages already equal a fresh render: a rerun writes nothing.
        for rel, expected in built()[1].items():
            self.assertEqual((ROOT / rel).read_bytes(), expected.encode("utf-8"), rel)

    def test_check_flags_missing_stale_unmatched_and_moved_blocks_and_writes_nothing(self):
        cousins = player("Kirk Cousins", "Jacksonville Jaguars")
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp)
            (copy / "docs").mkdir()
            shutil.copy(ROOT / "docs/repository_map.json", copy / "docs/repository_map.json")
            folder = SeasonPaths(2014, copy).record("player_profiles")
            folder.mkdir(parents=True)
            committed = (PROFILES / "kirk_cousins.md").read_text(encoding="utf-8")
            nobody = "# Pat Nobody — 2014 Player Profile\n\n**Team:** Jacksonville Jaguars  \n"
            (folder / "kirk_cousins.md").write_text(without_block(committed), encoding="utf-8")
            (folder / "pat_nobody.md").write_text(nobody, encoding="utf-8")
            (folder / "pat_nobody_stale.md").write_text(player_cards.with_card_block(
                nobody, player_cards.card_block(folder / "pat_nobody_stale.md", cousins, copy)), encoding="utf-8")
            (folder / "README.md").write_text("# 2014 player profiles\n", encoding="utf-8")
            before = {p.name: p.read_bytes() for p in folder.iterdir()}
            matched = {folder / "kirk_cousins.md": cousins}
            pages = player_cards.render_pages(copy, matched)
            rel = folder.relative_to(copy).as_posix()
            self.assertEqual(sorted(pages), ["%s/%s" % (rel, n) for n in ("kirk_cousins.md", "pat_nobody.md",
                                                                        "pat_nobody_stale.md")])
            self.assertEqual(pages["%s/kirk_cousins.md" % rel], committed)
            self.assertEqual(pages["%s/pat_nobody.md" % rel], nobody)       # no league page, no block
            self.assertEqual(pages["%s/pat_nobody_stale.md" % rel], nobody)  # a stale block is removed
            errors = player_cards.check(copy, {}, pages)
            self.assertEqual(errors, [
                "Jacksonville player card page lacks its career card: %s/kirk_cousins.md" % rel,
                "Jacksonville player card page has a career card it should not carry "
                "(no league page links back to it): %s/pat_nobody_stale.md" % rel])
            (folder / "kirk_cousins.md").write_text(committed.replace("kirk_cousins.svg", "x.svg"), encoding="utf-8")
            before["kirk_cousins.md"] = (folder / "kirk_cousins.md").read_bytes()
            self.assertIn("Jacksonville player card page career card stale: %s/kirk_cousins.md" % rel,
                          player_cards.check(copy, {}, player_cards.render_pages(copy, matched)))
            # A current block that has moved off the title fails the check, though it is current.
            block = page_block(committed)
            moved = without_block(committed).replace("<!-- /photo -->", "<!-- /photo -->\n\n" + block, 1)
            (folder / "kirk_cousins.md").write_text(moved, encoding="utf-8")
            before["kirk_cousins.md"] = moved.encode("utf-8")
            pages = player_cards.render_pages(copy, matched)
            self.assertEqual(pages["%s/kirk_cousins.md" % rel], committed)
            self.assertIn("Jacksonville player card page career card is not directly under its title: "
                          "%s/kirk_cousins.md" % rel, player_cards.check(copy, {}, pages))
            self.assertEqual({p.name: p.read_bytes() for p in folder.iterdir()}, before)
            # Write mode puts it back under the title.
            changed = [r for r, t in pages.items() if (copy / r).read_bytes() != t.encode("utf-8")]
            self.assertIn("%s/kirk_cousins.md" % rel, changed)


@unittest.skipUnless(os.environ.get("LISTED_IDENTITY_SOURCES"), "pinned nflverse sources not present")
class IdentityBuilderTests(unittest.TestCase):
    def test_committed_identity_rebuilds_from_the_pinned_sources(self):
        from scripts.research import build_2014_listed_player_identity as builder
        with redirect_stdout(io.StringIO()):
            self.assertEqual(builder.main([os.environ["LISTED_IDENTITY_SOURCES"], "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
