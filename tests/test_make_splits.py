import pandas as pd
import pytest
from src.make_splits import generate_chronological_splits, MatchSplits

def test_chronological_splits_no_overlap_and_strictly_ordered():
    # 10 matches on 10 consecutive days
    data = []
    for m in range(1, 11):
        data.append({
            "match_id": m,
            "match_date": f"2022-05-{m:02d}",
            "delivery_id": m * 100
        })
    df = pd.DataFrame(data)
    
    splits = generate_chronological_splits(df, train_ratio=0.6, val_ratio=0.2, n_folds=2)
    
    # 6 train (1-6), 2 val (7-8), 2 test (9-10)
    assert splits.train_matches == [1, 2, 3, 4, 5, 6]
    assert splits.val_matches == [7, 8]
    assert splits.test_matches == [9, 10]
    
    # Expanding folds verification:
    # fold 1: earlier train -> next block
    # fold 2: earlier train + next block -> following block
    assert len(splits.expanding_folds) == 2
    train_f1, val_f1 = splits.expanding_folds[0]
    train_f2, val_f2 = splits.expanding_folds[1]
    
    assert max(train_f1) < min(val_f1)
    assert max(train_f2) < min(val_f2)
    assert set(train_f1).issubset(set(train_f2))
    
    # Check helper method
    train_df = splits.get_split_deliveries(df, "train")
    assert set(train_df["match_id"].unique()) == set([1, 2, 3, 4, 5, 6])
