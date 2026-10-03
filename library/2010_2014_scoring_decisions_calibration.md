# 2010-2014 scoring decisions calibration

[Pre-build specification](2014_6_pre_build_specification.md) · [League base](2010_2014_calibration_base.md) · [Engine decisions](../runtime/2014_engine_decisions.md#kernel-20146-decisions-dated)

**What this is.** The league record behind the kernel 2014.6 scoring decisions (plan batch B3c, data only): the try decision (kick or go for two), two-point success, the onside kick decision and its recovery, and touchdowns scored by the side without the ball. The artifact is `library/data/2010_2014w4_scoring_decisions.json`, built by `scripts/research/build_2010_2014_scoring_decisions.py` with a `--check` mode. Nothing in `runtime/` reads it until batch B9.

**Data window.** NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, 2014), read only through the batch B2 source gate. 2013 and 2014 Weeks 1-4 are an anonymous post-divergence league population: they enter pooled counts only. No club's, game's or player's own row is stored; a club identity is read only to tell the kicking side from the receiving side, and the two-point team-quality proxy (a club-season red-zone touchdown share) lives in memory for one test and is never written.

## How each piece is counted

- **Try decision.** One decision per touchdown followed by a try, taken at the first try snap after it. Going for two means a two-point attempt from scrimmage. Kicking means an extra-point kick, including an aborted kick or a fake from kick formation (the decision was to kick). Touchdowns with no try, and overtime tries, are counted and left out. The state is the try team's margin after the touchdown and before the try (the committed builders' rebuilt running score) and the game seconds left.
- **The chart.** Time buckets Q1-Q3, then the fourth quarter at 900-601, 600-301, 300-121 and 120-0 seconds; one margin bucket per point from -15 to +15, plus 16 or more either way. Thin cells collapse by amendment A1, which was made after the preregistered collapse had been run and printed. The first three quarters are one cell per margin and never merge with the fourth quarter. Within the fourth quarter a thin group merges with its earlier neighbour of the same margin. The margin is never merged. A cell still thin after that is used as counted and flagged.
- **Two-point success.** One pooled rate over every two-point attempt from scrimmage that was not nullified, re-tries included. Each preregistered split is tested and adopted only when a likelihood-ratio test gives p below 0.01 pooled and the effect has the same sign in each pre-divergence season with at least 10 attempts per arm. The splits are pass against run, the 2-yard line against elsewhere, offensive against non-offensive touchdowns, the last five minutes, home, and the team red-zone proxy. The extra point is not duplicated here: it is the league base drive model's `rates.extra_point`, referenced with that artifact's digest.
- **Onside kicks.** Every valid kickoff from the kicking club's own 35 (2011-2014) or own 30 (2010) whose description says onside. Safety free kicks are reported apart. The state is the kicking club's margin and the seconds left, with half openers and the overtime opener in their own cell. An onside kick is *expected* when the kicking club trails in the fourth quarter with 300 seconds or less left, and a *surprise* otherwise. A recovery means the kicking club has the next offensive snap, holds `own_kickoff_recovery`, or scores on the kick. Spot records from the 35 keep the kick and return yards and the next start in the recovering club's frame. Each record carries the enforcement that closes its spot identity, and the check counts the records where that enforcement equals the kick row's accepted penalty yards.
- **Non-offensive touchdowns.** The units are valid interceptions on scrimmage downs, lost scrimmage fumbles without an interception, punts, missed field goals (blocked included), non-onside kickoffs from the 35 (2011-2014) and safety free kicks. Line-of-scrimmage bins (1-20, 21-40, 41-60, 61-80, 81-99) are adopted for a rate only when the test across bins gives p below 0.01. The return-touchdown records are feasibility-filtered:
  - air or gross yards at most the line of scrimmage plus 9;
  - an interception return covering 100 minus the line of scrimmage plus the air yards;
  - a punt return covering 100 minus the line of scrimmage plus the gross (blocked punts exempt);
  - a kickoff return covering 35 plus the kick yards;
  - a fumble spot on the field: the fumbled snap's line of scrimmage minus that snap's yards. The return is not tied to the fumble spot, because the ball is recovered where it rolls.

  A record that fails a check is dropped and counted.
- **Denominators against the base.** The interception units equal the base's interception drives, season by season. The punt units equal its punt-terminal drives, whatever category the drive ended in. One 2011 punt is a source defect, explained in the artifact: its rows are out of file order, so it ends no drive. The kickoff units are reported as the base's kickoff records, plus its retained kicks, plus return touchdowns and a counted remainder.
- **Try-snap participation.** From the 2013 snap counts, the first season nflverse publishes them. Club-game team snaps are regressed on the play-by-play counts of scrimmage snaps, no-play rows, two-point tries and kick snaps. The try coefficient is the number of on-field snaps a two-point try adds. It is a measured value, not a convention.

## Decision source

Every club and every autonomous run decides by these charts. Jacksonville's two-point and onside choices belong to Stone. They come from a call-sheet block (`decisions.two_point`, `decisions.kickoff`), a live pause or a dated delegation; U6 is unanswered, so the Week 5 inputs fail closed for Jacksonville without one. A decision drawn from the league model is never narrated as Stone's or a coach's. The success odds are the same for every club.

## Two passes

The primary pass reads nflverse. The second pass runs the same extraction on nflscrapR's own flags and its own rebuilt running score. Both files derive from the NFL GSIS feed, so the second pass checks the parse, not an independent observation of the seasons. nflscrapR lacks some extra-point and two-point rows, so its try counts and score states differ by those rows. The design phase's own second pass was description-driven, and it read the text after `REVERSED.` as the play that counted (amendment A3). Here both passes read the source flags, which already carry the final ruling, and only the penalty clauses are parsed from the counted text. That handling of replay reversals is why the interception and fourth-quarter counts can sit one or two plays from the design reviewer's figures.

## Reconciliation with the design readings

The design phase read 254 interception-return touchdowns in 2,088 interceptions, and the engineering review read 253 in 2,086. The review's description-driven pass handled replay reversals differently. In the fourth-quarter down-one try cells the design read 0 of 37 tries going for two and the review 0 of 36. This build's own figures are in the tables below and bind; the design readings are quoted for the record only.

## Figures

<!-- generated:begin -->
Generated by `scripts/research/build_2010_2014_scoring_decisions.py` from the artifact; do not edit.

| Season | Go | Tries | Touchdowns without a try |
|---|---|---|---|
| 2010 | 50 | 1267 | 3 |
| 2011 | 48 | 1257 | 4 |
| 2012 | 52 | 1293 | 4 |
| 2013 | 69 | 1336 | 2 |
| 2014w4 | 14 | 315 | 1 |

Chart season drift (stratified LR, pass 1): stat 131.987 on 121 df, p 0.233.

**Fourth-quarter two-point decision cells (go / tries)**

| Cell | Go | Tries | Thin |
|---|---|---|---|
| Q4 120-0|+2 | 0 | 23 |  |
| Q4 120-0|-1 | 2 | 29 |  |
| Q4 300-121+Q4 120-0|+0 | 0 | 20 |  |
| Q4 300-121+Q4 120-0|-4 | 0 | 33 |  |
| Q4 300-121+Q4 120-0|-8 | 0 | 27 |  |
| Q4 300-121|-1 | 0 | 22 |  |
| Q4 900-601+Q4 600-301+Q4 300-121+Q4 120-0|+1 | 23 | 27 |  |
| Q4 900-601+Q4 600-301+Q4 300-121+Q4 120-0|-2 | 32 | 34 |  |
| Q4 900-601+Q4 600-301+Q4 300-121+Q4 120-0|-3 | 0 | 22 |  |
| Q4 900-601+Q4 600-301+Q4 300-121+Q4 120-0|-5 | 16 | 20 |  |
| Q4 900-601+Q4 600-301+Q4 300-121+Q4 120-0|-6 | 0 | 22 |  |
| Q4 900-601+Q4 600-301+Q4 300-121+Q4 120-0|-7 | 0 | 37 |  |
| Q4 900-601+Q4 600-301+Q4 300-121+Q4 120-0|-9 | 0 | 17 | yes |
| Q4 900-601+Q4 600-301+Q4 300-121|+2 | 0 | 45 |  |
| Q4 900-601+Q4 600-301|+0 | 1 | 20 |  |
| Q4 900-601+Q4 600-301|-1 | 0 | 38 |  |
| Q4 900-601+Q4 600-301|-4 | 0 | 38 |  |
| Q4 900-601+Q4 600-301|-8 | 0 | 38 |  |

