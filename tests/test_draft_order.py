"""2014 draft order from the closed 2013 branch receipts (runtime.draft_order)."""
import unittest
import copy
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

from runtime import draft_order, postseason


class DraftOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.regular = draft_order._load(postseason.REGULAR_RECEIPTS)
        cls.post = draft_order._load(postseason.POSTSEASON_RECEIPTS)
        cls.rows = draft_order.order(cls.regular, cls.post, coin_flip={})
        cls.by_club = {r["club"]: r for r in cls.rows}

    def test_every_club_once_in_32_slots(self):
        self.assertEqual([r["slot"] for r in self.rows], list(range(1, 33)))
        self.assertEqual(len(self.by_club), 32)

    def test_playoff_groups_follow_elimination(self):
        groups = [r["group"] for r in self.rows]
        self.assertEqual(groups[:20], ["non-playoff"] * 20)
        self.assertEqual(groups[20:], ["wild_card"] * 4 + ["divisional"] * 4 + ["conference"] * 2
                         + ["super_bowl_loser", "champion"])
        self.assertEqual(self.rows[-1]["club"], postseason.winner(
            next(r for r in self.post if int(r["week"]) == 21)))

    def test_non_playoff_order_is_by_percentage_then_sos(self):
        head = self.rows[:20]
        for a, b in zip(head, head[1:]):
            self.assertLessEqual((a["pct"], round(a["sos"], 6)), (b["pct"], round(b["sos"], 6)))

    def test_jacksonville_lost_divisional(self):
        self.assertEqual(self.by_club["Jacksonville Jaguars"]["group"], "divisional")
        self.assertIn(self.by_club["Jacksonville Jaguars"]["slot"], range(25, 29))

    def test_cross_conference_tie_is_never_resolved_by_invention(self):
        for r in self.rows:
            if r["tie"] and r["tie"].startswith("coin flip pending"):
                self.assertTrue(any(o["tie"] and r["club"] in o["tie"] for o in self.rows))

    def test_order_requires_a_closed_super_bowl(self):
        with self.assertRaises(ValueError):
            draft_order.order(self.regular, [r for r in self.post if int(r["week"]) != 21])


class SevenRoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first = draft_order.order(coin_flip={})
        cls.register = draft_order.load_ownership()
        cls.rows = draft_order.seven_rounds(cls.first, cls.register)

    def asset(self, rnd, club):
        return next(r for r in self.rows if r["round"] == rnd and r["club"] == club)

    def test_all_224_assets_once_and_each_round_has_32_original_clubs(self):
        self.assertEqual(len(self.rows), 224)
        self.assertEqual(len({(r["round"], r["club"]) for r in self.rows}), 224)
        for rnd in range(1, 8):
            rows = [r for r in self.rows if r["round"] == rnd]
            self.assertEqual({r["club"] for r in rows}, set(draft_order.TEAMS))
            self.assertEqual({slot for r in rows for slot in r["slot_options"]}, set(range(1, 33)))
            self.assertEqual(len([r for r in rows if r["coin_flip_pending"]]), 2)

    def test_two_club_rotation_changes_seattle_second_to_36(self):
        self.assertEqual(self.asset(1, "Seattle Seahawks")["slot_options"], [5])
        self.assertEqual(self.asset(2, "Seattle Seahawks")["base_overall_options"], [36])
        self.assertEqual(self.asset(2, "Houston Texans")["base_overall_options"], [37])
        self.assertEqual(self.asset(3, "Seattle Seahawks")["slot_options"], [5])

    def test_larger_segment_rotates_even_when_sos_is_different(self):
        first = ["Denver Broncos", "Cleveland Browns", "Detroit Lions", "Chicago Bears", "Oakland Raiders", "Miami Dolphins"]
        for rnd in range(1, 8):
            offset = (rnd - 1) % len(first)
            expected = first[offset:] + first[:offset]
            actual = [r["club"] for r in self.rows if r["round"] == rnd and r["slot_options"][0] in range(7, 13)]
            self.assertEqual(actual, expected)

    def test_playoff_priority_groups_never_rotate_together(self):
        # Buffalo, KC, Pittsburgh and Tampa Bay all finished 9-7. The champion
        # remains 32; only the three Wild Card losers rotate among 21-23.
        for rnd in range(1, 8):
            self.assertEqual(self.asset(rnd, "Buffalo Bills")["slot_options"], [32])
            slots = [self.asset(rnd, c)["slot_options"][0] for c in
                     ("Kansas City Chiefs", "Pittsburgh Steelers", "Tampa Bay Buccaneers")]
            self.assertEqual(set(slots), {21, 22, 23})
            self.assertEqual(self.asset(rnd, "Dallas Cowboys")["slot_options"], [25])
            self.assertEqual(self.asset(rnd, "Philadelphia Eagles")["slot_options"], [29])

    def test_coin_uncertainty_matches_both_possible_realizations_every_round(self):
        # Independently enumerate the two permitted first-round arrangements.
        scenarios = []
        for reverse in (False, True):
            first = copy.deepcopy(self.first)
            if reverse:
                first[13], first[14] = first[14], first[13]
                first[13]["slot"], first[14]["slot"] = 14, 15
            for row in first:
                if row["tie"] and row["tie"].startswith("coin flip pending"):
                    row["tie"] = "test-only recorded coin result"
            scenarios.append(draft_order.seven_rounds(first, self.register))
        for row in self.rows:
            possibilities = set()
            for scenario in scenarios:
                actual = next(r for r in scenario if (r["round"], r["club"]) == (row["round"], row["club"]))
                possibilities.update(actual["slot_options"])
            self.assertEqual(set(row["slot_options"]), possibilities)
        self.assertEqual(self.asset(2, "Green Bay Packers")["slot_options"], [14, 19])

    def test_no_alphabetical_coin_result_for_same_conference(self):
        season = Mock(recording=False, notes=[])
        def fallback(*args):
            season.notes.append({"step": None})
            return "Miami Dolphins"
        season.best_of.side_effect = fallback
        rows = draft_order._break(season, ["Miami Dolphins", "New York Jets"], {})
        self.assertTrue(all(note.startswith("coin flip pending") for _, note in rows))
        self.assertFalse(season.recording)
        self.assertEqual(season.notes, [])

    def test_corrected_cousins_deal_has_one_owner_for_each_asset(self):
        washington = self.asset(1, "Washington Redskins")
        self.assertEqual(washington["owner"], "Jacksonville Jaguars")
        self.assertEqual(washington["base_overall_options"], [13])
        self.assertEqual(self.asset(1, "Jacksonville Jaguars")["base_overall_options"], [26])
        second = self.asset(2, "Jacksonville Jaguars")
        self.assertEqual((second["owner"], second["base_overall_options"]), ("Washington Redskins", [58]))
        owned = [r for r in self.rows if r["owner"] == "Jacksonville Jaguars"]
        self.assertEqual(len(owned), 9)  # No. 38 (Entry 99); Nos. 82 and 194 in (Entry 104) and out to Washington (Entry 105)
        self.assertEqual([r["round"] for r in owned], [1, 1, 2, 3, 4, 5, 5, 6, 7])
        self.assertEqual(draft_order.ownership_for(2015, 2, "Jacksonville Jaguars", self.register)[0], "Jacksonville Jaguars")  # returned by Washington (Entry 105)
        self.assertEqual(self.asset(1, "St. Louis Rams")["owner"], "St. Louis Rams")

    def test_traded_pick_follows_original_club_rotation_not_current_owner(self):
        carolina = self.asset(7, "Carolina Panthers")
        self.assertEqual(carolina["owner"], "San Francisco 49ers")
        self.assertEqual(carolina["slot_options"], [19])
        self.assertEqual(self.asset(7, "San Francisco 49ers")["slot_options"], [1])

    def test_compensatory_awards_fix_overall_numbers_after_round_three(self):
        comp = self.register["compensatory"]
        self.assertEqual(comp["status"], "announced")  # March 24, 2014, Entry 100
        self.assertEqual(comp["qualifying_free_agency_year"], 2013)
        self.assertEqual(sum(comp["round_counts"].values()), 32)
        for rnd in range(1, 8):
            row = self.asset(rnd, "Jacksonville Jaguars")
            self.assertEqual(row["compensatory_after_rounds"], list(range(3, rnd)))
        self.assertEqual(self.asset(3, "Jacksonville Jaguars")["base_overall_options"], [90])
        from scripts.render_draft_order import overall
        counts = comp["round_counts"]
        self.assertEqual(overall(self.asset(4, "Jacksonville Jaguars")), "122 + C3")
        self.assertEqual(overall(self.asset(4, "Jacksonville Jaguars"), counts), "129")
        self.assertEqual(overall(self.asset(7, "Jacksonville Jaguars"), counts), "241")

    def test_compensatory_awards_follow_the_adopted_method(self):
        import json
        from scripts import resolve_compensatory_picks as comp
        awards = json.loads(comp.OUT.read_text())
        self.assertEqual(awards, comp.resolve())
        self.assertEqual(len(awards["picks"]), 32)
        self.assertEqual({p["round"] for p in awards["picks"]} <= set(range(3, 8)), True)
        per_club = {}
        for p in awards["picks"]:
            if p["kind"] == "formula":
                per_club[p["club"]] = per_club.get(p["club"], 0) + 1
        self.assertLessEqual(max(per_club.values()), 4)
        self.assertEqual([p for p in awards["picks"] if p["club"] == "Jacksonville Jaguars"], [])
        self.assertEqual(awards["method_sha256"], comp.sha(comp.METHOD))
        overall = [p["overall"] for p in awards["picks"]]
        self.assertEqual(len(set(overall)), 32)
        self.assertEqual(max(overall), 256)

    def test_ownership_register_rejects_double_ownership_and_invalid_assets(self):
        bad = []
        duplicate = copy.deepcopy(self.register)
        extra = copy.deepcopy(duplicate["transfers"][0])
        extra["owner"] = "St. Louis Rams"
        duplicate["transfers"].append(extra)
        bad.append(duplicate)
        for field, value in (("round", 8), ("owner", "Unknown Team"), ("draft_year", 2013)):
            record = copy.deepcopy(self.register)
            record["transfers"][0][field] = value
            bad.append(record)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "picks.json"
            for record in bad:
                with self.subTest(record=record["transfers"][-1]):
                    path.write_text(json.dumps(record))
                    with self.assertRaises(ValueError):
                        draft_order.load_ownership(path)

    def test_chiefs_payment_uses_branch_condition(self):
        row = self.asset(2, "Kansas City Chiefs")
        self.assertEqual(row["ownership_status"], "recorded")
        self.assertEqual(row["owner"], "San Francisco 49ers")
        self.assertEqual(self.asset(3, "Kansas City Chiefs")["owner"], "Kansas City Chiefs")
        self.assertEqual(next(r for r in self.first if r['club'] == 'Kansas City Chiefs')['record'], '9-7-0')


class RecordedDrawAndOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = draft_order.seven_rounds()
        cls.register = draft_order.load_ownership()
        cls.draw = json.loads(draft_order.COIN_FLIP.read_text())

    def test_saved_single_draw_resolves_every_round_without_redraw(self):
        self.assertEqual(self.draw['result'], 'tails')
        self.assertEqual(self.draw['site_result'], '0 obverse, 1 reverse')
        self.assertEqual(self.draw['flip_count'], 1)
        self.assertEqual(self.draw['observed_at'], '2026-09-29T01:42:47Z')
        for club, expected in [('Indianapolis Colts', [14,19,18,17,16,15,14]),
                               ('Green Bay Packers', [15,14,19,18,17,16,15])]:
            self.assertEqual([r['slot_options'] for r in self.rows if r['club'] == club], [[n] for n in expected])
        for rnd in range(1, 8):
            self.assertEqual(sorted(r['slot_options'][0] for r in self.rows if r['round'] == rnd), list(range(1,33)))
        self.assertFalse(any(r['coin_flip_pending'] for r in self.rows))
        self.assertEqual(draft_order.seven_rounds(), self.rows)

    def test_coin_record_rejects_changed_winner_protocol_and_evidence(self):
        for field, value in [('winner','Green Bay Packers'), ('flip_count',2),
                             ('winner_slot',13), ('rerolls_permitted',True),
                             ('screenshot_sha256','0'*64)]:
            bad = dict(self.draw, **{field:value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                draft_order.order(coin_flip=bad)
        unrelated = draft_order.order(coin_flip={})
        unrelated[13]['club'] = 'Miami Dolphins'
        with self.assertRaises(ValueError):
            draft_order.apply_coin_flip(unrelated, self.draw)

    def test_all_assets_have_one_current_owner_and_specific_hold_status(self):
        self.assertEqual(len(self.rows),224)
        self.assertEqual(len({(r['draft_year'],r['round'],r['club']) for r in self.rows}),224)
        self.assertEqual(sum(r['ownership_status']=='recorded' for r in self.rows),20)  # No. 38 (Entry 99); Nos. 82 and 194 (Entries 104 and 105)
        self.assertEqual(sum(r['ownership_status']=='encumbered' for r in self.rows),10)
        self.assertFalse(any(r['ownership_status']=='provisional' for r in self.rows))
        self.assertEqual(sum(sum(r['owner']==c for r in self.rows) for c in draft_order.TEAMS),224)

    def test_inherited_detroit_fifth_not_missing_or_duplicated(self):
        row = next(r for r in self.rows if r['round']==5 and r['club']=='Detroit Lions')
        self.assertEqual(row['owner'],'Jacksonville Jaguars')
        self.assertEqual(row['base_overall_options'],[139])
        self.assertEqual(row['compensatory_after_rounds'],[3,4])
        self.assertEqual(sum(r['owner']=='Jacksonville Jaguars' for r in self.rows),9)  # No. 38 (Entry 99); Nos. 82 and 194 to Washington (Entry 105)

    def test_specific_claims_cannot_be_spent_or_booked_twice(self):
        self.assertEqual({c['id'] for c in self.register['conditional_claims']},{'revis','benn','rosario'})
        for claim in self.register['conditional_claims']:
            self.assertEqual(claim['max_picks'],1)
            for rnd in claim['round_options']:
                owner,status,_ = draft_order.ownership_for(2014,rnd,claim['original_club'],self.register)
                self.assertEqual(owner,claim['original_club'])
                self.assertEqual(status,'encumbered')
                with self.assertRaises(ValueError):
                    draft_order.require_clear_ownership(2014,rnd,claim['original_club'],self.register)
        self.assertEqual(draft_order.require_clear_ownership(2014,1,'Washington Redskins'),'Jacksonville Jaguars')
        for year,rnd,club in [(2015,1,'Dallas Cowboys'),(2014,8,'Dallas Cowboys')]:
            with self.assertRaises(ValueError):
                draft_order.require_clear_ownership(year,rnd,club)

    def test_register_rejects_future_transfer_missing_club_and_overlapping_claim(self):
        variants=[]
        bad=copy.deepcopy(self.register); bad['transfers'][0]['effective_date']='2014-06-01'; variants.append(bad)
        bad=copy.deepcopy(self.register); bad['audited_clubs'].pop(); variants.append(bad)
        bad=copy.deepcopy(self.register); bad['conditional_claims'].append(copy.deepcopy(bad['conditional_claims'][0])); variants.append(bad)
        bad=copy.deepcopy(self.register); bad['conditional_claims'][0]['original_club']='Jacksonville Jaguars'; bad['conditional_claims'][0]['round_options']=[2]; variants.append(bad)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'picks.json'
            for bad in variants:
                path.write_text(json.dumps(bad))
                with self.assertRaises(ValueError): draft_order.load_ownership(path)

    def test_closed_branch_receipts_prevent_real_midseason_transfer_import(self):
        regular=draft_order._load(postseason.REGULAR_RECEIPTS)
        for player,club,rounds in [('Trent Richardson','Cleveland Browns',[]),
                                  ('Isaac Sopoaga','Philadelphia Eagles',[6]),
                                  ('Jon Beason','Carolina Panthers',[]),
                                  ('Levi Brown','Arizona Cardinals',[])]:
            found=[r for r in regular if player in r['team_stats'].get(club,{}).get('players',{})]
            self.assertEqual(len(found),16, player)
        for club,rnd in [('Indianapolis Colts',1),('New England Patriots',5),
                         ('New York Giants',7),('Baltimore Ravens',4),('Baltimore Ravens',5)]:
            self.assertEqual(draft_order.require_clear_ownership(2014,rnd,club),club)

    def test_roster_and_palmer_conditions_use_branch_evidence(self):
        baseline=json.loads((draft_order.ROOT/'library/data/2013_week1_depth_charts.json').read_text())
        for club,player in [('Baltimore Ravens','A.Q. Shipley'),('New Orleans Saints','Parys Haralson')]:
            self.assertIn(player,[p['player_id'] for p in baseline['clubs'][club]['players']])
        palmer=next(p for p in baseline['clubs']['Arizona Cardinals']['players'] if p['player_id']=='Carson Palmer')
        self.assertEqual(palmer['slots'],'QB1')
        arizona=[r['team_stats']['Arizona Cardinals'] for r in draft_order._load(postseason.REGULAR_RECEIPTS) if 'Arizona Cardinals' in r['team_stats']]
        self.assertEqual(len(arizona),16)
        for team in arizona:
            self.assertEqual([p for p,s in team['players'].items() if s.get('pass_attempts',0)>0],['Carson Palmer'])

    def test_generated_order_is_current_and_shows_claims(self):
        from scripts.render_draft_order import render, OUT
        text=render()
        self.assertEqual(text,OUT.read_text())
        self.assertIn('eight', (draft_order.ROOT/'career/2014/draft/ownership_audit.md').read_text())
        self.assertNotIn(' †',text)
        self.assertIn('conditional hold',text)


if __name__ == "__main__":
    unittest.main()
