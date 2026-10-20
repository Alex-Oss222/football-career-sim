# January Staff Review: implementation specification and acceptance tests

**Design status:** Proposed. This document authorizes no changes to current repo, no 2014 season closure, no personnel event, and no hypothetical 2015 staff transaction. Preserves 2014 Weeks 1–5 as closed history.

## A. Why the workflow exists

The *Staff Status Report* presents information from football operations, the individual coach records, contracts, interviews and on-field evidence. Stone's *My Staff Decisions* supplies only his authorized actions. *Staff Moves* is an index/status account; every separate resolved coaching event has its own dated result. The status report is not an auto-written endorsement of incumbents and the result index is not a second contract owner.

**Scope:** Evaluating the current staff, deciding football assignments, pursuing retention/nonrenewal and confirming actual vacancies. The separate `Candidate Report → My Hire → Staff Hire` workflow owns a new hiring search after a real opening arises. Head-coach employment is settled first by Khan and Caldwell. This review is not the team season-review report, player assessments or the staff exit-interview transcript.

## B. Chronology and phase ownership

1. Close Jacksonville's actual final 2014 game. It may be December 28, 2014 if eliminated in the regular season or a later January/February 2015 playoff game if qualified. December 29 is not automatically Jacksonville's staff-review date.
2. The head-coach employment result establishes whether Stone is authorized to run this staff review. If dismissed, the Staff Status Report for **Stone** is not issued; a subsequent Jaguars staff plan belongs to the successor or authorized organization representative. Existing guarantees remain enforceable.
3. Issue review after sufficient records are available, or issue a limited preliminary report clearly dated before the final game and marked *not a final review*. A provisional self-scout may never order a coach released during a live playoff season without a valid separately authorized decision.
4. Store the 2014 season's exit interviews and team assessment under `career/2014/Season_Review/`, even when interviews happen in January 2015. The January 2015 staff retention/contract process belongs under the forthcoming **2015** `Early_Offseason` staff review/staff changes owner. The 2015 phase may contain preparatory event pages while the 2014 league season and handoff remain active. No automatic active-season switch or premature 2015 game release.
5. Re-check actual contract term, expiry day, competing interview permissions and budget on the day of each contemplated irreversible action. Current repo says nine assistant agreements run *through the 2014 season*, but their precise expiration **day** is unresolved. The repo's mention of a 'second Tuesday' rule is marked unverified. Do not convert either into January 1, January 13 or any other mandatory date. If an act requires the date, block **that act** and obtain the source.
6. If another club's formal request arrives at any legal point, the existing event-insert system issues a fresh immutable dated version of whichever relevant briefing Stone is entitled to receive. The original briefing remains as what he had read. Requests can also occur while Jacksonville remains in the postseason under the specific period's limits.
7. Close each independent outcome on its own simulated date, update its single authoritative coach/contract owner, create its unique separate reader-facing result and refresh the phase Staff Moves **index**. Never wait for the end of January to create a Tuesday result.

## C. Source-of-truth and responsibilities

| Issue | Owner/authority | Rule |
|---|---|---|
| Coach's existing terms | Individual coach's dated contract record under `data/people/coaches/`; relevant payroll record | No invented salary, guarantee, expiry or acceptance |
| Existing organization and duties | `state/current_job.json` delegation plus the 2014 Staff and coach records | Stone currently calls offense and defense, Tice prepares offense, Crennel prepares and relays defense, Westhoff calls kicking game. Evaluate what each actually owns |
| Staff selection/assignment | Stone under appointment Authority Map row 2 | Choices are user's; neither script nor ownership may manufacture them |
| Financial approval/execution | Caldwell / club administration under signed commitment and authority row 6 | Promised assistant budget exists but has **no verified numeric ceiling**. Scheduled assistant pay is not available headroom |
| An assistant's answer | That assistant or authorized representative | Pursue renewal ≠ signed extension; proposed separation ≠ coach's resignation |
| Head coach's employment | Khan and Caldwell | Stone must be employed with the club before controlling its subsequent staff decisions |
| Outside interview permission | Period-specific league anti-tampering rules, existing club permission authority and actual request | An offseason job vacancy is news, not an interview or offer to a particular assistant |
| Football evaluation | 2014 season/game reports, recorded practice, coach exit interviews | A unit statistic locates a question; it does not prove its coach taught correctly or incorrectly |
| Each concluded staff action | One canonical dated individual reader-facing event result, sourced from factual event owners | N separate resolved event actions → N separate result files and index links |

**Era-specific point:** For 2014-15, an assistant seeking a head-coach job was different from an assistant seeking another assistant/coordinator job. Moves from position coach to coordinator were not automatically protected; NFL recognition of bona fide coordinator promotions came later, in 2020. The Rooney Rule had not been expanded to coordinator searches in 2013, and the 2014-15 method must not enforce later requirements. Consult the documented 2013-14 period-specific interview windows and the separately sourced 2014-15 calendar.

