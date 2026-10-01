# Player birth dates and simulation ages

**Research and separate verification completed:** September 28, 2026.
**Permitted fact:** birth date and stable identity only, applicable before the 2013 divergence. Retrospective biographical sources do not authorize later career outcomes.
**Scope:** all 1,661 distinct people in the branch background depth library plus Jacksonville's current 53 and eight practice-squad players. This is not a claim to cover every historical NFL player or a future draft class.

## Controlling data and displays

[Birth-date registry](data/player_birth_dates.json) stores immutable DOBs, GSIS IDs, source IDs and verification status. It deliberately stores no current real-world age, last season, later team or retirement status. [Conflict reviews](data/player_birth_date_corrections.json) retain competing dates, selected evidence and the reason for each decision.

Document 4 and the [Jacksonville roster](../career/2013/roster.md) display DOB and completed years at Document 5's master date. The [league view](../career/2013/player_ages.md) includes every represented club and Jacksonville's practice squad. The source registry does not own roster membership. No DOB creates a rating, development curve or retirement deadline.

## Two passes and limitations

1. Research: downloaded nflverse `players.csv`; mapped background players by their existing GSIS IDs. Jacksonville namesakes and aliases were reviewed explicitly, not fuzzy-matched. Only the birth-date/identity fields were retained.
2. Verification: separately compared the 2013 roster data by GSIS ID and fetched ESPN's athlete birth-date field for every one of the 1,661 identities. The two nflverse exports agreed for 1,654 players; seven were missing from the season roster export. Those two exports are not independent publications. ESPN supplied a second publisher for all 1,661 checks: 1,650 dates matched, and 11 disagreements received a third-source review.

A matching database field is corroboration, not proof that all databases have independent upstream reporting. `corroborated` means agreement between the fetched nflverse and ESPN records. `reviewed_source_conflict` points to the explicit conflict record; it must not be relabeled as unanimous agreement.

The 11 conflicts: Andrew Whitworth, Charles Godfrey, Dashon Goldson, Dimitri Patterson, Jake McQuaide, Jerry Hughes, Kurt Coleman, Leonard Johnson, Luke Stocker, Steve Johnson and Tarvaris Jackson. Ten retain the nflverse DOB supported by the additional source. Kurt Coleman is corrected from April 1 to **July 1, 1988**, supported by a contemporaneous NFL birthday notice and ESPN/PFR. The incorrect April date also appears in a Panthers guide and is retained in the conflict note. Two ESPN links resolve to namesakes (Leonard Johnson and Steve Johnson), so those links are rejected as DOB evidence rather than silently treated as corrections.

Identity review also distinguishes C.J. Mosley (DT, 1983) from the later linebacker, C.J. Wilson (DE, 1987) from the defensive backs, Mike Brown (WR, 1989), Daryl Smith (LB, 1982), and Brandon King (Purdue DB, 1987). Mike Brewster maps to Michael Brewster's GSIS ID; Antwon Blake retains his 2013 name while mapping to the same stable identity later listed as Valentino Blake. Alex Smith (KC) and Alex Smith (CIN) retain distinct existing simulation IDs.

### 2014 Week 1 library import (October 1, 2026)

A fourth evidence class, `library_week1_source`, covers the 367 players of the [2014 Week 1 depth library](data/2014_week1_depth_charts.json) who had no registry row: 360 new identities and seven alias rows for a gsis id already registered under another spelling (for example `Jay Ratliff` for `Jeremiah Ratliff`), added only where both dates agree and marked `alias_of`. The birth date comes from the library's own `birth_date` field, which the user's nflverse-derived `user_nfl_2014_week1.json` supplied by gsis id (source key `library_week1_source_2014` in the registry). It is one provider: no second publisher was fetched, so these rows are not `corroborated` and must not be relabelled as such without that check. Phil Bates (Seattle) carries no library birth date and stays unregistered; he enters a weekly package only as a background player flagged `age_unverified`, the rule every non-Jacksonville player gets (runtime.week_inputs). The Carolina running back listed as `Jonathan Stewart` shares his name with the registered St. Louis linebacker (a different gsis id); the library row was not imported and the collision is open for identity review. Reproduce with `python scripts/research/import_2014_week1_birth_dates.py` (`--write` to apply; idempotent).

## Source provenance

| Source | Applicability and use | Limitation |
|---|---|---|
| [nflverse player data](https://github.com/nflverse/nflverse-data/releases/download/players/players.csv) | Research pass, DOB and GSIS identity; source SHA-256 saved in registry | Mutable retrospective dataset; all later career fields discarded |
| [nflverse 2013 rosters](https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_2013.csv) | DOB cross-check only | Same publisher, not independent verification; real team/control/status ignored |
| ESPN athlete API, exact URL template plus each `espn_id` in registry | Independent-publisher DOB comparison; all 1,661 fetched September 28, 2026 | Includes erroneous dates and namesakes; no current age/status/stats imported |
| Club/college bios, period media guides, Pro Football Reference and Pro Football Archives | Third-source conflict review, exact URL per player in corrections JSON | Birth-date proposition only; no later performance, health or destination evidence |

All sources were accessed September 28, 2026. Publication dates vary: the exact linked college/club editions and the contemporaneous Coleman notice are identified in each conflict review; mutable databases have no single publication date. Modern retrieval does not change a player's DOB applicability.

## Refresh and validation

```sh
python scripts/render_player_ages.py
python scripts/render_player_ages.py --check
python scripts/validate_repository.py
```

The renderer always reads Document 5's master date, never the machine clock or just the NFL season label. It increments age on the birthday, handles January postseason dates, and uses March 1 for a February 29 birthday in a non-leap year. Regeneration is idempotent. CI rejects stale DOB/age cells, stale date markers or missing identities. Verify and add a new signing's or prospect's DOB before preparing his first game.

Weekly input preparation also derives each participant's age on that game's actual scheduled date. This is a `player_ages` sidecar outside TeamInput and the frozen outcome packet, so it cannot alter an already committed draw or a replay.

To reproduce the research artifact, retain the two downloaded CSVs and the independent ESPN DOB-only responses in `SOURCE_DIR/espn_birth_dates/GSIS_ID.json` (fields: `player`, `espn_id`, `birth_date`). Raw downloads stay outside Git. The builder fails on an unreviewed disagreement:

```sh
python scripts/research/build_player_birth_dates.py SOURCE_DIR --checked-on YYYY-MM-DD
```

Historical retirement evidence is an explicitly requested audit in `archive/2013_jacksonville_historical_retirements.md`. Runtime does not load it. Announcements, final appearances, contracts, reserve transactions and ceremonial retirements are different events; a last NFL season is not an exact retirement date. Branch retirements require their own closed simulation event.
