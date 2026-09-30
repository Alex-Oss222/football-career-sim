# 2010-2012 production evidence (E1 second stream)

**Research date:** September 30, 2026. **Kernel target:** 2014.4 candidate, defect register items 1 (unit strength) and 19 (individual attribution). **Status:** research and data; read by `runtime/strength.py` on the candidate branch. **Policy:** `runtime/2014_engine_decisions.md` E1 (dated public evidence before the divergence of January 15, 2013; no real post-divergence result; no club treated differently). This file is the second evidence stream beside the [2010-2012 honours evidence](2010_2012_honours_evidence.md): where honours are sparse expert judgements that can only lift a player, production covers every qualifying player and can place him above or below Average.

Machine record: [`data/2010_2012_production_evidence.json`](data/2010_2012_production_evidence.json), built by `scripts/research/build_2010_2012_production_evidence.py` (sources and sha256 in the JSON). Calibration of the effect size: [2014 strength calibration](2014_strength_calibration.md), section 9.

## 1. What these receipts are, and are not

- Every row is a **season statistical line** from nflverse's redistribution of the official NFL gamebook totals (`stats_player_reg_{season}.csv`), keyed by gsis id, with its EPA sums recomputed play by play from the nflverse play-by-play file in a separate verification pass.
- Production is **contaminated**: it mixes the player with his teammates, his quarterback or receivers, his blocking and his scheme. A tier says how his season line compared with that season's qualifiers in his position group, not what he can do on his own. The runtime records this as a limit; it does not correct for it.
- EPA is a model quantity computed later from contemporaneous plays. The plays themselves were public on the game date; the model adds no information from after the divergence.
- No 2013-or-later season is read. A player without a qualifying season has **no production tier** (he stays an Average low-confidence fallback under the tier rule); a missing tier is not evidence of anything.

## 2. Public date rule

A season's final regular-season statistics are public on the date of its last regular-season game, recorded per season from the play-by-play game dates:

| Season | Last regular-season game | Before the divergence (2013-01-15) |
|---|---|---|
| 2010 | January 2, 2011 | yes |
| 2011 | January 1, 2012 | yes |
| 2012 | December 30, 2012 | yes |

The runtime applies the same gate as for honours: a season's rows are admissible only when that date is before the divergence and before the date the input is built for. A 2012 line is therefore rejected as future-dated for an input dated December 30, 2012 or earlier and admissible from December 31, 2012 (`tests/test_strength.py`).

## 3. Rule fixed before the first build

Written into the script's `PREREGISTERED` block before the first run.

**Position groups.** QB; RB (RB, HB, FB); WR; TE; OL (T, G, C and aliases); DL (DE, DT, NT); LB (OLB, ILB, MLB); DB (CB, S, SS, FS); K; P.

**Metrics, qualifying minimums and shrinkage.**

