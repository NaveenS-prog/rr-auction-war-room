import os
import re
import pytest
import pandas as pd
import numpy as np

from src.deck_generator import build_executive_deck


def count_pdf_pages(file_path: str) -> int:
    """Helper to count pages in a PDF file via binary regex scan."""
    with open(file_path, "rb") as f:
        content = f.read()
    # Matches /Type /Page objects in standard PDF structures
    return len(re.findall(rb"/Type\s*/Page\b", content))


def test_deck_compilation(tmp_path):
    """Canonical test verifying deck generation and non-empty output."""
    output_pdf = tmp_path / "Methodology_Report_SupeRR_Selector.pdf"
    mock_bat = pd.DataFrame([
        {
            "rank": i,
            "player_id": 100 + i,
            "player_name": f"Batter {i}",
            "n_eff_pressure": 100,
            "tsr_pressure": 25.0 - i,
            "tsr_overall": 10.0,
            "composite_score": 2.1 - i * 0.1,
            "raw_score": 2.2 - i * 0.1,
            "wpa_per_100_pressure": 0.08,
            "dot_avoidance_pressure": 0.75,
        }
        for i in range(1, 11)
    ])
    mock_bowl = pd.DataFrame([
        {
            "rank": i,
            "player_id": 200 + i,
            "player_name": f"Bowler {i}",
            "n_eff_pressure": 95,
            "ter_pressure": 1.8 - i * 0.1,
            "ter_overall": 0.5,
            "composite_score": 1.9 - i * 0.1,
            "raw_score": 2.0 - i * 0.1,
            "wpa_per_100_pressure": 0.07,
            "dot_pct_pressure": 0.45,
            "hl_wickets": 8 - (i % 4),
        }
        for i in range(1, 11)
    ])

    pdf_path = build_executive_deck(mock_bat, mock_bowl, {}, str(output_pdf))
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Non-empty PDF
    assert pdf_path == str(output_pdf)


def test_deck_has_exactly_16_pages(tmp_path):
    """Verifies that the generated presentation deck has exactly 16 landscape slides."""
    output_pdf = tmp_path / "deck_16_pages.pdf"
    mock_bat = pd.DataFrame([
        {
            "rank": i,
            "player_id": 100 + i,
            "player_name": f"Star Batter {i}",
            "n_eff_pressure": 120,
            "tsr_pressure": 22.5,
            "composite_score": 2.5 - i * 0.1,
        }
        for i in range(1, 11)
    ])
    mock_bowl = pd.DataFrame([
        {
            "rank": i,
            "player_id": 200 + i,
            "player_name": f"Star Bowler {i}",
            "n_eff_pressure": 110,
            "ter_pressure": 1.9,
            "composite_score": 2.2 - i * 0.1,
        }
        for i in range(1, 11)
    ])

    pdf_path = build_executive_deck(mock_bat, mock_bowl, {}, str(output_pdf))
    pages = count_pdf_pages(pdf_path)
    assert pages == 16, f"Expected exactly 16 pages, but got {pages}"


