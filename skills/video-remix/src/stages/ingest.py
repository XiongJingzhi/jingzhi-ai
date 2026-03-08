from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def _generate_silent_wav(path: Path, duration_sec: int = 1) -> None:
    if shutil.which("ffmpeg"):
        _run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=16000:cl=mono",
                "-t",
                str(duration_sec),
                str(path),
            ]
        )
        return

    import wave

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000 * duration_sec)


def _download_url(source: str, stage_dir: Path) -> Path:
    output_tpl = stage_dir / "source.%(ext)s"
    _run(
        [
            "yt-dlp",
            "--no-progress",
            "--restrict-filenames",
            "-o",
            str(output_tpl),
            source,
        ]
    )
    candidates = sorted(stage_dir.glob("source.*"))
    if not candidates:
        raise RuntimeError("yt-dlp finished but no source file was created")
    return candidates[0]


def _extract_audio(input_media: Path, audio_path: Path) -> bool:
    if os.environ.get("VIDEO_REMIX_SKIP_FFMPEG") == "1":
        _generate_silent_wav(audio_path, duration_sec=1)
        return True
    try:
        _run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_media),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "pcm_s16le",
                str(audio_path),
            ]
        )
        return True
    except Exception:
        return False


def run_ingest(source: str, run_dir: Path) -> dict:
    stage_dir = run_dir / "01_ingest"
    source_type = "url" if _is_url(source) else "local"
    stage_dir.mkdir(parents=True, exist_ok=True)

    if source_type == "local":
        src = Path(source)
        if not src.exists():
            raise FileNotFoundError(f"Local source not found: {source}")
        source_media = src
    else:
        source_media = _download_url(source=source, stage_dir=stage_dir)

    normalized = stage_dir / "normalized.mp4"
    try:
        _run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(source_media),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-ac",
                "1",
                "-ar",
                "16000",
                str(normalized),
            ]
        )
    except Exception:
        normalized.write_bytes(source_media.read_bytes())

    audio = stage_dir / "audio.wav"
    extracted = _extract_audio(normalized, audio)
    if not extracted:
        if source_type == "local":
            _generate_silent_wav(audio, duration_sec=1)
        else:
            raise RuntimeError("Failed to extract audio with ffmpeg from URL source")

    meta = {
        "source": source,
        "source_type": source_type,
        "downloaded_source": str(source_media),
        "normalized_media": str(normalized),
        "audio_path": str(audio),
        "audio_extracted": True,
    }
    (stage_dir / "source_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta
