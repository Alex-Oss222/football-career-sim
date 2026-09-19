# Game readiness

**Status: READY / VERIFIED for preseason, regular-season and background game resolution, subject to the mandatory live preflight before each execution.**

This is an administrative readiness assessment, not a simulated event. The career remains August 8, 2013 after the final walkthrough; Miami remains NOT STARTED.

| Requirement | Verified evidence | Executable proof |
|---|---|---|
| Current inputs | Current roster, staff, calendar, medical and phase records remain connected | Repository continuity plus private branch-snapshot binding |
| Era baseline | Independently checked 2012 aggregate, drive, turnover, penalty and special-teams artifact | Deterministic reconciliation and synthetic long-run bands |
| Period rules | 2013 structure, overtime, replay, roster, scoring, kicking, enforcement and ordered tiebreaks | Period-specific rule tests and sourcebook marker probe |
| Injury model | Sourced exposure model with position bands and medical severity/disposition | Deterministic replay, burden, ordering, duration and long-term bounds |
| Resolution implementation | One shared possession kernel with score/clock/stat/participation accounting and pause continuation | Kernel identity, invariant, symmetry and matchup-movement tests |
| Private state | Authenticated localhost-only service with storage under `/var/lib/football-career-sim-engine` and credential under `/run/secrets` | Live authenticated schema/kernel/snapshot/recovery probe; security/restart/idempotence tests |

`python scripts/check_game_readiness.py` is authoritative and fails closed. Manifest labels cannot override failed artifact, implementation, repository or private-service probes. No private seed, ratings, journal packet or opponent plan is returned by the service or stored in Git.
