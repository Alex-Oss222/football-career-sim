# Document 7: Game Simulation and Resolution Engine

**Document status:** Design approved, runtime NOT READY. The engine architecture and hidden-layer approach are locked, but the private Engine State store has not yet been instantiated for an active team and §8 era calibration remains incomplete. No game, including a background game, may be resolved from this document until both are complete.

**Lock status:** `DESIGN LOCKED; ERA CALIBRATION PENDING`

**Runtime status:** `AUTHORING MASTER - DO NOT LOAD DURING PLAY UNTIL §8 IS POPULATED`

**Document version:** `0.8-authoring`

**Last verified:** `2026-09-18`

**Last Document 7 content-changing update:** `2026-09-18 - clarified that engine design is approved but runtime state is not yet instantiated, disabled game resolution until §8 calibration and Engine State initialization are complete, reconciled the three output templates, and updated repository/library task descriptions.`

**Supersedes:** Nothing. This is an addition to the existing package, not a replacement of any of Documents 1-6.

## 0. Why this document exists, and why it is not a rebuild

Documents 1 through 6 were modeled on a separate legal-simulation project's document architecture: stable rules, a world/era sourcebook, a protagonist canon, a live-state register, a current snapshot, and an append-only event ledger, all governed by an evidence-labeling system and an atomic staged-commit protocol. That shape is not wrong for this project. Re-reading all six documents in full turned up a large amount of already-built, directly reusable machinery for a live, turn-by-turn simulation:

