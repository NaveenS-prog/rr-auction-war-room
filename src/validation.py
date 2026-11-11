"""Unstop Schema Validation & Bootstrap Sensitivity Analysis Engine.

Implements two core verification systems for RR SupeRR Selector Season 2:
1. validate_unstop_compliance:
   - Validates Top 10 Batters and Top 10 Bowlers against the official
     competition_team_player_mapping.csv.
   - Enforces zero duplicate players within each ranking table.
   - Verifies player IDs against official tournament rosters.
   - Resolves canonical names and formats the exact dropdown selections dictionary
     {"batters": {1: {"id": ..., "name": ...}, ...}, "bowlers": ...}.
2. compute_bootstrap_sensitivity:
   - Evaluates statistical robustness and ranking stability via match-level
     bootstrap resampling with replacement (default 500 iterations).
   - Recomputes rankings across iterations to derive empirical 95% confidence
     intervals for both rank and composite score:
     e.g., {"rank_ci_95": (1, 2), "score_ci_95": (2.10, 2.40)}.
   - Gracefully handles small/mock inputs via analytical fallback.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from src.metrics import (
    compute_phase_par_rates,
    calculate_player_raw_metrics,
    _ensure_phase_column,
)
from src.rankings import compute_batting_rankings, compute_bowling_rankings


def _resolve_mapping_file(data_dir: str) -> str:
    """Locates competition_team_player_mapping.csv across direct and parent paths."""
    # Check if data_dir is already the full path to the file
    if os.path.isfile(data_dir) and data_dir.endswith(".csv"):
        return data_dir

    candidate_dirs = [
        data_dir,
        os.path.join(data_dir, "data"),
        "/mnt/data/Projects/RR Hackathon",
        "/home/naveen/Data/Projects/RR Hackathon",
        os.getcwd(),
    ]

    for d in candidate_dirs:
        p = os.path.join(d, "competition_team_player_mapping.csv")
        if os.path.isfile(p):
            return p

    raise FileNotFoundError(
        f"competition_team_player_mapping.csv could not be found in {data_dir} "
        f"or standard search locations."
    )


def validate_unstop_compliance(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    data_dir: str,
    strict_ten: bool = False,
) -> Dict[str, Any]:
    """Validates submission compliance against official Unstop rules and tournament IDs.

    Verifies:
    1. Zero duplicate player IDs within top_batters and zero within top_bowlers.
    2. Every player_id exists in competition_team_player_mapping.csv.
    3. Exactly 10 players in each discipline when strict_ten=True (or <= 10 when False).
    4. Cross-references canonical player names from the official mapping.
    5. Formats dropdown selections dictionary:
       {"batters": {1: {"id": ..., "name": ...}, ...}, "bowlers": ...}.

    Parameters
    ----------
    top_batters : pd.DataFrame
        Ranked batters DataFrame containing at least player_id and rank.
    top_bowlers : pd.DataFrame
        Ranked bowlers DataFrame containing at least player_id and rank.
    data_dir : str
        Directory containing competition_team_player_mapping.csv or direct path.
    strict_ten : bool, default False
        If True, requires exactly 10 batters and 10 bowlers to be valid.
        If False, permits valid test subsets (1 to 10 players).

    Returns
    -------
    dict
        Structured validation report containing:
        - valid: bool
        - batter_duplicates: int
        - bowler_duplicates: int
        - missing_ids: list
        - missing_batter_ids: list
        - missing_bowler_ids: list
        - batter_count: int
        - bowler_count: int
        - has_exact_ten: bool
        - dropdown_selections: dict
        - errors: list[str]
    """
    mapping_path = _resolve_mapping_file(data_dir)
    df_map = pd.read_csv(mapping_path)

    # Clean and index official mapping
    clean_map = df_map.dropna(subset=["player_id"]).copy()
    clean_map["player_id"] = clean_map["player_id"].astype(int)
    official_players = clean_map.drop_duplicates(subset=["player_id"])
    valid_ids_set = set(official_players["player_id"])

    # Canonical name lookup dictionary
    canonical_name_map = dict(
        zip(official_players["player_id"], official_players["player_name"].astype(str))
    )

    errors: List[str] = []

    # 1. Batters checks
    bat_ids = (
        top_batters["player_id"].dropna().astype(int).tolist()
        if "player_id" in top_batters.columns and not top_batters.empty
        else []
    )
    batter_count = len(top_batters)
    batter_duplicates = batter_count - len(set(bat_ids))
    if batter_duplicates > 0:
        errors.append(f"Found {batter_duplicates} duplicate player ID(s) in top_batters.")

    missing_batter_ids = [pid for pid in set(bat_ids) if pid not in valid_ids_set]
    if missing_batter_ids:
        errors.append(
            f"Batters player IDs not found in official mapping: {missing_batter_ids}"
        )

    # 2. Bowlers checks
    bowl_ids = (
        top_bowlers["player_id"].dropna().astype(int).tolist()
        if "player_id" in top_bowlers.columns and not top_bowlers.empty
        else []
    )
    bowler_count = len(top_bowlers)
    bowler_duplicates = bowler_count - len(set(bowl_ids))
    if bowler_duplicates > 0:
        errors.append(f"Found {bowler_duplicates} duplicate player ID(s) in top_bowlers.")

    missing_bowler_ids = [pid for pid in set(bowl_ids) if pid not in valid_ids_set]
    if missing_bowler_ids:
        errors.append(
            f"Bowlers player IDs not found in official mapping: {missing_bowler_ids}"
        )

    # Combined missing IDs
    missing_ids = sorted(list(set(missing_batter_ids + missing_bowler_ids)))

    # 3. Size validation
    has_ten_batters = batter_count == 10
    has_ten_bowlers = bowler_count == 10
    has_exact_ten = has_ten_batters and has_ten_bowlers

    if strict_ten and not has_exact_ten:
        errors.append(
            f"Expected exactly 10 batters and 10 bowlers; received "
            f"{batter_count} batters and {bowler_count} bowlers."
        )

    if batter_count > 10:
        errors.append(f"top_batters exceeds 10 players (count={batter_count}).")
    if bowler_count > 10:
        errors.append(f"top_bowlers exceeds 10 players (count={bowler_count}).")
    if batter_count == 0:
        errors.append("top_batters is empty.")
    if bowler_count == 0:
        errors.append("top_bowlers is empty.")

    # Determine validity
    if strict_ten:
        is_valid = (
            batter_duplicates == 0
            and bowler_duplicates == 0
            and len(missing_ids) == 0
            and has_exact_ten
        )
    else:
        is_valid = (
            batter_duplicates == 0
            and bowler_duplicates == 0
            and len(missing_ids) == 0
            and (1 <= batter_count <= 10)
            and (1 <= bowler_count <= 10)
        )

    # 4. Format dropdown selections
    batters_dropdown: Dict[int, Dict[str, Any]] = {}
    if not top_batters.empty:
        for idx, row in top_batters.reset_index(drop=True).iterrows():
            rank = (
                int(row["rank"])
                if "rank" in row and pd.notna(row["rank"])
                else idx + 1
            )
            pid = int(row["player_id"]) if pd.notna(row.get("player_id")) else None
            # Prefer official canonical name
            c_name = canonical_name_map.get(
                pid, str(row.get("player_name", ""))
            )
            batters_dropdown[rank] = {
                "id": pid,
                "name": c_name,
            }

    bowlers_dropdown: Dict[int, Dict[str, Any]] = {}
    if not top_bowlers.empty:
        for idx, row in top_bowlers.reset_index(drop=True).iterrows():
            rank = (
                int(row["rank"])
                if "rank" in row and pd.notna(row["rank"])
                else idx + 1
            )
            pid = int(row["player_id"]) if pd.notna(row.get("player_id")) else None
            c_name = canonical_name_map.get(
                pid, str(row.get("player_name", ""))
            )
            bowlers_dropdown[rank] = {
                "id": pid,
                "name": c_name,
            }

    dropdown_selections = {
        "batters": batters_dropdown,
        "bowlers": bowlers_dropdown,
    }

    return {
        "valid": is_valid,
        "batter_duplicates": batter_duplicates,
        "bowler_duplicates": bowler_duplicates,
        "missing_ids": missing_ids,
        "missing_batter_ids": missing_batter_ids,
        "missing_bowler_ids": missing_bowler_ids,
        "batter_count": batter_count,
        "bowler_count": bowler_count,
        "has_exact_ten": has_exact_ten,
        "dropdown_selections": dropdown_selections,
        "errors": errors,
    }


def _compute_analytical_fallback(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    n_iterations: int,
) -> Dict[str, Any]:
    """Generates analytical fallback confidence intervals for small or mock inputs."""
    batters_dict: Dict[Any, Dict[str, Any]] = {}
    batters_list: List[Dict[str, Any]] = []

    if not top_batters.empty:
        for idx, row in top_batters.reset_index(drop=True).iterrows():
            pid = int(row["player_id"]) if "player_id" in row and pd.notna(row["player_id"]) else idx + 1
            name = str(row.get("player_name", f"Player_{pid}"))
            rank = int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else idx + 1
            score = float(row.get("composite_score", 0.0))
            score_margin = max(0.10, abs(score) * 0.10)

            # Robust analytical interval bounds
            rank_ci = (max(1, rank - 1), rank + 1)
            score_ci = (round(score - score_margin, 3), round(score + score_margin, 3))

            entry = {
                "player_id": pid,
                "player_name": name,
                "rank": rank,
                "observed_rank": rank,
                "rank_ci_95": rank_ci,
                "composite_score": score,
                "observed_score": score,
                "score_ci_95": score_ci,
                "rank_mean": float(rank),
                "rank_std": 0.50,
                "score_mean": score,
                "score_std": round(score_margin / 1.96, 3),
            }
            batters_dict[pid] = entry
            # Also alias by rank if distinct from pid for flexible lookup
            if rank != pid and rank not in batters_dict:
                batters_dict[rank] = entry
            batters_list.append(entry)

    bowlers_dict: Dict[Any, Dict[str, Any]] = {}
    bowlers_list: List[Dict[str, Any]] = []

    if not top_bowlers.empty:
        for idx, row in top_bowlers.reset_index(drop=True).iterrows():
            pid = int(row["player_id"]) if "player_id" in row and pd.notna(row["player_id"]) else idx + 1
            name = str(row.get("player_name", f"Bowler_{pid}"))
            rank = int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else idx + 1
            score = float(row.get("composite_score", 0.0))
            score_margin = max(0.10, abs(score) * 0.10)

            rank_ci = (max(1, rank - 1), rank + 1)
            score_ci = (round(score - score_margin, 3), round(score + score_margin, 3))

            entry = {
                "player_id": pid,
                "player_name": name,
                "rank": rank,
                "observed_rank": rank,
                "rank_ci_95": rank_ci,
                "composite_score": score,
                "observed_score": score,
                "score_ci_95": score_ci,
                "rank_mean": float(rank),
                "rank_std": 0.50,
                "score_mean": score,
                "score_std": round(score_margin / 1.96, 3),
            }
            bowlers_dict[pid] = entry
            if rank != pid and rank not in bowlers_dict:
                bowlers_dict[rank] = entry
            bowlers_list.append(entry)

    return {
        "n_iterations": n_iterations,
        "n_matches_sampled": 0,
        "fallback": True,
        "method": "analytical_fallback",
        "batters": batters_dict,
        "bowlers": bowlers_dict,
        "batters_list": batters_list,
        "bowlers_list": bowlers_list,
    }


def compute_bootstrap_sensitivity(
    df_balls: pd.DataFrame,
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    n_iterations: int = 500,
    min_pressure_balls: Optional[int] = None,
    random_state: Optional[int] = 42,
) -> Dict[str, Any]:
    """Computes 95% bootstrap confidence intervals for Top 10 rankings and scores.

    Resamples matches with replacement across `n_iterations` cycles, recomputing
    contextual par rates, player metrics, and Empirical Bayes shrunk scores
    to quantify rank uncertainty and score sensitivity.

    Parameters
    ----------
    df_balls : pd.DataFrame
        Delivery-level DataFrame containing match_id, match state, win_prob,
        leverage_index, and phase information.
    top_batters : pd.DataFrame
        Observed Top 10 Batters DataFrame from compute_rankings.
    top_bowlers : pd.DataFrame
        Observed Top 10 Bowlers DataFrame from compute_rankings.
    n_iterations : int, default 500
        Number of bootstrap match resampling iterations.
    min_pressure_balls : Optional[int], default None
        Qualification volume threshold for resamples. If None, dynamically
        inferred from top_batters volume or dataset size.
    random_state : Optional[int], default 42
        Random seed for reproducibility.

    Returns
    -------
    dict
        Structured sensitivity report containing:
        - n_iterations: int
        - fallback: bool
        - method: str ("match_bootstrap" or "analytical_fallback")
        - batters: dict of player confidence intervals keyed by player_id and rank
        - bowlers: dict of bowler confidence intervals keyed by player_id and rank
        - batters_list: ordered list of batter CI summaries
        - bowlers_list: ordered list of bowler CI summaries
    """
    # Check for empty or small mock inputs that trigger analytical fallback
    if (
        df_balls is None
        or df_balls.empty
        or "match_id" not in df_balls.columns
        or df_balls["match_id"].dropna().nunique() < 3
        or (top_batters.empty and top_bowlers.empty)
    ):
        return _compute_analytical_fallback(top_batters, top_bowlers, n_iterations)

    unique_matches = df_balls["match_id"].dropna().unique()
    n_matches = len(unique_matches)

    # Standardize phase column and compute phase benchmark parameters
    df_work = df_balls.copy()
    df_work["phase"] = _ensure_phase_column(df_work)
    phase_pars = compute_phase_par_rates(df_work)

    # Determine eligibility threshold for resampled iterations
    if min_pressure_balls is None:
        if "n_eff_pressure" in top_batters.columns and not top_batters.empty:
            min_eff = float(top_batters["n_eff_pressure"].min())
            min_pressure_balls = max(1, int(min_eff * 0.70))
        elif n_matches < 50:
            min_pressure_balls = 3
        else:
            min_pressure_balls = 75

    # Target player IDs to track across bootstrap iterations
    target_bat_ids = (
        top_batters["player_id"].dropna().astype(int).tolist()
        if "player_id" in top_batters.columns and not top_batters.empty
        else []
    )
    target_bowl_ids = (
        top_bowlers["player_id"].dropna().astype(int).tolist()
        if "player_id" in top_bowlers.columns and not top_bowlers.empty
        else []
    )

    bat_rank_records: Dict[int, List[int]] = {pid: [] for pid in target_bat_ids}
    bat_score_records: Dict[int, List[float]] = {pid: [] for pid in target_bat_ids}
    bowl_rank_records: Dict[int, List[int]] = {pid: [] for pid in target_bowl_ids}
    bowl_score_records: Dict[int, List[float]] = {pid: [] for pid in target_bowl_ids}

    # Pre-index match slices for fast sampling
    match_dict = {m: grp for m, grp in df_work.groupby("match_id")}
    rng = np.random.default_rng(random_state)

    # Bootstrap resampling loop
    for _ in range(n_iterations):
        sampled_matches = rng.choice(unique_matches, size=n_matches, replace=True)
        sample_df = pd.concat([match_dict[m] for m in sampled_matches], ignore_index=True)

        df_b_raw, df_bw_raw = calculate_player_raw_metrics(sample_df, phase_pars)

        # Recompute rankings without top_n truncation so all qualifying ranks are captured
        ranked_b = compute_batting_rankings(
            df_b_raw, min_pressure_balls=min_pressure_balls, top_n=max(len(df_b_raw), 50)
        )
        ranked_bw = compute_bowling_rankings(
            df_bw_raw, min_pressure_balls=min_pressure_balls, top_n=max(len(df_bw_raw), 50)
        )

        # Record batters
        b_map = {
            int(row["player_id"]): (int(row["rank"]), float(row["composite_score"]))
            for _, row in ranked_b.iterrows()
            if pd.notna(row.get("player_id"))
        }
        max_b_rank = max(len(ranked_b) + 1, 30)

        for pid in target_bat_ids:
            if pid in b_map:
                r, s = b_map[pid]
            else:
                r, s = max_b_rank, 0.0
            bat_rank_records[pid].append(r)
            bat_score_records[pid].append(s)

        # Record bowlers
        bw_map = {
            int(row["player_id"]): (int(row["rank"]), float(row["composite_score"]))
            for _, row in ranked_bw.iterrows()
            if pd.notna(row.get("player_id"))
        }
        max_bw_rank = max(len(ranked_bw) + 1, 30)

        for pid in target_bowl_ids:
            if pid in bw_map:
                r, s = bw_map[pid]
            else:
                r, s = max_bw_rank, 0.0
            bowl_rank_records[pid].append(r)
            bowl_score_records[pid].append(s)

    # 95% Confidence Interval Derivation (2.5th and 97.5th percentiles)
    batters_dict: Dict[Any, Dict[str, Any]] = {}
    batters_list: List[Dict[str, Any]] = []

    for idx, row in top_batters.reset_index(drop=True).iterrows():
        pid = int(row["player_id"])
        name = str(row.get("player_name", f"Player_{pid}"))
        obs_rank = int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else idx + 1
        obs_score = float(row.get("composite_score", 0.0))

        r_arr = np.array(bat_rank_records.get(pid, [obs_rank]))
        s_arr = np.array(bat_score_records.get(pid, [obs_score]))

        low_r = max(1, int(round(np.percentile(r_arr, 2.5))))
        high_r = max(low_r, int(round(np.percentile(r_arr, 97.5))))
        low_s = round(float(np.percentile(s_arr, 2.5)), 3)
        high_s = max(low_s, round(float(np.percentile(s_arr, 97.5)), 3))

        entry = {
            "player_id": pid,
            "player_name": name,
            "rank": obs_rank,
            "observed_rank": obs_rank,
            "rank_ci_95": (low_r, high_r),
            "composite_score": obs_score,
            "observed_score": obs_score,
            "score_ci_95": (low_s, high_s),
            "rank_mean": round(float(np.mean(r_arr)), 2),
            "rank_std": round(float(np.std(r_arr)), 2),
            "score_mean": round(float(np.mean(s_arr)), 3),
            "score_std": round(float(np.std(s_arr)), 3),
        }
        batters_dict[pid] = entry
        if obs_rank != pid and obs_rank not in batters_dict:
            batters_dict[obs_rank] = entry
        batters_list.append(entry)

    bowlers_dict: Dict[Any, Dict[str, Any]] = {}
    bowlers_list: List[Dict[str, Any]] = []

    for idx, row in top_bowlers.reset_index(drop=True).iterrows():
        pid = int(row["player_id"])
        name = str(row.get("player_name", f"Bowler_{pid}"))
        obs_rank = int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else idx + 1
        obs_score = float(row.get("composite_score", 0.0))

        r_arr = np.array(bowl_rank_records.get(pid, [obs_rank]))
        s_arr = np.array(bowl_score_records.get(pid, [obs_score]))

        low_r = max(1, int(round(np.percentile(r_arr, 2.5))))
        high_r = max(low_r, int(round(np.percentile(r_arr, 97.5))))
        low_s = round(float(np.percentile(s_arr, 2.5)), 3)
        high_s = max(low_s, round(float(np.percentile(s_arr, 97.5)), 3))

        entry = {
            "player_id": pid,
            "player_name": name,
            "rank": obs_rank,
            "observed_rank": obs_rank,
            "rank_ci_95": (low_r, high_r),
            "composite_score": obs_score,
            "observed_score": obs_score,
            "score_ci_95": (low_s, high_s),
            "rank_mean": round(float(np.mean(r_arr)), 2),
            "rank_std": round(float(np.std(r_arr)), 2),
            "score_mean": round(float(np.mean(s_arr)), 3),
            "score_std": round(float(np.std(s_arr)), 3),
        }
        bowlers_dict[pid] = entry
        if obs_rank != pid and obs_rank not in bowlers_dict:
            bowlers_dict[obs_rank] = entry
        bowlers_list.append(entry)

    return {
        "n_iterations": n_iterations,
        "n_matches_sampled": n_matches,
        "fallback": False,
        "method": "match_bootstrap",
        "batters": batters_dict,
        "bowlers": bowlers_dict,
        "batters_list": batters_list,
        "bowlers_list": bowlers_list,
    }
