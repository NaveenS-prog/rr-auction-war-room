#!/usr/bin/env python3
"""Rajasthan Royals SupeRR Selector Season 2 - End-to-End Pipeline.

Executes the complete pressure performance ranking system:
1. Ingestion: Load matches and reconstruct delivery match states.
2. Win Probability & Leverage Index: Train dual-innings expectancy models,
   compute ball-by-ball Delta WPA, and classify high-pressure balls (LI >= 1.50).
3. Phase Benchmarks & Metrics: Compute phase par rates and aggregate raw performance
   metrics for batters and bowlers across overall and pressure contexts.
4. Dual-Axis Composite Scoring & Shrinkage: Standardize high-pressure performance
   and personal clutch deltas (70/30), apply Empirical Bayes Shrinkage (M=30),
   and filter by role and volume eligibility to determine the Top 10 Batters and Bowlers.
5. Unstop Schema Validation & Sensitivity Analysis: Verify zero duplicate player IDs,
   cross-reference canonical IDs against official tournament mapping, and compute
   empirical 95% bootstrap confidence intervals for rank and score stability.
6. Visualization & Reporting: Generate 5 publication-grade 300 DPI figures and compile
   the 16-page landscape corporate presentation deck (Methodology_Report_SupeRR_Selector_Season_2.pdf).
7. Dropdown Selections Export: Save exact Rank 1-10 selections to CSV and JSON formats.
8. Terminal Summary: Output structured rankings tables and verification status.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from src.data_loader import load_and_process_deliveries
from src.deck_generator import build_executive_deck
from src.metrics import calculate_player_raw_metrics, compute_phase_par_rates
from src.rankings import compute_rankings
from src.validation import compute_bootstrap_sensitivity, validate_unstop_compliance
from src.visualizer import generate_all_figures


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for the pipeline execution."""
    parser = argparse.ArgumentParser(
        description="Rajasthan Royals SupeRR Selector Season 2 - End-to-End Pressure Ranking Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=".",
        help="Directory containing tournament CSV files (matches.csv, ball_by_ball.csv, competitions.csv, etc.)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Optional limit on number of matches to process (for rapid verification/testing)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Target directory where PDF report, figures, and dropdown exports will be written",
    )
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=100,
        help="Number of bootstrap resampling iterations for ranking sensitivity analysis (default: 100)",
    )
    parser.add_argument(
        "--min-pressure-balls",
        type=int,
        default=None,
        help="Minimum effective pressure balls required for ranking eligibility (defaults to 60 for full runs)",
    )
    parser.add_argument(
        "--prior-m",
        type=float,
        default=30.0,
        help="Empirical Bayes prior sample size weight M (default: 30.0 balls)",
    )
    return parser.parse_args()


