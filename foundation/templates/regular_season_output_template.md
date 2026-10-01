# Regular-season output template

**Status:** The user's weekly game turn template, confirmed September 30, 2026. Applies to every regular-season and postseason game turn from the 2014 season onward; 2013 turns keep the earlier format, retained in git history.
**When used:** Regular-season game weeks, byes and postseason turns. An unplayed slot contains preparation only; do not fill a result, player performance or box score before the game is resolved. Use the [preseason output template](preseason_output_template.md) for preseason turns and the [offseason output template](offseason_output_template.md) for offseason turns. Document 7 governs simulation; this template governs presentation.

Every weekly game turn follows this layout. Bracketed text is a field to fill. Italic text is an instruction to whoever writes the turn: it is carried out, then left out of the output.

The confirmed weekly layout has unnumbered Coach info followed by seven numbered sections. The game is section 3. Its quarter narrative and result summary lead directly into **Report to render**, followed by the existing player findings, decisions, availability and full generated statistics. Postgame media stays in section 4, coaching carry-forward in section 5, personnel in section 6 and closure in section 7. The preseason template has its own eight-section numbering; do not renumber either to match the other.

## Rules for every turn

*These rules govern the whole turn. None of this section appears in the output.*

1. **Facts come from the branch.** Scores, stats, rosters, injuries, schemes and results come only from the branch's recorded film findings, actual event owners, statbook and game receipt. No real-world result, stat or roster fact enters a turn.
2. **Research supplies form, never facts.** Research shows how a real week runs, what reporters really ask, how a head coach really answers, and how a real game story reads. The branch supplies everything those forms are filled with.
3. **Research is done every turn, before the section is written.** Each narrative section below opens with a research step that says where to look, how to look, and what to do with what is found. Open the pages and read them in full. A search result is not a source. Last week's turn is not a source.
4. **Never fake a research step.** If a step cannot be run, the engine note in Section 7 says which one and why. An invented question is never presented as a real one.
5. **Every player is tracked.** Every player who appears in the receipt appears in the full stats. Every change in health, role or depth appears in Section 6. The statbook is updated from the receipt before Section 7 is written.
6. **Nothing about the engine is shown** except the one engine note line in Section 7. No status block, event id, generation, kernel version or restart record.

### Prose standard

*Applies to every narrative passage: the week, the quarters, the takeaways.*

**Research before writing.** Before the first narrative passage of the turn, read three real pieces of the kind about to be written (listed in each section). Keep one open while drafting and compare against it.

- Past tense, third person, plain verbs.
- Ground the account in this game's people, assignments, situations and consequences. Use exact down, distance, yard line, clock or concept only when recorded; a sentence does not need a number to explain football.
- The quarter narrative reports what happened. The coaching report explains what the evidence supports about the work and why it matters for the next assignment. Separate observation from interpretation. Cut unsupported momentum, tone-setting, statement-game or importance claims.
- Nothing from inside a player's or coach's head unless he says it in a Q&A.
- No adjectives for effort, heart or character. No weather or crowd used as mood.
- No em dashes, no rhetorical questions, no one-line paragraphs for effect, no lists of three built for rhythm, no "not X but Y" constructions.
- A paragraph ends on its last fact. It does not end on a summary or a line that points ahead.
- The check: reread each sentence and ask whether it could appear unchanged in a story about a different game. If it could, rewrite it with this game's facts or cut it.

### Runner mechanics

*Carried out by whoever runs the turn. None of this block appears in the output.*

