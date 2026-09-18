# Document 6: Chronology, Game Ledger, and Handoff Protocol

## Purpose and status

**Document status:** Durable protocol and append-only ledger  
**Protocol version:** Rebuild draft 1.1 (post-audit QA)  
**Readiness:** `NOT READY` — no audited starting baseline and handoff have been closed  
**Global package checkpoint:** `NONE`

This document is the durable historical record of the simulation. It preserves what happened, when it happened, what the head coach decided, how games progressed, and what remains unresolved. It also defines the procedures for corrections, continuity audits, phase archives, atomic updates, and resuming in a new chat.

The protocol sections are stable. Dated records and archives are append-only. Document 5, Current Season State, remains the compact mutable snapshot reread before every response; this document supplies the evidence behind that snapshot.

**Where the actual entries live.** This document (in `foundation/`) defines the ledger's rules and record formats; it is never itself the place where a multi-year career's dated entries pile up. Once a career is initialized, the actual append-only entries for a given season live in `career/<year>/ledger.md`, one file per season, exactly mirroring how every rule in this document still applies. `career/README.md` describes that layout. Nothing about the rules below changes based on where the file physically lives.

Do not use turn numbers as dates. Do not use ratings, morale meters, trust scores, or opaque event codes. Use exact dates, plain-language labels, named people or groups, and stated uncertainty.

## 1. Canonical record rules

1. Record every material event on the date it occurred or became effective. During a live game, also record the period and game-clock time.
2. Assign the shared Document 2 canon class separately from the ledger record form. The active classes are `Verified pre-divergence fact`, `User canon`, `Post-divergence simulation event`, `Attributed report or assessment`, `Labeled inference`, `Unresolved legacy claim`, and `Undetermined`. An intentional counterfactual baseline uses `User canon` plus a Document 2 divergence entry. `Quarantined actual-future comparator` is authoring-only and never enters the active ledger.
3. Record only information that materially changes chronology, authority, personnel, availability, preparation, results, statistics, relationships, resources, commitments, or career options.
4. Never erase or silently rewrite a dated historical entry. Correct it through an appended supersession entry in this document.
5. Use the latest valid supersession in the latest closed canonical update when reconstructing state. Preserve the superseded text so the reason for the change remains visible.
6. A scheduled event, transaction, injury update, or staff change is not effective merely because it was discussed. Record the decision maker, approval, rule mechanism, effective time, and any condition precedent.
7. A rumor is not an event. Record its source, audience, and uncertainty without converting it into objective world state.
8. An unambiguous user decision is canon when the user makes it. A question, hypothetical, or incomplete instruction is not. Implementation and outcome are separate records.
9. Publicly verified facts about real people remain distinct from fictional post-divergence developments.
10. If a record cannot be reconciled, stop chronological advancement, identify the conflict, apply the project canon authority order, append the correction, and then continue.
11. This is a user-visible ledger. Never place an uncommunicated hidden fact, private thought, concealed opponent plan, unfinished medical conclusion, or confidential decision unknown to the head coach in it. If the platform supports private simulator state, preserve that state outside all six user-visible canonical documents. If it does not, leave the matter undetermined.
12. When a previously hidden fact is later communicated through a plausible channel, append the record on the communication date. The entry may state an earlier effective or occurrence date only then, and must distinguish “effective on” from “learned by the head coach on.” Never backdate the coach's knowledge.
13. Document 6 is the sole full correction and supersession history. Correction or revision tables in Documents 2-5 are current indexes only: they identify the controlling Document 6 correction entry and the present replacement value, but do not maintain a competing narrative history.

### Supersession format

Append corrections where the contradiction is discovered. Do not edit the original entry. A correction is a source record and must be the first staged record in any candidate update it controls, before candidate stable or mutable documents are versioned or replaced. It becomes committed only with that candidate bundle's close line.

```markdown
### Correction entered [exact date and time, with time zone if material]

- Supersedes: [exact dated entry and field]
- Canon class: [shared Document 2 class controlling the replacement]
- Conflict discovered: [what did not agree]
- Authoritative basis: [user correction, applicable rule, approved canon, official record, or arithmetic]
- Replacement: [complete corrected fact]
- Downstream records corrected: [schedule, roster, statistics, Current Season State, or other affected record]
- Remaining uncertainty: [none, or concise description]
- Head-coach knowledge date and channel: [when and how the correction became available to the coach, or “Not communicated; administrative canon correction only”]
```

Documents 2-5 may point to this entry by its exact heading and date. They must not reproduce a second full correction history.

## 2. Dated career chronology

Append one entry for each material event or coherent date range. Routine activity may be compressed. Do not manufacture an event to fill a date.

```markdown
### [Exact date or date range] | [Team] | [Season phase and week]

- Event: [concise factual account]
- Canon class: [shared Document 2 class]
- Record form: [verified baseline / dated user decision or correction / simulation event / attributed communication or report / inference note / unresolved material matter]
- Event/effective date: [date the event occurred or became effective]
- Head-coach knowledge date: [date/time learned, which may be later]
- Head-coach decision: [user's decision, or “No consequential head-coach decision”]
- Authority and implementation: [who had final authority and what was carried out]
- Consequences known now: [football, personnel, organizational, financial, or career effects]
- Linked record changes: [schedule/result, transaction, injury, staff, contract, game, or statistics]
- Information boundary: [what the head coach learned and through which plausible channel]
- Unresolved matter: [owner, deadline, and next expected update, or “None”]
```

Do not create this entry merely to preserve a simulator-only secret. If the event was unknown to the head coach when it occurred, enter it only after a plausible communication makes it user-visible, and retain both dates.

## 3. Schedule and results register

At the start of each season phase, append the verified or approved schedule baseline. Later changes and results are appended beneath it. A postponement, flex, venue change, cancellation, or correction must name the entry it supersedes.

### Schedule baseline template

| Competition week | Exact date and kickoff | Opponent | Venue and location | Home/away/neutral | Status | Source or canon basis |
|---|---|---|---|---|---|---|
| [Week] | [Date, time, time zone] | [Opponent] | [Venue] | [Home/away/neutral] | Scheduled | [Official source or approved fictional canon] |

### Schedule amendment or result template

```markdown
### [Date entered] | [Opponent] schedule/result update

- Applies to: [original scheduled game]
- Canon class and record form: [shared class; schedule amendment / completed result / correction]
- Change or result: [rescheduled details, cancellation, or final score with protagonist team listed first]
- Effective basis: [league action, institutional action, completed game, or correction]
- Team record after game: [overall and competition/division/conference record as applicable]
- Standings consequence: [verified position or concise effect]
- Linked game ledger: [date and opponent]
- Supersedes: [prior detail, or “Nothing”]
```

Do not update the team record until play has ended under the applicable rules and the mandatory postgame finalization in Section 7 has closed. Vacated, forfeited, suspended, or later-corrected results require a supersession entry and a standings/statistics reconciliation.

