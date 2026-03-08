import os

import pytest
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def _set_test_mode_env(monkeypatch):
    monkeypatch.setenv("VIDEO_REMIX_FAKE_ASR", "1")
    monkeypatch.setenv("VIDEO_REMIX_SKIP_FFMPEG", "1")
    monkeypatch.setenv("VIDEO_REMIX_FAKE_TRANSCRIPT_AI", "1")
    monkeypatch.setenv("VIDEO_REMIX_FAKE_LLM", "1")


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()
