"""Permanent player records and the player pages (rebuild step 3a).

runtime/people.py holds one record per player who has a page, with only the
facts that have no other owner; runtime/player_pages.py builds every player
page from the records and the owners they name, and scripts/render_player_pages.py
checks or writes them. The committed pages equal a fresh build; every record
keeps the schema and stores no fact another owner holds (awards, ages, the
owner map); a page's awards are the award results'; the numbers on a page
equal the statbook's; ages read the birth-date owners with the canon
overrides; a page follows the approved layout; and a closed season's player
folder is history. runtime/clean_pages.py's clean-page and folder-map checks
are tested here too. Counts, the current week and dated lines are worked out
from the stored facts (rebuild safeguard 7), never named.
"""
import io
import json
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402
sys.path.insert(0, str(ROOT))

from runtime import clean_pages, people, player_bios, player_cards, player_pages  # noqa: E402
from runtime.season_layout import LEAGUE_PLAYER_PAGES, PAGE_HISTORY, PLAYER_RECORDS  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.statbook import aggregate_receipts  # noqa: E402
from runtime.stat_tables import rating_value, thrown  # noqa: E402
from scripts import render_player_pages  # noqa: E402

LEAGUE = ROOT / LEAGUE_PLAYER_PAGES
FOLDER = SeasonPaths(2014, ROOT).record("player_profiles")
_CTX = None
_BUILT = None


def ctx():
    global _CTX
    if _CTX is None:
        _CTX = player_pages.Context(ROOT)
    return _CTX


def built():
    global _BUILT
    if _BUILT is None:
        _BUILT = player_pages.build(ctx=ctx())
    return _BUILT


def book(year, kind="regular"):
    paths = SeasonPaths(year, ROOT)
    folder = paths.receipts if kind == "regular" else paths.postseason_receipts
    return aggregate_receipts([json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))])


