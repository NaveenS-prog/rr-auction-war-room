import numpy as np
import pandas as pd
import pytest
from src.evaluate import compute_top10_jaccard_overlap, evaluate_predictive_validity
from src.models.player_ratings import FittedRatings

def test_top10_jaccard_overlap():
    list_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    list_b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11] # 9 out of 10 match
    score = compute_top10_jaccard_overlap(list_a, list_b)
    # 9 in intersection / 11 in union = 9/11 ~ 0.818
    assert round(score, 3) == 0.818

def test_evaluate_predictive_validity():
    ratings = FittedRatings(
        player_ids=[1, 2],
        normal_ability_mean=np.array([0.2, 0.1]),
        pressure_ability_mean=np.array([1.5, -0.5]),
        pressure_uplift_mean=np.array([1.3, -0.6]),
        conservative_score=np.array([1.2, -0.8]),
        prob_positive_uplift=np.array([0.95, 0.05]),
        player_stats=pd.DataFrame([
            {"player_id": 1, "total_balls": 100, "pressure_balls": 50},
            {"player_id": 2, "total_balls": 100, "pressure_balls": 50}
        ])
    )
    
    test_deliveries = pd.DataFrame([
        {"striker_id": 1, "is_pressure": 1, "v_bat": 1.4},
        {"striker_id": 1, "is_pressure": 1, "v_bat": 1.6},
        {"striker_id": 2, "is_pressure": 1, "v_bat": -0.4},
        {"striker_id": 2, "is_pressure": 1, "v_bat": -0.6}
    ])
    
    metrics = evaluate_predictive_validity(ratings, test_deliveries, target_col="v_bat", player_col="striker_id")
    assert "model_c_rmse" in metrics
    assert "correlation" in metrics
    assert metrics["correlation"] > 0.9
