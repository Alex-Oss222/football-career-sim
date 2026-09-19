# Stone offensive playbook — iteration index

This folder holds Alex Stone's authored, team-neutral offensive system across the whole coaching career. It evolves in dated iterations rather than being rewritten in place, so earlier books stay intact as history even after a later one supersedes them.

## Iterations

| Iteration | Effective seasons | File | Status once its range begins |
|---|---|---|---|
| I — 2013 Offensive Playbook | 2013-2015 | `alex_stone_2013_offensive_playbook_iteration_i.md` | Active from 2013 |
| II — Structure and Conflict | 2016-2017 | `alex_stone_2016_2017_offensive_evolution_ii.md` | Locked until 2016 |
| III | 2018-2020 | `alex_stone_2018_2020_offensive_evolution_iii.md` | Locked until 2018 |
| IV | 2021-2022 | `alex_stone_2021_2022_offensive_evolution_iv.md` | Locked until 2021 |
| V | 2023-2024 | `alex_stone_2023_2024_offensive_evolution_v.md` | Locked until 2023 |
| 2025-2026 Mature System (Multiple Stress Offense) | 2025-2026 | `alex_stone_2025_2026_mature_system_multiple_stress_offense.md` | Locked until 2025 |

Effective-season ranges come from each file's own frontmatter (`effective_seasons` / `seasons`). Iteration I runs through 2015 because Iteration II's frontmatter states `effective_seasons: [2016, 2017]` and gives no earlier start.

## The lock rule

Exactly one iteration is **active** at a time: the one whose effective-season range covers the current in-sim year, per `state/05_Current_Season_State.md`'s master clock.

- **Never open, quote, or draw on an iteration whose range starts after the current in-sim year.** That book is offensive theory Stone has not developed yet inside the story. Letting a task consult it — even just for a terminology idea or a personnel-grouping name — would let 2013 Stone call plays he hasn't invented, which is the same integrity problem as importing a real person's future outcome as an answer key (Document 2 §12), just applied to the user's own pre-written future material instead of real-world fact.
- A **past, superseded** iteration may be read for lineage — each book's `inheritance_rule`/`baseline` field points back to the one before it, and that chain is legitimate history — but only the active iteration is live for actual teaching, install work, scouting, or play-calling once its own range has begun.
- The book existing does not mean it is installed. Whether the active iteration's concepts are actually on the field yet is a separate, calendar-gated question — see the install rule below.

## Player access and installation

The active playbook is a real football playbook for human players and coaches. Once issued, **every player may possess and study the complete active iteration**. Players may read ahead, take notes, ask questions about any page, and prepare beyond the current practice menu.

"Installed" has a narrower football meaning: the staff has formally taught, walked through, practiced, and prepared a concept well enough to assign or call it as team football. Installation follows the real CBA offseason-program calendar already established in `career/[year]/offseason/the_prowl_player_readiness_standard.md`. The calendar controls what the club may formally teach and rep together; it does not function as a software lock on what a player is allowed to read.

A player is evaluated on material actually assigned, taught, and practiced for that phase. He is not penalized for failing to master an uninstalled section merely because it exists later in the same active book. Studying ahead is allowed.

## No percentage-driven football

The playbook supplies concepts, assignments, formations, personnel possibilities, protections, tags, and coaching intent. It does **not** pre-decide real football through usage percentages.

- No personnel percentage determines who is on the field.
- No preset snap share determines playing time.
- No touch quota determines carries or targets.
- No depth-chart probability determines who wins a job.
- No playbook percentage decides which concept succeeds.

Practice, minicamp, training camp, preseason, regular-season games, health, matchup, execution, correction retention, and coaching judgment determine what the team actually becomes.

If an authored iteration contains a historical planning percentage or numeric usage center, treat it only as a non-controlling design note. It must never be used as a runtime input to assign snaps, touches, personnel usage, roles, or outcomes. When the football evidence points somewhere else, the football evidence controls.
