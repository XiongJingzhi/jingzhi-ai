from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import asdict
from typing import Any

from .models import DataGap, MetricObservation


MISSING_IMPACT = "当前缺少该项关键数据，结论只能暂时保守，不得强下判断。"
_READ_CACHE: dict[str, str] = {}


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


def parse_multpl_current_percent_page(name: str, text: str, label: str) -> MetricObservation:
    pattern = re.compile(rf"\*\*{re.escape(label)}:\*\*\s*([0-9.,]+)%\s+([+-][0-9.,]+)\s+bps", re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"failed to parse {label}")
    latest = _to_float(match.group(1))
    delta_bps = _to_float(match.group(2))
    previous = latest - delta_bps / 100.0
    return MetricObservation(
        name=name,
        latest_value=round(latest, 4),
        previous_value=round(previous, 4),
        comparison_basis="前一发布值",
        direction=_direction(latest, previous),
    )


def parse_multpl_table_latest_two(name: str, text: str, up: str = "上升", down: str = "下降") -> MetricObservation:
    rows = re.findall(r"\|\s*[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s*\|\s*([0-9.,%-]+)\s*\|", text)
    if len(rows) < 2:
        raise ValueError("failed to parse latest two rows from multpl table")
    latest = _to_float(rows[0].replace("%", ""))
    previous = _to_float(rows[1].replace("%", ""))
    return MetricObservation(
        name=name,
        latest_value=round(latest, 4),
        previous_value=round(previous, 4),
        comparison_basis="前一发布值",
        direction=_direction(latest, previous, up=up, down=down),
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


def parse_cnn_market_momentum(text: str) -> MetricObservation:
    match = re.search(r"S&P 500\s+([0-9,]+\.[0-9]+)\s+125-day MA\s+([0-9,]+\.[0-9]+)", text, re.MULTILINE)
    if not match:
        raise ValueError("failed to parse CNN market momentum")
    latest = _to_float(match.group(1))
    baseline = _to_float(match.group(2))
    return MetricObservation(
        name="市场动量",
        latest_value=latest,
        previous_value=baseline,
        comparison_basis="125日均线",
        direction=_direction(latest, baseline),
    )


def parse_cnn_stock_breadth(text: str) -> MetricObservation:
    match = re.search(r"McClellan Volume Summation Index.*?([0-9,]+\.[0-9]+)\s+Last updated", text, re.DOTALL)
    if not match:
        raise ValueError("failed to parse CNN stock breadth")
    latest = _to_float(match.group(1))
    baseline = 0.0
    return MetricObservation(
        name="市场广度",
        latest_value=latest,
        previous_value=baseline,
        comparison_basis="零轴基准",
        direction="改善" if latest > baseline else "恶化" if latest < baseline else "持平",
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


def parse_eastmoney_quote_page(text: str, name: str) -> tuple[MetricObservation, MetricObservation]:
    match = re.search(
        rf"{re.escape(name)}.*?([0-9]+\.[0-9]+)\s+[-+0-9.\s%]+\s+今开:.*?成交量:\s*([0-9.]+)万.*?昨收:\s*([0-9]+\.[0-9]+)",
        text,
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"failed to parse Eastmoney quote page for {name}")
    latest = _to_float(match.group(1))
    volume = _to_float(match.group(2))
    previous = _to_float(match.group(3))
    price_observation = MetricObservation(
        name=name,
        latest_value=latest,
        previous_value=previous,
        comparison_basis="前一交易日",
        direction=_direction(latest, previous),
    )
    volume_observation = MetricObservation(
        name="成交量",
        latest_value=volume,
        previous_value=volume,
        comparison_basis="当日成交量",
        direction="持平",
    )
    return price_observation, volume_observation


def parse_etfdb_pe_ratio(name: str, text: str, symbol: str) -> MetricObservation:
    pattern = re.compile(
        rf"{re.escape(symbol)} Valuation.*?{re.escape(symbol)}\s+P/E Ratio\s+([0-9.]+).*?ETF Database Category Average\s+P/E Ratio\s+([0-9.]+)",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"failed to parse ETFDB P/E for {symbol}")
    latest = _to_float(match.group(1))
    previous = _to_float(match.group(2))
    return MetricObservation(
        name=name,
        latest_value=latest,
        previous_value=previous,
        comparison_basis="ETF类别均值代理",
        direction=_direction(latest, previous),
    )


def parse_etfdb_dividend_yield(name: str, text: str, symbol: str) -> MetricObservation:
    pattern = re.compile(
        rf"\|\s*Annual Dividend Yield\s*\|\s*([0-9.]+)%\s*\|\s*([0-9.]+)%\s*\|",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"failed to parse ETFDB dividend yield for {symbol}")
    latest = _to_float(match.group(1))
    previous = _to_float(match.group(2))
    return MetricObservation(
        name=name,
        latest_value=latest,
        previous_value=previous,
        comparison_basis="ETF类别均值代理",
        direction=_direction(latest, previous),
    )


def parse_etfdb_top10_concentration(name: str, text: str) -> MetricObservation:
    match = re.search(r"\|\s*% of Assets in Top 10\s*\|\s*([0-9.]+)%\s*\|\s*([0-9.]+)%\s*\|", text)
    if not match:
        raise ValueError("failed to parse ETFDB top 10 concentration")
    latest = _to_float(match.group(1))
    previous = _to_float(match.group(2))
    return MetricObservation(
        name=name,
        latest_value=latest,
        previous_value=previous,
        comparison_basis="ETF类别均值代理",
        direction=_direction(latest, previous),
    )


def parse_sia_monthly_sales_page(text: str) -> MetricObservation:
    match = re.search(
        r"global semiconductor sales were \$([0-9.]+) billion .*?increase(?: of)? ([0-9.]+)% compared to .*? and ([0-9.]+)% (?:more than|year-to-year)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        match = re.search(
            r"sales were \$([0-9.]+) billion .*?increase of ([0-9.]+)% compared to .*? and ([0-9.]+)% more than",
            text,
            re.IGNORECASE | re.DOTALL,
        )
    if not match:
        raise ValueError("failed to parse SIA monthly sales")
    mom_growth = _to_float(match.group(2))
    yoy_growth = _to_float(match.group(3))
    return MetricObservation(
        name="全球半导体销售增速",
        latest_value=yoy_growth,
        previous_value=mom_growth,
        comparison_basis="上月增速代理",
        direction="改善" if yoy_growth >= mom_growth else "恶化",
    )


def parse_tsmc_monthly_revenue_pages(current_year_text: str, previous_year_text: str) -> MetricObservation:
    current_rows = re.findall(r"(?:\|\s*)?([A-Z][a-z]{2}\.)\s*\|\s*([0-9,]+)\s*\|\s*([0-9.]+)%", current_year_text)
    previous_rows = re.findall(r"(?:\|\s*)?([A-Z][a-z]{2}\.)\s*\|\s*([0-9,]+)\s*\|\s*([0-9.]+)%", previous_year_text)
    if not current_rows:
        raise ValueError("failed to parse TSMC current-year monthly revenue")
    latest_yoy = _to_float(current_rows[-1][2])
    previous_yoy = _to_float(previous_rows[-1][2]) if previous_rows else latest_yoy
    return MetricObservation(
        name="台积电月营收同比",
        latest_value=latest_yoy,
        previous_value=previous_yoy,
        comparison_basis="前一发布值",
        direction="改善" if latest_yoy > previous_yoy else "恶化" if latest_yoy < previous_yoy else "持平",
    )


def parse_tradingeconomics_china_10y(text: str) -> MetricObservation:
    match = re.search(
        r"The yield on China 10Y Bond Yield .*? at ([0-9.]+)% .*? past month, the yield has edged (up|down) by ([0-9.]+) points",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ValueError("failed to parse TradingEconomics China 10Y")
    latest = _to_float(match.group(1))
    delta = _to_float(match.group(3))
    previous = latest - delta if match.group(2).lower() == "up" else latest + delta
    return MetricObservation(
        name="中国10年国债",
        latest_value=latest,
        previous_value=round(previous, 4),
        comparison_basis="前一月",
        direction=_direction(latest, previous),
    )


def get_proxy_map() -> dict[str, str]:
    proxies: dict[str, str] = {}
    for scheme in ("http", "https"):
        value = os.environ.get(f"{scheme.upper()}_PROXY") or os.environ.get(f"{scheme}_proxy")
        if value:
            proxies[scheme] = value
    return proxies


def _read_text(url: str) -> str:
    if url in _READ_CACHE:
        return _READ_CACHE[url]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    errors: list[Exception] = []
    proxy_map = get_proxy_map()
    openers = []
    if proxy_map:
        openers.append(urllib.request.build_opener(urllib.request.ProxyHandler(proxy_map)))
    openers.append(urllib.request.build_opener())
    for opener in openers:
        try:
            with opener.open(req, timeout=20) as response:
                text = response.read().decode("utf-8", "ignore")
                _READ_CACHE[url] = text
                return text
        except Exception as exc:
            errors.append(exc)
    raise errors[-1]


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
            ("dividend_yield", lambda: parse_multpl_current_percent_page("股息率", _read_text("https://r.jina.ai/http://www.multpl.com/s-p-500-dividend-yield"), "Current Yield"), "non_core"),
            ("eps_revision", lambda: parse_multpl_table_latest_two("EPS预期", _read_text("https://r.jina.ai/http://www.multpl.com/s-p-500-earnings/table/by-month"), up="上修", down="下修"), "core"),
            ("pb", lambda: parse_multpl_current_page("PB", _read_text("https://r.jina.ai/http://www.multpl.com/s-p-500-price-to-book"), "Current S&P 500 Price to Book Value"), "non_core"),
            ("us10y_yield", lambda: parse_fred_series("10年美债", _read_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")), "non_core"),
            ("market_breadth", lambda: parse_cnn_stock_breadth(_read_text("https://r.jina.ai/http://money.cnn.com/data/fear-and-greed/")), "non_core"),
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
        qqq_text = "https://r.jina.ai/http://etfdb.com/etf/QQQ/"
        for metric, fn, severity in [
            ("price_snapshot", lambda: parse_csv_price_history("纳斯达克100", _read_text("https://stooq.com/q/d/l/?s=%5Endq&i=d")), "core"),
            ("forward_pe", lambda: parse_etfdb_pe_ratio("Forward PE", _read_text(qqq_text), "QQQ"), "core"),
            ("dividend_yield", lambda: parse_etfdb_dividend_yield("股息率", _read_text(qqq_text), "QQQ"), "non_core"),
            ("concentration", lambda: parse_etfdb_top10_concentration("集中度", _read_text(qqq_text)), "non_core"),
            ("dxy", lambda: parse_fred_series("DXY", _read_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS")), "non_core"),
            ("us10y_yield", lambda: parse_fred_series("10年美债", _read_text("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")), "non_core"),
            ("market_breadth", lambda: parse_cnn_stock_breadth(_read_text("https://r.jina.ai/http://money.cnn.com/data/fear-and-greed/")), "non_core"),
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
        soxx_text = "https://r.jina.ai/http://etfdb.com/etf/SOXX/"
        for metric, fn, severity in [
            ("price_snapshot", lambda: parse_csv_price_history("半导体指数", _read_text("https://stooq.com/q/d/l/?s=soxx.us&i=d")), "core"),
            ("global_semiconductor_sales_growth", lambda: parse_sia_monthly_sales_page(_read_text("https://r.jina.ai/http://www.semiconductors.org/?s=January+2026+sales")), "core"),
            ("tsmc_monthly_revenue_yoy", lambda: parse_tsmc_monthly_revenue_pages(_read_text("https://r.jina.ai/http://investor.tsmc.com/english/monthly-revenue/2026"), _read_text("https://r.jina.ai/http://investor.tsmc.com/english/monthly-revenue/2025")), "core"),
            ("forward_pe", lambda: parse_etfdb_pe_ratio("Forward PE", _read_text(soxx_text), "SOXX"), "non_core"),
            ("dividend_yield", lambda: parse_etfdb_dividend_yield("股息率", _read_text(soxx_text), "SOXX"), "non_core"),
            ("concentration", lambda: parse_etfdb_top10_concentration("集中度", _read_text(soxx_text)), "non_core"),
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
        for metric, fn, severity in [
            ("price_snapshot", lambda: parse_eastmoney_quote_page(_read_text("https://r.jina.ai/http://quote.eastmoney.com/sh512890.html"), "红利低波ETF华泰柏瑞")[0], "core"),
            ("china10y_yield", lambda: parse_tradingeconomics_china_10y(_read_text("https://r.jina.ai/http://www.tradingeconomics.com/china/government-bond-yield")), "non_core"),
            ("excess_return_vs_csi300", lambda: self._compute_a_share_excess_return(), "non_core"),
            ("volume", lambda: parse_eastmoney_quote_page(_read_text("https://r.jina.ai/http://quote.eastmoney.com/sh512890.html"), "红利低波ETF华泰柏瑞")[1], "non_core"),
            ("vix", lambda: parse_cboe_vix_history(_read_text("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv")), "non_core"),
            ("cnn_fear_greed", lambda: parse_cnn_fear_greed_text(_read_text("https://r.jina.ai/http://money.cnn.com/data/fear-and-greed/")), "non_core"),
        ]:
            observation, gap = self._safe_collect(metric, fn, severity)
            if observation:
                observations[metric] = observation
            if gap:
                gaps.append(gap)
        return observations, gaps

    def _compute_a_share_excess_return(self) -> MetricObservation:
        dividend_page = _read_text("https://r.jina.ai/http://quote.eastmoney.com/sh512890.html")
        csi300_page = _read_text("https://r.jina.ai/http://quote.eastmoney.com/sh510300.html")
        dividend_obs, _ = parse_eastmoney_quote_page(dividend_page, "红利低波ETF华泰柏瑞")
        csi300_obs, _ = parse_eastmoney_quote_page(csi300_page, "沪深300ETF华泰柏瑞")
        dividend_return = (float(dividend_obs.latest_value) / float(dividend_obs.previous_value) - 1) * 100
        csi300_return = (float(csi300_obs.latest_value) / float(csi300_obs.previous_value) - 1) * 100
        excess = dividend_return - csi300_return
        return MetricObservation(
            name="相对沪深300超额收益",
            latest_value=round(excess, 4),
            previous_value=0.0,
            comparison_basis="相对沪深300当日收益差",
            direction="改善" if excess > 0 else "恶化" if excess < 0 else "持平",
        )


def observation_to_dict(observation: MetricObservation) -> dict[str, Any]:
    return asdict(observation)
