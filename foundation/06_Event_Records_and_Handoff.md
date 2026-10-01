# Document 6: Event Records and Handoff Protocol

## Purpose and status

**Document status:** Durable record-ownership and continuity protocol
**Protocol version:** 2.0, domain records and annual index
**Adopted:** October 1, 2026, at the user's instruction; no simulation clock advance.

Dated football evidence belongs in its actual trade, signing, hiring, medical, training, game or season-review record. There is no central annual record. This document governs those records; it does not collect their narratives. [Document 5](../state/05_Current_Season_State.md) is the current resume snapshot. [Record.md](../career/2014/Record.md) is a generated chronological index with one dated sentence and link per event. [The repository map](../docs/repository_map.json) identifies actual owners and compatibility aliases.

In the protocols below, a Document 6 event or evidence record means the appropriate domain-owned record governed here, never a second copy in this foundation file. A game play sequence or scoring record is part of its game receipt, not an annual narrative ledger. Preserve existing event identities and frozen receipts.

Calendars contain dates, deadlines and appointments. Records explain completed work. Current roster, contract and availability views derive from their sources. Write each full account once. Use descriptive links rather than visible entry numbers. Preserve corrections and original evidence; a presentation rewrite does not resolve new events or alter outcomes.

## 1. Canonical record rules

1. Record every material event on the date it occurred or became effective. During a live game, also record the period and game-clock time.
2. Assign the shared Document 2 canon class separately from the event record form. The active classes are `Verified pre-divergence fact`, `User canon`, `Post-divergence simulation event`, `Attributed report or assessment`, `Labeled inference`, `Unresolved legacy claim`, and `Undetermined`. An intentional counterfactual baseline uses `User canon` plus a Document 2 divergence entry. `Quarantined actual-future comparator` is authoring-only and never enters the active event record.
3. Record only information that materially changes chronology, authority, personnel, availability, preparation, results, statistics, relationships, resources, commitments, or career options.
4. Never erase or silently rewrite a dated historical entry. Correct it through a dated supersession in the affected event owner.
5. Use the latest valid supersession in the latest closed canonical update when reconstructing state. Preserve the superseded text so the reason for the change remains visible.
6. A scheduled event, transaction, injury update, or staff change is not effective merely because it was discussed. Record the decision maker, approval, rule mechanism, effective time, and any condition precedent.
7. A rumor is not an event. Record its source, audience, and uncertainty without converting it into objective world state.
8. An unambiguous user decision is canon when the user makes it. A question, hypothetical, or incomplete instruction is not. Implementation and outcome are separate records.
9. Publicly verified facts about real people remain distinct from fictional post-divergence developments.
10. If a record cannot be reconciled, stop chronological advancement, identify the conflict, apply the project canon authority order, append the correction, and then continue.
11. These are user-visible records. Never place an uncommunicated hidden fact, private thought, concealed opponent plan, unfinished medical conclusion, or confidential decision unknown to the head coach in it. If the platform supports private simulator state, preserve that state outside all six user-visible canonical documents. If it does not, leave the matter undetermined.
12. When a previously hidden fact is later communicated through a plausible channel, append the record on the communication date. The entry may state an earlier effective or occurrence date only then, and must distinguish “effective on” from “learned by the head coach on.” Never backdate the coach's knowledge.
13. The affected event owner retains the full correction and supersession history. Documents 2-5 retain only the controlling source reference and current value; they do not maintain a competing narrative history.

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

## 2. Annual record and dated event ownership

The annual `Record.md` contains only an actual date or date range, one plain-language sentence and a link to the event owner. It is generated from public event metadata at those owners. It contains no roster snapshot, cap table, practice narrative, numbered entry or software release. Split mixed updates into their actual dated events. File offseason events by their actual calendar year, including January-to-March events previously buried in the preceding year. January and February playoff and season-honours events remain with their NFL season.

Write the actual event once at its destination. Preserve its effective date, communication date when different, decision authority, conditions, supported consequences and unresolved matters where relevant. Use the existing format for that kind of work. Never manufacture an event or an additional file to fill a date.

Each source event uses an `event-record` comment with a descriptive stable `id`, ISO `date`, optional `date_end`, concise `summary`, and `status`. Technical reconciliation records use `kind: technical` and do not appear in the football record. A closed update carries its exact existing checkpoint label, canonical-through date and closure sequence at its actual source. Compatibility aliases for frozen numeric references belong only in the existing repository map. Metadata is not a second narrative record and never contains private engine material.

An event referring to the preceding NFL season, such as its January playoff game, may declare that season explicitly. Distinguish season membership from the calendar date. Regenerate the annual record after writing or correcting its source.

