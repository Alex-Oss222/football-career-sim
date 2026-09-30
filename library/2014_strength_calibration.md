# 2014 unit-strength calibration from public honours (E1 first pass)

**Research date:** September 29, 2026. **Kernel target:** 2014.4, defect register item 1 (every club has the same strength). **Status:** research and data. The 2014.4 candidate's `runtime/strength.py` reads it (see Section 8); the installed kernel is still 2014.3 until release. **Policy:** `runtime/2014_engine_decisions.md` E1 and the user's first-pass choice "Honours + role": pre-2013 public expert honours may move a player above Average; 2012 depth/role marks experience and job only; everyone else stays Average and low-confidence; Jacksonville is held to the identical rule; nothing is inferred from the branch's 2013 records; the effect size comes from real pre-divergence aggregates, never from a Jacksonville record.

Machine record: [`data/2014_strength_calibration.json`](data/2014_strength_calibration.json), built by `scripts/research/build_2014_strength_calibration.py` (sources and sha256 in the JSON). Evidence: [2010-2012 honours evidence](2010_2012_honours_evidence.md).

## 1. Rule fixed before fitting

The following was written into the script's `PREREGISTERED` block before the first fit ran, and was not changed after results were seen.

- **Window:** the two most recent completed pre-divergence seasons. 2012 calibration target: 2010-2011 honours. 2014 branch season: 2011-2012 honours (the 2013 real season is post-divergence and never used).
- **Tiers:** any AP All-Pro 1st team in the window -> **Elite**; AP 2nd team or an **original** Pro Bowl selection -> **Plus**; everyone else -> **Average** (low-confidence fallback meaning insufficient knowledge, not verified average ability).
- **Alternates/replacements: no effect.** They are chosen from a pool truncated by withdrawals and Super Bowl participation, their announcement dates are not pinned, and the 2012-season replacements may post-date the divergence.
- **Specialists:** K/P/KR/PR/LS/special-teamer honours are special-teams evidence only and never enter the offense/defense composites. They are listed but not fitted (the installed kernel does not read `special_teams_anchor`).
- **Values:** Elite 4, Plus 3, Average 2 (the existing `runtime/anchors.py` tier conversion). Player value = max over admissible honours of (tier value - 2) x evidence weight; evidence weight 1 for Confirmed two-pass, **0.5 for Single-pass**. So a single-pass Elite honour counts the same as a two-pass Plus.
- **Position weights (a priori):** QB 3, every other offensive starter 1, every defensive starter 1. Unit composite = sum of position weight x player value over the unit.
- **Role source (primary):** each club's 2012 Week 1 regular-season depth chart (nflverse `depth_charts_2012.csv`, depth_team 1, formation Offense/Defense). This is a published pre-game role document, used for job only. **Sensitivity:** every player on the Week 1 active weekly roster, grouped by position, at most one QB (the highest value).
- **Targets:** each club's 2012 regular-season per-drive touchdown share and points per drive, for its offense and allowed by its defense (nflverse play-by-play, `fixed_drive_result`; points = the possession team's score change over the drive). 6,053 drives; league TD share .195, points per drive 1.77.
- **Fit:** one slope per side, drive-weighted least squares over the 32 clubs with an intercept; shrinkage prior N(0, 0.025^2) per composite unit (the installed kernel's per-tier edge) declared in advance; leave-one-club-out prediction; drive-level joint check (offense composite, opposing defense composite, home) with a 500-draw game-cluster bootstrap, seed 20140401.

## 2. Results (2012 target, 2010-2011 honours)

111 starter slots across the league carry an above-Average tier (38 Elite and 48 Plus two-pass; 1 Elite and 24 Plus single-pass). Seventeen honoured players were not Week 1 starters in 2012 (for example Adrian Peterson, Maurice Jones-Drew, Jason Peters, Terrell Suggs) and do not count in the primary variant.

Slopes are per composite unit (one two-pass Plus non-QB starter = 1 unit; a two-pass Elite QB = 6). Defense slopes are reported as strength: a positive number lowers the rate allowed.

| Fit | Slope | SE | R^2 | Leave-one-club-out skill | Composite SD / max |
|---|---:|---:|---:|---:|---|
| Offense TD share | 0.0091 | 0.0030 | 0.24 | 0.18 (RMSE 0.0496 vs null 0.0548) | 2.91 / 14 |
| Defense TD share allowed | 0.0065 | 0.0036 | 0.10 | 0.06 (RMSE 0.0359 vs null 0.0370) | 1.75 / 7.5 |
| Offense points/drive | 0.0633 | 0.0216 | 0.22 | 0.17 (RMSE 0.3623 vs null 0.3968) | 2.91 / 14 |
| Defense points/drive allowed | 0.0508 | 0.0275 | 0.10 | 0.06 (RMSE 0.2722 vs null 0.2812) | 1.75 / 7.5 |

- **Shrunk (prior N(0, .025^2)) TD-share slopes:** offense **0.0090 +/- 0.0029**, defense **0.0064 +/- 0.0036**. The prior barely moves them because the data SE is far smaller than the prior SD.
- **Drive-level joint check** (opponent-adjusted, game-cluster bootstrap): offense 0.0089 (SE 0.0018), defense 0.0062 (SE 0.0028); points per drive offense 0.062 (0.012), defense 0.048 (0.020). Consistent with the club-level fit.
- **Sensitivity (whole Week 1 active roster):** offense 0.0102 (SE 0.0032), defense 0.0072 (SE 0.0034); leave-one-out skill 0.20 / 0.09.
- **Influence:** dropping any one club moves the offense slope between 0.0067 (without NE) and 0.0100 (without WAS); defense between 0.0052 (without CHI) and 0.0075 (without NYG). New England's 2012 offense (composite 14) is the most influential point.
- **Temporal out-of-sample check (2011 season, 2010 honours only, 2011 Week 1 depth charts).** Only one prior season exists in the evidence, so this is a one-season window and its composites are sparser than the rule's two-season window. Correlation of composite with TD share: offense 0.51, defense -0.31 (correct sign: more defensive honours, fewer TDs allowed). Applying the 2012 slopes to 2011 composites reduces centred RMSE from 0.0649 to 0.0575 (offense) and 0.0440 to 0.0420 (defense). A 2011-only fit gives offense 0.0149 (SE 0.0046), defense 0.0083 (SE 0.0048); the larger per-unit slope fits a sparser composite. No 2013 real season was used for any check.

**Reading.** Honours carry real signal, clearly for offense (driven substantially by quarterbacks) and weakly for defense (the defense slope is under two standard errors from zero in the club-level fit, about 2.2 SE in the drive-level fit). They explain roughly a quarter of the observed offensive club spread and a tenth of the defensive spread.

## 3. What the fitted effect implies for the kernel

**Target.** From the same 2012 drives: offense TD-share SD observed 0.0539, binomial noise 0.0289, implied true 0.0455; defense 0.0364 / 0.0288 / 0.0223. Combined true edge SD about 0.051 (the brief's .048), offense:defense variance about 4:1.

| Quantity (shrunk slopes, 2012 composites) | Value | Target |
|---|---:|---:|
| Club offense strength SD (TD share) | 0.0260 | 0.0455 |
| Club defense strength SD | 0.0112 | 0.0223 |
| Implied edge SD | **0.0284** | **.048** |
| Offense:defense variance | 5.4:1 | about 4:1 |
| Matchup edge SD over the real 2012 schedule | 0.0283 | - |
| Largest |edge| incl. the 0.008 home term (centred) | 0.117 | clamp .06 |
| Team-games beyond the +/-.06 clamp (centred / uncentred) | 3.7% / 5.5% | - |

The honours composite produces an edge SD of about **0.028, 59% of the .048 target** (about 31% of the true between-club variance). This is reported, not corrected. The composite is sparse: 19 of 32 2012 offenses and 21 of 32 defenses have composite 2 or less, and 6 offenses have none. Inflating the slope to hit .048 would give a few honoured units false precision while leaving the unmeasured two-thirds of variance unexplained, so it was not done.

**Anchor scale.** The installed `_edge` is (off_anchor - def_anchor) x 0.025 and uses one coefficient for both sides. The fit needs different per-side scales:

- Equivalent anchors: off_anchor = 2 + 0.358 x (C_off - mean C_off); def_anchor = 2 + 0.256 x (C_def - mean C_def). Over 2012 this spans offense 1.03 to 6.04 and defense 1.44 to 3.36: outside the 0-4 tier scale, because a unit sum is not a tier.
- Cleaner: a new per-side coefficient on the composite itself, edge = 0.0090 x dC_off - 0.0064 x dC_def (+ home), with d = deviation from the league-mean composite of the same season. This keeps the anchor/tier vocabulary for players and puts the fitted number in one place.

**Centring matters.** 2012 league-mean composites are 2.70 (offense) and 2.20 (defense). Uncentred, every honour only adds, the mean edge is +0.010 TD share per drive, and league scoring would drift above the 2012 drive model. Centred, the league mean stays on the calibrated mix, but clubs with no honoured starters sit **below** the league mean (for example -0.024 for an offense with none). That is what the regression says a no-honours unit's expected result is, but it also means the Average fallback no longer equals league average. A human must choose (Section 6).

**The +/-0.06 clamp binds.** Centred, New England's 2012 offense alone is +0.101; 3.7% of 2012 team-games would be clipped. In the 2014 preview Denver's offense alone is +0.064. The map's recommended log-odds tilt removes the need for a hard clamp; otherwise the clamp should be widened or the edge compressed, which is a design decision.

## 4. Home term (observation only, not part of item 1)

Real 2012: home margin +2.43 points per game (SD 15.67, n=256), home win rate 0.570; per-drive TD share home 0.206 vs away 0.183; points per drive 1.85 vs 1.69. The drive-level joint fit gives a home TD-share term of 0.0227 (SE 0.0102) against the kernel's 0.008 (about +0.6 points per game). Left unchanged here.

## 5. 2014 branch preview (data only)

Rule applied to 2011-2012 honours and the branch's player database (`career/2014/offseason/league_rails/league_players.json`, as of 2014-02-02; `inventory_club`). Jacksonville's 61 controlled players (53 plus 8 practice squad, matching `career/2013/roster.md`) are scored exactly like every other club. **No 2014 depth chart exists yet**, so the preview uses the sensitivity role rule (whole roster, one QB): it shows who carries evidence, not who will play. The kernel must compose from the actual available lineup (E1). Edge parts use the 2012 shrunk slopes, centred on the 2014 league means (offense 2.83, defense 2.19); resulting club SDs 0.0203 (offense) and 0.0140 (defense).

Tier marks: E = Elite, P = Plus, ½ = single-pass evidence (half weight). "Special teams only" players carry a specialist honour and are not in the composites (Patrick Peterson carries both).

| Club | Roster | With evidence | Average fallback | Off comp | Def comp | Off edge part | Def edge part | Tiered offense | Tiered defense | Special teams only |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| ARI | 61 | 4 | 57 | 1 | 1.5 | -0.016 | -0.004 | Larry Fitzgerald (P) | Daryl Washington (P); Patrick Peterson (P½) | Lorenzo Alexander (P½); Patrick Peterson (E) |
| ATL | 62 | 3 | 59 | 4 | 0 | +0.010 | -0.014 | Tony Gonzalez (E); Julio Jones (P½); Matt Ryan (P½) | - | - |
| BAL | 56 | 8 | 48 | 4 | 4.5 | +0.010 | +0.015 | Vonta Leach (E); Marshal Yanda (P); Ray Rice (P) | Terrell Suggs (E); Haloti Ngata (E); Elvis Dumervil (P½) | Jacoby Jones (E); Corey Graham (P½) |
| BUF | 59 | 1 | 58 | 0 | 1 | -0.025 | -0.008 | - | Jairus Byrd (P) | - |
| CAR | 61 | 2 | 59 | 1.5 | 0 | -0.012 | -0.014 | Steve Smith (P½); Ryan Kalil (P) | - | - |
| CHI | 65 | 10 | 55 | 3 | 6 | +0.002 | +0.024 | Brandon Marshall (E); Jermon Bushrod (P½); Matt Forte (P½) | Julius Peppers (P); Charles Tillman (E); Lance Briggs (P); Jay Ratliff (P½); Tim Jennings (P); Henry Melton (P½) | Devin Hester (P) |
| CIN | 64 | 2 | 62 | 1 | 2 | -0.016 | -0.001 | A.J. Green (P) | Geno Atkins (E) | - |
| CLE | 64 | 1 | 63 | 1 | 0 | -0.016 | -0.014 | Joe Thomas (E½) | - | - |
| DAL | 63 | 3 | 60 | 1.5 | 2 | -0.012 | -0.001 | Brian Waters (P½); Jason Witten (P) | DeMarcus Ware (E) | - |
| DEN | 57 | 5 | 52 | 10 | 3 | +0.064 | +0.005 | Wes Welker (E); Ryan Clady (E); Peyton Manning (E) | Champ Bailey (P); Von Miller (E) | - |
| DET | 61 | 3 | 58 | 2 | 1 | -0.007 | -0.008 | Calvin Johnson (E) | Ndamukong Suh (P) | David Akers (E) |
| GB | 65 | 4 | 61 | 6.5 | 1.5 | +0.033 | -0.004 | John Kuhn (P½); Aaron Rodgers (E) | B.J. Raji (P½); Clay Matthews (P) | - |
| HOU | 68 | 10 | 58 | 6.5 | 4 | +0.033 | +0.012 | Andre Johnson (P); Wade Smith (P½); Chris Myers (P½); Duane Brown (E); Arian Foster (P); Matt Schaub (P½) | Johnathan Joseph (P); Brian Cushing (P); J.J. Watt (E) | Shane Lechler (P½) |
| IND | 72 | 3 | 69 | 0.5 | 1 | -0.021 | -0.008 | Reggie Wayne (P½) | Robert Mathis (P½); LaRon Landry (P½) | - |
| JAX | 61 | 2 | 59 | 2 | 1 | -0.007 | -0.008 | Maurice Jones-Drew (E) | Jason Babin (P) | - |
| KC | 60 | 4 | 56 | 1 | 3.5 | -0.016 | +0.008 | Jamaal Charles (P) | Derrick Johnson (E); Tamba Hali (P); Eric Berry (P½) | - |
| MIA | 64 | 2 | 62 | 0.5 | 2 | -0.021 | -0.001 | Mike Wallace (P½) | Cameron Wake (E) | - |
| MIN | 63 | 6 | 57 | 3.5 | 3 | +0.006 | +0.005 | Greg Jennings (P½); Adrian Peterson (E); Jerome Felton (P) | Jared Allen (E); Chad Greenway (P) | Blair Walsh (E) |
| NE | 63 | 7 | 56 | 4.5 | 3 | +0.015 | +0.005 | Logan Mankins (P); Rob Gronkowski (E); Tom Brady (P½) | Andre Carter (P½); Vince Wilfork (E); Jerod Mayo (P½) | Matt Slater (P½) |
| NO | 64 | 4 | 60 | 5.5 | 0 | +0.024 | -0.014 | Jahri Evans (E); Jimmy Graham (P½); Drew Brees (P) | - | Thomas Morstead (P) |
| NYG | 65 | 5 | 60 | 3 | 2 | +0.002 | -0.001 | Chris Snee (P½); Victor Cruz (P); Eli Manning (P½) | Jason Pierre-Paul (E) | David Wilson (P) |
| NYJ | 65 | 4 | 61 | 1.5 | 1.5 | -0.012 | -0.004 | D'Brickashaw Ferguson (P½); Nick Mangold (P) | Ed Reed (P); Antonio Cromartie (P½) | - |
| OAK | 60 | 2 | 58 | 0 | 2 | -0.025 | -0.001 | - | Charles Woodson (E) | Sebastian Janikowski (P) |
| PHI | 59 | 2 | 57 | 3 | 0 | +0.002 | -0.014 | Jason Peters (E½); LeSean McCoy (E) | - | - |
| PIT | 64 | 5 | 59 | 5.5 | 2 | +0.024 | -0.001 | Heath Miller (P½); Maurkice Pouncey (E); Ben Roethlisberger (P) | Troy Polamalu (E) | Antonio Brown (P½) |
| SD | 61 | 4 | 57 | 3.5 | 2.5 | +0.006 | +0.002 | Antonio Gates (P½); Philip Rivers (P) | Dwight Freeney (P½); Eric Weddle (E) | - |
| SEA | 60 | 5 | 55 | 4.5 | 4 | +0.015 | +0.012 | Marshawn Lynch (E); Max Unger (E); Russell Okung (P½) | Earl Thomas (E); Richard Sherman (E) | - |
| SF | 60 | 12 | 48 | 3.5 | 10.5 | +0.006 | +0.053 | Frank Gore (P½); Joe Staley (P); Mike Iupati (E) | Justin Smith (E); Carlos Rogers (P); Donte Whitner (P½); Ahmad Brooks (P); Patrick Willis (E); Navorro Bowman (E); Aldon Smith (E) | Phil Dawson (P); Andy Lee (E) |
| STL | 61 | 2 | 59 | 1.5 | 0 | -0.012 | -0.014 | Scott Wells (P); Jake Long (P½) | - | - |
| TB | 67 | 5 | 62 | 2 | 4.5 | -0.007 | +0.015 | Davin Joseph (P); Carl Nicks (E½) | Darrelle Revis (E); Dashon Goldson (E); Gerald McCoy (P½) | - |
| TEN | 64 | 1 | 63 | 0 | 0 | -0.025 | -0.014 | - | - | Leon Washington (P½) |
| Unplaced (no club) | 204 | 1 | 203 | 0 | 1 | -0.025 | -0.008 | - | Ray Lewis (P) | - |
| WAS | 65 | 4 | 61 | 3 | 1 | +0.002 | -0.008 | Trent Williams (P½); Alfred Morris (P); Robert Griffin (P½) | London Fletcher (P) | - |

**Coverage.** 135 of the 2,004 players on the 32 club inventories (6.7%) carry any honour evidence; the other 1,869 are Average low-confidence fallbacks. Composite contributors: 41 Elite and 37 Plus two-pass, 3 Elite and 39 Plus single-pass. 140 players hold an admissible 2011-2012 honour; four are not in the league database (Adrian Wilson, Brian Urlacher, Jeff Saturday, Richard Seymour) and Ray Lewis is in it unplaced. Jacksonville: Maurice Jones-Drew (Elite, 2011 AP 1st team) and Jason Babin (Plus, 2011 AP 2nd team); 59 fallbacks.

## 6. Decisions a human must make

1. **Centring.** Centre composites on the season's league mean (keeps league scoring on the 2012 drive model; no-honours units fall below average) or leave uncentred (Average = zero edge; league scoring rises about 1 pp TD share per drive unless the base mix is recalibrated).
2. **Clamp or tilt.** The +/-0.06 clamp binds (NE 2012, DEN 2014 preview). Widen it, compress the edge, or adopt the log-odds tilt.
3. **Per-side scale.** Adopt per-side coefficients (0.0090 offense / 0.0064 defense per composite unit) or per-side anchor scaling; the kernel's single 0.025 cannot express both.
4. **Accept the dispersion shortfall.** Honours reach about 0.028 of the .048 edge SD. Closing the gap needs more permitted evidence (for example dated 2012 play-by-play receipts, decision item 1 in the engine map), not a larger multiplier.
5. **Single-pass evidence.** 42 of the 120 2014 composite contributors rest on single-pass honours (mostly the 2012 Pro Bowl list). Commission the second pass, or accept half weight.
6. **Research-pass source keys** (A*, P*, R*, AP*, PB*) must be recovered so every receipt's locator resolves; the six announcement dates need a second pass.
7. **2014 roles.** The preview is roster-level. The kernel needs the 2014 depth library (register item at :86) or live lineups before these composites mean "on the field".
8. **Home term** (+0.023 per-drive TD share fitted vs 0.008 installed) stays separate unless you decide otherwise.

## 7. Limitations

- Honours are reputation-weighted expert judgements with position quotas and fan voting; they are coarse and sparse, and repeat-selection inertia can lag real decline. They measure no specific job dimension, so they cannot yet feed E1's protection/coverage/run composites separately.
- The fit is a linear probability model on 32 clubs; confidence intervals are wide for defense.
- The Week 1 depth chart is a pre-game public document and can differ from who actually played; it is used for role only.
- The composite ignores depth, availability during the season, and help/opportunity costs, all of which E1 requires the kernel to model.

## 8. Decisions taken (September 29, 2026) and candidate implementation

Recorded from the user's decisions on Section 6; implemented in `runtime/strength.py` (kernel 2014.4 candidate; runtime/README.md).

1. **Centring:** centred on the 2012 study composite means (offense 2.703125, defense 2.203125). A unit with no honoured starter sits below the centre.
2. **Clamp:** widened from +/-0.06 to +/-0.12; no log-odds tilt.
3. **Per-side scale:** offense 0.00895127316177478, defense 0.006409703179081172 per composite unit (the study's shrunk slopes). edge = b_off x (off_comp - c_off) - b_def x (def_comp - c_def) + home, where def_comp is the defending unit's composite.
4. **Dispersion shortfall:** accepted; nothing is inflated.
5. **Single-pass evidence:** half weight, as preregistered.
7. **Roles:** composites come from each drive's actual available lineup (the live roster after injuries and removals), not the roster-level preview.
8. **Home term:** 0.023 per drive for the home offense at a home venue, none at a neutral site (replaces 0.008).

Item 6 (research-pass source keys and announcement dates) remains open research work.

## 9. Second pass (September 30, 2026): honours + production, calibrated by the same method

**Why.** The first pass reached 59% of the target edge spread with 135 evidenced players and 19 of 32 offenses at composite 2 or less. The user's decision: no 2014 game is played until strength is built properly, with no real 2013 data, no Madden and no market totals; extend E1 with a second, dated, pre-divergence production stream, preregistered and calibrated by the study's own method. Evidence: [2010-2012 production evidence](2010_2012_production_evidence.md) (`data/2010_2012_production_evidence.json`, two-pass verified). Machine record of this section: [`data/2014_strength_calibration_v2.json`](data/2014_strength_calibration_v2.json), built by `scripts/research/build_2014_strength_calibration_v2.py`, which imports the first study's functions unchanged (2012 Week 1 depth-chart starters for role, drive-weighted least squares of club TD share on the composite, shrinkage prior N(0, 0.025^2), leave-one-club-out prediction, drive-level joint check with the 500-draw game-cluster bootstrap, seed 20140401).

### 9.1 Rule fixed before the second fit

Written into the script's `PREREGISTERED` block before the first fit ran.

- **Player value.** With an admissible honour, the larger of the honours value (as the first pass; never below 0) and the production value; without one, the production value, negative tiers included. Production value: the window tier mapped Elite 2, Plus 1, Average 0, Below-Average -1, Replacement-Level -2, times its evidence weight (1.0 for a season the play-by-play recomputation confirmed or corrected, 0.5 unverified); 0 with no qualifying window season.
- **Why the honour lifts and production can lower.** A production tier is a measured, two-pass verified, pre-divergence season outcome covering every qualifier, so it can place a player above or below Average on its own; an honour is an expert judgement that can only lift a player. Keeping the honour's lift protects an honoured player whose production is contaminated by his old unit, and lets production speak for the unhonoured majority. The fitted two-term alternative was declared a sensitivity in advance; the kernel adopts this rule whatever it says.
- **Correction recorded (September 30, 2026).** The first fit of the script implemented the rule as max(honours value, production value) with honours value 0 for an unhonoured player, which floored every unhonoured starter at 0 and let no Below-Average or Replacement-Level tier enter a composite, contradicting the declared tier values. A unit test on the runtime exposed it before any game or acceptance run; the rule was corrected as declared above and refitted. The floored first fit is kept in the JSON (`variants_floored_first_fit`) for the record: its combined offense LOO skill was 0.144 (worse than honours alone) and its net implied SD 0.0292.
- **Side rule.** A QB honour or QB production tier counts only in the passer slot (weight 3, unchanged); a non-QB honour or tier never counts there; an offensive tier counts only on offense and a defensive tier only on defense; offensive linemen carry no production tier (job evidence only) and contribute honours alone.
- **Window.** As the honours window (2012 target: 2010-2011; 2014 branch: 2011-2012), with the 2014 branch's discounted 2010 fallback from the production file.
- **Age shrink on stale honours.** Halve the honours value of a player whose only admissible honours come from the earlier window season and whose age on September 1 of the target season is at or above the group threshold (QB 35, RB 29, WR 31, TE 31, OL 32, DL 31, LB 31, DB 31), before the comparison with production, never on production. Kept only if the leave-one-club-out skill improves on both sides; otherwise reported and left out.
- **Attribution tilt source (register item 19).** From the 2012 regular season: each club's top-target player's share of club targets, top-carry player's share of club carries and top sack-getter's share of club sacks, grouped by that player's combined tier from the 2010-2011 window; factor = tier mean share / all-club mean share, clipped to [0.6, 1.6], the Average tier included so the 2012 tier mix reproduces the all-club mean the rank shapes were built on; a tier with fewer than 3 clubs takes the nearest populated tier's factor toward Average.

### 9.2 Results (2012 target)

Slopes per composite unit; defense as strength (a positive number lowers the rate allowed); implied club SD = shrunk slope x composite SD; target 0.0455 offense, 0.0223 defense, 0.048 net; points per team-game = SD x 7.0 x 11.8.

| Variant | Side | Slope | SE | Shrunk | Composite mean | Composite SD | Range | R^2 | LOO skill | Implied club SD | Of target | Points per game SD |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| honours only (first pass, recomputed) | offense | 0.0091 | 0.0030 | 0.0090 | 2.70 | 2.91 | 0 to 14 | 0.239 | 0.182 | 0.0260 | 57% | 2.15 |
| | defense | 0.0065 | 0.0036 | 0.0064 | 2.20 | 1.75 | 0 to 7.5 | 0.098 | 0.057 | 0.0112 | 50% | 0.93 |
| | net | | | | | | | | | 0.0284 | 59% | 2.34 |
| production only | offense | 0.0056 | 0.0016 | 0.0056 | 3.25 | 5.09 | -5 to 14 | 0.280 | 0.199 | 0.0283 | 62% | 2.34 |
| | defense | 0.0048 | 0.0027 | 0.0048 | 7.78 | 2.37 | 3 to 13 | 0.099 | 0.061 | 0.0113 | 51% | 0.93 |
| | net | | | | | | | | | 0.0305 | 64% | 2.52 |
| **combined (primary, adopted)** | offense | 0.0058 | 0.0016 | **0.0058** | **4.30** | 5.17 | -4 to 17 | 0.312 | 0.238 | 0.0299 | 66% | 2.47 |
| | defense | 0.0046 | 0.0026 | **0.0046** | **8.11** | 2.46 | 3 to 15 | 0.098 | 0.063 | 0.0113 | 51% | 0.93 |
| | net | | | | | | | | | **0.0320** | **67%** | **2.64** |
| combined + age shrink | offense | 0.0057 | 0.0016 | 0.0057 | 4.23 | 5.19 | -4 to 17 | 0.306 | 0.232 | 0.0296 | 65% | 2.45 |
| | defense | 0.0049 | 0.0026 | 0.0048 | 8.08 | 2.45 | 3 to 15 | 0.107 | 0.074 | 0.0118 | 53% | 0.97 |
| | net | | | | | | | | | 0.0319 | 66% | 2.63 |
| continuous production (sensitivity, added after the first fit was read, labelled) | offense | 0.0059 | 0.0017 | 0.0059 | 3.69 | 4.91 | -4.4 to 16.3 | 0.292 | 0.217 | 0.0290 | 64% | 2.39 |
| | defense | 0.0047 | 0.0028 | 0.0047 | 6.75 | 2.28 | 2.8 to 13.5 | 0.089 | 0.051 | 0.0107 | 48% | 0.88 |
| | net | | | | | | | | | 0.0309 | 64% | 2.55 |

Drive-level joint check (opponent-adjusted, game-cluster bootstrap), combined: offense 0.00565 (SE 0.00095), defense 0.00372 (SE 0.00192), home 0.0230; consistent with the club-level fit. Two-term sensitivity (honours composite and production composite as separate predictors): offense 0.0043 honours + 0.0039 production, R^2 0.308, LOO skill 0.166; defense 0.0053 + 0.0039, R^2 0.160, LOO skill 0.080. Both terms keep their sign, so neither stream is redundant; the preregistered combined rule beats the two-term fit out of sample on offense.

**Reading, stated plainly.** On offense the second stream is a real gain: leave-one-club-out skill 0.182 to 0.238, R^2 0.239 to 0.312, implied club SD 0.0260 to 0.0299 (57% to 66% of target), and the slope is now more than three standard errors from zero. On defense it is not: LOO skill 0.057 to 0.063 and the implied SD unchanged at 0.0113 (51%); the disruption index adds coverage but little fitted signal, and the defense slope stays under two standard errors from zero at the club level. Net implied edge SD 0.0284 to 0.0320 (59% to 67% of the 0.048 target; 2.34 to 2.64 points per team-game). Nothing was inflated to close the gap.

**Age shrink: not adopted.** With it, offense LOO skill 0.232 against 0.238 without; defense 0.074 against 0.063. The preregistered rule required both sides to improve, so the kernel reads no birth date. 13 2012 starters would have been shrunk (Peyton Manning, Andre Johnson, Reggie Wayne, Julius Peppers, James Harrison, John Abraham, Michael Turner, Steven Jackson, Jordan Gross, Robert Mathis, Brandon Lloyd, Nnamdi Asomugha, Quintin Mikell).

**Composite range (combined, 2012 starters).** Offense -4 (ARI) to 17 (NE); JAX -2.5, STL -2.5; defense 3 (CLE, SD) to 15 (SF). 2012 means 4.30 and 8.11 are the centres, so a unit with no evidence at all sits below both.

### 9.3 Attribution tilt (register item 19)

2012 club-season top shares by the top player's combined tier (2010-2011 window):

| Credit | All-club mean (SD) | Elite | Plus | Average | Below-Average / Replacement-Level |
|---|---|---|---|---|---|
| top receiver's share of club targets | 0.239 (0.054) | 0.245, 9 clubs, factor 1.025 | 0.269, 9 clubs, 1.122 | 0.217, 14 clubs, 0.905 | no club: 0.905 (filled from Average) |
| top rusher's share of club carries | 0.529 (0.127) | 0.549, 7 clubs, 1.038 | 0.507, 7 clubs, 0.958 | 0.530, 18 clubs, 1.002 | no club: 1.002 |
| top sack-getter's share of club sacks | 0.278 (0.081) | 0.299, 21 clubs, 1.074 | 0.271, 6 clubs, 0.974 | 0.200, 5 clubs, 0.720 | no club: 0.720 |

The tier dependence is weak and noisy at this sample (Plus above Elite for receivers; the rusher row is flat). The factors are used as sourced: `runtime/usage.tilt_map` multiplies a player's rank weight by his tier's factor when a target, carry or sack/pressure credit is attributed; the number of random draws is unchanged and the possession stream never reads it (`tests/test_strength.py`, `AttributionTiltTests`). Two band rows in `runtime/bands.py` watch the per team-game top shares. A team-game top share runs above a club-season one (the same player is not the top target every game), so the rows have their own sourced centres from the 2012 play-by-play, per team-game over 512 team-games: top receiver's share of club targets 0.294 (SD 0.069), top non-QB rusher's share of club carries 0.707 (SD 0.158); tolerance three SDs over the root of the sample's team-game count (`team_game_top_shares_2012` in the JSON, added when the first club-season centres read OUTSIDE on the closed 2013 cohorts, before any acceptance row was graded on them). The closed 2013 cohorts read WITHIN on both rows (`career/2013/stats/calibration_audit.md`, regenerated to render the rows; no receipt changed).

### 9.4 Coverage of 2014 starters

Starters are the kernel's slot rule applied to the inventory in `branch_week1_slot` order (an identity ordering, not a 2014 depth chart): 704 slots across 32 clubs, Jacksonville by the identical rule.

| Group | Starters | With honours (before) | With production | With either (after) |
|---|---:|---:|---:|---:|
| QB | 32 | 10 (31%) | 28 | 28 (88%) |
| RB | 32 | 9 (28%) | 24 | 24 (75%) |
| FB | 24 | 2 (8%) | 4 | 5 (21%) |
| WR | 72 | 10 (14%) | 50 | 50 (69%) |
| TE | 32 | 5 (16%) | 24 | 24 (75%) |
| OL | 160 | 23 (14%) | 0 (job evidence only) | 23 (14%) |
| DL | 128 | 12 (9%) | 111 | 111 (87%) |
| LB | 96 | 12 (13%) | 93 | 93 (97%) |
| DB | 128 | 17 (13%) | 113 | 113 (88%) |
| **All** | **704** | **100 (14.2%)** | 447 (63.5%) | **471 (66.9%)** |

By club (starters with either, of 22): HOU 18; CAR, CLE 17; BAL, CHI, NO, PIT, SEA, WAS 16; ARI, ATL, IND, KC, MIN, NE, NYG, SF, TEN 15; CIN, DAL, DEN, GB, MIA, OAK, SD, STL, TB 14; DET, PHI 13; BUF, NYJ 12; **JAX 10** (no honour in the inventory's Jacksonville starter slots; at roster level Maurice Jones-Drew and Jason Babin still carry honours). Roster level: 948 of 2,004 inventory players carry any evidence (135 with honours, 906 with production); 1,056 Average fallbacks, every one listed with its reason.

### 9.5 What this pass still cannot do

Offensive linemen remain honours-only; contamination is unmodelled; no protection, coverage or run split, depth, help or coaching tradeoff is modelled (open E1 work); the special-teams strength is carried but not read; the composite explains about 67% of the target edge spread and the defense fit is still weak. The cheap complements listed in the user's decision that are not in this pass: matchup sub-composites and special teams.
