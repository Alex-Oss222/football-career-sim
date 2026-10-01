# Season review and 2015 (after Jacksonville’s final game)

**NOT_STARTED.** [The handoff manifest](season_handoff.json) is the single checklist and source map. Do not create a second transition packet. After Jacksonville's final actual game, close team reviews and player/staff exit interviews, then stage the next year. League postseason, awards and statistics may still need later closure; keep those gates visible without freezing permitted team offseason work.

## What transfers

| Record | Treatment at the year boundary |
|---|---|
| Player contracts | Preserve every remaining salary, bonus allocation, guarantee, option, tender status and expiry. Reconcile actual service/escalator triggers. No automatic extension or release |
| Player cap | Preserve dead money and future obligations; verify the new league cap, carryover election, adjustments, Top-51/full-roster transition and actual cash. Unknown room remains unknown |
| Organization finances | Carry Stone/coordinator/position-coach terms, paid and unpaid compensation, remaining guarantees and verified offsets; retain pending renewal decisions |
| Roster, roles and depth | Carry controlled players and supported assignments, distinguish unsigned rights, expired deals and pending choices. Reconcile on actual effective dates; opening working depth is not a legal game roster |
| Medical and availability | Preserve holds, restrictions, projections and the clearance authority. A January date or new folder never clears a player |
| Draft and league ownership | Carry future traded/conditional picks and prior ordinal swaps. The k-th actual Jacksonville selection pairs with the k-th historical Jacksonville pick, not the same round; follow existing collision rules |
| Player and coach development | Carry demonstrated strengths, unresolved corrections, delivered/undelivered feedback and next legal observation. Do not reset returning players to rookie status |
| Stats, awards and history | Keep prior receipts, standings, awards and season summaries under their original season. New-season counters start with no receipts; career history links closed seasons rather than duplicating totals |
| Calendar and rules | Source the next historical calendar and dated changes. Actual games/dates/byes stay historical; players, outcomes and playoff qualification remain branch-dependent |

## Close and stage

1. Run `python scripts/season_handoff.py prepare 2014` once. Repeating it preserves work already entered. Every future active season uses the same command with its year.
2. Complete each team gate in the existing review/event owners. Record the evidence path and SHA-256 in the manifest only after reviewing it. Set each completed gate to `COMPLETE`; leave unfinished league-statistics/award gates open until their real closure. Add unresolved user decisions to `pending_decisions`.
3. At the actual team closeout, freeze every carry-forward source hash in `source_sha256` and set `status` to `TEAM_CLOSED`. Source changes require reconciliation and renewed review. Run `python scripts/season_handoff.py check 2014`.
4. Verify the historical 2015 calendar, then run `python scripts/season_handoff.py stage 2014`. This writes a successor baseline and opening manifest, rebases evidence links, preserves prior files and refuses to overwrite different existing content. It preserves player cards with their earlier-year regular-season and playoff rows, while copying no prior-season team totals, award outcomes or game receipts into new-season counters.
5. The next administrative event reconciles opening contract years/expiry, medical/roles, league assets, financial owners, both state documents and `docs/repository_map.json` together. Record its completion at the relevant source, link prior history, and regenerate the annual `Record.md` and age/finance views. Staging deliberately leaves live ownership unchanged until that event is closed. Codex performs this bookkeeping; Stone retains the consequential football and contract choices.
6. Prepare the new active year's handoff in the same way. 2015→2016 follows the same route. Source the historical 2016 calendar when preparing that year; do not populate it with invented dates or open future playbooks now.

## Simulation after transfer

Passing a handoff check does not release games. Each season needs its own registered kernel, era rules, fixtures, legal rosters, financial control and closure acceptance. The existing six game-release gates remain in force. Stats and receipts are always season-qualified, and a missing successor input never falls back to 2013. The user's choice to start the next season cannot silently select draft targets, renew contracts, change roles or clear injuries.

<!-- folder-files -->
## Files in this folder

| File | What it contains |
|---|---|
| [season_handoff.json](season_handoff.json) | The annual review checklist, sources and uncompleted carry-forward decisions. |