- Document 1 §3 already separates user-controlled decisions from routine implementation the simulator may carry out on its own.
- Document 1 §7 already defines a layered fog-of-war so the coach only ever learns what a plausible in-world channel would tell him.
- Document 1 §9 already states the *philosophy* of bounded randomness and decision-quality-independent-of-outcome, and Document 1 §11 already defines pregame/live-game/postgame structure, four game-detail modes (Executive, Play-Calling, Critical-Decision, Full Tactical), and a list of pause triggers.
- Document 2 §12 already defines full autonomy for transactions between two non-protagonist clubs, and a real-draft-class-then-procedural-generation rule.
- Document 3 §10 already defines a compressed-turn procedure (batch the whole decision, don't narrate every step) for hiring searches — directly reusable for game weeks.
- Document 6 §6 already defines the bookkeeping format for a game ledger (drive summaries, scoring ledger, per-snap deltas) down to the last reconciliation check.

What none of the six documents ever supplied is an actual **algorithm**: something that takes "this team's pass protection is good, that team's pass rush is elite, it's 3rd and 8 in the fourth quarter" and produces a result. "Bounded randomness within a plausible range" was asserted as a constraint on outcomes, never implemented as a procedure. That gap — not the document shape — is what made the existing six documents unable to actually run a game. This document closes it, and only it.

Documents 1-6 are unchanged by this document except for the small cross-reference additions in §9 below. Nothing here overrides an existing rule; §1 explains the one place this document adds something Documents 1-6 did not already contain.

## 1. The one addition: a non-coach-facing Engine State store

Document 2 §1 already says: *"This document never contains hidden simulator facts... If the platform supports private state, essential hidden state remains there. Otherwise, leave the matter undetermined until a plausible event resolves it."* This document is that private state.

To compare a pass offense to a pass defense, weight a fourth-and-two, or decide whether a hit produces a fumble, the engine needs *some* internal, quantitative handle on player and unit quality. Documents 1 and 3 forbid ever showing the user a number, grade, tier score, or hidden rating — and that rule is unchanged. The resolution is the same one Document 2 already anticipated: the numbers live in a separate store the coach-facing documents (1-6) never reference and the user never sees. The user only ever sees the same five-tier qualitative language (elite / plus / average / below-average / replacement-level) already used elsewhere in this package for evaluation, plus narrated football outcomes. No probability, percentage, delta, or roll may ever appear in coach-facing text. This is a hard rule, not a style preference — a leak of a bare number here is the one failure mode every design reviewer flagged as the real risk of this whole document, and it is the one thing to check for in any output this engine produces.

**Governance.** The Engine State store keeps its own append-only correction ledger, mirroring Document 6's discipline but stored separately: every calibration change, anchor correction, or formula revision is appended with what changed and why, nothing is silently overwritten, and a staged change becomes canon only on an explicit "commit closed" line — the same atomic-commit habit Document 1 §13.2 already uses for coach-facing canon. Unlike Documents 1-6, the Engine Ledger is never coach-facing and is never quoted to the user, even in summarized form.

**Scope discipline (cost control, never adjudication-consistency control).** Corrected 2026-09-18, after a detailed user-supplied review identified the pre-correction version of this section as a real defect: it ran two different outcome adjudicators inside one competitive universe — a structured matchup-delta engine for the protagonist's games, and free-form narrative judgment for everyone else's — even though background results (standings, playoff seeding, draft order, the coaching market) go on to causally affect the protagonist. Cheaper *narration* is fine; cheaper *outcome-generation* is not, because it means two teams' seasons are being decided by different physics.

**Corrected rule: one outcome kernel for every game, leaguewide; narration depth is the only thing that varies by stakes.** Every game — the protagonist's, marquee/rivalry/postseason games, and ordinary background games alike — is sampled from the same §2 rating anchors, the same §3.2 matchup-delta/drive-shape mechanism, and the same §3.4 seeded-randomness procedure. What varies by stakes is narration granularity only:

1. The protagonist's own games, and marquee/rivalry/postseason games leaguewide, resolve at full per-drive granularity (§3-§5), narrated in full.
2. Every other background game resolves through the *same* mechanism, sampled at a coarser granularity (whole-game or a small number of aggregated segments rather than per-drive) to control cost, then narrated in 2-4 sentences of highlights rather than a full account. The final score, box-score topline, and standout performers still come from an actual sampled run of the real mechanism — never from a beat-writer's free-form judgment call about who should plausibly win.

Both paths write to the same schedule/results register in Document 6; a background game's coarser narration is never mentioned to the user as lower-fidelity, and — per §9.1 below — it is never lower-*integrity*: the same causal facts (unit quality, matchup, health, prior form) produce the same distribution regardless of whether the two teams on the field are being fully narrated or compressed to a highlight line.

**Delegated to Codex once runtime-ready.** Per the repo's `AGENTS.md`, background-league weeks may be run as a separate batch task only after this document is runtime-ready, §8 is calibrated for the active season, and the private Engine State store has been instantiated. Until then, the background-league task must stop without generating scores. Once enabled, Codex's task must actually execute the coarse-granularity version of the real mechanism (§2's anchors, §3.2's deltas, §3.4's seeded draw) and narrate only the result — never substitute its own narrative judgment for the sampling step, however plausible-sounding the shortcut seems. Highlights only in the writeup (final score, 2-4 sentences, standout performers, never play-by-play), written to `career/[year]/league_results/week_[NN].md`. Reactive events (a trade demand, a coaching hot seat) are allowed but must fire from an already-logged mechanical trigger, never manufactured to fill a quiet week, per §7's Locker Room/Media agent rule below — this is a hard bound on frequency, not a ban on the events themselves; the user has explicitly said unpredictable, consequential events are welcome as long as they're not happening to someone every single week.

## 2. Rating anchors

### 2.1 Player attributes

Attributes are grouped by position and used only inside the Engine State store; none of these names or values ever appear in coach-facing text, where the same information is expressed only as the qualitative dimensions Document 4 already defines (game performance, physical tools, technique, processing, fit, reliability, projection, confidence).

| Position group | Attributes |
|---|---|
| Quarterback | Arm strength/velocity; accuracy by depth (short/intermediate/deep); pre-snap read and processing speed; pocket mobility/escapability; decision-making and turnover avoidance under pressure; deep-ball touch; play-action/RPO sell; two-minute composure |
| Running back | Vision/patience reading blocks; contact balance; breakaway speed; pass-protection recognition and technique; receiving hands and route running |
| Wide receiver / tight end | Release versus press; route precision and separation quickness; contested-catch ability; yards-after-catch ability; run-blocking (in-line for TE, perimeter for WR) |
| Offensive tackle | Pass-set/anchor versus speed rush; hand technique; run-blocking drive/reach; stunt and blitz recognition |
| Interior offensive line | Anchor versus bull rush; zone/gap run-blocking athleticism; snap-exchange and shotgun/RPO timing (center); blitz-pickup communication |
| Defensive line | Run-gap discipline and anchor strength; pass-rush plan (bend/power/hand usage); motor/pursuit; one-gap versus two-gap fit |
| Linebacker | Downhill run-fit instincts; man coverage; zone coverage and spatial reading; blitz timing and disguise |
| Cornerback / safety | Man coverage technique; zone instincts and range; tackling in space; ball skills/turnover creation; run support (safety) |
| Specialists | Leg strength (kickoff distance/field-goal range); placekicking accuracy under pressure; punt hang time and directional control; long-snap consistency; return vision and burst |
| Cross-position modifiers (never a raw attribute) | Durability/injury-exposure tendency (bounded, historically informed, not a fixed health-point stat); scheme fit (recomputed per scheme, never global); development-trajectory archetype (early/on-time/late bloomer, sampled once and then adjusted by evidence, not a fixed age curve); discipline/penalty tendency; competitive toughness/composure |

### 2.2 Deriving an anchor without inventing a secret "true rating" for a real person

Document 3 §1.6 and Document 1 §8 prohibit treating a real person's actual, undocumented ability as a knowable fact. The conversion below is mechanical and evidence-bounded specifically so it never becomes that:

1. Assign the player's demonstrated, publicly documented performance (through the divergence point, or through the most recent verified evidence for a fictional or post-divergence player) to one of the five existing qualitative tiers, per relevant attribute, exactly as an evaluator would in Document 4's existing evaluation format.
2. Convert each tier to a fixed anchor value on a bounded internal scale via one static lookup table (elite / plus / average / below-average / replacement-level -> five fixed points), identical for every player at that position. The lookup table is the only place a number is chosen; no player ever receives a bespoke, evaluator's-discretion number.
3. Where evidence is thin, contested, or unavailable, the anchor is set to `average` for that attribute and flagged low-confidence in the Engine Ledger — never guessed toward "probably good because he made the league" or any other inference the coach-facing documents would not themselves make.
4. The anchor is a simulation input, not a claim about the real person's actual life; it is never described to the user in these terms and never appears outside the Engine State store.

### 2.3 Team and unit ratings

There is no team-overall number, stored or shown, ever — that would recreate exactly the "single true talent value" Document 1 §6.3 prohibits. A unit rating (pass protection, pass rush, coverage, run game, run defense, special teams, coaching/scheme fit) is instead assembled fresh each week as a snap-weighted composite of the currently available starters' relevant anchors, so it moves the moment a starter is ruled out or returns. Two modifiers layer on top:

- **Continuity bonus:** an offensive line or secondary that has started together multiple consecutive games gets a small additive bonus, reflecting real chemistry effects.
- **Scheme-fit multiplier:** an anchor counts for more or less depending on whether the specific playbook in use (not a global scheme label) plays to that attribute.

### 2.4 Development drift

Anchors drift slowly across a season and offseason through a bounded, sticky update: demonstrated evidence nudges an anchor toward what has actually been shown, but no single game or week swings it sharply, and a real player's own actual future career results are never imported as the answer key for where the drift should land (Document 1 §8's rule, applied to this mechanism specifically). Recalculation happens at the start of each week from the live depth chart and injury report, so a rating layer never goes stale mid-season.

## 3. Game and drive resolution

### 3.1 Unit of resolution

Games resolve at the **drive/possession level**, not down-by-down, except where §3.5 escalates a specific sequence. This is a deliberate middle point: down-by-down resolution for all 32 teams every week was rejected as expensive and repetitive in exactly the games the user watches most closely, while a single whole-game judgment call was rejected as unauditable and prone to drifting toward whatever result reads best. A drive is granular enough to carry real fatigue, injury, and field-position consequences forward, and coarse enough to keep a season's worth of games playable.

### 3.2 Per-drive procedure

1. **Context.** Down/distance, field position, personnel, tempo, weather, and the current injury-adjusted lineup are established — set by the user at the game-plan/tactical level for the protagonist's own team, or by the opposing coaching staff's sampled tendency profile (§7) for every other snap in the league.
2. **Matchup deltas.** For each relevant phase of the drive (run block vs. run front, pass protection vs. pass rush, route/separation vs. coverage, QB processing vs. pressure, special-teams phase), compute the net delta between the offense's and defense's unit ratings (§2.3), folding in situational modifiers: score/time pressure, fatigue accumulated so far in this game, weather, and any real scheme mismatch the week's game plan actually identified. **Normalization rule, added 2026-09-18:** a scheme-mismatch modifier is earned only by the plan specifying a concrete, checkable mismatch (a named unit, a named tendency, a stated exploit) that step 6's reconciliation could in principle verify happened — never by how persuasively, confidently, or at length the plan describes it. Reduce the user's actual game-plan input to that concrete claim before this step runs; the prose used to make the case is not itself an input.
3. **Drive shape.** Draw one outcome from a fixed set of drive shapes — three-and-out, stalled/punt, methodical drive into field-goal range, explosive scoring drive, turnover-ended drive, clock-eating grind — from a categorical distribution whose weights the deltas shift. This is never a flat coin flip and never a single team-overall comparison.
4. **Featured beats.** Within the chosen shape, two to five representative beats (a completion, a stuffed run, a sack) are narrated. The player featured in each beat is chosen by usage-share weighting (depth-chart slot, package assignment, recent workload) — not uniform-random, so stars produce star-shaped box scores without simulating every snap. A periodic variance-injection check lets a depth player produce a signature outlier beat even when usage share alone would never select him, so a full season of box scores does not become formulaic.
5. **Carry-forward state.** Score, clock, field position, and per-position-group snap load carry into the next drive and feed its fatigue modifier.
6. **Reconciliation.** Stats and the narrative are generated together from the same drive outcomes and usage shares, then sanity-checked so yardage, scores, and turnovers sum correctly — the same reconciliation discipline Document 6 §7 already requires, run against a generative pass instead of manual entry.

### 3.3 Turnovers, penalties, and injuries

Each carries its own low-probability bounded check per drive, calibrated to real, era-accurate base rates (§8 placeholder tables) and further conditioned by the same matchup and fatigue context — a badly overmatched pass-protection matchup raises strip-sack odds, heavy late-season workload raises soft-tissue injury odds. Injury severity and return timeline are then handed to the medical-authority mechanic in §7; the coach never learns more than a plausible in-world channel would tell him, per Document 1 §7.

### 3.4 Randomness model

Bounded, matchup-weighted, seeded, and fully logged in the Engine Ledger (condition plus draw, never a bare "roll"). A plus unit can still have a quiet drive without its underlying anchor changing; a lopsided matchup has a narrow plausible outcome range, a close matchup has a wide one, which is where most real in-game chaos actually lives. Seeding makes a result reproducible and auditable/correctable later without silently rewriting unrelated history, matching the append-only correction culture already established in Document 6.

**Resolution-packet freeze, added 2026-09-18, at the user's explicit instruction after a review identified that "seeded" randomness with no rule for who picks the seed, or when, is not actually an anti-bias mechanism — a seed chosen after the resolving process has formed a preferred outcome is bias wearing a randomness costume.** Before any drive, turnover/penalty/injury check (§3.3), or other consequential draw is generated, the Engine Ledger must commit a resolution packet containing: an event ID, the world-state snapshot it was computed from, the normalized inputs (per §3.2 step 2's rule — concrete facts, not persuasive framing), the resulting modifiers, the outcome distribution those modifiers produce, the engine-procedure version, and the seed. That packet is closed — logged as final — *before* the draw is generated and the result narrated. It may not be revised after the result is known, except through Document 6's documented correction procedure, and a correction must rerun from the original packet's pre-resolution state; it may never be used to reach for a more desirable result the second time.

