*Player card template: uploaded by the user on October 20, 2026 and adopted for every player page, built by the shared player-page builder (`runtime/player_pages.py`, run with `scripts/render_player_pages.py`); the worked example is [the Kirk Cousins preview](../../docs/examples/kirk_cousins_player_card_preview.md) and the record of the change is [the rebuild plan](../../docs/rebuild_plan.md) ("The pages to read", Player). The page keeps the photo and its credit below the As of line, as the user approved on the Kirk Cousins page on October 19, 2026. The text below is the user's.*

# [Player name]

**[Team] · [Position] · No. [number if known] · Age [verified age] · [actual roster status]**

[Height], [weight] · Born [verified date] · [College] · [Draft year and original club, or undrafted]

As of [actual career date].

**Current assignment:** [One plain, confirmed role. Example: Starting quarterback. No second sentence.]

**[Relevant position statistic]:** [Verified value] ([season and cutoff]).

[Use the actual metric name, not the generic phrase "position rating". A QB shows **Passer rating**. RB/FB may show **Yards per carry**, WR/TE **Yards per target** or **Catch rate**, DE/DT pass rushers **Sacks** or **Pressures** when tracked, LB **Tackles**, DB **Passes defended** or **Interceptions**, K **Field-goal percentage**, P **Net punting average**, LS **Long snaps** or **Recorded bad snaps**, OL **Sacks allowed** if individually attributable. If no meaningful validated metric exists, omit the line. For DBs, use **Passer rating allowed** only when actual target, completion, yard, touchdown and interception data support it. Never create a numerical all-position overall rating or use a real-world statistic for a simulated season.]

## Staff assessment

[Two to four direct football sentences. Start with the player's demonstrated NFL level and real role: for instance, "He has proven himself an NFL starting quarterback," or "He has been a reliable reserve," only if the record supports it. Name the most important football strength or strengths in concrete everyday football language. State the most relevant weakness or limitation, if supported. Don't turn game outcomes automatically into individual fault. Do not inflate standing or potential. Avoid stock phrases, mechanical grading, artificial symmetry, platitudes and verbose process explanations. If no genuine staff assessment exists, omit this section rather than invent one.]

*Staff view, [the actual documented assessment date].*

## Contract

[Verified current contract, terms and expiration; otherwise say not established.]

| Year | Base salary | Cap charge |
|---|---:|---:|
| [Year] | [Verified] | [Verified] |

## Statistics

### Regular season

[For quarterbacks, label the existing rating column **Passer rating**, not QBR. This is the recognized 0–158.3 NFL passing-efficiency rating calculated from actual simulator passing totals. For other positions use real recorded position statistics and standard derived rates, never invented ratings. Keep the metric label clear and the same across seasons.]

[Keep position-specific complete tables. Every annual row starts with Season, Team, Age and #. Preserve past years, show partial-year cutoff and verified cumulative totals. Never invent totals or backfill real-world career results.]

### Playoffs

[Same rules as regular season, but separate tables. Record no playoff appearance when confirmed.]

## Awards

[Actual earned awards only; otherwise "None."]

## Transactions

| Date | Transaction |
|---|---|
| [Recorded date] | [Actual signed/traded/waived/released/etc. event in the sim] |

---

**Editorial constraints, not text for the player page:** The "position statistic" is an objective statistic, not a numerical scouting judgment. ESPN Total QBR is a separate context-adjusted proprietary metric; do not manufacture it from passing totals or import the real player's QBR into an alternate-career season. Never show "QBR" when the value is passer rating.  No 1–10 grades, no automated trait grids, no "what the record shows/does not settle" matrix, no plays-worth-reviewing, no current coaching questions, no weekly diary, no invented comparison or dialogue. Keep the permanent record and existing dates intact. A current season's stats update from closed games without auto-rewriting the subjective assessment. Implement in the shared player-page renderer, rather than editing only the generated Markdown file. Leave approved prior-season pages unchanged.
