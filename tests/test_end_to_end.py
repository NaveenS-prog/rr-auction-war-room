"""End-to-End Pipeline Integration Tests.

Validates the complete execution flow from CLI invocation:
- CLI argument parsing (--data-dir, --output-dir, --sample-fraction)
- Ingestion and match state reconstruction
- GBDT expectations, Win probability and leverage calculation
- Out-of-sample contributions and Run-equivalent valuation
- Hierarchical Bayesian partial pooling and conservative Q0.10 scoring
- Unstop schema validation and export of CSV and JSON rankings
- Markdown methodology report generation
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
    """CLI pipeline execution with sample matches fraction."""
    python_bin = os.path.join(REPO_ROOT, ".venv", "bin", "python")
    if not os.path.exists(python_bin):
        python_bin = sys.executable

    test_out = str(tmp_path / "test_reports")
    cmd = [python_bin, "main.py", "--sample-fraction", "0.05", "--output-dir", test_out]
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    assert res.returncode == 0, f"Pipeline execution failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    md_path = os.path.join(test_out, "METHODOLOGY_REPORT.md")
    csv_path = os.path.join(test_out, "unstop_dropdown_rankings.csv")
    json_path = os.path.join(test_out, "unstop_dropdown_rankings.json")
    top_bat_path = os.path.join(test_out, "top10_batters.csv")
    top_bowl_path = os.path.join(test_out, "top10_bowlers.csv")

    assert os.path.exists(md_path), "METHODOLOGY_REPORT.md not found"
    assert os.path.exists(csv_path), "unstop_dropdown_rankings.csv not found"
    assert os.path.exists(json_path), "unstop_dropdown_rankings.json not found"
    assert os.path.exists(top_bat_path), "top10_batters.csv not found"
    assert os.path.exists(top_bowl_path), "top10_bowlers.csv not found"

    # Verify JSON content
    with open(json_path, "r") as f:
        data = json.load(f)
    assert "batters" in data
    assert "bowlers" in data

    # Verify CSV content
    df_csv = pd.read_csv(csv_path)
    assert "discipline" in df_csv.columns
    assert "rank" in df_csv.columns
    assert "player_id" in df_csv.columns
    assert "player_name" in df_csv.columns
    assert "conservative_score" in df_csv.columns

    # Verify terminal output includes rankings
    assert "TOP 10 BATTERS" in res.stdout
    assert "TOP 10 BOWLERS" in res.stdout