def page(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def label(year, kind="regular"):
    """The season row's label: the year, and while the season is open the latest week its game
    records cover (worked out from the receipts, never named)."""
    c = ctx()
    if c.complete.get(year, True) or year != c.active:
        return str(year)
    week = c.latest_week[(year, kind)]
    return "%d (through %s)" % (year, player_pages.ROUND_NAMES.get(week, "Week %d" % week))


def jaguars_page_ids():
    """The record ids the season's player folder must hold, from the stored facts: every player
    the roster shows Jacksonville controls, and every player its staff assessed this season."""
    c = ctx()
    controlled = {rid for rid, r in c.records.items() if player_pages.controlled_name(c, r)}
    assessed = {rid for rid, r in c.records.items()
                if any(a["season"] == c.active and "owner" not in a for a in r["assessments"])}
    return controlled, assessed


def tables(text, heading="### Regular season"):
    """[{season: {column: cell}}] for each table under ``heading`` of a page."""
    body = text.split(heading + "\n", 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
    out, lines = [], []
    for line in body.splitlines() + [""]:
        if line.startswith("|"):
            lines.append(line)
        elif lines:
            head = [c.strip() for c in lines[0].strip("|").split("|")]
            rows = [[c.strip() for c in l.strip("|").split("|")] for l in lines[2:]]
            out.append({r[0]: dict(zip(head, r)) for r in rows})
            lines = []
    return out


def league_page(name, club):
    return "%s/%s/%s.md" % (LEAGUE_PLAYER_PAGES, player_cards.club_slug(club), people.slugify(name))


def overlay(target, copies):
    """A root at ``target`` that reads as the repository through symbolic links, except each
    relative folder in ``copies``, which is a real copy, so a write there never reaches the
    repository."""
    tree = {}
    for rel in copies:
        node = tree
        for part in Path(rel).parts:
            node = node.setdefault(part, {})

    def build(source, dest, node, rel):
        dest.mkdir(exist_ok=True)
        for child in sorted(source.iterdir()):
            if child.name not in (".git", ".sim_cache") and child.name not in node:
                (dest / child.name).symlink_to(child)
        for name, sub in node.items():
            path = (rel / name).as_posix()
            if path in copies:
                if (source / name).is_dir():
                    shutil.copytree(source / name, dest / name, symlinks=True)
                else:
                    shutil.copyfile(source / name, dest / name)
            else:
                build(source / name, dest / name, sub, rel / name)
    build(ROOT, target, tree, Path())


class CommittedPageTests(unittest.TestCase):
    def test_committed_pages_and_records_are_current(self):
        self.assertEqual(player_pages.check(ROOT), [])

    def test_script_check_passes_on_the_committed_state(self):
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(render_player_pages.main(["--check"]), 0)
        self.assertIn("PLAYER PAGES CURRENT", out.getvalue())

    def test_build_is_deterministic(self):
        again, _ = player_pages.build(ROOT)
        self.assertEqual(again, built()[0])

    def test_one_league_page_per_player_and_one_record_per_page(self):
        files, missing = built()
        self.assertEqual(missing, [])
        data = ctx().data
        league = [r for r in files if r.startswith(LEAGUE_PLAYER_PAGES + "/") and not r.endswith("README.md")]
        self.assertEqual(len(league), len(data["players"]))
        self.assertEqual(len([r for r in files if r.endswith("/README.md") and r.count("/") == 3]), 32)
        self.assertFalse([r for r in files if not r.endswith(".md")])  # no career-card images
        jaguars = [r for r in files if r.startswith(FOLDER.relative_to(ROOT).as_posix() + "/")]
        controlled, assessed = jaguars_page_ids()
        self.assertEqual(len(controlled), len(ctx().roster))  # one record per rostered player
        self.assertEqual(len(jaguars), len(controlled | assessed) + 1)  # and the index
        # Every record is a game-record player's (one each) or a card-only Jaguar's.
        records = people.load_all(ROOT)
        matched = [ctx().league_player(r)["key"] for r in records.values() if ctx().league_player(r)]
        card_only = [rid for rid, r in records.items() if ctx().league_player(r) is None]
        self.assertEqual(len(set(matched)), len(matched))
        self.assertEqual(len(matched), len(data["players"]))
        self.assertEqual(len(records), len(data["players"]) + len(card_only))
        self.assertLessEqual(set(card_only), controlled | assessed)

    def test_a_jaguars_page_is_his_league_page_with_its_links_rebased(self):
        files, _ = built()
        compared = 0
        for rel, text in files.items():
            if not rel.startswith(FOLDER.relative_to(ROOT).as_posix() + "/") or rel.endswith("README.md"):
                continue
            name = re.match(r"# (.+)\n", text).group(1)
            twins = [r for r, t in files.items() if r.startswith(LEAGUE_PLAYER_PAGES + "/")
                     and r.endswith("/" + Path(rel).name) and t.startswith("# %s\n" % name)]
            if not twins:
                continue
            strip = lambda t: re.sub(r"\]\([^)]*\)", "]()", t)  # noqa: E731
            self.assertIn(strip(text), [strip(files[t]) for t in twins], rel)
            compared += 1
        self.assertGreaterEqual(compared, 60)

    def test_check_fails_on_a_stale_missing_or_extra_page_and_write_repairs_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            overlay(root, (LEAGUE_PLAYER_PAGES, FOLDER.relative_to(ROOT).as_posix(), PLAYER_RECORDS))
            cousins = root / FOLDER.relative_to(ROOT) / "kirk_cousins.md"
            cousins.write_text(cousins.read_text(encoding="utf-8") + "A hand edit.\n", encoding="utf-8")
            (root / LEAGUE_PLAYER_PAGES / "cincinnati_bengals" / "a_j_green.md").unlink()
            (root / LEAGUE_PLAYER_PAGES / "cincinnati_bengals" / "someone_else.md").write_text("x", encoding="utf-8")
            record = root / PLAYER_RECORDS / "kirk_cousins.json"
            data = json.loads(record.read_text(encoding="utf-8"))
            data["birth_date"] = "1991-08-19"
            record.write_text(people.dump(data), encoding="utf-8")
            errors = player_pages.check(root)
            self.assertIn("Player page stale or hand-edited: %s/kirk_cousins.md" % FOLDER.relative_to(ROOT).as_posix(),
                          errors)
            self.assertIn("Player page missing: %s/cincinnati_bengals/a_j_green.md" % LEAGUE_PLAYER_PAGES, errors)
            self.assertIn("Unexpected file among the player pages: %s/cincinnati_bengals/someone_else.md"
                          % LEAGUE_PLAYER_PAGES, errors)
            self.assertTrue([e for e in errors if "kirk_cousins.json: record keys" in e])
            # A fact stored twice is refused; with the record restored, write repairs the pages.
            del data["birth_date"]
            record.write_text(people.dump(data), encoding="utf-8")
            created, written, removed = player_pages.write(root)
            self.assertEqual((created, written, removed), (0, 2, 1))
            self.assertEqual(player_pages.check(root), [])

    def test_a_player_new_to_the_game_records_gets_an_identity_only_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            overlay(root, (LEAGUE_PLAYER_PAGES, FOLDER.relative_to(ROOT).as_posix(), PLAYER_RECORDS))
            (root / PLAYER_RECORDS / "a_j_green.json").unlink()
            errors = player_pages.check(root)
            self.assertIn("Player record missing for A.J. Green (Cincinnati Bengals); run the player page builder",
                          errors)
            created, _, _ = player_pages.write(root)
            self.assertEqual(created, 1)
            record = json.loads((root / PLAYER_RECORDS / "a_j_green.json").read_text(encoding="utf-8"))
            self.assertEqual((record["assessments"], record["transactions"]), ([], []))
            self.assertNotIn("awards", record)  # his awards stay with the award results
            self.assertEqual(player_pages.check(root), [])


def awards_section(text):
    return text.split("## Awards\n\n", 1)[1].split("\n\n## ", 1)[0].splitlines()


class AwardTests(unittest.TestCase):
    """The award results own every decided award; a page reads them, a record never holds one."""

    def test_a_page_lists_the_award_results_for_its_player(self):
        entries = player_cards.award_entries(ROOT, ctx().data["years"])
        rodgers = ["- " + e["award"] for e in entries if e["player"] == "Aaron Rodgers"]
        self.assertIn("- NFC Offensive Player of the Week (2013, Week 14)", rodgers)
        self.assertEqual(awards_section(page(league_page("Aaron Rodgers", "Green Bay Packers"))), rodgers)
        self.assertEqual(awards_section(page(league_page("A.J. Green", "Cincinnati Bengals"))),
                         ["- " + e["award"] for e in entries if e["player"] == "A.J. Green"] or ["None."])
        results = json.loads((SeasonPaths(2013, ROOT).awards_data / "results.json").read_text(encoding="utf-8"))
        drawn = results["week-14"]["awards"]["NFC-offense"]
        self.assertEqual(drawn["shortlist"][drawn["winner_index"]]["player"], "Aaron Rodgers")

    def test_every_page_award_is_decided_on_record(self):
        texts = sorted(e["award"] for e in player_cards.award_entries(ROOT, ctx().data["years"]))
        shown = sorted(line[2:] for rel, text in built()[0].items() if rel.startswith(LEAGUE_PLAYER_PAGES + "/")
                       and not rel.endswith("README.md") for line in awards_section(text) if line != "None.")
        self.assertEqual(shown, texts)
        self.assertEqual(ctx().data["unmatched_awards"], [])

    def test_a_replayed_draw_changes_only_the_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            awards = SeasonPaths(2013, ROOT).awards_data.relative_to(ROOT).as_posix()
            overlay(root, (LEAGUE_PLAYER_PAGES, FOLDER.relative_to(ROOT).as_posix(), PLAYER_RECORDS, awards))
            record = (root / PLAYER_RECORDS / "aaron_rodgers.json").read_bytes()
            results_path = root / awards / "results.json"
            results = json.loads(results_path.read_text(encoding="utf-8"))
            results["week-14"]["awards"]["NFC-offense"]["winner_index"] = None  # a voided draw
            results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
            rel = league_page("Aaron Rodgers", "Green Bay Packers")
            self.assertIn("Player page stale or hand-edited: " + rel, player_pages.check(root))
            player_pages.write(root)
            self.assertNotIn("- NFC Offensive Player of the Week (2013, Week 14)",
                             (root / rel).read_text(encoding="utf-8"))
            self.assertEqual((root / PLAYER_RECORDS / "aaron_rodgers.json").read_bytes(), record)
            self.assertEqual(player_pages.check(root), [])


class RecordTests(unittest.TestCase):
    def test_every_record_keeps_the_schema(self):
        records = people.load_all(ROOT)
        errors = [e for rid, r in records.items() for e in people.record_errors(rid, r, ROOT)]
        self.assertEqual(errors, [])
        for rid, r in records.items():
            # Facts with an owner are read through it, never stored here: no awards, no copy of
            # the owner map, no age in an assessment.
            self.assertLessEqual(set(r), set(people.RECORD_KEYS) | set(people.OPTIONAL_KEYS), rid)
            self.assertFalse({"awards", "read_through"} & set(r), rid)
            for a in r["assessments"]:
                self.assertFalse(people.OWNED_IN_ASSESSMENT & set(a), rid)

    def test_a_record_that_stores_an_owned_fact_is_refused(self):
        r = json.loads(json.dumps(people.load_all(ROOT)["kirk_cousins"]))
        opening = next(a for a in r["assessments"] if "owner" not in a)
        opening["age_as_written"] = "25"
        self.assertTrue([e for e in people.record_errors("kirk_cousins", r, ROOT) if "stores no age_as_written" in e])
        del opening["age_as_written"]
        r["awards"] = []
        self.assertTrue([e for e in people.record_errors("kirk_cousins", r, ROOT) if "record keys" in e])

    def test_the_owner_map_names_known_owners_in_order(self):
        for fact, owners in people.READ_THROUGH.items():
            self.assertTrue(owners and set(owners) <= set(people.OWNERS), fact)
        # The birth date: the canon change outranks every research source.
        self.assertEqual(people.READ_THROUGH["birth_date"][0], "canon_overrides")
        self.assertEqual(people.READ_THROUGH["college"], ("league_database", "listed_identity"))

    def test_cousins_record_holds_only_his_unowned_facts(self):
        r = people.load_all(ROOT)["kirk_cousins"]
        self.assertEqual(r["gsis_id"], "00-0029604")
        self.assertEqual(r["assessments"][0], {"season": 2013, "stage": "final",
                                               "owner": "career/2013/player_profiles/kirk_cousins.md"})
        opening = r["assessments"][1]
        self.assertEqual((opening["season"], opening["stage"], opening["date"], opening["by"]),
                         (2014, "opening", "2014-03-31", "Jacksonville staff"))
        self.assertEqual(opening["grades"][0], {"category": "Overall", "grade": "6.0 /10", "standing": "Staff judgment"})
        self.assertEqual([u["date"] for u in opening["updates"]][:1], ["2014-08-01"])
        # Year-only moves keep only the year; a window keeps the source's words.
        self.assertEqual([(t["date"], t["kind"]) for t in r["transactions"]], [("2012", "signed"), ("2013", "traded")])
        self.assertEqual(r["transactions"][1]["label"], "March 12 to April 24, 2013")
        # His birth date is read through its owners, never stored on the record, and no age is
        # stored either: on the opening assessment's date he was 22 by the canon birth date.
        self.assertNotIn("1991-08-19", json.dumps(r))
        self.assertNotIn("1988-08-19", json.dumps(r))
        self.assertNotIn("age_as_written", opening)
        self.assertEqual(player_bios.age_on(player_bios.load(ROOT)["Kirk Cousins"]["birth_date"], opening["date"]), 22)

    def test_every_2014_jaguar_has_his_opening_or_entry_assessment(self):
        self.assertEqual(player_pages.season_assessment_errors(2014, ROOT), [])
        self.assertEqual(player_pages.season_assessment_errors(2013, ROOT), [])
        # Every player Jacksonville controls is assessed, so the folder holds exactly the assessed.
        controlled, assessed = jaguars_page_ids()
        self.assertLessEqual(controlled, assessed)
        self.assertEqual(set(player_pages.jaguars_players(ctx())), assessed)

    def test_transactions_sort_a_draft_before_its_contract(self):
        moves = [{"date": "2014-05-10", "kind": "signed"}, {"date": "2014", "kind": "signed"},
                 {"date": "2014-05-10", "kind": "drafted"}, {"date": "2014-05", "kind": "signed"}]
        self.assertEqual([(m["date"], m["kind"]) for m in sorted(moves, key=people.sort_key)],
                         [("2014", "signed"), ("2014-05", "signed"), ("2014-05-10", "drafted"),
                          ("2014-05-10", "signed")])
        self.assertEqual(people.transaction_date_text({"date": "2014-05"}), "May 2014")
        self.assertEqual(people.transaction_date_text({"date": "2014-05-09"}), "May 9, 2014")
        self.assertEqual(people.transaction_date_text({"date": "2013", "label": "March 12 to April 24, 2013"}),
                         "March 12 to April 24, 2013")


class LayoutTests(unittest.TestCase):
    COUSINS = FOLDER.relative_to(ROOT).as_posix() + "/kirk_cousins.md"

    def test_cousins_page_follows_the_approved_layout(self):
        text = page(self.COUSINS)
        lines = text.splitlines()
        record = ctx().records["kirk_cousins"]
        age = player_bios.age_on("1991-08-19", ctx().jax_latest)  # the user's canon birth date
        self.assertEqual(lines[0], "# Kirk Cousins")
        self.assertEqual(lines[2], "**Jacksonville Jaguars · Quarterback · No. 8 · Age %d · %s**"
                         % (age, ctx().roster["Kirk Cousins"][1]))
        self.assertTrue(lines[4].startswith("6' 3\", 202 lb · Born August 19, 1991 · Michigan State · "
                                            "Drafted in 2012, fourth round, by Washington"), lines[4])
        self.assertTrue(any(l.startswith("![Kirk Cousins](https://") for l in lines))
        self.assertTrue(any(l.startswith("*Photo: ") for l in lines))
        headings = [l for l in lines if l.startswith("## ") or l.startswith("### ")]
        self.assertEqual(headings, ["## Staff assessment", "## Contract", "## Statistics", "### Regular season",
                                    "### Playoffs", "## Awards", "## Transactions"])
        opening = next(a for a in record["assessments"] if a["season"] == 2014 and "owner" not in a)
        self.assertIn("*Staff view, March 31, 2014; dated updates through %s.*"
                      % player_pages.long_date(max(u["date"] for u in opening["updates"])), text)
        y2015 = ctx().finances["Kirk Cousins"]["years"]["2015"]
        self.assertIn("| 2015 | %s | %s |" % (player_pages.money(y2015["base"]), player_pages.money(y2015["cap"])), text)
        self.assertNotIn(".svg", text)
        self.assertNotIn("Week 5 update", text)
        self.assertTrue(text.rstrip().endswith(player_pages.PAGE_MARK))

    def test_a_league_player_shows_no_staff_assessment_or_contract(self):
        text = page(league_page("A.J. Green", "Cincinnati Bengals"))
        headings = [l for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(headings, ["## Statistics", "## Awards", "## Transactions"])

    def test_a_former_jaguar_keeps_his_assessment_and_his_moves(self):
        text = page(league_page("Cecil Shorts", "Indianapolis Colts"))
        self.assertIn("## Staff assessment", text)
        self.assertNotIn("## Contract", text)
        self.assertIn("| March 31, 2014 | Traded by Jacksonville to Indianapolis, with Justin Blackmon, "
                      "for 2014 picks No. 82 and No. 194 |", text)

    def test_a_2013_final_sheet_is_read_through_its_owner(self):
        text = page(league_page("Brad Meester", "Jacksonville Jaguars"))
        self.assertIn("*Staff view at the 2013 season close, January 14, 2014.*", text)
        self.assertIn("| Overall at position | 5.5/10 |", text)

    def test_every_table_leads_with_season_team_age_and_number(self):
        for rel, text in built()[0].items():
            for line in text.splitlines():
                if line.startswith("| Season |"):
                    self.assertTrue(line.startswith("| Season | Team | Age | # |"), rel)


class ValueTests(unittest.TestCase):
    def test_cousins_equals_the_statbook(self):
        regular, _ = tables(page(league_page("Kirk Cousins", "Jacksonville Jaguars")))
        for year in (2013, 2014):
            line = book(year)["players"]["Kirk Cousins"]
            row = regular[label(year)]
            self.assertEqual(row["G"], str(line["games"]))
            self.assertEqual(row["CMP"], "{:,}".format(line["completions"]))
            self.assertEqual(row["ATT"], "{:,}".format(line["pass_attempts"]))
            self.assertEqual(row["YDS"], "{:,}".format(line["passing_yards"]))
            self.assertEqual(row["TD"], str(line["passing_touchdowns"]))
            self.assertEqual(row["INT"], str(thrown(line)))
            self.assertEqual(row["Rating"], "%.1f" % rating_value(line))
        playoffs, _ = tables(page(league_page("Kirk Cousins", "Jacksonville Jaguars")), "### Playoffs")
        self.assertEqual(playoffs["2013"]["YDS"], "{:,}".format(book(2013, "playoffs")["players"]["Kirk Cousins"]["passing_yards"]))

    def test_a_receiver_and_a_defender_equal_the_statbook(self):
        green = tables(page(league_page("A.J. Green", "Cincinnati Bengals")))[0]
        watt = tables(page(league_page("J.J. Watt", "Houston Texans")))[0]
        for year in (2013, 2014):
            g = book(year)["players"]["A.J. Green"]
            row = green[label(year)]
            self.assertEqual((row["Rec"], row["Yards"], row["Targets"]),
                             (str(g["receptions"]), "{:,}".format(g["receiving_yards"]), str(g["targets"])))
            w = book(year)["players"]["J.J. Watt"]
            self.assertEqual(watt[label(year)]["Tackles"], str(w["tackles"]))
            self.assertEqual(float(watt[label(year)]["Sacks"]), float(w["sacks"]))

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

    def test_fields_the_records_do_not_hold_read_na(self):
        rows = tables(page(league_page("Luke Joeckel", "Philadelphia Eagles")))[0]
        self.assertEqual((rows["2013"]["Starts"], rows["2013"]["Offensive snaps"]), ("N/A", "N/A"))
        self.assertEqual(rows["Career"]["Starts"], "N/A")
        self.assertEqual(rows[label(2014)]["Starts"],
                         str(book(2014)["players"]["Luke Joeckel"]["line_starts"]))

    def test_namesakes_keep_their_own_birth_dates(self):
        self.assertIn("Born March 21, 1987", page(league_page("Jonathan Stewart", "Carolina Panthers")))
        self.assertIn("Born November 23, 1990", page(league_page("Jonathan Stewart", "St. Louis Rams")))

    def test_ages_read_the_canon_override(self):
        text = page(league_page("Kirk Cousins", "Jacksonville Jaguars"))
        regular, _ = tables(text)
        self.assertEqual((regular["2013"]["Age"], regular[label(2014)]["Age"]), ("22", "23"))
        self.assertEqual(tables(text, "### Playoffs")[0]["2013"]["Age"], "22")
        self.assertEqual((regular["Career" if "Career" in regular else "With Jacksonville"]["Age"]), "")

    def test_the_number_follows_the_season_and_team(self):
        regular, _ = tables(page(league_page("Kirk Cousins", "Jacksonville Jaguars")))
        self.assertEqual((regular["2013"]["#"], regular[label(2014)]["#"]), ("N/A", "8"))
        no_club_twice = {}
        for p in ctx().data["players"]:
            if p["number"] is not None:
                no_club_twice.setdefault((p["team"], p["number"]), []).append(p["name"])
        self.assertEqual({k: v for k, v in no_club_twice.items() if len(v) > 1}, {})


class StatusTests(unittest.TestCase):
    def test_a_closed_seasons_player_folder_is_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = FOLDER.relative_to(ROOT).as_posix()
            review = SeasonPaths(2014, ROOT).record("closeouts/season_review.md").relative_to(ROOT).as_posix()
            overlay(root, (LEAGUE_PLAYER_PAGES, folder, PLAYER_RECORDS, Path(review).parent.as_posix()))
            before = {p.name: p.read_bytes() for p in sorted((root / folder).iterdir())}
            (root / review).parent.mkdir(parents=True, exist_ok=True)
            (root / review).write_text("# 2014 season review\n", encoding="utf-8")
            files, _ = player_pages.build(root)
            self.assertFalse([r for r in files if r.startswith(folder + "/")])
            player_pages.write(root)
            self.assertEqual({p.name: p.read_bytes() for p in sorted((root / folder).iterdir())}, before)
            self.assertEqual(player_pages.check(root), [])


class CleanPageTests(unittest.TestCase):
    def errors(self, line, rel="career/2014/Regular_Season/Games/Week_06/output.md"):
        return clean_pages.page_errors(rel, line + "\n", player_pages.MARKERS)

    def test_every_built_page_and_every_new_page_is_clean(self):
        self.assertEqual(clean_pages.clean_errors(ROOT), [])
        checked = clean_pages.checked_pages(ROOT)
        self.assertGreater(len(checked), 2000)
        self.assertIn(LayoutTests.COUSINS, [rel for rel, _ in checked])

    def test_each_kind_of_system_text_is_caught(self):
        for line, found in (
                ("The engine drew the punt.", "system word: engine"),
                ("In this branch he started.", "system word: branch"),
                ("See the receipt.", "system word: receipt"),
                ("Per decision 1C the staff agreed.", "internal code: 1C"),
                ("Closed under E1.", "internal code: E1"),
                ("Player 00-0029604 started.", "player identifier"),
                ("The fourth_down_policy held.", "system name: fourth_down_policy"),
                ("Run `close_week`.", "code span"),
                ("See [the data](../../../../data/2014/x.json).", "link to a system file"),
                ("Built by render_player_pages.py.", "script or module name"),
                ("<details>more</details>", "markup"),
                ("Disclaimer: this is a guess.", "policy note or disclaimer"),
                ("Exact theoretical personnel judgments.", "policy note or disclaimer"),
                ("Kernel 2014.6 applies.", "version label"),
                ("Recorded under Entry 109.", "entry number"),
        ):
            self.assertTrue([e for e in self.errors(line) if found in e], (line, self.errors(line)))

    def test_the_word_branch_passes_only_in_a_players_name(self):
        for line in ("The Branch resolved the game.", "This Branch week closed.", "Deion Branch caught it."):
            self.assertTrue([e for e in self.errors(line) if "system word: Branch" in e], line)
        names = clean_pages.proper_names(ROOT).pattern
        for name in ("Alan Branch", "Andre Branch", "Tyvon Branch"):
            self.assertIn(name.replace(" ", "\\ "), names)
            self.assertEqual(self.errors("%s made the tackle." % name), [], name)

    def test_football_prose_passes(self):
        for line in ("Andre Branch beat the left tackle twice.", "Tyvon Branch had 9 tackles.",
                     "*Photo: Keith Allison, [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0) "
                     "([source](https://commons.wikimedia.org/wiki/File:Cecil_Shorts_III.(cropped).jpg)).*",
                     "He ran a 4.52 40 in 2012 and threw for 3,981 yards.",
                     "[Week 5 report](../Week_05/output.md)", player_pages.PAGE_MARK):
            self.assertEqual(self.errors(line), [], line)

    def test_pages_written_before_week_6_are_history_while_unchanged(self):
        old = clean_pages.history(ROOT)
        checked = {rel for rel, _ in clean_pages.checked_pages(ROOT)}
        for rel, recorded in old.items():
            same = (ROOT / rel).is_file() and clean_pages.digest((ROOT / rel).read_bytes()) == recorded
            self.assertEqual(rel in checked, not same, rel)
        self.assertIn("career/2014/Regular_Season/Games/Week_05/output.md", old)

    def test_a_history_page_rewritten_later_is_checked(self):
        planted = "Kernel receipt checkpoint 1C."
        living = ("career/2014/Regular_Season/standings.md", "career/2014/Record.md", "career/2014/README.md")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = {}
            for rel in living + ("career/2014/Regular_Season/Games/Week_05/output.md",):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                data = (ROOT / rel).read_bytes()
                (root / rel).write_bytes(data)
                pages[rel] = clean_pages.digest(data)
            (root / PAGE_HISTORY).parent.mkdir(parents=True)
            (root / PAGE_HISTORY).write_text(json.dumps({"pages": pages}), encoding="utf-8")
            new = "career/2014/Regular_Season/Games/Week_06/output.md"
            (root / new).parent.mkdir(parents=True)
            (root / new).write_text("# Week 6\n\n" + planted + "\n", encoding="utf-8")
            unchanged = {e.split(":")[0] for e in clean_pages.clean_errors(root)}
            self.assertEqual(unchanged, {new})  # the history pages as written are exempt
            for rel in living:  # their generators rewrite them from Week 6 on
                with open(root / rel, "a", encoding="utf-8") as f:
                    f.write("\n" + planted + "\n")
            found = clean_pages.clean_errors(root)
            for rel in living + (new,):
                self.assertTrue([e for e in found if e.startswith(rel + ":") and "system word: Kernel" in e], rel)
                self.assertTrue([e for e in found if e.startswith(rel + ":") and "internal code: 1C" in e], rel)
            self.assertFalse([e for e in found if e.startswith("career/2014/Regular_Season/Games/Week_05/")])


class FolderMapTests(unittest.TestCase):
    def test_no_script_or_runtime_module_writes_a_season_path(self):
        self.assertEqual(clean_pages.folder_map_errors(ROOT), [])

    def test_season_paths_written_in_code_are_caught(self):
        source = "\n".join((
            '"""Docstrings may name career/2014/Regular_Season."""',
            'from pathlib import Path',
            'ROOT = Path(".")',
            'A = ROOT / "career/2014/stats"',
            'B = ROOT / "data" / "2013"',
            'C = ROOT / "Regular_Season" / "Games"',
            'D = "see ../../../../data/2014/Draft/x.json"',
            'E = SeasonPaths(2014, ROOT).record("stats")',
            'F = ROOT / "library/data/2012_league_base.json"',
            'G = "https://example.com/2014/x"',
        ))
        errors = clean_pages.module_errors("scripts/example.py", source)
        self.assertEqual(sorted(int(e.split(":")[1]) for e in errors), [4, 5, 6, 7])

    def test_joined_formatted_and_logical_paths_are_caught(self):
        source = "\n".join((
            'import os',
            'from pathlib import Path, PurePosixPath',
            'ROOT = Path(".")',
            'year = 2014',
            'A = f"career/{year}/stats/team_tracker/x.md"',
            'B = Path("career") / str(year) / "stats"',
            'C = os.path.join("career", "2014", "Regular_Season")',
            'D = "career/%d/regular_season/standings.md" % year',
            'E = "career/{}/x.md".format(year)',
            'F = ROOT / "career" / str(year) / "regular_season"',
            'G = PurePosixPath("data", str(year), "trades")',
            'H = "data/" + str(year)',
            'I = f"{ROOT}/career/{year}/x.md"',
            'J = Path(ROOT).joinpath("stats")',
            # Not season paths: a year-named research file, a logical name passed to the map, a
            # file inside a folder the map gave, string joins.
            'K = "no %d table (library/data/%d_db_families.json)" % (year, year)',
            'L = logical_path(year, f"stats/team_tracker/{year}")',
            'M = SeasonPaths(year, ROOT).preseason_data(1) / "depth_chart.json"',
            'N = ", ".join(["stats", "x"])',
            'O = "/".join(("a", "b"))',
        ))
        lines = sorted({int(e.split(":")[1]) for e in clean_pages.module_errors("scripts/zz_planted.py", source)})
        self.assertEqual(lines, list(range(5, 15)))
        self.assertIn("stats", clean_pages.LOGICAL_NAMES)
        self.assertIn("regular_season", clean_pages.LOGICAL_NAMES)
        self.assertIn("trades", clean_pages.LOGICAL_NAMES)
        self.assertNotIn("depth_chart.json", clean_pages.LOGICAL_NAMES)

    def test_the_map_itself_and_research_builders_are_exempt(self):
        self.assertEqual(clean_pages.MAP_MODULES, ("runtime/season_layout.py", "runtime/seasons.py"))
        # The frozen research builders write their own dated paths and are not scanned.
        research = sorted((ROOT / "scripts" / "research").glob("*.py"))
        self.assertTrue([p for p in research if clean_pages.module_errors(p.name, p.read_text(encoding="utf-8"))])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("scripts/research/frozen.py", "runtime/season_layout.py", "scripts/live.py"):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text('P = "career/2014/x.md"\n', encoding="utf-8")
            (root / "runtime/seasons.py").write_text('P = "career/2014/x.md"\n', encoding="utf-8")
            self.assertEqual([e.split(":")[0] for e in clean_pages.folder_map_errors(root)], ["scripts/live.py"])


if __name__ == "__main__":
    unittest.main()
