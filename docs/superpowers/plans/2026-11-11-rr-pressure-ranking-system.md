# Rajasthan Royals SupeRR Selector Season 2: Pressure Ranking System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade sports analytics engine and automated reporting pipeline that identifies and ranks the Top 10 Batters and Top 10 Bowlers under high pressure for the Rajasthan Royals IPL 2027 auction strategy, outputting a 15–20 page executive presentation deck PDF and validated Unstop rankings.

**Architecture:** A modular Python pipeline that: (1) reconstructs ball-by-ball delivery state across 2022–2026 IPL and T20Is; (2) calculates Win Expectancy $P(\text{Win})$ and Leverage Index ($LI \ge 1.50$) across both innings; (3) computes context-adjusted True Strike Rate, True Economy, Dot% impact, and high-leverage wickets; (4) establishes personal baselines and computes a $70/30$ Dual-Axis Composite Score smoothed via Empirical Bayes shrinkage; and (5) generates publication-grade visualizations and an executive landscape slide deck PDF.

**Tech Stack:** Python 3.14 (via `/usr/bin/uv`), `pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `reportlab`, `pytest`.

**Spec:** `/home/naveen/Data/Projects/RR Hackathon/docs/superpowers/specs/2026-11-10-rr-superr-selector-pressure-ranking-design.md`

---

## Global Constraints

- **Language & Runtime:** Python 3.14 managed through `/usr/bin/uv` within the local `.venv`.
- **Data Source:** Strictly bounded to `/home/naveen/Data/Projects/RR Hackathon/` (`ball_by_ball.csv`, `matches.csv`, `playing_eleven.csv`, `competition_team_player_mapping.csv`, `teams.csv`, `competitions.csv`).
- **Pressure Qualification Threshold:** Effective pressure deliveries $N_{\text{eff}} = \sum_{\text{balls}} W_{\text{comp}} \times \mathbb{I}(LI \ge 1.50) \ge 75$ deliveries.
- **Competition Weighting:** $W_{\text{comp}} = 1.00$ for IPL; $0.70 \le W_{\text{comp}} \le 0.95$ for T20Is based on ICC opposition quality tiers.
- **Empirical Bayes Prior Strength:** Prior weight $M = 30$ effective deliveries regressing toward population mean $\mu_0$.
- **Dual-Axis Weighting:** $70\%$ High-Pressure Absolute Performance Index ($HP$) + $30\%$ Personal Baseline Clutch Delta ($\Delta_{\text{Clutch}}$).
- **Deliverable Format:** A single 15–20 page landscape PDF presentation deck matching Unstop's single-file upload limit.

---

## Review Focus

1. **Super Overs and Rain-Shortened Matches (DLS/Revised Overs):** Revised targets and reduced overs in `matches.csv` must correctly override standard 20-over targets to prevent negative balls remaining or warped run rate spikes.
2. **First-Innings Leverage Bounds:** In the 1st innings, win probability is derived from expected final score vs venue par; extreme blowouts (e.g. 10/5 in 3 overs) must remain bounded in $[0.01, 0.99]$ without exploding the Leverage Index denominator.
3. **Bowler Extras & Unearned Runs Attribution:** Wides, no-balls, leg-byes, and byes must be partitioned accurately: bowler conceded runs include wides and no-balls, but exclude leg-byes and byes; run-outs must not be credited as bowler wickets.
4. **All-Rounder and Batting Position Sanity:** Pure tailenders hitting late boundaries must be filtered by requiring $\ge 50\%$ appearances in batting positions 1–7; bowlers must average $\ge 1.5$ overs per match in the dataset.
5. **Dropdown Schema Integrity:** Player IDs and names selected in Top 10 Batters and Top 10 Bowlers must exactly cross-reference `competition_team_player_mapping.csv` and allow zero duplicates.

---

## Task Decomposition

### Task 1: Environment Verification, Data Ingestion & Match State Reconstruction

**Files:**
- Create: `src/__init__.py`
- Create: `src/data_loader.py`
- Create: `tests/__init__.py`
- Test: `tests/test_data_loader.py`

**Interfaces:**
- Consumes: Raw CSV files from `/home/naveen/Data/Projects/RR Hackathon/`
- Produces: `load_and_process_deliveries(data_dir: str) -> pd.DataFrame` returning delivery-level records enriched with:
  - `cum_runs_innings`, `cum_wickets_innings`, `balls_elapsed_innings`, `balls_remaining_innings`
  - `phase` (`Powerplay`: 1–6, `Middle`: 7–15, `Death`: 16–20)
  - `target_runs`, `runs_required`, `required_run_rate`, `current_run_rate` (for 2nd innings)
  - `bowler_runs_conceded`, `is_bowler_wicket`
  - `comp_weight` ($1.0$ for IPL, $0.70$–$0.95$ for T20Is)

- [ ] **Step 1: Write the failing test for data loading and state reconstruction**

In `tests/test_data_loader.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_data_loader.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.data_loader'`

