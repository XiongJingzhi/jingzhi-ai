import json

from run_state import init_run
from stages.ingest import run_ingest


def test_ingest_local_source_writes_source_meta(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")
    run_dir = init_run(tmp_path, "run-1")

    run_ingest(source=str(source), run_dir=run_dir)

    meta = json.loads((run_dir / "01_ingest" / "source_meta.json").read_text())
    assert meta["source_type"] == "local"
