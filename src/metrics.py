"""Performance Metric Computation & Phase Par Baselines for RR SupeRR Selector.

Computes league-wide phase benchmarks and context-adjusted player metrics:
1. compute_phase_par_rates:
   - League par Strike Rate and Economy Rate for Powerplay (1-6), Middle (7-15),
     and Death (16-20) overs.
   - Computes expected runs per ball, dot %, and boundary %.
2. calculate_player_raw_metrics:
   - Raw performance tables for all batters and bowlers partitioned into
     overall baseline vs high-pressure (LI >= 1.50).
   - Batters: TSR, WPA per 100 balls, Dot ball avoidance, primary batting position,
     top-7 appearances, effective deliveries N_eff.
   - Bowlers: TER, High-leverage wickets (sum(Wickets * LI)), Dot %,
     average overs per match, effective deliveries N_eff.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple
import numpy as np
import pandas as pd

# Default Phase Par Baselines for T20 cricket when empirical data is sparse or absent
DEFAULT_PHASE_PARS: Dict[str, Dict[str, float]] = {
    "Powerplay": {
        "runs_per_ball": 1.25,
        "par_sr": 125.0,
        "par_er": 7.50,
        "dot_pct": 0.40,
        "boundary_pct": 0.16,
    },
    "Middle": {
        "runs_per_ball": 1.30,
        "par_sr": 130.0,
        "par_er": 7.80,
        "dot_pct": 0.35,
        "boundary_pct": 0.12,
    },
    "Death": {
        "runs_per_ball": 1.65,
        "par_sr": 165.0,
        "par_er": 9.90,
        "dot_pct": 0.28,
        "boundary_pct": 0.22,
    },
}

BATTER_COLUMNS = [
    "player_id",
    "player_name",
    "striker_id",
    "striker_name",
    "n_balls_overall",
    "n_eff_overall",
    "tsr_overall",
    "wpa_per_100_overall",
    "dot_avoidance_overall",
    "n_balls_pressure",
    "n_eff_pressure",
    "tsr_pressure",
    "wpa_per_100_pressure",
    "dot_avoidance_pressure",
    "primary_batting_pos",
    "top7_appearances",
    "total_innings",
    "top7_appearance_pct",
]

BOWLER_COLUMNS = [
    "player_id",
    "player_name",
    "bowler_id",
    "bowler_name",
    "n_balls_overall",
    "n_eff_overall",
    "ter_overall",
    "hl_wickets_overall",
    "dot_pct_overall",
    "avg_overs_per_match",
    "n_balls_pressure",
    "n_eff_pressure",
    "ter_pressure",
    "hl_wickets_pressure",
    "dot_pct_pressure",
]


def _ensure_phase_column(df: pd.DataFrame) -> pd.Series:
    """Ensures a valid phase series ('Powerplay', 'Middle', 'Death') exists."""
    if "phase" in df.columns:
        return df["phase"].fillna("Death")
    if "overid" in df.columns:
        overid = df["overid"].fillna(18).astype(int)
        return pd.Series(
            np.select(
                [overid <= 6, (overid >= 7) & (overid <= 15), overid >= 16],
                ["Powerplay", "Middle", "Death"],
                default="Death",
            ),
            index=df.index,
        )
    return pd.Series("Death", index=df.index)


def compute_phase_par_rates(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Benchmark league par Strike Rate and Economy Rate for Powerplay, Middle, and Death overs.

    Parameters
    ----------
    df : pd.DataFrame
        Delivery-level DataFrame.

    Returns
    -------
    dict
        Dictionary mapping phase names ('Powerplay', 'Middle', 'Death') to:
        - 'runs_per_ball': float
        - 'par_sr': float (runs_per_ball * 100.0)
        - 'par_er': float (runs_per_ball * 6.0)
        - 'dot_pct': float (fraction of dot balls)
        - 'boundary_pct': float (fraction of boundaries, 4s and 6s)
    """
    pars: Dict[str, Dict[str, float]] = {k: dict(v) for k, v in DEFAULT_PHASE_PARS.items()}

    if df.empty:
        return pars

    df_work = df.copy()
    phases = _ensure_phase_column(df_work)
    df_work["_phase"] = phases

    # Identify dot balls
    if "is_dot" in df_work.columns:
        is_dot = df_work["is_dot"].fillna(False).astype(bool)
    elif "bowler_runs_conceded" in df_work.columns:
        is_dot = df_work["bowler_runs_conceded"].fillna(0) == 0
    elif "runs" in df_work.columns:
        is_dot = df_work["runs"].fillna(0) == 0
    else:
        is_dot = pd.Series(False, index=df_work.index)

    # Identify wide deliveries
    if "is_wide" in df_work.columns:
        is_wide = df_work["is_wide"].fillna(False).astype(bool)
    elif "extras_type" in df_work.columns:
        is_wide = (
            df_work["extras_type"]
            .astype(str)
            .str.lower()
            .str.contains("wide", na=False)
        )
    else:
        is_wide = pd.Series(False, index=df_work.index)

    # Identify boundaries (fours and sixes)
    is_four = df_work.get("is_four", pd.Series(False, index=df_work.index)).fillna(False).astype(bool)
    is_six = df_work.get("is_six", pd.Series(False, index=df_work.index)).fillna(False).astype(bool)
    runs_series = df_work.get("runs", pd.Series(0, index=df_work.index)).fillna(0).astype(float)
    is_boundary = is_four | is_six | runs_series.isin([4, 6]) | (runs_series >= 4)

    # Determine runs and bowler runs
    bat_runs = runs_series
    if "bowler_runs_conceded" in df_work.columns:
        bowl_runs = df_work["bowler_runs_conceded"].fillna(0).astype(float)
    else:
        bowl_runs = bat_runs

    df_work["_is_dot"] = is_dot
    df_work["_is_wide"] = is_wide
    df_work["_is_boundary"] = is_boundary
    df_work["_bat_runs"] = bat_runs
    df_work["_bowl_runs"] = bowl_runs

    for phase in ["Powerplay", "Middle", "Death"]:
        phase_subset = df_work[df_work["_phase"] == phase]
        n_balls = len(phase_subset)
        if n_balls == 0:
            continue

        # Exclude wide deliveries when computing batting par rates
        non_wide_subset = phase_subset[~phase_subset["_is_wide"]]
        n_bat_balls = len(non_wide_subset)

        tot_bat_runs = (
            float(non_wide_subset["_bat_runs"].sum())
            if n_bat_balls > 0
            else float(phase_subset["_bat_runs"].sum())
        )
        tot_bowl_runs = float(phase_subset["_bowl_runs"].sum())
        dots = float(phase_subset["_is_dot"].sum())
        boundaries = float(phase_subset["_is_boundary"].sum())

        if n_bat_balls > 0:
            rpb = tot_bat_runs / n_bat_balls
            par_sr = rpb * 100.0
        else:
            rpb = tot_bat_runs / n_balls
            par_sr = rpb * 100.0

        # Bowler par ER is based on all deliveries (tot_bowl_runs / n_balls * 6.0)
        par_er = (tot_bowl_runs / n_balls) * 6.0
        dot_pct = dots / n_balls
        boundary_pct = boundaries / n_balls

        pars[phase] = {
            "runs_per_ball": float(rpb),
            "par_sr": float(par_sr),
            "par_er": float(par_er),
            "dot_pct": float(dot_pct),
            "boundary_pct": float(boundary_pct),
        }

    return pars


