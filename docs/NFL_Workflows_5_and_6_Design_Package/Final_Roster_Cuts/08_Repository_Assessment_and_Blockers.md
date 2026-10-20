# Final Roster Cuts: repository assessment and unresolved implementation requirements

## Actual established functionality

- `runtime.decisions.REGISTRY` names `Roster Cutdown Report`, `My Cut Recommendations`, `Final 53` as the `final_cuts` three-page workflow, currently **not implemented**.
- The 2014 career has one completed `final_roster_cuts.md` with genuine Aug 26/30–31 dates, a separate `roster_decisions.md` for Stone's depth and leadership choices, and individually linked completed roster/trade/medical records. It cannot be retrofitted or used as a future 2015 answer key.
- The 2014 six position-battle cards are closed Aug 30. `Team_Operations/Team/Depth_Chart/depth_chart.md` owns current depth, and the permanent roster/contract records own facts. A new `Final_53.md` should be generated from those current sources, never treated as a second independently editable roster.
- `runtime.events` and `scripts/render_annual_record.py` already support dated events at their actual owner and a derived year index. `docs/event_inserts.md` sets immutable brief reissues and per-individual results. The general-purpose routing for 2015 cutdown events and new queue blocks is **not demonstrated**.
- `state/current_job.json` holds authority; notably final roster cuts belong to Caldwell as an inferred personnel-authority row, while Stone's depth control is explicit from his contract. The distinction is preserved.

## True blockers before an implementation could be declared complete

1. **Destination conflict:** The registry’s `final_cuts` decision currently resolves through a shared parent route to `Training_Camp_and_Preseason/`, not the canonical `Training_Camp_and_Preseason/Roster_Decisions/`. Add a kind-specific mapped destination without moving training-camp or preseason-game workflows.
2. **The 2015 roster does not exist yet at a playable in-world date.** The remainder of 2014 is unplayed, and no 2015 signings, draft selections, medical results, camp work or decisions have occurred. The tool must refuse to populate these from real-life Jaguars historical results.
3. **No verified generic cutdown-specific writer/gate.** The current repo has manual 2014 roster moves and current owners, but not a demonstrated 2015 pipeline that takes Caldwell's legitimate decision, distinguishes waived/released/waived-injured/reserve rights, validates each contract, commits effects and produces per-player output atomically.
4. **No demonstrated 2015 waiver priority/claim resolver.** The rails exception defines other clubs' moves and own-player protection but does not by itself certify every 2015 waiver claim, contract right or random-market decision. Closed 2014 waiver outcomes cannot be reused.
5. **Unreconciled service-type fields:** 2011 Article 29's `credited service` legal definition and Article 33/2014 agreement's `accrued seasons` are not identical. A validator that checks only drafted year or the wrong count can turn an outright release into an illegal waiver, or vice versa.
6. **Two deadlines, not one.** The Sept 1 75-player state must be complete before the Sept 3 last preseason game. The Sept 5 53 and Sept 6 waiver/PS stage must have distinct dated statuses. A pregame roster compiler cannot replay its earlier 90-man input after the reduction.
7. **The next game is not the 53.** The 53 contains medically restricted or unavailable players when lawfully retained, while the eventual weekly game-day list has its own 46-player cap and Stone inactives. There is no automatic promotion or medical clearance from the new Final 53 template.
8. **Individual event records and idempotence:** one signed release event per player, one per rejected trade, one per failed practice-squad approach etc. Each result must be available promptly at its own date and survive future changes. The summary page cannot stand in for 22 independent releases.
9. **Financial effects:** an unknown cap figure does not authorize a precise projected saving. Permanent contract/financial records must reconcile bonuses, guarantee, dead money and relevant termination pay; a clean reader page simply explains confirmed effects.
10. **Roster/count authority:** statuses such as unsigned tenders, PUP/NFI, IR and waivers must be classified correctly for 2015 from the legal documents and current player record. The 2014 '74 signed + four unsigned rights' precedent is not a universal 2015 formula.
11. **Publication and clean-page rules:** requested guidance should be about the real coach's choice, not identifiers, code or fake personnel grades. Every 2015 issued briefing must have its own as-of content history and material-revision gate.

## Minimal future implementation changes

- Add `cutdown_75`, `cutdown_53` and player-scoped dependent decisions to `runtime/decision_queue.py` with per-deadline chronology checks.
- Add year-agnostic roster status/eligibility and service-year verifiers, then a correctly routed one-event/one-result personnel transaction writer. Keep information in `data/`/canonical owner, not new duplicate player tables.
- Render the triplet through the existing decision registry into `Roster_Decisions` with versioned brief and submitted Stone answers; ensure the three coach pages contain only football words.
- Stage an as-of count/deadline index for 75 and an actual, derived Final 53 for 53. Generate next-day waiver, practice-squad and medical results separately, with a refreshed roster if necessary.
- Attach existing trade/medical/contract event routing to this workflow, preserving one individual event output and the annual Record index. Do not add a new shared results omnibus.
- Add 68 proposed tests in `05_Implementation_and_Validation_Spec.md`; verify historical unchanged 2014 report/receipt hashes on a clean isolated clone.

## What should **not** be altered by integration

The 2013/2014 existing results, the completed 2014 roster cut names and dispositions, Stone's 2014 depth decisions, real historical league-date sources, the current-year 2014 Week 6 readiness gates and the season replay engine. Avoid trading correctness for a shorter workflow: a date, a roster count and an independently resolved player case cannot be invented or skipped.

**Conclusion for integration review:** This design has sufficient period rule structure and verified 2014 precedents to implement later, but the current repository does *not* demonstrate the 2015 cutdown transaction engine, future roster, season-specific waiver resolver or live user decision that would authorize closing this workflow. Tests have been specified, not run.
