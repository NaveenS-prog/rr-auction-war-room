import pytest
import pandas as pd
import numpy as np

from src.metrics import compute_phase_par_rates, calculate_player_raw_metrics


def test_metrics_computation():
    """Verify metrics computation against the canonical brief mock scenario."""
    df_mock = pd.DataFrame([
        {
            "match_id": 1, "innings": 1, "overid": 18, "phase": "Death",
            "striker_id": 101, "striker_name": "Test Batter", "batting_order": 5,
            "bowler_id": 201, "bowler_name": "Test Bowler",
            "runs": 4, "bowler_runs_conceded": 4, "is_bowler_wicket": False,
            "is_dot": False, "delta_wpa": 0.05, "leverage_index": 2.1,
            "is_high_pressure": True, "comp_weight": 1.0
        },
        {
            "match_id": 1, "innings": 1, "overid": 18, "phase": "Death",
            "striker_id": 101, "striker_name": "Test Batter", "batting_order": 5,
            "bowler_id": 201, "bowler_name": "Test Bowler",
            "runs": 0, "bowler_runs_conceded": 0, "is_bowler_wicket": True,
            "is_dot": True, "delta_wpa": -0.12, "leverage_index": 2.5,
            "is_high_pressure": True, "comp_weight": 1.0
        }
    ])
    phase_pars = compute_phase_par_rates(df_mock)
    assert "Death" in phase_pars
    df_batters, df_bowlers = calculate_player_raw_metrics(df_mock, phase_pars)
    assert not df_batters.empty
    assert not df_bowlers.empty
    assert "tsr_pressure" in df_batters.columns
    assert "ter_pressure" in df_bowlers.columns


def test_phase_par_rates_comprehensive():
    """Verify phase par computation across Powerplay, Middle, and Death."""
    rows = [
        # Powerplay (overs 1-6): 2 balls, runs: 1, 4 (1 dot, 1 boundary)
        {"match_id": 1, "overid": 2, "phase": "Powerplay", "runs": 1, "bowler_runs_conceded": 1, "is_dot": False, "is_four": False, "is_six": False},
        {"match_id": 1, "overid": 4, "phase": "Powerplay", "runs": 4, "bowler_runs_conceded": 4, "is_dot": False, "is_four": True, "is_six": False},
        # Middle (overs 7-15): 2 balls, runs: 0, 1 (1 dot, 0 boundary)
        {"match_id": 1, "overid": 8, "phase": "Middle", "runs": 0, "bowler_runs_conceded": 0, "is_dot": True, "is_four": False, "is_six": False},
        {"match_id": 1, "overid": 12, "phase": "Middle", "runs": 1, "bowler_runs_conceded": 1, "is_dot": False, "is_four": False, "is_six": False},
        # Death (overs 16-20): 2 balls, runs: 6, 0 (1 dot, 1 boundary)
        {"match_id": 1, "overid": 18, "phase": "Death", "runs": 6, "bowler_runs_conceded": 6, "is_dot": False, "is_four": False, "is_six": True},
        {"match_id": 1, "overid": 20, "phase": "Death", "runs": 0, "bowler_runs_conceded": 0, "is_dot": True, "is_four": False, "is_six": False},
    ]
    df = pd.DataFrame(rows)
    pars = compute_phase_par_rates(df)

    # Powerplay: 5 runs in 2 balls -> 2.5 runs/ball, par_sr=250, par_er=15.0, dot_pct=0.0, boundary_pct=0.5
    assert pars["Powerplay"]["runs_per_ball"] == pytest.approx(2.5)
    assert pars["Powerplay"]["par_sr"] == pytest.approx(250.0)
    assert pars["Powerplay"]["par_er"] == pytest.approx(15.0)
    assert pars["Powerplay"]["boundary_pct"] == pytest.approx(0.5)

    # Middle: 1 run in 2 balls -> 0.5 runs/ball, par_sr=50, par_er=3.0, dot_pct=0.5, boundary_pct=0.0
    assert pars["Middle"]["runs_per_ball"] == pytest.approx(0.5)
    assert pars["Middle"]["par_sr"] == pytest.approx(50.0)
    assert pars["Middle"]["par_er"] == pytest.approx(3.0)
    assert pars["Middle"]["dot_pct"] == pytest.approx(0.5)
    assert pars["Middle"]["boundary_pct"] == pytest.approx(0.0)

    # Death: 6 runs in 2 balls -> 3.0 runs/ball, par_sr=300, par_er=18.0, dot_pct=0.5, boundary_pct=0.5
    assert pars["Death"]["runs_per_ball"] == pytest.approx(3.0)
    assert pars["Death"]["par_sr"] == pytest.approx(300.0)
    assert pars["Death"]["par_er"] == pytest.approx(18.0)
    assert pars["Death"]["dot_pct"] == pytest.approx(0.5)
    assert pars["Death"]["boundary_pct"] == pytest.approx(0.5)


