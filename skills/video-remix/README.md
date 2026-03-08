# video-remix

A resumable pipeline that ingests a video (local path or URL), transcribes it, analyzes structure, applies style profile, and writes short+long outputs.

## Usage

```bash
video-remix --source "./demo.mp4" --mode auto --output both
video-remix --source "https://example.com/video" --mode step --output both
video-remix resume --run <run_id>
```
