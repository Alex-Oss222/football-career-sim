#!/usr/bin/env python3
"""Build the 2014 preseason opponent library: each opponent's 90-man camp
roster as it stood for its preseason game against Jacksonville, reconciled to
branch control. Game 1: Tampa Bay, August 8, 2014 (at Jacksonville). Game 2:
Chicago, August 14, 2014 (Jacksonville at Chicago).

Research tool only; the runtime never downloads anything. The real charts and
rosters are not available as a machine feed (nflverse carries no preseason
depth charts, weekly rosters or injury reports for 2014, and the season
roster file lists only players who reached a regular-season roster), so each
club's first unofficial depth chart and its July-to-game transaction log are
transcribed below from the dated public sources named in
library/2014_preseason_opponent_rosters.md. The identity files supply gsis
ids, birth dates, jersey numbers and photographs:

  library/data/player_birth_dates.json            (identity registry)
  library/data/2014_week1_depth_charts.json       (Week 1 library: bio fields)
  library/data/player_photos.json                 (open-licensed photographs)
  SOURCE_DIR/players.csv                          (nflverse players, optional)
  SOURCE_DIR/roster_2014.csv                      (nflverse 2014 season rosters, optional:
                                                   jersey numbers of players who reached
                                                   a regular-season roster)

Usage:
  python scripts/research/build_2014_preseason_opponent_rosters.py [SOURCE_DIR] \
      > library/data/2014_preseason_opponent_rosters.json

Read only: each club's first chart, its transactions through game day, its
dated pre-game availability reports, branch control from the 2014 roster and
the branch draft/undrafted pairing. No preseason score, statistic, game
participation or later transaction is an input. The same conventions as the
Week 1 builder (scripts/research/build_2014_week1_depth_charts.py) apply:
depth within a kernel group by chart string, then line slot, then chart
column, then jersey, then name; a Jacksonville-controlled player is removed
and the next man up takes his slot; a player the branch pairing places with
the club is added below every listed player of his group.

The library holds every club under `clubs`, keyed by club name, each with its
own `game`, `as_of`, `gate`, transaction log, `sources` and `cross_check`.
"""
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.usage import MINIMUM_GAME_DAY, group  # noqa: E402
from scripts.research.build_2014_week1_depth_charts import (  # noqa: E402
    BIO_FIELDS, OL_SLOT_ORDER, SIDE, BIRTH_DATES, ROSTER_MD,
    branch_control, compact, identity, jersey_key, norm,
)

SEASON = 2014
WEEK1_LIBRARY = ROOT / "library/data/2014_week1_depth_charts.json"
PHOTOS = ROOT / "library/data/player_photos.json"
PFR = "https://www.pro-football-reference.com/players/"
BRANCH_BASIS = "career/2014/team/roster/roster.md, August 1, 2014 (78 Jacksonville-controlled players: 74 under contract and four unsigned tenders)"

