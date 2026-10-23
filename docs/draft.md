# NFL Draft workflow: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 7 of the [rebuild plan](rebuild_plan.md). Corrected after the process check of October 20, 2026, against the rulings and the defaults the lead settled with it, each written below as this design's rule. No question in this design awaits the user. It relies on one that does, how the club decides Stone's 2014 employment ([season end design](season_end.md#how-the-club-decides-awaiting-the-users-decision)), since the Jacksonville draft pages go to Stone only if the Club Decision retains him (section A). Two other questions from the spring and summer process check are awaiting the user's decision and change nothing here: whether Document 7 §5.1 and Document 1 line 229 are reworded for the per-game preseason pages and the camp and cutdown pages (proposal: yes; the rulebook changes only with the user's approval), and how 2015 practice observations are produced (proposal: the 2014 authored, protagonist-blind method with its evidence rules; no resolver is approved yet), which governs what rookie minicamp records after the draft. The templates are in [foundation/templates/draft/](../foundation/templates/draft/), the worked example is [docs/examples/draft_jacksonville.md](examples/draft_jacksonville.md) and the research register and repository assessment are in [docs/draft_research.md](draft_research.md). What the build must add, in files outside this design, is listed in section L.

As uploaded: **Status:** Research and design contract. No file in `Alex-Oss222/football-career-sim` is changed by this package. No draft decision, trade, contract or simulated game is resolved. The tests below are specifications and were not executed against a checked-out repository.  
**Repository inspected:** `Alex-Oss222/football-career-sim`, `main`, at main commit `75fd41f` (Merge pull request #255) observed on 20 October 2026. The repository changed while this research was underway; revalidate against the then-current tree before implementation.  
**Current career:** Sunday 5 October 2014, after Jacksonville's Week 5 game; Week 6 remains unplayed. Do not back-port the new three-page draft process to the already completed 2014 draft.

## NFL Draft: researched three-page workflow package

**Repository:** `Alex-Oss222/football-career-sim`  
**Research snapshot:** main commit `75fd41f`, observed October 20, 2026  
**Scope:** the NFL Draft workflow in the established six-workflow redesign sequence, intended for the first future applicable draft and reusable with season-specific law and source checks. The actual 2015 draft begins April 30, not generically in May.  
**Current simulated career:** after Jacksonville's October 5, 2014 Week 5 game, Week 6 unplayed.  
**Status:** **Research and design only.** Nothing in this package has been installed in the repository's code, no league or Jacksonville selection has been simulated, and no future player, contract, roster assignment or staff outcome has been created.

### The three required coach-facing pages

| Order | Artifact | What the reader sees |
|---|---|---|
| 1 | [01 Scouting Department Report](../foundation/templates/draft/scouting_department_report_template.md) | A genuine college scouting briefing, presented by the general manager, with the actual pick inventory, roster football questions, dated eligible prospects, named uncertainty and the event inserts directly under its header. |
| 2 | [02 My Draft Recommendations](../foundation/templates/draft/my_draft_recommendations_template.md) | A natural head-coach memo to the general manager, with the user's selected priorities, individual first jobs, preferred prospects, precise fallbacks and conditions; it answers the report once and is frozen when the first round begins. The general manager retains final picks and trades. |
| 3 | [03 Draft Room Results](../foundation/templates/draft/draft_room_results_template.md) | A read-through of selections made and their football implications, linked to **separate dated pick, negotiation, contract and undrafted-pursuit results**, including failures. |

Answers to events raised during the draft go on the Draft folder's own My Responses page, from the shared [My Responses template](../foundation/templates/event_inserts/my_responses_template.md), with the registry's file name, `My_Responses.md`.

### Supporting implementation and example files

| File | Function |
|---|---|
| [04 Individual Selection Result](../foundation/templates/draft/selection_result_template.md) | The draft-selection form of the shared [event result](../foundation/templates/event_inserts/event_result_template.md): one dated result per completed selection, with its event-record line; never a combined result. Undrafted pursuits and rookie contracts use the [free-agent result](../foundation/templates/free_agency/free_agent_result_template.md) form, and draft-day trades the trade result. |
| [05 Implementation and Validation Specification](#a-fixed-scope-and-first-principles) | Detailed requirements for years, historical rails, roster/authority separation, draft stops, source gates, per-event outcomes and **72 proposed regression tests** (64 uploaded, eight added by the process check). |
| [06 Worked Jacksonville Example](examples/draft_jacksonville.md) | Three-page reorganization of **already completed 2014 facts**, including No. 205, plus the October 5, 2014 prospective 2015 nine-pick position. No future 2015 outcomes. |
| [07 Research and Source Register](draft_research.md#2014-2015-nfl-draft-research-law-contemporaneous-process-and-information-gates) | Original 2011 CBA, 2014-15 dated NFL sources, 2015 draft timetable, contemporary club scouting procedures and date-information boundaries. |
| [08 Repository Assessment and Blockers](draft_research.md#nfl-draft-redesign-repository-assessment-conflicts-and-implementation-blockers) | What works in the repository, missing implementation, precise risks and non-negotiable integration order. |

### Non-negotiable operating rules

- Do not change Alex Stone's executed contract, adopted philosophy or current job authority. David Caldwell makes binding draft, acquisition, trade and player-contract decisions on Stone's recommendation. Stone chooses only his own football recommendations and his documented franchise-quarterback consultation right (section B).
- Never invent a 2015 prospect grade, final 2014 record, 2015 Jacksonville draft slot, college-scout tape report, staff conversation, independent medical clearance or a future NFL player performance. A later real draft selection is never a scouting fact at an earlier in-story time. No real 2015 outcome is an input: not the real Jaguars' 2015 slot or class, and not the 2015 compensatory recipients.
- The user-approved 2014-onward historical league personnel exception applies to the other 31 clubs' real selections; Jacksonville's own pick ownership/order come from its career. Jacksonville can choose only a prospect whose real overall pick is at or after its live branch choice N, or who was undrafted; the real Jaguars k-th pick pairs with Jacksonville's k-th exercised selection (AGENTS.md rails rule 7). Enforce self-pairing, absent partners and unique player control without inventing compensation. Information becomes usable on its real public date.
- **One closed consequential event must get one own dated readable result.** Nine distinct concluded draft selections mean nine distinct pick results, not a nine-line summary alone. Likewise, two rejected negotiations mean two separate failed outcomes. The main report links; it never replaces. Every result is a form of the shared event result, in its owner's folder (section G).
- Stone answers the Scouting Department Report once, on My Draft Recommendations. Events inside the phase are inserts in the active brief, answered on the Draft folder's one My Responses page. Only an answer due before the event it holds stops the clock (section H).
- The draft, undrafted recruiting, rookie-contract negotiations and rookie minicamp are separate legal and football events. An acquired right is not a signed player; a signed contract is not a medical clearance; a medical clearance is not a starting job.
- Keep technical event IDs, data paths, source digests, script names and validation terminology out of live coach-facing pages. They belong in technical records and this documentation. The coach-facing pages use none of the words branch, simulation, receipt, kernel, engine, ledger, snapshot or checkpoint, and say play-by-play rather than receipt.

### The six spring and summer designs

The six spring and summer designs, this one included, were uploaded together on October 20, 2026; the [spring and summer index](spring_and_summer_designs.md) lists them and their build steps.

No scripts in this archive are intended to run against the active career. The tests specified here require implementation in a future authorized PR and must not be described as passing now.

## A. Fixed scope and first principles

Three permanent coach-facing draft page titles already exist in `runtime/decisions.py`:

| Registered workflow | Staff report | Stone's editable response | Published phase result |
|---|---|---|---|
| `draft` | `Scouting_Department_Report.md` | `My_Draft_Recommendations.md` | `Draft_Room_Results.md` |

Their logical destination is `SeasonPaths(draft_year).record('draft')`, resolving to `career/<draft_year>/Draft/` on the 2014+ season layout. The current registry says `when="May"`; the 2015 draft begins **Thursday, April 30**, and ends May 2, and the 2013 draft ran April 25 to 27. The build relabels the draft row's When as "Late April or May" in `runtime/decisions.py` and in the rebuild plan's phase table in one commit, because a test requires the two to match (section L); the pages take the draft's dates from the season's calendar, which owns them. The identity, file names and folder stay the same. No other three-page workflow needs to be reopened or redescribed.

Do not treat this as one disposable prompt called “simulate the draft.” It has dated preparation, potentially revised briefings, Stone's user-owned recommendation, individual league and Jacksonville picks, real offers if they arise, rights acquired, and distinct post-draft negotiations and unsigned players. Caldwell makes selections and conducts trades and contracts. The draft occurs alongside the April offseason program, whose Phase One may still be in progress April 30. A pick neither retroactively adds a rookie to April workouts nor decides the later rookie minicamp or OTA outcome.

**Two briefs at once.** When phases overlap, two briefs may carry inserts at the same time, and each event appears once, on its own phase's brief. While the Offseason Program Brief and the Scouting Department Report are both active (in 2015 from the report's April 29 issue; the report carries inserts until Draft Room Results is published after the undrafted pursuits, and the Offseason Program Brief until Phase Two closes on May 22), draft-pick trades and prospect, selection, rookie-contract and undrafted matters go in the Scouting Department Report and are answered on the Draft folder's My Responses page; practice, roster, medical and staff matters go in the Offseason Program Brief and are answered on the April program's My Responses page. A notice is never repeated on the other brief. Before the Scouting Department Report's first issue (April 29 in 2015), a draft matter, a pick-trade inquiry included, goes on the Offseason Program Brief, the only active brief, and is answered on the April program's My Responses page. Rookie-minicamp direction is a post-draft reissue of the Offseason Program Brief, not a Draft page.

**Who receives the pages.** If the club decision after the 2014 season retains Stone, he receives the Jacksonville pages. If he holds another job, he receives that job's version of the pages, with that job's scope ([rebuild plan](rebuild_plan.md#the-decisions-in-a-year)). If he is out of work, there is no Jacksonville brief or My page, and Caldwell drafts on his frozen board method (section B). This routing follows from rules already in place ([event inserts](event_inserts.md), section B); only the club-decision method itself awaits the user.

**Scope boundary:** the selection meeting and its immediately opened undrafted recruiting work belong in Draft. A scouting report is not a hidden full 2015 result set. The future 2015 draft can be designed now; it cannot be opened as a completed phase or populated from the real Jaguars' 2015 finish.

## B. Governing canon and authority

Read the current copies of `AGENTS.md`, `docs/rebuild_plan.md`, `docs/season_structure.md`, `docs/event_inserts.md`, `foundation/01_Project_Instructions.md`, `foundation/02_League_Era_and_Sourcebook.md` (especially §4.3a/§4.5 and §12), `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `foundation/06_Event_Records_and_Handoff.md`, `state/current_job.json`, `state/decision_queue.json` and the current career and draft records.

The authority rule of the [rebuild plan](rebuild_plan.md#the-decisions-in-a-year) governs: Stone decides depth, roles, inactives, practice and his staff; Caldwell decides acquisitions, the draft, contracts, claims and cuts on Stone's recommendation; the medical staff decide diagnosis and clearance.

- **Stone, head coach:** football assessment, role projection, which attributes and assignments matter, coaching costs, prioritized recommendations and his dated responses. He controls the depth chart and how the eventual rookies are coached; he does not choose the selected player, execute a draft-pick trade or sign a prospect.
- **Caldwell, GM:** final college scouting/board administration, choice of a player at every Jacksonville draft selection, trade offers and acceptances, rookie contract negotiations/execution, undrafted recruiting and personnel acquisition. A Stone target is not a pick, and a club press report is not Caldwell's decision in this career.
- **Franchise-quarterback matters:** the job record's row 3a gives Stone a written football projection and a meeting to resolve disagreement before Caldwell acts, with no concurrence or veto. It covers four matters, in the job record's words: "using the first-round pick on a QB, trading premium draft capital for one, a major multiyear financial commitment to one as the intended starter, or a major disposition of the starting QB." A first-round quarterback pick opens the consultation whatever role he is meant for, and so does trading premium capital for any quarterback. A quarterback taken after round 1, with no premium capital traded, does not open it, and a scouting discussion alone opens nothing.
- **Medical professionals:** medical assessments, restrictions, participation and clearance. Stone can assess a football role within communicated limitations. A press injury summary is not an authorized team physical or private medical finding.
- **Other clubs:** choose or trade based on the user-authorized historical personnel rails where those rails apply, but the branch's standings, playoff outcomes, existing pick transactions and coaching carousel are not copied from reality.

**Names on the pages.** Staff names come from the coach records (`data/people/coaches/`) and the job record's parties at issue time, never fixed in a template: the step 7 form is "[Mike Tice (or the offensive coordinator then in the coach records)]". The Scouting Department Report is presented by the general manager for the college scouting department, as the Pro Personnel Report is; a scout is named as an author only when he is a party in the job record, and today none is. Prospect evidence rests on dated public pre-draft sources, as in 2014, where no Jacksonville-authored report exists ([2014 draftees](../career/2014/Draft/draftees.md)).

**Caldwell and Stone's named players.** Caldwell takes an available, eligible player Stone named first at a pick, unless a recorded medical, eligibility or contract restriction says otherwise; that restriction is written on the selection page. In 2014 Caldwell took the player Stone named at all nine picks (at No. 205, the player Stone named when the pick stopped for him), and the runbook applied the authorized board ([2014 draftees](../career/2014/Draft/draftees.md); [2014 Draft README](../career/2014/Draft/README.md)). The same rule would apply to any head coach, so it passes the label swap.

**Caldwell's own board.** Where Stone names no one at a pick, or tells Caldwell to use his own board there, Caldwell selects by a board method frozen before the draft and checked with the label swap: the dated public pre-draft boards available by the information cutoff, weighed against roster need and Caldwell's documented philosophy, filtered by the availability rule (Document 2 §12 on Jacksonville's own evaluations and selecting-club behavior). No method is improvised at a deadline.

Continuing rules: four-year fully guaranteed Stone head-coach contract accepted January 15, 2013, no 2014 extension/authority change; offensive calls and defensive calls currently Stone's, Crennel prepares/transmits the defense, Westhoff calls special teams, and Tice coordinates offensive work. These do **not** require another April approval. Neither a successful draft nor a poor game changes these terms. The staff can change in January, and Westhoff's 2015 is not guaranteed ([season milestones](season_cycle_milestones.md)), so the pages read the staff at issue time. Stone's philosophy favors evidence-backed assignments, personnel flexibility, protection details, Dagger/Mesh/play-action and coherent front/coverage teaching; it is not permission to predetermine that the draft fixes those things.

## C. Chronology and exact era rules

The season's calendar and the library own these dates and rules; the pages and this design link them ([2015 calendar](../career/2015/Calendar.md), [its sources](../library/2015_historical_calendar.md), [event inserts](event_inserts.md) sections A.5 and A.6). Rows not yet in the 2015 calendar are added there after two passes (section L).

| Fact / constraint | Controlling 2015 value | Timing and information rule |
|---|---|---|
| Draft | April 30 to May 2; Auditorium Theatre, Roosevelt University, Chicago | NFL announcement **October 2, 2014**: legitimately knowable October 5. NFL announced Thursday R1, Friday R2-3, Saturday R4-7. The announcement date and venue are not yet in the 2015 calendar. |
| Daily starts | April 30 8 p.m. ET; May 1 7 p.m. ET; May 2 noon ET | Contemporary April 29/30 draft notes and the 2015 club fact sheets support the detailed start times. Do not assert an earlier public release of the precise hours without a dated notice. |
| Selection clock | R1 10 minutes; R2 7; R3-6 5; R7 4; compensatory choices in R3-7 4 | Contemporary 2015 draft notes, not today's draft clock. The four-minute round 7 and compensatory clocks were a change made shortly before the draft, reported by April 27, 2015; the league's own first public date is unverified and is fixed in the two-pass calendar entry, and a page issued before that date does not show the change. Pages show the era's clock limits only; no NFL clock time runs during a stop (section H). |
| Draft format | Seven rounds, normal 32 original clubs' choices per round, plus up to 32 additional compensatory selections (the CBA maximum, equal to the number of clubs) | 2011 CBA Article 6 §2 and §10. Branch recipients are resolved in the career and never imported. Any forfeiture, supplemental obligation or other league adjustment must be verified. |
| Underclassmen | January 15, 2015 application deadline, January 19 NFL special-eligibility announcement | Announcement identified 74 approved applicants and ten eligible graduates with college eligibility remaining. No full list in October 2014. Neither date is yet in the 2015 calendar. |
| Combine | February 17-23, 2015, Indianapolis | Invitation is not testing; results open on the day actually measured/performed. Private club interview/medical claims require a real club event. |
| Compensatory picks | 2015 award announced Monday, March 23, at the Annual Meeting; up to 32, placed in rounds 3 to 7 | The real recipients are not inputs and are not recorded here. Resolve from branch-eligible 2014 free-agent movements by the method of section D, frozen before the award date. 2015 comp picks were nontradeable. |
| First-round rookie contract | Four years with fifth-year club option | CBA Article 7 §3 and §7, not a completed fifth year or executed compensation schedule. |
| Rounds 2-7 rookie contract | Four-year fixed term | Draft rights, contract signature and rookie cap charge are separate dated events. |
| Undrafted rookie contracts | Three-year fixed term | No signing until the eligible principal draft has completed under Article 6 §11; a recruiting list does not create a player contract. |
| After-draft camp | Jacksonville historical May 8-10 rookie minicamp | An announced slot alone does not establish an eligible player's presence, signed contract, medical clearance, practice or teaching result. |

**Rookie contract pricing (settled by the lead).** Each 2015 pick is priced by the 2014 slot reconstruction ([2014 draftees](../career/2014/Draft/draftees.md), rookie contracts): the real same-slot 2015 contract with the 2015 minimum bases from the two-pass 2015 financial-rules entry, labelled a reconstruction. The comparator is the slot, never the selected player's own later deals.

### Source timing categories

Maintain for each evidence claim `event_at`, `announced_at` or `published_at`, `known_to_club_at` if privately and genuinely established, `source`, `source_scope` and `retrieved_at`. A document published later may corroborate that a rule existed earlier but cannot be used as a fictional in-world press release. Prospect video may be recorded during the college season but a later analytical report is not already authored at the game's date.

October 5, 2014 provides **only** the NFL's October 2, 2014 announced 2015 date/site, then-current branch roster and 2014 five-game football evidence, carried contracts and closed transfers. It does not provide January eligibility awards, combine times, final scouting analyses, 2014 NFL season finish, 2015 draft order, 2015 staff employment outcome, comp awards or real 2015 Jaguars draft choices. The publication date of the club's 2015 scheduled rookie minicamp was not recovered in the 2015 calendar research; it is a historical scheduling reference until a legitimate club-held or dated source establishes when Stone knew it.

## D. Live pick ownership and numbering

**Source owners:** original pick identities and dated transfers in the 2015 draft register under `data/2015/Draft/`; each trade retains its one distinct dated source in its contract/Trades owner; `career/2015/Draft/draft_order.md` is generated from reconciled records. Resolve this directory from `SeasonPaths`, not handwritten year-folder literals inside non-folder-map modules. **One fact, one place:** at the year change the 2015 register reads the 2014 register's 2015 entries as its dated sources and records only later transfers. Nothing is copied or relabelled, and the 2014 file is locked with its season.

**Verified holdings at the 2014 Week 5 date**, from the [pick register](../data/2014/Draft/pick_ownership.json) (every recorded move of a 2015 pick involving Jacksonville), the [2013 Cousins record](../career/2013/trades/trades.md) (the 2014 and 2015 seconds only) and the [2014 trade records](../career/2014/Team_Operations/Trades/completed_trades/README.md):

| Asset | October 5, 2014 disposition |
|---|---|
| Jacksonville's original 2015 first | **Owed to Arizona** (March 20, 2014 Nwaneri and picks trade) |
| Jacksonville's original 2015 second | **Held by Jacksonville**, reacquired from Washington March 31 |
| Jacksonville's original 2015 third | **Held by Jacksonville**; no transfer recorded; 2015 all-club audit pending |
| Miami's original 2015 third | **Held by Jacksonville**, March 24 Babin trade |
| Houston's original 2015 fourth | **Held by Jacksonville**, March 24 Alualu trade |
| Arizona's original 2015 fourth | **Held by Jacksonville**, acquired April 7 Allen trade |
| Jacksonville's original 2015 fourth | **Owed to Arizona** |
| Jacksonville's original 2015 fifth | **Held by Jacksonville**; no transfer recorded; 2015 all-club audit pending |
| Jacksonville's original 2015 sixth | **Held by Jacksonville**; no transfer recorded; 2015 all-club audit pending |
| Jacksonville's original 2015 seventh | **Held by Jacksonville**; no transfer recorded; 2015 all-club audit pending |
| Seattle's original 2015 seventh | **Held by Jacksonville**, acquired May 12 Rackley trade |
| Jacksonville's 2016 fifth | Future debt to Arizona; **not** a 2015 selection |
| Jacksonville's 2017 seventh | Future debt to Miami; **not** a 2015 selection |

Thus **nine 2015 ordinary pick assets are held** at this date: own second, own third, Miami third, Houston fourth, Arizona fourth, own fifth, own sixth, own seventh and Seattle seventh. These are not their eventual overall slot numbers and not a promise of nine selections on draft day. The register's audit scope says other 2015 assets are not yet audited, so the four own originals in rounds 3, 5, 6 and 7 stand as held with no transfer recorded until the audit. The current-state summaries (Document 5 section 5 and Document 4's draft capital) list five picks; their correction is handled separately from this design. The 2015 audit must enumerate **all 224 original seven-round assets for all 32 clubs** and determine final holders, restrictions, duplicate transfers and pending conditions, including the open Flynn 2015 condition ([2014 ownership audit](../career/2014/Draft/ownership_audit.md)), preserving all recorded branch deals. Unknown does not mean free and transferable.

**Other clubs' real pick trades.** A real inter-club pick transfer from the 2014 to 2015 period is booked in the 2015 register only when its player side rode the rails or is consistent with branch evidence; a pure pick swap with no player is not booked. Other clubs still draft their real players either way. This is how the 2014 audit worked, and it respects Document 2's ban on importing real pre-draft trades.

Compute original-club slot from the 2014 regular-season records and playoff eliminations of the closed 2014 games, then apply the correct lower-strength-of-schedule tiebreak, necessary division/conference steps and subsequent round rotation. A tie that survives strength of schedule and the tiebreakers is drawn by the private service under a protocol frozen beforehand, unless the user asks for an external flip again: the 2014 website flip was authorized for that tie only ([2014 coin flip record](../data/2014/Draft/coin_flip.json)). Join ownership by `(draft_year, round, original_club)`, never a previously guessed overall number. Honor all legal forfeitures if documented. The 2014 `runtime/draft_order.py` and `scripts/render_draft_order.py` are year-specific, including hardcoded 2014 coin-flip expectations; extracting reusable season logic must preserve the completed 2014 order byte-for-byte and must not resolve a 2015 tiebreak using the old flip.

**Compensatory method (settled by the lead).** Compensatory awards cannot be resolved merely from nominally available free agents or 2015 real recipients. The 2014 `scripts/resolve_compensatory_picks.py` and its frozen method apply **only** to 2014, using 2013 free agency, 2013 games/honours and a 2014 club order. For 2015 the 2014 value-points method, version 2 ([method](../data/2014/Draft/compensatory/method.json), adopted at the user's request for realism), is restated with 2014 league-year inputs (other clubs' real moves and Jacksonville's branch moves, audited contracts, the 2014 branch season and frozen 2014 season honours) and 2015 dates, committed before March 23, 2015 and resolved on that date. If the inputs are incomplete, **hold the affected final pick numbering and execution** rather than silently copying reality or awarding default zero compensatory choices. Show provisional round slots without claiming an exact global overall number.

The real Jaguars' 2015 draft slot is never an input and is not recorded in this design. Jacksonville's order is derived only from the closed 2014 games and the recorded ties. A reported trade of a comp selection in 2015 must fail validation even if later league rules would permit it.

## E. Player evidence, college eligibility and board rules

A separate library task, "Expand the real-data library: the 2015 NFL draft class" (two passes, pre-selection data only, dated gates), creates `library/2015_draft_information_gates.md` and a source-controlled 2015 eligible-player registry as the information reaches its legitimate dates, before the Scouting Department Report's scheduled issue. The build step adds only the machinery. The 2014 versions are **precedents**, not valid 2015 prospect data. Distinguish:

1. **College eligibility:** three seasons after the entering high-school class/graduation for special entry, the player's own declaration/league approval, or ordinary senior status, and relevant exceptions from Article 6. Keep uncertain eligibility out of executable selections.
2. **Evidence date:** completed 2014 college plays and honors become available when played/announced; all-star practice and game observations by their specific days; combine invitation and each measurement separately; pro days, permitted private workouts and player visits only if genuinely held/recorded.
3. **Film finding:** opponent, context, alignment and job, technique or read, observed action and limitation. College film does not prove NFL position mastery or a quantified development boost.
4. **Club assessment:** scouting department view and identifiable coaching contribution, with dissent preserved if an actual person expressed it. A scout is named only when he is a party in the job record. Do not create a fake scout interview, doctor clearance, background fault, leadership grade or testing result.
5. **Plan-to-use:** initially plausible NFL job, personnel grouping, coaching responsibility, learning cost and comparison with already-controlled players. No automatic starting job or playbook unlock based on pick round.
6. **Draft price:** named existing asset or value band, and a valid ordered fallback or explicit stop. A round-price judgement is not a numerical “talent score.” Never turn a table of comparative names into a preauthorized selection priority.

If only an old public scouting sheet exists, the scouting department may explain a narrow football inference from it; never label it an internal evaluation that no Jacksonville employee performed. User-authored Stone preference is a recorded preference, not proof of a scout's grade. No post-selection statistics, rookie-season injuries, NFL success or later personality commentary may influence a prospect decision.

The substantive prospect board remains Caldwell's scouting source, with Stone's **own** response on `My_Draft_Recommendations.md`; the two may disagree. The brief proposes; Stone's page decides his recommendations. The later `Draft_Room_Results.md` is not a new master board and must not rewrite the pre-draft evaluation after the result becomes known.

## F. Historical-league-rails exception, exact application

The rules in `AGENTS.md`, Document 2 §4.5, and `career/2014/League/personnel/method.md` §6 govern the 2014-and-later branch. The 2015 work must retain all of them, not import the real Jaguars' 2015 signing or draft class:

1. Other 31 clubs' **player selections** follow their actual corresponding draft selections, subject to actual branch ownership/control corrections and the approved pairing method. Their real draft **order** does not replace the branch's actual order, playoff results or acquired-pick ledger.
2. Jacksonville's prospect at simulated overall pick `N` passes the *special, user-authorized historical filter* only if the prospect was selected at real pick `N` or later, or went undrafted. Check ordinary NFL draft eligibility and no prior branch assignment too. The original NFL year and prospect identity must match.
3. Jacksonville's **k-th exercised selection** pairs with the real Jaguars' **k-th real selection**. That real player goes to the club that really drafted Jacksonville's chosen prospect, or if the prospect went undrafted to the club where he really signed. If no valid partner exists the player is unplaced. The method does not create an automatic fallback club.
4. Do not move a Jacksonville-controlled player away simply because the real Jaguars' k-th name appears on another line. Treat self-pairing and already-controlled players as explicit exceptions, as occurred with Telvin Smith in 2014. Never duplicate an acquired player or a Week 1 depth slot.
5. Reconcile other clubs' affected Week 1 depth charts **when their dated source material is allowed**; remove the Jacksonville-controlled prospect from his original club, apply permitted counterpart relocation and next-man-up rules. Do not invent a replacement football result or import real post-draft performance. A real signing involving a Jacksonville-controlled player cannot supersede the branch contract. Retirements retain the special league-wide rule on their real dates.
6. For each Jacksonville **undrafted signing** after its actual acceptance, remove the player from the relevant real club only in accordance with the UDFA rails; if he really signed with Jacksonville, that does not create a second player. A declined proposal does not remove him from that club. **Acceptance (settled by the lead):** one private market draw per pursued player against the contract he really signed, from a method frozen before the draft (rails rule 6; [league rails method](../career/2014/League/personnel/method.md), section 4). A player whose real club was the real Jaguars has no rival offer (rails rule 4) and decides under the uncontested rule, as the [February and March design](re_signing_and_free_agency.md) restates it for 2015 (section 3: a player with no rival real contract when Jacksonville's offer can first be signed decides at the 0.90 ceiling). The 2014 calls were resolved by judgment, a one-off that is not rerun.

**Information partition:** An internal as-of-N historical availability check may use real overall pick metadata **solely as the mandated eligibility/availability constraint**. It is forbidden to display a future real pick, true later NFL destination, or later prospect achievements in a previously issued coaching briefing or as a reason Stone/Caldwell preferred him. A prospective 2015 illustrative pick example must not choose names from the completed real 2015 Jaguars class. **No league sequence is built:** the branch keeps no slot-by-slot league selection order, and a prospect whose real pick comes before N can belong to a club whose branch slot comes after N. At Jacksonville's pick N, each named target whose real selection came before N is shown as already taken, with his real club. The real overall number used for the test stays in the data area, because on a reader page it would read as Jacksonville's own pick number. No page names "the preceding selection" or times other clubs' picks.

**Hard collision:** the real-Jaguars k-th pick pairing uses ordinal rather than overall slot. When branch picks and historical pick positions differ, two affected source picks may compete for one player or one club's depth slot, especially when an actual Jacksonville choice was originally a real Jaguar. The 2014 executed draft demonstrates both self-pairing and duplicate-control cases. The 2015 pairing is stored as one structured record in the data area, and the League pairing page is built from it; the 2014 page stays as written. The build must preflight the complete selection permutation, preserve uniqueness by stable person identity and legal rights, and issue an explicit, noninvented unplaced outcome when the frozen rules have no valid destination. An irreconcilable source mismatch is a blocker for the affected pick, not license for ad hoc compensating players. This method's fidelity limits should remain visible to the implementer, never masked as realistic talent scouting. Reader pages show only each move (date, club, player, move) and link the League pairing page; the method and the counterpart logic stay here and in the data area.

## G. Three pages, authoritative owners and derived views

**Ownership rule: one owner per fact.** Each fact below has one owner; every page is built from it, and no page carries a second editable copy.

| Fact/result | Sole owner | How the draft pages use it |
|---|---|---|
| The simulated year, date, employed job and ongoing authority | current-state/job and canonical event owners | Read-only, dynamically checked on issue and execution. |
| Draft dates, round starts, pick clocks, eligibility and award dates, the year's draft rules | `career/<year>/Calendar.md` with its library source register, and the year's rules entry in the library | Show only verified and then-known dates; this design and the pages link them. |
| Original asset, holder, condition, draft tie, final number | dated trade owner + `data/<year>/Draft/pick_ownership.json` (the 2015 register reading the 2014 register's 2015 entries as sources, section D) | Render table from canonical ownership; no manually maintained second list. |
| Real-eligibility and scouting source dates | year-specific library prospect evidence and as-of records | Only visible when allowed. |
| Full Caldwell-approved scouting board | exactly one prospect/board evidence owner under the draft department's data store | The Scouting Department Report cites it; Stone's page does not overwrite it. |
| Scouting Department Report editions | the shared phase-brief issue history (issue dates, digests), the one the February and March briefs use, keyed by phase | The current page is the latest edition; every earlier edition is kept as issued beside it, with its date in its name, as the Game Week Briefing's are. |
| Stone's priorities, written QB projection, fallbacks and undrafted priorities | `My_Draft_Recommendations.md` | Editable until checked and applied before Round 1, then frozen as the record of his recommendations (the 2014 pre-draft amendments were edits of this kind). The brief proposes; this page decides. The undrafted list lives only here. |
| Stone's answers during the draft | the Draft folder's `My_Responses.md`, each answer tied to its pick or event: an exhausted pick, a trade call, a franchise-quarterback consultation, a change to his undrafted priorities | Linked from the result it fed. |
| Draft-day offer or refused trade | `Team_Operations/Trades`: dated negotiated process + **one standalone closed Trade Result** | Insert in the Scouting Department Report; Draft Room Results links only. `EVENTS.trade_talks` is reused. |
| One Jacksonville pick, including its decision date and selection rights | `Draft/Selections`: **one dated page in the draft-selection form of the shared event result**, with its event-record line | `Draft_Room_Results.md` indexes it; no outcome born on rerender. |
| Other-club real-pick displacement/pairing | one structured pairing record in the data area; `League/personnel/draft_pairing.md` is built from it | Reader pages show the move and link the League page; summary only, not alternate editable roster. |
| Drafted-rookie contract or refused/withdrawn negotiation | `Team_Operations/Free_Agency`: its own result in the free-agent result form, and the player's contract record | Linked from the selection page and Draft Room Results. Not inferred from a selection. No copy of terms as a separate draft-only master contract. |
| Undrafted contact, signed/declined/failed pursuit | `Team_Operations/Free_Agency`: **one result per pursued player** in the free-agent result form | Short result index in Draft Room Results; no bonus/slot booked for failure. |
| Depth chart and role after lawful onboarding | Stone's depth decisions; the depth data own the depth chart | A first job may be proposed after a selection; actual assignment requires separate valid decision and eligibility. |
| Rookie-minicamp direction | the Offseason Program Brief, reissued after the draft | Draft Room Results points to it. |
| Report across the draft | `Draft_Room_Results.md`, derived from individual owners | Football narrative and links; no unique transaction/selection facts authored here. |
| Chronological annual index | generated `career/<year>/Record.md` | One line and link per canonical concluded event, from each result's event-record line, not second output. |
| The 2014 draft records | `career/2014/Draft/` and the 2014 pairing page, as written (rebuild rule 1) | Precedent only; never migrated into per-selection pages. |

For the coach-facing three-page workflow, keep exact registry naming. In addition create a **separate, dated individual Markdown result for each concluded Jacksonville selection** (the selection result template gives its reading layout) and for every actual draft-related concluded event. This strengthens the 2014 pattern in `draftees.md`, which grouped selection results by days but is closed history and must not be rewritten. A single selection's dated standalone result is its one public authoritative outcome; any retained `draftees.md` page for 2015 may be a generated linked roster/index, not another independently editable result. A truly completed rejected trade **still receives its own output**, even if Caldwell bought no pick.

Individual selection pages live in the registered `Draft` owner's `Selections` folder, at a collision-proof path resolved from the season folder map. A displayed title is `Draft Selection: [name]`, not an ID. A file path may include date + original asset and stable selection identity; internal IDs and cross-file keys remain in metadata/data, never in coach prose. Player contracts and undrafted pursuits live in `Team_Operations/Free_Agency`, the signings owner of the [rebuild plan](rebuild_plan.md); a selection page links its contract when later signed. Use existing event-insert results rather than duplicating trade and contract outcomes inside Draft.

## H. Execution lifecycle, stops and revision semantics

**Currently implemented?** No. `runtime/decisions.py` registers the `draft` row without the implemented flag; its newer `EVENTS` registry covers cross-phase trade talks and other inserts. `runtime/decision_queue.py` permits `personnel_recommendation` but its listed `BLOCK_KINDS` are game inputs/close, call-sheet parts and season staging/opening, not a draft-selection gate. `runtime/draft_order.py`, `scripts/render_draft_order.py`, `scripts/resolve_compensatory_picks.py` and the present `Draft` 2014 pages were built for the **completed 2014** cycle. Do not pretend a draft stop is enforced merely by putting it in markdown or a generic queue item.

Proposed state progression, not an executed state change:

1. **PREPARATION:** college scouting gathers available evidence; current 2014 career continues untouched. No 2015 board/recommendation is inferred from this package.
2. **SEASON_FINISHED:** final branch 2014 regular season/postseason, 2015 league year and validated 2015 pick order/ownership determine assets. Other work can proceed while a lawful unresolved asset is held.
3. **REPORT_ISSUED:** the Scouting Department Report has one scheduled issue, after the last calendar event before the draft that can move a pick: for 2015, April 29, after the restricted free agents' matching period closes ([2015 calendar](../career/2015/Calendar.md); the April 24 offer-sheet deadline is not the last such date). It carries its source/time cutoff and the event inserts directly under its header. Stone's answer on My Draft Recommendations is due before 8 p.m. ET April 30. A read/open never advances time.
4. **RECOMMENDATIONS_PENDING / ADOPTED:** preserve Stone's original wording, normalize authorized alternatives behind the scenes and validate against current eligibility/assets. The page can be edited until it is checked and applied before Round 1; then it is frozen as the record of his recommendations. Silence cannot select a player, consent to a trade or waive the right of franchise-QB consultation.
5. **DRAFT_OPEN:** league clock and earlier ordinary selections advance in date/order. A new edition of the report is issued only under the one reissue rule ([event inserts](event_inserts.md), section A, item 6): a new event needs Stone's answer, a dated finding materially changes a choice still pending, or an answer falls due before the next scheduled issue. Earlier editions are kept. Inform Stone only of material, actionable updates, not each irrelevant rumor.
6. **JAX_ON_CLOCK:** fetch actual owned asset; check unresolved condition and current source cutoff; check named priority, real-N historical filter, already-selected persons and authorized fallback. Then, under the rule settled by the lead from the 2014 precedent ([2014 board](../career/2014/Draft/player_draft_board.md): a selection stops for Stone's choice when no precise fallback is authorized):
   - If an available, eligible player Stone named is there, in his order, Caldwell selects him unless a recorded medical, eligibility or contract restriction says otherwise (section B).
   - If Stone named players at this pick and all are gone with no further instruction, the selection **stops for Stone**, unless his page tells Caldwell to use his own board there. The question is an ACTION REQUIRED insert in a reissued report, answered on the Draft folder's My Responses page. Never auto-select a “best player available” for him.
   - If Stone named no one at this pick, Caldwell selects by his frozen board method (section B).
   - A stop holds that pick and Jacksonville's later picks only. Other clubs' real selections are applied club by club and do not wait. No NFL clock time runs during a stop, and pages show the era's clock limits only; never claim that the historical NFL draft paused, and never resolve a pick by a fictional expiry.
7. **PICK_RESOLVED:** commit once, on its exact date/time, with selected player and rights, pairing/deduplication result and dated individual `Draft Selection` page. No contract or 53-man role is implied. Move to next slot only after records are consistent.
8. **DRAFT_CLOSED:** after the legitimate final league selection, unlock lawful UDFA recruiting. Each pursued player's answer comes from the market draw of section F. Record individual offers/answers separately and promptly. Do not assume recruitment finishes when the clock reads May 2 if a real negotiation remains open.
9. **REPORT_PUBLISHED:** build the full `Draft_Room_Results.md` from committed owners and link every pick, concluded trade approach and concluded UDFA pursuit. Unresolved matters remain open and explicitly dated.
10. **HANDOFF:** notify the rookie-minicamp and OTA workflows of actual acquired rights/contract/eligibility through the Offseason Program Brief reissued after the draft; never fabricate an April workout, rookie physical or minicamp participation.

**The stop rule and the clock (settled).** The upload left open whether the draft pauses between picks for Stone or runs on a real clock with a frozen standing priority. The lead settled it as above, applying the user's October 20, 2026 rule that only an answer due before the event it holds stops the clock: Stone's ordered preferences and fallbacks are frozen before the draft; a pick stops for him only when his named list there is exhausted and his page gives no further instruction; Caldwell keeps his independent final call and his own frozen board where Stone named no one. The display may show authentic NFL clock limits without representing elapsed real-world seconds.

**Independent event flow:** `EVENTS.trade_talks` may create an insert in the Scouting Department Report, answered on the Draft folder's `My_Responses.md`. A real concluded negotiation creates its own dated Trade Result in the trade department even if rejected; a late offer cannot rewrite a frozen already-exercised selection. How a partner club answers a Jacksonville-initiated draft-day pick trade comes from a method frozen before the draft (in 2014 the Jimmy Johnson chart priced the March trades, [trade sheets](../career/2014/Team_Operations/Trades/supporting_records/trade_sheets_2014-03-24.md)). The same applies to a concluded contract offer or UDFA recruitment attempt. No software module should manufacture approaches or infer a closed negotiation from an unchanged priority list. Do not reopen completed January/February/March templates merely to route a draft event.

**Immutable issue history:** each issued briefing's content, issue timestamp and evidence cutoff are immutable. A later college result, accepted trade, medical communication or drafted player becoming unavailable creates a new edition when the one reissue rule calls for it, not an overwrite. The active view points to the latest valid edition; links back to the particular edition that elicited Stone's answer. Draft board versions are separate from later result narration. Preserve the same event ID across insert, response, actor resolution and standalone result; metadata belongs in data or invisible authorized event markers only.

## I. Validation implementation contracts

Implement read-only checks plus action precondition checks, run on **a staging clone of the repository at implementation time**. They must not alter historical 2014 output, generate a pick, invoke private outcome draws or advance the active state. For each individual pick/trade/UDFA event, validate:

- Unique stable event identity and one official outcome; a report rebuild cannot rerun, change or duplicate it.
- Exact authorized owner, original asset, current holder, pick number, selection date/order, eligible prospect and market-specific constraints.
- Separate rights acquisition, player contract execution, salary-cap entry, draft-pairing effect, roster membership and on-field role authority. Reject phantom guaranteed starters or guaranteed improvement.
- Clear as-of source and candidate provenance; public prospect information and private club information are distinguished and time-gated.
- No real future Jaguars outcomes, the real Jaguars' 2015 slot, future prospect NFL statistics or hindsight commentary entering an ex-ante report.
- All closed incidents have their own dated Markdown result; the phase result and annual record link them. Rejected/declined/no-deal events change no cap or personnel rights.
- Role-specific clean pages: no identifiers, file paths, script instructions, internal score/seed/weights or metacommentary in the three public pages or individual selection result. Implementation/source files may show them.
- No authored player grade outside the existing narrow player-sheet exception; no invented staff dialogue, medical diagnosis or invented scouting cutup.

### Proposed unit and end-to-end regression suite (72 tests)

**Clock, source timing and era law**

1. At the October 5, 2014 snapshot the 2015 dates and Chicago site announced October 2 appear as calendar information, while an imagined 2015 prospect grade does not.
2. The registry's draft row reads "Late April or May" in both `runtime/decisions.py` and the rebuild plan's phase table, and a 2015 page takes the draft's dates from the 2015 calendar: it begins April 30, not generic May.
3. 2015 first round begins at the sourced 8 p.m. ET start if that information is allowed by issue date.
4. Round 1/2/3/4/5/6/7 normal pick clocks are respectively 10/7/5/5/5/5/4 minutes, and the round 7 four-minute clock appears only on a page issued after its public date.
5. A 2015 compensatory selection receives a four-minute clock, shown only after its public date.
6. A 2015 compensatory selection cannot be included in a completed trade.
7. The January 15 early-entry deadline and January 19 league eligibility announcement are distinct events with separate gates.
8. January 19 eligibility list is unavailable in an October 5, 2014 briefing.
9. A combine invitation never materializes test results before February 17-23, 2015 workouts.
10. A prospect pro-day, campus interview or private visit is unavailable before its evidenced occurrence and cannot be inferred from a general report.
11. A player is not draft-eligible solely because a public mock draft mentions him.
12. A post-draft performance/injury fact is neither loaded into an earlier scouting report nor used by the historical availability filter as ability evidence.
13. A modern 2020s rookie-contract option guarantee or modern trade rule is not substituted for the 2011 terms applicable to the 2015 class.

**Assets, standings, compensatory and legal order**

14. The October 5 2014 initial 2015 JAX asset inventory lists exactly its nine held picks (own second, own third, Miami third, Houston fourth, Arizona fourth, own fifth, own sixth, own seventh, Seattle seventh), the four own originals marked held with no transfer recorded pending the audit, and the known moved/debt assets, without invented overall numbers.
15. Jacksonville's original first and fourth cannot appear as owned in the initial 2015 register.
16. Miami third, Houston fourth, Arizona fourth and Seattle seventh each resolve to their own original-club assets, not duplicate Jacksonville originals.
17. Washington's returned Jacksonville original second is not simultaneously owned by Washington.
18. The 2016 fifth and 2017 seventh are future debts and cannot become 2015 active picks.
19. A 2014 Week 5 standings snapshot never supplies a completed 2014 regular-season draft order.
20. The 2015 order is derived only from the closed 2014 games (regular records, elimination groups and strength of schedule) and the recorded ties; the test asserts that derivation, never that the result differs from a real club's slot.
21. Tied-club order follows the correct year-specific tiebreak and rotation; a tie that survives them is drawn by the private service under the frozen protocol, and an unresolved draw holds its picks instead of falling back to alphabetical club order.
22. Pick ownership is keyed by draft year, round and original club; original asset movement does not transfer the wrong rotated selection.
23. Every 2015 ordinary asset is unique and has a verifiable holder or a specifically flagged unresolved restriction; an absent file does not mean Jacksonville owns it.
24. A 2015 trade contingent on a branch performance/roster event does not execute unless the condition is actually met and authoritatively closed.
25. The final order is not labelled complete until forfeitures, transfer chains and league-wide compensatory offsets are resolved.
26. The real March 23, 2015 compensatory recipient list is not imported; the value-points method restated before March 23 with frozen 2014 league-year inputs drives the career's recipients.
27. The 2014 compensatory script's 2013 inputs, 2014 slot mapping and 2014 dates do not leak into a 2015 award calculation.
28. A selected asset cannot be transferred twice, spent under an open hold or exercised after transfer to another club.
29. Generating the 2015 draft order and related owners leaves the closed 2014 order, picks, annual entries and compensatory record byte-identical.

**Stone and Caldwell authority, recommendations and live decisions**

30. A genuine Stone recommendation cannot execute a Jacksonville draft pick or sign a player.
31. The user may decline to list a late-round preference; the system may not fill it with a fabricated ranked list.
32. An authorized first-choice-and-fallback sequence can be followed only if the current player/asset/era conditions match.
33. If every player Stone named at a pick is gone and his page gives no further instruction, the pick stops for his answer unless his page tells Caldwell to use his own board there; the next unranked comparison is never an automatic choice.
34. A Caldwell selection different from Stone's preference is possible, recorded by its actual independent authority and not rewritten into prior unanimity.
35. Each of row 3a's four matters (the first-round pick on a quarterback, premium draft capital traded for one, a major multiyear commitment to one as the intended starter, a major disposition of the starting quarterback) requires Stone's genuine dated written projection and a meeting before Caldwell acts, but grants no veto; a first-round quarterback opens it whatever role he is meant for.
36. A quarterback taken after round 1, with no premium capital traded, does not open the consultation; a scouting discussion alone opens nothing.
37. Stone cannot medical-clear a prospect, execute a trade, set contract terms or transfer a draft pick by filling his coaching page.
38. A standing instruction remains in force where valid; the draft workflow does not demand reauthorization of offensive/defensive callers or other unrelated standing choices.
39. An issued/edited plan is not final merely because its Markdown file was opened; exact material decisions are validated and dated before application.
40. A new briefing after a trade, pick or medical update preserves the bytes, date and visible contents of its earlier issued versions, and an informational event alone issues no new edition.
41. A filled verbose recommendation and an equivalent brief one produce equivalent normalized football instructions, without rewarding prose confidence or favoritism.
42. A stop records no NFL clock time; pages show only the era's clock limits, and the document renderer generates no fictional timeout or expiry.

**Historical personnel rails and collision safety**

43. A Jacksonville selection at branch overall N of a prospect who was selected at real pick below N is unavailable under the standing exception.
44. A prospect taken in the real draft at N or later, or who went undrafted, passes that specific filter only if all other eligibility/control checks pass.
45. The third party cannot receive the same rights that Jacksonville acquired; original real-club slot is properly vacated under the permitted rails.
46. Jacksonville's k-th executed pick pairs with the real Jaguars' k-th selection, not the k-th round, real overall pick N, or a player occupying the same position.
47. A self-pairing (2014 Telvin Smith precedent) creates no duplicate player or forced real Jaguars import.
48. An already-Jacksonville-controlled counterpart cannot be gifted to a second club to satisfy the pairing.
49. A missing real counterpart becomes explicitly unplaced rather than a manufactured substitute or trade.
50. The 31 other clubs' actual historical **player selection** rails do not import their real 2014 season records, playoff seeds, coaches or club-owned original pick order.
51. The future real 2015 draft list may be consulted only as the hidden exception's availability/identity rule and never displayed as advance scouting evidence.
52. Rebuilding later Week 1 depth charts after verified rail availability neither duplicates player rights nor erases the dated Jacksonville contract owner.

**Pick results, offers, rookie contracts and handoff**

53. Two Jacksonville picks concluded on the same day produce **two** standalone dated pick results in `Draft/Selections`; the main Draft Room Results only links them.
54. One rejected draft-day trade and one accepted trade produce two separate dated Trade Result documents under the trade owner, including the rejection.
55. Two independent declined undrafted offers and one accepted one, each decided by one market draw against the contract the player really signed, yield three separate completed-pursuit results in `Team_Operations/Free_Agency`, not a combined paragraph; only the accepted signing changes control after execution.
56. A real offer answered by a counteroffer still open has a process record, not a falsely final result.
57. A target on Stone's UDFA watch list does not generate an actual outreach, bid or signing.
58. A drafted player obtains negotiating rights on selection, not a fabricated completed four-year contract and cap amount.
59. First-round fifth-year option exists under 2011 rules but is not counted as already exercised and is not guaranteed under later-era clauses.
60. A signed rookie's actual 2015 cap/rookie allocation reconciles to the financial owner exactly once; declined/unsigned players create no phantom cap charge.
61. A May 2 draft selection cannot retrospectively attend the April 20 start of Jacksonville's Phase One.
62. Rookie-minicamp participant and medical access is checked on the appropriate May date, not inferred from the draft, signed offer or future camp result.
63. Every concluded single-event report has a unique event ID, correct date, canonical owner and annual index link; rerender does not duplicate a completed draft or draw.
64. The draft workflow passes clean-page validation and season-layout resolution, preserves the October 5, 2014 Week 5 closure and leaves Week 6 unplayed when run in design/read-only mode.

**Added by the process check**

65. My Draft Recommendations can be edited until it is checked and applied before the first round; afterwards a change to it is refused, and an answer during the draft is written on the Draft folder's My Responses page, tied to its pick or event.
66. A stopped pick holds only that pick and Jacksonville's later picks; other clubs' real selections still apply; with "use your own board" written for the pick, Caldwell selects by his frozen board method without a stop.
67. At a pick where an available, eligible player Stone named first is there, Caldwell selects him, unless a recorded medical, eligibility or contract restriction is stated on the selection page.
68. No reader page names "the preceding selection", shows another club's real overall pick number or lists the league's selections in branch order; a named target whose real pick came before N shows as already taken, with his real club.
69. Reader draft pages show other clubs' moves as date, club, player and move only, link the League pairing page, and contain no explanation of the pairing method.
70. No issued page names a scout as an author unless he is a party in the job record, and the staff names on an issued page match the coach records and the job record at its issue date.
71. While the Offseason Program Brief and the Scouting Department Report are both active, each event appears once, on its own phase's brief: pick trades and prospect, selection, rookie-contract and undrafted matters on the report; practice, roster, medical and staff matters on the Offseason Program Brief.
72. A Stone not employed by Jacksonville receives no Jacksonville draft brief or My page; in another job he receives that job's version with its scope; with no Jacksonville My page, Caldwell drafts on his frozen board method.

### Acceptance gate

No implementation is accepted solely because the three pages render. A staged test must show a full 2015 draft built from **synthetic test-season** facts with two controlled Jacksonville picks, one exhausted fallback that stops for Stone, one pick where Stone named no one, a compensatory asset rejected for trade, one legitimate accepted pick trade, one failed pick trade, a self-pairing and one unsigned rookie, each with correct legal rights and its own event output. Then verify the original repo's 2014 frozen draft pages and Week 5 game output are unchanged; the new season's 2015 real player outcomes remain unplayed. Before any real close, the operator must separately verify actual 2015 picks, the restated comp method, College Draft eligibility, authority, event output uniqueness and exact dates. Run repository validation and appropriate tests in the eventual implementation PR, not now.

## J. Known blockers and decisions not to guess

1. **No registered 2015 draft runner or released 2015 order.** The 2014 scripts and game records are year-specific. Generalize only after parity tests; season 2015's actual standings are future.
2. **2015 full original-pick ownership audit absent.** The nine Jacksonville holdings are established (four of them own originals with no transfer recorded), but the current 2014 data register cannot prove every original 2015 asset, claim, conditional clause and future trade. Must reconcile before certifying slots.
3. **2015 compensatory calculation lacks frozen inputs.** The method is settled (section D); its 2014 league-year inputs and frozen 2014 season honours are not built. The historical NFL recipients are expressly not the career answer. The 2014 calculation is an era-calibrated branch approximation, not the NFL's secret algorithm. Do not silently choose new recipients.
4. **No complete date-gated 2015 scouting sourcebook/eligible-pool registry.** A separate library task builds it (section E). Do not generate a final class at October 5, 2014 or conflate the scouting staff's private knowledge with internet draft rankings.
5. **Draft stops not implemented.** The rule is settled (section H); the decision-queue block that holds a stopped pick, Caldwell's frozen board method and their tests are not built.
6. **Collision control in historical pairing.** The approved ordinal-real-Jaguars swap is deliberately artificial and can fail to define a valid new club/player slot. Preserve explicit unplaced outcomes rather than invent compensation.
7. **Multiple distinct dated result pages not yet wired.** The existing event registry handles named inserts, but a draft event-per-selection transaction with immutable result/page indexing is additional implementation work.
8. **Time-gating of source announcements and information at draft preparation.** Known in October 2014: draft date/site, branch football/ownership. Not known: 2015 final player board, underclassman list, complete 2014 finish, comp awards or eventual draft destination. A finished realistic April report must await its own genuine date.
9. **Parallel April workflows.** April offseason-program dates overlap the first draft day; new rookies cannot be silently included in existing Phase One or retroactively credited with teaching. The routing rule is settled (section A); the event inserts design still assumes one active brief and is updated in the build (section L).
10. **Repo movement during research.** The main branch advanced between earlier inspection and this package; use the commit above as a review reference and reread source owners at implementation. No current GitHub test execution or merger is represented here.

## K. Key source and owner references

- Original **2011 NFL/NFLPA CBA**, Articles 6-7, original publication: https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf (printed pp. 17-33; PDF pages 32-48 approximately; use article headings, not a modern paraphrase).
- **NFL, Oct 2, 2014**, Chicago 2015 dates/site: https://www.nfl.com/news/2015-nfl-draft-to-be-held-in-chicago-0ap3000000404486 .
- **NFL, Jan 19, 2015**, 74 special eligibility applicants plus ten eligible graduates: https://www.nfl.com/news/list-of-underclassmen-granted-eligibility-for-2015-nfl-draft-0ap3000000460791 .
- **NFL, March 23, 2015**, the compensatory announcement at the Annual Meeting. Cited by outlet and date only: its web address names recipients, so it goes into the two-pass 2015 rules entry when the build creates it (section L). No library record of it exists yet.
- **Contemporary April 29, 2015 draft times**: https://www.wafb.com/story/28930500/2015-nfl-draft-key-dates-and-times/ and https://www.canalstreetchronicles.com/2015/4/30/8518837/nfl-draft-2015-time-tv-schedule-draft-order-history .
- **Acme Packing Company, April 27, 2015**, the round 7 and compensatory four-minute clocks: https://www.acmepackingcompany.com/nfl-draft-2015-packers/2015/4/27/8504825/2015-nfl-draft-pick-timing-changes-for-seventh-round-compensatory-picks (read through a search extract on October 23, 2026; the page could not be retrieved directly), with the Raiders' [2015 draft facts and figures](https://www.raiders.com/news/2015-nfl-draft-facts-and-figures-15142674) (publication date not verified) giving the same limits. The league's own first public date is unverified and is fixed in the two-pass calendar entry.
- **NFL later official legal clarification** on comp picks, allowed to trade beginning 2017: https://www.nfl.com/news/compensatory-picks-to-be-tradable-beginning-in-2017-0ap3000000592818 (used to verify 2015 rule, not as a 2015 in-story announcement).
- **Jaguars May 7, 2014** Caldwell scouting/contingency practice: https://www.jaguars.com/news/jaguars-com-live-caldwell-ready-for-draft-12966178 . **Jaguars May 5, 2014** pre-draft board preparation: https://www.jaguars.com/news/what-we-learned-setting-the-tone-12951777 (date and board content confirmed October 23, 2026). These report **real-period practice**, not the simulation's Caldwell decisions.
- Repository owners: `career/2014/Draft/` (closed historical precedent), `career/2014/League/personnel/draft_pairing.md` (approved swap edge cases), `career/2014/Team_Operations/Trades/` (dated future-pick transfers), `data/2014/Draft/pick_ownership.json` (2015 pick transfers to date), `state/current_job.json` (row 3a and the parties), `data/people/coaches/` (staff names), `runtime/decisions.py` (`REGISTRY` and `EVENTS`), `runtime/draft_order.py`, `scripts/render_draft_order.py`, `scripts/resolve_compensatory_picks.py`, `runtime/decision_queue.py`, `runtime/events.py`, `scripts/render_annual_record.py`, and `runtime/clean_pages.py`.

## L. What the build must add

The process check of October 20, 2026 found these needs. Each fix belongs in a file outside this design and is made in the build step named; process documents and code are not edited here. The AGENTS.md lines that need 2015 wording are flagged for the build, and the 2013 methods apply meanwhile.

| Need | Files | Step |
|---|---|---|
| Relabel the draft row's When "Late April or May", in one commit, because `tests/test_game_week_pages.py` requires the plan table to equal the registry; add a build-record line to the rebuild plan's change log | `runtime/decisions.py` (draft row), `docs/rebuild_plan.md` (phase table) | 7 |
| Folder-map places for `Draft/Selections` and the Draft folder's `My_Responses.md`; the registry's owner entry for signings in `Team_Operations/Free_Agency`, with undrafted-pursuit and rookie-contract result kinds | `runtime/season_layout.py`, `runtime/decisions.py` | 7 |
| A draft order built per season from the closed games, with 2014 byte-identical; the 2015 order needs the closed 2014 postseason and its slots file, and a two-pass 2015 draft-order rules entry like 2014's (Document 2 §12: verify exact order, compensatory rules and tiebreaks) | `runtime/draft_order.py`, `scripts/render_draft_order.py`, library | 6 (postseason slots) and 7 |
| The tie protocol: a private-service draw frozen beforehand | `runtime/draft_order.py`, the Draft data area | 7 |
| 2015 compensatory inputs from the 2014 league year, frozen 2014 season honours (`season_honours.py` is built for 2013 only), and the restated value-points method committed before March 23, 2015 and resolved on that date | `scripts/resolve_compensatory_picks.py`, `data/2015/Draft/compensatory/` | 6 (honours) and 7 |
| A 224-asset 2015 ownership audit, covering the open Flynn 2015 condition, Jacksonville's four own originals and the rule for other clubs' real pick trades (section D) | `data/2015/Draft/pick_ownership.json` | 7 |
| The current-state draft capital lists nine 2015 picks, not five, with the Document 4 and 5 pointers moved together and the private snapshot advanced after merge | `state/05_Current_Season_State.md` section 5, `state/04_Roster_and_Staff_Register.md` draft capital | Handled separately from this design |
| A decision-queue block kind for one draft pick (season and overall number) that `personnel_recommendation` and `quarterback_consultation` may hold | `runtime/decision_queue.py` | 7 |
| Scouting Department Report editions in the shared phase-brief issue history (issue dates, digests), keyed by phase, with the earlier copies kept beside the current page | the Draft data area and the Draft folder | 7 |
| A parser and check for My Draft Recommendations: owned picks, eligible pool, exact names, ordered fallbacks, "use your own board", normalized so wording length does not matter (test 41), and refusal of an edit after it is applied (test 65) | `runtime`, `scripts` | 7 |
| Builders for the per-selection, per-pursuit and per-contract result pages, each with its event-record line, the Draft Room Results index built from them and the Record.md lines | `scripts`, `runtime/events.py` | 7 |
| A structured pairing record with a collision preflight (self-pairing, already-controlled player, no partner, unique identity), the League page built from it, applied to other clubs at the 2015 Week 1 rails build | `data/2015/League/personnel/` | 7 and the pre-Week-1 build |
| Methods frozen before the draft: the undrafted market draw with the uncontested rule (section F), Caldwell's board method (section B), rookie pricing by slot reconstruction (section C) and a partner club's answer to a Jacksonville pick-trade proposal (section H) | `career/2015/League/personnel/`, `data/2015/Draft/`, the Trades owner | 7 |
| A two-pass 2015 compensatory-rules entry holding the two web addresses the designs cite by outlet and date only, because each names a real later outcome: the NFL's March 23, 2015 compensatory announcement and the NFL's 2017 compensatory-awards announcement that confirms the 2017 tradability change; the entry records both, with the December 2015 rule-change article, and no recipient from either feeds the career | library | 6 or 7, before March 23, 2015 |
| The 2015 rookie minimum-salary schedule and slot inputs, from the two-pass 2015 financial-rules entry the March design already requires | library, financial inputs | 7 |
| The 2015 draft-class research: information gates (modelled on `library/2014_draft_information_gates.md`, starting from the research file's 2015 visibility table, which the library then owns), eligible-pool registry, combine results and dated prospect evidence, pre-selection data only (the AGENTS.md library task) | `library/2015_*` | A library task before the report's scheduled issue |
| 2015 calendar rows after two passes: the October 2, 2014 announcement and venue, January 15 and 19, March 23 (the release's address held in the compensatory rules entry below), the round starts and clocks with the late-April date of the clock change | `career/2015/Calendar.md`, `library/2015_historical_calendar.md` | 6 |
| At each signing: a permanent player record, roster record row, contract inputs, a verified birth date, an entry assessment (the two-assessments rule), player pages and the development cohort | `data/people/players`, the roster record, financial inputs | 7 |
| Player-state entries for 2015 draftees and undrafted signings before any 2015 game (Document 7 §6.1; the builders cover 2014 only) | library data, the private service binding | Before 2015 Week 1 |
| Two briefs may carry inserts at once when phases overlap, each event once on its own phase's brief; the event inserts design assumes one active brief | `docs/event_inserts.md` | 7 |
| Text outside this design names the three Draft pages, the selection results and their owners: the AGENTS.md "Run the [year] offseason cycle" task (it names `career/[year]/offseason/draft/player_draft_board.md`; flagged, the 2013 method applying meanwhile); the season milestones rows for the early offseason (the memo no longer carries the scouting board), "Before the draft" and "April 30 to May 2" (its "By hand" becomes the built pairing record); the update workflow's "Draft selection or rookie contract" row, split so a selection result goes in `Draft/Selections` and each contract and undrafted pursuit in `Team_Operations/Free_Agency`; the season structure's `Draft` row (undrafted signings move to `Team_Operations/Free_Agency`); the template catalog's draft row, with the note that from 2015 the draft is not run through the offseason output's section 5; and a 2015 Draft README that links this design (the 2014 README stays as written) | `AGENTS.md`, `docs/season_cycle_milestones.md`, `docs/update_workflow.md`, `docs/season_structure.md`, `foundation/templates/README.md`, `career/2015/Draft/README.md` | 7 |
| A synthetic test-season fixture for the acceptance gate | `tests` | 7 |
