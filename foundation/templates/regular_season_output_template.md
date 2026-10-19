# Game Report template (regular season and postseason)

**Status:** The user's weekly game turn template, confirmed September 30, 2026. Applies to every regular-season and postseason game turn from the 2014 season onward; 2013 turns keep the earlier format, retained in git history. From 2014 Week 6 (October 19, 2026, rebuild step 4) the filled page is the week's **Game Report**, `Game_Report.md` in the week's folder, the result page of the game week's three pages: the Game Week Briefing (what Stone needed to know), his Game Plan (what he decided) and the Game Report (what happened and what changed). 2014 Weeks 1 to 5 keep their `output.md` as written. From Week 6 section 6 is headed "Weekly personnel and availability", without the earlier last word, which the clean-page check does not allow on a page; the earlier reports keep their heading as written.
**When used:** Regular-season game weeks, byes and postseason turns. An unplayed slot contains preparation only; do not fill a result, player performance or box score before the game is resolved. Use the [preseason output template](preseason_output_template.md) for preseason turns and the [offseason output template](offseason_output_template.md) for offseason turns. Document 7 governs simulation; this template governs presentation.

Every Game Report follows this layout. Bracketed text is an authoring prompt, not a requirement to manufacture content. Italic instructions are carried out and left out of the output. Apply the [game-output workflow](../../docs/game_output_workflow.md) before writing or restyling a turn.

The confirmed weekly layout has unnumbered Coach info followed by seven numbered sections. The game is section 3. Its quarter narrative and result summary lead directly into the **Game review** (the block the earlier outputs titled "Report to render"), followed by the existing player findings, decisions, availability and full generated statistics. Postgame media stays in section 4, coaching carry-forward in section 5, personnel in section 6 and closure in section 7. The preseason template has its own eight-section numbering; do not renumber either to match the other.

## Rules for every turn

*These rules govern the whole turn. None of this section appears in the output.*

1. **Keep the career and its evidence.** Use the existing preparation, user decisions, result, medical record and statistics. A presentation revision does not run another game, advance the clock, change a role or supply a missing conversation. Retain recorded preparation dates and supporting sources.
2. **Statistics are generated; the football account is authored.** Preserve the complete receipt-derived statistics below. Verified record and score tables may also be rendered. Write the preparation, story, coaching review and media from the actual evidence; do not turn a field or JSON key into a sentence to fill a section.
3. **Research informs the writing.** Use the inspected references in the [media method](../../docs/head_coach_media_method.md) and report research. Consult more sources when an unfamiliar situation or a factual question requires them. There is no per-section browsing quota. Sources supply form and football context, never this career's events or dialogue.
4. **Questions are original.** Ask what a reporter could reasonably ask from public information at that point. Let follow-ups respond to Stone's answer. Do not transplant another session's questions or assign an invented line to a real reporter.
5. **Stone remains user-controlled.** In an authorized media writeup, routine answers may express recorded decisions and established positions in his voice. Preserve the user's actual words and their meaning. Do not create a new commitment, policy, personnel decision, accusation or private motive; a consequential unanswered choice returns to the user.
6. **Keep machinery in its proper owners.** Preserve event metadata, receipts and validation records. Their contents do not become football narration. A material evidence gap is described once in the supporting notes, and in the football account only where it changes the conclusion or the next decision.
7. **The page is football only.** A Game Report passes the clean-page check in repository validation (rebuild rule 4): no internal code or identifier, no file path, script or module name, no system note, disclaimer or version label, and none of the words engine, branch, receipt, kernel, ledger, snapshot, checkpoint or simulation. Write "the game book", "the play-by-play", "the film", "the staff record". Link to pages (the Game Week Briefing, the Game Plan, the medical history, the standings, the statistics), never to a file in the data area. The only markup is the event-record line and the two box-score markers, each on a line of its own.

### Prose standard

