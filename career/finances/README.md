# Jaguars finances

| Area | Open | Authoritative inputs |
|---|---|---|
| Player contracts and salary cap | [Cap table](jaguars_cap.md), [contract detail](jaguars_contract_details.md) | [Existing financial inputs](jaguars_cap_inputs.json), [current contract table](../2014/offseason/contract_table.md), [club accounting](../2014/offseason/current_cap_worksheet.md) |
| Organization finances | [Coaching payroll and terms](organization_finances.md) | [Current staff register](../2014/coaching_staff.md), [Stone's accepted contract](../2013/offseason/head_coach_contract.md) |

## Reading the cap table

Current cap summary comes first, then current-player salary/bonus detail, annual team totals, position totals and each player's annual obligations. The main horizon has nine years, 2014–2022, followed by three additional years, 2023–2025. Dollar amounts are whole US dollars. A blank outside an existing contract is no recorded commitment, not a zero-dollar contract. Unknown accounting is labeled unresolved. Neither unexercised options nor proposed replacements become obligations.

The two screenshots guide the presentation: a cap overview and a player-by-year payroll matrix. There are no invented league rankings, guessed bonus components or trade controls in these documents. An optional cap-only scenario calculation remains separate from recorded totals and creates no new scenario document.

## Keep one source for each fact

Update the actual signing, amendment, tender, departure or accounting event first, with the current roster/contract views and ledger. Then update the existing financial input for every remaining year. Replace the superseded agreement or tender; do not add the new deal on top of it. Keep departed players' history and surviving liabilities, counted once. Adopted reconstruction amounts remain operative until a specific correction changes them.

Assistant compensation is generated from the staff register. Do not maintain a second editable staff payroll. Stone's unspecified salary remains unspecified. Scheduled cash, actual payments, remaining guarantees and cap allocation are different figures.

Run `python scripts/render_jaguars_cap_tracker.py`, then `python scripts/render_jaguars_cap_tracker.py --check` and `python scripts/validate_repository.py`. The cap, detail and organization pages are generated views. Preserve completed-year inputs and their history when rolling the display forward. Reconcile the successor-year cap rules, carryover, counted salary and sources before certifying room; a year change alone creates no financial event.
