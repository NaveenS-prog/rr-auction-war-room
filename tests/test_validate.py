import pandas as pd
import pytest
from src.validate import run_data_validation, ValidationReport

def test_run_data_validation_catches_invalid_wickets():
    bad_df = pd.DataFrame([{
        "match_id": 1, "innings": 1, "delivery_id": 1, "legal_balls_bowled": 10,
        "legal_balls_remaining": 110, "runs_before": 10, "wickets_before": 11, # Invalid: > 10
        "target": None, "runs_required": None, "total_runs": 1, "is_legal_delivery": True,
        "striker_id": 10, "bowler_id": 20, "is_wicket": False, "scheduled_innings_balls": 120
    }])
    matches = pd.DataFrame([{"match_id": 1}])
    report = run_data_validation(bad_df, matches)
    assert not report.is_valid
    assert 1 in report.quarantined_matches
    assert "wickets_out_of_bounds" in report.error_summary

def test_run_data_validation_valid_match():
    valid_df = pd.DataFrame([
        {
            "match_id": 2, "innings": 1, "delivery_id": 1, "legal_balls_bowled": 0,
            "legal_balls_remaining": 120, "runs_before": 0, "wickets_before": 0,
            "target": None, "runs_required": None, "total_runs": 4, "is_legal_delivery": True,
            "striker_id": 10, "bowler_id": 20, "is_wicket": False, "scheduled_innings_balls": 120
        },
        {
            "match_id": 2, "innings": 1, "delivery_id": 2, "legal_balls_bowled": 1,
            "legal_balls_remaining": 119, "runs_before": 4, "wickets_before": 0,
            "target": None, "runs_required": None, "total_runs": 0, "is_legal_delivery": True,
            "striker_id": 10, "bowler_id": 20, "is_wicket": True, "scheduled_innings_balls": 120
        }
    ])
    matches = pd.DataFrame([{"match_id": 2}])
    report = run_data_validation(valid_df, matches)
    assert report.is_valid
    assert report.reconciled_match_count == 1
    assert len(report.quarantined_matches) == 0
