import numpy as np
import pandas as pd
import pytest
from src.models.pressure import PressureEngine

def test_pressure_engine_win_prob_and_leverage():
    # Construct a close final over vs a blowout match
    df = pd.DataFrame([
        # Tight finish: 2nd innings, 6 balls remaining, 10 runs required, 3 wickets down (7 in hand)
        {
            "innings": 2, "legal_balls_remaining": 6, "wickets_remaining": 7,
            "runs_before": 150, "target": 160, "runs_required": 10, "required_run_rate": 10.0,
            "batting_team_won": 1
        },
        # Dead rubber / blowout: 2nd innings, 6 balls remaining, 60 runs required, 9 wickets down (1 in hand)
        {
            "innings": 2, "legal_balls_remaining": 6, "wickets_remaining": 1,
            "runs_before": 100, "target": 160, "runs_required": 60, "required_run_rate": 60.0,
            "batting_team_won": 0
        },
        # Mid-innings balanced
        {
            "innings": 2, "legal_balls_remaining": 60, "wickets_remaining": 8,
            "runs_before": 80, "target": 160, "runs_required": 80, "required_run_rate": 8.0,
            "batting_team_won": 1
        },
        # Innings 1
        {
            "innings": 1, "legal_balls_remaining": 12, "wickets_remaining": 4,
            "runs_before": 140, "target": np.nan, "runs_required": np.nan, "required_run_rate": np.nan,
            "batting_team_won": 1
        }
    ])
    
    engine = PressureEngine()
    engine.fit(df)
    
    win_probs = engine.predict_win_probability(df)
    assert len(win_probs) == len(df)
    assert (win_probs >= 0.0).all() and (win_probs <= 1.0).all()
    
    leverage = engine.compute_leverage_spread(df)
    assert len(leverage) == len(df)
    assert (leverage >= 0.0).all()
    
    # The close game must have higher leverage than the blowout game
    assert leverage[0] > leverage[1]
    
    pressure_mask = engine.classify_pressure(df, percentile=50.0)
    assert len(pressure_mask) == len(df)
    assert pressure_mask.dtype == bool