# ---------------------------------------------------------------------------
# Game 1: Tampa Bay Buccaneers, August 8, 2014, at Jacksonville.
#
# The club's first 2014 unofficial depth chart, released August 5, 2014
# (buccaneers.com "Depth Chart Reflects Ongoing Competition"; SI.com
# August 6 and Bucs Nation August 5 transcriptions; Bleacher Report "2014
# Virtual Program"). Each column is (formation, chart label, kernel-group
# position of the column, [players in listed order]). "Other" entries follow
# the ranked ones. Players under contract on August 8 who do not appear on any
# available transcription are listed under `unlisted` and placed below every
# listed player of their group. Jeremy Grable (SLB4) and Mycal Swaim were on
# the chart but waived/injured August 4, so they are not roster members.
# ---------------------------------------------------------------------------
TAMPA_BAY = {
    "team": "Tampa Bay Buccaneers",
    "code": "TB",
    "game": "preseason-01",
    "as_of": "2014-08-08",
    "gate": "gated: usable for the August 8, 2014 preseason game and after. The chart was public August 5, 2014 and the pregame report August 8, 2014; no preseason score, statistic, participation or later transaction is an input.",
    "chart": [
        ("Offense", "QB", "QB", ["Josh McCown", "Mike Glennon", "Mike Kafka", "Alex Tanney"]),
        ("Offense", "RB", "RB", ["Doug Martin", "Bobby Rainey", "Charles Sims", "Mike James", "Jeff Demps"]),
        ("Offense", "FB", "FB", ["Jorvorskie Lane", "Lonnie Pryor", "Ian Thompson"]),
        ("Offense", "WR", "WR", ["Vincent Jackson", "Louis Murphy", "Tommy Streeter", "Robert Herron", "Skye Dawson", "Solomon Patton"]),
        ("Offense", "WR", "WR", ["Chris Owusu", "Mike Evans", "Eric Page", "Lavelle Hawkins", "Russell Shepard"]),
        ("Offense", "TE", "TE", ["Brandon Myers", "Timothy Wright", "Luke Stocker", "Austin Seferian-Jenkins", "Cameron Brate"]),
        ("Offense", "LT", "T", ["Anthony Collins", "Kevin Pamphile", "J.B. Shugarts"]),
        ("Offense", "LG", "G", ["Oniel Cousins", "Kadeem Edwards", "Josh Allen"]),
        ("Offense", "C", "C", ["Evan Dietrich-Smith", "Jace Daniels", "Jason Foster", "Josh Allen", "Andrew Miller"]),
        ("Offense", "RG", "G", ["Jamon Meredith", "Patrick Omameh", "Andrew Miller"]),
        ("Offense", "RT", "T", ["Demar Dotson", "Matt Patchan"]),
        ("Defense", "LDE", "DE", ["Adrian Clayborn", "William Gholston", "Chaz Sutton"]),
        ("Defense", "DT", "DT", ["Gerald McCoy", "Da'Quan Bowers", "Ronald Talley", "Euclid Cummings"]),
        ("Defense", "DT", "DT", ["Clinton McDonald", "Akeem Spence", "Matthew Masifilo", "Jibreel Black"]),
        ("Defense", "RDE", "DE", ["Michael Johnson", "Steven Means", "Scott Solomon"]),
        ("Defense", "SLB", "OLB", ["Jonathan Casillas", "Ka'Lial Glaud", "Nate Askew"]),
        ("Defense", "MLB", "MLB", ["Mason Foster", "Dane Fletcher", "Damaso Munoz"]),
        ("Defense", "WLB", "OLB", ["Lavonte David", "Danny Lansanah", "Brandon Magee"]),
        ("Defense", "LCB", "CB", ["Alterraun Verner", "Rashaan Melvin"]),
        ("Defense", "RCB", "CB", ["Mike Jenkins", "Johnthan Banks", "Deveron Carr", "Keith Lewis", "Anthony Gaitor"]),
        ("Defense", "NB", "CB", ["Leonard Johnson", "Quinton Pointer"]),
        ("Defense", "SS", "SS", ["Mark Barron", "Major Wright", "Bradley McDougald"]),
        ("Defense", "FS", "FS", ["Dashon Goldson", "Keith Tandy", "Kelcie McCray"]),
        ("Special Teams", "PK", "K", ["Connor Barth", "Patrick Murray"]),
        ("Special Teams", "P", "P", ["Michael Koenen"]),
        ("Special Teams", "LS", "LS", ["Andrew DePaola", "Jeremy Cain"]),
        ("Special Teams", "KR", None, ["Eric Page", "Jeff Demps", "Mike James"]),
        ("Special Teams", "PR", None, ["Eric Page", "Bobby Rainey", "Robert Herron", "Skye Dawson"]),
    ],
    # Under contract on August 8, 2014 but on no available transcription of
    # the August 5 chart: name -> (position, basis).
    "unlisted": {
        "Ryne Giddins": ("DE", "signed August 4, 2014, after the chart was prepared"),
        "James Ruffin": ("DE", "signed August 4, 2014, after the chart was prepared"),
        "Kip Edwards": ("CB", "signed July 29, 2014; his chart cell was not located in any available transcription"),
        "Danny Gorrer": ("CB", "re-signed March 13, 2014; his chart cell was not located in any available transcription (injured in camp; placed on injured reserve August 25)"),
        "Mark Joyce": ("S", "signed August 3, 2014, after the chart was prepared; waived August 9"),
    },
    # Rank at which "Other" entries start in a chart column (after the third string).
    "other_from": {"WR": 7, "DT": 4, "RCB": 4},
    # Held out of the August 8 game under a pre-game report dated by August 8
    # (buccaneers.com "Jacksonville Pregame Report", August 8, 2014; "Camp
    # Notes: Verner Easing Back In"; Bucs Nation August 3 and 6 camp notes).
    "held_out": {
        "Alterraun Verner": "hamstring; will not play (pregame report, August 8)",
        "Mike Jenkins": "lower-leg (hamstring) injury; will not play (pregame report, August 8)",
        "Dashon Goldson": "held out as planned after offseason foot surgery (pregame report, August 8)",
    },
    # Transactions July 21 to August 9, 2014 (ESPN and Pro Football Reference
    # transaction logs; buccaneers.com and Bucs Nation dated notices). Recorded
    # for the reconciliation list; the roster above already reflects them.
    "transactions_key": "transactions_july_21_to_august_9",
    "transactions": [
        ("2014-07-21", "Signed LB Jeremy Grable (undrafted) and OT J.B. Shugarts"),
        ("2014-07-23", "Claimed LB Brandon Magee off waivers from Cleveland; placed DE Ronald Talley on the active/non-football injury list (activated by August 3)"),
        ("2014-07-27", "Re-signed CB Anthony Gaitor; signed DT Jibreel Black (undrafted); waived WR Quintin Payton and RB Brendan Bigelow"),
        ("2014-07-29", "Signed CB Kip Edwards (ESPN also lists July 31; ProFootballTalk's July 30 notice says the signing was announced with Nicks's release)"),
        ("2014-07-30", "Released G Carl Nicks (mutual parting announced July 25; ESPN lists July 29)"),
        ("2014-08-03", "Signed S Mark Joyce; released WR David Gettis with an injury settlement"),
        ("2014-08-04", "Signed DE Ryne Giddins and DE James Ruffin; waived/injured LB Jeremy Grable and S Mycal Swaim"),
        ("2014-08-09", "Waived S Mark Joyce (after the game; ESPN lists August 12). Not applied: he is a roster member on August 8"),
    ],
    # Names the registry or nflverse spell differently from the chart.
    "aliases": {"Evan Dietrich-Smith": "Evan Smith", "Timothy Wright": "Tim Wright"},
    "identities": {},
    "ids": {},
    "no_jersey": set(),
    "notes": [
        "Next man up after the removals: Rashaan Melvin at LCB (Verner), Andrew DePaola the only long snapper (Cain); Brate's removal leaves four tight ends",
        "Chart cells not located for Kip Edwards, Danny Gorrer and Mark Joyce; the long-snapper order and the WR column assignments are single-source transcriptions. Jersey numbers are stored only for players who reached a 2014 regular-season roster (Week 1 library or nflverse roster_2014); the camp-only players carry none, so their ties break by name.",
        # The chart's long-snapper order was not located; DePaola is listed
        # first only because Cain is removed by branch control.
        "Long snapper: the chart order between DePaola and Cain was not located; Cain is removed by branch control, so the order has no effect",
    ],
    "sources": {
        "depth_chart": "Tampa Bay's first 2014 unofficial depth chart, released August 5, 2014: buccaneers.com 'Depth Chart Reflects Ongoing Competition' (August 5), si.com 'Tampa Bay Buccaneers release depth chart: Mike Evans behind Chris Owusu' (August 6), bucsnation.com 'Buccaneers Depth Chart: Observations and Reaction' (August 5), bleacherreport.com 'Buccaneers 2014 Virtual Program' (August 2014); transcribed from search-engine extracts because the pages themselves were not reachable from this session (see the record's limits)",
        "roster_membership": "the chart's listed players plus the dated transaction log (ESPN and Pro Football Reference 2014 transaction pages; buccaneers.com and bucsnation.com notices), with later arrivals (Larry English August 13, Rishaw Johnson August 21, Marc Anthony and Jeremiah Warren August 25, Logan Mankins August 26, Garrett Gilkey August 31, Brandon Dixon September 6) excluded by their dates",
        "availability": "buccaneers.com 'Jacksonville Pregame Report' (August 8, 2014) and 'Camp Notes: Verner Easing Back In'; bucsnation.com camp notes of August 3 and 6, 2014. Only players reported as not playing are unavailable; practice absences alone do not make a player unavailable",
        "co_listed_order": "chart string, then line slot LT-LG-C-RG-RT, then chart column, then jersey number, then name (the Week 1 rule); unlisted players rank below every listed player of their group",
        "identity": "library/data/player_birth_dates.json, then nflverse players.csv (single 2014-active match by name); jersey from the Week 1 library or nflverse roster_2014.csv; photographs from library/data/player_photos.json; page_url from the Week 1 library or the nflverse pfr id",
        "branch_control": "career/2014/team/roster/roster.md matched by gsis id through the identity registry and the league database, as in the Week 1 build",
        "draft_and_undrafted_pairing": "career/2014/league/personnel/draft_pairing.md and career/2014/draft/udfa_signings.md",
        "trades_and_free_agency": "career/2014/trades/completed_trades/trades.md, career/2014/free_agency/signings.md, career/2014/league/personnel/fa_draws.md",
        "retirements": "career/2014/league/personnel/retirements.md (none affecting Tampa Bay by August 8, 2014)",
    },
    # The identity basis as counted on the research date (October 1, 2026,
    # before the 42 Tampa Bay registry additions landed). Frozen so the club's
    # stored record stays as published; a rebuild today would count every
    # identified player from the registry.
    "cross_check_frozen": {"gsis_nflverse_players": 41, "gsis_none": 5, "gsis_registry": 41,
                           "jersey_nflverse_2014": 54, "jersey_unknown": 33},
}