def test_detailed_batter_and_bowler_metrics():
    """Verify exact TSR, TER, WPA/100, HL wickets, and pressure partition logic."""
    phase_pars = {
        "Powerplay": {"runs_per_ball": 1.20, "par_sr": 120.0, "par_er": 7.20, "dot_pct": 0.40, "boundary_pct": 0.15},
        "Middle": {"runs_per_ball": 1.30, "par_sr": 130.0, "par_er": 7.80, "dot_pct": 0.35, "boundary_pct": 0.12},
        "Death": {"runs_per_ball": 1.80, "par_sr": 180.0, "par_er": 10.80, "dot_pct": 0.25, "boundary_pct": 0.25},
    }

    # Batter 101:
    # Ball 1: Low pressure (LI 1.0, W_comp 0.9), Middle, runs 1, delta_wpa 0.01, is_dot False
    # Ball 2: High pressure (LI 2.0, W_comp 0.9), Death, runs 4, delta_wpa 0.06, is_dot False
    # Ball 3: High pressure (LI 2.5, W_comp 0.9), Death, runs 0, delta_wpa -0.04, is_dot True
    # Bowler 201 bowls all 3 balls:
    # Ball 1: conceded 1, is_bowler_wicket False, is_dot False
    # Ball 2: conceded 4, is_bowler_wicket False, is_dot False
    # Ball 3: conceded 0, is_bowler_wicket True, is_dot True
    rows = [
        {
            "match_id": 10, "innings": 2, "overid": 10, "phase": "Middle",
            "striker_id": 101, "striker_name": "Clutch Batter", "batting_order": 3,
            "bowler_id": 201, "bowler_name": "Ace Bowler",
            "runs": 1, "bowler_runs_conceded": 1, "is_bowler_wicket": False,
            "is_dot": False, "delta_wpa": 0.01, "leverage_index": 1.0,
            "is_high_pressure": False, "comp_weight": 0.90
        },
        {
            "match_id": 10, "innings": 2, "overid": 18, "phase": "Death",
            "striker_id": 101, "striker_name": "Clutch Batter", "batting_order": 3,
            "bowler_id": 201, "bowler_name": "Ace Bowler",
            "runs": 4, "bowler_runs_conceded": 4, "is_bowler_wicket": False,
            "is_dot": False, "delta_wpa": 0.06, "leverage_index": 2.0,
            "is_high_pressure": True, "comp_weight": 0.90
        },
        {
            "match_id": 10, "innings": 2, "overid": 18, "phase": "Death",
            "striker_id": 101, "striker_name": "Clutch Batter", "batting_order": 3,
            "bowler_id": 201, "bowler_name": "Ace Bowler",
            "runs": 0, "bowler_runs_conceded": 0, "is_bowler_wicket": True,
            "is_dot": True, "delta_wpa": -0.04, "leverage_index": 2.5,
            "is_high_pressure": True, "comp_weight": 0.90
        },
    ]
    df = pd.DataFrame(rows)
    df_batters, df_bowlers = calculate_player_raw_metrics(df, phase_pars)

    # Batter assertions:
    bat = df_batters[df_batters["player_id"] == 101].iloc[0]
    assert bat["n_balls_overall"] == 3
    assert bat["n_eff_overall"] == pytest.approx(2.7)
    assert bat["n_balls_pressure"] == 2
    assert bat["n_eff_pressure"] == pytest.approx(1.8)

    # Actual SR overall = (5 / 3) * 100 = 166.666...
    # Expected runs overall = 1*1.30 (Middle) + 2*1.80 (Death) = 4.90
    # Expected SR overall = (4.90 / 3) * 100 = 163.333...
    # TSR overall = 166.666... - 163.333... = 3.333...
    assert bat["tsr_overall"] == pytest.approx((5 - 4.9) / 3 * 100.0)

    # Pressure: 2 balls in Death. Actual runs = 4. Exp runs = 2 * 1.80 = 3.60.
    # Actual SR = (4 / 2) * 100 = 200.0. Exp SR = 180.0. TSR = +20.0
    assert bat["tsr_pressure"] == pytest.approx(20.0)

    # Dot avoidance:
    # Overall: 2 non-dots / 3 balls = 0.6666...
    # Pressure: 1 non-dot / 2 balls = 0.50
    assert bat["dot_avoidance_overall"] == pytest.approx(2 / 3)
    assert bat["dot_avoidance_pressure"] == pytest.approx(0.50)

    # WPA per 100:
    # Overall: (0.01 + 0.06 - 0.04) / 3 * 100 = 0.03 / 3 * 100 = 1.00
    # Pressure: (0.06 - 0.04) / 2 * 100 = 0.02 / 2 * 100 = 1.00
    assert bat["wpa_per_100_overall"] == pytest.approx(1.00)
    assert bat["wpa_per_100_pressure"] == pytest.approx(1.00)

    # Batting order:
    assert bat["primary_batting_pos"] == 3
    assert bat["top7_appearance_pct"] == pytest.approx(1.0)

    # Bowler assertions:
    bowl = df_bowlers[df_bowlers["player_id"] == 201].iloc[0]
    assert bowl["n_balls_overall"] == 3
    assert bowl["n_eff_overall"] == pytest.approx(2.7)
    assert bowl["n_balls_pressure"] == 2
    assert bowl["n_eff_pressure"] == pytest.approx(1.8)

    # TER overall:
    # Conceded = 1 + 4 + 0 = 5.
    # Exp conceded = 1*1.30 + 2*1.80 = 4.90.
    # Expected par ER - Actual ER = (4.90 - 5.0) / 3 * 6.0 = -0.10 / 3 * 6.0 = -0.20
    assert bowl["ter_overall"] == pytest.approx(-0.20)

    # TER pressure:
    # Conceded = 4. Exp conceded = 2 * 1.80 = 3.60.
    # Expected par ER - Actual ER = (3.60 - 4.0) / 2 * 6.0 = -0.40 / 2 * 6.0 = -1.20
    assert bowl["ter_pressure"] == pytest.approx(-1.20)

    # High-leverage wickets:
    # Ball 3 is wicket with LI = 2.5 (pressure). Ball 1 & 2 no wicket.
    assert bowl["hl_wickets_overall"] == pytest.approx(2.5)
    assert bowl["hl_wickets_pressure"] == pytest.approx(2.5)

    # Dot %:
    # Overall: 1 dot / 3 balls = 0.333...
    # Pressure: 1 dot / 2 balls = 0.50
    assert bowl["dot_pct_overall"] == pytest.approx(1 / 3)
    assert bowl["dot_pct_pressure"] == pytest.approx(0.50)

    # Avg overs per match:
    # 3 balls in 1 match -> (3 / 6.0) / 1 = 0.50
    assert bowl["avg_overs_per_match"] == pytest.approx(0.50)