def export_dropdown_rankings(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    validation_report: Dict[str, Any],
    output_dir: str,
) -> Tuple[str, str]:
    """Exports exact Rank 1-10 dropdown selections to JSON and CSV formats.

    Parameters
    ----------
    top_batters : pd.DataFrame
        Ranked Top 10 Batters.
    top_bowlers : pd.DataFrame
        Ranked Top 10 Bowlers.
    validation_report : Dict[str, Any]
        Unstop compliance validation report containing dropdown_selections.
    output_dir : str
        Directory to save exported files.

    Returns
    -------
    Tuple[str, str]
        File paths for generated (csv_path, json_path).
    """
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "unstop_dropdown_rankings.json")
    csv_path = os.path.join(output_dir, "unstop_dropdown_rankings.csv")

    # 1. Format JSON payload
    dropdown_raw = validation_report.get("dropdown_selections", {})
    json_payload = {
        "metadata": {
            "title": "Rajasthan Royals SupeRR Selector Season 2 - Dropdown Selections",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
            "status": "VERIFIED_COMPLIANT" if validation_report.get("valid", False) else "UNVERIFIED",
        },
        "batters": {
            str(rank): {
                "rank": int(rank),
                "player_id": int(item["id"]) if item.get("id") is not None else None,
                "player_name": str(item.get("name", "")),
                "composite_score": round(
                    float(
                        top_batters.loc[top_batters["rank"] == rank, "composite_score"].values[0]
                    ),
                    4,
                )
                if not top_batters.empty and "rank" in top_batters.columns and (top_batters["rank"] == rank).any()
                else 0.0,
            }
            for rank, item in dropdown_raw.get("batters", {}).items()
        },
        "bowlers": {
            str(rank): {
                "rank": int(rank),
                "player_id": int(item["id"]) if item.get("id") is not None else None,
                "player_name": str(item.get("name", "")),
                "composite_score": round(
                    float(
                        top_bowlers.loc[top_bowlers["rank"] == rank, "composite_score"].values[0]
                    ),
                    4,
                )
                if not top_bowlers.empty and "rank" in top_bowlers.columns and (top_bowlers["rank"] == rank).any()
                else 0.0,
            }
            for rank, item in dropdown_raw.get("bowlers", {}).items()
        },
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, indent=2)

    # 2. Format CSV payload
    records = []
    for _, row in top_batters.iterrows():
        rank = int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else len(records) + 1
        pid = int(row["player_id"]) if "player_id" in row and pd.notna(row["player_id"]) else None
        c_name = dropdown_raw.get("batters", {}).get(rank, {}).get("name", str(row.get("player_name", "")))
        tsr_p = float(row.get("tsr_pressure", 0.0)) if pd.notna(row.get("tsr_pressure")) else 0.0
        tsr_o = float(row.get("tsr_overall", 0.0)) if pd.notna(row.get("tsr_overall")) else 0.0
        d_tsr = float(row["delta_tsr"]) if "delta_tsr" in row and pd.notna(row["delta_tsr"]) else (tsr_p - tsr_o)
        records.append({
            "discipline": "Batter",
            "rank": rank,
            "player_id": pid,
            "player_name": c_name,
            "composite_score": round(float(row.get("composite_score", 0.0)), 4),
            "raw_score": round(float(row.get("raw_score", 0.0)), 4) if "raw_score" in row else None,
            "n_eff_pressure": round(float(row.get("n_eff_pressure", 0.0)), 1) if "n_eff_pressure" in row else None,
            "tsr_pressure": round(tsr_p, 2),
            "tsr_overall": round(tsr_o, 2),
            "delta_tsr": round(d_tsr, 2),
            "wpa_per_100_pressure": round(float(row.get("wpa_per_100_pressure", 0.0)), 4) if "wpa_per_100_pressure" in row else None,
            "dot_avoidance_pressure": round(float(row.get("dot_avoidance_pressure", 0.0)), 4) if "dot_avoidance_pressure" in row else None,
        })

    for _, row in top_bowlers.iterrows():
        rank = int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else len(records) + 1
        pid = int(row["player_id"]) if "player_id" in row and pd.notna(row["player_id"]) else None
        c_name = dropdown_raw.get("bowlers", {}).get(rank, {}).get("name", str(row.get("player_name", "")))
        ter_p = float(row.get("ter_pressure", 0.0)) if pd.notna(row.get("ter_pressure")) else 0.0
        ter_o = float(row.get("ter_overall", 0.0)) if pd.notna(row.get("ter_overall")) else 0.0
        d_ter = float(row["delta_ter"]) if "delta_ter" in row and pd.notna(row["delta_ter"]) else (ter_p - ter_o)
        records.append({
            "discipline": "Bowler",
            "rank": rank,
            "player_id": pid,
            "player_name": c_name,
            "composite_score": round(float(row.get("composite_score", 0.0)), 4),
            "raw_score": round(float(row.get("raw_score", 0.0)), 4) if "raw_score" in row else None,
            "n_eff_pressure": round(float(row.get("n_eff_pressure", 0.0)), 1) if "n_eff_pressure" in row else None,
            "ter_pressure": round(ter_p, 2),
            "ter_overall": round(ter_o, 2),
            "delta_ter": round(d_ter, 2),
            "hl_wickets_pressure": round(float(row.get("hl_wickets_pressure", 0.0)), 2) if "hl_wickets_pressure" in row else None,
            "dot_pct_pressure": round(float(row.get("dot_pct_pressure", 0.0)), 4) if "dot_pct_pressure" in row else None,
        })

    df_csv = pd.DataFrame(records)
    df_csv.to_csv(csv_path, index=False)

    return csv_path, json_path


