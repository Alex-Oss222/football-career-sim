"""Injury replacement in season, end to end (rebuild step 5, D1; docs/rebuild_plan.md, step 5).

Every test runs in a throwaway copy of the checkout: the copy's open week is closed by relabelling
the week before it (tests/support_roster_moves.py), with Jacksonville injuries of the severities a
test names, and the copy's clock is moved to dated mid-week records. Stone answers through My
Responses (runtime/responses.py), the general manager's decision is a transaction record, and
scripts/apply_transaction.py writes it. Synthetic waiver and signing rows are added to the copy's
league record only, marked as test rows. Weeks and dates come from the fixtures and the receipts,
never from today's date; nothing is written to the real repository and the real private service is
never contacted (the draws use tests/local_private_service.py).
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from datetime import date, timedelta
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import (clean_pages, decision_queue, open_events, people, player_bios, player_contracts,  # noqa: E402
                     rails, responses, transactions as tx)
from runtime import roster as roster_record  # noqa: E402
from runtime.events import annual_record_path, load_events  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from scripts import apply_transaction, injury_events, render_club_pages  # noqa: E402
import support_roster_moves as srm  # noqa: E402
from local_private_service import local_service  # noqa: E402

SEASON = int(json.loads((ROOT / "docs/repository_map.json").read_text(encoding="utf-8"))["active_season"])
GRADE = re.compile(r"/\s*10\b|\bgrad(?:e|es|ed|ing)\b|\brat(?:ed|ing)\b", re.I)


def first(data, position, lists=("active",)):
    return next(r["name"] for r in data["players"] if r["position"] == position and r["list"] in lists)


class Case(unittest.TestCase):
    """A copy with the open week closed; ``close`` names the injuries."""

    def setUp(self):
        self.root = srm.copy_repo(self)
        self.paths = SeasonPaths(SEASON, self.root)
        data = tx.roster(SEASON, self.root)
        self.corner = first(data, "CB")
        self.linebacker = first(data, "LB")
        self.quarterbacks = [r["name"] for r in data["players"] if r["position"] == "QB" and r["list"] == "active"]
        self.squad = [r["name"] for r in data["players"] if r["list"] == "practice_squad"]

    def close(self, injuries):
        self.week, self.game, self.receipt = srm.close_open_week(self.root, SEASON, injuries)
        self.played = date.fromisoformat(self.game["date"])
        self.monday = self.played + timedelta(days=1)
        self.day = self.monday
        self.next = self.week + 1

    def clock(self, hour, day=None, minute=0):
        self.day = day or self.day
        srm.midweek(self.root, self.day, hour, self.next, minute)

    def open_events(self, hour=9):
        self.clock(hour)
        lines = []
        code = injury_events.main([str(self.week), "--season", str(SEASON)], root=self.root, out=lines.append)
        self.assertEqual(code, 0, lines)
        return [e for e in open_events.load(SEASON, self.root) if e["kind"] == tx.KIND]

    def answer(self, event, words, hour=10, conditions=""):
        """Stone's answer on My Responses, checked and applied as the runner does (A3)."""
        queue = decision_queue.load(self.root)
        item = next(i for i in queue["items"] if i["id"] == event["queue_item"])
        period = event["period"]
        record = responses.record_of(SEASON, period, self.root)
        heading = responses.event_heading(event, [b["heading"] for b in record.get("blocks") or ()])
        page = responses.append_block(period, heading, item, self.root, SEASON)
        text = page.read_text(encoding="utf-8")
        block = text[text.index("## %s" % heading):]
        filled = block.replace("**My answer:**\n", "**My answer:** %s\n" % words, 1)
        if conditions:
            filled = filled.replace("**Conditions or instructions:**\n", "**Conditions or instructions:** %s\n"
                                    % conditions, 1)
        page.write_text(text.replace(block, filled), encoding="utf-8")
        self.clock(hour)
        problems, applied = responses.apply(SEASON, period, self.root)
        self.assertEqual(problems, [])
        self.assertEqual(applied, [heading])
        return open_events.get(SEASON, event["id"], self.root)

    def decision(self, event, moves, hour=11, n=1, criteria=0, basis=None, day=None):
        day = day or self.day
        self.clock(hour, day)
        source = event["raised"]["source"]
        return {"schema": tx.SCHEMA, "id": "%s-decision-%d" % (event["id"], n), "season": SEASON,
                "event": event["id"], "date": day.isoformat(), "at": open_events.iso(open_events.et(day, hour)),
                "decided_by": event["authority"]["decides"], "criteria": criteria,
                "recommendation": tx.recommendation_of(event),
                "basis": {"text": basis or "The club keeps its numbers at the position for the next game.",
                          "source": source},
                "moves": moves, "source": source, "status": "decided"}

    def place(self, record):
        path = self.root / ("decision_%s.json" % record["id"])
        path.write_text(json.dumps(record), encoding="utf-8")
        lines = []
        code = apply_transaction.main(["--file", str(path), "--season", str(SEASON)], root=self.root,
                                      out=lines.append)
        return code, lines

    def apply(self, record, rebuild=False, client=None):
        code, lines = self.place(record)
        self.assertEqual(code, 0, lines)
        out = []
        result = apply_transaction.apply(self.root, SEASON, record["id"], client=client, rebuild=rebuild,
                                         out=out.append)
        return result, out

    def medical(self, name):
        return {"text": "No communicated restriction (a test medical communication for %s)" % name,
                "source": self.event_source}

    def reserve(self, name, designation="ordinary"):
        return {"player": name, "kind": "reserve", "from_list": "active", "to_list": "reserve",
                "designation": designation}

    def promote(self, name):
        return {"player": name, "kind": "promoted", "from_list": "practice_squad", "to_list": "active",
                "availability": self.medical(name)}

    def holds(self, kind, week):
        return [i["id"] for i in decision_queue.load(self.root)["items"]
                if decision_queue.holds(i, decision_queue.event(kind, SEASON, week))]


