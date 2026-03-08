from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from run_state import init_run, mark_completed, read_status, write_status
from stages.analyze import run_analyze
from stages.ingest import run_ingest
from stages.rewrite import run_rewrite
from stages.style import run_style
from stages.transcript import run_transcript
from stages.transcribe import run_transcribe

app = typer.Typer(add_completion=False, help="Video remix pipeline")


def entrypoint() -> None:
    app()


def _run_pipeline(
    run_dir: Path,
    mode: str,
    output: str,
    source: Optional[str] = None,
    persona_dir: Optional[Path] = None,
) -> None:
    status = read_status(run_dir)
    completed = set(status.get("completed_stages", []))

    def checkpoint(point: str) -> bool:
        if mode != "step":
            return False
        status_local = read_status(run_dir)
        status_local["paused_at"] = point
        write_status(run_dir, status_local)
        return True

    if "ingest" not in completed:
        if not source:
            raise typer.BadParameter("source is required for ingest")
        run_ingest(source=source, run_dir=run_dir)
        mark_completed(run_dir, "ingest")

    if "transcribe" not in completed:
        run_transcribe(run_dir=run_dir)
        mark_completed(run_dir, "transcribe")
        if checkpoint("after_transcribe"):
            return

    if "transcript" not in completed:
        run_transcript(run_dir=run_dir)
        mark_completed(run_dir, "transcript")

    if "analyze" not in completed:
        run_analyze(run_dir=run_dir)
        mark_completed(run_dir, "analyze")
        if checkpoint("after_analyze"):
            return

    if mode == "step":
        status_local = read_status(run_dir)
        if status_local.get("paused_at") is None and "rewrite" not in completed:
            status_local["paused_at"] = "before_rewrite"
            write_status(run_dir, status_local)
            return

    if "style" not in completed:
        run_style(run_dir=run_dir, persona_dir=persona_dir)
        mark_completed(run_dir, "style")

    if "rewrite" not in completed:
        run_rewrite(run_dir=run_dir, output=output)
        mark_completed(run_dir, "rewrite")

    final_status = read_status(run_dir)
    final_status["paused_at"] = None
    write_status(run_dir, final_status)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    source: Optional[str] = typer.Option(None, "--source"),
    mode: str = typer.Option("auto", "--mode"),
    output: str = typer.Option("both", "--output"),
    persona_dir: Optional[Path] = typer.Option(None, "--persona-dir"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
    run_id: Optional[str] = typer.Option(None, "--run-id"),
) -> None:
    if ctx.invoked_subcommand:
        return
    if not source:
        raise typer.BadParameter("--source is required")

    run_name = run_id or "run-default"
    run_dir = init_run(base_dir, run_name)
    status = read_status(run_dir)
    status["mode"] = mode
    status["source"] = source
    status["output"] = output
    status["persona_dir"] = str(persona_dir) if persona_dir else None
    write_status(run_dir, status)
    _run_pipeline(
        run_dir=run_dir,
        mode=mode,
        output=output,
        source=source,
        persona_dir=persona_dir,
    )
    typer.echo(f"run_id={run_name}")


@app.command("ingest")
def ingest_cmd(
    source: str = typer.Option(..., "--source"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
    run_id: str = typer.Option(..., "--run-id"),
) -> None:
    run_dir = init_run(base_dir, run_id)
    run_ingest(source=source, run_dir=run_dir)
    mark_completed(run_dir, "ingest")


@app.command("transcribe")
def transcribe_cmd(
    run: str = typer.Option(..., "--run"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
) -> None:
    run_dir = init_run(base_dir, run)
    run_transcribe(run_dir=run_dir)
    mark_completed(run_dir, "transcribe")


@app.command("analyze")
def analyze_cmd(
    run: str = typer.Option(..., "--run"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
) -> None:
    run_dir = init_run(base_dir, run)
    run_analyze(run_dir=run_dir)
    mark_completed(run_dir, "analyze")


@app.command("transcript")
def transcript_cmd(
    run: str = typer.Option(..., "--run"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
) -> None:
    run_dir = init_run(base_dir, run)
    run_transcript(run_dir=run_dir)
    mark_completed(run_dir, "transcript")


@app.command("style")
def style_cmd(
    run: str = typer.Option(..., "--run"),
    style_samples: Optional[Path] = typer.Option(None, "--style-samples"),
    style_rules: Optional[Path] = typer.Option(None, "--style-rules"),
    persona_dir: Optional[Path] = typer.Option(None, "--persona-dir"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
) -> None:
    run_dir = init_run(base_dir, run)
    run_style(
        run_dir=run_dir,
        style_samples_dir=style_samples,
        style_rules_file=style_rules,
        persona_dir=persona_dir,
    )
    mark_completed(run_dir, "style")


@app.command("rewrite")
def rewrite_cmd(
    run: str = typer.Option(..., "--run"),
    output: str = typer.Option("both", "--output"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
) -> None:
    run_dir = init_run(base_dir, run)
    run_rewrite(run_dir=run_dir, output=output)
    mark_completed(run_dir, "rewrite")


@app.command("resume")
def resume_cmd(
    run: str = typer.Option(..., "--run"),
    base_dir: Path = typer.Option(Path("runs"), "--base-dir"),
) -> None:
    run_dir = init_run(base_dir, run)
    status = read_status(run_dir)
    mode = status.get("mode", "auto")
    source = status.get("source")
    output = status.get("output", "both")
    persona_dir = Path(status["persona_dir"]) if status.get("persona_dir") else None

    paused_at = status.get("paused_at")
    if mode == "step" and paused_at == "after_transcribe":
        status["paused_at"] = None
        write_status(run_dir, status)
        _run_pipeline(
            run_dir=run_dir, mode="step", output=output, source=source, persona_dir=persona_dir
        )
        return
    if mode == "step" and paused_at == "after_analyze":
        status["paused_at"] = None
        write_status(run_dir, status)
        _run_pipeline(
            run_dir=run_dir, mode="step", output=output, source=source, persona_dir=persona_dir
        )
        return
    if mode == "step" and paused_at == "before_rewrite":
        status["mode"] = "auto"
        status["paused_at"] = None
        write_status(run_dir, status)
        _run_pipeline(
            run_dir=run_dir, mode="auto", output=output, source=source, persona_dir=persona_dir
        )
        return

    _run_pipeline(run_dir=run_dir, mode=mode, output=output, source=source, persona_dir=persona_dir)
