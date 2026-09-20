# Football runtime

`game_runner.py` is the only production game entry point. It validates normalized roster-bound inputs, creates one canonical packet, closes that packet through the authenticated private service, domain-separates the returned opaque event reference into kernel entropy, invokes `kernel.py`, and rejects any result that fails kernel invariants. It has no caller-supplied seed parameter. Interactive and background names are aliases of this same runner; low-level `kernel.py` access exists only for synthetic calibration tests.

`player_evidence.py` supplies roster-aware participation, position-correct statistical attribution, sparse qualitative observations, and separate assignment, communication, processing, technique, physical execution, observable effort, correction, medical, teaching, and special-teams fields. Rotation status and actual football roles guide opportunity without hardcoded snap shares or roster-survival probabilities. `calibration.py`, `rules.py`, `injuries.py`, and `anchors.py` supply deterministic period inputs, medical events, and private evidence conversion. `packets.py` retains canonical journal-before-draw sampling support.

`private_service.py` is the authenticated Engine State reference service. Its persistent volume and bearer credential stay outside the repository. The store seeds the career once, binds the current branch snapshot and kernel/schema identity, journals immutable event identifiers before closure, refuses altered packets, supports idempotent replay, records corrections append-only, and exercises a recovery digest during readiness. Event closure has one identity source: the canonical packet's `event_id`. Production `/events/close` is bodyless: the authenticated POST carries only URL-encoded `event_id` plus `packet_sha256`, where the digest is computed from canonical packet JSON locally. The private service journals that immutable identity and never needs packet contents. Older flat/wrapped JSON bodies remain compatibility-only paths and may never override packet identity. The current production write API is bodyless end-to-end: event closure, administrative canary, compare-and-swap snapshot advancement, and correction recording use authenticated POSTs whose validated inputs are URL-encoded where needed. JSON request bodies exist only as backward-compatibility paths for older clients. The API never exposes the seed, packet contents, ratings, or journal rows.

The public adapter reads `ENGINE_RUNTIME_URL` and `ENGINE_API_TOKEN`; the older local token-file variables remain available only for local service tests. No secret belongs in Git. `python scripts/check_game_readiness.py` validates repository continuity, artifacts, shared-kernel identity, exact current-state snapshot, the real `/events/close` path with a reserved contract-derived administrative event whose identity changes with the canary payload contract, and the authenticated live deployment. It fails closed on missing environment variables, credentials, service loss, schema/procedure/kernel mismatch, absent private seed, snapshot mismatch, non-idempotent event closure, or failed recovery. After an atomic canon-changing commit, run `python scripts/advance_private_snapshot.py CHECKPOINT` to compare-and-swap the private binding to the actual Document 5 digest; transition history remains private and append-only.

`Dockerfile.engine` runs `scripts/validate_repository.py` and the full unit-test suite in a verification stage before producing the runtime image; a validation or test failure therefore blocks Railway deployment.

Preseason uses the consolidated-block architecture: Document 5 may remain at the block-start snapshot while the four uniquely identified game packets are closed sequentially. Every packet must be rebuilt from the then-current roster, medical, availability, and role inputs. No later game may reuse stale football inputs; the final atomic public closure advances Document 5 once, after which the explicit snapshot helper advances the private binding.


## Public season statbook

`runtime/statbook.py` is downstream post-processing for already-closed games. It converts a closed game result into a public stat-only receipt and can aggregate those receipts into season totals. It has no access to the private career seed and does not participate in resolution, packet closure, matchup weighting or outcome selection.

Current Markdown views are rendered from the receipt set with `scripts/render_season_stats.py`. Incomplete legacy receipt coverage must remain labeled and formal league leaderboards are withheld until the gap is reconciled.


## Kernel 2013.3 snap-detail contract

Kernel 2013.3 keeps score/outcome generation at the possession layer and adds a deterministic public detail stream after each drive is resolved.

- `runtime/play_detail.py` allocates a resolved drive into public snap rows without consuming the possession RNG.
- `TeamInput.offensive_call_sheet` carries the structured weekly call menu used for named-call accounting.
- Display aliases are excluded from the football-substance outcome commitment, so rewording a call label does not change the score draw.
- `play_ledger` records every generated scrimmage snap plus scoring/punt/kickoff terminal plays.
- `play_call_stats` aggregates named offensive call usage for the closed game.
- The player dictionary now supports passing, rushing, receiving, protection, defense, kicking, punting and return counters.
- `runtime/statbook.py` stores player stats, the full snap ledger and named-call totals in each public game receipt and accumulates them across the season.

The snap-detail layer is public post-resolution accounting. It never receives the private career seed directly outside the kernel call, and it cannot alter the already-resolved drive outcome.
