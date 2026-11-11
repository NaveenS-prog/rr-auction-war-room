"""End-to-End Pipeline Integration Tests.

Validates the complete execution flow from CLI invocation:
- CLI argument parsing (--data-dir, --sample, --output-dir, --bootstrap-iterations)
- Ingestion and match state reconstruction
- Win probability and leverage calculation
- Metric aggregation and dual-axis ranking computation
- Unstop schema validation and bootstrap sensitivity analysis
- Generation of high-res figures and 16-page executive PDF presentation deck
- Export of CSV and JSON rankings
- Formatted terminal output
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import pandas as pd
import pytest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_full_pipeline_cli(tmp_path):
    """Canonical test from specification: CLI pipeline execution with sample matches."""
    python_bin = os.path.join(REPO_ROOT, ".venv", "bin", "python")
    if not os.path.exists(python_bin):
        python_bin = sys.executable

    # Run main pipeline on 20-match sample
    cmd = [python_bin, "main.py", "--sample", "20"]
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    assert res.returncode == 0, f"Pipeline execution failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    assert os.path.exists("reports/Methodology_Report_SupeRR_Selector_Season_2.pdf")
    assert os.path.exists("reports/unstop_dropdown_rankings.csv")
    assert os.path.exists("reports/unstop_dropdown_rankings.json")

    # Verify PDF non-empty
    pdf_size = os.path.getsize("reports/Methodology_Report_SupeRR_Selector_Season_2.pdf")
    assert pdf_size > 10000, f"Generated PDF is unexpectedly small ({pdf_size} bytes)"

    # Verify JSON content
    with open("reports/unstop_dropdown_rankings.json", "r") as f:
        data = json.load(f)
    assert "batters" in data
    assert "bowlers" in data
    assert len(data["batters"]) == 10
    assert len(data["bowlers"]) == 10

    # Verify CSV content
    df_csv = pd.read_csv("reports/unstop_dropdown_rankings.csv")
    assert "discipline" in df_csv.columns
    assert "rank" in df_csv.columns
    assert "player_id" in df_csv.columns
    assert "player_name" in df_csv.columns
    assert "composite_score" in df_csv.columns
    assert len(df_csv) == 20

    # Verify 5 figures exist
    for fig_name in [
        "fig1_win_prob_curves.png",
        "fig2_leverage_distribution.png",
        "fig3_batters_baseline_vs_pressure.png",
        "fig4_bowlers_baseline_vs_pressure.png",
        "fig5_top_players_radar.png",
    ]:
        fig_path = os.path.join("reports", "figures", fig_name)
        assert os.path.exists(fig_path), f"Expected figure not found: {fig_path}"

    # Verify terminal output includes rankings
    assert "Top 10 Batters" in res.stdout or "TOP 10 BATTERS" in res.stdout
    assert "Top 10 Bowlers" in res.stdout or "TOP 10 BOWLERS" in res.stdout


def test_custom_output_dir_cli(tmp_path):
    """Test CLI pipeline execution with custom output directory and bootstrap iterations."""
    python_bin = os.path.join(REPO_ROOT, ".venv", "bin", "python")
    if not os.path.exists(python_bin):
        python_bin = sys.executable

    out_dir = str(tmp_path / "custom_reports")
    cmd = [
        python_bin,
        "main.py",
        "--sample",
        "10",
        "--output-dir",
        out_dir,
        "--bootstrap-iterations",
        "15",
    ]
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    assert res.returncode == 0, f"Execution failed:\n{res.stderr}"
    assert os.path.exists(os.path.join(out_dir, "Methodology_Report_SupeRR_Selector_Season_2.pdf"))
    assert os.path.exists(os.path.join(out_dir, "unstop_dropdown_rankings.csv"))
    assert os.path.exists(os.path.join(out_dir, "unstop_dropdown_rankings.json"))
    assert os.path.exists(os.path.join(out_dir, "figures", "fig1_win_prob_curves.png"))
