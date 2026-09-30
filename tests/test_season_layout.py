"""Routing and presentation must preserve season identity and recorded outcomes."""
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

from runtime.season_layout import season_relative, rebase_markdown, repository_relative
from runtime.seasons import SeasonPaths
from scripts.render_award_pages import award_cards, render_pages
from scripts.render_trade_pages import render as trade_pages

ROOT=Path(__file__).resolve().parents[1]


class SeasonLayoutTests(unittest.TestCase):
    def test_new_years_route_records_without_changing_2013(self):
        for year in (2014,2015,2016):
            self.assertEqual(season_relative(year,'roster.md'),'00_team/roster/roster.md')
            self.assertEqual(season_relative(year,'offseason/otas/plan.md'),
                             '03_offseason_training/03_otas/staff_plan.md')
            self.assertEqual(season_relative(year,'postseason/divisional/output.md'),
                             '07_postseason/games/divisional/output.md')
            actual=SeasonPaths(year,ROOT).receipts
            self.assertIn(f'career/{year}/06_regular_season/statistics/records/game_receipts',str(actual))
        self.assertEqual(season_relative(2013,'roster.md'),'roster.md')
        self.assertEqual(season_relative(2013,'postseason/divisional/output.md'),'postseason/divisional/output.md')
        for name in ('../../state.md','/tmp/roster.md'):
            with self.assertRaises(ValueError):season_relative(2014,name)

    def test_moving_a_page_preserves_links_and_frozen_references(self):
        source='career/2014/offseason/otas/plan.md'
        target='career/2014/03_offseason_training/03_otas/staff_plan.md'
        text='[Report](output.md#handoff) [Cap](../../../finances/jaguars_cap.md)'
        self.assertEqual(rebase_markdown(text,source,target),
                         '[Report](training_report.md#handoff) [Cap](../../../finances/01_salary_cap/cap_tracker.md)')
        self.assertEqual(repository_relative('career/2014/draft/coin_flip_2026-09-29.jpg'),
                         'career/2014/04_draft/coin_flip_2026-09-29.jpg')
        legacy='[Receipts](../stats/game_receipts/)'
        self.assertEqual(rebase_markdown(legacy,'career/2013/player_profiles/card.md',
                                        'career/2013/player_profiles/card.md'),legacy)

    def test_award_winner_is_centered_even_when_not_top_scored(self):
        rows=[{'player':'First & One','team':'A','score':30},
              {'player':'Second','team':'B','score':25},
              {'player':'Recorded Winner','team':'C','score':20}]
        svg=award_cards('Weekly award',rows,2)
        tree=ET.fromstring(svg)
        texts={e.text:e.attrib for e in tree.iter() if e.tag.endswith('text')}
        self.assertEqual(texts['Recorded Winner']['x'],'480')
        self.assertEqual(texts['First & One']['x'],'165')
        self.assertEqual(texts['Second']['x'],'795')
        borders=[e for e in tree.iter() if e.attrib.get('stroke-width')=='4']
        self.assertEqual([e.attrib['x'] for e in borders],['331'])
        self.assertNotIn('2nd',svg)
        self.assertNotIn('votes',svg)

    def test_unplayed_awards_create_navigation_without_candidates_or_results(self):
        pages=render_pages(2014,{})
        self.assertEqual(len([p for p in pages if p.startswith('week_')]),17)
        self.assertNotIn('results.json',pages)
        self.assertFalse(any(p.endswith('.svg') for p in pages))
        self.assertIn('Not awarded yet',pages['week_01/README.md'])
        with self.assertRaises(ValueError):render_pages(2014,{'recorded':{}})

    def test_completed_trade_views_keep_both_sides_and_accounting(self):
        pages=trade_pages(ROOT,2014)
        rackley=next(text for p,text in pages.items() if 'deals/seattle_rackley' in str(p) and p.name=='README.md')
        self.assertIn('G Will Rackley',rackley)
        self.assertIn("Seattle's original 2015 seventh-round pick, unconditional",rackley)
        self.assertIn('$154,868',rackley)
        self.assertIn('$936,000',rackley)
        self.assertEqual(sum(p.name=='exchange.svg' for p in pages),7)


if __name__=='__main__':unittest.main()
