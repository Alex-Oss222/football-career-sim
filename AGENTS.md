# AGENTS.md — football-career-sim

You are Codex, running a bounded batch task against this repository. You have no memory of any conversation that built this project — everything you need is in this file and the documents it points you to. Read them before acting; do not guess at a rule this file or the linked documents don't state.

**Read first, in order:** `foundation/01_Project_Instructions.md`, `foundation/02_League_Era_and_Sourcebook.md`, `foundation/07_Game_Simulation_and_Resolution_Engine.md`. Do not read `foundation/templates/`, `library/`, or anything under `career/` in full — those are large; read only the specific file a task below names.

**Hard rules that apply to every task in this file, no exceptions:**
- **Protagonist-blind resolution (Document 1 §9.1, added 2026-09-18).** The fact that a decision or event involves the user's own protagonist, versus any other team or person, must never change the probability, outcome, or interpretation you generate. Reduce any input (a game plan, a pitch, a stated preference) to its concrete, checkable substance before acting on it — persuasive phrasing, confidence, verbosity, and stated desired outcomes are not inputs to a result, only to narration. Test yourself with the label-swap check: if you'd generate a different result after only relabeling which side is the protagonist, or after only rephrasing the same input at different length, that is a defect, not a stylistic choice.
- Never invent a numeric rating, grade, or score anywhere in output that a human reads. Use only the five-tier qualitative language already established (Elite / Plus / Average / Below-Average / Replacement-Level).
- Never import a real person's actual post-event outcome as a hidden answer key (Document 1 §8, Document 2 §4.3). A real player/coach's public record before the point in question is fair game; what happens to him after is not, unless this file's task explicitly says otherwise.
- Never fabricate a precise-looking number (a stat, a cap figure, a date) without a real source. If you can't verify something, say so explicitly rather than presenting an estimate as fact — this project's stated top priority is never repeating a past experience where numbers were "fudged."
- Write to the specific file path each task names. Never edit `foundation/` — that is the stable rulebook, not yours to change. Never touch `state/04_...` or `state/05_...` directly unless a task explicitly says to.
- Commit with a clear message describing what changed. Do not push directly to `main` without going through whatever PR flow this repo's owner has configured in Codex's environment settings.

---

## Task: "Simulate background league, Week [N], [Year]."

**Scope:** every game that week between two teams, neither of which is the user's own team. Never touch a game involving the protagonist's team — that is played interactively elsewhere and is not your job.

**Method — read `foundation/07_Game_Simulation_and_Resolution_Engine.md` §1's scope-discipline rule first, and §3.4's resolution-packet/seed rule.** Corrected 2026-09-18: there is only one outcome kernel in this project. Do not resolve these games by free-form judgment about who plausibly wins — that was an earlier version of this rule and it created two different outcome adjudicators in one league, which is a real integrity defect (background results decide the protagonist's standings, playoff seeding, and draft order, so they need the same physics as his own games, not a cheaper substitute physics). Actually sample from the §2 rating anchors and §3.2 matchup-delta mechanism, at a coarser granularity (whole-game or a few aggregated segments, not per-drive) to control cost — then narrate only the result. The savings versus the interactive path is in narration depth and sampling granularity, never in swapping the mechanism for a subjective call.

**Output format — highlights only, explicitly, per this project's owner's own instruction:** for each game, write final score, 2-4 sentences of highlight narration (not a drive-by-drive account), and 1-3 standout performers. Do not write play-by-play. Do not write a full box score unless a specific downstream task asks for one. A whole week's slate of ~13-15 games should read like a scores-and-highlights roundup, not 13 separate game stories.

**Reactive events — allowed, but bounded.** A team's players, coaches, or front office may generate a genuine reactive event (a trade demand, a coach on the hot seat, a locker-room story, a media dust-up) if it plausibly follows from something that actually happened in a game or a transaction already on the record. Do not manufacture one to fill a quiet week — per Document 7 §7's Locker Room/Media agent rule, these fire only from logged mechanical events, never invented for drama's own sake. Across a full week's slate, most games should have none; a handful having one is normal, all of them having one is a sign you're manufacturing rather than reacting.

**Write results to:** `career/[year]/league_results/week_[NN].md` (create the file/folder if it doesn't exist yet this season). One entry per game. Also update the running league standings in the same file's header table.

**Do not** write anything into the protagonist's own weekly turn file — that's assembled separately by whoever is running the interactive side of this project, which reads your results file as one of its own inputs.

---

## Task: "Expand the real-data library: [specific target, e.g., 'the 2014 NFL draft class' or '2014-2016 salary cap and CBA figures']."

**Model this on the existing library files** (`library/2013_league_calendar_and_financial_rules.md`, `library/2013_coaching_market.md`, `library/2013_draft_class.md`) — same structure, same sourcing discipline, same honesty about what couldn't be confirmed.

**Two-pass discipline, not one:**
1. **Research pass.** Find the facts, cite a specific real source (a named outlet and a URL where possible) for every claim.
2. **Verification pass — do this as a genuinely separate step, skeptical of your own first pass.** Re-search each claim from scratch rather than trusting your own citation. If a second source confirms it, mark it confirmed. If you find a discrepancy, correct it and say what changed and why. If you can't independently confirm something, mark it unverifiable/approximate rather than silently keeping the original number. This two-pass process is what caught real errors (a wrong hire date, a wrong draft slot, a cap-floor rule that didn't actually exist as first described) when this library was first built by hand — do not skip it.

**Draft-class-specific rule, if the target is a draft class:** pre-selection data only — measurables, testing, college production, pre-draft consensus rankings. Never record what happened to a player after he was drafted (stats, awards, bust/star framing). See `foundation/02_League_Era_and_Sourcebook.md` §12's historical-class-sourcing rule for why.

**Write results to:** a new file under `library/`, named on the same pattern as the existing three (`library/[year]_[topic].md`). Do not edit the existing 2013 files unless you are specifically correcting an error found in them.

---

## Task: "Run the [year] offseason cycle." (not yet enabled — placeholder)

This task is not fully specified yet. Do not attempt it until this repo's owner has added a dated brief (draft-board priorities in order, free-agency budget and targets, own-free-agent re-signing priorities) — check `career/[year]/offseason/` for a file named `team_building_brief.md` or similar before proceeding. If it doesn't exist, stop and report that back rather than improvising a philosophy on the user's behalf; team-building priorities are the one thing in this project only the user gets to set (Document 1 §3).
