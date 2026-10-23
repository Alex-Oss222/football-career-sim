# Season cycle and career milestones

This guide maps Alex Stone's football year as Jacksonville's head coach and the career points his contract and reviews create. For each step it says what the repository resolves on its own, where the run stops for the user, and which file or command owns the step. It is a map, not a schedule and not a decision. Each season's `Calendar.md` holds the dates, the event owners hold what actually happened, and nothing here advances the career or makes a choice for Stone, Caldwell or ownership.

The research behind the hiring rules and career norms is in [the coaching career path](../library/nfl_coaching_career_path.md) and [the 2014 hiring and anti-tampering rules](../library/2014_coaching_hiring_and_anti_tampering_rules.md). Final authority for every decision is [Document 3's Authority Map](../foundation/03_Head_Coach_Organization_and_Authority_Canon.md) (section 5).

**How to read the tables.** A **stop** means the next step needs Stone's choice from the user: a weekly packet, a phase plan, a memo to Caldwell, or an answer to a live pause. **Automatic** means the step resolves under existing rules, a method frozen before its draw, or a standing instruction, without asking the user. Caldwell's and ownership's own decisions are resolved from their recorded authority and criteria, never assumed, and every automatic draw reads only concrete inputs, never which club is Stone's (Document 1 §9.1). `Y` is the NFL season; dates in brackets are the 2014 season's remaining dates, then the 2015 cycle's, from [the 2014 calendar](../career/2014/Calendar.md) and [the 2015 calendar](../career/2015/Calendar.md).

Apart from a live pause, which the game itself enforces, a stop is enforced only through a decision-queue item of the class that fits it ([decision classes](career_layer.md)); a stop written only in prose here does not halt a script.

## 1. The yearly cycle

| Window | Milestone | Resolves automatically | Stops for the user | Owner or command |
|---|---|---|---|---|
| Regular-season game weeks [2014: October 12 to December 28; 2015: September 13 to January 3, 2016] | Preparation, game and review for one week | Every other game in the week's slate, game records, standings, statistics, weekly league awards, medical reassessments on their recorded dates, other clubs' real roster moves on their dates | Stone's weekly packet: plan, call sheet, inactives and any open role decision. During the game, every Jacksonville fourth down unless the frozen call sheet carries standing fourth-down rules, and any consequential Jacksonville injury replacement. Two-point tries and kickoffs follow his standing sheet rules | [Run Week](run_week.md); `python scripts/build_week_inputs.py N --season Y`; `python scripts/close_week.py N --season Y --close`; `career/Y/Regular_Season/Games/`. Pause rules: [2014 engine decisions](../runtime/2014_engine_decisions.md) |
| Bye week [2014: November 16] | Practice, recovery and self-scout; no game | The week's other games, which close while Stone's bye answers are open | The bye-week plan: from 2014, his My Adjustments page | From 2014, three pages: Bye Week Review, My Adjustments and Bye Week Report ([bye week design](bye_week.md), built in step 5 of the [rebuild plan](rebuild_plan.md)); 2013 kept the week's own output |
| Each month, from the league's announcement date [October awards after Week 9's first game] | Monthly league awards | The draw | None | `python scripts/league_awards.py month NAME --season Y --close`, then render `career/Y/Regular_Season/Awards/` |
| Reserve practice-return windows [2014: October 14 for the PUP and NFI lists; Lowery may practice from October 20 and return no earlier than November 3] | A reserve player becomes eligible to practice or return | Medical clearance, by the medical staff only (Authority Map rows 15 and 16) | Stone's recommendation once a return is possible; the transaction is Caldwell's (row 20) | [Medical history](../career/2014/Team_Operations/Medical/medical_history.md); roster transactions in `Team_Operations/Team/Roster/` |
| Trading deadline [2014: October 28, 4 p.m.; 2015: November 3, 4 p.m.] | Last day for trades | Other clubs' real trades on their real dates | Only if Stone recommends a trade; Caldwell decides (row 20) | [Trades](../career/2014/Team_Operations/Trades/README.md) |
| End of the regular season [2014: December 28; 2015: January 3, 2016] | Futures signing opens the next day; some extensions become possible (Thielen, the day after Jacksonville's last 2014 regular-season game); other clubs' coaching vacancies open | Other clubs' head-coach changes and searches, by a method frozen before its draw. If Jacksonville is out, requests for its assistants under the standing permission default | Futures and extension recommendations to Caldwell, who decides; any change to the permission default | [Upcoming contract decisions](../career/finances/upcoming_decisions/README.md); [January 2014 carousel method](../data/2014/Early_Offseason/staff_changes/carousel_method.json) |
| Postseason [January 3 to February 1, 2015; January 9 to February 7, 2016] | Jacksonville's playoff games if it qualifies. Interview windows for its assistants follow its own results: bye clubs through the Wild Card games, Wild Card winners until the Divisional games end, Super Bowl assistants one second interview | Other playoff games; permission inside the windows; no hire of a Jacksonville assistant before Jacksonville is eliminated | Each Jacksonville playoff game, as for a game week | `close_week.py` for postseason weeks; `career/Y/Postseason/`. Needs `library/data/Y_postseason_slots.json`, which exists for 2013 only |
| Season honours, Pro Bowl, Super Bowl MVP [January and February] | League honours on their dates | Draws from methods frozen before any draw | None | `scripts/season_honours.py`, `scripts/pro_bowl.py`, `scripts/super_bowl_mvp.py` are built for the 2013 season; each later season needs its own frozen method first |
| After Jacksonville's final game | Player and coach exit interviews, the team season review, final player assessments, the ownership and GM review | Handoff bookkeeping and generated views | Stone's part in each exit interview, with every statement recorded as actually made. What he presents and asks for at the ownership and GM review. Renewal or replacement of expiring assistant contracts (row 2, within Caldwell's budget, row 6) | [Season review](../career/2014/Season_Review/README.md); `python scripts/season_handoff.py prepare Y`; `python scripts/build_annual_player_sheets.py --season Y`; [performance review](../career/Stone/Performance_Reviews.md) |
| January coaching carousel | Other clubs replace head coaches and coordinators; some ask about Jacksonville's assistants | Other clubs' searches (Document 3 §10.3); permission answers under the standing default (grant head-coach requests, grant a position coach's move to coordinator, refuse same-title moves) | Replacing any assistant who leaves: one turn for the candidate slate, then offers and counteroffers (Document 3 §10.2) | [Staff changes](../career/2014/Early_Offseason/staff_changes/README.md); `scripts/coaching_carousel.py` is built for the January 2014 cycle only, so each later cycle needs its own frozen method |
| Early offseason [2015: tag window February 16 to March 2, 4 p.m.; Scouting Combine February 17 to 23] | Futures, tags, tenders and scouting preparation | Offers made on Stone's memo terms by a fixed method (2014 precedent: `futures_method.json`) | Stone's offseason memo to Caldwell: tag, tender and futures recommendations; the scouting board. Caldwell decides | [Early offseason](../career/2014/Early_Offseason/README.md); [Stone's 2014 memo](../career/2014/Early_Offseason/stone_to_caldwell_2014_offseason_decisions.md) |
| League year opens [2015: negotiating window March 7 to 10; league year, free agency and trades March 10, 4 p.m.] | Free agency and trades open; contracts ending with the prior season expire | Market draws for the players Jacksonville pursues; other clubs' real moves on their real dates | The free-agency board and trade targets; Caldwell executes | `career/Y/Team_Operations/Free_Agency/`; 2014 precedent `league_year_method.json`; [rails method](../career/2014/League/personnel/method.md) |
| Annual Meeting [2015: March 22 to 25, Phoenix] | League event | Recorded as a league event | None | Calendar |
| Offseason program [2015: April 20, the returning-head-coach start] | Phase One and Phase Two | Practice and training results from the work actually done | The phase plans and staff plan | `career/Y/Offseason_Training/` (`staff_plan.md`, `training_report.md`) |
| Draft [2015: April 30 to May 2, Chicago] | Selections and undrafted signings | Jacksonville's draft order from its own standings; other clubs' real selections | Stone's draft board and recommendations; the picks are Caldwell's (row 4) | `career/Y/Draft/`; `scripts/render_draft_order.py` renders the 2014 order only |
| Rookie minicamp, OTAs, mandatory minicamp [2015: May 8 to 10; ten announced OTA dates May 26 to June 12; June 16 to 18] | Spring teaching | Results from the work actually done | The phase plans | `career/Y/Offseason_Training/` |
| Training camp [2015: reporting July 27 and 30; first practice July 31] | Camp and position battles | Practice results | The camp plan; decisions on actual contested spots | `career/Y/Training_Camp_and_Preseason/` |
| Preseason games [2015: August 14, 22 and 28, September 3] | Four games | The game and its record | Each frozen game plan; a live pause where the rules call for one | `python scripts/close_preseason_game.py N --season Y --close` |
| Roster cuts [2015: to 75 by September 1, to 53 by September 5, each before 4 p.m.] | Cutdowns | Waiver outcomes for other clubs' players on the rails | Stone's recommendation; Caldwell executes (row 7) | `Roster_Decisions/final_roster_cuts.md` |

## 2. Career milestones

| Milestone | When | What happens | Stops for the user? | Owner |
|---|---|---|---|---|
| Hire (closed) | January 15, 2013 | Four-year contract, fully guaranteed in all four years. Stone selects the staff, calls the offense and controls the depth chart and game day; Caldwell holds contracts, cap, scouting, acquisitions, the draft and the final franchise-quarterback call after consultation | Closed | [Hiring search](../career/2013/offseason/hiring_search.md), Entries 6 and 7; [contract sheet](../career/2013/offseason/head_coach_contract.md); Document 3 §3.1 |
| First season review (closed) | January 15, 2014 | Retained on the existing contract, with no extension, raise or authority change, decided from criteria frozen before Stone's review was read. Caldwell's first 2014 measures: scoring margin and the quarterback's ball security (the review's summary adds protection) | Closed | [Owner and GM review](../career/2013/season_review/owner_and_gm_review.md) |
| Running assessment | After each season, an employment decision, or a material change to a standing concern | Ownership's analytical view of his standing. It is not a club decision | No | [Performance review](../career/Stone/Performance_Reviews.md); his record by season on the [Coach page](../career/Stone/README.md), built from the closed games (the [coach sheet](../career/Stone/Coach_Sheet_through_October_2014.md) is history through October 2014); `python scripts/render_coach_record.py Y` |
| 2014 season review, end of contract year 2 | After Jacksonville's final 2014 game, on a date the club sets | Ownership and Caldwell decide whether he stays (row 1) | **Yes**: what Stone presents and whether he asks for an extension, raise, authority or staff budget | `career/2014/Season_Review/` (the season review when held). The rule for resolving the club's decision is still open (section 4, item 3) |
| Assistant contracts | Nine contracts end after 2014 (Bush, Yarno, Bates, Drake, Spencer, Oden, Pleasant, Zernhelt, Skalaski); Crennel, Tice and Westhoff after 2015 (Westhoff's 2015 is not guaranteed) | Renewal, replacement or departure | **Yes**: renew, replace or let go (row 2, within Caldwell's budget, row 6) | [Staff register](../career/2014/Team_Operations/Staff/coaching_staff.md); [coaching payroll](../career/finances/coaching_and_organization/coaching_payroll.md) |
| Requests for his assistants | Each January, from the end of Jacksonville's season | Other clubs ask; Jacksonville answers under the standing default | Only for replacing a coach who leaves, or if the user changes the default | [Carousel method](../data/2014/Early_Offseason/staff_changes/carousel_method.json), stage 4 |
| Extension window | At the 2014 or 2015 review, if the term ends after 2016. Clubs usually extend before a final contract year, a pattern seen only in later sources | An offer, or none | **Yes**: whether to ask, then accept, counter or decline | [Upcoming contract decisions](../career/finances/upcoming_decisions/README.md) ("Before Stone's term ends after 2016") |
| Final contract year | 2016, if no extension is signed | Staff recruiting and retention become harder (later sources) | Indirectly, through the staff decisions it affects | Same |
| Contract end | The later of January 31, 2017 or the day after Jacksonville's last game of the 2016 season (a labelled reconstruction in Stone's coach record, stated so in Document 3 §3.1) | He becomes a free coach: any club may talk to him without permission | **Yes**: whether and where to seek work, through a written job-search brief | AGENTS.md, "Run the [year] hiring search"; Document 3 §10 |
| Firing | After any season, rarely during one | The employer decides (row 1). All four years are guaranteed. Dismissed without cause, he is owed the unpaid remainder, less dollar-for-dollar pay from another coaching job through the end of the term (the offset), with no separate buyout; dismissed for cause, nothing further (completed terms in Stone's coach record). He is free at once. A new head coach may release or reassign the assistants, subject to their guarantees | No for the firing itself. **Yes** for his next move | Document 3 §3.1 and row 1; staff register (head-coach change); AGENTS.md hiring-search task |
| Another club asks for him | Offseason only; during his season no club may ask | Shad Khan alone decides Jacksonville's consent: grant, refuse, or ask for compensation, which may be negotiated for a head coach only (Document 3 row 1a, the user's decision of October 20, 2026) | Not while his standing answer holds: he is not open to job offers, so a request and Khan's answer reach him as news. He may change that answer at any time | Rules file H1 to H3; the job record's standing instructions |
| Resignation | Any time | Not free to join another club without Jacksonville's consent | **Yes**: his own choice | Rules file E5 |

## 3. Going from one year to the next

**Checklist, October 17, 2026.** This section lists existing commands and owners only; it adds no rule, event, ledger or transition packet. [Season folders and record ownership](season_structure.md) (season continuity) remains the layout authority and the [season review and handoff](../career/2014/Season_Review/README.md) remains the single closeout manifest, with the full eight steps. The example is the 2014 season into 2015. A staged or reviewed season does not renew a contract, clear an injury, decide a job or authorize a game, and Stone keeps every consequential football and contract choice along the way.

**A. Research ahead (any time; never advances the clock)**

| Need | Owner | Tool today | 2014 into 2015 |
|---|---|---|---|
| Next year's calendar, two passes | `career/Y+1/Calendar.md`, `library/Y+1_historical_calendar.md` | By hand | Present |
| This season's postseason format and slots | `library/Y_postseason_format_and_schedule.md`, `library/data/Y_postseason_slots.json` | By hand (2013 precedent) | Missing; needed before the Week 18 build |
| Season honours, Pro Bowl and Super Bowl MVP methods, frozen before any draw | `career/Y/Postseason/Awards/`, `career/Y/Postseason/Pro_Bowl/` | `season_honours.py`, `pro_bowl.py` and `super_bowl_mvp.py` read 2013 paths only | Missing |

**B. Finish the season**

1. Close Weeks 1 to 17 with the Run Week workflow, drawing each month's awards on the league's announcement date.
2. Close each playoff round with `python scripts/close_week.py WEEK --season Y --close` (weeks 18 to 21); it needs the slots file above.
3. Draw the season honours, the Pro Bowl and the Super Bowl MVP on their dates and record each at its owner.
4. The annual record keeps postseason events with their NFL season (season continuity). Whether the January exit interviews and ownership review that close season Y also carry `"season": Y` in their event metadata is an open question for the user ([cleanup report](repository_cleanup_2026-10-17.md), Y10).

**C. Team closeout (after Jacksonville's final game; handoff steps 1 to 3)**

`python scripts/season_handoff.py prepare Y`; the player and coach exit interviews (**Stone stop**); the team review; the final player assessments (`python scripts/build_annual_player_sheets.py --season Y`, then `--review`); each team gate and reference group completed with hashed evidence in the manifest; then `python scripts/season_handoff.py check Y`.

**D. Stage and review the opening (handoff steps 4 to 7)**

Verify the next historical calendar, then `python scripts/season_handoff.py stage Y`. Author each returning player's opening assessment from his reviewed final, reconcile the seven opening areas, then run `python scripts/season_handoff.py check-opening Y+1` and `review-opening Y+1`. Staging leaves an existing `career/Y+1/README.md` untouched; `career/2015/README.md` already exists, so its wording has to be reconciled when 2015 is activated ([cleanup report](repository_cleanup_2026-10-17.md), Y23).

**E. Activate Y+1 (handoff step 8: one authorized administrative event, one commit)**

Inspect and update, as the atomic progression rule requires:

- `docs/repository_map.json`: `active_season`, the `current_records` keys, `record_years` and `required_files` for new owners; `phases` as each phase plan is written; `active_playbooks` only when an iteration's effective range ends.
- `state/05_Current_Season_State.md` and `state/04_Roster_and_Staff_Register.md`, with their versions and checkpoints advanced together.
- `career/Y+1/README.md`, `career/README.md` and the root `README.md` start links.
- The generated views: `python scripts/render_annual_record.py Y+1`, `python scripts/render_player_ages.py`, `python scripts/render_player_pages.py`, then `python scripts/validate_repository.py`.
- Year-named instructions in `AGENTS.md` (the 2014 carry-forward, 2014 individual training and film, and 2014 E1/E2 sections) need the user's own Y+1 wording: flag them, do not rewrite them ([cleanup report](repository_cleanup_2026-10-17.md), Y22).

**F. New-year work by information date**

Each item closes as its own event at its owner on its real date. The 2015 dates are from [the 2015 calendar](../career/2015/Calendar.md).

| 2015 date | Work | Owner | Tool today |
|---|---|---|---|
| January | Coaching carousel and permission requests (**Stone stop** for replacements) | `Early_Offseason/staff_changes/` | The January 2014 scripts are one-offs; a 2015 method and a season-aware script are needed |
| January to February | Reserve/future contracts (**Stone stop**) | `Team_Operations/Free_Agency/` | `futures_2014.py` is a one-off |
| February 16 to March 2 | Franchise and transition tags (**Stone stop**) | Free agency, contract status | By hand |
| March 10, 4 p.m. | League year: expiring contracts end, tenders, market draws, other clubs' moves on the rails | Finances, `League/personnel/` | `league_year_2014.py` is a one-off. The cap tracker's year range and its 2014-specific rows need review first ([cleanup report](repository_cleanup_2026-10-17.md), Y20) |
| March | Compensatory picks | `Draft/compensatory/` | `resolve_compensatory_picks.py` resolves the 2014 picks only |
| Before the draft | Draft order and a pick-ownership audit | `Draft/` | `render_draft_order.py` and `runtime/draft_order.py` cover the 2014 draft only |
| April 20 | Offseason program begins; preseason dates announced | `Offseason_Training/`; `Preseason_Games/fixtures.json` | Phase plans by template; fixtures by hand |
| April 21, 8 p.m. | Regular-season schedule release | `Regular_Season/Schedule/fixtures.json` | No builder |
| April 30 to May 2 | Draft and the rails pairing (**Stone stop** for the board) | `Draft/`, `League/personnel/draft_pairing.md` | By hand |
| August | Preseason opponent rosters | `library/Y+1_preseason_opponent_rosters.md` | The builder covers 2014 only |
| Before Week 1 | The season's release record (seven gates), awards method, Week 1 depth library, in-season rails, defensive-back families, player-state table and binding, and the game depth chart | `runtime/season_readiness.json`, `library/data/Y+1_*`, `Regular_Season/Awards/methodology.json` | The builders cover 2014 only; `python scripts/bind_latent_season.py Y+1` from merged `main` |

**G. Checks**

`python scripts/season_handoff.py check Y`, `check-opening Y+1`, `python scripts/render_annual_record.py Y --check`, `python scripts/render_player_ages.py --check`, `python scripts/render_jaguars_cap_tracker.py --check` and `python scripts/validate_repository.py`; then `python scripts/check_game_readiness.py --season Y+1` before any game. A green check is not game authorization.

## 4. Open questions for the user

These gaps affect the milestones above. Each needs a canon decision or a dated research note, not a guess.

1. **Stone's contract end date.** Resolved: the later of January 31, 2017 or the day after Jacksonville's last game of the 2016 season, completed from the wording of Jacksonville's own 2010 assistant contracts under the user's October 18, 2026 delegation (Stone's coach record, `data/people/coaches/alex_stone.json`; [Contract and jobs](../career/Stone/Contract_and_Jobs.md)). Document 3 §3.1 states it, labelled as a reconstruction, since October 20, 2026.
2. **Consent to approach Stone.** Resolved October 20, 2026 by the user: Shad Khan alone decides (Document 3 row 1a), and Stone's standing answer is that he is not open to job offers. Document 3 §3.2 (supervisor, evaluator, escalation path) is still unset.
3. **The 2014 employment decision.** The January 2014 carousel left Jacksonville out because the January 15 review had already retained Stone. Before the 2014 season ends, the method should state, in a way that passes the label-swap test, whether Jacksonville's decision is resolved by a review with criteria frozen first, as in January 2014, or by the same base-rate draw other clubs receive.
4. **Assistant contract expiry within the offseason.** Terms are recorded by season. The second-Tuesday rule for expiring contracts is unverified, so the date the nine 2014 contracts lapse is not fixed.
5. **Inputs the 2014 postseason and January 2015 need.** A `library/data/2014_postseason_slots.json` file, frozen 2014 honours methods and a January 2015 carousel method; today's scripts cover 2013 honours and the January 2014 carousel only.
6. **Stale lines.** [The 2015 calendar](../career/2015/Calendar.md)'s clock and E1/E2 lines were corrected in the October 17, 2026 cleanup. [The 2015 calendar research](../library/2015_historical_calendar.md) still tells the reader to apply the branch-standings rule to two opponents, which the user's September 29, 2026 clarification replaced; that dated research note should be annotated, not rewritten.
7. **No 2016 calendar.** The derived final contract season has no sourced calendar yet. It can be researched ahead without advancing the clock.
