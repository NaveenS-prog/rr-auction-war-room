# Design Document: Rajasthan Royals SupeRR Selector Season 2 — Dynamic Pressure Ranking System

**Author**: Antigravity & Lead Data Analyst  
**Date**: 2026-11-10  
**Target Deadline**: 16 November 2026, 11:59 PM IST  
**Status**: Pending Review & Builder Check  
**Repository Path**: `/home/naveen/Data/Projects/RR Hackathon`

---

## 1. Intent & The Why

### Context & Stakes
The Rajasthan Royals (RR) have launched **SupeRR Selector Season 2**, a nationwide competitive analytics challenge aimed at identifying the game's most reliable performers under high-pressure situations for the upcoming IPL 2027 auction strategy. In Season 1, the winning analytics solution led directly to RR bidding for and signing uncapped talent Vignesh Puthur at the IPL 2026 auction. 

The evaluators for this challenge include RR Head Coach **Kumar Sangakkara** and Director of Strategy and Analytics **Giles Lindsay**. To secure qualification for the top 16 in-person hackathon in Mumbai, our solution must depart from naive heuristics and deliver an elite, statistically grounded, war-room-ready framework.

### Core Objective
Build a mathematically rigorous, fully reproducible data-driven pipeline that:
1. Quantifies match context and delivery-level pressure using a dynamic **Win Probability and Leverage Index (WPA / LI)** model.
2. Evaluates batters and bowlers by comparing their high-pressure execution against their baseline using **Context-Adjusted Par Rates (True Strike Rate, True Economy, Dot% impact, and Wicket Clutchness)**.
3. Ranks the **Top 10 Batters** and **Top 10 Bowlers** under pressure using a **Dual-Axis Composite Metric** stabilized by **Empirical Bayes Shrinkage** and competition weighting.
4. Generates two corporate-grade deliverables: a publication-quality **Methodology Whitepaper (PDF)** and an **Executive Pitch Deck (Slides)**.

---

## 2. Goals, Non-Goals & Anti-Goals

### Primary Goals
- **G1**: Engineer a ball-by-ball Win Expectancy model $P(\text{Win} \mid \text{Match State})$ for IPL and T20I matches from 2022 to 2026.
- **G2**: Define situational pressure objectively via the **Leverage Index ($LI$)**, establishing $LI \ge 1.5$ as high-pressure and $LI \ge 3.0$ as extreme clutch situations.
- **G3**: Compute context-adjusted performance metrics for all qualifying players:
  - Batters: True Strike Rate ($\Delta \text{SR}$ vs phase/innings par), Dot Ball Avoidance, and WPA contribution.
  - Bowlers: True Economy Rate ($\Delta \text{ER}$ saved below par), Dot Ball % generated, and high-leverage dismissal value.
- **G4**: Isolate the **Pressure Delta** ($\text{Metric}_{\text{Pressure}} - \text{Metric}_{\text{Baseline}}$) and integrate it with absolute high-pressure skill using a 70/30 dual-axis blend.
- **G5**: Enforce statistical reliability using **Empirical Bayes shrinkage** and sample size cutoffs ($\ge 75$ pressure deliveries faced/bowled).
- **G6**: Produce verified Top 10 Batters and Top 10 Bowlers that match Unstop dropdown IDs exactly.
- **G7**: Author a reproducible, publication-grade Methodology Whitepaper and a 15–20 slide Executive Presentation Deck.

### Non-Goals
- **NG1**: Predicting player auction monetary bids or financial valuation models (the task is strictly on-field pressure performance ranking).
- **NG2**: Expanding scope beyond T20 cricket (ODIs and Tests are excluded as out of scope per tournament dataset).
- **NG3**: Building a heavyweight persistent SaaS cloud application; the deliverable requires an offline reproducible Python analytical pipeline and formatted PDF/slide artifacts.

### Anti-Goals (What would make this a failure)
- **AG1: Naive Descriptive Stats**: Relying solely on raw strike rates or economy rates without adjusting for phase (Powerplay vs Death) and match state.
- **AG2: Small-Sample Flukes**: Allowing a player who faced 12 pressure balls and hit two sixes to appear in the Top 10 (eliminated via sample floors and Bayesian shrinkage).
- **AG3: Generic LLM Synthesis**: Generating a hand-wavy methodology report without explicit mathematical equations, empirical distribution charts, and reproducibility code.
- **AG4: Mismatched IDs**: Outputting names that do not map directly to Unstop's internal player selection dropdown schema.

---

## 3. Constraints

1. **Dataset Scope**: Strictly bounded to the supplied data pack (`ball_by_ball.csv`, `matches.csv`, `playing_eleven.csv`, `competition_team_player_mapping.csv`, `teams.csv`, `competitions.csv`) covering 2022–2026 IPL and T20Is.
2. **Submission Format**: 
   - Unstop dropdowns: Rank 1 through Rank 10 for Batters, Rank 1 through Rank 10 for Bowlers.
   - Methodology document: Single uploaded document.