class OpeningTests(Case):
    def test_a_shorter_injury_opens_nothing(self):
        self.close([(self.linebacker, "multi_week", 24)])
        self.assertEqual(self.open_events(), [])
        self.assertEqual(tx.load(SEASON, self.root), [])

    def test_a_long_term_injury_opens_one_event_with_legal_options_and_no_grades(self):
        self.close([(self.corner, "long_term", 70), (self.linebacker, "multi_week", 24)])
        events = self.open_events()
        self.assertEqual([e["subject"] for e in events], [self.corner])
        event = events[0]
        self.assertEqual(event["authority"], {"rows": ["3", "5", "7"], "decides": "caldwell"})
        self.assertEqual(event["stone_part"], "recommends")
        self.assertEqual(event["process"][0]["kind"], "criteria")
        names = {o["name"] for o in event["options"]}
        self.assertTrue(set(self.squad) <= names)
        for text in [f["value"] for f in event["facts"]] + [o["basis"] for o in event["options"]] + \
                [event["process"][0]["what"]]:
            self.assertIsNone(GRADE.search(text), text)
        # A second run opens nothing new: one event per open roster question.
        self.assertEqual(len(self.open_events()), 1)
        self.assertEqual(open_events.validation_errors(self.root), [])
        # The answer it asks for holds its own event only: Sunday's game is not held by it.
        self.assertEqual(self.holds("week_inputs", self.next), [])
        self.assertEqual(self.holds("event_resolution", None) if False else [], [])

    def test_a_close_without_the_medical_communication_is_refused(self):
        self.close([(self.corner, "long_term", 70)])
        data = json.loads(self.paths.roster.read_text(encoding="utf-8"))
        row = next(r for r in data["players"] if r["name"] == self.corner)
        row["availability"] = "No communicated restriction"
        self.paths.roster.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
        self.clock(9)
        lines = []
        self.assertEqual(injury_events.main([str(self.week), "--season", str(SEASON)], root=self.root,
                                            out=lines.append), 1)
        self.assertIn("medical communication", lines[-1])