# ---------------------------------------------------------------------------
# Game 2: Chicago Bears, August 14, 2014, Jacksonville at Chicago.
#
# The club's first 2014 unofficial depth chart, released Sunday, August 3, 2014
# (Windy City Gridiron "Chicago Bears First 2014 Training Camp Depth Chart
# Released", August 3; SI.com "Chicago Bears release depth chart: Jordan
# Palmer backup to Jay Cutler", August 5; CBS Chicago "View: Bears' Initial
# Depth Chart"). Co-listed cells ("D.J. Williams/Jon Bostic", "Pat
# O'Donnell/Tress Way", "Brandon Hartson/Chad Rempel") are ranked in listed
# order. Conor O'Neill (WLB4) was on the chart but waived August 4, and Graham
# Pocic (RG4) was waived August 10, so neither is a roster member on August
# 14; Rob Turner (signed August 10), Greg Herd (signed August 5) and Chris
# Smith (branch pairing) are `unlisted`.
# ---------------------------------------------------------------------------
CHICAGO = {
    "team": "Chicago Bears",
    "code": "CHI",
    "game": "preseason-02",
    "as_of": "2014-08-14",
    "gate": "gated: usable for the August 14, 2014 preseason game and after. The chart was public August 3, 2014 and the club's game-day list of players not suiting up was published August 14, 2014; no preseason score, statistic, participation or later transaction is an input.",
    "chart": [
        ("Offense", "QB", "QB", ["Jay Cutler", "Jordan Palmer", "Jimmy Clausen", "David Fales"]),
        ("Offense", "RB", "RB", ["Matt Forte", "Shaun Draughn", "Michael Ford", "Ka'Deem Carey", "Senorise Perry", "Jordan Lynch"]),
        ("Offense", "FB", "FB", ["Tony Fiammetta"]),
        ("Offense", "WR", "WR", ["Brandon Marshall", "Marquess Wilson", "Josh Bellamy", "Chris Williams", "Armanti Edwards"]),
        ("Offense", "WR", "WR", ["Alshon Jeffery", "Eric Weems", "Josh Morgan", "Micheal Spurlock", "Dale Moss"]),
        ("Offense", "TE", "TE", ["Martellus Bennett", "Dante Rosario", "Zach Miller", "Matthew Mulligan", "Jeron Mastrud"]),
        ("Offense", "LT", "T", ["Jermon Bushrod", "Charles Leno Jr.", "Dennis Roland"]),
        ("Offense", "LG", "G", ["Matt Slauson", "James Brown", "Ryan Groy"]),
        ("Offense", "C", "C", ["Roberto Garza", "Brian de la Puente", "Taylor Boggs"]),
        ("Offense", "RG", "G", ["Kyle Long", "Michael Ola", "Dylan Gandy", "Graham Pocic"]),
        ("Offense", "RT", "T", ["Jordan Mills", "Eben Britton", "Joe Long"]),
        ("Defense", "LDE", "DE", ["Lamarr Houston", "Willie Young", "Austen Lane", "David Bass"]),
        ("Defense", "DT", "DT", ["Jeremiah Ratliff", "Will Sutton", "Nate Collins", "Brandon Dunn"]),
        ("Defense", "NT", "DT", ["Stephen Paea", "Ego Ferguson", "Tracy Robertson", "Lee Pegues"]),
        ("Defense", "RDE", "DE", ["Jared Allen", "Trevor Scott", "Cornelius Washington"]),
        ("Defense", "SLB", "OLB", ["Shea McClellin", "Christian Jones", "Jordan Senn"]),
        ("Defense", "MLB", "MLB", ["D.J. Williams", "Jon Bostic", "DeDe Lattimore"]),
        ("Defense", "WLB", "OLB", ["Lance Briggs", "Khaseem Greene", "Jerry Franklin", "Conor O'Neill"]),
        ("Defense", "LCB", "CB", ["Tim Jennings", "Kyle Fuller", "Sherrick McManis", "C.J. Wilson", "Demontre Hurst"]),
        ("Defense", "RCB", "CB", ["Charles Tillman", "Kelvin Hayden", "Isaiah Frey", "Al Louis-Jean", "Derricus Purdy"]),
        ("Defense", "SS", "SS", ["Ryan Mundy", "Danny McCray", "Adrian Wilson", "Marcus Trice"]),
        ("Defense", "FS", "FS", ["Brock Vereen", "M.D. Jennings", "Chris Conte", "Craig Steltz"]),
        ("Special Teams", "K", "K", ["Robbie Gould"]),
        ("Special Teams", "P", "P", ["Pat O'Donnell", "Tress Way"]),
        ("Special Teams", "LS", "LS", ["Brandon Hartson", "Chad Rempel"]),
        ("Special Teams", "KR", None, ["Eric Weems", "Michael Ford", "Chris Williams", "Micheal Spurlock", "Armanti Edwards"]),
        ("Special Teams", "PR", None, ["Eric Weems", "Chris Williams", "Micheal Spurlock", "Armanti Edwards"]),
    ],
    # On the chart but not under contract on August 14, 2014: name -> reason.
    "departed": {
        "Conor O'Neill": "waived August 4, 2014 (club transaction log; the club's August 5 article on the Herd signing)",
        "Graham Pocic": "waived August 10, 2014 (ESPN; the club's log lists August 9 and 10)",
    },
    # Under contract on August 14, 2014 but on no available transcription of
    # the August 3 chart, or placed by the branch: name -> (position, basis).
    "unlisted": {
        "Greg Herd": ("WR", "signed August 5, 2014, after the chart was released (the club's August 5 article; its transaction log lists August 4)"),
        "Rob Turner": ("C", "signed August 10, 2014, after the chart was released (ESPN; the club's log lists August 9)"),
        "Chris Smith": ("DE", "branch draft pairing: the real Jaguars' seventh selection (pick 159) goes to Chicago, the club that really drafted Jacksonville's Charles Leno Jr.; he never held a cell on Chicago's real chart, and his real Week 1 slot applies when the Week 1 rails are built"),
    },
    "other_from": {},
    # Not suiting up for the August 14 game under reports dated by August 14
    # (CBS Sports, 'Bears list inactives for Week 2 of preseason', August 14,
    # 2014, the club's list of ten; ESPN Chicago Bears blog, 'Bears hold out
    # six from practice', August 12, 2014; Bleacher Report, 'Chicago vs.
    # Jacksonville: Bears Preseason Week 2 Game Preview'; chicagobears.com,
    # 'Special teams a top priority for Bears', August 11, 2014).
    "held_out": {
        "Marquess Wilson": "fractured clavicle, August 4; will not suit up (club list, August 14)",
        "Craig Steltz": "groin; off the active/PUP list by August 10 but will not suit up (club list, August 14)",
        "Isaiah Frey": "hamstring, carted off August 12; will not suit up (club list, August 14)",
        "Chris Conte": "shoulder; off the active/PUP list by August 10 but will not suit up (club list, August 14)",
        "Eben Britton": "hamstring; will not suit up (club list, August 14)",
        "Brian de la Puente": "did not practice August 10 to 12; will not suit up (club list, August 14)",
        "Jordan Mills": "foot, injured in the August 5 practice; will not suit up (club list, August 14)",
        "Chris Williams": "hamstring, injured in the August 8 opener; will not suit up (club list, August 14)",
        "Dante Rosario": "calf; will not suit up (club list, August 14)",
        "Willie Young": "bruised knee; will not suit up (club list, August 14)",
    },
    # Transactions July 25 to August 18, 2014 (ESPN transaction log and the
    # club's own transaction page, both read directly; club articles). Recorded
    # for the reconciliation list; the roster above already reflects them.
    "transactions_key": "transactions_july_25_to_august_18",
    "transactions": [
        ("2014-07-25", "Signed G/C Dylan Gandy; waived DE Jamil Merrell (the club's log lists July 24)"),
        ("2014-07-27", "Waived G James Dunbar (the club's log lists July 26)"),
        ("2014-07-29", "Signed WR Dale Moss (the club's log lists July 28)"),
        ("2014-07-31", "Signed OL Graham Pocic and T Dennis Roland; released WR Terrence Toliver with an injury settlement; waived T Cody Booth (the club's log lists July 30)"),
        ("2014-08-04", "Waived LB Conor O'Neill (club log and the club's August 5 article; ESPN's log omits the move)"),
        ("2014-08-05", "Signed WR Greg Herd, one day after Marquess Wilson fractured his clavicle (the club's article of Tuesday, August 5; its log lists August 4). Suspended TE Martellus Bennett indefinitely for the August 4 practice altercation (ESPN; the club's article of August 5)"),
        ("2014-08-10", "Reinstated TE Martellus Bennett, who rejoined the club Sunday, August 10 (ESPN; one transaction summary dates it August 11). Signed C/G Rob Turner; waived G Graham Pocic (ESPN; the club's log lists August 9 and 10). S Chris Conte and S Craig Steltz, on the active/PUP list from the start of camp, practiced August 10"),
        ("2014-08-15", "Placed TE Zach Miller on injured reserve; signed WR Kofi Hughes (ESPN and the club's August 15 article; the club's log also lists August 14). After the game: not applied, both are outside the August 14 roster"),
        ("2014-08-16", "Terminated the contract of WR Eric Weems; signed WR Santonio Holmes. After the game: not applied; Weems is a roster member on August 14"),
        ("2014-08-18", "Signed KR/PR Darius Reynaud and CB Peyton Thompson; waived LS Chad Rempel and P Tress Way. After the game: not applied; Rempel and Way are roster members on August 14"),
    ],
    # Names the registry or nflverse spell differently from the chart.
    "aliases": {"Jeremiah Ratliff": "Jay Ratliff", "Rob Turner": "Robert Turner"},
    # Reviewed identities for names the registry or nflverse share with a
    # namesake: the 2009 receiver, not the 2008 guard; the 2013 cornerback,
    # not the 2010 end; the 2009 tight end (Nebraska-Omaha), not Seattle's;
    # the 2007 center (New Mexico), whose nflverse namesake has no gsis id.
    "identities": {"Chris Williams": "00-0026691", "C.J. Wilson": "00-0030141", "Zach Miller": "00-0027125",
                   "Rob Turner": "00-0025761"},
    # Player ids for the namesakes, matching the identity registry's keys.
    "ids": {"Chris Williams": "Chris Williams (CHI)", "C.J. Wilson": "C.J. Wilson (CHI)", "Zach Miller": "Zach Miller (CHI)"},
    # A pairing-placed player's Week 1 library number is his real club's,
    # not a Chicago camp number.
    "no_jersey": {"Chris Smith"},
    "notes": [
        "Next man up after the removals: Dennis Roland at LT2 (Leno), Jordan Senn at SLB2 (Christian Jones)",
        "Chris Smith enters below every listed defensive lineman under the branch pairing; he held no cell on Chicago's real chart",
        "The third and fourth defensive-end strings differ between transcriptions: SI's table has LDE Houston, Young, Lane, Bass and RDE Allen, Scott, Washington; the Windy City Gridiron extract has Washington third at LDE and Bass third at RDE. SI's table is used; the difference only reorders reserves within the DL group",
        "Co-listed cells (Williams/Bostic at MLB, O'Donnell/Way at punter, Hartson/Rempel at long snapper) are ranked in listed order; the long-snapper order is a single-transcription detail. Jersey numbers are stored only for players who reached a 2014 regular-season roster (Week 1 library or nflverse roster_2014); the camp-only players carry none, so their ties break by name.",
        "Conte and Steltz opened camp on the active/PUP list and practiced from August 10; the game-day list still names them. Jared Allen and Kyle Long, held out of the August 8 opener, are not on the August 14 list and are available",
    ],
    "sources": {
        "depth_chart": "Chicago's first 2014 unofficial depth chart, released August 3, 2014: windycitygridiron.com 'Chicago Bears First 2014 Training Camp Depth Chart Released' (August 3), si.com 'Chicago Bears release depth chart: Jordan Palmer backup to Jay Cutler' (August 5), cbsnews.com/chicago 'View: Bears' Initial Depth Chart'; transcribed from search-engine extracts because those pages were not reachable from this session (see the record's limits). The club's own release article was not located",
        "roster_membership": "the chart's listed players plus the dated transaction log, read directly from chicagobears.com/team/transactions/2014 and the ESPN 2014 transactions page, with the club's August 5 (Herd) and August 15 (Miller) articles; later arrivals (Kofi Hughes August 15, Santonio Holmes August 16, Darius Reynaud and Peyton Thompson August 18, Terrance Mitchell and Roy Philon practice squad September 1, Jeremy Cain September 1, Rashad Ross September 16) excluded by their dates. Count check: 90 under contract on August 14",
        "availability": "CBS Sports 'Bears list inactives for Week 2 of preseason' (August 14, 2014; the club's list of ten players not suiting up, read as a search extract); ESPN Chicago Bears blog 'Bears hold out six from practice' (August 12, 2014); Bleacher Report 'Chicago vs. Jacksonville: Bears Preseason Week 2 Game Preview' (pre-game); chicagobears.com 'Special teams a top priority for Bears' (August 11, 2014, read directly); ESPN 'Bears reinstate Martellus Bennett' (August 10, 2014, read directly). Only players on the game-day list are unavailable; practice absences alone (Tillman and Ratliff rested August 12) do not make a player unavailable",
        "co_listed_order": "chart string, then line slot LT-LG-C-RG-RT, then chart column, then jersey number, then name (the Week 1 rule); unlisted players rank below every listed player of their group",
        "identity": "library/data/player_birth_dates.json, then nflverse players.csv (single 2014-active match by name; three reviewed namesakes by gsis id); jersey from the Week 1 library or nflverse roster_2014.csv; photographs from library/data/player_photos.json; page_url from the Week 1 library or the nflverse pfr id",
        "branch_control": "career/2014/team/roster/roster.md matched by gsis id through the identity registry and the league database, as in the Week 1 build",
        "draft_and_undrafted_pairing": "career/2014/league/personnel/draft_pairing.md (k=7: Chris Smith to Chicago for Charles Leno Jr.) and career/2014/draft/udfa_signings.md (Christian Jones signed with Jacksonville; leaves Chicago)",
        "trades_and_free_agency": "career/2014/trades/completed_trades/trades.md, career/2014/free_agency/signings.md, career/2014/league/personnel/fa_draws.md (Jeremy Cain's real September 1 Chicago signing does not occur; he is not a camp member on August 14 in any case)",
        "retirements": "career/2014/league/personnel/retirements.md; Patrick Mannelly's real June 20, 2014 retirement precedes camp and he is on no 2014 roster",
    },
    "cross_check_frozen": None,
}