**Current policy discrepancy to fix:** `data/2014/Early_Offseason/staff_changes/carousel_method.json` records Jacksonville's 2014 default to grant a head-coach interview request, grant a position-coach-to-coordinator request and refuse certain lateral requests. But the October 5, 2014 `state/current_job.json` standing-instructions list contains play-calling, inactives and game-management rules, **not a staff interview-permission instruction**. Do not claim the 2014 carousel's default automatically resolves new 2015 queue items through the current job's in-force standing-rule mechanism. Establish the user-authorized 2015 instruction and close semantics, or flag that a real permission choice must be made.

## D. Format and validation

### Staff Status Report

- Built or issued from current, date-appropriate coach terms, salary, authority, documented role work and actual season results. Displays entire staff **once** in its contract-control table.
- Separately highlights only coaches with real expiry issues, performance concerns, legitimate revised assignments or genuine outside contacts. No mandatory positive and negative entries per coach, number of paragraphs, interview quotes or constructed disagreement.
- Meaningful evidence points to actual film/practice/game/event entries and identifies what was assigned, what was observed and what is inferred. The report must not invent a missing protection diagnosis, staff conversation, coaching motive or future real-world hire.
- Contains 2015 review-specific action inserts at the top only when real events exist; no fake offers from other teams. The date of issue cannot precede a result it quotes.

### My Staff Decisions

- Exactly the fixed numbered headings from the template. Parse each explicit coach-specific action and verify current employment, control, contract status and stated contingencies.
- `No change` is valid for existing job assignments and contracts still in force. For an expiring contract it is insufficient to create a renewal; name pursue, do not pursue, lawful lapse or a pending fact.
- A shared action (e.g. 'Pursue renewal for all nine expiring assistants') may be compiled to the nine named individuals **only** when the explicit target set and conditions are unambiguous and shown to Stone for validation. It yields nine independent negotiation matters, never nine automatic signatures.
- Defer/awaiting information is meaningful and remains **open** with reason and applicable deadline; a blank field or silence never means approval, denial or waiver. If a deadline has real independent effect, resolve the clock according to the actual governing mechanism, not an invented agent assent.
- A changed caller or role is a separate authorized football action with dated update to `state/current_job.json` and relevant coach records. Its effects are not inferred from a renewal.
- No creation of separate user answer pages for every assistant. The one staff decision page can contain many responses, while separate event inserts use `My_Responses.md` where appropriate.

### Staff Moves and separate event outputs

- Render the phase's one Staff Moves index from immutable individual concluded events. Index can be revised as new events occur but cannot be primary employment evidence.
- Each finalized individual event creates exactly one reader-facing result, including a declined renewal, expired contract at a verified time, permitted/denied interview, release, resignation, material reassignment or actual hiring. A formal continuation with unchanged terms may also warrant a result if it was explicitly raised as a consequential decision. Unchanged coaches who never had a separate event do not receive fake 'retained' transaction files.
- A counteroffer, revised terms and meeting updates belonging to the **same open negotiation** are versioned process facts, not repeatedly final results. Separate distinct requests from two outside clubs each get their own outcomes.
- A vacancy resulting from an event leads to Candidate Report later; do not record a hired replacement here before an actual offer is accepted.
- A proposed contract creates no new coach employment entry, no scheduled salary, and no fake cap charge; on actual execution update coach record and the coaching payroll. Coaching salaries do **not** consume the player salary cap.

## E. Technical integration points

1. `runtime/decisions.py`: January staff registry entry already exists as `january_staff` at step 6, unimplemented; preserve its three page names and use `SeasonPaths` to route the 2015 Early_Offseason folder. Avoid duplicating the 2014 historical `Early_Offseason` folder.
2. `runtime/decision_queue.py`: extend or add a scoped `staff_review`, `assistant_retention`, `assistant_interview_permission` and `staff_role_change` event path, with per-item controlling authority, deadline and dependent block. Current `staff_appointment` is not a blanket implementation of all these choices. Never hold whole unrelated regular-season slates for a staff paperwork event.
3. Issue the Staff Status Report with source/date digest and immutable history. A change in coach availability, an external request or a submitted signed offer triggers a fresh dated issue, not a silent rewrite of a previously delivered report.
4. Parse `My_Staff_Decisions.md` into validated, dated instructions and any pending negotiations. Bind every decision to the issued brief version and source coach identity, never to an arbitrary row index. Re-apply changed answers only while no irreversible dependent result has been finalized.
5. Use `data/people/coaches/<coach>.json` to store dated `contract_signed`, `contract_amended`, `role_changed`, `departed` and other existing kinds where appropriate. Do not create parallel contract numbers in `Staff_Moves.md`. Preserve term/guarantee/offset across a season handoff until legally changed.
6. Update the single Staff page renderer, coaching payroll renderer, coaching profiles, current appointment and 2015 phase/annual indexes **only if facts changed**, in the same atomic event update.
7. Reuse the established `docs/football_event_inserts_v2_separate_outputs/` route for outside interviews, unsolicited renewal contacts, offers and departures. Never generate separate mini-briefs for each; reuse the active phase briefing and one shared response journal.
8. Add Staff Moves as an index of separate canonical event results. A terminated, retained-under-new-contract and interview-permission result on the same day appear as three distinct links, not one synthesized outcome.
9. Check 2014-to-2015 handoff: the 2014 Season Review remains the football/exit-interview owner, while 2015 Early_Offseason owns new staff contracts; the later 2015 baseline only carries actually settled new employment rights, with pending items still pending.
10. Keep game outputs, game receipts, game results and 2014 historical contract records unchanged during a template-only implementation. A staff *action* can change current authority and future team preparation, never retroactively rewrite played calls or the previous game's story.