def test_zero_pressure_player():
    """Verify player with zero high-pressure deliveries receives 0.0 pressure metrics."""
    phase_pars = {
        "Powerplay": {"runs_per_ball": 1.25, "par_sr": 125.0, "par_er": 7.50, "dot_pct": 0.40, "boundary_pct": 0.15},
        "Middle": {"runs_per_ball": 1.30, "par_sr": 130.0, "par_er": 7.80, "dot_pct": 0.35, "boundary_pct": 0.12},
        "Death": {"runs_per_ball": 1.65, "par_sr": 165.0, "par_er": 9.90, "dot_pct": 0.30, "boundary_pct": 0.20},
    }
    df = pd.DataFrame([
        {
            "match_id": 1, "innings": 1, "overid": 2, "phase": "Powerplay",
            "striker_id": 999, "striker_name": "Low Stress Batter", "batting_order": 1,
            "bowler_id": 888, "bowler_name": "Low Stress Bowler",
            "runs": 2, "bowler_runs_conceded": 2, "is_bowler_wicket": False,
            "is_dot": False, "delta_wpa": 0.01, "leverage_index": 0.8,
            "is_high_pressure": False, "comp_weight": 1.0
        }
    ])
    df_batters, df_bowlers = calculate_player_raw_metrics(df, phase_pars)

    bat = df_batters.iloc[0]
    assert bat["n_balls_overall"] == 1
    assert bat["n_balls_pressure"] == 0
    assert bat["n_eff_pressure"] == 0.0
    assert bat["tsr_pressure"] == 0.0
    assert bat["wpa_per_100_pressure"] == 0.0
    assert bat["dot_avoidance_pressure"] == 0.0

    bowl = df_bowlers.iloc[0]
    assert bowl["n_balls_overall"] == 1
    assert bowl["n_balls_pressure"] == 0
    assert bowl["n_eff_pressure"] == 0.0
    assert bowl["ter_pressure"] == 0.0
    assert bowl["hl_wickets_pressure"] == 0.0
    assert bowl["dot_pct_pressure"] == 0.0


def test_empty_dataframe():
    """Verify empty dataframe handling returns structured empty DataFrames."""
    phase_pars = compute_phase_par_rates(pd.DataFrame())
    assert "Powerplay" in phase_pars
    assert "Middle" in phase_pars
    assert "Death" in phase_pars

    df_batters, df_bowlers = calculate_player_raw_metrics(pd.DataFrame(), phase_pars)
    assert df_batters.empty
    assert df_bowlers.empty
    assert "player_id" in df_batters.columns
    assert "tsr_pressure" in df_batters.columns
    assert "player_id" in df_bowlers.columns
    assert "ter_pressure" in df_bowlers.columns


