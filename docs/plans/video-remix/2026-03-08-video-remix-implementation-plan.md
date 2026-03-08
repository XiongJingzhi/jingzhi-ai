# Video Remix Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a resumable hybrid pipeline skill that ingests local/URL videos and outputs timestamped transcript, short script, and long article with style transfer.

**Architecture:** Use a Python CLI orchestrator (`video-remix`) with stage modules (`ingest`, `transcribe`, `analyze`, `style`, `rewrite`) and run-state persistence under `runs/<run_id>/`. Auto mode runs all stages; step mode pauses at review checkpoints and resumes with run id.

**Tech Stack:** Python 3.11, ffmpeg, yt-dlp, faster-whisper (or equivalent ASR), pytest.

---

### Task 1: Project Skeleton + CLI Entry

**Files:**
- Create: `video-remix/pyproject.toml`
- Create: `video-remix/src/video_remix/cli.py`
- Create: `video-remix/src/video_remix/__init__.py`
- Create: `video-remix/tests/test_cli_help.py`

**Step 1: Write the failing test**

```python
from video_remix.cli import app

def test_cli_help_contains_main_commands(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ingest" in result.output
    assert "transcribe" in result.output
    assert "analyze" in result.output
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/test_cli_help.py -v`
Expected: FAIL due to missing CLI app.

**Step 3: Write minimal implementation**

```python
import typer
app = typer.Typer()
app.command()(lambda: None)
```

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/test_cli_help.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/pyproject.toml video-remix/src/video_remix video-remix/tests/test_cli_help.py
git commit -m "feat: bootstrap video-remix cli skeleton"
```

### Task 2: Run State and Directory Contract

**Files:**
- Create: `video-remix/src/video_remix/run_state.py`
- Create: `video-remix/tests/test_run_state.py`

**Step 1: Write the failing test**

```python
def test_init_run_creates_stage_dirs(tmp_path):
    # expects runs/<run_id>/01_ingest ... /final
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/test_run_state.py -v`
Expected: FAIL because run-state helper not implemented.

**Step 3: Write minimal implementation**

Implement `init_run(base_dir, run_id)` that creates required stage folders and `status.json`.

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/test_run_state.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/src/video_remix/run_state.py video-remix/tests/test_run_state.py
git commit -m "feat: add run initialization and status persistence"
```

### Task 3: Ingest Stage (Local + URL)

**Files:**
- Create: `video-remix/src/video_remix/stages/ingest.py`
- Create: `video-remix/tests/stages/test_ingest.py`

**Step 1: Write the failing test**

```python
def test_ingest_local_source_writes_source_meta(tmp_path):
    # asserts source_meta.json has source_type=local
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/stages/test_ingest.py -v`
Expected: FAIL with missing stage function.

**Step 3: Write minimal implementation**

Implement local-file path first; for URL path, add downloader adapter interface with TODO fallback.

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/stages/test_ingest.py -v`
Expected: PASS for local source path.

**Step 5: Commit**

```bash
git add video-remix/src/video_remix/stages/ingest.py video-remix/tests/stages/test_ingest.py
git commit -m "feat: implement ingest stage with source metadata"
```

### Task 4: Transcribe Stage with Timestamped Output

**Files:**
- Create: `video-remix/src/video_remix/stages/transcribe.py`
- Create: `video-remix/tests/stages/test_transcribe.py`

**Step 1: Write the failing test**

```python
def test_transcribe_emits_jsonl_and_timestamped_md(tmp_path):
    # expects transcript.jsonl and transcript.timestamped.md
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/stages/test_transcribe.py -v`
Expected: FAIL because outputs are missing.

**Step 3: Write minimal implementation**

Add adapter-based ASR call; write normalized segment rows with `[mm:ss]` markdown lines.

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/stages/test_transcribe.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/src/video_remix/stages/transcribe.py video-remix/tests/stages/test_transcribe.py
git commit -m "feat: add timestamped transcription outputs"
```

