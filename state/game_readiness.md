# Game readiness

**Status: 2014 public release requirements VERIFIED; each game still needs its live and weekly checks.** `runtime/season_readiness.json` accepts kernel 2014.6 ([kernel 2014.6 release](../runtime/README.md#kernel-20146-release-october-17-2026), October 17, 2026). As of October 17, 2026 its seven 2014 gates, `tier1_engine`, `season_rules`, `season_closure`, `dated_fixtures`, `legal_rosters`, `financial_control` and `player_state`, all read VERIFIED; `player_state` was bound October 17, 2026 (`library/data/2014_player_state_binding.json`). The readiness file holds each gate's current status and evidence. A game still needs the live private-runtime probe of `python scripts/check_game_readiness.py --season 2014`, the week's frozen call sheet, Stone's game-day inactives and the weekly TeamInput exclusivity gate. See [the 2014 checklist](../career/2014/Supporting_Records/readiness.md).

**Earlier record (October 1, 2026).** This page then read BLOCKED for 2014. Kernel 2014.4 had been verified on the live private runtime September 30, 2026 (`tier1_engine`); `season_rules`, `season_closure` and `financial_control` were verified October 1, 2026 at the August 1 to 4, 2014 clock, the dated fixtures had been frozen from the April 23 release, and `legal_rosters` was verified October 1, 2026 for preseason games only. The regular season then waited on the season depth chart and the Week 1 library's September 7, 2014 gate.

`python scripts/check_game_readiness.py --season 2014` checks those public requirements before any authenticated canary. A successful service response cannot override them. The older table below records legacy implementation evidence, not a 2014 release.

| Requirement | Verified evidence | Executable proof |
|---|---|---|
| Current inputs | Current roster, staff, calendar, medical and phase records remain connected | Repository continuity plus private branch-snapshot binding |
| Era baseline | Independently checked 2012 aggregate, drive, turnover, penalty and special-teams artifact | Deterministic reconciliation and synthetic long-run bands |
| Period rules | 2013 structure, overtime, replay, roster, scoring, kicking, enforcement and ordered tiebreaks | Period-specific rule tests and sourcebook marker probe |
| Injury model | Sourced exposure model with position bands and medical severity/disposition | Deterministic replay, burden, ordering, duration and long-term bounds |
| Resolution implementation | One shared possession kernel with score/clock/stat/participation accounting and pause continuation | Kernel identity, invariant, symmetry and matchup-movement tests |
| Private state | Authenticated external Engine State service with deployment secrets and persistent storage outside Git | Live authenticated schema/procedure/kernel/snapshot/seed-presence/recovery probe plus a repeatable persistent-journal canary; security/restart/idempotence tests |

`python scripts/check_game_readiness.py` is authoritative and fails closed, including when `ENGINE_RUNTIME_URL` or `ENGINE_API_TOKEN` is absent. Manifest labels cannot override failed artifact, implementation, repository or private-service probes. No private seed, ratings, journal packet or opponent plan is returned by the service or stored in Git.