For a real historical simulation, actual future results after the divergence point are not schedule results and must not be imported as canon.

## 4. Personnel, medical, staff, and career ledgers

Each ledger is append-only. Later developments reference the prior dated entry. Record an internally confidential matter here only if it has been communicated to the head coach and is therefore part of the user's legitimate information picture; otherwise keep it outside the user-visible canonical documents or leave it undetermined.

### Transaction or roster record

```markdown
### [Date/time entered and communicated] | [Player] | [Transaction or roster action]

- Canon class and record form: [shared class; transaction/roster event or attributed report]
- Effective date and time: [actual effective time; may be earlier only if first learned now]
- From / to: [prior status] -> [new status]
- Governing mechanism: [trade, waiver, release, signing, reserve list, promotion, scholarship, transfer, or other exact rule]
- Final authority and approvals: [named role or institution]
- Head-coach role: [decision, recommendation, objection, consultation, or no authority]
- Contract, cap, budget, eligibility, or roster effect: [verified details and uncertainty]
- Public status: [public, internally communicated, confidential, or pending announcement]
- Related depth-chart or package effect: [if material]
- Unresolved condition or deadline: [if any]
```

### Injury and availability record

```markdown
### [Date and time] | [Player] | [Medical/availability update]

- Canon class and record form: [shared class; communicated medical/availability event or attributed report]
- Trigger or observation: [play, practice, reported symptom, examination, or scheduled review]
- Information communicated to the head coach: [only what arrived through medical or reporting channels]
- Diagnosis: [verified medical wording, or “Not established”]
- Practice status: [full, limited, did not participate, or competition-specific equivalent]
- Game availability: [available, available with limitations, game-time decision, unavailable, or not yet determined]
- Functional limitation or planned workload: [medical/performance guidance, not a coaching diagnosis]
- Clearance authority: [medical professional or process]
- Recovery estimate: [range and confidence, or “Not responsibly estimable”]
- Next evaluation or reporting deadline: [exact date/time]
- Supersedes: [prior availability entry, if any]
```

Medical diagnosis and clearance remain with medical personnel. Coaching use of a cleared player is recorded separately from clearance.

### Staff or organizational record

```markdown
### [Date entered and communicated] | [Person or unit] | [Staff/organizational change]

- Canon class and record form: [shared class; staff/organizational event or attributed report]
- Effective date: [actual effective date; may be earlier only if first learned now]
- Change: [hire, departure, dismissal, promotion, reassignment, leave, reporting-line change, or delegation change]
- Final authority and approvals: [named role or institution]
- Head-coach decision or recommendation: [user-established action]
- Responsibilities and play-calling effect: [before and after]
- Contract, budget, or search effect: [verified terms and limits]
- Relationships or workload materially affected: [plain-language description]
- Unresolved matter: [candidate, negotiation, replacement, obligation, or deadline]
```

### Head-coach career or contract record

```markdown
### [Date entered or communicated] | [Organization] | [Career/contract event]

- Canon class and record form: [shared class; career/contract event, user decision, or attributed report]
- Event/effective date: [date, which may differ from communication date]
- Event: [inquiry, permission request, interview, offer, negotiation, extension, termination, resignation, acceptance, rejection, or transition]
- Source and status: [official, directly communicated, reported, or rumor]
- Decision authority: [organization and governing roles]
- Head-coach decision: [user's exact decision, if made]
- Material terms: [length, compensation, buyout, control, reporting line, staff pool, start date, and verified uncertainty]
- Current-team obligations: [contractual, operational, staff, player, media, or transition duties]
- Relocation/family effect: [only if included by the user]
- Next deadline or condition: [exact date]
```

## 5. General consequential decision-quality records

Use these paired records for every consequential head-coach decision outside a live game, including material weekly-plan, practice-allocation, depth, personnel, staff, discipline, communication, contract, interview, and career choices. The live-game form in Section 6 adds game-state fields but follows the same rule. Close the pre-result decision before resolving implementation or outcome. When one response contains both, use two ordered closed updates inside that response: decision-only first, outcome second.

```markdown
### General pre-result decision | [Exact date/time and plain-language decision]

- Canon class and record form: [User canon; dated user decision]
- Situation known at the time: [material football, organizational, contractual, calendar, resource, and relationship facts]
- Information channels: [what the head coach learned, from whom, when, and with what confidence]
- Authority: [final authority; head coach's decision, recommendation, consultation, objection, or no-authority role]
- Advice and disagreement: [attributed recommendations, reasoning, and uncertainty]
- Realistic constraints and deadline: [rules, contract, resources, time, medical limits, and implementation capacity]
- Plausible alternatives: [material alternatives, not a closed menu]
- User's exact choice: [decision without invented motive, wording, or promise]
- Ex-ante assessment: [sound, defensible, questionable, or clear error, with reasoning and confidence based only on decision-time information]
- Material unknowns: [facts or responses not yet known]
- Target decision-only global checkpoint: [human-readable label]
```

Only after the decision-only checkpoint closes may implementation or outcome be resolved. Append the linked result without editing the ex-ante judgment:

```markdown
### General decision outcome | [Exact date/time and same plain-language decision]

- Canon class and record form: [Post-divergence simulation event; decision implementation/outcome]
- Pre-result record and closed checkpoint: [exact heading and label]
- Implementation: [who acted, under what authority, and when]
- Outcome: [what occurred, including refusal, delay, partial completion, or no material change]
- Independent actors and variance: [material contribution without invented private motive]
- New planning evidence: [what can now be learned]
- Decision-quality treatment: [unchanged, or altered only because decision-time information was formally corrected—never because the result was favorable or unfavorable]
- Downstream records: [chronology, roster, staff, schedule, contract, relationship, or Current Season State]
```

A migrated past decision may use a `MIGRATED RETROSPECTIVE RECONSTRUCTION` under the same evidence limits as the live-game protocol. A missed ex-ante record during active play is an audit failure, not permission to invent hindsight.

## 6. Game record

Create a game record before kickoff. Once play begins, append events in order and preserve an exact live checkpoint in Document 5.

Throughout every game record, scoring ledger, live checkpoint, statistical summary, schedule result, and postgame record, write score pairs with the protagonist's current team first and the opponent second, regardless of which team is home, possesses the ball, or just scored. Name both teams whenever a bare pair could be ambiguous. Never reverse score orientation within a game.

Canon class and record form remain operational at every level. The pregame baseline states its own class. Every toss, snap, compressed sequence, decision, and outcome states its class and form. A drive summary, scoring row, or statistical aggregate is a derived view rather than a new event: it must cite the exact source event(s) and inherits their class. If source entries have different classes, list each instead of collapsing them.

### Pregame setup

