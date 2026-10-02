"""In-season roster rails (library/2014_inseason_rails.md, runtime/rails.py).

Synthetic fixtures carry every case that needs a move after the master
clock (rules review C5: no post-clock real move is committed or named);
the committed data are checked for the information gate, their stripped
forms, identities, invariants and the closed weeks.
"""
import json
import re
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from runtime import depth_library, rails, week_inputs
from runtime.usage import protection_front
from scripts import build_week_inputs, close_week, render_inseason_rails
from scripts.check_week_input_exclusivity import check_inputs
from scripts.render_season_stats import load_receipts
from runtime.seasons import SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
LAST = {4: date(2014, 9, 27)}


# ---- synthetic league ---------------------------------------------------------------

# 53 players: the first five linemen are LT, LG, C, RG, RT at depths 1 to 5.
LINE = ("T", "G", "C", "G", "T", "T", "G", "C", "G", "T")
GROUPS = (("QB", "QB", 3), ("RB", "RB", 4), ("FB", "FB", 1), ("WR", "WR", 6), ("TE", "TE", 3), ("OL", None, 10),
          ("DL", "DE", 4), ("DL", "DT", 4), ("LB", "OLB", 4), ("LB", "ILB", 3), ("DB", "CB", 5), ("DB", "SS", 2),
          ("DB", "FS", 2), ("K", "K", 1), ("P", "P", 1))
CODES = {"AAA": 1, "BBB": 2, "CCC": 3}


def pid(code, grp, k):
    return "%s %s%d" % (code, grp, k)


def uid(code, grp, k):
    return "90-%03d%s%02d" % (CODES[code], grp[:2].ljust(2, "x"), k)


def synthetic_club(code, size=53):
    players, depth = [], {}
    for grp, pos, count in GROUPS:
        for i in range(count):
            position = LINE[i] if grp == "OL" else pos
            depth[grp] = depth.get(grp, 0) + 1
            k = depth[grp]
            row = {"player_id": pid(code, grp, k), "position": position, "depth": k, "gsis_id": uid(code, grp, k),
                   "slots": "%s%d" % (grp, k)}
            if grp == "K":
                row["roles"] = ["placekicker"]
            if grp == "P":
                row["roles"] = ["punt"]
            players.append(row)
    while len(players) < size:
        depth["WR"] += 1
        k = depth["WR"]
        players.append({"player_id": pid(code, "WR", k), "position": "WR", "depth": k, "gsis_id": uid(code, "WR", k)})
    while len(players) > size:
        last = max((p for p in players if p["position"] == "WR"), key=lambda p: p["depth"])
        players.remove(last)
    return {"code": code, "players": players, "branch_changes": [], "notes": []}


def league(sizes=None, ps=None, verified=None):
    sizes = sizes or {"AAA": 53, "BBB": 53, "CCC": 52}
    library = {"clubs": {"%s Club" % code: synthetic_club(code, n) for code, n in sizes.items()}}
    base = {"clubs": {code: {"base_as_of": {"active": "2014-09-06", "practice_squad": "2014-09-01"},
                             "ps_base_verified": (verified or {}).get(code, False),
                             "practice_squad": (ps or {}).get(code, []), "fill_excluded": []}
                      for code in sizes},
            "corrections": [], "unplaced_former_jaguars": []}
    manifest = {"season": 2014, "effective_from_week": 5, "as_of": "2014-10-04",
                "base": {"path": "base.json", "sha256": "x"}, "shards": []}
    return library, base, manifest


def row(rid, gate, club, kind, uid, pid, pos="WR", outcome="APPLY", efw=5, counterparty=None):
    return {"id": rid, "effective_from_week": efw, "gate_date": gate, "real_date": gate, "club": club, "kind": kind,
            "counterparty": counterparty, "player": pid, "player_id": pid, "uid": uid, "gsis_id": uid,
            "position": pos, "outcome": outcome}


def ps_entry(uid, pid, pos="WR", since="2014-09-01"):
    return {"uid": uid, "player_id": pid, "position": pos, "since": since}


NO_CONTROL = rails.Control({})


def state(rows, library=None, base=None, manifest=None, cutoff="2014-10-04", control=NO_CONTROL, events=(),
          lasts=LAST):
    if library is None:
        library, base, manifest = league()
    data = rails.from_parts(manifest, base, rows, library)
    return rails.league_state(data, date.fromisoformat(cutoff), rails.Branch(control, tuple(events)), lasts)


def actives(st, code):
    return [p["player_id"] for p in st.clubs[code]["active"]]


# ---- ordering (rules review B1) -------------------------------------------------------