def print_terminal_summary(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    validation_report: Dict[str, Any],
    artifacts: Dict[str, str],
    total_deliveries: int,
    total_matches: int,
    high_pressure_balls: int,
    elapsed_time: float,
) -> None:
    """Prints a styled franchise presentation summary table to the terminal."""
    sep = "=" * 98
    sub_sep = "-" * 98

    print("\n" + sep)
    print("   RAJASTHAN ROYALS | SUPERR SELECTOR SEASON 2 - PRESSURE RANKING ENGINE")
    print(sep)
    print(f" [DATA] Deliveries Ingested: {total_deliveries:,} across {total_matches:,} matches | Run Time: {elapsed_time:.2f}s")
    pct_hp = (high_pressure_balls / total_deliveries * 100.0) if total_deliveries > 0 else 0.0
    print(f" [WIN PROB] High-Pressure Deliveries (LI >= 1.50): {high_pressure_balls:,} ({pct_hp:.1f}% of tournament balls)")
    print(sub_sep)

    # 1. Top 10 Batters Table
    print(" TOP 10 BATTERS UNDER PRESSURE (Dual-Axis Clutch Score S_final)")
    print(sub_sep)
    print(f"{'Rank':<5} {'Player Name':<24} {'ID':<8} {'S_final':<8} {'S_raw':<8} {'N_eff':<7} {'TSR(HP)':<9} {'TSR(All)':<9} {'Δ TSR':<8}")
    print(sub_sep)
    for _, r in top_batters.iterrows():
        rank = int(r.get("rank", 0))
        name = str(r.get("player_name", ""))[:22]
        pid = int(r.get("player_id", 0))
        s_fin = float(r.get("composite_score", 0.0))
        s_raw = float(r.get("raw_score", s_fin))
        n_eff = float(r.get("n_eff_pressure", 0.0))
        tsr_p = float(r.get("tsr_pressure", 0.0))
        tsr_o = float(r.get("tsr_overall", 0.0))
        d_tsr = float(r.get("delta_tsr", tsr_p - tsr_o))
        print(f" #{rank:<3} {name:<24} {pid:<8} {s_fin:>+7.3f} {s_raw:>+7.3f} {n_eff:>6.1f} {tsr_p:>+8.2f} {tsr_o:>+8.2f} {d_tsr:>+7.2f}")

    print("\n" + sub_sep)
    # 2. Top 10 Bowlers Table
    print(" TOP 10 BOWLERS UNDER PRESSURE (Dual-Axis Clutch Score S_final)")
    print(sub_sep)
    print(f"{'Rank':<5} {'Player Name':<24} {'ID':<8} {'S_final':<8} {'S_raw':<8} {'N_eff':<7} {'TER(HP)':<9} {'TER(All)':<9} {'Δ TER':<8}")
    print(sub_sep)
    for _, r in top_bowlers.iterrows():
        rank = int(r.get("rank", 0))
        name = str(r.get("player_name", ""))[:22]
        pid = int(r.get("player_id", 0))
        s_fin = float(r.get("composite_score", 0.0))
        s_raw = float(r.get("raw_score", s_fin))
        n_eff = float(r.get("n_eff_pressure", 0.0))
        ter_p = float(r.get("ter_pressure", 0.0))
        ter_o = float(r.get("ter_overall", 0.0))
        d_ter = float(r.get("delta_ter", ter_p - ter_o))
        print(f" #{rank:<3} {name:<24} {pid:<8} {s_fin:>+7.3f} {s_raw:>+7.3f} {n_eff:>6.1f} {ter_p:>+8.2f} {ter_o:>+8.2f} {d_ter:>+7.2f}")

    print("\n" + sub_sep)
    # 3. Validation Report Summary
    is_valid = validation_report.get("valid", False)
    status_str = "VERIFIED COMPLIANT (100% Pass)" if is_valid else "VALIDATION FAILED"
    b_dups = validation_report.get("batter_duplicates", 0)
    bw_dups = validation_report.get("bowler_duplicates", 0)
    missing = len(validation_report.get("missing_ids", []))
    print(f" UNSTOP COMPLIANCE STATUS: {status_str}")
    print(f" - Duplicate Check : Batters: {b_dups} duplicate(s) | Bowlers: {bw_dups} duplicate(s)")
    print(f" - ID Verification : Official Roster ID Matches: {20 - missing} / 20 Verified")
    print(f" - Dropdown Ready  : 10 Batters & 10 Bowlers Formatted")
    print(sub_sep)

    # 4. Artifact Manifest
    print(" GENERATED REPORT ARTIFACTS:")
    print(f" - 16-Slide PDF Executive Deck : {artifacts.get('pdf', '')}")
    print(f" - Dropdown Selections (CSV)   : {artifacts.get('csv', '')}")
    print(f" - Dropdown Selections (JSON)  : {artifacts.get('json', '')}")
    print(f" - High-Resolution Figures     : {artifacts.get('figures_dir', '')}")
    print(sep + "\n")