- [ ] **Step 3: Implement `src/data_loader.py`**

Implement `load_and_process_deliveries(data_dir: str, sample_matches: int = None) -> pd.DataFrame`:
- Read `competitions.csv`, `matches.csv`, and `ball_by_ball.csv`.
- Assign `comp_weight`: IPL competitions get $1.00$; tier T20Is using ICC top-8 teams vs associate lookup ($0.95$ for Top-8 vs Top-8, $0.85$ for Top-8 vs Associate, $0.70$ for Associate vs Associate).
- Calculate cumulative runs, cumulative wickets, and balls remaining per match innings.
- Incorporate DLS/revised targets from `matches.csv` (`revised_target`, `second_inn_revised_overs`).
- Separate bowler runs conceded from batter runs and non-bowler extras (byes, leg-byes).
- Flag `is_bowler_wicket` (dismissals excluding Run Out, Retired Hurt, Obstructing Field).

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_data_loader.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/__init__.py src/data_loader.py tests/__init__.py tests/test_data_loader.py
git commit -m "feat: implement data loading and match state reconstruction"
```

---

### Task 2: Win Probability Modeling & Leverage Index ($LI$) Calculation

**Files:**
- Create: `src/win_prob.py`
- Test: `tests/test_win_prob.py`

**Interfaces:**
- Consumes: Enriched deliveries DataFrame from `src.data_loader`
- Produces:
  - `train_win_prob_models(df: pd.DataFrame) -> dict`: Returns trained models for Innings 1 and Innings 2.
  - `compute_win_probability_and_leverage(df: pd.DataFrame, models: dict) -> pd.DataFrame`: Appends `win_prob`, `delta_wpa`, `leverage_index`, and `is_high_pressure` ($LI \ge 1.50$).

- [ ] **Step 1: Write the failing test for win probability and leverage calculation**

In `tests/test_win_prob.py`:
```python
import pytest
import numpy as np
import pandas as pd
from src.win_prob import train_win_prob_models, compute_win_probability_and_leverage