## F. Required regression tests

1. The issue is attempted before Jacksonville's final 2014 game: refuse a **completed** year-end staff review; allow only an explicitly limited preliminary brief.
2. The Jaguars reach the 2014-season playoffs: do not hardcode Dec 29 or Jan 1 as their final game or staff decision date.
3. Stone is fired by Khan/Caldwell: no Stone-authored Jacksonville staff selection and no future confidential Jaguars staff briefing.
4. Stone retained: valid staff review can be issued with 12 actual assistant entries as of source date.
5. The nine 2014-term endings display as expiring, not automatically unemployed Jan 1; the three 2015 contracts are not mislabeled expired.
6. Exact contractual expiration day unknown: block any action requiring the date and name the uncertainty; do not assume the unverified second-Tuesday convention.
7. Stone writes `No change` for current play-call arrangements: existing Tice/Crennel/Westhoff responsibilities and current delegation do not silently switch.
8. Stone proposes terminating Tice despite a 2015 guarantee: the financial obligation/offset is checked; performance disagreement is not reclassified as termination for cause.
9. Stone writes 'renew all nine': each receives its own authorized negotiation opportunity; none is automatically signed or given an invented salary.
10. Two coaches accept offers, one declines, another remains in talks: exactly three individual **resolved** result files, one pending process record, and three corresponding links; no combined result page.
11. A coach rejects a renewal offer: one standalone declined-offer result, no renewed contract, no forced resignation before the old deal actually ends.
12. A coach with no new staff action remains unchanged without a manufactured 'retained' transaction.
13. Two outside clubs separately ask to interview the same coach: keep two requests and two event outcomes, with legal status evaluated at each date.
14. Position-coach-to-coordinator interview in January 2015: no erroneous modern guaranteed right; apply the actual era's club permission and recorded standing instruction if valid.
15. Playoff assistant interview requests obey 2014-15 windows; do not hire a live team's assistant while prohibited by period rules.
16. Current carousel method's 'default policy' is not mistaken for an `IN_FORCE` standing instruction that the decision queue can apply automatically.
17. A new serious coaching vacancy triggers **Candidate Report**, not a fabricated finalist or automatic hire inside Staff Moves.
18. A contract and its payroll view reconcile dollar for dollar with the individual coach record; no assistant pay is put into the player cap.
19. A staff briefing re-issued on a newly received request preserves the original dated issue and its exact content.
20. A dated staff role change updates current job delegation, coach record, Staff page and phase results together, without rewriting closed game results.
21. The 2014 Season Review and 2015 Early_Offseason links work even before the 2015 playing season is activated; no premature handoff acceptance.
22. Staff page omits repeated generic 'communication improved' judgments absent a concrete episode; reject unsourced attribution and invented interviews in editorial review.
23. Empty action cycle: result index truthfully says no concluded actions, with the continuing staff and any open questions intact.
24. A later independent real-world 2015 assistant job or team firing is never imported as the predetermined outcome of the counterfactual career.

## G. Sources to read when implementing

Repository: `career/2014/Team_Operations/Staff/README.md`; `coaching_staff.md`; `career/finances/coaching_and_organization/coaching_payroll.md`; `career/Assistant_Coaches/staff_profiles.md`; `state/current_job.json`; `docs/season_cycle_milestones.md` open questions; `career/2015/Calendar.md`; `foundation/templates/season_review/exit_interview.md`; `runtime/decisions.py`; `runtime/decision_queue.py`; and `docs/football_event_inserts_v2_separate_outputs/Implementation_Spec.md`.

Contemporaneous research (used for **procedural principles**, not for importing later coaching outcomes):
- https://www.nfl.com/news/what-offseason-nfl-coaches-busy-preparing-for-2014-campaign-0ap2000000323842
- https://www.espn.com/nfl/story/_/id/10376181/jason-garrett-coach-dallas-cowboys-had-authority-make-staff-changes
- https://www.washingtonpost.com/news/football-insider/wp/2014/12/29/jay-gruden-to-meet-with-bruce-allen-and-daniel-snyder-this-week-on-assistants-team/
- https://www.si.com/nfl/2014/01/16/nfl-finances-concussion-settlement-playoff-pay
- https://www.dallascowboys.com/news/st-coach-bisaccia-interviewing-for-skins-head-coaching-job-345951
- https://www.nfl.com/news/rooney-rule-will-not-be-extended-to-coordinators-0ap1000000152292
