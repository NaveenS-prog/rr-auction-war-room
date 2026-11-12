from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json
import pandas as pd

@dataclass
class ValidationReport:
    is_valid: bool
    reconciled_match_count: int
    quarantined_matches: List[int] = field(default_factory=list)
    error_summary: Dict[str, int] = field(default_factory=dict)
    
    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "is_valid": self.is_valid,
                "reconciled_match_count": self.reconciled_match_count,
                "quarantined_matches": self.quarantined_matches,
                "error_summary": self.error_summary
            }, f, indent=2)

def run_data_validation(df: pd.DataFrame, matches: pd.DataFrame) -> ValidationReport:
    quarantined = set()
    errors: Dict[str, int] = {}
    
    # 1. Check wickets bounds (0 <= wickets_before <= 10)
    invalid_wkts = df[(df["wickets_before"] < 0) | (df["wickets_before"] > 10)]
    if not invalid_wkts.empty:
        bad_matches = invalid_wkts["match_id"].unique().tolist()
        quarantined.update(bad_matches)
        errors["wickets_out_of_bounds"] = len(bad_matches)
        
    # 2. Check legal ball bounds
    if "scheduled_innings_balls" in df.columns:
        invalid_balls = df[df["legal_balls_bowled"] > df["scheduled_innings_balls"]]
        if not invalid_balls.empty:
            bad_matches = invalid_balls["match_id"].unique().tolist()
            quarantined.update(bad_matches)
            errors["balls_bowled_exceed_scheduled"] = len(bad_matches)
            
    # 3. Check null player IDs
    null_players = df[df["striker_id"].isna() | df["bowler_id"].isna()]
    if not null_players.empty:
        bad_matches = null_players["match_id"].unique().tolist()
        quarantined.update(bad_matches)
        errors["null_player_ids"] = len(bad_matches)
        
    all_match_ids = set(matches["match_id"].unique()) if "match_id" in matches.columns else set(df["match_id"].unique())
    reconciled_count = len(all_match_ids - quarantined)
    
    return ValidationReport(
        is_valid=(len(quarantined) == 0),
        reconciled_match_count=reconciled_count,
        quarantined_matches=sorted(list(quarantined)),
        error_summary=errors
    )
