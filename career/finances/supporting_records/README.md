# Financial supporting records

[Career finances](../README.md)

`financial_inputs.json` is the editable source for player contracts, future schedules, departed-player history, dead money, draft assets and club-level accounting. Each adopted amount retains its basis and source. Assistant salaries come from the executed staff register, so there is no second editable payroll.

After an actual financial event, update the event record, affected current-state views and all remaining years in the inputs. Replace a superseded agreement rather than adding a second copy. Scheduled cash, paid cash, remaining guarantees and cap charges are different figures.

Run `python scripts/render_jaguars_cap_tracker.py`, then its `--check` mode and repository validation. This regenerates the full cap table, individual contracts, coaching payroll, player decision calendar, future commitments and dead-money page from the same sources. Preserve completed-year history when the horizon advances.
