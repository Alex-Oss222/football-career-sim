# Final Roster Cuts: implementation and validation contract

**Status:** Design-only proposed workflow, never executed. Repository inspected at `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` (2026-10-20). Active career still October 5, 2014 after the Week 5 Pittsburgh game. This package did not make a transaction, medical designation, assistant appointment or Stone decision.

## 1. Three-page workflow, two mandatory roster deadlines

The `final_cuts` registry entry in `runtime/decisions.py` fixes three primary coach-facing pages:

| Role | Filename | Owner and status |
|---|---|---|
| Caldwell/staff briefing | `Roster_Cutdown_Report.md` | `career/<year>/Training_Camp_and_Preseason/Roster_Decisions/`; **requires a narrow route correction** because the present `final_cuts` shared place resolves to the parent `Training_Camp_and_Preseason/`; stage-specific editions, as-of and dated |
| Stone's natural football recommendation | `My_Cut_Recommendations.md` | Same folder, Stone's submitted words/versions; may cover distinct 75 and 53 stages without overwriting an earlier approved answer |
| Roster filing result | `Final_53.md` | Same folder, derived **after** Caldwell actually completes and files his 53; current exact 53 only as-of a real date and no secondary roster owner |

Do not compress the 2015 **September 1 by 4 p.m. ET reduction to 75** into the September 5 final 53. September 3 is the fourth preseason game and must use the compliant post-75 roster. The first stage gets its dated 75 count, each actual completed transaction at its individual owner, and a historical issue/revision of the Cutdown Report. A coach's main three pages can span the process; no second fake 'Final 75' authoritative roster is necessary. A short 75-stage index links its completed individual events and lawful count; after the final reduction, `Final_53.md` is built from the one current roster source.

## 2. NFL 2014–15 rule table

| Rule | Correct 2015 requirement | Source and design consequence |
|---|---|---|
| Camp list and first reduction | Preseason 90-man maximum, **75 by Tue Sep 1, 4 p.m. ET** on applicable Active List | 2015 league calendar, Seahawks July 15 and NBC/PFT August 27. Count legally classified players; a four-player rights list is not necessarily four signed active contracts. |
| Last exhibition | Thu Sep 3: Jacksonville at Washington, 7:30 p.m. ET | Jaguars Apr 20; 75 must be resolved before game-four freeze. |
| Final reduction | **53 by Sat Sep 5, 4 p.m. ET**, on Active/Inactive List | Contemporaneous league bulletin as reproduced by Seahawks, contemporary Jaguars Sep 4/5 announcements and other sources; resolve conflicting 6 p.m. secondary extract in favor of primary/concordant 4 p.m. sources. |
| Game-day list | Up to **46** players dressed for regular-season/postseason in 2015, with legal minimum subject to rules; the 53 is not 46 | Contemporary Vikings Sept 9 plus period NFL calendar. Stone owns the game-day inactives, not all roster slots. Do not apply later 48-player or offensive-line game-day rules. |
| Waiver vs outright release | Article 29 §1: a player who has completed his **fourth credited-service year** becomes a free agent on release before trade deadline; players below that threshold normally go through waivers. After trade deadline the procedure changes. | 2011 CBA original PDF printed p. 155. Verify *credited* service from source record; don't equate it mechanically with *accrued* service used for a different purpose. |
| Contact while on waivers | No other club coach/personnel may contact until player released by waiving club | Article 29 §2. Waivers pending are not a free-agent negotiation. |
| Waivers at 53 | Sunday Sep 6 **noon ET** claiming period ends; league notice approx 1 p.m. | 2015 NFL important dates, see CBS/NBC and current library verification; only then can a waiver-cleared eligible player be separately signed to practice squad. |
| Practice squad | Up to **10** in 2014 and 2015, including at most **two** of the enlarged eligibility class (up to two accrued seasons), with prior service requirements and rights verified | NFLPA August 19, 2014 side agreement modifying 2011 CBA Article 33. No automatic squad signing or 'stash' of a cut player. |
| Practice squad contractual status | New agreement and player assent after legally available | Article 33 and period personnel notice; reserve/unrestricted/cut claims are separate. |
| PUP/NFI at 53 | For a player on Active/PUP or Active/NFI, club chooses reserve list, waiver/release, trade or retaining Active List slot when permitted | Contemporaneous league bulletin. Status and med opinion must be individually verified, not inferred from an injury. |
| Injured waiver and IR | 'Waived/injured' involves waivers; if player clears and the applicable process calls for reversion, only then move him to Reserve/Injured. An agreed settlement or claim can change the outcome. | Contemporary 2015 Jaguars Aug 29 report; apply the actual transaction stages. No phantom IR assignment. |
| Designated return | **One 2015 designated-return possibility** subject to eligibility and the post-Sep 6, 4 p.m. ET window and period conditions | Period NFL bulletin (NBC/PFT Aug 27, CBS 2015 dates); do not import modern multiple-return rules or make a same-day Sep 5 designation. |
| Contract/cap | Release may have dead money, guarantees, termination pay and notice obligations | `career/finances` and actual signed contracts; no invented salaries or precise savings from a nominal roster number. |

