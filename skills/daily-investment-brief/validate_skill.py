from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SKILL_PATH = ROOT / "SKILL.md"
PRESSURE_TESTS_PATH = ROOT / "pressure-tests.md"


REQUIRED_SECTIONS = [
    "## Overview",
    "## When to Use",
    "## Role",
    "## Goal",
    "## Supported Assets",
    "## Execution Flow",
    "## Input Schema",
    "## Output Schema",
    "## Decision Rules",
    "## Fallback Rules",
    "## Asset-Specific Rules",
    "## Rendering Rules",
    "## Prohibited Behaviors",
    "## Pressure Test Checklist",
]

REQUIRED_TOKENS = [
    "analysis_json",
    "report_text",
    "cnn_fear_greed",
    "vix",
    "偏正面",
    "偏中性",
    "偏谨慎",
    "信号分化",
    "当前缺少该项关键数据，结论只能暂时保守，不得强下判断。",
    "当前信号分化，暂不支持强结论。",
]

REQUIRED_ASSET_HEADERS = [
    "### SP500",
    "### Nasdaq 100",
    "### Semiconductor",
    "### A-share Dividend Low Vol",
]


def validate_skill() -> list[str]:
    errors: list[str] = []
    text = SKILL_PATH.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing section: {section}")

    for token in REQUIRED_TOKENS:
        if token not in text:
            errors.append(f"missing token: {token}")

    for asset_header in REQUIRED_ASSET_HEADERS:
        if asset_header not in text:
            errors.append(f"missing asset block: {asset_header}")

    if text.count("## ") < len(REQUIRED_SECTIONS):
        errors.append("insufficient top-level sections")

    if "Only these asset types are supported:" not in text:
        errors.append("missing supported asset type contract")

    if text.count("Priority order:") != 4:
        errors.append("expected exactly 4 priority order blocks")

    return errors


def validate_pressure_tests() -> list[str]:
    errors: list[str] = []
    text = PRESSURE_TESTS_PATH.read_text(encoding="utf-8")
    scenarios = [line for line in text.splitlines() if line.startswith("## ")]

    if len(scenarios) != 8:
        errors.append(f"expected 8 pressure test scenarios, found {len(scenarios)}")

    required_snippets = [
        "结论不能是 `偏正面`",
        "结论只能保守",
        "`confidence = low`",
        "结论为 `信号分化`",
        "最新值 + 方向 + 含义",
    ]
    for snippet in required_snippets:
        if snippet not in text:
            errors.append(f"missing pressure test expectation: {snippet}")

    return errors


def main() -> int:
    errors = [*validate_skill(), *validate_pressure_tests()]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("daily-investment-brief validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
