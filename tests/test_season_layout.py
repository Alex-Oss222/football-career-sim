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
        # Rebuild step 3b: the roster record is the owner; the page is built from it.
        self.assertEqual(paths.roster, ROOT/'data/2014/Team_Operations/Team/Roster/roster.json')
        self.assertEqual(paths.roster_page, ROOT/'career/2014/Team_Operations/Team/Roster/roster.md')
        self.assertEqual(SeasonPaths(2013, ROOT).roster, ROOT/'career/2013/roster.md')
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
        self.assertIn('Awarded after the week’s games',pages['README.md'])
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

    def test_in_season_records_follow_the_folder_map(self):
        # Rebuild step 5: the repository map names the in-season records and pages where the folder
        # map places them, so neither can drift from the other.
        from runtime import decisions, season_layout
        mapping=json.loads((ROOT/'docs/repository_map.json').read_text())
        records=mapping['in_season_records']
        year=mapping['active_season']
        paths=SeasonPaths(year,ROOT)
        rel=lambda p: Path(p).relative_to(ROOT).as_posix()
        owner=lambda name: decisions.Event('x','x','x',name,'x',5)
        self.assertEqual(set(records['event_stores']), set(records['result_folders']))
        for name, store in records['event_stores'].items():
            self.assertEqual(rel(decisions.event_store(owner(name),year,ROOT)), store)
            self.assertEqual(rel(decisions.event_folder(owner(name),year,ROOT)), records['result_folders'][name])
        kinds={e.owner for e in decisions.EVENTS+decisions.NEWS if e.step==5}
        self.assertEqual(kinds, set(records['event_stores']))
        self.assertEqual(rel(decisions.event_folder(owner('free_agency'),year,ROOT)), records['signing_records'])
        # The September 8 signing record is the precedent for the name.
        self.assertTrue(paths.signing_record('alan_ball','2014-09-08').is_file())
        self.assertEqual(rel(paths.signing_record('alan_ball','2014-09-08').parent), records['signing_records'])
        with self.assertRaises(ValueError): paths.signing_record('Alan Ball','2014-09-08')
        self.assertEqual(rel(paths.transactions), records['transactions'])
        self.assertEqual(rel(paths.league_dates), records['league_dates'])
        self.assertEqual(season_layout.PLAYER_CONTRACTS, records['player_contracts'])
        self.assertEqual([rel(paths.record(p)) for p in ('finances/player_contracts/Player_Contracts.md',
                                                        'finances/salary_cap/Salary_Cap.md')],
                         records['contract_pages'])
        # The new contract pages never collide with the old ones on a case-insensitive disk.
        for page in records['contract_pages']:
            folder=ROOT/Path(page).parent
            self.assertFalse(any(p.name.lower()==Path(page).name.lower() and p.name!=Path(page).name
                                 for p in folder.iterdir()), page)
        self.assertEqual(rel(paths.record('trades/trade_offers.md').parent), records['trade_call_pages'])
        self.assertEqual(rel(paths.coaching_changes), records['coaching_changes']['pages'])
        self.assertEqual(rel(paths.data_for(paths.coaching_changes)), records['coaching_changes']['data'])
        self.assertEqual(season_relative(year,'league/coaching_changes/README.md'),
                         'League/Coaching_Changes/README.md')
        week=decisions.week_pages(year,6,ROOT)
        self.assertEqual([week.responses.name], records['week_pages'])
        self.assertEqual([p.name for p in (week.practice_log,week.game_day_changes,week.responses_record)],
                         records['week_records'])
        self.assertEqual((week.practice_log,week.game_day_changes,week.responses_record),
                         (paths.practice_log(6),paths.game_day_changes(6),paths.responses_record(week.folder)))
        bye=records['bye_week']
        club='Jacksonville Jaguars'
        self.assertFalse([g for g in paths.regular_games() if g['week']==bye['week'] and club in (g['home'],g['away'])])
        pages=decisions.bye_pages(year,bye['week'],ROOT)
        self.assertEqual([rel(p) for p in (pages.readme,pages.review,pages.adjustments,pages.report,pages.responses)],
                         bye['pages'])
        self.assertEqual([rel(p) for p in (pages.briefings,pages.staff_review,pages.applied,pages.practice_log,
                                           pages.responses_record)], bye['data'])

    def test_result_file_names_and_reserved_headings(self):
        from tempfile import TemporaryDirectory
        from runtime import decisions
        with TemporaryDirectory() as directory:
            root=Path(directory)
            first=decisions.result_file('trade_talks','2014-10-21','Club A',root)
            self.assertEqual(first.relative_to(root).as_posix(),
                             'career/2014/Team_Operations/Trades/Trade_Result_2014-10-21_Club_A.md')
            first.parent.mkdir(parents=True)
            first.write_text('')
            self.assertEqual(decisions.result_file('trade_talks','2014-10-21','Club A',root).name,
                             'Trade_Result_2014-10-21_Club_A_2.md')
            self.assertEqual(decisions.result_file('injury_replacement','2014-10-14',"Ka'imi T.J. Smith",root).name,
                             'Transaction_2014-10-14_Kaimi_TJ_Smith.md')
            change=decisions.result_file('head_coach_change','2014-10-13','Club B',root)
            self.assertEqual(change.relative_to(root).as_posix(),
                             'career/2014/League/Coaching_Changes/Head_Coach_Change_2014-10-13_Club_B.md')
            # A January date names its season: the postseason before or the offseason after.
            with self.assertRaises(ValueError): decisions.result_file('trade_talks','2015-01-10','Club A',root)
            self.assertEqual(decisions.result_file('trade_talks','2015-01-10','Club A',root,season=2014).parent,
                             first.parent)
            with self.assertRaises(ValueError): decisions.result_file('trade_talks','2014-10-21','  ',root)
            with self.assertRaises(ValueError): decisions.result_file('no_such_kind','2014-10-21','Club A',root)
        self.assertEqual(decisions.RESERVED_HEADINGS, ('Depth and inactives change','Practice week'))
        self.assertEqual([decisions.game_day_change_heading(n) for n in (1,2,3)],
                         ['Depth and inactives change','Depth and inactives change 2','Depth and inactives change 3'])
        self.assertEqual([decisions.reserved_heading(h) for h in ('Practice week','Depth and inactives change 2',
                                                                  'Depth and inactives change 1','Trade call')],
                         ['Practice week','Depth and inactives change',None,None])

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