**Seed derivation is non-discretionary.** The resolving process never selects or adjusts a seed by feel. A seed is derived mechanically — for example `hash(career master seed + canonical event ID + engine-procedure version)` — so the same frozen packet always reproduces the same result, and nothing about the derivation involves a judgment call by whatever is running the resolution. Where no code execution is available to compute an actual hash, the nearest available non-discretionary substitute (e.g., a pre-committed, purely mechanical counter or external random source fixed before the packet closes) governs — the requirement is that the seed's source is fixed and auditable before the result exists, not that a specific algorithm is used.

**This is the mechanical enforcement of Document 1 §9.1.** That section states the invariant (protagonist status must not affect any outcome); this subsection is what makes it checkable rather than aspirational — a resolution packet frozen before the draw, from normalized inputs, using a non-discretionary seed, is falsifiable in a way "try to be fair" is not.

### 3.5 Granularity dial and manual escalation

Document 1 §11.2 already defines four game-detail modes (Executive, Play-Calling, Critical-Decision, Full Tactical). That existing dial sets the user's default narration depth for their own games. Independently of the dial, any sequence automatically escalates to denser, near-play-by-play narration at flagged spotlight moments (money downs, the two-minute drill, goal-to-go, trick plays, a live 4th-down call) or whenever the user names a sequence and asks to "go under the hood" on it — this escalation is prose density only, never an extra user turn, and never a deviation from the underlying drive-level mechanic that actually produced the result.