class OrderingTests(unittest.TestCase):
    def test_a_readdition_after_a_departure_puts_the_player_back(self):
        st = state([row("R1", "2014-09-09", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6)),
                    row("R2", "2014-09-12", "AAA", "re_signing", uid("AAA", "WR", 6), pid("AAA", "WR", 6))])
        self.assertIn(pid("AAA", "WR", 6), actives(st, "AAA"))
        rec = next(p for p in st.clubs["AAA"]["active"] if p["player_id"] == pid("AAA", "WR", 6))
        wr = [p["depth"] for p in st.clubs["AAA"]["active"] if p["group"] == "WR"]
        self.assertEqual(rec["depth"], max(wr))  # back at the bottom of his group

    def test_a_departure_after_an_in_window_addition_removes_him(self):
        st = state([row("R1", "2014-09-10", "CCC", "fa_signing", "80-0000001", "Free Agent"),
                    row("R2", "2014-09-16", "CCC", "released", "80-0000001", "Free Agent")])
        self.assertNotIn("Free Agent", actives(st, "CCC"))
        self.assertNotIn("80-0000001", st.where)

    def test_same_day_departures_go_first(self):
        # AAA is at 53: the same-day release opens the place for the signing.
        st = state([row("R2", "2014-09-20", "AAA", "fa_signing", "80-0000002", "Newcomer"),
                    row("R1", "2014-09-20", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6))])
        self.assertIn("Newcomer", actives(st, "AAA"))
        self.assertFalse(st.held["AAA"]["active"])

    def test_every_player_ends_where_his_own_applied_rows_put_him(self):
        data = rails.load(2014)
        st = rails.league_state(data, date(2014, 10, 4), rails.Branch(rails.jacksonville_control(2014)), LAST)
        last = {}
        for e in st.log:
            if e["action"].startswith(("added_", "filled_", "removed_")) or e["action"] in ("retired", "implied_ps_release"):
                last[e["uid"]] = e
        for uid, e in last.items():
            loc = st.where.get(uid)
            if e["action"].startswith(("added_", "filled_")):
                layer = e["action"].split("_", 1)[1]
                if loc != (e["club"], layer):
                    # Only a later branch event may have moved him (C6 or Jacksonville).
                    self.assertTrue(loc is None or loc[1] == "reserve", (uid, e, loc))
            else:
                self.assertFalse(loc and loc[0] == e["club"] and loc[1] in ("active", "practice_squad")
                                 and e["action"] != "implied_ps_release", (uid, e, loc))


# ---- holds and freed places (C1 to C4, C7) -------------------------------------------

class HoldTests(unittest.TestCase):
    def test_a_club_at_53_holds_and_a_later_departure_fills_oldest_first(self):
        rows = [row("R1", "2014-09-10", "AAA", "fa_signing", "80-0000001", "First In"),
                row("R2", "2014-09-12", "AAA", "fa_signing", "80-0000002", "Second In"),
                row("R3", "2014-09-15", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6))]
        st = state(rows)
        self.assertIn("First In", actives(st, "AAA"))
        self.assertNotIn("Second In", actives(st, "AAA"))
        self.assertEqual([h["uid"] for h in st.held["AAA"]["active"]], ["80-0000002"])
        self.assertEqual(len(st.clubs["AAA"]["active"]), 53)
        # A held free agent is signed by his real club, awaiting a place: in no TeamInput.
        self.assertEqual(st.where["80-0000002"], ("AAA", "held"))
        self.assertNotIn("Second In", [p["player_id"] for p in st.club_entry("AAA")["players"]])

    def test_the_held_players_own_later_move_cancels_the_hold(self):
        rows = [row("R1", "2014-09-10", "AAA", "fa_signing", "80-0000001", "Wanted"),
                row("R2", "2014-09-12", "CCC", "fa_signing", "80-0000001", "Wanted"),
                row("R3", "2014-09-15", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6))]
        st = state(rows)
        self.assertIn("Wanted", actives(st, "CCC"))
        self.assertFalse(st.held["AAA"]["active"])
        self.assertNotIn("Wanted", actives(st, "AAA"))
        rows = [row("R1", "2014-09-10", "AAA", "fa_signing", "80-0000001", "Wanted"),
                row("R2", "2014-09-12", "AAA", "released", "80-0000001", "Wanted"),
                row("R3", "2014-09-15", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6))]
        st = state(rows)
        self.assertFalse(st.held["AAA"]["active"])
        self.assertTrue(any(e["action"] == "hold_lapsed" for e in st.log))

    def test_a_held_poach_stays_on_his_squad_until_it_fills(self):
        library, base, manifest = league(ps={"BBB": [ps_entry("80-0000003", "Squad Man")]})
        rows = [row("R1", "2014-09-10", "AAA", "ps_poach", "80-0000003", "Squad Man", counterparty="BBB")]
        st = state(rows, library, base, manifest)
        self.assertEqual(st.where["80-0000003"], ("BBB", "practice_squad"))
        st = state(rows + [row("R2", "2014-09-20", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6))],
                   library, base, manifest)
        self.assertIn("Squad Man", actives(st, "AAA"))
        self.assertFalse(st.clubs["BBB"]["practice_squad"])

    def test_the_practice_squad_limit_binds_only_where_the_base_is_verified(self):
        squad = [ps_entry("81-00000%02d" % i, "Squad %d" % i) for i in range(10)]
        rows = [row("R1", "2014-09-10", "AAA", "ps_signing", "80-0000009", "Eleventh"),
                row("R2", "2014-09-10", "BBB", "ps_signing", "80-0000008", "Eleventh B")]
        library, base, manifest = league(ps={"AAA": squad, "BBB": [ps_entry("82-00000%02d" % i, "B Squad %d" % i)
                                                                   for i in range(10)]},
                                         verified={"AAA": True})
        st = state(rows, library, base, manifest)
        self.assertEqual(len(st.clubs["AAA"]["practice_squad"]), 10)
        self.assertEqual([h["uid"] for h in st.held["AAA"]["practice_squad"]], ["80-0000009"])
        self.assertEqual(len(st.clubs["BBB"]["practice_squad"]), 11)

    def test_a_club_over_53_at_the_base_keeps_its_players_and_holds(self):
        library, base, manifest = league(sizes={"AAA": 55, "BBB": 53, "CCC": 52})
        rows = [row("R1", "2014-09-10", "AAA", "fa_signing", "80-0000001", "New One"),
                row("R2", "2014-09-12", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6))]
        st = state(rows, library, base, manifest)
        self.assertEqual(len(st.clubs["AAA"]["active"]), 54)
        self.assertNotIn("New One", actives(st, "AAA"))
        self.assertEqual(st.carry["AAA"], 2)

    def test_real_data_every_addition_saw_a_place_and_every_departure_is_real(self):
        data = rails.load(2014)
        st = rails.league_state(data, date(2014, 10, 4), rails.Branch(rails.jacksonville_control(2014)), LAST)
        self.assertEqual(st.errors, [])
        base = rails.base_state(data, date(2014, 10, 4))
        counts = {code: len(c["active"]) for code, c in base.clubs.items()}
        rows = {r["id"] for r in data.rows}
        for e in st.log:
            if e["action"] in ("added_active", "filled_active"):
                self.assertLess(counts[e["club"]], 53, e)
                counts[e["club"]] += 1
            elif e["action"] == "removed_active":
                self.assertIn(e["ref"], rows)  # never an invented release
                counts[e["club"]] -= 1
            elif e["action"] == "retired" and e["uid"] in {p["uid"] for c in base.clubs.values() for p in c["active"]}:
                counts[e["club"]] -= 1
        for code, c in st.clubs.items():
            self.assertLessEqual(len(c["active"]), max(53, len(base.clubs[code]["active"])))


