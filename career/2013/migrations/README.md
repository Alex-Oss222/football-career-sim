# 2013 migrations

Closed technical migration records of the 2013 season. They are frozen history; the [2013 index](../README.md) links the Week 1 restart and reset.

| File | What it records |
|---|---|
| [week_01_kernel_2013_4_restart.md](week_01_kernel_2013_4_restart.md) | Week 1 restart under kernel 2013.4 (closed; generation 3) |
| [week_01_full_fidelity_reset.md](week_01_full_fidelity_reset.md) | Week 1 full-fidelity reset (superseded audit history of generations 1 and 2) |
| [week_01_full_fidelity_reset.json](week_01_full_fidelity_reset.json) | Control metadata for the Week 1 reset |
| [week_14_generation_void.md](week_14_generation_void.md) | Week 14 generation-1 void (closed; replayed as generation 2) |
| [event_generations.json](event_generations.json) | Voided and current event generations, read by `scripts/void_week_generation.py` |
| [injury_projection_recovery.json](injury_projection_recovery.json) | The audited injury-projection recovery, written by `scripts/recover_injury_projection.py` |

**Retired helpers.** The Week 1 helpers these records name, `scripts/check_week1_reset_ready.py` and `scripts/mark_week1_generations_void.py`, were retired in commit e04dd82 (September 27, 2026) after closure. Recover either with `git show e04dd82^:scripts/NAME.py`.
