# Archive

This directory holds superseded, historical, or quarantined material that must not participate in normal runtime resolution.

- `00_Audit_Migration_and_Stress_Test_Report.md` documents the 2026-09-17 rebuild that removed the incompatible legacy project layers. It is historical reference only, not a runtime instruction source.
- `2013_coaching_market_historical_comparator.md` preserves the real later 2013 coaching hires, staffs, and hindsight research. It is excluded from normal hiring-search input.
- The abandoned earlier Chicago test career is not imported into active canon or `career/`. Git history and external user records may preserve it, but normal simulation tasks do not load it.
- Discarded coaching-philosophy drafts and other external personal working files are not runtime dependencies and are not referenced by local machine paths.

- `02_League_Era_and_Sourcebook_authoring_0.6.md` preserves the superseded authoring master, including unused templates and the Detroit candidate. Do not load it during normal play.
- `2013_jacksonville_historical_retirements.md` and `.json`: explicitly requested retirement audit; quarantined actual-future comparator, never a runtime input. Branch retirements come only from their own closed events (rails rule 5 applies retirements on their real dates through the rails, not from this file).

### Uploads and retired tools (moved October 17, 2026)

- `uploads/2026-10-02_football_snap_estimates/`: uploaded October 2, 2026 (commit 6fa033a) as `docs/football_snap_estimates (1)/`. Not used: the estimates were fitted with full-season 2014 data, beyond the information gate. See [the 2014 engine decisions](../runtime/2014_engine_decisions.md#the-uploaded-snap-estimates-and-evidence-builder-not-used-in-20146), section "The uploaded snap estimates and evidence builder: not used in 2014.6".
- `uploads/2026-10-02_free_nfl_evidence_build/`: uploaded package (same commit 6fa033a), formerly the doubly nested `docs/free_nfl_evidence_build/free_nfl_evidence_build/`. Not adopted (same decision-record section); kept for reference by a future committed builder. Not run by CI: the test runner discovers only `tests/`.
- `scripts/migrate_season_layout.py` and `scripts/test_layout_migration.py`: the 2014 layout migration, applied in a953aa5 (September 30, 2026). The script was generic for seasons 2014 to 2100 but is retired because new seasons are staged directly in the readable layout. Not runnable from the archive; the layout helpers stay tested in `tests/test_season_layout.py`.

Nothing in `archive/` overrides `foundation/`, `state/`, the active pre-hire ledger, or closed career history.