def test_missing_names_and_wides():
    """Verify missing player names fallback to ID string and wides are excluded for batters."""
    phase_pars = compute_phase_par_rates(pd.DataFrame())
    df = pd.DataFrame([
        {
            "match_id": 1, "innings": 1, "overid": 5, "phase": "Powerplay",
            "striker_id": 999, "striker_name": None, "batting_order": 2,
            "bowler_id": 888, "bowler_name": None,
            "runs": 0, "bowler_runs_conceded": 1, "extras_type": "wides",
            "is_bowler_wicket": False, "is_dot": False, "delta_wpa": -0.01,
            "leverage_index": 1.6, "is_high_pressure": True, "comp_weight": 0.8
        },
        {
            "match_id": 1, "innings": 1, "overid": 5, "phase": "Powerplay",
            "striker_id": 999, "striker_name": None, "batting_order": 2,
            "bowler_id": 888, "bowler_name": None,
            "runs": 4, "bowler_runs_conceded": 4, "extras_type": None,
            "is_bowler_wicket": False, "is_dot": False, "delta_wpa": 0.05,
            "leverage_index": 1.6, "is_high_pressure": True, "comp_weight": 0.8
        }
    ])
    df_batters, df_bowlers = calculate_player_raw_metrics(df, phase_pars)
    assert df_batters.iloc[0]["player_name"] == "999"
    assert df_batters.iloc[0]["n_balls_overall"] == 1  # 1 ball faced (wide excluded)
    assert df_batters.iloc[0]["n_eff_overall"] == pytest.approx(0.8)
    assert df_bowlers.iloc[0]["player_name"] == "888"
    assert df_bowlers.iloc[0]["n_balls_overall"] == 2  # 2 balls bowled (wide included)


def test_missing_batting_order_nan_handling():
    """Verify missing/all-NaN batting_order does not raise ValueError and defaults to 4."""
    phase_pars = compute_phase_par_rates(pd.DataFrame())
    df = pd.DataFrame([
        {
            "match_id": 1, "innings": 1, "overid": 10, "phase": "Middle",
            "striker_id": 555, "striker_name": "Unknown Order Batter",
            "batting_order": np.nan,
            "bowler_id": 666, "bowler_name": "Test Bowler",
            "runs": 2, "bowler_runs_conceded": 2,
            "is_bowler_wicket": False, "is_dot": False, "delta_wpa": 0.02,
            "leverage_index": 1.1, "is_high_pressure": False, "comp_weight": 1.0
        },
        {
            "match_id": 1, "innings": 1, "overid": 10, "phase": "Middle",
            "striker_id": 555, "striker_name": "Unknown Order Batter",
            "batting_order": None,
            "bowler_id": 666, "bowler_name": "Test Bowler",
            "runs": 1, "bowler_runs_conceded": 1,
            "is_bowler_wicket": False, "is_dot": False, "delta_wpa": 0.01,
            "leverage_index": 1.1, "is_high_pressure": False, "comp_weight": 1.0
        }
    ])
    df_batters, df_bowlers = calculate_player_raw_metrics(df, phase_pars)
    assert not df_batters.empty
    assert df_batters.iloc[0]["primary_batting_pos"] == 4
    assert df_batters.iloc[0]["top7_appearance_pct"] == pytest.approx(1.0)


def test_phase_par_rates_wides_exclusion():
    """Verify that league par SR excludes wides from denominator while par ER includes all balls."""
    df = pd.DataFrame([
        {
            "match_id": 1, "overid": 3, "phase": "Powerplay",
            "runs": 0, "bowler_runs_conceded": 1, "extras_type": "wides",
            "is_dot": False, "is_four": False, "is_six": False
        },
        {
            "match_id": 1, "overid": 3, "phase": "Powerplay",
            "runs": 4, "bowler_runs_conceded": 4, "extras_type": None,
            "is_dot": False, "is_four": True, "is_six": False
        }
    ])
    pars = compute_phase_par_rates(df)
    # Total balls = 2, non-wide balls = 1, bat runs = 4, bowl runs = 5
    # RPB = 4 / 1 = 4.0 -> par_sr = 400.0
    # Par ER = (5 / 2) * 6.0 = 15.0
    assert pars["Powerplay"]["runs_per_ball"] == pytest.approx(4.0)
    assert pars["Powerplay"]["par_sr"] == pytest.approx(400.0)
    assert pars["Powerplay"]["par_er"] == pytest.approx(15.0)


