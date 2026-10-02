# Kernel 2014.6 pre-build specification, written after the results it cites were seen

[Engine decisions](../runtime/2014_engine_decisions.md#kernel-20146-decisions-dated) · [Runtime README](../runtime/README.md) · [Defect register](../runtime/defect_register.md) · [Strength studies](2014_strength_calibration.md)

**What this is.** The fixed rules for every builder, fit, runtime mechanism and acceptance run of kernel 2014.6, frozen October 2, 2026 in batch B0, before any of them is built. The design phase had already computed and printed the results this file cites, so it is **not a blind preregistration**. The earlier cluster "preregistrations" are folded in under this name, with each rule chosen after a result was seen marked as such. What it fixes: the data window and the 2014 cut; the weighting rule and the structural filters; the raw-count thresholds; every selection rule a later batch uses; the graded or informational status of every new band row; fresh acceptance seed blocks.

**How it binds.**
- This file is never edited. `scripts/research/pre_build_specification.py` pins its sha256 and `tests/test_pre_build_specification.py` fails on any change. A rule change needs a new dated file and a recorded decision.
- Every 2014.6 artifact header records this file's sha256 (`python scripts/research/pre_build_specification.py` prints it).
- Rules here are definitions, edges, thresholds and procedures. Every fitted value, band centre and table entry is produced by a committed builder with a `--check` mode, never typed. A figure marked *indicative* is a design-phase reading, shown for disclosure only; the builder's value binds.
- The authority for the scope is the dated decision record ([Kernel 2014.6 decisions](../runtime/2014_engine_decisions.md#kernel-20146-decisions-dated)): U1(b), the player-state policy, the defaults U2 to U5 and U7, and the added live fourth-down decision (B9F). U6 is unanswered.
- The machine-readable block at the end repeats the constants and lists below. Where prose and block disagree, the block is the defect: the check script tests the block against itself, and a reviewer tests it against the prose.

## 1. Data window and the 2014 cut

- **Seasons:** NFL regular seasons 2010, 2011, 2012 and 2013, plus 2014 Weeks 1-4. Postseason rows are not part of the base.
- **2014 cut:** `season_type == REG`, `week <= 4` and `game_date <= 2014-09-29`. That is 61 games (16 + 16 + 16 + 13), 10,893 nflverse play-by-play rows and 10,852 nflscrapR rows. The cut is applied at fetch: only cut files are written (B2).
- **Information gate:** the base is usable in the branch from September 30, 2014 (`public_from`), after the September 29 Monday game became public. It is frozen at the first Week 5 event, Thursday, October 2, 2014 (Minnesota at Green Bay), and stays frozen for the rest of the 2014 season. Weeks 1-4 of 2014 stand as played on the 2012 base.
- **Refused at fetch and at load:** any season after 2014; any 2014 row after the cut; every `stats_player_reg_*` file (season aggregates: strength targets are recomputed from play-by-play, player-state lines come from weekly statistics and play-by-play); any path under `career/`; the Week 5 injury reports of October 1-3, 2014 (outside the games-through-September-29 window; the October 2-3 reports also postdate the first Week 5 kickoff; design item D5 dropped).
- **Column allowlists:** `players.csv` gsis_id, birth_date, draft fields, pff_id, pfr_id, and never rookie_season, last_season, status or years_of_experience; `draft_picks` season, round, pick, team, gsis_id, position, and never the career columns (to, allpro, probowls, seasons_started, av, statistics).
- **Positions** come from that season's own roster or weekly roster, never from the current player database.
- **Source pins:** nflverse play-by-play 2010-2012 equal the pins in `library/data/2010_2012_production_evidence.json`, 2013-2014 the pins in `library/data/passer_interception_persistence.json`; nflscrapR `reg_pbp_2012` equals the pin in `library/data/2012_nfl_field_position_model.json`. The other nflscrapR seasons carry the design-phase digests listed in the block; B2 verifies them and fails closed on a mismatch.
- **Post-divergence caveat:** 2013 and 2014 Weeks 1-4 are an anonymous post-divergence league population. They enter pooled fits only. No club's or player's own 2013-2014 rows ever set that same club's or player's value, and no per-club or per-player 2013-2014 outcome row is committed. Self-influence is reported as a distribution for every club and player alike, computed in `--check` and not stored.
- **Branch records:** no branch receipt, branch audit reading or branch result enters any fit, centre or weighting choice. Branch receipts were read in the design phase only to measure the installed kernel's own behaviour (defect evidence).

## 2. Weighting, structural filters and homogeneity

- **Weighting:** equal weight per event, pooled over seasons. The 2-season recency half-life was fitted and not adopted: paired difference -0.044 (SE 0.044, t -1.0) against natural pooling, flat from 1.5 to 10 (*indicative*). A fitted weighting parameter that fails its test is treated like any term without evidence. Artifacts store per-season integer counts so a weight table could be switched on later; that would also need weighted draws.
- **Structural filters (dated rule changes, handled by exclusion, never by weighting):**
  - kickoffs from 2011 (kickoff moved to the 35); the 2010 kicks from the 30 are excluded from kickoff pools and kick-return rates, and counted in the onside unit from the 30;
  - overtime from 2012 (modified sudden death in the regular season); the 88 overtime drives of 2010-2011 are excluded from the overtime pools and from the overtime and late drive-share centres alike;
  - safety free kicks from every season;
  - the 2014 points of emphasis only through B12 (R24), never through the pool mix alone;
  - the 2012 replacement-officials games (2012 Weeks 1-3) stay in, with the penalty sensitivity reported (*indicative* about 0.03 per team-game).
- **Homogeneity:** every rate carries a per-season drift test with its p value (likelihood-ratio or chi-square). The pooled rate is used whatever the test reads; drift is reported, because a recency weight would be a chosen parameter.
- **Source defects explained, not repaired by hand:** 2010_12_CAR_CLE play 3904 (a split drive, repaired by the source `drive` key) and 2013_05_SD_OAK (two field-goal attempts on one drive, counted in rates only).

## 3. Raw-count thresholds and collapse rules

Every threshold is applied to raw counts, never to weighted counts.

| Threshold | Value | Use |
|---|---|---|
| `MIN_CELL` | 30 | drive cells (late, `h1_late`, overtime, neutral ladders) |
| `MIN_TIMEOUT_POOL` | 30 | a timeout level is used only when the pool holds this many matching tuples |
| `k_transition` | 20 | transition pools (kickoffs, free kicks, punts, interceptions, fumbles) |
| two-point chart minimum | 20 | tries per (time, diff) cell |
| player-state minimum cell | 30 | events per fitted cell (amendment 3) |
| climatology minimum | 5 | games per venue-month cell; fewer uses the venue's all-season mean plus the league month offset (a labelled convention) |

Collapse rules:
- **Late cells:** a thin late cell merges into the adjacent later time bucket; a thin `le120` bucket merges into the adjacent earlier one; repeated. Need is never merged.
- **`h1_late`:** the existing first-half rule applied to the new buckets: a thin bucket merges into the next larger bucket, the largest into the next smaller.
- **Two-point chart (amendment A1, made after the preregistered collapse was printed):** Q1-Q3 is one cell per diff and never merges with the fourth quarter. Within the fourth quarter, scanning from the last bucket back, a thin group merges with the adjacent earlier group of the same diff (the earliest, 900-601, with the next later one), repeated until no group is thin or one group is left. A cell still thin after that is used as counted and flagged. Diff is never merged. Minimum cell and bucket edges are unchanged and no target rate was used.

## 4. Selection rules, by batch

### End of half and late game (B3a partition, B5, B6)

- **R17a seconds:** drive seconds come from the first row of the drive group carrying `drive_time_of_possession`; accepted when 0 <= TOP - e <= 45, with e the game-clock time elapsed from first snap to terminal snap; otherwise seconds = e + that group's own median (interior, first-half clock expiry, end-of-game clock). The pooled `clock_scale` is recomputed from the corrected sums and each season's own scale is stored.
- **Partition (schema 3):** neutral is over 600 s; `h1_late` is first half at or under 600 s, keyed 0-30 / 31-60 / 61-120 / 121-240 / 241-600; late is the second half at or under 600 s, three time bins (`le120`, `121-300`, `301-600`) by the eight needs below; overtime is `ot_first` (2012-2014 opening possessions) and `ot_sudden` (later tied possessions). The `h1_final` pools are retired on the 2014.6 path and kept only under `PROFILE_2014_5`.
- **Needs (R10 edges, offense points minus defense points):** lead9 9 or more; lead1_8 1 to 8; tied 0; trail1_3 -1 to -3; trail4_8 -4 to -8; trail9_11 -9 to -11; trail12_16 -12 to -16; trail17p -17 or less.
- **R17 time match:** a first-half possession with window w at or under 600 s draws from `h1_late` tuples whose own start time is within 40 s of w; otherwise within 80 s (an engineering fallback, counted); then the bucket cell, the union, `_clock_fallback` and `_fit_or_expire`. A real final must be time-feasible (s <= w <= s + 40); a non-final must fit (s < w), and fit draws use non-final tuples. Over 600 s there is no redirect: the fitting neutral draw is the primary path.
- **R7:** a clock tuple is feasible only if its end decision zone (own half 50-99, opponent 49-35, opponent 34-1) equals its real end zone, in every regime and in `_clock_fallback`. `ZERO_TUPLE` is exempt.
- **R10:** every late fallback (need union, late clock fallback, `_fit_or_expire`) masks each category whose count is zero in the time cell actually drawn.
- **R14:** `ot_first` when the overtime history is empty, `ot_sudden` otherwise. A trailing overtime offense uses the late trail1_3 cell at the overtime clock's own time label, with punt masked and its weight moved to downs (an inference: 0 punts in 6 real trailing drives); the exclusion passes through `_fit_or_expire`. **Spike rule:** a tuple with a spike is feasible only if w - own + (seconds from its last spike to its end) <= 148. 148 s is the pre-divergence maximum (2010_12_PHI_CHI, 2011_16_MIN_WAS); the builder's `--check` must reproduce it. Overtime timeout counts are marked Confirmed only with a rulebook citation found in two passes.
- **W5b:** every timeout-conditioned draw prefers tuples whose real clubs used no more timeouts than the branch clubs hold, inside `resample_drive` too. No category is masked by timeouts; `timeout_unavailable_kept` is counted for the drawn category only; the existing cap stays as a backstop.
- **W3 early field goal:** `early_fg_ok` holds when the drive ends its window; or, in regulation, the kick-snap clock (w - own + kick length) is at most 43 s; or, in overtime, the kick ends the game. 43 s is the pre-divergence maximum (2012_15_SF_NE; next 2013_13_OAK_DAL 38 s, 2012_13_NE_MIA 36 s), measured at the kick snap; the builder must reproduce it. Otherwise a field-goal tuple with `term_down < 4` must admit a fourth-down layout (`chain_feasible`); a closable last fallback admits the real down with a counted diagnostic.
- **W5a clock stamps (records only):** the *gap table* is the mean seconds between consecutive snaps by the previous play's kind (run, run out of bounds, completion, completion out of bounds, incompletion, sack, timeout, spike, kneel) in three clock contexts (normal; the fourth quarter from 5:00 to 2:00; inside 2:00 of a half), with the sack gap kept separately for 2010-2013 and 2014 Weeks 1-4 (the 2014 running clock after a sack outside two minutes) and selected by kernel version. The *kick-length table* is the mean seconds from the last scrimmage snap to the kick snap by kick (punt, field goal) and the last snap's kind. Both are built by B3a from pass 1 and checked against pass 2. Each gap is at least 1 s, except where a drive's own seconds are fewer than its gaps; a zero-play kick is stamped at its start; a timeout row is seated after a clock-running snap and never after a terminal snap; two-minute warnings appear in periods 2 and 4, in overtime (regular season, preseason and the postseason countdown) and in all four Pro Bowl quarters. Stamps allocate the real drive's own seconds and change no result.

### Scoring decisions (B3c, B9)

- **Try unit:** one decision per touchdown followed by a try, the first try snap after it (a nullified first attempt still shows the choice; a re-try is a change, not a second decision). Go = a two-point attempt from scrimmage; kick = an extra-point kick, including aborted kicks and fakes from kick formation. Touchdowns with no try are excluded and counted.
- **Two-point chart:** state = the try team's margin after the touchdown and before the try, and game seconds left. Time buckets Q1-Q3 (over 900 s), Q4 900-601, 600-301, 300-121, 120-0; diff buckets each integer from -15 to +15, then -16 or less and 16 or more; collapse by amendment A1 (section 3).
- **Two-point success:** one pooled rate over every two-point attempt from scrimmage not nullified. A split (season, pass or run, spot, offensive or non-offensive touchdown, the last 5:00, home, the team red-zone proxy) is adopted only if a likelihood-ratio test gives p < 0.01 pooled and the effect has the same sign in each pre-divergence season with at least 10 attempts per arm. The extra point is the drive model's single pair, referenced, not duplicated.
- **Onside unit:** every valid kickoff from the kicking team's own 35 (2011-2014) or own 30 (2010) whose description contains "onside"; safety free kicks reported apart and given no onside branch. State = kicking team margin after the try and game seconds left, half openers flagged. Time buckets Q1-Q3, Q4 900-301, 300-121, 120-0; diff buckets lead 1 or more, tied, trail 1-3, trail 4-8, trail 9-16, trail 17 or more. **Expected** = the kicking team trails in the fourth quarter with 300 s or less left; **surprise** = every other onside kick. Recovery = the kicking team has the next offensive snap, or `own_kickoff_recovery`, or scores on the kick; a re-kick after a nullifying penalty is the attempt. In overtime, library rule R4 applies to every kickoff before the receiving club's first possession, and the opening onside kick uses the "opening" chart cell (default 1B.8).
- **Non-offensive touchdowns (R15):** units are valid interceptions on scrimmage downs, lost scrimmage fumbles without an interception, punts, missed field goals (blocked included), non-onside kickoffs from the 35 (2011-2014) and safety free kicks. Line-of-scrimmage bins 1-20, 21-40, 41-60, 61-80, 81-99 are adopted for a rate only if a likelihood-ratio test across bins gives p < 0.01; otherwise one pooled rate. Records are feasibility-filtered: gross or air yards at most LOS + 9 and the side-aware spot identity; a fumble's spot is the fumbled snap's LOS minus that snap's ledger yards. Kick-return touchdown chains have an engineering cap of 8, failing closed.
- **Decision source:** Jacksonville's two-point and onside decisions come from Stone (U6, unanswered): a call-sheet block (`decisions.two_point`, `decisions.kickoff`), a live pause, or a dated delegation, with basis `policy:i`, `delegated:league` or a live answer; every other club and every autonomous run uses the league chart (basis `league`). Without a block or a pause path the controlled club's user-controlled inputs fail closed. Success odds are the same for every club.
- **Extraction amendments (disclosed):** A2, pass 1 treats a play as nullified only when its description says No Play; A3, pass 2 reads the text after REVERSED. as the play that counted.

### Ball security and penalties (B3b, B10, B11, B12)

- **Fumbles:** the per-drive fumble list (snap order, kind, outcome, forced, forcer and recoverer groups) is the single source of the lost-fumble terminal kind (R12 layer B). Kept fumbles are seated nearest the stored snap order, never on a terminal snap, a kneel or a spike. A muffer follows `muffer_role`: the club returner by a deterministic depth fallback, or a group draw from the return unit for "other". Retained kicks apply at their real frequency (kickoffs from 2011); overtime punts exclude retained records, counted, until a two-source rule amendment on muffs against return fumbles lands. Forcers, recoverers, muffers and foulers are group draws with an `attribution` field and are never player evidence.
- **Penalties (R11):** records are replayed with `decision_source: "replayed"`; accept or decline is the real record's, never a decision. Half-distance records are placed only where floor(spot / 2) equals their yards; kick-play events are classified by their position in the drive; foulers come from `slot_lineup` with `fouler_basis: "group_draw"`; team counters go to the fouling club; the penalty term enters every layout rung; a static relocation gate masks infeasible tuples on the possession stream. 2014 season tables are split by definition (Weeks 1-4 offense-charged counters; Week 5 on, each accepted foul charged to the fouling club) and combined penalty ranks are withheld. If R11 is held, the counter keeps the Bernoulli at the base's per-play factor with `randint(5, 10)` labelled unsourced, and B12 is held with it.
- **2014 emphasis (R24, U2 persists through Week 17):** the emphasis set is five type-sides, each with its exposure: defensive holding (dropbacks), illegal contact (dropbacks), offensive pass interference (dropbacks), illegal use of hands by the defense (snaps) and illegal use of hands by the offense (dropbacks). Dropbacks include no-play dropbacks. Accepted fouls only drive the weights; declined emphasis fouls ride with their drives. The target is each type-side's 2014 Weeks 1-4 rate per exposure. Each tuple's weight is the Poisson likelihood ratio, the product over types of rho^n x exp(-(rho - 1) x lambda x exposure), with rho fitted by fixed point (rho <- rho x target / weighted rate) until the largest relative error is at most 1e-6, on the adopted pool with equal weight per drive. The weights are precomputed per tuple in the artifact; the runtime recomputation must agree within 1e-12 relative. On for regular season and postseason, off for preseason and the Pro Bowl. **No completion tilt** (U2 as decided): completion follows the pooled base.

### Yardage (B3b, B13)

- **R16a:** each replayed drive keeps its own real rushing yards, passing yards, completions and sack losses (`losses_random=False` in every rung). The relocation delta d (the change in the drive's free yardage when its start spot moves) is split between the kinds: the runs take round(d x |R| / (|R| + |P|)), with R and P the real rushing and passing yards (half each when both are 0), all of d when the drive has no completion and none when it has no run. Within each kind d goes to the non-terminal snaps by the **gains-proportional rule**: for d > 0 each snap weighs max(gain - 3, 0) + 1; for d < 0 each weighs max(gain - 3, 0) and loses at most that much; largest-remainder rounding within those caps; whatever cannot be placed moves one yard at a time over the longest non-terminal snaps of the kind. The terminal snap is never changed. `other_yards` become R11 enforcement entries; if R11 is held they are spread as the installed kernel spreads them. Fixed completions bind every rung: pass yards are 0 when completions are 0, or a forced completion is counted. The rule was chosen by the review after the prototype comparison was seen (disclosed).
- **R16b:** each drive's real run values and completion values replace the uniform allocation; the terminal value stays on the terminal slot, and the other values are the real drive's own, their order shuffled on the existing snap-detail substream (the design prototype's rule). With R11 shipped, `other_yards` become R11 enforcement entries and never touch scrimmage values.
- **Placeholder draws:** the current gauss and randint draws are still taken under their exact current conditions (including `gauss_next`), so the possession stream is unchanged where no split applies.

### Context and conditions (B3d, B14)

- **Covariates:** indoor = roof dome or closed (an open retractable counts as outdoor); wind = outdoor mph, 0 indoor; cold = max(0, 50 - temp F) / 10 outdoor, 0 indoor; alt = a game at Denver's home venue; turf = surface not grass; precip = the feed's weather string mentions rain, snow, shower, drizzle, sleet, flurries or storm (report only, single source); tz_edge, alt_edge and body_edge as signed offense edges, 0 at neutral sites. An outdoor game without temperature or wind is dropped from every weather model, counted.
- **Forms:** field-goal make, logit on season fixed effects, distance and kicker fixed effects, refit with the kernel's distance model as an offset; punt gross, least squares on punts from `yardline_100 >= 55` with centres over that same population; kickoff touchback, logit on 2011 to 2014 Week 4 kickoffs from the 35, not onside, applied as a likelihood ratio on the kickoff record draw; drive touchdown share, logit with season, start-bin, home, offense club-season and defense club-season fixed effects, applied through the edge before the clamp (the 0.65/0.35 reallocation is unsourced and disclosed); interception rate, sack rate and passing-touchdown share are fitted and live only if kept by the rule; yards have no channel in the drive replay (report only). Pooled slopes only: no per-club or kicker fixed effect is stored.
- **Keep rule:** a term is kept if and only if (i) it has a preregistered sign, (ii) its full-sample estimate has that sign, (iii) its leave-one-stadium-out skill is positive (every stadium, neutral venues their own group, held out once with both models refit; log loss for binary, squared error for continuous), and (iv) the independent second pass reproduces (ii) and (iii). Kept terms on one outcome are refit jointly; a kept term whose joint sign flips is dropped (lower single skill first) and the rest refit. No shrinkage. A term with no preregistered sign is reported only. Altitude terms are at slope 0 (default 1B.2: the rule cannot test a one-venue term).
- **Centring:** a shift is slope x (x - mean x over the adopted base pool's events of that outcome), so the league mean stays on the base.
- **Inputs:** the default basis is static venue facts plus 2010-2013 climatology; the observed-weather flag is off and no 2014 file is read at runtime (default 1B.3). A retractable roof uses (1 - closed share) x the open-roof means. Prose states weather only when the basis is observed.
- **Plans and defensive calls:** the offense plan test (early-down neutral pass rate against drive touchdown share, first differences, leave-one-club-out) is reported only and cannot be adopted in 2014.6. Defensive records label each snap deterministically with the applicable row of Stone's structured sheet (default 1B.5); no drawn per-snap call and no outcome effect.

### Inputs and participation (B15)

- **DB families:** the chart slot first (LCB, RCB, CB, NB, NCB, NKL corner; SS, FS, S safety), then the contemporaneous 2014 weekly-roster label; never the nflverse depth-chart `position` or `players.csv`. The nickel is settled first, then the base four. The participation slot convention `SCRIMMAGE_SLOT_MIX` is unchanged (default 1B.4).
- **Background game-day units (R21):** the real Week 1 53 (the 2014 Week 1 weekly-roster statuses A01 and I01 only) is completed in the library; suspended players are added as available; Week 1 PUP, NFI and reserve players are not added (default 1B.14). Depth comes from a second pre-first-game chart, otherwise below all listed players, flagged and counted. The additions' availability uses only reports public before each game (a per-game cutoff, never later than the clock at freeze). Dressed = min(46, legal available); a club that cannot dress a legal 46 records a dated, 2014-legal background transaction under U7. Gated from 2014 Week 5: the Weeks 1-4 packages must rebuild unchanged.

### Credit concentration (B16; credit only)

- Within-group credit is a conditional logit over depth rank, capped at RB 3, WR 5, TE 3, DL 5, LB 4 and DB 5; prior-role bins on carry share 0.10 / 0.30 / 0.50, target share 0.05 / 0.12 / 0.20 and sack share 0.10 / 0.20, plus a no-role class; a sack position class (edge = DE and OLB); attribution tiers (Elite, Plus, Below-Average, Replacement-Level, none, against Average). The bins and caps were chosen after the leave-one-season-out results were seen (disclosed).
- Selection on 2011-2013, confirmed once on 2014 Weeks 1-4; the applied lag (two seasons for 2014) is the fit's lag; the no-evidence class is fitted leaving out the player's own draft class; missing cells (fullback, receiver and tight-end carries; fullback targets) are rank-only. The usage swing (R19b) is at sigma 0 (default 1B.11).

### Player states (B4b, B7)

- **Families and metrics:** QB EPA per dropback; RB, WR and TE EPA per opportunity; DL, LB and DB disruption per game (sacks + 0.5 QB hits + tackles for loss + interceptions + 0.5 passes defended, tackles for loss from the play-by-play in every season); K field goals made over expected per attempt; P net yards per punt; KR and PR yards per return. Offensive linemen have no public performance rate: no state (honours plus starts).
- **Fit floors:** QB 50 dropbacks; RB 30, WR 20, TE 15 opportunities; DL, LB and DB 4 games; K 10 attempts; P 20 punts; KR and PR 8 returns. The tier population is defined on the committed production-evidence qualifier floors.
- **Centring and noise:** each rate centred on its season's opportunity-weighted league mean over floor qualifiers; per-family-season noise variance from the within-season split-half moment.
- **Aging (amendments 2 and 3, U5):** fitted on one-step forecast residuals from the persistent-plus-AR(1) Kalman filter, not raw deltas. Candidates Z (no drift), C (constant), M1 (constant and a quadratic in age - 27), M2 (M1 and experience 0 and 1 indicators). A candidate is eligible only if it beats Z in both passes (pass 1 leave-one-season-pair-out SSE, pass 2 BIC); among eligible candidates the lowest pass 1 SSE is adopted; none eligible means Z.
- **Swing (C):** C_k = sb2 + rho^k su2 over lags 0-4, rho on a 0.01 grid, 200 bootstrap resamples of players. Kept only if su2's 95% interval excludes 0 in both passes. Size: pass 1 when pass 2's point estimate lies inside pass 1's interval (Confirmed two-pass), otherwise the smaller point estimate (Reconciled down, flagged). Innovation SD tau = sqrt(su2 (1 - rho^2)).
- **Draft-slot priors (B, U4):** first and second seasons above floor; drafted x = c0 + c1 log(overall pick), undrafted a separate intercept; each player's real selection slot or undrafted status for every club, Jacksonville-controlled players included; priors fitted leaving out the player's own draft class. The slope is kept only if kept in both passes and negative (an earlier pick predicts a higher rate; the sign rule was added after pass 1's tight-end result was seen).
- **Feedback (D):** role change and seasons missed, standardised and pooled over families; a term is kept only if its leave-one-club-out skill is positive with the declared sign (positive for role, negative for availability) in both passes; weight = pass 1's slope when pass 2's slope is within 2 pass-1 standard errors, otherwise the smaller magnitude, flagged; the predictor cap q is chosen from 0.5, 0.75, 0.9 and 1.0 by the same skill. Snaps carry weight 0 (no public outcome season). Role is at slope 0 for the 2015 transition until Stone decides (default 1B.13); availability applies from 2015; the feedback F is 0 in 2014.
- **Honours and record family:** honours enter as a pseudo-observation split by the Kalman gain, with `EVIDENCE_WEIGHT` 1.0 for Confirmed two-pass and 0.5 for Single-pass. The record family is the family holding most of the player's 2010-2012 opportunities (the latest season breaks ties), frozen at first entry, with the z-transfer applied at league-year transitions (default 1B.10).
- **Tolerances and checks:** 2 SE from their own n; the 2013-to-2014 Weeks 1-4 pair is held out of the fit; a 2014 row asserts week <= 4 and game date <= 2014-09-29; the punter curve takes pass 1's coefficients when pass 2 is within 2 SE, otherwise the smaller, labelled.
- **Boundary:** player-state values are hidden-state statistical priors for the engine only. They are never scouting evidence, never a staff-facing grade, and no staff assessment, grade or E2 advice reads them or their tiers.

### Strength v4 (B4c)

- **Targets (U1(b)):** 2012 outcomes with 2010-2011 evidence, plus 2013 outcomes with 2011-2012 evidence; club outcomes from play-by-play. Inputs are one-step-forecast E-values from the player-state model at each target's evidence cutoff.
- **Units:** DB units are the slot-family base four on contemporaneous labels (chart slot family, then that season's weekly roster position, never the back-filled depth-chart position).
- **Fit and keep rule:** pooled drive-weighted least squares with season intercepts, leave-one-club-out prediction and the shrinkage prior N(0, 0.025^2) per composite unit. A term is kept only if its leave-one-club-out skill is positive and its sign is right, reproduced by pass 2's independent nflscrapR classifier. The rule applies symmetrically (U3): a live term that fails goes to slope 0 (protection-to-sack may turn off) and a newly passing term becomes live (for example the unit passing-to-interception term). The individual passer interception term stays not adopted (October 2 decision).
- **Centres** are the target-set means of the E-value composites; `HOME_EDGE` is fitted by the drive-level joint regression; `PUNTER_SLOPE` is refit on the committed `pt_net_yards` definition with the 2013 pairs, pass 2 on the same definition, and if the passes still disagree the smaller is adopted, labelled single-pass; the punter's input stays his public pre-divergence net. Kicker and returner terms stay at 0. Only aggregate fits are committed.

## 5. Band rows: graded or informational

Centres and tolerances come from the builders' artifacts by the plan's tolerance formulas. "Graded" means a WITHIN or OUTSIDE reading for the 2014.6 cohort only; a new OUTSIDE row goes to the user (U8) and is never auto-registered.

| Batch | Graded | Informational |
|---|---|---|
| B5 | drive shares (touchdown, field-goal attempt, punt, turnover, downs, safety, clock); drives per team-game; FGA and FGM per team-game; drive-ending punts; clock-expired drives; offensive-drive turnovers; interception share of turnovers; FG accuracy by band and overall; kickoff touchback share; punt net by LOS bin; return means; sacks per dropback; volume rows (points, plays, net yards, first downs, third-down attempts and rate); first-half final FG share and clock share; P(final) for first-half starts 61-120 s and 121-240 s; the first-half start-window distribution; clock-expired first halves ending inside the 30; FG attempts inside 2:00 of Q4 trailing by 12 or more; defensive timeouts per second-half possession starting over 10:00; **timeouts per team-game**; overtime spikes over 148 s and trailing overtime punts (zero tolerance); injury rows by the 2014.4 method; usage shares; top receiver and rusher team-game shares | extra point (B5); FG attempts inside 2:00 trailing by 9-11 |
| B6 | `field_goal_before_fourth_down` (audit-only until the sweep reads 0, then zero tolerance) | `spike_outside_window`; `kick_clock_shared`, `snap_at_zero`, `timeout_rows_mismatch` and `two_minute_warning_missing` are audit-only until the sweep reads 0 |
| B9 | two-point attempt share; two-point conversion (at 30+ attempts); extra point (informational under B5, graded from B9); Q4 go share when down 2 and onside share trailing 1-8 inside 2:00 (on the 1,000-game block); onside kicks per team-game; expected onside recovery (at 30+); interception-return, fumble-return, punt return or block and kick-return touchdown shares | surprise onside recovery; blocked-FG touchdowns; non-offensive touchdowns per team-game; points per team-game (measured, no forecast) |
| B10 | fumbles per team-game; lost per team-game; offense-kept share of scrimmage fumbles; sack share of lost scrimmage fumbles; kicking-team recoveries per team-game; muffer role share | forced share; forcer also recovers; muffs per punt |
| B11 | accepted penalties per team-game; penalty yards per team-game; penalty first downs per team-game | defense share, declined, offsetting and kick-play penalties; net-yards shift (reported, never tuned) |
| B12 | non-emphasis drive fouls per team-game; drive categories, points and plays against the same build with weights 1 (the plan's 2014 completion row is not used: U2, no completion tilt) | emphasis fouls per team-game (a wiring check: it reproduces its target by construction); per type-side rates |
| B13 | yards per carry; completion rate (pooled base, U2); run share; rushing yards per team-game; shares of runs losing yards, of 20+ yards and of 1-3 yards; `layout_ok_flip` (0 expected, listed flips only) | completions of 20+ per attempt; per-snap rows on real cohorts (graded only on synthetic all-club samples) |
| B14 | the centring sample's FG accuracy and bands, touchback share, punt net bins and drive touchdown share | observed or climatology mix; mean applied shifts; the touchback and FG rates the recorded terms imply |
| B16 | season concentration rows only on 5 or more synthetic seasons with a removal-carrying harness | leader rows; the branch's labelled mixed-kernel detection |

## 6. Seed blocks

Fresh labels, never used before this file. Kernel entropy is derived from each label as the production runner derives it from an event reference, sha256(ENTROPY_DOMAIN + sha256(label)) with `ENTROPY_DOMAIN` from `runtime/game_runner.py`, and the label is the event id. A fixture or venue assignment may depend on the label's index only, never on an outcome, and no label is replaced after its result is seen.

| Block | Labels | Use |
|---|---|---|
| A1 acceptance | `acc-2014.6-0` to `acc-2014.6-999` | the 1,000-game block, strength records absent and present |
| A2 extended | `acc-2014.6-x0` to `acc-2014.6-x1999` | the 2,000-game block for the end-of-half rows |
| A6 sweep | `sweep-2014.6-<fixture>-0` to `-3999` for each of the three fixtures of `scripts/research/seed_sweep.py` | 12,000 autonomous games; 0 refused games |
| Latent references | `latref-0` to `latref-19` | 20 synthetic season references for the player-state draws (B7, A3) |

The standard 250-game sample is reported alongside, never as the gate for a new row.

## 7. Outside this file

- **B9F** (the live Jacksonville fourth-down decision) was added after these rules were drafted. Its rules are frozen in its own design record (runtime README and the decision record) before its code; they are not part of this file, so its digest does not change.
- **U6** (Stone's two-point and onside rule, or a dated delegation) is unanswered. The mechanism accepts either a live pause or a call-sheet decision block and fails closed for Jacksonville without one.
- **U8** (a graded row still OUTSIDE after acceptance) is the user's.
- Needed later, not decided here: authorization to update the rulebook's section 8 era note; the two AGENTS.md workflow lines (conditions built inside `build_week_inputs`; staff assessments never read player-state values or tiers); Week 1 PUP, NFI and reserve treatment; role feedback before 2015; observed weather; per-snap defensive calls.

## 8. Frozen rules (machine-readable)

<!-- frozen-rules:begin -->
```json
{
  "specification": "kernel-2014.6-pre-build-specification",
  "written": "2026-10-02",
  "blind": false,
  "data_window": {
    "seasons": [2010, 2011, 2012, 2013, 2014],
    "season_type": "REG",
    "cut_2014": {"max_week": 4, "max_game_date": "2014-09-29", "games": 61,
                 "games_by_week": [16, 16, 16, 13], "rows_nflverse": 10893, "rows_nflscrapr": 10852},
    "public_from": "2014-09-30",
    "frozen_at": {"date": "2014-10-02", "event": "first 2014 Week 5 event (Minnesota at Green Bay)"},
    "frozen_through": "the rest of the 2014 season",
    "refused": ["any season after 2014", "2014 rows after the cut", "stats_player_reg_*", "paths under career/",
                "2014 Week 5 injury reports (October 1-3, 2014)"],
    "players_columns": ["gsis_id", "birth_date", "draft fields", "pff_id", "pfr_id"],
    "draft_picks_columns": ["season", "round", "pick", "team", "gsis_id", "position"],
    "nflscrapr_reg_pbp_sha256": {
      "2010": "64224b82b8efc7b5c6d8c0c4e0054346bb1ac5df4c073c84d2ab8fb3e730f9da",
      "2011": "ba412141e8033103807810605ecdbdb5bf19d9dd683e1ff3173af1303fced12c",
      "2012": "9129396fc41597f9f44ab14d4d0fca890a3c56fea686b0b7dc92885aaedd0f98",
      "2013": "37b64a2510bf3da54430deaa0d3cbbdd8113d3be9ca4e1512d3cbf0d40320950",
      "2014": "f8d02fa4134bbe1ddd2a3cb789be4f6436d04fe2155aa197bc5b128dce52cdcb"
    }
  },
  "weighting": {"rule": "equal weight per event", "recency_half_life": null, "per_season_integer_counts": true},
  "structural_filters": {"kickoffs_from_season": 2011, "overtime_from_season": 2012,
                         "safety_free_kicks": "all seasons", "excluded_2010_2011_overtime_drives": 88,
                         "replacement_officials_2012_weeks_1_3": "kept, sensitivity reported"},
  "thresholds": {"MIN_CELL": 30, "MIN_TIMEOUT_POOL": 30, "K_TRANSITION": 20, "TWO_POINT_MIN_CELL": 20,
                 "PLAYER_STATE_MIN_CELL": 30, "CLIMATOLOGY_MIN_GAMES": 5},
  "end_of_half": {
    "NEUTRAL_OVER_SECONDS": 600,
    "H1_LATE_SECONDS": 600,
    "H1_LATE_EDGES": [[0, 30], [31, 60], [61, 120], [121, 240], [241, 600]],
    "LATE_TIME_BUCKETS": {"le120": [0, 120], "121-300": [121, 300], "301-600": [301, 600]},
    "NEEDS": {"lead9": [9, 999], "lead1_8": [1, 8], "tied": [0, 0], "trail1_3": [-3, -1], "trail4_8": [-8, -4],
              "trail9_11": [-11, -9], "trail12_16": [-16, -12], "trail17p": [-999, -17]},
    "TIME_MATCH_SECONDS": 40,
    "TIME_MATCH_FALLBACK_SECONDS": 80,
    "FINAL_FEASIBLE_SLACK_SECONDS": 40,
    "DECISION_ZONES": {"own_half": [50, 99], "opp_49_35": [35, 49], "opp_34_1": [1, 34]},
    "SPIKE_WINDOW": 148,
    "SPIKE_WINDOW_SOURCES": ["2010_12_PHI_CHI", "2011_16_MIN_WAS"],
    "EARLY_FG_SECONDS": 43,
    "EARLY_FG_SOURCE": "2012_15_SF_NE",
    "R17A_TOP_ACCEPT_SECONDS": [0, 45],
    "OVERTIME_CELLS": ["ot_first", "ot_sudden"],
    "W5A_GAP_KINDS": ["run", "run_oob", "complete", "complete_oob", "incomplete", "sack", "timeout", "spike", "kneel"],
    "W5A_CLOCK_CONTEXTS": ["normal", "q4_2_to_5_min", "inside_2_min"],
    "W5A_KICKS": ["punt", "field_goal"]
  },
  "scoring": {
    "two_point_time_buckets": ["Q1-Q3", "Q4 900-601", "Q4 600-301", "Q4 300-121", "Q4 120-0"],
    "two_point_diff_range": [-15, 15],
    "two_point_collapse": "A1: within the fourth quarter only; Q1-Q3 one cell per diff; diff never merged",
    "heterogeneity_keep": {"p_below": 0.01, "same_sign_each_pre_divergence_season": true, "min_attempts_per_arm": 10},
    "onside_kick_spot": {"2010": 30, "2011-2014": 35},
    "onside_time_buckets": ["Q1-Q3", "Q4 900-301", "Q4 300-121", "Q4 120-0"],
    "onside_diff_buckets": ["lead 1+", "tied", "trail 1-3", "trail 4-8", "trail 9-16", "trail 17+"],
    "onside_expected": "kicking team trails in Q4 with 300 s or less left",
    "return_td_los_bins": [[1, 20], [21, 40], [41, 60], [61, 80], [81, 99]],
    "return_td_bins_keep_p_below": 0.01,
    "kick_return_chain_cap": 8,
    "basis_values": ["policy:i", "delegated:league", "league"]
  },
  "emphasis_2014": {
    "persist_through_week": 17,
    "completion_tilt": false,
    "types": [["defense", "Defensive Holding", "dropbacks"],
              ["defense", "Illegal Contact", "dropbacks"],
              ["offense", "Offensive Pass Interference", "dropbacks"],
              ["defense", "Illegal Use of Hands", "snaps"],
              ["offense", "Illegal Use of Hands", "dropbacks"]],
    "accepted_only": true,
    "fixed_point_max_relative_error": 1e-6,
    "runtime_recompute_relative_tolerance": 1e-12,
    "game_types_on": ["regular", "postseason"],
    "game_types_off": ["preseason", "pro_bowl"]
  },
  "yardage": {
    "relocation_rule": "gains-proportional",
    "gain_threshold_yards": 3,
    "positive_delta_weight": "max(gain - 3, 0) + 1",
    "negative_delta_weight": "max(gain - 3, 0), also the per-snap removal cap",
    "kind_split": "runs take round(d * |R| / (|R| + |P|)); half each when both are 0",
    "rounding": "largest remainder",
    "terminal_snap_fixed": true,
    "value_replay": "real run and completion values, terminal value on the terminal slot, others shuffled on the snap-detail substream"
  },
  "context": {
    "cold_reference_f": 50,
    "cold_scale_f": 10,
    "punt_gross_min_yardline_100": 55,
    "keep_rule": "preregistered sign, full-sample sign, positive leave-one-stadium-out skill, pass-2 reproduction",
    "altitude_slope": 0,
    "default_basis": "climatology",
    "observed_weather": false
  },
  "credit_concentration": {
    "rank_caps": {"RB": 3, "WR": 5, "TE": 3, "DL": 5, "LB": 4, "DB": 5},
    "role_bins": {"carry": [0.10, 0.30, 0.50], "target": [0.05, 0.12, 0.20], "sack": [0.10, 0.20]},
    "edge_positions": ["DE", "OLB"],
    "tiers": ["Elite", "Plus", "Below-Average", "Replacement-Level", "none"],
    "selection_seasons": [2011, 2012, 2013],
    "usage_swing_sigma": 0
  },
  "player_state": {
    "fit_floors": {"QB": 50, "RB": 30, "WR": 20, "TE": 15, "DL": 4, "LB": 4, "DB": 4, "K": 10, "P": 20, "KR": 8, "PR": 8},
    "drift_candidates": ["Z", "C", "M1", "M2"],
    "age_centre": 27,
    "swing_lags": [0, 1, 2, 3, 4],
    "rho_grid_step": 0.01,
    "bootstrap_resamples": 200,
    "feedback_cap_quantiles": [0.5, 0.75, 0.9, 1.0],
    "feedback_slope_tolerance_se": 2,
    "evidence_weight": {"Confirmed two-pass": 1.0, "Single-pass": 0.5},
    "snap_feedback_weight": 0,
    "role_feedback_2015": 0,
    "feedback_in_2014": 0,
    "draft_slot": "real selection slot or undrafted, every club, own draft class left out"
  },
  "strength_v4": {
    "targets": [{"outcomes": 2012, "evidence": [2010, 2011]}, {"outcomes": 2013, "evidence": [2011, 2012]}],
    "prior_sd": 0.025,
    "keep_rule": "leave-one-club-out skill > 0 and right sign, reproduced in pass 2; symmetric",
    "kicker_slope": 0,
    "returner_slope": 0
  },
  "seeds": {
    "entropy": "sha256(ENTROPY_DOMAIN + sha256(label))",
    "acceptance": {"prefix": "acc-2014.6-", "count": 1000},
    "extended": {"prefix": "acc-2014.6-x", "count": 2000},
    "sweep": {"pattern": "sweep-2014.6-<fixture>-<i>", "per_fixture": 4000, "fixtures": 3, "games": 12000},
    "latent_references": {"prefix": "latref-", "count": 20}
  }
}
```
<!-- frozen-rules:end -->
