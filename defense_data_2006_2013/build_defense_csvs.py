"""
Build free defensive datasets for 2006-2013 from nflverse releases.

Usage: python3 -I build_defense_csvs.py RAW_DIR OUT_DIR

RAW_DIR must contain (from github.com/nflverse/nflverse-data releases):
  pbp_{2005..2013}.parquet          play_by_play_{year}.parquet
  depth_{2005..2013}.parquet        depth_charts_{year}.parquet
  roster_{2006..2013}.parquet       roster_{year}.parquet
  stats_reg_{2006..2013}.parquet    stats_player_reg_{year}.parquet
  snaps_2013.parquet                snap_counts_2013.parquet
  players.parquet                   players.parquet

2005 is read only to build prior-season (lag) columns for 2006.
Nothing from 2014 or later is read or written.
"""
import sys
import numpy as np
import pandas as pd

RAW, OUT = sys.argv[1], sys.argv[2]
SEASONS = list(range(2006, 2014))
LAG_SEASONS = [2005] + SEASONS
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA", "SL": "LA", "ARZ": "ARI", "BLT": "BAL",
            "CLV": "CLE", "HST": "HOU", "JAC": "JAX", "LAR": "LA", "SDG": "LAC", "RAI": "LV",
            "GNB": "GB", "KAN": "KC", "NWE": "NE", "NOR": "NO", "SFO": "SF", "TAM": "TB"}

DL = {"DE", "DT", "NT", "DL", "LDE", "RDE", "LDT", "RDT", "NDT", "EDGE"}
LB = {"OLB", "ILB", "MLB", "LB", "LOLB", "ROLB", "LILB", "RILB", "SLB", "WLB", "MIKE", "WILL", "SAM"}
DB = {"CB", "SS", "FS", "S", "DB", "LCB", "RCB", "NB", "SAF", "NCB"}