# ---- C5, C6 and the emergency path ------------------------------------------------------

class InjuryRuleTests(unittest.TestCase):
    def test_a_real_injury_never_touches_membership(self):
        rows = [{"id": "R1", "gate_date": "2014-09-10", "club": "AAA", "outcome": "NOT_APPLIED_INJURY",
                 "effective_from_week": 5, "source_pages": []},
                row("R2", "2014-09-10", "AAA", "fa_signing", "80-0000001", "Replacement")]
        st = state(rows)
        starter = next(p for p in st.clubs["AAA"]["active"] if p["player_id"] == pid("AAA", "QB", 1))
        self.assertTrue(starter["available"])
        self.assertNotIn("Replacement", actives(st, "AAA"))  # held: the injury never happened

    def test_not_applied_rows_are_inert_in_the_committed_data(self):
        data = rails.load(2014)
        control = rails.Branch(rails.jacksonville_control(2014))
        full = rails.league_state(data, date(2014, 10, 4), control, LAST)
        applied = rails.from_parts(data.manifest, data.base, [r for r in data.rows if r["outcome"] == "APPLY"],
                                   data.library, labels=data.labels)
        self.assertEqual(full.digest(), rails.league_state(applied, date(2014, 10, 4), control, LAST).digest())

    def test_branch_reserve_frees_a_place_and_never_touches_jacksonville(self):
        returns = [{"player": pid("AAA", "WR", 6), "team": "AAA Club", "played": date(2014, 10, 5),
                    "back": date(2015, 1, 20), "week": 5},
                   {"player": "Jax Man", "team": "Jacksonville Jaguars", "played": date(2014, 10, 5),
                    "back": date(2015, 1, 20), "week": 5},
                   {"player": pid("AAA", "WR", 5), "team": "AAA Club", "played": date(2014, 10, 5),
                    "back": date(2014, 12, 1), "week": 5}]
        lasts = {**LAST, 5: date(2014, 10, 4)}
        events = rails.c6_events(returns, date(2014, 12, 28), lasts, lambda r: r["week"], 5)
        self.assertEqual([e["player_id"] for e in events], [pid("AAA", "WR", 6)])
        self.assertEqual(events[0]["effective_from_week"], 6)
        rows = [row("R1", "2014-09-20", "AAA", "fa_signing", "80-0000001", "Waiting")]
        st = state(rows, cutoff="2014-10-11", events=events, lasts=lasts)
        self.assertIn("Waiting", actives(st, "AAA"))
        self.assertIn(pid("AAA", "WR", 6), [p["player_id"] for p in st.clubs["AAA"]["reserve"]])
        before = state(rows, cutoff="2014-10-04", events=events, lasts=lasts)
        self.assertNotIn("Waiting", actives(before, "AAA"))  # effective from the next week only

    def test_an_emergency_promotion_gives_a_legal_unit(self):
        library, base, manifest = league(ps={"AAA": [ps_entry("80-0000007", "Squad QB", "QB")]})
        st = state([], library, base, manifest)
        qbs = [p["player_id"] for p in st.clubs["AAA"]["active"] if p["group"] == "QB"]
        out = {pid: date(2014, 11, 1) for pid in qbs}
        events = rails.emergency_events(st, "AAA", 5, out, date(2014, 10, 4), depth_library.available)
        self.assertEqual([e["player_id"] for e in events], ["Squad QB"])
        self.assertIn("reserve_uid", events[0])  # AAA is at 53: its longest-out QB goes on reserve
        after = state([], library, base, manifest, events=events)
        self.assertIn("Squad QB", actives(after, "AAA"))
        self.assertEqual(len(after.clubs["AAA"]["active"]), 53)
        self.assertEqual(rails.emergency_events(after, "BBB", 5, {}, date(2014, 10, 4), depth_library.available), [])


# ---- Jacksonville control, unplaced former Jaguars, retirements -------------------------

