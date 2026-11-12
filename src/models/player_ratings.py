from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

@dataclass
class FittedRatings:
    player_ids: List[int]
    normal_ability_mean: np.ndarray
    pressure_ability_mean: np.ndarray
    pressure_uplift_mean: np.ndarray
    conservative_score: np.ndarray
    prob_positive_uplift: np.ndarray
    posterior_samples: Dict[int, np.ndarray] = field(default_factory=dict)
    player_stats: pd.DataFrame = field(default_factory=pd.DataFrame)

class HierarchicalPlayerModel:
    def __init__(self, n_samples: int = 1000, conservative_quantile: float = 0.10, random_state: int = 42):
        self.n_samples = n_samples
        self.conservative_quantile = conservative_quantile
        self.random_state = random_state

    def fit(
        self,
        df: pd.DataFrame,
        target_col: str = "v_bat",
        player_col: str = "striker_id",
        pressure_col: str = "is_pressure"
    ) -> FittedRatings:
        rng = np.random.default_rng(self.random_state)
        
        # Clean data
        sub = df[[player_col, pressure_col, target_col]].dropna().copy()
        sub[player_col] = sub[player_col].astype(int)
        sub[pressure_col] = sub[pressure_col].astype(int)
        sub[target_col] = sub[target_col].astype(float)
        
        # Population parameters
        y_all = sub[target_col].values
        h_all = sub[pressure_col].values
        
        normal_mask = (h_all == 0)
        pressure_mask = (h_all == 1)
        
        mu_pop = float(np.mean(y_all[normal_mask])) if normal_mask.any() else float(np.mean(y_all))
        p_mean = float(np.mean(y_all[pressure_mask])) if pressure_mask.any() else mu_pop
        beta_pop = p_mean - mu_pop
        
        sigma_e = float(np.std(y_all))
        if sigma_e < 1e-4:
            sigma_e = 1.0
        var_e = sigma_e ** 2
        
        # Player-level stats
        stats = sub.groupby(player_col).agg(
            total_balls=(target_col, "count"),
            normal_balls=(pressure_col, lambda x: (x == 0).sum()),
            pressure_balls=(pressure_col, lambda x: (x == 1).sum()),
            normal_mean=(target_col, lambda x: x[sub.loc[x.index, pressure_col] == 0].mean() if (sub.loc[x.index, pressure_col] == 0).any() else np.nan),
            pressure_mean=(target_col, lambda x: x[sub.loc[x.index, pressure_col] == 1].mean() if (sub.loc[x.index, pressure_col] == 1).any() else np.nan)
        ).reset_index()
        
        # Estimate empirical variance of player effects
        valid_normal_means = stats["normal_mean"].dropna()
        sigma_a = float(np.std(valid_normal_means)) if len(valid_normal_means) > 1 else 0.5
        sigma_a = max(sigma_a, 0.1)
        var_a = sigma_a ** 2
        
        valid_uplifts = (stats["pressure_mean"] - stats["normal_mean"]).dropna()
        sigma_d = float(np.std(valid_uplifts)) if len(valid_uplifts) > 1 else 0.5
        sigma_d = max(sigma_d, 0.1)
        var_d = sigma_d ** 2
        
        player_ids = stats[player_col].tolist()
        normal_ability_list = []
        pressure_ability_list = []
        pressure_uplift_list = []
        conservative_score_list = []
        prob_positive_list = []
        posterior_draws = {}
        
        for _, row in stats.iterrows():
            pid = int(row[player_col])
            n_0 = row["normal_balls"]
            n_1 = row["pressure_balls"]
            y_bar_0 = row["normal_mean"]
            y_bar_1 = row["pressure_mean"]
            
            # 1. Normal ability deviation a_i
            if n_0 > 0 and pd.notna(y_bar_0):
                tau_0 = n_0 / var_e
                tau_prior_a = 1.0 / var_a
                post_var_a = 1.0 / (tau_prior_a + tau_0)
                post_mu_a = post_var_a * (tau_0 * (y_bar_0 - mu_pop))
            else:
                post_var_a = var_a
                post_mu_a = 0.0
                
            # 2. Pressure deviation d_i
            if n_1 > 0 and pd.notna(y_bar_1):
                tau_1 = n_1 / var_e
                tau_prior_d = 1.0 / var_d
                post_var_d = 1.0 / (tau_prior_d + tau_1)
                # Deviation from expected (mu + a_i + beta)
                post_mu_d = post_var_d * (tau_1 * (y_bar_1 - (mu_pop + post_mu_a + beta_pop)))
            else:
                post_var_d = var_d
                post_mu_d = 0.0
                
            # Sample from posterior
            a_draws = rng.normal(post_mu_a, np.sqrt(post_var_a), size=self.n_samples)
            d_draws = rng.normal(post_mu_d, np.sqrt(post_var_d), size=self.n_samples)
            
            norm_draws = mu_pop + a_draws
            uplift_draws = beta_pop + d_draws
            press_draws = norm_draws + uplift_draws
            
            posterior_draws[pid] = press_draws
            
            normal_ability_list.append(float(np.mean(norm_draws)))
            pressure_ability_list.append(float(np.mean(press_draws)))
            pressure_uplift_list.append(float(np.mean(uplift_draws)))
            conservative_score_list.append(float(np.percentile(press_draws, self.conservative_quantile * 100.0)))
            prob_positive_list.append(float(np.mean(uplift_draws > 0)))
            
        stats["normal_ability_mean"] = normal_ability_list
        stats["pressure_ability_mean"] = pressure_ability_list
        stats["pressure_uplift_mean"] = pressure_uplift_list
        stats["conservative_score"] = conservative_score_list
        stats["prob_positive_uplift"] = prob_positive_list
        
        return FittedRatings(
            player_ids=player_ids,
            normal_ability_mean=np.array(normal_ability_list),
            pressure_ability_mean=np.array(pressure_ability_list),
            pressure_uplift_mean=np.array(pressure_uplift_list),
            conservative_score=np.array(conservative_score_list),
            prob_positive_uplift=np.array(prob_positive_list),
            posterior_samples=posterior_draws,
            player_stats=stats
        )
