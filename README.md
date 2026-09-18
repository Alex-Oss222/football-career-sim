# Football Career Simulation

An LLM-first, choice-driven American-football head-coaching simulation. The user creates and controls one protagonist head coach, Alex-Lamar Stone (ordinary name: Alex Stone); the simulator represents the football world, its people, its institutions, and the consequences of the head coach's choices.

## Where things stand

This repository was rebuilt from scratch on 2026-09-17. The prior structure (`engine/`, `modules/`, `teams/`, `world/`, `characters/`) was a set of incompatible legacy layers — a January 2009 job-search profile, a counterfactual 2009-10 Detroit world, a structurally wrong 2010 cap model, a mismatched late-2010s offensive catalogue, and an unrelated 2024 high-school RPG mode, among others — that could not be run reliably as written. `00_Audit_Migration_and_Stress_Test_Report.md` documents that audit in full. The prior structure has been removed entirely; nothing from it is active canon.

The current, sole source of truth is eight documents:

- **`00_Audit_Migration_and_Stress_Test_Report.md`** — the audit that produced this rebuild. Historical/reference; not itself a runtime rule source.
- **`01_Project_Instructions.md`** — stable governing instructions: user/simulator division of control, authority boundaries, football-reasoning rules, fog-of-war, real-person and divergence handling, career/outcome resolution.
- **`02_League_Era_and_Sourcebook.md`** — the league, era, and rules the simulation runs under: divergence register, competition identity, calendar and period register, playing rules, roster/transaction/labor/financial rules, the historical-draft-class and hiring-search procedures, source provenance.
- **`03_Head_Coach_Organization_and_Authority_Canon.md`** — Alex Stone's identity/background canon (resolved 2026-09-17, see §1.6 for the full resolution record), his contract and authority map, staff and organization structure, the external hiring-market and search-cycle procedure (§10), and revision controls.
- **`04_Roster_and_Staff_Register.md`** — the active roster and staff register once a career is initialized.
- **`05_Current_Season_State.md`** — the current in-world date, season, and status; the initialization gate lives here.
- **`06_Chronology_Game_Ledger_and_Handoff.md`** — the dated event/game ledger and cross-chat handoff record. This is the sole supersession history once play begins.
- **`07_Game_Simulation_and_Resolution_Engine.md`** — the actual game/drive resolution mechanism, hidden rating-anchor system, turn-economy leverage gate, weekly turn structure, and world-agent autonomy rules that Documents 1-6 assumed but never implemented. Added 2026-09-17, after a judged three-way design competition; see its §0 for why the six-document shape didn't need to be rebuilt, only extended.

All eight remain **authoring templates; no career is initialized.** Document 3's biographical fields are resolved, but team, contract, season, and coaching-identity fields stay open by design until the user completes Document 1's initialization gate. Document 7 has its own short list of outstanding decisions in its §11.

## How to use this repo

Read Document 1 first, then Documents 2-7 in order. Do not generate any in-world event until the initialization gate (Document 1 §2, cross-checked against Document 3 §12 and Document 5) is satisfied and the user explicitly says to initialize the career.
