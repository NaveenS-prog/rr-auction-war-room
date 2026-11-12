import pandas as pd
import pytest
from src.canonical_data import build_delivery_state

def test_delivery_state_reconstruction_legal_and_extras():
    # Synthetic 3-ball innings
    raw_deliveries = pd.DataFrame([
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 1, "innings_ball_num": 1,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 100, "striker_name": "Batter A",
            "non_striker_id": 101, "non_striker_name": "Batter B", "bowler_id": 200, "bowler_name": "Bowler X",
            "runs": 0, "is_four": False, "is_six": False, "is_wicket": False, "dismissal_type": None,
            "dismissed_player_id": None, "extras_type": "wides", "extras1_runs": 1, "extras_2_runs": 0
        },
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 1, "innings_ball_num": 2,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 100, "striker_name": "Batter A",
            "non_striker_id": 101, "non_striker_name": "Batter B", "bowler_id": 200, "bowler_name": "Bowler X",
            "runs": 4, "is_four": True, "is_six": False, "is_wicket": False, "dismissal_type": None,
            "dismissed_player_id": None, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0
        },
        {
            "match_id": 1, "innings": 1, "overid": 1, "over_ball_num": 2, "innings_ball_num": 3,
            "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 100, "striker_name": "Batter A",
            "non_striker_id": 101, "non_striker_name": "Batter B", "bowler_id": 200, "bowler_name": "Bowler X",
            "runs": 0, "is_four": False, "is_six": False, "is_wicket": True, "dismissal_type": "caught",
            "dismissed_player_id": 100, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0
        }
    ])
    
    matches = pd.DataFrame([{
        "match_id": 1, "comp_id": 1000, "match_date": "2022-04-01", "venue_id": 50,
        "first_inn_revised_overs": None, "second_inn_revised_overs": None, "revised_target": None,
        "home_team_id": 10, "away_team_id": 20, "win_team_id": 10
    }])
    
    result = build_delivery_state(raw_deliveries, matches)
    
    # Ball 1 (Wide): legal balls bowled before is 0, remaining is 120, score before is 0
    assert result.iloc[0]["legal_balls_bowled"] == 0
    assert result.iloc[0]["legal_balls_remaining"] == 120
    assert result.iloc[0]["runs_before"] == 0
    assert result.iloc[0]["is_legal_delivery"] == False
    assert result.iloc[0]["wides"] == 1
    
    # Ball 2 (after wide, legal ball 1): score before is 1, legal balls bowled before is 0
    assert result.iloc[1]["runs_before"] == 1
    assert result.iloc[1]["legal_balls_bowled"] == 0
    assert result.iloc[1]["is_legal_delivery"] == True
    assert result.iloc[1]["runs_off_bat"] == 4
    
    # Ball 3 (legal ball 2): score before is 5, legal balls bowled before is 1, wickets before is 0
    assert result.iloc[2]["runs_before"] == 5
    assert result.iloc[2]["legal_balls_bowled"] == 1
    assert result.iloc[2]["wickets_before"] == 0
    assert result.iloc[2]["bowler_credited_wicket"] == True
    assert result.iloc[2]["striker_dismissed"] == True

def test_second_innings_target_and_run_rate():
    # 2 innings match
    inn1 = pd.DataFrame([{
        "match_id": 2, "innings": 1, "overid": 1, "over_ball_num": 1, "innings_ball_num": 1,
        "batting_team_id": 10, "bowling_team_id": 20, "striker_id": 100, "striker_name": "A",
        "non_striker_id": 101, "non_striker_name": "B", "bowler_id": 200, "bowler_name": "X",
        "runs": 6, "is_four": False, "is_six": True, "is_wicket": False, "dismissal_type": None,
        "dismissed_player_id": None, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0
    }])
    inn2 = pd.DataFrame([{
        "match_id": 2, "innings": 2, "overid": 1, "over_ball_num": 1, "innings_ball_num": 1,
        "batting_team_id": 20, "bowling_team_id": 10, "striker_id": 201, "striker_name": "C",
        "non_striker_id": 202, "non_striker_name": "D", "bowler_id": 102, "bowler_name": "Y",
        "runs": 1, "is_four": False, "is_six": False, "is_wicket": False, "dismissal_type": None,
        "dismissed_player_id": None, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0
    }])
    raw = pd.concat([inn1, inn2], ignore_index=True)
    matches = pd.DataFrame([{
        "match_id": 2, "comp_id": 1000, "match_date": "2022-04-02", "venue_id": 50,
        "first_inn_revised_overs": None, "second_inn_revised_overs": None, "revised_target": None,
        "home_team_id": 10, "away_team_id": 20, "win_team_id": 10
    }])
    
    res = build_delivery_state(raw, matches)
    inn2_row = res[res["innings"] == 2].iloc[0]
    
    # Target should be 6 + 1 = 7
    assert inn2_row["target"] == 7
    assert inn2_row["runs_required"] == 7
    # 7 runs required in 120 balls = (7 / 120) * 6 = 0.35
    assert round(inn2_row["required_run_rate"], 2) == 0.35