```markdown
## Game: [Team] vs. [Opponent] | [Exact date]

- Canon class and record form: [shared class; verified/user-approved pregame baseline]
- Competition and season: [league/governing body and season]
- Venue, location, surface: [verified details]
- Kickoff: [time and time zone]
- Applicable game rules: [rulebook/season, overtime, replay/challenge, active-roster limits]
- Records entering game: [both teams]
- Conditions: [weather/field facts that materially affect play]
- Active and inactive players: [source and late changes]
- Availability limitations and emergency roles: [material only]
- Offensive play caller: [person and limits]
- Defensive play caller: [person and limits]
- Special-teams responsibility: [person and limits]
- Head-coach game-management authority: [timeouts, challenges, fourth downs, personnel, and any organizational limits]
- User-approved plan: [offense, defense, special teams, personnel, pace, and situational priorities]
- Opponent tendencies actually available: [source, sample, and uncertainty]
- Preparation assessment: [what was installed and demonstrated; do not guarantee execution]
- Material uncertainties: [unresolved matchup, health, communication, conditions, or scouting questions]
```

### Coin toss and period-possession entitlement

Record the opening toss before the opening kickoff and a new toss or choice before overtime whenever the applicable rules require one. This record controls later-half and overtime possession; the kickoff receiver alone is not always sufficient to reconstruct the choice.

```markdown
### [Opening / overtime] possession entitlement | [Date, period, and clock if applicable]

- Canon class and record form: [Post-divergence simulation event; game-administration event]
- Toss winner: [team]
- Choice: [receive, kick, defend goal, defer, or competition-specific choice]
- Other team's choice: [choice]
- Opening kickoff receiver: [team]
- Second-half kickoff entitlement: [team and basis]
- Overtime opening possession entitlement: [team and basis, or not applicable]
- Direction defended: [team and goal, when material]
- Rule source: [Document 2 version and exact rule]
```

At every period transition, record whether possession carries over, a kickoff occurs, or another competition-specific procedure controls. Never infer second-half or overtime possession from narrative convention.

### Game event ledger

Use human-readable sequence labels such as “Opening drive, play 1” or “Third quarter, protagonist drive 2.” A single-snap entry uses every field below. A field may say `Not applicable`, but it may not be silently omitted.

```markdown
### [Drive and play] | [Quarter/period, clock before snap]

- Canon class and record form: [Post-divergence simulation event; single-snap game event]
- Football state before: [possession; down and distance; ball location and direction; score with protagonist team first; both teams' timeouts]
- Administrative state before: [pending/cleared penalty, enforcement, replay, challenge, measurement, timeout, injury administration, period procedure, or none]
- Game clock before: [exact value; running/stopped; restart condition]
- Pre-snap play clock: [exact value; running/stopped/not started; reset value and restart basis]
- Personnel/package before snap: [offensive personnel and package; defensive personnel/package when tracked]
- Formation/alignment/motion: [formation, material alignments, motion/shift, and set status when the selected granularity requires them; otherwise “Not required in selected mode”]
- Substitution and eligibility state: [players entering/leaving; declared eligible/ineligible reports; offense-substitution status; whether the defense received and completed its rule-required matching opportunity; legality confirmed]
- Decision/call: [only information and choices properly known; identify user decision when applicable]
- Result: [yardage, scoring, turnover, kick, penalty, injury, or no play]
- Enforcement/replay: [accepted/declined/offsetting penalty, challenge, review, ruling, and timeout effect]
- Football state after: [possession; down and distance; ball location and direction; score with protagonist team first; both teams' timeouts]
- Administrative state after: [pending/cleared penalty, enforcement, replay, challenge, measurement, timeout, injury administration, substitution restriction, period procedure, or none]
- Clocks after: [game-clock value, running/stopped status, and restart; play-clock value/status/reset when begun]
- Personnel/package after: [on-field personnel, temporary absence, substitution still in progress, or next-snap state not yet declared]
- Availability change: [if any]
- Statistical deltas: [every pass/rush/target/sack/turnover/kick/return/penalty/scoring/team-play delta produced by this snap or no-play ruling]
```

An eligibility report, substitution, defensive matching opportunity, replay change, accepted or declined penalty, no-play ruling, charged timeout, and administrative clock action must appear even when it produces no ordinary player statistic.

### Compressed routine-sequence entry

Routine snaps may share one ledger entry only when no consequential head-coach decision, unresolved administrative ruling, material availability decision, or required granularity stop occurs between them. Compression changes presentation, not state fidelity. The entry must preserve every snap's state transition and statistical delta; “three-and-out,” “touchdown drive,” or a prose drive summary alone is insufficient.

```markdown
### Compressed routine sequence | [Drive/period, start clock through end clock]

- Canon class and record form: [Post-divergence simulation event; reconstructable compressed game-event sequence]
- Compression basis: [selected game mode and why no user stop occurred]
- Sequence state before: [full football, administrative, clock, play-clock, personnel, substitution/eligibility, and protagonist-team-first score state]

| Snap | Pre-snap game/play clocks and status | Down, distance, spot/direction | Personnel/package; formation/motion if required | Substitution/eligibility/matching state | Call and result | Enforcement/administration | State and clocks after | Statistical deltas |
|---|---|---|---|---|---|---|---|---|
| [Play label] | [exact] | [exact] | [state] | [state] | [call/result] | [state] | [possession, down, spot/direction, protagonist-first score, timeouts, clock/restart] | [all deltas] |

- Sequence state after: [full football, administrative, clock, play-clock, personnel, availability, and protagonist-team-first score state]
- Sequence arithmetic: [plays, net yards, elapsed game time, first downs, possession result, scoring, timeouts, penalties, and player/team statistical deltas reconciled]
- User-control check: [no consequential head-coach decision was passed]
```

If even one required per-snap delta cannot be reconstructed, do not compress that sequence.

At each change of possession, append a drive summary:

| Possessing team | Start | End | Plays | Net yards | Elapsed game time | Result | Source events and inherited class |
|---|---|---|---:|---:|---|---|---|
| [Team] | [Period/clock/spot] | [Period/clock/spot] | [Number] | [Yards] | [Time] | [Punt, score, turnover, downs, half, or game] | [exact events; class] |

The next drive must begin from the preceding scoring play, kick, punt, turnover, failed fourth down, safety free kick, period transition, or other rule-valid transfer. Do not assume alternating possession when an onside recovery, muff, replay change, or period rule produces another result.

### Scoring ledger

| Period and clock | Scoring team | Scoring play | Points | Protagonist-team–opponent score after play | Ensuing possession basis | Source event and inherited class |
|---|---|---|---:|---|---|---|
| [Period/clock] | [Team] | [Description] | [Points] | [Protagonist team score-opponent score] | [Kickoff, free kick, overtime rule, or game over] | [exact event; class] |

### Head-coach decision-quality records

