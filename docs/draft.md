# NFL Draft workflow: implementation and validation specification

**Status:** Uploaded by the user on October 20, 2026 and adopted; built in step 7 of the [rebuild plan](rebuild_plan.md). The templates are in [foundation/templates/draft/](../foundation/templates/draft/), the worked example is [docs/examples/draft_jacksonville.md](examples/draft_jacksonville.md) and the research register and repository assessment are in [docs/draft_research.md](draft_research.md).

As uploaded: **Status:** Research and design contract. No file in `Alex-Oss222/football-career-sim` is changed by this package. No draft decision, trade, contract or simulated game is resolved. The tests below are specifications and were not executed against a checked-out repository.  
**Repository inspected:** `Alex-Oss222/football-career-sim`, `main`, with tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` observed on 20 October 2026. The repository changed while this research was underway; revalidate against the then-current tree before implementation.  
**Current career:** Sunday 5 October 2014, after Jacksonville's Week 5 game; Week 6 remains unplayed. Do not back-port the new three-page draft process to the already completed 2014 draft.

## NFL Draft: researched three-page workflow package

**Repository:** `Alex-Oss222/football-career-sim`  
**Research snapshot:** `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24`, observed October 20, 2026  
**Scope:** the NFL Draft workflow in the established six-workflow redesign sequence, intended for the first future applicable draft and reusable with season-specific law and source checks. The actual 2015 draft begins April 30, not generically in May.  
**Current simulated career:** after Jacksonville's October 5, 2014 Week 5 game, Week 6 unplayed.  
**Status:** **Research and design only.** Nothing in this ZIP has been installed in GitHub, no league or Jacksonville selection has been simulated, and no future player, contract, roster assignment or staff outcome has been created.

### The three required coach-facing pages

| Order | Artifact | What the reader sees |
|---|---|---|
| 1 | [01 Scouting Department Report](../foundation/templates/draft/scouting_department_report_template.md) | A genuine college scouting briefing, actual pick inventory, roster football questions, dated eligible prospects, named uncertainty and permitted live action inserts. |
| 2 | [02 My Draft Recommendations](../foundation/templates/draft/my_draft_recommendations_template.md) | A natural head-coach memo to David Caldwell, with the user's selected priorities, individual first jobs, preferred prospects, precise fallbacks and conditions; Caldwell retains final picks and trades. |
| 3 | [03 Draft Room Results](../foundation/templates/draft/draft_room_results_template.md) | A read-through of selections made and their football implications, linked to **separate dated pick, negotiation, contract and undrafted-pursuit results**, including failures. |

### Supporting implementation and example files

| File | Function |
|---|---|
| [04 Individual Selection Result](../foundation/templates/draft/selection_result_template.md) | A reference for one dated result per completed selection; never a combined result. |
| [05 Implementation and Validation Specification](#a-fixed-scope-and-first-principles) | Detailed requirements for years, historical rails, roster/authority separation, draft clock, source gates, per-event outcomes and **64 proposed regression tests**. |
| [06 Worked Jacksonville Example](examples/draft_jacksonville.md) | Three-page reorganization of **already completed 2014 facts**, including No. 205, plus October 5, 2014 prospective 2015 five-asset position. No future 2015 outcomes. |
| [07 Research and Source Register](draft_research.md#2014-2015-nfl-draft-research-law-contemporaneous-process-and-information-gates) | Original 2011 CBA, 2014-15 dated NFL sources, 2015 draft timetable, contemporary club scouting procedures and date-information boundaries. |
| [08 Repository Assessment and Blockers](draft_research.md#nfl-draft-redesign-repository-assessment-conflicts-and-implementation-blockers) | What works in the repository, missing implementation, precise risks and non-negotiable integration order. |

### Non-negotiable operating rules

- Do not change Alex Stone's executed contract, adopted philosophy or current job authority. David Caldwell makes binding draft, acquisition, trade and player-contract decisions. Stone chooses only his own football recommendations and documented franchise-QB consultation rights.
- Never invent a 2015 prospect grade, final 2014 record, 2015 Jacksonville draft slot, college-scout tape report, staff conversation, independent medical clearance or a future NFL player performance. A later real draft selection is never a scouting fact at an earlier in-story time.
- The user-approved 2014-onward historical league personnel exception applies to the other 31 clubs' real selections; Jacksonville's own pick ownership/order come from its career. Jacksonville can choose only a prospect whose real overall pick is at or after its live branch choice N, or who was undrafted; the real Jaguars k-th pick pairs with Jacksonville's k-th exercised selection. Enforce self-pairing, absent partners and unique player control without inventing compensation.
- **One closed consequential event must get one own dated readable result.** Nine distinct concluded draft selections mean nine distinct pick results, not a nine-line summary alone. Likewise, two rejected negotiations mean two separate failed outcomes. The main report links; it never replaces.
- The draft, undrafted recruiting, rookie-contract negotiations and rookie minicamp are separate legal and football events. An acquired right is not a signed player; a signed contract is not a medical clearance; a medical clearance is not a starting job.
- Keep technical event IDs, data paths, source digests, script names and validation terminology out of live coach-facing pages. They belong in technical records and this documentation.

### Six-workflow design sequence

| Work item | Design status after this package |
|---|---|
| 1. April Offseason Program | Completed in the preceding design package; GitHub integration separately pending. |
| 2. NFL Draft | **This complete research/template design package; GitHub implementation pending.** |
| 3. May-June OTAs and Minicamp | Next, not yet redesigned in this sequence. |
| 4. Training Camp Position Battles | Not yet redesigned in this sequence. |
| 5. Every Preseason Game | Not yet redesigned in this sequence. |
| 6. Final Roster Cuts | Not yet redesigned in this sequence. |

No scripts in this archive are intended to run against the active career. The tests specified here require implementation in a future authorized PR and must not be described as passing now.

## A. Fixed scope and first principles

Three permanent coach-facing draft page titles already exist in `runtime/decisions.py`:

| Registered workflow | Staff report | Stone's editable response | Published phase result |
|---|---|---|---|
| `draft` | `Scouting_Department_Report.md` | `My_Draft_Recommendations.md` | `Draft_Room_Results.md` |

Their logical destination is `SeasonPaths(draft_year).record('draft')`, resolving to `career/<draft_year>/Draft/` on the 2014+ season layout. The current registry says `when="May"`; the 2015 draft begins **Thursday, April 30**, and ends May 2. Correct the registry's display window to an actual calendar-derived span without changing its identity, file names or folder. No other three-page workflow needs to be reopened or redescribed.

Do not treat this as one disposable prompt called “simulate the draft.” It has dated preparation, potentially revised briefings, Stone's user-owned recommendation, individual league and Jacksonville picks, real offers if they arise, rights acquired, and distinct post-draft negotiations and unsigned players. Caldwell makes selections and conducts trades and contracts. The draft occurs alongside the April offseason program, whose Phase One may still be in progress April 30. A pick neither retroactively adds a rookie to April workouts nor decides the later rookie minicamp or OTA outcome.

**Scope boundary:** the selection meeting and its immediately opened undrafted recruiting work belong in Draft. A scouting report is not a hidden full 2015 result set. The future 2015 draft can be designed now; it cannot be opened as a completed phase or populated from the real Jaguars' 2015 finish. A different employing club or coaching role must rebind the relevant local football recommendations and authority before a report is issued; this design does not force a Jaguars briefing after a coaching departure.

## B. Governing canon and authority

Read the current copies of `AGENTS.md`, `docs/rebuild_plan.md`, `docs/season_structure.md`, `docs/event_inserts.md`, `foundation/01_Project_Instructions.md`, `foundation/02_League_Era_and_Sourcebook.md` (especially §4.3a/§4.5 and §12), `foundation/03_Head_Coach_Organization_and_Authority_Canon.md`, `foundation/06_Event_Records_and_Handoff.md`, `state/current_job.json`, `state/decision_queue.json` and the current career and draft records.

- **Stone, head coach:** football assessment, role projection, which attributes and assignments matter, coaching costs, prioritized recommendations and his dated responses. He controls the depth chart and how the eventual rookies are coached; he does not choose the selected player, execute a draft-pick trade or sign a prospect.
- **Caldwell, GM:** final college scouting/board administration, choice of a player at every Jacksonville draft selection, trade offers and acceptances, rookie contract negotiations/execution, undrafted recruiting and personnel acquisition. A Stone target is not a pick, and a club press report is not Caldwell's decision in this career.
- **Leading quarterback matters:** the established row 3a written football projection and consultation before Caldwell's franchise-level commitment. No concurrence/veto was agreed. Only trigger the formal consultation when a genuine leading-quarterback acquisition/draft commitment is being considered, not for every quarterback scout card.
- **Medical professionals:** medical assessments, restrictions, participation and clearance. Stone can assess a football role within communicated limitations. A press injury summary is not an authorized team physical or private medical finding.
- **Other clubs:** choose or trade based on the user-authorized historical personnel rails where those rails apply, but the branch's standings, playoff outcomes, existing pick transactions and coaching carousel are not copied from reality.

Continuing rules: four-year fully guaranteed Stone head-coach contract accepted January 15, 2013, no 2014 extension/authority change; offensive calls and defensive calls currently Stone's, Crennel prepares/transmits the defense, Westhoff controls the designated special-teams calls, and Tice coordinates offensive work. These do **not** require another April approval. Neither a successful draft nor a poor game changes these terms. Stone's philosophy favors evidence-backed assignments, personnel flexibility, protection details, Dagger/Mesh/play-action and coherent front/coverage teaching; it is not permission to predetermine that the draft fixes those things.

## C. Chronology and exact era rules

| Fact / constraint | Controlling 2015 value | Timing and information rule |
|---|---|---|
| Draft | April 30 to May 2; Auditorium Theatre, Roosevelt University, Chicago | NFL announcement **October 2, 2014**: legitimately knowable October 5. NFL announced Thursday R1, Friday R2-3, Saturday R4-7. |
| Daily starts | April 30 8 p.m. ET; May 1 7 p.m. ET; May 2 noon ET | Contemporary April 29/30 draft notes support the detailed start times. Do not assert an earlier public release of the precise hours without a dated notice. |
| Selection clock | R1 10 minutes; R2 7; R3-6 5; R7 4; compensatory choices in R3-7 4 | Contemporary 2015 draft notes, not today's draft clock. Actual team-pick deadline is a live NFL order/clock fact, not the top-of-the-hour event start. |
| Draft format | Seven rounds, normal 32 original clubs' choices per round, plus up to 32 additional compensatory selections | 2011 CBA Article 6 §2 and §10. Actual 2015 league had 32 compensatory choices; branch recipients are not imported. Any forfeiture, supplemental obligation or other league adjustment must be verified. |
| Underclassmen | January 15, 2015 application deadline, January 19 NFL special-eligibility announcement | Announcement identified 74 approved applicants and ten eligible graduates with college eligibility remaining. No full list in October 2014. |
| Combine | February 17-23, 2015, Indianapolis | Invitation is not testing; results open on the day actually measured/performed. Private club interview/medical claims require a real club event. |
| Compensatory picks | 2015 award announced Monday March 23; 32 actual choices to 14 real-world clubs | Do **not** import recipient list into the divergent career. Recompute/resolve from branch-eligible 2014 free-agent movements by a method frozen before awards. 2015 comp picks were nontradeable. |
| First-round rookie contract | Four years with fifth-year club option | CBA Article 7 §3 and §7, not a completed fifth year or executed compensation schedule. |
| Rounds 2-7 rookie contract | Four-year fixed term | Draft rights, contract signature and rookie cap charge are separate dated events. |
| Undrafted rookie contracts | Three-year fixed term | No signing until the eligible principal draft has completed under Article 6 §11; a recruiting list does not create a player contract. |
| After-draft camp | Jacksonville historical May 8-10 rookie minicamp | An announced slot alone does not establish an eligible player's presence, signed contract, medical clearance, practice or teaching result. |

### Source timing categories

Maintain for each evidence claim `event_at`, `announced_at` or `published_at`, `known_to_club_at` if privately and genuinely established, `source`, `source_scope` and `retrieved_at`. A document published later may corroborate that a rule existed earlier but cannot be used as a fictional in-world press release. Prospect video may be recorded during the college season but a later analytical report is not already authored at the game's date.

October 5, 2014 provides **only** the NFL's October 2, 2014 announced 2015 date/site, then-current branch roster and 2014 five-game football evidence, carried contracts and closed transfers. It does not provide January eligibility awards, combine times, final scouting analyses, 2014 NFL season finish, 2015 draft order, 2015 staff employment outcome, comp awards or real 2015 Jaguars draft choices. The publication date of the club's 2015 scheduled rookie minicamp was not recovered in the 2015 calendar research; it is a historical scheduling reference until a legitimate club-held or dated source establishes when Stone knew it.

## D. Live pick ownership and numbering

**Source owners:** original pick identities and dated transfers in the 2015 draft register under `data/2015/Draft/`; each trade retains its one distinct dated source in its contract/Trades owner; `career/2015/Draft/draft_order.md` is generated from reconciled records. Do not copy an older year's snapshot and relabel it. Resolve this directory from `SeasonPaths`, not handwritten year-folder literals inside non-folder-map modules.

**Verified holdings at the 2014 Week 5 date** from `state/05_Current_Season_State.md` §5 and the individual trade owners:

| Asset | October 5, 2014 disposition |
|---|---|
| Jacksonville's original 2015 first | **Owed to Arizona** (March 20, 2014 Nwaneri and picks trade) |
| Jacksonville's original 2015 second | **Held by Jacksonville**, reacquired from Washington March 31 |
| Miami's original 2015 third | **Held by Jacksonville** |
| Houston's original 2015 fourth | **Held by Jacksonville** |
| Arizona's original 2015 fourth | **Held by Jacksonville**, acquired April 7 Allen trade |
| Jacksonville's original 2015 fourth | **Owed to Arizona** |
| Seattle's original 2015 seventh | **Held by Jacksonville**, acquired May 12 Rackley trade |
| Jacksonville's 2016 fifth | Future debt to Arizona; **not** a 2015 selection |
| Jacksonville's 2017 seventh | Future debt to Miami; **not** a 2015 selection |

Thus **five 2015 ordinary pick assets are held** at this date, not their eventual overall slot numbers and not a promise of five selections on draft day. Do not silently infer the missing original fifth/sixth, claims and all-club audit from this summary. The 2015 audit must enumerate **all original seven-round assets for all 32 clubs** and determine final holders, restrictions, duplicate transfers and pending conditions, preserving all recorded branch deals and any historical inherited transactions that still legitimately apply. Unknown does not mean free and transferable.

Compute original-club slot from *the simulated 2014 regular-season records and playoff eliminations*, then apply the correct lower-strength-of-schedule tiebreak, necessary division/conference steps or recorded coin flip and subsequent round rotation. Join ownership by `(draft_year, round, original_club)`, never a previously guessed overall number. Honor all legal forfeitures if documented. The 2014 `runtime/draft_order.py` and `scripts/render_draft_order.py` are year/receipt-specific, including hardcoded 2014 coin-flip expectations; extracting reusable season logic must preserve the completed 2014 order byte-for-byte and must not resolve a 2015 tiebreak using the old flip.

Compensatory awards cannot be resolved merely from nominally available free agents or 2015 real recipients. The 2014 `scripts/resolve_compensatory_picks.py` and its frozen method apply **only** to 2014, using 2013 free agency, 2013 games/honours and a 2014 club order. A 2015 resolver needs 2014 branch inputs, audited free-agency classes/contracts, 2014 branch season data, a separately chosen ex-ante formula with acknowledged unpublished NFL weights and its own signed-off output. If it is impossible to establish the recipient/round method, **hold the affected final pick numbering and execution** rather than silently copying reality or awarding default zero compensatory choices. Show provisional round slots without claiming an exact global overall number.

The 2015 real Jaguars' No. 3 choice belongs to historical context **only** and is forbidden as a Jacksonville draft slot in this career. A reported trade of a comp selection in 2015 must fail validation even if later league rules would permit it.

## E. Player evidence, college eligibility and board rules

Create `library/2015_draft_information_gates.md` and a source-controlled 2015 eligible-player registry when the information reaches its legitimate dates. The 2014 versions are **precedents**, not valid 2015 prospect data. Distinguish:

1. **College eligibility:** three seasons after the entering high-school class/graduation for special entry, the player's own declaration/league approval, or ordinary senior status, and relevant exceptions from Article 6. Keep uncertain eligibility out of executable selections.
2. **Evidence date:** completed 2014 college plays and honors become available when played/announced; all-star practice and game observations by their specific days; combine invitation and each measurement separately; pro days, permitted private workouts and player visits only if genuinely held/recorded.
3. **Film finding:** opponent, context, alignment and job, technique or read, observed action and limitation. College film does not prove NFL position mastery or a quantified development boost.
4. **Club assessment:** scouting department view and identifiable coaching contribution, with dissent preserved if an actual person expressed it. Do not create a fake scout interview, doctor clearance, background fault, leadership grade or testing result.
5. **Plan-to-use:** initially plausible NFL job, personnel grouping, coaching responsibility, learning cost and comparison with already-controlled players. No automatic starting job or playbook unlock based on pick round.
6. **Draft price:** named existing asset or value band, and a valid ordered fallback or explicit stop. A round-price judgement is not a numerical “talent score.” Never turn a table of comparative names into a preauthorized selection priority.

If only an old public scouting sheet exists, the scouting department may explain a narrow football inference from it; never label it an internal evaluation that no Jacksonville employee performed. User-authored Stone preference is a recorded preference, not proof of a scout's grade. No post-selection statistics, rookie-season injuries, NFL success or later personality commentary may influence a prospect decision.

The substantive prospect board remains Caldwell's scouting source, with Stone's **own** response on `My_Draft_Recommendations.md`; the two may disagree. The later `Draft_Room_Results.md` is not a new master board and must not rewrite the pre-draft evaluation after the result becomes known.

## F. Historical-league-rails exception, exact application

The rules in `AGENTS.md`, Document 2 §4.5, and `career/2014/League/personnel/method.md` §6 govern the 2014-and-later branch. The 2015 work must retain all of them, not import the real Jaguars' 2015 signing or draft class:

1. Other 31 clubs' **player selections** follow their actual corresponding draft selections, subject to actual branch ownership/control corrections and the approved pairing method. Their real draft **order** does not replace the branch's actual order, playoff results or acquired-pick ledger.
2. Jacksonville's prospect at simulated overall pick `N` passes the *special, user-authorized historical filter* only if the prospect was selected at real pick `N` or later, or went undrafted. Check ordinary NFL draft eligibility and no prior branch assignment too. The original NFL year and prospect identity must match.
3. Jacksonville's **k-th exercised selection** pairs with the real Jaguars' **k-th real selection**. That real player goes to the club that really drafted Jacksonville's chosen prospect, or if the prospect went undrafted to the club where he really signed. If no valid partner exists the player is unplaced. The method does not create an automatic fallback club.
4. Do not move a Jacksonville-controlled player away simply because the real Jaguars' k-th name appears on another line. Treat self-pairing and already-controlled players as explicit exceptions, as occurred with Telvin Smith in 2014. Never duplicate an acquired player or a Week 1 depth slot.
5. Reconcile other clubs' affected Week 1 depth charts **when their dated source material is allowed**; remove the Jacksonville-controlled prospect from his original club, apply permitted counterpart relocation and next-man-up rules. Do not invent a replacement football result or import real post-draft performance. A real signing involving a Jacksonville-controlled player cannot supersede the branch contract. Retirements retain the special league-wide rule on their real dates.
6. For each Jacksonville **undrafted signing** after its actual acceptance, remove the player from the relevant real club only in accordance with the UDFA rails; if he really signed with Jacksonville, that does not create a second player. A declined proposal does not remove him from that club.

**Information partition:** An internal as-of-N historical availability check may use real overall pick metadata **solely as the mandated eligibility/availability constraint**. It is forbidden to display a future real pick, true later NFL destination, or later prospect achievements in a previously issued coaching briefing or as a reason Stone/Caldwell preferred him. A prospective 2015 illustrative pick example must not choose names from the completed real 2015 Jaguars class. During actual draft play, record that another club's pick became known only as its proper event resolved.

**Hard collision:** the real-Jaguars k-th pick pairing uses ordinal rather than overall slot. When branch picks and historical pick positions differ, two affected source picks may compete for one player or one club's depth slot, especially when an actual Jacksonville choice was originally a real Jaguar. The 2014 executed draft demonstrates both self-pairing and duplicate-control cases. The 2015 build must preflight the complete selection permutation, preserve uniqueness by stable person identity and legal rights, and issue an explicit, noninvented unplaced outcome when the frozen rules have no valid destination. An irreconcilable source mismatch is a blocker for the affected pick, not license for ad hoc compensating players. This method's fidelity limits should remain visible to the implementer, never masked as realistic talent scouting.

## G. Three pages, authoritative owners and derived views

| Fact/result | Sole owner | How the draft pages use it |
|---|---|---|
| The simulated year, date, employed job and ongoing authority | current-state/job and canonical event owners | Read-only, dynamically checked on issue and execution. |
| Year-specific selection calendar | `career/<year>/Calendar.md` with sourced history in library | Show only verified and then-known dates. |
| 2015 original asset, holder, condition, draft tie, final number | dated trade owner + `data/<year>/Draft/pick_ownership.json` or evolved generic structured owner | Render table from canonical ownership; no manually maintained second list. |
| Real-eligibility and scouting source dates | year-specific library prospect evidence and as-of records | Only visible when allowed. |
| Full Caldwell-approved scouting board | exactly one prospect/board evidence owner under the draft department's data store | Scouting Report cites; Stone's page does not overwrite. |
| Stone's authored priorities, written QB projection, dated fallback | recorded user decision with immutable original prose | `My_Draft_Recommendations.md` is the user-facing authoritative decision, with versioned amendments. |
| Draft-day offer or refused trade | `Team_Operations/Trades` dated negotiated process + **one standalone closed event result** | Prominent insert if relevant; draft result links only. Existing `EVENTS.trade_talks` and shared `My_Responses.md` may be reused. |
| One Jacksonville pick, including its decision date and selection rights | year-specific selection event in draft structured records, with **one dated readable pick-result file** | `Draft_Room_Results.md` indexes it; no outcome born on rerender. |
| Other-club real-pick displacement/pairing | `League/personnel/draft_pairing.md` built from the sole structured pairing owner | Summary only, not alternate editable roster. |
| Drafted-rookie contract or refused/withdrawn negotiation | respective financial/contract owner + distinct dated outcome | Not inferred from a selection. No copy of terms as a separate draft-only master contract. |
| Undrafted contact, signed/declined/failed pursuit | dated personnel/recruiting owner, with **one distinct closed result per player/pursuit** | Short result index; no bonus/slot booked for failure. |
| Coaching assignment after lawful onboarding | Stone's depth-chart/phase-plan owner | May be proposed after a selection; actual assignment requires separate valid decision and eligibility. |
| Report across the draft | `Draft_Room_Results.md`, derived from individual owners | Football narrative and links; no unique transaction/selection facts authored here. |
| Chronological annual index | generated `career/<year>/Record.md` | One line and link per canonical concluded event, not second output. |

For the coach-facing three-page workflow, keep exact registry naming. In addition create a **separate, dated individual Markdown result for each concluded Jacksonville selection** (the reference file supplied in this package gives its reading layout) and for every actual draft-related concluded event. This strengthens the 2014 pattern in `draftees.md`, which grouped selection results by days but is closed history and must not be rewritten. A single selection's dated standalone result is its one public authoritative outcome; any retained `draftees.md` page for 2015 may be a generated linked roster/index, not another independently editable result. A truly completed rejected trade **still receives its own output**, even if Caldwell bought no pick.

For simplicity and clarity, place individual selection reports within the registered `Draft` owner at a collision-proof path resolved from the season folder map (e.g., logical draft selection results, under a `Selections` child folder). A displayed title is `Draft Selection: [name]`, not an ID. A file path may include date + original asset and stable selection identity; internal IDs and cross-file keys remain in metadata/data, never in coach prose. Put player contracts in the real contract owner; a selection page links them when later signed. Use existing event-insert results rather than duplicating trade and contract outcomes inside Draft.

## H. Execution lifecycle, pause and revision semantics

**Currently implemented?** No. `runtime/decisions.py` registers the `draft` row without the implemented flag; its newer `EVENTS` registry covers cross-phase trade talks and other inserts. `runtime/decision_queue.py` permits `personnel_recommendation` but its listed `BLOCK_KINDS` are game inputs/close, call-sheet parts and season staging/opening, not a draft-selection gate. `runtime/draft_order.py`, `scripts/render_draft_order.py`, `scripts/resolve_compensatory_picks.py` and the present `Draft` 2014 pages were built for the **completed 2014** cycle. Do not pretend a draft stop is enforced merely by putting it in markdown or a generic queue item.

Proposed state progression, not an executed state change:

1. **PREPARATION:** college scouting gathers available evidence; current 2014 career continues untouched. No 2015 board/recommendation is inferred from this package.
2. **SEASON_FINISHED:** final branch 2014 regular season/postseason, 2015 league year and validated 2015 pick order/ownership determine assets. Other work can proceed while a lawful unresolved asset is held.
3. **REPORT_ISSUED:** issue an immutable scouting report with source/time cutoff; include actual shared event inserts at top. A read/open never advances time.
4. **RECOMMENDATIONS_PENDING / ADOPTED:** preserve Stone's original wording, normalize authorized alternatives behind the scenes and validate against current eligibility/assets. Silence cannot select a player, consent to a trade or waive the right of franchise-QB consultation.
5. **DRAFT_OPEN:** league clock and earlier ordinary selections advance in date/order. When a relevant factual change occurs, generate a new immutable report version while keeping earlier one. Inform Stone only of material, actionable updates, not each irrelevant rumor.
6. **JAX_ON_CLOCK:** fetch actual owned asset; check unresolved condition and current source cutoff; check named priority, real-N historical filter, already-selected persons and authorized fallback. If the approved player is available and Caldwell independently chooses him, the selection may close. **If no authorized fallback exists, stop for Stone's response if his football recommendation is requested; never auto-select a “best player available” for him. Caldwell retains final authority and can make his own independent selection by a concrete, frozen method, which must not be invented in response to a deadline.** If the NFL pick clock expires and the era rules apply, record that consequence rather than silently extending time.
7. **PICK_RESOLVED:** commit once, on its exact date/time, with selected player and rights, pairing/deduplication result and dated individual `Draft Selection` output. No contract or 53-man role is implied. Move to next slot only after records are consistent.
8. **DRAFT_CLOSED:** after the legitimate final league selection, unlock lawful UDFA recruiting. Record individual offers/answers separately and promptly. Do not assume recruitment finishes when the clock reads May 2 if a real negotiation remains open.
9. **REPORT_PUBLISHED:** build the full `Draft_Room_Results.md` from committed owners and link every pick, concluded trade approach and concluded UDFA pursuit. Unresolved matters remain open and explicitly dated.
10. **HANDOFF:** notify the rookie-minicamp and OTA workflows of actual acquired rights/contract/eligibility, never fabricate an April workout, rookie physical or minicamp participation.

**Critical gap in the draft-clock design:** the repo does not expose a proven draft-room clock/timeout procedure or a valid way for Caldwell to act independently at every expiry. It would be dishonest to assert that a response can be requested, received and processed within seven minutes by a free-form asynchronous Markdown exchange. Before implementation, specify whether the draft is paused *between* picks for deliberate Stone input, or fully real-time with a published standing priority and exceptional live pause. The realistic default is **freeze Stone's ordered preferences and fallback cases before the draft; intervene only when a material new issue breaks the authorized instruction**, while Caldwell retains his independent final call. The display may show authentic NFL clock limits without falsely representing elapsed real-world seconds. Never resolve an expired live pick using a fictional off-clock selection or claim that the historical NFL draft paused for the user.

**Independent event flow:** `EVENTS.trade_talks` may create an insert and use the existing shared `My_Responses.md`. A real concluded negotiation creates its own dated trade result in the trade department even if rejected; a late offer cannot rewrite a frozen already-exercised selection. The same applies to a concluded contract offer or UDFA recruitment attempt. No software module should manufacture approaches or infer a closed negotiation from an unchanged priority list. Do not reopen completed January/February/March templates merely to route a draft event.

**Immutable issue history:** each issued briefing's content, issue timestamp and evidence cutoff are immutable. A later college result, accepted trade, medical communication or drafted player becoming unavailable creates a new issue, not an overwrite. The active view points to the latest valid issue; links back to the particular issue that elicited Stone's answer. Draft board versions are separate from later result narration. Preserve the same event ID across insert, response, actor resolution and standalone result; metadata belongs in data or invisible authorized event markers only.

## I. Validation implementation contracts

Implement read-only checks plus action precondition checks, run on **a staging clone of the repository at implementation time**. They must not alter historical 2014 output, generate a pick, invoke private outcome draws or advance the active state. For each individual pick/trade/UDFA event, validate:

- Unique stable event identity and one official outcome; a report rebuild cannot rerun, change or duplicate it.
- Exact authorized owner, original asset, current holder, pick number, selection date/order, eligible prospect and market-specific constraints.
- Separate rights acquisition, player contract execution, salary-cap entry, draft-pairing effect, roster membership and on-field role authority. Reject phantom guaranteed starters or guaranteed improvement.
- Clear as-of source and candidate provenance; public prospect information and private club information are distinguished and time-gated.
- No real future Jaguars outcomes, 2015 actual Jaguars pick order, future prospect NFL statistics or hindsight commentary entering an ex-ante report.
- All closed incidents have their own dated Markdown result; the phase result and annual record link them. Rejected/declined/no-deal events change no cap or personnel rights.
- Role-specific clean pages: no identifiers, file paths, script instructions, internal score/seed/weights or metacommentary in the three public pages or individual selection result. Implementation/source files may show them.
- No authored player grade outside the existing narrow player-sheet exception; no invented staff dialogue, medical diagnosis or invented scouting cutup.

### Proposed unit and end-to-end regression suite (64 tests)

**Clock, source timing and era law**

1. At the October 5, 2014 snapshot the 2015 dates and Chicago site announced October 2 appear as calendar information, while an imagined 2015 prospect grade does not.
2. The 2015 `draft.when` rendering begins April 30, not generic May.
3. 2015 first round begins at the sourced 8 p.m. ET start if that information is allowed by issue date.
4. Round 1/2/3/4/5/6/7 normal pick clocks are respectively 10/7/5/5/5/5/4 minutes.
5. A 2015 compensatory selection receives a four-minute clock.
6. A 2015 compensatory selection cannot be included in a completed trade.
7. The January 15 early-entry deadline and January 19 league eligibility announcement are distinct events with separate gates.
8. January 19 eligibility list is unavailable in an October 5, 2014 briefing.
9. A combine invitation never materializes test results before February 17-23, 2015 workouts.
10. A prospect pro-day, campus interview or private visit is unavailable before its evidenced occurrence and cannot be inferred from a general report.
11. A player is not draft-eligible solely because a public mock draft mentions him.
12. A post-draft performance/injury fact is neither loaded into an earlier scouting report nor used by the historical availability filter as ability evidence.
13. A modern 2020s rookie-contract option guarantee or modern trade rule is not substituted for the 2011 terms applicable to the 2015 class.

**Assets, standings, compensatory and legal order**

14. The October 5 2014 initial 2015 JAX asset inventory lists exactly its known five held picks and known moved/debt assets, without invented overall numbers.
15. Jacksonville's original first and fourth cannot appear as owned in the initial 2015 register.
16. Miami third, Houston fourth, Arizona fourth and Seattle seventh each resolve to their own original-club assets, not duplicate Jacksonville originals.
17. Washington's returned Jacksonville original second is not simultaneously owned by Washington.
18. The 2016 fifth and 2017 seventh are future debts and cannot become 2015 active picks.
19. A 2014 Week 5 standings snapshot never supplies a completed 2014 regular-season draft order.
20. Simulated 2014 elimination groups, regular records and strength of schedule set 2015 pick slots; the actual Jaguars No. 3 slot is not imported.
21. Tied-club order follows the correct year-specific tiebreak and rotation, and an unresolved draw holds its picks instead of falling back to alphabetical club order.
22. Pick ownership is keyed by draft year, round and original club; original asset movement does not transfer the wrong rotated selection.
23. Every 2015 ordinary asset is unique and has a verifiable holder or a specifically flagged unresolved restriction; an absent file does not mean Jacksonville owns it.
24. A 2015 trade contingent on a branch performance/roster event does not execute unless the condition is actually met and authoritatively closed.
25. The final order is not labelled complete until forfeitures, transfer chains and league-wide compensatory offsets are resolved.
26. The real March 23, 2015 32-pick comp recipient table is not automatically imported; a 2014 branch-based method/frozen inputs drive the career's recipients.
27. The 2014 compensatory script's 2013 inputs, 2014 slot mapping and method do not leak into a 2015 award calculation.
28. A selected asset cannot be transferred twice, spent under an open hold or exercised after transfer to another club.
29. Generating the 2015 draft order and related owners leaves the closed 2014 order, picks, annual entries and compensatory record byte-identical.

**Stone and Caldwell authority, recommendations and live decisions**

30. A genuine Stone recommendation cannot execute a Jacksonville draft pick or sign a player.
31. The user may decline to list a late-round preference; the system may not fill it with a fabricated ranked list.
32. An authorized first-choice-and-fallback sequence can be followed only if the current player/asset/era conditions match.
33. If named choices are gone and no ranked fallback exists, ask Stone for the remaining football recommendation when his input is required; never use the next unranked comparison as an automatic choice.
34. A Caldwell selection different from Stone's preference is possible, recorded by its actual independent authority and not rewritten into prior unanimity.
35. A future leading-quarterback commitment requires Stone's genuine dated written projection and a consultation before Caldwell acts, but grants no veto.
36. A nonfranchise backup-QB scouting discussion does not automatically trigger the major-QB consultation gate.
37. Stone cannot medical-clear a prospect, execute a trade, set contract terms or transfer a draft pick by filling his coaching page.
38. A standing instruction remains in force where valid; the draft workflow does not demand reauthorization of offensive/defensive callers or other unrelated standing choices.
39. An issued/edited plan is not final merely because its Markdown file was opened; exact material decisions are validated and dated before application.
40. A new briefing after a trade, pick or medical update preserves the bytes, date and visible contents of its earlier issued versions.
41. A filled verbose recommendation and an equivalent brief one produce equivalent normalized football instructions, without rewarding prose confidence or favoritism.
42. A genuine pick-clock expiry is handled under a specifically approved time model; no fictional real-time timeouts are generated by the document renderer.

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

53. Two Jacksonville picks concluded on the same day produce **two** standalone dated pick results; the main Draft Room Results only links them.
54. One rejected draft-day trade and one accepted trade produce two separate dated Trade Result documents under the trade owner, including the rejection.
55. Two independent declined undrafted offers and one accepted one yield three separate completed-pursuit results, not a combined paragraph; only the accepted signing changes control after execution.
56. A real offer answered by a counteroffer still open has a process record, not a falsely final result.
57. A target on Stone's UDFA watch list does not generate an actual outreach, bid or signing.
58. A drafted player obtains negotiating rights on selection, not a fabricated completed four-year contract and cap amount.
59. First-round fifth-year option exists under 2011 rules but is not counted as already exercised and is not guaranteed under later-era clauses.
60. A signed rookie's actual 2015 cap/rookie allocation reconciles to the financial owner exactly once; declined/unsigned players create no phantom cap charge.
61. A May 2 draft selection cannot retrospectively attend the April 20 start of Jacksonville's Phase One.
62. Rookie-minicamp participant and medical access is checked on the appropriate May date, not inferred from the draft, signed offer or future camp result.
63. Every concluded single-event report has a unique event ID, correct date, canonical owner and annual index link; rerender does not duplicate a completed draft or draw.
64. The draft workflow passes clean-page validation and season-layout resolution, preserves the October 5, 2014 Week 5 closure and leaves Week 6 unplayed when run in design/read-only mode.

### Acceptance gate

No implementation is accepted solely because the three pages render. A staged test must show a full 2015 draft built from **synthetic test-season** facts with two controlled Jacksonville picks, one exhausted fallback, a compensatory asset rejected for trade, one legitimate accepted pick trade, one failed pick trade, a self-pairing and one unsigned rookie, each with correct legal rights and its own event output. Then verify the original repo's 2014 frozen draft pages and Week 5 game output are unchanged; the new season's 2015 real player outcomes remain unplayed. Before any real close, the operator must separately verify actual 2015 picks, approved comp method, College Draft eligibility, authority, event output uniqueness and exact dates. Run repository validation and appropriate tests in the eventual implementation PR, not now.

## J. Known blockers and decisions not to guess

1. **No registered 2015 draft runner or released 2015 order/comp method.** The 2014 scripts and receipts are year-specific. Generalize only after parity tests; season 2015's actual standings are future.
2. **2015 full original-pick ownership audit absent.** The five known Jacksonville holdings are established, but the current 2014 data register cannot prove every original 2015 asset, claim, conditional clause and future trade. Must reconcile before certifying slots.
3. **2015 compensatory calculation lacks valid frozen inputs and method.** The historical NFL recipients are expressly not the career answer. The 2014 calculation is an era-calibrated branch approximation, not the NFL's secret algorithm. Do not silently choose new recipients.
4. **No complete date-gated 2015 scouting sourcebook/eligible-pool registry.** Do not generate a final class at October 5, 2014 or conflate the scouting staff's private knowledge with internet draft rankings.
5. **NFL pick-clock handling not designed end-to-end.** Stop semantics under a seven- or four-minute clock, Caldwell's independent fallback and the limits of asynchronous coach input need a declared and testable operating protocol.
6. **Collision control in historical pairing.** The approved ordinal-real-Jaguars swap is deliberately artificial and can fail to define a valid new club/player slot. Preserve explicit unplaced outcomes rather than invent compensation.
7. **Multiple distinct dated result pages not yet wired.** The existing event registry handles named inserts, but a draft event-per-selection transaction with immutable result/page indexing is additional implementation work.
8. **Time-gating of source announcements and information at draft preparation.** Known in October 2014: draft date/site, branch football/ownership. Not known: 2015 final player board, underclassman list, complete 2014 finish, comp awards or eventual draft destination. A finished realistic April report must await its own genuine date.
9. **Parallel April workflows.** April offseason-program dates overlap the first draft day; new rookies cannot be silently included in existing Phase One or retroactively credited with teaching. The integration must preserve both owners and prospective participation rules.
10. **Repo movement during research.** The main branch advanced between earlier inspection and this package; use the SHA above as a review reference and reread source owners at implementation. No current GitHub test execution or merger is represented here.

## K. Key source and owner references

- Original **2011 NFL/NFLPA CBA**, Articles 6-7, original publication: https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf (printed pp. 17-33; PDF pages 32-48 approximately; use article headings, not a modern paraphrase).
- **NFL, Oct 2, 2014**, Chicago 2015 dates/site: https://www.nfl.com/news/2015-nfl-draft-to-be-held-in-chicago-0ap3000000404486 .
- **NFL, Jan 19, 2015**, 74 special eligibility applicants plus ten eligible graduates: https://www.nfl.com/news/list-of-underclassmen-granted-eligibility-for-2015-nfl-draft-0ap3000000460791 .
- **NFL, March 23, 2015**, 32 compensatory awards: https://www.nfl.com/news/chiefs-seahawks-broncos-lead-2015-compensatory-draft-picks-0ap3000000480988 .
- **Contemporary April 29, 2015 draft times**: https://www.wafb.com/story/28930500/2015-nfl-draft-key-dates-and-times/ and https://www.canalstreetchronicles.com/2015/4/30/8518837/nfl-draft-2015-time-tv-schedule-draft-order-history .
- **NFL later official legal clarification** on comp picks, allowed to trade beginning 2017: https://www.nfl.com/news/compensatory-picks-to-be-tradable-beginning-in-2017-0ap3000000592818 (used to verify 2015 rule, not as a 2015 in-story announcement).
- **Jaguars May 7, 2014** Caldwell scouting/contingency practice: https://www.jaguars.com/news/jaguars-com-live-caldwell-ready-for-draft-12966178 . **Jaguars May 5, 2014** pre-draft board preparation: https://www.jaguars.com/news/what-we-learned-setting-the-tone-12951777 . These report **real-period practice**, not the simulation's Caldwell decisions.
- Repository owners: `career/2014/Draft/` (closed historical precedent), `career/2014/League/personnel/draft_pairing.md` (approved swap edge cases), `career/2014/Team_Operations/Trades/` (dated future-pick transfers), `state/05_Current_Season_State.md` §5 (current 2015 pick holdings), `runtime/decisions.py` (`REGISTRY` and `EVENTS`), `runtime/draft_order.py`, `scripts/render_draft_order.py`, `scripts/resolve_compensatory_picks.py`, `runtime/decision_queue.py`, `runtime/events.py`, `scripts/render_annual_record.py`, and `runtime/clean_pages.py`.
