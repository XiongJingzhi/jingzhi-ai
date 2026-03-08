from run_state import init_run
from stages.ingest import run_ingest
from stages.transcribe import run_transcribe


def test_transcribe_emits_jsonl_and_timestamped_md(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")
    run_dir = init_run(tmp_path, "run-1")
    run_ingest(source=str(source), run_dir=run_dir)

    run_transcribe(run_dir=run_dir)

    assert (run_dir / "02_transcribe" / "transcript.jsonl").exists()
    assert (run_dir / "02_transcribe" / "transcript.timestamped.md").exists()


def test_transcribe_normalizes_to_simplified_and_keeps_english(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")
    run_dir = init_run(tmp_path, "run-2")
    run_ingest(source=str(source), run_dir=run_dir)

    def fake_asr(_):
        return [
            {"start": 0.0, "end": 1.0, "text": "這是繁體中文", "confidence": 0.9},
            {"start": 1.0, "end": 2.0, "text": "hello world", "confidence": 0.9},
        ]

    run_transcribe(run_dir=run_dir, asr=fake_asr)
    content = (run_dir / "02_transcribe" / "transcript.timestamped.md").read_text(
        encoding="utf-8"
    )
    assert "这是繁体中文" in content
    assert "hello world" in content
