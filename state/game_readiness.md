# Game readiness

**Status: BLOCKED for 2014.** The season-specific release gate in `runtime/season_readiness.json` remains open independently of private-service availability. Kernel 2014.4 carries E1/E2 and the other Tier 1 fixes (release wired September 30, 2026) but the live private runtime is not yet verified on it; applicable 2014 rules, legal inputs, financial/control reconciliation and a full isolated closure still need acceptance. The dated fixtures were frozen from the April 23 release. See [the 2014 checklist](../career/2014/supporting_records/readiness.md).

`python scripts/check_game_readiness.py --season 2014` checks those public requirements before any authenticated canary. A successful service response cannot override them. The older table below records legacy implementation evidence, not a 2014 release. This environment also lacks the live URL/token, so the deployed version/snapshot cannot be certified here.

| Requirement | Verified evidence | Executable proof |
|---|---|---|
| Current inputs | Current roster, staff, calendar, medical and phase records remain connected | Repository continuity plus private branch-snapshot binding |
| Era baseline | Independently checked 2012 aggregate, drive, turnover, penalty and special-teams artifact | Deterministic reconciliation and synthetic long-run bands |
| Period rules | 2013 structure, overtime, replay, roster, scoring, kicking, enforcement and ordered tiebreaks | Period-specific rule tests and sourcebook marker probe |
| Injury model | Sourced exposure model with position bands and medical severity/disposition | Deterministic replay, burden, ordering, duration and long-term bounds |
| Resolution implementation | One shared possession kernel with score/clock/stat/participation accounting and pause continuation | Kernel identity, invariant, symmetry and matchup-movement tests |
| Private state | Authenticated external Engine State service with deployment secrets and persistent storage outside Git | Live authenticated schema/procedure/kernel/snapshot/seed-presence/recovery probe plus a repeatable persistent-journal canary; security/restart/idempotence tests |

`python scripts/check_game_readiness.py` is authoritative and fails closed, including when `ENGINE_RUNTIME_URL` or `ENGINE_API_TOKEN` is absent. Manifest labels cannot override failed artifact, implementation, repository or private-service probes. No private seed, ratings, journal packet or opponent plan is returned by the service or stored in Git.
