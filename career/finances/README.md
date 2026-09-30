# Jaguars finances

| Area | Open | Authoritative inputs |
|---|---|---|
| Player contracts and salary cap | [Cap table](jaguars_cap.md), [contract detail](jaguars_contract_details.md) | [Financial inputs](jaguars_cap_inputs.json), [current contract table](../2014/offseason/contract_table.md), [club accounting](../2014/offseason/current_cap_worksheet.md) |
| Organization finances | [Coaching payroll and terms](organization_finances.md) | [Current staff register](../2014/coaching_staff.md), [Stone's accepted contract](../2013/offseason/head_coach_contract.md) |

## Reading the cap table

Current cap summary comes first: the league cap, the working Top-51 reconciliation with the separate dead money and the opening workout charge, and the 2013 rollover as a labeled working estimate. Then the current-player salary and bonus breakdown, annual team totals, position totals, each player's annual obligations, the futures contracts, the dead-money ledger, the draft class with its selections and signings, the decision calendar, expirations and scheduled cash. The main horizon has nine years, 2014 to 2022, followed by three additional years, 2023 to 2025. Dollar amounts are whole US dollars. A blank outside an existing contract is no recorded commitment, not a zero-dollar contract. Unknown accounting is labeled unresolved. Neither unexercised options nor proposed replacements become obligations, and a working difference below the league cap is not certified room.

## The inputs

`jaguars_cap_inputs.json` is the only editable source. Each player carries his control status, term, bonus and guarantee terms, sources and one row for every league year in the horizon; former players keep their history with a departure date and source. `dead_money` lists each departed contract's surviving charge. `draft_picks` lists the selection rights and, once exercised, the selection, its date and the contract signing. `team_years` holds the club accounting that is not yet reconciled (carryover, adjustments, counted salary, reserves), plus two labeled working figures for the current year: `opening_workout_charge` with its worksheet source, and `carryover_working_estimate` as a low-to-high range with the worksheet section that calculates it. The generator validates every schedule against the current roster and contract table before rendering, so a stale checkpoint, a duplicate player, a numeric placeholder or a guarantee that disagrees with its annual rows stops the render.

## Keep one source for each fact

Update the actual signing, amendment, tender, departure or accounting event first, with the current roster/contract views and ledger. Then update the financial inputs for every remaining year. Replace the superseded agreement or tender; do not add the new deal on top of it. Keep departed players' history and surviving liabilities, counted once. Adopted reconstruction amounts remain operative until a specific correction changes them. Scheduled cash, actual payments, remaining guarantees and cap allocation are different figures.

Assistant compensation is generated from the staff register. Do not maintain a second editable staff payroll. Stone's unspecified salary remains unspecified.

## Commands

Run `python scripts/render_jaguars_cap_tracker.py` after every financial change, then `python scripts/render_jaguars_cap_tracker.py --check`, `python scripts/validate_repository.py` and `python -m unittest tests.test_cap_tracker`. The cap, detail and organization pages are generated views; edit the inputs, never the pages. Preserve completed-year inputs and their history when rolling the display forward. Reconcile the successor-year cap rules, carryover, counted salary and sources before certifying room; a year change alone creates no financial event.