class DecisionTests(Case):
    def setUp(self):
        super().setUp()
        self.close([(self.corner, "long_term", 70)])
        self.event = self.open_events()[0]
        self.event_source = self.event["raised"]["source"]["path"]

    def test_the_decision_is_apart_from_stones_answer_and_two_wordings_give_one_record(self):
        thomas = next(n for n in self.squad if n in {o["name"] for o in self.event["options"]})
        answered = self.answer(self.event, "I recommend %s for the place." % thomas)
        substance = answered["response"]["substance"]
        self.assertEqual(substance, {"kind": "recommend", "option": thomas})
        other = responses.compile_substance("%s. He knows the calls and is ready to play on Sunday." % thomas, "",
                                            answered)
        self.assertEqual(other, substance)
        # The general manager may decide otherwise: the record keeps Stone's substance, apart.
        chosen = next(n for n in self.squad if n != thomas)
        record = self.decision(answered, [self.reserve(self.corner), self.promote(chosen)])
        twin = copy.deepcopy(record)
        twin["recommendation"] = other
        self.assertEqual(record, twin)
        result, out = self.apply(record)
        self.assertEqual(result, "applied", out)
        stored = tx.get(SEASON, record["id"], self.root)
        self.assertEqual(stored["recommendation"], substance)
        self.assertEqual([m["player"] for m in stored["moves"]], [self.corner, chosen])

    def test_a_decision_without_its_preceding_criteria_is_refused(self):
        answered = self.answer(self.event, "I recommend %s." % self.squad[0])
        responses_at = [n for n, e in enumerate(answered["process"]) if e["kind"] == "response"][0]
        record = self.decision(answered, [self.reserve(self.corner), self.promote(self.squad[0])],
                               criteria=responses_at)
        code, lines = self.place(record)
        self.assertEqual(code, 1)
        self.assertIn("criteria", lines[-1])
        self.assertEqual(tx.load(SEASON, self.root), [])

    def test_a_decision_while_stones_answer_is_due_is_refused(self):
        record = self.decision(self.event, [self.reserve(self.corner), self.promote(self.squad[0])])
        self.clock(11)
        code, lines = self.place(record)
        self.assertEqual(code, 0, lines)
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        self.assertIn("due", str(caught.exception))

    def test_after_the_apply_every_record_agrees(self):
        thomas = self.squad[-1]
        answered = self.answer(self.event, "I recommend %s." % thomas)
        # The close's page rebuild opens the next week (its briefing, Game Plan and index) first.
        from scripts import rebuild_pages
        self.assertEqual(rebuild_pages.rebuild(self.root, SEASON)[1], [])
        plan_page = decisions_page(self.root, self.next)
        self.assertIsNotNone(plan_page)
        before = digests(self.root, self.next)
        log_before = len(json.loads(self.paths.record("team/depth_chart/update_log.json").read_text())["entries"])
        record = self.decision(answered, [self.reserve(self.corner), self.promote(thomas)])
        result, out = self.apply(record, rebuild=True)
        self.assertEqual(result, "applied", out)
        self.assertEqual(tx.validation_errors(self.root), [])
        # The roster record, the rails' control and the exclusivity gate on the next week's inputs,
        # built in the copy by the game path's own builder (Week 5's frozen sheet standing in).
        gate = subprocess.run([sys.executable, "-c", GATE, str(self.root), str(self.next)], cwd=str(self.root),
                              capture_output=True, text=True, env={"PYTHONPATH": str(self.root), "PATH": "/usr/bin:/bin"})
        self.assertEqual(gate.stdout.strip().splitlines()[-1:], ["[]"], gate.stderr[-2000:])
        data = tx.roster(SEASON, self.root)
        rows = {r["name"]: r for r in data["players"]}
        self.assertEqual(rows[self.corner]["list"], "reserve")
        self.assertEqual(rows[thomas]["list"], "active")
        self.assertEqual(roster_record.counts(data)["active"], 53)
        registry = player_bios.load(self.root)
        control = rails.jacksonville_control(SEASON, self.root)
        self.assertTrue(control.controlled(registry[thomas]["gsis_id"], self.monday))
        self.assertTrue(control.controlled(registry[self.corner]["gsis_id"], self.monday))
        from scripts.check_week_input_exclusivity import controlled_players_from_roster
        self.assertIn(thomas, controlled_players_from_roster(self.paths.roster))
        # The contract records, the players block and the chart with its log.
        self.assertEqual(player_contracts.errors(self.root), [])
        current = player_contracts.contract_on(player_contracts.load(people.slugify(thomas), self.root))
        self.assertEqual(current["start"]["method"]["name"], "promotion")
        chart = json.loads(self.paths.depth_chart.read_text(encoding="utf-8"))
        self.assertNotIn(self.corner, sum(chart["depth"].values(), []))
        self.assertEqual(chart["depth"]["DB"][-1], thomas)
        log = json.loads(self.paths.record("team/depth_chart/update_log.json").read_text())["entries"]
        self.assertEqual(len(log), log_before + 1)
        # The player records and the one result page.
        prec = people.load_all(self.root)
        self.assertEqual(prec[people.slugify(thomas)]["transactions"][-1]["kind"], "promoted")
        for rid, record_ in prec.items():
            self.assertEqual(people.record_errors(rid, record_, self.root), [])
        event = open_events.get(SEASON, self.event["id"], self.root)
        self.assertEqual(event["state"], "resolved")
        page = self.root / event["resolution"]["result_page"]
        self.assertTrue(page.name.startswith("Transaction_%s_" % self.monday.isoformat()))
        text = page.read_text(encoding="utf-8")
        self.assertEqual(clean_pages.page_errors(page.relative_to(self.root).as_posix(), text, root=self.root), [])
        self.assertIn(self.event["id"], load_events(self.root))
        self.assertIn(thomas, annual_record_path(self.root, SEASON).read_text(encoding="utf-8"))
        self.assertEqual(open_events.validation_errors(self.root), [])
        # The Game Plan and the call sheet of the next week are untouched (F11).
        self.assertEqual(digests(self.root, self.next), before)
        self.assertEqual(decisions_page(self.root, self.next), plan_page)
        # The pages were rebuilt with the moves: the club pages check clean against the new records.
        self.assertEqual(render_club_pages.check(self.root), [])
        # Applied once: a second apply is refused.
        with self.assertRaises(tx.Refused):
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)

    def test_a_missing_identity_fails(self):
        answered = self.answer(self.event, "I recommend %s." % self.squad[0])
        former = next(o["name"] for o in answered["options"] if "former" in o["basis"])
        registry_path = self.root / "library/data/player_birth_dates.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["players"].pop(former, None)
        registry_path.write_text(json.dumps(registry, indent=1), encoding="utf-8")
        record = self.decision(answered, [self.reserve(self.corner), {
            "player": former, "kind": "signed", "from_list": "none", "to_list": "active", "via": "former_player",
            "availability": self.medical(former), "contract": {"credited_seasons": 0, "source": self.event_source}}])
        code, lines = self.place(record)
        self.assertEqual(code, 0, lines)
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        self.assertIn("gsis id", str(caught.exception))

    def test_a_practice_squad_of_eleven_fails(self):
        answered = self.answer(self.event, "I recommend %s." % self.squad[0])
        formers = [o["name"] for o in answered["options"] if "former" in o["basis"]]
        registry = player_bios.load(self.root)
        formers = [n for n in formers if (registry.get(n) or {}).get("birth_date")]
        open_places = 10 - len(self.squad)
        moves = [{"player": n, "kind": "practice_squad", "from_list": "none", "to_list": "practice_squad",
                  "via": "former_player"} for n in formers[:open_places + 1]]
        self.assertEqual(len(moves), open_places + 1)
        record = self.decision(answered, moves)
        code, lines = self.place(record)
        self.assertEqual(code, 0, lines)
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        self.assertIn("practice squad", str(caught.exception))

    def test_a_release_is_not_built(self):
        answered = self.answer(self.event, "I recommend %s." % self.squad[0])
        record = self.decision(answered, [{"player": self.linebacker, "kind": "released", "from_list": "active",
                                           "to_list": "none"}])
        code, lines = self.place(record)
        self.assertEqual(code, 1)
        self.assertIn("put to the user", lines[-1])

    def test_a_paused_game_records_nothing(self):
        answered = self.answer(self.event, "I recommend %s." % self.squad[0])
        record = self.decision(answered, [self.reserve(self.corner), self.promote(self.squad[0])])
        self.assertEqual(self.place(record)[0], 0)
        pause = self.paths.paused_game(self.next)
        pause.parent.mkdir(parents=True, exist_ok=True)
        pause.write_text(json.dumps({"status": "paused"}), encoding="utf-8")
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        self.assertIn("paused", str(caught.exception))
        self.assertEqual(tx.get(SEASON, record["id"], self.root)["status"], "decided")
        # A paused game's substitutions are its own record: the game is not closed, so no roster
        # question opens from it.
        lines = []
        self.assertEqual(injury_events.main([str(self.next), "--season", str(SEASON)], root=self.root,
                                            out=lines.append), 1)
        self.assertIn("not closed", lines[-1])


