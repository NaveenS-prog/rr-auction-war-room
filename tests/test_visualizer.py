import os
import pytest
import pandas as pd
import numpy as np
from src.visualizer import generate_all_figures


def test_visualizer_generates_required_figures(tmp_path):
    """Canonical test from specification verifying all 5 required figures are created."""
    output_dir = tmp_path / "figures"
    # Create minimal mock dfs
    df_mock_balls = pd.DataFrame({
        "leverage_index": [0.5, 1.2, 1.8, 2.5, 3.2],
        "win_prob": [0.5, 0.55, 0.40, 0.70, 0.95],
        "balls_remaining_innings": [100, 80, 50, 20, 5]
    })
    mock_bat = pd.DataFrame([
        {"player_name": f"P{i}", "tsr_pressure": 20 - i, "tsr_overall": 10, "composite_score": 1.5 - i * 0.1}
        for i in range(10)
    ])
    mock_bowl = pd.DataFrame([
        {"player_name": f"B{i}", "ter_pressure": 2 - i * 0.1, "ter_overall": 1, "composite_score": 1.5 - i * 0.1}
        for i in range(10)
    ])

    fig_paths = generate_all_figures(df_mock_balls, mock_bat, mock_bowl, str(output_dir))
    assert isinstance(fig_paths, dict)
    assert len(fig_paths) == 5

    required_keys = [
        "fig1_win_prob_curves",
        "fig2_leverage_distribution",
        "fig3_batters_baseline_vs_pressure",
        "fig4_bowlers_baseline_vs_pressure",
        "fig5_top_players_radar",
    ]
    for key in required_keys:
        assert key in fig_paths
        path = fig_paths[key]
        assert os.path.exists(path)
        assert os.path.getsize(path) > 1000  # Non-trivial file size


def test_visualizer_creates_output_directory(tmp_path):
    """Verifies that non-existent nested output directories are created automatically."""
    output_dir = tmp_path / "nested" / "subfolder" / "figures"
    df_mock_balls = pd.DataFrame({
        "leverage_index": [1.0, 2.0],
        "win_prob": [0.5, 0.6],
        "balls_remaining_innings": [60, 30]
    })
    mock_bat = pd.DataFrame([
        {"player_name": f"Batter {i}", "tsr_pressure": 15 + i, "tsr_overall": 10, "composite_score": 1.0}
        for i in range(5)
    ])
    mock_bowl = pd.DataFrame([
        {"player_name": f"Bowler {i}", "ter_pressure": 1.5 + i, "ter_overall": 1.0, "composite_score": 1.0}
        for i in range(5)
    ])

    assert not output_dir.exists()
    fig_paths = generate_all_figures(df_mock_balls, mock_bat, mock_bowl, str(output_dir))
    assert output_dir.exists()
    for path in fig_paths.values():
        assert os.path.exists(path)


def test_visualizer_with_rich_columns_and_multiple_matches(tmp_path):
    """Verifies that rich metrics and match metadata are visualized cleanly."""
    output_dir = tmp_path / "rich_figures"

    # Multi-match ball data with overid, innings, and high pressure swings
    rows = []
    for match_id in [101, 102]:
        for b in range(1, 121):
            li = 0.5 + 2.5 * (b / 120.0) ** 2 if b > 80 else 0.8
            wp = 0.50 + 0.40 * np.sin(b / 20.0)
            rows.append({
                "match_id": match_id,
                "innings": 2,
                "overid": (b - 1) // 6 + 1,
                "over_ball_num": (b - 1) % 6 + 1,
                "balls_remaining_innings": 120 - b,
                "win_prob": np.clip(wp, 0.01, 0.99),
                "leverage_index": li,
            })
    df_balls = pd.DataFrame(rows)

    bat_data = []
    for i in range(10):
        bat_data.append({
            "player_id": 1000 + i,
            "player_name": f"Star Batter {i+1}",
            "rank": i + 1,
            "composite_score": 2.5 - i * 0.15,
            "raw_score": 2.7 - i * 0.18,
            "tsr_pressure": 28.0 - i * 1.2,
            "tsr_overall": 12.0 + i * 0.5,
            "wpa_per_100_pressure": 0.08 - i * 0.005,
            "dot_avoidance_pressure": 0.75 - i * 0.02,
            "n_eff_pressure": 120 - i * 3,
            "delta_score": 1.2 - i * 0.1,
        })
    df_batters = pd.DataFrame(bat_data)

    bowl_data = []
    for i in range(10):
        bowl_data.append({
            "player_id": 2000 + i,
            "player_name": f"Star Bowler {i+1}",
            "rank": i + 1,
            "composite_score": 2.4 - i * 0.14,
            "raw_score": 2.6 - i * 0.16,
            "ter_pressure": 2.2 - i * 0.1,
            "ter_overall": 0.9 + i * 0.05,
            "hl_wickets_pressure": 8 - i * 0.5,
            "dot_pct_pressure": 0.48 - i * 0.02,
            "n_eff_pressure": 115 - i * 3,
            "delta_score": 1.1 - i * 0.1,
        })
    df_bowlers = pd.DataFrame(bowl_data)

    fig_paths = generate_all_figures(df_balls, df_batters, df_bowlers, str(output_dir))
    for key, path in fig_paths.items():
        assert os.path.exists(path)
        assert os.path.getsize(path) > 5000  # Detailed figure has substantive byte size


def test_visualizer_handles_small_or_edge_case_inputs(tmp_path):
    """Verifies robustness with only 2 players and missing optional metrics."""
    output_dir = tmp_path / "edge_figures"
    df_balls = pd.DataFrame({
        "leverage_index": [1.5],
        "win_prob": [0.5],
    })
    mock_bat = pd.DataFrame([
        {"player_name": "Solo Batter", "tsr_pressure": 15.0}
    ])
    mock_bowl = pd.DataFrame([
        {"player_name": "Solo Bowler", "ter_pressure": 1.2}
    ])

    fig_paths = generate_all_figures(df_balls, mock_bat, mock_bowl, str(output_dir))
    assert len(fig_paths) == 5
    for path in fig_paths.values():
        assert os.path.exists(path)
