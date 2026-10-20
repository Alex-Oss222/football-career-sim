# Research assessment and six-workflow design checklist

**Scope:** Design packages for the remaining two decisions: every preseason game and final roster cuts, based on `Alex-Oss222/football-career-sim` at GitHub `main` tree `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24`, inspected October 20, 2026. The career is at October 5, 2014, after simulated Jacksonville Week 5. This package is **not** a recorded coaching action, not implemented in GitHub, and not authorization to play a 2015 game or make a transaction.

## Assessment: what is supported

The club already has four completed **simulated** 2014 exhibition games with distinct frozen inputs, game outputs, injury results and preseason-only statistics. Those historical career results are controlled by the branch and remain unedited. The existing `runtime.preseason` compiler, `runtime.rotation` controls, production closer and validation tests supply relevant foundations. The prior eight-section preseason output already includes a story, real coaching analysis, complete generated box score and a cumulative review. The new three-page structure must retain their substance, not replace them with generic narrative or run a second result for one game.

The completed 2014 reduction to 53 documents a lawful **no-cut first deadline** when Jacksonville counted 74 contracted players against 75, then a separate reduction to 53, a next-day waiver process and individually recorded practice-squad agreements. Stone's depth calls and Caldwell's transactions were distinct. The six documented 2014 position battles closed August 30, not automatically after an exhibition performance.

## Assessment: CBA and historical calendar

- The **2011 collective bargaining agreement** and then-applicable 2014 practice-squad expansion, not modern roster or waiver rules, govern this period. Waiver exemption under Article 29 depends on **credited service**. Practice-squad exceptions under Article 33 and the 2014 agreement rely on **accrued seasons** and their distinct tests. No substitute based solely on years since draft is valid.
- The 2015 Jacksonville preseason schedule was announced by the club April 20, 2015: Pittsburgh at Jacksonville August 14, Jacksonville at the NY Giants August 22, Detroit at Jacksonville August 28 and Jacksonville at Washington September 3, each with the established kickoff. Publication date controls what can appear in an earlier briefing.
- The NFL's May 19, 2015 extra-point rule changes the kicked try to the 15-yard-line snap, leaves two-point attempts at the 2, and allows defensive two-point returns. The released 2014 preseason rules may not be reused unmodified for 2015.
- **September 1, 2015 before 4 p.m. ET** is the 75-player limit, before preseason game four on September 3. **September 5 before 4 p.m. ET** is the 53-player filing, with the September 6 noon waiver checkpoint and later practice-squad window. A single end-of-August reduction would be incorrect.

## Specific implementation blockers

1. In `runtime.decisions.py`, the two unimplemented decisions `preseason_game` and `final_cuts` use a shared path that currently resolves to the *parent* `Training_Camp_and_Preseason` folder. The new plans need kind-specific routing: four `Preseason_Games/Game_0N/` triplets and the separate `Roster_Decisions/` cutdown triplet.
2. `scripts/close_preseason_game.py` currently owns the older `output.md` rendering. The new `Preseason_Game_Report.md` must become the only reader-facing owner for **future** games while frozen 2014 output bytes remain unchanged. Existing statistics and event records must not be double-written.
3. The 2014 game release does not prove a valid 2015 released game environment. The 2015 rules, medical status, opponent rosters, personnel, rotation, fixture and gameplay inputs require their own readiness gates and date limits. The remainder of 2014 has not been simulated.
4. A new decision-queue block is needed for a particular preseason game freeze and close, while a separate event-specific gate is needed at 75 and 53. Unrelated personnel business should not block independent events; a real roster dependency must.
5. The current 2014 practice and roster documents are histories, not machine-writable 2015 outcomes. Individual medical, contract, waiver and signed-player dispositions must be legally verified, idempotent and stored at the correct source of truth.
6. The current 2014 examples are **not** scripts for 2015 player development, camp grades, other clubs' transactions or waiver outcomes. The 2015 roster is not available at the October 2014 simulated date. Training-camp work and draft/cap outcomes must actually occur before they can appear.
7. For every separately resolved matter, including one player's cut, a rejected trade, a failed waiver claim or an unsuccessful practice-squad pursuit, generate **one separate dated result**. Main phase summaries link each result. A two-person injury case or twenty-person cutdown must not collapse into one invented universal result.
8. Final roster ownership belongs to Caldwell. Stone owns team depth, playing roles and game-day inactives and can advise on acquisition and retention. Medical personnel decide clearance. The 53 does not determine the dressed 46 or appoint the next available player automatically.

The package spells out **56 proposed preseason-game tests** and **68 proposed cutdown tests**, plus acceptance scenarios. These tests have **not** been run against GitHub and are not a claim that the workflows have been installed.

## Design checklist

| Order | Workflow | Research and downloadable design | GitHub implementation |
|---:|---|---|---|
| 1 | April Offseason Program | Complete in prior package | Not established by this work |
| 2 | NFL Draft | Complete in prior package | Not established by this work |
| 3 | May–June OTAs and Minicamp | Complete in prior package | Not established by this work |
| 4 | Training Camp Position Battles | Complete in prior package | Not established by this work |
| 5 | Every Preseason Game | **Complete in this package: ten documents** | **Not implemented** |
| 6 | Final Roster Cuts | **Complete in this package: ten documents** | **Not implemented** |

**Remaining design workflows:** none of the original six. **Remaining engineering work:** implementation and validation of all workflows not already demonstrably installed in GitHub, beginning with the specific routing, record-ownership, legality and date gates described above. Nothing in this research package creates a pull request, executes a roster move or advances the career clock.

## Primary sources

1. [August 4, 2011 NFL/NFLPA collective bargaining agreement, Articles 23, 29, 33](https://nflps.org/wp-content/uploads/2012/05/collective-bargaining-agreement-2011-2020.pdf).
2. [NFLPA, NFL–NFLPA agreement expanding practice squads](https://nflpa.com/press/nfl-nflpa-agree-to-expand-practice-squads), August 19, 2014.
3. [Jacksonville Jaguars 2015 preseason fixture announcement](https://www.jaguars.com/news/jaguars-announce-preseason-schedule-15157774), April 20, 2015.
4. [NFL, 2015 extra-point rule change](https://www.nfl.com/news/nfl-moves-extra-point-to-15-yard-line-for-2015-season-0ap3000000493347), May 19, 2015.
5. [2015 NFL season key dates, Seahawks](https://www.seahawks.com/news/nfl-announces-important-dates-for-2015-2016-126071), July 2015; verify league date against contemporaneous reports.
6. Existing repository's `career/2015/Calendar.md`, `library/2015_historical_calendar.md`, `docs/rebuild_plan.md`, `docs/event_inserts.md` and the closed 2014 game/roster owner pages. These are described with precise paths in each package's technical specification.