### 3.6 Long-run consistency check

Variance compresses as sample size grows: a single game can upset, but a season-long arc must still track underlying unit quality. This is checked the same way Document 6 §7 already checks statistical legality (completions never exceed attempts, turnovers reconcile) — as a standing postgame and end-of-season audit step, not a one-time design promise.

### 3.7 Named plays from the coach's own playbook

The user has a large personal playbook (real play concepts, each with design characteristics and a self-described "expected yards" figure) that they explicitly do not want ingested into this project wholesale — it is a token-cost concern, and more importantly an "expected yards" annotation in a real playbook is design intent, not a promised outcome, which is exactly consistent with this engine's own bounded-randomness philosophy.

**Storage:** the playbook stays wherever the user already keeps it, referenced by file path. It is never pasted into a conversation or read in bulk, and no version of it is embedded in this document or any other canon file.

**When it actually gets touched:** only at the moment the user, in Play-Calling or Full Tactical mode (Document 1 §11.2), names a specific play during an actual game. At that point, only that one play's entry is looked up (a targeted search by name, not a read of the whole document) — the same way a real coordinator's own call sheet is a huge document of which exactly one line matters per call.

**How a named play enters resolution:** the play's design characteristics (concept type, target depth/area, run or pass, personnel grouping) become one more situational modifier feeding §3.2 step 2's matchup-delta calculation, in the same slot "a real scheme mismatch the week's game plan identified" already occupies. The play's own "expected yards" figure is never used as a lookup result and never overrides the drive-shape/variance mechanic in §3.2-§3.4 — a well-designed call against a bad matchup can still produce nothing, exactly as in real football. This is flavor and situational color, not a second resolution system.

