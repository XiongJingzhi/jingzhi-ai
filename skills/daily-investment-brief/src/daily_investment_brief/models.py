from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MetricObservation:
    name: str
    latest_value: float | int | str
    previous_value: float | int | str
    comparison_basis: str
    direction: str
    implication: str = ""


@dataclass(slots=True)
class DataGap:
    metric: str
    severity: str
    impact: str