class ControlTests(unittest.TestCase):
    def test_a_jacksonville_controlled_player_never_joins_another_club(self):
        control = rails.Control({"80-0000005": ((None, None),)}, names={"80-0000005": "Our Man"})
        st = state([row("R1", "2014-09-10", "BBB", "fa_signing", "80-0000005", "Our Man")], control=control)
        self.assertNotIn("Our Man", actives(st, "BBB"))
        self.assertTrue(any(e["reason"] == "NOT_APPLIED_JAX_CONTROL" for e in st.log))
        # Forced onto a club anyway, both the league-wide and the slate checks fail.
        st.clubs["BBB"]["active"].append(dict(st.clubs["BBB"]["active"][0], uid="80-0000005", player_id="Our Man"))
        st.where["80-0000005"] = ("BBB", "active")
        st.errors = []
        rails.check_rails_state(st, rails.Branch(control))
        self.assertTrue(any("Jacksonville-controlled" in e for e in st.errors))
        unit = depth_library.club_input("BBB Club", st.club_entry("BBB"), offense_anchor=2.0, defense_anchor=2.0,
                                        special_teams_anchor=2.0, week=5)
        package = {"games": [{"away": "BBB Club", "home": "Jacksonville Jaguars", "away_input": unit,
                              "home_input": {"team_id": "Jacksonville Jaguars", "roster": [], "active_players": []}}]}
        self.assertTrue(any("Jacksonville-controlled player appears on BBB Club" in e
                            for e in check_inputs(package, {"Our Man"})))

    def test_real_jaguars_rows_and_unplaced_former_jaguars_are_inert(self):
        library, base, manifest = league()
        base["unplaced_former_jaguars"] = ["80-0000006"]
        rows = [row("R1", "2014-09-10", "JAX", "fa_signing", "80-0000001", "Real Jag"),
                row("R2", "2014-09-10", "BBB", "fa_signing", "80-0000006", "Former Jag")]
        st = state(rows, library, base, manifest)
        self.assertNotIn("80-0000001", st.where)
        self.assertNotIn("80-0000006", st.where)
        self.assertEqual(sorted(e["reason"] for e in st.log if e["action"] == "not_applied"),
                         ["NOT_APPLIED_REAL_JAGUARS", "REVIEW_UNPLACED"])

    def test_a_jacksonville_acquisition_takes_him_off_a_background_squad(self):
        library, base, manifest = league(ps={"BBB": [ps_entry("80-0000004", "Signed By Us")]})
        control = rails.Control({"80-0000004": ((date(2014, 9, 20), None),)}, names={"80-0000004": "Signed By Us"})
        self.assertIn("80-0000004", state([], library, base, manifest, cutoff="2014-09-19", control=control).where)
        self.assertNotIn("80-0000004", state([], library, base, manifest, control=control).where)

    def test_the_real_control_intervals_resolve_every_controlled_player(self):
        control = rails.jacksonville_control(2014)
        self.assertEqual(len(control.controlled_ids(date(2014, 9, 28))), 64)
        ball = next(u for u, n in control.names.items() if n == "Alan Ball")
        self.assertFalse(control.controlled(ball, date(2014, 9, 7)))
        self.assertTrue(control.controlled(ball, date(2014, 9, 8)))
        shaw = next(u for u, n in control.names.items() if n == "Connor Shaw")
        self.assertFalse(control.controlled(shaw, date(2014, 9, 2)))

    def test_retirement_then_a_later_signing(self):
        st = state([row("R1", "2014-09-05", "FA", "retirement", "80-0000002", "Old Pro", "OLB"),
                    row("R2", "2014-09-23", "CCC", "fa_signing", "80-0000002", "Old Pro", "OLB")])
        self.assertIn("Old Pro", actives(st, "CCC"))
        retired = state([row("R1", "2014-09-05", "AAA", "retirement", uid("AAA", "WR", 6), pid("AAA", "WR", 6))])
        self.assertNotIn(pid("AAA", "WR", 6), actives(retired, "AAA"))

    def test_a_jacksonville_retirement_without_its_record_fails_the_build(self):
        control = rails.Control({"80-0000005": ((None, None),)}, names={"80-0000005": "Our Man"})
        # A real retirement applies to Jacksonville too (method section 5):
        # without its retirements.md entry the build fails closed.
        rows = [dict(row("R1", "2014-09-10", "FA", "retirement", "80-0000005", "Our Man"))]
        library, base, manifest = league()
        data = rails.from_parts(manifest, base, rows, library)
        with mock.patch.object(rails, "_effective_outcome", return_value="APPLY"):
            st = rails.league_state(data, date(2014, 10, 4), rails.Branch(control), LAST)
        self.assertTrue(any("retirements.md" in e for e in st.errors))
        ok = rails.Control(control.intervals, frozenset({"Our Man"}), control.names)
        with mock.patch.object(rails, "_effective_outcome", return_value="APPLY"):
            st = rails.league_state(data, date(2014, 10, 4), rails.Branch(ok), LAST)
        self.assertFalse(st.errors)


# ---- cutoffs, the information gate and the Week 5 build -------------------------------

def extended(rows):
    """The committed data plus synthetic rows (never a real post-clock move)."""
    data = rails.load(2014)
    return rails.from_parts(dict(data.manifest, as_of="2014-10-04"), data.base, data.rows + rows, data.library,
                            labels=data.labels)