For every consequential live-game head-coach decision, create and close the pre-result record below before sampling randomness, selecting an outcome, simulating the next snap, or learning the result. This is mandatory, not optional. The user's choice and the ex-ante assessment form a decision-only canonical update; the outcome is a later linked entry. A sound decision may fail, and a questionable decision may succeed.

```markdown
### Pre-result decision | [Date, game period, clock, and plain-language decision]

- Canon class and record form: [User canon; dated live-game user decision]
- Situation known at the time: [score with protagonist team first, clock and clock status, field position, timeouts, personnel, rules, opponent evidence, and uncertainty]
- Head-coach choice: [user's exact decision]
- Authority and advice: [who decided; staff recommendations and disagreements]
- Plausible alternatives: [material alternatives, not a closed menu]
- Ex-ante assessment: [sound, defensible, questionable, or clear error, with reasoning and confidence]
- Model evidence: [only if a suitable model exists; state model, assumptions, range, and limitations]
- Information deliberately unavailable: [hidden result, opponent call, unresolved medical or officiating fact]
- Decision-only global package checkpoint: [exact human-readable update label]
```

Only after that update is closed may the simulator resolve the event. Append the outcome without editing the pre-result assessment:

```markdown
### Decision outcome | [same date, period, clock, and plain-language decision]

- Canon class and record form: [Post-divergence simulation event; live-game decision outcome]
- Pre-result record: [exact heading]
- Result: [what occurred]
- Execution and opponent contribution: [material evidence]
- Post-result assessment: [new planning evidence, if any]
- Decision-quality treatment: [unchanged, or changed only because previously unavailable decision-time information was corrected—not because the result was good or bad]
```

A retrospective ex-ante reconstruction is permitted only when migrating a decision that occurred before this protocol was adopted. Label it `MIGRATED RETROSPECTIVE RECONSTRUCTION`, cite the surviving contemporaneous evidence, and state what cannot be recovered. Never use retrospective reconstruction to repair a missed record from current live simulation; treat that omission as an audit failure and leave the ex-ante judgment unrecorded until the user is notified and canon is corrected.

## 7. Game and statistical validation

Run the score, clock, possession, field-position, timeout, and entitlement checks before every closed live-game checkpoint. Run the complete statistical reconciliation at every period boundary, before presenting a final score, and during the mandatory postgame audit.

### Score and clock

- Sum every scoring-ledger entry under the selected season's rules. The sum must equal the displayed score with the protagonist team first and opponent second.
- Reconstruct the total from the rule-valid value of each touchdown, try, field goal, safety, defensive conversion, or competition-specific score. Do not hard-code one competition's scoring rules into another.
- Confirm every score change has a valid scoring event and that the next possession follows the applicable kickoff, free-kick, overtime, or end-of-game rule.
- Confirm period transitions, untimed downs, runoff decisions, overtime timing, and final expiration are rule-valid.
- Confirm the game-clock and play-clock running/stopped states and their restart conditions follow from the preceding play, enforcement, timeout, review, period change, or administrative ruling.
- Confirm timeout totals never become negative and every charged timeout, challenge consequence, or injury timeout appears in the event ledger.

### Possession and field position

- Every drive has a valid start, end, and possession-transfer source.
- Ball spots and distance-to-gain progress coherently after plays and enforcement.
- Turnovers, fourth-down failures, kicks, safeties, and replay reversals place the next possession at the rule-valid spot.
- Opening, second-half, and overtime possession agree with the recorded toss, choices, deferral, and applicable period rule.
- The live checkpoint agrees with the last committed event, not with an intended or proposed next play.
- Each team's drive-possession times reconcile with its reported time of possession, and both teams' totals reconcile with played clock time under the applicable statistical convention.

### Team and player statistics

- Use the selected competition's official statistical conventions, especially for sacks, kneel-downs, spikes, laterals, team plays, and overtime.
- Completions do not exceed attempts. Team passing, receiving, rushing, sack, return, kicking, and scoring totals reconcile with individual and team entries under those conventions.
- Interceptions thrown equal opponent interceptions made. Fumbles lost equal opponent recoveries. Team giveaways and takeaways reconcile.
- Field goals made do not exceed attempts; successful tries reconcile with touchdowns and scoring entries.
- Offensive plays, drives, first downs, penalties, and possession totals agree with the event ledger when reported.
- Every compressed routine-sequence total equals the sum of its per-snap state and statistical deltas; its ending state equals the next ledger entry's starting state.
- Individual scoring sums to the team score, allowing only rule-defined team or return scores.
- A player cannot receive a statistic while inactive or unavailable unless the record or governing rules explain the apparent conflict.
- Season totals equal the prior verified total plus the current verified game. Never estimate a missing total and present it as exact.

If any check fails, do not declare the game final. Locate the first inconsistent event, append a supersession if already committed, correct every dependent total, and rerun the audit.

### Final game statistical summary

After the checks pass and before the game is declared final, append a verified final summary. Keep it compact, but include every total needed to preserve score, record, later season totals, workload, evaluation, and historical continuity.

```markdown
### Final game statistics | [Team vs. opponent, exact date]

- Canon class and record form: [Post-divergence simulation event; derived verified final-game statistical summary]
- Final score, protagonist team first: [protagonist team-opponent]
- Final event-ledger entry: [exact heading]
- Statistical convention: [competition, season, and sourcebook version]
- Verification status: [reconciled, or not final]

| Team total | Protagonist team | Opponent | Ledger reconciliation |
|---|---:|---:|---|
| Offensive plays | [value] | [value] | [basis] |
| First downs | [value] | [value] | [basis] |
| Rushing attempts-yards | [value] | [value] | [basis] |
| Completions-attempts-gross passing yards | [value] | [value] | [basis] |
| Sacks-yards and net passing yards | [value] | [value] | [basis] |
| Total net yards | [value] | [value] | [basis] |
| Turnovers | [value] | [value] | [basis] |
| Penalties-yards | [value] | [value] | [basis] |
| Third and fourth downs | [value] | [value] | [basis] |
| Possession time | [value] | [value] | [basis] |
| Kicking, returns, and other material totals | [value] | [value] | [basis] |

| Player | Status/role | Statistical category | Verified game total | Workload or continuity consequence |
|---|---|---|---:|---|
| [Player] | [active role] | [passing/rushing/receiving/defense/kicking/return/other] | [value] | [material note] |

- Scoring total reconciled: [yes/no]
- Possession and drive totals reconciled: [yes/no]
- Team and individual totals reconciled: [yes/no]
- Open statistical uncertainty: [none, or exact item preventing final status]
```

### Cumulative season statistics register

After on-field play ends and the final game statistics reconcile, append a new dated cumulative snapshot as part of postgame finalization. The previous snapshot remains historical evidence; the latest closed snapshot controls. Every new total must equal the prior verified total plus the verified game delta under the applicable statistical convention.