## 3. Schedule and results register

The calendar holds the verified or approved schedule and dated amendments. Results belong in game outputs and receipts; the annual record links to them. A postponement, flex, venue change, cancellation or correction names its source and the announcement it supersedes. Do not append results, roster totals or coaching findings to the calendar.

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

## 4. Personnel, medical, staff, and career records

Each domain record preserves its dated history. Later developments reference the prior dated entry. Record an internally confidential matter here only if it has been communicated to the head coach and is therefore part of the user's legitimate information picture; otherwise keep it outside the user-visible canonical documents or leave it undetermined.

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
- Game-day staff arrangements: [record a meaningful change when applicable]
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

Routine snaps may share one source event only when no consequential head-coach decision, unresolved administrative ruling, material availability decision, or required granularity stop occurs between them. Compression changes presentation, not state fidelity. The entry must preserve every snap's state transition and statistical delta; “three-and-out,” “touchdown drive,” or a prose drive summary alone is insufficient.

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

- Sum every scoring-source event under the selected season's rules. The sum must equal the displayed score with the protagonist team first and opponent second.
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
- Every compressed routine-sequence total equals the sum of its per-snap state and statistical deltas; its ending state equals the next source event's starting state.
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
- Final event-source event: [exact heading]
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

- Scoring-source events and sum: [exact references; protagonist total and opponent total]
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
- Document 5 global checkpoint and source-version manifest reconciled to candidate Documents 2–4 and the closed source records: [yes/no]
- Non-game audit cadence after mandatory audit reset: [0]
- Open canonical update or unresolved invariant: [none required]

### Finalization declaration

- Every required field above passed or resolved: [yes/no]
- Canonical game status: [write `Final — protagonist team [score], opponent [score]` only if yes; otherwise `ENDED ON FIELD — FINALIZATION PENDING`]
- Global package checkpoint: [exact closed label; required for Final status]
```

If any required proof is missing or failed, keep the pending status, correct the first inconsistent record through Document 6 supersession, rerun the full audit, and complete a new finalization record. Media publication, an official-looking scoreboard, or elapsed chat time cannot substitute for canonical finalization.

## 8. Atomic continuity update order

Every state-changing task closes a complete candidate bundle. A consequential head-coach choice still needs a closed pre-result decision before its outcome is resolved. Reorganization and report editing never substitute for those two updates.

1. Reconcile the last closed state, exact date, authority, information boundaries, rules, roster, pending decisions and any live-game checkpoint.
2. Stage the full change outside active canon. Write the decision, correction or event first in the appropriate owner, using an exact date and descriptive label. Preserve earlier evidence and the pre-result record.
3. Validate rules, chronology, medical and organizational authority, roster eligibility and the applicable score, clock, possession, field-position, timeout, replay and statistical invariants. Apply Section 7's mandatory game finalization before any final result.
4. Update affected current views only: roster, availability, role, contract, cap, picks, staff, statistics and standings. Plans change only when the approved teaching or operating method changes. Calendars change only when dates or scheduled appointments change.
5. Prepare changed foundation versions when the user changes a rule or authority. Document 4 changes only when its owned facts change; otherwise preserve its existing content version and checkpoint.
6. Prepare Document 5 from those exact owners, naming the effective foundation versions and Document 4 version. Preserve the preceding active snapshot until all checks pass.
7. Attach the closure to the actual event owner using the stable source reference, exact `Canonical update` label, canonical-through date and ordered closure sequence. Preserve any actual preceding-checkpoint and content-version proof. One source carries the closure for a mixed batch; each constituent event retains its own effective date and owner. No central closure narrative or separate event registry is created.
8. Regenerate the annual one-line record and affected derived views. Review summaries against their source before refreshing any review receipt. Run repository continuity and relevant domain checks against the entire candidate bundle.
9. Promote all changed owners and current views in one logical commit. Document 5's global checkpoint must match the latest closed source metadata; Document 4's retained checkpoint must resolve to a legitimate earlier closure. If the write is interrupted or checks disagree, use the preceding closed bundle, never a partial candidate.
10. Present the football result only after closure. Private seeds, outcome packets and uncommunicated state remain outside public Git. A change to Document 5 does not permit advancing the private snapshot from an unmerged branch.

A candidate-only event has no canonical result until its bundle closes. An explicit user decision remains the controlling instruction even after an interrupted write; restage that exact choice without inventing further intent or rerunning a closed outcome. Current-source metadata supplies continuity, while the annual record supplies navigation.

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
- No uncommunicated hidden fact or private state has entered the user-visible event record, audit, archive, or handoff.
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

Archives do not replace the dated source records. They provide one possible verified baseline. New-chat handoffs use the latest suitable closed continuity checkpoint—whether an initialization baseline, prior handoff, audit checkpoint, phase archive, or team-tenure closure—and name only the later excerpts that remain necessary.

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

- Global package checkpoint: [must equal Document 5 and the latest closed source metadata]
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

The receiving chat must confirm that Document 5's global package checkpoint equals the latest closed source metadata and that Document 5 names the exact effective versions of Documents 1–4 used at that checkpoint. A Document 2, 3, or 4 content-changing pointer may legitimately be older than the global checkpoint when its owned content did not change. Restate any true mismatch before advancing time. Absence of a prior-chat detail is not permission to invent it.

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
- Last committed event-source event: [human-readable drive/play label]
- Required current-game excerpts beyond this checkpoint: [finite list of exact headings, or none]
```