def test_win_prob_and_leverage_pipeline():
    # Synthetic match data for quick test
    rows = []
    for inn in [1, 2]:
        for b in range(1, 121):
            rows.append({
                "match_id": 1001, "innings": inn, "overid": (b - 1) // 6 + 1,
                "over_ball_num": (b - 1) % 6 + 1, "balls_remaining_innings": 120 - b,
                "cum_runs_innings": int(b * 1.4), "cum_wickets_innings": min(b // 20, 9),
                "phase": "Powerplay" if b <= 36 else ("Middle" if b <= 90 else "Death"),
                "runs": 1, "is_bowler_wicket": False, "comp_weight": 1.0,
                "target_runs": 170 if inn == 2 else 0,
                "runs_required": max(0, 170 - int(b * 1.4)) if inn == 2 else 0,
                "required_run_rate": ((170 - int(b * 1.4)) / max(1, 120 - b)) * 6 if inn == 2 else 0.0,
                "venue_country": "India", "home_team_id": 1, "away_team_id": 2, "win_team_id": 2
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_win_prob.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.win_prob'`

- [ ] **Step 3: Implement `src/win_prob.py`**

Implement:
- `train_win_prob_models(df: pd.DataFrame) -> dict`:
  - **Innings 1**: Calibrated regressor predicting final score from `(balls_remaining_innings, cum_wickets_innings, cum_runs_innings)`, converted to win probability via logistic CDF against historical venue par distribution.
  - **Innings 2**: Calibrated Logistic Regression classifier predicting chase success from `(runs_required, balls_remaining_innings, cum_wickets_innings, required_run_rate)`.
- `compute_win_probability_and_leverage(df: pd.DataFrame, models: dict) -> pd.DataFrame`:
  - Compute ball-by-ball $P(\text{Win})$.
  - Compute delivery outcome expectation swing: $\Delta WPA = P_t - P_{t-1}$.
  - Compute $LI_t = \frac{\mathbb{E}[|\Delta WPA(S_t)|]}{\overline{\Delta WPA}}$.
  - Add boolean flag: `is_high_pressure = (leverage_index >= 1.50)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_win_prob.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/win_prob.py tests/test_win_prob.py
git commit -m "feat: implement unified win probability and leverage index engine"
```

---

### Task 3: Performance Metric Computation & Phase Par Baselines

**Files:**
- Create: `src/metrics.py`
- Test: `tests/test_metrics.py`

**Interfaces:**
- Consumes: Deliveries with win probability & leverage from `src.win_prob`
- Produces:
  - `compute_phase_par_rates(df: pd.DataFrame) -> dict`: Benchmark league par Strike Rate and Economy Rate for Powerplay, Middle, and Death overs.
  - `calculate_player_raw_metrics(df: pd.DataFrame, phase_pars: dict) -> tuple[pd.DataFrame, pd.DataFrame]`: Returns raw performance tables for all batters and bowlers partitioned into overall baseline vs high-pressure ($LI \ge 1.50$).

- [ ] **Step 1: Write the failing test for metrics computation**

In `tests/test_metrics.py`:
```python
import pytest
import pandas as pd
from src.metrics import compute_phase_par_rates, calculate_player_raw_metrics

def test_metrics_computation():
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.metrics'`

- [ ] **Step 3: Implement `src/metrics.py`**

Implement:
- `compute_phase_par_rates(df: pd.DataFrame) -> dict`: League average runs per ball, boundary %, and dot % across Powerplay, Middle, Death.
- `calculate_player_raw_metrics(df: pd.DataFrame, phase_pars: dict) -> tuple[pd.DataFrame, pd.DataFrame]`:
  - Batters: Total balls faced, effective pressure balls $N_{\text{eff}}$, Actual SR vs Par SR $\rightarrow True Strike Rate (TSR)$, Dot Ball % Avoidance, Cumulative WPA per 100 balls.
  - Bowlers: Total balls bowled, effective pressure balls $N_{\text{eff}}$, Par ER vs Actual ER $\rightarrow True Economy Rate (TER)$, Pressure Dot Ball %, High-Leverage Wickets taken ($Wickets \times LI$).
  - Compute each metric across **Overall Baseline** and **High-Pressure** ($LI \ge 1.50$).

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_metrics.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/metrics.py tests/test_metrics.py
git commit -m "feat: implement phase-par benchmarking and context-adjusted metrics"
```

---

### Task 4: Dual-Axis Composite Scoring, Empirical Bayes Shrinkage & Top 10 Ranking

**Files:**
- Create: `src/rankings.py`
- Test: `tests/test_rankings.py`

**Interfaces:**
- Consumes: Raw player metrics from `src.metrics`
- Produces:
  - `compute_rankings(df_batters: pd.DataFrame, df_bowlers: pd.DataFrame, min_pressure_balls: int = 75, prior_m: float = 30.0) -> tuple[pd.DataFrame, pd.DataFrame]`: Returns fully ordered Top 10 Batters and Top 10 Bowlers with normalized composite scores, baseline deltas, and shrinkage adjustments.

- [ ] **Step 1: Write the failing test for rankings and shrinkage**

In `tests/test_rankings.py`:
```python
import pytest
import pandas as pd
from src.rankings import compute_rankings

def test_rankings_dual_axis_and_shrinkage():
    # Generate mock batter and bowler records
    bat_data = []
    for i in range(1, 25):
        bat_data.append({
            "player_id": 100 + i, "player_name": f"Batter {i}",
            "n_eff_pressure": 85 if i <= 15 else 30, # Some below threshold
            "tsr_pressure": 15.0 + i, "tsr_overall": 10.0 + (i * 0.5),
            "wpa_per_100_pressure": 0.04 + (i * 0.005), "wpa_per_100_overall": 0.02,
            "dot_avoidance_pressure": 0.65 + (i * 0.01), "dot_avoidance_overall": 0.60,
            "primary_batting_pos": 4
        })
    bowl_data = []
    for i in range(1, 25):
        bowl_data.append({
            "player_id": 200 + i, "player_name": f"Bowler {i}",
            "n_eff_pressure": 90 if i <= 15 else 20,
            "ter_pressure": 1.2 + (i * 0.1), "ter_overall": 0.8 + (i * 0.05),
            "hl_wickets_pressure": 5 + i, "hl_wickets_overall": 10,
            "dot_pct_pressure": 0.40 + (i * 0.01), "dot_pct_overall": 0.35,
            "avg_overs_per_match": 3.5
        })
    df_top_bat, df_top_bowl = compute_rankings(pd.DataFrame(bat_data), pd.DataFrame(bowl_data), min_pressure_balls=75)
    
    assert len(df_top_bat) == 10
    assert len(df_top_bowl) == 10
    # Ensure rank order is descending by final regressed score
    assert df_top_bat["composite_score"].is_monotonic_decreasing
    assert df_top_bowl["composite_score"].is_monotonic_decreasing
    # Ensure all qualifiers have at least 75 pressure balls
    assert (df_top_bat["n_eff_pressure"] >= 75).all()
    assert (df_top_bowl["n_eff_pressure"] >= 75).all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_rankings.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.rankings'`

- [ ] **Step 3: Implement `src/rankings.py`**

Implement `compute_rankings(df_batters, df_bowlers, min_pressure_balls=75, prior_m=30.0)`:
- Standardize components via z-score:
  - $HP_{\text{Bat}} = 0.50 \cdot z(TSR) + 0.30 \cdot z(WPA_{100}) + 0.20 \cdot z(\text{DotAvoid})$
  - $\Delta_{\text{Bat}} = z(TSR_{\text{Pressure}}) - z(TSR_{\text{Overall}})$
  - $S_{\text{raw, Bat}} = 0.70 \cdot HP_{\text{Bat}} + 0.30 \cdot \Delta_{\text{Bat}}$
  - $HP_{\text{Bowl}} = 0.45 \cdot z(TER) + 0.35 \cdot z(\text{HL\_Wickets}) + 0.20 \cdot z(\text{Dot}\%)$
  - $\Delta_{\text{Bowl}} = z(TER_{\text{Pressure}}) - z(TER_{\text{Overall}})$
  - $S_{\text{raw, Bowl}} = 0.70 \cdot HP_{\text{Bowl}} + 0.30 \cdot \Delta_{\text{Bowl}}$
- Apply Empirical Bayes Shrinkage toward population mean $\mu_0$:
  $$S_{\text{final}} = \frac{N_{\text{eff}}}{N_{\text{eff}} + M} S_{\text{raw}} + \frac{M}{N_{\text{eff}} + M} \mu_0$$
- Filter by $N_{\text{eff}} \ge 75$ and role criteria ($\ge 50\%$ top-7 batting appearances for batters; $\ge 1.5$ overs/match for bowlers).
- Return Top 10 Batters and Top 10 Bowlers sorted by $S_{\text{final}}$ descending with Rank 1 to 10.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_rankings.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/rankings.py tests/test_rankings.py
git commit -m "feat: implement dual-axis composite scoring and empirical bayes shrinkage"
```

---

### Task 5: Schema Validation & Sensitivity Analysis

**Files:**
- Create: `src/validation.py`
- Test: `tests/test_validation.py`

**Interfaces:**
- Consumes: Ranked Top 10 DataFrames from `src.rankings` and `competition_team_player_mapping.csv`
- Produces:
  - `validate_unstop_compliance(top_batters: pd.DataFrame, top_bowlers: pd.DataFrame, data_dir: str) -> dict`: Verifies zero duplicates, player existence in official ID mappings, and outputs exact dropdown values.
  - `compute_bootstrap_sensitivity(df_balls: pd.DataFrame, top_batters: pd.DataFrame, top_bowlers: pd.DataFrame, n_iterations: int = 500) -> dict`: Computes $95\%$ bootstrap confidence intervals for player rankings and scores.

- [ ] **Step 1: Write the failing test for validation and bootstrap checks**

In `tests/test_validation.py`:
```python
import pytest
import pandas as pd
from src.validation import validate_unstop_compliance

def test_unstop_compliance_verification():
    mock_bat = pd.DataFrame([{"player_id": 1187, "player_name": "Jason Roy", "rank": 1}])
    mock_bowl = pd.DataFrame([{"player_id": 1772, "player_name": "Sheldon Cottrell", "rank": 1}])
    report = validate_unstop_compliance(mock_bat, mock_bowl, "/home/naveen/Data/Projects/RR Hackathon")
    assert report["valid"] is True
    assert report["batter_duplicates"] == 0
    assert report["bowler_duplicates"] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_validation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.validation'`

- [ ] **Step 3: Implement `src/validation.py`**

Implement:
- `validate_unstop_compliance(top_batters, top_bowlers, data_dir)`: Checks against `competition_team_player_mapping.csv`, confirms IDs exist, verifies no player is duplicated within the same top-10 list, and formats dropdown-ready output.
- `compute_bootstrap_sensitivity(df_balls, top_batters, top_bowlers, n_iterations=500)`: Resamples matches with replacement, recomputes rankings, and derives $95\%$ rank confidence intervals (e.g., Rank 1 [CI: 1–2]) to demonstrate statistical robustness in the report.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_validation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/validation.py tests/test_validation.py
git commit -m "feat: implement unstop schema validation and bootstrap sensitivity analysis"
```

---

### Task 6: Visualizations & Publication Figure Generation

**Files:**
- Create: `src/visualizer.py`
- Test: `tests/test_visualizer.py`

**Interfaces:**
- Consumes: Models from `src.win_prob`, deliveries DataFrame, and Top 10 rankings
- Produces: Generates high-res vector/PNG figures in `reports/figures/`:
  - `fig1_win_prob_curves.png`: Dynamic Win Probability swings across classic high-leverage matches.
  - `fig2_leverage_distribution.png`: Histogram & density of $LI$ highlighting the $LI \ge 1.50$ high-pressure threshold.
  - `fig3_batters_baseline_vs_pressure.png`: Scatter plot showing personal baseline vs pressure performance with shrinkage vectors.
  - `fig4_bowlers_baseline_vs_pressure.png`: Scatter plot for True Economy and Wicket Clutchness.
  - `fig5_top_players_radar.png`: Multivariate skill radar charts for the Top 3 Batters and Top 3 Bowlers.

- [ ] **Step 1: Write the failing test for figure generation**

In `tests/test_visualizer.py`:
```python
import os
import pytest
import pandas as pd
from src.visualizer import generate_all_figures

def test_visualizer_generates_required_figures(tmp_path):
    output_dir = tmp_path / "figures"
    # Create minimal mock dfs
    df_mock_balls = pd.DataFrame({
        "leverage_index": [0.5, 1.2, 1.8, 2.5, 3.2],
        "win_prob": [0.5, 0.55, 0.40, 0.70, 0.95],
        "balls_remaining_innings": [100, 80, 50, 20, 5]
    })
    mock_bat = pd.DataFrame([{"player_name": f"P{i}", "tsr_pressure": 20-i, "tsr_overall": 10, "composite_score": 1.5-i*0.1} for i in range(10)])
    mock_bowl = pd.DataFrame([{"player_name": f"B{i}", "ter_pressure": 2-i*0.1, "ter_overall": 1, "composite_score": 1.5-i*0.1} for i in range(10)])
    
    fig_paths = generate_all_figures(df_mock_balls, mock_bat, mock_bowl, str(output_dir))
    for key, path in fig_paths.items():
        assert os.path.exists(path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_visualizer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.visualizer'`

- [ ] **Step 3: Implement `src/visualizer.py`**

Implement `generate_all_figures(df_balls, top_batters, top_bowlers, output_dir)` using Matplotlib and Seaborn with a clean, dark/navy Rajasthan Royals franchise aesthetic (navy blue `#0b1a30`, royal pink `#ea1a7f`, and gold `#d4af37` accents).
- Export all 5 required high-resolution visual evidence assets.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_visualizer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/visualizer.py tests/test_visualizer.py
git commit -m "feat: implement high-resolution publication visualization engine"
```

---

### Task 7: Executive Presentation Deck PDF Generation

**Files:**
- Create: `src/deck_generator.py`
- Test: `tests/test_deck_generator.py`

**Interfaces:**
- Consumes: Top 10 rankings, validation report, and generated figures from `src/visualizer.py`
- Produces: `build_executive_deck(top_batters: pd.DataFrame, top_bowlers: pd.DataFrame, figures: dict, output_path: str) -> str`: Compiles the 16-page landscape corporate PDF presentation deck ready for Unstop upload.

- [ ] **Step 1: Write the failing test for deck compilation**

In `tests/test_deck_generator.py`:
```python
import os
import pytest
import pandas as pd
from src.deck_generator import build_executive_deck

def test_deck_compilation(tmp_path):
    output_pdf = tmp_path / "Methodology_Report_SupeRR_Selector.pdf"
    mock_bat = pd.DataFrame([{"rank": i, "player_name": f"Batter {i}", "n_eff_pressure": 100, "tsr_pressure": 25.0, "composite_score": 2.1} for i in range(1, 11)])
    mock_bowl = pd.DataFrame([{"rank": i, "player_name": f"Bowler {i}", "n_eff_pressure": 95, "ter_pressure": 1.8, "composite_score": 1.9} for i in range(1, 11)])
    
    pdf_path = build_executive_deck(mock_bat, mock_bowl, {}, str(output_pdf))
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000 # Non-empty PDF
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_deck_generator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.deck_generator'`

- [ ] **Step 3: Implement `src/deck_generator.py`**

Implement `build_executive_deck(top_batters, top_bowlers, figures, output_path)`:
- Using ReportLab / Matplotlib PDF backend to build a 16-slide landscape ($16:9$, $1920\times1080$ aspect ratio) executive presentation:
  - Slide 1: Cover Slide & Mission Brief (Rajasthan Royals War Room).
  - Slide 2: Executive Summary & The Pressure Performance Problem.
  - Slide 3: Unified Win Expectancy ($P(\text{Win})$) Across Both Innings.
  - Slide 4: Quantifying Situational Stakes: The Leverage Index ($LI \ge 1.50$).
  - Slide 5: Performance Metric Formulations: True Strike Rate ($TSR$) & True Economy Rate ($TER$).
  - Slide 6: The Dual-Axis Evaluation Model ($70\%$ Absolute Performance $+ 30\%$ Personal Baseline Delta).
  - Slide 7: Statistical Control: Competition Quality Weights & Empirical Bayes Shrinkage ($M=30$).
  - Slide 8: **Top 10 Batters Under Pressure: Full Roster & Score Breakdown**.
  - Slide 9: Top 3 Batters Spotlight: Individual Tactical Profile Cards.
  - Slide 10: **Top 10 Bowlers Under Pressure: Full Roster & Score Breakdown**.
  - Slide 11: Top 3 Bowlers Spotlight: Individual Tactical Profile Cards.
  - Slide 12: Empirical Evidence: Win Probability Swings in Decisive Overs.
  - Slide 13: Distribution Analysis: High-Leverage vs Low-Leverage Delivery Spread.
  - Slide 14: Model Reliability, Cross-Match Consistency & $95\%$ Bootstrap Confidence Intervals.
  - Slide 15: Strategic War Room Rationale for the IPL 2027 Auction.
  - Slide 16: Appendix & Reproducibility Code Manifest.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_deck_generator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/deck_generator.py tests/test_deck_generator.py
git commit -m "feat: implement 16-page executive landscape presentation deck builder"
```

---

### Task 8: End-to-End Pipeline Integration, Full Dataset Execution & Verification

**Files:**
- Create: `main.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: All modules from Tasks 1 through 7
- Produces:
  - `reports/Methodology_Report_SupeRR_Selector_Season_2.pdf` (The single submission document)
  - `reports/unstop_dropdown_rankings.json` and `reports/unstop_dropdown_rankings.csv` (The exact Rank 1–10 selections)
  - Execution summary printed to stdout.

- [ ] **Step 1: Write integration test**

In `tests/test_end_to_end.py`:
```python
import os
import pytest
import subprocess

def test_full_pipeline_cli():
    # Run main pipeline on sample
    cmd = [".venv/bin/python", "main.py", "--sample", "20"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert os.path.exists("reports/Methodology_Report_SupeRR_Selector_Season_2.pdf")
    assert os.path.exists("reports/unstop_dropdown_rankings.csv")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_end_to_end.py -v`
Expected: FAIL with `python: can't open file 'main.py'`

- [ ] **Step 3: Implement `main.py`**

Wire the complete workflow:
1. Parse CLI arguments (`--data-dir`, `--sample`, `--output-dir`).
2. Run `data_loader.load_and_process_deliveries`.
3. Run `win_prob.train_win_prob_models` and calculate $P(\text{Win})$ and $LI$.
4. Run `metrics.calculate_player_raw_metrics`.
5. Run `rankings.compute_rankings` to produce Top 10 Batters and Bowlers.
6. Run `validation.validate_unstop_compliance` and `compute_bootstrap_sensitivity`.
7. Run `visualizer.generate_all_figures`.
8. Run `deck_generator.build_executive_deck`.
9. Export `reports/unstop_dropdown_rankings.csv` and `reports/unstop_dropdown_rankings.json`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_end_to_end.py -v`
Expected: PASS

- [ ] **Step 5: Execute full dataset and commit**

Run: `.venv/bin/python main.py`
Expected: Full generation of Top 10 rankings and final submission PDF.
```bash
git add main.py tests/test_end_to_end.py
git commit -m "feat: complete end-to-end analytics and presentation generation pipeline"
```