```markdown
### Cumulative season statistics | [Team, season] | Through [exact date and game]

- Canon class and record form: [derived cumulative-statistics snapshot; cite every source heading and inherited class, which may mix a Verified pre-divergence fact baseline with Post-divergence simulation events]
- Prior cumulative snapshot: [exact heading, or initialization baseline]
- Added game summary: [exact heading]
- Games and team record covered: [value]
- Convention/sourcebook version: [reference]

| Team category | Prior verified total | Game delta | New verified total |
|---|---:|---:|---:|
| [Category] | [value] | [value] | [value] |

| Player | Category | Prior verified total | Game delta | New verified total | Availability/workload note |
|---|---|---:|---:|---:|---|
| [Player] | [Category] | [value] | [value] | [value] | [note] |

- Arithmetic and roster-status checks: [passed, or unresolved item]
- Statistics intentionally not carried cumulatively: [categories and reason]
```

Do not silently drop a traded, released, transferred, injured, or departed player's prior team statistics. Preserve totals through the effective departure date and apply the competition's official team/player attribution rules.

### Mandatory postgame finalization

When play ends on the field, set the game status to `ENDED ON FIELD — FINALIZATION PENDING`. Do not label the game `Final`, publish a final schedule result, advance the team record, or proceed to the next event until one completed postgame finalization record proves every item below and closes under the atomic update protocol.

```markdown
## Postgame finalization | [Protagonist team vs. opponent] | [Exact date]

- Canon class and record form: [Post-divergence simulation event; postgame validation/finalization]
- On-field ending event: [exact final event-ledger heading and rule-valid expiration/end condition]
- Score orientation: [protagonist team first throughout]
- Candidate final score: [protagonist team-opponent]

### Score, chronology, and possession proof

- Scoring-ledger entries and sum: [exact references; protagonist total and opponent total]
- Scoreboard/event-ledger agreement: [passed/failed]
- Scoring chronology order: [verified exact order]
- Drive and possession continuity: [verified from opening entitlement through final possession]
- Clock, timeout, penalty, replay, and final-play legality: [passed/failed]
- Score correction required: [none or controlling supersession]

### Final game and cumulative statistics

- Final game statistical summary: [exact heading]
- Team/player arithmetic validation: [passed/failed]
- Prior cumulative season snapshot: [exact heading]
- New cumulative season snapshot: [exact heading]
- Prior totals + game deltas = new totals: [passed/failed]
- Remaining statistical uncertainty: [none, or game remains pending]

### Record, standings, and schedule

- Team record before game: [value]
- Result applied: [win/loss/tie or competition-specific result]
- Team record after game: [value and arithmetic proof]
- Division/conference/competition record after game: [value]
- Standings and tiebreak status: [verified as of exact date/time, source or simulated table]
- Schedule/result entry: [exact heading; protagonist-team-first score]

### Injuries, availability, roster, and workload

- In-game injuries or availability changes: [players and communicated facts, or none]
- Medical records appended: [exact headings or none]
- Document 4 availability/depth/workload updates: [version and changes]
- Document 5 decision-relevant availability: [updated/none]
- Unresolved evaluation or next medical report: [owner and exact time, or none]

### Head-coach decisions: process separate from result

| Decision | Closed pre-result assessment | Outcome | Post-result planning evidence | Quality changed only for corrected decision-time information? |
|---|---|---|---|---|
| [Exact decision heading] | [sound/defensible/questionable/clear error with original reasoning] | [result] | [new evidence or none] | [no, or documented correction—not outcome bias] |

- Consequential decisions all linked: [yes/no]
- Missing pre-result record: [none, or audit failure preventing finalization]

### Reactions and evaluation kept separate

- Internal football evaluation: [attributed staff/executive/player observations, uncertainty, or none yet]
- Internal organizational consequence: [observable action or none]
- Media reporting: [attributed public reports/claims, or none observed]
- Fan/public reaction: [supported observable reaction, or none established]
- Separation check: [internal evaluation was not inferred from media/public reaction, and no private thought was exposed]

### Next state and full continuity audit

- Exact next scheduled event: [date/time, event, location]
- Current focus and pending head-coach decision: [state or none]
- Full postgame continuity audit: [exact heading and passed/failed]
- Audit covered score, game clock, possession, roster, availability, statistics, authority, decisions, schedule, record, standings, deadlines, and information boundaries: [yes/no]
- Canon corrections entered first: [exact headings or none]
- Document 5 global checkpoint and source-version manifest reconciled to candidate Documents 2–4 and this ledger: [yes/no]
- Non-game audit cadence after mandatory audit reset: [0]
- Open canonical update or unresolved invariant: [none required]

### Finalization declaration

- Every required field above passed or resolved: [yes/no]
- Canonical game status: [write `Final — protagonist team [score], opponent [score]` only if yes; otherwise `ENDED ON FIELD — FINALIZATION PENDING`]
- Global package checkpoint: [exact closed label; required for Final status]
```

If any required proof is missing or failed, keep the pending status, correct the first inconsistent record through Document 6 supersession, rerun the full audit, and complete a new finalization record. Media publication, an official-looking scoreboard, or elapsed chat time cannot substitute for canonical finalization.

## 8. Atomic continuity update order

Treat each response's state change as one closed canonical update, except that every consequential head-coach decision requires a closed decision-only update before a separate implementation/outcome update. Both may occur in one response when chronology permits, but the decision checkpoint must close first. Use a human-readable shared label, not an opaque code:

`Canonical update — [exact date/time or game period/clock] — [plain-language scope]`

### Staging and closed-state rules

1. Prepare the complete candidate bundle outside the active copies of the canonical documents, including a candidate Document 6 copy whenever new ledger entries are required. Temporary notes, draft calculations, tentative random outcomes, and validation work are staging only. They are not canon and must not be pasted into an active canonical record area.
2. Preserve the active closed version of every affected file in recoverable version history or temporary rollback storage until the candidate bundle is promoted.
3. The candidate Document 6 contains the candidate-bundle manifest below. It states the target and preceding global checkpoints, the candidate/current version of every Document 1–5 file, each file's preceding content-changing update, and whether owned content changes. Changed Documents 1–4 identify the version they supersede; unchanged documents retain their older content-changing pointers.
4. Document 5 lists the exact effective versions of Documents 1–4 used at the target global checkpoint. The active Document 5 global checkpoint must equal Document 6's latest closed register row. Per-document content-changing pointers need not equal that global checkpoint.
5. An update is open until the candidate Document 6 contains its exact `Commit closed` line and matching closed-register row and the complete candidate bundle is promoted. An open label, a mismatched global checkpoint, or an interrupted write has no canonical force. Restore the affected files to the preceding global checkpoint before resuming.
6. Do not store simulator-only hidden facts in staging destined for a user-visible canonical file. Private state, when supported, remains outside this document system.

