# Jaguars financial tracker

[Open the 2014 to 2023 cap table](jaguars_cap_2014_2023.md) | [Individual contract details](jaguars_contract_details.md)

The fixed ten-year view covers every current player, the six signed futures and Monroe’s unsigned tender. Each covered year contains a dollar amount. Years after a deal ends stay blank, as do years before a pending free agent signs a new agreement. A blank is not a zero-dollar contract.

Use researched original contracts and executed branch deals first. Entry 91 adopts realistic simulation terms for missing details under the user’s explicit authorization. Those terms are fixed working inputs, included in position and team totals. The player notes distinguish them from recovered history. Never replace them with generic missing-data labels on the next turn. The [original-contract research](../../library/2014_jaguars_original_contract_reconstruction.md) and [completion research](../../library/2014_jaguars_contract_completion.md) explain the numbers.

## Keeping it current

1. Record each signing, tender, extension, trade, release, retirement or accounting correction in its event owner. Update the contract register/table, relevant current views and ledger together under the [dependency workflow](../../docs/update_workflow.md).
2. Edit [the financial inputs](jaguars_cap_inputs.json), including every remaining annual salary, cap, cash, bonus and guarantee amount, the end year and the source. Preserve the adopted schedule until a specific amendment or correction replaces it. A waiver ends a deal; a later futures signing does not restore the waived salary schedule.
3. Replace affected obligations instead of adding an extension alongside its old contract or counting a tender twice. When a player leaves, retain financial history with `former_player: true`, `departure_date` and `departure_source`. Record any surviving liability in the player row or dead-money register once, never both. Preserve closed-year figures.
4. Keep scheduled player commitments separate from actual cash receipts, club carryover and league adjustments. Do not erase a paid signing bonus’s remaining cap allocation merely because unpaid guarantees are zero. Pending offers, options and future draft picks do not become signed contracts automatically.
5. Run `python scripts/render_jaguars_cap_tracker.py`, `python scripts/render_jaguars_cap_tracker.py --check` and `python scripts/validate_repository.py`. The two Markdown views are generated; change the inputs, not their totals.

The generator checks current roster coverage, current-year contract-table amounts, all covered future years, cap components and remaining guarantees. The horizon is 2014-2023; future turns add actual contract events into the existing columns. The tracker is the financial view, while the roster and depth-chart owners control player status and roles.