def test_deck_with_all_figures_and_reports(tmp_path):
    """Verifies deck generation when figures and validation/bootstrap reports are provided."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Create dummy image files
    fig_dir = tmp_path / "figs"
    fig_dir.mkdir()
    fig_paths = {}
    for name in [
        "fig1_win_prob_curves",
        "fig2_leverage_distribution",
        "fig3_batters_baseline_vs_pressure",
        "fig4_bowlers_baseline_vs_pressure",
        "fig5_top_players_radar",
    ]:
        p = fig_dir / f"{name}.png"
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot([1, 2, 3], [4, 5, 6])
        ax.set_title(name)
        fig.savefig(str(p), dpi=100)
        plt.close(fig)
        fig_paths[name] = str(p)

    output_pdf = tmp_path / "full_deck.pdf"
    mock_bat = pd.DataFrame([
        {
            "rank": i,
            "player_id": 10 + i,
            "player_name": f"Elite Batter {i}",
            "n_eff_pressure": 85,
            "tsr_pressure": 30.0 - i * 2,
            "tsr_overall": 12.0,
            "composite_score": 3.0 - i * 0.2,
            "raw_score": 3.2 - i * 0.2,
            "wpa_per_100_pressure": 0.09,
            "dot_avoidance_pressure": 0.80,
        }
        for i in range(1, 11)
    ])
    mock_bowl = pd.DataFrame([
        {
            "rank": i,
            "player_id": 30 + i,
            "player_name": f"Elite Bowler {i}",
            "n_eff_pressure": 90,
            "ter_pressure": 2.5 - i * 0.15,
            "ter_overall": 0.8,
            "composite_score": 2.8 - i * 0.2,
            "raw_score": 3.0 - i * 0.2,
            "wpa_per_100_pressure": 0.08,
            "dot_pct_pressure": 0.48,
            "hl_wickets": 10 - i,
        }
        for i in range(1, 11)
    ])

    mock_validation = {
        "valid": True,
        "batter_count": 10,
        "bowler_count": 10,
        "batter_duplicates": 0,
        "bowler_duplicates": 0,
        "has_exact_ten": True,
        "missing_ids": [],
    }

    mock_bootstrap = {
        "n_iterations": 500,
        "batters": {
            10 + i: {
                "rank_ci_95": (max(1, i - 1), min(10, i + 1)),
                "score_ci_95": (2.0, 3.2),
            }
            for i in range(1, 11)
        },
        "bowlers": {
            30 + i: {
                "rank_ci_95": (max(1, i - 1), min(10, i + 1)),
                "score_ci_95": (1.8, 2.9),
            }
            for i in range(1, 11)
        },
    }

    pdf_path = build_executive_deck(
        top_batters=mock_bat,
        top_bowlers=mock_bowl,
        figures=fig_paths,
        output_path=str(output_pdf),
        validation_report=mock_validation,
        bootstrap_report=mock_bootstrap,
    )

    assert os.path.exists(pdf_path)
    assert count_pdf_pages(pdf_path) == 16
    assert os.path.getsize(pdf_path) > 10000


def test_deck_graceful_fallbacks_for_missing_figures(tmp_path):
    """Verifies that missing or corrupt figure paths don't crash deck compilation."""
    output_pdf = tmp_path / "fallback_deck.pdf"
    mock_bat = pd.DataFrame([{"rank": i, "player_name": f"P{i}", "composite_score": 1.0} for i in range(1, 11)])
    mock_bowl = pd.DataFrame([{"rank": i, "player_name": f"B{i}", "composite_score": 1.0} for i in range(1, 11)])

    # Figures with non-existent paths
    bad_figures = {
        "fig1_win_prob_curves": "/path/does/not/exist/fig1.png",
        "fig2_leverage_distribution": None,
    }

    pdf_path = build_executive_deck(mock_bat, mock_bowl, bad_figures, str(output_pdf))
    assert os.path.exists(pdf_path)
    assert count_pdf_pages(pdf_path) == 16


def test_deck_creates_nested_output_directory(tmp_path):
    """Verifies that non-existent nested target directories are created automatically."""
    output_pdf = tmp_path / "deeply" / "nested" / "reports" / "deck.pdf"
    mock_bat = pd.DataFrame([{"rank": i, "player_name": f"P{i}", "composite_score": 1.0} for i in range(1, 11)])
    mock_bowl = pd.DataFrame([{"rank": i, "player_name": f"B{i}", "composite_score": 1.0} for i in range(1, 11)])

    assert not output_pdf.parent.exists()
    pdf_path = build_executive_deck(mock_bat, mock_bowl, {}, str(output_pdf))
    assert output_pdf.parent.exists()
    assert os.path.exists(pdf_path)
    assert count_pdf_pages(pdf_path) == 16
