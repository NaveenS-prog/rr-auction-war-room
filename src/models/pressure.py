from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

# Outcome distribution: (runs_added, is_wicket, prior_prob)
TRANSITION_OUTCOMES = [
    (0, False, 0.35),
    (1, False, 0.35),
    (2, False, 0.06),
    (4, False, 0.12),
    (6, False, 0.06),
    (0, True, 0.06),
]

class PressureEngine:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model_inn1 = LogisticRegression(max_iter=500, C=1.0, random_state=random_state)
        self.model_inn2 = LogisticRegression(max_iter=500, C=1.0, random_state=random_state)
        self.is_fitted = False
        self._leverage_cutoff = 0.05

    def _get_inn1_features(self, df: pd.DataFrame) -> pd.DataFrame:
        X = pd.DataFrame(index=df.index)
        X["runs_before"] = pd.to_numeric(df["runs_before"], errors="coerce").fillna(0.0)
        X["legal_balls_remaining"] = pd.to_numeric(df["legal_balls_remaining"], errors="coerce").fillna(60.0)
        X["wickets_remaining"] = pd.to_numeric(df["wickets_remaining"], errors="coerce").fillna(5.0)
        crr = pd.to_numeric(df.get("current_run_rate", 7.5), errors="coerce").fillna(7.5)
        X["current_run_rate"] = crr
        return X

    def _get_inn2_features(self, df: pd.DataFrame) -> pd.DataFrame:
        X = pd.DataFrame(index=df.index)
        runs_req = pd.to_numeric(df.get("runs_required", 50.0), errors="coerce").fillna(50.0)
        balls_rem = pd.to_numeric(df["legal_balls_remaining"], errors="coerce").fillna(60.0)
        wkts_rem = pd.to_numeric(df["wickets_remaining"], errors="coerce").fillna(5.0)
        overs_rem = np.maximum(balls_rem / 6.0, 0.1)
        rrr = np.clip(runs_req / overs_rem, 0.0, 36.0)
        
        # Domain feature: run deficit relative to par 8 RRR
        X["rrr"] = rrr
        X["balls_remaining"] = balls_rem
        X["wickets_remaining"] = wkts_rem
        X["run_deficit"] = runs_req - (balls_rem * (8.0 / 6.0))
        return X

    def fit(self, train_df: pd.DataFrame) -> "PressureEngine":
        valid = train_df[train_df["batting_team_won"].isin([0, 1])].copy()
        
        # Fit Innings 1 if sufficient data
        df_inn1 = valid[valid["innings"] == 1]
        if len(df_inn1) >= 10 and len(df_inn1["batting_team_won"].unique()) > 1:
            X1 = self._get_inn1_features(df_inn1)
            y1 = df_inn1["batting_team_won"].astype(int)
            self.model_inn1.fit(X1, y1)
        else:
            self.model_inn1 = None
            
        # Fit Innings 2 if sufficient data
        df_inn2 = valid[valid["innings"] == 2]
        if len(df_inn2) >= 10 and len(df_inn2["batting_team_won"].unique()) > 1:
            X2 = self._get_inn2_features(df_inn2)
            y2 = df_inn2["batting_team_won"].astype(int)
            self.model_inn2.fit(X2, y2)
        else:
            self.model_inn2 = None
            
        self.is_fitted = True
        
        # Compute baseline leverage cutoff on train_df
        leverage = self.compute_leverage_spread(train_df)
        self._leverage_cutoff = float(np.percentile(leverage, 80.0))
        return self

    def predict_win_probability(self, df: pd.DataFrame) -> np.ndarray:
        probs = np.full(len(df), 0.5)
        
        inn1_mask = (df["innings"] == 1).values
        inn2_mask = (df["innings"] == 2).values
        
        # Innings 1 predictions
        if inn1_mask.any():
            if self.model_inn1 is not None and self.is_fitted:
                X1 = self._get_inn1_features(df[inn1_mask])
                probs[inn1_mask] = self.model_inn1.predict_proba(X1)[:, 1]
            else:
                runs = pd.to_numeric(df.loc[inn1_mask, "runs_before"], errors="coerce").fillna(0)
                probs[inn1_mask] = 1.0 / (1.0 + np.exp(-(runs - 160) / 30.0))
                
        # Innings 2 predictions
        if inn2_mask.any():
            sub = df[inn2_mask].copy()
            p2 = np.full(len(sub), 0.5)
            
            runs_req = pd.to_numeric(sub.get("runs_required", 50), errors="coerce").fillna(50).values
            balls_rem = pd.to_numeric(sub["legal_balls_remaining"], errors="coerce").fillna(60).values
            wkts_rem = pd.to_numeric(sub["wickets_remaining"], errors="coerce").fillna(5).values
            
            # Boundary conditions
            already_won = runs_req <= 0
            # Mathematically impossible: need more than 6 runs per ball
            impossible = (runs_req > balls_rem * 6) | (wkts_rem <= 0) | (balls_rem <= 0)
            
            p2[already_won] = 1.0
            p2[impossible & (~already_won)] = 0.001
            
            live_mask = ~(already_won | impossible)
            if live_mask.any():
                if self.model_inn2 is not None and self.is_fitted:
                    X2 = self._get_inn2_features(sub[live_mask])
                    p2[live_mask] = self.model_inn2.predict_proba(X2)[:, 1]
                else:
                    # Calibrated heuristic: sigmoid on RRR deficit and wickets
                    overs_rem = np.maximum(balls_rem[live_mask] / 6.0, 0.1)
                    rrr = runs_req[live_mask] / overs_rem
                    # Par RRR depends on wickets in hand
                    par_rrr = 7.5 + (wkts_rem[live_mask] - 5) * 0.5
                    z = (par_rrr - rrr) * 0.4
                    p2[live_mask] = 1.0 / (1.0 + np.exp(-z))
                    
            probs[inn2_mask] = p2
            
        return np.clip(probs, 0.001, 0.999)

    def compute_leverage_spread(self, df: pd.DataFrame) -> np.ndarray:
        p_current = self.predict_win_probability(df)
        
        # Outcome transitions
        next_states_probs = []
        for runs_add, is_wkt, prob_o in TRANSITION_OUTCOMES:
            df_next = df.copy()
            df_next["legal_balls_remaining"] = np.maximum(0, df["legal_balls_remaining"] - 1)
            if "runs_required" in df.columns:
                df_next["runs_required"] = np.maximum(0, df["runs_required"] - runs_add)
                overs_rem = df_next["legal_balls_remaining"] / 6.0
                df_next["required_run_rate"] = np.where(overs_rem > 0, df_next["runs_required"] / overs_rem, 36.0)
            df_next["runs_before"] = df["runs_before"] + runs_add
            if is_wkt:
                df_next["wickets_remaining"] = np.maximum(0, df["wickets_remaining"] - 1)
                
            p_next = self.predict_win_probability(df_next)
            next_states_probs.append((p_next, prob_o))
            
        p_bar = sum(prob_o * p_next for p_next, prob_o in next_states_probs)
        var_p = sum(prob_o * ((p_next - p_bar) ** 2) for p_next, prob_o in next_states_probs)
        leverages = np.sqrt(np.maximum(0.0, var_p))
        
        # Late overs urgency weighting
        urgency = 1.0 + (120 - pd.to_numeric(df["legal_balls_remaining"], errors="coerce").fillna(60)) / 120.0
        leverages = leverages * urgency.values
        return leverages

    def compute_benchmark_pressure(self, df: pd.DataFrame) -> np.ndarray:
        balls_rem = pd.to_numeric(df["legal_balls_remaining"], errors="coerce").fillna(60.0).values
        wkts_rem = pd.to_numeric(df["wickets_remaining"], errors="coerce").fillna(5.0).values
        rrr = pd.to_numeric(df.get("required_run_rate", 8.0), errors="coerce").fillna(8.0).values
        
        rrr_factor = np.clip(rrr / 8.0, 0.5, 3.0)
        wkt_factor = np.clip(10.0 / np.maximum(wkts_rem, 1.0), 1.0, 3.0)
        phase_factor = (120.0 - balls_rem) / 120.0
        
        score = (rrr_factor * 0.4) + (wkt_factor * 0.3) + (phase_factor * 0.3)
        return score

    def classify_pressure(self, df: pd.DataFrame, percentile: float = 80.0) -> np.ndarray:
        leverage = self.compute_leverage_spread(df)
        cutoff = np.percentile(leverage, percentile) if len(leverage) > 0 else 0.05
        return (leverage >= cutoff)
