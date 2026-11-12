from pathlib import Path
import pandas as pd
import pytest
from src.report import generate_methodology_report

def test_generate_methodology_report(tmp_path):
    batters = pd.DataFrame([{
        "rank": 1, "player_id": 101, "player_name": "Test Batter", "team_name": "Team A",
        "conservative_score": 1.5, "pressure_ability_mean": 1.8, "normal_ability_mean": 0.5,
        "pressure_uplift_mean": 1.3, "prob_positive_uplift": 0.95,
        "total_balls": 150, "pressure_balls": 80, "pressure_matches": 15
    }])
    bowlers = pd.DataFrame([{
        "rank": 1, "player_id": 201, "player_name": "Test Bowler", "team_name": "Team B",
        "conservative_score": 1.2, "pressure_ability_mean": 1.5, "normal_ability_mean": 0.4,
        "pressure_uplift_mean": 1.1, "prob_positive_uplift": 0.90,
        "total_balls": 140, "pressure_balls": 75, "pressure_matches": 14
    }])
    
    report_file = generate_methodology_report(
        batters_df=batters,
        bowlers_df=bowlers,
        eval_metrics={"model_c_rmse": 0.42, "normal_baseline_rmse": 0.65, "correlation": 0.78},
        sensitivity_metrics={"quantile_stability": {"Q_0.05": 0.90, "Q_0.10": 1.0, "Q_0.20": 0.90}},
        output_dir=tmp_path
    )
    
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Test Batter" in content
    assert "Test Bowler" in content
    assert "Pressure Definition" in content
    assert "Reliability and Limitations" in content
    assert (tmp_path / "top10_batters.csv").exists()
    assert (tmp_path / "top10_bowlers.csv").exists()