The CBA rights distinction is nontrivial: the **fourth credited service year** in Article 29's waiver exemption is not the same datum as an accrued season for free agency or eligibility for the expanded practice squad. A working legal status should carry the relevant source and use the *correct* year-type for each question.

## 3. Repository inspection and required changes

| Existing path/system | What works now | Needed behind-scenes behavior |
|---|---|---|
| `runtime/decisions.py` `final_cuts` | Triplet is registered, not implemented. **Current shared `training_camp_and_preseason` route lands in `Training_Camp_and_Preseason/`, not `Roster_Decisions/`** | Preserve exact names; add a **kind-specific `final_cuts` route** to `SeasonPaths.record('training_camp_and_preseason/roster_cuts')`. Do not move the `camp` pages when fixing it. |
| `state/current_job.json`, Document 3 | Stone final authority for depth (9), practice (11), gameday (8); Caldwell final roster cuts (7, stated inference), player contracts/transactions (5,20); medical clearance external (16) | Enforce owner-specific actions. Stone's opinions don't turn into transfers; Caldwell cannot settle Stone's depth-choice without explicit standing authority. |
| `runtime/decision_queue.py` | `personnel_recommendation`, `personnel_transaction`, `depth_and_roles`, `medical_status` exist; no cutdown-specific frozen transaction blockers | Add `cutdown_75` and `cutdown_53` dependencies, scoped by season, and event-level blocks for actual contested business. User-unanswered requested recommendation blocks the *dependent* action but not league/background events. |
| `career/2014/Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md` | Completed 2014 reductions, 74 signed at 75, 53 on Aug 30, waivers and eight squad signings Aug 31, legally distinct owners | Preserve exact historical bytes; use it as a precedent not 2015 template data. New dates differ. |
| `career/2014/Training_Camp_and_Preseason/Roster_Decisions/roster_decisions.md` | Stone's separately dated depth and game-day decisions | Keep current depth owner under `Team_Operations/Team/Depth_Chart`; `Final_53.md` is a read-only derivative linking those decisions. |
| `Position_Battles/` cards | Six 2014 competitions preserved with dated evidence and August 30 decisions | Fresh 2015 contests only when actually established. Cutdown does not conjure a winner; stage references individual closures. |
| `Team_Operations/Team/Roster/`, `Finances`, `Medical` | Current personnel, contract and individual medical source domains | Add 2015 period-specific transaction writer with atomic roster/cap/list/waiver effects; one permanent player/contract owner; do not edit displayed views independently. |
| `runtime/rails.py`, 2014 league personnel method | Other 31 clubs' real moves on real dates, with Jacksonville exception and same-kind/same-window departing-player rule | Waiver claims, other-club moves and practice-squad signings need 2015 dated rail scope and legal status checks. Do not assume real future Jacksonville cut/signing. |
| `docs/event_inserts.md`, `runtime.events`, annual index | One material briefing revision and one individual dated result per resolved event, with domain owner and annual index | Render this inside the active Cutdown Report, shared `My_Responses.md` for *off-phase* offers, independent dated personnel events, and the 75/final-53 index. |
| `scripts/validate_repository.py`, `runtime/clean_pages.py` | Football-only Markdown/owner path rules, historical byte protection | Reject direct system paths, machine IDs, snapshot/technical content on three reader pages, duplicate event owner, mismatched final 53 and stale views. |
| Current game compiler | Game 4 inputs need final legal pregame roster | Hold 2015 Sep 3 game-four freeze until Sep 1 reduction documented. Post Sep 5 53 does not change already played game. |

