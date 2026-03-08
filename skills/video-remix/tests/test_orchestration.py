import json

from cli import app


def test_step_mode_pauses_at_checkpoints(tmp_path, runner):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")

    result = runner.invoke(
        app,
        [
            "--source",
            str(source),
            "--mode",
            "step",
            "--output",
            "both",
            "--base-dir",
            str(tmp_path),
            "--run-id",
            "run-step",
        ],
    )

    assert result.exit_code == 0
    status = json.loads((tmp_path / "run-step" / "status.json").read_text())
    assert status["paused_at"] == "after_transcribe"

    resume = runner.invoke(
        app,
        ["resume", "--run", "run-step", "--base-dir", str(tmp_path)],
    )
    assert resume.exit_code == 0
