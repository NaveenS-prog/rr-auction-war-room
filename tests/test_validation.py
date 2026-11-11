"""Tests for Unstop Schema Validation and Bootstrap Sensitivity Analysis.

Verifies:
1. Unstop submission format compliance:
   - Exactly 10 batters and 10 bowlers (or subset in partial tests).
   - Zero duplicate player IDs within rankings.
   - All player IDs exist in official competition_team_player_mapping.csv.
   - Dropdown selections format structure.
2. Bootstrap sensitivity analysis:
   - Match-level resampling with replacement across n iterations.
   - 95% bootstrap confidence intervals for rank and composite score.
   - Graceful fallback for mock and small match inputs.
"""

from __future__ import annotations

import os
import pytest
import pandas as pd
import numpy as np

from src.validation import validate_unstop_compliance, compute_bootstrap_sensitivity

DATA_DIR = "/mnt/data/Projects/RR Hackathon"


def test_unstop_compliance_verification():
    """Canonical test from specification: single mock batter and bowler verification."""
    mock_bat = pd.DataFrame([{"player_id": 1187, "player_name": "Jason Roy", "rank": 1}])
    mock_bowl = pd.DataFrame([{"player_id": 1772, "player_name": "Sheldon Cottrell", "rank": 1}])
    report = validate_unstop_compliance(mock_bat, mock_bowl, DATA_DIR)
    assert report["valid"] is True
    assert report["batter_duplicates"] == 0
    assert report["bowler_duplicates"] == 0
    assert len(report["missing_ids"]) == 0
    assert "dropdown_selections" in report
    assert 1 in report["dropdown_selections"]["batters"]
    assert report["dropdown_selections"]["batters"][1]["id"] == 1187
    assert report["dropdown_selections"]["batters"][1]["name"] == "Jason Roy"


def test_unstop_compliance_duplicate_detection():
    """Verify duplicate player IDs within rankings are caught."""
    # 2 batters with the same player_id
    mock_bat = pd.DataFrame([
        {"player_id": 1187, "player_name": "Jason Roy", "rank": 1},
        {"player_id": 1187, "player_name": "Jason Roy", "rank": 2},
    ])
    mock_bowl = pd.DataFrame([
        {"player_id": 1772, "player_name": "Sheldon Cottrell", "rank": 1},
        {"player_id": 786, "player_name": "Chris Jordan", "rank": 2},
    ])
    report = validate_unstop_compliance(mock_bat, mock_bowl, DATA_DIR)
    assert report["valid"] is False
    assert report["batter_duplicates"] == 1
    assert report["bowler_duplicates"] == 0


def test_unstop_compliance_missing_id_detection():
    """Verify non-existent player IDs are caught against mapping."""
    mock_bat = pd.DataFrame([{"player_id": 99999999, "player_name": "Ghost Batter", "rank": 1}])
    mock_bowl = pd.DataFrame([{"player_id": 1772, "player_name": "Sheldon Cottrell", "rank": 1}])
    report = validate_unstop_compliance(mock_bat, mock_bowl, DATA_DIR)
    assert report["valid"] is False
    assert 99999999 in report["missing_ids"]
    assert 99999999 in report["missing_batter_ids"]


def test_unstop_compliance_dropdown_formatting():
    """Verify dropdown dictionary structure matches {discipline: {rank: {id, name}}}."""
    mock_bat = pd.DataFrame([
        {"player_id": 1187, "player_name": "J Roy", "rank": 1},
        {"player_id": 1596, "player_name": "M Ali", "rank": 2},
    ])
    mock_bowl = pd.DataFrame([
        {"player_id": 1772, "player_name": "S Cottrell", "rank": 1},
        {"player_id": 786, "player_name": "C Jordan", "rank": 2},
    ])
    report = validate_unstop_compliance(mock_bat, mock_bowl, DATA_DIR)
    assert report["valid"] is True
    dropdown = report["dropdown_selections"]
    assert "batters" in dropdown and "bowlers" in dropdown
    # Canonical name resolution from mapping: 1596 is Moeen Ali, 786 is Chris Jordan
    assert dropdown["batters"][2]["name"] == "Moeen Ali"
    assert dropdown["bowlers"][2]["name"] == "Chris Jordan"


def test_unstop_compliance_strict_ten():
    """Verify strict_ten enforces exactly 10 batters and 10 bowlers."""
    # 2 players each
    mock_bat = pd.DataFrame([
        {"player_id": 1187, "player_name": "Jason Roy", "rank": 1},
        {"player_id": 1596, "player_name": "Moeen Ali", "rank": 2},
    ])
    mock_bowl = pd.DataFrame([
        {"player_id": 1772, "player_name": "Sheldon Cottrell", "rank": 1},
        {"player_id": 786, "player_name": "Chris Jordan", "rank": 2},
    ])
    # Permissive mode (default): valid because <= 10 and no errors
    report_permissive = validate_unstop_compliance(mock_bat, mock_bowl, DATA_DIR, strict_ten=False)
    assert report_permissive["valid"] is True
    assert report_permissive["has_exact_ten"] is False

    # Strict mode: invalid because count is not 10
    report_strict = validate_unstop_compliance(mock_bat, mock_bowl, DATA_DIR, strict_ten=True)
    assert report_strict["valid"] is False


