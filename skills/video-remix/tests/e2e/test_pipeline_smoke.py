from cli import app


def test_pipeline_smoke_generates_required_final_artifacts(tmp_path, runner):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")

    result = runner.invoke(
        app,
        [
            "--source",
            str(source),
            "--mode",
            "auto",
            "--output",
            "both",
            "--base-dir",
            str(tmp_path),
            "--run-id",
            "run-smoke",
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / "run-smoke" / "02_transcribe" / "transcript.timestamped.md").exists()
    assert (tmp_path / "run-smoke" / "02_transcribe" / "transcript.corrected.md").exists()
    assert (tmp_path / "run-smoke" / "final" / "script.short.md").exists()
    assert (tmp_path / "run-smoke" / "final" / "article.long.md").exists()
