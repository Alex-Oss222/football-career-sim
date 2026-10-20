# NFL Draft redesign: repository assessment, conflicts and implementation blockers

**Research target:** `Alex-Oss222/football-career-sim`, `main`; observed tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24`, October 20, 2026. The tree moved 27 commits forward while this workflow was being researched; this reference identifies what was inspected, not a lock or implementation commit. This assessment contains technical names intentionally; the three coach-facing draft pages do not.

## A. What is sound and should stay

**Closed football canon:** The 2014 draft is already executed and recorded. Nine selected players, their distinct draft dates, Caldwell's final authority, the No. 205 reopened Stone recommendation, May 11 rookie contracts, and actual 2014 undrafted calls are fixed past events. The redesigned draft **starts prospectively**. Nothing in a new template changes a 2014 result, adds a 2015 player or advances past October 5, 2014.

**Existing phase shape:** `runtime/decisions.py` already names the exact three pages and maps `draft` to the year-specific Draft folder. This design requires an implementation and tests, not another unrelated naming scheme or a separate questionnaire replacing the user's natural recommendation page.

**Single-ownership model:** `runtime/events.py`, `docs/season_structure.md`, `docs/rebuild_plan.md` and the existing generated annual record define how real events own their dated outcomes. `docs/event_inserts.md` and the new `EVENTS` registry define where genuine consequential business appears. A draft report may display a short summary and **link** to each independently resolved outcome, but never become its substitute.

**Head-coach powers:** `state/current_job.json`, the executed Stone contract and Document 3 already distinguish Stone's football recommendations from Caldwell's binding choices. The written-projection and meeting right for franchise-level quarterbacks is narrower than a draft veto. No fake shared GM authority is necessary.

**Historical league rails:** The approved 2014 method already specifies availability-at-N, ordinal pairing with the real Jaguars' k-th selection, no duplicated Jaguars-controlled players and explicit unplaced counterparts. The 2014 completed pairing demonstrates the collision rules. They are not ordinary draft mechanics and must remain transparently labelled as this simulator's specific historical-personnel exception in the technical spec.

**Actual 2015 inventory:** As of the October 5 state, Jacksonville holds its own second, Miami's third, Houston's fourth, Arizona's fourth and Seattle's seventh. Jacksonville's original first/fourth are gone. These original-club identifiers are sufficient for current planning. Numbers cannot be honestly supplied yet.

## B. Where the current repository is not ready

| Area | Verified issue | Engineering requirement | Risk if skipped |
|---|---|---|---|
| Decision registry | `draft` registered with `when="May"`, not implemented. April 30 is the real first day. | Reuse exact `REGISTRY` page trio, set season-derived date presentation, build phase open/edit/freeze/report flow. | Wrong date and a Markdown-only mock workflow. |
| Actual draft gate | `runtime/decision_queue.py` has `personnel_recommendation`, but its configured blocking event kinds do not include `draft_pick`. | Add a scoped on-clock pick gate, dependency and standing priority/fallback semantics, plus resumption when settled. | A draft can execute despite a required Stone consultation or an illegal pick. |
| League order | `runtime/draft_order.py` derives its order from 2013 receipts and the 2014 recorded Indianapolis/Green Bay coin. | Parametrize a truly year-specific order and implement independent 2015 ties, rounds, original assets, statuses and exact current owners. | Carries 2014 picks and the wrong league finish into 2015. |
| Renderer | `scripts/render_draft_order.py` is fixed to 2014. | Write generic mapping-based render from year-local structured owners and compare every displayed value against inputs. | Hardcoded stale 2014 results or output inconsistent with file ownership. |
| Compensatory awards | `scripts/resolve_compensatory_picks.py` uses 2013 branch records and 2014 method and assets. | Obtain approved 2015 method and complete 2014 branch losses/gains; persist results on their historical award date. | Leaks the real 2015 compensatory list or applies an uncalibrated 2014 model silently. |
| Full 2015 original-asset register | Five JAX holdings are known, but no complete league-wide 2015 ownership file and audited conditions are ready. | Audit all original 2015 picks, already moved assets, third-party claims, conditions, rotations and allowable post-cutoff transfers. | A single slot appears under two teams, or an unavailable asset is sold. |
| 2015 date-gated scouting | `library/2014_draft_information_gates.md`, `2014_draft_pool_registry.md` and other 2014 entries are excellent precedents, **not** a 2015 class. | Build dated 2015 eligibility registry, actual available prospect evidence, combine/pro-day dates and authorized team-specific reports. | Real draft hindsight disguised as pre-draft scouting. |
| Live room + league clocks | No verified 2015 draft-clock scheduler or independent Caldwell pick/fallback decision procedure. | Explicitly choose live card-clock behavior and Stone consultation/resumption. Test expired clocks and timeouts. | Unrealistic full draft halted for unlimited user discussion or fictional picks after legal expiry. |
| Per-pick result ownership | `draftees.md` groups the closed 2014 event results by day; no general 2015 separate-pick result builder exists. | One new dated Markdown result for **each** completed Jacksonville selection under the draft owner, plus `Record.md` links. | Violates user's separate event output requirement. |
| Intra-draft business | New `EVENTS` names some staff/trade inserts, but cannot be assumed installed for draft, recruitment and contracts. | Reuse shared insert renderer for actual trade/personnel business, `My_Responses` where needed and individually closed results in each department. | Rejected trade and failed undrafted recruiting disappear into phase summary. |
| Other-club rail pairing | 2014 pairing is recorded, but no generalized 2015 pairing/collision validator shown. | Use unique person identity, original k-th Jaguars position, self-pairing/unplaced rules and actual real-club eligibility metadata behind a firewall. | Two clubs acquire the same player, or a club gets a fabricated replacement. |
| Handoff to rookie minicamp | Draft, offseason program, rookie minicamp and May OTA owners are independent. | Transfer only valid rights/contract eligibility, staff first-job recommendation, medical restrictions and actual dates. | Invented April workouts, medical clearance or guaranteed roster jobs. |

## C. Genuine legal and design ambiguities

**1. Real clock versus asynchronous coach approval.** The original 2015 draft allotted 10/7/5/4 minutes depending on round and four minutes for compensatory choices. A written free-form decision page is not a live NFL phone-room interface. The **recommended alternative** is to obtain Stone's ranked preferences, trade ceilings, first-job projections and explicitly authorized fallback instructions before day one; show the true pick clock during play and prompt only for real exceptions. The time model must still declare what happens when an answer cannot arrive before the clock expires, including Caldwell's independent legal authority. No arbitrary “pause the NFL” assumption.

**2. The real compensatory algorithm is not fully public at the chosen historical point.** The 2014 project already adopts a measured branch formula using signed contract values, playing time, honours, cancellations and league totals. That method is an approved *simulation approximation*, not proof of the league's secret weights. The 2015 method is unapproved and cannot inherit real-world 2015 recipients. No silent replacement.

**3. Historical availability rule deliberately introduces a narrow future-fact dependency.** A 2015 player's actual real draft position can be consulted behind the scenes **only** to enforce availability-at-N under the user exception. This fact must not be shown in a January or April pre-draft talent discussion, or converted into a scouting evaluation. A separate history rails validator handles it.

**4. A specific prospective rookie's eligibility, interview and medical status must be independently established.** Even when a public prospect's real college identity is known in October 2014, declaring him NFL draft eligible ahead of the Jan 2015 process or naming his later measured combine performance is hindsight. No invented medical clearance. College scout film and professional role judgments can be authored only from actual available evidence.

**5. Who speaks for Stone when a pick is due.** The existing emergency-practice succession has no delegated draft-selection authority. Tice or Crennel cannot be made a draft-day proxy because one of them may run practice when Stone is unavailable. Caldwell can make his **own** draft decisions, but a missing Stone response to an actual mandatory franchise-QB consultation cannot be manufactured into consent.

**6. Per-event versus grouped historical outcomes.** The current 2014 selection/UDFA records are genuine completed history under their prior archival method. Adding nine retroactive individual result files now would create new authoritative-looking events or change the 2014 historical view, violating the Week 5 preservation rule. Make one dated result per pick and per closed recruiting/contract/trade matter **from the next implemented draft onward**. Do not fake new May 2014 outputs.

**7. Same-day completed pursuits and source-date precision.** The completed 2014 undrafted file establishes May 10 for many signings/declines, but not a minute-by-minute timestamp for each call. A prospective separate result in 2015 must use exactly the known resolution date and time if recorded, rather than invent one. The lack of a time does not erase the individual event.

**8. Unverified future transfers and staff remain open.** The 2015 draft may eventually involve a changed employment role, roster, medical situation, pick owner or signed contract as the career advances. No template can assume that Stone is still Jacksonville's coach in April 2015 solely because he had a four-year deal in October 2014; absent a future club decision the current contract stands, but new information must be checked at the actual draft issue time.

## D. Ownership and implementation order

1. Verify active current job, season and the frozen October 5, 2014 history; preserve 2014 draft and game records byte-identical.
2. Generalize year-local order and ownership *without* rewriting the 2014 draft scripts' historic output. Add full 2015 original-club transaction audit, conditions and compensatory method before any correct overall pick number can be published.
3. Establish dated 2015 prospect eligibility and genuinely supported scouting evidence. Keep the restricted historical real-pick availability metadata separate from exposed evaluation.
4. Implement issue/version history for the report, natural recommendation page and immutable recorded Stone response with known fallback/priority semantics and formal franchise-QB consultation gate.
5. Implement Caldwell's independent pick/negotiation decision from explicitly authorized inputs, draft-day trade constraints and real 2015 clock behavior. Never ask the assistant to improvise a player or source result.
6. Implement one canonical per-selection event with its dated reader result, and event-specific failed and successful transaction/UDFA outputs through existing owners and `My_Responses` inserts.
7. Implement ordinal historic-pick pairing, missing partner behavior, legal rookie rights, subsequent financial execution and annual-record reconciliation.
8. Build the summary and new season handoff **from canonical results**; use the proper roster, medical and future program gates. Do not write outcomes during Markdown render or open.
9. Test on a synthetic year fixture, validate clean pages and file ownership, and check 2014 records plus Oct 5 2014 state remain unchanged. Run the actual repo test suite only in a future authorized implementation PR.

## E. Acceptance/validation position

The accompanying implementation contract lists **64 proposed regression tests**, including no-hindsight, era clock, original asset lineage, tradeable assets, user authority, failed negotiations, per-player recruiting results, pick self-pairings, role separation, signed-contract effects, and preserving the 2014 archive. These are **not passed tests**. The Markdown package is design-only; it is neither a complete runnable draft scheduler nor evidence that GitHub has integrated the pages.

**Result of assessment:** The proposed three-page NFL Draft experience is feasible within the repository's established boundaries, but the 2015 selection runner, complete ownership, compensatory methodology, dated scouting and unambiguous clock protocol are **implementation blockers**. Treating those missing pieces as “a language model will figure it out when we get there” would manufacture precisely the football realism and user agency the redesign is intended to protect.
