"""Dual-Axis Composite Scoring, Empirical Bayes Shrinkage & Top 10 Ranking Engine.

Implements the Rajasthan Royals SupeRR Selector Season 2 ranking methodology:
1. Standardizes absolute high-pressure performance components (HP_Bat, HP_Bowl).
2. Computes personal clutch baseline deltas (Delta_Bat, Delta_Bowl).
3. Combines into a 70/30 Dual-Axis Composite Score (S_raw).
4. Smooths estimates via Empirical Bayes Shrinkage toward the population mean (mu_0)
   to penalize small sample variance (prior weight M = 30 balls).
5. Applies strict volume and role eligibility thresholds (N_eff >= 75 balls,
   batting positions 1-7, >= 1.5 overs/match).
6. Outputs ranked Top 10 Batters and Top 10 Bowlers under pressure.
"""

from __future__ import annotations

from typing import Tuple
import numpy as np
import pandas as pd


def _standardize(series: pd.Series) -> pd.Series:
    """Computes sample z-score standardization (zero mean, unit variance).

    Handles zero variance, NaN values, and single-item series safely.
    """
    s = series.fillna(0.0).astype(float)
    std = s.std(ddof=0)
    if std == 0.0 or np.isnan(std):
        return pd.Series(0.0, index=s.index, dtype=float)
    return (s - s.mean()) / std


