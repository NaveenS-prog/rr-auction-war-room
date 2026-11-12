import pandas as pd
import pytest
from src.ranking import RankingEngine
from src.models.player_ratings import FittedRatings
import numpy as np

def test_ranking_engine_eligibility_and_top_10():
    ratings = FittedRatings(
        player_ids=[1, 2],
        normal_ability_mean=np.array([0.5, 0.5]),
        pressure_ability_mean=np.array([1.8, 2.5]),
        pressure_uplift_mean=np.array([1.3, 2.0]),
        conservative_score=np.array([1.45, 2.00]),
        prob_positive_uplift=np.array([0.95, 0.99]),
        player_stats=pd.DataFrame([
            {"player_id": 1, "total_balls": 150, "pressure_balls": 60, "normal_balls": 90},
            {"player_id": 2, "total_balls": 120, "pressure_balls": 15, "normal_balls": 105} # Ineligible (<40 pressure balls)
        ])
    )
    
    match_counts = pd.DataFrame([
        {"player_id": 1, "pressure_matches": 12},
        {"player_id": 2, "pressure_matches": 4}
    ])
    
    player_meta = pd.DataFrame([
        {"player_id": 1, "player_name": "Player Eligible Top", "team_name": "Team A"},
        {"player_id": 2, "player_name": "Player Ineligible (Low Sample)", "team_name": "Team B"}
    ])
    
    eligibility = {"min_total_balls": 100, "min_pressure_balls": 40, "min_pressure_matches": 8}
    engine = RankingEngine(eligibility=eligibility)
    
    leaderboard = engine.generate_leaderboard(ratings, match_counts, player_meta)
    top_10 = engine.get_top_10(leaderboard)
    
    assert len(top_10) == 1
    assert top_10.iloc[0]["player_id"] == 1
    assert top_10.iloc[0]["rank"] == 1
    assert top_10.iloc[0]["is_eligible"] == True