Candidate Document 6 must contain this staging manifest before validation. It is omitted from the active ledger if the candidate fails; when the update closes, retain it with the close record as the exact package proof.

| Candidate file | Candidate/current version | Target global checkpoint | Preceding global checkpoint | Preceding content-changing update | Owned content changes? |
|---|---|---|---|---|---|
| Document 1 | [version] | [target] | [preceding] | [label/revision] | [yes/no] |
| Document 2 | [version] | [target] | [preceding] | [label] | [yes/no] |
| Document 3 | [version] | [target] | [preceding] | [label] | [yes/no] |
| Document 4 | [version] | [target] | [preceding] | [label] | [yes/no] |
| Document 5 | [replacement version] | [target] | [preceding] | [preceding snapshot checkpoint] | yes — replacement snapshot |

### Unified commit order

1. Reconcile the last closed state: exact date, authority, information boundaries, rules, roster, pending decisions, and—during a game—the last event and live checkpoint.
2. Stage the full candidate update outside canon. For a consequential live decision, stage only the user's choice and mandatory pre-result assessment, close that decision update under this procedure, and only then resolve or sample the outcome in a later update.
3. Validate the staged material against rules, chronology, roster eligibility, medical and organizational authority, score, clock states and restart rules, possession entitlement, field position, timeouts, replay, and statistics.
4. In the candidate Document 6 copy, begin the shared update. Append controlling correction and supersession records first, followed by all other granular source records: pre-result decisions, game events or outcomes, transactions, medical communications, staff changes, career events, final game statistics, and cumulative-statistic snapshots. Then append the linked schedule/result and dated chronology entries.
5. If the user changes a stable project instruction, create candidate Document 1. If the change affects governing rules, competition, team, location, divergence, head-coach contract, reporting line, authority, or play calling, create the corresponding dated candidate version of Document 2 and/or Document 3. Each changed version identifies what it supersedes; the candidate-bundle manifest supplies its target/preceding global checkpoints and preceding content-changing update.
6. When current player, staff, roster, financial-reconciliation, depth, package, availability, workload, or candidate records change, prepare a candidate Document 4 containing only those content changes plus regenerated dependent summaries and identifying the version it supersedes. The candidate-bundle manifest supplies its target/preceding checkpoints. If none of its owned content changes, retain the active Document 4 version.
7. Always create a full replacement candidate Document 5. Include the exact effective versions of Documents 1–4, target and preceding global checkpoints, current time, current focus, pending matters, live checkpoint if applicable, and audit counter. Do not destroy the active snapshot yet.
8. Run all applicable invariants and the required audit against the complete candidate set. Append the audit, continuity checkpoint, phase archive, team-tenure record, handoff, or mandatory postgame finalization only after its inputs reconcile. A correction entry itself must never be deferred to this step; it belongs at the start of step 4. A completed game cannot receive `Final` status unless the postgame finalization record passes here.
9. In the candidate Document 6, append:

   `Commit closed — [same shared update label] — canonical through [exact date/time or live-game clock]`

   Append the matching row to the candidate Closed canonical update register, then promote candidate Document 6, candidate Document 5, and every changed Document 1–4 version as one logical commit. Document 6 and Document 5 adopt the new global package checkpoint; changed Documents 1–4 adopt it as their content-changing update; unchanged Documents 1–4 retain their existing content versions. If the storage layer cannot replace multiple files atomically, readers continue using the preceding bundle until every candidate file is written and the Document 6 close line, register row, Document 5 checkpoint, and Document 5 version manifest agree.
10. Only after closure present the narrative and compact continuity update to the user.

If interruption occurs before the close line, no simulated implementation or result in the open update happened in canon. Restore or reread the preceding closed versions and discard or restage the temporary material. An explicit user decision in the user's message remains the controlling source instruction: restage and close that exact choice before resolving it, but do not infer additional intent, advance time, or apply an outcome.

## 9. Continuity audits

### Enforceable non-game audit cadence

A `substantive non-game response` is one assistant response outside a live game that closes at least one canonical update and does one or more of the following: advances the master date or time; implements or resolves a material user decision; changes roster, availability, staff, authority, preparation, resources, schedule, record, standing, contract, career, or another continuity-critical fact; or compresses a quiet period to a later dated state. It counts once even if that response contains several closed updates.

Do not count a clarification that advances no simulation state, a verbatim restatement, research performed before a decision, pre-initialization migration work, or a live-game response. A contradiction or correction invokes its own audit trigger rather than being counted as routine cadence.

Store these fields in every audit result and mirror the current count in Document 5:

- Substantive non-game responses since the last full audit: [0-3]
- Qualifying response dates and closed update labels: [list]
- Last full audit: [exact heading/date]
- Next cadence audit: [after how many additional qualifying responses]

Increment the candidate count before closing a qualifying response. If it would reach four, perform the full audit within that response, state that the fourth response triggered it, and reset the closed count to zero. Any other mandatory full audit also resets the count to zero. The count is an audit-control measure, not elapsed time or a simulation turn number.

### Mandatory triggers

Conduct a full audit:

1. After every on-field game ending and before canonical `Final` status.
2. After every four substantive non-game responses.
3. At the end of a season phase.
4. After a major injury.
5. After a major transaction.
6. After a staff or play-calling change.
7. After a head-coach contract change.
8. Before and after a long time jump.
9. Before creating a new-chat handoff.
10. Whenever a contradiction or unexplained gap is detected.
11. At former-team tenure closure and again after the new-team baseline is complete.

### Audit checklist

- Exact master date, season, phase, week, elapsed time, and next event.
- Schedule, completed results, team record, standings, postseason implications, and deadlines.
- Live-game score, period, game/play-clock values and running/stopped/restart states, possession, down and distance, ball location, direction, toss/deferral and next-period entitlement, timeouts, replay/challenge status, and last play.
- Roster status, active/inactive list, transactions, contracts or eligibility, health, availability, depth chart, packages, and recent workloads.
- Game and season statistics, scoring chronology, drive ledger, and arithmetic.
- Organizational authority, reporting lines, play-calling delegation, medical authority, and staff responsibilities.
- User decisions, approved game plans, standing instructions, promises, objections, and unresolved commitments.
- Staff/player/organizational relationships only where supported by events or communications.
- Applicable league, labor, roster, transaction, recruiting, historical, and social rules for the exact date.
- Information known to the head coach, its source, and material information still unknown.
- No uncommunicated hidden fact or private state has entered the user-visible ledger, audit, archive, or handoff.
- Conflicts between Documents 1-6 and any correction or supersession required.
- Non-game audit count, qualifying response list, last reset, and next cadence trigger.

Append a concise audit result stating the date range checked, conflicts found, corrections entered, unresolved uncertainty, qualifying-response count before the audit, triggering update, and reset count. Do not certify accuracy when a check remains open.

## 10. Season-phase archives

