from pathlib import Path

import llm


def test_complete_agent_prefers_claude_then_codex_then_openai(monkeypatch):
    monkeypatch.delenv("VIDEO_REMIX_FAKE_LLM", raising=False)
    monkeypatch.setenv("VIDEO_REMIX_LLM_PROVIDER", "agent")

    calls: list[str] = []

    def fake_claude(prompt: str, cwd: Path) -> str | None:
        calls.append("claude")
        return "from claude"

    def fake_codex(prompt: str, cwd: Path) -> str | None:
        calls.append("codex")
        return "from codex"

    def fake_openai(prompt: str) -> str | None:
        calls.append("openai")
        return "from openai"

    monkeypatch.setattr(llm, "_call_claude", fake_claude, raising=False)
    monkeypatch.setattr(llm, "_call_codex", fake_codex)
    monkeypatch.setattr(llm, "_call_openai", fake_openai)

    result = llm.complete(run_dir=Path("."), task="analyze", prompt="hello")

    assert result == "from claude"
    assert calls == ["claude"]


def test_complete_claude_provider_falls_back_to_codex_then_openai(monkeypatch):
    monkeypatch.delenv("VIDEO_REMIX_FAKE_LLM", raising=False)
    monkeypatch.setenv("VIDEO_REMIX_LLM_PROVIDER", "claude")

    calls: list[str] = []

    def fake_claude(prompt: str, cwd: Path) -> str | None:
        calls.append("claude")
        return None

    def fake_codex(prompt: str, cwd: Path) -> str | None:
        calls.append("codex")
        return "from codex"

    def fake_openai(prompt: str) -> str | None:
        calls.append("openai")
        return "from openai"

    monkeypatch.setattr(llm, "_call_claude", fake_claude, raising=False)
    monkeypatch.setattr(llm, "_call_codex", fake_codex)
    monkeypatch.setattr(llm, "_call_openai", fake_openai)

    result = llm.complete(run_dir=Path("."), task="analyze", prompt="hello")

    assert result == "from codex"
    assert calls == ["claude", "codex"]
