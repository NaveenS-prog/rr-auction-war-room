from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import yaml

@dataclass
class PipelineConfig:
    raw_data_dir: Path
    processed_data_dir: Path
    artifacts_dir: Path
    reports_dir: Path
    split_ratios: Dict[str, float] = field(default_factory=lambda: {"train": 0.6, "val": 0.2, "test": 0.2})
    n_folds: int = 3
    eligibility: Dict[str, Any] = field(default_factory=lambda: {
        "min_total_balls": 100,
        "min_pressure_balls": 40,
        "min_pressure_matches": 8,
        "exclude_teams": ["Pakistan", "Pakistan A"],
        "exclusion_reason": "IPL Auction Ineligibility: BCCI regulatory policy restrictions",
    })
    ranking: Dict[str, float] = field(default_factory=lambda: {
        "pressure_percentile": 80.0,
        "conservative_quantile": 0.10
    })

def load_config(config_path: str = "config/settings.yaml") -> PipelineConfig:
    p = Path(config_path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    with open(p, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = yaml.safe_load(f) or {}
    
    data_cfg = data.get("data", {})
    splits_cfg = data.get("splits", {})
    eligibility_cfg = data.get("eligibility", {})
    ranking_cfg = data.get("ranking", {})
    
    return PipelineConfig(
        raw_data_dir=Path(data_cfg.get("raw_dir", "data/raw")),
        processed_data_dir=Path(data_cfg.get("processed_dir", "data/processed")),
        artifacts_dir=Path(data_cfg.get("artifacts_dir", "artifacts")),
        reports_dir=Path(data_cfg.get("reports_dir", "reports")),
        split_ratios={
            "train": float(splits_cfg.get("train", 0.6)),
            "val": float(splits_cfg.get("val", 0.2)),
            "test": float(splits_cfg.get("test", 0.2))
        },
        n_folds=int(splits_cfg.get("n_folds", 3)),
        eligibility={
            "min_total_balls": int(eligibility_cfg.get("min_total_balls", 100)),
            "min_pressure_balls": int(eligibility_cfg.get("min_pressure_balls", 40)),
            "min_pressure_matches": int(eligibility_cfg.get("min_pressure_matches", 8)),
            "exclude_teams": list(eligibility_cfg.get("exclude_teams", ["Pakistan", "Pakistan A"])),
            "exclude_player_ids": list(eligibility_cfg.get("exclude_player_ids", [1318])),
            "exclusion_reason": str(eligibility_cfg.get("exclusion_reason", "IPL Auction Ineligibility: BCCI regulatory policy restrictions and IPL retirement declarations")),
        },
        ranking={
            "pressure_percentile": float(ranking_cfg.get("pressure_percentile", 80.0)),
            "conservative_quantile": float(ranking_cfg.get("conservative_quantile", 0.10))
        }
    )
