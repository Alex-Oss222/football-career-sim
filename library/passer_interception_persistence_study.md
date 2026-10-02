# Individual passer interception-rate persistence, 2010 to 2014 (research only)

**Research date:** October 2, 2026. **Asked by:** Alex Stone, head coach, after Week 2 of the 2014 season. **Status:** research only. Nothing in `runtime/` reads this file or its data; `runtime/strength.py`, every calibration file the kernel reads, every state file and every player card are unchanged. **Policy:** `runtime/2014_engine_decisions.md` E1 (dated public evidence before the divergence of January 15, 2013; no real post-divergence outcome as an answer key for a real person; no club treated differently).

Machine record: [`data/passer_interception_persistence.json`](data/passer_interception_persistence.json), built by `scripts/research/build_passer_interception_persistence.py` (sources, sha256 values, every qualifier row, every season pair, both passes' fits).

## 1. The question

The kernel's interception channel carries no passer term. Phase 2 of the kernel 2014.4 calibration fitted the offensive passing composite (the passer at weight 3 plus WR1-3 and TE1) on the 2012 per-drive interception share across the 32 clubs and dropped it: slope 0.00062 per composite unit, SE 0.00070, leave-one-club-out skill -0.057 ([2014 strength calibration](2014_strength_calibration.md), section 10.3). The channel is wired with slope 0 (`runtime/strength.py`, `int_share_offense_passing`), so in the branch every passer's interception draw comes from the 2012 league base and the drive situation, not from who is throwing.

The coach's question is whether the dropped term was the wrong test rather than the wrong idea. The punter term survived a different test: not a club-level cross-section but a season-pair persistence test, the specialist's own next-season metric regressed on his prior-season metric over 2010 to 2011 and 2011 to 2012, kept with leave-one-pair-out skill 0.039 (section 10.4; `PUNTER_SLOPE` 0.3399). This study runs that same test on an individual passer's interception rate per dropback, and reports what 2010 to 2014 would say.

## 2. Sources

All fetched October 2, 2026 from the nflverse GitHub release assets (the same host and files the [2010-2012 production evidence](2010_2012_production_evidence.md) used; the proxy allowed github.com and its release-asset redirect, no host was refused):

| File | URL | sha256 |
|---|---|---|
| stats_player_reg_2010.csv | https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_reg_2010.csv | a0ea4f13… (matches the pinned production-evidence hash) |
| stats_player_reg_2011.csv | …/stats_player/stats_player_reg_2011.csv | f8a8e44c… (matches) |
| stats_player_reg_2012.csv | …/stats_player/stats_player_reg_2012.csv | 6cdfbf3b… (matches) |
| stats_player_reg_2013.csv | …/stats_player/stats_player_reg_2013.csv | 342fd27e… |
| stats_player_reg_2014.csv | …/stats_player/stats_player_reg_2014.csv | in the JSON |
| play_by_play_2010.csv.gz to 2012 | …/pbp/play_by_play_{season}.csv.gz | all three match the pinned hashes |
| play_by_play_2013.csv.gz, 2014 | …/pbp/play_by_play_{season}.csv.gz | in the JSON |

Full hashes are in the JSON's `sources` block. The 2010-2012 files are byte-identical to the ones the production-evidence build pinned on September 30, 2026.

**Public-date rule.** A season's statistics are public on its last regular-season game: 2010 January 2, 2011; 2011 January 1, 2012; 2012 December 30, 2012 (all before the divergence); 2013 December 29, 2013; 2014 December 28, 2014 (both after it). The 2013 and 2014 seasons are read here only as a league population, and the JSON labels every number from them "post-divergence league population, information only".

**Protagonist exclusion.** Kirk Cousins's real 2013 and 2014 lines are the real post-divergence outcomes of a real person. They are excluded from the 2013 and 2014 populations entirely (`EXCLUDE_POST_DIVERGENCE` in the script: not a qualifier row, not a pair, not a reliability input) and are not quoted anywhere in this study, not for his value and not as a comparison. His 2012 Washington line is a pre-divergence public record and is used (section 6).

## 3. Method, fixed before the first run

Written into the script's `PREREGISTERED` block before it was run.

- **Dropbacks** = pass attempts + sacks suffered, two-point tries excluded, spikes counted as attempts (the production evidence file's definition). **Interceptions** = `passing_interceptions`.
- **Qualifier:** 200 dropbacks in each season of a pair (the production file's QB minimum).
- **Outcome:** the season t+1 raw interception rate, weighted by t+1 dropbacks (the punter test's shape: next raw metric, weight the next denominator).
- **Predictors:** (a) the season-t raw rate minus the season-t league mean (dropback-weighted over qualifiers); (b) the season-t shrunk rate minus that mean, shrunk = (n x raw + k x mean) / (n + k), the repository's shrinkage form. The punter test's two predictors were the tier and the shrunk deviation; a passer has no interception tier, so the raw deviation stands in for the first.
- **Reliability constant k**, per season t: signal variance = dropback-weighted variance of qualifier rates minus the dropback-weighted mean binomial variance p(1-p)/n, p the league mean; k = p(1-p) / signal variance. A non-positive signal variance means the qualifiers' spread is no wider than the binomial draw alone, k is infinite and the shrunk predictor collapses to the league mean.
- **Fit:** weighted least squares with intercept (the `wls` of the calibration scripts); shrinkage prior N(0, 1^2) on the dimensionless slope, as the punter's continuous term; leave-one-pair-out skill = 1 - (rmse / null rmse)^2 against the weighted league mean of the other pairs; Pearson correlation reported unweighted.
- **Keep rule:** a term has skill only with positive leave-one-pair-out skill and a positive slope (the phase-2 rule).
- **Populations:** 2010 to 2011 and 2011 to 2012 are the clean pre-divergence pairs; their pool is the headline; 2012 to 2013 and 2013 to 2014 are information only.
- **Verification:** every attempt, sack and interception count recomputed from the play-by-play file by gsis id, exact match required.

## 4. First pass (stats files)

Qualifiers per season: 2010 34, 2011 35, 2012 38, 2013 39, 2014 36 (the 2013 and 2014 counts are after the protagonist exclusion; no excluded line appears in any table, pair or reliability input). League mean interception rate per dropback over qualifiers: 2010 0.0261, 2011 0.0263, 2012 0.0242, 2013 0.0249 (without the excluded line), 2014 in the JSON.

### 4.1 Reliability (binomial-noise-corrected variance ratio)

| Season t | Qualifiers | League mean | Observed variance | Mean binomial variance | Signal variance | Signal SD | k | Reliability at mean dropbacks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2010 | 34 | 0.0261 | 8.92e-05 | 5.49e-05 | 3.43e-05 | 0.0059 | 740 | 0.38 (463 dropbacks) |
| 2011 | 35 | 0.0263 | 7.52e-05 | 5.50e-05 | 2.02e-05 | 0.0045 | 1,266 | 0.27 (466) |
| 2012 | 38 | 0.0242 | 4.48e-05 | 4.95e-05 | **-4.7e-06** | 0 | infinite | 0 |
| 2013 (population only) | 39 | 0.0249 | 8.22e-05 | 5.30e-05 | 2.93e-05 | 0.0054 | 830 | |
| 2010-2012 pooled (within-season deviations) | 107 | 0.0255 | 6.86e-05 | 5.29e-05 | 1.57e-05 | 0.0040 | **1,585** | 0.23 at 470 |

Read plainly: among passers who throw 200 or more times, the spread of interception rates in a season is mostly binomial noise. The pooled pre-divergence signal SD is 0.0040 per dropback (about 2 interceptions over 500 dropbacks), against a binomial SD of about 0.0073 at 470 dropbacks. In 2012 the 38 qualifiers were spread less than chance alone would spread them. The pooled k of 1,585 means a full 500-dropback season earns only 24% weight against the league mean.

### 4.2 Season pairs

| Pair | Population | n | Predictor | Correlation | Slope (SE) | Shrunk slope | Intercept | R^2 | LOO skill | Keep |
|---|---|---:|---|---:|---|---:|---:|---:|---:|---|
| 2010 to 2011 | pre-divergence | 23 | raw deviation | 0.008 | 0.016 (0.189) | 0.016 | 0.0251 | 0.000 | -0.060 | no |
| | | | shrunk deviation (k 740) | 0.037 | 0.097 (0.476) | 0.079 | 0.0252 | 0.002 | -0.061 | no |
| 2011 to 2012 | pre-divergence | 27 | raw deviation | 0.514 | 0.335 (0.125) | 0.330 | 0.0243 | 0.224 | 0.189 | yes |
| | | | shrunk deviation (k 1,266) | 0.516 | 1.338 (0.461) | 1.103 | 0.0244 | 0.252 | 0.213 | yes |
| **Pooled 2010-2012** | **pre-divergence** | **50** | **raw deviation** | **0.245** | **0.173 (0.111)** | **0.171** | 0.0247 | 0.048 | **0.028** | **yes, marginal** |
| | | | shrunk deviation | 0.210 | 0.471 (0.331) | 0.424 | 0.0248 | 0.040 | 0.011 | yes, marginal |
| 2012 to 2013 | post-divergence population, information only | 29 | raw deviation | 0.401 | 0.493 (0.257) | 0.462 | 0.0251 | 0.120 | 0.125 | (yes) |
| | | | shrunk deviation | degenerate: 2012 k infinite, predictor identically 0 | | | | | | (no) |
| 2013 to 2014 | post-divergence population, information only | 26 | raw deviation | -0.022 | 0.051 (0.148) | 0.050 | 0.0222 | 0.005 | -0.134 | (no) |
| | | | shrunk deviation (k 830) | 0.052 | 0.232 (0.388) | 0.202 | 0.0223 | 0.015 | -0.080 | (no) |

Next-season rate by prior-season third (dropback-weighted means; information only):

| Pair | Lowest third prior to next | Middle third | Highest third |
|---|---|---|---|
| 2010 to 2011 | 0.0133 to 0.0273 (7) | 0.0243 to 0.0205 (9) | 0.0359 to 0.0296 (7) |
| 2011 to 2012 | 0.0172 to 0.0217 (9) | 0.0251 to 0.0219 (9) | 0.0366 to 0.0294 (9) |
| Pooled 2010-2012 | 0.0154 to 0.0229 (16) | 0.0248 to 0.0240 (18) | 0.0364 to 0.0270 (16) |
| 2012 to 2013 (population) | 0.0154 to 0.0192 (9) | 0.0235 to 0.0254 (11) | 0.0296 to 0.0290 (9) |
| 2013 to 2014 (population) | 0.0143 to 0.0228 (8) | 0.0222 to 0.0195 (10) | 0.0355 to 0.0248 (8) |

Examples from the 2011 to 2012 pair, the one pair that carries the signal (pre-divergence public lines): Alex Smith 5 interceptions in 489 dropbacks then 5 in 242; Aaron Rodgers 6 in 537 then 8 in 603; Christian Ponder 13 in 321 then 12 in 515; Carson Palmer 16 in 345 then 14 in 591; John Skelton 14 in 298 then 9 in 216. The highest third of 2011 passers regressed from 0.0366 to 0.0294 and the lowest third rose from 0.0172 to 0.0217: the ordering held, at about a third of the prior gap.

## 5. Second pass (separate verification)

**Counts.** A second script, written separately from the first, read only the play-by-play files (never the stats files), rebuilt every passer's attempts, sacks and interceptions from `passer_player_id`, `play_type`, `sack`, `interception` and `two_point_attempt`, and formed the qualifier sets on its own. All five seasons: the qualifier sets are identical to the first pass (34, 35, 38, 39, 36) and every attempt, sack and interception count matches exactly (0 corrected rows; the JSON's `verification` block per season). No passer qualified on the play-by-play count and not on the stats file, or the reverse.

**Fits.** The second script recomputed every pair's weighted least squares with numpy's normal equations and its own leave-one-out loop. Every slope, intercept, standard error and leave-one-pair-out skill agrees with the first pass to the printed precision (nine decimals on the slope and skill). The second-pass script is `scripts/research/verify_passer_interception_persistence.py` (it needs numpy); the JSON holds the first pass. Reliability constants agree (740, 1,266, infinite, 830).

**Spot check against public summaries (October 2, 2026; search-result summaries, page fetches not attempted; pre-divergence lines only).** Mark Sanchez 2012: public 453 attempts, 18 interceptions; file 487 dropbacks (453 attempts + 34 sacks), 18 interceptions: confirmed. Carson Palmer 2011 (Oakland): public 328 attempts, 16 interceptions; file 345 dropbacks (328 + 17 sacks), 16: confirmed. Kirk Cousins 2012: public 33 of 48 for 466 yards, 4 touchdowns, 3 interceptions; file 48 attempts, 3 sacks, 3 interceptions, 466 yards: confirmed.

**Discrepancy found between passes:** none. **One finding about the method, recorded rather than fixed:** the shrunk predictor is undefined when a season's signal variance is non-positive (2012). The preregistered rule did not say what to do then; the script leaves the predictor at zero and the JSON records the fit as degenerate. The raw predictor is unaffected.

## 6. Kirk Cousins

**What may be used.** His pre-divergence record: 2012 Washington, 51 dropbacks (48 attempts, 3 sacks), 3 interceptions, public December 30, 2012. The branch's own record: the 2013 season from `career/2013/stats/season_totals.json` (564 attempts, 38 sacks, 602 dropbacks, 18 interceptions) and 2014 through Week 2 from `career/2014/05_Regular_Season/Statistics/records/season_totals.json` (69 attempts, 5 sacks, 74 dropbacks, 3 interceptions). His real 2013 and 2014 statistics are not used and not quoted.

**What the branch interceptions are evidence of.** The 2013 branch season ran on kernel 2013.x with Average anchors and no passer term; the two 2014 weeks ran on kernel 2014.4, whose interception channel has slope 0. In both, the interception draw never read who the passer was. Those 21 interceptions are therefore evidence of the draw, not of Cousins's ability. They are included below only because the coach asked for the combined estimate; the combined figure is a description of the record, not a measurement of the player.

**Shrunk estimate** under the pooled pre-divergence reliability (k 1,585, league mean 0.0255 per dropback), each line weighted by its dropbacks:

| Line | Dropbacks | Interceptions | Raw rate | Shrunk rate | Above league mean |
|---|---:|---:|---:|---:|---:|
| 2012 real, pre-divergence | 51 | 3 | 0.0588 | 0.0265 | +0.0010 |
| 2013 branch (no passer term in the draw) | 602 | 18 | 0.0299 | 0.0267 | +0.0012 |
| 2014 branch, Weeks 1-2 (slope 0) | 74 | 3 | 0.0405 | 0.0262 | +0.0007 |
| All three combined | 727 | 24 | 0.0330 | **0.0279** | **+0.0024** |
| Pre-divergence plus the 2014 weeks only | 125 | 6 | 0.0480 | 0.0271 | +0.0016 |

The combined record earns 31% weight against the league mean (727 / (727 + 1,585)). The shrunk estimate sits 0.0024 above the league mean, about 1.2 interceptions over a 500-dropback season, and well inside the pooled signal SD of 0.0040: nothing in the admissible record separates him from an ordinary passer on this metric.

**Binomial distance of the branch results from the league mean (0.0255):**

| Result | Expected | Binomial SD | z | Probability of at least this many |
|---|---:|---:|---:|---:|
| 3 in 74 (2014, Weeks 1-2) | 1.89 | 1.36 | +0.82 | 0.29 |
| 18 in 602 (2013 season) | 15.34 | 3.87 | +0.69 | 0.28 |
| 3 in 51 (2012 real, for reference) | 1.30 | 1.13 | +1.51 | 0.14 |

Three interceptions in 74 dropbacks is a result a league-average passer produces about three times in ten; eighteen in a season of 602 dropbacks, about three times in ten. Neither is unusual. The branch's own league drew 0.0255 interceptions per dropback in 2013 (492 in 19,301) and 0.0252 through 2014 Week 2 (61 in 2,423), both in line with the real 2010-2012 means, so the draw is not running high either.

## 7. Conclusion, stated plainly

1. **A pre-divergence passer term with real but weak skill exists under the punter's test, and it rests on one of the two pairs.** Pooled 2010 to 2012, 50 pairs: slope 0.173 on the raw deviation (SE 0.111, correlation 0.245), leave-one-pair-out skill 0.028, positive and of the right sign, so it passes the phase-2 keep rule. That is the same order as the punter's 0.039. But 2010 to 2011 shows nothing (correlation 0.008, skill -0.060) while 2011 to 2012 shows a lot (correlation 0.514, skill 0.189, slope 0.335 with SE 0.125). A term that passes on one pair and fails on the other is fragile at this sample size, and 2012 itself had less spread among its passers than binomial noise.
2. **The post-divergence league population, for information only, repeats the pattern:** 2012 to 2013 carries skill (0.125) and 2013 to 2014 none (-0.134). Across the four pairs, two show persistence and two show none.
3. **Implied slope under the repository's shrinkage convention.** If adopted as the punter term was (continuous predictor, shrunk deviation, prior N(0, 1)): slope 0.424 per unit of shrunk deviation (pooled, LOO skill 0.011), or, on the raw deviation, 0.171 (LOO skill 0.028; the raw predictor has the higher skill and would be adopted by the phase-2 tie rule). Implied passer SD in rate terms: 0.171 x 0.0096 (pooled raw-deviation SD) = 0.0016 interceptions per dropback, or 0.424 x 0.0032 = 0.0013 with the shrunk predictor. At the 2012 study's 3.13 dropbacks per drive (18,957 dropbacks over 6,053 drives), that is about 0.004 to 0.005 of per-drive interception share, against the dropped passing-composite term's implied club SD of 0.0029 per drive (which had no skill at all). A passer term of this size would move a 500-dropback season by about 0.8 interceptions per SD of passer: real, small and hard to see in one season.
4. **For the coach's quarterback:** nothing admissible places Cousins above or below the league on interception rate. His pre-divergence line is 51 dropbacks. The branch interceptions were drawn without reference to him. The combined shrunk estimate is 0.0279 against 0.0255, and his two branch results are within one binomial SD of the league mean.

## 8. What adopting a term would require

- **A user decision.** This study changes nothing. A passer interception term is a result-changing kernel change under `runtime/2014_engine_decisions.md` E1 and the defect register's release process: preregister the rule, fit on 2012 as the other phase-2 terms were, pass the acceptance gates (label swap, direction check, no future evidence), publish the term on every receipt, and release it as a new kernel version from merged `main` with live verification.
- **The evidence base would be the pre-divergence pairs only** (50 pairs, one of which carries the signal). The 2013 and 2014 populations may not inform the slope; they are shown here for information.
- **The predictor would need a pre-divergence line per passer.** A passer's admissible deviation would come from his 2011 and 2012 rates under the production file's public-date gate, shrunk with k 1,585 (or a preregistered alternative). A passer without 200 pre-divergence dropbacks, which includes Cousins (51), would carry a deviation of nearly zero: the term would move his draw by about a tenth of an interception per season.
- **No retroactive rerun.** Closed games stay closed. The 2013 season and 2014 Weeks 1 and 2 were drawn under slope 0 and remain so; a term would apply from its release forward, never to a closed result (Document 1 section 9.1 and the migration rules in AGENTS.md).
- **Honest expectation.** With a signal SD of 0.004 per dropback, the kernel would still draw almost all of any passer's interception variation from chance. Adopting the term would make the league's interception draw a little more faithful; it would not explain, and could not have prevented, 3 in 74.

## 9. Limits

- 50 pre-divergence pairs, 23 and 27; the keep rule is mechanical but the result depends on which pair is in the sample.
- Interception rate per dropback mixes the passer with his receivers, protection, play-calling and game script. The persistence measured here is persistence of the whole line, not of the passer alone.
- The shrunk predictor is undefined when a season's signal variance is non-positive (2012); recorded in section 5.
- Public spot checks are search-result summaries, not page fetches.
- The study was not blind: the coach's question arrived with his branch results known. The rule was still fixed before any pair was fitted, and nothing in it reads a branch record.
