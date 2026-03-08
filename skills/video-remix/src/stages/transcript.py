from __future__ import annotations

import json
import os
from pathlib import Path

from llm import complete, load_prompt
from stages.transcribe import _normalize_segment_text


def _parse_timestamped_lines(content: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if "]" in line and line.startswith("["):
            ts, text = line.split("]", 1)
            rows.append((ts + "]", text.strip()))
        else:
            rows.append(("", line))
    return rows


def _heuristic_fix(text: str) -> str:
    fixed = text.strip().replace(",", "，").replace("??", "？").replace("。。", "。")
    return _normalize_segment_text(fixed)


def _llm_correct(lines: list[str], run_dir: Path) -> list[str] | None:
    if os.environ.get("VIDEO_REMIX_FAKE_TRANSCRIPT_AI") == "1":
        return [_heuristic_fix(x) for x in lines]

    prompt_tpl = load_prompt(run_dir, "transcript_correction.md")
    prompt = f"{prompt_tpl}\n\n输入：\n{json.dumps(lines, ensure_ascii=False)}"
    content = complete(run_dir=run_dir, task="transcript_correct", prompt=prompt)
    if not content:
        return None

    try:
        corrected = json.loads(content)
        if not isinstance(corrected, list) or len(corrected) != len(lines):
            return None
        return [_normalize_segment_text(str(x).strip()) for x in corrected]
    except json.JSONDecodeError:
        return None


def run_transcript(run_dir: Path) -> Path:
    transcribe_file = run_dir / "02_transcribe" / "transcript.timestamped.md"
    corrected_file = run_dir / "02_transcribe" / "transcript.corrected.md"

    raw = transcribe_file.read_text(encoding="utf-8")
    rows = _parse_timestamped_lines(raw)
    input_lines = [text for _, text in rows]

    corrected_lines = _llm_correct(input_lines, run_dir=run_dir)
    if corrected_lines is None:
        corrected_lines = [_heuristic_fix(x) for x in input_lines]

    merged: list[str] = []
    for idx, (ts, _) in enumerate(rows):
        text = corrected_lines[idx] if idx < len(corrected_lines) else ""
        if ts:
            merged.append(f"{ts} {text}".rstrip())
        else:
            merged.append(text)

    corrected_file.write_text("\n".join(merged) + "\n", encoding="utf-8")
    return corrected_file
