from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable


SegmentGenerator = Callable[[Path], list[dict]]

_TRAD_TO_SIMP = str.maketrans(
    {
        "這": "这",
        "個": "个",
        "會": "会",
        "為": "为",
        "說": "说",
        "點": "点",
        "後": "后",
        "裡": "里",
        "麼": "么",
        "麼": "么",
        "麼": "么",
        "體": "体",
        "與": "与",
        "學": "学",
        "習": "习",
        "號": "号",
        "長": "长",
        "開": "开",
        "關": "关",
        "們": "们",
    }
)


def _fmt_timestamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"[{m:02d}:{s:02d}]"


def _to_simplified(text: str) -> str:
    try:
        from opencc import OpenCC  # type: ignore

        return OpenCC("t2s").convert(text)
    except Exception:
        return text.translate(_TRAD_TO_SIMP)


def _normalize_segment_text(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return t
    # Keep English as-is; normalize Chinese to simplified.
    if any("\u4e00" <= ch <= "\u9fff" for ch in t):
        return _to_simplified(t)
    return t


def _fake_asr(_: Path) -> list[dict]:
    return [
        {"start": 0.0, "end": 2.0, "text": "test transcript segment one", "confidence": 1.0},
        {"start": 2.0, "end": 4.0, "text": "test transcript segment two", "confidence": 1.0},
    ]


def _whisper_asr(audio_path: Path) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed. Run: python3 -m pip install faster-whisper"
        ) from exc

    model_size = os.environ.get("VIDEO_REMIX_WHISPER_MODEL", "small")
    device = os.environ.get("VIDEO_REMIX_WHISPER_DEVICE", "auto")
    compute_type = os.environ.get("VIDEO_REMIX_WHISPER_COMPUTE_TYPE", "int8")
    lang = os.environ.get("VIDEO_REMIX_WHISPER_LANG", "auto").strip().lower()
    language = None if lang in {"", "auto"} else lang

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments_iter, _ = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
        beam_size=5,
    )

    segments: list[dict] = []
    for seg in segments_iter:
        text = _normalize_segment_text(seg.text or "")
        if not text:
            continue
        segments.append(
            {
                "start": float(seg.start),
                "end": float(seg.end),
                "text": text,
                "confidence": None,
            }
        )

    if not segments:
        raise RuntimeError("ASR produced no speech segments")
    return segments


def run_transcribe(run_dir: Path, asr: SegmentGenerator | None = None) -> list[dict]:
    ingest_audio = run_dir / "01_ingest" / "audio.wav"
    stage_dir = run_dir / "02_transcribe"
    stage_dir.mkdir(parents=True, exist_ok=True)

    if asr is not None:
        asr_fn = asr
    elif os.environ.get("VIDEO_REMIX_FAKE_ASR") == "1":
        asr_fn = _fake_asr
    else:
        asr_fn = _whisper_asr

    segments = asr_fn(ingest_audio)
    for seg in segments:
        seg["text"] = _normalize_segment_text(str(seg.get("text", "")))

    jsonl_path = stage_dir / "transcript.jsonl"
    md_path = stage_dir / "transcript.timestamped.md"

    with jsonl_path.open("w", encoding="utf-8") as fp:
        for segment in segments:
            fp.write(json.dumps(segment, ensure_ascii=False) + "\n")

    lines = [f"{_fmt_timestamp(seg['start'])} {seg['text']}" for seg in segments]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return segments
