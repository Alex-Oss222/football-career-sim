# Football Career Simulation

An LLM-first, choice-driven American-football head-coaching simulation. The user creates and controls one protagonist head coach, Alex-Lamar Stone (ordinary name: Alex Stone); the simulator represents the football world, its people, its institutions, and the consequences of the head coach's choices.

## Where things stand

This repository was rebuilt from scratch on 2026-09-17. The prior structure (`engine/`, `modules/`, `teams/`, `world/`, `characters/`) was a set of incompatible legacy layers — a January 2009 job-search profile, a counterfactual 2009-10 Detroit world, a structurally wrong 2010 cap model, a mismatched late-2010s offensive catalogue, and an unrelated 2024 high-school RPG mode, among others — that could not be run reliably as written. `00_Audit_Migration_and_Stress_Test_Report.md` documents that audit in full. The prior structure has been removed entirely; nothing from it is active canon.

The repository is organized to mirror a separate SCOTUS-simulation project's proven layout — a stable rulebook, an always-current snapshot, and per-season instance history — rather than one flat pile of files:

```
foundation/     the stable rulebook: Documents 00-03, 06, 07, and foundation/templates/ (output formats). Never holds a dated instance record.
state/          the always-current, in-place-updated snapshot: Documents 04 and 05. Rewritten as events happen; never append-only.
career/         the actual played history, one folder per season, created only once that season is reached. Empty until initialization. See career/README.md.
archive/        superseded/quarantined material kept for reference only, never active canon. See archive/README.md.
library/        real-world reference data with no dedicated slot elsewhere: era-specific research (team/coaching-market dossiers, draft-class data). Load-bearing values are copied into foundation/02's real tables; these files keep them traceable to a source.
```

- **`foundation/00_Audit_Migration_and_Stress_Test_Report.md`** — the audit that produced this rebuild. Historical/reference; not itself a runtime rule source.
- **`foundation/01_Project_Instructions.md`** — stable governing instructions: user/simulator division of control, authority boundaries, football-reasoning rules, fog-of-war, real-person and divergence handling, career/outcome resolution, response design (§12, superseded for actual output by the templates below).
- **`foundation/02_League_Era_and_Sourcebook.md`** — the league, era, and rules the simulation runs under: divergence register, competition identity, calendar and period register, playing rules, roster/transaction/labor/financial rules, the historical-draft-class and hiring-search procedures, source provenance.
- **`foundation/03_Head_Coach_Organization_and_Authority_Canon.md`** — Alex Stone's identity/background canon (resolved 2026-09-17, see §1.6 for the full resolution record), his contract and authority map, staff and organization structure, the external hiring-market and search-cycle procedure (§10), and revision controls.
- **`foundation/06_Chronology_Game_Ledger_and_Handoff.md`** — the ledger's rules and record formats. The actual dated entries live in `career/<year>/ledger.md`, not here.
- **`foundation/07_Game_Simulation_and_Resolution_Engine.md`** — the actual game/drive resolution mechanism, hidden rating-anchor system, turn-economy leverage gate, weekly turn structure, free-agency/draft procedures, and world-agent autonomy rules that the other documents assumed but never implemented. Added and locked 2026-09-17 after a judged three-way design competition; see its §0 for why the document shape didn't need to be rebuilt, only extended, and its §12 for the layout this README describes.
- **`foundation/templates/season_output_template.md`**, **`foundation/templates/offseason_output_template.md`**, and **`foundation/templates/hiring_search_output_template.md`** — the three confirmed output formats: in-season, offseason, and pre-hire candidacy turns respectively. There is no input template or form — every turn asks one specific question and the user answers in their own words (Document 1 bans closed-choice menus).
- **`state/04_Roster_and_Staff_Register.md`** — the active roster and staff register once a career is initialized.
- **`state/05_Current_Season_State.md`** — the current in-world date, season, and status; the initialization gate lives here.
- **`library/2013_league_calendar_and_financial_rules.md`, `library/2013_coaching_market.md`, `library/2013_draft_class.md`** — the first real-data library build (added 2026-09-17): verified 2013 NFL calendar/cap/CBA figures, the real situational picture for all five of Stone's established candidate teams plus the full coordinator-hiring carousel, and the real 2013 draft class's pre-selection-only prospect pool. Every fact is independently cross-checked, with anything that couldn't be confirmed precisely flagged rather than silently presented as exact.

Everything remains **authoring templates; no career is initialized.** Document 3's biographical fields are resolved, but team, contract, season, and coaching-identity fields stay open by design until the user completes Document 1's initialization gate.

## How to use this repo

Read `foundation/01_Project_Instructions.md` first, then the rest of `foundation/` in number order, then `state/`. Do not generate any in-world event until the initialization gate (Document 1 §2, cross-checked against Document 3 §12 and Document 5) is satisfied and the user explicitly says to initialize the career. Once initialized, actual play is written into `career/<year>/`, never into `foundation/` or as a competing format outside the two templates.
