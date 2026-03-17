from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import asdict
from typing import Any

from .models import DataGap, MetricObservation


MISSING_IMPACT = "当前缺少该项关键数据，结论只能暂时保守，不得强下判断。"


def _to_float(value: str) -> float:
    return float(str(value).replace(",", "").strip())


def _direction(latest: float, previous: float, up: str = "上升", down: str = "下降") -> str:
    if latest > previous:
        return up
    if latest < previous:
        return down
    return "持平"


def parse_csv_price_history(name: str, csv_text: str) -> MetricObservation:
    lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
    rows = [line.split(",") for line in lines[1:]]
    latest = _to_float(rows[-1][4])
    previous = _to_float(rows[-2][4])
    return MetricObservation(
        name=name,
        latest_value=latest,
        previous_value=previous,
        comparison_basis="前一交易日",
        direction=_direction(latest, previous),
    )


def parse_fred_series(name: str, csv_text: str) -> MetricObservation:
    rows = [line.strip().split(",") for line in csv_text.splitlines() if line.strip()][1:]
    clean = [row for row in rows if row[1] != "."]
    latest = _to_float(clean[-1][1])
    previous = _to_float(clean[-2][1])
    return MetricObservation(
        name=name,
        latest_value=latest,
        previous_value=previous,
        comparison_basis="前一发布值",
        direction=_direction(latest, previous),
    )


def parse_cboe_vix_history(csv_text: str) -> MetricObservation:
    rows = [line.strip().split(",") for line in csv_text.splitlines() if line.strip()][1:]
    latest = _to_float(rows[-1][4])
    previous = _to_float(rows[-2][4])
    return MetricObservation(
        name="VIX",
        latest_value=latest,
        previous_value=previous,
        comparison_basis="前一交易日",
        direction=_direction(latest, previous),
    )


def parse_multpl_current_page(name: str, text: str, label: str) -> MetricObservation:
    pattern = re.compile(rf"\*\*{re.escape(label)}:\*\*\s*([0-9.,]+)\s+([+-][0-9.,]+)")
    match = pattern.search(text)
    if not match:
        raise ValueError(f"failed to parse {label}")
    latest = _to_float(match.group(1))
    delta = _to_float(match.group(2))
    previous = latest - delta
    return MetricObservation(
        name=name,
        latest_value=round(latest, 4),
        previous_value=round(previous, 4),
        comparison_basis="前一发布值",
        direction=_direction(latest, previous),
    )


def parse_cnn_fear_greed_text(text: str) -> MetricObservation:
    normalized = re.sub(r"\s+", " ", text)
    match = re.search(r"Overview Timeline (\d{1,3}) Previous close (\d{1,3})", normalized)
    if not match:
        raise ValueError("failed to parse CNN fear and greed page")
    latest = int(match.group(1))
    previous = int(match.group(2))
    return MetricObservation(
        name="CNN恐惧贪婪指数",
        latest_value=latest,
        previous_value=previous,
        comparison_basis="前一交易日",
        direction=_direction(latest, previous),
    )


def parse_eastmoney_kline(payload: dict[str, Any]) -> MetricObservation:
    data = payload["data"]
    rows = [line.split(",") for line in data["klines"]]
    latest = _to_float(rows[-1][2])
    previous = _to_float(rows[-2][2])
    return MetricObservation(
        name=data["name"],
        latest_value=latest,
        previous_value=previous,
        comparison_basis="前一交易日",
        direction=_direction(latest, previous),
    )


def _read_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", "ignore")