3. **Execution Environment**: Local Python virtual environment managed via `/usr/bin/uv` on Linux.
4. **Time Constraint**: Submissions close **16 November 2026, 11:59 PM IST**.

---

## 4. Approaches Considered & Trade-offs

During architectural brainstorming, three design alternatives were evaluated:

| Approach | Description | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Approach A (Selected)** | **Dynamic Win Probability (WPA) & Leverage Index (LI) + Empirical Bayes Shrinkage** | Aligns with professional Sabermetrics; captures actual game swings; provides sound mathematical grounding for Giles Lindsay & RR war room. | Requires training a calibrated win-expectancy model on ball-by-ball historical states. | **Chosen** |
| **Approach B** | **Contextual Expected Value (xRuns / xWickets) Residual Model** | Isolates individual execution from match context; fast to fit with gradient boosting. | Ignores whether a match is already decided (treats garbage-time boundaries equal to last-over chases). | Rejected |
| **Approach C** | **Heuristic Rule-Based Situational Matrix** | Trivial to implement; transparent rules (e.g., Death overs + margin < 24 runs). | Arbitrary boundary thresholds; lacks corporate/academic credibility; easily outperformed by probabilistic models. | Rejected |

---

## 5. System Architecture & Methodology Specification

### 5.1 Stage 1: Data Engineering & State Reconstruction
1. **Deliveries Ingestion**:
   - Parse `ball_by_ball.csv` (41MB, ~150k+ deliveries).
   - Clean extras, extract batter runs vs bowler conceded runs, flag dismissals (excluding run outs for bowler stats).
2. **Match State Tracker**:
   - Reconstruct cumulative score, wickets fallen, balls elapsed, and balls remaining per innings.
   - For 2nd innings (chases): calculate target, runs required, required run rate ($RRR$), and current run rate ($CRR$).
   - Account for revised targets via `matches.csv` (`revised_target`, `second_inn_revised_overs`).
3. **Competition Quality Rating ($W_{\text{comp}}$)**:
   - IPL matches: $W_{\text{comp}} = 1.00$.
   - T20I matches: Tiered between $0.70$ and $0.95$ based on ICC ranking tiers of participating teams (e.g., IND vs AUS = $0.95$, Full Member vs Associate = $0.70$).

### 5.2 Stage 2: Dynamic Win Expectancy & Leverage Index ($LI$)
1. **Two-Innings Unified Win Expectancy Model**:
   - **Innings 1 (Projected Score & Win Conversion)**:
     - Train an Expected Final Score model $\mathbb{E}[\text{Total Score} \mid \text{Over}, \text{Wickets Lost}, \text{Current Score}, \text{Venue Par}]$.
     - Convert projected total score to win probability $P_1(\text{Win})$ via a logistic distribution fitted against historical 1st innings scores at that venue tier.
     - Any delivery causing a large variance in projected score (e.g., top-order collapse or death-overs acceleration) generates high leverage.
   - **Innings 2 (Direct Target Chase Binary Model)**:
     - Supervised classification model (Logistic Regression with calibrated splines) trained on target chase states:
       $$S_t = \{ \text{Balls Remaining}, \text{Runs Required}, \text{Wickets Lost}, \text{Required Run Rate}, \text{Venue Par} \}$$
       producing direct chase win probability $P_2(\text{Win} \mid S_t) \in [0, 1]$.
   - This ensures **100% of deliveries across both innings are evaluated** without dropping 1st innings data.
2. **Win Probability Added ($WPA$)**:
   $$\Delta WPA_t = P_t - P_{t-1}$$
3. **Leverage Index ($LI$)**:
   - Quantified as the expected win probability swing on delivery $t$ normalized by the tournament average swing:
     $$LI_t = \frac{\mathbb{E} \left[ |\Delta WPA(S_t, \text{outcome})| \right]}{\overline{\Delta WPA}_{\text{all}}}$$
   - **Operational Thresholds**:
     - Low / Medium Pressure: $LI < 1.50$
     - **High Pressure**: $LI \ge 1.50$ (Qualifying threshold for pressure evaluation)
     - Extreme Clutch: $LI \ge 3.00$

### 5.3 Stage 3: Context-Adjusted Performance Metrics & Composite Formulas
1. **Standardized Value Metrics (Run Value Equivalence)**:
   - In modern T20 analytics, runs and wickets are converted into common **Run Value ($RV$)**: 1 wicket in high leverage $\approx 3.8$ runs; 1% dot ball reduction $\approx 0.8$ runs per 100 balls.
2. **Batting High-Pressure Index ($HP_{\text{Bat}}$)**:
   - $HP_{\text{Bat}} = 0.50 \times z(\text{True Strike Rate}) + 0.30 \times z(\text{Pressure WPA / 100}) + 0.20 \times z(\text{Dot Avoidance Rate})$
