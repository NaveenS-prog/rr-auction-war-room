import pytest
import pandas as pd
import numpy as np

from src.rankings import compute_rankings, compute_batting_rankings, compute_bowling_rankings


def test_rankings_dual_axis_and_shrinkage():
    """Canonical test from specification verifying dual-axis scoring, shrinkage, and top 10 ranking."""
    # Generate mock batter and bowler records
    bat_data = []
    for i in range(1, 25):
        bat_data.append({
            "player_id": 100 + i,
            "player_name": f"Batter {i}",
            "n_eff_pressure": 85 if i <= 15 else 30,  # Some below threshold
            "tsr_pressure": 15.0 + i,
            "tsr_overall": 10.0 + (i * 0.5),
            "wpa_per_100_pressure": 0.04 + (i * 0.005),
            "wpa_per_100_overall": 0.02,
            "dot_avoidance_pressure": 0.65 + (i * 0.01),
            "dot_avoidance_overall": 0.60,
            "primary_batting_pos": 4,
        })
    bowl_data = []
    for i in range(1, 25):
        bowl_data.append({
            "player_id": 200 + i,
            "player_name": f"Bowler {i}",
            "n_eff_pressure": 90 if i <= 15 else 20,
            "ter_pressure": 1.2 + (i * 0.1),
            "ter_overall": 0.8 + (i * 0.05),
            "hl_wickets_pressure": 5 + i,
            "hl_wickets_overall": 10,
            "dot_pct_pressure": 0.40 + (i * 0.01),
            "dot_pct_overall": 0.35,
            "avg_overs_per_match": 3.5,
        })
    df_top_bat, df_top_bowl = compute_rankings(
        pd.DataFrame(bat_data),
        pd.DataFrame(bowl_data),
        min_pressure_balls=75,
    )

    assert len(df_top_bat) == 10
    assert len(df_top_bowl) == 10
    # Ensure rank order is descending by final regressed score
    assert df_top_bat["composite_score"].is_monotonic_decreasing
    assert df_top_bowl["composite_score"].is_monotonic_decreasing
    # Ensure all qualifiers have at least 75 pressure balls
    assert (df_top_bat["n_eff_pressure"] >= 75).all()
    assert (df_top_bowl["n_eff_pressure"] >= 75).all()
    # Ensure ranks are 1 to 10
    assert list(df_top_bat["rank"]) == list(range(1, 11))
    assert list(df_top_bowl["rank"]) == list(range(1, 11))


def test_eligibility_role_filtering():
    """Verify role-based filtering: tailenders and part-time bowlers must be excluded."""
    bat_data = [
        # Qualified batter (pos 3, n_eff 100)
        {
            "player_id": 1, "player_name": "Top Order Bat",
            "n_eff_pressure": 100, "tsr_pressure": 25.0, "tsr_overall": 10.0,
            "wpa_per_100_pressure": 0.10, "dot_avoidance_pressure": 0.70,
            "primary_batting_pos": 3, "top7_appearance_pct": 1.0,
        },
        # Tailender (pos 9, top7_pct 0.1, n_eff 100) - should be filtered out
        {
            "player_id": 2, "player_name": "Tailender Slogger",
            "n_eff_pressure": 100, "tsr_pressure": 40.0, "tsr_overall": 5.0,
            "wpa_per_100_pressure": 0.15, "dot_avoidance_pressure": 0.75,
            "primary_batting_pos": 9, "top7_appearance_pct": 0.10,
        },
        # Low pressure balls batter (pos 4, n_eff 40) - should be filtered out
        {
            "player_id": 3, "player_name": "Low Volume Bat",
            "n_eff_pressure": 40, "tsr_pressure": 30.0, "tsr_overall": 10.0,
            "wpa_per_100_pressure": 0.12, "dot_avoidance_pressure": 0.72,
            "primary_batting_pos": 4, "top7_appearance_pct": 0.90,
        },
    ]

    bowl_data = [
        # Regular bowler (3.5 overs/match, n_eff 100)
        {
            "player_id": 10, "player_name": "Frontline Bowler",
            "n_eff_pressure": 100, "ter_pressure": 2.5, "ter_overall": 1.0,
            "hl_wickets_pressure": 15, "dot_pct_pressure": 0.50,
            "avg_overs_per_match": 3.8,
        },
        # Part-time bowler (0.8 overs/match, n_eff 100) - should be filtered out
        {
            "player_id": 11, "player_name": "Part-timer Lucky",
            "n_eff_pressure": 100, "ter_pressure": 4.0, "ter_overall": 0.5,
            "hl_wickets_pressure": 12, "dot_pct_pressure": 0.55,
            "avg_overs_per_match": 0.8,
        },
        # Low volume bowler (3.0 overs/match, n_eff 30) - should be filtered out
        {
            "player_id": 12, "player_name": "Low Volume Bowler",
            "n_eff_pressure": 30, "ter_pressure": 3.0, "ter_overall": 1.0,
            "hl_wickets_pressure": 10, "dot_pct_pressure": 0.45,
            "avg_overs_per_match": 3.0,
        },
    ]

    df_bat, df_bowl = compute_rankings(
        pd.DataFrame(bat_data),
        pd.DataFrame(bowl_data),
        min_pressure_balls=75,
    )

    # Only player 1 and player 10 should qualify
    assert len(df_bat) == 1
    assert df_bat.iloc[0]["player_id"] == 1
    assert df_bat.iloc[0]["rank"] == 1

    assert len(df_bowl) == 1
    assert df_bowl.iloc[0]["player_id"] == 10
    assert df_bowl.iloc[0]["rank"] == 1