class RecommendationTests(Case):
    def test_stone_raises_one_by_his_recommendation(self):
        self.close([(self.linebacker, "multi_week", 24)])
        self.assertEqual(self.open_events(), [])
        page = self.root / "career" / str(SEASON) / "Team_Operations" / "Team" / "Roster" / "test_recommendation.md"
        page.write_text("# Test recommendation\n\nA test page of Stone's.\n", encoding="utf-8")
        rel = page.relative_to(self.root).as_posix()
        lines = []
        self.assertEqual(injury_events.main(["--recommend", self.linebacker, "--source", rel, "--season", str(SEASON)],
                                            root=self.root, out=lines.append), 0, lines)
        event = next(e for e in open_events.load(SEASON, self.root) if e["subject"] == self.linebacker)
        self.assertEqual((event["raised"]["by"], event["authority"]["decides"]), ("stone", "caldwell"))
        self.assertEqual(open_events.validation_errors(self.root), [])
        # Without a page of his that names it: refused.
        self.assertEqual(injury_events.main(["--recommend", self.corner, "--season", str(SEASON)], root=self.root,
                                            out=lines.append), 1)


class DueTimeTests(Case):
    def test_past_the_due_time_with_no_answer_the_general_manager_decides(self):
        self.close([(self.corner, "long_term", 70)])
        event = self.open_events()[0]
        self.event_source = event["raised"]["source"]["path"]
        due = open_events.parse_at(event["deadline"]["at"])
        record = self.decision(event, [self.reserve(self.corner), self.promote(self.squad[0])],
                               hour=due.hour + 1, day=due.date())
        self.assertEqual(record["recommendation"], "none on file")
        result, out = self.apply(record)
        self.assertEqual(result, "applied", out)
        item = next(i for i in decision_queue.load(self.root)["items"] if i["id"] == event["queue_item"])
        self.assertEqual((item["status"], item["resolution"]["by"]), ("WITHDRAWN", "organization"))
        self.assertIn(open_events.DUE_TIME_SUMMARY, item["resolution"]["summary"])
        page = self.root / open_events.get(SEASON, event["id"], self.root)["resolution"]["result_page"]
        self.assertIn("No recommendation was given", page.read_text(encoding="utf-8"))
        self.assertEqual(open_events.validation_errors(self.root), [])


