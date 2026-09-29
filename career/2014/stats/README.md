# 2014 statistics storage

**NOT_STARTED.** No game has closed. [Game receipts](game_receipts/README.md) own regular-season statistical evidence; [postseason receipts](postseason_receipts/README.md) remain separate. Preseason results never enter regular-season standings or awards.

After the game release is accepted, preserve full Jacksonville receipts and compact-stat background receipts. Every new event ID starts with `2014-`; the receipt carries `season: 2014`. Reject a foreign-season receipt before rendering. Use `python scripts/render_season_stats.py 2014 --team "Jacksonville Jaguars"` and `python scripts/render_standings.py 2014`. A generated empty view is not evidence of played football. The [statbook](../statbook.md) is the human-facing entry point.