class CutoffTests(unittest.TestCase):
    def test_week_5_cutoffs_come_from_the_schedule(self):
        cut = rails.slate_cutoffs(week_inputs.schedule(5, 2014))
        by_home = {key.split("|")[2]: day for key, day in cut.items()}
        self.assertEqual(by_home["Green Bay Packers"], date(2014, 10, 1))      # Thursday October 2
        self.assertEqual(by_home["New England Patriots"], date(2014, 10, 4))  # Sunday
        self.assertEqual(by_home["Washington Redskins"], date(2014, 10, 4))   # Monday: October 5 waits a week

    def test_a_jacksonville_thursday_game_or_bye_moves_every_cutoff_back(self):
        for week in (11, 16):
            games = week_inputs.schedule(week, 2014)
            cut = rails.slate_cutoffs(games)
            ours = [g for g in games if "Jacksonville Jaguars" in (g["away"], g["home"])]
            freeze = date.fromisoformat((ours or sorted(games, key=lambda g: g["date"]))[0]["date"])
            self.assertEqual(set(cut.values()), {freeze - timedelta(days=1)})

    def test_building_week_5_before_october_2_applies_exactly_the_rows_on_or_before_the_cutoff(self):
        extra = [row("X1", "2014-09-30", "GB", "fa_signing", "99-0000001", "Synthetic Mover", "WR"),
                 row("X2", "2014-10-01", "GB", "ps_signing", "99-0000002", "Synthetic Squad", "CB"),
                 row("X3", "2014-10-02", "GB", "waived", "99-0000001", "Synthetic Mover", "WR"),
                 row("X4", "2014-10-03", "CLE", "waiver_claim", "99-0000001", "Synthetic Mover", "WR",
                     counterparty="GB"),
                 row("X5", "2014-10-05", "CLE", "ps_signing", "99-0000003", "Synthetic Late", "CB")]
        data = extended(extra)
        control = rails.Branch(rails.jacksonville_control(2014))
        thursday = rails.league_state(data, date(2014, 10, 1), control, LAST)
        refs = {e["ref"] for e in thursday.log}
        applied = {r["id"] for r in data.rows if r["outcome"] == "APPLY" and rails.KINDS[r["kind"]][0] != "inert"}
        due = {rid for rid in applied if rails.replay_date(next(r for r in data.rows if r["id"] == rid), LAST)
               <= date(2014, 10, 1)}
        self.assertEqual(due & applied, {rid for rid in applied if rid in refs})
        self.assertTrue({"X1", "X2"} <= refs)
        self.assertFalse({"X3", "X4", "X5"} & refs)
        self.assertIn("Synthetic Mover", [p["player_id"] for p in thursday.clubs["GB"]["active"]])
        sunday = rails.league_state(data, date(2014, 10, 4), control, LAST)
        self.assertIn("Synthetic Mover", [p["player_id"] for p in sunday.clubs["CLE"]["active"]])
        self.assertNotIn("X5", {e["ref"] for e in sunday.log})

    def test_the_slate_defers_a_player_already_used_by_an_earlier_game(self):
        extra = [row("X1", "2014-09-30", "GB", "fa_signing", "99-0000001", "Synthetic Mover", "WR"),
                 row("X3", "2014-10-02", "GB", "waived", "99-0000001", "Synthetic Mover", "WR"),
                 row("X4", "2014-10-03", "CLE", "waiver_claim", "99-0000001", "Synthetic Mover", "WR",
                     counterparty="GB")]
        data = extended(extra)
        receipts = [r for r in load_receipts(SeasonPaths(2014).receipts)]
        with mock.patch.object(rails, "load", return_value=data):
            slate = week_inputs.rails_slate(5, 2014, receipts)
            clubs, deferred = week_inputs._rails_clubs(slate, week_inputs.schedule(5, 2014), 2014)
        thursday = [c for (key, team), c in clubs.items() if team == "Green Bay Packers"][0]
        sunday = [c for (key, team), c in clubs.items() if team == "Cleveland Browns"][0]
        self.assertIn("Synthetic Mover", [p["player_id"] for p in thursday["players"]])
        self.assertNotIn("Synthetic Mover", [p["player_id"] for p in sunday["players"]])
        self.assertEqual([d["player_id"] for d in deferred], ["Synthetic Mover"])

    def test_a_game_day_row_waits_for_the_clubs_next_game(self):
        games = week_inputs.schedule(5, 2014)
        thursday = next(g for g in games if g["home"] == "Green Bay Packers")
        self.assertLess(rails.slate_cutoffs(games)[rails.game_key(thursday)], date.fromisoformat(thursday["date"]))

    def test_a_late_found_row_never_changes_a_closed_weeks_state(self):
        lasts = {**LAST, 5: date(2014, 10, 4)}
        base_rows = [row("R1", "2014-09-10", "CCC", "fa_signing", "80-0000001", "On Time")]
        late = row("R2", "2014-09-12", "CCC", "fa_signing", "80-0000002", "Found Late", efw=6)
        self.assertEqual(rails.replay_date(late, lasts), date(2014, 10, 5))
        parts = league(sizes={"AAA": 53, "BBB": 53, "CCC": 50})
        week5 = state(base_rows, *parts, cutoff="2014-10-04", lasts=lasts).digest()
        self.assertEqual(week5, state(base_rows + [late], *parts, cutoff="2014-10-04", lasts=lasts).digest())
        self.assertIn("Found Late", actives(state(base_rows + [late], *parts, cutoff="2014-10-11", lasts=lasts), "CCC"))

    def test_a_player_who_has_played_leaves_only_by_a_dated_departure(self):
        lasts = {**LAST, 5: date(2014, 10, 4)}
        receipt = {"week": 5, "away": "AAA Club", "home": "BBB Club",
                   "team_stats": {"AAA Club": {"players": [pid("AAA", "WR", 6)]}, "BBB Club": {"players": []}}}
        dates = {(5, "AAA Club", "BBB Club"): "2014-10-05"}
        codes = {"AAA Club": "AAA", "BBB Club": "BBB"}
        later = state([row("R1", "2014-10-07", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6), efw=6)],
                      cutoff="2014-10-11", lasts=lasts)
        self.assertEqual(rails.receipt_departure_errors(later, [receipt], dates, codes, 5), [])
        silent = state([], cutoff="2014-10-11", lasts=lasts)
        silent.clubs["AAA"]["active"] = [p for p in silent.clubs["AAA"]["active"] if p["player_id"] != pid("AAA", "WR", 6)]
        silent.where.pop(uid("AAA", "WR", 6))
        self.assertTrue(rails.receipt_departure_errors(silent, [receipt], dates, codes, 5))

    def test_the_coverage_gate_blocks_week_5_until_the_moves_reach_its_cutoff(self):
        self.assertIn("committed through 2014-09-28", build_week_inputs.rails_coverage_error(5, 2014))
        self.assertIsNone(build_week_inputs.rails_coverage_error(4, 2014))
        errors = close_week.rails_package_errors({"week": 5}, 5, 2014)
        self.assertEqual(errors, ["package lacks its in-season rails record (rebuild with build_week_inputs.py)"])
        with mock.patch.object(rails, "load", return_value=extended([])):
            self.assertIsNone(build_week_inputs.rails_coverage_error(5, 2014))

    def test_depth_library_requires_a_cutoff_from_the_effective_week(self):
        anchors = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}
        with self.assertRaisesRegex(ValueError, "cutoff date is required"):
            depth_library.team_input("Pittsburgh Steelers", week=5, season=2014, **anchors)
        unit = depth_library.team_input("Pittsburgh Steelers", week=5, season=2014, cutoff=date(2014, 10, 4), **anchors)
        self.assertTrue(unit["roster"])


