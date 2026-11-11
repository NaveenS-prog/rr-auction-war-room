import numpy as np
import pandas as pd
import pytest

from src.win_prob import compute_win_probability_and_leverage, train_win_prob_models


def test_win_prob_and_leverage_pipeline():
    # Synthetic match data for quick test
    rows = []
    for inn in [1, 2]:
        for b in range(1, 121):
            rows.append({
                "match_id": 1001,
                "innings": inn,
                "overid": (b - 1) // 6 + 1,
                "over_ball_num": (b - 1) % 6 + 1,
                "balls_remaining_innings": 120 - b,
                "cum_runs_innings": int(b * 1.4),
                "cum_wickets_innings": min(b // 20, 9),
                "phase": "Powerplay" if b <= 36 else ("Middle" if b <= 90 else "Death"),
                "runs": 1,
                "is_bowler_wicket": False,
                "comp_weight": 1.0,
                "target_runs": 170 if inn == 2 else 0,
                "runs_required": max(0, 170 - int(b * 1.4)) if inn == 2 else 0,
                "required_run_rate": ((170 - int(b * 1.4)) / max(1, 120 - b)) * 6 if inn == 2 else 0.0,
                "venue_country": "India",
                "home_team_id": 1,
                "away_team_id": 2,
                "win_team_id": 2,
            })
    df_synthetic = pd.DataFrame(rows)
    models = train_win_prob_models(df_synthetic)
    df_result = compute_win_probability_and_leverage(df_synthetic, models)

    assert "win_prob" in df_result.columns
    assert "delta_wpa" in df_result.columns
    assert "leverage_index" in df_result.columns
    assert "is_high_pressure" in df_result.columns
    assert ((df_result["win_prob"] >= 0.0) & (df_result["win_prob"] <= 1.0)).all()
    assert (df_result["leverage_index"] >= 0.0).all()


def test_win_prob_bounds_and_extremes():
    # Innings 1 blowout test: 10/5 in 3 overs (18 balls, 102 balls left)
    blowout_rows = [
        {
            "match_id": 9999,
            "innings": 1,
            "overid": 3,
            "over_ball_num": 6,
            "balls_remaining_innings": 102,
            "cum_runs_innings": 10,
            "cum_wickets_innings": 5,
            "phase": "Powerplay",
            "runs": 0,
            "is_bowler_wicket": True,
            "comp_weight": 1.0,
            "target_runs": 0,
            "runs_required": 0,
            "required_run_rate": 0.0,
            "venue_country": "India",
            "home_team_id": 1,
            "away_team_id": 2,
            "win_team_id": 2,
        },
        # Innings 2 terminal won state
        {
            "match_id": 9999,
            "innings": 2,
            "overid": 19,
            "over_ball_num": 4,
            "balls_remaining_innings": 8,
            "cum_runs_innings": 172,
            "cum_wickets_innings": 4,
            "phase": "Death",
            "runs": 4,
            "is_bowler_wicket": False,
            "comp_weight": 1.0,
            "target_runs": 170,
            "runs_required": 0,
            "required_run_rate": 0.0,
            "venue_country": "India",
            "home_team_id": 1,
            "away_team_id": 2,
            "win_team_id": 2,
        },
        # Innings 2 terminal lost state (all out)
        {
            "match_id": 9999,
            "innings": 2,
            "overid": 18,
            "over_ball_num": 2,
            "balls_remaining_innings": 16,
            "cum_runs_innings": 120,
            "cum_wickets_innings": 10,
            "phase": "Death",
            "runs": 0,
            "is_bowler_wicket": True,
            "comp_weight": 1.0,
            "target_runs": 170,
            "runs_required": 50,
            "required_run_rate": 18.75,
            "venue_country": "India",
            "home_team_id": 1,
            "away_team_id": 2,
            "win_team_id": 1,
        },
    ]
    df_blowout = pd.DataFrame(blowout_rows)
    models = train_win_prob_models(df_blowout)
    result = compute_win_probability_and_leverage(df_blowout, models)

    # Innings 1 blowout must be bounded in [0.01, 0.99]
    inn1_prob = result.loc[result["innings"] == 1, "win_prob"].iloc[0]
    assert 0.01 <= inn1_prob <= 0.99

    # Innings 2 won state must have win_prob >= 0.95
    won_prob = result.loc[(result["innings"] == 2) & (result["runs_required"] == 0), "win_prob"].iloc[0]
    assert won_prob >= 0.95

    # Innings 2 all out state must have win_prob <= 0.05
    lost_prob = result.loc[(result["innings"] == 2) & (result["cum_wickets_innings"] >= 10), "win_prob"].iloc[0]
    assert lost_prob <= 0.05


def test_high_pressure_flag_and_li_scaling():
    rows = []
    # Match where chase comes down to wire: 12 off 6 balls
    for b in range(1, 121):
        if b <= 114:
            req = 170 - int(b * 1.3)
        else:
            req = 12 - (b - 114) * 2  # down to wire
        rows.append({
            "match_id": 2001,
            "innings": 2,
            "overid": (b - 1) // 6 + 1,
            "over_ball_num": (b - 1) % 6 + 1,
            "balls_remaining_innings": 120 - b,
            "cum_runs_innings": 170 - req,
            "cum_wickets_innings": 6,
            "phase": "Powerplay" if b <= 36 else ("Middle" if b <= 90 else "Death"),
            "runs": 2 if b > 114 else 1,
            "is_bowler_wicket": False,
            "comp_weight": 1.0,
            "target_runs": 170,
            "runs_required": max(0, req),
            "required_run_rate": (max(0, req) / max(1, 120 - b)) * 6,
            "venue_country": "India",
            "home_team_id": 1,
            "away_team_id": 2,
            "win_team_id": 2,
        })
    df_tight = pd.DataFrame(rows)
    models = train_win_prob_models(df_tight)
    res = compute_win_probability_and_leverage(df_tight, models)

    # Boolean high pressure flag must match leverage_index >= 1.50
    assert (res["is_high_pressure"] == (res["leverage_index"] >= 1.50)).all()

    # The final tense overs (balls 115-120) should have high leverage
    final_over_li = res.loc[res["balls_remaining_innings"] <= 5, "leverage_index"].mean()
    early_over_li = res.loc[res["balls_remaining_innings"] >= 90, "leverage_index"].mean()
    assert final_over_li > early_over_li


def test_delta_wpa_innings_start():
    rows = [
        {
            "match_id": 3001,
            "innings": 1,
            "overid": 1,
            "over_ball_num": 1,
            "balls_remaining_innings": 119,
            "cum_runs_innings": 4,
            "cum_wickets_innings": 0,
            "phase": "Powerplay",
            "runs": 4,
            "is_bowler_wicket": False,
            "comp_weight": 1.0,
            "target_runs": 0,
            "runs_required": 0,
            "required_run_rate": 0.0,
            "venue_country": "India",
            "home_team_id": 1,
            "away_team_id": 2,
            "win_team_id": 1,
        },
        {
            "match_id": 3001,
            "innings": 1,
            "overid": 1,
            "over_ball_num": 2,
            "balls_remaining_innings": 118,
            "cum_runs_innings": 4,
            "cum_wickets_innings": 1,
            "phase": "Powerplay",
            "runs": 0,
            "is_bowler_wicket": True,
            "comp_weight": 1.0,
            "target_runs": 0,
            "runs_required": 0,
            "required_run_rate": 0.0,
            "venue_country": "India",
            "home_team_id": 1,
            "away_team_id": 2,
            "win_team_id": 1,
        },
    ]
    df = pd.DataFrame(rows)
    models = train_win_prob_models(df)
    res = compute_win_probability_and_leverage(df, models)

    # First ball should not be NaN
    assert not res["delta_wpa"].isna().any()
    # Ball 1 was a boundary four (runs=4), ball 2 was a wicket (runs=0, wkt=1)
    # Wicket should cause delta_wpa to drop compared to ball 1
    assert res.loc[1, "delta_wpa"] < 0


def test_win_prob_on_real_data_sample():
    from src.data_loader import load_and_process_deliveries
    df = load_and_process_deliveries("/home/naveen/Data/Projects/RR Hackathon", sample_matches=5)
    assert not df.empty
    models = train_win_prob_models(df)
    res = compute_win_probability_and_leverage(df, models)

    assert "win_prob" in res.columns
    assert "delta_wpa" in res.columns
    assert "leverage_index" in res.columns
    assert "is_high_pressure" in res.columns
    assert not res["win_prob"].isna().any()
    assert not res["delta_wpa"].isna().any()
    assert not res["leverage_index"].isna().any()
    assert not res["is_high_pressure"].isna().any()
    assert ((res["win_prob"] >= 0.01) & (res["win_prob"] <= 0.99)).all()
    assert (res["leverage_index"] >= 0.0).all()



def test_chase_ball1_baseline_anchor_no_artificial_spike():
    # Verify that chasing an extreme target (215 runs) does not artificially spike Ball 1 LI
    rows = []
    for b in range(1, 13):
        rows.append({
            "match_id": 4001,
            "innings": 2,
            "overid": (b - 1) // 6 + 1,
            "over_ball_num": (b - 1) % 6 + 1,
            "balls_remaining_innings": 120 - b,
            "cum_runs_innings": b,
            "cum_wickets_innings": 0,
            "phase": "Powerplay",
            "runs": 1,
            "is_bowler_wicket": False,
            "comp_weight": 1.0,
            "target_runs": 215,
            "runs_required": 215 - b,
            "required_run_rate": ((215 - b) / (120 - b)) * 6.0,
            "venue_country": "India",
            "home_team_id": 1,
            "away_team_id": 2,
            "win_team_id": 1,
        })
    df = pd.DataFrame(rows)
    models = train_win_prob_models(df)
    res = compute_win_probability_and_leverage(df, models)

    # Ball 1 delta_wpa should be a small swing (not |0.02 - 0.50| = 0.48)
    ball1_delta = abs(res.loc[0, "delta_wpa"])
    assert ball1_delta < 0.10, f"Ball 1 delta_wpa={ball1_delta} is too large (artificial spike)"

    # Ball 1 LI should not explode (must be <= 3.0, not 15+)
    ball1_li = res.loc[0, "leverage_index"]
    assert ball1_li < 3.0, f"Ball 1 LI={ball1_li} exploded"


def test_over1_vs_over20_leverage_progression_real_data():
    from src.data_loader import load_and_process_deliveries
    df = load_and_process_deliveries("/home/naveen/Data/Projects/RR Hackathon", sample_matches=30)
    models = train_win_prob_models(df)
    res = compute_win_probability_and_leverage(df, models)

    inn2 = res[res["innings"] == 2]
    over1_li = inn2.loc[inn2["overid"] == 1, "leverage_index"].mean()
    over20_li = inn2.loc[inn2["overid"] == 20, "leverage_index"].mean()

    # Over 1 should be realistic (~0.7 to 1.3), and Over 20 should be significantly higher
    assert 0.7 <= over1_li <= 1.3, f"Over 1 LI={over1_li} is unrealistic"
    assert over20_li > over1_li, f"Over 20 LI={over20_li} should be higher than Over 1 LI={over1_li}"