At each actual defined phase boundary, append a frozen archive before rewriting Current Season State for the next phase. Typical phases include preseason or camp, regular season, postseason, and offseason; use the selected competition's actual calendar. A coaching departure in the middle of a phase is not a phase boundary and uses the team-tenure closure record in Section 12 instead.

```markdown
## Phase archive | [Team] | [Season and completed phase] | Closed [exact date]

- Global package checkpoint: [exact closed label]
- Governing Documents 1–5: [exact version/effective date; for Documents 1–4 include each last content-changing update]
- Date range covered: [start through end]
- Record and final standing/status: [verified]
- Schedule and results: [compact list or linked register span]
- Roster at close: [active status summary and link to Document 4]
- Significant transactions and injuries: [dated list]
- Staff, authority, and play-calling changes: [dated list]
- Verified team and player statistics: [only continuity-critical totals]
- Material head-coach decisions: [dated list with decision-quality records]
- Organizational and career developments: [dated list]
- Corrections/superseded records during phase: [list]
- Commitments carrying forward: [owner, deadline, and status]
- Information still uncertain: [list]
- Next phase and first scheduled event: [exact date]
```

Archives do not replace the append-only ledgers. They provide one possible verified baseline. New-chat handoffs use the latest suitable closed continuity checkpoint—whether an initialization baseline, prior handoff, audit checkpoint, phase archive, or team-tenure closure—and name only the later excerpts that remain necessary.

## 11. New-chat handoff

Before a new chat, run a full audit and close a dated handoff update. The handoff must be bounded. Select the latest closed continuity checkpoint that already proves the required state, then name only the later Document 6 excerpts needed to verify current decisions, changes, and unresolved matters. Never require every entry since a season-phase boundary or the entire prior game/season merely because those records exist.

Permitted baselines, in descending preference, are:

1. The latest audited new-chat handoff or live-game checkpoint that remains compatible with the current state.
2. The latest full-audit continuity checkpoint or team-tenure closure.
3. The latest phase archive.
4. Before any phase archive exists, the closed initialization or pre-initialization migration baseline.
5. If none exists, create and audit a compact baseline before creating the handoff; do not fall back to chat memory.

The receiving chat reads the exact versions of Documents 1-5 named in the handoff, the selected baseline, and the explicitly named relevant excerpts. It does not read an unbounded ledger span or need the prior chat. Simulator-only hidden state is never copied into this user-visible handoff.

### Midseason or offseason handoff

```markdown
## New-chat handoff | As of [exact date and time]

- Global package checkpoint: [must equal Document 5 and the latest Document 6 closed-register row]
- Preceding global package checkpoint: [exact label]
- Document 5 source-version manifest: [exact manifest heading/checkpoint]
- Document 1 version/effective date and last content-changing update: [exact]
- Document 2 version/effective date, lock, and last content-changing update: [exact]
- Document 3 version/effective date and last content-changing update: [exact]
- Document 4 content version/effective date and last content-changing update: [exact]
- Document 5 snapshot version/effective date: [exact]
- Selected closed continuity baseline: [exact heading/date/update label]
- Last fully committed event: [dated entry]
- Team, competition, season, phase, and week: [state]
- Factual divergence point: [exact event/date]
- Record, standing, and schedule status: [state]
- Next opponent/event and time remaining: [exact date/time]
- Head-coach contract, reporting line, and final authority: [summary]
- Offensive, defensive, and special-teams play callers: [names/responsibilities]
- Current roster/depth/packages source: [Document 4 version/date]
- Material availability limits: [players and current medical status]
- Approved strategy or game plan: [current standing instructions]
- Most recent user decisions: [dated list]
- Pending head-coach decisions: [decision, deadline, authority, and known information]
- Active personnel, staff, contract, or organizational matters: [owner/deadline]
- Upcoming league/institutional deadlines: [exact dates]
- Unresolved promises, objections, disputes, and career contacts: [list]
- Known information boundaries and live rumors: [source/uncertainty]
- Latest completed continuity audit: [date and result]
- Substantive non-game responses since that audit: [count and qualifying update labels]
- Corrections the new chat must honor: [supersession list]
- Required Document 6 excerpts to read: [finite list of exact headings/date ranges and why each remains relevant]
- Open or staged updates: [none; a handoff cannot close otherwise]
```

The receiving chat must confirm that Document 5's global package checkpoint equals Document 6's latest closed register row and that Document 5 names the exact effective versions of Documents 1–4 used at that checkpoint. A Document 2, 3, or 4 content-changing pointer may legitimately be older than the global checkpoint when its owned content did not change. Restate any true mismatch before advancing time. Absence of a prior-chat detail is not permission to invent it.

### Live-game exact checkpoint

Create and close this checkpoint after every response during a game and immediately before a live-game chat handoff. A live-game handoff uses this checkpoint as its closed continuity baseline and names only the current-game scoring, drive, decision, availability, and statistical excerpts not already reproduced here.

```markdown
## Live-game checkpoint | [Game] | Committed through [period and clock]

- Global package checkpoint: [exact closed label; must equal the active Document 5 checkpoint]
- Exact game date, local time, and time zone: [exact]
- Document 5 snapshot version/effective time: [exact]
- Document 5 source-version manifest: [exact manifest heading or complete Documents 1–4 version list]
- Governing Document 2 game-rule version: [exact]
- Score, protagonist team first: [protagonist team-opponent]
- Period and game clock: [exact]
- Game-clock status and restart: [running/stopped; starts on snap/ready/referee signal/other exact rule]
- Play clock: [exact when material; mandatory at a live decision stop]
- Play-clock status and restart: [running/stopped/not started; reset value and controlling event]
- Possession: [team]
- Down and distance: [exact]
- Ball location and direction: [exact]
- Timeouts remaining: [both teams]
- Challenge/replay status: [remaining challenges, active review, or none]
- Immediately preceding play: [result and enforcement]
- Current drive: [start, plays, net yards, elapsed time, and result so far]
- Possession source: [how this team obtained the ball]
- Opening toss and choice: [winner, receive/kick/defer/goal choice, and first-half kickoff receiver]
- Second-half possession entitlement: [team and basis, or already exercised]
- Overtime toss and opening-possession entitlement: [result/basis, not applicable, or not yet reached]
- Next period/half possession procedure: [carryover down, kickoff team/receiver, overtime procedure, or game over]
- On-field personnel/package: [when material]
- Relevant availability and snap/workload limits: [current]
- Ejections, disqualifications, or temporary absences: [current]
- Staff recommendations and observed opponent behavior: [known to head coach]
- Approved in-game adjustments still in force: [list]
- Offensive/defensive play caller and head-coach game-management authority: [state]
- Pending penalty, review, measurement, medical update, or substitution: [state]
- Pending head-coach decision: [exact question and time available, or none]
- Scoring-ledger total check: [reconciled protagonist-team–opponent score]
- Statistical checkpoint: [only totals needed to resume accurately]
- Last committed event-ledger entry: [human-readable drive/play label]
- Required current-game excerpts beyond this checkpoint: [finite list of exact headings, or none]
```

