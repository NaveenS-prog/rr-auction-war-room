import argparse
import logging
from pathlib import Path
import sys
import pandas as pd
import numpy as np

from src.config import load_config, PipelineConfig
from src.canonical_data import reconstruct_canonical_deliveries
from src.validate import run_data_validation
from src.make_splits import generate_chronological_splits
from src.contributions import generate_out_of_sample_contributions
from src.models.player_ratings import HierarchicalPlayerModel
from src.ranking import RankingEngine
from src.evaluate import evaluate_predictive_validity, run_sensitivity_analysis
from src.report import generate_methodology_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pipeline")

def run_pipeline(
    config_path: str = "config/settings.yaml",
    raw_dir_override: str = None,
    sample_fraction: float = 1.0,
    skip_validation: bool = False
):
    logger.info("Initializing SupeRR Selector Pressure Pipeline...")
    cfg = load_config(config_path)
    if raw_dir_override:
        cfg.raw_data_dir = Path(raw_dir_override)
        
    cfg.processed_data_dir.mkdir(parents=True, exist_ok=True)
    cfg.artifacts_dir.mkdir(parents=True, exist_ok=True)
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Canonical State Reconstruction
    canonical_parquet = cfg.processed_data_dir / "canonical_deliveries.parquet"
    if canonical_parquet.exists():
        logger.info(f"Loading existing canonical deliveries from {canonical_parquet}...")
        df = pd.read_parquet(canonical_parquet)
    else:
        logger.info(f"Reconstructing canonical delivery state from {cfg.raw_data_dir}...")
        df = reconstruct_canonical_deliveries(cfg.raw_data_dir)
        df.to_parquet(canonical_parquet, index=False)
        logger.info(f"Saved canonical table ({len(df)} deliveries) to {canonical_parquet}.")
        
    if sample_fraction < 1.0 and sample_fraction > 0:
        sample_matches = df["match_id"].drop_duplicates().sample(frac=sample_fraction, random_state=42)
        df = df[df["match_id"].isin(sample_matches)].copy()
        logger.info(f"Subsampled to {len(sample_matches)} matches ({len(df)} deliveries).")

    # 2. Data Validation
    if not skip_validation:
        matches_df = pd.read_csv(cfg.raw_data_dir / "matches.csv")
        report = run_data_validation(df, matches_df)
        report.save(cfg.artifacts_dir / "data_validation_report.json")
        logger.info(f"Validation complete: {report.reconciled_match_count} reconciled matches, {len(report.quarantined_matches)} quarantined.")

    # 3. Chronological Splits
    logger.info("Generating chronological match-level splits and expanding folds...")
    splits = generate_chronological_splits(
        df,
        train_ratio=cfg.split_ratios["train"],
        val_ratio=cfg.split_ratios["val"],
        n_folds=cfg.n_folds
    )
    logger.info(f"Splits generated: {len(splits.train_matches)} train, {len(splits.val_matches)} val, {len(splits.test_matches)} test matches.")

    # 4. Out-of-Sample Contributions
    logger.info("Computing out-of-sample delivery expectations, leverage spread, and run-equivalent values...")
    contrib_df = generate_out_of_sample_contributions(
        df,
        splits,
        pressure_percentile=cfg.ranking["pressure_percentile"]
    )
    
    # 5. Model C: Hierarchical Player Ratings
    logger.info("Fitting Model C hierarchical partial pooling model for Batters...")
    player_model = HierarchicalPlayerModel(
        n_samples=500,
        conservative_quantile=cfg.ranking["conservative_quantile"]
    )
    batters_ratings = player_model.fit(
        contrib_df,
        target_col="v_bat",
        player_col="striker_id",
        pressure_col="is_pressure"
    )
    
    logger.info("Fitting Model C hierarchical partial pooling model for Bowlers...")
    bowlers_ratings = player_model.fit(
        contrib_df,
        target_col="v_bowl",
        player_col="bowler_id",
        pressure_col="is_pressure"
    )

    # 6. Metadata and Match Counts
    logger.info("Aggregating pressure match counts and joining player mappings...")
    player_map_path = cfg.raw_data_dir / "competition_team_player_mapping.csv"
    if player_map_path.exists():
        player_meta = pd.read_csv(player_map_path)
    else:
        player_meta = pd.DataFrame()

    # Batter pressure match counts
    press_bat_matches = contrib_df[contrib_df["is_pressure"]].groupby("striker_id")["match_id"].nunique().reset_index()
    press_bat_matches.columns = ["player_id", "pressure_matches"]

    # Bowler pressure match counts
    press_bowl_matches = contrib_df[contrib_df["is_pressure"]].groupby("bowler_id")["match_id"].nunique().reset_index()
    press_bowl_matches.columns = ["player_id", "pressure_matches"]

    # 7. Ranking Engine
    logger.info("Applying eligibility criteria and computing conservative Q0.10 rankings...")
    ranker = RankingEngine(eligibility=cfg.eligibility)
    
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

    # 9. Report & Submission Outputs
    logger.info(f"Generating methodology report and submission tables in {cfg.reports_dir} and {cfg.artifacts_dir}...")
    report_path = generate_methodology_report(
        batters_df=top10_batters,
        bowlers_df=top10_bowlers,
        eval_metrics=eval_metrics,
        sensitivity_metrics=sensitivity_metrics,
        output_dir=cfg.reports_dir
    )
    # Also copy submission CSVs to artifacts
    top10_batters.to_csv(cfg.artifacts_dir / "top10_batters.csv", index=False)
    top10_bowlers.to_csv(cfg.artifacts_dir / "top10_bowlers.csv", index=False)
    
    logger.info(f"Pipeline completed successfully! Methodology report saved to: {report_path}")
    print("\n" + "="*80)
    print("🏆 TOP 10 BATTERS UNDER PRESSURE (Conservative Q0.10 Score)")
    print("="*80)
    print(top10_batters[["rank", "player_name", "team_name", "conservative_score", "pressure_ability_mean", "normal_ability_mean", "pressure_uplift_mean", "pressure_balls"]].to_string(index=False))

    print("\n" + "="*80)
    print("🎯 TOP 10 BOWLERS UNDER PRESSURE (Conservative Q0.10 Score)")
    print("="*80)
    print(top10_bowlers[["rank", "player_name", "team_name", "conservative_score", "pressure_ability_mean", "normal_ability_mean", "pressure_uplift_mean", "pressure_balls"]].to_string(index=False))
    print("="*80 + "\n")
    
    return {
        "top10_batters": top10_batters,
        "top10_bowlers": top10_bowlers,
        "report_path": report_path
    }

def main():
    parser = argparse.ArgumentParser(description="SupeRR Selector Pressure Pipeline")
    parser.add_argument("--config", default="config/settings.yaml", help="Path to config yaml")
    parser.add_argument("--raw-dir", default=None, help="Override raw data directory")
    parser.add_argument("--sample", type=float, default=1.0, help="Fraction of matches to sample for fast dry runs")
    parser.add_argument("--skip-validation", action="store_true", help="Skip data validation checks")
    args = parser.parse_args()

    run_pipeline(
        config_path=args.config,
        raw_dir_override=args.raw_dir,
        sample_fraction=args.sample,
        skip_validation=args.skip_validation
    )

if __name__ == "__main__":
    main()