class MarketDataFetcher:
    def _gap(self, metric: str, severity: str = "core") -> dict[str, str]:
        return asdict(DataGap(metric=metric, severity=severity, impact=MISSING_IMPACT))

    def _safe_collect(self, metric: str, fn, severity: str = "core") -> tuple[MetricObservation | None, dict[str, str] | None]:
        try:
            return fn(), None
        except Exception:
            return None, self._gap(metric, severity=severity)

    def fetch_sp500(self) -> tuple[dict[str, MetricObservation], list[dict[str, str]]]:
        observations: dict[str, MetricObservation] = {}
        gaps: list[dict[str, str]] = []
        for metric, fn, severity in [
            ("price_snapshot", lambda: parse_csv_price_history("标普500", _read_text("https://stooq.com/q/d/l/?s=%5Espx&i=d")), "core"),
            ("forward_pe", lambda: parse_multpl_current_page("Forward PE", _read_text("https://r.jina.ai/http://www.multpl.com/s-p-500-pe-ratio"), "Current S&P 500 PE Ratio"), "core"),
            ("pb", lambda: parse_multpl_current_page("PB", _read_text("https://r.jina.ai/http://www.multpl.com/s-p-500-price-to-book"), "Current S&P 500 Price to Book Value"), "non_core"),
            ("us10y_yield", lambda: parse_fred_series("10年美债", _read_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")), "non_core"),
            ("vix", lambda: parse_cboe_vix_history(_read_text("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv")), "non_core"),
            ("cnn_fear_greed", lambda: parse_cnn_fear_greed_text(_read_text("https://r.jina.ai/http://money.cnn.com/data/fear-and-greed/")), "non_core"),
        ]:
            observation, gap = self._safe_collect(metric, fn, severity)
            if observation:
                observations[metric] = observation
            if gap:
                gaps.append(gap)
        return observations, gaps

    def fetch_nasdaq100(self) -> tuple[dict[str, MetricObservation], list[dict[str, str]]]:
        observations: dict[str, MetricObservation] = {}
        gaps: list[dict[str, str]] = []
        for metric, fn, severity in [
            ("price_snapshot", lambda: parse_csv_price_history("纳斯达克100", _read_text("https://stooq.com/q/d/l/?s=%5Endq&i=d")), "core"),
            ("us10y_yield", lambda: parse_fred_series("10年美债", _read_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")), "non_core"),
            ("vix", lambda: parse_cboe_vix_history(_read_text("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv")), "non_core"),
            ("cnn_fear_greed", lambda: parse_cnn_fear_greed_text(_read_text("https://r.jina.ai/http://money.cnn.com/data/fear-and-greed/")), "non_core"),
        ]:
            observation, gap = self._safe_collect(metric, fn, severity)
            if observation:
                observations[metric] = observation
            if gap:
                gaps.append(gap)
        return observations, gaps

    def fetch_semiconductor(self) -> tuple[dict[str, MetricObservation], list[dict[str, str]]]:
        observations: dict[str, MetricObservation] = {}
        gaps: list[dict[str, str]] = []
        for metric, fn, severity in [
            ("price_snapshot", lambda: parse_csv_price_history("半导体指数", _read_text("https://stooq.com/q/d/l/?s=soxx.us&i=d")), "core"),
            ("us10y_yield", lambda: parse_fred_series("10年美债", _read_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")), "non_core"),
            ("vix", lambda: parse_cboe_vix_history(_read_text("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv")), "non_core"),
            ("cnn_fear_greed", lambda: parse_cnn_fear_greed_text(_read_text("https://r.jina.ai/http://money.cnn.com/data/fear-and-greed/")), "non_core"),
        ]:
            observation, gap = self._safe_collect(metric, fn, severity)
            if observation:
                observations[metric] = observation
            if gap:
                gaps.append(gap)
        return observations, gaps

    def fetch_a_share_dividend_low_vol(self) -> tuple[dict[str, MetricObservation], list[dict[str, str]]]:
        observations: dict[str, MetricObservation] = {}
        gaps: list[dict[str, str]] = []
        url = (
            "https://push2his.eastmoney.com/api/qt/stock/kline/get"
            "?secid=1.512890&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56"
            "&klt=101&fqt=1&end=20500101&lmt=5"
        )
        for metric, fn, severity in [
            ("price_snapshot", lambda: parse_eastmoney_kline(json.loads(_read_text(url))), "core"),
            ("vix", lambda: parse_cboe_vix_history(_read_text("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv")), "non_core"),
            ("cnn_fear_greed", lambda: parse_cnn_fear_greed_text(_read_text("https://r.jina.ai/http://money.cnn.com/data/fear-and-greed/")), "non_core"),
        ]:
            observation, gap = self._safe_collect(metric, fn, severity)
            if observation:
                observations[metric] = observation
            if gap:
                gaps.append(gap)
        return observations, gaps


def observation_to_dict(observation: MetricObservation) -> dict[str, Any]:
    return asdict(observation)