**Not currently demonstrated:** a general-purpose 2015 cutdown transaction engine, a waiver claim priority/result implementation for 2015, 53 cutdown dependencies, a deterministic multi-event result publisher, and 2015 roster/legal release. The 2014 completion record does not establish these services for 2015.

## 4. Single-fact ownership and event lifecycle

**Data owner design:** Each player has one permanent identity and contract/history source (`data/people/players` plus contract sources); the season has dated event ownership (waiver/release/IR transaction at roster+finance owner; medical diagnosis/restriction at medical owner; trade offer and disposition at Trades; actual practice-squad contract at contract/roster owner). Reader-facing `Final_53.md` is computed from the *current post-Caldwell roster control state*, not an editable table retyped from Stone's recommendation.

Minimal privately stored event fields: stable `event_id`, `season`, `raised_at`, `known_to`, player/club IDs, actor/final authority, transaction subtype, source paths/digests, pre-status and legal right, applicable deadline, Stone answer ref (if requested), other-club reply/state (if relevant), `status` open/withdrawn/closed, concluded timestamp, new contract rights/status, cap/guarantees/medical dependency, single canonical Markdown result path. Do not make the user see these identifiers.

**Each independently resolved event, including every released/waived player case, has its own dated outcome**, regardless of success. A 20-player reduction therefore can have 20 individually readable outcomes, plus a one-line index and a 53 roster derived view. If a player is subsequently claimed, that is a new independently dated event, not a silent rewrite of his original waiver submission. For an existing trade/medical document already owning one event, link it instead of double-recording. A coaching role appointment is a Stone decision, not a Caldwell transaction, and requires its proper dated depth owner.

State transition example for one player:

1. **Proposed:** staff/Stone recommendation, visible to Caldwell, no roster effect.
2. **Caldwell decides:** verify signed contract, accumulated credited service, medical/legal status and exact deadline. If the action needs player/third-party assent or a waiver period, record submitted action; do not leap to the final status.
3. **Submitted waiver/release:** dated individual result for the action, plus owner update. A waiver remains open for independent claims. Outright release grants free-agent status per period rules when applicable.
4. **Waiver closes at Sept 6 noon:** independent actual claim result or waiver clearance recorded at its own dated owner; no automatic sign-back or squad place.
5. **Practice squad:** only after eligibility, waiver clearance or other correct free-agent status and both player + Caldwell contractual assent. A declined PS request remains a dated unsuccessful pursuit.
6. **Views:** rebuild roster, finances, medical availability, depth choice if user-made, `Final_53.md` as-of and `Record.md` links from owner events. Rebuilding is idempotent and does not cause another transaction.

## 5. Stage-specific execution

### Before September 1: 75

Prepare a dated roster count based on actual active/offseason contracts and applicable list exemptions. Consult Stone where a meaningful coaching recommendation is requested. Caldwell can legally decide which contracts, waiver requests, injured designations or trades to execute. Execute **only when actor/outcome is real**. Close the 75 stage with its actual count and individually filed decisions; preserve current `Preseason_Game_Briefing` input dependencies for Sept 3. A club already below 75 needs no manufactured cut. A drafted/unsigned or tendered player's rights do not automatically count as an Active List contract without verified league status.

### After September 3 preseason game four: 53

