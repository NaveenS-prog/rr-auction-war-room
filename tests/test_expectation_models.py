import numpy as np
import pandas as pd
import pytest
from src.models.expectation import ExpectationModelPipeline, BattingExpectations, BowlingExpectations

def test_expectation_models_fit_and_predict():
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        "innings": np.random.choice([1, 2], n),
        "legal_balls_remaining": np.random.randint(1, 120, n),
        "wickets_remaining": np.random.randint(1, 11, n),
        "runs_before": np.random.randint(0, 180, n),
        "required_run_rate": np.random.uniform(6.0, 12.0, n),
        "current_run_rate": np.random.uniform(5.0, 10.0, n),
        "is_legal_delivery": [True] * (n - 10) + [False] * 10,
        "runs_off_bat": np.random.choice([0, 1, 2, 4, 6], n),
        "wides": [0] * (n - 5) + [1] * 5,
        "no_balls": [0] * (n - 5) + [1] * 5,
        "striker_dismissed": np.random.choice([0, 1], p=[0.95, 0.05], size=n),
        "bowler_credited_wicket": np.random.choice([0, 1], p=[0.95, 0.05], size=n),
        "total_runs": np.random.choice([0, 1, 2, 4, 6], n)
    })
    
    pipeline = ExpectationModelPipeline()
    pipeline.fit(df)
    
    bat_exp = pipeline.predict_batting_expectations(df)
    assert isinstance(bat_exp, BattingExpectations)
    assert len(bat_exp.expected_runs) == n
    assert (bat_exp.expected_runs >= 0).all()
    assert (bat_exp.dismissal_prob >= 0).all() and (bat_exp.dismissal_prob <= 1).all()
    
    bowl_exp = pipeline.predict_bowling_expectations(df)
    assert isinstance(bowl_exp, BowlingExpectations)
    assert len(bowl_exp.expected_conceded) == n
    assert (bowl_exp.expected_conceded >= 0).all()
    assert (bowl_exp.wicket_prob >= 0).all() and (bowl_exp.wicket_prob <= 1).all()

def test_opponent_adjusted_features_and_priors():
    """Verify that player IDs, batting order, and pace/spin features are properly extracted and prior-adjusted."""
    n = 100
    df = pd.DataFrame({
        "innings": [1] * n,
        "legal_balls_remaining": [60] * n,
        "wickets_remaining": [5] * n,
        "runs_before": [80] * n,
        "required_run_rate": [0.0] * n,
        "current_run_rate": [8.0] * n,
        "is_legal_delivery": [True] * n,
        "runs_off_bat": [1] * n,
        "wides": [0] * n,
        "no_balls": [0] * n,
        "striker_dismissed": [0] * n,
        "bowler_credited_wicket": [0] * n,
        "total_runs": [1] * n,
        "striker_id": [101] * (n // 2) + [102] * (n // 2),
        "bowler_id": [201] * (n // 2) + [202] * (n // 2),
        "batting_order": [1] * (n // 2) + [9] * (n // 2),
        "pace_or_spin": ["Pace"] * (n // 2) + ["Spin"] * (n // 2),
    })
    
    pipeline = ExpectationModelPipeline()
    pipeline.fit(df)
    assert pipeline.is_fitted
    assert len(pipeline.bowler_priors) == 2
    assert len(pipeline.batter_priors) == 2
    
    bat_features = pipeline._extract_batting_features(df)
    assert "opp_bowler_econ" in bat_features.columns
    assert "opp_bowler_wkt" in bat_features.columns
    assert "batting_order" in bat_features.columns
    assert "is_spin" in bat_features.columns
    
    bowl_features = pipeline._extract_bowling_features(df)
    assert "opp_batter_sr" in bowl_features.columns
    assert "opp_batter_dis" in bowl_features.columns