**Versioning across a career.** The user expects this to be a living, modern scheme that evolves in iterations across a multi-year career, not a document frozen at hire date. The playbook's actual content stays entirely external and version management is the user's own (a version note in their file, separate files per iteration, whatever they prefer) — this project does not track playbook content. What this project DOES track, per Document 6 §1's existing dated-supersession discipline, is *when* an iteration happened: the first time the user calls a play from a new iteration, or explicitly says the scheme changed, that transition date is recorded as a dated entry in the relevant `career/<year>/` file (an offseason note, or a same-season entry if the change happens mid-year), never silently assumed. This matters because a play lookup always uses whatever iteration was actually in effect on the in-world date being played — if the story ever revisits an earlier game, that earlier game resolves against the scheme that existed then, not against whatever the user's file currently says, exactly as Document 6 already insists real chronology never gets rewritten by later facts.

**The playbook's own embedded simulation rules govern, not a restatement here.** Inspected 2026-09-18: the user's actual playbook files each already contain a dedicated section written for exactly this purpose (in the two iterations checked, titled "Simulation Rules" and "Simulation Directives for [years]" respectively) — call-generation priority, personnel/motion/rotation rules, and explicit boundaries against importing a later era's tendencies into an earlier one. Where a playbook file's own directives are more specific than this document's general rule, follow the playbook's directive; this document does not duplicate or override it. Each iteration file also carries its own dated change log against the prior iteration (promoted/added/reduced concepts) — when a new iteration is confirmed in effect, that changelog is what actually explains what's different, not an assumption.

This is the direct fix for the standing rule against wasting turns on routine decisions (the same principle Document 3 §10.2 already applies to hiring searches, extended here to game weeks and game days). Effort scales with actual stakes: a blowout can resolve in a single exchange with no in-game pauses; a one-score fourth quarter naturally produces several.

The gate does not introduce a new, separately-computed "win probability" number. It operationalizes Document 1 §11.3's existing pause-trigger list into concrete situational thresholds, so the trigger is auditable without exposing any new hidden statistic:

| Trigger (from Document 1 §11.3) | Concrete threshold for this engine |
|---|---|
| Important fourth down | Any 4th down where the protagonist's own team is on offense or defense, inside the opponent's territory, or in the final 5 minutes of either half regardless of field position |
| End-of-half / endgame management | Final 2 minutes of either half, or any point where a single score changes the leader, in a game involving the protagonist's team |
| Two-point attempts | Every one, always, for the protagonist's team |
| Material injury substitution | Any injury to a starter or a player in a featured role for either team in a game involving the protagonist |
| Major tactical departure | Any point the protagonist's staff would plausibly recommend deviating from the approved game plan |
| Timeouts, replay/challenge choices, unusual special teams, serious sideline conflicts | As Document 1 §11.3 already states, unchanged |

Outside these triggers, the drive resolves and narrates automatically under the play-calling delegation the coach already set. The threshold table above is a starting default and is explicitly user-adjustable — tighten it for more control, loosen it for faster games — without requiring a different engine.

## 5. Weekly turn structure

Adapted directly from Document 3 §10.2's compressed-turn procedure, extended from hiring searches to an ordinary game week:

1. **Week Brief (one user turn).** Last week's league-wide results and standings shift, this week's opponent scouting summary, both teams' injury/availability report, any item genuinely needing the coach's response, and a single consolidated game-plan/practice-priority decision — presented together, never as a string of separate questions.
2. **Practice week (auto-resolved).** Practice days, walkthroughs, and travel run in the background and are narrated only if something material happened (an injury, a standout practice, a staff disagreement). A decision point is raised only when a real complication earns one — never on a fixed schedule. This is Document 3 §10.2's own rule, applied here verbatim.
3. **Pregame lock (optional, foldable into step 1).** Inactive/game-day designations and final situational stances, raised as its own turn only when genuinely borderline.
4. **Game day.** Resolves per §3-§4 above; the other 31 teams' games resolve in parallel via the cheap path from §1, consuming no user turn.
5. **Postgame Report (one user turn).** Final result, a decision-quality log entry only for moments the coach actually decided, updated standings/stats/injury report, and next week's preview.

A full week costs roughly three to five user-facing exchanges when nothing unusual happens, growing only when the game or the week actually earns it.