Reconcile only actually completed game four evidence and injuries. Issue an updated material Cutdown Report when Stone owes a choice. Preserve his 75 recommendation as a prior, date-stamped answer, while he supplies any changed final advice. Caldwell executes player movements in compliance by Sept 5 at 4 p.m. ET. Run legality and cap review before and after. Derive the 53 names and preserve exact player-count identity; do not assign Stone's depth or inactives by falling back to a roster table.

### September 6 and beyond

At noon ET resolve actual legal waiver claims, then the league notice and eligible practice-squad negotiations. After 4 p.m., apply period-specific designated-for-return eligibility where appropriate. Each independently settled outcome gets a fresh dated result; build a new as-of roster view, retaining the Sept 5 filing history. No belief that the 'final 53' remains unchanged once waiver claims and roster trades can occur.

## 6. Proposed regression tests (not run)

### Dates, lists, status accounting

1. At Oct 5, 2014 the 2015 53 cannot contain any player inferred from a future transaction.
2. Year selection uses the 2015 Sep 1 4 p.m. 75 deadline, not 2014 Aug 26.
3. Year selection uses the 2015 Sep 5 4 p.m. 53 deadline, not 2014 Aug 30.
4. Game four Sep 3 cannot freeze while the 75 stage is unresolved or count exceeds legal limit.
5. A valid 74-person contracted active count passes the 75 deadline without a fabricated release.
6. A true 76-person active count cannot pass the 75 deadline without an authorized action or valid exemption.
7. Four unsigned tenders are not automatically four active game participants, nor automatically all free agents.
8. A rights-only unsigned player does not alter roster count unless governing period classification requires it.
9. A 53 built from 52 distinct names cannot be described as exactly 53.
10. A 53 with a duplicated multiposition player is counted once and rejected as duplicate row.
11. Reserve/Injured, Active/PUP and Active/NFI have distinct counted/not-counted status based on lawful case.
12. Moving one player onto a properly eligible reserve list changes count only at the recorded effective time.
13. A projected medical return never triggers automatic clearance or promotion.
14. An unavailable but retained player may occupy a 53 slot without being falsely dressed for Week 1.
15. A plan or cut report from the future 2015 season cannot read actual future real-Jaguars roster changes.

### Authority, football decisions and individual events

16. Stone's recommendation changes no contracts or control before Caldwell acts.
17. Caldwell's completed waiver does not secretly change Stone's depth call to the next line player.
18. A genuine unresolved head-coach depth decision is returned to Stone even during a roster deadline.
19. A 75-stage Stone recommendation is preserved when his later 53 preference changes.
20. The same football recommendation phrased differently cannot change a market/waiver draw.
21. Caldwell's evaluation/outcome is protagonist blind and does not reward Stone's persuasive phrasing.
22. A requested Stone answer remains open when blank; silence is never an agreement to release a player.
23. Unrelated league events may proceed while a particular player-release recommendation waits for Stone, unless genuinely blocked by an input dependency.
24. One 20-person Caldwell cut batch creates 20 distinct dated person-level result pages and one phase index.
25. A rejected trade proposal while cuts are active gets its own dated Trade result, never buried in `Final_53.md`.
26. A failed waiver-claim or practice-squad pursuit gets a dated unsuccessful outcome, not an invented signing.
27. Each corrected injury list / waiver result retains the original issued state and subsequent outcome history.
28. The main phase report contains links, not duplicated verbatim personal transaction narratives.
29. An unchanged roster due to an unsuccessful trade retains all old player contracts and rights.
30. Pre-2014 Week 6 pages retain their exact historical bytes, including 2014 Aug cutdown results.

### CBA waivers, injury and practice squad