class LegalTeamTests(Case):
    def test_a_legal_team_vacancy_holds_the_build_until_the_move_is_applied(self):
        starter, backup = self.quarterbacks[:2]
        self.close([(starter, "long_term", 70), (backup, "multi_week", 24)])
        events = self.open_events()
        self.assertEqual([e["subject"] for e in events], [starter])
        event = events[0]
        self.assertTrue(open_events.cannot_dress(event))
        held = self.holds("week_inputs", self.next)
        self.assertEqual(sorted(held), sorted([event["queue_item"], event["id"] + "-transaction"]))
        self.event_source = event["raised"]["source"]["path"]
        squad_qb = next(n for n in self.squad if tx.roster(SEASON, self.root)["players"][
            [r["name"] for r in tx.roster(SEASON, self.root)["players"]].index(n)]["position"] == "QB")
        answered = self.answer(event, "I recommend %s." % squad_qb)
        # Stone's answer alone never releases the build: the general manager's item still holds it.
        self.assertEqual(self.holds("week_inputs", self.next), [event["id"] + "-transaction"])
        record = self.decision(answered, [self.reserve(starter), self.promote(squad_qb)])
        result, out = self.apply(record)
        self.assertEqual(result, "applied", out)
        self.assertEqual(self.holds("week_inputs", self.next), [])
        self.assertEqual(open_events.validation_errors(self.root), [])


class TwoEventTests(Case):
    def test_two_injuries_make_two_events_two_pages_and_two_results(self):
        self.close([(self.corner, "long_term", 70), (self.linebacker, "long_term", 70)])
        events = self.open_events()
        self.assertEqual(sorted(e["subject"] for e in events), sorted([self.corner, self.linebacker]))
        self.event_source = events[0]["raised"]["source"]["path"]
        pages = []
        for n, (event, hour) in enumerate(zip(sorted(events, key=lambda e: e["subject"]), (10, 12))):
            answered = self.answer(event, "I recommend %s." % self.squad[n], hour=hour)
            record = self.decision(answered, [self.reserve(event["subject"]), self.promote(self.squad[n])],
                                   hour=hour + 1)
            self.clock(hour + 1)
            result, out = self.apply(record)
            self.assertEqual(result, "applied", out)
            pages.append(open_events.get(SEASON, event["id"], self.root)["resolution"]["result_page"])
        self.assertEqual(len(set(pages)), 2)
        results, _ = open_events.period_events(SEASON, {"week": self.next}, self.root)
        self.assertEqual(sorted(r["resolution"]["result_page"] for r in results if r["kind"] == tx.KIND),
                         sorted(pages))
        listed = annual_record_path(self.root, SEASON).read_text(encoding="utf-8")
        for event in events:
            self.assertIn(event["id"], load_events(self.root))
        self.assertEqual(open_events.validation_errors(self.root), [])


class ReturnTests(Case):
    def test_the_designated_player_returns_through_the_same_tool_and_needs_a_place(self):
        data = tx.roster(SEASON, self.root)
        row = next(r for r in data["players"] if "designated for return" in r["status"].lower())
        name = row["name"]
        window = tx.return_window(row)
        self.close([(self.linebacker, "multi_week", 24)])
        # Before the eight weeks: refused.
        self.clock(9, window[1] - timedelta(days=1))
        with self.assertRaises(tx.Refused):
            tx.return_event(SEASON, name, self.root)
        # On the day, without the medical staff's clearance: refused.
        self.clock(9, window[1])
        with self.assertRaises(tx.Refused) as caught:
            tx.return_event(SEASON, name, self.root)
        self.assertIn("clearance", str(caught.exception))
        # With the clearance recorded, the question opens; the full 53 means he needs a place.
        data = json.loads(self.paths.roster.read_text(encoding="utf-8"))
        row = next(r for r in data["players"] if r["name"] == name)
        row["availability"] = "No communicated restriction (a test clearance on %s)" % srm.week_pages.long_date(window[1])
        self.paths.roster.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        lines = []
        self.assertEqual(injury_events.main(["--return", name, "--season", str(SEASON)], root=self.root,
                                            out=lines.append), 0, lines)
        event = next(e for e in open_events.load(SEASON, self.root) if e["subject"] == name)
        self.event_source = event["raised"]["source"]["path"]
        answered = self.answer(event, "I support his return to the 53.", hour=10)
        back = {"player": name, "kind": "reinstated", "from_list": "reserve", "to_list": "active",
                "availability": self.medical(name)}
        record = self.decision(answered, [back], hour=11)
        code, lines = self.place(record)
        self.assertEqual(code, 0, lines)
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        self.assertIn("above the 53", str(caught.exception).replace("53 allowed", "53"))
        # A place made by a reserve placement in the same decision: applied.
        record2 = self.decision(answered, [self.reserve(self.linebacker), back], hour=11, n=2)
        result, out = self.apply(record2)
        self.assertEqual(result, "applied", out)
        rows = {r["name"]: r for r in tx.roster(SEASON, self.root)["players"]}
        self.assertEqual(rows[name]["list"], "active")
        self.assertIn("returned from reserve/injured", rows[name]["status"])