### Task 5: Analyze Stage (Structure/Arguments/Evidence/Rhythm)

**Files:**
- Create: `video-remix/src/video_remix/stages/analyze.py`
- Create: `video-remix/tests/stages/test_analyze.py`

**Step 1: Write the failing test**

```python
def test_analysis_contains_required_sections(tmp_path):
    # must include sections: topic, arguments, evidence, rhythm
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/stages/test_analyze.py -v`
Expected: FAIL because required sections absent.

**Step 3: Write minimal implementation**

Generate `analysis.md` from transcript + LLM prompt template with required section headings.

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/stages/test_analyze.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/src/video_remix/stages/analyze.py video-remix/tests/stages/test_analyze.py
git commit -m "feat: implement analysis stage with mandatory structure"
```

### Task 6: Style Profile Stage (Samples + Rules)

**Files:**
- Create: `video-remix/src/video_remix/stages/style.py`
- Create: `video-remix/tests/stages/test_style.py`

**Step 1: Write the failing test**

```python
def test_style_profile_contains_tone_lexicon_forbidden(tmp_path):
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/stages/test_style.py -v`
Expected: FAIL due to missing style profile generation.

**Step 3: Write minimal implementation**

Create `style_profile.json` with keys: `tone`, `sentence_length`, `lexicon`, `forbidden`, `pacing`.

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/stages/test_style.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/src/video_remix/stages/style.py video-remix/tests/stages/test_style.py
git commit -m "feat: add style profile extraction from samples and rules"
```

### Task 7: Rewrite Stage (Dual Output + Style Diff)

**Files:**
- Create: `video-remix/src/video_remix/stages/rewrite.py`
- Create: `video-remix/tests/stages/test_rewrite.py`

**Step 1: Write the failing test**

```python
def test_rewrite_outputs_short_long_and_diff(tmp_path):
    # expects script.short.md, article.long.md, diff.style-applied.md
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/stages/test_rewrite.py -v`
Expected: FAIL due to missing files.

**Step 3: Write minimal implementation**

Generate short/long outputs and one style-change explanation file.

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/stages/test_rewrite.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/src/video_remix/stages/rewrite.py video-remix/tests/stages/test_rewrite.py
git commit -m "feat: add dual-output rewrite with style diff"
```

### Task 8: Orchestrator Modes (auto/step/resume)

**Files:**
- Modify: `video-remix/src/video_remix/cli.py`
- Create: `video-remix/tests/test_orchestration.py`

**Step 1: Write the failing test**

```python
def test_step_mode_pauses_at_checkpoints(tmp_path):
    # verifies pause after transcribe/analyze/pre-rewrite
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/test_orchestration.py -v`
Expected: FAIL because pause/resume not implemented.

**Step 3: Write minimal implementation**

Wire stage execution graph with mode switch and `resume --run <run_id>` support.

**Step 4: Run test to verify it passes**

Run: `cd video-remix && pytest tests/test_orchestration.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/src/video_remix/cli.py video-remix/tests/test_orchestration.py
git commit -m "feat: implement hybrid orchestration with resume"
```

### Task 9: End-to-End Smoke + Documentation

**Files:**
- Create: `video-remix/tests/e2e/test_pipeline_smoke.py`
- Create: `video-remix/README.md`

**Step 1: Write the failing test**

```python
def test_pipeline_smoke_generates_required_final_artifacts(tmp_path):
    # end-to-end on fixture input
    ...
```

**Step 2: Run test to verify it fails**

Run: `cd video-remix && pytest tests/e2e/test_pipeline_smoke.py -v`
Expected: FAIL at missing pipeline behavior.

**Step 3: Write minimal implementation/docs**

Finalize fixture wiring and write README usage examples for auto/step/resume modes.

**Step 4: Run full test suite**

Run: `cd video-remix && pytest -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add video-remix/tests/e2e/test_pipeline_smoke.py video-remix/README.md
git commit -m "test/docs: add e2e smoke and usage documentation"
```
