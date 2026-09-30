# 2014 strength, development and in-game availability

[Defect register](defect_register.md) · [Player development](../career/2014/team/player_development/README.md)

**Decision record:** Stone approved E1 and E2 in the September 28–29, 2026 follow-up to PR #132, with the branch still at February 2, 2014. This adopts their policy, including team construction and coaching, without releasing a kernel. Kernel 2014.3 remains installed; Tier 1 remains open. No 2013 receipt, rating input or outcome is rewritten.

## Implementation status checked September 29, 2026

| Piece | Present behavior | Required before claiming completion |
|---|---|---|
| Unequal team strength | 2014.4 candidate (not released): `runtime/strength.py` builds each club's dated evidence record (`TeamInput.strength`, same rule for Jacksonville) from two pre-divergence streams, 2011-2012 honours and two-pass verified 2011-2012 production tiers (`library/2010_2012_production_evidence.md`; 2010 as a discounted fallback), and the kernel scores each drive's actual available lineup (runtime/README.md, kernel 2014.4 candidate and its second-pass acceptance). Coverage 67% of inventory starters (offensive line honours-only); the fitted composite explains about 67% of the target edge spread. 2013 inputs keep the Average anchors | Matchup sub-composites (protection, coverage, run), special teams, offensive-line production, shared-assignment composition, coaching tradeoffs and release |
| Offseason player progression | Live roster-derived cohort, position-specific trait registry, causal case validation, hidden-versus-observed state contract and externally calibrated transition interface are present | Calibrated priors, private persisted latent states, player evidence coverage, matchup consumption and release validation; the new foundation does not change a game draw by itself |
| Coaching contribution | Living [Stone](../career/coaching_profiles/alex_stone.md) and [staff](../career/coaching_profiles/staff_profiles.md) assessments now trace supported choices and open questions | Consume only scoped evidence and actual installed/selected work; model benefits and costs without an overall coach bonus |
| Live injury substitution | 2014.4 candidate (not released): `runtime/kernel.py` draws onsets at the end of each drive from recorded exposure (`runtime/participation.py`, `runtime/injury_model.py`), removes the player from every later role, promotes by depth on both clubs, lets a backup pass, and for a consequential Jacksonville removal returns a partial result with a token-bound continuation (`runtime/game_runner.py`). `scripts/close_week.py` does not yet request user-controlled management | Weekly closure wired to the pause, live private runtime check, release |

The documentation work completes the decision and evidence-recording method. **E1 (first pass, then the second pass adding dated production evidence and tier-weighted attribution) and E2 are implemented on the kernel 2014.4 candidate and accepted on the synthetic sample and on a synthetic slate over the real 2014 inventory (September 30, 2026; runtime/README.md); the candidate is not released and no 2014 game has run on it. The user's standing decision: no 2014 game until strength is built properly, with no real 2013 data, no Madden and no market totals.** Existing 2013 outcomes remain closed; they are not training labels for a team/coach talent model.

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

Kernel 2014.3 (installed) resolves the game before its injury loop and creates its user-controlled pause after resolution; that is not a resumable live injury decision, and its one-passer validation rejects backup passing. The 2014.4 candidate replaces this: onsets are drawn at each drive's end from recorded exposure, the removal applies to every later role, the pause returns completed events only with a continuation token bound to the partial state, resuming re-runs the same packet from the same private event reference so the prefix and the frozen injury reproduce, and the validator distinguishes the game-opening front from later legal substitutions. Still open: `scripts/close_week.py` runs every game autonomously, so a Jacksonville pause never reaches the user in the weekly closure until the closure requests `management_mode="user_controlled"` and carries the continuation; and the private service needs no code change (its closure is idempotent for the unchanged packet), but the live service must be verified at release.

### E2 acceptance gates

- Force an onset at a known boundary: no affected participation or credit occurs afterward for the removed player, on either side.
- Force QB1 removal: QB2 throws legally and both individual lines reconcile to team totals. Test defense, OL, returner and specialist replacements too.
- A pause has no future events or final result. Resuming with the same choice reproduces the same suffix; choosing a different legal player preserves the prefix and original injury.
- Reject an inactive, absent, held or newly injured replacement, duplicate personnel and tampered continuation data. Handle exhausted depth explicitly.
- Normalize position aliases and derive risk from actual exposure, including special teams. Zero participation creates no participation injury. Source class/severity/onset denominators before calibration; no arbitrary head/neck share.
- Physical and cognitive restrictions remain separately authoritative. A date projection is not clearance; the simulated coach does not make a diagnosis.

## Release boundary

Policy approval is complete. Implementation, starter evidence coverage, calibration and a new kernel release are still required. Tier 1 clock, chain/distance and injury-rate defects also remain mandatory release work. A preseason fixture in the calendar is not permission to run a game on 2014.3. Use the defect register's release process, meaningful isolated tests and season-aware 2014 input/closure paths; never rerun the closed 2013 season.
