from pathlib import Path
import pytest
from src.config import load_config, PipelineConfig

def test_load_config_defaults(tmp_path):
    yaml_content = """
    data:
      raw_dir: "/mnt/data/Projects/RR Hackathon"
      processed_dir: "data/processed"
      artifacts_dir: "artifacts"
      reports_dir: "reports"
    splits:
      train: 0.6
      val: 0.2
      test: 0.2
      n_folds: 3
    eligibility:
      min_total_balls: 100
      min_pressure_balls: 40
      min_pressure_matches: 8
    ranking:
      pressure_percentile: 80.0
      conservative_quantile: 0.10
    """
    cfg_file = tmp_path / "settings.yaml"
    cfg_file.write_text(yaml_content)
    
    cfg = load_config(str(cfg_file))
    assert isinstance(cfg, PipelineConfig)
    assert cfg.split_ratios["train"] == 0.6
    assert cfg.eligibility["min_total_balls"] == 100
    assert cfg.ranking["conservative_quantile"] == 0.10
    assert cfg.ranking["pressure_percentile"] == 80.0
