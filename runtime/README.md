# Football runtime

`game_runner.py` is the only production game entry point. It validates normalized roster-bound inputs, creates one canonical packet, closes that packet through the authenticated private service, domain-separates the returned opaque event reference into kernel entropy, invokes `kernel.py`, and rejects any result that fails kernel invariants. It has no caller-supplied seed parameter. Interactive and background names are aliases of this same runner; low-level `kernel.py` access exists only for synthetic calibration tests.

`player_evidence.py` supplies roster-aware participation, position-correct statistical attribution, sparse qualitative observations, and separate assignment, communication, processing, technique, physical execution, observable effort, correction, medical, teaching, and special-teams fields. Rotation status and actual football roles guide opportunity without hardcoded snap shares or roster-survival probabilities. `calibration.py`, `rules.py`, `injuries.py`, and `anchors.py` supply deterministic period inputs, medical events, and private evidence conversion. `packets.py` supplies `canonical()`, the canonical JSON encoding behind every packet digest (`game_runner.py`, `private_client.py`, `private_service.py`), plus a tested reference `Packet`/`resolve` journal-before-draw implementation (Document 7 §3.4, `tests/test_packets.py`) that is not on the production path.

`private_service.py` is the authenticated Engine State reference service. Its persistent volume and bearer credential stay outside the repository. The store seeds the career once, binds the current branch snapshot and kernel/schema identity, journals immutable event identifiers before closure, refuses altered packets, supports idempotent replay, records corrections append-only, and exercises a recovery digest during readiness. Event closure has one identity source: the canonical packet's `event_id`. Production `/events/close` is bodyless: the authenticated POST carries only URL-encoded `event_id` plus `packet_sha256`, where the digest is computed from canonical packet JSON locally. The private service journals that immutable identity and never needs packet contents. Older flat/wrapped JSON bodies remain compatibility-only paths and may never override packet identity. The current production write API is bodyless end-to-end: event closure, administrative canary, compare-and-swap snapshot advancement, and correction recording use authenticated POSTs whose validated inputs are URL-encoded where needed. JSON request bodies exist only as backward-compatibility paths for older clients. The API never exposes the seed, packet contents, ratings, or journal rows.

**Locked startup.** When a newer merged image starts against a store still bound to the previous Document 5 digest (for example after a Railway auto-deploy on merge), it starts **locked** instead of crashing: `/ready` reports `snapshot_advance_pending`, readiness stays blocked, and `/events/close` and `/admin/probe` are refused until `python scripts/advance_private_snapshot.py CHECKPOINT` from merged `main` performs the ordinary CAS advance. The stored snapshot is never overwritten at startup. Corrections via `Client.record_correction` remain available while locked.

**Canonical snapshot recovery.** Recovery to the checked-in snapshot is a separate, explicit path. A deployment operator may set `ENGINE_RECOVER_TO_CHECKED_IN_SNAPSHOT=1` together with a nonempty `ENGINE_RECOVERY_REASON` only to recover from a verified uncommitted-public-transaction failure. The target is not caller-selected: it is the SHA-256 of the checked-in Document 5 shipped in that verified image. The previous and restored bindings are appended to the private `snapshot_recoveries` ledger. This flag is one-time recovery machinery, not a normal progression mechanism. Normal week progression must merge public canon first and only then call the ordinary snapshot CAS helper.

The public adapter reads `ENGINE_RUNTIME_URL` and `ENGINE_API_TOKEN`; the older local token-file variables remain available only for local service tests. No secret belongs in Git. `python scripts/check_game_readiness.py` validates repository continuity, artifacts, shared-kernel identity, exact current-state snapshot, the real `/events/close` path with a reserved contract-derived administrative event whose identity changes with the canary payload contract, and the authenticated live deployment. It fails closed on missing environment variables, credentials, service loss, schema/procedure/kernel mismatch, absent private seed, snapshot mismatch, non-idempotent event closure, or failed recovery. After an atomic canon-changing public PR is merged, run `python scripts/advance_private_snapshot.py CHECKPOINT` from the merged canonical checkout to compare-and-swap the private binding to the actual Document 5 digest. New transitions use append-only `snapshot_transitions_v2`; audited recovery history remains separate, allowing a legitimate later progression from a restored checkpoint without deleting the original failed transition record.

`Dockerfile.engine` runs `scripts/validate_repository.py` and the full unit-test suite in a verification stage before producing the runtime image; a validation or test failure therefore blocks Railway deployment. The reference service, the public probe and the kernel use only the Python standard library, so the image installs no packages.

**Railway auto-deploy prerequisite.** The engine-runtime service deploys from `main` only while the Railway GitHub App is *installed* on this repository (GitHub Settings > Applications > Installed GitHub Apps), not merely authorized for login. Without the installation, Railway shows "Auto deploy unavailable", merges never reach the engine, and `/health` keeps reporting the previous kernel. After a kernel change merges, confirm `/health` reports the new kernel before advancing the snapshot.

Preseason uses the consolidated-block architecture: Document 5 may remain at the block-start snapshot while the four uniquely identified game packets are closed sequentially. Every packet must be rebuilt from the then-current roster, medical, availability, and role inputs. No later game may reuse stale football inputs; the final atomic public closure advances Document 5 once, after which the explicit snapshot helper advances the private binding.


## Public season statbook

`runtime/statbook.py` is downstream post-processing for already-closed games. It converts a closed game result into a public stat-only receipt and can aggregate those receipts into season totals. It has no access to the private career seed and does not participate in resolution, packet closure, matchup weighting or outcome selection.

Every public statistical page is generated from the receipt set: season views by `scripts/render_season_stats.py` (shared columns in `runtime/stat_tables.py`), standings and tiebreakers by `scripts/render_standings.py` (`runtime/standings.py`, alignment in `runtime/league.py`), and each week's box score by `scripts/render_box_score.py`. Incomplete receipt coverage stays labeled and formal league leaderboards are withheld until the gap is reconciled.


## Kernel attribution and volume contract (2013.4; 2013.5 adds emergency specialists; 2013.6 replaces the drive draw)

`runtime/usage.py` loads `library/data/2012_nfl_position_usage_baseline.json` (two-source 2012 play-by-play; see `library/2012_position_usage_calibration.md`). Player attribution is depth-chart aware: one game passer per club (`PlayerInput.depth`, then a `passer` role, then rotation status, then roster order), carries/targets/defensive credits by sourced position-group share and usage rank, assisted tackles, losing runs and tackles for loss. Through 2013.5, `runtime/kernel.py` drew plays and clock per drive from the resolved result and scaled them to the verified team-game totals (kernel 2013.6 replaces this; see below); third-down and first-down volume use sourced rates. `runtime/game_runner.py` rejects a TeamInput that is not a legal game-day unit. Kernel 2013.5 adds one rule: a club with no available kicker has its punter kick, and one with no available punter has its kicker punt, as NFL clubs do in an emergency; the game-day check accepts that coverage. The rule changes nothing for a club that dresses both specialists, and every Week 1 and Week 2 club did. `runtime/bands.py` audits closed receipts against the shapes without touching any result. The private service must be redeployed at the same kernel version; readiness fails closed on a mismatch.

