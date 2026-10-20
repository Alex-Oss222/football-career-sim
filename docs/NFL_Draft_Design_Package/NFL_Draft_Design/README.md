# NFL Draft: researched three-page workflow package

**Repository:** `Alex-Oss222/football-career-sim`  
**Research snapshot:** `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24`, observed October 20, 2026  
**Scope:** the NFL Draft workflow in the established six-workflow redesign sequence, intended for the first future applicable draft and reusable with season-specific law and source checks. The actual 2015 draft begins April 30, not generically in May.  
**Current simulated career:** after Jacksonville's October 5, 2014 Week 5 game, Week 6 unplayed.  
**Status:** **Research and design only.** Nothing in this ZIP has been installed in GitHub, no league or Jacksonville selection has been simulated, and no future player, contract, roster assignment or staff outcome has been created.

## The three required coach-facing pages

| Order | Artifact | What the reader sees |
|---|---|---|
| 1 | [01 Scouting Department Report](01_Scouting_Department_Report_TEMPLATE.md) | A genuine college scouting briefing, actual pick inventory, roster football questions, dated eligible prospects, named uncertainty and permitted live action inserts. |
| 2 | [02 My Draft Recommendations](02_My_Draft_Recommendations_TEMPLATE.md) | A natural head-coach memo to David Caldwell, with the user's selected priorities, individual first jobs, preferred prospects, precise fallbacks and conditions; Caldwell retains final picks and trades. |
| 3 | [03 Draft Room Results](03_Draft_Room_Results_TEMPLATE.md) | A read-through of selections made and their football implications, linked to **separate dated pick, negotiation, contract and undrafted-pursuit results**, including failures. |

## Supporting implementation and example files

| File | Function |
|---|---|
| [04 Individual Selection Result](04_Individual_Selection_Result_TEMPLATE.md) | A reference for one dated result per completed selection; never a combined result. |
| [05 Implementation and Validation Specification](05_Implementation_and_Validation_Spec.md) | Detailed requirements for years, historical rails, roster/authority separation, draft clock, source gates, per-event outcomes and **64 proposed regression tests**. |
| [06 Worked Jacksonville Example](06_Worked_Jacksonville_Example.md) | Three-page reorganization of **already completed 2014 facts**, including No. 205, plus October 5, 2014 prospective 2015 five-asset position. No future 2015 outcomes. |
| [07 Research and Source Register](07_2015_Research_and_Source_Register.md) | Original 2011 CBA, 2014-15 dated NFL sources, 2015 draft timetable, contemporary club scouting procedures and date-information boundaries. |
| [08 Repository Assessment and Blockers](08_Repository_Assessment_and_Blockers.md) | What works in the repository, missing implementation, precise risks and non-negotiable integration order. |

## Non-negotiable operating rules

- Do not change Alex Stone's executed contract, adopted philosophy or current job authority. David Caldwell makes binding draft, acquisition, trade and player-contract decisions. Stone chooses only his own football recommendations and documented franchise-QB consultation rights.
- Never invent a 2015 prospect grade, final 2014 record, 2015 Jacksonville draft slot, college-scout tape report, staff conversation, independent medical clearance or a future NFL player performance. A later real draft selection is never a scouting fact at an earlier in-story time.
- The user-approved 2014-onward historical league personnel exception applies to the other 31 clubs' real selections; Jacksonville's own pick ownership/order come from its career. Jacksonville can choose only a prospect whose real overall pick is at or after its live branch choice N, or who was undrafted; the real Jaguars k-th pick pairs with Jacksonville's k-th exercised selection. Enforce self-pairing, absent partners and unique player control without inventing compensation.
- **One closed consequential event must get one own dated readable result.** Nine distinct concluded draft selections mean nine distinct pick results, not a nine-line summary alone. Likewise, two rejected negotiations mean two separate failed outcomes. The main report links; it never replaces.
- The draft, undrafted recruiting, rookie-contract negotiations and rookie minicamp are separate legal and football events. An acquired right is not a signed player; a signed contract is not a medical clearance; a medical clearance is not a starting job.
- Keep technical event IDs, data paths, source digests, script names and validation terminology out of live coach-facing pages. They belong in technical records and this documentation.

## Six-workflow design sequence

| Work item | Design status after this package |
|---|---|
| 1. April Offseason Program | Completed in the preceding design package; GitHub integration separately pending. |
| 2. NFL Draft | **This complete research/template design package; GitHub implementation pending.** |
| 3. May-June OTAs and Minicamp | Next, not yet redesigned in this sequence. |
| 4. Training Camp Position Battles | Not yet redesigned in this sequence. |
| 5. Every Preseason Game | Not yet redesigned in this sequence. |
| 6. Final Roster Cuts | Not yet redesigned in this sequence. |

No scripts in this archive are intended to run against the active career. The tests specified here require implementation in a future authorized PR and must not be described as passing now.