3. **Bowling High-Pressure Index ($HP_{\text{Bowl}}$)**:
   - $HP_{\text{Bowl}} = 0.45 \times z(\text{True Economy Rate}) + 0.35 \times z(\text{High-Leverage Wicket Take Rate}) + 0.20 \times z(\text{Pressure Dot}\%)$
   *(All component metrics are standardized via z-score scaling prior to weighting)*.

### 5.4 Stage 4: Baseline Definition, Pressure Delta & Empirical Bayes Shrinkage
1. **Personal Baseline Definition**:
   - Baseline is defined as the player's **overall career/dataset performance across all deliveries** ($TSR_{\text{Overall}}, TER_{\text{Overall}}$), providing a robust, non-noisy denominator.
2. **The Pressure Delta ($\Delta_{\text{Clutch}}$)**:
   $$\Delta_{\text{Bat}} = z(TSR_{\text{Pressure}}) - z(TSR_{\text{Overall}})$$
   $$\Delta_{\text{Bowl}} = z(TER_{\text{Pressure}}) - z(TER_{\text{Overall}})$$
3. **Dual-Axis Composite ($S_{\text{raw}}$)**:
   $$S_{\text{raw, Bat}} = 0.70 \times HP_{\text{Bat}} + 0.30 \times \Delta_{\text{Bat}}$$
   $$S_{\text{raw, Bowl}} = 0.70 \times HP_{\text{Bowl}} + 0.30 \times \Delta_{\text{Bowl}}$$
4. **Empirical Bayes Shrinkage & Qualification**:
   $$S_{\text{final}} = \frac{N_{\text{eff}}}{N_{\text{eff}} + M} S_{\text{raw}} + \frac{M}{N_{\text{eff}} + M} \mu_0$$
   - Effective volume $N_{\text{eff}} = \sum_{\text{balls}} W_{\text{comp}} \times \mathbb{I}(LI \ge 1.50)$, with $M = 30$ deliveries.
   - Eligibility Floor: $N_{\text{eff}} \ge 75$ pressure deliveries.
   - Role Sanity: Batters must have batted at positions 1–7 in at least 50% of matches; bowlers must average $\ge 1.5$ overs per match. True all-rounders qualifying on both floors may appear in both lists on objective merit.

### 5.5 Stage 5: Deliverables & Visualization Pipeline
1. **Python Core Pipeline**:
   - Modular scripts in `src/`:
     - `src/data_loader.py`: CSV ingestion and match state feature engineering.
     - `src/win_prob.py`: Win expectancy and Leverage Index calculation.
     - `src/metrics.py`: TSR, TER, Dot%, WPA, and Bayes shrinkage.
     - `src/rankings.py`: Generating Top 10 Batters and Top 10 Bowlers with full statistical breakdown.
2. **Corporate Whitepaper (PDF)**:
   - Executive Summary
   - Formal Mathematical Definitions ($P(\text{Win})$, $LI$, $TSR$, $TER$, Bayesian Shrinkage)
   - Methodology Visuals: Win Probability Curves, Leverage Distribution, Metric Scatter Plots
   - Top 10 Batters Dossier (individual breakdown cards, pressure stats vs baseline)
   - Top 10 Bowlers Dossier (individual breakdown cards, death over leverage stats)
   - Sensitivity, Reliability & Limitation Analysis
3. **Executive Slide Summary (Deck)**:
   - 15–20 slide high-impact deck summarizing key insights for Kumar Sangakkara & Giles Lindsay.

---

## 6. What's Left to the Builder (Implementation Decisions)

1. Selection of exact machine learning classifier for win probability (e.g. Logistic Regression with calibrated sigmoid vs LightGBM).
2. Exact ICC team ranking lookup table for 2022–2026 T20I competition weighting.
3. Aesthetic styling and toolchain for PDF compilation (Typst, WeasyPrint, or ReportLab).
4. Generation of player radar charts and Seaborn visual aesthetics.

---

## 7. Timeline & Milestones (Nov 10 – Nov 16)

- **Day 1 (Nov 10–11)**: Environment setup, data parsing, Win Probability model & Leverage Index generation.
- **Day 2 (Nov 11–12)**: End-to-end MVP rankings pipeline, baseline comparison, and empirical Bayes shrinkage.
- **Day 3 (Nov 12–13)**: Deep parameter tuning, sensitivity analysis, bootstrap confidence intervals, and outlier auditing.
- **Day 4 (Nov 13–14)**: Generate all high-res publication figures (WPA curves, radar plots, scatter matrices).
- **Day 5 (Nov 14–15)**: Author the Corporate Whitepaper PDF and Executive Slide Deck.
- **Day 6 (Nov 15–16)**: Final review, Unstop dropdown verification, package bundling, and submission readiness.