# ---- closed weeks and determinism ----------------------------------------------------------

class ClosedWeekTests(unittest.TestCase):
    def test_weeks_before_5_return_the_week_1_library_entries(self):
        data = rails.load(2014)
        library = json.loads((ROOT / "library/data/2014_week1_depth_charts.json").read_text())
        self.assertEqual(rails.clubs_block_sha256(library), data.manifest["base"]["library_clubs_sha256"])
        anchors = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}
        for name, club in library["clubs"].items():
            unit = depth_library.team_input(name, week=4, season=2014, **anchors)
            self.assertEqual([p["player_id"] for p in unit["roster"]], [p["player_id"] for p in club["players"]])
        for week in range(1, 5):
            self.assertIsNone(week_inputs.rails_slate(week, 2014, []))

    def test_closed_receipts_rebuild_from_the_week_1_library(self):
        receipts = load_receipts(SeasonPaths(2014).receipts)
        anchors = {"offense_anchor": 2.0, "defense_anchor": 2.0, "special_teams_anchor": 2.0}
        checked = 0
        for r in receipts:
            week = int(r["week"])
            prior = [x for x in receipts if int(x["week"]) < week]
            game = next(g for g in week_inputs.schedule(week, 2014) if g["away"] == r["away"] and g["home"] == r["home"])
            for team in (r["away"], r["home"]):
                if team == "Jacksonville Jaguars":
                    continue
                unit = week_inputs.background_input(team, week, prior, date.fromisoformat(game["date"]), anchors, 2014)
                self.assertEqual(set(unit["active_players"]), set(r["team_stats"][team]["players"]), (week, team))
                checked += 1
        self.assertGreaterEqual(checked, 118)

    def test_the_replay_is_deterministic_and_label_free(self):
        rows = [row("R1", "2014-09-10", "AAA", "fa_signing", "80-0000001", "First In"),
                row("R2", "2014-09-12", "BBB", "fa_signing", "80-0000002", "Other"),
                row("R3", "2014-09-15", "AAA", "waived", uid("AAA", "WR", 6), pid("AAA", "WR", 6))]
        self.assertEqual(state(rows).digest(), state(rows).digest())
        swap = {"AAA": "BBB", "BBB": "AAA", "CCC": "CCC"}
        library, base, manifest = league()
        swapped_library = {"clubs": {"%s Club" % swap[c["code"]]: dict(c, code=swap[c["code"]])
                                     for c in library["clubs"].values()}}
        swapped_base = dict(base, clubs={swap[k]: v for k, v in base["clubs"].items()})
        swapped_rows = [dict(r, club=swap[r["club"]]) for r in rows]
        a = state(rows, library, base, manifest).summary()
        b = state(swapped_rows, swapped_library, swapped_base, manifest).summary()
        self.assertEqual({swap[k]: v for k, v in a.items()}, b)

    def test_the_state_does_not_depend_on_the_opponent(self):
        data = rails.load(2014)
        control = rails.Branch(rails.jacksonville_control(2014))
        first = rails.league_state(data, date(2014, 10, 4), control, LAST)
        with mock.patch.object(week_inputs, "schedule", side_effect=AssertionError("schedule read")):
            second = rails.league_state(data, date(2014, 10, 4), control, LAST)
        self.assertEqual(first.digest(), second.digest())

    def test_the_kernel_never_imports_the_rails(self):
        for name in ("kernel.py", "game_runner.py", "packets.py"):
            text = (ROOT / "runtime" / name).read_text()
            self.assertNotRegex(text, r"\brails\b")