## Snap-detail contract (introduced in kernel 2013.3; tag v3 from 2013.6, v4 from 2013.7, v5 from 2014.3)

The kernel keeps score/outcome generation at the possession layer and adds a deterministic public detail stream after each drive is resolved.

- `runtime/play_detail.py` allocates a resolved drive into public snap rows without consuming the possession RNG.
- `TeamInput.offensive_call_sheet` carries the structured weekly call menu used for named-call accounting.
- Display aliases are excluded from the football-substance outcome commitment, so rewording a call label does not change the score draw.
- `play_ledger` records every generated scrimmage snap plus scoring/punt/kickoff terminal plays.
- `play_call_stats` aggregates named offensive call usage for the closed game.
- The player dictionary now supports passing, rushing, receiving, protection, defense, kicking, punting and return counters.
- `runtime/statbook.py` supports `full` receipts for Jacksonville/protagonist games and `compact_stats` receipts for ordinary background games. Both preserve generated statistical production and a games-active row for every game-day player; only the full receipt keeps zero counters, the snap ledger and named-call detail.

The snap-detail layer is public post-resolution accounting. It never receives the private career seed directly outside the kernel call, and it cannot alter the already-resolved drive outcome.

## Kernel 2013.6 drive-model contract

Kernel 2013.6 replaces the 2013.5 drive-outcome draw. It was built after Week 3 and before Week 4 of the 2013 season. Weeks 1-3 (kernels 2013.4/2013.5) stand unchanged and are never rerun; their receipts appear only as a legacy cohort in the band audit.

**Model.** `runtime/drive_model.py` loads `library/data/2012_nfl_drive_model.json` (built by `scripts/research/build_2012_drive_model.py`; method and verification in `library/2012_drive_model_calibration.md`). Categories: `touchdown`, `field_goal_attempt`, `punt`, `interception`, `fumble_lost`, `downs`, `safety`, `clock`. Opponent-touchdown drives are remapped to the play that caused them (interception, fumble, punt, blocked field goal); the defence's score is not modelled. Each possession resamples one real 2012 drive of its category, so plays, net yards and seconds come from the same drive. No field position, start spot or down-and-distance is published (superseded after Week 8 by the kernel 2013.7 field-position contract below).

**Streams.** Every draw that can change score, possession, clock or a team counter (including kick and punt returns) is on the possession stream (`kernel._rng(seed, packet)`), in this order per possession:

1. category from the interior mix shifted by the anchor/home edge (`drive_model.apply_edge`: touchdown +edge, punt -0.65 edge, interception and fumble lost pro rata -0.35 edge; identical for every club);
2. a uniform tuple of that category; seconds = max(1, round(tuple seconds x clock_scale));
3. if those seconds reach the end of the window, a half-final category (same edge) for the pre-registered bucket of seconds left and a tuple that fits; a `clock` draw or no fitting tuple makes it a clock-expired possession (`end_of_half`, `end_of_game` or `end_of_overtime`). A half-final possession is the half's (or OT period's) final possession: its seconds are exactly the time left, and no further possession or kickoff follows it in that window;
4. pass plays and sacks; an interception keeps one non-sack attempt and a touchdown keeps one feasible scoring type;
5. touchdown type (pass 757/1,158, restricted to the feasible types); the turnover type is the category;
6. one sack loss per sack;
7. gross passing and rushing yards split by the sourced per-attempt and per-carry means, rescaled so that they equal the tuple's net plus sack losses, with a feasibility fit on touchdown drives so the scoring snap can come last;
8. penalties and chains (unchanged);
9. terminal scoring: touchdown 6 plus an extra-point draw (1,229/1,237) unless the touchdown ends overtime; field-goal make/miss by the tuple's kick distance; punt return; turnovers; downs; safety (2 to the defence); clock expiry;
10. kickoffs: the opening kickoff, the second-half kickoff to the non-opening receiver, an overtime kickoff after a new coin toss, and a kickoff (or post-safety free kick) after a score only when time remains in the window and the game has not ended. A touchback draw uses the stored 2012 rate.

The snap-detail stream (`public-snap-detail-v3`) and the kickoff-detail stream (`public-kickoff-detail-v1`) only name players, order snaps and split the already fixed yardage. The terminal snap (touchdown, interception, fumble) is always the drive's last snap. Changing either tag or a call name leaves the final score, possessions and team counters byte-identical.

**Halves and overtime.** Each regulation half is a 1,800-second window; a possession never crosses halftime or runs from regulation into overtime, an interior drive that fits leaves its remaining time to the next possession, and the half-final possession always runs out the window. Overtime follows `rules.ot_status`: a first-possession touchdown or any safety ends the game; a first-possession field goal gives the opponent one possession; otherwise sudden death; a regular-season period expiry ends the game (possibly tied); a postseason game continues.

**Checks.** `kernel.validate_result` applies the score identity 6 x TD + XPM + 3 x FGM + 2 x safeties (legacy results without `extra_points_made` use 7 x TD + 3 x FG), half clocks of 1,800 seconds, the second-half receiver, the kickoff count and `play_detail.check_ledger`. `check_ledger` runs on a full snap ledger or, ledger-free, on the compact `drives` summary that every 2013.6 receipt (full and compact_stats) carries. `runtime/bands.py` audits 2013.6 receipts as their own cohort and reports ledger-coherence counts with zero tolerance. `STATBOOK_SCHEMA_VERSION` stays 3; the new team counters (`field_goal_attempts`, `extra_point_attempts`, `extra_points_made`, `safeties`, `turnovers_on_downs`, `clock_expired_drives`, `kickoffs`, `drives`) aggregate as absent for older receipts.

**Correction of the double-final defect (found by the acceptance audit).** The first 2013.6 build let the time left after a half-final possession start another possession. That possession almost always expired, so about 99% of halves ended on a clock drive (2012: 73%) and drives per team-game ran above the band. The half-final pool holds the last offensive possession of each 2012 half, so the corrected kernel makes it exactly that: it runs out the window and nothing follows it. No coefficient, bucket edge, pool or tolerance was changed.

**Known 2013.6 limitations, not tuned** (history; the Weeks 4-8 receipts keep them, and the kernel 2013.7 contract below supersedes this list after Week 8).