### 5.1 Preseason exception

Per explicit user instruction, the preseason period (Document 2 §6.1's training-camp/preseason window) does not run the weekly loop above at all. It resolves as a single bulk turn: one consolidated brief covering roster-cut decisions, the preseason-game slate's results and notable performances, and camp-battle outcomes, presented once at the transition into the regular season rather than week by week. A preseason event escalates out of the bulk summary only for something that would already force a decision under Document 1's ordinary rules regardless of period — a season-ending injury to a projected starter, for instance — never merely because a preseason week occurred.

### 5.2 Three output formats — user-authored, confirmed 2026-09-17

Resolved. The user supplied the in-season and offseason formats as drafts and they were refined together: `foundation/templates/season_output_template.md` (every in-season turn, preseason bulk report through the last postseason game) and `foundation/templates/offseason_output_template.md` (season end through the next preseason). A third, `foundation/templates/hiring_search_output_template.md`, covers the pre-hire candidacy phase (Document 3 §10.2) and was added the same day once the user asked, before starting play, what the actual input/output shape of a turn was. Document 1 §12.1's normal-response shape is superseded by all three for anything in-world; §12.1 remains accurate as a general communication-style guide but the actual field-by-field layout lives in the template files. Do not invent a fourth format or silently deviate from any template's structure.

### 5.3 Regular-season length is a real, not hardcoded, fact

The number of regular-season weeks and games, and how postseason rounds are structured, always follows Document 2's real rules-by-year for the season actually in play (for example, 17 weeks/16 games before the 2021 realignment, 18 weeks/17 games from 2021 onward) rather than any fixed assumption in this document. Document 2 §5 and §6 are the source of truth; this document only consumes whatever season length Document 2 states for the current year.

## 6. Draft, scouting classes, and the free-agent market

### 6.1 Draft

Reuses Document 2 §12's existing procedure without modification: real classes are used with pre-selection data only, real post-selection outcomes are quarantined, and once real documented classes are exhausted, later classes are generated by sampling real historical position/round distributions and bust/hit base rates. Every generated or real prospect receives an anchor through the identical §2.2 conversion used for rostered players, so draft evaluation runs under the same uncertainty framework as everything else in this engine.

### 6.2 Free agency and other-team signings

Document 2 §9.3 defines the rules of free agency (movement categories, tender levels, negotiating windows); this section defines how the protagonist actually participates in that market, mirroring the draft's real-market-plus-simulated-behavior pattern and Document 3 §10.2's compressed-turn discipline.

1. **Market generation.** At the open of a free-agency period, the available player pool is the real historical set of scheduled free agents for that real year and league (if using real personnel) or the simulation's own generated set (once real documented markets are exhausted or personnel have diverged), each carrying the same qualitative evaluation fields as a rostered player, never a real player's actual post-departure destination or outcome as a hidden answer.
2. **Coach's plan, one consolidated turn.** The coach states priorities and constraints once — target need(s), acceptable cost range against actual available cap space (§8, sourced from real numbers, never invented), and any hard limits — rather than being walked through one candidate at a time.
3. **Other clubs' pursuit resolves autonomously.** Every non-protagonist club's free-agent pursuit, offer, and signing resolves in the background per Document 2 §12's autonomy rule, extended here from draft-day trades to free agency generally; competing offers from other teams are a real market pressure the coach can lose to, not a scripted obstacle.
4. **Outcome report.** The coach receives one consolidated result per plan (signed at what terms; lost the market to a named or generic competing offer and why, e.g. outbid, scheme fit elsewhere, term length; or unsigned/still available) — never a play-by-play negotiation transcript unless the coach specifically wants to negotiate a live offer, which is then its own single compressed exchange, not a haggling loop.
5. **Cap accounting is immediate.** The instant a signing closes, Document 4's cap/cash reconciliation updates in the same turn — never deferred to the next weekly cycle — per §6.3 below.

### 6.3 State update cadence

Per explicit user instruction: roster and cap/cash state update the moment the triggering event happens, not on any batch or weekly delay — a signing updates cap space immediately, a draft pick or trade updates the roster immediately, and a coach's own lineup/depth-chart call updates immediately. Standings, by contrast, update once per week, after that week's full slate of games (protagonist's and background) has resolved, never mid-week. This is not a new rule so much as a restatement of what Document 4 (current reconciliation) and Document 6 (dated event ledger) already require — every state change is written when it happens, per Document 1 §13.2's atomic-commit discipline — stated here explicitly because it is a specific point the user flagged as a past failure elsewhere (see §6.4).

### 6.4 Financial precision commitment

The user's stated top priority for building this engine at all is not repeating a prior experience where salary-cap numbers were vague or inconsistent ("fudged"). Three existing rules already exist specifically to prevent that, and this document adds no new ones, only names them together:

- Document 2 §11.1/§11.2 already requires the season's actual real financial rules and forbids ever presenting a fictional budget as a league cap, or calculating cap room in an uncapped season.
- Document 4's financial/contract/eligibility reconciliation table is the sole detailed owner of cap, cash, and internal-budget numbers, and Document 6 §7 already requires numeric totals to reconcile exactly at every update — a cap error is a validation failure, not a narrative choice.
- The real-data library effort (separate from this document, tracking the user's own "build the library" request) is what actually supplies precise, sourced, per-year CBA numbers — cap ceiling/floor, bonus proration rules, dead-money accounting — for the confirmed January 2013 baseline and forward. Document 2 §17's source-provenance schema (exact source, publication date, scope, applicability through divergence) is the mechanism that keeps those numbers traceable rather than approximate.

## 7. World-agent roster

Extends Document 1 §3.3, Document 2 §12, and Document 3 §10.3, rather than replacing any of them. Every entry below defaults to full autonomy; the "becomes user-facing when" column is the only trigger that pulls the user in.

| Agent | Scope | Autonomy rule | Becomes user-facing when |
|---|---|---|---|
| Opposing front offices | Trades, signings, extensions, releases, draft selections for all non-protagonist clubs | Fully autonomous, zero confirmation, reported as a transaction digest | The protagonist's own organization is a party |
| Opposing coaching staffs | Play-calling and weekly game-planning for every team the user doesn't control, including games between two non-protagonist teams | Fully autonomous, driven by a coaching-tendency profile (aggressiveness, pace, scheme identity) sampled once per staff and applied consistently, not re-rolled each week | Never, for games not involving the protagonist |
| Protagonist's own coordinators/assistants | Detailed install and play-calling within the philosophy the coach set | Autonomous within delegated scope; may push back or deviate under pressure for a stated reason | The coach's plan conflicts with new information, or the coach chooses to override (tracked as a qualitative relationship note, never a number) |
| Players, leaguewide | On-field performance (resolved by §3, not narrated per player), development, morale, contract stance, trade requests | Fully autonomous internal state; the coach learns about it only through a plausible in-world channel | A player's situation specifically requires the coach's or front office's response |
| Medical staff | Injury occurrence, diagnosis, clearance, and return timeline | Independent medical authority; cannot be overridden by the coach, per Document 1 §4 | Never for the medical decision itself; the resulting availability change is always communicated |
| Ownership/front office (protagonist's own org) | Cap management outside the coach's authority-map rows, and season mandate/pressure | Acts and evaluates independently | A move changes the roster the coach must plan with, or ownership initiates a genuine mandate conversation |
| Media | Coverage, storylines, coaching-search and contract rumors | Fully autonomous, grounded strictly in actual results and known context; never fabricates private misconduct and never a hidden lever for manufacturing drama the user didn't ask for | The user chooses to respond directly (a press conference, a statement) |
| Locker room / team chemistry | Ambient player-to-player and player-to-coach climate | Fully autonomous, but fires only from events already logged elsewhere (a benching, a trade, a stat-leader emergence) — it never invents conflict to fill a quiet week | A specific conflict rises to needing the coach's actual response |
| League office / officiating | Rule enforcement, discipline, scheduling, in-game officiating | Fully autonomous and impartial; may plausibly err, as in real football, never targeted at the protagonist | Never directly; the coach reacts to a ruling like any other game event |
| Agents/contract representatives | Contract negotiation and free-agency demands leaguewide | Fully autonomous for every other roster | The player is the protagonist's own free agent — then compressed into a single 1-2 turn decision, never a back-and-forth haggle loop |

## 8. Era-calibration placeholders

Target season confirmed by the user on 2026-09-17: **January 2013 forward**, matching Document 3's HC-candidate starting point. The following still require real, sourced values before this document can leave `AUTHORING MASTER` status — populating them is the job of the real-data library effort (player/draft-class data, team/league rules-by-year, coaching/front-office market data) the user separately requested, not a re-derivation here:

- League-average yards per attempt/carry, completion rate, and explosive-play rate for the 2012-2013 NFL season and forward: `[PENDING LIBRARY BUILD]`
- League-average sack rate, interception rate, and fumble rate for the same window: `[PENDING LIBRARY BUILD]`
- Position-group injury-exposure rates per snap, and typical return timelines by severity tier: `[PENDING LIBRARY BUILD]`
- Real 2013-era-forward salary-cap ceiling/floor, bonus-proration rule, and dead-money accounting, sourced and cited per Document 2 §17's provenance schema: `[PENDING LIBRARY BUILD]`
- Any rule differences affecting drive outcomes (overtime format, replay/challenge rules, kickoff/onside-kick rules, and — per §5.3 — the 2021 season-length change) for the years actually played: cross-reference Document 2's own playing-rules tables rather than duplicating them here.

## 9. Cross-references added to Documents 1-6

Only these pointers are added; no existing rule in Documents 1-6 is changed:

- Document 1 §2 (Initialization gate), item 6, "Game granularity and career/off-field detail level," now also requires this document's §11 decisions to be resolved.
- Document 3 §12 (Initialization gate) gains a line: "Document 7 (Game Simulation and Resolution Engine) reconciled and locked."
- Document 6 §6 (game ledger format) is the ledger this engine's outputs are written into; no change to its schema was needed.

## 10. What this document deliberately does not change

The evidence-labeling system, the real-person protections, the append-only ledger discipline, the anti-stock-character rule, the authority map, and the qualitative-only coach-facing evaluation system all carry over unmodified. This document adds a resolution mechanism and a private data layer underneath the existing package; it does not relitigate any of the philosophy Documents 1-6 already settled.

## 11. Outstanding decisions

1. **Hidden Engine State layer.** Design confirmed by the user 2026-09-17. The storage contract is defined in §1, but the runtime store is not instantiated until a team is hired and the initialization build creates the active roster, staff, and season inputs.
2. **Default granularity dial.** Not separately asked; adopted as recommended — Document 1 §11.2's existing "Executive head-coach mode" as the default, with the leverage gate in §4 forcing a pause regardless of mode at the listed triggers. Changeable at any time without a redesign; revisit if the user objects.
3. **Target season/era for calibration.** Confirmed by the user 2026-09-17: January 2013 forward (Alex Stone, HC candidate, not yet hired), matching Document 3's starting canon. §8's placeholders now wait on the real-data library build rather than on this decision.
4. **Three output formats.** Resolved: pre-hire hiring search, in-season, and offseason — see `foundation/templates/`.
5. **Repository folder structure.** Resolved 2026-09-17: the flat 8-file layout was reorganized to mirror the SCOTUS project's `foundation/` + `state/` + `terms/` pattern, at the user's explicit request. See §12 below.
6. **The coach's own real-world playbook.** Resolved 2026-09-17, per §3.7: kept entirely external, referenced by file path, and looked up one play at a time only when actually called in-game — never ingested wholesale. Its "expected yards" annotations are a situational modifier into the existing matchup-delta calculation, never a lookup result.
7. **Hiring-search output format and persistence.** Resolved 2026-09-17: `foundation/templates/hiring_search_output_template.md` gives the pre-hire candidacy phase the same concrete shape the season/offseason templates give post-hire play, and every turn is appended to `career/<year>/offseason/hiring_search.md` rather than existing only in chat — see Document 3 §10.2 items 6-8 and `career/README.md`'s exception to "empty until initialization."

## 12. Repository layout

Resolved 2026-09-17, mirroring the SCOTUS project's proven layout at the user's request:

- **`foundation/`** — the stable rulebook: Documents 00, 01, 02, 03, 06, 07, and `foundation/templates/` (three output templates: pre-hire search, in-season, offseason). Never holds a dated instance record.
- **`state/`** — the always-current, in-place-updated snapshot: Documents 04 (Roster and Staff Register) and 05 (Current Season State). Rewritten as events happen, per §6.3; never append-only.
- **`career/`** — the actual played history, one folder per season, created only once a season is reached in play. See `career/README.md` for the exact per-season layout (preseason, regular-season weeks, postseason rounds, offseason draft/free-agency records, and that season's slice of the Document 6 ledger).
- **`archive/`** — superseded or quarantined material kept for reference only, never active canon. See `archive/README.md`.
- **`library/`** — supporting reference material that is not itself canonical authority: sourced era research, clean runtime views, quarantined actual-future comparators, and non-authoritative character reference. Runtime tasks must read only the files explicitly permitted for their phase. For the 2013 hiring search, use `library/2013_coaching_market_pre_hire.md` and do not load the hindsight comparator `library/2013_coaching_market.md`. Load-bearing rules still belong in Document 2.

This mirrors SCOTUS's `foundation/` (stable rulebook) + `state/` (current trackers) + `terms/OT<year>/` (per-term instance folders) + `archive/` almost exactly, plus one addition (`library/`) for supporting reference material the SCOTUS project did not need in the same way. No document's internal numbering or content changed because of this move — only where each file physically lives.

**`AGENTS.md`** — the bounded batch-task contract. It defines the pre-hire search resolver, research-library expansion, a background-league task that remains disabled until this engine is runtime-ready, and a gated offseason placeholder. Any protagonist choice not explicitly covered by a user-authored standing instruction returns to the user rather than being invented by the agent.