class WaiverTests(Case):
    """Synthetic waiver and claim rows in the copy's league record (test rows only)."""

    def add_rows(self, rows, as_of):
        folder = rails.data_dir(SEASON, self.root)
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        shard = folder / manifest["shards"][-1]["path"]
        data = json.loads(shard.read_text(encoding="utf-8"))
        data["rows"].extend(rows)
        shard.write_text(json.dumps(data, indent=1), encoding="utf-8")
        manifest["as_of"] = as_of.isoformat()
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        rails._load.cache_clear()

    def row(self, n, kind, club, player, when, counterparty=None):
        registry = player_bios.load(self.root)
        ident = registry[player]
        return {"id": "R14-9%03d" % n, "effective_from_week": self.next, "gate_date": when.isoformat(),
                "real_date": when.isoformat(), "date_basis": "test", "club": club, "kind": kind, "kind_basis": "test",
                "counterparty": counterparty, "player": player, "player_id": player, "uid": ident["gsis_id"],
                "gsis_id": ident["gsis_id"], "position": "CB", "kernel_group": "DB",
                "birth_date": ident.get("birth_date"), "identity_basis": "test", "outcome": "APPLY",
                "reason": "a test row", "verification": "test", "sources": {}, "source_pages": [],
                "research_ref": "test"}

    def setUp(self):
        super().setUp()
        self.close([(self.corner, "long_term", 70)])
        # A background corner on another club's roster, with an identity on the registry.
        week1 = json.loads((self.root / "library/data/2014_week1_depth_charts.json").read_text(encoding="utf-8"))
        registry = player_bios.load(self.root)
        self.waiver_club, self.player = None, None
        for club, info in sorted(week1["clubs"].items()):
            if club == srm.JAX:
                continue
            for row in info.get("players") or ():
                name = row.get("player_id")
                if row.get("position") == "CB" and (registry.get(name) or {}).get("birth_date") and \
                        (registry.get(name) or {}).get("gsis_id") == row.get("gsis_id"):
                    self.waiver_club, self.player = info["code"], name
                    break
            if self.player:
                break
        self.assertIsNotNone(self.player, "no background corner with an identity in the Week 1 library")

    def claim(self):
        """A waived background corner, Stone's recommendation and the general manager's claim, placed."""
        self.add_rows([self.row(1, "waived", self.waiver_club, self.player, self.monday)], self.monday)
        event = self.open_events(hour=9)[0]
        self.event_source = event["raised"]["source"]["path"]
        candidates = [o for o in event["options"] if o["name"] == self.player]
        self.assertEqual(len(candidates), 1, [o["name"] for o in event["options"]])
        self.assertNotIn("cleared", candidates[0]["basis"])
        answered = self.answer(event, "I recommend %s." % self.player)
        claim = {"player": self.player, "kind": "claimed", "from_list": "none", "to_list": "active",
                 "via": "waiver_claim", "waived_on": self.monday.isoformat(), "position": "CB",
                 "availability": self.medical(self.player)}
        record = self.decision(answered, [self.reserve(self.corner), claim])
        self.assertEqual(self.place(record)[0], 0)
        # Before the league's record of the day's claims is in: refused, naming no move.
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        self.assertIn("claim period", str(caught.exception))
        return event, record, tx.claim_period_end(self.monday)

    def order(self, day):
        rows = tx.waiver_order(SEASON, day, self.root)
        mine = dict((r[0], r[1]) for r in rows)[open_events.employer_club(self.root)]
        ahead = [r[0] for r in rows if tx._pct(r[1]) < tx._pct(mine)]
        behind = [r[0] for r in rows if tx._pct(r[1]) > tx._pct(mine)]
        return ahead, behind

    def settle(self, record, end, claimant=None):
        rows = []
        if claimant is not None:
            rows.append(self.row(2, "waiver_claim", tx.club_codes(SEASON, self.root)[claimant], self.player,
                                 end.date(), self.waiver_club))
        self.add_rows(rows, end.date() + timedelta(days=1))
        self.clock(9, end.date() + timedelta(days=1))
        return apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)

    def test_a_claim_no_club_made_is_awarded_when_its_period_ends(self):
        event, record, end = self.claim()
        self.assertEqual(self.settle(record, end), "applied")
        rows = {r["name"]: r for r in tx.roster(SEASON, self.root)["players"]}
        self.assertEqual(rows[self.player]["list"], "active")
        self.assertIn("claimed", rows[self.player]["status"])
        registry = player_bios.load(self.root)
        self.assertTrue(rails.jacksonville_control(SEASON, self.root).controlled(registry[self.player]["gsis_id"],
                                                                                 end.date()))
        current = player_contracts.contract_on(player_contracts.load(people.slugify(self.player), self.root))
        self.assertIn("Unresolved", current["start"]["value_text"])
        self.assertEqual(player_contracts.errors(self.root), [])
        self.assertEqual(tx.get(SEASON, record["id"], self.root)["award"]["claimed_by"], None)
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(tx.validation_errors(self.root), [])

    def test_a_claim_against_a_club_ahead_in_the_order_is_lost(self):
        event, record, end = self.claim()
        ahead, _ = self.order(end.date())
        if not ahead:
            self.skipTest("no club stands ahead of Jacksonville in the copy's order")
        self.assertEqual(self.settle(record, end, ahead[0]), "claim_lost")
        stored = tx.get(SEASON, record["id"], self.root)
        self.assertEqual((stored["status"], stored["award"]["claimed_by"]), ("claim_lost", ahead[0]))
        event = open_events.get(SEASON, event["id"], self.root)
        self.assertNotEqual(event["state"], "resolved")
        self.assertIn(ahead[0], event["process"][-1]["what"])
        rows = {r["name"] for r in tx.roster(SEASON, self.root)["players"]}
        self.assertNotIn(self.player, rows)
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(tx.validation_errors(self.root), [])

    def test_a_claim_against_a_club_behind_in_the_order_is_awarded(self):
        event, record, end = self.claim()
        _, behind = self.order(end.date())
        self.assertTrue(behind)
        self.assertEqual(self.settle(record, end, behind[-1]), "applied")
        stored = tx.get(SEASON, record["id"], self.root)
        self.assertEqual((stored["award"]["claimed_by"], stored["award"]["jacksonville"]), (behind[-1], True))
        self.assertEqual(open_events.validation_errors(self.root), [])

    def test_a_section_4_pursuit_waits_for_the_real_signing_and_is_drawn_against_it(self):
        self.add_rows([self.row(1, "released", self.waiver_club, self.player, self.monday - timedelta(days=3))],
                      self.monday)
        event = self.open_events(hour=9)[0]
        self.event_source = event["raised"]["source"]["path"]
        free = next(f for f in event["facts"] if f["label"] == "Free agents Jacksonville may pursue")
        self.assertIn(self.player, free["value"])
        answered = self.answer(event, "I recommend %s." % self.squad[0])
        pursue = {"player": self.player, "kind": "signed", "from_list": "none", "to_list": "active", "via": "section_4",
                  "position": "CB", "availability": self.medical(self.player),
                  "offer": {"method": "in_season_minimum", "credited_seasons": 3, "source": self.event_source}}
        record = self.decision(answered, [self.reserve(self.corner), pursue])
        self.assertEqual(self.place(record)[0], 0)
        # He has signed nowhere: there is no contract to compare, so no draw and no signing.
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        message = str(caught.exception)
        self.assertIn("has not signed with any club", message)
        self.assertIn("cannot be drawn", message)
        # His real signing, still ahead of the clock, is never read: the refusal names no later move.
        signed = self.monday + timedelta(days=2)
        codes = tx.club_codes(SEASON, self.root)
        other = next(c for n, c in sorted(codes.items()) if c not in (self.waiver_club, "JAX"))
        self.add_rows([self.row(2, "fa_signing", other, self.player, signed)], signed)
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        later = str(caught.exception)
        self.assertIn("has not signed with any club", later)
        self.assertNotIn(tx.club_name(SEASON, other, self.root), later)
        self.assertNotIn(tx.long_date(signed), later)
        # Once his real signing is public, without the contract he signed, no draw.
        srm.midweek(self.root, signed, 18, self.next)
        with self.assertRaises(tx.Refused) as caught:
            apply_transaction.apply(self.root, SEASON, record["id"], rebuild=False, out=lambda *_: None)
        self.assertIn("researched under the two-pass rule", str(caught.exception))
        # With a far richer real contract the money index is below 0.80: the chance is 0 and he signs there.
        stored = tx.get(SEASON, record["id"], self.root)
        stored["moves"][1]["comparison"] = {"apy": 10000000, "guarantee": 5000000, "source": self.event_source}
        tx.write(stored, self.root)
        snapshot = hashlib.sha256((self.root / srm.STATE).read_bytes()).hexdigest()
        _, client = local_service(self, self.root / "private", "pursuit", snapshot=snapshot)
        result = apply_transaction.apply(self.root, SEASON, record["id"], client=client, rebuild=False,
                                         out=lambda *_: None)
        self.assertEqual(result, "pursuit_lost")
        stored = tx.get(SEASON, record["id"], self.root)
        self.assertEqual(stored["draw"]["chance"], 0.0)
        self.assertEqual(set(stored["draw"]["inputs"]), {"jacksonville", "real", "offer_date", "signing_date"})
        self.assertNotIn(self.player, json.dumps(stored["draw"]["inputs"]))
        self.assertEqual(open_events.validation_errors(self.root), [])


