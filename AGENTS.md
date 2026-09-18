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

**Availability gate:** this task is disabled until `foundation/07_Game_Simulation_and_Resolution_Engine.md` is marked runtime-ready, its §8 era calibration is complete for the season being played, and the private Engine State store has been instantiated. If any of those conditions is missing, stop without generating scores.

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

For historical draft work, preserve **information timing**, not just a final cutoff. Model 2013 on `library/2013_draft_information_gates.md`: declarations, combine invitations/results, pro days, medical/workout updates, and final boards become runtime-eligible only on their dated release/event. Eligibility/pool coverage belongs in a separate registry such as `library/2013_draft_pool_registry.md`; do not infer eligibility from who was eventually drafted or signed.

**Write results to:** a new file under `library/`, named on the same pattern as the existing three (`library/[year]_[topic].md`). Do not edit the existing 2013 files unless you are specifically correcting an error found in them.

---

## Task: "Run the [year] hiring search."

This is the bounded pre-hire phase that may run before full career initialization. It produces organization-side developments and records the user's own already-authorized career choices, but it never invents a choice for Alex Stone.

**Prerequisite.** `career/[year]/offseason/hiring_search_brief/` must contain the user's own instructions covering the teams to pursue, priority/order, material terms or non-negotiables, concessions, and walk-away conditions. If a material choice is not covered, stop at that branch and report what decision is needed.

**Read, in this order:**
1. `foundation/03_Head_Coach_Organization_and_Authority_Canon.md` §10.
2. `foundation/templates/hiring_search_output_template.md`.
3. `library/alex_stone_character_dossier_pre_hire.md`, using its factual record and §11 evidence boundaries only. It does not supply Stone's interview answers, motives, philosophy, or negotiating preferences.
4. `library/2013_coaching_market_pre_hire.md`.
5. Only after the criteria freeze described below is written, read `career/[year]/offseason/hiring_search_brief/`.

**Do not load `library/2013_coaching_market.md` while resolving this search.** That file contains quarantined actual-future outcomes and is for research/audit only.

**Criteria freeze before the brief.** Before opening the user's brief, write a `Criteria freeze` entry into `career/[year]/offseason/hiring_search.md` for every organization already established in Document 3's search scope. Use only the pre-hire market file. Record documented needs and constraints, identify any labeled inference, and leave unsupported private weighting unknown. This entry is the pre-hire equivalent of Document 1 §9.4's ex-ante record and must close before Stone's pitch or terms are evaluated.

**Procedure:**
1. Reduce the user's brief to concrete terms. Persuasiveness, length, confidence, and desired outcome are not resolution inputs.
2. Resolve organization-side actions from the frozen criteria: interest, interview requests, rejection, second-stage requests, negotiation positions, counters, deadlines, and offers.
3. Routine scheduling and administrative implementation may proceed without another user turn when directly authorized by the brief.
4. A consequential Alex Stone choice remains user-controlled unless the brief contains an explicit standing instruction that covers the exact branch. Examples that require user control unless expressly pre-authorized: agreeing to a materially new interview condition, changing a non-negotiable, making a new promise, accepting a counter outside the stated range, accepting an offer, declining an offer, or choosing between simultaneous offers.
5. A walk-away rule in the brief may be executed automatically only when the triggering condition is objectively satisfied as written.
6. An acceptance rule may be executed automatically only when the exact offered terms satisfy an explicit pre-written acceptance condition. "Team is my first choice" is not by itself authorization to accept any contract.
7. Never use the eventual real hire, later coordinator staff, later roster move, or later career outcome as an answer key.
8. If every team resolves without a hire, close the search as `NO HIRE`. If a user-authorized acceptance occurs, close it as `HIRED — INITIALIZATION BUILD REQUIRED`. Do not begin roster, staff, game, press-conference, or season play.

**Persistence and ex-ante discipline.** Write every criteria freeze, user instruction relied on, material organization-side development, unresolved user decision, offer, and final search status to `career/[year]/offseason/hiring_search.md`. During this pre-hire phase that file is the authorized decision ledger. Do not write simulated hiring events into Document 6 before career initialization.

**Do not** edit Document 3, Document 6, or the state files as part of this batch task. After the search concludes, the interactive initialization build reconciles the accepted outcome into Documents 2–6 before active career play.

---

## Task: "Run the [year] offseason cycle." (not yet enabled — placeholder)

This task is not fully specified yet. Do not attempt it until this repo's owner has added a dated brief (draft-board priorities in order, free-agency budget and targets, own-free-agent re-signing priorities) — check `career/[year]/offseason/` for a file named `team_building_brief.md` or similar before proceeding. If it doesn't exist, stop and report that back rather than improvising a philosophy on the user's behalf; team-building priorities are the one thing in this project only the user gets to set (Document 1 §3).
