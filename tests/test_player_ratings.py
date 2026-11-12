import numpy as np
import pandas as pd
import pytest
from src.models.player_ratings import HierarchicalPlayerModel, FittedRatings

def test_hierarchical_player_model_shrinkage():
    np.random.seed(42)
    # Player 1: Elite pressure player with 100 balls, +1.0 avg contribution
    # Player 2: Small sample noisy player with 5 balls, +1.0 avg contribution
    data = []
    for _ in range(100):
        data.append({"player_id": 1, "is_pressure": 1, "v_contribution": 1.0 + np.random.normal(0, 0.1), "match_id": 10})
        data.append({"player_id": 1, "is_pressure": 0, "v_contribution": 0.2 + np.random.normal(0, 0.1), "match_id": 10})
    for _ in range(5):
        data.append({"player_id": 2, "is_pressure": 1, "v_contribution": 1.0 + np.random.normal(0, 0.1), "match_id": 11})
        data.append({"player_id": 2, "is_pressure": 0, "v_contribution": 0.2 + np.random.normal(0, 0.1), "match_id": 11})
        
    df = pd.DataFrame(data)
    model = HierarchicalPlayerModel(n_samples=500, random_state=42)
    ratings = model.fit(df, target_col="v_contribution", player_col="player_id")
    
    assert isinstance(ratings, FittedRatings)
    assert 1 in ratings.player_ids
    assert 2 in ratings.player_ids
    
    p1_idx = ratings.player_ids.index(1)
    p2_idx = ratings.player_ids.index(2)
    
    # Player 2 with few samples must shrink more and have wider uncertainty interval
    # Thus Player 1's conservative 10th percentile score must exceed Player 2's
    assert ratings.conservative_score[p1_idx] > ratings.conservative_score[p2_idx]
    assert ratings.prob_positive_uplift[p1_idx] > 0.5
