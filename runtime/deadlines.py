"""The league's dated windows shown under COMING UP (rebuild step 5, builder A5): the trade deadline
and the other league dates of the season, and each player's eligibility windows from the roster
record's availability note.

STUB until A5 (wave 2): ``coming_up`` returns no window, so no brief shows COMING UP. A window is a
dict: ``key`` (a stable name), ``title``, ``at`` (an ISO datetime with its ET offset, or None),
``why``, ``state``, ``action`` and ``source`` ({path, anchor} of the page that records it). A window
is never an event: it has no queue item, holds nothing and has no result page.
"""


def coming_up(season, issued_at, root):
    """The windows a brief issued at ``issued_at`` shows under COMING UP, soonest first (none yet)."""
    return []
