from cli import app


def test_cli_help_contains_main_commands(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ingest" in result.output
    assert "transcribe" in result.output
    assert "transcript" in result.output
    assert "analyze" in result.output
