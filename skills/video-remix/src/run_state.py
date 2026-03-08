from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGE_DIRS = [
    "input",
    "01_ingest",
    "02_transcribe",
    "03_analyze",
    "04_style",
    "05_rewrite",
    "final",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_run(base_dir: Path | str, run_id: str) -> Path:
    base = Path(base_dir)
    run_dir = base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    for dirname in STAGE_DIRS:
        (run_dir / dirname).mkdir(parents=True, exist_ok=True)

    status_file = run_dir / "status.json"
    if not status_file.exists():
        write_status(
            run_dir,
            {
                "run_id": run_id,
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
                "mode": "auto",
                "source": None,
                "output": "both",
                "completed_stages": [],
                "paused_at": None,
            },
        )
    return run_dir


def read_status(run_dir: Path) -> dict[str, Any]:
    return json.loads((run_dir / "status.json").read_text(encoding="utf-8"))


def write_status(run_dir: Path, status: dict[str, Any]) -> None:
    status["updated_at"] = _now_iso()
    (run_dir / "status.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def mark_completed(run_dir: Path, stage_name: str) -> None:
    status = read_status(run_dir)
    completed = set(status.get("completed_stages", []))
    completed.add(stage_name)
    status["completed_stages"] = sorted(completed)
    write_status(run_dir, status)
