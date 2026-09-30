# Release the historical 2014 schedule

**Prepared; no games released for execution.** Historical dates and pairings are selected under Entry 101. Public release remains April 23, 2014, 8 p.m. Eastern. Researching dates ahead does not create opponent preparation or advance the clock.

## Build the league fixture input

Retrieve the actual 256-game release as schedule facts: season, week, local date, Eastern kickoff with correct DST, home/away, venue and neutral-site designation. Exclude scores, players, standings and injury outcomes. Preserve source publication and separately dated flex/revision notices; apply each revision at its historical effective date. Never move a game to improve Jacksonville's matchup, fit an extra practice or match simulated standings.

The generated historical opponent inventory provides reciprocal pairing checks. Historical division order is used for those pairings only; branch receipts continue to own results, playoff qualification and draft order. No branch same-place solver or Buffalo/Miami substitution is needed.

## Acceptance before execution

Require 256 unique games, 32 clubs, 16 games per club, eight designated home/eight away, 17 weeks, at most one game per club per week, one bye and agreement with the historical opponent inventory. Preserve the three sourced London fixtures and neutral-site treatment. Validate kickoff timezone, venue and revision provenance against the historical release. Jacksonville's Week 11 bye and December 18 Thursday game remain fixed.

Publish `career/2014/schedule/fixtures.json` only after complete source verification, with season-qualified IDs, `season: 2014` and `status: RELEASED`. Regenerate readable views from that data and pass the existing game release gates. The current Jacksonville reference contains all 16 games but is not a substitute for the missing full-league executable input.