Before closure, verify both clock statuses and restart rules, toss/deferral records, next-period entitlement, and the pending-decision boundary against the game ledger. Never simulate the pending decision or next snap in the handoff. The new chat resumes from the last closed state.

## 12. Team-change protocol and unresolved obligations

A change of teams ends the head coach's authority over the former team but does not erase career history, contractual duties, promises, or unresolved processes.

Before the effective change:

1. Run a full audit through the final instant of the coach's former-team authority.
2. Record the contact, interview, offer, user decision, contract terms, permission, buyout, and effective date in the career appointment/contract record.
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
- Departure basis and career-source event: [reference]
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
5. Close a full audit proving that Documents 2-5 and the closed source records agree.

Carry automatically only the head coach's established background, user-confirmed standing personal instructions, audience-specific reputation supported by prior events, lawful relationships, and expressly portable commitments. Former-team contractual duties remain active obligations even when they are not portable authority within the new organization.

### Carry-forward obligations template

| Matter | Originating team | Responsible authority now | Head-coach remaining role | Deadline | Status and next update |
|---|---|---|---|---|---|
| [Contract/staff/player/operations matter] | [Team] | [Person/role] | [Duty, consultation, no authority, or none] | [Exact date] | [Open/fulfilled/transferred/disputed] |

Do not treat silence after departure as resolution. Close each matter with a dated fulfillment, transfer, expiration, waiver, rejection, or supersession entry.
Mirror every still decision-relevant obligation and deadline in Document 5 until it closes, even though the coach no longer has former-team authority.

## 12.5 Pre-hire search record boundary

Before full career initialization, the January 2013 hiring search is the one authorized simulated phase that does **not** write event-by-event records into Document 6. Its ex-ante decision record lives in `career/<year>/offseason/hiring_search.md` under Documents 1 §9.4 and 3 §10.

Document 6 must not independently generate, resolve, or duplicate hiring-search turns during PRE-HIRE SEARCH. After a user-authorized offer is accepted and the project enters HIRED / INITIALIZATION BUILD, the initialization baseline may import one concise `PRE-HIRE SEARCH CLOSURE` summarizing the already-resolved search: date range, teams pursued, material user decisions, offers/counters, accepted result, and the exact hiring-search record reference. That import is a continuity bridge, not a second resolution of the search.
## 13. Record destinations and readiness

- Trades: the individual negotiation/completed trade, with a short completed-trades index.
- Signings, releases and tenders: free-agency event history; ongoing amounts in the contract owner.
- Medical: the dated incident or communicated availability history; the current injury view links to it. Preserve an incident across season boundaries and distinguish medical clearance from coaching deployment.
- Staff: the hiring/departure or responsibility decision; the current staff register and payroll derive from it.
- Training: the phase report, including dated individual findings. The plan owns intended work.
- Games: the established preseason or regular-season output and its one canonical receipt. Cumulative statistics and standings are generated from receipts.
- Player assessments: the opening annual player card, carrying dated during-year observations without overwriting its baseline, and a separate final assessment after the season closes. There is no new full assessment card after every phase.
- Position battles: one preseason card per documented contested spot, grouped by unit and position, comparing the actual candidates. No card or empty position directory when no competition exists. Cards cite observations and decisions; they do not award roles.
- Season review: player exit interviews, coach reviews, final assessments and the handoff.
- Repository changes: existing technical documentation at the affected subsystem, omitted from the football chronology.

Initialization still requires the accepted divergence and team, reconciled rules and authority, audited roster, exact source versions, a bounded handoff and a closed administrative baseline. `READY` describes consistency; it never initializes the career or authorizes a game by itself. Preserve the PRE-HIRE SEARCH exception in Section 12.5 and all game-readiness gates.

The annual record is generated navigation. If it disagrees with its source, repair the index after validating the owner. A current snapshot never overrides the owner it summarizes.
