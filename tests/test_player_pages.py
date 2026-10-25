"""Permanent player records and the player pages (rebuild step 3a).

runtime/people.py holds one record per player who has a page, with only the
facts that have no other owner; runtime/player_pages.py builds every player
page from the records and the owners they name, and scripts/render_player_pages.py
checks or writes them. The committed pages equal a fresh build; every record
keeps the schema and stores no fact another owner holds (awards, ages, the
owner map); a page's awards are the award results'; the numbers on a page
equal the statbook's; ages read the birth-date owners with the canon
overrides; a page follows the user's player card template (the current
assignment from the depth chart's own seats and roles, the position statistic
and the short staff assessment from the closed games, no grade anywhere); and
a closed season's player folder is history. runtime/clean_pages.py's clean-page and folder-map checks
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

import copy  # noqa: E402

from datetime import timedelta  # noqa: E402

from runtime import assignments, clean_pages, people, player_bios, player_cards, player_pages  # noqa: E402
from runtime.season_layout import LEAGUE_PLAYER_PAGES, PAGE_HISTORY, PLAYER_RECORDS  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.statbook import aggregate_receipts  # noqa: E402
from runtime.stat_tables import rating_value, thrown  # noqa: E402
from scripts import render_player_pages  # noqa: E402
from scripts.build_annual_player_sheets import season_closeout_paths  # noqa: E402

LEAGUE = ROOT / LEAGUE_PLAYER_PAGES
FOLDER = SeasonPaths(2014, ROOT).record("player_profiles")
# The season's review (either name) closes the season and makes its player folder history.
REVIEWS = tuple(p.relative_to(ROOT).as_posix() for p in season_closeout_paths(2014, ROOT))
POSTSEASON = SeasonPaths(2014, ROOT).postseason_receipts.relative_to(ROOT).as_posix()
JAX = player_cards.JAX
_CTX = None
_BUILT = None
_FOLDER_BUILT = None


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


def folder_built():
    """The build with the season's player folder in it: built() while the season is open; once
    its review has made the folder history (StatusTests), a build of the same stored facts with
    the folder still written, so the folder's rules are proved on a fresh build at every week."""
    global _FOLDER_BUILT
    if _FOLDER_BUILT is None:
        if ctx().folder_open:
            _FOLDER_BUILT = built()
        else:
            opened = copy.copy(ctx())
            opened.folder_open = True
            _FOLDER_BUILT = player_pages.build(ctx=opened)
    return _FOLDER_BUILT


def folder_page(rel):
    """A page of the season's player folder: the committed page while the season is open (it
    equals a fresh build), else the page ``folder_built`` writes."""
    return page(rel) if ctx().folder_open else folder_built()[0][rel]


def reopen(root):
    """Remove the season's review from an overlay ``root`` (its folder must be a copy), so the
    copy's season is open and its player folder is checked and written again; True when a review
    was there."""
    found = [root / rel for rel in REVIEWS if (root / rel).is_file()]
    for path in found:
        path.unlink()
    return bool(found)


def book(year, kind="regular"):
    paths = SeasonPaths(year, ROOT)
    folder = paths.receipts if kind == "regular" else paths.postseason_receipts
    return aggregate_receipts([json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))])


