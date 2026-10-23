"""Dated practice and rest records, every week, byes included (rebuild step 5; docs/rebuild_plan.md,
step 5; docs/bye_week.md, sections 3 to 7).

A placeholder until the practice builder replaces this body. The module stays outside the career
layer (tests/test_career_layer_isolation.py): nothing on the game path imports it, and it imports
nothing from runtime.current_job, runtime.decision_queue, scripts.render_career_views or any module
in that test's LAYER, at module level or inside a function. It takes the week's schedule, records
and events as arguments.
"""

# The record's vocabulary (docs/rebuild_plan.md, step 5): the days of a practice week, each
# session's type and equipment, and whom a day off is for. The job record's standing practice
# instruction is written in the same words (runtime/current_job.py validates it against these), so
# the practice builder keeps them when it replaces this placeholder.
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
SESSION_TYPES = ("practice", "walkthrough", "meeting", "film", "conditioning", "treatment")
EQUIPMENT = ("helmets_and_shoulder_pads", "helmets", "none")
PADDED = "helmets_and_shoulder_pads"
DAY_OFF_SCOPES = ("team", "players")
