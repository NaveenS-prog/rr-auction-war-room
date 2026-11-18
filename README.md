# Rajasthan Royals — SupeRR Selector Season 2
## High-Leverage Pressure Reliability Platform | IPL 2027 Auction War Room

[![Vercel Production](https://img.shields.io/badge/Vercel-Production%20Live-000000?style=flat&logo=vercel)](https://rr-auction-war-room.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![WCAG 2.1 AA](https://img.shields.io/badge/A11y-WCAG%202.1%20AA-047857.svg)](#)

> **Executive Analytics & Strategy Briefing**  
> Prepared for Kumar Sangakkara, Giles Lindsay, and Zubin Bharucha.  
> **Live Console**: [https://rr-auction-war-room.vercel.app](https://rr-auction-war-room.vercel.app)

---

### 1. Overview
The **SupeRR Selector High-Leverage Pressure Reliability Platform** isolates clutch variance in T20 cricket from canonical ball-by-ball tracking data (200,999 deliveries across 867 IPL & T20I matches, 2022–2026). 

Standard aggregate cricket statistics fail during high-pressure auction decisions due to small-sample noise, survivorship bias, and context conflation. This engine isolates context-neutral player ability under pressure using:
1. **Dynamic Leverage Weighting**: Ball-by-ball leverage calculation $L(s) = \sqrt{\sum P(o)[p(s_o) - \bar{p}(s)]^2} \times \text{urgency}$.
2. **Hierarchical Empirical Bayes Shrinkage**: Shrinks small-sample extremes toward discipline priors.
3. **Conservative Quantile Regularization ($Q_{0.10}$)**: Ranks players by their 10th percentile Bayesian credibility bound ($\mu_i - 1.282\sigma_i$), penalizing high posterior uncertainty.

---

### 2. Architecture & Modules
- **Roster Evaluation Matrix (`/`)**: Full 20-player audited leaderboard with live search, discipline filters (Batter/Bowler), and master-detail scouting dossiers.
- **Bivariate Performance Map**: Scatter matrix contrasting pressure ability ($\mu_{\text{press}}$) against normal par ($\mu_{\text{norm}}$) across 4 tactical quadrants.
- **Pairwise Scouting Dossier**: Side-by-side head-to-head comparison sheets with statistical deltas and Bayesian posterior curves.
- **Auction Allocation Ledger**: Interactive squad builder enforcing IPL roster constraints ($\le 4$ Overseas, budget caps in ₹ Cr, cumulative reliability floor).
- **Methodology & Empirical Verification**: Out-of-sample holdout proof (-19.3% RMSE for batters, -15.1% RMSE for bowlers) and mathematical formulations.

---

### 3. Deployment
- **Platform**: Vercel Global Edge Network
- **Production URL**: [https://rr-auction-war-room.vercel.app](https://rr-auction-war-room.vercel.app)
- **Root Directory**: `dashboard/`
- **Continuous Deployment**: Automatic preview and production deployments triggered on push to `main`.
