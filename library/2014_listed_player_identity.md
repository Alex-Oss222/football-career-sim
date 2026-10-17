# 2014 listed player identity

**What it is.** [2014_listed_player_identity.json](data/2014_listed_player_identity.json) gives, by gsis id, the listed height (inches), weight (lb), college and jersey number that the [league player cards](../career/league_players/README.md) show. It is reader data only: no game, evaluation or decision reads it. Birth dates, the 2014 Week 1 roster numbers and the league player database's college stay in their own committed sources and take precedence where the cards use them. A source entry keyed by name is used for a player only when its gsis id is his, because two players can share a record name across seasons.

**Built by** `scripts/research/build_2014_listed_player_identity.py SOURCE_DIR` from three pinned public nflverse files: the two the [2014 in-season rails](2014_inseason_rails.md) pin and the 2013 season roster the [league player database](../career/2014/League/personnel/league_database_report.md) pins. `--check` rebuilds from the files and compares with the committed JSON; the builder stops if any file's sha256 differs from its pin. Text is HTML-unescaped (the weekly file stores `Texas A&amp;M`; the JSON holds `Texas A&M`).

| File | Used for | sha256 |
|---|---|---|
| nflverse [roster_weekly_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2014.csv) | 2014 regular season, Weeks 1 to 4 only: height, weight, college and jersey number with his club and week | 331022cd3b0c69d99c581f02b6fde6853e87ac431739c4b49841ee6e02893d6c |
| nflverse [roster_2013.csv](https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2013.csv) | A player with no Weeks 1-4 row: height, weight and college from his latest 2013 week | abf73c2b1ef10914af78f6b7397338508bd0c9f0372d2f0667a630e06a4484ed |
| nflverse [players.csv](https://github.com/nflverse/nflverse-data/releases/download/players/players.csv) | College when the roster rows leave it blank; for a player in neither roster file, college, and height and weight only when his last listed season there is 2013 or earlier | e85b2736908bd6701b038d18d98025e2b31e6e9db7cebf6f21e71fb0c88f9ba1 |

Fallback listings are kept only for gsis ids that a committed identity source of this repository names.

**Information gate.** Only Weeks 1 to 4 of 2014 are read from the weekly file, the rosters public by the latest game on record (September 29, 2014). Later weeks enter only when the career clock reaches them and the builder is rerun with a later gate. The 2013 season roster was public before the 2014 season. The player file holds each player's latest listing, which can date from a later season, so its height and weight are used only when that listing is from 2013 or earlier; otherwise the card shows N/A. College is the school he attended before entering the league.

**Per player.** Height, weight and college come from his latest Weeks 1-4 row that carries each field. Heights outside 60-90 inches and weights outside 150-400 lb are dropped as unusable. The number is his latest Weeks 1-4 row's jersey number with that row's club and week; nflverse club codes ARZ, BLT, CLV, HST and SL are normalized to ARI, BAL, CLE, HOU and STL. A player the real 2014 Jaguars listed in Weeks 1-4 also carries that number as `jaguars_number`.

**The number a card shows** (runtime/player_cards.py):

- Another club's player: his 2014 Week 1 roster number with that club, unless that Week 1 row places him there through a Jacksonville trade (it then carries his real club's number); else his Weeks 1-4 listing when it was with the club of his latest game on record; else N/A.
- A Jacksonville player: Jacksonville has not recorded jersey numbers. For a player Jacksonville currently controls (active roster, reserve and practice squad, as the weekly input gate reads the roster), the card shows his real 2014 Jaguars number when he had one; else the number he wore in 2014 with his real club, when no other current Jaguar holds or claims that number; else N/A. A former Jaguar whose latest game was with Jacksonville shows N/A.

**Coverage at the September 29, 2014 build.** 2,627 players: 1,788 from Weeks 1-4 rows, 622 from the 2013 season roster and 217 from the player file. Of the 2,028 players in the game records, 1,652 cards use Weeks 1-4 rows, 371 the 2013 season roster and 5 the player file; 2,026 have a height, weight and college, and 1,566 a number. 33 of the 68 players whose latest game was with Jacksonville show a number; 51 of those 68 are current Jaguars. Casey Kreiter and Adrian Phillips have no dated height or weight listing.
