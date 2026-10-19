"""Routing and presentation must preserve season identity and recorded outcomes."""
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

from runtime.season_layout import season_relative, rebase_markdown, repository_relative, readable_relative, opening_guides
from runtime.seasons import SeasonPaths
from scripts.render_award_pages import award_cards, render_pages
from scripts.render_trade_pages import render as trade_pages

ROOT=Path(__file__).resolve().parents[1]


class SeasonLayoutTests(unittest.TestCase):
    def test_new_years_route_records_without_changing_2013(self):
        for year in (2014,2015,2016):
            self.assertEqual(season_relative(year,'roster.md'),'Team_Operations/Team/Roster/roster.md')
            self.assertEqual(season_relative(year,'offseason/otas/plan.md'),
                             'Offseason_Training/OTAs/staff_plan.md')
            self.assertEqual(season_relative(year,'postseason/divisional/output.md'),
                             'Postseason/Games/divisional/output.md')
            actual=SeasonPaths(year,ROOT).receipts
            self.assertIn(f'data/{year}/Regular_Season/Statistics/records/game_receipts',str(actual))
        for readable in ('Team_Operations/Team/Roster/roster.md','Team_Operations/Trades/completed_trades/trades.md',
                         'Regular_Season/Games/Week_01/output.md','Offseason_Training/OTAs/staff_plan.md',
                         'Regular_Season/Statistics/records/game_receipts'):
            self.assertEqual(season_relative(2014,readable),readable)
        self.assertEqual(season_relative(2014,'trades/trades.md'),'Team_Operations/Trades/completed_trades/trades.md')
        self.assertEqual(season_relative(2013,'roster.md'),'roster.md')
        self.assertEqual(season_relative(2013,'postseason/divisional/output.md'),'postseason/divisional/output.md')
        for name in ('../../state.md','/tmp/roster.md'):
            with self.assertRaises(ValueError):season_relative(2014,name)

    def test_numbered_names_and_system_files_follow_rebuild_step_2b(self):
        # The numbered folder names stay readable aliases for frozen references.
        self.assertEqual(season_relative(2014,'05_Regular_Season/Games/Week_05/output.md'),
                         'Regular_Season/Games/Week_05/output.md')
        self.assertEqual(repository_relative('career/2014/00_Team_Operations/Team/Roster/roster.md'),
                         'career/2014/Team_Operations/Team/Roster/roster.md')
        # A system file resolves into the data area; a page or image stays in the season folder.
        self.assertEqual(repository_relative('career/2014/05_Regular_Season/Games/Week_05/call_sheet.json'),
                         'data/2014/Regular_Season/Games/Week_05/call_sheet.json')
        self.assertEqual(repository_relative('career/2014/offseason/league_rails/league_players.json'),
                         'data/2014/League/personnel/league_players.json')
        self.assertEqual(repository_relative('career/2014/draft/coin_flip_2026-09-29.jpg'),
                         'career/2014/Draft/coin_flip_2026-09-29.jpg')
        self.assertEqual(repository_relative('career/2013/stats/game_receipts/x.json'),
                         'career/2013/stats/game_receipts/x.json')
        paths = SeasonPaths(2014, ROOT)
        self.assertEqual(paths.depth_chart, ROOT/'data/2014/Team_Operations/Team/Depth_Chart/game_depth_chart.json')
        self.assertEqual(paths.roster, ROOT/'career/2014/Team_Operations/Team/Roster/roster.md')
        self.assertEqual(paths.call_sheet(5), ROOT/'data/2014/Regular_Season/Games/Week_05/call_sheet.json')
        self.assertEqual(paths.week_folder(5), ROOT/'career/2014/Regular_Season/Games/Week_05')
        self.assertEqual(paths.file_in(paths.stats, 'season_totals.json'),
                         ROOT/'data/2014/Regular_Season/Statistics/records/season_totals.json')
        self.assertEqual(paths.file_in(paths.stats, 'league_leaders.md'),
                         ROOT/'career/2014/Regular_Season/Statistics/records/league_leaders.md')
        self.assertEqual(paths.awards_data, ROOT/'data/2014/Regular_Season/Awards')
        old = SeasonPaths(2013, ROOT)
        self.assertEqual(old.data, old.career)
        self.assertEqual(old.depth_chart, ROOT/'career/2013/depth_chart.json')
        self.assertEqual(old.receipts, ROOT/'career/2013/stats/game_receipts')
        self.assertEqual(old.generations, ROOT/'career/2013/migrations/event_generations.json')
        # No system file is left in a season folder from 2014 on.
        self.assertEqual(sorted(p for p in (ROOT/'career/2014').rglob('*') if p.suffix in ('.json', '.csv', '.gz')), [])

    def test_moving_a_page_preserves_links_and_frozen_references(self):
        source='career/2014/offseason/otas/plan.md'
        target='career/2014/Offseason_Training/OTAs/staff_plan.md'
        text='[Report](output.md#handoff) [Cap](../../../finances/jaguars_cap.md)'
        self.assertEqual(rebase_markdown(text,source,target),
                         '[Report](training_report.md#handoff) [Cap](../../../finances/salary_cap/cap_tracker.md)')
        self.assertEqual(repository_relative('career/2014/draft/coin_flip_2026-09-29.jpg'),
                         'career/2014/Draft/coin_flip_2026-09-29.jpg')
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

    def test_unplayed_awards_have_one_index_without_placeholder_pages(self):
        pages=render_pages(2014,{})
        self.assertEqual(set(pages), {'README.md'})
        self.assertNotIn('results.json',pages)
        self.assertFalse(any(p.endswith('.svg') for p in pages))
        self.assertIn('Awaiting closed games and awards',pages['README.md'])
        self.assertNotIn('](week_01/README.md)',pages['README.md'])
        with self.assertRaises(ValueError):render_pages(2014,{'recorded':{}})

    def test_existing_layout_aliases_and_physical_directories(self):
        self.assertEqual(season_relative(2014, 'team/player_cards/cousins.md'),
                         'Team_Operations/Team/Player_Cards/cousins.md')
        self.assertEqual(readable_relative(2014, 'regular_season/README.md'),
                         'Regular_Season/README.md')
        self.assertEqual(repository_relative('career/2014/regular_season/README.md'),
                         'career/2014/Regular_Season/README.md')
        self.assertEqual(season_relative(2014, 'postseason/statistics/README.md'),
                         'Postseason/Statistics/README.md')
        self.assertEqual(repository_relative('career/2014/trades/targets_and_offers/README.md'),
                         'career/2014/Team_Operations/Trades/targets_and_offers/README.md')
        self.assertEqual(season_relative(2014, 'preseason/game_01/output.md'),
                         'Training_Camp_and_Preseason/Preseason_Games/Game_01/output.md')
        self.assertEqual(SeasonPaths(2015, ROOT).calendar.name, 'Calendar.md')
        self.assertEqual(set(opening_guides(2015)), {'README.md'})
        self.assertEqual(repository_relative('foundation/06_Chronology_Game_Ledger_and_Handoff.md'),
                         'foundation/06_Event_Records_and_Handoff.md')
        self.assertEqual(rebase_markdown('[Record](old.md)', 'docs/index.md', 'docs/index.md',
                                        aliases={'docs/old.md': 'docs/new.md'}),
                         '[Record](new.md)')
        self.assertEqual(repository_relative('career/2014/offseason_training/otas/player_assessments.md'),
                         'career/2014/Offseason_Training/OTAs/training_report.md')
        old = '[Handoff](offseason_training/phases_one_and_two/training_report.md#may-2-phase-one-handoff)'
        self.assertEqual(rebase_markdown(old, 'career/2014/README.md', 'career/2014/README.md'),
                         '[Handoff](Offseason_Training/Phase_One/training_report.md#may-2-phase-one-handoff)')

    def test_week_folder_uses_sortable_current_name(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            paths = SeasonPaths(2015, Path(directory))
            self.assertEqual(paths.week_folder(2).name, 'Week_02')
            dated = paths.regular_season/'Week_02_jacksonville_at_oakland'
            dated.mkdir(parents=True)
            self.assertEqual(paths.week_folder(2), dated)
            (paths.regular_season/'week_02').mkdir()
            with self.assertRaisesRegex(ValueError, 'Multiple output folders'):
                paths.week_folder(2)

    def test_completed_trade_views_keep_both_sides_and_accounting(self):
        pages=trade_pages(ROOT,2014)
        self.assertEqual(len(pages), 1)
        self.assertFalse(any('deals' in p.parts or p.suffix == '.svg' for p in pages))
        index=next(iter(pages.values()))
        self.assertEqual(sum(line.startswith('| ') and '](' in line for line in index.splitlines()), 7)
        rackley=SeasonPaths(2014,ROOT).record('trades/rackley_to_seattle_2014-05-12.md').read_text()
        self.assertIn('G Will Rackley',rackley)
        self.assertIn("Seattle's own 2015 seventh-round pick, unconditional",rackley)
        self.assertIn('$154,868',rackley)
        self.assertIn('$936,000',rackley)


if __name__=='__main__':unittest.main()
