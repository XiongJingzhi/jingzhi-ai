import json

from run_state import init_run
from stages.style import run_style


def test_style_profile_contains_tone_lexicon_forbidden(tmp_path):
    run_dir = init_run(tmp_path, "run-1")
    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()
    (samples_dir / "a.md").write_text("稳重、有观点、用词克制")
    rules = tmp_path / "rules.txt"
    rules.write_text("forbidden: 绝对, 保证")
    persona_dir = tmp_path / "persona"
    persona_dir.mkdir()
    (persona_dir / "profile.json").write_text(
        json.dumps(
            {
                "catchphrases": ["说白了", "本质上"],
                "common_expressions": ["我们拆开看", "先说结论"],
                "forbidden_expressions": ["躺赚", "无脑"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    run_style(
        run_dir=run_dir,
        style_samples_dir=samples_dir,
        style_rules_file=rules,
        persona_dir=persona_dir,
    )

    profile = json.loads((run_dir / "04_style" / "style_profile.json").read_text())
    assert "tone" in profile
    assert "lexicon" in profile
    assert "forbidden" in profile
    assert "catchphrases" in profile
    assert "说白了" in profile["catchphrases"]
