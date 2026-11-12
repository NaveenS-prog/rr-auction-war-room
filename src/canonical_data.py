from pathlib import Path
from typing import Optional, Union
import numpy as np
import pandas as pd

NON_BOWLER_DISMISSALS = {
    "run out", "retired hurt", "retired out", "obstructing the field", "timed out"
}

def build_delivery_state(raw_deliveries: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    df = raw_deliveries.copy()
    
    # 1. Clean types and sort
    sort_cols = ["match_id", "innings", "overid", "over_ball_num", "innings_ball_num"]
    avail_sort_cols = [c for c in sort_cols if c in df.columns]
    df = df.sort_values(avail_sort_cols).reset_index(drop=True)
    
    # Generate unique delivery_id
    if "delivery_id" not in df.columns:
        df["delivery_id"] = np.arange(1, len(df) + 1)
        
    # Standardize extras and runs
    df["runs"] = pd.to_numeric(df["runs"], errors="coerce").fillna(0).astype(int)
    df["runs_off_bat"] = df["runs"]
    df["extras1_runs"] = pd.to_numeric(df["extras1_runs"], errors="coerce").fillna(0).astype(int)
    df["extras_2_runs"] = pd.to_numeric(df["extras_2_runs"], errors="coerce").fillna(0).astype(int)
    df["total_extras"] = df["extras1_runs"] + df["extras_2_runs"]
    df["total_runs"] = df["runs_off_bat"] + df["total_extras"]
    
    # Extras categorization
    extras_type = df["extras_type"].astype(str).str.lower().fillna("none")
    df["wides"] = np.where(extras_type.str.contains("wide"), df["total_extras"], 0)
    df["no_balls"] = np.where(extras_type.str.contains("no ball"), df["total_extras"], 0)
    df["byes"] = np.where(extras_type.str.contains("bye") & ~extras_type.str.contains("leg"), df["total_extras"], 0)
    df["leg_byes"] = np.where(extras_type.str.contains("leg bye"), df["total_extras"], 0)
    
    # Legal ball definition: not wide and not no-ball
    df["is_legal_delivery"] = ~extras_type.isin(["wides", "wide", "no balls", "no_balls", "noball"])
    
    # Wicket classification
    is_wkt = df["is_wicket"].astype(str).str.lower().isin(["true", "1"])
    df["is_wicket"] = is_wkt
    dismissal_str = df["dismissal_type"].astype(str).str.lower().fillna("")
    
    df["bowler_credited_wicket"] = is_wkt & (~dismissal_str.isin(NON_BOWLER_DISMISSALS))
    
    if "dismissed_player_id" in df.columns:
        dismissed_id = pd.to_numeric(df["dismissed_player_id"], errors="coerce")
        striker_id = pd.to_numeric(df["striker_id"], errors="coerce")
        df["striker_dismissed"] = is_wkt & (dismissed_id == striker_id)
    else:
        df["striker_dismissed"] = is_wkt

    # Cumulative calculations per match and innings
    grp = df.groupby(["match_id", "innings"], group_keys=False)
    
    # Pre-delivery state features
    df["runs_before"] = grp["total_runs"].shift(1).fillna(0).astype(int)
    df["wickets_before"] = grp["is_wicket"].shift(1).fillna(0).astype(int)
    # Cumulative sum
    df["runs_before"] = grp["total_runs"].cumsum() - df["total_runs"]
    df["wickets_before"] = grp["is_wicket"].cumsum() - df["is_wicket"]
    df["wickets_remaining"] = np.maximum(0, 10 - df["wickets_before"])
    
    # Cumulative legal balls bowled before this delivery
    legal_int = df["is_legal_delivery"].astype(int)
    df["legal_balls_bowled"] = df.groupby(["match_id", "innings"])[legal_int.name].cumsum() - legal_int
    
    # Match metadata join
    match_meta = matches[["match_id"]].copy()
    if "comp_id" in matches.columns:
        match_meta["comp_id"] = matches["comp_id"]
    if "match_date" in matches.columns:
        match_meta["match_date"] = matches["match_date"]
    if "venue_id" in matches.columns:
        match_meta["venue_id"] = matches["venue_id"]
    if "first_inn_revised_overs" in matches.columns:
        match_meta["first_inn_revised_overs"] = pd.to_numeric(matches["first_inn_revised_overs"], errors="coerce")
    if "second_inn_revised_overs" in matches.columns:
        match_meta["second_inn_revised_overs"] = pd.to_numeric(matches["second_inn_revised_overs"], errors="coerce")
    if "revised_target" in matches.columns:
        match_meta["revised_target"] = pd.to_numeric(matches["revised_target"], errors="coerce")
    if "win_team_id" in matches.columns:
        match_meta["win_team_id"] = matches["win_team_id"]
        
    df = df.merge(match_meta, on="match_id", how="left")
    
    # Determine scheduled balls per innings
    def get_scheduled_balls(row):
        inn = row["innings"]
        if inn == 1 and pd.notna(row.get("first_inn_revised_overs")) and row["first_inn_revised_overs"] > 0:
            return int(row["first_inn_revised_overs"] * 6)
        if inn == 2 and pd.notna(row.get("second_inn_revised_overs")) and row["second_inn_revised_overs"] > 0:
            return int(row["second_inn_revised_overs"] * 6)
        return 120

    df["scheduled_innings_balls"] = df.apply(get_scheduled_balls, axis=1)
    df["legal_balls_remaining"] = np.maximum(0, df["scheduled_innings_balls"] - df["legal_balls_bowled"])
    
    # Target and Chase requirements
    # 1st innings total per match
    first_inn_totals = df[df["innings"] == 1].groupby("match_id")["total_runs"].sum().to_dict()
    
    targets = []
    for _, row in df.iterrows():
        mid = row["match_id"]
        inn = row["innings"]
        if inn == 1:
            targets.append(np.nan)
        else:
            rev_tgt = row.get("revised_target")
            if pd.notna(rev_tgt) and rev_tgt > 0:
                targets.append(float(rev_tgt))
            elif mid in first_inn_totals:
                targets.append(float(first_inn_totals[mid] + 1))
            else:
                targets.append(np.nan)
                
    df["target"] = targets
    df["runs_required"] = np.where(
        df["innings"] == 2,
        np.maximum(0, df["target"] - df["runs_before"]),
        np.nan
    )
    
    # Current Run Rate & Required Run Rate
    # CRR: runs_before / (legal_balls_bowled / 6)
    overs_bowled = df["legal_balls_bowled"] / 6.0
    df["current_run_rate"] = np.where(overs_bowled > 0, df["runs_before"] / overs_bowled, 0.0)
    
    # RRR: runs_required / (legal_balls_remaining / 6)
    overs_remaining = df["legal_balls_remaining"] / 6.0
    df["required_run_rate"] = np.where(
        (df["innings"] == 2) & (overs_remaining > 0),
        df["runs_required"] / overs_remaining,
        np.nan
    )
    
    # Batting team won indicator (for win probability models)
    if "win_team_id" in df.columns and "batting_team_id" in df.columns:
        df["batting_team_won"] = (df["batting_team_id"] == df["win_team_id"]).astype(int)
    else:
        df["batting_team_won"] = np.nan
        
    return df

def reconstruct_canonical_deliveries(raw_dir: Union[str, Path]) -> pd.DataFrame:
    raw_p = Path(raw_dir)
    bbb_path = raw_p / "ball_by_ball.csv"
    matches_path = raw_p / "matches.csv"
    competitions_path = raw_p / "competitions.csv"
    
    if not bbb_path.exists():
        raise FileNotFoundError(f"Missing ball_by_ball.csv at {bbb_path}")
    if not matches_path.exists():
        raise FileNotFoundError(f"Missing matches.csv at {matches_path}")
        
    raw_bbb = pd.read_csv(bbb_path, low_memory=False)
    matches = pd.read_csv(matches_path, low_memory=False)
    
    if competitions_path.exists():
        comps = pd.read_csv(competitions_path, low_memory=False)
        matches = matches.merge(comps[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")
        
    canonical_df = build_delivery_state(raw_bbb, matches)
    return canonical_df
