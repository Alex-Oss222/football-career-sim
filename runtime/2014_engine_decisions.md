# 2014 strength, development and in-game availability

[Defect register](defect_register.md) · [Player development](../career/2014/00_Team_Operations/Player_Development/README.md)

**Decision record:** Stone approved E1 and E2 in the September 28–29, 2026 follow-up to PR #132, with the branch still at February 2, 2014. This adopts their policy, including team construction and coaching, without releasing a kernel. Kernel 2014.3 remains installed; Tier 1 remains open. No 2013 receipt, rating input or outcome is rewritten.

<!-- event-record: {"closure": {"checkpoint": "Canonical correction - February 2, 2014 - 2014 operating handoff and readiness reconciled", "sequence": 82, "through": "2014-02-02"}, "date": "2014-02-02", "id": "2014-02-02-2014-operating-handoff-and-readiness-reconciled", "kind": "technical", "status": "closed", "summary": "2014 operating handoff and readiness reconciled."} -->

## Implementation status checked September 30, 2026 (phase 3: release wired)

| Piece | Present behavior | Required before claiming completion |
|---|---|---|
| Unequal team strength | Kernel 2014.4 (installed September 30, 2026; live private runtime verification pending after merge; centring adopted at the 2012 study centres, the real-2014-depth-chart alternative noted and not taken): `runtime/strength.py` builds each club's dated evidence record (`TeamInput.strength`, same rule for Jacksonville) from two pre-divergence streams, 2011-2012 honours and two-pass verified 2011-2012 production tiers (`library/2010_2012_production_evidence.md`; 2010 as a discounted fallback), and the kernel scores each drive's actual available lineup (runtime/README.md, kernel 2014.4 candidate and its second-pass acceptance). Phase 2 (E1 phase 2 acceptance): six matchup sub-composites per drive with three fitted terms (passing and run defense on touchdown share, protection on sack rate), offensive-line job evidence (unproven lineman -1), a punter term, the field-goal distance model and a layout resample; net implied edge SD 0.0328 (68% of target); roster coverage 1,171 of 2,004 inventory players. Coverage, rush, interception and run-offense terms carry no fitted signal (slope 0). 2013 inputs keep the Average anchors | Live private runtime verification of the flipped kernel (runtime/season_readiness.json); later: shared-assignment composition and communication badges, depth and help tradeoffs, coaching tradeoffs |
| Offseason player progression | Live roster-derived cohort, position-specific trait registry, causal case validation, hidden-versus-observed state contract and externally calibrated transition interface are present | Calibrated priors, private persisted latent states, player evidence coverage, matchup consumption and release validation; the new foundation does not change a game draw by itself |
| Coaching contribution | Living [Stone](../career/coaching_profiles/alex_stone_coaching_profile.md) and [staff](../career/coaching_profiles/staff_profiles.md) assessments now trace supported choices and open questions | Consume only scoped evidence and actual installed/selected work; model benefits and costs without an overall coach bonus |
| Live injury substitution | Kernel 2014.4 (installed September 30, 2026): `runtime/kernel.py` draws onsets at the end of each drive from recorded exposure (`runtime/participation.py`, `runtime/injury_model.py`), removes the player from every later role, promotes by depth on both clubs, lets a backup pass, and for a consequential Jacksonville removal returns a partial result with a token-bound continuation (`runtime/game_runner.py`). `scripts/close_week.py` runs Jacksonville user controlled, records the pause in the week folder's `paused_game.json` and resumes with `--continue ANSWER.json` through the same event reference (phase 3, wired) | Live private runtime check after merge, then acceptance of the tier1_engine gate |

The documentation work completes the decision and evidence-recording method. **E1 (first pass, the second pass adding dated production evidence and tier-weighted attribution, and phase 2 adding matchup sub-composites, offensive-line job evidence, special teams and the field-goal distance model) and E2 are implemented on the kernel 2014.4 candidate and accepted on the synthetic samples, a synthetic slate over the real 2014 inventory, a label swap on real inputs and a 306-game 2013 replay (September 30, 2026; runtime/README.md); no 2014 game has run on it. Phase 3 (September 30, 2026): the user approved the result-changing release and kept the 2012 study centres; `KERNEL_VERSION` and the service `KERNEL` read 2014.4; `scripts/close_week.py` carries the E2 pause for Jacksonville. Release pending live verification: the flipped private runtime is verified only from merged `main` (`runtime/season_readiness.json`, tier1_engine, records the command sequence), after which that gate may read VERIFIED. The user's standing decision: no 2014 game until strength is built properly, with no real 2013 data, no Madden and no market totals.** Existing 2013 outcomes remain closed; they are not training labels for a team/coach talent model.

## E1: build football differences from the people and the job

