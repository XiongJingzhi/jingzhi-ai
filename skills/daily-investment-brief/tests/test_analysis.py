from daily_investment_brief.analysis import analyze_asset, render_report
from daily_investment_brief.models import MetricObservation


def obs(name: str, latest: float, previous: float, direction: str, implication: str = "") -> MetricObservation:
    return MetricObservation(
        name=name,
        latest_value=latest,
        previous_value=previous,
        comparison_basis="前一交易日",
        direction=direction,
        implication=implication,
    )


def test_sp500_missing_top3_metric_forces_conservative_stance():
    result = analyze_asset(
        asset_type="sp500",
        observations={
            "price_snapshot": obs("标普500", 6700, 6650, "上升"),
            "forward_pe": obs("Forward PE", 28.8, 28.5, "上升"),
            "us10y_yield": obs("10年美债", 4.28, 4.21, "上升"),
            "market_breadth": obs("市场广度", 40, 44, "恶化"),
            "vix": obs("VIX", 23.51, 27.19, "下降"),
        },
        data_gaps=[],
    )

    assert result["analysis_json"]["stance"] == "偏中性"
    assert result["analysis_json"]["confidence"] == "low"
    assert "eps_revision" in {gap["metric"] for gap in result["analysis_json"]["data_gaps"]}


def test_signal_conflict_returns_signal_split():
    result = analyze_asset(
        asset_type="nasdaq100",
        observations={
            "price_snapshot": obs("纳斯达克100", 22462.73, 22374.18, "上升"),
            "forward_pe": obs("Forward PE", 31.0, 30.2, "上升"),
            "eps_revision": obs("EPS预期", 250.0, 251.5, "下修"),
            "us10y_yield": obs("10年美债", 4.28, 4.21, "上升"),
            "cnn_fear_greed": obs("CNN恐惧贪婪指数", 22, 22, "持平"),
            "vix": obs("VIX", 23.51, 27.19, "下降"),
        },
        data_gaps=[],
    )

    assert result["analysis_json"]["stance"] == "信号分化"
    assert "当前信号分化" in result["report_text"]


def test_nasdaq_structure_signal_can_trigger_split():
    result = analyze_asset(
        asset_type="nasdaq100",
        observations={
            "price_snapshot": obs("纳斯达克100", 22462.73, 22374.18, "上升"),
            "forward_pe": obs("Forward PE", 31.0, 31.0, "持平"),
            "eps_revision": obs("EPS预期", 252.0, 252.8, "下修"),
            "us10y_yield": obs("10年美债", 4.28, 4.28, "持平"),
            "dxy": obs("DXY", 104.3, 104.3, "持平"),
            "concentration": obs("集中度", 57.45, 52.88, "上升"),
            "vix": obs("VIX", 23.51, 27.19, "下降"),
        },
        data_gaps=[],
    )

    assert result["analysis_json"]["stance"] == "信号分化"
    assert any(item["name"] == "集中度" for item in result["analysis_json"]["key_data"])


def test_rendered_report_keeps_sentiment_separate():
    result = analyze_asset(
        asset_type="semiconductor",
        observations={
            "price_snapshot": obs("半导体指数", 338.32, 337.83, "上升"),
            "us10y_yield": obs("10年美债", 4.28, 4.21, "上升"),
            "cnn_fear_greed": obs("CNN恐惧贪婪指数", 22, 22, "持平"),
            "vix": obs("VIX", 23.51, 27.19, "下降"),
        },
        data_gaps=[],
    )

    report = render_report(result["analysis_json"])
    assert "【最新关键数据】" in report
    assert "【情绪指标】" in report
    assert report.index("【情绪指标】") > report.index("【最新关键数据】")
