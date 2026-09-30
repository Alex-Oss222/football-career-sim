# Annual NFL player sheets

Every Jacksonville-controlled player gets one annual sheet for each NFL season
in which he is part of the career. The sheet answers a simple question: **who is
this player at this checkpoint?**

The canonical format is
[the player-sheet template](../../foundation/templates/player_sheet_template.md).
Season files live at `career/YEAR/player_profiles/<player>.md`.

## The player is the player

A new season does not reset the player to unknown. Demonstrated capabilities
carry forward. If a quarterback has already shown the arm to drive the ball
through an NFL window, a January calendar change does not remove that arm. If a
receiver has demonstrated long speed or a large functional catch radius, those
remain part of his baseline. If a corner has demonstrated recovery speed, a bad
coverage decision does not make him physically slower.

Separate:

1. **Capability:** what the player has demonstrated he can do.
2. **Access/execution:** whether recognition, assignment, positioning or the
   play situation lets him use it.
3. **Consistency:** how often he reproduces it.
4. **Staff certainty:** how strong the evidence is.

Progression is therefore:

`prior established player + supported offseason changes = current player`

not a fresh scouting exercise every year.

## Grades and NFL standing

The annual sheet may contain human-facing `/10` personnel grades because the
user asked for a compact comparison across seasons. Those grades are dated
summaries, not hidden game probabilities, not potential, and not an input that
the resolver may consume directly. The underlying position-specific evidence
still controls the simulation.

`NFL standing` remains plain language. Examples include Top 5, Top 10,
high-end starter, starter, rotational/role player, backup, fringe roster, and
unassessed. Do not infer standing from salary, draft slot or depth-chart title.

A grade may remain unassessed where evidence is thin. Do not manufacture a
number merely to fill the table.

## Year-to-year use

The prior annual sheet is the starting identity record. At a new checkpoint:

- carry established capabilities forward;
- apply only evidence-supported physical, technical, processing, consistency,
  conditioning or role changes;
- show the change in the year-over-year table;
- keep unchanged strengths unchanged;
- preserve uncertainty where the staff still does not know;
- never use later real-life career outcomes to tune the branch.

New Jacksonville acquisitions do not have Jacksonville continuity, but their
football ability does not reset. Import only evidence that is permitted at the
branch date, while Jacksonville terminology and teammate timing begin as new
system context.

## File maintenance

Use:

```sh
python scripts/build_annual_player_sheets.py --season 2013
python scripts/build_annual_player_sheets.py --season 2014
python scripts/build_annual_player_sheets.py --season 2014 --check
```

The builder creates missing sheets and never overwrites an existing evaluated
sheet unless `--force` is supplied. A roster move therefore creates the new
player's annual sheet without deleting the archived sheet of a player who
departed during the same season.
