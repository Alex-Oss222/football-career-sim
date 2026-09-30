# Release the historical 2014 schedule

**Released April 23, 2014, 8 p.m. ET; recorded in the [ledger](../../ledger.md).** [fixtures.json](fixtures.json) holds the verified 256-game release ([sources and verification](sources.md), [readable view](fixtures.md)). The release does not open the other season release gates.

## Build the league fixture input

Retrieve the actual 256-game release as schedule facts: season, week, local date, Eastern kickoff with correct DST, home/away, venue and neutral-site designation. Exclude scores, players, standings and injury outcomes. Preserve source publication and separately dated flex/revision notices; apply each revision at its historical effective date. Never move a game to improve Jacksonville's matchup, fit an extra practice or match simulated standings.

The generated historical opponent inventory provides reciprocal pairing checks. Historical division order is used for those pairings only; branch receipts continue to own results, playoff qualification and draft order. No branch same-place solver or Buffalo/Miami substitution is needed.

## Acceptance before execution

Require 256 unique games, 32 clubs, 16 games per club, eight designated home/eight away, 17 weeks, at most one game per club per week, one bye and agreement with the historical opponent inventory. Preserve the three sourced London fixtures and neutral-site treatment. Validate kickoff timezone, venue and revision provenance against the historical release. Jacksonville's Week 11 bye and December 18 Thursday game remain fixed.

`fixtures.json` carries season-qualified IDs equal to the runtime event ids, `season: 2014` and `status: RELEASED`, with `usable_from` set to the gate. Later dated amendments (the Week 12 Buffalo relocation and Week 17 flexes) are listed separately and are not applied until their historical dates; two release-slot questions remain open in [sources](sources.md). `tests/test_2014_fixtures.py` runs every acceptance check above. The `dated_fixtures` gate in `runtime/season_readiness.json` is VERIFIED from this release; apply the listed amendments on their historical dates. The current Jacksonville reference contains all 16 games but is not a substitute for the missing full-league executable input.