Before closure, verify both clock statuses and restart rules, toss/deferral records, next-period entitlement, and the pending-decision boundary against the game ledger. Never simulate the pending decision or next snap in the handoff. The new chat resumes from the last closed state.

## 12. Team-change protocol and unresolved obligations

A change of teams ends the head coach's authority over the former team but does not erase career history, contractual duties, promises, or unresolved processes.

Before the effective change:

1. Run a full audit through the final instant of the coach's former-team authority.
2. Record the contact, interview, offer, user decision, contract terms, permission, buyout, and effective date in the career ledger.
3. Create a `Team-tenure closure` record and a frozen outgoing Document 4 snapshot. Do not close or rename the competition's season phase unless the departure coincides with a real phase boundary.
4. List every unresolved former-team matter with its responsible authority, deadline, confidentiality/public status, and whether the departing coach retains a duty, consultation role, or merely an interest.
5. Record assistant contracts, interview permissions, retention decisions, offers, and follow-up obligations individually. Staff members and their employers decide independently whether they move.
6. Record outstanding player conversations, discipline or communicated medical processes, personnel recommendations, media duties, and transition work without inventing promises the user did not make or exposing hidden information.
7. Preserve tampering, contact, recruiting, transfer, confidentiality, and contract restrictions applicable on the exact date.
8. Freeze the former-team record, schedule progress, game summaries, and cumulative team/player statistics only through the effective departure instant. The former organization and season continue independently after the protagonist leaves.

```markdown
## Team-tenure closure | [Head coach] | [Former team] | Effective [exact date/time]

- Global package checkpoint: [exact closed label]
- Tenure date range: [start through effective departure]
- Departure basis and career-ledger entry: [reference]
- Final former-team authority instant: [exact]
- Record, standing, schedule progress, and active phase at departure: [state; phase remains open if competition says so]
- Frozen Document 4 version/date: [exact outgoing roster/staff snapshot]
- Frozen availability, depth, packages, and staff responsibilities: [compact reference/extract]
- Game and cumulative season statistics through departure: [exact final-game/cumulative headings]
- Former-team Document 2 and Document 3 versions at closure: [exact]
- Unresolved obligations carried separately: [list/table references]
- Information and confidentiality boundary: [what may lawfully carry]
- Corrections or open audits: [none required for closure]
```

For the new team, complete a new baseline before any football activity advances:

1. Version and re-lock Document 2 for the new team, location, exact date, competition, governing rules, schedule, calendar, roster/labor or eligibility system, finances, technology, and historical boundary. If the competition rules are unchanged, cite the continuing rule version while still replacing team- and location-specific fields. If the league or level changes, rebuild every applicable rule section.
2. Create a dated Document 3 version for the new contract, reporting structure, authority map, organizational structure, staff-hiring rights, play-calling role, and first effective date.
3. Create a new Document 4 roster/staff baseline without overwriting the frozen outgoing snapshot.
4. Replace Document 5 with the new team's current state while continuing to list any former-team duty, payment, permission, staff, or transition deadline that still affects the coach.
5. Close a full audit proving that Documents 2-5 and this ledger agree.

Carry automatically only the head coach's established background, user-confirmed standing personal instructions, audience-specific reputation supported by prior events, lawful relationships, and expressly portable commitments. Former-team contractual duties remain active obligations even when they are not portable authority within the new organization.

### Carry-forward obligations template

| Matter | Originating team | Responsible authority now | Head-coach remaining role | Deadline | Status and next update |
|---|---|---|---|---|---|
| [Contract/staff/player/operations matter] | [Team] | [Person/role] | [Duty, consultation, no authority, or none] | [Exact date] | [Open/fulfilled/transferred/disputed] |

Do not treat silence after departure as resolution. Close each matter with a dated fulfillment, transfer, expiration, waiver, rejection, or supersession entry.
Mirror every still decision-relevant obligation and deadline in Document 5 until it closes, even though the coach no longer has former-team authority.

## 13. Canonical record area

Before career initialization, this area may contain only:

- verified historical facts that form the proposed starting baseline;
- explicit user-confirmed coach or alternate-history canon;
- migration provenance and conflict records;
- corrections and supersessions of supplied material;
- source, rules, roster, staff, schedule, or authority reconciliation records;
- pre-initialization audits, continuity checkpoints, and handoffs.

Label each such entry `PRE-INITIALIZATION RECORD — NOT A SIMULATED EVENT`. It may document what was verified, migrated, rejected, corrected, or left unresolved, but it may not create a game, practice, conversation, transaction, injury, hiring result, player choice, press event, career development, or other post-start simulated occurrence. After explicit initialization, append simulation records under the same closed-update protocol.

Keep protocol text above unchanged unless the user approves a system revision. Document 6 remains the sole complete correction history; Documents 2-5 retain only current values and pointers to entries below.

### Pre-initialization readiness transition

Set this document's `Readiness` to `READY` only in the same closed pre-initialization global checkpoint that:

1. records the accepted starting baseline, migration corrections, and source/canon classifications without creating an in-world event;
2. confirms a locked active-only Document 2, a substantively complete candidate `READY` Document 3, and a `RECONCILED` or nonblocking `RECONCILED WITH NOTED UNCERTAINTY` Document 4 for the exact same mode, team, date, and divergence point;
3. validates the complete candidate Document 5 snapshot and sets its `Readiness` to `READY`;
4. includes a full continuity audit and bounded first handoff;
5. has no open update or blocking conflict; and
6. closes Documents 3, 5, and 6 together under one global package checkpoint.

This simultaneous administrative transition avoids a circular prerequisite: each candidate is checked against the others before any is promoted. `READY` means the package can be initialized or resumed accurately; it does not itself initialize the career. Document 5's `Simulation status` remains `NOT INITIALIZED` until the user's later explicit command.

### Closed canonical update register

Append one row for each closed update. The final valid row is Document 6's global package checkpoint and must equal active Document 5; never rewrite an earlier row.

| Global package checkpoint label | Canonical through | Preceding global checkpoint | Content versions changed | Closed continuity baseline created | Non-game cadence count after closure |
|---|---|---|---|---|---:|
| `[No closed updates]` | — | — | — | — | 0 |

An open update is never entered in this register. Candidate entries bearing a label with no matching close row have no canonical force.

### Pre-initialization baselines, verified history, and migration corrections

[No entries]

### Dated chronology

[No entries]

### Schedule and results

[No entries]

### Transactions, injuries, staff, and career events

[No entries]

### Game records and decision-quality logs

[No entries]

### Final game summaries, cumulative season statistics, and postgame finalizations

[No entries]

### Audits, phase archives, corrections, and handoffs

[No entries]
