from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier

@dataclass
class BattingExpectations:
    expected_runs: np.ndarray
    dismissal_prob: np.ndarray

@dataclass
class BowlingExpectations:
    expected_conceded: np.ndarray
    wicket_prob: np.ndarray

class ExpectationModelPipeline:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model_bat_runs = HistGradientBoostingRegressor(
            max_iter=100, max_depth=5, min_samples_leaf=20, random_state=random_state
        )
        self.model_bat_dismissal = HistGradientBoostingClassifier(
            max_iter=100, max_depth=4, min_samples_leaf=20, loss="log_loss", random_state=random_state
        )
        self.model_bowl_runs = HistGradientBoostingRegressor(
            max_iter=100, max_depth=5, min_samples_leaf=20, random_state=random_state
        )
        self.model_bowl_wicket = HistGradientBoostingClassifier(
            max_iter=100, max_depth=4, min_samples_leaf=20, loss="log_loss", random_state=random_state
        )
        self.is_fitted = False
        self.bowler_priors = {}
        self.batter_priors = {}
        self.global_bowler_econ = 1.30
        self.global_bowler_wkt = 0.05
        self.global_batter_sr = 1.25
        self.global_batter_dis = 0.05
        self._default_dismissal_rate = 0.05
        self._default_wicket_rate = 0.05

    def _compute_priors(self, train_df: pd.DataFrame) -> None:
        """Computes Empirical Bayes baseline priors for opposing players strictly from training data."""
        if "bowler_id" in train_df.columns:
            wides = pd.to_numeric(train_df.get("wides", 0), errors="coerce").fillna(0)
            no_balls = pd.to_numeric(train_df.get("no_balls", 0), errors="coerce").fillna(0)
            runs_off_bat = pd.to_numeric(train_df.get("runs_off_bat", 0), errors="coerce").fillna(0)
            bowler_conceded = runs_off_bat + wides + no_balls
            bowler_wkts = pd.to_numeric(train_df.get("bowler_credited_wicket", 0), errors="coerce").fillna(0)
            
            b_df = pd.DataFrame({
                "bowler_id": pd.to_numeric(train_df["bowler_id"], errors="coerce").fillna(-1).astype(int),
                "conceded": bowler_conceded,
                "wkts": bowler_wkts,
            })
            b_agg = b_df.groupby("bowler_id").agg(
                balls=("conceded", "count"),
                conceded=("conceded", "sum"),
                wkts=("wkts", "sum")
            ).reset_index()
            
            total_balls = b_agg["balls"].sum()
            self.global_bowler_econ = float(b_agg["conceded"].sum() / max(1, total_balls))
            self.global_bowler_wkt = float(b_agg["wkts"].sum() / max(1, total_balls))
            
            # Empirical Bayes prior shrinkage with 60 pseudo-balls (10 overs)
            m_balls = 60.0
            b_agg["prior_econ"] = (b_agg["conceded"] + m_balls * self.global_bowler_econ) / (b_agg["balls"] + m_balls)
            b_agg["prior_wkt"] = (b_agg["wkts"] + m_balls * self.global_bowler_wkt) / (b_agg["balls"] + m_balls)
            self.bowler_priors = b_agg.set_index("bowler_id")[["prior_econ", "prior_wkt"]].to_dict(orient="index")

        if "striker_id" in train_df.columns:
            legal_mask = train_df.get("is_legal_delivery", pd.Series([True] * len(train_df), index=train_df.index)).astype(bool)
            bat_train = train_df[legal_mask] if legal_mask.sum() > 0 else train_df
            bat_runs = pd.to_numeric(bat_train.get("runs_off_bat", 0), errors="coerce").fillna(0)
            bat_dis = pd.to_numeric(bat_train.get("striker_dismissed", 0), errors="coerce").fillna(0)
            
            bat_df = pd.DataFrame({
                "striker_id": pd.to_numeric(bat_train["striker_id"], errors="coerce").fillna(-1).astype(int),
                "runs": bat_runs,
                "dis": bat_dis
            })
            bat_agg = bat_df.groupby("striker_id").agg(
                balls=("runs", "count"),
                runs=("runs", "sum"),
                dis=("dis", "sum")
            ).reset_index()
            
            tot_bat_balls = bat_agg["balls"].sum()
            self.global_batter_sr = float(bat_agg["runs"].sum() / max(1, tot_bat_balls))
            self.global_batter_dis = float(bat_agg["dis"].sum() / max(1, tot_bat_balls))
            
            m_balls = 60.0
            bat_agg["prior_sr"] = (bat_agg["runs"] + m_balls * self.global_batter_sr) / (bat_agg["balls"] + m_balls)
            bat_agg["prior_dis"] = (bat_agg["dis"] + m_balls * self.global_batter_dis) / (bat_agg["balls"] + m_balls)
            self.batter_priors = bat_agg.set_index("striker_id")[["prior_sr", "prior_dis"]].to_dict(orient="index")

    def _extract_base_features(self, df: pd.DataFrame) -> pd.DataFrame:
        X = pd.DataFrame(index=df.index)
        X["innings"] = pd.to_numeric(df.get("innings", 1), errors="coerce").fillna(1.0).astype(float)
        X["legal_balls_remaining"] = pd.to_numeric(df.get("legal_balls_remaining", 60.0), errors="coerce").fillna(60.0)
        X["wickets_remaining"] = pd.to_numeric(df.get("wickets_remaining", 5.0), errors="coerce").fillna(5.0)
        X["runs_before"] = pd.to_numeric(df.get("runs_before", 0.0), errors="coerce").fillna(0.0)
        
        # Innings phase: Death (<=30 balls), Powerplay (>84 balls)
        X["phase_death"] = (X["legal_balls_remaining"] <= 30).astype(float)
        X["phase_powerplay"] = (X["legal_balls_remaining"] > 84).astype(float)
        
        # Rates
        if "current_run_rate" in df.columns:
            X["current_run_rate"] = pd.to_numeric(df["current_run_rate"], errors="coerce").fillna(7.5)
        else:
            X["current_run_rate"] = 7.5
            
        if "required_run_rate" in df.columns:
            rrr = pd.to_numeric(df["required_run_rate"], errors="coerce")
            X["required_run_rate"] = np.where(X["innings"] == 1, 0.0, rrr.fillna(8.0))
        else:
            X["required_run_rate"] = 0.0
            
        # Matchup Context: Batting Order and Bowling Type
        if "batting_order" in df.columns:
            order = pd.to_numeric(df["batting_order"], errors="coerce").fillna(4.0).clip(1, 11)
        else:
            order = pd.Series(4.0, index=df.index)
        X["batting_order"] = order
        
        if "pace_or_spin" in df.columns:
            p_or_s = df["pace_or_spin"].astype(str).str.lower()
            X["is_spin"] = p_or_s.str.contains("spin").astype(float)
        else:
            X["is_spin"] = 0.0
        return X

    def _extract_batting_features(self, df: pd.DataFrame) -> pd.DataFrame:
        X = self._extract_base_features(df)
        if "bowler_id" in df.columns:
            bowler_ids = pd.to_numeric(df["bowler_id"], errors="coerce").fillna(-1).astype(int)
            X["opp_bowler_econ"] = [self.bowler_priors.get(bid, {}).get("prior_econ", self.global_bowler_econ) for bid in bowler_ids]
            X["opp_bowler_wkt"] = [self.bowler_priors.get(bid, {}).get("prior_wkt", self.global_bowler_wkt) for bid in bowler_ids]
        else:
            X["opp_bowler_econ"] = self.global_bowler_econ
            X["opp_bowler_wkt"] = self.global_bowler_wkt
        return X

    def _extract_bowling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        X = self._extract_base_features(df)
        if "striker_id" in df.columns:
            striker_ids = pd.to_numeric(df["striker_id"], errors="coerce").fillna(-1).astype(int)
            X["opp_batter_sr"] = [self.batter_priors.get(sid, {}).get("prior_sr", self.global_batter_sr) for sid in striker_ids]
            X["opp_batter_dis"] = [self.batter_priors.get(sid, {}).get("prior_dis", self.global_batter_dis) for sid in striker_ids]
        else:
            X["opp_batter_sr"] = self.global_batter_sr
            X["opp_batter_dis"] = self.global_batter_dis
        return X

    def _extract_features(self, df: pd.DataFrame, for_bowling: bool = False) -> pd.DataFrame:
        """Unified feature extractor maintaining backwards compatibility."""
        if for_bowling:
            return self._extract_bowling_features(df)
        return self._extract_batting_features(df)

    def fit(self, train_df: pd.DataFrame) -> "ExpectationModelPipeline":
        self._compute_priors(train_df)
        
        # 1. Batting models: trained on legal deliveries with opponent bowler difficulty
        legal_mask = train_df.get("is_legal_delivery", pd.Series([True] * len(train_df), index=train_df.index)).astype(bool)
        if legal_mask.sum() == 0:
            legal_mask = pd.Series([True] * len(train_df), index=train_df.index)
            
        bat_train = train_df[legal_mask]
        X_bat = self._extract_batting_features(bat_train)
        y_bat_runs = pd.to_numeric(bat_train.get("runs_off_bat", 0), errors="coerce").fillna(0.0).astype(float)
        y_bat_dismissal = pd.to_numeric(bat_train.get("striker_dismissed", 0), errors="coerce").fillna(0).astype(int)
        
        self.model_bat_runs.fit(X_bat, y_bat_runs)
        if len(y_bat_dismissal.unique()) > 1:
            self.model_bat_dismissal.fit(X_bat, y_bat_dismissal)
        else:
            self.model_bat_dismissal = None
            self._default_dismissal_rate = float(y_bat_dismissal.mean()) if len(y_bat_dismissal) > 0 else 0.05
            
        # 2. Bowling models: trained on all deliveries with opponent batter potency
        X_bowl = self._extract_bowling_features(train_df)
        wides = pd.to_numeric(train_df.get("wides", 0), errors="coerce").fillna(0)
        no_balls = pd.to_numeric(train_df.get("no_balls", 0), errors="coerce").fillna(0)
        runs_off_bat = pd.to_numeric(train_df.get("runs_off_bat", 0), errors="coerce").fillna(0)
        bowler_conceded = runs_off_bat + wides + no_balls
        
        y_bowl_runs = bowler_conceded.astype(float)
        y_bowl_wicket = pd.to_numeric(train_df.get("bowler_credited_wicket", 0), errors="coerce").fillna(0).astype(int)
        
        self.model_bowl_runs.fit(X_bowl, y_bowl_runs)
        if len(y_bowl_wicket.unique()) > 1:
            self.model_bowl_wicket.fit(X_bowl, y_bowl_wicket)
        else:
            self.model_bowl_wicket = None
            self._default_wicket_rate = float(y_bowl_wicket.mean()) if len(y_bowl_wicket) > 0 else 0.05
            
        self.is_fitted = True
        return self

    def predict_batting_expectations(self, df: pd.DataFrame) -> BattingExpectations:
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before calling predict.")
        X = self._extract_batting_features(df)
        
        pred_runs = np.maximum(0.0, self.model_bat_runs.predict(X))
        
        if self.model_bat_dismissal is not None:
            pred_prob = self.model_bat_dismissal.predict_proba(X)[:, 1]
        else:
            pred_prob = np.full(len(df), self._default_dismissal_rate)
            
        return BattingExpectations(expected_runs=pred_runs, dismissal_prob=pred_prob)

    def predict_bowling_expectations(self, df: pd.DataFrame) -> BowlingExpectations:
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before calling predict.")
        X = self._extract_bowling_features(df)
        
        pred_conceded = np.maximum(0.0, self.model_bowl_runs.predict(X))
        
        if self.model_bowl_wicket is not None:
            pred_wkt_prob = self.model_bowl_wicket.predict_proba(X)[:, 1]
        else:
            pred_wkt_prob = np.full(len(df), self._default_wicket_rate)
            
        return BowlingExpectations(expected_conceded=pred_conceded, wicket_prob=pred_wkt_prob)
