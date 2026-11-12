from typing import Optional
import numpy as np
import pandas as pd
from src.models.expectation import ExpectationModelPipeline
from src.models.pressure import PressureEngine
from src.make_splits import MatchSplits

def compute_wicket_run_value(df: pd.DataFrame, base_wicket_value: float = 9.0) -> np.ndarray:
    balls_rem = pd.to_numeric(df["legal_balls_remaining"], errors="coerce").fillna(60.0).values
    wkts_rem = pd.to_numeric(df["wickets_remaining"], errors="coerce").fillna(5.0).values
    
    # Dynamic run value: higher with more overs & wickets left
    factor = 0.6 + 0.25 * (balls_rem / 120.0) + 0.25 * (wkts_rem / 10.0)
    return base_wicket_value * np.clip(factor, 0.5, 1.4)

def compute_run_equivalent_contributions(
    df: pd.DataFrame,
    base_wicket_value: float = 9.0
) -> pd.DataFrame:
    res = df.copy()
    
    # Batting residuals
    runs_off_bat = pd.to_numeric(res.get("runs_off_bat", 0), errors="coerce").fillna(0)
    exp_runs = pd.to_numeric(res.get("expected_runs", 1.0), errors="coerce").fillna(1.0)
    res["r_runs"] = runs_off_bat - exp_runs
    
    striker_dismissed = pd.to_numeric(res.get("striker_dismissed", 0), errors="coerce").fillna(0)
    dismissal_prob = pd.to_numeric(res.get("dismissal_prob", 0.05), errors="coerce").fillna(0.05)
    # Higher is better: surviving (0) when dismissal prob was p gives +p; getting dismissed (1) gives -(1-p)
    res["r_survival"] = dismissal_prob - striker_dismissed
    
    # Bowling residuals
    wides = pd.to_numeric(res.get("wides", 0), errors="coerce").fillna(0)
    no_balls = pd.to_numeric(res.get("no_balls", 0), errors="coerce").fillna(0)
    conceded = runs_off_bat + wides + no_balls
    exp_conceded = pd.to_numeric(res.get("expected_conceded", 1.2), errors="coerce").fillna(1.2)
    # Higher is better: conceding fewer runs than expected gives positive score
    res["r_economy"] = exp_conceded - conceded
    
    bowler_wkt = pd.to_numeric(res.get("bowler_credited_wicket", 0), errors="coerce").fillna(0)
    wkt_prob = pd.to_numeric(res.get("wicket_prob", 0.05), errors="coerce").fillna(0.05)
    # Higher is better: taking a wicket gives +(1 - wkt_prob)
    res["r_wickets"] = bowler_wkt - wkt_prob
    
    # Dynamic wicket cost
    c_s = compute_wicket_run_value(res, base_wicket_value=base_wicket_value)
    res["wicket_run_value"] = c_s
    
    # Run-equivalent composites
    res["v_bat"] = res["r_runs"] + (c_s * res["r_survival"])
    res["v_bowl"] = res["r_economy"] + (c_s * res["r_wickets"])
    
    return res

def generate_out_of_sample_contributions(
    df: pd.DataFrame,
    splits: MatchSplits,
    pressure_percentile: float = 80.0,
    base_wicket_value: float = 9.0
) -> pd.DataFrame:
    # 1. Fit expectation and pressure models on training data
    train_df = splits.get_split_deliveries(df, "train")
    if train_df.empty:
        train_df = df.copy()
        
    exp_pipeline = ExpectationModelPipeline()
    exp_pipeline.fit(train_df)
    
    press_engine = PressureEngine()
    press_engine.fit(train_df)
    
    # Predict across entire dataset
    bat_exp = exp_pipeline.predict_batting_expectations(df)
    bowl_exp = exp_pipeline.predict_bowling_expectations(df)
    
    df_out = df.copy()
    df_out["expected_runs"] = bat_exp.expected_runs
    df_out["dismissal_prob"] = bat_exp.dismissal_prob
    df_out["expected_conceded"] = bowl_exp.expected_conceded
    df_out["wicket_prob"] = bowl_exp.wicket_prob
    
    # Pressure classification
    leverage = press_engine.compute_leverage_spread(df)
    df_out["leverage"] = leverage
    cutoff = np.percentile(press_engine.compute_leverage_spread(train_df), pressure_percentile)
    df_out["is_pressure"] = (leverage >= cutoff)
    
    # Benchmark pressure for comparative evaluation
    df_out["benchmark_pressure"] = press_engine.compute_benchmark_pressure(df)
    
    # Contributions
    df_out = compute_run_equivalent_contributions(df_out, base_wicket_value=base_wicket_value)
    return df_out