- *Storage. The complete protagonist turn is the week's `output.md`, at `career/[year]/05_Regular_Season/Games/Week_NN/output.md` for a regular-season week and under `career/[year]/06_Postseason/Games/` for a postseason game; both resolve through `runtime.seasons.SeasonPaths.week_folder`. No separate prep, press, recap or highlights file. Background games go to `career/[year]/05_Regular_Season/League_Results/week_NN.md` as a scores-and-highlights roundup and are never expanded into this format.*
- *Receipts. Every closed game produces a public stat receipt under the season's stats directory (`SeasonPaths.receipts`, with postseason receipts in the sibling `postseason_receipts` directory): a full receipt with the complete player dictionaries, snap `play_ledger`, drives and named-call statistics for the protagonist's game, and a `compact_stats` receipt for each background game. Everything statistical is generated from the receipts, never typed: the full stats block below, the standings (`python scripts/render_standings.py YEAR`) and the season statistics (`python scripts/render_season_stats.py YEAR --team TEAM_ID`) are all regenerated after the week closes. A missing attribution stays missing; no real historical statistic fills it.*
- *The full stats block. The whole "Full stats for the game" block is generated by `python scripts/render_box_score.py --season YEAR --write <output.md>` between the markers `<!-- box-score event=EVENT_ID team=[Team name] -->` and `<!-- /box-score -->`, which sit where that block belongs. Nothing inside the markers is typed or edited by hand; `scripts/validate_repository.py` fails if the block differs from its receipt. The renderer records in its docstring which rows and columns the receipt supports and leaves out the rest.*
- *Call sheet. Before the draw, Stone's executable offensive menu is frozen as `call_sheet.json` in the week folder and passed to the simulator as structured `TeamInput.offensive_call_sheet` data. A call entry may contain `name`, `family`, `type` (`run`, `pass`, `any` or `mixed`), `personnel`, `formation`, `motion`, `protection` and `tags`. Supply only structure that was actually prepared; if only the family is established, give only the family, name and type. A named-call total may be reported only from the generated snap ledger, never inferred from the prose.*
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

### Research before writing

*Carry this out, then write the section. None of this block appears in the output.*

**What to find out.** What a real NFL staff and roster do on each day of a week shaped like this one, and how that work is reported in writing.

**Where to look.**

- Practice reports and game-week notebooks published by team sites and beat writers during real NFL weeks.
- Long accounts of how a game plan is built: coaches' own writing on game planning and opening scripts (Bill Walsh and Brian Billick both wrote on it), and features that follow one staff through one week.
- The league's own rules for the week on the NFL Football Operations site: practice participation reports, game status designations, the inactive list deadline, practice-squad elevations, padded-practice limits.

**How to look.**

1. Name the shape of this week from the branch: standard Sunday, short week, long week, after a bye, opener, after a win or a loss, a new starter, a key player on a medical hold.
2. Find and read in full at least three real pieces, at least one of them from a real week with the same shape.
3. From each, note four things: what the staff and players did on each day, the order in which the plan was installed, the working words used for it, and what the writer reported as fact versus left out.

**What to do with it.**

- Build the branch's week on the real skeleton: what real clubs do on the day after a game, the players' day off when the staff builds the plan, the three practice days and what each installs, the day-before walkthrough, and game day through the inactive list.
- Use the real vocabulary where it fits the branch's facts. Do not borrow a real club's facts, quotes or sentences.
- Report the week the way the real pieces do: what was installed, who practiced and how much, who was ruled out, what was cut from the plan. Follow the prose standard.
- If the branch has no information on something a real staff would know, say the staff did not have it. Do not fill the gap.

### Section layout

*Prose paragraphs under these four labels. No tables.*

**Opponent context.** \[One paragraph from the branch's own film and statbook: what the opponent showed on offense, defense and special teams, its record and recent results in the branch, the players the plan had to account for, and its availability. State plainly anything the staff did not know going in.\]

**Stone's priorities and decisions.** \[One or two paragraphs. The priorities for the week and the decision each one drove. Starters and any change from last week. The shape of the call sheet: base personnel, the openers and what they were built to find out, third down, red zone, the defensive plan. What was on the menu, and what was taken off it and why.\]

**The week, day by day.** \[One short paragraph per day from the day after the last game through the day before this one. For each day: what was reviewed, installed or rehearsed, the teaching point, and who was limited or held out. Shift the days for a Thursday, Saturday or Monday game and say so.\]

**Availability.** \[Practice participation for every player who was not a full participant, by day. Final game status for each. Players ruled out, elevations, and the inactive list.\]

## 2. Pregame media Q&A

### Research before writing

*Carry this out, then write the section. None of this block appears in the output.*

**What to find out.** Which questions real reporters have asked real NFL head coaches in the situations this game presents, and how those coaches answered.

**Where to look.**

- Press-conference transcripts that NFL clubs publish on their own sites, midweek and end of week.
- The ASAP Sports transcript archive.
- Full press-conference video, and beat writers' own transcriptions in their practice-week coverage.

**How to look.**

1. Look at this game and list what a beat reporter would ask about. Use only what is public in the branch: last week's result, a lineup change, a player's first start, the injury report, the opponent's best players, the opposing coach, a streak, the standings, a short or long week.
2. For each item, find a real head coach's pregame press conference where the same situation existed. A rookie tackle's first start. A quarterback's first start for a new club. A starter held out by the medical staff. An opener. A return to a former club.
3. Read the whole transcript, not the one question. Note how the session ran, which questions were asked, and how they were worded.
4. Read at least two more transcripts from other head coaches for the range of how coaches answer.

**What to do with it.**

- **Questions.** Take each question as the reporter asked it. Keep its wording, length and angle, including the ones that are statements, two questions in one, or loosely phrased. Change only the names and details that belong to the branch. Do not write a question from scratch.
- **Answers.** Answer as Stone. His voice from earlier turns governs. The transcripts supply how a head coach handles each kind of question: what he answers straight, what he declines, how he talks about injuries, rookies and the opponent, and how long he talks.
- **Facts.** Stone's answers contain only what Section 1 and the branch support. The podium answer may hold back what Section 1 shows. It never contradicts the branch.
- **Order.** Run the questions in the order a real session runs, not grouped by topic.
- **Method.** Apply the [head-coach media method](../../docs/head_coach_media_method.md): its catalogue of real answers, its anti-slop rules (no answer restates the question; no lists of three built for rhythm; no "at the end of the day"; no sermon; no unprompted plan rationale; the tape deferral and "I'll have to look at it" at most once each per session, with a specific observation; one-sentence answers where a real coach gives one; numbers only as held at the podium) and Stone's voice sheet (straight on his own decisions, blame first and short after a loss, named credit, the injury answer stops at the medical record, the roster is Caldwell's, no job decided from the podium).

