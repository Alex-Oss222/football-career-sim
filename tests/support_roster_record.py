"""Synthetic roster records (runtime/roster.py) for tests that build a repository copy."""
import json

from runtime import roster


def record(rows, as_of="2014-08-01", event="at a synthetic test date", departures=()):
    """A valid roster record from (name, position, status[, availability]) rows; the list follows
    the status, an active player sits in a synthetic group and the practice squad carries no
    availability."""
    players = []
    for row in rows:
        name, position, status = row[:3]
        lst = roster.list_for(status) or "reserve"
        availability = None if lst == "practice_squad" else (row[3] if len(row) > 3 else "No communicated restriction")
        sources = {"status": "test fixture"}
        if availability is not None:
            sources["availability"] = "test fixture"
        players.append({"name": name, "position": position, "list": lst,
                        "group": "Players" if lst == "active" else None, "status": status,
                        "availability": availability, "sources": sources})
    return {"team": "Jacksonville Jaguars", "season": int(as_of[:4]), "as_of": {"date": as_of, "event": event},
            "practice_squad_places": 10, "active_limit": 53, "about": "A synthetic test roster.",
            "field_sources": {}, "players": players, "departures": list(departures)}


def write(path, rows, **kw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record(rows, **kw), indent=1) + "\n", encoding="utf-8")
    return path
