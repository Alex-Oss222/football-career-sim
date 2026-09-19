# Phase record maintenance template

This template describes repository records. It does not replace the approved in-world response formats.

## Output

Start with a `sim-meta` JSON comment declaring `kind: phase_output`, `status` (`NOT_STARTED`, `IN_PROGRESS` or `COMPLETE`), `through` (ISO date or null), and `event_entry` (season-ledger entry or null). Follow it with a human-readable overall status, links to the plan/calendar/standouts, and dated event sections.

Each actual section records authorization, participants/control, fresh medical communication, work performed, observed evidence, actual decisions, dependencies affected or unchanged, and the next event. Preserve old dated statements as history.

## Standouts

Use `kind: evidence_summary`, the matching status/date, the repository-relative output `source`, and SHA-256 of the complete reviewed source file as `source_sha256`. Record person/unit, observed work, source section, improvement or remaining question, and limits. Never infer a permanent role from a practice summary.

Review the actual new evidence before refreshing the digest. Changing a digest alone is not a completed update. An empty future summary is permitted only while its output is `NOT_STARTED`.

## Plans

Keep a durable-plan label and links to results. Do not duplicate the changing execution status inside the plan. Revise teaching content only when the user changes it.
