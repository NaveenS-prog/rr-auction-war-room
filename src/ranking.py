import re
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from src.models.player_ratings import FittedRatings

class RankingEngine:
    def __init__(self, eligibility: Optional[Dict[str, Any]] = None):
        self.eligibility = eligibility or {
            "min_total_balls": 100,
            "min_pressure_balls": 40,
            "min_pressure_matches": 8,
            "exclude_teams": ["Pakistan", "Pakistan A"],
            "exclusion_reason": "IPL Auction Ineligibility: BCCI regulatory policy restrictions",
        }

    def generate_leaderboard(
        self,
        ratings: FittedRatings,
        match_counts: pd.DataFrame,
        player_meta: pd.DataFrame
    ) -> pd.DataFrame:
        stats = ratings.player_stats.copy()
        if "player_id" not in stats.columns and len(ratings.player_ids) == len(stats):
            stats["player_id"] = ratings.player_ids
            
        # Ensure ratings metrics are populated in dataframe
        if "conservative_score" not in stats.columns and len(ratings.conservative_score) == len(stats):
            stats["conservative_score"] = ratings.conservative_score
        if "pressure_ability_mean" not in stats.columns and len(ratings.pressure_ability_mean) == len(stats):
            stats["pressure_ability_mean"] = ratings.pressure_ability_mean
        if "normal_ability_mean" not in stats.columns and len(ratings.normal_ability_mean) == len(stats):
            stats["normal_ability_mean"] = ratings.normal_ability_mean
        if "pressure_uplift_mean" not in stats.columns and len(ratings.pressure_uplift_mean) == len(stats):
            stats["pressure_uplift_mean"] = ratings.pressure_uplift_mean
        if "prob_positive_uplift" not in stats.columns and len(ratings.prob_positive_uplift) == len(stats):
            stats["prob_positive_uplift"] = ratings.prob_positive_uplift

        # Merge match counts
        if not match_counts.empty and "player_id" in match_counts.columns:
            stats = stats.merge(match_counts[["player_id", "pressure_matches"]], on="player_id", how="left")
        else:
            stats["pressure_matches"] = 0
        stats["pressure_matches"] = stats["pressure_matches"].fillna(0).astype(int)
        
        # Merge player metadata
        if not player_meta.empty and "player_id" in player_meta.columns:
            meta_dedup = player_meta.drop_duplicates(subset=["player_id"])
            cols_to_use = [c for c in ["player_id", "player_name", "team_name"] if c in meta_dedup.columns]
            stats = stats.merge(meta_dedup[cols_to_use], on="player_id", how="left")
        else:
            stats["player_name"] = "Player " + stats["player_id"].astype(str)
            stats["team_name"] = "Unknown"
            
        # Fill missing names
        stats["player_name"] = stats["player_name"].fillna("Player " + stats["player_id"].astype(str))
        stats["team_name"] = stats["team_name"].fillna("Unknown")
            
        # Eligibility filtering
        min_tot = self.eligibility.get("min_total_balls", 100)
        min_press = self.eligibility.get("min_pressure_balls", 40)
        min_matches = self.eligibility.get("min_pressure_matches", 8)
        exclude_teams = self.eligibility.get("exclude_teams", ["Pakistan", "Pakistan A"])
        exclusion_reason = self.eligibility.get(
            "exclusion_reason",
            "IPL Auction Ineligibility: BCCI regulatory policy restrictions"
        )

        # Identify players who have represented excluded teams/nations
        excluded_pids = set()
        if exclude_teams and not player_meta.empty and "team_name" in player_meta.columns:
            pat = "|".join([re.escape(t) for t in exclude_teams])
            mask_team = player_meta["team_name"].str.contains(pat, case=False, na=False)
            if "team_id" in player_meta.columns:
                mask_team = mask_team | player_meta["team_id"].isin([25, 341])
            excluded_pids = set(player_meta.loc[mask_team, "player_id"].dropna().astype(int))

        stats["is_auction_eligible"] = ~stats["player_id"].isin(excluded_pids)
        stats["ineligibility_reason"] = np.where(
            ~stats["is_auction_eligible"],
            exclusion_reason,
            ""
        )
        
        stats["is_eligible"] = (
            (stats["total_balls"] >= min_tot) &
            (stats["pressure_balls"] >= min_press) &
            (stats["pressure_matches"] >= min_matches) &
            stats["is_auction_eligible"]
        )
        
        # Sorting: Eligible first, sorted by conservative_score descending
        stats = stats.sort_values(
            by=["is_eligible", "conservative_score", "pressure_ability_mean", "pressure_balls"],
            ascending=[False, False, False, False]
        ).reset_index(drop=True)
        
        # Assign 1-indexed ranks to eligible players
        eligible_mask = stats["is_eligible"]
        stats["rank"] = np.nan
        stats.loc[eligible_mask, "rank"] = np.arange(1, eligible_mask.sum() + 1).astype(int)
        
        return stats

    def get_top_10(self, leaderboard: pd.DataFrame) -> pd.DataFrame:
        eligible = leaderboard[leaderboard["is_eligible"]].copy()
        top_10 = eligible.head(10).copy()
        if not top_10.empty and "rank" in top_10.columns:
            top_10["rank"] = top_10["rank"].astype(int)
        return top_10