31. A player finishing his fourth **credited** service year, released before deadline, receives correct free-agent treatment.
32. A player lacking four credited-service years is routed through valid waivers, not a same-day free-agent signing.
33. The code distinguishes credited service for waiver purposes from accrued seasons for practice squad eligibility.
34. No outside club contacts a player while his waiver claim is pending in prohibited window.
35. The 2015 Sep 6 noon waiver resolution cannot be assumed in a Sep 5 final-53 report.
36. A player claimed by another club cannot also be on Jacksonville's newly signed practice squad.
37. A waiver-cleared player is not automatically re-signed by Jacksonville, or signed by anybody else.
38. A waived/injured player does not enter IR until applicable reversion and medical/legal process close.
39. An injury settlement cannot be issued without its actual contractual process and assent.
40. A newly cut player may decline a proposed practice-squad contract without penalty invention.
41. Maximum 10 practice-squad contracts under 2015 agreement; 11th valid proposal cannot be executed.
42. Maximum two exceptional players with up to two accrued seasons; third exception is refused if ineligible otherwise.
43. Practice-squad past-season counter follows 2014/15 six-game rule, not old three-game definition.
44. A 2015 practice squad is not filled before required waiver clearance and personnel notice.
45. A player on 53 at filing and injured later may enter proper Sep 6 designated-return process only after the lawful window.
46. An early pre-window Reserve/Injured placement does not gain an illicit designated-return label.
47. Original signed bonus/guarantee/termination-pay terms control cap effect, not a canned amount.
48. A cut player's salary does not vanish from cap if contract guarantees/dead money remain.
49. Waiver claims follow actual branch standings priority and club chronology, not real 2014 Jaguars standings.
50. A player moving through the historical other-club rails does so only on the permitted real public date and same-kind/same-window exit condition.

### View and record validation

51. The 53 roster is a read-only derived view of executed Caldwell outcomes in the mapped `Roster_Decisions` destination, never the parent folder or the current team roster owner.
52. Stone's depth chart remains its own owner, with legal retained players only.
53. A release cannot appear in the Final 53 remaining list at the same effective timestamp.
54. A complete 53 must include every signed counted player exactly once, regardless of multiposition roles.
55. One retained medically unavailable player does not appear on legal Week 1 game-day active 46 before clearance.
56. A 2015 Week 1 active list contains no modern 48-player rule or mandatory 8-linemen rule.
57. An actual team's 53 may lawfully differ from rigid prefilled 2-QB/3-RB/6-WR counts; no invented quotas.
58. An existing open battle remains open until Stone closes it; no automatic 'winner' from keeping a player.
59. A roster deal requiring Caldwell and another club has its own signed acceptance/notice; no phantom trade.
60. A roster list change rerenders the current team/contract/cap pages once from data owners.
61. Every individually closed event has one unique stable ID and one canonical dated reader result.
62. An event summary/index link can point only to an already concluded event, never an unissued future page.
63. Re-rendering a Final 53 does not execute waivers, redraw another club's claim or backdate the roster.
64. An `Event_Results.md` omnibus cannot replace any dated individual outcomes, including failed pursuits.
65. The clean-page validator rejects internal paths, IDs, disclaimers, generic rating tables, invented media dialogue and ungrounded exact salaries in coach-facing pages.
66. The prior 2014 salary-cap, season history, draft/FA personnel, camp and preseason receipts remain unchanged and test-stable.
67. The Sept 5 filed 53 and Sept 6 revised 53 are distinct **as-of** states, not contradictory identical-date copies.
68. The annual event index carries correct owner URLs and per-event dates, without extra duplicate narratives.

## 7. Acceptance and no-commit rehearsal

A future implementation PR should use a synthetic 75 -> preseason game four -> 53 -> waiver claims -> squad signing run in an isolated test repository with no actual career progression. First stage: 74 signed players at the 75 deadline produces zero fabricated cuts. Second: 76 requires one authorized action before game four. Third: a 75-to-53 reduction outputs **22 player-level** results if all 22 are independently terminated, and not 1 aggregate 'roster downsized' page. Fourth: three failed squad approaches remain three dated failures and the 53 remains legally exact. Confirm the single current roster and individual owners, no double charges, no old 2014 file mutation and unchanged game state. Then run the repository validation, clean-page checks and existing game readiness separately. These 68 tests are proposed, not executed here.
