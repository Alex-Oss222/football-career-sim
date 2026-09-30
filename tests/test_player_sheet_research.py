import csv
import json
import statistics
import tempfile
import unittest
from pathlib import Path

from scripts.build_annual_player_sheets import POSITION_SHEET_TRAITS, load_season_players, target_path
from scripts.research.build_2013_player_sheet_benchmarks import build, reference, STAT_FIELDS
from scripts.research.complete_2013_player_sheets import (
    ROOT, DATA, REVIEW_SOURCE, branch_tables, postseason_tables, counterpart,
    pool_rows, render, branch_metric,
)


class PlayerSheetResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.players = load_season_players(2013)
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))
        cls.findings = json.loads(REVIEW_SOURCE.read_text(encoding='utf-8'))['players']
        cls.regular = branch_tables()
        cls.playoffs = postseason_tables()

    def player(self, name):
        return next(p for p in self.players if p.player == name)

    def test_all_remaining_reviews_have_frozen_sources_and_valid_traits(self):
        self.assertEqual(set(self.findings), {p.player for p in self.players if p.player != 'Kirk Cousins'})
        for p in self.players:
            if p.player == 'Kirk Cousins':
                continue
            finding = self.findings[p.player]
            self.assertEqual(finding['source'], p.evidence)
            self.assertTrue(set(finding['trait_findings']) <= set(POSITION_SHEET_TRAITS[p.pos]))
            self.assertEqual(finding['established'], p.identity)
            self.assertTrue(finding['strengths'] and finding['limitations'] and finding['unassessed_reason'])

    def test_reviewed_cards_reproduce_without_filling_grades_from_production(self):
        for p in self.players:
            if p.player == 'Kirk Cousins':
                continue
            text = target_path(2013, p.player).read_text(encoding='utf-8')
            self.assertEqual(text, render(p, self.findings[p.player], self.data, self.regular, self.playoffs))
            self.assertNotIn('Pending historical benchmark', text)
            self.assertIn('Evidence and historical-context review completed', text)
            grades = text.split('## Position grades')[1].split('## Historical NFL benchmark')[0]
            self.assertEqual(grades.count('— /10'), 1 + len(POSITION_SHEET_TRAITS[p.pos]))

    def test_qualified_means_and_tied_extremes_recompute(self):
        for pos, refs in self.data['references'].items():
            for metric, ref in refs.items():
                if not ref:
                    continue
                qualified = [r for r in self.data['records'] if r['position'] == pos
                             and r.get(metric) is not None
                             and (r.get(ref['opportunity']) or 0) >= ref['minimum']]
                self.assertEqual(len(qualified), ref['n'])
                self.assertAlmostEqual(statistics.mean(r[metric] for r in qualified), ref['average'], places=3)
                self.assertEqual({r['player'] for r in qualified if r[metric] == max(x[metric] for x in qualified)},
                                 {r['player'] for r in ref['top']})
                self.assertEqual({r['player'] for r in qualified if r[metric] == min(x[metric] for x in qualified)},
                                 {r['player'] for r in ref['low']})

    def test_qb_references_match_2013_qualified_leaders(self):
        ref = self.data['references']['QB']['passer_rating']
        self.assertEqual(ref['minimum'], 224)
        self.assertEqual(ref['top'][0]['player'], 'Nick Foles')
        self.assertAlmostEqual(ref['top'][0]['value'], 119.2, places=1)
        self.assertEqual(ref['low'][0]['player'], 'Geno Smith')

    def test_small_branch_sample_does_not_claim_peer_standing(self):
        p = self.player('C.J. Anderson')
        rows = '\n'.join(pool_rows(p, self.regular['Running backs'][p.player], self.data))
        self.assertIn('below 100-opportunity threshold', rows)
        self.assertNotIn('branch above', rows)
        self.assertNotIn('branch below this production mean', rows)

    def test_missing_defensive_snaps_does_not_claim_qualification(self):
        p = self.player("Sen'Derrick Marks")
        rows = '\n'.join(pool_rows(p, self.regular['Defensive line'][p.player], self.data))
        self.assertIn('qualification unknown', rows)
        self.assertNotIn('branch above', rows)

    def test_same_name_and_alias_counterparts_are_resolved(self):
        self.assertEqual(counterpart(self.player('C.J. Wilson'), self.data)['position'], 'DE')
        self.assertEqual(counterpart(self.player('Mike Brewster'), self.data)['player'], 'Michael Brewster')
        self.assertIsNone(counterpart(self.player('Brandon King'), self.data))

    def test_playoff_counts_are_separate_and_receipt_derived(self):
        regular = self.regular['Running backs']['Maurice Jones-Drew']
        playoffs = self.playoffs['Running backs']['Maurice Jones-Drew']
        self.assertEqual((regular['CAR'], regular['YDS']), ('282', '1334'))
        self.assertEqual((playoffs['CAR'], playoffs['YDS']), ('35', '186'))
        self.assertEqual(self.playoffs['Kickers']['Josh Scobee']['FGM'], '3')
        self.assertEqual(self.playoffs['Wide receivers']['Adam Thielen']['LOST'], '1')

    def test_zero_denominator_and_missing_counter_are_not_zero_rates(self):
        self.assertIsNone(branch_metric({'REC': '0', 'TGT': '0'}, 'catch_pct', None))
        self.assertIsNone(branch_metric({}, 'passer_rating', 'RTG'))
        self.assertIsNone(reference([{'player': 'No snaps', 'metric': 10, 'snaps': None}], 'metric', 'snaps', 300))

    def test_future_and_playoff_inputs_cannot_enter_historical_pools(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            def write(name, rows):
                fields = list(dict.fromkeys(key for row in rows for key in row))
                with (directory/name).open('w', encoding='utf-8', newline='') as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)
            base = {**{key: 0 for key in STAT_FIELDS}, 'season': '2013', 'season_type': 'REG',
                    'position': 'QB', 'player_display_name': 'Test QB', 'player_id': 'test-id',
                    'recent_team': 'JAX', 'attempts': 224, 'completions': 112, 'passing_yards': 1568}
            write('stats_player_reg_2013.csv', [base, {**base, 'season': '2014'}, {**base, 'season_type': 'POST'}])
            write('roster_2013.csv', [{'season': '2013', 'gsis_id': 'test-id', 'full_name': 'Test QB', 'birth_date': '1990-01-01', 'position': 'QB'}])
            snap = {'season': '2013', 'game_type': 'REG', 'player': 'Test QB', 'position': 'QB', 'offense_snaps': 300, 'defense_snaps': 0}
            write('snap_counts_2013.csv', [snap, {**snap, 'game_type': 'POST'}, {**snap, 'season': '2014'}])
            workout = {'season': '2012', 'player_name': 'Test QB', 'pos': 'QB', 'forty': '4.8'}
            write('combine.csv', [workout, {**workout, 'season': '2014'}, {**workout, 'player_name': 'Not rostered'}])
            data = build(directory)
            self.assertEqual(len(data['records']), 1)
            self.assertEqual(data['records'][0]['offense_snaps'], 300)
            self.assertEqual(len(data['workouts']), 1)
            self.assertEqual(data['workouts'][0]['test_year'], 2012)

    def test_restored_future_template_preserves_overall_and_stats_at_bottom(self):
        text = (ROOT/'foundation/templates/player_sheet_2014_onward_template.md').read_text(encoding='utf-8')
        self.assertIn('| Overall |', text)
        self.assertIn('| Trait | vs. Average | vs. Best | vs. Worst |', text)
        headings = [line for line in text.splitlines() if line.startswith('## ')]
        self.assertEqual(headings[-2:], ['## Regular-season statistics by year', '## Playoff statistics by year'])
        self.assertEqual(text.count('| 2014 | Not played | Not played |'), 2)
        self.assertIn('2015, 2016, and onward', text)


if __name__ == '__main__':
    unittest.main()