- Write preparation and game accounts in past tense, third person, with plain verbs and named people. Media answers use Stone's spoken voice.
- Explain what happened and what the evidence supports. A sack establishes a sack; a recorded protection finding can explain it. Do not invent a missed assignment, film session or sideline exchange to bridge the two.
- Give important football detail room. Select statistics and sequences because they explain a finding, rather than repeating every table or narrating every possession.
- Keep the seven sections and their purposes. Subheadings and fields are prompts; omit unsupported optional findings, empty lists and duplicate explanations. No quota for praise, criticism, standout players or words.
- Let the story, coaching review and next work do different jobs. The story gives the action; the review examines the actual work; the carry-forward names the resulting task.
- Avoid generic importance claims, slogans, staged drama and audit language. Do not invent private thoughts, crowd reactions or weather as mood. Read the prose aloud and rewrite sentences that sound like a form being completed.
- No em dashes, rhetorical questions in the narrator's voice, or one-line paragraphs for dramatic effect. Reporter questions and ordinary spoken answers remain natural.

### Runner mechanics

*Carried out by whoever runs the turn. None of this block appears in the output.*

- *Storage. The complete protagonist turn is the week's Game Report, `runtime.seasons.SeasonPaths.game_report(N)`: `career/[year]/Regular_Season/Games/Week_NN/Game_Report.md` for a regular-season week and under `career/[year]/Postseason/Games/` for a postseason game (2014 Weeks 1 to 5: `output.md`, as written). It sits beside the week's Game Week Briefing and Game Plan; no separate prep, press, recap or highlights file. Background games go to `career/[year]/Regular_Season/League_Results/week_NN.md` as a scores-and-highlights roundup and are never expanded into this format: `python scripts/render_week_pages.py --season YEAR` builds that page's dates, byes, score table and one heading per game, and the highlights (two to four sentences and one to three standouts per game) and the reactive events are stored in that page's data twin, `data/[year]/Regular_Season/League_Results/week_NN.json` (`games` keyed by event id, `reactive_events`), which the page renders under those headings. The page is never edited by hand; a rebuild replaces anything written on it.*
- *The event record. The game's event-record line sits on a line of its own in the Game Report. Its one-line summary becomes the game's line in the annual record, which the clean-page check reads, so it is written in football words: the score, the decisive sequences, the material decisions, injuries and transactions, the record and the standing. No kernel, generation, audit or validation wording; `python scripts/render_annual_record.py YEAR` refuses a summary that breaks the rule and names the problem.*
- *Receipts. Every closed game produces a public stat receipt under the season's stats directory (`SeasonPaths.receipts`, with postseason receipts in the sibling `postseason_receipts` directory): a full receipt with the complete player dictionaries, snap `play_ledger`, drives and named-call statistics for the protagonist's game, and a `compact_stats` receipt for each background game. Everything statistical is generated from the receipts, never typed: the full stats block below, the standings (`python scripts/render_standings.py YEAR`) and the season statistics (`python scripts/render_season_stats.py YEAR --team TEAM_ID`) are all regenerated after the week closes. A missing attribution stays missing; no real historical statistic fills it.*
- *The full stats block. The whole "Full stats for the game" block is generated by `python scripts/render_box_score.py --season YEAR --write <Game_Report.md>` between the markers `<!-- box-score event=EVENT_ID team=[Team name] -->` and `<!-- /box-score -->`, each on a line of its own where that block belongs. Nothing inside the markers is typed or edited by hand; `scripts/validate_repository.py` fails if the block differs from its receipt. In a Game Report the sacks columns are headed SCK/YDS (an `output.md` keeps SCK-YDS as written). The renderer records in its docstring which rows and columns the receipt supports and leaves out the rest.*
- *The pages the close rewrites. After the game closes: the box score above; `python scripts/render_week_pages.py --season YEAR` for the Games and league-results indexes, the league-results week page, the injury report built from the roster record, the medical history's dated entry for the game's Jacksonville injuries and an incident record for each new injury; then the annual record. Hand-written medical updates (a reassessment, a clearance, a hold released) are dated entries appended at the end of the medical history, each with its event-record line, in football words.*
- *Call sheet. Before the draw, Stone's executable offensive menu is frozen as `call_sheet.json` in the week's data folder (`SeasonPaths.call_sheet`), applied from his Game Plan, and passed to the simulator as structured `TeamInput.offensive_call_sheet` data. A call entry may contain `name`, `family`, `type` (`run`, `pass`, `any` or `mixed`), `personnel`, `formation`, `motion`, `protection` and `tags`. Supply only structure that was actually prepared; if only the family is established, give only the family, name and type. A named-call total may be reported only from the generated snap ledger, never inferred from the prose.*
- *Coach info. The record table is printed by `python scripts/render_coach_record.py YEAR --opponent "[Opponent name]" --date YYYY-MM-DD` from the receipts and the recorded hire date, with the template's omission rules applied.*

