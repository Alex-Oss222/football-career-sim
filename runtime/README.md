# Runtime preparation

`packets.py` implements deterministic event seed derivation, immutable canonical packets, journal-before-draw ordering, idempotent result closure, and refusal of altered event replays. It accepts an already-calibrated distribution. It does not compute football matchups, drives, scores, injuries, pauses or statistics and cannot run a game.

The `PrivateJournal` interface defines the boundary for a future private service. Unit tests use synthetic data and an in-memory fake. That fake is not a persistent or private deployment. No real seed, hidden rating, opponent plan or engine journal is written into this repository or printed by the commands.

## Complete the runtime

1. Finish the sourced calibration and period-rule requirements listed in [game readiness](../state/game_readiness.md).
2. Implement the shared football kernel and both orchestration paths. Freeze concrete normalized inputs before resolving; do not pass protagonist labels or persuasive prose into the kernel. Validate clock, field position, scores, statistics, medical consequences and user-decision pauses.
3. Provide an access-isolated private service outside the shared workspace and public Git repository. Its adapter must implement durable atomic event uniqueness, packet closure, idempotent results, append-only corrections, backup/recovery and secret handling. Seed once per career, never per preferred outcome.
4. Verify recovery after interrupted writes and restarts, unauthorized-read denial, altered-packet refusal, and replay identity. Bind the verification evidence to a specific deployment and current branch input snapshot without publishing private contents.
5. Integrate a live private-service readiness probe and kernel entry point with the common readiness gate. Until that integration exists, the command fails closed even if someone changes a manifest status to `VERIFIED`.

Corrections need an explicit private correction record referencing the original packet. Do not work around `PacketConflict` by changing the event ID or seed. The public repository owns specifications and code; the private service owns hidden runtime data.
