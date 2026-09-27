"""2013 NFL conference and division alignment (unchanged 2002-2019).

Club names match the team identifiers used in game receipts.
"""

DIVISIONS = {
    "AFC East": ("Buffalo Bills", "Miami Dolphins", "New England Patriots", "New York Jets"),
    "AFC North": ("Baltimore Ravens", "Cincinnati Bengals", "Cleveland Browns", "Pittsburgh Steelers"),
    "AFC South": ("Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Tennessee Titans"),
    "AFC West": ("Denver Broncos", "Kansas City Chiefs", "Oakland Raiders", "San Diego Chargers"),
    "NFC East": ("Dallas Cowboys", "New York Giants", "Philadelphia Eagles", "Washington Redskins"),
    "NFC North": ("Chicago Bears", "Detroit Lions", "Green Bay Packers", "Minnesota Vikings"),
    "NFC South": ("Atlanta Falcons", "Carolina Panthers", "New Orleans Saints", "Tampa Bay Buccaneers"),
    "NFC West": ("Arizona Cardinals", "St. Louis Rams", "San Francisco 49ers", "Seattle Seahawks"),
}

DIVISION_OF = {team: division for division, teams in DIVISIONS.items() for team in teams}
TEAMS = tuple(sorted(DIVISION_OF))
CONFERENCES = ("AFC", "NFC")
PLAYOFF_CLUBS_PER_CONFERENCE = 6


def conference_of(team):
    return DIVISION_OF[team].split()[0]


def division_teams(division):
    return DIVISIONS[division]


def conference_divisions(conference):
    return tuple(d for d in DIVISIONS if d.startswith(conference + " "))