def test_empirical_bayes_shrinkage_effect():
    """Verify that Empirical Bayes shrinkage pulls smaller sample sizes toward population mean."""
    # Two players with identical raw metrics, but Player A has 200 balls and Player B has 80 balls.
    # Player A's score should shrink less toward the mean than Player B's.
    bat_data = [
        # High volume standout
        {
            "player_id": 1, "player_name": "Veteran Finisher",
            "n_eff_pressure": 200, "tsr_pressure": 30.0, "tsr_overall": 10.0,
            "wpa_per_100_pressure": 0.15, "dot_avoidance_pressure": 0.75,
            "primary_batting_pos": 5, "top7_appearance_pct": 1.0,
        },
        # Lower volume standout with identical raw rates
        {
            "player_id": 2, "player_name": "Emerging Finisher",
            "n_eff_pressure": 80, "tsr_pressure": 30.0, "tsr_overall": 10.0,
            "wpa_per_100_pressure": 0.15, "dot_avoidance_pressure": 0.75,
            "primary_batting_pos": 5, "top7_appearance_pct": 1.0,
        },
        # Average reference player
        {
            "player_id": 3, "player_name": "Average Batter",
            "n_eff_pressure": 100, "tsr_pressure": 10.0, "tsr_overall": 10.0,
            "wpa_per_100_pressure": 0.02, "dot_avoidance_pressure": 0.55,
            "primary_batting_pos": 4, "top7_appearance_pct": 1.0,
        },
        # Below average reference player
        {
            "player_id": 4, "player_name": "Struggling Batter",
            "n_eff_pressure": 100, "tsr_pressure": -10.0, "tsr_overall": 5.0,
            "wpa_per_100_pressure": -0.05, "dot_avoidance_pressure": 0.40,
            "primary_batting_pos": 4, "top7_appearance_pct": 1.0,
        },
    ]

    df_bat = compute_batting_rankings(pd.DataFrame(bat_data), min_pressure_balls=75, prior_m=30.0)

    p1 = df_bat[df_bat["player_id"] == 1].iloc[0]
    p2 = df_bat[df_bat["player_id"] == 2].iloc[0]

    # Both have the same raw_score
    assert p1["raw_score"] == pytest.approx(p2["raw_score"])
    # Player 1 has higher n_eff (200 vs 80), so shrinkage weight (200/230 > 80/110)
    # Since raw_score > mu_0 (above average), Player 1 retains more of the high score!
    assert p1["composite_score"] > p2["composite_score"]
    assert p1["rank"] == 1
    assert p2["rank"] == 2


def test_empty_and_minimal_rankings():
    """Verify graceful handling of empty inputs and small pools."""
    df_empty = pd.DataFrame()
    top_bat, top_bowl = compute_rankings(df_empty, df_empty)
    assert top_bat.empty
    assert top_bowl.empty
    assert "composite_score" in top_bat.columns
    assert "rank" in top_bat.columns
    assert "composite_score" in top_bowl.columns
    assert "rank" in top_bowl.columns

    # Fewer than 10 players
    small_bat = pd.DataFrame([
        {
            "player_id": 1, "player_name": "Solo Bat",
            "n_eff_pressure": 100, "tsr_pressure": 15.0, "tsr_overall": 10.0,
            "wpa_per_100_pressure": 0.05, "dot_avoidance_pressure": 0.60,
            "primary_batting_pos": 3,
        }
    ])
    small_bowl = pd.DataFrame([
        {
            "player_id": 2, "player_name": "Solo Bowl",
            "n_eff_pressure": 100, "ter_pressure": 1.5, "ter_overall": 1.0,
            "hl_wickets_pressure": 8, "dot_pct_pressure": 0.45,
            "avg_overs_per_match": 4.0,
        }
    ])
    top_bat, top_bowl = compute_rankings(small_bat, small_bowl, min_pressure_balls=75)
    assert len(top_bat) == 1
    assert top_bat.iloc[0]["rank"] == 1
    assert len(top_bowl) == 1
    assert top_bowl.iloc[0]["rank"] == 1


