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

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        X = pd.DataFrame(index=df.index)
        X["innings"] = df["innings"].astype(float)
        X["legal_balls_remaining"] = pd.to_numeric(df["legal_balls_remaining"], errors="coerce").fillna(60.0)
        X["wickets_remaining"] = pd.to_numeric(df["wickets_remaining"], errors="coerce").fillna(5.0)
        X["runs_before"] = pd.to_numeric(df["runs_before"], errors="coerce").fillna(0.0)
        
        # Innings phase: 0=Powerplay (balls_rem > 84), 1=Middle (30-84), 2=Death (<30)
        X["phase_death"] = (X["legal_balls_remaining"] <= 30).astype(float)
        X["phase_powerplay"] = (X["legal_balls_remaining"] > 84).astype(float)
        
        # Rates
        if "current_run_rate" in df.columns:
            X["current_run_rate"] = pd.to_numeric(df["current_run_rate"], errors="coerce").fillna(7.5)
        else:
            X["current_run_rate"] = 7.5
            
        if "required_run_rate" in df.columns:
            # Leave NaNs for HistGradientBoosting native handling or fill 0.0 for 1st innings
            rrr = pd.to_numeric(df["required_run_rate"], errors="coerce")
            X["required_run_rate"] = np.where(X["innings"] == 1, 0.0, rrr.fillna(8.0))
        else:
            X["required_run_rate"] = 0.0
            
        return X

    def fit(self, train_df: pd.DataFrame) -> "ExpectationModelPipeline":
        # 1. Batting models: trained on legal deliveries
        legal_mask = train_df["is_legal_delivery"].astype(bool)
        if legal_mask.sum() == 0:
            legal_mask = pd.Series([True] * len(train_df), index=train_df.index)
            
        bat_train = train_df[legal_mask]
        X_bat = self._extract_features(bat_train)
        y_bat_runs = bat_train["runs_off_bat"].astype(float)
        y_bat_dismissal = bat_train["striker_dismissed"].astype(int)
        
        self.model_bat_runs.fit(X_bat, y_bat_runs)
        if len(y_bat_dismissal.unique()) > 1:
            self.model_bat_dismissal.fit(X_bat, y_bat_dismissal)
        else:
            # Degenerate case fallback
            self.model_bat_dismissal = None
            self._default_dismissal_rate = float(y_bat_dismissal.mean())
            
        # 2. Bowling models: trained on all deliveries
        X_bowl = self._extract_features(train_df)
        wides = pd.to_numeric(train_df.get("wides", 0), errors="coerce").fillna(0)
        no_balls = pd.to_numeric(train_df.get("no_balls", 0), errors="coerce").fillna(0)
        runs_off_bat = pd.to_numeric(train_df.get("runs_off_bat", 0), errors="coerce").fillna(0)
        bowler_conceded = runs_off_bat + wides + no_balls
        
        y_bowl_runs = bowler_conceded.astype(float)
        y_bowl_wicket = train_df["bowler_credited_wicket"].astype(int)
        
        self.model_bowl_runs.fit(X_bowl, y_bowl_runs)
        if len(y_bowl_wicket.unique()) > 1:
            self.model_bowl_wicket.fit(X_bowl, y_bowl_wicket)
        else:
            self.model_bowl_wicket = None
            self._default_wicket_rate = float(y_bowl_wicket.mean())
            
        self.is_fitted = True
        return self

    def predict_batting_expectations(self, df: pd.DataFrame) -> BattingExpectations:
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before calling predict.")
        X = self._extract_features(df)
        
        pred_runs = np.maximum(0.0, self.model_bat_runs.predict(X))
        
        if self.model_bat_dismissal is not None:
            pred_prob = self.model_bat_dismissal.predict_proba(X)[:, 1]
        else:
            pred_prob = np.full(len(df), self._default_dismissal_rate)
            
        return BattingExpectations(expected_runs=pred_runs, dismissal_prob=pred_prob)

    def predict_bowling_expectations(self, df: pd.DataFrame) -> BowlingExpectations:
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before calling predict.")
        X = self._extract_features(df)
        
        pred_conceded = np.maximum(0.0, self.model_bowl_runs.predict(X))
        
        if self.model_bowl_wicket is not None:
            pred_wkt_prob = self.model_bowl_wicket.predict_proba(X)[:, 1]
        else:
            pred_wkt_prob = np.full(len(df), self._default_wicket_rate)
            
        return BowlingExpectations(expected_conceded=pred_conceded, wicket_prob=pred_wkt_prob)