## Header

*The matchup is the top of the turn. Away club first, home club second. Nothing sits above it. The coach info follows it.*

**\[Away team\] at \[Home team\]**

Week \[X\] · \[Day, Month Date, Year\] · \[Kickoff time\] · \[Stadium, City\]

## Coach info

*Sits directly under the matchup header, with no section number. Every value is as of the end of this turn, after the game in Section 3. Records come from the closed-game receipts and the corresponding canonical coaching record. The layout follows how real coaching records are kept: regular season, postseason and overall, for the current club and for the career, as on [FootballDB's head coaching records](https://www.footballdb.com/coaches/john-harbaugh-harbajo01) and the [list of current NFL head coaches](https://en.wikipedia.org/wiki/List_of_current_NFL_head_coaches).*

**Alex Stone** · Age \[XX\] · Head Coach, \[Team name\] (\[W-L\]) · Season \[X\] with the team · Contract year \[X\] of \[Y\] · Day \[XXX\] since career start

**Next:** \[Week X+1 vs. / at Opponent name, Day, Month Date, Time\]

| Record | Regular season | Postseason | Overall |
| --- | --- | --- | --- |
| This season | \[W-L-T\] | \[W-L\] | \[W-L-T\] |
| With \[Team name\] | \[W-L-T (.XXX)\] | \[W-L\] | \[W-L-T (.XXX)\] |
| NFL head coach, career | \[W-L-T (.XXX)\] | \[W-L\] | \[W-L-T (.XXX)\] |
| Against \[Opponent name\] | \[W-L-T\] | \[W-L\] | \[W-L-T\] |

*Leave out the postseason column until Stone has coached a postseason game. Leave out the "This season" row in his first season with a team, when it repeats the row below it.*

## 1. Week setup and game preparation

### Preparation evidence

*Read the dated preparation record, approved priorities, opponent evidence and actual availability first. Preserve the recorded week. Use comparable practice-week accounts only if they help explain an unfamiliar schedule or reporting form; verify an applicable rule separately when it changes the work. A standard NFL week is not evidence that a particular meeting, drill or instruction occurred here.*

### Section layout

*Prose paragraphs under these four labels. No tables.*

**Opponent context.** \[From this season's own film and game records, as the Game Week Briefing gave them: what the opponent showed on offense, defense and special teams, its record and recent results this season, the players the plan had to account for, and its availability. State plainly anything the staff did not know going in.\]

**Stone's priorities and decisions.** \[From his Game Plan: the priorities for the week and the decision each one drove. Starters and any change from last week. The shape of the call sheet: base personnel, the openers and what they were built to find out, third down, red zone, the defensive plan. What was on the menu, and what was taken off it and why.\]

**The week, day by day.** \[Preserve the recorded dates and sequence of preparation. Describe what was actually reviewed, installed or rehearsed and material restrictions. Combine quiet days when useful; do not invent activity for a missing day or silently discard existing preparation evidence.\]

**Availability.** \[Practice participation for every player who was not a full participant, by day. Final game status for each. Players ruled out, elevations, and the inactive list.\]

## 2. Pregame media Q&A

*Follow the [head-coach media method](../../docs/head_coach_media_method.md). Use public information available before kickoff: the previous result, an announced role change, availability, the opponent and the coming game. Keep internal game-plan detail private unless Stone has already made it public. Research examples inform spoken form; the questions themselves are written for this week.*

**Reporter:** \[An original question about a specific public football matter.\]

**Stone:** \[A spoken answer expressing an established position or authorized decision.\]

*Continue when the week gives the room another worthwhile question. A follow-up responds to what was just said. There is no minimum, maximum or required topic checklist. Avoid variations of a question already answered. If no pregame session occurred, retain the section with that brief fact instead of inventing one during a retrospective rewrite.*

## 3. Game

### Game evidence

*Read the scoring, possession and play records together. Resolve a factual conflict before writing. The full generated statistics preserve the complete accounting; the quarter narrative selects the sequences needed to understand the result. Use the report research when it helps with form, never to import another game's plays or causes.*

### Section layout

**Week \[X\]: \[Away team\] at \[Home team\]**

*Keep the four quarter labels and game order. Explain the scoring changes, consequential turnovers and sequences that shaped the result without translating the drive chart into prose. Use the exact clock, distance, call or drive length when supported and useful; they are not a required bundle for every score. A quiet quarter can be brief. Add overtime only when played.*

**First quarter.** \[The supported action and its consequences in this quarter.\]

**Second quarter.** \[The supported action and its consequences in this quarter.\]

**Third quarter.** \[The supported action and its consequences in this quarter.\]

**Fourth quarter.** \[The supported action and its consequences in this quarter.\]

**Final: \[Winning team\] \[XX\], \[Losing team\] \[XX\]**

| Team | 1 | 2 | 3 | 4 | Final |
| --- | --- | --- | --- | --- | --- |
| \[Away team\] | \[X\] | \[X\] | \[X\] | \[X\] | \[XX\] |
| \[Home team\] | \[X\] | \[X\] | \[X\] | \[X\] | \[XX\] |

*Add an OT column only if overtime was played.*

### Game review

**Review:** \[Immediate postgame assessment, or completed staff review with the actual evidence-through date.\]

*The prompts below identify possible football questions; select the ones this game actually tested. A unit does not need a sentence on each listed technique or an inventory of missing observations. Give each finding one main home, and revisit it only to add a different conclusion. Read the prepared call sheet, participation and substitutions, public play record, medical instructions and recorded coaching findings. Use the active, taught playbook to interpret the job. Explain assignments, recognition, technique, physical execution and decisions separately where the distinction matters. A statistic does not supply an unrecorded cause. Research informs the questions and writing, never missing events. The [report research](../../docs/preseason_game_reports.md) explains this method for both game formats.*

#### The team's performance

\[Lead with the game-level finding that connects the units. Explain what repeatedly sustained or stopped the team and how possession, field position and game situations linked their work. Leave the detailed unit findings to their sections below. Use representative sequences already established above without telling the quarters again. Include what the opponent forced the team to change. Distinguish a repeated problem from one costly play.\]

#### Offense

\[Assess the offense the actual personnel ran. Explain how the line, backs, quarterback and receivers connected the run track, protection, route spacing and timing. Which prepared calls remained usable when the defense changed its look or took away the first answer? Include meaningful reserve and mixed-group work, with its opposition and support, rather than assuming a quarterback change replaced the whole unit. Describe what worked as specifically as what failed.\]

\[Trace a breakdown only as far as the evidence allows. Correct protection identification and a lost block are different findings; a late throw and a wrong route are different findings. Discuss relevant third-down, red-zone or clock work, the support a successful package required and any cost elsewhere. Do not infer an individual's blocking, route or read error from the team result.\]

#### Defense

\[Connect front control, fits, force and pursuit; connect rush lanes to coverage and help. Explain the players' actual responses to formations, motion and personnel changes. Include useful block defeat, leverage, coverage and tackling away from the final statistic when recorded. Compare starting, rotational and replacement combinations where the game tested them. Explain whether an adjustment held on later opportunities, or remains untested.\]

#### Special teams

\[Explain snap, hold, protection, kick instruction and placement, releases, coverage lanes, blocks and return decisions where supported. Separate a specialist's execution from the unit around him. Name contributions from reserves when their work is recorded. Connect the operation to the field position it produced without treating every made kick or return yard as proof that all assignments were sound.\]

#### Communication and coaching response

\[Develop a material communication or coaching finding not already explained in the unit review. Relevant evidence may concern the path from sideline call to alignment and shared assignment: substitutions, protection declarations, coverage exchanges, tempo, replacement callers and clock handling when relevant. Separate a call not received, conflicting instructions, a recognition error and a correctly understood job executed poorly. A low penalty total does not establish clean communication.\]

\[Assess the staff's contribution as well as the players'. Was the call timely, the instruction consistent and the support suitable for the job? Describe a delivered correction and its later response only when recorded. If the cause is unresolved, identify the football question for review. Recommendations and untested adjustments remain proposals. Section 5 carries the resulting work forward. Do not invent Stone's private thoughts or a staff meeting.\]

#### Player findings and material decisions

*Use the existing fields below for individual conclusions that add to the unit review; do not add another standout list or repeat the same statistical line. Develop the relevant assignment, technique, opposition and repeated or contrary evidence behind the player's work. Include a useful strength and a limitation together when both occurred. A narrow opportunity stays narrow. Record material during-year changes as dated observations on the opening annual card; this report does not create another full assessment or a new preseason position-battle card.*

**Player of the game:** \[Retain an established selection, with the supporting performance. Do not invent an award solely to fill the field.\]

**Standout performances**

- &#91;Player\]: \[The meaningful work, its supporting evidence and any relevant limit. Either club may appear; no player-count quota and no second statistical recap.\]

**Material game-management decisions:** \[Assess the consequential decisions Stone actually made against what he knew at the time. Refer to a sequence already told rather than retelling it; preserve his recorded reason and distinguish the choice from its outcome. Omit when there is no additional finding.\]

**Injuries and availability from the game:** \[Material removals and their effect on the game. Medical findings and restrictions appear only when communicated; section 6 gives the current status and next-game implications. Omit when there was no change.\]

### Full stats for the game

*The last item in the Game section. Generated from the receipt, never typed by hand. The layout follows the official NFL gamebook: scoring summary, team statistics, individual statistics for each club, drive chart, snap counts. Clubs are named by their team names throughout, for example "Jaguars stats for the game". One row per player who recorded a stat in a category. Player lines add up to the team totals, and the scoring summary adds up to the line score. A table with no entries is left out. A table or column the receipt cannot support is left out, never estimated.*

*Layout basis: the NFL gamebook, read in full for [Chargers at Patriots, January 13, 2019](https://static.clubs.nfl.com/image/upload/patriots/ogsuocwzbpwtfrbwkscl.pdf) and [Chiefs at Titans, 2000 preseason](https://nflgsis.com/2000/pre/02/934/Gamebook.pdf), the league's [Guide for Statisticians](https://www.nflgsis.com/gsis/documentation/stadiumguides/guide_for_statisticians.pdf), and [Sharp Football's advanced box scores](https://www.sharpfootballanalysis.com/stats-nfl/nfl-advanced-box-scores/) for drives, success rate and explosive plays.*

#### Scoring summary

*Every scoring play in game order. The last row matches the final score.*

| Qtr | Time | Team | Scoring play | Drive | \[Away team name\] | \[Home team name\] |
| --- | --- | --- | --- | --- | --- | --- |
| \[X\] | \[XX:XX\] | \[Team name\] | \[Scorer, yards, run / pass from passer / kick / return (extra point or two-point result)\] | \[Plays-yards, time\] | \[XX\] | \[XX\] |

#### Team stats for the game

*Definitions. Net yards passing: gross passing yards minus sack yardage. Average gain per pass play: net passing yards divided by attempts plus sacks. Third and fourth down: an attempt is any third-down or fourth-down run, pass or sack. Total return yardage: punt returns plus interception returns, kickoffs not included. Red zone and goal to go: touchdowns over trips. Success rate: the share of runs and passes that gain at least 45% of the yards to go on first down, 60% on second down, and all of them on third or fourth down, with kneel-downs and spikes excluded. Explosive plays: runs of 10 or more yards and completions of 20 or more. Points per drive: points scored by the offense divided by its drives, with kneel-down drives excluded.*

| Group | Statistic | \[Team name\] | \[Opponent name\] |
| --- | --- | --- | --- |
| Score | Final score | \[XX\] | \[XX\] |
| Possession | Time of possession | \[XX:XX\] | \[XX:XX\] |
|  | Drives | \[XX\] | \[XX\] |
|  | Average drive start | \[Own XX\] | \[Own XX\] |
|  | Points per drive | \[X.XX\] | \[X.XX\] |
| First downs | Total first downs | \[XX\] | \[XX\] |
|  | By rushing | \[X\] | \[X\] |
|  | By passing | \[X\] | \[X\] |
|  | By penalty | \[X\] | \[X\] |
| Downs | Third down efficiency | \[X-XX, XX%\] | \[X-XX, XX%\] |
|  | Fourth down efficiency | \[X-X, XX%\] | \[X-X, XX%\] |
| Total offense | Total net yards | \[XXX\] | \[XXX\] |
|  | Total offensive plays | \[XX\] | \[XX\] |
|  | Average gain per play | \[X.X\] | \[X.X\] |
|  | Success rate | \[XX%\] | \[XX%\] |
|  | Explosive plays | \[X\] | \[X\] |
| Rushing | Net yards rushing | \[XXX\] | \[XXX\] |
|  | Rushing plays | \[XX\] | \[XX\] |
|  | Average gain per rush | \[X.X\] | \[X.X\] |
|  | Tackled for loss, number and yards | \[X-XX\] | \[X-XX\] |
| Passing | Net yards passing | \[XXX\] | \[XXX\] |
|  | Gross yards passing | \[XXX\] | \[XXX\] |
|  | Sacked, number and yards lost | \[X-XX\] | \[X-XX\] |
|  | Attempts-completions-intercepted | \[XX-XX-X\] | \[XX-XX-X\] |
|  | Average gain per pass play | \[X.X\] | \[X.X\] |
| Kicking game | Kickoffs, number and touchbacks | \[X-X\] | \[X-X\] |
|  | Punts, number and average | \[X-XX.X\] | \[X-XX.X\] |
|  | Net punting average | \[XX.X\] | \[XX.X\] |
|  | Punts had blocked | \[X\] | \[X\] |
|  | Field goals and extra points had blocked | \[X-X\] | \[X-X\] |
| Returns | Total return yardage | \[XXX\] | \[XXX\] |
|  | Punt returns, number and yards | \[X-XX\] | \[X-XX\] |
|  | Kickoff returns, number and yards | \[X-XX\] | \[X-XX\] |
|  | Interception returns, number and yards | \[X-XX\] | \[X-XX\] |
| Penalties | Penalties, number and yards | \[X-XX\] | \[X-XX\] |
| Ball security | Turnovers | \[X\] | \[X\] |
|  | Interceptions thrown | \[X\] | \[X\] |
|  | Fumbles, number and lost | \[X-X\] | \[X-X\] |
| Scoring | Touchdowns | \[X\] | \[X\] |
|  | Rushing-passing-returns | \[X-X-X\] | \[X-X-X\] |
|  | Extra points, made-attempts | \[X-X\] | \[X-X\] |
|  | Two-point conversions, made-attempts | \[X-X\] | \[X-X\] |
|  | Field goals, made-attempts | \[X-X\] | \[X-X\] |
|  | Safeties | \[X\] | \[X\] |
| Scoring chances | Red zone efficiency | \[X-X, XX%\] | \[X-X, XX%\] |
|  | Goal to go efficiency | \[X-X, XX%\] | \[X-X, XX%\] |

#### &#91;Team name\] stats for the game

**Passing**

| Player | CMP/ATT | YDS | AVG | TD | INT | SCK/YDS | LNG | RTG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| \[Name\] | \[XX/XX\] | \[XXX\] | \[X.X\] | \[X\] | \[X\] | \[X-XX\] | \[XX\] | \[XXX.X\] |

**Rushing**

| Player | CAR | YDS | AVG | LNG | TD |
| --- | --- | --- | --- | --- | --- |
| \[Name\] | \[XX\] | \[XXX\] | \[X.X\] | \[XX\] | \[X\] |
| Team total | \[XX\] | \[XXX\] | \[X.X\] | \[XX\] | \[X\] |

**Receiving**

| Player | TGT | REC | YDS | AVG | LNG | TD |
| --- | --- | --- | --- | --- | --- | --- |
| \[Name\] | \[XX\] | \[X\] | \[XXX\] | \[XX.X\] | \[XX\] | \[X\] |
| Team total | \[XX\] | \[XX\] | \[XXX\] | \[XX.X\] | \[XX\] | \[X\] |

**Interceptions**

| Player | INT | YDS | AVG | LNG | TD |
| --- | --- | --- | --- | --- | --- |
| \[Name\] | \[X\] | \[XX\] | \[XX.X\] | \[XX\] | \[X\] |

**Fumbles**

| Player | FUM | LOST | OWN REC | OPP REC | FORCED |
| --- | --- | --- | --- | --- | --- |
| \[Name\] | \[X\] | \[X\] | \[X\] | \[X\] | \[X\] |

**Defense**

| Player | TOT | SOLO | AST | SCK/YDS | TFL | QB HITS | PD | INT | FF | FR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| \[Name\] | \[XX\] | \[X\] | \[X\] | \[X.X-XX\] | \[X\] | \[X\] | \[X\] | \[X\] | \[X\] | \[X\] |
| Team total | \[XX\] | \[XX\] | \[XX\] | \[X.X-XX\] | \[X\] | \[X\] | \[X\] | \[X\] | \[X\] | \[X\] |

**Special teams defense**

| Player | TOT | SOLO | AST | FF | FR | BLK |
| --- | --- | --- | --- | --- | --- | --- |
| \[Name\] | \[X\] | \[X\] | \[X\] | \[X\] | \[X\] | \[X\] |

**Kicking**

| Player | FGM | FGA | FG% | LNG | XPM | XPA | PTS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| \[Name\] | \[X\] | \[X\] | \[XXX.X\] | \[XX\] | \[X\] | \[X\] | \[XX\] |

*Under the kicking table, one line listing each field goal attempt by distance and result.*

**Punting**

| Player | PUNTS | YDS | AVG | NET | TB | IN20 | LNG |
| --- | --- | --- | --- | --- | --- | --- | --- |
| \[Name\] | \[X\] | \[XXX\] | \[XX.X\] | \[XX.X\] | \[X\] | \[X\] | \[XX\] |

**Punt returns**

| Player | RET | YDS | AVG | FC | LNG | TD |
| --- | --- | --- | --- | --- | --- | --- |
| \[Name\] | \[X\] | \[XX\] | \[XX.X\] | \[X\] | \[XX\] | \[X\] |

**Kickoff returns**

| Player | RET | YDS | AVG | LNG | TD |
| --- | --- | --- | --- | --- | --- |
| \[Name\] | \[X\] | \[XX\] | \[XX.X\] | \[XX\] | \[X\] |

#### &#91;Opponent name\] stats for the game

*The same eleven tables, in the same order and columns, for the opponent.*

#### Drive chart

*One table per club, headed by the team name. Every possession in game order.*

| # | Qtr | Time received | How obtained | Began at | Plays | Net yards | Time of possession | How given up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| \[X\] | \[X\] | \[XX:XX\] | \[Kickoff / punt / interception / fumble / downs\] | \[Own XX / Opp XX\] | \[XX\] | \[XX\] | \[X:XX\] | \[Touchdown / field goal / punt / interception / fumble / downs / missed field goal / end of half\] |

#### Snap counts

*One table per club, headed by the team name. Every player who played a snap, with his count and his share of the unit's snaps.*

| Player | POS | Offense | Defense | Special teams |
| --- | --- | --- | --- | --- |
| \[Name\] | \[POS\] | \[XX (XX%)\] | \[XX (XX%)\] | \[XX (XX%)\] |

## 4. Postgame media Q&A

*Follow the [head-coach media method](../../docs/head_coach_media_method.md), using what was publicly observable at this session's time. Lead with the game matter likely to draw attention, then let the answers give reporters something to pursue. A reporter can press an important choice; a loss alone does not require hostility or a longer session.*

**Reporter:** \[An original question arising from this game's public action or an earlier public answer.\]

**Stone:** \[His response, with enough football to answer the question and no newly invented decision or diagnosis.\]

*Continue only while another question adds something. Short answers, fuller explanations and ordinary acknowledgment all have a place. Do not make Stone recite the gamebook or the author's evidence checks. Keep later film findings out of an immediate postgame answer.*

## 5. Coaching takeaways and next-week carry-forward

*The staff's supported football conclusions and resulting work. Preserve Stone's recorded choices without inventing his private reaction. Use the game report above and actual coaching evidence; a statistic alone cannot establish the cause. Develop each field as far as its material work requires, without repeating the unit review.*

**What held up:** \[What the staff can retain for the next week because of the findings above. Do not retell the supporting plays.\]

**What must be corrected:** \[The resulting correction or unresolved football question, with its player or unit. Do not manufacture a fault or repeat the complete unit assessment.\]

**Next-week carry-forward:** \[Turn those conclusions into the actual or proposed next work: the cutups, the corrections, what stays on the menu and what waits. Name the responsible actual coach and the next useful opportunity for each material correction. Distinguish work proposed, instruction delivered and improvement actually observed.\]

## 6. Weekly personnel and availability

*The roster as it stands leaving this game. Preserve the unit headings and tables, with concise current-role and availability entries. Full participation is accounted for in the generated statistics; this section explains material role, medical and evaluation findings. Do not recopy every player's statistical line or invent a new judgment for an unchanged group. An unchanged group retains its supported current view; the evidence column can point to the finding above rather than restate it. Link the controlling roster and medical records.*

### Offense

| Group | Primary personnel / current role | Availability | Current qualitative read | This week's evidence / issue |
| --- | --- | --- | --- | --- |
| QB | \[QB1; QB2\] | \[Available / name and status\] | \[Supported current view\] | \[Material football finding or current open issue\] |
| RB / FB | \[Lead back; rotation; FB\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| WR | \[Starters; WR3\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| TE | \[Lead; TE2; package roles\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| OL | \[LT; LG; C; RG; RT; swing\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |

**Offensive role changes:** \[Each change, or "None."\]

### Defense

| Group | Primary personnel / current role | Availability | Current qualitative read | This week's evidence / issue |
| --- | --- | --- | --- | --- |
| Interior DL | \[Starters; rotation\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| Edge | \[Starters; rotation\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| LB | \[Starters; next man\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| CB | \[Starters\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| Nickel | \[Player\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| S | \[Starters\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |

**Defensive role changes:** \[Each change, or "None."\]

### Special teams

| Unit | Primary personnel / role | Availability | Current qualitative read | This week's evidence / issue |
| --- | --- | --- | --- | --- |
| K | \[Player\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| P | \[Player\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| LS / operation | \[Player\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| Kick return | \[Players\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| Punt return | \[Players\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |
| Coverage units | \[Players\] | \[Availability\] | \[Supported current view\] | \[Evidence\] |

### Material personnel changes this week

- **Injuries / limitations:** \[New injuries and limitations, and the standing of anyone already held out. "None new" if none.\]
- **Activations / elevations / transactions:** \[Each move, or "None."\]
- **Depth-chart / rotation changes:** \[Each change, or "None."\]
- **Role consequences for next week:** \[Who plays more or less next week and why, or what has to be reviewed before that is decided.\]

## 7. Week closure

*Written last, after the statistics, standings, awards, medical pages and indexes have been rebuilt from the closed game.*

**Record after game:** \[W-L-T\]

**Division / conference position:** \[Place in the division and how ties were broken; conference seed if the season ended today.\] See \[standings link\].

**Statistics:** \[Link to the updated season statistics and their through-date. Put a coverage limitation here only if it affects their use.\]

**Supporting notes:** \[Compact links to the week's pages: the Game Week Briefing, the Game Plan, the medical history and injury report, the league results, the awards. State a material evidence limitation once if needed, in football words. Any new writing references are references for form, not the source of a reporter's words. Omit routine execution, browsing and validation logs, and every link into the data area. Preserve machine metadata in its existing place.\]

**Dated record:** \[A link to the season's annual record, where this game's event line indexes this report. A presentation-only rewrite retains the existing event.\]

**Next event:** \[Week X+1 vs. / at Opponent, Day, Month Date, Time\], or \[bye / playoff round / offseason phase\].