CLUBS = [TAMPA_BAY, CHICAGO]


def load_week1_bio():
    """gsis id -> (Week 1 club code, player row); bio fields are club-neutral,
    the jersey is used only when the Week 1 club is the built club."""
    rows = {}
    for club in json.load(open(WEEK1_LIBRARY, encoding="utf-8"))["clubs"].values():
        for player in club["players"]:
            if player.get("gsis_id"):
                rows[player["gsis_id"]] = (club["code"], player)
    return rows


def load_nflverse(source):
    """gsis id -> (display name, birth date, pfr id) and (club, gsis) -> 2014 jersey."""
    players, jerseys = {}, {}
    if source is None:
        return players, jerseys
    path = Path(source) / "players.csv"
    if path.is_file():
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                players[row["gsis_id"]] = row
    path = Path(source) / "roster_2014.csv"
    if path.is_file():
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("jersey_number"):
                    jerseys[(row["team"], row["gsis_id"])] = row["jersey_number"]
    return players, jerseys


class Shared:
    """Identity and control inputs read once for every club."""

    def __init__(self, source):
        self.control = branch_control(ROSTER_MD)
        ids = identity()
        self.registry = json.load(open(BIRTH_DATES, encoding="utf-8"))["players"]
        self.registry_by_gsis = {}
        for name, row in self.registry.items():
            if row.get("gsis_id") and row.get("birth_date"):
                self.registry_by_gsis.setdefault(row["gsis_id"], row)
        self.week1 = load_week1_bio()
        self.photos = json.load(open(PHOTOS, encoding="utf-8"))["players"]
        self.nfl_players, self.nfl_jerseys = load_nflverse(source)
        self.nfl_by_name = collections.defaultdict(list)
        for row in self.nfl_players.values():
            self.nfl_by_name[norm(row["display_name"])].append(row)
        self.control_by_gsis, self.control_by_norm = {}, {}
        for name, (position, reason) in self.control.items():
            gsis = ids.get(name)
            if gsis:
                self.control_by_gsis[gsis] = (name, position, reason)
            self.control_by_norm[norm(name)] = (name, position, reason)


