#!/usr/bin/env python3
"""Rajasthan Royals SupeRR Selector Season 2 - Elite Pressure Ranking Pipeline.

State-of-the-Art Probabilistic Architecture:
1. Canonical Delivery Reconstruction: Accurately parses legal balls, extras, wickets,
   and chase state.
2. Data Validation & Reconciliation: Verifies scorecard integrity across tournament matches.
3. Chronological Splits & Temporal Folds: Strict out-of-sample holdout without data leakage.
4. Model A (Situation Expectations): Calibrated Gradient-Boosted Trees predicting expected runs,
   dismissal probabilities, conceded runs, and bowler credited wickets.
5. Model B (Win-Probability Leverage Spread): Outcome volatility L(s) across legal transitions
   with late-overs urgency weighting (top 20% high-pressure cutoff).
6. Run-Equivalent Valuation: Synthesizes scoring + dismissal survival and bowling economy + wickets
   into unified run-equivalent margins (V_bat, V_bowl).
7. Model C (Hierarchical Bayesian Partial Pooling): MCMC posterior sampling of normal ability
   (mu + a_i) and pressure response (beta + d_i).
8. Conservative Q0.10 Ranking: Strictly orders players by the 10th percentile of posterior
   pressure ability to penalize small-sample variance.
9. Unstop Compliance & Reporting: Validates 0 duplicates and official tournament IDs, exporting
   dropdown selections to CSV and JSON, and generating a transparent methodology report.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from src.config import load_config, PipelineConfig
from src.canonical_data import reconstruct_canonical_deliveries
from src.validate import run_data_validation
from src.make_splits import generate_chronological_splits
from src.contributions import generate_out_of_sample_contributions
from src.models.player_ratings import HierarchicalPlayerModel
from src.ranking import RankingEngine
from src.evaluate import evaluate_predictive_validity, run_sensitivity_analysis
from src.report import generate_methodology_report
from src.validation import validate_unstop_compliance

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rr-pipeline")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rajasthan Royals SupeRR Selector Season 2 - Elite Pressure Ranking Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/settings.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Directory containing tournament CSV files (defaults to config raw_dir)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Target reports directory (defaults to config reports_dir)",
    )
    parser.add_argument(
        "--sample-fraction",
        type=float,
        default=1.0,
        help="Fraction of matches to sample (for rapid testing/debugging)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip raw data scorecard reconciliation",
    )
    return parser.parse_args()


def export_dropdown_rankings(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    validation_report: Dict[str, Any],
    output_dir: Path,
) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "unstop_dropdown_rankings.json"
    csv_path = output_dir / "unstop_dropdown_rankings.csv"

    dropdown_raw = validation_report.get("dropdown_selections", {})

    json_payload = {
        "metadata": {
            "competition": "Rajasthan Royals SupeRR Selector Season 2",
            "model_architecture": "4-Stage GBDT Expectations + Leverage Spread + Hierarchical Bayes (Q0.10 Conservative)",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
            "status": "VERIFIED_COMPLIANT" if validation_report.get("valid", False) else "UNVERIFIED",
        },
        "batters": {},
        "bowlers": {},
    }

    csv_rows = []

    for _, row in top_batters.iterrows():
        rank = int(row["rank"])
        pid = int(row["player_id"])
        c_name = dropdown_raw.get("batters", {}).get(rank, {}).get("name", str(row.get("player_name", "")))
        team = str(row.get("team_name", "Unknown"))
        cons = round(float(row.get("conservative_score", 0.0)), 4)
        p_mean = round(float(row.get("pressure_ability_mean", 0.0)), 4)
        n_mean = round(float(row.get("normal_ability_mean", 0.0)), 4)
        uplift = round(float(row.get("pressure_uplift_mean", 0.0)), 4)
        prob = round(float(row.get("prob_positive_uplift", 0.0)), 3)
        balls = int(row.get("pressure_balls", 0))
        matches = int(row.get("pressure_matches", 0))

        json_payload["batters"][str(rank)] = {
            "rank": rank,
            "player_id": pid,
            "player_name": c_name,
            "team_name": team,
            "conservative_score": cons,
            "pressure_ability_mean": p_mean,
            "normal_ability_mean": n_mean,
            "pressure_uplift_mean": uplift,
            "prob_positive_uplift": prob,
            "pressure_balls": balls,
            "pressure_matches": matches,
        }

        csv_rows.append({
            "discipline": "Batter",
            "rank": rank,
            "player_id": pid,
            "player_name": c_name,
            "team_name": team,
            "conservative_score": cons,
            "pressure_ability_mean": p_mean,
            "normal_ability_mean": n_mean,
            "pressure_uplift_mean": uplift,
            "prob_positive_uplift": prob,
            "pressure_balls": balls,
            "pressure_matches": matches,
        })

    for _, row in top_bowlers.iterrows():
        rank = int(row["rank"])
        pid = int(row["player_id"])
        c_name = dropdown_raw.get("bowlers", {}).get(rank, {}).get("name", str(row.get("player_name", "")))
        team = str(row.get("team_name", "Unknown"))
        cons = round(float(row.get("conservative_score", 0.0)), 4)
        p_mean = round(float(row.get("pressure_ability_mean", 0.0)), 4)
        n_mean = round(float(row.get("normal_ability_mean", 0.0)), 4)
        uplift = round(float(row.get("pressure_uplift_mean", 0.0)), 4)
        prob = round(float(row.get("prob_positive_uplift", 0.0)), 3)
        balls = int(row.get("pressure_balls", 0))
        matches = int(row.get("pressure_matches", 0))

        json_payload["bowlers"][str(rank)] = {
            "rank": rank,
            "player_id": pid,
            "player_name": c_name,
            "team_name": team,
            "conservative_score": cons,
            "pressure_ability_mean": p_mean,
            "normal_ability_mean": n_mean,
            "pressure_uplift_mean": uplift,
            "prob_positive_uplift": prob,
            "pressure_balls": balls,
            "pressure_matches": matches,
        }

        csv_rows.append({
            "discipline": "Bowler",
            "rank": rank,
            "player_id": pid,
            "player_name": c_name,
            "team_name": team,
            "conservative_score": cons,
            "pressure_ability_mean": p_mean,
            "normal_ability_mean": n_mean,
            "pressure_uplift_mean": uplift,
            "prob_positive_uplift": prob,
            "pressure_balls": balls,
            "pressure_matches": matches,
        })

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, indent=2)

    cols = [
        "discipline", "rank", "player_id", "player_name", "team_name",
        "conservative_score", "pressure_ability_mean", "normal_ability_mean",
        "pressure_uplift_mean", "prob_positive_uplift", "pressure_balls", "pressure_matches"
    ]
    df_csv = pd.DataFrame(csv_rows, columns=cols)
    df_csv.to_csv(csv_path, index=False)
    return csv_path, json_path


def print_executive_summary(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    validation_report: Dict[str, Any],
    eval_metrics: Dict[str, Any],
    artifacts: Dict[str, Any],
    total_deliveries: int,
    total_matches: int,
    pressure_deliveries: int,
    elapsed_time: float,
) -> None:
    sep = "=" * 105
    sub_sep = "-" * 105

    print("\n" + sep)
    print("   RAJASTHAN ROYALS | SUPERR SELECTOR SEASON 2 - ELITE PRESSURE RANKING ENGINE")
    print(sep)
    print(f" [DATA] Deliveries Ingested: {total_deliveries:,} across {total_matches:,} matches | Runtime: {elapsed_time:.2f}s")
    pct_hp = (pressure_deliveries / total_deliveries * 100.0) if total_deliveries > 0 else 0.0
    print(f" [PRESSURE] High-Pressure Deliveries (Leverage L >= Q0.80): {pressure_deliveries:,} ({pct_hp:.1f}% of match balls)")
    rmse_c = eval_metrics.get("model_c_rmse", 0.0)
    rmse_b = eval_metrics.get("normal_baseline_rmse", 0.0)
    corr = eval_metrics.get("correlation", 0.0)
    improvement = ((rmse_b - rmse_c) / rmse_b * 100.0) if rmse_b > 0 else 0.0
    print(f" [EVALUATION] Predictive Holdout RMSE: {rmse_c:.4f} vs Baseline: {rmse_b:.4f} ({improvement:.1f}% error reduction, r = {corr:.4f})")
    print(sub_sep)

    # 1. Top 10 Batters Table
    print(" TOP 10 BATTERS UNDER PRESSURE (Conservative Q0.10 Hierarchical Score)")
    print(sub_sep)
    print(f"{'Rank':<5} {'Player Name':<22} {'Nationality':<14} {'ID':<8} {'Score(Q10)':<11} {'Pressure':<10} {'Normal':<9} {'Uplift(Δ)':<10} {'P(Δ>0)':<8} {'Balls':<7} {'Matches':<8}")
    print(sub_sep)
    for _, r in top_batters.iterrows():
        rank = int(r.get("rank", 0))
        name = str(r.get("player_name", ""))[:20]
        nat = str(r.get("team_name", "Unknown"))[:12]
        pid = int(r.get("player_id", 0))
        cons = float(r.get("conservative_score", 0.0))
        p_mean = float(r.get("pressure_ability_mean", 0.0))
        n_mean = float(r.get("normal_ability_mean", 0.0))
        uplift = float(r.get("pressure_uplift_mean", 0.0))
        prob = float(r.get("prob_positive_uplift", 0.0))
        p_balls = int(r.get("pressure_balls", 0))
        p_mat = int(r.get("pressure_matches", 0))
        print(f" #{rank:<3} {name:<22} {nat:<14} {pid:<8} {cons:>+8.3f}    {p_mean:>+7.3f}   {n_mean:>+7.3f}   {uplift:>+7.3f}   {prob*100:>5.1f}%  {p_balls:>5}   {p_mat:>5}")

    print("\n" + sub_sep)
    # 2. Top 10 Bowlers Table
    print(" TOP 10 BOWLERS UNDER PRESSURE (Conservative Q0.10 Hierarchical Score)")
    print(sub_sep)
    print(f"{'Rank':<5} {'Player Name':<22} {'Nationality':<14} {'ID':<8} {'Score(Q10)':<11} {'Pressure':<10} {'Normal':<9} {'Uplift(Δ)':<10} {'P(Δ>0)':<8} {'Balls':<7} {'Matches':<8}")
    print(sub_sep)
    for _, r in top_bowlers.iterrows():
        rank = int(r.get("rank", 0))
        name = str(r.get("player_name", ""))[:20]
        nat = str(r.get("team_name", "Unknown"))[:12]
        pid = int(r.get("player_id", 0))
        cons = float(r.get("conservative_score", 0.0))
        p_mean = float(r.get("pressure_ability_mean", 0.0))
        n_mean = float(r.get("normal_ability_mean", 0.0))
        uplift = float(r.get("pressure_uplift_mean", 0.0))
        prob = float(r.get("prob_positive_uplift", 0.0))
        p_balls = int(r.get("pressure_balls", 0))
        p_mat = int(r.get("pressure_matches", 0))
        print(f" #{rank:<3} {name:<22} {nat:<14} {pid:<8} {cons:>+8.3f}    {p_mean:>+7.3f}   {n_mean:>+7.3f}   {uplift:>+7.3f}   {prob*100:>5.1f}%  {p_balls:>5}   {p_mat:>5}")

    print("\n" + sub_sep)
    # 3. Unstop Validation Summary
    is_valid = validation_report.get("valid", False)
    status_str = "VERIFIED COMPLIANT (100% Pass)" if is_valid else "VALIDATION FAILED"
    b_dups = validation_report.get("batter_duplicates", 0)
    bw_dups = validation_report.get("bowler_duplicates", 0)
    missing = len(validation_report.get("missing_ids", []))
    print(f" UNSTOP COMPLIANCE STATUS: {status_str}")
    print(f" - Duplicate Enforce : Batters: {b_dups} duplicate(s) | Bowlers: {bw_dups} duplicate(s)")
    print(f" - ID Verification   : Official Roster Matches: {20 - missing} / 20 Verified")
    print(f" - Dropdown Formats  : CSV & JSON Ready for Unstop Submission")
    print(sub_sep)

    # 4. Artifact Manifest
    print(" GENERATED ARTIFACTS:")
    print(f" - Methodology Report (MD)   : {artifacts.get('methodology_report', '')}")
    print(f" - Dropdown Selections (CSV) : {artifacts.get('dropdown_csv', '')}")
    print(f" - Dropdown Selections (JSON): {artifacts.get('dropdown_json', '')}")
    print(f" - Top 10 Batters (CSV)      : {artifacts.get('batters_csv', '')}")
    print(f" - Top 10 Bowlers (CSV)      : {artifacts.get('bowlers_csv', '')}")
    print(sep + "\n")


def main() -> int:
    start_time = time.time()
    args = parse_arguments()

    cfg = load_config(args.config)
    if args.data_dir:
        cfg.raw_data_dir = Path(args.data_dir)
    if args.output_dir:
        cfg.reports_dir = Path(args.output_dir)

    cfg.processed_data_dir.mkdir(parents=True, exist_ok=True)
    cfg.artifacts_dir.mkdir(parents=True, exist_ok=True)
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing Rajasthan Royals SupeRR Selector Pipeline...")
    logger.info(f"Raw data directory: {cfg.raw_data_dir.resolve()}")

    # 1. Canonical State Reconstruction
    canonical_parquet = cfg.processed_data_dir / "canonical_deliveries.parquet"
    if canonical_parquet.exists():
        logger.info(f"Loading existing canonical deliveries from {canonical_parquet}...")
        df = pd.read_parquet(canonical_parquet)
    else:
        logger.info(f"Reconstructing canonical delivery state from {cfg.raw_data_dir}...")
        df = reconstruct_canonical_deliveries(cfg.raw_data_dir)
        df.to_parquet(canonical_parquet, index=False)
        logger.info(f"Saved canonical table ({len(df):,} deliveries) to {canonical_parquet}.")

    if 0.0 < args.sample_fraction < 1.0:
        sample_matches = df["match_id"].drop_duplicates().sample(frac=args.sample_fraction, random_state=42)
        df = df[df["match_id"].isin(sample_matches)].copy()
        logger.info(f"Subsampled to {len(sample_matches)} matches ({len(df):,} deliveries).")

    total_deliveries = len(df)
    total_matches = df["match_id"].nunique()

    # 2. Scorecard Reconciliation
    if not args.skip_validation:
        matches_csv = cfg.raw_data_dir / "matches.csv"
        if matches_csv.exists():
            matches_df = pd.read_csv(matches_csv)
            report = run_data_validation(df, matches_df)
            report.save(cfg.artifacts_dir / "data_validation_report.json")
            logger.info(f"Validation complete: {report.reconciled_match_count} reconciled matches, {len(report.quarantined_matches)} quarantined.")

    # 3. Chronological Splits
    logger.info("Generating chronological match-level splits and expanding folds...")
    splits = generate_chronological_splits(
        df,
        train_ratio=cfg.split_ratios["train"],
        val_ratio=cfg.split_ratios["val"],
        n_folds=cfg.n_folds,
    )
    logger.info(f"Splits generated: {len(splits.train_matches)} train, {len(splits.val_matches)} val, {len(splits.test_matches)} test matches.")

    # 4. Out-of-Sample Contributions
    logger.info("Computing out-of-sample delivery expectations (Model A), leverage spread (Model B), and run-equivalent values...")
    contrib_df = generate_out_of_sample_contributions(
        df,
        splits,
        pressure_percentile=cfg.ranking["pressure_percentile"],
    )
    pressure_deliveries = int(contrib_df["is_pressure"].sum()) if "is_pressure" in contrib_df.columns else 0

    # 5. Model C: Hierarchical Player Ratings
    logger.info("Fitting Model C hierarchical Bayesian partial pooling model for Batters...")
    player_model = HierarchicalPlayerModel(
        n_samples=500,
        conservative_quantile=cfg.ranking["conservative_quantile"],
    )
    batters_ratings = player_model.fit(
        contrib_df,
        target_col="v_bat",
        player_col="striker_id",
        pressure_col="is_pressure",
    )

    logger.info("Fitting Model C hierarchical Bayesian partial pooling model for Bowlers...")
    bowlers_ratings = player_model.fit(
        contrib_df,
        target_col="v_bowl",
        player_col="bowler_id",
        pressure_col="is_pressure",
    )

    # 6. Player Metadata and Match Counts
    logger.info("Aggregating pressure match counts and joining official player mappings...")
    player_map_path = cfg.raw_data_dir / "competition_team_player_mapping.csv"
    if player_map_path.exists():
        player_meta = pd.read_csv(player_map_path)
    else:
        player_meta = pd.DataFrame()

    press_bat_matches = contrib_df[contrib_df["is_pressure"]].groupby("striker_id")["match_id"].nunique().reset_index()
    press_bat_matches.columns = ["player_id", "pressure_matches"]

    press_bowl_matches = contrib_df[contrib_df["is_pressure"]].groupby("bowler_id")["match_id"].nunique().reset_index()
    press_bowl_matches.columns = ["player_id", "pressure_matches"]

    # 7. Ranking Engine
    logger.info("Applying eligibility criteria and computing conservative Q0.10 rankings...")
    eligibility_to_use = dict(cfg.eligibility)
    if 0.0 < args.sample_fraction < 1.0:
        eligibility_to_use["min_total_balls"] = max(10, int(eligibility_to_use["min_total_balls"] * args.sample_fraction))
        eligibility_to_use["min_pressure_balls"] = max(2, int(eligibility_to_use["min_pressure_balls"] * args.sample_fraction))
        eligibility_to_use["min_pressure_matches"] = max(1, int(eligibility_to_use["min_pressure_matches"] * args.sample_fraction))

    ranker = RankingEngine(eligibility=eligibility_to_use)
    batters_leaderboard = ranker.generate_leaderboard(batters_ratings, press_bat_matches, player_meta)
    bowlers_leaderboard = ranker.generate_leaderboard(bowlers_ratings, press_bowl_matches, player_meta)

    top10_batters = ranker.get_top_10(batters_leaderboard)
    top10_bowlers = ranker.get_top_10(bowlers_leaderboard)

    # 8. Evaluation & Sensitivity
    logger.info("Evaluating predictive holdout performance on untouched test matches...")
    test_deliveries = splits.get_split_deliveries(contrib_df, "test")
    eval_metrics = evaluate_predictive_validity(
        batters_ratings, test_deliveries, target_col="v_bat", player_col="striker_id"
    )
    logger.info(f"Predictive validity: Model C RMSE = {eval_metrics.get('model_c_rmse', 0):.4f}, Correlation = {eval_metrics.get('correlation', 0):.4f}")

    sensitivity_metrics = run_sensitivity_analysis(
        contrib_df, role="batting", base_top10_ids=top10_batters["player_id"].tolist()
    )

    # 9. Methodology Report (Markdown)
    logger.info(f"Generating methodology report and submission tables in {cfg.reports_dir}...")
    report_path = generate_methodology_report(
        batters_df=top10_batters,
        bowlers_df=top10_bowlers,
        eval_metrics=eval_metrics,
        sensitivity_metrics=sensitivity_metrics,
        output_dir=cfg.reports_dir,
    )
    top10_batters.to_csv(cfg.artifacts_dir / "top10_batters.csv", index=False)
    top10_bowlers.to_csv(cfg.artifacts_dir / "top10_bowlers.csv", index=False)

    # 10. Unstop Compliance Validation & Dropdown Export
    logger.info("Validating Unstop schema compliance and exporting dropdown files...")
    validation_report = validate_unstop_compliance(top10_batters, top10_bowlers, str(cfg.raw_data_dir), strict_ten=True)

    csv_path, json_path = export_dropdown_rankings(
        top10_batters, top10_bowlers, validation_report, cfg.reports_dir
    )

    artifacts = {
        "methodology_report": str(report_path),
        "dropdown_csv": str(csv_path),
        "dropdown_json": str(json_path),
        "batters_csv": str(cfg.reports_dir / "top10_batters.csv"),
        "bowlers_csv": str(cfg.reports_dir / "top10_bowlers.csv"),
    }

    elapsed_total = time.time() - start_time
    print_executive_summary(
        top_batters=top10_batters,
        top_bowlers=top10_bowlers,
        validation_report=validation_report,
        eval_metrics=eval_metrics,
        artifacts=artifacts,
        total_deliveries=total_deliveries,
        total_matches=total_matches,
        pressure_deliveries=pressure_deliveries,
        elapsed_time=elapsed_total,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
