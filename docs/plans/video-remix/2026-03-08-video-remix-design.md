# Video Remix Skill Design (Local + URL, Dual Output)

Date: 2026-03-08  
Status: Approved

## 1. Scope and Goals

Build a skill pipeline that takes either a local video file or a video URL, then produces:
- a short speaking script (30-90 seconds), and
- a long-form article.

The system runs in hybrid mode:
- default: one-command full pipeline,
- optional: pause at key checkpoints for human review.

## 2. Confirmed Product Decisions

- Source type: local file + URL.
- Output type: both short script and long article.
- Execution mode: hybrid (auto + optional human checkpoints).
- Style transfer input: historical writing samples + explicit style rules.
- Compliance mode: no mandatory legal/authorization blocking; user self-judges.

## 3. Architecture

Use a pipeline design with one orchestrator plus five stage modules.

### 3.1 Orchestrator
- `video-remix`
- Responsibilities:
  - parse inputs and runtime mode,
  - dispatch stages,
  - track status and resumability,
  - handle pause/continue checkpoints.

### 3.2 Stage Modules
1. `ingest`
- Download from URL or read local file.
- Normalize media format.
- Outputs: `source_meta.json`, normalized media, extracted audio.

2. `transcribe`
- ASR with timestamped segments.
- Outputs: `transcript.timestamped.md`, `transcript.jsonl`.

3. `analyze`
- Structural decomposition and rhetorical analysis.
- Outputs: `analysis.md`.

4. `style`
- Build style profile from user samples + rule file.
- Outputs: `style_profile.json`.

5. `rewrite`
- Generate dual deliverables using analysis + style profile.
- Outputs: `script.short.md`, `article.long.md`, `diff.style-applied.md`.

## 4. Human-in-the-Loop Checkpoints

In step mode, pause at three points:
1. after transcription (fix names, terms, entities),
2. after analysis (adjust outline/arguments),
3. before final rewrite (set style intensity: conservative/medium/aggressive).

## 5. Data Flow and Run State

Flow:
`source -> ingest -> transcribe -> analyze -> style -> rewrite`

Each run writes status metadata and supports resume by run id.

## 6. Directory Contract

Recommended run layout:
- `runs/<run_id>/input/`
- `runs/<run_id>/01_ingest/`
- `runs/<run_id>/02_transcribe/`
- `runs/<run_id>/03_analyze/`
- `runs/<run_id>/04_style/`
- `runs/<run_id>/05_rewrite/`
- `runs/<run_id>/final/`

## 7. CLI Contract

### 7.1 Main commands
- `video-remix --source "<url-or-path>" --mode auto --output both`
- `video-remix --source "<url-or-path>" --mode step --output both`
- `video-remix resume --run <run_id>`

### 7.2 Stage commands
- `video-remix ingest --source ...`
- `video-remix transcribe --run <run_id>`
- `video-remix analyze --run <run_id>`
- `video-remix style --run <run_id> --style-samples <dir> --style-rules <file>`
- `video-remix rewrite --run <run_id> --output both`

## 8. File Interfaces

Required artifacts:
- `source_meta.json`
- `transcript.jsonl`
- `transcript.timestamped.md`
- `analysis.md`
- `style_profile.json`
- `final/script.short.md`
- `final/article.long.md`
- `diff.style-applied.md`

## 9. Reliability and Quality Gates

### 9.1 Error handling
- Retry and fallback for download failures.
- Preserve audio and allow ASR engine rerun on transcription failure.
- Retry per output artifact for generation failures.
- Graceful degradation when style samples are insufficient.

### 9.2 Stage gates
- Transcription gate: timestamp continuity and acceptable low-confidence ratio.
- Analysis gate: must include topic/argument/evidence/rhythm sections.
- Rewrite gate:
  - short script pacing suitable for speaking,
  - long article has complete structure,
  - style similarity passes threshold.

## 10. Acceptance Criteria

- For both local path and URL input, pipeline produces:
  - `transcript.timestamped.md`
  - `final/script.short.md`
  - `final/article.long.md`
- Step mode must support pause and continue at three checkpoints.
- Resume from `run_id` should avoid full reruns.
- Repeated runs on same source should preserve structural consistency.

## 11. Out of Scope (Current Version)

- Auto-posting to content platforms.
- Mandatory legal/rights enforcement.
- Perfect verbatim transcription as primary objective.

