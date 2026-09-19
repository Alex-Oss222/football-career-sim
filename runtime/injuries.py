"""Period-calibrated football injury occurrence and medical disposition."""
from dataclasses import dataclass

POSITION_MULTIPLIER = {"RB": 1.30, "TE": 1.15, "LB": 1.20, "DB": 1.10,
                       "WR": 1.00, "DL": 1.10, "OL": .85, "QB": .70,
                       "K": .25, "P": .25, "LS": .25}
SEVERITY = ((.57, "minor", 0, 3), (.79, "short", 4, 14),
            (.95, "multi_week", 15, 56), (1.0, "long_term", 57, 180))

@dataclass(frozen=True)
class Injury:
    injury_class: str
    severity: str
    restriction: str
    return_days: int
    reassessment_days: int

def maybe_injury(rng, position, exposures, setting="game"):
    base = .00072 if setting == "game" else .00021
    risk = 1 - (1 - base * POSITION_MULTIPLIER.get(position, 1.0)) ** max(0, exposures)
    if rng.random() >= risk:
        return None
    draw = rng.random()
    for ceiling, name, low, high in SEVERITY:
        if draw < ceiling:
            days = rng.randint(low, high)
            klass = rng.choice(("lower_extremity", "upper_extremity", "trunk", "head_neck"))
            restriction = "independent medical hold" if klass == "head_neck" else ("limited" if not days else "out")
            return Injury(klass, name, restriction, days, min(max(days // 3, 1), 7))
    raise AssertionError