def compute_batting_rankings(
    df_batters: pd.DataFrame,
    min_pressure_balls: int = 75,
    prior_m: float = 30.0,
    top_n: int = 10,
) -> pd.DataFrame:
    """Computes dual-axis composite pressure score and rankings for batters.

    Formula:
      HP_Bat = 0.50 * z(TSR_Pressure) + 0.30 * z(WPA_100_Pressure) + 0.20 * z(DotAvoid_Pressure)
      Delta_Bat = z(TSR_Pressure) - z(TSR_Overall)
      S_raw = 0.70 * HP_Bat + 0.30 * Delta_Bat
      S_final = (N_eff / (N_eff + M)) * S_raw + (M / (N_eff + M)) * mu_0

    Parameters
    ----------
    df_batters : pd.DataFrame
        Batters metrics DataFrame containing TSR, WPA/100, dot avoidance, and volume.
    min_pressure_balls : int, default 75
        Minimum effective pressure deliveries required to qualify.
    prior_m : float, default 30.0
        Empirical Bayes prior sample size weight.
    top_n : int, default 10
        Number of top-ranked players to return.

    Returns
    -------
    pd.DataFrame
        Ranked qualifying batters with composite score, component scores, and rank.
    """
    base_cols = [
        "rank",
        "player_id",
        "player_name",
        "composite_score",
        "raw_score",
        "hp_index",
        "delta_score",
        "shrinkage_weight",
    ]
    if df_batters.empty:
        return pd.DataFrame(columns=base_cols)

    df = df_batters.copy()

    # Column name resolution with graceful fallbacks
    tsr_press = df.get("tsr_pressure", pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    tsr_over = df.get("tsr_overall", tsr_press).fillna(0.0).astype(float)
    wpa_press = (
        df.get("wpa_per_100_pressure", df.get("wpa_pressure", pd.Series(0.0, index=df.index)))
        .fillna(0.0)
        .astype(float)
    )
    dot_avoid = (
        df.get(
            "dot_avoidance_pressure",
            df.get("dot_avoid_pressure", pd.Series(0.0, index=df.index)),
        )
        .fillna(0.0)
        .astype(float)
    )
    n_eff = (
        df.get("n_eff_pressure", df.get("n_balls_pressure", pd.Series(0.0, index=df.index)))
        .fillna(0.0)
        .astype(float)
    )

    # 1. Z-Score Standardization
    z_tsr_press = _standardize(tsr_press)
    z_tsr_over = _standardize(tsr_over)
    z_wpa_press = _standardize(wpa_press)
    z_dot_avoid = _standardize(dot_avoid)

    # 2. High-Pressure Index & Baseline Delta
    hp_bat = 0.50 * z_tsr_press + 0.30 * z_wpa_press + 0.20 * z_dot_avoid
    delta_bat = z_tsr_press - z_tsr_over

    # 3. Dual-Axis Composite Score (70% Absolute High-Pressure + 30% Clutch Delta)
    s_raw = 0.70 * hp_bat + 0.30 * delta_bat

    # 4. Empirical Bayes Shrinkage toward population mean mu_0
    mu_0 = float(s_raw.mean()) if not s_raw.empty else 0.0
    denom = (n_eff + prior_m).replace(0.0, 1.0)
    w_sample = n_eff / denom
    w_prior = prior_m / denom
    s_final = w_sample * s_raw + w_prior * mu_0

    df["hp_index"] = hp_bat
    df["delta_score"] = delta_bat
    df["raw_score"] = s_raw
    df["shrinkage_weight"] = w_sample
    df["composite_score"] = s_final

    # 5. Role and Volume Eligibility Filters
    has_pos = "primary_batting_pos" in df.columns
    has_top7 = "top7_appearance_pct" in df.columns or "top7_pct" in df.columns
    top7_col = "top7_appearance_pct" if "top7_appearance_pct" in df.columns else "top7_pct"

    if has_pos and has_top7:
        role_mask = (df["primary_batting_pos"].fillna(4).astype(float) <= 7) | (
            df[top7_col].fillna(0.0).astype(float) >= 0.50
        )
    elif has_pos:
        role_mask = df["primary_batting_pos"].fillna(4).astype(float) <= 7
    elif has_top7:
        role_mask = df[top7_col].fillna(0.0).astype(float) >= 0.50
    else:
        role_mask = pd.Series(True, index=df.index)

    volume_mask = n_eff >= min_pressure_balls
    eligible = df[role_mask & volume_mask].copy()

    # Sort descending by composite score, breaking ties by TSR pressure and n_eff
    sort_cols = ["composite_score"]
    ascending_order = [False]
    if "tsr_pressure" in eligible.columns:
        sort_cols.append("tsr_pressure")
        ascending_order.append(False)
    if "n_eff_pressure" in eligible.columns:
        sort_cols.append("n_eff_pressure")
        ascending_order.append(False)

    ranked = eligible.sort_values(by=sort_cols, ascending=ascending_order).head(top_n).copy()
    ranked["rank"] = range(1, len(ranked) + 1)

    # Reorder columns: rank, player_id, player_name, composite_score, followed by remaining
    priority_cols = ["rank"]
    for c in ["player_id", "player_name", "composite_score", "raw_score", "hp_index", "delta_score", "n_eff_pressure"]:
        if c in ranked.columns and c not in priority_cols:
            priority_cols.append(c)
    other_cols = [c for c in ranked.columns if c not in priority_cols]
    final_cols = priority_cols + other_cols

    return ranked[final_cols].reset_index(drop=True)


def compute_bowling_rankings(
    df_bowlers: pd.DataFrame,
    min_pressure_balls: int = 75,
    prior_m: float = 30.0,
    top_n: int = 10,
) -> pd.DataFrame:
    """Computes dual-axis composite pressure score and rankings for bowlers.

    Formula:
      HP_Bowl = 0.45 * z(TER_Pressure) + 0.35 * z(HL_Wickets_Pressure) + 0.20 * z(DotPct_Pressure)
      Delta_Bowl = z(TER_Pressure) - z(TER_Overall)
      S_raw = 0.70 * HP_Bowl + 0.30 * Delta_Bowl
      S_final = (N_eff / (N_eff + M)) * S_raw + (M / (N_eff + M)) * mu_0

    Parameters
    ----------
    df_bowlers : pd.DataFrame
        Bowlers metrics DataFrame containing TER, HL wickets, dot%, and volume.
    min_pressure_balls : int, default 75
        Minimum effective pressure deliveries required to qualify.
    prior_m : float, default 30.0
        Empirical Bayes prior sample size weight.
    top_n : int, default 10
        Number of top-ranked players to return.

    Returns
    -------
    pd.DataFrame
        Ranked qualifying bowlers with composite score, component scores, and rank.
    """
    base_cols = [
        "rank",
        "player_id",
        "player_name",
        "composite_score",
        "raw_score",
        "hp_index",
        "delta_score",
        "shrinkage_weight",
    ]
    if df_bowlers.empty:
        return pd.DataFrame(columns=base_cols)

    df = df_bowlers.copy()

    # Column name resolution with graceful fallbacks
    ter_press = df.get("ter_pressure", pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    ter_over = df.get("ter_overall", ter_press).fillna(0.0).astype(float)
    hl_wkts = (
        df.get(
            "hl_wickets_pressure",
            df.get("hl_wickets", pd.Series(0.0, index=df.index)),
        )
        .fillna(0.0)
        .astype(float)
    )
    dot_pct = (
        df.get(
            "dot_pct_pressure",
            df.get("dot_pct", pd.Series(0.0, index=df.index)),
        )
        .fillna(0.0)
        .astype(float)
    )
    n_eff = (
        df.get("n_eff_pressure", df.get("n_balls_pressure", pd.Series(0.0, index=df.index)))
        .fillna(0.0)
        .astype(float)
    )

    # 1. Z-Score Standardization
    z_ter_press = _standardize(ter_press)
    z_ter_over = _standardize(ter_over)
    z_hl_wkts = _standardize(hl_wkts)
    z_dot_pct = _standardize(dot_pct)

    # 2. High-Pressure Index & Baseline Delta
    hp_bowl = 0.45 * z_ter_press + 0.35 * z_hl_wkts + 0.20 * z_dot_pct
    delta_bowl = z_ter_press - z_ter_over

    # 3. Dual-Axis Composite Score (70% Absolute High-Pressure + 30% Clutch Delta)
    s_raw = 0.70 * hp_bowl + 0.30 * delta_bowl

    # 4. Empirical Bayes Shrinkage toward population mean mu_0
    mu_0 = float(s_raw.mean()) if not s_raw.empty else 0.0
    denom = (n_eff + prior_m).replace(0.0, 1.0)
    w_sample = n_eff / denom
    w_prior = prior_m / denom
    s_final = w_sample * s_raw + w_prior * mu_0

    df["hp_index"] = hp_bowl
    df["delta_score"] = delta_bowl
    df["raw_score"] = s_raw
    df["shrinkage_weight"] = w_sample
    df["composite_score"] = s_final

    # 5. Role and Volume Eligibility Filters
    if "avg_overs_per_match" in df.columns:
        role_mask = df["avg_overs_per_match"].fillna(0.0).astype(float) >= 1.5
    else:
        role_mask = pd.Series(True, index=df.index)

    volume_mask = n_eff >= min_pressure_balls
    eligible = df[role_mask & volume_mask].copy()

    # Sort descending by composite score, breaking ties by TER pressure and n_eff
    sort_cols = ["composite_score"]
    ascending_order = [False]
    if "ter_pressure" in eligible.columns:
        sort_cols.append("ter_pressure")
        ascending_order.append(False)
    if "n_eff_pressure" in eligible.columns:
        sort_cols.append("n_eff_pressure")
        ascending_order.append(False)

    ranked = eligible.sort_values(by=sort_cols, ascending=ascending_order).head(top_n).copy()
    ranked["rank"] = range(1, len(ranked) + 1)

    # Reorder columns: rank, player_id, player_name, composite_score, followed by remaining
    priority_cols = ["rank"]
    for c in ["player_id", "player_name", "composite_score", "raw_score", "hp_index", "delta_score", "n_eff_pressure"]:
        if c in ranked.columns and c not in priority_cols:
            priority_cols.append(c)
    other_cols = [c for c in ranked.columns if c not in priority_cols]
    final_cols = priority_cols + other_cols

    return ranked[final_cols].reset_index(drop=True)


def compute_rankings(
    df_batters: pd.DataFrame,
    df_bowlers: pd.DataFrame,
    min_pressure_balls: int = 75,
    prior_m: float = 30.0,
    top_n: int = 10,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Computes Top 10 Batters and Top 10 Bowlers rankings under high pressure.

    Executes dual-axis composite scoring (HP index + clutch delta), Empirical
    Bayes shrinkage, role-based sanity filtering, and volume qualification.

    Parameters
    ----------
    df_batters : pd.DataFrame
        Batters raw metrics table.
    df_bowlers : pd.DataFrame
        Bowlers raw metrics table.
    min_pressure_balls : int, default 75
        Effective pressure delivery eligibility threshold (N_eff >= 75).
    prior_m : float, default 30.0
        Empirical Bayes shrinkage strength parameter.
    top_n : int, default 10
        Number of top performers to select for each discipline.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        df_top_batters, df_top_bowlers ranked 1 to 10 with composite scores.
    """
    df_top_batters = compute_batting_rankings(
        df_batters,
        min_pressure_balls=min_pressure_balls,
        prior_m=prior_m,
        top_n=top_n,
    )
    df_top_bowlers = compute_bowling_rankings(
        df_bowlers,
        min_pressure_balls=min_pressure_balls,
        prior_m=prior_m,
        top_n=top_n,
    )
    return df_top_batters, df_top_bowlers
