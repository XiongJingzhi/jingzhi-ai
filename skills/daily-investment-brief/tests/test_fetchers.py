from daily_investment_brief.fetchers import (
    MarketDataFetcher,
    get_proxy_map,
    parse_cnn_market_momentum,
    parse_cnn_stock_breadth,
    parse_eastmoney_quote_page,
    parse_cnn_fear_greed_text,
    parse_csv_price_history,
    parse_cboe_vix_history,
    parse_eastmoney_kline,
    parse_fred_series,
    parse_multpl_current_page,
    parse_multpl_current_percent_page,
    parse_sia_monthly_sales_page,
    parse_tsmc_monthly_revenue_pages,
)


def test_parse_csv_price_history_returns_latest_and_previous():
    csv_text = "\n".join(
        [
            "Date,Open,High,Low,Close,Volume",
            "2026-03-13,6673.49,6733.3,6623.92,6632.19,2967819370",
            "2026-03-16,6674.37,6729.79,6674.37,6699.38,3034952790",
            "2026-03-17,6728.66,6754.16,6711.68,6722.66,822292500",
        ]
    )

    observation = parse_csv_price_history("标普500", csv_text)

    assert observation.latest_value == 6722.66
    assert observation.previous_value == 6699.38
    assert observation.direction == "上升"


def test_parse_fred_series_returns_latest_and_previous():
    csv_text = "\n".join(
        [
            "DATE,DGS10",
            "2026-03-11,4.21",
            "2026-03-12,4.27",
            "2026-03-13,4.28",
        ]
    )

    observation = parse_fred_series("10年美债", csv_text)

    assert observation.latest_value == 4.28
    assert observation.previous_value == 4.27
    assert observation.direction == "上升"


def test_parse_cboe_vix_history_returns_latest_and_previous():
    csv_text = "\n".join(
        [
            "DATE,OPEN,HIGH,LOW,CLOSE",
            "03/12/2026,25.48,27.33,24.60,27.29",
            "03/13/2026,27.85,28.47,24.67,27.19",
            "03/16/2026,25.88,26.42,23.23,23.51",
        ]
    )

    observation = parse_cboe_vix_history(csv_text)

    assert observation.latest_value == 23.51
    assert observation.previous_value == 27.19
    assert observation.direction == "下降"


def test_parse_multpl_page_extracts_current_value_and_delta():
    text = """
**Current S&P 500 PE Ratio:** 28.80  +0.30 (1.05%)
4:00 PM EDT, Mon Mar 16
"""

    observation = parse_multpl_current_page("Forward PE", text, "Current S&P 500 PE Ratio")

    assert observation.latest_value == 28.8
    assert observation.previous_value == 28.5
    assert observation.direction == "上升"


def test_parse_multpl_percent_page_handles_bps_delta():
    text = """
**Current Yield:** 1.17%  -1.22 bps
4:00 PM EDT, Mon Mar 16
"""

    observation = parse_multpl_current_percent_page("股息率", text, "Current Yield")

    assert observation.latest_value == 1.17
    assert observation.previous_value == 1.1822
    assert observation.direction == "下降"


def test_parse_cnn_fear_greed_text_extracts_current_and_previous():
    text = """
Fear & Greed Index
Overview
Timeline
22
Previous close
18
1 week ago
26
"""

    observation = parse_cnn_fear_greed_text(text)

    assert observation.latest_value == 22
    assert observation.previous_value == 18
    assert observation.direction == "上升"


def test_parse_cnn_market_momentum_extracts_price_and_moving_average():
    text = """
S&P 500

5,675.12

125-day MA

5,901.59
"""

    observation = parse_cnn_market_momentum(text)

    assert observation.latest_value == 5675.12
    assert observation.previous_value == 5901.59
    assert observation.direction == "下降"


def test_parse_cnn_stock_breadth_extracts_latest_reading():
    text = """
### McClellan Volume Summation Index
Market breadth strong
Market breadth weak
667.63
Last updated Mar 17 at 12:31:16 PM EDT
"""

    observation = parse_cnn_stock_breadth(text)

    assert observation.latest_value == 667.63
    assert observation.previous_value == 0.0
    assert observation.direction == "改善"


def test_parse_eastmoney_kline_returns_latest_and_previous():
    payload = {
        "data": {
            "name": "红利低波ETF华泰柏瑞",
            "klines": [
                "2026-03-13,1.201,1.205,1.212,1.201,5583094",
                "2026-03-16,1.205,1.205,1.211,1.198,7622685",
                "2026-03-17,1.203,1.210,1.214,1.203,4753267",
            ],
        }
    }

    observation = parse_eastmoney_kline(payload)

    assert observation.name == "红利低波ETF华泰柏瑞"
    assert observation.latest_value == 1.210
    assert observation.previous_value == 1.205
    assert observation.direction == "上升"


def test_parse_eastmoney_quote_page_returns_latest_previous_and_volume():
    text = """
红利低波ETF华泰柏瑞 512890

1.210

0.005 0.41%

今开: 1.203 最高: 1.214 涨停: 1.326 换手: 1.83%成交量: 475.3万 振幅: 0.91%外盘: 270.1万
昨收: 1.205 最低: 1.203 跌停: 1.085 量比: 0.83 成交额: 5.753亿 均价: 1.210 内盘: 205.2万
"""

    observation, volume = parse_eastmoney_quote_page(text, "红利低波ETF华泰柏瑞")

    assert observation.latest_value == 1.210
    assert observation.previous_value == 1.205
    assert observation.direction == "上升"
    assert volume.latest_value == 475.3
    assert volume.direction == "持平"


def test_parse_sia_monthly_sales_page_extracts_sales_and_growth():
    text = """
global semiconductor sales were $82.5 billion during the month of January 2026, an increase of 3.7% compared to the December 2025 total of $79.6 billion and 46.1% more than the January 2025 total of $56.5 billion.
"""

    observation = parse_sia_monthly_sales_page(text)

    assert observation.latest_value == 46.1
    assert observation.previous_value == 3.7
    assert observation.direction == "改善"


def test_parse_tsmc_monthly_revenue_pages_handles_year_boundary():
    current_year = """
### 2026 Monthly Revenue
Jan. | 401,255 | 36.8%
Feb. | |
Total | 401,255 | 36.8%
"""
    previous_year = """
### 2025 Monthly Revenue
Nov. | 276,058 | 34.0%
Dec. | 278,163 | 27.0%
Total | 3809,050 | 31.6%
"""

    observation = parse_tsmc_monthly_revenue_pages(current_year, previous_year)

    assert observation.latest_value == 36.8
    assert observation.previous_value == 27.0
    assert observation.direction == "改善"


def test_get_proxy_map_reads_uppercase_and_lowercase_env(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:7897")
    monkeypatch.setenv("https_proxy", "http://127.0.0.1:7898")

    proxies = get_proxy_map()

    assert proxies["http"] == "http://127.0.0.1:7897"
    assert proxies["https"] == "http://127.0.0.1:7898"


def test_fetcher_returns_gaps_instead_of_crashing_when_source_fails(monkeypatch):
    fetcher = MarketDataFetcher()

    def fail(url: str) -> str:
        raise TimeoutError(f"boom: {url}")

    monkeypatch.setattr("daily_investment_brief.fetchers._read_text", fail)

    observations, data_gaps = fetcher.fetch_sp500()

    assert observations == {}
    assert {gap["metric"] for gap in data_gaps} >= {"price_snapshot", "forward_pe", "pb", "us10y_yield", "vix", "cnn_fear_greed"}
