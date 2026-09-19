"""One protagonist-blind possession kernel for interactive and background games."""
from dataclasses import dataclass, asdict
import hashlib, json, random
from .calibration import load, validate
from .injuries import maybe_injury
from .rules import RULES
from .player_evidence import (choose, empty_player_stats, normalize_players,
                              observation)

@dataclass(frozen=True)
class TeamInput:
    team_id: str
    active_players: tuple
    offense_anchor: float = 2.0
    defense_anchor: float = 2.0
    special_teams_anchor: float = 2.0
    scheme: str = "balanced"
    plan: str = "balanced"
    roster: tuple = ()
    personnel_packages: tuple = ()
    rotation_plan: tuple = ()

def _rng(seed, packet):
    digest = hashlib.sha256(seed + json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).digest()
    return random.Random(int.from_bytes(digest, "big"))

def resolve_game(home, away, *, seed, event_id, venue="home", weather="normal",
                 game_type="regular", management_mode="autonomous", resume=None):
    if not isinstance(seed, bytes) or len(seed) < 32: raise ValueError("private seed required")
    home_players, away_players = normalize_players(home), normalize_players(away)
    if not home_players or not away_players: raise ValueError("active participants required")
    packet = {"event_id": event_id, "home": asdict(home), "away": asdict(away),
              "venue": venue, "weather": weather, "game_type": game_type}
    rng = _rng(seed, packet)
    cal = load(); assert not validate(cal)
    probs = cal["model"]["drive_outcomes"]
    possessions = []
    teams = {home.team_id: home, away.team_id: away}
    rosters = {home.team_id: home_players, away.team_id: away_players}
    stats = {t.team_id: {"points":0,"touchdowns":0,"field_goals":0,"punts":0,
            "turnovers":0,"sacks_allowed":0,"penalties":0,"penalty_yards":0,
            "passing_yards":0,"rushing_yards":0,"first_downs":0,
            "third_down_attempts":0,"third_down_conversions":0,"time_of_possession":0,
            "kick_returns":0,"punt_returns":0,"players":empty_player_stats(rosters[t.team_id])}
            for t in (home,away)}
    evidence=[]
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
        available=rosters[offense]; defenders=rosters[defense.team_id]
        qb=choose(rng,available,{"QB"},"passer"); runner=choose(rng,available,{"RB","FB","QB"},"rusher")
        receiver=choose(rng,available,{"WR","TE","RB","FB"},"receiver")
        qbs=s["players"][qb.player_id]; qbs["pass_attempts"]+=pass_plays; qbs["passing_yards"]+=pass_yards
        rs=s["players"][runner.player_id]; rs["rushing_attempts"]+=plays-pass_plays; rs["rushing_yards"]+=rush_yards
        rec=s["players"][receiver.player_id]; rec["receptions"]+=max(0,round(pass_plays*.6)); rec["receiving_yards"]+=pass_yards
        if sacks:
            blocker=choose(rng,available,{"OT","OG","C"},"pass_protection"); s["players"][blocker.player_id]["sacks_allowed"]+=sacks
            rusher=choose(rng,defenders,{"DE","DT","DL","LB"},"pass_rush"); stats[defense.team_id]["players"][rusher.player_id]["sacks"]+=sacks
            evidence.append(observation(blocker,unit="offense",role="pass protection",responsibility="protect assigned gap/edge",situation="generated passing downs",assignment="assignment identified",technique="leverage lost",physical_execution="pressure reached quarterback",observable_effort="recovered into the play after initial loss"))
        s["first_downs"]+=max(0,round((pass_yards+rush_yards)/15)); third=max(0,plays//3); s["third_down_attempts"]+=third
        s["third_down_conversions"]+=sum(rng.random()<cal["model"]["third_down_rate"] for _ in range(third))
        pens=sum(rng.random()<cal["model"]["penalty_per_play"] for _ in range(plays)); s["penalties"]+=pens; s["penalty_yards"]+=pens*rng.randint(5,10)
        points=0
        if outcome=="touchdown": points=7; s["touchdowns"]+=1
        elif outcome=="field_goal":
            points=3; s["field_goals"]+=1
            kicker=choose(rng,available,{"K"},"placekicker")
            s["players"][kicker.player_id]["field_goals_made"]+=1
        elif outcome=="punt": s["punts"]+=1; s["punt_returns"]+=rng.random()<.52
        elif outcome=="turnover": s["turnovers"]+=1
        s["points"]+=points; s["time_of_possession"]+=seconds
        if points and rng.random() > cal["model"]["kickoff_touchback_rate"]:
            stats[defense.team_id]["kick_returns"] += 1
        if outcome=="turnover":
            qbs["interceptions"]+=1
            evidence.append(observation(qb,unit="offense",role="passer",responsibility="protect the football",situation="turnover drive",processing="decision arrived late",physical_execution="throw was intercepted"))
        else:
            evidence.append(observation(receiver,unit="offense",role="route participant",responsibility="execute assigned route",situation=f"{outcome} drive",assignment="assignment held",observable_effort="sustained route responsibility through the rep"))
        if outcome=="punt":
            punter=choose(rng,available,{"P"},"punt"); s["players"][punter.player_id]["punts"]+=1
            cover=choose(rng,available,{"LB","CB","S","WR","RB","TE"},"punt_coverage")
            evidence.append(observation(cover,unit="special teams",role="punt coverage",responsibility="maintain coverage lane and leverage",situation="punt",assignment="coverage lane held",communication="substitution responsibility confirmed",observable_effort="coverage pursuit continued to the finish",special_teams_responsibility="coverage lane, leverage and tackle finish"))
        possessions.append({"number":drive_no,"team":offense,"start_clock":clock+seconds,
                            "end_clock":clock,"seconds":seconds,"outcome":outcome,"points":points})
        offense=defense.team_id
    total=RULES.quarter_seconds*4
    overtime_seconds=0
    if stats[home.team_id]["points"] == stats[away.team_id]["points"]:
        ot_limit=RULES.postseason_ot_seconds if game_type=="postseason" else RULES.regular_ot_seconds
        ot_offense=offense; possessions_in_ot=0
        while True:
            seconds=min(ot_limit-overtime_seconds,rng.randint(75,190))
            if seconds <= 0:
                if game_type=="postseason": ot_limit += RULES.postseason_ot_seconds; continue
                break
            overtime_seconds += seconds; possessions_in_ot += 1
            team=teams[ot_offense]; defense=away if ot_offense==home.team_id else home
            draw=rng.random(); cumulative=0
            for outcome,chance in probs.items():
                cumulative += chance
                if draw <= cumulative: break
            points=7 if outcome=="touchdown" else 3 if outcome=="field_goal" else 0
            plays=rng.randint(3,9); pass_plays=sum(rng.random()<cal["model"]["pass_play_share"] for _ in range(plays))
            sacks=sum(rng.random()<cal["derived"]["sack_rate"]["value"] for _ in range(pass_plays))
            pass_yards=max(-sacks*6,round(rng.gauss((pass_plays-sacks)*6.55,max(6,pass_plays*3))))
            rush_yards=max(-5,round(rng.gauss((plays-pass_plays)*4.26,max(4,(plays-pass_plays)*2))))
            s=stats[ot_offense]; s["passing_yards"]+=pass_yards; s["rushing_yards"]+=rush_yards; s["sacks_allowed"]+=sacks
            if outcome=="touchdown": s["touchdowns"]+=1
            elif outcome=="field_goal": s["field_goals"]+=1
            elif outcome=="punt": s["punts"]+=1
            elif outcome=="turnover": s["turnovers"]+=1
            s["points"]+=points; s["time_of_possession"]+=seconds
            available=rosters[ot_offense]
            qb=choose(rng,available,{"QB"},"passer"); runner=choose(rng,available,{"RB","FB","QB"},"rusher"); receiver=choose(rng,available,{"WR","TE","RB"},"receiver")
            s["players"][qb.player_id]["pass_attempts"]+=pass_plays; s["players"][qb.player_id]["passing_yards"]+=pass_yards
            s["players"][runner.player_id]["rushing_attempts"]+=plays-pass_plays; s["players"][runner.player_id]["rushing_yards"]+=rush_yards
            s["players"][receiver.player_id]["receptions"]+=max(0,round(pass_plays*.6)); s["players"][receiver.player_id]["receiving_yards"]+=pass_yards
            possessions.append({"number":drive_no+possessions_in_ot,"team":ot_offense,"period":"OT",
                                "start_clock":ot_limit-(overtime_seconds-seconds),"end_clock":ot_limit-overtime_seconds,
                                "seconds":seconds,"outcome":outcome,"points":points})
            lead=stats[home.team_id]["points"]!=stats[away.team_id]["points"]
            # Opening TD/defensive score ends play; an opening FG allows a reply.
            if lead and (points==7 or possessions_in_ot>=2): break
            ot_offense=defense.team_id
            if overtime_seconds>=ot_limit and game_type!="postseason": break
        total += overtime_seconds
    # Allocate rounding/administrative time to the final possessing team.
    used=sum(v["time_of_possession"] for v in stats.values()); stats[offense]["time_of_possession"]+=total-used
    injuries=[]
    for team in (home,away):
        for p in rosters[team.team_id]:
            injury=maybe_injury(rng,p.position,20,"game")
            if injury: injuries.append({"team":team.team_id,"player":p.player_id,**asdict(injury)})
    pauses=[]
    if management_mode=="user_controlled" and not resume:
        pauses.append({"trigger":"material_hc_decision","continuation_token":hashlib.sha256((event_id+":pause").encode()).hexdigest()})
    return {"kernel_version":"2013.2","event_id":event_id,"final_score":{k:v["points"] for k,v in stats.items()},
            "possessions":possessions,"team_stats":stats,"player_evidence":evidence,"injuries":injuries,"pauses":pauses,"terminated":True}

def validate_result(result):
    errors=[]
    for team,score in result["final_score"].items():
        s=result["team_stats"][team]
        if score != s["touchdowns"]*7+s["field_goals"]*3: errors.append("score ledger mismatch")
        if sum(p["passing_yards"] for p in s["players"].values()) != s["passing_yards"]: errors.append("passing yardage mismatch")
        if sum(p["rushing_yards"] for p in s["players"].values()) != s["rushing_yards"]: errors.append("rushing yardage mismatch")
        if sum(p["receiving_yards"] for p in s["players"].values()) != s["passing_yards"]: errors.append("receiving yardage mismatch")
    elapsed=sum(p["seconds"] for p in result["possessions"])
    if sum(s["time_of_possession"] for s in result["team_stats"].values()) != elapsed: errors.append("clock mismatch")
    if any(p["end_clock"]<0 or p["start_clock"]<p["end_clock"] for p in result["possessions"]): errors.append("invalid clock")
    return errors
