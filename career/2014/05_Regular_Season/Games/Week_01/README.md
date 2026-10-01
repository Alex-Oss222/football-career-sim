# Week 1 — at Philadelphia (September 7, 2014)

[All weeks](../README.md) · [Regular-season statistics](../../Statistics/README.md) · [Week 1 awards](../../Awards/week_01/README.md)

The game has not been played. Its plan, call sheet, report and box score belong here when the week is prepared and closed.

**Inputs in place (August 31, 2014).** The 53 was set August 30 and the practice squad signed August 31 ([final roster cuts](../../../04_Training_Camp_and_Preseason/Roster_Decisions/final_roster_cuts.md)); Stone's season game depth chart, the released 2014 game input, is at [game_depth_chart.json](../../../00_Team_Operations/Team/Depth_Chart/game_depth_chart.json) with the seven Week 1 inactives (Nicks and Hoskins by medical instruction; Butler, Linsley, Edebali, Todd Davis and Gabriel by Stone's standing rule) and the six captains ([roster decisions](../../../04_Training_Camp_and_Preseason/Roster_Decisions/roster_decisions.md)). The [August 28 packet](Regular-season%20Week%201.md) holds the Week 1 work plan, the proposed opening menu and the situational sheets; the staff's August 29 review opened the Philadelphia study ([camp report](../../../04_Training_Camp_and_Preseason/Training_Camp/training_report.md#august-29-the-atlanta-review-and-the-cutdown-meeting)).

**Still owed before the build.** Stone's frozen call sheet (`call_sheet.json`, `{"offensive_call_sheet": [...]}` with labelled calls) from the September 1 to 6 preparation, and the clock reaching game day: `python scripts/build_week_inputs.py 1 --season 2014` refuses earlier (the information gate), and the Week 1 depth-chart library must be rebuilt for the August 30 dispositions (Cain to Chicago on September 1; Edwards and Blake unplaced) before the inputs are frozen. The chart passed the build and the exclusivity gate (16 games) in a scratch copy with the clock set forward on August 31, 2014; the real build runs on game day.

Scheduled kickoff (Eastern Time): 1 p.m. The [calendar](../../../Calendar.md) controls dated amendments and the permitted preparation. Review the [current roster](../../../00_Team_Operations/Team/Roster/roster.md), [depth chart](../../../00_Team_Operations/Team/Depth_Chart/depth_chart.md), medical instructions and game-readiness requirements before execution.

After a closed game, link its actual public receipt and refresh season statistics, player cards and standings. No result or player performance is supplied by this schedule folder.
