from __future__ import annotations

import json
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_samples(style_samples_dir: Path | None) -> list[str]:
    if style_samples_dir is None or not style_samples_dir.exists():
        return []
    texts: list[str] = []
    for file in sorted(style_samples_dir.glob("*")):
        if file.is_file():
            texts.append(file.read_text(encoding="utf-8"))
    return texts


def _read_forbidden(style_rules_file: Path | None) -> list[str]:
    if style_rules_file is None or not style_rules_file.exists():
        return []
    text = style_rules_file.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.lower().startswith("forbidden:"):
            _, value = line.split(":", 1)
            return [x.strip() for x in value.split(",") if x.strip()]
    return []


def _read_persona(persona_dir: Path | None) -> dict:
    base_dir = persona_dir or (_project_root() / "resources" / "persona")
    payload = {
        "catchphrases": [],
        "common_expressions": [],
        "forbidden_expressions": [],
    }
    if not base_dir.exists():
        return payload

    for file in sorted(base_dir.glob("*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        for key in payload:
            vals = data.get(key, [])
            if isinstance(vals, list):
                payload[key].extend([str(v).strip() for v in vals if str(v).strip()])

    for key in payload:
        payload[key] = sorted(set(payload[key]))
    return payload


def run_style(
    run_dir: Path,
    style_samples_dir: Path | None = None,
    style_rules_file: Path | None = None,
    persona_dir: Path | None = None,
) -> dict:
    samples = _read_samples(style_samples_dir)
    forbidden = _read_forbidden(style_rules_file)
    persona = _read_persona(persona_dir)

    lexicon = []
    if samples:
        words = " ".join(samples).replace("，", " ").replace("。", " ").split()
        lexicon = sorted(set(words[:60]))

    profile = {
        "tone": "balanced",
        "sentence_length": "medium",
        "lexicon": lexicon,
        "forbidden": sorted(set(forbidden + persona["forbidden_expressions"])),
        "pacing": "steady",
        "catchphrases": persona["catchphrases"],
        "common_expressions": persona["common_expressions"],
    }
    out = run_dir / "04_style" / "style_profile.json"
    out.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    return profile
