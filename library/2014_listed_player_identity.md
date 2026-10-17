# 2014 listed player identity

**What it is.** [2014_listed_player_identity.json](data/2014_listed_player_identity.json) gives, by gsis id, the listed height (inches), weight (lb), college and jersey number that the [league player cards](../career/league_players/README.md) show. It is reader data only: no game, evaluation or decision reads it. Birth dates, the 2014 Week 1 roster numbers and the league player database's college stay in their own committed sources and take precedence where the cards use them.

**Built by** `scripts/research/build_2014_listed_player_identity.py SOURCE_DIR` from two pinned public nflverse files, the same files the [2014 in-season rails](2014_inseason_rails.md) pin. `--check` rebuilds from the files and compares with the committed JSON; the builder stops if either file's sha256 differs from its pin.

| File | Used for | sha256 |
|---|---|---|
| nflverse [roster_weekly_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2014.csv) | 2014 regular season, Weeks 1 to 4 only: height, weight, college and jersey number with his club and week | 331022cd3b0c69d99c581f02b6fde6853e87ac431739c4b49841ee6e02893d6c |
| nflverse [players.csv](https://github.com/nflverse/nflverse-data/releases/download/players/players.csv) | Fallback height, weight and college for a player with no Weeks 1-4 row, and college when his Weeks 1-4 rows leave it blank; kept only for gsis ids a committed identity source of this repository names | e85b2736908bd6701b038d18d98025e2b31e6e9db7cebf6f21e71fb0c88f9ba1 |

**Information gate.** Only Weeks 1 to 4 of 2014 are read from the weekly file, the rosters public by the latest game on record (September 29, 2014). Later weeks enter only when the career clock reaches them and the builder is rerun with a later gate. The player file's listing is that file's latest, which can date from a later season; the cards say so on those players' pages ("the public player file's latest listing").

**Per player.** Height, weight and college come from his latest Weeks 1-4 row that carries each field; when every one of those rows leaves the college blank, the player file's college is used. Heights outside 60-90 inches and weights outside 150-400 lb are dropped as unusable. The number is his latest Weeks 1-4 row's jersey number with that row's club and week; nflverse club codes ARZ, BLT, CLV, HST and SL are normalized to ARI, BAL, CLE, HOU and STL. A player the real 2014 Jaguars listed in Weeks 1-4 also carries that number as `jaguars_number`.

**The number a card shows** (runtime/player_cards.py):

- Another club's player: his 2014 Week 1 roster number with that club; else his Weeks 1-4 listing when it was with the club of his latest game on record; else N/A.
- A Jacksonville player: Jacksonville has not recorded jersey numbers. The card shows his real 2014 Jaguars number when he had one; else the number he wore in 2014 with his real club, when no other current Jaguar holds or claims that number; else N/A.

**Coverage at the September 29, 2014 build.** 2,627 players: 1,788 from Weeks 1-4 rows, 839 from the player file. Of the 2,028 players in the game records, every one has a height and weight, 2,026 a college and 1,574 a number; 39 of the 68 players whose latest game was with Jacksonville show a number.
