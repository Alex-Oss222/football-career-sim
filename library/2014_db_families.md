# 2014 defensive-back families for the background clubs (kernel 2014.6, batch B15, W2b)

**Built:** October 16, 2026 (branch clock September 28, 2014, after Week 4). **Football information window:** the real 2014 Week 1 depth charts (public September 2 to 5, 2014) and the 2014 weekly rosters of regular-season Weeks 1 to 4 (the specification's cut: game dates on or before September 29, 2014). **Status: PREPARED, GATED.** Read from the in-season rails' first week (2014 Week 5) by a kernel that seats defensive backs by family (profile flag `db_slots`); kernel 2014.5, Weeks 1 to 4 and the 2013 season never read it.

**Machine artifact:** [data/2014_db_families.json](data/2014_db_families.json). **Builder:** `scripts/research/build_2014_db_families.py` (`--check` rebuilds it byte for byte from the gated sources). **Reader:** `runtime.depth_library.relabel_defensive_backs`, applied by `runtime.week_inputs.build_package` to each background club's rails entry. **Tests:** `tests/test_db_slots.py`.

## What it is for

Kernel 2014.6 seats each club's defensive backs by position family (`runtime/participation.py`, `db_seats`): two outside corners, two safeties and the nickel, the nickel settled first, a removed corner replaced from the corners and a removed safety from the safeties. That needs each defensive back's family. The Week 1 library's `position` comes from the player's best depth-chart slot when the slot label is a kernel group, and otherwise from the nflverse depth chart's `position` column, which is back-filled and was wrong for corner slots: DeAngelo Hall (Washington, LCB1), Kareem Jackson (Houston, LCB1) and eleven other corners whose chart slot is LCB or RCB were stored as safeties. The rule (plan batch B15; [pre-build specification](2014_6_pre_build_specification.md), section 4, "Inputs and participation") is the chart slot first, then the contemporaneous 2014 weekly-roster label, never the depth chart's `position` column or `players.csv`.

The Week 1 library itself is not rebuilt: the in-season rails pin its clubs block (`library_clubs_sha256`) and the closed Weeks 1 to 4 packages must rebuild unchanged, so the labels live in this separate table and apply from Week 5 only.

## Sources

| Use | Source | Scope | sha256 |
|---|---|---|---|
| Pass 1: chart slots | the committed [Week 1 library](data/2014_week1_depth_charts.json) `slots` field | every library player, by gsis id | recorded in the artifact |
| Pass 2: chart slots, read afresh | nflverse [depth_charts_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_2014.csv), cut by `scripts/research/sources_2010_2014.py` to `depth_charts_2014w4.csv` | Week 1, regular season, defense rows | fetched 37c5d02473ebec605aaf68747a50ec77f02347f68f16e69cb5d84862f75c6d3a; cut 9ff91980447562de73852864d2426ee2226a01876c3f003b07b0e9f65c2a7108 |
| Weekly label | nflverse [roster_weekly_2014.csv](https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2014.csv), cut to `roster_weekly_2014w4.csv` | regular season, Weeks 1 to 4, the player's latest week | fetched 331022cd3b0c69d99c581f02b6fde6853e87ac431739c4b49841ee6e02893d6c; cut fc963d8ddd38aef3541f7db07b8732e1a7c0780ce0fba6bf02775b2c9cf5558c |
| Newcomers | the committed [in-season rails](2014_inseason_rails.md) base (real-53 fill, restorations, practice squads) and rows | their stated positions | the rails manifest's pins |

## The rule

1. **Chart slot.** The best-ranked family slot of the player's Week 1 chart rows: LCB, RCB, CB, NB, NCB or NKL a corner; SS, FS or S a safety. A corner's label is CB; a safety keeps his slot label.
2. **Weekly roster.** Otherwise the label of his latest regular-season week in 2014 Weeks 1 to 4: CB a corner; S, SS, FS or SAF a safety.
3. **Rails position.** Otherwise the in-season rails' stated position (the Week 1 chart's, the weekly roster's or the source's, `runtime/rails.py`); a generic DB label keeps no family and fills a short seat.
4. **Nickel.** A Week 1 chart NB, NCB or NKL slot at the player's own branch club gives him the `nickel` role there. The source's only such label is Tampa Bay's Leonard Johnson (NKL1). No chart in the source labels an outside reserve, so no background club has one and the move-up convention applies (`runtime/participation.py`).

## Counts and verification

- 363 defensive backs with a family: 286 by chart slot, 27 by weekly label, 50 by the rails position; 14 rails newcomers with a generic DB label and no weekly row keep no family.
- Pass 2 reproduces pass 1's family for all 290 library defensive backs (the builder stops on any difference).
- No player's chart-slot family disagrees with his weekly label.
- 15 library positions change: 13 corners by chart slot (DeAngelo Hall, Corey Graham, Charles Godfrey, Darius Butler, Lardarius Webb, Walter Thurmond, Sherrick McManis, Kareem Jackson, Ron Parker, Omar Bolden, Logan Ryan, Andre Hal, Keith McGill) and two Buffalo deep-safety-slot players by weekly label (Da'Norris Searcy and Duke Williams, SS to FS; a DS slot is not on the rule's list).

## Limits

- The charts are single-publisher, as in the Week 1 library.
- A newcomer who joined after Week 4 and was on no Week 1 chart takes the rails' stated position; the weekly label after Week 4 is beyond the information gate.
- The table is labels only: no statistic, grade or football judgement is read or written, and nothing here is evidence about a player.
