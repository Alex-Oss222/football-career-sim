# Release and freeze the 2014 schedule

**Prepared, not executed.** Opponents are known now. The [calendar](../calendar.md) gates preseason pairings to April 9 and the complete regular schedule to **April 23, 2014, 8 p.m. ET**. The three November 2013 London announcements are already usable. No game is scheduled by this plan.

## April 23 work

1. Recheck the [generated opponent matrix](league_opponents.json) against the closed 2013 branch receipts. The ordinary draft coin flip does not determine division place. Freeze the current matrix and source digests.
2. Retrieve the historical release as **schedule facts only**: date, local/ET kickoff, week, venue, designated home/away and the announced bye. Exclude scores, records, injuries, lineups and subsequent flex changes. Preserve release provenance and its dated revision.
3. Compare all 256 released pairings with the branch matrix. Keep compatible fixture placements and the three fixed London dates. Reassign conflicting same-place games as a league-wide problem; do not patch just Jacksonville. Historical Week 11 bye and Week 16 Thursday are candidates until reconciliation validates them. No schedule change may be selected for Jacksonville's competitive benefit.
4. Use a deterministic, documented reconciliation policy with the same constraints for every club. Prefer the smallest set of changes from the released calendar subject to feasibility. Preserve stadium availability and existing fixed events, legal rest/travel, broadcast commitments that still apply, division home/away and one game per club per week. If a historical broadcast slot cannot survive a pairing change, explicitly record the change rather than inventing network consent.
5. Publish the 256 dated branch fixtures, each with stable ID, season, week, date/time/timezone, clubs, designated home, venue/neutral flag, source and any branch adjustment. Publish the 32 bye assignments and a short adjustment audit. The readable Jacksonville week index and calendar must derive from the frozen data; no manually independent schedule.
6. Connect the season-aware runtime loader to this 2014 source and reject a 2013 fallback for a 2014 request. Refresh closure/readiness, standings and receipt-coverage consumers for the requested season before executing any 2014 game. Preserve prior 2013 reproduction.

## Required acceptance before freezing

- Exactly 256 games, 32 clubs, 16 games per club, eight designated home/eight away, and exact multiset equality to the opponent matrix.
- Seventeen league weeks, at most one game per club per week, exactly one bye for each club, and no duplicate fixture IDs.
- Six division games, four from each required rotation and two correct same-place games for every club.
- All three fixed London week/date/venue assignments retained; neutral-site treatment is explicit. Shared venues have no impossible simultaneous bookings.
- Every game lies in its league-week window. Kickoffs have correct timezones/DST. Short weeks, travel, bye placement and venue exceptions are checked against dated rules, not guessed minimums.
- No imported results, rankings, injuries, real participants in postseason or undisclosed later flex decisions. Historical-record merit does not decide a branch opening showcase.

These are execution acceptance conditions, not a claim that a dated solver is already implemented or the season is game-ready. The [2014 release blockers](../operating_baseline.md#before-any-2014-game) must close separately. If a particular schedule constraint cannot be met, report the actual conflict and an auditable adjustment; do not ask Stone to hand-build the league schedule.