# ---- placement and roles -------------------------------------------------------------------

class PlacementTests(unittest.TestCase):
    def test_a_newcomer_joins_the_bottom_and_departures_leave_gaps(self):
        st = state([row("R1", "2014-09-10", "AAA", "waived", uid("AAA", "OL", 3), pid("AAA", "OL", 3), "C"),
                    row("R2", "2014-09-11", "CCC", "fa_signing", "80-0000001", "New Lineman", "C")])
        ol = sorted(p["depth"] for p in st.clubs["AAA"]["active"] if p["group"] == "OL")
        self.assertNotIn(3, ol)  # the gap stays
        new = next(p for p in st.clubs["CCC"]["active"] if p["player_id"] == "New Lineman")
        self.assertEqual(new["depth"], max(p["depth"] for p in st.clubs["CCC"]["active"] if p["group"] == "OL"))

    def test_releasing_the_center_keeps_the_line_seated(self):
        st = state([row("R1", "2014-09-10", "AAA", "waived", uid("AAA", "OL", 3), pid("AAA", "OL", 3), "C")])
        players = [SimpleNamespace(player_id=p["player_id"], position=p["position"], depth=p["depth"],
                                   roles=(), responsibilities=(), rotation_status=None)
                   for p in st.clubs["AAA"]["active"]]
        front = {slot: p.player_id for slot, p in protection_front(players).items()}
        self.assertEqual((front["LT"], front["LG"], front["RG"], front["RT"]),
                         tuple(pid("AAA", "OL", k) for k in (1, 2, 4, 5)))
        self.assertEqual(next(p for p in players if p.player_id == front["C"]).position, "C")

    def test_a_kicking_role_moves_to_a_newcomer_only_when_vacant(self):
        st = state([row("R1", "2014-09-10", "CCC", "fa_signing", "80-0000001", "Second Kicker", "K")])
        newcomer = next(p for p in st.clubs["CCC"]["active"] if p["player_id"] == "Second Kicker")
        self.assertNotIn("placekicker", newcomer["roles"])
        st = state([row("R1", "2014-09-10", "CCC", "released", uid("CCC", "K", 1), pid("CCC", "K", 1), "K"),
                    row("R2", "2014-09-10", "CCC", "fa_signing", "80-0000001", "New Kicker", "K")])
        kicker = [p for p in st.clubs["CCC"]["active"] if p["group"] == "K"]
        self.assertEqual([k["player_id"] for k in kicker], ["New Kicker"])
        self.assertIn("placekicker", kicker[0]["roles"])

    def test_newcomers_are_available_and_a_movers_week_1_status_travels(self):
        library, base, manifest = league(sizes={"AAA": 53, "BBB": 53, "CCC": 50})
        mover = library["clubs"]["AAA Club"]["players"][20]
        mover.update(available=False, return_week=7)
        rows = [row("R1", "2014-09-10", "AAA", "waived", mover["gsis_id"], mover["player_id"], mover["position"]),
                row("R2", "2014-09-12", "CCC", "fa_signing", mover["gsis_id"], mover["player_id"], mover["position"]),
                row("R3", "2014-09-12", "CCC", "fa_signing", "80-0000001", "Fresh", "WR")]
        st = state(rows, library, base, manifest)
        moved = st.club_entry("CCC")["players"]
        fresh = next(p for p in moved if p["player_id"] == "Fresh")
        self.assertNotIn("available", fresh)
        # Out until Week 7 at Week 1: the status travels through his spell as a free agent.
        moved_row = next(p for p in moved if p["player_id"] == mover["player_id"])
        self.assertEqual((moved_row.get("available"), moved_row.get("return_week")), (False, 7))


# ---- committed data, identities and records -------------------------------------------------

