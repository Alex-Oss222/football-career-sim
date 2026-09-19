"""One protagonist-blind possession kernel for interactive and background games."""
from dataclasses import dataclass, asdict
import hashlib, json, random
from .calibration import load, validate
from .injuries import maybe_injury
from .rules import RULES

@dataclass(frozen=True)
class TeamInput:
    team_id: str
    active_players: tuple
    offense_anchor: float = 2.0
    defense_anchor: float = 2.0
    special_teams_anchor: float = 2.0
    scheme: str = "balanced"
    plan: str = "balanced"

def _rng(seed, packet):
    digest = hashlib.sha256(seed + json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).digest()
    return random.Random(int.from_bytes(digest, "big"))

def resolve_game(home, away, *, seed, event_id, venue="home", weather="normal",
                 game_type="regular", management_mode="autonomous", resume=None):
    if not isinstance(seed, bytes) or len(seed) < 32: raise ValueError("private seed required")
    if not home.active_players or not away.active_players: raise ValueError("active participants required")
    packet = {"event_id": event_id, "home": asdict(home), "away": asdict(away),
              "venue": venue, "weather": weather, "game_type": game_type}
    rng = _rng(seed, packet)
    cal = load(); assert not validate(cal)
    probs = cal["model"]["drive_outcomes"]
    possessions = []
    teams = {home.team_id: home, away.team_id: away}
    stats = {t.team_id: {"points":0,"touchdowns":0,"field_goals":0,"punts":0,
            "turnovers":0,"sacks_allowed":0,"penalties":0,"penalty_yards":0,
            "passing_yards":0,"rushing_yards":0,"first_downs":0,
            "third_down_attempts":0,"third_down_conversions":0,"time_of_possession":0,
            "kick_returns":0,"punt_returns":0,"players":{p:{"scrimmage_yards":0} for p in t.active_players}}
            for t in (home,away)}
    clock = RULES.quarter_seconds * 4
    offense = away.team_id if rng.random() < .5 else home.team_id
    drive_no = 0
    while clock > 0:
        team=teams[offense]; defense=away if offense==home.team_id else home
        drive_no += 1
        seconds=min(clock, rng.randint(95,205)); clock-=seconds
        edge=max(-.06,min(.06,(team.offense_anchor-defense.defense_anchor)*.025 + (.008 if team is home else 0)))
        adjusted=dict(probs); adjusted["touchdown"]+=edge; adjusted["punt"]-=edge*.65; adjusted["turnover"]-=edge*.35
        draw=rng.random(); cumulative=0
        for outcome,chance in adjusted.items():
            cumulative+=chance
            if draw<=cumulative: break
        plays=rng.randint(3,10); pass_plays=sum(rng.random()<cal["model"]["pass_play_share"] for _ in range(plays))
        sacks=sum(rng.random()<cal["derived"]["sack_rate"]["value"] for _ in range(pass_plays))
        pass_yards=max(-sacks*6, round(rng.gauss((pass_plays-sacks)*6.55, max(6,pass_plays*3))))
        rush_yards=max(-5, round(rng.gauss((plays-pass_plays)*4.26, max(4,(plays-pass_plays)*2))))
        s=stats[offense]; s["passing_yards"]+=pass_yards; s["rushing_yards"]+=rush_yards; s["sacks_allowed"]+=sacks
        s["first_downs"]+=max(0,round((pass_yards+rush_yards)/15)); third=max(0,plays//3); s["third_down_attempts"]+=third
        s["third_down_conversions"]+=sum(rng.random()<cal["model"]["third_down_rate"] for _ in range(third))
        pens=sum(rng.random()<cal["model"]["penalty_per_play"] for _ in range(plays)); s["penalties"]+=pens; s["penalty_yards"]+=pens*rng.randint(5,10)
        points=0
        if outcome=="touchdown": points=7; s["touchdowns"]+=1
        elif outcome=="field_goal": points=3; s["field_goals"]+=1
        elif outcome=="punt": s["punts"]+=1; s["punt_returns"]+=rng.random()<.52
        elif outcome=="turnover": s["turnovers"]+=1
        s["points"]+=points; s["time_of_possession"]+=seconds
        featured=team.active_players[drive_no%len(team.active_players)]; s["players"][featured]["scrimmage_yards"]+=pass_yards+rush_yards
        possessions.append({"number":drive_no,"team":offense,"start_clock":clock+seconds,
                            "end_clock":clock,"seconds":seconds,"outcome":outcome,"points":points})
        offense=defense.team_id
    total=RULES.quarter_seconds*4
    # Allocate rounding/administrative time to the final possessing team.
    used=sum(v["time_of_possession"] for v in stats.values()); stats[offense]["time_of_possession"]+=total-used
    injuries=[]
    for team in (home,away):
        for p in team.active_players:
            pos=p.split(":",1)[0] if ":" in p else "WR"
            injury=maybe_injury(rng,pos,20,"game")
            if injury: injuries.append({"team":team.team_id,"player":p,**asdict(injury)})
    pauses=[]
    if management_mode=="user_controlled" and not resume:
        pauses.append({"trigger":"material_hc_decision","continuation_token":hashlib.sha256((event_id+":pause").encode()).hexdigest()})
    return {"kernel_version":"2013.1","event_id":event_id,"final_score":{k:v["points"] for k,v in stats.items()},
            "possessions":possessions,"team_stats":stats,"injuries":injuries,"pauses":pauses,"terminated":True}

resolve_background_game = resolve_game
resolve_protagonist_game = resolve_game

def validate_result(result):
    errors=[]
    for team,score in result["final_score"].items():
        s=result["team_stats"][team]
        if score != s["touchdowns"]*7+s["field_goals"]*3: errors.append("score ledger mismatch")
        if sum(p["scrimmage_yards"] for p in s["players"].values()) != s["passing_yards"]+s["rushing_yards"]: errors.append("yardage mismatch")
    if sum(s["time_of_possession"] for s in result["team_stats"].values()) != 3600: errors.append("clock mismatch")
    if any(p["end_clock"]<0 or p["start_clock"]<p["end_clock"] for p in result["possessions"]): errors.append("invalid clock")
    return errors
