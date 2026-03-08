from run_state import init_run


def test_init_run_creates_stage_dirs(tmp_path):
    run_dir = init_run(tmp_path, "run-test")

    assert (run_dir / "input").exists()
    assert (run_dir / "01_ingest").exists()
    assert (run_dir / "02_transcribe").exists()
    assert (run_dir / "03_analyze").exists()
    assert (run_dir / "04_style").exists()
    assert (run_dir / "05_rewrite").exists()
    assert (run_dir / "final").exists()
    assert (run_dir / "status.json").exists()
