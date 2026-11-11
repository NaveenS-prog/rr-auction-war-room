"""Win Probability Modeling & Leverage Index (LI) Engine for RR SupeRR Selector.

Unified two-innings analytical engine:
1. Innings 1: Calibrated regression model predicting projected final total score
   from (balls_remaining_innings, cum_wickets_innings, cum_runs_innings), converted
   to win expectancy via logistic CDF against historical venue par distribution.
2. Innings 2: Calibrated logistic classifier predicting chase victory from
   (runs_required, balls_remaining_innings, cum_wickets_innings, required_run_rate).
3. Ball-by-ball Win Probability Added (delta_wpa = P_t - P_{t-1}).
4. Leverage Index (LI = expected_swing / tournament_mean_swing) and high pressure
   classification (is_high_pressure = LI >= 1.50).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# T20 Cricket Anchor Points for Model Regularization and Cold-Start Safety
# Innings 1: [balls_remaining, cum_wickets, cum_runs] -> projected final score
INNINGS_1_ANCHORS = [
    [120, 0, 0, 168.0],
    [102, 1, 24, 165.0],
    [84, 1, 50, 166.0],
    [60, 2, 80, 165.0],
    [60, 5, 60, 135.0],
    [30, 3, 125, 172.0],
    [30, 7, 95, 130.0],
    [12, 4, 150, 175.0],
    [12, 8, 120, 135.0],
    [0, 5, 168, 168.0],
    [0, 10, 115, 115.0],
]

# Innings 2: [runs_required, balls_remaining, cum_wickets, required_run_rate] -> chase win (1/0)
INNINGS_2_ANCHORS = [
    [170, 120, 0, 8.50, 1],
    [170, 120, 0, 8.50, 0],
    [130, 90, 1, 8.67, 1],
    [130, 90, 4, 8.67, 0],
    [80, 60, 2, 8.00, 1],
    [95, 60, 5, 9.50, 0],
    [40, 30, 3, 8.00, 1],
    [50, 30, 6, 10.00, 0],
    [12, 12, 4, 6.00, 1],
    [24, 12, 7, 12.00, 0],
    [6, 6, 3, 6.00, 1],
    [18, 6, 7, 18.00, 0],
    [2, 6, 4, 2.00, 1],
    [25, 6, 8, 25.00, 0],
]

# Outcome transition probabilities for Leverage Index expected swing:
# Based on typical T20 historical distribution of ball outcomes
OUTCOME_PROBABILITIES: Dict[str, float] = {
    "dot": 0.35,
    "single": 0.40,
    "four": 0.12,
    "six": 0.06,
    "wicket": 0.07,
}

# Run increments for outcomes
OUTCOME_RUNS: Dict[str, int] = {
    "dot": 0,
    "single": 1,
    "four": 4,
    "six": 6,
    "wicket": 0,
}


def _get_batting_team_win_series(df: pd.DataFrame) -> pd.Series:
    """Helper to extract whether the batting team won for each delivery."""
    if "batting_team_id" in df.columns and "win_team_id" in df.columns:
        return (df["batting_team_id"] == df["win_team_id"]).astype(int)
    elif "away_team_id" in df.columns and "win_team_id" in df.columns:
        is_inn2 = df["innings"] == 2
        arr = np.where(
            is_inn2,
            (df["away_team_id"] == df["win_team_id"]).astype(int),
            (df["home_team_id"] == df["win_team_id"]).astype(int),
        )
        return pd.Series(arr, index=df.index, dtype=int)
    return pd.Series(0, index=df.index, dtype=int)


def _predict_inn1_win_prob(
    balls_rem: np.ndarray,
    cum_wkts: np.ndarray,
    cum_runs: np.ndarray,
    venue_keys: Optional[pd.Series],
    models: Dict[str, Any],
) -> np.ndarray:
    """Predicts Innings 1 batting team win probability."""
    reg1 = models["inn1_model"]
    v_stats = models["inn1_venue_stats"]
    global_mu, global_scale = v_stats["global"]
    venue_map = v_stats.get("venues", {})

    X = np.column_stack([balls_rem, cum_wkts, cum_runs])
    projected_final = reg1.predict(X)

    # Physical cricket bounds: cannot project less than currently scored
    projected_final = np.maximum(cum_runs, projected_final)
    # If all out or no balls left, score is final
    terminal_mask = (cum_wkts >= 10) | (balls_rem <= 0)
    projected_final[terminal_mask] = cum_runs[terminal_mask]

    # Venue par location and scale lookup
    mu_arr = np.full(len(balls_rem), global_mu, dtype=float)
    scale_arr = np.full(len(balls_rem), global_scale, dtype=float)

    if venue_keys is not None:
        v_keys_list = venue_keys.tolist() if isinstance(venue_keys, pd.Series) else list(venue_keys)
        for i, vk in enumerate(v_keys_list):
            if vk in venue_map:
                m, s = venue_map[vk]
                mu_arr[i] = m
                scale_arr[i] = s

    # Logistic CDF: P = 1 / (1 + exp(-(proj - mu) / scale))
    z = (projected_final - mu_arr) / scale_arr
    z_clipped = np.clip(z, -30.0, 30.0)
    win_prob = 1.0 / (1.0 + np.exp(-z_clipped))

    # Review Focus 2: Innings 1 leverage bounds in [0.01, 0.99]
    return np.clip(win_prob, 0.01, 0.99)


def _predict_inn2_win_prob(
    runs_req: np.ndarray,
    balls_rem: np.ndarray,
    cum_wkts: np.ndarray,
    rrr: np.ndarray,
    models: Dict[str, Any],
) -> np.ndarray:
    """Predicts Innings 2 chasing team win probability."""
    pipe2 = models["inn2_model"]
    X = np.column_stack([runs_req, balls_rem, cum_wkts, rrr])
    probs = pipe2.predict_proba(X)[:, 1]

    # Boundary conditions
    # 1. Target reached / chase completed
    won_mask = runs_req <= 0
    probs[won_mask] = 0.99

    # 2. All out before target reached
    all_out_mask = (cum_wkts >= 10) & (runs_req > 0)
    probs[all_out_mask] = 0.01

    # 3. Balls exhausted before target reached
    exhausted_mask = (balls_rem <= 0) & (runs_req > 0)
    probs[exhausted_mask] = 0.01

    return np.clip(probs, 0.01, 0.99)


def _predict_all_win_prob(
    df: pd.DataFrame, models: Dict[str, Any]
) -> np.ndarray:
    """Computes win probability for every delivery in df."""
    n = len(df)
    if n == 0:
        return np.array([], dtype=float)

    win_prob = np.full(n, 0.50, dtype=float)

    venue_key_col = None
    if "venue_id" in df.columns:
        venue_key_col = "venue_id"
    elif "venue_country" in df.columns:
        venue_key_col = "venue_country"
    v_keys = df[venue_key_col] if venue_key_col else None

    inn = df["innings"].to_numpy()
    inn1_mask = inn == 1
    inn2_mask = inn >= 2

    # 1. Innings 1 Win Probability
    if np.any(inn1_mask):
        idx1 = np.where(inn1_mask)[0]
        b_rem1 = df["balls_remaining_innings"].iloc[idx1].to_numpy()
        c_wkt1 = df["cum_wickets_innings"].iloc[idx1].to_numpy()
        c_run1 = df["cum_runs_innings"].iloc[idx1].to_numpy()
        v_keys1 = v_keys.iloc[idx1] if v_keys is not None else None

        win_prob[idx1] = _predict_inn1_win_prob(b_rem1, c_wkt1, c_run1, v_keys1, models)

    # 2. Innings 2 Win Probability
    if np.any(inn2_mask):
        idx2 = np.where(inn2_mask)[0]
        r_req2 = df["runs_required"].iloc[idx2].to_numpy()
        b_rem2 = df["balls_remaining_innings"].iloc[idx2].to_numpy()
        c_wkt2 = df["cum_wickets_innings"].iloc[idx2].to_numpy()
        rrr2 = df["required_run_rate"].iloc[idx2].to_numpy()

        win_prob[idx2] = _predict_inn2_win_prob(r_req2, b_rem2, c_wkt2, rrr2, models)

    return win_prob


def _compute_expected_swings(
    df: pd.DataFrame, models: Dict[str, Any]
) -> pd.Series:
    """Computes delivery-level expected win probability swing E[|Delta WPA(S_t)|]."""
    n = len(df)
    if n == 0:
        return pd.Series([], dtype=float)

    # Identify venue key column
    venue_key_col = None
    if "venue_id" in df.columns:
        venue_key_col = "venue_id"
    elif "venue_country" in df.columns:
        venue_key_col = "venue_country"

    v_keys = df[venue_key_col] if venue_key_col else None

    # Determine pre-delivery state within (match_id, innings)
    grp = df.groupby(["match_id", "innings"])

    # Balls remaining before delivery
    balls_rem_pre = grp["balls_remaining_innings"].shift(1)
    balls_rem_pre = balls_rem_pre.fillna(df["balls_remaining_innings"] + 1).to_numpy()

    # Cumulative wickets before delivery
    cum_wkts_pre = grp["cum_wickets_innings"].shift(1).fillna(0).to_numpy()

    # Cumulative runs before delivery
    cum_runs_pre = grp["cum_runs_innings"].shift(1).fillna(0).to_numpy()

    # Runs required before delivery
    runs_req_pre = grp["runs_required"].shift(1)
    runs_req_pre = runs_req_pre.fillna(df["target_runs"]).to_numpy()

    # Win prob before delivery
    win_prob_pre = grp["win_prob"].shift(1).fillna(0.50).to_numpy() if "win_prob" in df.columns else np.full(n, 0.50)

    inn = df["innings"].to_numpy()
    inn1_mask = inn == 1
    inn2_mask = inn >= 2

    expected_swing = np.zeros(n, dtype=float)

    # Evaluate counterfactual outcomes: dot, single, four, six, wicket
    for outcome, prob in OUTCOME_PROBABILITIES.items():
        run_add = OUTCOME_RUNS[outcome]
        wkt_add = 1 if outcome == "wicket" else 0

        # Innings 1 counterfactuals
        if np.any(inn1_mask):
            idx1 = np.where(inn1_mask)[0]
            b_cf1 = np.maximum(0, balls_rem_pre[idx1] - 1)
            w_cf1 = np.minimum(10, cum_wkts_pre[idx1] + wkt_add)
            r_cf1 = cum_runs_pre[idx1] + run_add
            v_keys1 = v_keys.iloc[idx1] if v_keys is not None else None

            p_cf1 = _predict_inn1_win_prob(b_cf1, w_cf1, r_cf1, v_keys1, models)
            swing1 = np.abs(p_cf1 - win_prob_pre[idx1])
            expected_swing[idx1] += prob * swing1

        # Innings 2 counterfactuals
        if np.any(inn2_mask):
            idx2 = np.where(inn2_mask)[0]
            b_cf2 = np.maximum(0, balls_rem_pre[idx2] - 1)
            w_cf2 = np.minimum(10, cum_wkts_pre[idx2] + wkt_add)
            req_cf2 = np.maximum(0, runs_req_pre[idx2] - run_add)

            b_safe = np.maximum(1, b_cf2)
            rrr_calc = (req_cf2 / b_safe) * 6.0
            rrr_cf2 = np.where(
                b_cf2 > 0,
                rrr_calc,
                np.where(req_cf2 > 0, 99.0, 0.0),
            )

            p_cf2 = _predict_inn2_win_prob(req_cf2, b_cf2, w_cf2, rrr_cf2, models)
            swing2 = np.abs(p_cf2 - win_prob_pre[idx2])
            expected_swing[idx2] += prob * swing2

    return pd.Series(expected_swing, index=df.index, dtype=float)


def train_win_prob_models(df: pd.DataFrame) -> Dict[str, Any]:
    """Trains Innings 1 and Innings 2 win probability models.

    Parameters
    ----------
    df : pd.DataFrame
        Delivery-level DataFrame enriched by `data_loader`.

    Returns
    -------
    Dict[str, Any]
        Dictionary holding trained models, venue statistics, and baseline swing.
    """
    # -------------------------------------------------------------
    # 1. Innings 1 Model: Final Score Regressor & Venue Par Fitting
    # -------------------------------------------------------------
    df_inn1 = df[df["innings"] == 1].copy() if not df.empty else pd.DataFrame()

    anchors_inn1_arr = np.array(INNINGS_1_ANCHORS, dtype=float)
    X1_anchors = anchors_inn1_arr[:, :3]
    y1_anchors = anchors_inn1_arr[:, 3]

    use_anchors_only = True
    match_finals = pd.Series(dtype=float)

    if not df_inn1.empty and "cum_runs_innings" in df_inn1.columns:
        match_stats = df_inn1.groupby("match_id").agg(
            max_runs=("cum_runs_innings", "max"),
            min_balls=("balls_remaining_innings", "min"),
            max_wkts=("cum_wickets_innings", "max"),
            ball_count=("balls_remaining_innings", "count"),
        )
        # Completed matches only
        completed = match_stats[
            (match_stats["max_runs"] >= 60)
            | (match_stats["min_balls"] <= 10)
            | (match_stats["max_wkts"] >= 10)
            | (match_stats["ball_count"] >= 60)
        ]

        if not completed.empty:
            match_finals = completed["max_runs"]
            df_completed = df_inn1[df_inn1["match_id"].isin(completed.index)].copy()
            df_completed["final_score"] = df_completed["match_id"].map(match_finals)

            features_inn1 = [
                "balls_remaining_innings",
                "cum_wickets_innings",
                "cum_runs_innings",
            ]
            if all(f in df_completed.columns for f in features_inn1):
                X1_real = df_completed[features_inn1].fillna(0).to_numpy()
                y1_real = df_completed["final_score"].to_numpy()

                if len(completed) < 5 or y1_real.std() < 5.0:
                    X1 = np.vstack([X1_real, X1_anchors])
                    y1 = np.concatenate([y1_real, y1_anchors])
                else:
                    X1 = X1_real
                    y1 = y1_real
                use_anchors_only = False

    if use_anchors_only:
        X1 = X1_anchors
        y1 = y1_anchors

    reg1 = Ridge(alpha=5.0)
    reg1.fit(X1, y1)

    # Historical Venue Par Distribution (mean and std of 1st innings total scores)
    venue_map: Dict[Any, Tuple[float, float]] = {}
    if not match_finals.empty:
        global_mean = float(match_finals.mean())
        global_std = float(match_finals.std()) if len(match_finals) > 1 else 22.0
        if np.isnan(global_mean) or global_mean < 80.0:
            global_mean = 168.0
        if np.isnan(global_std) or global_std < 5.0:
            global_std = 22.0

        venue_col = None
        if "venue_id" in df_inn1.columns:
            venue_col = "venue_id"
        elif "venue_country" in df_inn1.columns:
            venue_col = "venue_country"

        if venue_col:
            v_matches = (
                df_inn1[["match_id", venue_col]]
                .drop_duplicates()
                .merge(match_finals.rename("total_runs"), on="match_id", how="inner")
            )
            v_stats = (
                v_matches.groupby(venue_col)["total_runs"]
                .agg(["mean", "std", "count"])
                .reset_index()
            )
            for _, vrow in v_stats.iterrows():
                v_id = vrow[venue_col]
                v_cnt = vrow["count"]
                v_m = float(vrow["mean"]) if v_cnt >= 3 and not np.isnan(vrow["mean"]) else global_mean
                v_s = float(vrow["std"]) if v_cnt >= 3 and not np.isnan(vrow["std"]) and vrow["std"] >= 5.0 else global_std
                v_scale = max(10.0, v_s * np.sqrt(3.0) / np.pi)
                venue_map[v_id] = (v_m, v_scale)
    else:
        global_mean = 168.0
        global_std = 22.0

    global_scale = max(10.0, global_std * np.sqrt(3.0) / np.pi)

    # -------------------------------------------------------------
    # 2. Innings 2 Model: Calibrated Chase Victory Classifier
    # -------------------------------------------------------------
    df_inn2 = df[df["innings"] == 2].copy() if not df.empty else pd.DataFrame()

    anchors_inn2_arr = np.array(INNINGS_2_ANCHORS, dtype=float)
    X2_anchors = anchors_inn2_arr[:, :4]
    y2_anchors = anchors_inn2_arr[:, 4]

    features_inn2 = [
        "runs_required",
        "balls_remaining_innings",
        "cum_wickets_innings",
        "required_run_rate",
    ]

    pipe2 = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs")),
    ])

    if not df_inn2.empty and all(c in df_inn2.columns for c in features_inn2):
        y2_real = _get_batting_team_win_series(df_inn2).to_numpy()
        X2_real = df_inn2[features_inn2].fillna(0).to_numpy()

        # If single class or small dataset, blend with anchors
        if len(np.unique(y2_real)) < 2 or len(df_inn2) < 50:
            X2 = np.vstack([X2_real, X2_anchors])
            y2 = np.concatenate([y2_real, y2_anchors])
        else:
            X2 = X2_real
            y2 = y2_real
    else:
        X2 = X2_anchors
        y2 = y2_anchors

    pipe2.fit(X2, y2)

    # Baseline tournament average swing for Leverage Index scaling
    mean_swing = 0.045

    models = {
        "inn1_model": reg1,
        "inn1_venue_stats": {
            "global": (global_mean, global_scale),
            "venues": venue_map,
        },
        "inn2_model": pipe2,
        "mean_swing": mean_swing,
    }

    # Calibrate mean_swing on training data if available
    if not df.empty and len(df) >= 20:
        sample_df = df.head(min(5000, len(df))).copy()
        sample_df["win_prob"] = _predict_all_win_prob(sample_df, models)
        swings = _compute_expected_swings(sample_df, models)
        m_swing = float(swings.mean())
        if not np.isnan(m_swing) and m_swing > 0.005:
            models["mean_swing"] = m_swing

    return models


def compute_win_probability_and_leverage(
    df: pd.DataFrame, models: Dict[str, Any]
) -> pd.DataFrame:
    """Computes delivery-level win probability, Delta WPA, and Leverage Index.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched deliveries DataFrame.
    models : Dict[str, Any]
        Dictionary returned by `train_win_prob_models`.

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns:
        - `win_prob`: Batting team's estimated win probability in [0.01, 0.99].
        - `delta_wpa`: Delivery swing = P_t - P_{t-1}.
        - `leverage_index`: Ratio of expected swing to tournament mean swing.
        - `is_high_pressure`: Boolean flag True if leverage_index >= 1.50.
    """
    res = df.copy()

    if res.empty:
        res["win_prob"] = pd.Series([], dtype=float)
        res["delta_wpa"] = pd.Series([], dtype=float)
        res["leverage_index"] = pd.Series([], dtype=float)
        res["is_high_pressure"] = pd.Series([], dtype=bool)
        return res

    # 1. Compute Win Probability for all deliveries
    res["win_prob"] = _predict_all_win_prob(res, models)

    # 2. Delivery Outcome Win Probability Added (Delta WPA)
    # Group by (match_id, innings) to prevent cross-match/cross-innings leakage
    grp = res.groupby(["match_id", "innings"])
    win_prob_prev = grp["win_prob"].shift(1).fillna(0.50)
    res["delta_wpa"] = res["win_prob"] - win_prob_prev

    # 3. Leverage Index (LI)
    expected_swing = _compute_expected_swings(res, models)
    mean_swing = models.get("mean_swing", 0.045)
    if mean_swing is None or mean_swing <= 1e-6:
        mean_swing = float(expected_swing.mean())
        if np.isnan(mean_swing) or mean_swing <= 1e-6:
            mean_swing = 1.0

    res["leverage_index"] = np.maximum(0.0, expected_swing / mean_swing)
    res["is_high_pressure"] = res["leverage_index"] >= 1.50

    return res