GATE = r"""
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); sys.path.insert(0, str(root))
from runtime.seasons import SeasonPaths
from runtime.week_inputs import build_package
from scripts.build_week_inputs import AVERAGE_ANCHORS
from scripts.render_season_stats import load_receipts
from scripts.check_week_input_exclusivity import check_inputs, controlled_players_from_roster
paths = SeasonPaths(int(json.loads((root / "docs/repository_map.json").read_text())["active_season"]), root)
week = int(sys.argv[2])
frozen = max(w for w in range(1, week) if paths.call_sheet(w).is_file())
sheet = json.loads(paths.call_sheet(frozen).read_text(encoding="utf-8"))
receipts = [r for r in load_receipts(paths.receipts) if int(r["week"]) < week]
package = build_package(week, receipts, sheet["offensive_call_sheet"], AVERAGE_ANCHORS, paths.year,
                        decisions=sheet.get("decisions"), defensive_sheet=sheet.get("defensive_call_sheet"))
print(check_inputs(package, controlled_players_from_roster(paths.roster), expected_games=len(package["games"])))
"""


class PursuitWinTests(WaiverTests):
    test_a_claim_no_club_made_is_awarded_when_its_period_ends = None
    test_a_claim_against_a_club_ahead_in_the_order_is_lost = None
    test_a_claim_against_a_club_behind_in_the_order_is_awarded = None
    test_a_section_4_pursuit_waits_for_the_real_signing_and_is_drawn_against_it = None

    def test_a_won_draw_signs_him_at_his_real_signing_date(self):
        self.add_rows([self.row(1, "released", self.waiver_club, self.player, self.monday - timedelta(days=3))],
                      self.monday)
        event = self.open_events(hour=9)[0]
        self.event_source = event["raised"]["source"]["path"]
        answered = self.answer(event, "I recommend %s." % self.squad[0])
        pursue = {"player": self.player, "kind": "signed", "from_list": "none", "to_list": "active", "via": "section_4",
                  "position": "CB", "availability": self.medical(self.player),
                  "offer": {"method": "in_season_minimum", "credited_seasons": 3, "source": self.event_source},
                  "comparison": {"apy": 645000, "guarantee": 0, "source": self.event_source}}
        record = self.decision(answered, [self.reserve(self.corner), pursue])
        self.assertEqual(self.place(record)[0], 0)
        signed = self.monday + timedelta(days=2)
        codes = tx.club_codes(SEASON, self.root)
        other = next(c for n, c in sorted(codes.items()) if c not in (self.waiver_club, "JAX"))
        self.add_rows([self.row(2, "fa_signing", other, self.player, signed)], signed)
        self.clock(18, signed)
        snapshot = hashlib.sha256((self.root / srm.STATE).read_bytes()).hexdigest()
        _, client = local_service(self, self.root / "private", "pursuit-win", snapshot=snapshot)
        # A fixed reference gives a fixed result: with the chance fixed at one the draw goes to Jacksonville.
        with patch.object(tx, "chance", lambda m: 1.0):
            result = apply_transaction.apply(self.root, SEASON, record["id"], client=client, rebuild=False,
                                             out=lambda *_: None)
        self.assertEqual(result, "applied")
        stored = tx.get(SEASON, record["id"], self.root)
        self.assertTrue(stored["draw"]["jacksonville"])
        self.assertEqual(stored["applied"]["date"], signed.isoformat())
        rows = {r["name"]: r for r in tx.roster(SEASON, self.root)["players"]}
        self.assertIn("signed %s" % srm.week_pages.long_date(signed), rows[self.player]["status"])
        signing = self.root / stored["applied"]["signings"][self.player]
        self.assertTrue(signing.is_file())
        self.assertIn(signing.name, (self.paths.record("free_agency") / "signings.md").read_text(encoding="utf-8"))
        self.assertEqual(clean_pages.text_errors(signing.relative_to(self.root).as_posix(),
                                                 signing.read_text(encoding="utf-8"), self.root), [])
        registry = player_bios.load(self.root)
        self.assertTrue(rails.jacksonville_control(SEASON, self.root).controlled(registry[self.player]["gsis_id"], signed))
        self.assertEqual(player_contracts.errors(self.root), [])
        self.assertEqual(open_events.validation_errors(self.root), [])
        self.assertEqual(tx.validation_errors(self.root), [])


def digests(root, week):
    from runtime import decisions
    pages = decisions.week_pages(SEASON, week, root)
    out = {}
    for path in (pages.plan, pages.data / "call_sheet.json", pages.data / "applied_plan.json"):
        out[path.name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return out


def decisions_page(root, week):
    from runtime import decisions
    path = decisions.week_pages(SEASON, week, root).plan
    return path.read_bytes() if path.is_file() else None


if __name__ == "__main__":
    unittest.main()
