import subprocess
import sys
from pathlib import Path

def test_pipeline_dry_run_or_help():
    repo_root = str(Path(__file__).resolve().parent.parent)
    result = subprocess.run(
        [sys.executable, "-m", "src.pipeline", "--help"],
        cwd=repo_root,
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "SupeRR Selector Pressure Pipeline" in result.stdout
