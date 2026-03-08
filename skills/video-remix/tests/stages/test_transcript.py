from run_state import init_run
from stages.ingest import run_ingest
from stages.transcribe import run_transcribe
from stages.transcript import run_transcript


def test_transcript_emits_corrected_markdown(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")

    run_dir = init_run(tmp_path, "run-1")
    run_ingest(source=str(source), run_dir=run_dir)
    run_transcribe(run_dir=run_dir)

    run_transcript(run_dir=run_dir)

    corrected = run_dir / "02_transcribe" / "transcript.corrected.md"
    assert corrected.exists()
    assert corrected.read_text(encoding="utf-8").strip()