def page(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def season_row(rows, year):
    """A table's one row for the season: labelled the year, or while the season is open the year
    and the latest week his club's games reach, which a bye can hold behind the league's (the
    label itself: test_the_metric_and_the_season_row_read_through_the_as_of_week)."""
    found = [row for key, row in rows.items() if key == str(year) or key.startswith("%d (through " % year)]
    assert len(found) == 1, (year, sorted(rows))
    return found[0]


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


def club_week(club):
    """His club's latest closed regular-season week in the active season, worked out from the
    receipts: a bye leaves it behind the league's latest week."""
    c = ctx()
    return max(w for (team, when), w in c.weeks.items()
               if team == club and when.startswith(str(c.active)) and w not in player_pages.ROUND_NAMES)


def period(club=JAX):
    """The position statistic's period on a page of ``club``'s player: the active season and,
    while it is open, the club's latest regular-season week (the page's As of week)."""
    c = ctx()
    if c.complete.get(c.active, True):
        return str(c.active)
    return "%d, through Week %d" % (c.active, club_week(club))


def jacksonville_games(paths):
    """[(receipt file, receipt)] of Jacksonville's closed regular-season games, in week order."""
    games = []
    for f in sorted(paths.receipts.glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if JAX in r["team_stats"]:
            games.append((r["week"], f, r))
    return [(f, r) for _week, f, r in sorted(games, key=lambda g: g[0])]


def regular_season_only(root, restore=False):
    """Empty an overlay ``root``'s copy of the 2014 playoff receipts (``POSTSEASON``), or with
    ``restore`` copy the repository's back: the bracket is seeded from the regular season, so
    while a regular-season game is taken away no playoff game can be placed, and with none a
    playoff figure has nothing to read."""
    for f in sorted((root / POSTSEASON).glob("*.json")):
        f.unlink()
    for f in sorted((ROOT / POSTSEASON).glob("*.json")) if restore else ():
        shutil.copyfile(f, root / POSTSEASON / f.name)


def game_date(paths, r):
    """A regular-season receipt's game day, from the schedule (a receipt holds no date)."""
    return next(g["date"] for g in json.loads(paths.schedule.read_text(encoding="utf-8"))["games"]
                if (g["week"], g["away"], g["home"]) == (r["week"], r["away"], r["home"]))


def month_day(iso):
    d = player_pages.date.fromisoformat(iso)
    return "%s %d" % (d.strftime("%B"), d.day)


def preview_short():
    """Kirk Cousins's short staff assessment in the user's own words (the preview), as tokens."""
    return {
        "text": "Kirk Cousins has proven he is an NFL starting quarterback. He started all "
                "{{2013.regular.games}} regular-season games for Jacksonville in 2013, led the team to the playoffs "
                "and remains the starter in 2014. He runs the offense well, particularly its protection calls and "
                "short-to-intermediate passing game. Interceptions remain his biggest concern: "
                "{{2013.regular.interceptions_thrown}} in 2013 and {{2014.regular.interceptions_thrown:words}} "
                "through the first {{2014.regular.games:words}} games of 2014.",
        "date": "2014-10-05", "recorded": "2026-10-20", "by": "Jacksonville staff",
        "summarizes": [{"season": 2014, "stage": "opening"}, {"season": 2013, "stage": "final"}],
        "source": "docs/examples/kirk_cousins_player_card_preview.md"}


def with_short(rid, short, index=None):
    """A copy of a record with ``short`` on its latest assessment (or the one at ``index``)."""
    record = copy.deepcopy(people.load_all(ROOT)[rid])
    a = record["assessments"][index] if index is not None else player_pages.latest_assessment(record)
    a["short"] = short
    return record


def opening_index(rid, season=2014):
    """The index of a record's opening assessment of ``season``."""
    return next(i for i, a in enumerate(people.load_all(ROOT)[rid]["assessments"])
                if a["season"] == season and a["stage"] == "opening")


def preview_record(short=None):
    """Kirk Cousins's record as the preview was written for it: ``short`` (else the preview) on
    his 2014 opening assessment and nothing recorded after it, so the opening is his page's
    latest assessment even once the season's final assessment follows it on the record."""
    i = opening_index("kirk_cousins")
    record = with_short("kirk_cousins", short or preview_short(), i)
    record["assessments"] = record["assessments"][:i + 1]
    return record


def shorts(records):
    """(record id, record, assessment) for every assessment that carries a short. A page reads
    its record's latest assessment, so a short a later assessment (the season's final) has
    superseded is read on the record as it stood while it was the latest: cut after it."""
    for rid, record in sorted(records.items()):
        for i, a in enumerate(record["assessments"]):
            if "short" not in a:
                continue
            held = dict(record, assessments=record["assessments"][:i + 1])
            if player_pages.latest_assessment(held) is a:
                yield rid, held, a


def staff_section(text):
    return text.split("## Staff assessment\n\n", 1)[1].split("\n\n## ", 1)[0]


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
        folder = FOLDER.relative_to(ROOT).as_posix() + "/"
        if not ctx().folder_open:  # a closed season's folder is history: neither built nor checked
            self.assertFalse([r for r in files if r.startswith(folder)])
            self.assertNotIn(FOLDER, player_pages.owned_folders(ctx()))
        jaguars = [r for r in folder_built()[0] if r.startswith(folder)]
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
        files, _ = folder_built()
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
            overlay(root, (LEAGUE_PLAYER_PAGES, FOLDER.relative_to(ROOT).as_posix(), PLAYER_RECORDS,
                           Path(REVIEWS[0]).parent.as_posix()))
            # The copy's season is open, so its folder is checked; a folder the review froze is
            # first brought to the open season's build (a closed one is never checked: StatusTests).
            if reopen(root):
                player_pages.write(root)
                self.assertEqual(player_pages.check(root), [])
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
        # Year-only moves keep only the year; a window keeps the source's words. A move since (a
        # reserve list, say) follows them in date order, dated 2014 or later.
        self.assertEqual([(t["date"], t["kind"]) for t in r["transactions"][:2]], [("2012", "signed"), ("2013", "traded")])
        self.assertEqual(r["transactions"][1]["label"], "March 12 to April 24, 2013")
        self.assertFalse([t for t in r["transactions"][2:] if t["date"] < "2014"])
        self.assertEqual(r["transactions"], sorted(r["transactions"], key=people.sort_key))
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
        text = folder_page(self.COUSINS)
        lines = text.splitlines()
        record = ctx().records["kirk_cousins"]
        p = ctx().league_player(record)
        age = player_bios.age_on("1991-08-19", ctx().jax_latest)  # the user's canon birth date
        self.assertEqual(lines[0], "# Kirk Cousins")
        self.assertEqual(lines[2], "**Jacksonville Jaguars · Quarterback · No. 8 · Age %d · %s**"
                         % (age, ctx().roster["Kirk Cousins"][1]))
        self.assertTrue(lines[4].startswith("6' 3\", 202 lb · Born August 19, 1991 · Michigan State · "
                                            "Drafted in 2012, fourth round, by Washington"), lines[4])
        self.assertTrue(lines[6].startswith("As of %s" % player_pages.long_date(ctx().jax_latest)), lines[6])
        headings = [l for l in lines if l.startswith("## ") or l.startswith("### ")]
        self.assertEqual(headings, ["## Staff assessment", "## Contract", "## Statistics", "### Regular season",
                                    "### Playoffs", "## Awards", "## Transactions"])
        # The photo stays below As of; then the assignment, the passer rating, the staff assessment.
        # The assignment is the depth chart's (the starter's seat while he holds it); on a reserve
        # list he has none and the line is left out.
        photo = next(i for i, l in enumerate(lines) if l.startswith("![Kirk Cousins](https://"))
        self.assertTrue(lines[photo + 2].startswith("*Photo: "))
        assignment = player_pages.current_assignment(ctx(), record, p, True)
        if ctx().lists.get("Kirk Cousins") == "active" and ctx().chart["depth"].get("QB", [])[:1] == ["Kirk Cousins"]:
            self.assertEqual(assignment, "Starting quarterback")
        rating = rating_value(book(2014)["players"]["Kirk Cousins"])
        order = [photo] + ([lines.index("**Current assignment:** %s." % assignment)] if assignment else []) + [
            lines.index("**Passer rating:** %.1f (%s)." % (rating, period())), lines.index("## Staff assessment")]
        self.assertEqual(order, sorted(order))
        self.assertGreater(order[0], 6)
        self.assertEqual(bool(assignment), "**Current assignment:**" in text)
        opening = record["assessments"][opening_index("kirk_cousins")]
        section = staff_section(text)
        if player_pages.latest_assessment(record) is not opening:  # the season's final now leads
            self.assertEqual(section, "%s\n\n*%s*" % player_pages.staff_view(ctx(), record, p, self.COUSINS))
        elif "short" in opening:  # its 2014 figures are his Jacksonville games, dated through his last
            self.assertIn("*Staff assessment originally dated March 31, 2014; 2014 results current through %s.*"
                          % month_day(player_pages.jacksonville_block(p, 2014, "regular")["through"]), text)
            self.assertTrue(2 <= people.sentence_count(section.split("\n\n")[0]) <= 4)
        else:  # until his short is written, the staff read as written
            self.assertIn("*Staff view, March 31, 2014; dated updates through %s.*"
                          % player_pages.long_date(max(u["date"] for u in opening["updates"])), text)
        for absent in ("/10", "| Category | Grade |", "{{", "QBR"):
            self.assertNotIn(absent, text)
        y2015 = ctx().finances["Kirk Cousins"]["years"]["2015"]
        self.assertIn("| 2015 | %s | %s |" % (player_pages.money(y2015["base"]), player_pages.money(y2015["cap"])), text)
        self.assertNotIn(".svg", text)
        self.assertNotIn("Week 5 update", text)
        self.assertTrue(text.rstrip().endswith(player_pages.PAGE_MARK))

    def test_a_league_player_shows_no_staff_assessment_and_no_established_contract(self):
        text = page(league_page("A.J. Green", "Cincinnati Bengals"))
        headings = [l for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(headings, ["## Contract", "## Statistics", "## Awards", "## Transactions"])
        # The template: "otherwise say not established"; the records hold no other club's contract.
        self.assertIn("\n## Contract\n\n%s\n\n## Statistics" % player_pages.NO_CONTRACT, text)
        # His Week 1 slot (WR1) with Cincinnati while nothing has moved him (an applied move, or a
        # reserve list from an injury in the closed games, takes the line away), and his yards per
        # target from the statbook.
        c, record = ctx(), ctx().records["a_j_green"]
        p = c.league_player(record)
        self.assertEqual(assignments.week1_assignment(c.week1[("Cincinnati Bengals", record["gsis_id"])]),
                         "Starting wide receiver")
        expected = player_pages.current_assignment(c, record, p, False)
        if record["gsis_id"] not in c.rails_moved and not any(
                ("Cincinnati Bengals", n) in c.branch_reserve for n in p["record_names"]):
            self.assertEqual(expected, "Starting wide receiver")
        if expected is None:
            self.assertNotIn("**Current assignment:**", text)
        else:
            self.assertIn("\n**Current assignment:** %s.\n" % expected, text)
        g = book(2014)["players"]["A.J. Green"]
        self.assertIn("\n**Yards per target:** %.1f (%s).\n" % (g["receiving_yards"] / g["targets"],
                                                               period("Cincinnati Bengals")), text)

    def test_a_former_jaguar_keeps_his_assessment_and_his_moves(self):
        text = page(league_page("Cecil Shorts", "Indianapolis Colts"))
        self.assertIn("## Staff assessment", text)
        self.assertIn("\n## Contract\n\n%s\n" % player_pages.NO_CONTRACT, text)
        self.assertNotIn("| Year | Base salary | Cap charge |", text)
        # The branch placed him at Indianapolis: his Week 1 slot there describes another man's job.
        self.assertNotIn("**Current assignment:**", text)
        self.assertIn("| March 31, 2014 | Traded by Jacksonville to Indianapolis, with Justin Blackmon, "
                      "for 2014 picks No. 82 and No. 194 |", text)

    def test_a_2013_final_sheet_is_read_through_its_owner(self):
        text = page(league_page("Brad Meester", "Jacksonville Jaguars"))
        pointer = player_pages.latest_assessment(ctx().records["brad_meester"])
        self.assertEqual(people.assessment_date(pointer, ROOT), "2014-01-14")  # the sheet's season close
        if "short" in pointer:
            self.assertIn("*Staff view, January 14, 2014.*", text)
        else:
            self.assertIn("*Staff view at the 2013 season close, January 14, 2014.*", text)
        self.assertNotIn("Overall at position", text)
        self.assertNotIn("/10", text)
        # The frozen sheet keeps its grades.
        self.assertIn("5.5/10", page(pointer["owner"]).replace(" /10", "/10"))

    def test_no_page_shows_a_grade(self):
        for rel, text in built()[0].items():
            self.assertNotIn("| Category | Grade |", text, rel)
            self.assertIsNone(re.search(r"\d(?:\.\d)? ?/10\b", text), rel)

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
            row = season_row(regular, year)
            self.assertEqual(row["G"], str(line["games"]))
            self.assertEqual(row["CMP"], "{:,}".format(line["completions"]))
            self.assertEqual(row["ATT"], "{:,}".format(line["pass_attempts"]))
            self.assertEqual(row["YDS"], "{:,}".format(line["passing_yards"]))
            self.assertEqual(row["TD"], str(line["passing_touchdowns"]))
            self.assertEqual(row["INT"], str(thrown(line)))
            self.assertEqual(row["Passer rating"], "%.1f" % rating_value(line))
        playoffs, _ = tables(page(league_page("Kirk Cousins", "Jacksonville Jaguars")), "### Playoffs")
        self.assertEqual(playoffs["2013"]["YDS"], "{:,}".format(book(2013, "playoffs")["players"]["Kirk Cousins"]["passing_yards"]))

    def test_a_receiver_and_a_defender_equal_the_statbook(self):
        green = tables(page(league_page("A.J. Green", "Cincinnati Bengals")))[0]
        watt = tables(page(league_page("J.J. Watt", "Houston Texans")))[0]
        for year in (2013, 2014):
            g = book(year)["players"]["A.J. Green"]
            row = season_row(green, year)
            self.assertEqual((row["Rec"], row["Yards"], row["Targets"]),
                             (str(g["receptions"]), "{:,}".format(g["receiving_yards"]), str(g["targets"])))
            w = book(year)["players"]["J.J. Watt"]
            self.assertEqual(season_row(watt, year)["Tackles"], str(w["tackles"]))
            self.assertEqual(float(season_row(watt, year)["Sacks"]), float(w["sacks"]))

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
        self.assertEqual(season_row(rows, 2014)["Starts"],
                         str(book(2014)["players"]["Luke Joeckel"]["line_starts"]))

    def test_namesakes_keep_their_own_birth_dates(self):
        self.assertIn("Born March 21, 1987", page(league_page("Jonathan Stewart", "Carolina Panthers")))
        self.assertIn("Born November 23, 1990", page(league_page("Jonathan Stewart", "St. Louis Rams")))

    def test_ages_read_the_canon_override(self):
        text = page(league_page("Kirk Cousins", "Jacksonville Jaguars"))
        regular, _ = tables(text)
        self.assertEqual((regular["2013"]["Age"], season_row(regular, 2014)["Age"]), ("22", "23"))
        self.assertEqual(tables(text, "### Playoffs")[0]["2013"]["Age"], "22")
        self.assertEqual((regular["Career" if "Career" in regular else "With Jacksonville"]["Age"]), "")

    def test_the_number_follows_the_season_and_team(self):
        regular, _ = tables(page(league_page("Kirk Cousins", "Jacksonville Jaguars")))
        self.assertEqual((regular["2013"]["#"], season_row(regular, 2014)["#"]), ("N/A", "8"))
        # Jacksonville shows one number once. Another club's number comes from that club's own
        # dated roster (its Week 1 roster or a later week's listing), and no such roster gives one
        # number twice; across the season a club reissues a number a departed player wore (Scott
        # Solomon's 56 at Week 1, Jacquies Smith's from his claim), so the source is part of the key.
        no_club_twice = {}
        codes = ctx().ident.codes
        for p in ctx().data["players"]:
            if p["number"] is None:
                continue
            if p["team"] == JAX:
                no_club_twice.setdefault((p["team"], p["number"]), []).append(p["name"])
                continue
            w1, listed = p["_w1"] or {}, p["_listed"]
            self.assertTrue((w1.get("club") == p["team"] and not w1.get("branch_note")
                             and str(w1.get("jersey")) == str(p["number"]))
                            or (listed.get("number") == p["number"]
                                and (listed.get("number_basis") or {}).get("club") == codes.get(p["team"])), p["name"])
            no_club_twice.setdefault((p["team"], p["number"], p["number_note"]), []).append(p["name"])
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



class ShortRecordTests(unittest.TestCase):
    """The short staff assessment on a record: its schema and the static rules on its words."""

    def errors(self, rid, short, index=None):
        return people.record_errors(rid, with_short(rid, short, index), ROOT)

    def meester(self, **change):
        short = {"text": "Brad Meester was a veteran NFL center who started two games for Jacksonville in 2013. "
                         "His line calls and communication were his best work.",
                 "date": "2014-10-05", "recorded": "2026-10-20", "by": "Jacksonville staff",
                 "summarizes": [{"season": 2013, "stage": "final"}]}
        short.update(change)
        return {k: v for k, v in short.items() if v is not None}

    def test_a_pointer_or_a_transcribed_entry_may_carry_a_short(self):
        self.assertEqual(self.errors("brad_meester", self.meester()), [])
        # The preview on the assessment it was written for, his 2014 opening, wherever it now sits.
        self.assertEqual(self.errors("kirk_cousins", preview_short(), opening_index("kirk_cousins")), [])

    def test_each_broken_rule_is_refused(self):
        found = lambda errors, words: [e for e in errors if words in e]  # noqa: E731
        cases = (
            (self.meester(extra="x"), "keys must be"),
            (self.meester(by=None), "keys must be"),
            (self.meester(text="He started 2 games at center for Jacksonville. His calls were his best work."),
             "every figure in a staff assessment is a token"),
            (self.meester(text="He played in {{2013.regular.snaps}} games. His calls were good."), "unknown measure"),
            (self.meester(text="He played in {{2013.preseason.games}} games. His calls were good."),
             "malformed token"),
            (self.meester(text="He played in {{2012.regular.games}} games. His calls were good."),
             "names a season"),
            (self.meester(text="He threw {{2013.regular.interceptions}} picks. His calls were good."), "ambiguous"),
            (self.meester(text="He had {{2013.regular.passer_rating:words}} as a mark. His calls were good."),
             "formats a rate"),
            (self.meester(text="Brad Meester was a veteran NFL center."), "two to four sentences"),
            (self.meester(text="He was a center. He made calls. He was steady. He was a leader. He retired."),
             "two to four sentences"),
            (self.meester(text="He was a veteran center. See [his sheet](../x.md) for more."), "no link"),
            (self.meester(text="He was a veteran center. His overall grade was high."), "grade or rating"),
            (self.meester(text="He was a veteran center. The engine liked his calls."), "clean-page rule"),
            (self.meester(text="He was a veteran center. No spring record named an individual rep of his."),
             "not a statement about the records"),
            (self.meester(text="He was a veteran center, with nothing charged to him on the recorded reps."
                               " His calls were good."), "not a statement about the records"),
            (self.meester(text="He was a veteran center. His blocking was not individually evaluated."),
             "not a statement about the records"),
            (self.meester(summarizes=[{"season": 2014, "stage": "opening"}]), "the one carrying it"),
            (self.meester(summarizes=[{"season": 2013, "stage": "final"}, {"season": 2014, "stage": "final"}]),
             "not on the record"),
            (self.meester(date="2014-01-13"), "before the assessment it summarizes"),
            (self.meester(date=(player_bios.master_date(ROOT) + timedelta(days=1)).isoformat()), "after the master date"),
            (self.meester(recorded="October 20"), "recorded must be an ISO date"),
            (self.meester(source="docs/no_such_file.md"), "does not exist"),
        )
        for short, words in cases:
            self.assertTrue(found(self.errors("brad_meester", short), words), (short, words))

    def test_abbreviations_do_not_end_a_sentence(self):
        self.assertEqual(people.sentence_count("C.J. Anderson and A.J. Green ran. Charles Leno Jr. wore No. 72 "
                                               "on St. Patrick's Day."), 2)
        self.assertEqual(people.sentence_count("He threw for 82.4 on the year. He was steady!"), 2)


class TokenTests(unittest.TestCase):
    """A short's season figures are read from the closed games when the page is built."""

    def cousins(self):
        record = preview_record()
        return record, ctx().league_player(record)

    def test_the_users_preview_renders_from_the_statbook(self):
        record, p = self.cousins()
        text, line = player_pages.staff_view(ctx(), record, p, "x.md")
        line13, line14 = book(2013)["players"]["Kirk Cousins"], book(2014)["players"]["Kirk Cousins"]
        self.assertIn("all %d regular-season games" % line13["games"], text)
        self.assertIn("concern: %d in 2013 and %s through the first %s games of 2014."
                      % (thrown(line13), player_pages.words(thrown(line14)), player_pages.words(line14["games"])),
                      text)
        # Its 2014 figures are regular-season games, dated through his last Jacksonville one.
        self.assertEqual(line, "Staff assessment originally dated March 31, 2014; 2014 results current through %s."
                         % month_day(player_pages.jacksonville_block(p, 2014, "regular")["through"]))
        # Against the closed games through Week 5 these are the preview's own sentences.
        if ctx().jax_latest == "2014-10-05":
            preview = page("docs/examples/kirk_cousins_player_card_preview.md")
            self.assertIn("\n%s\n\n*%s*\n" % (text, line), preview)
        # The page itself: the short, its dated line and nothing of the grades.
        target = FOLDER.relative_to(ROOT).as_posix() + "/kirk_cousins.md"
        section = staff_section(player_pages.render(ctx(), record, target))
        self.assertEqual(section, "%s\n\n*%s*" % (text, line))

    def test_words_spell_zero_to_nine(self):
        self.assertEqual([player_pages.words(n) for n in (0, 7, 9, 10, 1234)], ["zero", "seven", "nine", "10", "1,234"])
        self.assertEqual(player_pages.words(5, capital=True), "Five")
        with self.assertRaises(ValueError):
            player_pages.words(2.5)

    def test_a_rate_and_a_count_equal_the_statbook(self):
        _, p = self.cousins()
        line = book(2014)["players"]["Kirk Cousins"]
        for token, value in (("{{2014.regular.passer_rating}}", "%.1f" % rating_value(line)),
                             ("{{2014.regular.passing_yards}}", "{:,}".format(line["passing_yards"])),
                             ("{{2014.regular.completion_percentage}}",
                              "%.1f" % (line["completions"] / line["pass_attempts"] * 100)),
                             ("{{2013.playoffs.passing_touchdowns}}",
                              str(book(2013, "playoffs")["players"]["Kirk Cousins"]["passing_touchdowns"]))):
            self.assertEqual(player_pages.resolve_tokens(ctx(), p, token)[0], value, token)

    def test_unresolvable_figures_are_refused(self):
        _, p = self.cousins()
        # The playoff refusal reads him with no 2014 playoff game, so it holds once he has one.
        none = copy.deepcopy(p)
        none["seasons"][2014]["playoffs"] = None
        for club in (none["seasons"][2014].get("by_club") or {}).values():
            club["playoffs"] = None
        for player, token in ((p, "{{2014.regular.field_goal_percentage}}"),   # no attempts
                              (none, "{{2014.playoffs.games}}"),               # no playoff games yet
                              (p, "{{%d.regular.games}}" % (ctx().active + 1)),  # after the active season
                              (p, "{{2014.regular.interceptions}}")):          # ambiguous
            with self.assertRaises(ValueError, msg=token):
                player_pages.resolve_tokens(ctx(), player, token)
        playoffs = player_pages.jacksonville_block(p, 2014, "playoffs")
        if playoffs:  # a playoff game with Jacksonville: the same token resolves to his games
            self.assertEqual(player_pages.resolve_tokens(ctx(), p, "{{2014.playoffs.games}}")[0], str(playoffs["games"]))
        # A former Jaguar's season with another club is never cited.
        shorts = ctx().league_player(ctx().records["cecil_shorts"])
        with self.assertRaises(ValueError):
            player_pages.resolve_tokens(ctx(), shorts, "{{2014.regular.games}}")
        self.assertEqual(player_pages.resolve_tokens(ctx(), shorts, "{{2013.regular.games:Words}}")[0],
                         player_pages.words(book(2013)["players"]["Cecil Shorts"]["games"], capital=True))

    def test_only_figures_after_the_assessment_date_move_the_line(self):
        self.assertEqual(player_pages.date_line("2014-01-14", [(2013, "regular", "2013-12-29")]),
                         "Staff view, January 14, 2014.")
        # With no current figure the line is dated by the view the summary draws on.
        self.assertEqual(player_pages.date_line("2014-03-31", [], "2014-10-04"), "Staff view, October 4, 2014.")
        self.assertEqual(player_pages.date_line("2014-03-31", [(2014, "regular", "2014-10-05")], "2014-10-04"),
                         "Staff assessment originally dated March 31, 2014; 2014 results current through October 5.")
        # Figures that end before that view (he left Jacksonville first) never date the line earlier.
        self.assertEqual(player_pages.date_line("2014-03-31", [(2014, "regular", "2014-09-21")], "2014-10-04"),
                         "Staff view, October 4, 2014; 2014 results current through September 21.")
        self.assertEqual(player_pages.date_line("2014-03-31", [(2014, "playoffs", "2015-01-04")]),
                         "Staff assessment originally dated March 31, 2014; 2014 results current through "
                         "January 4, 2015.")

    @staticmethod
    def line_dates(line):
        """Every date a dated line names, as ISO dates (a month and day take the line's season)."""
        season = re.search(r"(\d{4}) results", line)
        months = [player_pages.date(2000, i, 1).strftime("%B") for i in range(1, 13)]
        out = []
        for m in re.finditer(r"([A-Z][a-z]+) (\d{1,2})(?:, (\d{4}))?", line):
            if m.group(1) in months:
                year = int(m.group(3) or season.group(1))
                out.append(player_pages.date(year, months.index(m.group(1)) + 1, int(m.group(2))).isoformat())
        return out

    def test_the_dated_line_is_never_earlier_than_what_the_short_draws_on(self):
        """The line names the latest dated entry the summary draws on: the assessment's own date or
        its latest dated update up to the summary's date, never an earlier one."""
        c = ctx()
        updated = 0
        for rid, record, a in shorts(c.records):
            view = player_pages.view_date(record, a, ROOT)
            ups = [u["date"] for u in a.get("updates", ()) if u["date"] <= a["short"]["date"]]
            self.assertEqual(view, max([people.assessment_date(a, ROOT)] + ups), rid)
            _text, line = player_pages.staff_view(c, record, c.league_player(record), "x.md")
            self.assertGreaterEqual(max(self.line_dates(line)), view, (rid, line))
            if line.startswith("Staff view, ") and ups and max(ups) > people.assessment_date(a, ROOT):
                self.assertEqual(line, "Staff view, %s." % player_pages.long_date(max(ups)), rid)
                updated += 1
        self.assertTrue(updated)  # shorts with no current figure that draw on a later dated update

    def test_a_game_for_another_club_leaves_his_jacksonville_figures(self):
        """A Jaguar whose latest closed game was for another club (a move in season) keeps his
        short's Jacksonville figures and their cutoff; nothing refuses the check or the write.
        Jacksonville's latest closed game is the scenario, so it holds at every week: without that
        game his figures run through the game before it; with it, and him on the other side, they
        still do."""
        paths = SeasonPaths(2014, ROOT)
        receipts = paths.receipts.relative_to(ROOT).as_posix()
        (_, previous), (last_file, last) = jacksonville_games(paths)[-2:]
        mover = next(record for _rid, record, a in shorts(ctx().records)
                     if "{{2014.regular." in a["short"]["text"] and ".playoffs." not in a["short"]["text"]
                     and all(record["name"] in r["team_stats"][JAX]["players"] for r in (previous, last))
                     and (ctx().league_player(record) or {}).get("seasons", {}).get(2014, {}).get("clubs") == [JAX])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            overlay(root, (LEAGUE_PLAYER_PAGES, FOLDER.relative_to(ROOT).as_posix(), PLAYER_RECORDS, receipts,
                           POSTSEASON))
            regular_season_only(root)
            (root / receipts / last_file.name).unlink()
            earlier = player_pages.Context(root)
            # The game given back with him on the other side (its score, and so the bracket, unchanged).
            other = next(t for t in last["team_stats"] if t != JAX)
            last["team_stats"][other]["players"][mover["name"]] = last["team_stats"][JAX]["players"].pop(mover["name"])
            last.update(injuries=[])
            (root / receipts / last_file.name).write_text(json.dumps(last), encoding="utf-8")
            regular_season_only(root, restore=True)
            later = player_pages.Context(root)
            p = later.league_player(mover)
            self.assertEqual(p["seasons"][2014]["clubs"], [JAX, other])
            before = player_pages.staff_view(earlier, mover, earlier.league_player(mover), "x.md")
            after = player_pages.staff_view(later, mover, p, "x.md")
            self.assertEqual(after, before)  # his Jacksonville games, dated through his last one
            self.assertEqual(player_pages.jacksonville_block(p, 2014, "regular")["through"],
                             max(d for (t, d), w in earlier.weeks.items()
                                 if t == JAX and w not in player_pages.ROUND_NAMES))
            self.assertEqual(player_pages.assessment_errors(later), [])
            self.assertFalse([e for e in player_pages.check(root) if "staff assessment" in e])
            player_pages.write(root)

    def test_a_bad_short_stops_check_and_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            overlay(root, (LEAGUE_PLAYER_PAGES, FOLDER.relative_to(ROOT).as_posix(), PLAYER_RECORDS, POSTSEASON))
            regular_season_only(root)  # no playoff game, so a playoff figure cannot resolve at any week
            short = dict(preview_short(), text=preview_short()["text"].replace("2014.regular.games:words",
                                                                              "2014.playoffs.games:words"))
            record = preview_record(short)
            (root / PLAYER_RECORDS / "kirk_cousins.json").write_text(people.dump(record), encoding="utf-8")
            errors = player_pages.check(root)
            self.assertTrue([e for e in errors if "kirk_cousins.json" in e and "2014.playoffs.games" in e], errors)
            with self.assertRaises(ValueError):
                player_pages.write(root)

    def test_a_closed_game_changes_the_figures_and_the_cutoff_but_not_the_words(self):
        """His latest closed Jacksonville game, taken away and then given back, moves the figures
        and the dated line; the words of the short stay as written."""
        paths = SeasonPaths(2014, ROOT)
        receipts = paths.receipts.relative_to(ROOT).as_posix()
        games = jacksonville_games(paths)
        his = max(i for i, (_f, r) in enumerate(games) if "Kirk Cousins" in r["team_stats"][JAX]["players"])
        record = preview_record()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            overlay(root, (receipts, POSTSEASON))
            regular_season_only(root)
            for f, _r in games[his:]:  # his latest game, and any Jacksonville game after it
                (root / receipts / f.name).unlink()
            earlier = player_pages.Context(root)
            shutil.copyfile(games[his][0], root / receipts / games[his][0].name)
            later = player_pages.Context(root)
            before, before_line = player_pages.staff_view(earlier, record, earlier.league_player(record), "x.md")
            after, after_line = player_pages.staff_view(later, record, later.league_player(record), "x.md")
            games_played = book(2014)["players"]["Kirk Cousins"]["games"]
            self.assertIn("the first %s games" % player_pages.words(games_played - 1), before)
            self.assertIn("the first %s games" % player_pages.words(games_played), after)
            self.assertNotEqual(before_line, after_line)
            self.assertTrue(after_line.endswith("current through %s." % month_day(game_date(paths, games[his][1]))),
                            after_line)
            pattern = lambda t: re.sub(r"\b(\d[\d,]*|zero|one|two|three|four|five|six|seven|eight|nine)\b", "#", t)  # noqa: E731
            self.assertEqual(pattern(before), pattern(after))  # the words never change


class MetricTests(unittest.TestCase):
    """The position statistic: the template's metric for each position, from the closed games."""

    def line(self, name):
        return book(ctx().active)["players"][name]

    def metric(self, name, club):
        return [l for l in page(league_page(name, club)).splitlines()
                if l.startswith("**") and not l.startswith("**Current assignment:**") and " · " not in l]

    def test_each_position_equals_the_statbook(self):
        f1 = lambda v: "%.1f" % v  # noqa: E731
        cases = (
            ("Kirk Cousins", JAX, "Passer rating", lambda l: f1(rating_value(l))),
            ("Maurice Jones-Drew", JAX, "Yards per carry", lambda l: f1(l["rushing_yards"] / l["rushing_attempts"])),
            ("A.J. Green", "Cincinnati Bengals", "Yards per target", lambda l: f1(l["receiving_yards"] / l["targets"])),
            ("Marcedes Lewis", JAX, "Yards per target", lambda l: f1(l["receiving_yards"] / l["targets"])),
            ("J.J. Watt", "Houston Texans", "Sacks", lambda l: player_cards.sack_text(l["sacks"])),
            ("Paul Posluszny", JAX, "Tackles", lambda l: str(l["tackles"])),
            ("Aqib Talib", JAX, "Passes defended", lambda l: str(l["passes_defended"])),
            ("Josh Scobee", JAX, "Field-goal percentage",
             lambda l: f1(l["field_goals_made"] / l["field_goals_attempted"] * 100)),
            ("Casey Kreiter", JAX, "Long snaps", lambda l: str(l["long_snaps"])),
            ("Eugene Monroe", JAX, "Sacks allowed", lambda l: str(l["sacks_allowed"])),
        )
        for name, club, label, value in cases:
            self.assertEqual(self.metric(name, club),
                             ["**%s:** %s (%s)." % (label, value(self.line(name)), period(club))], name)

    def test_the_punters_net_average_is_worked_out_from_the_games(self):
        paths = SeasonPaths(ctx().active, ROOT)
        punts = yards = returned = touchbacks = 0
        for f in sorted(paths.receipts.glob("*.json")):
            r = json.loads(f.read_text(encoding="utf-8"))
            mine = r["team_stats"].get(JAX, {}).get("players", {})
            if "Bryan Anger" not in mine or not mine["Bryan Anger"].get("punts"):
                continue
            self.assertEqual([p for p, l in mine.items() if l.get("punts")], ["Bryan Anger"])  # the only punter
            opp = next(t for t in r["team_stats"] if t != JAX)
            line = mine["Bryan Anger"]
            punts += line["punts"]
            yards += line["punt_yards"]
            touchbacks += line.get("punt_touchbacks", 0)
            returned += sum(l.get("punt_return_yards", 0) for l in r["team_stats"][opp]["players"].values())
        net = (yards - returned - 20 * touchbacks) / punts
        self.assertEqual(self.metric("Bryan Anger", JAX), ["**Net punting average:** %.1f (%s)." % (net, period())])

    def test_no_attempt_or_an_unrecorded_field_omits_the_line(self):
        # Every quarterback with games this season and no pass attempt (a backup who dressed and
        # never threw), worked out from the closed games: an injury that sends Chad Henne in takes
        # him off this list, not the rule.
        idle = [p for p in ctx().data["players"] if p["group"] == "QB"
                and ((p["seasons"].get(ctx().active) or {}).get("regular") or {}).get("games")
                and not p["seasons"][ctx().active]["regular"]["totals"].get("pass_attempts", 0)]
        self.assertTrue(idle)
        for p in idle:
            self.assertIsNone(player_pages.position_metric(ctx(), p, p["pos"]), p["name"])
            rel = "%s/%s/%s.md" % (LEAGUE_PLAYER_PAGES, player_cards.club_slug(p["team"]), p["slug"])
            self.assertNotIn("**Passer rating:**", page(rel), rel)
        anger = copy.deepcopy(ctx().league_player(ctx().records["bryan_anger"]))
        block = anger["seasons"][ctx().active]["regular"]
        block["tiles"] = [(k, "N/A" if k == "NET" else v) for k, v in block["tiles"]]
        self.assertIsNone(player_pages.position_metric(ctx(), anger, "P"))  # not his club's only punter
        kreiter = copy.deepcopy(ctx().league_player(ctx().records["casey_kreiter"]))
        kreiter["seasons"][ctx().active]["regular"]["available"]["long_snaps"] = False
        self.assertIsNone(player_pages.position_metric(ctx(), kreiter, "LS"))
        # A defender's snaps not recorded: his games are the opportunity.
        talib = copy.deepcopy(ctx().league_player(ctx().records["aqib_talib"]))
        talib["seasons"][ctx().active]["regular"]["available"]["defensive_snaps"] = False
        self.assertEqual(player_pages.position_metric(ctx(), talib, "CB")[0], "Passes defended")
        # No game this season: no line.
        self.assertIsNone(player_pages.position_metric(ctx(), ctx().league_player(ctx().records["brad_meester"]), "C"))

    def test_the_metric_and_the_season_row_read_through_the_as_of_week(self):
        """His position statistic, his partial-season row and his As of line name the same week,
        his club's latest: a club whose latest game came before the league's latest week (a bye)
        reads its own week, not the league's."""
        c = ctx()
        if c.complete.get(c.active, True):
            self.skipTest("the season is complete")
        latest = c.latest_week[(c.active, "regular")]
        checked, behind = 0, 0
        for rel, text in built()[0].items():
            if not rel.startswith(LEAGUE_PLAYER_PAGES + "/"):
                continue
            as_of = re.search(r"^As of .*, after Week (\d+)\.$", text, re.M)
            metric = re.search(r"^\*\*[^*]+:\*\* \S+ \(%d, through Week (\d+)\)\.$" % c.active, text, re.M)
            if not (as_of and metric):
                continue
            self.assertEqual(metric.group(1), as_of.group(1), rel)
            self.assertIn("| %d (through Week %s) |" % (c.active, as_of.group(1)), text, rel)
            checked += 1
            behind += int(as_of.group(1)) < latest
        self.assertTrue(checked)
        # Every club whose latest game is behind the league's has its pages checked above.
        early = {t for (t, when), w in c.weeks.items() if when.startswith(str(c.active))
                 and w not in player_pages.ROUND_NAMES and club_week(t) < latest}
        self.assertEqual(bool(early), bool(behind))

    def test_a_metric_is_never_qbr_or_a_rating_of_the_player(self):
        labels = {m[0] for m in player_pages.METRICS.values()}
        self.assertEqual(labels, {"Passer rating", "Yards per carry", "Yards per target", "Sacks", "Tackles",
                                  "Passes defended", "Field-goal percentage", "Net punting average", "Long snaps",
                                  "Sacks allowed"})
        for rel, text in built()[0].items():
            self.assertNotIn("QBR", text, rel)


class AssignmentTests(unittest.TestCase):
    """The Current assignment line: the depth chart's own seats and roles for a Jaguar, the
    season's Week 1 slot for another club's player while nothing has moved him."""

    def depth_page(self):
        return page(SeasonPaths(ctx().active, ROOT).record("depth_chart.md").relative_to(ROOT).as_posix())

    def assignment(self, name):
        rel = FOLDER.relative_to(ROOT).as_posix() + "/%s.md" % people.slugify(name)
        m = re.search(r"^\*\*Current assignment:\*\* (.+)\.$", folder_page(rel), re.M)
        return m.group(1) if m else None

    def rows(self, heading):
        body = self.depth_page().split(heading + "\n", 1)[1].split("\n## ", 1)[0]
        out = []
        for line in [l for l in body.splitlines() if l.startswith("|")][2:]:  # past the head and rule
            cells = [c.strip() for c in line.strip("|").split("|")]
            out.append((cells[0], re.findall(r"\[([^\]]+)\]", cells[1])))
        return out

    def test_every_jaguar_matches_the_depth_chart_page(self):
        seats = {label: words for _group, _i, label, words in assignments.OFFENSE_SEATS}
        depth, roles = ctx().chart["depth"], ctx().chart.get("roles") or {}
        labels = assignments.stone_labels(ctx().working)
        offense = self.rows("## First-unit offense")
        # Every seat with a holder, in order (a group emptied by injuries shows no seat).
        self.assertEqual([seat for seat, _ in offense], [label for group, i, label, _w in assignments.OFFENSE_SEATS
                                                         if i < len(depth.get(group) or [])])
        for seat, names in offense:
            self.assertEqual(self.assignment(names[0]), seats[seat], seat)
        positions = ctx().chart["positions"]
        for _unit, names in self.rows("## Base defense"):
            for name in names:
                self.assertEqual(self.assignment(name), "Starting " + assignments.POSITION_WORDS[positions[name]])
        # A situational role's words, for its first holder unless a seat or Stone's label (which
        # come first) names him, or for the dime seat a role does; else the one shared source's.
        first = {n for g, i, _l, _w in assignments.OFFENSE_SEATS for n in (depth.get(g) or [])[i:i + 1]}
        first |= {n for g, _u, count in assignments.DEFENSE_FIRST for n in (depth.get(g) or [])[:count]}
        first |= {n for g, _j in assignments.SPECIALISTS for n in (depth.get(g) or [])[:1]}
        words = {"Nickel corner": ("Nickel cornerback", set()),
                 "Outside corner reserve": ("Reserve outside cornerback", {"nickel"}),
                 "Dime, sixth defensive back": ("Dime defensive back",
                                                {"nickel", "outside_reserve", "kick_return", "punt_return"})}
        for role, names in self.rows("## Situational defensive roles"):
            text, earlier = words[role]
            name = names[0]
            if name in first or name in labels or earlier & set(roles.get(name) or ()):
                self.assertEqual(self.assignment(name),
                                 assignments.jacksonville_assignment(name, ctx().chart, ctx().working), role)
            else:
                self.assertEqual(self.assignment(name), text, role)
        jobs = {job: names for job, names in self.rows("## Special teams")}
        for job in ("Kicker", "Punter", "Long snapper"):
            self.assertEqual(self.assignment(jobs[job][0]), job)
        # Every player on the active roster has the line the one shared source gives him, and a
        # player the depth chart page names in no seat, label or role has none: like that page,
        # the player page infers no unnamed reserve assignment from the order.
        seated = {depth[g][i] for g, i, _l, _w in assignments.OFFENSE_SEATS if i < len(depth.get(g) or [])}
        seated |= {n for g, _u, count in assignments.DEFENSE_FIRST for n in (depth.get(g) or [])[:count]}
        seated |= {n for g, _j in assignments.SPECIALISTS for n in (depth.get(g) or [])[:1]}
        group, index = assignments.DIME
        seated |= set((depth.get(group) or [])[index:index + 1]) | set((depth.get("QB") or [])[1:2])
        unnamed = 0
        for name, lst in ctx().lists.items():
            expected = (assignments.jacksonville_assignment(name, ctx().chart, ctx().working)
                        if lst == "active" else None)
            self.assertEqual(self.assignment(name), expected, name)
            if lst == "active":
                named = name in seated or name in labels or bool(roles.get(name))
                self.assertEqual(expected is not None, named, name)
                unnamed += not named
            self.assertFalse((expected or "").startswith("Reserve ") and name not in labels
                             and not roles.get(name), name)
        self.assertTrue(unnamed)  # the roster has reserves with no named role

    def test_reserve_lists_and_the_practice_squad_have_no_line(self):
        others = [n for n, lst in ctx().lists.items() if lst != "active"]
        self.assertTrue(others)
        for name in others:
            self.assertIsNone(self.assignment(name), name)

    def test_a_label_without_page_words_fails_the_check(self):
        # A player on the game chart in no seat, with no label and no named role (a receiver when
        # one is such a reserve), worked out from the chart, so a move into a seat, a role or a
        # reserve list never takes the case away.
        c = ctx()
        depth, roles, labels = c.chart["depth"], c.chart.get("roles") or {}, assignments.stone_labels(c.working)
        reserve = next(name for group in ["WR"] + sorted(set(depth) - {"WR"}) for name in depth[group]
                       if c.lists.get(name, "active") == "active" and name not in labels and not roles.get(name)
                       and assignments.jacksonville_assignment(name, c.chart, c.working) is None)
        working = copy.deepcopy(c.working)
        working["stone_role_decisions"].append({"date": "October 6, 2014",
                                                "decisions": [{"player": reserve, "role": "Slot specialist"}]})
        self.assertTrue([e for e in assignments.label_errors(working) if "Slot specialist" in e])
        self.assertEqual(assignments.label_errors(c.working), [])
        with self.assertRaises(ValueError):
            assignments.jacksonville_assignment(reserve, c.chart, working)
        # A later decision with no role clears the label, and an unseated player with no named
        # role then has no confirmed assignment.
        working["stone_role_decisions"].append({"date": "October 7, 2014",
                                                "decisions": [{"player": reserve, "role": None}]})
        self.assertIsNone(assignments.jacksonville_assignment(reserve, c.chart, working))

    def test_every_week1_slot_code_has_words(self):
        self.assertTrue(ctx().library)
        self.assertEqual(assignments.slot_errors(ctx().library), [])
        bad = copy.deepcopy(ctx().library)
        next(iter(bad["clubs"].values()))["players"][0]["slots"] = "ZZ1"
        self.assertTrue(assignments.slot_errors(bad))
        entry = {"player_id": "X", "position": "WR", "slots": "WR2,KR1,PR1"}
        self.assertEqual(assignments.week1_assignment(entry), "Reserve wide receiver")
        self.assertEqual(assignments.week1_assignment(dict(entry, slots="KR1,PR1")), "Kick returner")
        self.assertEqual(assignments.week1_assignment(dict(entry, slots="QB2")), "Backup quarterback")
        self.assertEqual(assignments.week1_assignment(dict(entry, slots="H1")), None)
        self.assertEqual(assignments.week1_assignment(dict(entry, slots="OFF3")), None)
        self.assertEqual(assignments.week1_assignment({"position": "OLB", "slots": "JACK1"}),
                         "Starting outside linebacker")
        self.assertEqual(assignments.week1_assignment(dict(entry, slots="LT2,RT1")), "Starting right tackle")

    def test_moved_and_placed_players_have_no_line(self):
        c = ctx()
        moved = [r for r in c.records.values() if r["gsis_id"] in c.rails_moved and c.league_player(r)
                 and c.league_player(r)["team"] != JAX and (c.league_player(r)["team"], r["gsis_id"]) in c.week1]
        self.assertTrue(moved)
        for record in moved:
            p = c.league_player(record)
            self.assertIsNone(player_pages.current_assignment(c, record, p, False), record["name"])
            rel = "%s/%s/%s.md" % (LEAGUE_PLAYER_PAGES, player_cards.club_slug(p["team"]), p["slug"])
            self.assertNotIn("**Current assignment:**", page(rel), record["name"])
        placed = [r for r in c.records.values() if c.league_player(r)
                  and (c.league_player(r)["team"], r["name"]) in c.week1_added]
        self.assertIn("Cecil Shorts", [r["name"] for r in placed])
        for record in placed:
            self.assertIsNone(player_pages.current_assignment(c, record, c.league_player(record), False))


if __name__ == "__main__":
    unittest.main()