Teams need different capabilities, vulnerabilities and ways to play. A single club grade cannot describe those differences. The implementation must follow the causal path from an available player, through an assigned job and supporting unit, to the actual matchup. A good roster can be poorly deployed; a limited roster can find a favorable matchup. Neither has a guaranteed result.

### Evidence and uncertainty

| Evidence | Permitted use | Limit |
|---|---|---|
| Dated public evidence before the actual divergence | Starting physical, technical and processing assessment, with source and observation scope | Do not use real post-divergence careers, rankings or results to fill a gap |
| Permitted rookie scouting available at the relevant branch date | Initial hypotheses for the relevant jobs | Draft slot, reputation and contract cost are not ability measurements |
| Dated branch practice and football observations | Refine a specific skill or reliability assessment; document instruction and conditions | A planned drill is not an observation; a same-session correction is not durable growth |
| The branch's completed 2013 season | Experience, roles actually held, situations encountered and review locators | Win totals and point differential cannot establish talent; the equal-strength engine generated them |
| 2013 individual statistics and generated explanations | Locate the underlying play and identify questions | Do not infer processing from an interception, blocking from a randomly charged sack, or ability from production by depth |
| Current roster and dated transaction rails | Identity, control and available lineup | No ability, future injury or future award inferred from them |

*Dated scope note (October 2, 2026):* Stone's adoption of draft-slot starting estimates for kernel 2014.6 supersedes the draft-slot row only for the engine's hidden-state prior of a player with no pre-2013 record. The row still governs scouting, staff assessments and every reader-facing judgment ([Kernel 2014.6 decisions](#kernel-20146-decisions-dated)).

Each evidence receipt needs stable player ID, source locator, source/public date, observation date, allowed branch cutoff, dimension/job, direct observation versus inference, applicable conditions, confidence and known contamination. Reject future-dated evidence before composing an input. Keep disputed and contradictory observations visible. A low-confidence Average fallback means insufficient knowledge, not verified league-average ability.

Use position-specific evidence and keep the private matchup conversion separate from user-facing summaries. The annual player sheet may show the user a dated /10 personnel grade and plain-language NFL standing. Those fields are descriptive snapshots only: they are not potential grades, permanent archetypes, personality scores, probability inputs or a substitute for the underlying traits. Separate what a player can physically do, what he understands, what he has executed reliably and what has not been observed. Established capabilities carry forward by default; skill changes only with a stated football reason.

### Team construction and matchup

| Component | What must affect the relevant resolution | What cannot substitute for it |
|---|---|---|
| Pass protection | Actual five linemen, assigned help, back/TE responsibility, pressure source, exchange communication and QB answer | Average all offensive talent into one pass bonus; blame the tackle for any sack |
| Passing | QB recognition, timing and placement; actual routes, separation and spacing; coverage/help and rush timing | Give a star receiver's value to every target or count protection help twice |
| Running | Blocking jobs against the called front, leverage, runner track/read and available space; pursuit and tackling | Treat rushing average as an individual runner rating |
| Coverage and pressure | Actual coverage personnel, leverage, help, matchups and rush/contain purpose | Charge every completion to the nearest defender or every low sack total to weak rushing |
| Special teams | Designated snapper/holder/kicker, protection, punt/return instructions and actual coverage roles | One generic special-teams strength or random returner selection |
| Depth and availability | Relevant eligible replacement, changed package and losses of specific capability | Clone the starter's ability into the backup; double-charge an injury as a global morale penalty |
| Continuity and fit | Evidence of shared calls/exchanges and familiarity with the assigned work | Automatic chemistry for years together, popularity or a successful record |

The unit is not a simple average of stars. A weak protection link matters when exposed, and help can address it while taking a receiver out of the route. A coverage shell can protect a corner while conceding something elsewhere. A powerful run front can be less suitable for a passing situation. These tradeoffs must be represented by the same available-player and assignment model on both sides.

### Unit communication, execution and individual playmaking

Stone's September 29, 2026 clarification applies the same two assessments, **Communication** and **Plan execution**, separately to offense and defense, while retaining the capabilities of each actual player. The install and development standard applies equally to both units. This refines E1's required behavior; it does not implement or release it.

On offense, communication covers organizing the eleven, recognizing the defensive picture, sharing protection/blocking and route adjustments, using verbal and visual signals, and staying connected when the picture changes. Execution covers the assigned blocking, exchanges, timing, spacing, reads, throws, catches and ball security. Assess the actual offense rather than making quarterback command stand in for the whole group.

Communication covers the defense operating together: receiving the call, recognizing the offensive presentation, identifying man or zone/match responsibilities, passing verbal and visual adjustments, and responding together as motion and routes change the picture. The helmet receiver is one participant, not the whole assessment. Plan execution covers carrying out the intended fits, leverage, coverage exchanges, pressure, pursuit and finish. A scheme mismatch, physical loss or deliberate concession is distinguishable from players misunderstanding one another.

Show each badge with the existing qualitative tiers, the applicable lineup/package, supporting observations and uncertainty. It summarizes the evidence for that group, not a sum of completed communication steps or a permanent club trait. Missing evidence stays unassessed. A substitution can change the group's operation without erasing every returning player's experience. No badge is awarded in this planning update.

The resolver must use each unit's relevant shared-assignment evidence alongside the offensive and defensive calls and actual matchups. Do not stack badge bonuses on top of the same player/continuity evidence or make the labels independent success rolls. Either unit can communicate correctly and still be outplayed; an individual can rescue a breakdown without making that breakdown disappear. Do not reduce the contest to comparing two overall unit badges.

Preserve offensive playmaking on the same terms as defensive disruption. A blocker can win despite unfavorable numbers, a receiver can beat sound coverage, a runner can create yards beyond the blocking, and a quarterback can anticipate an opening or extend a play. Use the actual ability, available information, taught freedom and effect on teammates. Evaluate the action and its assignment consequences separately from the result: a rescued completion does not erase a protection misunderstanding, and an incompletion does not itself prove poor communication. The active offensive book's protection, adjustment and scramble rules supply the assigned work, without awarding unsupported freedom or guaranteed success.

Preserve individual disruption and anticipation. A lineman can defeat his blocker early enough to spoil a sound offensive concept. A coverage player can recognize a tendency, win his matchup or make an informed departure from the expected movement. Represent his actual ability, available cues, coaching freedom, timing and the help or space he leaves behind. A correct anticipation, physical win, failed gamble and missed assignment are different events. Neither automatic punishment for improvisation nor unrestricted star immunity is acceptable. Historical reputation and future careers cannot supply a 2014 rookie's abilities or guarantee an outcome.

When implementing E1, verify on both sides that a supported communication difference changes the relevant exchanges without changing individual physical technique. An offensive protection/route misunderstanding must remain distinguishable from a lost block or coverage win. A supported individual receiving, running or quarterback advantage can create a play against sound defense, just as a rush advantage can disrupt a sound offense, with communication held constant. A failed anticipation or improvisation exposes its actual assignment cost on either side. These are required checks for the future implementation, not tests claimed to pass today.

Football basis: [Belichick's September 24, 2013 explanation](https://www.patriots.com/news/bill-belichick-conference-call-transcript-191316) describes rapid shared decisions against motion, splits and bunches; [LeBeau's September 20, 2012 comments](https://www.steelers.com/news/coordinator-s-corner-haley-lebeau-8328896) describe safety freedom changing with the tandem. [McCourty's January 27, 2017 explanation](https://www.patriots.com/news/devin-mccourty-press-conference-transcript-1-27-289476) supplies a later instructional account of distributed verbal and hand-signal communication. The latter is background explanation, not 2014 player evidence or a branch event. These sources support the football relationships; the badge presentation is Stone's requested simulation design.

Offensive assignment basis: the active [Iteration I book](../career/playbook/alex_stone_2013_offensive_playbook_iteration_i.md), especially its Pre-Snap Five, Freedom Package, protection and Movement and Scramble Rules. These define taught responsibilities and available choices; they do not establish that a particular player has mastered them.

### Coaching without a magic multiplier

Coaches affect the taught menu, clarity of shared rules, practice allocation, scouting hypotheses, available adjustments, substitutions and actual calls. Those choices create opportunities and costs. Staff reputation alone adds nothing to a draw. A sound plan may meet an effective counter; an ambitious install can remain poorly communicated. An observed teaching failure belongs in that shared-job assessment before a player is downgraded.

Store the plan that was actually installed and the evidence that its participants can operate it. Record responsibility for an unresolved rule. Do not create hidden access to an opponent's intentions or guarantee a correct coach adjustment. The same permitted scouting information, decision budget and rule set govern background coaches. Stone's prose, desired outcome and protagonist status do not change the odds.

When reporting a play, describe only causes represented by its event record or independently observed evidence. The current kernel's generic processing sentence after an interception is not a scouting observation. Narrative must not invent a detailed technical cause to make a coarse draw look richer than it is.

### Development stays open

The full season belongs to the player even when the old engine cannot support a talent inference. Preserve experience and established practice strengths. Revisit the player's own interpretation, preferences and questions when actually expressed. Compare multiple plausible explanations and give him a suitable opportunity to demonstrate more, rather than funneling him toward a preselected type.

Review at phase handoffs, a material assignment change, return from a restriction, or a coherent new body of evidence. The previous proposal for automatic four-game review blocks is superseded. There is no calendar-triggered upgrade, compulsory one-tier step, fixed age curve, XP, guaranteed breakthrough or growth penalty for voluntary absence. An assessment may stay the same, gain confidence, narrow its scope, broaden, or be revised downward. Any material change must explain the evidence and uncertainty.

*Dated scope note (October 2, 2026):* the fitted aging and experience curves adopted for kernel 2014.6 are population priors on the hidden engine value, not a development rule, and staff assessments never read them; this section still governs staff assessment and the development program ([Kernel 2014.6 decisions](#kernel-20146-decisions-dated)).

Separate **lineup change** from **development**. Replace an unavailable player immediately in the next applicable input; do not wait for a review block. A player learning a new job does not lose his established capability in a familiar job. Medical recovery is not a lesson that attendance or effort can accelerate.

### Practical league build

1. Join the existing league IDs and dated roster/control records to permitted evidence. Preserve provenance and unresolved identity joins. Automated public-data joins can supply identity and source indexes, not manufacture individual scouting conclusions.
2. Cover every projected starter, specialist and first relevant replacement by job. A coverage report must show supported dimensions, unresolved dimensions and explicit fallbacks for all 32 clubs, including Jacksonville. Other players remain individually identifiable and get appropriate assessment when an actual role requires it.
3. Audit sources and contamination, then compose available lineups and shared assignments. Prevent duplicated evidence from masquerading as independent support. Do not transplant a departed player's value with his old team's aggregate.
4. Connect matchup components to the common resolver. `scripts/build_week_inputs.py` currently supplies unconditional Average values; `runtime/anchors.py` is not an implemented player/matchup system. Merely changing three broad TeamInput numbers does not close E1.
5. Calibrate internal mappings against permitted aggregate evidence and predeclared synthetic checks. Fix seeds and acceptance criteria before inspecting outcomes. Preserve older versions for receipt reproduction. Do not tune until Jacksonville reaches a desired record.

### E1 acceptance gates

- Swap team names and protagonist status while preserving causal inputs: the distribution remains unchanged.
- Hold scheme and personnel constant, alter one supported relevant capability: the corresponding matchup changes in the expected direction. An unrelated matchup does not receive a bonus.
- Change help or personnel: the benefit and opportunity cost both appear. More talent does not guarantee every individual play or game.
- Reject future evidence and unsupported direct imports from 2013 win totals. Display missing coverage and confidence; do not silently mark the league researched.
- Substitute a backup: the actual backup's relevant profile is used. Compare sampled distributions, not a single lucky game.
- Qualitative reports trace to real evidence or an explicitly limited mechanical event. No outcome-generated scouting loop and no invented hidden opponent knowledge.

## E2: removal is automatic; consequential coaching choices are live

A medically unavailable player leaves automatically. Stone cannot override removal. Pause a Jacksonville game for an important replacement or tactical choice; use a previously authorized depth contingency for routine replacements. Background clubs use the same injury, exposure, medical and eligibility mechanics with autonomous coaching choices.

### Required event sequence

1. Resolve an eligible participation interval and record the actual participants and exposure. Freeze injury onset and disposition at its legitimate event boundary. A drive-based first implementation must use end-of-drive onset explicitly; it cannot backdate an injury to an earlier snap while leaving the player on later snaps in that drive.
2. Remove the player from all subsequent affected roles, including return/coverage and emergency packages. Clear all cached starter/usage choices. Projected return dates cannot override an independent medical hold.
3. Determine legal available substitutes and any package consequences. If no legal personnel solution exists, stop for a valid resolution; do not create an eleventh player or reuse an unavailable one.
4. For a consequential Jacksonville choice, return a genuinely partial receipt: score, clock, completed events, eligible choices and known medical availability only. Do not generate or expose the final score, future opponent decisions or later injury draws.
5. Record the selected eligible replacement and authorized tactical changes in a continuation decision. Reject stale or altered choices and any attempt to change completed events, the frozen injury, the original packet or unrelated information.
6. Resume from the same partial game and private random state. Preserve the prefix exactly. The choice may affect future football outcomes; it must not reroll the original injury or replay completed possessions.
7. Recompute actual personnel, usage and relevant matchup inputs. A backup quarterback can attempt passes; more than one passer is legal. Attribute subsequent snaps and credits to the participants, not the game-opening lineup.

An important substitution includes a quarterback, designated caller, featured role or unavailable player whose removal changes the legal package. The coach's approved contingency can cover ordinary depth replacements; absent such a contingency, do not silently assume a new tactical preference. Pause before the next affected play/possession, never after the game has already been decided. No pause allows unavailable participation while the user thinks.

### Current-code gaps

Kernel 2014.3 resolved the game before its injury loop and created its user-controlled pause after resolution; that was not a resumable live injury decision, and its one-passer validation rejected backup passing. Kernel 2014.4 (installed September 30, 2026) replaces this: onsets are drawn at each drive's end from recorded exposure, the removal applies to every later role, the pause returns completed events only with a continuation token bound to the partial state, resuming re-runs the same packet from the same private event reference so the prefix and the frozen injury reproduce, and the validator distinguishes the game-opening front from later legal substitutions. `scripts/close_week.py` now requests `management_mode="user_controlled"` for Jacksonville and carries the continuation (`--continue ANSWER.json`), so a pause reaches the user in the weekly closure. The private service needed no closure change (idempotent for the unchanged packet); it journals the kernel change on its live store (`kernel_transitions`). Still open: the live service must be verified on 2014.4 after merge.

### E2 acceptance gates

- Force an onset at a known boundary: no affected participation or credit occurs afterward for the removed player, on either side.
- Force QB1 removal: QB2 throws legally and both individual lines reconcile to team totals. Test defense, OL, returner and specialist replacements too.
- A pause has no future events or final result. Resuming with the same choice reproduces the same suffix; choosing a different legal player preserves the prefix and original injury.
- Reject an inactive, absent, held or newly injured replacement, duplicate personnel and tampered continuation data. Handle exhausted depth explicitly.
- Normalize position aliases and derive risk from actual exposure, including special teams. Zero participation creates no participation injury. Source class/severity/onset denominators before calibration; no arbitrary head/neck share.
- Physical and cognitive restrictions remain separately authoritative. A date projection is not clearance; the simulated coach does not make a diagnosis.

## Decisions of October 2, 2026 (after Week 2 of the 2014 season)

Stone adopted three recommendations on October 2, 2026, with the branch at September 14, 2014, before Week 3 is run. Each is recorded here as the E1 policy record requires; nothing below rewrites a closed game, a receipt, a rating input or a result.

### Kernel 2014.5: call labels follow the sheet's situational menus (engine change, labelling only)

**Decision.** The call-label stream must condition on the game situation. Through kernel 2014.4 each generated snap took its descriptive call uniformly from the frozen sheet's family-compatible calls, with no regard to down, distance, field zone or clock. The 2014 Week 1 and Week 2 play-by-play therefore recorded calls nobody made (Snag, a low-red-zone-only call, in the open field; the Dagger kept to third-and-long on third-and-1; the Power Pass shot on backed-up snaps; the opener's first call "unsent"; a Jacksonville pass with no sheet label), and the game reviews charged Cousins and the sideline with decisions that were artifacts of the label draw. From 2014.5 a snap takes its label from the sheet menu that matches its walked down and distance, its zone, the half clock and the score, or from the opening sequence in the packet's order with its returns, falling back to the nearest menu, then the sheet's unrestricted calls, then a generic label, and records which path labelled it (`label_source`, `situation`, `script_position`). A call confined to a menu (Snag on the low red zone; a shot kept to one menu) can appear only there. A stated condition on a call stays coaching guidance on the sheet and is not modelled as a probability. Full method: `runtime/README.md`, kernel 2014.5; the classification conventions come from the active 2013 iteration's section 15 and the weekly packets' third-down scripts.

**Acceptance evidence.** `tests/test_call_situations.py`: `OutcomeInvarianceTests` runs the same seeded games under the Week 2 sheet with its menus and under the same sheet stripped of them (the 2014.4 rule) and asserts identical final score, possessions, kickoffs, team and player statistics, injuries, substitutions and every snap-ledger field but the labels, with a byte-identical outcome packet; `SituationalLabelTests` prove Snag labels only inside the 10, a probe call kept to third-and-long never lands elsewhere, every menu label is a menu the snap is in and the call declares, the opening sequence runs in script order, and ledger coherence is zero; the 40 identity digests and the 250-game sample's results reproduce. The mechanism that keeps the result identical is the label stream's own keyed RNG substream, separate from the possession, chain-layout, snap-detail and kickoff streams since kernel 2013.7, and the exclusion of the menu and opener fields from the outcome packet.

**Boundary.** Menus are label sources for narration and call statistics, never a mechanism that changes who plays, which package is used or what succeeds (the no-percentage rule). Closed games keep their 2014.4 labels and are not regenerated; the Week 1 and Week 2 reviews' sideline-procedure findings are closed as an engine artifact in `runtime/defect_register.md` (item 25). The kernel version is `2014.5` in the repository and `runtime/season_readiness.json` accepts it; the private service deploys from merged `main`, readiness fails closed on the kernel mismatch until that deploy completes, and the live verification follows the merge. No snapshot advance.

### No individual passer interception term (recorded, no engine change)

**Decision.** No individual passer interception term is adopted. Study: `library/passer_interception_persistence_study.md` (research only, October 2, 2026). The season-pair persistence of a passer's own interception rate is a weak skill resting on one of the two pre-divergence season pairs, and Cousins's pre-divergence record (51 dropbacks) shows a near-zero deviation from the league rate, so a term would add a fitted parameter with no evidence that it would move his own draws anywhere. The interception channel keeps the kernel 2014.4 phase 2 result: the passing composite fitted on the 2012 per-drive interception share and dropped with slope 0 (`library/2014_strength_calibration.md`, section 10). Decided once on this evidence; not revisited on the same evidence. The E1 rule stands: no real player's post-divergence outcomes ever set his own value.

### The 2012 calibration base stays through the 2014 season (recorded, no engine change)

**Decision.** The 2012 calibration base (`library/2012_*` and the calibration tables the kernel reads) stays through the whole 2014 season: no mid-season base change, whatever the band audit reads, and an OUTSIDE row remains an investigation item, never grounds to rerun, select or edit a closed result. Any roll-forward of the base is a season-end policy decision for 2015, taken with the post-divergence caveat: real league base rates for a later season may be considered as a league population, but no real player's post-divergence outcomes ever set his own value, and the 2013 and 2014 branch results are never calibration evidence of talent. The rulebook's era note is not edited by this record (foundation/ is not in scope); this file and `runtime/README.md` carry the decision.

*Superseded October 2, 2026* for league rates and fits from Week 5 by Stone's decision U1(b): the 2010-2014 league base, frozen at Week 5's first event for the rest of the 2014 season, arrives with kernel 2014.6; Weeks 1-4 stand as played on the 2012 base ([Kernel 2014.6 decisions](#kernel-20146-decisions-dated)).

## Kernel 2014.6 decisions (dated)

**Record.** Stone made these decisions on October 2, 2026, with the branch at Sunday, September 28, 2014, after Week 4 (Document 5) and before any Week 5 event. His words are quoted verbatim from the session, with the time (UTC). A **default** is a call Claude stated to him on October 2 that he did not object to; it is recorded as his decision on that basis and he may override it. Nothing here reruns a closed game, edits a receipt or changes a 2013 or 2014 Weeks 1-4 result. Kernel 2014.5 and the 2012 base stay installed until kernel 2014.6 is released (plan batch B18). Until then every 2014.6 mechanism is built behind a frozen profile that production cannot select. The rules every batch must follow are frozen in the [pre-build specification](../library/2014_6_pre_build_specification.md) (sha256 `2ce1018dee17052aa9e59bff8e80b2639f085376dd91310210417cb9aa53d70d`).

### Scope: the full plan before Week 5

- Stone's list of fixes (12:33): "make fixes for A first half can end in field-goal range with no kick tried." It goes on through two-point tries, onside kicks, late field goals, penalties, fumbles, overtime, return touchdowns, rushing yards, first-half finals, season leaders, weather and venue, background promotions, the 2014 downfield-foul emphasis, defensive calls, the Week 3 field goal and substitution record, the Week 4 muff and timeouts, and ends "Timeouts are tracked per possession, not per snap. before week 5".
- Then (15:10): "make the fixes and and let me know when we can start again".
- Given the full release, a split release or playing Week 5 on the current engine, he chose the full release (18:59): "we can wait until done to fully so 5". Week 5 waits for the release.

### U1 (b): the 2010-2014 league base replaces the 2012 base from Week 5

- Stone's words (12:35): "earlier you recomend dont add information for 2010-2012 i say expand now from 2010-2014". And (12:38): "remember to model player states we used 2012 averages , lets update and expand realistically".
- Scope: the league base from Week 5. That covers drive pools, game rates, band centres and every league effect fit (strength terms, weather terms, penalties, scoring charts). Claude confirmed at 12:36 that the wider window replaces the October 2 decision to keep the 2012 base, and the full release he chose at 18:59 carries it.
- This **supersedes** "The 2012 calibration base stays through the 2014 season" (above) for league rates and fits from Week 5. Weeks 1-4 of 2014 stand as played on the 2012 base, and the 2014 views show two cohorts.
- Data: the 2010-2013 regular seasons and 2014 Weeks 1-4, the 61 games through Monday, September 29, 2014. The base is usable from September 30 and frozen at Week 5's first event (Thursday, October 2, 2014, Minnesota at Green Bay) for the rest of the 2014 season. No later base change follows whatever the band audit reads. An OUTSIDE row remains an investigation item, never grounds to rerun, select or edit a result.
- Post-divergence caveat: the pooled fits contain every club's and player's own 2013-2014 rows as anonymous league data. Those rows never set that same club's or player's value, and no per-club or per-player 2013-2014 outcome row is committed.
- No branch receipt, branch audit reading or branch result entered any fit, centre or weighting choice. The design read branch receipts only to measure the installed kernel's behaviour (defect evidence). Seasons are weighted equally per event: the fitted recency half-life failed its test and is not adopted (specification, section 2).
- The rulebook's era note (foundation section 8) is not edited by this record. Authorization to name the new base there is needed later.

### The player-state policy (A to D)

- Stone's words (12:59), adopting word for word the four points Claude had recommended at 12:48: "with A player's real career up to 2012, carried forward on aging and experience curves pooled across every player from 2010 to 2014. Draft-slot starting estimates for players without that record. Your recorded once-per-season swing, with its size and carryover fitted from the data rather than chosen, drawn by Railway for every player. Your capped feedback idea, applied to what the branch can honestly observe: snaps played, role held and availability. The weight would come from a fit, not set at 20%."
- Scope: hidden-state statistical priors for the engine only. They are never scouting evidence and never a staff-facing grade. A real player's own 2013-2014 statistics never set his own value. Branch production (yards, sacks, interceptions) is not feedback; only snaps, role and availability are, as his words state. The private service draws and records each player's season swing. No one sees the drawn values: not Stone, the staff, the reports or Claude. Only the public expectations and a commitment hash are visible.
- **Staff assessments, grades and E2 advice never read player-state values or tiers.** The AGENTS.md line for this awaits approval; until then the rule lives here and in `runtime/README.md`.
- The evidence table's draft-slot row ("Draft slot, reputation and contract cost are not ability measurements", E1 above) still governs scouting, staff assessments and every reader-facing judgment. Stone's adoption of draft-slot starting estimates supersedes it only for the hidden-state prior of a player with no pre-2013 record.
- "Development stays open" ("no calendar-triggered upgrade, compulsory one-tier step, fixed age curve", above) still governs staff assessment and the development program. The fitted aging and experience curves are population priors on the hidden engine value, the same for every player of a family. They never trigger a staff upgrade or downgrade, and a family that fails its test has no curve.
- A dated pointer note is added to the [progression model](../career/2014/00_Team_Operations/Player_Development/progression_model.md).

### U2 to U8

- **U2 (default):** the 2014 Weeks 1-4 emphasis-foul level persists through Week 17, as a season-long officiating directive. There is no separate completion tilt; completion follows the pooled base.
- **U3 (default):** the strength keep rule applies symmetrically. A live term that fails on the 2010-2014 refit goes to slope 0 (protection-to-sack may turn off), and a newly passing term becomes live (for example the unit passing-to-interception term). The individual passer interception term stays not adopted (decided once on October 2, above); a unit composite term is a different term and follows the keep rule.
- **U4 (default):** draft-slot estimates use each player's real selection slot, or undrafted status, for every club, Jacksonville-controlled players included, so Jacksonville's own draft choices cannot raise anyone's estimate. This is the one use of a real selection fact for a Jacksonville player, and it is limited to the hidden-state prior.
- **U5 (default):** the player-model amendments made after early results were seen are accepted and disclosed as not blind (the 2014.4 study precedent). Amendment 2 replaces the delta method with forecast residuals. Amendment 3 covers the two-pass conjunction for aging, the negative-sign rule for draft slopes, the 30-event minimum cell, and the tier population defined on the committed production-evidence qualifier floors. If overridden, every family gets zero aging and flat rookie estimates.
- **U6 is not answered.** It covers Stone's two-point and onside-kick rule for Jacksonville, or a dated delegation such as "otherwise follow the league default". The mechanism accepts either a live pause or a call-sheet block (`decisions.two_point`, `decisions.kickoff`), and Jacksonville's user-controlled inputs fail closed without one. No agent writes this decision; Stone's answer arrives with the Week 5 call sheet.
- **U7 (default):** a background club that cannot dress a legal 46 from its real roster records a dated, 2014-legal background transaction. That is a practice-squad signing to the 53, paired with a reserve/injured placement of that club's longest-held unavailable player, under one rule for all 31 clubs. Claude stated it to Stone as "If a background club can't dress 46, it makes a dated, legal practice-squad signing."
- **U8** (a graded row still OUTSIDE after acceptance) has not arisen. It is never auto-registered.
- **Plan defaults 1B.1 to 1B.14 stand as written in the plan.** They cover:
  - equal weight per event;
  - altitude terms at slope 0;
  - static venue facts plus 2010-2013 climatology, with no 2014 file read at runtime;
  - the participation slot convention unchanged;
  - defensive records labelled deterministically from Stone's sheet;
  - an on-field player still choosable as an explicit reassignment;
  - the DB slot-family base four;
  - the opening overtime onside cell;
  - a trailing overtime punt weight moved to downs;
  - family-free player draws with the z-transfer;
  - the usage swing at sigma 0;
  - no second returners;
  - role feedback at slope 0 for the 2015 transition, availability from 2015 and snaps at 0;
  - no Week 1 PUP, NFI or reserve additions, with suspended players added as available.

### Fourth downs: Stone's live call (batch B9F, added to the plan)

- Stone's words (18:55): "Fourth downs remain my call. I want the decision prepared before third down whenever possible. Skalaski gives me distance, field position, score, timeouts, clock and the kicking information; Tice gives me the best prepared conversion call."
- Through kernel 2014.5 the engine decides every club's fourth downs inside the drawn drive, Jacksonville's included, so this standing instruction has had no effect.
- What Claude told him (18:55), with no objection:
  - a Jacksonville game pauses at each fourth down, as it does for a key injury, with Skalaski's information and Tice's prepared conversion call;
  - Stone answers go, field goal or punt, and gives the call if he goes;
  - the result comes from conversion, field-goal and punt rates measured on 2010-2014 data, with the same matchup terms used for every club and no bonus for the user's team;
  - the other 31 clubs decide by the 2010-2014 league decision chart.
- The decision source is an input, never a probability shift. A pause shows only what the staff would supply; the engine's hidden make probability is never shown. B9F freezes its own rules in its design record before its code.

### Other inputs in force

- The 2014 points of emphasis are modelled before Week 5, from Stone's list.
- The other 31 clubs' in-season roster rails, with the over-53 rule "hold, never invent", are built separately (branch `rails-2014-6`) and reach this build before batch B15.

### The uploaded snap estimates and evidence builder: not used in 2014.6

- The snap estimates uploaded under `docs/football_snap_estimates (1)/` were fitted with full-season 2014 data; most of the 2014 rows are from Weeks 5-17, beyond the information gate. Their positions came from the current player database, and they were partly built from the same production statistics the fits use. They are not used in kernel 2014.6, and never for availability.
- Any later use needs a guarded rebuild:
  - trained only on real 2013 snaps and 2014 weeks public at the time;
  - each player estimated by a model fitted without his own rows;
  - positions from that week's roster;
  - a `measurement` label kept apart from observed snaps;
  - never a reader-facing statistic;
  - never a denominator for per-snap rates of the statistics it was built from;
  - fitted weights corrected for measurement error by position group;
  - special-teams share and fullbacks kept out of fitted weights;
  - CC BY 4.0 attribution.
- The `free_nfl_evidence` package is not adopted. Its fixable ideas (status-aware availability, club-code mapping, a divergence gate) may inform a committed builder.

### Design scratch hygiene

- The design phase's scratch trees held full-season 2014 and post-2014 files. In B0 they were moved out of those trees, with a manifest (sha256, size, original path), and are never read again:
  - 39 full-season 2014 files, plus 6 links to them removed;
  - 10 post-2014 files, plus 1 link;
  - the 2013 season-aggregate player statistics;
  - 67 products derived from full-season 2014 (the snap-estimate reproductions, the audit's training sets and the scratch tilt refit).
- The scratch file holding real Jacksonville club rows (`context/p1_plan.csv`) was deleted.
- The scratch strength tilt refit (`tilt_refit.py`) read full-season 2014 season statistics; nothing from it is adopted.
- The full-season 2014 weekly player-statistics sums printed once by mistake in the design phase entered no value.
- No scratch output is promoted into `library/data`. Only committed builders produce artifacts, and they cut 2014 at fetch.

### Needed later (not decided here)

- Authorization to name the new base in the rulebook's era note (foundation section 8).
- Two AGENTS.md workflow lines, which await Stone's approval: Run Week N step 4 builds the week's `conditions.json` inside `build_week_inputs.py` once kernel 2014.6 ships, and staff assessments, grades and E2 advice never read player-state values or tiers. Until approved, both live here and in `runtime/README.md`.
- Week 1 PUP, NFI and reserve treatment and the library rule 6 use of real later recovery dates; role feedback before the 2015 transition; observed weather as a rail; per-snap defensive calls.

### Release preconditions

`python scripts/research/release_preconditions_2014_6.py` reports, read-only, that there is no pending `paused_game.json`, no journaled-but-unreceipted 2014 event in the local caches, and that the Week 5 inputs are not frozen. It never calls the private service; the service's own journal is checked at release.

## Release boundary

Policy approval is complete and kernel 2014.5 is installed (labelling only; kernel 2014.4 released the Tier 1 fixes on September 30, 2026, and the 2014.5 flip of October 2, 2026 changes no result). The 2014 release stays BLOCKED until the live private runtime is verified from merged `main` and `runtime/season_readiness.json` accepts the kernel; the other 2014 gates (rules, legal rosters, financial control, an isolated closure) remain open. A preseason fixture in the calendar is not permission to run a game. Use the defect register's release process, meaningful isolated tests and season-aware 2014 input/closure paths; never rerun the closed 2013 season.