def test_bootstrap_sensitivity_fallback_on_mock():
    """Verify graceful fallback when match data is sparse or mock."""
    empty_balls = pd.DataFrame()
    mock_bat = pd.DataFrame([
        {"player_id": 1187, "player_name": "Jason Roy", "rank": 1, "composite_score": 2.25},
        {"player_id": 1596, "player_name": "Moeen Ali", "rank": 2, "composite_score": 1.80},
    ])
    mock_bowl = pd.DataFrame([
        {"player_id": 1772, "player_name": "Sheldon Cottrell", "rank": 1, "composite_score": 2.10},
        {"player_id": 786, "player_name": "Chris Jordan", "rank": 2, "composite_score": 1.65},
    ])

    result = compute_bootstrap_sensitivity(empty_balls, mock_bat, mock_bowl, n_iterations=100)
    assert result["fallback"] is True
    assert "batters" in result
    assert "bowlers" in result

    # Check batter CI structure
    p1 = result["batters"][1187]
    assert "rank_ci_95" in p1
    assert "score_ci_95" in p1
    assert isinstance(p1["rank_ci_95"], tuple)
    assert isinstance(p1["score_ci_95"], tuple)
    assert p1["rank_ci_95"][0] <= p1["rank_ci_95"][1]
    assert p1["score_ci_95"][0] <= p1["score_ci_95"][1]


def test_bootstrap_sensitivity_with_matches():
    """Verify bootstrap sensitivity on actual match sample produces valid CIs."""
    from src.data_loader import load_and_process_deliveries
    from src.win_prob import train_win_prob_models, compute_win_probability_and_leverage
    from src.metrics import compute_phase_par_rates, calculate_player_raw_metrics
    from src.rankings import compute_rankings

    # Load 10 matches for rapid testing
    df_deliveries = load_and_process_deliveries(DATA_DIR, sample_matches=10)
    models = train_win_prob_models(df_deliveries)
    df_state = compute_win_probability_and_leverage(df_deliveries, models)
    pars = compute_phase_par_rates(df_state)
    df_batters, df_bowlers = calculate_player_raw_metrics(df_state, pars)
    top_bat, top_bowl = compute_rankings(df_batters, df_bowlers, min_pressure_balls=5, top_n=5)

    assert not top_bat.empty
    assert not top_bowl.empty

    # Run 30 iterations for fast test
    result = compute_bootstrap_sensitivity(
        df_state, top_bat, top_bowl, n_iterations=30, min_pressure_balls=3, random_state=42
    )

    assert result["fallback"] is False
    assert result["n_iterations"] == 30

    for pid in top_bat["player_id"]:
        bat_res = result["batters"][pid]
        assert "rank_ci_95" in bat_res
        assert "score_ci_95" in bat_res
        low_r, high_r = bat_res["rank_ci_95"]
        assert low_r >= 1
        assert low_r <= high_r
        low_s, high_s = bat_res["score_ci_95"]
        assert low_s <= high_s

    for pid in top_bowl["player_id"]:
        bowl_res = result["bowlers"][pid]
        assert "rank_ci_95" in bowl_res
        assert "score_ci_95" in bowl_res
        low_r, high_r = bowl_res["rank_ci_95"]
        assert low_r >= 1
        assert low_r <= high_r


def test_end_to_end_validation_and_sensitivity():
    """Verify integrated flow: rankings generation -> Unstop schema check -> sensitivity report."""
    from src.data_loader import load_and_process_deliveries
    from src.win_prob import train_win_prob_models, compute_win_probability_and_leverage
    from src.metrics import compute_phase_par_rates, calculate_player_raw_metrics
    from src.rankings import compute_rankings

    df_deliveries = load_and_process_deliveries(DATA_DIR, sample_matches=12)
    models = train_win_prob_models(df_deliveries)
    df_state = compute_win_probability_and_leverage(df_deliveries, models)
    pars = compute_phase_par_rates(df_state)
    df_batters, df_bowlers = calculate_player_raw_metrics(df_state, pars)
    top_bat, top_bowl = compute_rankings(df_batters, df_bowlers, min_pressure_balls=5, top_n=10)

    # 1. Unstop validation
    report = validate_unstop_compliance(top_bat, top_bowl, DATA_DIR)
    assert report["batter_duplicates"] == 0
    assert report["bowler_duplicates"] == 0
    assert len(report["missing_ids"]) == 0
    assert report["valid"] is True

    # 2. Sensitivity analysis
    sensitivity = compute_bootstrap_sensitivity(
        df_state, top_bat, top_bowl, n_iterations=20, min_pressure_balls=3, random_state=42
    )
    assert "batters" in sensitivity
    assert "bowlers" in sensitivity
    assert len(sensitivity["batters_list"]) == len(top_bat)
    assert len(sensitivity["bowlers_list"]) == len(top_bowl)
