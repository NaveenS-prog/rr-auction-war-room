from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

@dataclass
class MatchSplits:
    train_matches: List[int]
    val_matches: List[int]
    test_matches: List[int]
    expanding_folds: List[Tuple[List[int], List[int]]] = field(default_factory=list)
    
    def get_split_deliveries(self, df: pd.DataFrame, split_name: str) -> pd.DataFrame:
        if split_name == "train":
            return df[df["match_id"].isin(self.train_matches)].copy()
        elif split_name == "val":
            return df[df["match_id"].isin(self.val_matches)].copy()
        elif split_name == "test":
            return df[df["match_id"].isin(self.test_matches)].copy()
        else:
            raise ValueError(f"Unknown split_name: {split_name}. Must be 'train', 'val', or 'test'.")

def generate_chronological_splits(
    df: pd.DataFrame,
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
    n_folds: int = 3
) -> MatchSplits:
    # 1. Deduplicate match_ids preserving chronological order
    if "match_date" in df.columns:
        match_meta = df[["match_id", "match_date"]].drop_duplicates()
        match_meta["match_date"] = pd.to_datetime(match_meta["match_date"], errors="coerce")
        match_meta = match_meta.sort_values(["match_date", "match_id"]).reset_index(drop=True)
        sorted_matches = match_meta["match_id"].tolist()
    else:
        sorted_matches = sorted(df["match_id"].unique().tolist())
        
    n_total = len(sorted_matches)
    n_train = int(round(n_total * train_ratio))
    n_val = int(round(n_total * val_ratio))
    
    # Ensure non-empty partitions
    n_train = max(1, min(n_train, n_total - 2))
    n_val = max(1, min(n_val, n_total - n_train - 1))
    
    train_matches = sorted_matches[:n_train]
    val_matches = sorted_matches[n_train:n_train + n_val]
    test_matches = sorted_matches[n_train + n_val:]
    
    # 2. Expanding chronological folds within the train (or train+val) period
    # We partition train_matches into n_folds + 1 slices
    expanding_folds: List[Tuple[List[int], List[int]]] = []
    dev_matches = train_matches
    if len(dev_matches) >= (n_folds + 1):
        chunks = np.array_split(dev_matches, n_folds + 1)
        for i in range(n_folds):
            train_fold = [m for c in chunks[:i + 1] for m in c.tolist()]
            val_fold = chunks[i + 1].tolist()
            if train_fold and val_fold:
                expanding_folds.append((train_fold, val_fold))
    else:
        # Fallback if too few matches
        mid = len(dev_matches) // 2
        if mid > 0:
            expanding_folds.append((dev_matches[:mid], dev_matches[mid:]))
            
    return MatchSplits(
        train_matches=train_matches,
        val_matches=val_matches,
        test_matches=test_matches,
        expanding_folds=expanding_folds
    )