### Section layout

*Five to eight questions. The number follows how much the week gives reporters to ask about. Each answer is one paragraph in Stone's spoken voice, as long as a real coach's answer to that kind of question.*

**Reporter:** \[Real question, adapted to the branch's names and details.\]

**Stone:** \[Answer.\]

*Repeat for each question.*

**Question sources:** \[One line per question: the coach who was asked it, the club, the date, and a link to the transcript.\]

## 3. Game

### Research before writing

*Carry this out, then write the quarters. None of this block appears in the output.*

**What to find out.** How working sportswriters write a game one quarter at a time.

**Where to look.**

- Associated Press game stories.
- Quarter-by-quarter recaps and game summaries on team sites.
- Newspaper game stories by beat writers.

**How to look.**

1. Name the shape of this game from the receipt: a blowout, a comeback, a defensive game, a game decided late, a game decided by turnovers.
2. Find and read in full at least three real pieces, at least one a quarter-by-quarter recap and at least one of a real game with the same shape.
3. Note how each one reports a scoring drive (plays, yards, the key play, the scorer, the clock), how it reports a turnover and what came of it, how it handles a possession that went nowhere, and how little comment it adds.

**What to do with it.**

- Write each quarter to that pattern using only the receipt. Every play, player, yardage and clock time cited must be in the receipt.
- Do not borrow a real story's sentences. Follow the prose standard.

### Section layout

**Week \[X\]: \[Away team\] at \[Home team\]**

*One paragraph per quarter, in game order. Each paragraph covers every score and every turnover of that quarter in the order they happened. A scoring drive gets its length in plays and yards, its key play with down, distance and concept, the scorer, and the clock. A possession that did not score is mentioned only when it explains field position or a later score. A scoreless quarter still gets a paragraph on what each side's possessions did. The paragraph stops at the quarter's last event. Add an overtime paragraph only if overtime was played.*

**First quarter.** \[One paragraph.\]

**Second quarter.** \[One paragraph.\]

**Third quarter.** \[One paragraph.\]

**Fourth quarter.** \[One paragraph.\]

**Final: \[Winning team\] \[XX\], \[Losing team\] \[XX\]**

| Team | 1 | 2 | 3 | 4 | Final |
| --- | --- | --- | --- | --- | --- |
| \[Away team\] | \[X\] | \[X\] | \[X\] | \[X\] | \[XX\] |
| \[Home team\] | \[X\] | \[X\] | \[X\] | \[X\] | \[XX\] |

*Add an OT column only if overtime was played.*

### Report to render

**Review:** \[Immediate postgame assessment, or completed staff review with the actual evidence-through date.\]

*Read the prepared call sheet, participation and substitutions, public play record, medical instructions and recorded coaching findings. Use the active, taught playbook to interpret the job. Explain assignments, recognition, technique, physical execution and decisions separately where the distinction matters. A statistic does not supply an unrecorded cause. Research informs the questions and writing, never missing events. The [report research](../../docs/preseason_game_reports.md) explains this method for both game formats.*

#### The team's performance

\[Lead with the main supported football finding. Explain what repeatedly sustained or stopped the team and how the units affected one another through possession, field position and game situations. Use representative sequences already established above without telling the quarters again. Include what the opponent forced the team to change. Distinguish a repeated problem from one costly play.\]

#### Offense

\[Assess the offense the actual personnel ran. Explain how the line, backs, quarterback and receivers connected the run track, protection, route spacing and timing. Which prepared calls remained usable when the defense changed its look or took away the first answer? Include meaningful reserve and mixed-group work, with its opposition and support, rather than assuming a quarterback change replaced the whole unit. Describe what worked as specifically as what failed.\]

\[Trace a breakdown only as far as the evidence allows. Correct protection identification and a lost block are different findings; a late throw and a wrong route are different findings. Discuss relevant third-down, red-zone or clock work, the support a successful package required and any cost elsewhere. Do not infer an individual's blocking, route or read error from the team result.\]

#### Defense

\[Connect front control, fits, force and pursuit; connect rush lanes to coverage and help. Explain the players' actual responses to formations, motion and personnel changes. Include useful block defeat, leverage, coverage and tackling away from the final statistic when recorded. Compare starting, rotational and replacement combinations where the game tested them. Explain whether an adjustment held on later opportunities, or remains untested.\]

#### Special teams

\[Explain snap, hold, protection, kick instruction and placement, releases, coverage lanes, blocks and return decisions where supported. Separate a specialist's execution from the unit around him. Name contributions from reserves when their work is recorded. Connect the operation to the field position it produced without treating every made kick or return yard as proof that all assignments were sound.\]

#### Communication and coaching response

\[Describe the actual path from sideline call to alignment and shared assignment: substitutions, protection declarations, coverage exchanges, tempo, replacement callers and clock handling when relevant. Separate a call not received, conflicting instructions, a recognition error and a correctly understood job executed poorly. A low penalty total does not establish clean communication.\]

\[Assess the staff's contribution as well as the players'. Was the call timely, the instruction consistent and the support suitable for the job? Describe a delivered correction and its later response only when recorded. If the cause is unresolved, identify the football question for review. Recommendations and untested adjustments remain proposals. Section 5 carries the resulting work forward. Do not invent Stone's private thoughts or a staff meeting.\]

#### Player findings and material decisions

*Use the existing fields below for the individual findings; do not add another standout list. Develop the relevant assignment, technique, opposition and repeated or contrary evidence behind the player's line. Include a useful strength and a limitation together when both occurred. A narrow opportunity stays narrow. Record material during-year changes as dated observations on the opening annual card; this report does not create another full assessment or a new preseason position-battle card.*

**Player of the game:** \[Name, position, club\]. \[His line from the full stats and the plays it came on. One player, from either club.\]

**Standout performances**

- &#91;Player\]: \[his line from the full stats and the play or plays it came on.\]
- &#91;Three to five players. Either club may appear.\]

**Material game-management decisions:** \[Each fourth-down, challenge, timeout or clock decision by Stone that entered the result, with the situation and the outcome. "None recorded" if there were none.\]

**Injuries and availability from the game:** \[Each player who left, his club and when it happened; the medical finding, restriction and projected return only when communicated. Distinguish an observation from a diagnosis and a forecast from clearance. "None" if there were none.\]

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

| Player | CMP/ATT | YDS | AVG | TD | INT | SCK-YDS | LNG | RTG |
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

| Player | TOT | SOLO | AST | SCK-YDS | TFL | QB HITS | PD | INT | FF | FR |
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

### Research before writing

*The same method as Section 2, run on postgame transcripts. Carry it out, then write the section. None of this block appears in the output.*

**Where to look.** Postgame press-conference transcripts on club sites and in the ASAP Sports archive, full postgame press-conference video, and the quotes sections of real game stories.

**How to look.**

1. Look at this game and list what a reporter would ask about. Use the four quarter paragraphs and the full stats: the result, the quarterback's line, turnovers, sacks allowed, third down, a rookie's day, a back who outgained the starter, a late score, an injury, a decision Stone made.
2. For each item, find a real head coach's postgame press conference after a real game where the same thing happened. A win with two interceptions. A rookie tackle charged with sacks. A defense with takeaways and no sack. A loss decided on a late drive.
3. Read the whole transcript and at least two more from other head coaches, including one after a win and one after a loss.

**What to do with it.** As in Section 2: real questions in their real wording with only the branch's names and details changed, Stone's answers in his own voice, facts only from the branch, real session order. After a loss, or a game with a disputed decision, the real sessions run longer and press harder. Match that. The [head-coach media method](../../docs/head_coach_media_method.md) governs the answers as in Section 2; its section 6 is a worked postgame example after an overtime loss.

### Section layout

*Five to twelve questions. A routine result sits at the low end. A loss, an injury to a starter or a disputed decision pushes it up. At least one question goes to the worst sequence of the game or Stone's hardest decision.*

**Reporter:** \[Real question, adapted to the branch's names and details.\]

**Stone:** \[Answer.\]

*Repeat for each question.*

**Question sources:** \[One line per question: the coach who was asked it, the club, the date, and a link to the transcript.\]

## 5. Coaching takeaways and next-week carry-forward

*The staff's supported football conclusions and resulting work. Preserve Stone's recorded choices without inventing his private reaction. Use the game report above and actual coaching evidence; a statistic alone cannot establish the cause. Develop each field as far as its material work requires, without repeating the unit review.*

**What held up:** \[What worked and the evidence for it.\]

**What must be corrected:** \[Each problem, the evidence, and the player or unit it belongs to.\]

**Next-week carry-forward:** \[What next week's preparation starts from: the cutups, the corrections, what stays on the menu and what waits. Name the responsible actual coach and the next useful opportunity for each material correction. Distinguish work proposed, instruction delivered and improvement actually observed.\]

## 6. Weekly personnel and availability snapshot

*The roster as it stands leaving this game. Every player on the active roster sits in one of these groups, and every player who appeared in the full stats is accounted for. The evidence column uses this week's numbers from the receipt.*

### Offense

| Group | Primary personnel / current role | Availability | Current qualitative read | This week's evidence / issue |
| --- | --- | --- | --- | --- |
| QB | \[QB1; QB2\] | \[Available / name and status\] | \[One phrase\] | \[Line from the full stats; open issue\] |
| RB / FB | \[Lead back; rotation; FB\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| WR | \[Starters; WR3\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| TE | \[Lead; TE2; package roles\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| OL | \[LT; LG; C; RG; RT; swing\] | \[Availability\] | \[One phrase\] | \[Evidence\] |

**Offensive role changes:** \[Each change, or "None."\]

### Defense

| Group | Primary personnel / current role | Availability | Current qualitative read | This week's evidence / issue |
| --- | --- | --- | --- | --- |
| Interior DL | \[Starters; rotation\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| Edge | \[Starters; rotation\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| LB | \[Starters; next man\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| CB | \[Starters\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| Nickel | \[Player\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| S | \[Starters\] | \[Availability\] | \[One phrase\] | \[Evidence\] |

**Defensive role changes:** \[Each change, or "None."\]

### Special teams

| Unit | Primary personnel / role | Availability | Current qualitative read | This week's evidence / issue |
| --- | --- | --- | --- | --- |
| K | \[Player\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| P | \[Player\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| LS / operation | \[Player\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| Kick return | \[Players\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| Punt return | \[Players\] | \[Availability\] | \[One phrase\] | \[Evidence\] |
| Coverage units | \[Players\] | \[Availability\] | \[One phrase\] | \[Evidence\] |

### Material personnel changes this week

- **Injuries / limitations:** \[New injuries and limitations, and the standing of anyone already held out. "None new" if none.\]
- **Activations / elevations / transactions:** \[Each move, or "None."\]
- **Depth-chart / rotation changes:** \[Each change, or "None."\]
- **Role consequences for next week:** \[Who plays more or less next week and why, or what has to be reviewed before that is decided.\]

## 7. Week closure

*Written last, after the statbook has been updated from the receipt.*

**Record after game:** \[W-L-T\]

**Division / conference position:** \[Place in the division and how ties were broken; conference seed if the season ended today.\] See \[standings link\].

**Statbook:** \[Through Week X; receipts counted; coverage complete or the gaps; leaders published.\]

**Engine note:** \[Only if something affected the result or its record, or a research step could not be run. Leave the line out otherwise.\]

**Dated record:** \[Descriptive link to the completed game/event owner; the annual Record.md provides its one-line index. A presentation-only rewrite retains the existing event.\]

**Next event:** \[Week X+1 vs. / at Opponent, Day, Month Date, Time\], or \[bye / playoff round / offseason phase\].