| Group | Metric | Minimum | Shrinkage k |
|---|---|---:|---:|
| QB | passing EPA per dropback (attempts + sacks) | 200 dropbacks | 100 |
| RB | (rushing EPA + receiving EPA) per opportunity (carries + targets) | 100 opportunities | 50 |
| WR | same | 60 | 50 |
| TE | same | 40 | 50 |
| OL | starts (weeks on the club's weekly depth chart at depth 1, formation Offense, regular season) and games played: **job evidence only, no production line and no tier** | 1 | none |
| DL, LB, DB | disruption per game = sacks + 0.5 x QB hits + tackles for loss + interceptions + 0.5 x passes defended | 8 games | 4 |
| K | field goals made over expected per attempt, expected from that season's league make rate in six distance bands (0-19, 20-29, 30-39, 40-49, 50-59, 60+) | 15 attempts | 10 |
| P | net yards per punt (nflverse `pt_net_yards`) | 30 punts | 10 |

Shrunk value = (n x raw + k x league mean) / (n + k), the league mean being the denominator-weighted mean over that season's qualifiers in the group. Tiers are cut on the shrunk value. Kicker and punter tiers are carried for the special-teams strength the kernel does not read yet.

**Tiers by fixed percentile cut-points**, among that season's qualifiers in the same group, with share_above = (qualifiers with a strictly higher shrunk value) / qualifiers: Elite below 0.10; Plus from 0.10 to 0.30; Average from 0.30 to 0.70; Below-Average from 0.70 to 0.90; Replacement-Level from 0.90. No tier is assigned by judgement.

**Window.** A player's production tier is the best tier over the two most recent completed pre-divergence seasons before the season being played (2014 branch: 2011 and 2012; 2012 study target: 2010 and 2011). For the 2014 branch, 2010 counts only when neither window season qualifies and is discounted one tier (Elite to Plus, and so on; Replacement-Level stays). The 2012 study target has no earlier season built, so it has no fallback.

**Amendments recorded after the first build, before any calibration fit or tier was read.** (1) The stats file's `def_tackles_for_loss` column is unpopulated (all zero) in 2010 and 2011, so the tackles-for-loss term is taken from the play-by-play recomputation (`tackle_for_loss_1/2_player_id`) in every season; the 2012 column is kept beside it for comparison only (2012: 614 defenders, 520 equal, 94 with a higher play-by-play count; means 3.43 against 3.63). (2) The play-by-play recomputation excludes two-point tries from attempts, carries and targets, as the official totals do; the first build's off-by-one to off-by-three count differences were all two-point tries.

## 4. Coverage

1,709 players, 3,399 player-seasons with a qualifying line (2,684 tiered rows plus 715 offensive-line job-evidence rows, 495 of them with eight or more starts).

Qualifiers per season and group (with the league mean the shrinkage pulls toward):

| Season | QB | RB | WR | TE | DL | LB | DB | K | P |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2010 | 34 (0.069) | 58 (-0.050) | 80 (0.201) | 38 (0.187) | 198 (0.88) | 189 (0.81) | 241 (0.57) | 31 (0.016) | 32 (37.7) |
| 2011 | 35 (0.055) | 61 (-0.045) | 78 (0.204) | 34 (0.226) | 194 (0.96) | 188 (0.86) | 246 (0.54) | 33 (0.024) | 34 (38.9) |
| 2012 | 38 (0.052) | 54 (-0.049) | 73 (0.234) | 38 (0.173) | 180 (1.01) | 182 (0.88) | 252 (0.50) | 31 (0.022) | 32 (39.9) |

The tier shares follow the cut-points to within rounding (for example 2012 QB: 4 Elite, 8 Plus, 15 Average, 8 Below-Average, 3 Replacement-Level of 38). The 2012 Elite quarterbacks are Tom Brady, Peyton Manning, Matt Ryan and Colin Kaepernick (234 dropbacks, shrunk from 0.226 to 0.174); Blaine Gabbert (300 dropbacks, -0.125 raw) is Below-Average; Mark Sanchez, John Skelton and Brady Quinn are Replacement-Level.

**What the metrics reward, stated plainly.** EPA per opportunity favours efficient, often pass-catching backs: the 2012 Elite running backs are Darren Sproles, Pierre Thomas, Danny Woodhead, Marcel Reece, Joique Bell and C.J. Spiller, while Adrian Peterson (348 carries, 2,097 yards) is Plus. The disruption index is a counting statistic per game and favours pass rushers and ball-hawking corners; a run-stuffing tackle or a shutdown corner who is not thrown at is under-rated by it. These are properties of the declared metrics, reported, not corrected after the fact.

## 5. Verification pass

**Method.** Every count and EPA sum was recomputed from scratch from the play-by-play file by gsis id (dropbacks and passing EPA from `qb_epa` on the passer's pass plays including sacks and spikes; carries and rushing EPA on runs and kneels; targets and receiving EPA on the receiver's pass plays; sacks with half sacks at 0.5, QB hits, interceptions, passes defended and tackles for loss from the player-id fields; field goals by kicker with distance bands; punts by punter, blocked punts excluded). Tolerance: counts exact; EPA sums within 1.0 EPA or 2 percent of the larger magnitude.

| Label | Player-seasons | Meaning |
|---|---:|---|
| Confirmed two-pass | 2,616 | both computations agree inside tolerance |
| Corrected | 68 | the play-by-play recomputation is adopted over the stats file (EPA sums 1.05 to 3.3 EPA apart; median 1.05; every count exact); no tier moved by more than one step and most did not move |
| Unverified | 0 | none after the amendments |
| Job evidence | 715 | offensive-line rows, no production line to verify |

**Spot check against public search summaries (September 30, 2026; page fetches are blocked by the session proxy, so these are search-result summaries, each a second source independent of nflverse).** 23 figures for 20 players:

| Player, season | Public figure (search summary) | File | Result |
|---|---|---|---|
| Tom Brady 2012 | 637 attempts, 27 sacks | 664 dropbacks, 27 sacks | confirmed |
| Peyton Manning 2012 | 583 attempts, 21 sacks | 604 dropbacks, 21 sacks | confirmed |
| Drew Brees 2011 | 657 attempts, 24 sacks | 684 dropbacks (660 attempts), 24 sacks | **differs by 3 attempts** (nflverse counts 660); no tier effect (Elite either way); recorded as unresolved against the public figure |
| Cam Newton 2011 | 517 attempts, 35 sacks | 552 dropbacks, 35 sacks | confirmed |
| Blaine Gabbert 2012 | 278 attempts, 22 sacks | 300 dropbacks, 22 sacks | confirmed |
| Adrian Peterson 2012 | 348 carries, 40 receptions | 348, 40 | confirmed |
| Arian Foster 2012 | 351 carries, 40 receptions | 351, 40 | confirmed |
| Ray Rice 2011 | 291 carries, 76 receptions | 291, 76 | confirmed |
| Maurice Jones-Drew 2011 | 343 carries, 43 receptions | 343, 43 | confirmed |
| Calvin Johnson 2012 | 122 receptions, 204 targets | 122, 204 | confirmed |
| Wes Welker 2011 | 122 receptions, 173 targets | 122, 173 | confirmed |
| Rob Gronkowski 2011 | 90 receptions, 124 targets | 90, 124 | confirmed |
| Jimmy Graham 2011 | 99 receptions, 149 targets | 99, 149 | confirmed |
| J.J. Watt 2012 | 20.5 sacks, 16 passes defended | 20.5, 16 | confirmed |
| Von Miller 2012 | 18.5 sacks | 18.5 | confirmed |
| Jared Allen 2011 | 22 sacks | 22 | confirmed |
| DeMarcus Ware 2011 | 19.5 sacks | 19.5 | confirmed |
| Richard Sherman 2012 | 8 interceptions, 24 passes defended | 8, 24 | confirmed |
| Charles Tillman 2012 | 3 interceptions, 16 passes defended | 3, 16 | confirmed |
| Justin Tucker 2012 | 30 of 33 field goals | 30 of 33 | confirmed |
| Matt Prater 2012 | 26 of 32 | 26 of 32 | confirmed |
| Andy Lee 2012 | 67 punts, 43.2 net | 67, 43.24 | confirmed |
| Shane Lechler 2011 | 78 punts, 40.9 net | 78, 40.03 | **net differs by 0.9 yards**: nflverse `pt_net_yards` and the NFL's net definition disagree for this line (Lee's agrees); the punter metric uses the nflverse definition for every punter, so the ordering is consistent but the level is not the NFL's; recorded as unresolved |

Two of the 23 figures differ from the public summary; neither moves a tier. Both are recorded in the JSON's verification notes.

## 6. Known limits a human should keep in view

1. **Offensive linemen have no production tier.** Their strength value comes from honours only; starts and games are job evidence. Pre-2013 snap counts are not available in the pinned sources.
2. **Contamination is unmodelled** (section 1). A quarterback's EPA per dropback rides on his protection and receivers; a receiver's on his quarterback.
3. **Percentile tiers are relative to that season's qualifiers.** A 2010 Plus and a 2012 Plus are the same rank, not the same absolute level.
4. **The defensive index is a counting index** without snap denominators (none exist pre-2013 in the sources), so a rotational rusher with few games is shrunk toward the mean but a full-time run defender is not credited for what the index does not count.
5. **nflverse EPA and net-punt definitions** are the source's, not the NFL's (Brees, Lechler above).