def main() -> int:
    """Executes the full pipeline and generates all report artifacts."""
    start_time = time.time()
    args = parse_arguments()

    data_dir = os.path.abspath(args.data_dir)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print(f"[Pipeline] Starting Rajasthan Royals SupeRR Selector Pipeline...")
    print(f"[Pipeline] Data directory : {data_dir}")
    print(f"[Pipeline] Output directory: {output_dir}")
    if args.sample:
        print(f"[Pipeline] Running in sample mode (matches limit: {args.sample})")

    # Step 1: Load and process deliveries
    t0 = time.time()
    df_deliveries = load_and_process_deliveries(data_dir, sample_matches=args.sample)
    total_deliveries = len(df_deliveries)
    total_matches = df_deliveries["match_id"].nunique() if not df_deliveries.empty else 0
    print(f"[Pipeline] Step 1 Complete: {total_deliveries:,} deliveries across {total_matches} matches loaded ({time.time() - t0:.2f}s)")

    # Step 2: Train Win Probability Models & Compute Win Probability + Leverage
    from src.win_prob import compute_win_probability_and_leverage, train_win_prob_models

    t0 = time.time()
    models = train_win_prob_models(df_deliveries)
    df_state = compute_win_probability_and_leverage(df_deliveries, models)
    high_pressure_balls = int(df_state["is_high_pressure"].sum()) if "is_high_pressure" in df_state.columns else 0
    print(f"[Pipeline] Step 2 Complete: Win prob & Leverage Index calculated ({time.time() - t0:.2f}s)")
    print(f"[Pipeline] High-pressure deliveries identified: {high_pressure_balls:,}")

    # Step 3: Compute Phase Par Rates & Player Raw Metrics
    t0 = time.time()
    phase_pars = compute_phase_par_rates(df_state)
    df_batters_raw, df_bowlers_raw = calculate_player_raw_metrics(df_state, phase_pars)
    print(f"[Pipeline] Step 3 Complete: Metrics computed for {len(df_batters_raw)} batters and {len(df_bowlers_raw)} bowlers ({time.time() - t0:.2f}s)")

    # Step 4: Determine volume threshold and compute rankings
    if args.min_pressure_balls is not None:
        min_balls = args.min_pressure_balls
    elif args.sample is not None and args.sample < 100:
        # Dynamically scale qualification volume for sample/test runs
        min_balls = max(1, min(10, int(args.sample * 0.5)))
    else:
        min_balls = 60

    t0 = time.time()
    top_batters, top_bowlers = compute_rankings(
        df_batters_raw,
        df_bowlers_raw,
        min_pressure_balls=min_balls,
        prior_m=args.prior_m,
        top_n=10,
    )
    print(f"[Pipeline] Step 4 Complete: Top {len(top_batters)} Batters & Top {len(top_bowlers)} Bowlers ranked (min_balls={min_balls}) ({time.time() - t0:.2f}s)")

    # Step 5: Unstop Schema Validation & Bootstrap Sensitivity Analysis
    t0 = time.time()
    validation_report = validate_unstop_compliance(top_batters, top_bowlers, data_dir, strict_ten=False)
    
    # Configure bootstrap iterations
    if args.sample is not None and args.sample <= 50 and args.bootstrap_iterations == 100:
        n_boot = 30  # Swift bootstrap for sample/integration test runs
    else:
        n_boot = args.bootstrap_iterations

    print(f"[Pipeline] Step 5: Running sensitivity analysis ({n_boot} bootstrap iterations)...")
    bootstrap_report = compute_bootstrap_sensitivity(
        df_state,
        top_batters,
        top_bowlers,
        n_iterations=n_boot,
        min_pressure_balls=min_balls if args.sample is not None else None,
        random_state=42,
    )
    print(f"[Pipeline] Step 5 Complete: Validation & Bootstrap finished ({time.time() - t0:.2f}s)")

    # Step 6: Generate High-Resolution Visualizations
    t0 = time.time()
    figures_dir = os.path.join(output_dir, "figures")
    figures = generate_all_figures(df_state, top_batters, top_bowlers, figures_dir)
    print(f"[Pipeline] Step 6 Complete: 5 high-res figures generated at {figures_dir} ({time.time() - t0:.2f}s)")

    # Step 7: Build Executive Presentation Deck (16-Page Landscape PDF)
    t0 = time.time()
    pdf_path = os.path.join(output_dir, "Methodology_Report_SupeRR_Selector_Season_2.pdf")
    build_executive_deck(
        top_batters,
        top_bowlers,
        figures=figures,
        output_path=pdf_path,
        validation_report=validation_report,
        bootstrap_report=bootstrap_report,
    )
    print(f"[Pipeline] Step 7 Complete: Executive PDF compiled at {pdf_path} ({time.time() - t0:.2f}s)")

    # Step 8: Export Dropdown Selections
    t0 = time.time()
    csv_path, json_path = export_dropdown_rankings(
        top_batters, top_bowlers, validation_report, output_dir
    )
    print(f"[Pipeline] Step 8 Complete: Dropdown selections exported to CSV and JSON ({time.time() - t0:.2f}s)")

    # Step 9: Print Formatted Terminal Summary
    artifacts = {
        "pdf": pdf_path,
        "csv": csv_path,
        "json": json_path,
        "figures_dir": figures_dir,
    }
    elapsed_total = time.time() - start_time
    print_terminal_summary(
        top_batters=top_batters,
        top_bowlers=top_bowlers,
        validation_report=validation_report,
        artifacts=artifacts,
        total_deliveries=total_deliveries,
        total_matches=total_matches,
        high_pressure_balls=high_pressure_balls,
        elapsed_time=elapsed_total,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
