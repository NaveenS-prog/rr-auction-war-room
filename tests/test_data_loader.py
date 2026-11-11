import pytest
import pandas as pd
from src.data_loader import load_and_process_deliveries

def test_data_loader_reconstructs_match_state():
    df = load_and_process_deliveries("/home/naveen/Data/Projects/RR Hackathon", sample_matches=5)
    assert not df.empty
    expected_cols = [
        "match_id", "innings", "overid", "over_ball_num", "striker_id", "bowler_id",
        "cum_runs_innings", "cum_wickets_innings", "balls_remaining_innings", "phase",
        "bowler_runs_conceded", "is_bowler_wicket", "comp_weight"
    ]
    for col in expected_cols:
        assert col in df.columns
    # Check that Powerplay is overs 1-6
    pp_balls = df[df["phase"] == "Powerplay"]
    assert (pp_balls["overid"] <= 6).all()
    # Check that bowler conceded runs ignores leg-byes
    lb_deliveries = df[df["extras_type"] == "Leg-byes"]
    if not lb_deliveries.empty:
        assert (lb_deliveries["bowler_runs_conceded"] == 0).all()

def test_data_loader_chase_metrics():
    df = load_and_process_deliveries("/home/naveen/Data/Projects/RR Hackathon", sample_matches=5)
    inn2 = df[df["innings"] == 2]
    assert not inn2.empty
    assert "target_runs" in inn2.columns
    assert "runs_required" in inn2.columns
    assert "required_run_rate" in inn2.columns
    assert "current_run_rate" in inn2.columns
    assert (inn2["target_runs"] > 0).all()
    assert (inn2["runs_required"] >= 0).all()
    assert (inn2["required_run_rate"] >= 0.0).all()

def test_data_loader_bowler_wickets_excludes_runouts():
    df = load_and_process_deliveries("/home/naveen/Data/Projects/RR Hackathon", sample_matches=20)
    runouts = df[df["dismissal_type"].astype(str).str.lower() == "runout"]
    if not runouts.empty:
        assert (~runouts["is_bowler_wicket"]).all()
    caught = df[df["dismissal_type"].astype(str).str.lower() == "caught"]
    if not caught.empty:
        assert (caught["is_bowler_wicket"]).all()

def test_data_loader_competition_weights():
    df = load_and_process_deliveries("/home/naveen/Data/Projects/RR Hackathon", sample_matches=50)
    assert "comp_weight" in df.columns
    assert (df["comp_weight"] >= 0.70).all()
    assert (df["comp_weight"] <= 1.00).all()

def test_data_loader_dls_revised_target():
    # Match 21586 is IPL 2023 final with 90 balls and revised target 171
    df = load_and_process_deliveries("/home/naveen/Data/Projects/RR Hackathon", sample_matches=265)
    m21586 = df[df["match_id"] == 21586]
    assert not m21586.empty
    inn2 = m21586[m21586["innings"] == 2]
    assert not inn2.empty
    assert (inn2["target_runs"] == 171).all()
    assert (inn2["balls_remaining_innings"] <= 90).all()

