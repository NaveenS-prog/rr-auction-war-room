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