def build_club(spec, shared):
    registry, nfl_players, nfl_by_name = shared.registry, shared.nfl_players, shared.nfl_by_name
    code = spec["code"]

    def lookup(name, player_id):
        """gsis id and birth date for a chart name, registry first."""
        reviewed = spec["identities"].get(name)
        for candidate in (player_id, name, spec["aliases"].get(name)):
            if candidate and candidate in registry and registry[candidate].get("gsis_id"):
                row = registry[candidate]
                if reviewed and row["gsis_id"] != reviewed:
                    raise SystemExit("registry key %s is not the reviewed %s" % (candidate, name))
                return row["gsis_id"], row.get("birth_date"), "registry"
        if reviewed:
            if reviewed in shared.registry_by_gsis:
                return reviewed, shared.registry_by_gsis[reviewed].get("birth_date"), "registry"
            row = nfl_players.get(reviewed)
            if row is None:
                raise SystemExit("reviewed identity %s for %s has no nflverse row" % (reviewed, name))
            return reviewed, row.get("birth_date") or None, "nflverse_players"
        for candidate in (name, spec["aliases"].get(name)):
            if not candidate:
                continue
            rows = [r for r in nfl_by_name.get(norm(candidate), ())
                    if r.get("rookie_season") and int(r["rookie_season"]) <= SEASON]
            if len(rows) > 1:
                # A namesake who left the league before 2014 (the 2004 Keith
                # Lewis) yields to the one active in 2014.
                rows = [r for r in rows if r.get("last_season") and int(r["last_season"]) >= SEASON]
            if len(rows) == 1:
                return rows[0]["gsis_id"], rows[0].get("birth_date") or None, "nflverse_players"
        return None, None, None

    entries = collections.OrderedDict()
    for column, (formation, label, position, names) in enumerate(spec["chart"]):
        for rank, name in enumerate(names, 1):
            if name in spec.get("departed", {}):
                continue
            entry = entries.setdefault(name, {"name": name, "slots": [], "position": None})
            if position and entry["position"] is None:
                entry["position"] = position
            other_from = spec["other_from"].get(label)
            entry["slots"].append((formation, label, rank, column, other_from is not None and rank >= other_from))
    for name, (position, basis) in spec["unlisted"].items():
        entries[name] = {"name": name, "slots": [], "position": position, "unlisted": basis}

    players, changes, removed, cross = [], [], [], collections.Counter()
    for name, entry in entries.items():
        position = entry["position"]
        grp = group(position)
        if grp is None:
            raise SystemExit("unmapped position %r for %s" % (position, name))
        player_id = spec["ids"].get(name, name)
        gsis, birth, basis = lookup(name, player_id)
        controlled = shared.control_by_gsis.get(gsis) if gsis else None
        if controlled is None and norm(name) in shared.control_by_norm and gsis is None:
            controlled = shared.control_by_norm[norm(name)]
        if controlled:
            changes.append("Removed %s (%s): %s" % (name, position, controlled[2]))
            removed.append(name)
            continue
        football = [s for s in entry["slots"] if s[0] in {"Offense", "Defense"}]
        if football:
            best = min(football, key=lambda s: (s[2], s[3]))
            tier, column = best[2], best[3]
            ol_slot = OL_SLOT_ORDER.index(best[1]) if best[1] in OL_SLOT_ORDER else 9
        elif entry["slots"]:
            best = min(entry["slots"], key=lambda s: (s[2], s[3]))
            tier, ol_slot, column = best[2], 9, best[3]
        else:
            tier, ol_slot, column = 9, 9, 9
            changes.append("Added %s (%s) below every listed %s: %s" % (name, position, grp, entry["unlisted"]))
        roles = []
        for formation, label, rank, _, _ in entry["slots"]:
            if label == "KR" and rank == 1:
                roles.append("kick_return")
            if label == "PR" and rank == 1:
                roles.append("punt_return")
        if grp == "K":
            roles.append("placekicker")
        if grp == "P":
            roles.append("punt")
        slots = ",".join("%s%d" % (s[1], s[2]) for s in entry["slots"])
        week1_code, week1_row = shared.week1.get(gsis, (None, {})) if gsis else (None, {})
        # The built club's jersey only: the Week 1 number of a player who
        # reached another club (Meredith at Tennessee, McCray at Kansas City)
        # is not his camp number here.
        nfl_jersey = shared.nfl_jerseys.get((code, gsis)) if gsis else None
        jersey = nfl_jersey or (week1_row.get("jersey") if week1_code == code else None) or None
        if name in spec["no_jersey"]:
            jersey = None
        cross["jersey_nflverse_2014" if nfl_jersey else ("jersey_week1_%s" % code.lower() if jersey else "jersey_unknown")] += 1
        cross["gsis_" + (basis or "none")] += 1
        held = spec["held_out"].get(name)
        player = {
            "player_id": player_id, "name": name, "position": position, "listed_position": position,
            "group": grp, "available": held is None, "injury_report": "Out" if held else None,
            "return_week": None, "roles": sorted(set(roles)), "gsis_id": gsis, "jersey": jersey,
            "slots": slots, "_order": (tier, ol_slot, column, jersey_key(jersey), name),
        }
        if held:
            player["availability_note"] = held
        if birth:
            player["birth_date"] = birth
        for field in BIO_FIELDS:
            if week1_row.get(field) and field != "birth_date":
                player[field] = week1_row[field]
        photo = shared.photos.get(gsis) if gsis else None
        if photo and not player.get("headshot_url"):
            player["headshot_url"] = photo["url"]
            player["headshot_license"] = photo["license"]
            player["headshot_license_url"] = photo["license_url"]
            player["headshot_credit"] = photo["credit"]
            player["headshot_page"] = photo["source_page"]
        if not player.get("page_url") and gsis and nfl_players.get(gsis, {}).get("pfr_id"):
            pfr_id = nfl_players[gsis]["pfr_id"]
            player["page_url"] = "%s%s/%s.htm" % (PFR, pfr_id[0], pfr_id)
        players.append(player)

    by_group = collections.defaultdict(list)
    for player in players:
        by_group[player["group"]].append(player)
    for members in by_group.values():
        for rank, player in enumerate(sorted(members, key=lambda p: p["_order"]), 1):
            player["depth"] = rank
    for player in players:
        del player["_order"]
    players.sort(key=lambda p: (list(SIDE).index(p["group"]), p["depth"]))
    notes = []
    counts = collections.Counter(p["group"] for p in players if p["available"])
    short = {g: need for g, need in MINIMUM_GAME_DAY.items() if counts.get(g, 0) < need}
    if short:
        notes.append("Below the game-day minimum: %s" % ", ".join(
            "%s %d of %d" % (g, counts.get(g, 0), n) for g, n in short.items()))
    notes.extend(spec["notes"])

    seen = {}
    for player in players:
        if player.get("gsis_id") in shared.control_by_gsis:
            raise SystemExit("controlled player %s retained" % player["player_id"])
        if player["player_id"] in seen:
            raise SystemExit("duplicate player %s" % player["player_id"])
        seen[player["player_id"]] = True

    def stored(player):
        out = compact(player)
        if player.get("availability_note"):
            out["availability_note"] = player["availability_note"]
        return out

    club = collections.OrderedDict()
    club["code"] = code
    club["game"] = spec["game"]
    club["as_of"] = spec["as_of"]
    club["gate"] = spec["gate"]
    club[spec["transactions_key"]] = ["%s: %s" % t for t in spec["transactions"]]
    club["sources"] = spec["sources"]
    club["cross_check"] = spec["cross_check_frozen"] or dict(sorted(cross.items()))
    club["branch_changes"] = changes
    club["notes"] = notes
    club["players"] = [stored(p) for p in players]
    return club, removed