- *Kickoffs per team-game* is rendered INFORMATIONAL, not graded. Its 2012 centre (PFR-based 2,665; play-by-play 2,620 unresolved) counts kickoffs the kernel does not model by design: after non-offensive touchdowns (134 in 2012, about 0.26 per team-game), onside kicks and re-kicks, and after a score on a half's final drive whose return ran out the clock. The 250-game acceptance run read 4.83 against 5.205.
- *Drive-ending punts per team-game* stays graded and can read OUTSIDE (acceptance run 5.02, WITHIN; test sample 5.15 against 4.82 ± 0.29). An interior drive that would overrun the window is redirected to the half-final draw, so the interior drives that survive are skewed short and punt-heavy: about 11.0 interior drives per team-game against 10.69 in 2012, with an interior punt share of 0.464 against 0.450, roughly +0.2 to +0.3 punts per team-game. `tests/test_usage_bands.py` tolerates this one row up to twice its tolerance and fails on any other OUTSIDE row. A later kernel should revisit the draw order; no coefficient, centre, pool, bucket edge or tolerance was changed.
- *No field position.* Each possession resamples a real 2012 drive with no start spot, so drive length is not tied to where the previous kick or drive left the ball. The ledger records a one-snap, seven-yard touchdown drive after a touchback (Entry 40), a one-net-yard touchdown drive after an unreturned punt and a safety after a touchback (Entry 41); Entry 39 left this gap open deliberately. The ledger coherence check cannot see it.
- *Call labels are not carrier-true.* `play_detail._choose_call` draws each snap's label uniformly from the sheet's calls of that run/pass type, independent of the ball carrier (Entry 41), so named-call counts show label assignment, not Stone's call frequencies.
- *No score-dependent fourth-down choice.* A drive's ending (punt, field goal, turnover on downs) comes from its resampled category, which does not depend on the score (Entry 41: a punt with 1:56 left while trailing by two).
- *Neutral site ignored.* `kernel._edge` gives its 0.008 home term to the designated home team whatever the packet venue, so the designated home team at Wembley received it (Week 4 Minnesota, Week 8 Jacksonville; Entry 45). The public receipt does not record the venue.
- *Non-offensive touchdowns are not modelled.* Scoring runs about 1.3 points per team-game below 2012 (Entry 39).
- *Sack rate reads low, with no graded band row.* The 2013.6 cohort (Weeks 4-5, 29 games) recorded 91 sacks on 2,144 dropbacks (4.24%) against the kernel's 0.0617 sack draw (`library/data/2012_nfl_aggregate_baseline.json`). `runtime/bands.py` grades no sack-rate row, so `calibration_audit.md` cannot show it. It is under investigation for kernel 2013.7 and is never grounds to rerun a closed week.

**Fixed in kernel 2013.7 (after Week 8; Weeks 4-8 stand and are never rerun).** No field position: every possession now starts at a published spot carried by real 2012 transition records. Call labels are carrier-true: a label follows the ball carrier or target through the committed 2013 call-family map. Score-dependent fourth-down choice: late-game possessions and fourth-down terminals come from the 2012 late-game cells. Sack rate: every possession replays the real drive's own runs, attempts and sacks, so no sack is converted to an attempt, and `sacks per dropback` is a graded band row. The punt-bias and kickoff-count limitations and the absence of non-offensive touchdowns remain (see below).

## Kernel 2013.7 field-position contract

Kernel 2013.7 replaces the 2013.6 drive draw for every slate closed after Week 8 of the 2013 season. It was built after Week 5; its acceptance did not pass, Weeks 6-8 closed under kernel 2013.6 (Entries 43-45), and the user adopted it as documented on September 27, 2026 (acceptance status below). Weeks 1-8 (kernels 2013.4-2013.6) stand unchanged and are never rerun; their receipts appear as the legacy and 2013.6 detection-only cohorts of the band audit. `KERNEL_VERSION` (`runtime/__init__.py`) and the private service's `KERNEL` are both `2013.7`; `STATBOOK_SCHEMA_VERSION` stays 3.

**Model.** `runtime/field_position.py` loads `library/data/2012_nfl_field_position_model.json` (built by `scripts/research/build_2012_field_position_model.py`; method, pre-registration and both verification passes in `library/2012_field_position_model_calibration.md`). It holds the same 5,984 drives and eight categories as the 2013.6 artifact, each as a real tuple with its start and end spot, seconds, first-snap clock and score state, terminal down and distance, real chains, and real runs, attempts, sacks, kneels, spikes and scoring kind; and the real 2012 kickoff, safety free kick, punt, interception and fumble transition records. `runtime/drive_model.py` still supplies the category list, `apply_edge`, the clock scale, field-goal accuracy by distance and the kick rates.

**Regimes and cells.** A possession's state picks its pool: first half, a neutral drive by start bin (90-99, 81-89, 80, 70-79, 60-69, 50-59, 40-49, 30-39, 20-29, 1-19), redirected to the first-half final pool for the seconds left (0-30, 31-60, 61-1800) when a clock draw or a drive that would reach halftime comes up; second half with more than 600 seconds left, a neutral drive whose seconds fit the window; the last 600 seconds, a late cell by time left (301-600, 121-300, 120 or less) and the offense's score need (trail 9+, trail 4-8, trail 1-3, tied, lead 1-8, lead 9+), collapsed to at least 30 drives each by the pre-registered `cell_map`; overtime, the overtime cell (a trailing offense uses the 120-or-less trail 1-3 cell, an inference because 2012 had four such drives).

**Streams and draw order.** Everything that can change score, possession, clock, spot or a team counter is on the possession stream (`kernel._rng(seed, packet)`), in this order:

