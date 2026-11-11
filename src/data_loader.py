"""Data ingestion and match state reconstruction engine for RR SupeRR Selector.

Reconstructs ball-by-ball delivery states across 2022-2026 IPL and T20Is:
- Cumulative runs and wickets per innings, balls remaining.
- Overs phase (Powerplay: 1-6, Middle: 7-15, Death: 16-20).
- DLS / revised target and revised overs handling.
- Bowler runs conceded (excluding leg-byes, byes, penalty) and bowler wickets.
- Competition quality weights (IPL = 1.0, T20Is = 0.70 to 0.95).
"""

from __future__ import annotations

import os
from typing import Optional

import numpy as np
import pandas as pd

# Top-8 ICC Men's T20 teams for competition weighting
ICC_TOP_8 = {
    "India",
    "Australia",
    "England",
    "South Africa",
    "New Zealand",
    "Pakistan",
    "West Indies",
    "Sri Lanka",
}

# Dismissals that are NOT credited to the bowler
NON_BOWLER_DISMISSALS = {
    "runout",
    "run out",
    "retire out",
    "retired out",
    "retired hurt",
    "obstracting the field",
    "obstructing the field",
}


def compute_competition_weights(matches_df: pd.DataFrame, comps_df: pd.DataFrame) -> pd.DataFrame:
    """Assigns competition quality weights (W_comp) to matches.

    - IPL matches: 1.00
    - T20Is (Top-8 vs Top-8): 0.95
    - T20Is (Top-8 vs Associate): 0.85
    - T20Is (Associate vs Associate): 0.70
    """
    matches_merged = matches_df.merge(
        comps_df[["comp_id", "comp_name", "match_format"]],
        on="comp_id",
        how="left",
    )

    def _assign_weight(row: pd.Series) -> float:
        comp_name = str(row.get("comp_name", "")).upper()
        if "IPL" in comp_name or "INDIAN PREMIER LEAGUE" in comp_name:
            return 1.00

        home = str(row.get("home_team", ""))
        away = str(row.get("away_team", ""))
        home_top = home in ICC_TOP_8
        away_top = away in ICC_TOP_8

        if home_top and away_top:
            return 0.95
        elif home_top or away_top:
            return 0.85
        else:
            return 0.70

    matches_merged["comp_weight"] = matches_merged.apply(_assign_weight, axis=1)
    return matches_merged