def build(source=None):
    shared = Shared(source)
    clubs, removed_by_club, games = collections.OrderedDict(), {}, collections.OrderedDict()
    for spec in CLUBS:
        club, removed = build_club(spec, shared)
        clubs[spec["team"]] = club
        removed_by_club[spec["team"]] = removed
        games[spec["game"]] = spec["team"]
    return {
        "schema_version": 2,
        "season": SEASON,
        "games": games,
        "branch_basis": BRANCH_BASIS,
        "branch_controlled_count": len(shared.control),
        "removed_by_club": removed_by_club,
        "clubs": clubs,
    }


def dumps(library):
    lines = ["{"]
    for key, value in library.items():
        if key == "clubs":
            continue
        lines.append("  %s: %s," % (json.dumps(key), json.dumps(value)))
    lines.append('  "clubs": {')
    teams = list(library["clubs"])
    for t_index, team in enumerate(teams):
        club = library["clubs"][team]
        lines.append("    %s: {" % json.dumps(team))
        for key, value in club.items():
            if key == "players":
                continue
            lines.append("      %s: %s," % (json.dumps(key), json.dumps(value)))
        lines.append('      "players": [')
        for p_index, player in enumerate(club["players"]):
            comma = "," if p_index < len(club["players"]) - 1 else ""
            lines.append("        %s%s" % (json.dumps(player), comma))
        lines.append("      ]")
        lines.append("    }" + ("," if t_index < len(teams) - 1 else ""))
    lines += ["  }", "}"]
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) > 2:
        sys.exit(__doc__)
    sys.stdout.write(dumps(build(sys.argv[1] if len(sys.argv) == 2 else None)))


if __name__ == "__main__":
    main()