def calculate_player_raw_metrics(
    df: pd.DataFrame, phase_pars: Dict[str, Dict[str, float]]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Calculates context-adjusted raw performance tables for all batters and bowlers.

    Partitioned into overall baseline vs high-pressure (LI >= 1.50).

    Parameters
    ----------
    df : pd.DataFrame
        Delivery-level DataFrame enriched with match state, win probability,
        leverage index, and phase annotations.
    phase_pars : dict
        Phase benchmark dictionary output from compute_phase_par_rates.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        df_batters, df_bowlers containing raw overall and pressure metrics.
    """
    if df.empty:
        return (
            pd.DataFrame(columns=BATTER_COLUMNS),
            pd.DataFrame(columns=BOWLER_COLUMNS),
        )

    df_work = df.copy()

    # 1. Standardize phase
    df_work["_phase"] = _ensure_phase_column(df_work)

    # 2. Standardize pressure flag
    if "is_high_pressure" in df_work.columns:
        is_pressure = df_work["is_high_pressure"].fillna(False).astype(bool)
    elif "leverage_index" in df_work.columns:
        is_pressure = df_work["leverage_index"].fillna(1.0) >= 1.50
    else:
        is_pressure = pd.Series(False, index=df_work.index)
    df_work["_is_pressure"] = is_pressure

    # 3. Standardize competition weight
    if "comp_weight" in df_work.columns:
        df_work["_comp_weight"] = df_work["comp_weight"].fillna(1.0).astype(float)
    else:
        df_work["_comp_weight"] = 1.0

    # 4. Standardize leverage index and delta WPA
    df_work["_leverage_index"] = (
        df_work["leverage_index"].fillna(1.0).astype(float)
        if "leverage_index" in df_work.columns
        else 1.0
    )
    df_work["_delta_wpa"] = (
        df_work["delta_wpa"].fillna(0.0).astype(float)
        if "delta_wpa" in df_work.columns
        else 0.0
    )

    # 5. Map phase expectations
    def _get_phase_rpb(phase_name: str) -> float:
        if phase_name in phase_pars:
            return phase_pars[phase_name].get("runs_per_ball", 1.35)
        return DEFAULT_PHASE_PARS.get(phase_name, {}).get("runs_per_ball", 1.35)

    def _get_phase_er(phase_name: str) -> float:
        if phase_name in phase_pars:
            return phase_pars[phase_name].get("par_er", 8.10)
        return DEFAULT_PHASE_PARS.get(phase_name, {}).get("par_er", 8.10)

    df_work["_phase_rpb"] = df_work["_phase"].map(_get_phase_rpb).fillna(1.35)
    df_work["_phase_er"] = df_work["_phase"].map(_get_phase_er).fillna(8.10)
    df_work["_phase_bowl_rpb"] = df_work["_phase_er"] / 6.0

    # =========================================================================
    # BATTERS AGGREGATION
    # =========================================================================
    df_batters = _aggregate_batters(df_work)

    # =========================================================================
    # BOWLERS AGGREGATION
    # =========================================================================
    df_bowlers = _aggregate_bowlers(df_work)

    return df_batters, df_bowlers


def _aggregate_batters(df_work: pd.DataFrame) -> pd.DataFrame:
    """Aggregates batting performance across overall and pressure contexts."""
    # Exclude wide deliveries from balls faced by the striker
    if "is_wide" in df_work.columns:
        is_wide = df_work["is_wide"].fillna(False).astype(bool)
        df_bat = df_work[~is_wide].copy()
    elif "extras_type" in df_work.columns:
        is_wide = (
            df_work["extras_type"]
            .astype(str)
            .str.lower()
            .str.contains("wide", na=False)
        )
        df_bat = df_work[~is_wide].copy()
    else:
        df_bat = df_work.copy()

    # Filter out missing striker_id
    if "striker_id" not in df_bat.columns:
        return pd.DataFrame(columns=BATTER_COLUMNS)

    df_bat = df_bat[df_bat["striker_id"].notna()].copy()
    if df_bat.empty:
        return pd.DataFrame(columns=BATTER_COLUMNS)

    # Batter runs
    df_bat["_bat_runs"] = (
        df_bat["runs"].fillna(0).astype(float) if "runs" in df_bat.columns else 0.0
    )

    # Batter dot ball
    if "is_dot" in df_bat.columns:
        df_bat["_is_dot"] = df_bat["is_dot"].fillna(False).astype(bool)
    else:
        df_bat["_is_dot"] = df_bat["_bat_runs"] == 0
    df_bat["_is_not_dot"] = (~df_bat["_is_dot"]).astype(float)

    # Expected runs
    df_bat["_exp_runs"] = df_bat["_phase_rpb"]

    # Player names
    if "striker_name" in df_bat.columns:
        names = df_bat.groupby("striker_id")["striker_name"].last()
    else:
        names = pd.Series(
            df_bat["striker_id"].unique().astype(str),
            index=df_bat["striker_id"].unique(),
        )

    # Overall metrics
    grp_all = df_bat.groupby("striker_id")
    n_balls_overall = grp_all.size()
    n_eff_overall = grp_all["_comp_weight"].sum()
    runs_overall = grp_all["_bat_runs"].sum()
    exp_runs_overall = grp_all["_exp_runs"].sum()
    tsr_overall = ((runs_overall - exp_runs_overall) / n_balls_overall) * 100.0
    wpa_overall = grp_all["_delta_wpa"].sum()
    wpa_per_100_overall = (wpa_overall / n_balls_overall) * 100.0
    not_dots_overall = grp_all["_is_not_dot"].sum()
    dot_avoidance_overall = not_dots_overall / n_balls_overall

    # Batting order and top 7 role sanity
    if "batting_order" in df_bat.columns:
        df_bat = df_bat.assign(_order=df_bat["batting_order"].fillna(4).astype(float))
        primary_pos = (
            df_bat.groupby("striker_id")["_order"]
            .median()
            .round()
            .astype(int)
        )
        # Unique match-innings appearances
        subset_cols = ["match_id", "innings", "striker_id"]
        avail_sub = [c for c in subset_cols if c in df_bat.columns]
        if len(avail_sub) >= 2:
            match_inn = df_bat.drop_duplicates(subset=avail_sub)
            top7_match = match_inn[match_inn["_order"] <= 7]
            top7_count = top7_match.groupby("striker_id").size()
            total_inn = match_inn.groupby("striker_id").size()
            top7_pct = (top7_count / total_inn).fillna(0.0)
        else:
            top7_count = pd.Series(1, index=n_balls_overall.index)
            total_inn = pd.Series(1, index=n_balls_overall.index)
            top7_pct = pd.Series(1.0, index=n_balls_overall.index)
    else:
        primary_pos = pd.Series(4, index=n_balls_overall.index)
        top7_count = pd.Series(1, index=n_balls_overall.index)
        total_inn = pd.Series(1, index=n_balls_overall.index)
        top7_pct = pd.Series(1.0, index=n_balls_overall.index)

    # Pressure metrics
    df_press = df_bat[df_bat["_is_pressure"]]
    if not df_press.empty:
        grp_p = df_press.groupby("striker_id")
        n_balls_press = grp_p.size()
        n_eff_press = grp_p["_comp_weight"].sum()
        runs_press = grp_p["_bat_runs"].sum()
        exp_runs_press = grp_p["_exp_runs"].sum()
        tsr_press = ((runs_press - exp_runs_press) / n_balls_press) * 100.0
        wpa_press = grp_p["_delta_wpa"].sum()
        wpa_per_100_press = (wpa_press / n_balls_press) * 100.0
        not_dots_press = grp_p["_is_not_dot"].sum()
        dot_avoidance_press = not_dots_press / n_balls_press
    else:
        n_balls_press = pd.Series(dtype=int)
        n_eff_press = pd.Series(dtype=float)
        tsr_press = pd.Series(dtype=float)
        wpa_per_100_press = pd.Series(dtype=float)
        dot_avoidance_press = pd.Series(dtype=float)

    # Combine into DataFrame
    player_ids = n_balls_overall.index
    res = pd.DataFrame(index=player_ids)
    res["player_id"] = player_ids
    res["striker_id"] = player_ids
    fallback_names = pd.Series(player_ids.astype(str), index=player_ids)
    res["player_name"] = names.reindex(player_ids).fillna(fallback_names)
    res["striker_name"] = res["player_name"]

    res["n_balls_overall"] = n_balls_overall
    res["n_eff_overall"] = n_eff_overall
    res["tsr_overall"] = tsr_overall
    res["wpa_per_100_overall"] = wpa_per_100_overall
    res["dot_avoidance_overall"] = dot_avoidance_overall

    res["n_balls_pressure"] = n_balls_press.reindex(player_ids).fillna(0).astype(int)
    res["n_eff_pressure"] = n_eff_press.reindex(player_ids).fillna(0.0)
    res["tsr_pressure"] = tsr_press.reindex(player_ids).fillna(0.0)
    res["wpa_per_100_pressure"] = wpa_per_100_press.reindex(player_ids).fillna(0.0)
    res["dot_avoidance_pressure"] = dot_avoidance_press.reindex(player_ids).fillna(0.0)

    res["primary_batting_pos"] = primary_pos.reindex(player_ids).fillna(4).astype(int)
    res["top7_appearances"] = top7_count.reindex(player_ids).fillna(0).astype(int)
    res["total_innings"] = total_inn.reindex(player_ids).fillna(0).astype(int)
    res["top7_appearance_pct"] = top7_pct.reindex(player_ids).fillna(1.0)

    return res[BATTER_COLUMNS].reset_index(drop=True)


def _aggregate_bowlers(df_work: pd.DataFrame) -> pd.DataFrame:
    """Aggregates bowling performance across overall and pressure contexts."""
    if "bowler_id" not in df_work.columns:
        return pd.DataFrame(columns=BOWLER_COLUMNS)

    df_bowl = df_work[df_work["bowler_id"].notna()].copy()
    if df_bowl.empty:
        return pd.DataFrame(columns=BOWLER_COLUMNS)

    # Conceded runs
    if "bowler_runs_conceded" in df_bowl.columns:
        df_bowl["_conceded"] = df_bowl["bowler_runs_conceded"].fillna(0).astype(float)
    elif "runs" in df_bowl.columns:
        df_bowl["_conceded"] = df_bowl["runs"].fillna(0).astype(float)
    else:
        df_bowl["_conceded"] = 0.0

    # Bowler wickets
    if "is_bowler_wicket" in df_bowl.columns:
        is_wkt = df_bowl["is_bowler_wicket"].fillna(False).astype(bool)
    elif "is_wicket" in df_bowl.columns:
        is_wkt = df_bowl["is_wicket"].fillna(False).astype(bool)
    else:
        is_wkt = pd.Series(False, index=df_bowl.index)
    df_bowl["_is_wicket"] = is_wkt

    # High-leverage wicket value: is_wicket * LI
    df_bowl["_hl_wicket_value"] = is_wkt.astype(float) * df_bowl["_leverage_index"]

    # Dot balls for bowler
    if "is_dot" in df_bowl.columns:
        df_bowl["_is_dot"] = df_bowl["is_dot"].fillna(False).astype(bool)
    else:
        df_bowl["_is_dot"] = df_bowl["_conceded"] == 0
    df_bowl["_is_dot_float"] = df_bowl["_is_dot"].astype(float)

    # Expected runs
    df_bowl["_exp_conceded"] = df_bowl["_phase_bowl_rpb"]

    # Names
    if "bowler_name" in df_bowl.columns:
        names = df_bowl.groupby("bowler_id")["bowler_name"].last()
    else:
        names = pd.Series(
            df_bowl["bowler_id"].unique().astype(str),
            index=df_bowl["bowler_id"].unique(),
        )

    # Overall metrics
    grp_all = df_bowl.groupby("bowler_id")
    n_balls_overall = grp_all.size()
    n_eff_overall = grp_all["_comp_weight"].sum()
    conceded_overall = grp_all["_conceded"].sum()
    exp_conceded_overall = grp_all["_exp_conceded"].sum()
    # TER = Expected ER - Actual ER = (ExpRuns - Conceded) / n_balls * 6.0
    ter_overall = ((exp_conceded_overall - conceded_overall) / n_balls_overall) * 6.0
    hl_wkts_overall = grp_all["_hl_wicket_value"].sum()
    dots_overall = grp_all["_is_dot_float"].sum()
    dot_pct_overall = dots_overall / n_balls_overall

    # Matches and average overs per match
    if "match_id" in df_bowl.columns:
        matches_count = grp_all["match_id"].nunique()
    else:
        matches_count = pd.Series(1, index=n_balls_overall.index)
    avg_overs_per_match = (n_balls_overall / 6.0) / matches_count.replace(0, 1)

    # Pressure metrics
    df_press = df_bowl[df_bowl["_is_pressure"]]
    if not df_press.empty:
        grp_p = df_press.groupby("bowler_id")
        n_balls_press = grp_p.size()
        n_eff_press = grp_p["_comp_weight"].sum()
        conceded_press = grp_p["_conceded"].sum()
        exp_conceded_press = grp_p["_exp_conceded"].sum()
        ter_press = ((exp_conceded_press - conceded_press) / n_balls_press) * 6.0
        hl_wkts_press = grp_p["_hl_wicket_value"].sum()
        dots_press = grp_p["_is_dot_float"].sum()
        dot_pct_press = dots_press / n_balls_press
    else:
        n_balls_press = pd.Series(dtype=int)
        n_eff_press = pd.Series(dtype=float)
        ter_press = pd.Series(dtype=float)
        hl_wkts_press = pd.Series(dtype=float)
        dot_pct_press = pd.Series(dtype=float)

    # Combine into DataFrame
    player_ids = n_balls_overall.index
    res = pd.DataFrame(index=player_ids)
    res["player_id"] = player_ids
    res["bowler_id"] = player_ids
    fallback_names = pd.Series(player_ids.astype(str), index=player_ids)
    res["player_name"] = names.reindex(player_ids).fillna(fallback_names)
    res["bowler_name"] = res["player_name"]

    res["n_balls_overall"] = n_balls_overall
    res["n_eff_overall"] = n_eff_overall
    res["ter_overall"] = ter_overall
    res["hl_wickets_overall"] = hl_wkts_overall
    res["dot_pct_overall"] = dot_pct_overall
    res["avg_overs_per_match"] = avg_overs_per_match

    res["n_balls_pressure"] = n_balls_press.reindex(player_ids).fillna(0).astype(int)
    res["n_eff_pressure"] = n_eff_press.reindex(player_ids).fillna(0.0)
    res["ter_pressure"] = ter_press.reindex(player_ids).fillna(0.0)
    res["hl_wickets_pressure"] = hl_wkts_press.reindex(player_ids).fillna(0.0)
    res["dot_pct_pressure"] = dot_pct_press.reindex(player_ids).fillna(0.0)

    return res[BOWLER_COLUMNS].reset_index(drop=True)