def load_and_process_deliveries(
    data_dir: str, sample_matches: Optional[int] = None
) -> pd.DataFrame:
    """Loads CSV data and enriches ball-by-ball deliveries with reconstructed match state.

    Parameters
    ----------
    data_dir : str
        Path to directory containing competitions.csv, matches.csv, ball_by_ball.csv.
    sample_matches : Optional[int]
        If provided, limits processing to the first N matches for rapid testing.

    Returns
    -------
    pd.DataFrame
        Delivery-level DataFrame enriched with match state metrics.
    """
    comps_path = os.path.join(data_dir, "competitions.csv")
    matches_path = os.path.join(data_dir, "matches.csv")
    bbb_path = os.path.join(data_dir, "ball_by_ball.csv")

    comps_df = pd.read_csv(comps_path)
    matches_df = pd.read_csv(matches_path)

    # Filter sample matches if requested
    if sample_matches is not None and sample_matches > 0:
        sample_ids = matches_df["match_id"].unique()[:sample_matches]
        matches_df = matches_df[matches_df["match_id"].isin(sample_ids)].copy()

    # Calculate competition weights
    matches_enriched = compute_competition_weights(matches_df, comps_df)

    # Read ball-by-ball deliveries
    if sample_matches is not None and sample_matches > 0:
        # Filter during read or after
        bbb_df = pd.read_csv(bbb_path)
        bbb_df = bbb_df[bbb_df["match_id"].isin(matches_df["match_id"])].copy()
    else:
        bbb_df = pd.read_csv(bbb_path)

    if bbb_df.empty:
        return bbb_df

    # Standardize extras_type ("legbyes" -> "Leg-byes", etc.)
    extras_replace = {
        "legbyes": "Leg-byes",
        "byes": "Byes",
        "wide": "Wide",
    }
    bbb_df["extras_type"] = bbb_df["extras_type"].replace(extras_replace)

    # Calculate runs per delivery for batting team and bowler
    bat_runs = bbb_df["runs"].fillna(0).astype(int)
    extra_runs_2 = bbb_df["extras_2_runs"].fillna(0).astype(int)
    extras_type_clean = (
        bbb_df["extras_type"]
        .astype(str)
        .str.lower()
        .str.replace("-", "", regex=False)
        .str.replace(" ", "", regex=False)
    )

    # Identify extras categories
    is_wide = extras_type_clean == "wide"
    is_noball = extras_type_clean.isin(["overstep", "other", "noball"])
    is_legbye = extras_type_clean == "legbyes"
    is_bye = extras_type_clean == "byes"
    is_penalty = extras_type_clean == "penalty"

    # Team total runs on delivery
    # Wides/no-balls/byes/leg-byes add 1 run penalty, penalty adds 5 runs
    penalty_runs = np.where(
        is_wide | is_noball | is_legbye | is_bye,
        1,
        np.where(is_penalty, 5, 0),
    )
    bbb_df["total_delivery_runs"] = bat_runs + extra_runs_2 + penalty_runs

    # Bowler conceded runs:
    # - Leg-byes, byes, penalty are NOT charged to bowler
    # - Wides: 1 penalty + extra_runs_2
    # - No-balls: 1 penalty + bat_runs + extra_runs_2
    # - Normal: bat_runs + extra_runs_2
    bowler_runs = np.where(
        is_legbye | is_bye | is_penalty,
        0,
        np.where(
            is_wide,
            1 + extra_runs_2,
            np.where(is_noball, 1 + bat_runs + extra_runs_2, bat_runs + extra_runs_2),
        ),
    )
    bbb_df["bowler_runs_conceded"] = bowler_runs

    # Bowler wickets (excludes runouts, retire outs, obstructing field)
    is_wkt = bbb_df["is_wicket"].fillna(False).astype(bool)
    dis_type = (
        bbb_df["dismissal_type"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )
    is_non_bowler = dis_type.isin(NON_BOWLER_DISMISSALS)
    bbb_df["is_bowler_wicket"] = is_wkt & (~is_non_bowler)

    # Overs phase: Powerplay (1-6), Middle (7-15), Death (16-20)
    overid = bbb_df["overid"]
    bbb_df["phase"] = np.select(
        [overid <= 6, (overid >= 7) & (overid <= 15), overid >= 16],
        ["Powerplay", "Middle", "Death"],
        default="Death",
    )

    # Legal deliveries (exclude wides and no-balls)
    is_illegal = is_wide | is_noball
    bbb_df["is_legal_ball"] = ~is_illegal

    # Sort deliveries chronologically within match and innings
    bbb_df = bbb_df.sort_values(
        by=["match_id", "innings", "innings_ball_num"]
    ).reset_index(drop=True)

    # Cast boolean series to int before groupby for cumsum
    bbb_df["is_wicket_int"] = bbb_df["is_wicket"].fillna(False).astype(int)
    bbb_df["is_legal_ball_int"] = bbb_df["is_legal_ball"].astype(int)

    # Group by match_id and innings for state tracking
    grouped = bbb_df.groupby(["match_id", "innings"])
    bbb_df["cum_runs_innings"] = grouped["total_delivery_runs"].cumsum()
    bbb_df["cum_wickets_innings"] = grouped["is_wicket_int"].cumsum()
    bbb_df["balls_elapsed_innings"] = grouped["is_legal_ball_int"].cumsum()

    bbb_df = bbb_df.drop(columns=["is_wicket_int", "is_legal_ball_int"])

    # Merge match metadata
    match_cols = [
        "match_id",
        "comp_id",
        "match_date",
        "venue_id",
        "venue_country",
        "home_team_id",
        "home_team",
        "away_team_id",
        "away_team",
        "win_team_id",
        "result",
        "first_inn_revised_overs",
        "second_inn_revised_overs",
        "revised_target",
        "comp_weight",
    ]
    # Keep only available match columns
    match_cols_avail = [c for c in match_cols if c in matches_enriched.columns]
    merged_df = bbb_df.merge(
        matches_enriched[match_cols_avail], on="match_id", how="left"
    )

    # Calculate scheduled total balls per innings
    # revised_overs in matches.csv is given in total balls (e.g. 66.0 = 11 overs)
    inn = merged_df["innings"]
    first_rev = merged_df["first_inn_revised_overs"]
    second_rev = merged_df["second_inn_revised_overs"]

    # Innings 1 scheduled balls
    inn1_sched = np.where(
        first_rev.notna() & (first_rev > 0),
        first_rev.fillna(120).astype(int),
        120,
    )
    # Innings 2 scheduled balls: check second_rev first, fallback to first_rev, else 120
    inn2_sched = np.where(
        second_rev.notna() & (second_rev > 0),
        second_rev.fillna(120).astype(int),
        np.where(
            first_rev.notna() & (first_rev > 0),
            first_rev.fillna(120).astype(int),
            120,
        ),
    )

    scheduled_balls = np.where(
        inn == 1,
        inn1_sched,
        np.where(inn == 2, inn2_sched, 6),  # Super over = 6 balls
    )
    merged_df["balls_remaining_innings"] = np.maximum(
        0, scheduled_balls - merged_df["balls_elapsed_innings"]
    )

    # Determine 1st innings total runs per match
    inn1_totals = (
        merged_df[merged_df["innings"] == 1]
        .groupby("match_id")["total_delivery_runs"]
        .sum()
        .rename("inn1_total_runs")
    )
    merged_df = merged_df.merge(inn1_totals, on="match_id", how="left")

    # Determine 2nd innings target_runs:
    # Use revised_target if present, else inn1_total_runs + 1
    has_revised_target = merged_df["revised_target"].notna() & (
        merged_df["revised_target"] > 0
    )
    calc_target = np.where(
        has_revised_target,
        merged_df["revised_target"].fillna(0).astype(int),
        merged_df["inn1_total_runs"].fillna(0).astype(int) + 1,
    )

    merged_df["target_runs"] = np.where(merged_df["innings"] == 2, calc_target, 0)
    merged_df["runs_required"] = np.where(
        merged_df["innings"] == 2,
        np.maximum(0, merged_df["target_runs"] - merged_df["cum_runs_innings"]),
        0,
    )

    # Required run rate (RRR) and Current run rate (CRR)
    rem_balls = merged_df["balls_remaining_innings"]
    req_runs = merged_df["runs_required"]
    merged_df["required_run_rate"] = np.where(
        (merged_df["innings"] == 2) & (rem_balls > 0) & (req_runs > 0),
        (req_runs / rem_balls) * 6.0,
        0.0,
    )

    elap_balls = merged_df["balls_elapsed_innings"]
    cum_runs = merged_df["cum_runs_innings"]
    merged_df["current_run_rate"] = np.where(
        elap_balls > 0,
        (cum_runs / elap_balls) * 6.0,
        0.0,
    )

    # Clean up intermediate column
    if "inn1_total_runs" in merged_df.columns:
        merged_df = merged_df.drop(columns=["inn1_total_runs"])

    return merged_df