class CommittedDataTests(unittest.TestCase):
    def test_the_data_pass_the_gate_and_schema_checks(self):
        self.assertEqual(rails.data_errors(2014, date(2014, 9, 28)), [])
        self.assertTrue(rails.data_errors(2014, date(2014, 9, 27)))  # a row gated September 28 is past it

    def test_a_row_past_the_clock_fails_validation(self):
        folder = rails.data_dir(2014)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "library/data/2014_inseason_rails"
            target.mkdir(parents=True)
            for f in folder.iterdir():
                (target / f.name).write_bytes(f.read_bytes())
            (root / "library/data/2014_week1_depth_charts.json").write_bytes(
                (ROOT / "library/data/2014_week1_depth_charts.json").read_bytes())
            shard = json.loads((target / "week_05.json").read_text())
            shard["rows"][-1]["gate_date"] = "2014-10-02"
            (target / "week_05.json").write_text(json.dumps(shard))
            manifest = json.loads((target / "manifest.json").read_text())
            manifest["shards"][0]["sha256"] = rails.sha256_file(target / "week_05.json")
            (target / "manifest.json").write_text(json.dumps(manifest))
            with mock.patch.object(rails, "data_dir", return_value=target):
                errors = rails.data_errors(2014, date(2014, 9, 28), root)
        self.assertTrue(any("after the clock" in e for e in errors))

    def test_stripped_rows_carry_no_identity_and_every_row_its_dates(self):
        data = rails.load(2014)
        for r in data.rows:
            self.assertLessEqual(r["gate_date"], data.manifest["as_of"])
            if r["outcome"] in rails.STRIPPED_OUTCOMES:
                self.assertEqual(set(r), set(rails.STRIPPED_FIELDS))
            else:
                self.assertLessEqual(r["real_date"], r["gate_date"])
                self.assertIn(r["kind"], rails.KINDS)
        text = (rails.data_dir(2014) / "week_05.json").read_text()
        self.assertNotIn("designated-for-return", text)

    def test_each_gsis_id_has_one_player_id_and_a_mover_keeps_it(self):
        data = rails.load(2014)
        ids = {}
        entries = [r for r in data.rows if r.get("uid")] + list(data.base["corrections"])
        entries += [p for c in data.base["clubs"].values() for p in c["practice_squad"]]
        for e in entries:
            ids.setdefault(e["uid"], set()).add(e["player_id"])
        for c in data.library["clubs"].values():
            for p in c["players"]:
                if p["gsis_id"] in ids:
                    ids[p["gsis_id"]].add(p["player_id"])
        self.assertEqual({u: v for u, v in ids.items() if len(v) > 1}, {})
        by_id = {}
        for uid, pids in ids.items():
            by_id.setdefault(next(iter(pids)), set()).add(uid)
        self.assertEqual({p: u for p, u in by_id.items() if len(u) > 1}, {})
        cj = [r for r in data.rows if r.get("uid") == "00-0030141"]
        self.assertTrue(cj and all(r["player_id"] == "C.J. Wilson (CHI)" for r in cj))

    def test_the_fill_never_adds_a_controlled_unplaced_or_placed_player(self):
        data = rails.load(2014)
        control = rails.jacksonville_control(2014)
        library = {p["gsis_id"] for c in data.library["clubs"].values() for p in c["players"]}
        for c in data.base["corrections"]:
            if c["kind"] == "fill":
                self.assertNotIn(c["uid"], control.names)
                self.assertNotIn(c["uid"], data.base["unplaced_former_jaguars"])
                self.assertNotIn(c["uid"], library)

    def test_each_player_is_in_one_place_league_wide(self):
        data = rails.load(2014)
        st = rails.league_state(data, date(2014, 10, 4), rails.Branch(rails.jacksonville_control(2014)), LAST)
        self.assertEqual(st.errors, [])
        seen = {}
        for code, c in st.clubs.items():
            for layer, players in c.items():
                for p in players:
                    self.assertNotIn(p["uid"], seen)
                    seen[p["uid"]] = code

    def test_the_week_5_package_joins_every_club_by_gsis(self):
        receipts = load_receipts(SeasonPaths(2014).receipts)
        sheet = json.loads((SeasonPaths(2014).week_folder(4) / "call_sheet.json").read_text())["offensive_call_sheet"]
        package = week_inputs.build_package(5, receipts, sheet, build_week_inputs.AVERAGE_ANCHORS, 2014)
        self.assertEqual(len(package["strength_coverage"]), 30)
        for team, cov in package["strength_coverage"].items():
            self.assertFalse([f for f in cov["fallbacks"] if f["reason"].startswith("identity")], team)
        self.assertEqual(check_inputs(package, set(), "Jacksonville Jaguars", expected_games=15), [])
        self.assertEqual(package["rails"]["as_of"], "2014-09-28")
        for game in package["games"]:
            for side in ("away_input", "home_input"):
                self.assertTrue(all("gsis_id" not in p for p in game[side]["roster"]))

    def test_the_weekly_record_renders_and_no_page_is_written_early(self):
        self.assertEqual(render_inseason_rails.check(2014), [])
        self.assertFalse(render_inseason_rails.page_path(2014, 5).exists())
        text = render_inseason_rails.render(2014, 5)
        self.assertIn("## Held additions", text)
        meta = json.loads(re.search(r"<!-- rails-week: (\{.*?\}) -->", text).group(1))
        self.assertEqual(set(meta["state_digests"]), {"2014-10-01", "2014-10-04"})


class BuilderTests(unittest.TestCase):
    def test_the_builder_refuses_a_date_past_the_clock_and_a_rewrite(self):
        import io
        import contextlib
        import sys
        from scripts.research import build_2014_inseason_rails as builder
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["x", "/nonexistent", "--through", "2014-10-04"]), \
                contextlib.redirect_stdout(out):
            self.assertEqual(builder.main(), 1)
        self.assertIn("after the master date", out.getvalue())
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["x", "/nonexistent", "--through", "2014-09-28"]), \
                contextlib.redirect_stdout(out):
            self.assertEqual(builder.main(), 1)
        self.assertIn("never edited", out.getvalue())

    def test_name_spellings_match_across_sources(self):
        from scripts.research.build_2014_inseason_rails import similar_names
        self.assertTrue(similar_names("Will Poehls", "William Poehls"))
        self.assertTrue(similar_names("Darrin Reaves", "Darrin Reeves"))
        self.assertTrue(similar_names("George Atkinson", "George Atkinson III"))
        self.assertFalse(similar_names("Adarius Taylor", "Adarius Glanton"))


if __name__ == "__main__":
    unittest.main()
