---
name: video-remix
description: Use when you need to transform a local video file or video URL into structured written outputs (timestamped transcript, AI-corrected transcript, short speaking script, and long-form article), especially when you want resumable auto/step execution.
---

# Video Remix

## Overview

Convert one video source (local path or URL) into four artifacts:
- timestamped transcript
- AI-corrected transcript
- short speaking script
- long-form article

The pipeline supports:
- `auto` mode: run end-to-end
- `step` mode: pause at checkpoints and continue with `resume`

## When to Use

Use this skill when:
- you need fast content repurposing from video to text
- you want a resumable pipeline (`run_id`) instead of one-shot scripts
- you need both short and long written outputs from the same source

Do not use this skill when:
- input is already a text transcript (no video/audio processing needed)
- you need direct publishing to platforms (out of current scope)

## Inputs

- `--source`: local video path or URL
- `--mode`: `auto` or `step`
- `--output`: `both`, `short`, or `long`
- `--run-id` (optional but recommended for tracking/resume)
- `--base-dir` (optional, default `runs`)
- transcript correction provider: default `agent` with fallback order `claude -> codex -> openai`
- set `VIDEO_REMIX_LLM_PROVIDER=claude|codex|openai|agent` to choose the preferred provider
- local Claude provider uses the machine `claude` CLI; OpenAI provider requires `OPENAI_API_KEY`

## Commands

### Full pipeline

```bash
video-remix --source "./demo.mp4" --mode auto --output both --run-id run-demo
```

```bash
video-remix --source "https://example.com/video" --mode step --output both --run-id run-step
```

### Resume paused run

```bash
video-remix resume --run run-step
```

### Stage-by-stage

```bash
video-remix ingest --source "./demo.mp4" --run-id run-1
video-remix transcribe --run run-1
video-remix transcript --run run-1
video-remix analyze --run run-1
video-remix style --run run-1 --style-samples ./samples --style-rules ./rules.txt
video-remix rewrite --run run-1 --output both
```

## Output Contract

For each run: `runs/<run_id>/`

Required artifacts:
- `02_transcribe/transcript.timestamped.md`
- `02_transcribe/transcript.jsonl`
- `02_transcribe/transcript.corrected.md`
- `03_analyze/analysis.md`
- `04_style/style_profile.json`
- `05_rewrite/diff.style-applied.md`
- `final/script.short.md`
- `final/article.long.md`