1. opening coin toss; each kickoff or safety free kick is one uniform real 2012 record (own-35 kickoffs, 2,444 records; free kicks from the 20, 13 records), which fixes touchback, kick, return, enforcement and the receiving club's start;
2. per possession, the category from the cell's 2012 counts shifted by `apply_edge` (touchdown +edge, punt -0.65 edge, turnovers -0.35 edge pro rata; identical for every club), with every category masked that has no count or no real drive feasible from the start spot, then renormalised;
3. a uniform real drive of that category from the start bin (ladder: the bin's list, then the same zone, stepping when no tuple of the rung is feasible at both the spot and the clock; a thin neutral list adds the nearest bins), feasible from the spot: end spot in the field, net inside the (category, start bin) 2012 envelope, sacks and kneels fitting the field, seconds fitting the window (late and overtime finals match the time bucket instead; fourth-quarter fourth-down terminals must match the terminal bucket). Touchdown net = start; safety net = start - 100; field goal, punt, downs, interception and fumble lost keep the real end spot; clock keeps the real net. Fallbacks, counted in `diagnostics`: the union of the need's late cells, then the nearest-bucket clock tuple; the `[0, 0, 0]` clock tuple must never occur;
4. the drive's own real runs, attempts, sacks, kneels, spikes and scoring kind (no pass or sack Bernoulli, no touchdown-type draw);
5. one sack loss per non-terminal sack (randint(3, 10)); losses are fitted to the net when the drive has no free snap, and capped so the ball stays out of the own end zone when only sacks precede a scoring snap;
6. gross passing and rushing yards over the free snaps (the 2013.6 gauss split), with the touchdown feasibility fit;
7. penalties (counters only, unchanged) and the drive's real chains: first downs by scrimmage and penalty, third- and fourth-down attempts and conversions;
8. terminal scoring (extra point 1,229/1,237 unless the touchdown ends overtime; field goal by the real kick distance; safety 2 to the defence) and the transition: punt, the 20 real punts nearest the line of scrimmage plus every record tied at the 20th distance, feasible at the spot (a touchback only when the gross reaches the goal line); interception or fumble lost, the same nearest-record rule on the turnover spot; downs, 100 - end; missed field goal, min(80, 110 - distance); a kickoff after a score when time remains.

The snap-detail stream (`public-snap-detail-v4`), the kickoff-detail stream (`public-kickoff-detail-v2`) and the label stream (`public-call-label-v1`) are separate, keyed on the seed, event, drive and offense, and never feed the possession stream. They name players, order snaps inside the field, split the already fixed yardage and choose labels. Changing a tag, a call name or a carrier/target declaration leaves final score, possessions, kickoffs and team counters byte-identical.

**Published fields (append-only).** Each possession adds `start_spot`, `start_kind` (`kickoff`, `kickoff_touchback`, `free_kick`, `punt`, `interception`, `fumble_lost`, `downs`, `missed_fg`, `period_change`), `end_spot`, `next_start`, `score_diff`, `cell`, `tuple_terminal_bucket`, `chains`, `fourth_down`, `kneels` and `spikes`; `kickoff_after` adds `next_start`, `touchback` and `enforcement`. Kickoff records carry `next_start`, `touchback`, `kick_yards`, `return_yards`, `enforcement` and `outcome`. Spots are `yardline_100` (distance to the opponent's goal line). Every receipt's compact `drives` summary carries the 11 new fields after the 14 kernel 2013.6 fields; 2013.6 rows stay 14 fields long. Snap rows add `yardline`, `kneel` and `spike`; punt rows add line of scrimmage, gross, return, enforcement, outcome, touchback and next start; field-goal and downs rows carry the fourth-down state.

**Fourth down.** A punt, field-goal or downs terminal publishes `fourth_down`: down, distance, line of scrimmage, clock, clock bucket (second half), half, score difference, need, decision zone (own half, opp 49-35, opp 34-1), the drawn cell, the tuple's own terminal bucket and the action (`punt`, `field_goal`, `go`). The decision is the resampled real drive's; late cells make it depend on score and time. It is the league-wide 2012 model for every club in autonomous mode, not a Stone preference; `user_controlled` pauses remain a stub.

**Call labels.** `runtime/call_families.py` maps each committed call family to the position groups that may carry (runs) or be targeted (passes), grounded in the active 2013 offensive iteration; a call may override its family with explicit `carrier` or `target` lists. A declaration may also be `unspecified`: that call is never chosen as a label. An unknown family, a carrier outside QB/RB/FB/WR/TE or a target outside RB/FB/WR/TE (or `any`) fails closed in `build_game_packet`, `week_inputs.jacksonville_input` (`build_week_inputs.py` reports `WEEK_INPUTS: BLOCKED`) and `validate_repository.py`. Declarations, call names and duplicate listings stay out of the outcome packet (`canonical_call_sheet`). On the label stream a run takes a uniform sheet run whose carrier groups include the runner's group; a pass takes a sheet pass whose targets include the target's group (any pass for a sack); a quarterback carry is a scramble with the 2012 share (nflverse 681/1,223) and then takes any sheet pass (or `QB Scramble`), otherwise a quarterback-carrier run (or `Generic Run`); kneels and spikes are `Victory (kneel)` and `Clock (spike)`. Clubs without a sheet get `Generic Run`/`Generic Pass`. Label frequencies are descriptive only: 2012 play-by-play has no concept source.

**Checks.** `validate_result` adds the chain-counter identity for spot results. `play_detail.check_ledger` evaluates 32 classes: the 15 legacy classes, and for results whose every possession has a start spot, 17 spot and label classes (`start_spot_out_of_field` through `kneel_spike_mislabelled`; the kick-spot and label classes need the full snap ledger). `measurable_classes` says which classes a receipt can show. `runtime/bands.py` audits three cohorts (legacy, 2013.6 detection-only, current); the current cohort adds `audit_field_position`: graded kickoff touchback share, mean non-touchback kickoff start, realised punt net by line-of-scrimmage bin, late trailing punt shares, third-down attempts per punt drive, sacks per dropback and DL/LB/DB sack-credit shares, and informational start, outcome-by-start, points-per-drive, scramble, fourth-down, kneel and overtime rows. Rows under 30 events read INSUFFICIENT. `render_season_stats.py` and `render_box_score.py` add field-position views and a drive chart for 2013.7 receipts only; older views render unchanged.

**Acceptance status: adopted as documented by the user; three rows known detections.** On the 250-game synthetic acceptance sample every structural, coherence, defect, label, isolation and determinism criterion passes, and every field-position and sack row is WITHIN; three graded drive-model rows read OUTSIDE (drive share: clock 0.0507 against 0.0628 +/- 0.0095; clock-expired drives per team game 0.598 against 0.734 +/- 0.115; FGM per team game 1.840 against 1.664 +/- 0.173), all traced to the first-half half-final redirect below. By the user's explicit decision of September 27, 2026 the kernel is adopted as documented: the three rows are registered in `runtime/bands.py` `KNOWN_DETECTIONS` for the 2013.7 cohort (with the existing punt row), stay graded, are labelled as known detections in `calibration_audit.md`, and `tests/test_usage_bands.py` tolerates each up to `KNOWN_DETECTION_BOUND` (2) times its tolerance; any other graded row OUTSIDE still fails. No centre, tolerance, coefficient, pool, cell or bucket edge was changed. Details and both acceptance runs: `library/2012_field_position_model_calibration.md`.

**Known 2013.7 limitations, not tuned.**

- *No per-snap down, distance or explicit go-for-it model.* Converted fourth downs inside a drive are real chain counts; a failed go is the downs terminal; a continuation after a converted late fourth down is not a separate event. Snap-level replay is deferred to kernel 2013.8.
- *Fourth downs before the fourth quarter and outside late cells* keep the resampled drive's own decision, including end-of-first-half urgency and second-half drives that start with more than 10:00 left; a neutral second-half drive that runs into the last 10:00 is counted (`h2_neutral_into_late`), not terminal-checked.
- *Late-cell mixes are not conditioned on start position* (cells of 30-131 drives); start enters only through masking, the envelope and the bin-to-zone ladder. A masked category's weight is renormalised onto the others; because the terminal-bucket match applies only to punt, field-goal and downs tuples, thin cells mask those more often than touchdowns, and late cells run touchdown-heavy.
- *The first half still ends through the half-final redirect*, so first-half final possessions start earlier than in 2012 and are field-goal-heavy and clock-light. Drive-ending punts per team game, FGM per team game, drive share: clock and clock-expired drives per team game are `KNOWN_DETECTIONS` (graded, labelled, tolerated within twice their tolerance); a later kernel should revisit the first-half draw.
- *Snap order is not derived from real downs*: a reader cannot reconstruct down and distance from the snap ledger.
- *Not modelled:* onside kicks, kicking-team recoveries and retained punts, return touchdowns of every kind and the defence's score, blocked field goals (missed-field-goal rule), two-point tries, timeouts, penalty safeties as penalties. Kickoffs per team-game stays informational.
- *Unsourced constants that remain* (none moves the ball spot): non-terminal sack loss randint(3, 10), penalty yards randint(5, 10) and the penalty Bernoulli, the gauss split spreads, the `_edge` 0.025 / 0.008 / +/-0.06 and `apply_edge` 0.65 / 0.35 coefficients, passes-defended 0.35 and pressure 0.20.
- *Definitions:* `kick_returns` still counts every non-touchback kick; `punt_returns` now counts the play-by-play `returned` outcome (no band row). The Pro Football Reference reconciliation is still unresolved.
- *The scramble share rests on one GSIS feed* whose two description revisions disagree (681/1,223 against 643/1,228); nflverse is used and the row is informational.
- *Resampled real drives recur* across a season with different players and labels.
- *Not conditioned:* weather, venue (e.g. altitude touchbacks), per-staff tendency profiles.
- *Postseason overtime period change* (not reachable in the regular season): a clock-expired overtime possession passes the ball to the other club at the same spot, as the possession loop alternates; a real period change keeps possession. **Fixed in kernel 2013.8** (below).
- *Overtime walk-off drives run out the period.* **Fixed in kernel 2013.8** (below); the Week 10 Washington at Minnesota receipt keeps it.
- *Neutral site still ignored* in 2013.7-2013.10: `kernel._edge` gave its 0.008 home term to the designated home team whatever the venue (Entry 45). Fixed in 2013.11.
- *Closed canon is not rerun.* Weeks 1-8 keep their defects (for example the Week 4 seven-yard touchback touchdown, the Week 5 touchback safety, one-yard touchdown and 1:56 punt, and the Weeks 6-8 field-position and label defects of Entries 43-45).

## Kernel 2013.8 overtime and 2013 rules correction

Kernel 2013.8 corrects the overtime state machine to the 2013 NFL rules sourced in `library/2013_nfl_playing_rules_for_simulation.md` (research and verification passes, plus the rule-by-rule audit of this runtime). Regulation is unchanged: no centre, pool, coefficient, cell, bucket edge or tolerance moved, and a regulation half draws exactly what kernel 2013.7 drew from the same packet. `KERNEL_VERSION` (`runtime/__init__.py`) and the private service's `KERNEL` are both `2013.8`; `STATBOOK_SCHEMA_VERSION` stays 3 and the receipt/drives-summary fields are unchanged.

**The defect.** The 2012 overtime pool flags a drive `final` when its score ended the game (a walk-off), not only when the clock ran out. Kernel 2013.7 replayed every `final` overtime tuple as consuming the whole remaining window, so an opening-possession field goal could run out the 15-minute period and the expiry rule then ended the game with the other club never possessing (Week 10 Washington at Minnesota, drive 26). On the 250-game synthetic sample, 10 of 21 kernel 2013.7 overtimes had a non-clock drive run out the period: one opening field goal ended the game, one downs drive produced a tie, and eight walk-offs were clocked to 0:00. Closed 2013.7 receipts stand and are never rerun.

**Overtime in 2013.8.**

- *Regular season and preseason:* a new coin toss (possession stream) picks the receiver; one 15-minute period (`RULES.regular_ot_seconds`) on a real clock. In the overtime regime only a clock-expired drive ends the period (`field_position.ends_window`); every other 2012 drive, walk-off or not, replays with its own scaled seconds and must fit the time left. Possessions alternate; `rules.ot_status` applies modified sudden death (opening touchdown or any safety ends it; an opening field goal gives the other club a possession, whose touchdown wins, field goal leads to sudden death and anything else loses; after both possess, or after a scoreless opening possession, the next score wins). When the period expires the game ends, tied if level. No try follows a walk-off touchdown.
- *Postseason:* the same possession rule over 15-minute periods laid on one continuous countdown of `RULES.postseason_ot_period_bound` (10) periods, so a possession carries across a period break (the 2010 rule) and the game never ends tied. Snap and kick rows are labelled `OT`, `OT2`, ... by `play_detail._period_clock` given `("OT", periods, length)`; a possession's `period` is its starting period; `render_box_score.clock_text` renders the drive chart the same way. The bound is an engine limit, not a rule: exhausting it raises rather than ending a game level.
- The trailing club in overtime still draws the late 120-or-less trail 1-3 cell (the 2013.7 labelled inference).

**Other rule corrections.** `rules.review_authority` gives the booth every overtime review; the unused and incorrect `rules.overtime_ends` is removed (`ot_status` is the single implementation); `game_runner.build_game_packet` fails closed on more than 46 game-day actives (`RULES.active_limit`). New sourced constants in `Rules2013`: two-minute warning 120 s, safety kick and scrimmage-kick touchback at the 20, two-point snap at the 2, regular-season overtime timeouts 2 (unverified for 2013; no effect), postseason overtime intermission 120 s.

**Audit cohorts.** `bands.cohorts` still splits legacy, 2013.6 and field-position-era receipts; `bands.current_cohorts` splits the field-position era by exact kernel version, so kernel 2013.7 (Weeks 9-10) and 2013.8 receipts are never pooled. `KNOWN_DETECTIONS["2013.8"]` carries the 2013.7 registry over unchanged (the first-half redirect is untouched). `calibration_audit.md` renders a 2013.8 section only once a 2013.8 receipt exists, so committed views are unchanged until then.

**Tests and sample.** `tests/test_overtime.py` scripts the overtime draws after real tied regulations: an opening made field goal gives the other club a possession; an opening touchdown ends it with no try; a safety ends it; an expired regular-season period ties; a postseason overtime crosses into `OT2` and ends decided; walk-off tuples never run out the period; and every unscripted overtime alternates and ties only at regular-season expiry. On the shared 250-game synthetic sample (same seeds as the 2013.7 acceptance) every band row is WITHIN, the drive-model rows read as in 2013.7 (18 WITHIN, the same three known detections within twice their tolerance), every field-position row is WITHIN, and ledger coherence is zero; 21 games reached overtime, none tied, none ended on an opening field goal.

**Still not modelled (listed in the rules library):** two-point tries, onside kicks and kicking-team recoveries (so the overtime kicking-team-recovery branch cannot occur), defensive and return touchdowns (so the only defensive overtime score is a safety), per-snap timeouts, two-minute warning and play clock (drive durations are real 2012 durations).

## Kernel 2013.9 spike seating

Kernel 2013.9 changes one thing: where a spike sits in a drive's snap order. The kernel draws a real 2012 drive's spike count, and `play_detail._layout` used to shuffle spikes into any slot, so a spike could be a drive's first snap or follow an incompletion. Both mean spiking a clock that is already stopped: a change of possession is an administrative stoppage (`library/2013_nfl_playing_rules_for_simulation.md` R14), and an incompletion stops the clock. In Week 12, Houston spiked on its first snap after a fair catch (ledger Entry 53).

**The fix.** `play_detail._seat_spikes` runs after the final snap order is set. It moves each misplaced spike, inside the free prefix, to just after the nearest snap that leaves the clock running (a run, a sack or a completion), earlier first. A spike gains nothing, so every running spot, prefix bound, kind total and the terminal snap are unchanged. No randomness is consumed, so the same packet draws the same drives, scores, statistics and attributions as 2013.8; only snap order can differ. A drive with no clock-running snap keeps its spike after the first snap, never first.

**Evidence.** On the shared 250-game synthetic sample, the 2013.8 layout misplaced 40 of 87 spikes and 2013.9 misplaces none. Final scores and the drive summaries are identical in all 250 games. `tests/test_spike_seating.py` covers the moves and the sample.

**Versions and cohorts.** `KERNEL_VERSION` and the private service's `KERNEL` are both `2013.9`. `KNOWN_DETECTIONS["2013.9"]` carries the 2013.8 registry over unchanged; `bands.current_cohorts` gives 2013.9 receipts their own audit section. Closed receipts (including the Week 12 spike) are never rerun.

## Kernel 2013.10 personnel-true call labels

Kernel 2013.10 changes one thing: which call label a snap carries. Labels are chosen after each snap is resolved, on their own random stream, from the calls whose family covers the carrier's or target's position group. Through 2013.9 the call's personnel was never consulted, so a receiver who is not in a package could carry that package's label. In Week 13, for example, the WR4 caught a touchdown labelled "22 Heavy Right, Snag", though 22 personnel carries one receiver (Entry 55; 7 of 135 labelled passes in Weeks 10-13).

**The fix.** `play_detail._personnel_fits` reads a two-digit personnel code as backs then tight ends, with receivers as the rest of five. A labelled player needs a slot in his group, and his depth rank in that group may be at most one past the slot count: one rotation spot, as the weekly plans rotate "Thielen / Blackmon" and "MJD / Grimes". A fullback needs two backs. A quarterback, and any code with no skill layout (6OL), always fit. When no call on the sheet fits, the snap carries the generic label rather than a wrong one.

**Evidence.** On the shared 250-game sample, scores, drives and every player statistic are identical to 2013.9, since labels never feed back into resolution. Of club A's 16,481 labelled snaps, 1,717 changed label and 340 (2.1%) became generic, against 3 before; ledger coherence is zero. `tests/test_personnel_labels.py` covers the rule and checks every sample label.

**Versions and cohorts.** `KERNEL_VERSION` and the service `KERNEL` are both `2013.10`. `KNOWN_DETECTIONS["2013.10"]` carries the 2013.9 registry over. Closed receipts keep their labels and are never rerun.

## Postseason bracket (no kernel change)

The postseason runs on kernel 2013.10 unchanged. `runtime/postseason.py` builds each round's games from closed receipts only.

**Seeding.** `seeds` takes the final `standings.compute` order per conference: the four division winners are seeds 1-4, and the two best remaining clubs are seeds 5-6.

**Rounds.** Postseason weeks are numbered 18-21: Wild Card, Divisional, Conference and Super Bowl.

| Week | Round | Pairings |
|---:|---|---|
| 18 | Wild Card | 6 at 3 and 5 at 4 |
| 19 | Divisional | Reseeded: the lowest surviving seed at 1, the other survivor at 2 |
| 20 | Conference | The higher remaining seed hosts |
| 21 | Super Bowl | The two conference champions at a neutral site, with the designated home conference from the slots file |

A round raises `ValueError` until every game of the round before it has a closed receipt. A tied postseason receipt also raises, since postseason games cannot tie.

**Slots.** Each game takes the real 2013-14 date, kickoff and network of the slot with its conference and seed matchup (`library/data/2013_postseason_slots.json`). The rule is result-blind.

**Pipeline.** `week_inputs.schedule` delegates weeks 18-21 here, and the package carries `game_type: postseason`, the round and the seeds.
- `build_week_inputs.py` also finds call sheets under `career/2013/postseason/`.
- `close_week.py` passes `game_type` to `run_game`, so the 2013.8 postseason overtime applies, and writes the receipts to `career/2013/stats/postseason_receipts/`. Standings, the regular-season statbook, awards and the calibration audit read `game_receipts/` only, so they stay regular-season views.
- `render_box_score.py` finds receipts in either directory.
- Tests: `tests/test_postseason.py`.

**Neutral site.** Kernel 2013.11 (Entry 66) removes the home term at a neutral venue, so the Super Bowl's designated home team gets no home edge; home-venue games are unchanged.

## Kernel 2013.11 neutral-site correction

Kernel 2013.11 changes one thing: `kernel._edge` adds its 0.008 home term only when the packet venue is not `neutral`. Through 2013.10 the designated home team received it at any venue, so Minnesota (Week 4) and Jacksonville (Week 8) got it at Wembley (Entry 45). The anchor term is unchanged.

**Scope.** Only games drawn with venue `neutral` change. Every home-venue game resolves exactly as under 2013.10, since the function is identical there. In the 2013 branch the only remaining neutral-site game is Super Bowl XLVIII; the Wembley receipts are closed and never rerun. Tests: `tests/test_neutral_site.py`.

**Versions and cohorts.** `KERNEL_VERSION` and the service `KERNEL` are both `2013.11`. `KNOWN_DETECTIONS["2013.11"]` carries the 2013.10 registry over.


## Kernel 2014.1 timeouts, kneel zones and goal to go

Kernel 2014.1 fixes the clock-management defects recorded in Entries 60, 64 and 67 and the fourth-down display defect. The user directed these fixes before any 2014 game.

**Data.** The 2012 field-position artifact moves to schema v2 (`library/data/2012_nfl_field_position_model.json`, rebuilt by `scripts/research/build_2012_field_position_model.py`; `--check` reproduces it byte for byte).
- **New tuple fields.** Every drive tuple gains four fields: each club's charged timeouts at the drive's first offensive snap (`posteam_timeouts_remaining`, `defteam_timeouts_remaining`) and the timeout rows each club called during the drive (`timeout_team`).
- **Second pass.** The nflscrapR comparison covers the new counts. The starting counts differ on 36 (defence) and 32 (offence) of 5,940 matched drives, almost always by one timeout. Both files are equally self-consistent (5,247 of 5,276 same-half possession changes carry both counts exactly).
- **Explained deviations.** The zero-timeout buckets and total defence timeouts used exceed the count tolerance; they are recorded as explained in the builder.

**Timeout state.** Each club holds three charged timeouts at the start of each half.
- **Regular-season overtime:** two per club (`RULES.regular_ot_timeouts`; library R6, Unverified for 2013).
- **Postseason overtime:** three per club per two-period "half" (`RULES.postseason_ot_timeouts_per_half`; labelled inference).
- **Usage:** after each possession, each club's count falls by the timeouts the replayed real drive used, capped at what it holds.
- **Publication:** every possession publishes `timeouts` = [offence before, defence before, offence used, defence used] and `timeout_level`.

**Conditioned draws (`field_position.timeout_match`, `_timeout_options`).** First-half-final, late (last 10:00) and overtime draws condition on the two counts through a ladder:

| Level | Match rule |
|---|---|
| 0 | Both counts equal the real drive's |
| 1 | The clock-stopping side's count equals (the offence when it trails, otherwise the defence) |
| 2 | That side's count is in the same band (0, 1-2, 3) |
| 3 | Unconditioned |

- **Minimum pool:** a level is used only when the pool holds at least 30 matching drives (`MIN_TIMEOUT_POOL`, the pre-registered `min_cell`).
- **Category weights:** each category's 2012 cell count times the share of its drives that match, an estimate of P(category | cell, timeouts). So the timeouts move the choice between kneeling out, punting, a field goal or going.
- **Tuple choice:** within a category the tuple is drawn from the matching feasible drives, or from the category's feasible set when none matches. The timeout filter never masks a category; masking stays spot and clock feasibility, as in 2013.x.

**Kneel start zone.** A drive with kneel-downs is feasible only from its own real start zone (A 80-99, B 50-79, C 1-49). All 83 real first-half-final kneel drives started in the offence's own half; the Super Bowl XLVIII receipt shows an own-half kneel drive replayed from the opponent's 1 through the clock fallback.

**End-of-half fallback.** When the first-half-final draw finds nothing feasible, a real drive from the same start bin that fits the time left is drawn before any clock fallback (`h1_fit_fallback`).

**Goal to go.** A published fourth-down record's `ydstogo` is at most the distance to the goal line, and `goal_to_go` says when the real distance reached it.

**Not modelled separately.** The two-minute warning and the play clock are still embedded in each real drive's duration. Late draws now match the clubs' timeouts, but no snap-by-snap clock is simulated.

**Checks.** Two coherence classes are evaluated only on 2014.1 receipts:
- `timeout_state_invalid`: counts stay within the allowance and carry exactly from possession to possession.
- `fourth_down_beyond_goal`.

Tests: `tests/test_timeouts.py`.

**Acceptance (250-game synthetic sample).** Every structural, coherence and determinism check passes, with zero coherence violations on results and receipts. Every graded band row is inside its band except the two clock rows already registered as known detections (drive share: clock 0.0493; clock-expired drives per team game 0.582).
- **Improved:** FGM per team game is back inside (1.832).
- **At the edge:** drive share: touchdown reads 0.2100 against 0.1945 +/- 0.0155, the band's ceiling (2013.11 on the same sample: 0.2090).
- **Low but inside:** the trailing 1-8 late punt share reads 0.062 against 0.119 +/- 0.064.
- **Why:** both trace to the late cells' existing masking bias. A category with no drive feasible at the spot and clock is removed and its weight goes to touchdowns, which are always feasible. Conditioning puts a little more weight on states where that bias bites. The conditioned mix before masking is close to 2012 (late touchdown probability 0.165 against 0.159 real). Recalibrating the late-cell masking is a separate, larger change.
- **Effect on the defects:**
  - A leading offence in the last two minutes punted 16 of 115 times under 2013.11 and 11 of 126 under 2014.1.
  - With the defence out of timeouts, it punted 1 of 50 times and otherwise ran out the clock.
  - First-half kneel drives outside their start zone can no longer occur.

**Versions and cohorts.** `KERNEL_VERSION` and the service `KERNEL` are both `2014.1`. `KNOWN_DETECTIONS["2014.1"]` carries the registry over. Closed 2013 receipts keep their defects and are never rerun.

## Kernel 2014.2 late-game recalibration

Kernel 2014.2 corrects the late-cell masking bias recorded at the 2014.1 acceptance. The user directed it before any 2014 game.

**The bias.** A late category's weight came from its score-and-time cell, but the tuple had to be feasible at the current spot and clock.
- **What went wrong:** when none was feasible, the category was masked and its weight went pro rata to the rest. Touchdowns, which are always feasible, gained most.
- **Size:** on the 250-game sample an average of 1.7 categories were masked per late draw. The expected late touchdown share went from 0.166 before masking to 0.209 after (2012: 0.159).
- **Causes:** spot masking dominated for turnovers, downs and clock drives, and clock masking for field goals.

**The correction (`runtime/field_position.py`).**
- **Start-zone weights (`ZONE_CONDITIONING`, `zone_likelihood`).** In a conditioned draw (first-half final, late, overtime), each category's weight is multiplied by P(start zone | category) / P(start zone), with add-one smoothing. The estimate comes from a larger reference pool: the need's union of late cells, every first-half final, or the overtime pool. This is Bayes on the cell mix, P(category | cell, zone) up to a constant, assuming the start zone depends on the category and need but not the time bucket.
- **Need-union rungs (`NEED_UNION_RUNGS`).** A late cell with no feasible drive of a category takes one from the same need's other time buckets: same bin, same zone, then any start feasible at the spot (end in the field, net inside the current start bin's 2012 envelope). The same clock filters apply. A category is masked only when none of these supplies a drive.

**Evidence (identical seeds, 2014.1 against 2014.2).**
- **Masking:** masked categories per late draw fell from 1.47 (zone weights alone) to 0.74.
- **Expected late touchdown share:** 0.199 under 2014.1 and 0.170 under 2014.2 on 750 fresh games (2012: 0.159). Realized was 0.2016 and 0.1770, consistent with the expected values.
- **Drive share: touchdown on the same 750 games:** 0.2027 under 2014.1 and 0.1991 under 2014.2 (centre 0.1945).
- **Expected late mix by need against 2012 (250-game sample):**

| Need | Touchdown | Punt |
|---|---|---|
| lead 1-8 | 0.089 (2012: 0.078) | 0.435 (0.436) |
| trail 4-8 | 0.294 (0.255) | 0.173 (0.179) |
| trail 9+ | 0.276 (0.246) | 0.129 (0.135) |

**Acceptance (250-game synthetic sample).** Zero coherence violations. Every graded row is inside its band, with these known detections:
- **Carried from 2013.7:** the two clock rows, drive-ending punts per team game and FGM per team game.
- **Two rows registered for 2014.2:**
  - FGA per team game: 2.178 against 1.984 +/- 0.189. It rises with FGM from the first-half half-final redirect, and late field goals are no longer masked; their expected share by need tracks 2012.
  - Punt share of possessions ending in Q4's last 5:00 or OT, offence trailing 1-8: 0.043 against 0.119 +/- 0.067. About 70 events; 0.087 on the 750-game sample, inside its tolerance there.
- **Who registered them:** Claude, on September 28, 2026, while carrying out the user's recalibration request. They are reversible, stay graded and labelled, and are tolerated only within twice their tolerance.

**Still open (not late-game).** On 750 games the field-goal-attempt share (0.179 against 0.170) and the turnover share (0.117 against 0.125) sit outside their narrower 750-game tolerances under both 2014.1 and 2014.2. Both trace to the first-half redirect and the neutral pools.

**Snap detail.** A drive whose only running-clock snap is its terminal snap keeps its spike after the first snap (the 2013.9 rule). `tests/test_spike_seating.py` now checks only drives with a running snap before the terminal tail. Borrowed late drives produce the case about twice in 250 games.

**Versions and cohorts.** `KERNEL_VERSION` and the service `KERNEL` are both `2014.2`. `KNOWN_DETECTIONS["2014.2"]` adds the two rows above. No closed 2013 receipt is rerun.

## Kernel 2014.3 credit rules (on-field line, coverage, long snaps)

Kernel 2014.3 changes who is credited, never what happens. The user directed it after the 2013 season honours (Entry 71) showed that individual line and coverage statistics carried no participation signal. Every rule reads only the club's own depth order and roles and applies to every club alike.

**What was wrong (2013.4 through 2014.2).**
- **Sacks allowed** were charged by an equal draw over every dressed lineman, backups included (`choose` over the whole line, drawn before the rusher). In Weeks 11-17, 32% of background sacks went to linemen outside the five on the field, which is what chance predicts.
- **Coverage tackles** were never credited. The punt cover player was drawn from a position set that missed OLB, ILB, MLB, SS and FS, and was praised for "coverage lane held" whatever happened.
- **Long snappers** did nothing statistically.
- **Returners** were drawn afresh on every kick when a club designated none (Jacksonville used 18 kick returners in 2013).

**The rules (`runtime/usage.py`, `runtime/play_detail.py`).**
- **The line on the field** (`protection_front`): the five available linemen lowest in the club's depth order start and earn `line_starts`. Their labels only seat them: the center at C, tackles at LT then RT, guards at LG then RG, and anyone left takes an open slot in depth order (a first-string guard playing right tackle starts there, ahead of a backup tackle).
- **Sack blame** (`beaten_slots`): the rusher is drawn from the sourced sack shares, and now drawn first. An edge rusher (DE, OLB, a defensive back) beats a tackle; an interior rusher (DT, NT, ILB, MLB) a guard or the center; a generic LB or DL label, which says neither, any of the five. The lineman is drawn evenly among those slots. The ledger records `blocker_slot`.
- **Coverage tackles** (`coverage_unit`, `special_teams_tackles`): on a kickoff or punt that is actually returned (not a touchback, fair catch, muff or kick out of bounds), one player of the kicking club's coverage unit is credited, evenly. The unit is the club's designated `kickoff_coverage` / `punt_coverage` players, filled to 10 (kickoffs) or 9 (punts) by a mechanical make-up from non-starters by depth: 3 linebackers, 4 defensive backs (3 on punts), a tight end, a fullback or back and a receiver. Base starters, skipped first, are one back, three receivers, one tight end, four linebackers (so a 3-4 club's starters stay out too) and four defensive backs (a labelled convention, `BASE_STARTERS`). The club's own returners are left out.
- **Returners** (`club_returner`): for each role (kick, punt), the designated returner, else the club's first non-starter receiver, back or defensive back by depth. One kick returner and one punt returner per club per game; they are the same player unless the club designates different ones.
- **Long snaps** (`long_snapper`, `long_snaps`): the first long snapper, else the center on the field, on every punt, field goal and try.
- **Player evidence:** the lineman facing the rusher is named on a sack without a technique finding (which of the eligible linemen is an even draw), and a punt coverage player is named only when he made the tackle.
- **Stream tags:** snap detail v5, kickoff detail v3 (snap layouts are redrawn; no team counter moves). The possession stream is untouched.

**Validation (`kernel.validate_result`).** Five line starts per club (fewer only if it dresses fewer linemen); no sack charged to a lineman off the field; one coverage tackle per returned kick, none on any other kick, and each player's coverage tackles equal to his ledger rows; long snaps equal to punts plus field-goal and extra-point attempts. Legacy inputs without linemen or a long snapper keep the old fallbacks.

**Acceptance (identical seeds, 2014.2 against 2014.3).**
- **Replay:** every game of the frozen Weeks 11-17 TeamInput packages, replayed with ten fresh seeds each (1,090 games), is identical to 2014.2 (final score, every possession, kickoffs, injuries, the opening receiver and every team counter), with zero validation errors and zero coherence violations.
- **Credit on the same games:** all 4,947 sacks charged to the five on the field (left tackle 26.1%, right tackle 27.1%, left guard 15.3%, center 15.8%, right guard 15.7%). Across the 218 frozen team-games no available first-string lineman sat. Coverage tackles came to 4.7 per team game (tight ends 17.5%, cornerbacks 15.1%, outside linebackers 11.9%, backs 10.3%, receivers 10.0%, the rest fullbacks, inside linebackers and safeties). Every long snap went to a long snapper. One kick returner and one punt returner per club in 87% of team games (the rest had no return of that kind).
- **Guard in the suite:** `tests/test_attribution.py` (ResultIdentityTests) replays 40 synthetic regular and postseason games and requires the result digests recorded under 2014.2 (`tests/data/result_identity.json`). A kernel that deliberately changes results replaces that file in its own commit.

**What this does and does not give.** These statistics now record who was on the field, who was beaten and who made the tackle. They still carry no individual quality signal: the engine has no per-player ability (Document 7 section 2.2 describes per-attribute tiers that are not built), so which eligible lineman is beaten, or which coverage player makes the tackle, is drawn evenly. Closed 2013 receipts are not rerun and keep the old credit.

### Pro Bowl game type (kernel 2014.3)

`resolve_game(..., game_type="pro_bowl")` plays the 2014 Pro Bowl structure (`library/2013_super_bowl_mvp_and_pro_bowl_procedure.md` section 3; the branch readings of its unverified rules are in `career/2013/pro_bowl/method.json`). Regular and postseason games never reach these branches; the 1,090-game replay above was rerun after they were added and stayed identical.
- **No kickoffs:** every quarter opens with the ball at the offence's 25 (`start_kind` "placement"), and after every score the next possession starts there. The team scored upon takes it; after a safety, the scoring team.
- **Quarters:** the possession in progress ends when any quarter ends (`end_of_quarter` after the first and third). Possession alternates at the start of each quarter from the opening coin toss. Timeouts reset at each half.
- **Draws:** quarters 1 to 3 draw as first-half windows of 15:00 that end the possession, quarter 4 as the second half's last 15:00 (late cells). The play-level exhibition rules (two-minute warning each quarter, late-quarter clock, play clock, defensive restrictions) are not modelled; drives stay real 2012 regular-season drives.
- **Overtime:** the regular-season rules, opened at the 25.
- **Checks:** `validate_result` and `check_ledger` replace the kickoff and second-half-receiver checks with the quarter rules (every quarter opens at the 25, possession alternates, no possession crosses a quarter, no kick rows). 300 synthetic Pro Bowl games at acceptance: zero validation errors and zero coherence violations; `tests/test_pro_bowl.py` replays 80 each run.