def test_end_to_end_pipeline_ranking():
    """Verify end-to-end flow from loaded match sample to final Top 10 rankings."""
    from src.data_loader import load_and_process_deliveries
    from src.win_prob import train_win_prob_models, compute_win_probability_and_leverage
    from src.metrics import compute_phase_par_rates, calculate_player_raw_metrics

    # Load 15 matches for quick end-to-end verification
    df_deliveries = load_and_process_deliveries("/mnt/data/Projects/RR Hackathon", sample_matches=15)
    models = train_win_prob_models(df_deliveries)
    df_state = compute_win_probability_and_leverage(df_deliveries, models)
    pars = compute_phase_par_rates(df_state)
    df_batters, df_bowlers = calculate_player_raw_metrics(df_state, pars)

    # Use a lower threshold (e.g. 10 balls) because sample_matches=15 is a small slice
    top_bat, top_bowl = compute_rankings(df_batters, df_bowlers, min_pressure_balls=10, top_n=5)

    assert not top_bat.empty
    assert not top_bowl.empty
    assert len(top_bat) <= 5
    assert len(top_bowl) <= 5
    assert top_bat["composite_score"].is_monotonic_decreasing
    assert top_bowl["composite_score"].is_monotonic_decreasing
    assert "rank" in top_bat.columns
    assert "player_name" in top_bat.columns
    assert "player_id" in top_bat.columns
    assert list(top_bat["rank"]) == list(range(1, len(top_bat) + 1))


def test_audit_specialist_batter_and_no_inverted_delta_penalty():
    """Verify Ponytail audit fixes:
    1. Low-volume pinch-floaters (e.g. Ashwin with <350 overall balls) are filtered.
    2. Elite overall batters (+30 TSR overall, +40 TSR pressure) outrank mediocre batters.
    3. 60-ball threshold qualifies high-impact finishers (e.g. Klaasen with 70 balls).
    """
    bat_data = [
        # Elite Destructive Finisher (e.g. Heinrich Klaasen): 70 pressure balls, TSR_press=55, TSR_over=25, n_balls_overall=1400
        {
            "player_id": 101,
            "player_name": "Elite Finisher",
            "n_eff_pressure": 70.0,
            "n_balls_overall": 1400,
            "tsr_pressure": 55.0,
            "tsr_overall": 25.0,
            "wpa_per_100_pressure": 0.50,
            "dot_avoidance_pressure": 0.75,
            "primary_batting_pos": 5,
            "top7_appearance_pct": 1.0,
        },
        # Elite Overall Batter (e.g. Tim David / Surya): 150 pressure balls, TSR_press=42, TSR_over=32, n_balls_overall=800
        {
            "player_id": 102,
            "player_name": "Elite All-Round Batter",
            "n_eff_pressure": 150.0,
            "n_balls_overall": 800,
            "tsr_pressure": 42.0,
            "tsr_overall": 32.0,
            "wpa_per_100_pressure": 0.60,
            "dot_avoidance_pressure": 0.72,
            "primary_batting_pos": 4,
            "top7_appearance_pct": 1.0,
        },
        # Bowler / Pinch Floater (e.g. Ashwin): 80 pressure balls, TSR_press=15, TSR_over=-10, n_balls_overall=300 (<350)
        {
            "player_id": 103,
            "player_name": "Pinch Floater Bowler",
            "n_eff_pressure": 80.0,
            "n_balls_overall": 300,  # Below 350 volume threshold
            "tsr_pressure": 15.0,
            "tsr_overall": -10.0,
            "wpa_per_100_pressure": -0.10,
            "dot_avoidance_pressure": 0.60,
            "primary_batting_pos": 5,
            "top7_appearance_pct": 0.75,
        },
    ]

    bowl_data = [
        # Frontline Bowler
        {
            "player_id": 201,
            "player_name": "Frontline Bowler",
            "n_eff_pressure": 120.0,
            "ter_pressure": 2.0,
            "ter_overall": 0.5,
            "hl_wickets_pressure": 25.0,
            "dot_pct_pressure": 0.45,
            "avg_overs_per_match": 3.8,
        }
    ]

    top_bat, top_bowl = compute_rankings(
        pd.DataFrame(bat_data),
        pd.DataFrame(bowl_data),
        min_pressure_balls=60,
        min_overall_balls=350,
    )

    # Pinch floater bowler with 300 overall balls must be excluded
    assert "Pinch Floater Bowler" not in top_bat["player_name"].values
    # Elite finisher (70 balls >= 60 threshold) must be included
    assert "Elite Finisher" in top_bat["player_name"].values
    assert "Elite All-Round Batter" in top_bat["player_name"].values
    # Both elite batters must rank above any tailender
    assert len(top_bat) == 2


