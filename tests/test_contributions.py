import numpy as np
import pandas as pd
import pytest
from src.contributions import compute_run_equivalent_contributions, generate_out_of_sample_contributions
from src.make_splits import MatchSplits

def test_compute_run_equivalent_contributions():
    deliveries = pd.DataFrame([
        {
            "runs_off_bat": 6, "expected_runs": 1.2,
            "striker_dismissed": 0, "dismissal_prob": 0.05,
            "total_runs": 6, "expected_conceded": 1.2,
            "bowler_credited_wicket": 0, "wicket_prob": 0.05,
            "wides": 0, "no_balls": 0,
            "wickets_remaining": 8, "legal_balls_remaining": 60
        }
    ])
    
    result = compute_run_equivalent_contributions(deliveries)
    # Batter hit a 6 when 1.2 was expected: +4.8 runs off bat
    assert round(result.iloc[0]["r_runs"], 2) == 4.8
    # Batter survived: +0.05 survival residual
    assert round(result.iloc[0]["r_survival"], 2) == 0.05
    # Bowler conceded 6 when 1.2 was expected: -4.8 economy residual
    assert round(result.iloc[0]["r_economy"], 2) == -4.8
    # v_bat must be greater than r_runs due to survival bonus
    assert result.iloc[0]["v_bat"] > result.iloc[0]["r_runs"]

def test_generate_out_of_sample_contributions_pipeline():
    # Synthetic mini-match dataset with 4 matches
    data = []
    for m in range(1, 5):
        for b in range(1, 20):
            data.append({
                "match_id": m,
                "innings": 1,
                "legal_balls_remaining": 120 - b,
                "wickets_remaining": 9,
                "runs_before": b * 2,
                "required_run_rate": 0.0,
                "current_run_rate": 8.0,
                "is_legal_delivery": True,
                "runs_off_bat": 1,
                "total_runs": 1,
                "wides": 0,
                "no_balls": 0,
                "striker_dismissed": 0,
                "bowler_credited_wicket": 0,
                "batting_team_won": 1,
                "striker_id": 100,
                "bowler_id": 200
            })
    df = pd.DataFrame(data)
    splits = MatchSplits(
        train_matches=[1, 2],
        val_matches=[3],
        test_matches=[4],
        expanding_folds=[([1], [2])]
    )
    
    contrib_df = generate_out_of_sample_contributions(df, splits)
    assert "v_bat" in contrib_df.columns
    assert "v_bowl" in contrib_df.columns
    assert "is_pressure" in contrib_df.columns
    assert len(contrib_df) == len(df)
