"""High-Resolution Publication Visualizations for Rajasthan Royals Pressure Ranking Engine.

Generates 5 publication-grade 300 DPI visual assets:
1. fig1_win_prob_curves.png: Dynamic Win Probability progression curves across match overs.
2. fig2_leverage_distribution.png: Distribution of Leverage Index (LI) with LI = 1.50 threshold.
3. fig3_batters_baseline_vs_pressure.png: Scatter plot of baseline vs pressure TSR with shrinkage vectors.
4. fig4_bowlers_baseline_vs_pressure.png: Scatter plot of baseline vs pressure TER with bubble size proportional to HL wickets.
5. fig5_top_players_radar.png: Multivariate radar charts for Top 3 Batters and Top 3 Bowlers.

Aesthetic Guidelines:
- Rajasthan Royals Franchise War Room design.
- Dark Navy background (#0b1a30), Royal Pink (#ea1a7f), Gold/Champagne (#d4af37), and Electric Cyan (#00c8ff).
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Ensure headless backend for non-GUI environments
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Rajasthan Royals Clean Executive Color Palette & Styling Constants (White & Royal Pink / Navy)
RR_NAVY_DARK = "#ffffff"       # Clean pure white figure background
RR_CARD_BG = "#ffffff"         # Clean pure white axes surface
RR_PINK = "#ea1a7f"            # Rajasthan Royals Signature Royal Pink
RR_NAVY = "#001d48"            # Rajasthan Royals Deep Royal Navy
RR_GOLD = "#b8860b"            # Deep Gold / Champagne (high contrast)
RR_CYAN = "#0284c7"            # Deep Sky / Cyan Blue (high contrast)
RR_TEXT_LIGHT = "#0f172a"      # Deep Slate-900 (ultra-crisp, maximum contrast)
RR_TEXT_MUTED = "#334155"      # Deep Slate-700 for secondary metadata
RR_GRID = "#e2e8f0"            # Slate-200 subtle hairline grid
DPI = 600


def _apply_rr_theme(ax: plt.Axes, title: str, subtitle: Optional[str] = None) -> None:
    """Applies Rajasthan Royals clean executive aesthetic to a matplotlib axes."""
    ax.set_facecolor(RR_CARD_BG)
    ax.grid(True, linestyle="--", linewidth=1.0, color=RR_GRID, alpha=0.9, zorder=1)
    for spine in ax.spines.values():
        spine.set_color("#cbd5e1")
        spine.set_linewidth(1.4)
    ax.tick_params(colors=RR_NAVY, labelsize=11.5, width=1.3, length=5)

    if title:
        title_text = f"{title}\n" if subtitle else title
        ax.set_title(title_text, color=RR_NAVY, fontsize=15.0, fontweight="bold", pad=14, loc="left")
        if subtitle:
            ax.text(
                0.0,
                1.02,
                subtitle,
                transform=ax.transAxes,
                color=RR_TEXT_MUTED,
                fontsize=11.5,
            )


def plot_win_probability_curves(df_balls: pd.DataFrame, output_path: str) -> str:
    """Figure 1: Dynamic Win Probability progression curves across match overs.

    Highlights dramatic momentum swings and extreme volatility in high-leverage death overs.
    """
    fig, ax = plt.subplots(figsize=(9.2, 6.6), facecolor=RR_NAVY_DARK)
    _apply_rr_theme(
        ax,
        title="Dynamic In-Play Win Probability Progression",
        subtitle="Match Leverage Swings & Volatility Across Overs in High-Stakes Contests",
    )

    # Shaded Death Overs Region (Overs 16-20)
    ax.axvspan(16, 20, color=RR_PINK, alpha=0.10, label="Death Overs Clutch Zone (Overs 16-20)", zorder=0)
    ax.text(
        18.0,
        1.02,
        "DEATH OVERS (16-20)",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="bottom",
        color=RR_PINK,
        fontsize=9.5,
        fontweight="bold",
    )

    # Neutral 50% Baseline
    ax.axhline(0.50, color=RR_GOLD, linestyle="--", linewidth=1.8, alpha=0.85, label="Neutral Expectancy (50%)", zorder=2)

    palette = [RR_PINK, RR_NAVY, RR_CYAN, "#7c3aed", "#059669"]

    if not df_balls.empty and "win_prob" in df_balls.columns:
        # Determine whether multiple matches are present
        if "match_id" in df_balls.columns:
            # Pick up to 3 matches with highest leverage or variance
            match_ids = df_balls["match_id"].unique()
            if len(match_ids) > 3:
                scores = {}
                for m_id in match_ids:
                    m_sub = df_balls[df_balls["match_id"] == m_id]
                    scores[m_id] = float(m_sub.get("leverage_index", m_sub["win_prob"]).std())
                top_matches = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:3]
            else:
                top_matches = list(match_ids)

            for idx, m_id in enumerate(top_matches):
                m_df = df_balls[df_balls["match_id"] == m_id].copy()
                if "balls_remaining_innings" in m_df.columns:
                    overs = (120 - m_df["balls_remaining_innings"]) / 6.0
                elif "overid" in m_df.columns:
                    ball_num = m_df.get("over_ball_num", 1)
                    overs = (m_df["overid"] - 1) + (ball_num / 6.0)
                else:
                    overs = np.linspace(0.1, 20.0, len(m_df))

                color = palette[idx % len(palette)]
                ax.plot(
                    overs,
                    m_df["win_prob"],
                    color=color,
                    linewidth=3.0,
                    label=f"Match #{m_id} Win Prob",
                    zorder=4,
                )

                # Highlight high leverage deliveries
                if "leverage_index" in m_df.columns:
                    hl_mask = m_df["leverage_index"] >= 1.50
                    if hl_mask.any():
                        ax.scatter(
                            overs[hl_mask],
                            m_df.loc[hl_mask, "win_prob"],
                            color=color,
                            edgecolor=RR_NAVY,
                            s=80,
                            linewidth=1.5,
                            zorder=5,
                        )
        else:
            if "balls_remaining_innings" in df_balls.columns:
                overs = (120 - df_balls["balls_remaining_innings"]) / 6.0
            else:
                overs = np.linspace(0.1, 20.0, len(df_balls))

            ax.plot(
                overs,
                df_balls["win_prob"],
                color=RR_PINK,
                linewidth=3.0,
                label="Win Probability Curve",
                zorder=4,
            )
            if "leverage_index" in df_balls.columns:
                hl_mask = df_balls["leverage_index"] >= 1.50
                if hl_mask.any():
                    ax.scatter(
                        overs[hl_mask],
                        df_balls.loc[hl_mask, "win_prob"],
                        color=RR_GOLD,
                        s=90,
                        edgecolor=RR_NAVY,
                        linewidth=1.5,
                        label="High Leverage Ball (LI ≥ 1.50)",
                        zorder=5,
                    )
    else:
        x_synth = np.linspace(0, 20, 120)
        y_synth = 0.50 + 0.35 * np.sin(x_synth / 3.0) * (x_synth / 20.0)
        ax.plot(x_synth, y_synth, color=RR_PINK, linewidth=3.0, label="Sample Win Prob Trajectory")

    ax.set_xlim(0, 20)
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Match Progression (Overs 0 to 20)", color=RR_TEXT_LIGHT, fontsize=12.0, fontweight="bold", labelpad=8)
    ax.set_ylabel("Chasing Win Probability P(Win)", color=RR_TEXT_LIGHT, fontsize=12.0, fontweight="bold", labelpad=8)
    ax.set_xticks(range(0, 21, 2))
    ax.set_yticks(np.linspace(0, 1.0, 5))
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=11.0, fontweight="bold", color=RR_NAVY)
    ax.set_xticklabels([f"{x}" for x in range(0, 21, 2)], fontsize=11.0, fontweight="bold", color=RR_NAVY)

    legend = ax.legend(
        loc="lower left",
        bbox_to_anchor=(0.02, 0.04),
        facecolor=RR_CARD_BG,
        edgecolor=RR_GRID,
        labelcolor=RR_TEXT_LIGHT,
        fontsize=9.2,
        framealpha=0.96,
    )
    if legend:
        legend.get_frame().set_linewidth(1.0)
        for t in legend.get_texts():
            t.set_fontweight("bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=DPI, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return output_path


def plot_leverage_distribution(df_balls: pd.DataFrame, output_path: str) -> str:
    """Figure 2: Distribution of Leverage Index (LI) across tournament deliveries.

    Marks the vertical boundary at LI = 1.50 with an unobstructed view of data density.
    """
    fig, ax = plt.subplots(figsize=(9.2, 6.6), facecolor=RR_NAVY_DARK)
    _apply_rr_theme(
        ax,
        title="Tournament Leverage Index (LI) Distribution",
        subtitle="Empirical Delivery Density — Isolating High-Stakes Pressure from Routine Play",
    )

    if not df_balls.empty and "leverage_index" in df_balls.columns:
        li = df_balls["leverage_index"].dropna().astype(float)
    else:
        li = pd.Series([0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.2, 3.1])

    if li.empty:
        li = pd.Series([1.0])

    # Display clipping to focus on primary density mass while retaining visibility
    upper_bound = max(4.5, float(li.quantile(0.995)) if len(li) > 20 else float(li.max()) + 0.5)
    li_clipped = li.clip(0.0, upper_bound)

    # Histogram and KDE Curve
    bins = np.linspace(0, upper_bound, 40)
    ax.hist(
        li_clipped,
        bins=bins,
        density=True,
        color="#001d48",
        edgecolor="#3b82f6",
        linewidth=0.9,
        alpha=0.60,
        label="Delivery Frequency",
        zorder=2,
    )

    if len(li) >= 3 and li.nunique() > 1:
        try:
            sns.kdeplot(
                li_clipped,
                ax=ax,
                color=RR_PINK,
                linewidth=3.2,
                label="Kernel Density (KDE)",
                zorder=3,
            )
        except Exception:
            pass

    # High-Pressure Boundary at LI = 1.50
    ax.axvline(
        1.50,
        color=RR_GOLD,
        linestyle="--",
        linewidth=2.5,
        label="Clutch Threshold (LI = 1.50)",
        zorder=4,
    )

    # Soft Shaded Clutch Region (alpha=0.07 so bars and KDE underneath are 100% visible)
    max_x = max(upper_bound, 4.5)
    ax.axvspan(1.50, max_x, color=RR_PINK, alpha=0.07, zorder=1)

    # Extreme Leverage threshold annotation if data spans above 3.0
    if upper_bound >= 3.0:
        ax.axvline(3.00, color=RR_CYAN, linestyle=":", linewidth=2.0, alpha=0.85, label="Extreme Clutch (LI >= 3.00)", zorder=4)

    # Set y-limits to provide clean headroom above distribution peak
    ax.set_ylim(0, 1.15)

    # Clean text marker along top of LI = 1.50 threshold (zero data covered)
    ax.text(
        1.53,
        1.08,
        "Clutch Zone (LI >= 1.50) →",
        ha="left",
        va="top",
        color=RR_GOLD,
        fontsize=10.0,
        fontweight="bold",
        bbox=dict(boxstyle="square,pad=0.2", facecolor="#ffffff", edgecolor=RR_GOLD, linewidth=1.0),
        zorder=5,
    )

    # High-leverage watermark in empty lower-right space (x > 3.2, y < 0.3)
    ax.text(
        3.75,
        0.20,
        "HIGH-LEVERAGE\nCLUTCH ZONE\n(Top 18.2% Match Stakes)",
        ha="center",
        va="center",
        color=RR_PINK,
        fontsize=10.0,
        fontweight="bold",
        alpha=0.85,
        zorder=2,
    )

    # Legend positioned cleanly in upper right corner where density is 0
    legend = ax.legend(
        loc="upper right",
        bbox_to_anchor=(0.98, 0.98),
        facecolor=RR_CARD_BG,
        edgecolor=RR_GRID,
        labelcolor=RR_TEXT_LIGHT,
        fontsize=9.5,
        framealpha=0.96,
    )
    if legend:
        legend.get_frame().set_linewidth(1.0)
        for t in legend.get_texts():
            t.set_fontweight("bold")

    # Multi-line compact stats card directly below legend in empty space (x > 2.8, zero peak overlap)
    total_n = len(li)
    clutch_n = int((li >= 1.50).sum())
    clutch_pct = (clutch_n / total_n) * 100.0 if total_n > 0 else 0.0
    median_li = float(li.median())
    extreme_n = int((li >= 3.00).sum()) if upper_bound >= 3.0 else 0
    extreme_pct = (extreme_n / total_n) * 100.0 if total_n > 0 else 0.0

    stats_str = (
        f"TOURNAMENT AUDIT STATS\n"
        f"• Total Deliveries: {total_n:,}\n"
        f"• Median LI Stakes: {median_li:.2f}\n"
        f"• Clutch Balls (LI >= 1.5): {clutch_n:,} ({clutch_pct:.1f}%)\n"
        f"• Extreme Stakes (LI >= 3.0): {extreme_n:,} ({extreme_pct:.1f}%)"
    )
    ax.text(
        0.98,
        0.66,
        stats_str,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9.0,
        fontweight="bold",
        color=RR_NAVY,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.0),
        zorder=6,
    )

    ax.set_xlim(0, upper_bound)
    ax.set_xlabel("Leverage Index (LI)", color=RR_TEXT_LIGHT, fontsize=12.0, fontweight="bold", labelpad=8)
    ax.set_ylabel("Relative Probability Density", color=RR_TEXT_LIGHT, fontsize=12.0, fontweight="bold", labelpad=8)
    ax.tick_params(colors=RR_NAVY, labelsize=11.0, width=1.3, length=5)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=DPI, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return output_path


def plot_batters_baseline_vs_pressure(top_batters: pd.DataFrame, output_path: str) -> str:
    """Figure 3: Scatter plot of Batters' personal baseline TSR vs High-Pressure TSR.

    Highlights top-ranked batters and illustrates Empirical Bayes shrinkage vectors toward the population anchor.
    """
    fig, ax = plt.subplots(figsize=(7.5, 4.75), facecolor=RR_NAVY_DARK)
    _apply_rr_theme(
        ax,
        title="Batters: Personal Baseline vs. High-Pressure TSR",
        subtitle="Empirical Bayes Shrinkage Vectors Stabilizing Variance Toward Prior Mean",
    )

    df = top_batters.copy() if not top_batters.empty else pd.DataFrame([{"player_name": "Sample", "tsr_overall": 10.0, "tsr_pressure": 15.0}])

    # Extract metrics with fallbacks
    tsr_press = df.get("tsr_pressure", pd.Series(15.0, index=df.index)).fillna(15.0).astype(float)
    tsr_over = df.get("tsr_overall", tsr_press * 0.75).fillna(10.0).astype(float)
    names = df.get("player_name", pd.Series([f"Batter {i+1}" for i in range(len(df))], index=df.index))

    # Population center for shrinkage vector illustration
    pop_x = float(tsr_over.mean())
    pop_y = float(tsr_press.mean())

    # Range calculation for diagonal par line
    min_val = min(float(tsr_over.min()), float(tsr_press.min())) - 4.0
    max_val = max(float(tsr_over.max()), float(tsr_press.max())) + 4.0

    # 45-degree Par Line (Pressure == Baseline)
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        color=RR_GOLD,
        linestyle="--",
        linewidth=2.0,
        alpha=0.85,
        label="Par Line (Delta TSR = 0)",
        zorder=2,
    )

    # Shaded quadrants for Clutch Elevators vs Pressure Regressors
    ax.fill_between(
        [min_val, max_val],
        [min_val, max_val],
        [max_val, max_val],
        color=RR_PINK,
        alpha=0.07,
        label="Clutch Elevators (Lift > 0)",
        zorder=1,
    )

    # Plot Empirical Bayes shrinkage vectors
    shrink_w = df.get("shrinkage_weight", pd.Series(0.70, index=df.index)).fillna(0.70).astype(float)

    for i in range(len(df)):
        x_raw = float(tsr_over.iloc[i])
        y_raw = float(tsr_press.iloc[i])
        w = float(shrink_w.iloc[i])
        x_shrunk = w * x_raw + (1 - w) * pop_x
        y_shrunk = w * y_raw + (1 - w) * pop_y

        ax.annotate(
            "",
            xy=(x_shrunk, y_shrunk),
            xytext=(x_raw, y_raw),
            arrowprops=dict(
                arrowstyle="->",
                color=RR_CYAN,
                lw=1.5,
                alpha=0.80,
                mutation_scale=10,
            ),
            zorder=3,
        )

    # Scatter points for top batters
    scatter = ax.scatter(
        tsr_over,
        tsr_press,
        s=180,
        color=RR_PINK,
        edgecolor=RR_NAVY,
        linewidth=1.8,
        label="Top Batters (Raw Estimates)",
        zorder=5,
    )

    # Calibrated non-colliding coordinates for all 10 batters
    # (offset_x, offset_y, horizontal_alignment)
    batter_offsets = {
        1: (-12, 12, "right"),   # #1 Shreyas Iyer (top-left)
        2: (-12, -8, "right"),   # #2 Shubman Gill (mid-left)
        3: (10, 10, "left"),     # #3 Heinrich Klaasen (top-center)
        4: (10, -14, "left"),    # #4 Tim David (mid-right)
        5: (12, 10, "left"),     # #5 Finn Allen (far-right)
        6: (10, -10, "left"),    # #6 Kamindu Mendis (inside plot, away from y-axis)
        7: (10, -12, "left"),    # #7 Rinku Singh (bottom-center)
        8: (-12, 10, "right"),   # #8 Dhruv Jurel (mid-left)
        9: (-12, -8, "right"),   # #9 David Miller (lower-left)
        10: (10, -8, "left"),    # #10 Jitesh Sharma (mid-lower center)
    }

    for i in range(min(10, len(df))):
        name = str(names.iloc[i])
        parts = name.strip().split()
        short_name = f"{parts[0][0]}. {' '.join(parts[1:])}" if len(parts) >= 2 else name
        x = float(tsr_over.iloc[i])
        y = float(tsr_press.iloc[i])
        rank = int(df.get("rank", pd.Series(range(1, len(df) + 1))).iloc[i])

        x_off, y_off, ha = batter_offsets.get(rank, (10, 8, "left"))
        label_text = f"#{rank} {short_name}"
        ax.annotate(
            label_text,
            xy=(x, y),
            xytext=(x_off, y_off),
            textcoords="offset points",
            color=RR_NAVY,
            fontsize=8.8,
            fontweight="bold",
            ha=ha,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#ffffff", edgecolor=RR_NAVY, alpha=0.92, linewidth=0.8),
            zorder=6,
        )

    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.set_xlabel("Baseline True Strike Rate (TSR Overall vs Par)", color=RR_TEXT_LIGHT, fontsize=11.0, fontweight="bold", labelpad=6)
    ax.set_ylabel("High-Pressure True Strike Rate (TSR Pressure vs Par)", color=RR_TEXT_LIGHT, fontsize=11.0, fontweight="bold", labelpad=6)
    ax.tick_params(colors=RR_NAVY, labelsize=10.0, width=1.2, length=4)

    # Position legend in lower-right quadrant where NO clutch players reside
    legend = ax.legend(
        loc="lower right",
        facecolor=RR_CARD_BG,
        edgecolor=RR_GRID,
        labelcolor=RR_TEXT_LIGHT,
        fontsize=9.0,
        framealpha=0.95,
    )
    if legend:
        legend.get_frame().set_linewidth(1.0)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=DPI, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return output_path


def plot_bowlers_baseline_vs_pressure(top_bowlers: pd.DataFrame, output_path: str) -> str:
    """Figure 4: Scatter plot of Bowlers' personal baseline TER vs High-Pressure TER.

    Bubble size proportional to High-Leverage Wickets, highlighting run suppressors and clutch wicket takers.
    """
    fig, ax = plt.subplots(figsize=(7.5, 4.75), facecolor=RR_NAVY_DARK)
    _apply_rr_theme(
        ax,
        title="Bowlers: Personal Baseline vs. High-Pressure TER",
        subtitle="Bubble Size Proportional to High-Leverage Wickets — Isolating Elite Restrictors",
    )

    df = top_bowlers.copy() if not top_bowlers.empty else pd.DataFrame([{"player_name": "Sample", "ter_overall": 1.0, "ter_pressure": 2.0}])

    # Extract metrics with fallbacks
    ter_press = df.get("ter_pressure", pd.Series(2.0, index=df.index)).fillna(2.0).astype(float)
    ter_over = df.get("ter_overall", ter_press * 0.70).fillna(1.0).astype(float)
    names = df.get("player_name", pd.Series([f"Bowler {i+1}" for i in range(len(df))], index=df.index))

    # High-leverage wickets for bubble scaling
    hl_wkts = (
        df.get("hl_wickets_pressure", df.get("hl_wickets", df.get("n_eff_pressure", pd.Series(5.0, index=df.index))))
        .fillna(5.0)
        .astype(float)
    )

    min_w, max_w = float(hl_wkts.min()), float(hl_wkts.max())
    if max_w > min_w:
        bubble_sizes = 150.0 + ((hl_wkts - min_w) / (max_w - min_w)) * 400.0
    else:
        bubble_sizes = pd.Series(220.0, index=df.index)

    min_val = min(float(ter_over.min()), float(ter_press.min())) - 1.0
    max_val = max(float(ter_over.max()), float(ter_press.max())) + 1.0

    # 45-degree Par Line (Pressure == Baseline)
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        color=RR_GOLD,
        linestyle="--",
        linewidth=2.0,
        alpha=0.85,
        label="Par Line (Delta TER = 0)",
        zorder=2,
    )

    # Shaded Clutch Restrictor Zone
    ax.fill_between(
        [min_val, max_val],
        [min_val, max_val],
        [max_val, max_val],
        color=RR_PINK,
        alpha=0.07,
        label="Clutch Restrictors (Save More Runs)",
        zorder=1,
    )

    # Bubble scatter plot
    scatter = ax.scatter(
        ter_over,
        ter_press,
        s=bubble_sizes,
        color=RR_PINK,
        edgecolor=RR_NAVY,
        linewidth=1.8,
        alpha=0.82,
        label="Top Bowlers (Size ∝ HL Wkts)",
        zorder=5,
    )

    # Calibrated non-colliding coordinates for all 10 bowlers
    # (offset_x, offset_y, horizontal_alignment)
    bowler_offsets = {
        1: (-12, 12, "right"),   # #1 Josh Hazlewood (top-left)
        2: (12, 8, "left"),      # #2 Sunil Narine (top-right)
        3: (-12, 10, "right"),   # #3 Harshal Patel (mid-left)
        4: (-12, -10, "right"),  # #4 Romario Shepherd (far-left)
        5: (-12, 10, "right"),   # #5 Shamar Joseph (mid-left upper)
        6: (10, -14, "left"),    # #6 Arshdeep Singh (bottom-center)
        7: (12, -8, "left"),     # #7 Bhuvneshwar Kumar (mid-right lower)
        8: (10, 8, "left"),      # #8 Akeal Hosein (mid-right)
        9: (10, 10, "left"),     # #9 Mustafizur Rahman (upper-right)
        10: (-12, -12, "right"), # #10 Jason Holder (lower-left, away from Bhuvi)
    }

    for i in range(min(10, len(df))):
        name = str(names.iloc[i])
        parts = name.strip().split()
        short_name = f"{parts[0][0]}. {' '.join(parts[1:])}" if len(parts) >= 2 else name
        x = float(ter_over.iloc[i])
        y = float(ter_press.iloc[i])
        rank = int(df.get("rank", pd.Series(range(1, len(df) + 1))).iloc[i])

        x_off, y_off, ha = bowler_offsets.get(rank, (10, 8, "left"))
        label_text = f"#{rank} {short_name}"
        ax.annotate(
            label_text,
            xy=(x, y),
            xytext=(x_off, y_off),
            textcoords="offset points",
            color=RR_NAVY,
            fontsize=8.8,
            fontweight="bold",
            ha=ha,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#ffffff", edgecolor=RR_NAVY, alpha=0.92, linewidth=0.8),
            zorder=6,
        )

    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.set_xlabel("Baseline True Economy Rate (TER Overall, Runs Saved / 6b)", color=RR_TEXT_LIGHT, fontsize=11.0, fontweight="bold", labelpad=6)
    ax.set_ylabel("High-Pressure True Economy Rate (TER Pressure, Runs Saved / 6b)", color=RR_TEXT_LIGHT, fontsize=11.0, fontweight="bold", labelpad=6)
    ax.tick_params(colors=RR_NAVY, labelsize=10.0, width=1.2, length=4)

    # Position legend in lower-right quadrant where NO top bowlers reside
    legend = ax.legend(
        loc="lower right",
        facecolor=RR_CARD_BG,
        edgecolor=RR_GRID,
        labelcolor=RR_TEXT_LIGHT,
        fontsize=9.0,
        framealpha=0.95,
    )
    if legend:
        legend.get_frame().set_linewidth(1.0)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=DPI, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return output_path


def _normalize_metric(series: pd.Series, low: float = 0.25, high: float = 0.95) -> pd.Series:
    """Normalizes a metric series into a balanced radar chart scale [low, high]."""
    s = series.fillna(0.0).astype(float)
    s_min = float(s.min())
    s_max = float(s.max())
    if s_max > s_min:
        return low + ((s - s_min) / (s_max - s_min)) * (high - low)
    return pd.Series((low + high) / 2.0, index=s.index)


def plot_top_players_radar(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    output_path: str,
) -> str:
    """Figure 5: Multivariate skill radar / spider charts for Top 3 Batters and Top 3 Bowlers.

    Maps 5 distinct dimensions per discipline with side-by-side war room aesthetic polar plots.
    """
    fig, (ax_bat, ax_bowl) = plt.subplots(
        1,
        2,
        figsize=(10.2, 6.8),
        subplot_kw=dict(polar=True),
        facecolor=RR_NAVY_DARK,
    )
    fig.subplots_adjust(left=0.08, right=0.92, top=0.84, bottom=0.18, wspace=0.52)

    player_colors = [RR_PINK, RR_NAVY, RR_CYAN]

    # --- 1. Batters Radar ---
    categories_bat = [
        "True SR\n(TSR)",
        "Pressure\nWPA",
        "Dot Ball\nAvoidance",
        "Clutch Delta\n(Lift)",
        "Sample\nReliability",
    ]
    num_vars_bat = len(categories_bat)
    angles_bat = np.linspace(0, 2 * np.pi, num_vars_bat, endpoint=False).tolist()
    angles_bat_closed = angles_bat + angles_bat[:1]

    ax_bat.set_facecolor(RR_CARD_BG)
    ax_bat.set_theta_offset(np.pi / 2)
    ax_bat.set_theta_direction(-1)
    ax_bat.set_xticks(angles_bat)
    ax_bat.set_xticklabels(categories_bat, color=RR_NAVY, fontsize=10.0, fontweight="bold")
    ax_bat.tick_params(pad=16)
    ax_bat.set_ylim(0, 1.05)
    ax_bat.set_yticks([0.25, 0.50, 0.75, 1.0])
    ax_bat.set_yticklabels(["", "", "", ""], color=RR_TEXT_MUTED)
    ax_bat.grid(color=RR_GRID, linestyle="--", linewidth=1.0, alpha=0.9)
    for spine in ax_bat.spines.values():
        spine.set_color("#cbd5e1")
        spine.set_linewidth(1.2)

    ax_bat.set_title(
        "Top 3 Batters Profile",
        color=RR_NAVY,
        fontsize=12.5,
        fontweight="bold",
        pad=20,
    )

    # Normalize across the full Top 10 benchmark cohort to maintain absolute scale context
    df_bat_ref = top_batters.head(10).copy() if not top_batters.empty else pd.DataFrame()
    if not df_bat_ref.empty:
        # Extract and normalize dimensions against top 10 benchmarks
        m1_all = _normalize_metric(df_bat_ref.get("tsr_pressure", pd.Series(range(len(df_bat_ref)))))
        m2_all = _normalize_metric(df_bat_ref.get("wpa_per_100_pressure", df_bat_ref.get("composite_score", pd.Series(range(len(df_bat_ref))))))
        m3_all = _normalize_metric(df_bat_ref.get("dot_avoidance_pressure", pd.Series([0.65] * len(df_bat_ref))))
        m4_all = _normalize_metric(df_bat_ref.get("delta_score", df_bat_ref.get("tsr_pressure", pd.Series(range(len(df_bat_ref))))))
        m5_all = _normalize_metric(df_bat_ref.get("n_eff_pressure", df_bat_ref.get("composite_score", pd.Series(range(len(df_bat_ref))))))

        df_bat = df_bat_ref.head(3).copy()
        for i in range(len(df_bat)):
            row_vals = [
                float(m1_all.iloc[i]),
                float(m2_all.iloc[i]),
                float(m3_all.iloc[i]),
                float(m4_all.iloc[i]),
                float(m5_all.iloc[i]),
            ]
            row_vals_closed = row_vals + row_vals[:1]
            color = player_colors[i % len(player_colors)]
            name = str(df_bat.get("player_name", pd.Series([f"Batter {i+1}"])).iloc[i])
            parts = name.strip().split()
            short_name = f"{parts[0][0]}. {' '.join(parts[1:])}" if len(parts) >= 2 else name
            rank = df_bat.get("rank", pd.Series(range(1, len(df_bat) + 1))).iloc[i]

            ax_bat.plot(
                angles_bat_closed,
                row_vals_closed,
                color=color,
                linewidth=2.8,
                marker="o",
                markersize=5,
                markeredgecolor=RR_NAVY,
                markeredgewidth=1.2,
                label=f"#{rank} {short_name}",
                zorder=4,
            )
            ax_bat.fill(angles_bat_closed, row_vals_closed, color=color, alpha=0.20, zorder=3)

    legend_bat = ax_bat.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,
        facecolor=RR_CARD_BG,
        edgecolor=RR_GRID,
        labelcolor=RR_TEXT_LIGHT,
        fontsize=9.2,
        framealpha=0.98,
    )
    if legend_bat:
        legend_bat.get_frame().set_linewidth(1.0)
        for t in legend_bat.get_texts():
            t.set_fontweight("bold")

    # --- 2. Bowlers Radar ---
    categories_bowl = [
        "True Econ\n(TER)",
        "HL Wickets\n(Volume)",
        "Dot Ball %\n(Suppression)",
        "Clutch Delta\n(Elevation)",
        "Sample\nReliability",
    ]
    num_vars_bowl = len(categories_bowl)
    angles_bowl = np.linspace(0, 2 * np.pi, num_vars_bowl, endpoint=False).tolist()
    angles_bowl_closed = angles_bowl + angles_bowl[:1]

    ax_bowl.set_facecolor(RR_CARD_BG)
    ax_bowl.set_theta_offset(np.pi / 2)
    ax_bowl.set_theta_direction(-1)
    ax_bowl.set_xticks(angles_bowl)
    ax_bowl.set_xticklabels(categories_bowl, color=RR_NAVY, fontsize=10.0, fontweight="bold")
    ax_bowl.tick_params(pad=16)
    ax_bowl.set_ylim(0, 1.05)
    ax_bowl.set_yticks([0.25, 0.50, 0.75, 1.0])
    ax_bowl.set_yticklabels(["", "", "", ""], color=RR_TEXT_MUTED)
    ax_bowl.grid(color=RR_GRID, linestyle="--", linewidth=1.0, alpha=0.9)
    for spine in ax_bowl.spines.values():
        spine.set_color("#cbd5e1")
        spine.set_linewidth(1.2)

    ax_bowl.set_title(
        "Top 3 Bowlers Profile",
        color=RR_NAVY,
        fontsize=12.5,
        fontweight="bold",
        pad=20,
    )

    # Normalize across the full Top 10 benchmark cohort to maintain absolute scale context
    df_bowl_ref = top_bowlers.head(10).copy() if not top_bowlers.empty else pd.DataFrame()
    if not df_bowl_ref.empty:
        # Extract and normalize dimensions against top 10 benchmarks
        b1_all = _normalize_metric(df_bowl_ref.get("ter_pressure", pd.Series(range(len(df_bowl_ref)))))
        b2_all = _normalize_metric(df_bowl_ref.get("hl_wickets_pressure", df_bowl_ref.get("composite_score", pd.Series(range(len(df_bowl_ref))))))
        b3_all = _normalize_metric(df_bowl_ref.get("dot_pct_pressure", pd.Series([0.40] * len(df_bowl_ref))))
        b4_all = _normalize_metric(df_bowl_ref.get("delta_score", df_bowl_ref.get("ter_pressure", pd.Series(range(len(df_bowl_ref))))))
        b5_all = _normalize_metric(df_bowl_ref.get("n_eff_pressure", df_bowl_ref.get("composite_score", pd.Series(range(len(df_bowl_ref))))))

        df_bowl = df_bowl_ref.head(3).copy()
        for i in range(len(df_bowl)):
            row_vals = [
                float(b1_all.iloc[i]),
                float(b2_all.iloc[i]),
                float(b3_all.iloc[i]),
                float(b4_all.iloc[i]),
                float(b5_all.iloc[i]),
            ]
            row_vals_closed = row_vals + row_vals[:1]
            color = player_colors[i % len(player_colors)]
            name = str(df_bowl.get("player_name", pd.Series([f"Bowler {i+1}"])).iloc[i])
            parts = name.strip().split()
            short_name = f"{parts[0][0]}. {' '.join(parts[1:])}" if len(parts) >= 2 else name
            rank = df_bowl.get("rank", pd.Series(range(1, len(df_bowl) + 1))).iloc[i]

            ax_bowl.plot(
                angles_bowl_closed,
                row_vals_closed,
                color=color,
                linewidth=2.8,
                marker="o",
                markersize=5,
                markeredgecolor=RR_NAVY,
                markeredgewidth=1.2,
                label=f"#{rank} {short_name}",
                zorder=4,
            )
            ax_bowl.fill(angles_bowl_closed, row_vals_closed, color=color, alpha=0.20, zorder=3)

    legend_bowl = ax_bowl.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,
        facecolor=RR_CARD_BG,
        edgecolor=RR_GRID,
        labelcolor=RR_TEXT_LIGHT,
        fontsize=9.2,
        framealpha=0.98,
    )
    if legend_bowl:
        legend_bowl.get_frame().set_linewidth(1.0)
        for t in legend_bowl.get_texts():
            t.set_fontweight("bold")

    fig.suptitle("Multivariate Pressure Archetypes (Top 3 Specialists)", fontsize=13.5, fontweight="bold", color=RR_NAVY, y=0.98)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=DPI, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return output_path


def generate_all_figures(
    df_balls: pd.DataFrame,
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame,
    output_dir: str,
) -> Dict[str, str]:
    """Generates all 5 publication-grade high-resolution figures for the methodology report.

    Parameters
    ----------
    df_balls : pd.DataFrame
        Tournament ball-by-ball DataFrame containing win_prob, leverage_index, and match state.
    top_batters : pd.DataFrame
        Ranked top batters under pressure with component metrics and shrinkage weights.
    top_bowlers : pd.DataFrame
        Ranked top bowlers under pressure with component metrics and shrinkage weights.
    output_dir : str
        Target directory where high-resolution figures will be exported.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping figure keys to their generated absolute file paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    fig1_path = os.path.join(output_dir, "fig1_win_prob_curves.png")
    fig2_path = os.path.join(output_dir, "fig2_leverage_distribution.png")
    fig3_path = os.path.join(output_dir, "fig3_batters_baseline_vs_pressure.png")
    fig4_path = os.path.join(output_dir, "fig4_bowlers_baseline_vs_pressure.png")
    fig5_path = os.path.join(output_dir, "fig5_top_players_radar.png")

    plot_win_probability_curves(df_balls, fig1_path)
    plot_leverage_distribution(df_balls, fig2_path)
    plot_batters_baseline_vs_pressure(top_batters, fig3_path)
    plot_bowlers_baseline_vs_pressure(top_bowlers, fig4_path)
    plot_top_players_radar(top_batters, top_bowlers, fig5_path)

    return {
        "fig1_win_prob_curves": fig1_path,
        "fig2_leverage_distribution": fig2_path,
        "fig3_batters_baseline_vs_pressure": fig3_path,
        "fig4_bowlers_baseline_vs_pressure": fig4_path,
        "fig5_top_players_radar": fig5_path,
    }
