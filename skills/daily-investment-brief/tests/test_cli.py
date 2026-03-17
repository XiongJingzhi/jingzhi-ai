from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_python_module_cli_emits_report():
    repo_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "skills" / "daily-investment-brief" / "src")
    env["DAILY_INVESTMENT_BRIEF_FAKE_FETCH"] = "1"
    cmd = [
        sys.executable,
        "-m",
        "daily_investment_brief.cli",
        "--asset",
        "sp500",
        "--render-mode",
        "report",
    ]
    result = subprocess.run(
        cmd,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert result.stdout.strip()
