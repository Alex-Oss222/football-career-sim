"""Private qualitative evidence conversion. Numeric results must stay private."""
import hashlib

TIERS = {"Elite": 4, "Plus": 3, "Average": 2, "Below-Average": 1,
         "Replacement-Level": 0}

def evidence_anchor(evidence):
    """Team/protagonist labels are deliberately excluded from accepted evidence."""
    tier = evidence.get("tier", "Average")
    if tier not in TIERS:
        raise ValueError("unknown qualitative tier")
    samples = max(0, int(evidence.get("contemporaneous_samples", 0)))
    # Thin evidence regresses toward Average. Stable digest breaks no ties and
    # exists only to make canonical evidence identity explicit.
    weight = min(samples, 16) / 16
    value = 2.0 + (TIERS[tier] - 2.0) * weight
    identity = str(evidence.get("evidence_id", "thin-evidence"))
    return {"value": value, "evidence_digest": hashlib.sha256(identity.encode()).hexdigest()}


def initialize_team(team_id, player_evidence, unit_evidence):
    """Build normalized private input from date-eligible evidence for any club."""
    from .kernel import TeamInput
    active = tuple(sorted(f"{p.get('position','WR')}:{p['player_id']}"
                          for p in player_evidence if p.get('medical_status') == 'available'))
    if not active:
        raise ValueError('no medically available players')
    return TeamInput(team_id=team_id, active_players=active,
                     offense_anchor=evidence_anchor(unit_evidence.get('offense', {}))['value'],
                     defense_anchor=evidence_anchor(unit_evidence.get('defense', {}))['value'],
                     special_teams_anchor=evidence_anchor(unit_evidence.get('special_teams', {}))['value'],
                     scheme=unit_evidence.get('scheme', 'balanced'),
                     plan=unit_evidence.get('plan', 'balanced'))