**Two-point success**: 115 of 232 (0.4957); season LR p 0.902; adopted splits: none.

| Split | Arm true | Arm false | LR p | Same sign | Adopted |
|---|---|---|---|---|---|
| home | 68/124 | 47/108 | 0.0850 | True | False |
| last_5_minutes | 45/91 | 70/141 | 0.9769 | False | False |
| offensive_touchdown | 112/216 | 3/16 | 0.0081 | False | False |
| red_zone_proxy_above_median | 64/115 | 51/117 | 0.0658 | True | False |
| spot_2 | 103/214 | 12/18 | 0.1277 | False | False |
| type_pass | 80/174 | 35/58 | 0.0574 | True | False |

**Onside**: onside share by season LR 1.703 on 4 df, p 0.790; chart season drift p 0.570.

| Class | Recovered | Onside kicks | 2011-2014 sensitivity |
|---|---|---|---|
| expected | 18 | 163 | 13/128 |
| surprise | 21 | 87 | 17/65 |

Onside spot records from the 35: 27 kicking-club, 153 receiving-club; checks enforcement_explained 165, enforcement_unexplained 15, feasible 180.

| Unit | Touchdowns | Units | Season LR p | LOS LR p | Bins adopted |
|---|---|---|---|---|---|
| interception | 254 | 2088 | 0.108 | 0.0000 | True |
| fumble_lost | 93 | 1166 | 0.173 | 0.0000 | True |
| punt | 93 | 10475 | 0.392 | 0.0000 | True |
| missed_field_goal | 5 | 678 | 0.373 | - | - |
| kickoff | 31 | 8049 | 0.570 | - | - |
| safety_free_kick | 0 | 65 | 1.000 | - | - |

Return-touchdown records kept: interception_return_td 250, fumble_return_td 80, punt_return_or_block_td 91, kickoff_return_td 30; checks fumble_dropped 13, fumble_feasible 80, interception_dropped 4, interception_feasible 250, kickoff_dropped 1, kickoff_feasible 30, punt_dropped 2, punt_feasible 91.

Try-snap participation (2013 snap counts): +1.06 offensive and +1.06 defensive snaps per two-point try (SE 0.11 and 0.11; 512 and 512 club-games).

**Second pass (nflscrapR)**

| Metric | nflverse | nflscrapR |
|---|---|---|
| tries (go/tries) pooled | 233/5468 | 220/5018 |
| two-point success | 115/232 | 113/220 |
| onside expected recovery | 18/163 | 17/147 |
| onside surprise recovery | 21/87 | 21/78 |
| interception return TD | 254/2088 | 237/1965 |
| fumble return TD | 93/1166 | 92/1164 |
| punt return or block TD | 93/10475 | 93/10426 |
| kickoff return TD | 31/8049 | 31/8030 |
| missed field goal return TD | 5/678 | 5/675 |

Chart season drift, pass 2: p 0.183; onside chart drift, pass 2: p 0.662; onside share LR, pass 2: p 0.861.
<!-- generated:end -->