def pos_group(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return None
    p = str(p).upper()
    if p in DL:
        return "DL"
    if p in LB:
        return "LB"
    if p in DB:
        return "DB"
    return None


def fix_team(s):
    return s.map(lambda t: TEAM_FIX.get(t, t) if isinstance(t, str) else t)


PBP_COLS = [
    "season", "season_type", "game_id", "play_id", "posteam", "defteam", "week",
    "play_type", "pass", "rush", "sack", "qb_hit", "qb_scramble", "complete_pass",
    "incomplete_pass", "interception", "pass_attempt", "yards_gained", "epa", "success",
    "wp", "half_seconds_remaining", "special_teams_play", "fumble_lost",
    "fixed_drive", "fixed_drive_result", "total_home_score", "total_away_score",
    "home_team", "away_team",
    "solo_tackle_1_player_id", "solo_tackle_1_team", "solo_tackle_2_player_id", "solo_tackle_2_team",
    "tackle_with_assist_1_player_id", "tackle_with_assist_1_team",
    "tackle_with_assist_2_player_id", "tackle_with_assist_2_team",
    "assist_tackle_1_player_id", "assist_tackle_1_team", "assist_tackle_2_player_id", "assist_tackle_2_team",
    "assist_tackle_3_player_id", "assist_tackle_3_team", "assist_tackle_4_player_id", "assist_tackle_4_team",
    "tackle_for_loss_1_player_id", "tackle_for_loss_2_player_id",
    "sack_player_id", "half_sack_1_player_id", "half_sack_2_player_id",
    "qb_hit_1_player_id", "qb_hit_2_player_id",
    "pass_defense_1_player_id", "pass_defense_2_player_id", "interception_player_id",
    "forced_fumble_player_1_player_id", "forced_fumble_player_1_team",
    "forced_fumble_player_2_player_id", "forced_fumble_player_2_team",
    "fumble_recovery_1_player_id", "fumble_recovery_1_team",
    "penalty_player_id", "penalty_team", "penalty_type", "penalty_yards",
]


def load_pbp(y):
    p = pd.read_parquet(f"{RAW}/pbp_{y}.parquet", columns=PBP_COLS)
    p = p[p.season_type == "REG"].copy()
    for c in ["posteam", "defteam", "home_team", "away_team", "penalty_team", "fumble_recovery_1_team",
              "forced_fumble_player_1_team", "forced_fumble_player_2_team"] + \
             [c for c in PBP_COLS if c.endswith("_team") and "tackle" in c]:
        p[c] = fix_team(p[c])
    return p


# ---------------------------------------------------------------- player credits
def player_credits(p):
    """Long table: one row per (play, player, credit_type)."""
    scrim = p[p.play_type.isin(["pass", "run"])]  # live scrimmage snaps incl. sacks and scrambles
    base = ["season", "game_id", "play_id", "defteam", "rush", "pass", "sack", "complete_pass",
            "yards_gained", "epa", "success"]
    out = []

    def add(df, idcol, kind, value=1.0, teamcol=None):
        d = df[df[idcol].notna()]
        if teamcol is not None:
            d = d[d[teamcol] == d["defteam"]]
        d = d[base + [idcol]].rename(columns={idcol: "gsis_id"})
        d["kind"] = kind
        d["value"] = value
        out.append(d)

    add(scrim, "solo_tackle_1_player_id", "tkl_solo", teamcol="solo_tackle_1_team")
    add(scrim, "solo_tackle_2_player_id", "tkl_solo", teamcol="solo_tackle_2_team")
    add(scrim, "tackle_with_assist_1_player_id", "tkl_with_ast", teamcol="tackle_with_assist_1_team")
    add(scrim, "tackle_with_assist_2_player_id", "tkl_with_ast", teamcol="tackle_with_assist_2_team")
    for i in range(1, 5):
        add(scrim, f"assist_tackle_{i}_player_id", "tkl_ast", teamcol=f"assist_tackle_{i}_team")
    add(scrim, "tackle_for_loss_1_player_id", "tfl_official")
    add(scrim, "tackle_for_loss_2_player_id", "tfl_official")
    add(scrim, "sack_player_id", "sack", 1.0)
    add(scrim, "half_sack_1_player_id", "sack", 0.5)
    add(scrim, "half_sack_2_player_id", "sack", 0.5)
    add(scrim, "qb_hit_1_player_id", "qb_hit")
    add(scrim, "qb_hit_2_player_id", "qb_hit")
    add(scrim, "pass_defense_1_player_id", "pd")
    add(scrim, "pass_defense_2_player_id", "pd")
    add(scrim, "interception_player_id", "int")
    add(scrim, "forced_fumble_player_1_player_id", "ff", teamcol="forced_fumble_player_1_team")
    add(scrim, "forced_fumble_player_2_player_id", "ff", teamcol="forced_fumble_player_2_team")
    add(scrim, "fumble_recovery_1_player_id", "fr", teamcol="fumble_recovery_1_team")

    # defensive penalties on scrimmage downs (including nullified plays), excluding special teams
    pen = p[(p.penalty_player_id.notna()) & (p.penalty_team == p.defteam) &
            ((p["pass"] == 1) | (p["rush"] == 1) | (p.play_type.isin(["pass", "run", "no_play"]) &
                                                  (p.special_teams_play != 1)))]
    pen = pen[~pen.play_type.isin(["punt", "kickoff", "field_goal", "extra_point"])]
    d = pen[base + ["penalty_player_id", "penalty_type", "penalty_yards"]].rename(
        columns={"penalty_player_id": "gsis_id"})
    d["kind"] = "pen"
    d["value"] = 1.0
    out.append(d)
    return pd.concat(out, ignore_index=True)


def aggregate_players(cred):
    key = ["season", "defteam", "gsis_id"]
    c = cred.copy()
    tk = c[c.kind.isin(["tkl_solo", "tkl_with_ast", "tkl_ast"])]
    # one tackle involvement per player per play
    tkp = tk.drop_duplicates(key + ["play_id", "game_id"])
    is_run = tkp["rush"] == 1
    is_cmp = (tkp["complete_pass"] == 1) & (tkp["sack"] != 1)

    g = {}
    cnt = c.groupby(key + ["kind"])["value"].sum().unstack(fill_value=0)
    for col in ["tkl_solo", "tkl_with_ast", "tkl_ast", "tfl_official", "sack", "qb_hit", "pd", "int", "ff", "fr", "pen"]:
        if col not in cnt:
            cnt[col] = 0.0
    res = cnt[["tkl_solo", "tkl_with_ast", "tkl_ast", "tfl_official", "sack", "qb_hit", "pd", "int", "ff", "fr"]].rename(
        columns={"tkl_solo": "tackles_solo", "tkl_with_ast": "tackles_with_assist", "tkl_ast": "tackle_assists",
                 "sack": "sacks", "qb_hit": "qb_hits", "pd": "passes_defensed", "int": "interceptions",
                 "ff": "forced_fumbles", "fr": "fumble_recoveries"})

    res["tackle_plays"] = tkp.groupby(key).size()
    r = tkp[is_run]
    res["run_tackle_plays"] = r.groupby(key).size()
    res["run_stops"] = r[r.success == 0].groupby(key).size()
    res["run_tackle_yards_mean"] = r.groupby(key)["yards_gained"].mean()
    res["run_tackle_epa_mean"] = r.groupby(key)["epa"].mean()
    q = tkp[is_cmp]
    res["pass_tackle_plays"] = q.groupby(key).size()
    res["pass_stops"] = q[q.success == 0].groupby(key).size()
    res["pass_tackle_yards_mean"] = q.groupby(key)["yards_gained"].mean()
    res["pass_tackle_epa_mean"] = q.groupby(key)["epa"].mean()
    bl = tkp[(tkp["sack"] != 1) & (tkp["yards_gained"] < 0)]
    res["tackles_behind_los"] = bl.groupby(key).size()

    sk = c[c.kind == "sack"].drop_duplicates(key + ["game_id", "play_id"])
    hit = c[c.kind == "qb_hit"].drop_duplicates(key + ["game_id", "play_id"])
    res["sack_plays"] = sk.groupby(key).size()
    res["qb_hits_non_sack"] = hit[hit["sack"] != 1].groupby(key).size()
    pr = pd.concat([sk, hit]).drop_duplicates(key + ["game_id", "play_id"])
    res["pressure_plays"] = pr.groupby(key).size()

    pen = c[c.kind == "pen"]
    res["def_penalties"] = pen.groupby(key).size()
    res["def_penalty_yards"] = pen.groupby(key)["penalty_yards"].sum()
    dpi = pen[pen.penalty_type == "Defensive Pass Interference"]
    res["dpi"] = dpi.groupby(key).size()
    res["dpi_yards"] = dpi.groupby(key)["penalty_yards"].sum()
    hc = pen[pen.penalty_type.isin(["Defensive Holding", "Illegal Contact", "Illegal Use of Hands"])]
    res["holding_contact_pen"] = hc.groupby(key).size()
    rp = pen[pen.penalty_type == "Roughing the Passer"]
    res["roughing_passer_pen"] = rp.groupby(key).size()
    ps = pen[pen.penalty_type.isin(["Defensive Offside", "Encroachment", "Neutral Zone Infraction"])]
    res["pre_snap_pen"] = ps.groupby(key).size()

    res["games_with_def_stat"] = c[c.kind != "pen"].groupby(key)["game_id"].nunique()
    res = res.reset_index().rename(columns={"defteam": "team"})
    return res


# ---------------------------------------------------------------- depth charts
def load_depth(y):
    d = pd.read_parquet(f"{RAW}/depth_{y}.parquet")
    d = d[(d.game_type == "REG") & (d.formation == "Defense") & d.gsis_id.notna()].copy()
    d["team"] = fix_team(d.club_code)
    for c in ["depth_position", "position", "full_name"]:
        d[c] = d[c].astype("string").str.strip().replace("", pd.NA)
    d["depth_team"] = pd.to_numeric(d.depth_team, errors="coerce")
    d["week"] = pd.to_numeric(d.week, errors="coerce")
    d["season"] = y
    return d


def depth_player_summary(d):
    key = ["season", "team", "gsis_id"]
    wk = d.drop_duplicates(key + ["week"])
    s = wk.groupby(key)["week"].nunique().rename("depth_weeks_listed").to_frame()
    st = d[d.depth_team == 1].drop_duplicates(key + ["week"])
    s["depth_weeks_starter"] = st.groupby(key)["week"].nunique()
    s["depth_position"] = d.groupby(key)["depth_position"].agg(lambda x: x.mode().iat[0] if len(x.mode()) else None)
    s["depth_roster_position"] = d.groupby(key)["position"].agg(lambda x: x.mode().iat[0] if len(x.mode()) else None)
    s["depth_name"] = d.groupby(key)["full_name"].agg(lambda x: x.mode().iat[0] if len(x.mode()) else None)
    return s.reset_index()


# ---------------------------------------------------------------- main build
def main():
    pbp = {y: load_pbp(y) for y in LAG_SEASONS}
    depth = {y: load_depth(y) for y in LAG_SEASONS}
    players = pd.read_parquet(f"{RAW}/players.parquet")
    players = players.drop_duplicates("gsis_id").set_index("gsis_id")

    # ---------------- player-season file
    prows = []
    for y in SEASONS:
        agg = aggregate_players(player_credits(pbp[y]))
        dep = depth_player_summary(depth[y])
        m = agg.merge(dep, on=["season", "team", "gsis_id"], how="outer")
        ros = pd.read_parquet(f"{RAW}/roster_{y}.parquet")
        ros["team"] = fix_team(ros.team)
        ros = ros.sort_values("week").drop_duplicates("gsis_id", keep="last")
        ros = ros[["gsis_id", "full_name", "position", "pfr_id", "birth_date", "years_exp", "team"]].rename(
            columns={"full_name": "roster_name", "position": "roster_position", "team": "roster_team"})
        m = m.merge(ros, on="gsis_id", how="left")
        st = pd.read_parquet(f"{RAW}/stats_reg_{y}.parquet")[["player_id", "games", "player_display_name", "position"]]
        st = st.rename(columns={"player_id": "gsis_id", "games": "games_season_all_teams",
                                "player_display_name": "stats_name", "position": "stats_position"})
        m = m.merge(st, on="gsis_id", how="left")
        prows.append(m)
    P = pd.concat(prows, ignore_index=True)

    # identity fill
    pl = players.reindex(P.gsis_id)
    P["player_name"] = P.depth_name.fillna(P.roster_name).fillna(P.stats_name).fillna(
        pd.Series(pl.display_name.values, index=P.index))
    P["pfr_id"] = P.pfr_id.fillna(pd.Series(pl.pfr_id.values, index=P.index))
    # first source whose position is a defensive one, in order of specificity to this team-season
    cands = [P.depth_roster_position, P.roster_position, P.stats_position,
             pd.Series(pl.position.values, index=P.index), P.depth_position]
    pos = pd.Series([None] * len(P), index=P.index, dtype=object)
    for c in cands:
        ok = pos.isna() & c.map(pos_group).notna()
        pos[ok] = c[ok]
    # an offensive player that season, never on the defensive depth chart, stays unclassified
    off_season = (P.depth_weeks_listed.fillna(0) == 0) & P.roster_position.notna() & \
        P.roster_position.map(pos_group).isna() & P.stats_position.map(pos_group).isna()
    pos[off_season] = None
    P["position"] = pos
    P["position_group"] = P.position.map(pos_group)
    P["birth_date"] = P.birth_date.fillna(pd.Series(pl.birth_date.values, index=P.index))
    bd = pd.to_datetime(P.birth_date, errors="coerce")
    sept1 = pd.to_datetime(P.season.astype(int).astype(str) + "-09-01")
    P["age_sept1"] = ((sept1 - bd).dt.days / 365.25).round(2)
    P["draft_year"] = pl.draft_year.values
    P["draft_round"] = pl.draft_round.values
    P["draft_pick"] = pl.draft_pick.values
    P["rookie_season"] = pl.rookie_season.values

    dropped = P[P.position_group.isna()]
    P = P[P.position_group.notna()].copy()

    # team games and teams per player-season
    tg = pd.concat([pbp[y].groupby("defteam")["game_id"].nunique().rename("team_games").reset_index().assign(season=y)
                    for y in SEASONS]).rename(columns={"defteam": "team"})
    P = P.merge(tg, on=["season", "team"], how="left")
    # weekly depth charts per team differ by season (16 to 18), so give a share as well as a count
    dc = pd.concat([depth[y].groupby("team")["week"].nunique().rename("team_depth_charts").reset_index().assign(season=y)
                    for y in SEASONS])
    P = P.merge(dc, on=["season", "team"], how="left")
    P["depth_starter_share"] = (P.depth_weeks_starter.fillna(0) / P.team_depth_charts).round(3)
    P["n_teams_season"] = P.groupby(["season", "gsis_id"])["team"].transform("nunique")

    # 2013 snap counts (nflverse 2012 file is empty)
    sn = pd.read_parquet(f"{RAW}/snaps_2013.parquet")
    sn = sn[sn.game_type == "REG"].copy()
    sn["team"] = fix_team(sn.team)
    team_snaps = sn.groupby(["team", "game_id"])["defense_snaps"].max().groupby("team").sum().rename("team_def_snaps_2013")
    # team defensive snaps per game = max player snaps is a lower bound; use snaps/pct where pct>0
    sn_pct = sn[(sn.defense_pct > 0) & (sn.defense_snaps > 0)].copy()
    sn_pct["team_game_snaps"] = (sn_pct.defense_snaps / sn_pct.defense_pct).round()
    tgs = sn_pct.groupby(["team", "game_id"])["team_game_snaps"].median().groupby("team").sum().rename("team_def_snaps")
    ps = sn.groupby(["team", "pfr_player_id"]).agg(def_snaps=("defense_snaps", "sum"),
                                                   games_with_def_snap=("defense_snaps", lambda x: int((x > 0).sum()))).reset_index()
    ps = ps.merge(tgs.reset_index(), on="team", how="left")
    ps["def_snap_pct"] = (ps.def_snaps / ps.team_def_snaps).round(4)
    ps["season"] = 2013
    ps = ps.rename(columns={"pfr_player_id": "pfr_id"})
    P = P.merge(ps[["season", "team", "pfr_id", "def_snaps", "def_snap_pct", "games_with_def_snap", "team_def_snaps"]],
                on=["season", "team", "pfr_id"], how="left")
    P.loc[(P.season == 2013) & P.def_snaps.isna() & P.pfr_id.notna(), ["def_snaps"]] = 0

    count_cols = ["tackles_solo", "tackles_with_assist", "tackle_assists", "tackle_plays", "run_tackle_plays",
                  "run_stops", "pass_tackle_plays", "pass_stops", "tackles_behind_los", "sacks", "sack_plays",
                  "qb_hits", "qb_hits_non_sack", "pressure_plays", "passes_defensed", "interceptions",
                  "forced_fumbles", "fumble_recoveries", "def_penalties", "def_penalty_yards", "dpi", "dpi_yards",
                  "holding_contact_pen", "roughing_passer_pen", "pre_snap_pen", "games_with_def_stat",
                  "depth_weeks_listed", "depth_weeks_starter", "tfl_official"]
    for c in count_cols:
        P[c] = P[c].fillna(0)
    # coverage gaps: official TFL not recorded 2006-2007; QB hits recorded from 2006 on
    P.loc[P.season < 2008, "tfl_official"] = np.nan

    order = ["season", "team", "gsis_id", "pfr_id", "player_name", "position", "position_group", "depth_position",
             "age_sept1", "years_exp", "draft_year", "draft_round", "draft_pick", "n_teams_season",
             "team_games", "games_with_def_stat", "games_season_all_teams", "team_depth_charts", "depth_weeks_listed", "depth_weeks_starter",
             "depth_starter_share",
             "def_snaps", "def_snap_pct", "games_with_def_snap", "team_def_snaps",
             "sacks", "sack_plays", "qb_hits", "qb_hits_non_sack", "pressure_plays", "roughing_passer_pen",
             "tackle_plays", "tackles_solo", "tackles_with_assist", "tackle_assists",
             "run_tackle_plays", "run_stops", "run_tackle_yards_mean", "run_tackle_epa_mean",
             "tackles_behind_los", "tfl_official",
             "pass_tackle_plays", "pass_stops", "pass_tackle_yards_mean", "pass_tackle_epa_mean",
             "passes_defensed", "interceptions", "dpi", "dpi_yards", "holding_contact_pen",
             "forced_fumbles", "fumble_recoveries", "def_penalties", "def_penalty_yards", "pre_snap_pen"]
    P = P[order].sort_values(["season", "team", "position_group", "depth_weeks_starter", "tackle_plays"],
                             ascending=[True, True, True, False, False])
    for c in ["run_tackle_yards_mean", "run_tackle_epa_mean", "pass_tackle_yards_mean", "pass_tackle_epa_mean"]:
        P[c] = P[c].round(3)
    assert P.season.max() <= 2013 and P.season.min() >= 2006
    P.to_csv(f"{OUT}/defense_player_season_2006_2013.csv", index=False)
    print("player rows", len(P), "dropped (no defensive position)", len(dropped))
    keep = ["season", "team", "gsis_id", "pfr_id", "player_name", "roster_position", "stats_position",
            "depth_position", "tackle_plays", "sacks", "qb_hits", "passes_defensed", "interceptions",
            "forced_fumbles", "def_penalties"]
    dropped = dropped.assign(player_name=dropped.depth_name.fillna(dropped.roster_name).fillna(dropped.stats_name))
    dropped[keep].fillna({"tackle_plays": 0}).to_csv(f"{OUT}/defense_unclassified_players_2006_2013.csv", index=False)

    # ---------------- team-season file
    T = build_team(pbp, depth)
    T.to_csv(f"{OUT}/defense_team_season_2006_2013.csv", index=False)
    print("team rows", len(T))


def build_team(pbp, depth):
    rows = []
    for y in LAG_SEASONS:
        p = pbp[y]
        P = p[((p["pass"] == 1) | (p["rush"] == 1)) & p.epa.notna()].copy()
        drop = P[P["pass"] == 1]
        att = P[(P.complete_pass == 1) | (P.incomplete_pass == 1) | (P.interception == 1)]
        att = att[att.sack != 1]
        run = P[P["rush"] == 1]
        neutral = (P.wp.between(0.1, 0.9)) & (P.half_seconds_remaining > 120)

        # leave-one-out opponent offense means (same season)
        def loo(df, by="posteam"):
            s = df.groupby(by)["epa"].agg(["sum", "count"])
            pair = df.groupby([by, "defteam"])["epa"].agg(["sum", "count"])
            j = pair.join(s, on=by, rsuffix="_tot")
            j["loo"] = (j["sum_tot"] - j["sum"]) / (j["count_tot"] - j["count"])
            return j["loo"]

        drop_l = drop.join(loo(drop), on=["posteam", "defteam"])
        run_l = run.join(loo(run), on=["posteam", "defteam"])
        lg_drop, lg_run = drop.epa.mean(), run.epa.mean()

        g = pd.DataFrame(index=sorted(P.defteam.dropna().unique()))
        g["season"] = y
        g["games"] = p.groupby("defteam")["game_id"].nunique()
        g["plays"] = P.groupby("defteam").size()
        g["dropbacks"] = drop.groupby("defteam").size()
        g["pass_attempts"] = att.groupby("defteam").size()
        g["rushes"] = run.groupby("defteam").size()
        g["epa_per_play"] = P.groupby("defteam")["epa"].mean()
        g["epa_per_dropback"] = drop.groupby("defteam")["epa"].mean()
        g["epa_per_pass_att"] = att.groupby("defteam")["epa"].mean()
        g["epa_per_rush"] = run.groupby("defteam")["epa"].mean()
        g["success_dropback"] = drop.groupby("defteam")["success"].mean()
        g["success_rush"] = run.groupby("defteam")["success"].mean()
        g["epa_per_dropback_neutral"] = drop[neutral.loc[drop.index]].groupby("defteam")["epa"].mean()
        g["epa_per_rush_neutral"] = run[neutral.loc[run.index]].groupby("defteam")["epa"].mean()
        # opponent adjustment: play EPA minus the offense's mean against everyone else, recentred to league mean
        g["epa_per_dropback_adj"] = (drop_l.epa - drop_l["loo"]).groupby(drop_l.defteam).mean() + lg_drop
        g["epa_per_rush_adj"] = (run_l.epa - run_l["loo"]).groupby(run_l.defteam).mean() + lg_run
        g["sack_rate"] = drop.groupby("defteam")["sack"].mean()
        hit_or_sack = ((drop.qb_hit == 1) | (drop.sack == 1)).astype(float)
        g["qb_hit_or_sack_rate"] = hit_or_sack.groupby(drop.defteam).mean()
        if y < 2006:
            g["qb_hit_or_sack_rate"] = np.nan  # QB hits not recorded in 2005 pbp
        g["int_rate"] = att.groupby("defteam")["interception"].mean()
        pdflag = (att.pass_defense_1_player_id.notna() | att.interception_player_id.notna()).astype(float)
        g["pass_defensed_rate"] = pdflag.groupby(att.defteam).mean()
        g["completion_rate_allowed"] = att.groupby("defteam")["complete_pass"].mean()
        g["explosive_pass_rate"] = (att.yards_gained >= 20).groupby(att.defteam).mean()
        g["explosive_run_rate"] = (run.yards_gained >= 10).groupby(run.defteam).mean()
        g["run_stuff_rate"] = (run.yards_gained <= 0).groupby(run.defteam).mean()
        g["yards_per_rush"] = run.groupby("defteam")["yards_gained"].mean()

        # defensive penalties on scrimmage downs
        pen = p[(p.penalty_team == p.defteam) & p.penalty_type.notna() &
                ~p.play_type.isin(["punt", "kickoff", "field_goal", "extra_point"]) & (p.special_teams_play != 1)]
        g["def_penalties_per_game"] = pen.groupby("defteam").size() / g["games"]
        dpi = pen[pen.penalty_type == "Defensive Pass Interference"]
        g["dpi_count"] = dpi.groupby("defteam").size()
        g["dpi_yards"] = dpi.groupby("defteam")["penalty_yards"].sum()

        # drives faced
        dr = p[p.fixed_drive.notna() & p.posteam.notna() & p.defteam.notna()]
        dr = dr.groupby(["game_id", "fixed_drive"]).agg(defteam=("defteam", "first"),
                                                       result=("fixed_drive_result", "first")).reset_index()
        g["drives_faced"] = dr.groupby("defteam").size()
        for name, res in [("td_per_drive", "Touchdown"), ("fg_per_drive", "Field goal"),
                          ("turnover_per_drive", "Turnover"), ("punt_per_drive", "Punt")]:
            g[name] = (dr.result == res).groupby(dr.defteam).mean()
        g["points_per_drive_approx"] = (7 * (dr.result == "Touchdown") + 3 * (dr.result == "Field goal")).groupby(dr.defteam).mean()

        # points allowed per game (final scores, includes non-offensive scores)
        fin = p.groupby("game_id").agg(home=("home_team", "first"), away=("away_team", "first"),
                                       hs=("total_home_score", "max"), as_=("total_away_score", "max"))
        pa = pd.concat([fin[["home", "as_"]].rename(columns={"home": "team", "as_": "pa"}),
                        fin[["away", "hs"]].rename(columns={"away": "team", "hs": "pa"})])
        g["points_allowed_per_game"] = pa.groupby("team")["pa"].mean()

        # starter continuity from depth charts (leakage-safe: season t week-1 chart vs season t-1 starters)
        if y - 1 in depth:
            cur, prev = depth[y], depth[y - 1]
            wk1 = cur[cur.week == cur.week.min()]
            prev_st = prev[prev.depth_team == 1].drop_duplicates(["team", "gsis_id", "week"])
            prev_weeks = prev_st.groupby(["team", "gsis_id"]).size().rename("w").reset_index()
            share, ret = {}, {}
            for t in g.index:
                pw = prev_weeks[prev_weeks.team == t]
                listed = set(wk1[wk1.team == t].gsis_id)
                starters = set(wk1[(wk1.team == t) & (wk1.depth_team == 1)].gsis_id)
                share[t] = pw[pw.gsis_id.isin(listed)].w.sum() / pw.w.sum() if pw.w.sum() else np.nan
                ret[t] = len(starters & set(pw[pw.w >= 4].gsis_id))
            g["prev_starter_weeks_share_returning"] = pd.Series(share)
            g["wk1_starters_returning"] = pd.Series(ret)
        rows.append(g.rename_axis("team").reset_index())

    T = pd.concat(rows, ignore_index=True)
    lag_cols = ["epa_per_play", "epa_per_dropback", "epa_per_pass_att", "epa_per_rush", "epa_per_dropback_adj",
                "epa_per_rush_adj", "success_dropback", "success_rush", "sack_rate", "qb_hit_or_sack_rate",
                "int_rate", "td_per_drive", "points_per_drive_approx"]
    T = T.sort_values(["team", "season"])
    for c in lag_cols:
        T[c + "_prev"] = T.groupby("team")[c].shift(1)
        # guard against gaps
        T.loc[T.groupby("team")["season"].diff() != 1, c + "_prev"] = np.nan
    T = T[T.season.isin(SEASONS)].sort_values(["season", "team"])
    num = T.select_dtypes("number").columns.difference(["season", "games", "plays", "dropbacks", "pass_attempts",
                                                        "rushes", "dpi_count", "dpi_yards", "drives_faced",
                                                        "wk1_starters_returning"])
    T[num] = T[num].round(4)
    assert len(T) == 256 and T.season.max() <= 2013
    return T


if __name__ == "__main__":
    main()
