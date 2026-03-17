from __future__ import annotations

from dataclasses import asdict

from .models import DataGap, MetricObservation


MISSING_IMPACT = "当前缺少该项关键数据，结论只能暂时保守，不得强下判断。"
SPLIT_IMPACT = "当前信号分化，暂不支持强结论。"

ASSET_LABELS = {
    "sp500": "标普500",
    "nasdaq100": "纳斯达克100",
    "semiconductor": "半导体",
    "a_share_dividend_low_vol": "A股红利低波",
}

PRIORITIES = {
    "sp500": ["price_snapshot", "forward_pe", "eps_revision", "us10y_yield", "market_breadth"],
    "nasdaq100": ["price_snapshot", "forward_pe", "eps_revision", "us10y_yield", "dxy", "market_breadth", "concentration"],
    "semiconductor": [
        "price_snapshot",
        "global_semiconductor_sales_growth",
        "tsmc_monthly_revenue_yoy",
        "equipment_order_trend",
        "forward_pe",
        "us10y_yield",
    ],
    "a_share_dividend_low_vol": [
        "price_snapshot",
        "dividend_yield",
        "pb",
        "china10y_yield",
        "excess_return_vs_csi300",
    ],
}

SECONDARY_PRIORITIES = {
    "sp500": ["pb", "dividend_yield"],
    "nasdaq100": ["market_breadth", "concentration", "dividend_yield"],
    "semiconductor": ["concentration", "dividend_yield"],
    "a_share_dividend_low_vol": ["volume"],
}


def _build_gap(metric: str, severity: str = "core") -> dict[str, str]:
    return asdict(DataGap(metric=metric, severity=severity, impact=MISSING_IMPACT))


def _implication(metric_key: str, direction: str) -> str:
    mapping = {
        "forward_pe": {"上升": "估值压力上行", "下降": "估值压力缓和", "持平": "估值变化有限"},
        "pb": {"上升": "估值支撑走弱", "下降": "估值支撑改善", "持平": "估值变化有限"},
        "us10y_yield": {"上升": "利率对估值形成压力", "下降": "利率压力缓和", "持平": "利率影响中性"},
        "china10y_yield": {"上升": "股息比较优势收窄", "下降": "股息比较优势改善", "持平": "利率比较变化有限"},
        "market_breadth": {"改善": "上涨扩散度改善", "恶化": "上涨质量转弱", "持平": "结构变化有限"},
        "concentration": {"上升": "龙头集中度抬升，结构扩散不足", "下降": "龙头集中度回落，结构更均衡", "持平": "集中度变化有限"},
        "eps_revision": {"上修": "盈利预期改善", "下修": "盈利预期转弱", "持平": "盈利预期变化有限"},
        "dxy": {"上升": "美元走强通常不利成长估值", "下降": "美元压力缓和", "持平": "美元影响中性"},
        "dividend_yield": {"上升": "股息吸引力提升", "下降": "股息吸引力回落", "持平": "股息吸引力稳定"},
        "excess_return_vs_csi300": {"改善": "相对收益继续占优", "恶化": "防御风格相对优势转弱", "持平": "相对表现变化有限"},
        "global_semiconductor_sales_growth": {"改善": "行业景气继续回升", "恶化": "行业景气修复放缓", "持平": "行业景气变化有限"},
        "tsmc_monthly_revenue_yoy": {"改善": "龙头营收验证需求回暖", "恶化": "龙头营收动能走弱", "持平": "龙头营收动能变化有限"},
        "equipment_order_trend": {"改善": "设备订单开始回暖", "恶化": "设备订单仍未确认回升", "持平": "设备订单仍待确认"},
        "volume": {"上升": "成交活跃度提升", "下降": "成交活跃度回落", "持平": "成交活跃度变化有限"},
        "cnn_fear_greed": {"上升": "风险偏好改善", "下降": "风险偏好走弱", "持平": "风险偏好变化有限"},
        "vix": {"上升": "短期避险情绪升温", "下降": "短期恐慌缓和", "持平": "短期恐慌变化有限"},
        "price_snapshot": {"上升": "价格走势偏强", "下降": "价格走势转弱", "持平": "价格走势中性"},
    }
    return mapping.get(metric_key, {}).get(direction, "该指标方向需结合核心逻辑解读")


def _score_signals(asset_type: str, observations: dict[str, MetricObservation]) -> tuple[int, int]:
    positive = 0
    negative = 0

    for key, obs in observations.items():
        if asset_type == "sp500":
            if key == "price_snapshot" and obs.direction == "上升":
                positive += 1
            if key == "forward_pe" and obs.direction == "上升":
                negative += 1
            if key == "eps_revision" and obs.direction == "上修":
                positive += 1
            if key == "eps_revision" and obs.direction == "下修":
                negative += 1
            if key == "us10y_yield" and obs.direction == "下降":
                positive += 1
            if key == "us10y_yield" and obs.direction == "上升":
                negative += 1
            if key == "market_breadth" and obs.direction == "改善":
                positive += 1
            if key == "market_breadth" and obs.direction == "恶化":
                negative += 1
        elif asset_type == "nasdaq100":
            if key == "price_snapshot" and obs.direction == "上升":
                positive += 1
            if key in {"forward_pe", "us10y_yield", "dxy"} and obs.direction == "上升":
                negative += 1
            if key == "eps_revision" and obs.direction == "上修":
                positive += 1
            if key == "eps_revision" and obs.direction == "下修":
                negative += 1
            if key == "market_breadth" and obs.direction == "改善":
                positive += 1
            if key == "market_breadth" and obs.direction == "恶化":
                negative += 1
            if key == "concentration" and obs.direction == "下降":
                positive += 1
            if key == "concentration" and obs.direction == "上升":
                negative += 1
        elif asset_type == "semiconductor":
            if key == "price_snapshot" and obs.direction == "上升":
                positive += 1
            if key in {"global_semiconductor_sales_growth", "tsmc_monthly_revenue_yoy", "equipment_order_trend"} and obs.direction == "改善":
                positive += 1
            if key in {"global_semiconductor_sales_growth", "tsmc_monthly_revenue_yoy", "equipment_order_trend"} and obs.direction == "恶化":
                negative += 1
            if key == "us10y_yield" and obs.direction == "上升":
                negative += 1
        elif asset_type == "a_share_dividend_low_vol":
            if key == "dividend_yield" and obs.direction == "上升":
                positive += 1
            if key == "dividend_yield" and obs.direction == "下降":
                negative += 1
            if key == "pb" and obs.direction == "下降":
                positive += 1
            if key == "pb" and obs.direction == "上升":
                negative += 1
            if key == "excess_return_vs_csi300" and obs.direction == "改善":
                positive += 1
            if key == "excess_return_vs_csi300" and obs.direction == "恶化":
                negative += 1

    fear = observations.get("cnn_fear_greed")
    vix = observations.get("vix")
    if fear and vix and fear.direction == "下降" and vix.direction == "上升":
        negative += 1
    return positive, negative


def _stance(asset_type: str, observations: dict[str, MetricObservation], data_gaps: list[dict[str, str]]) -> tuple[str, str]:
    positive, negative = _score_signals(asset_type, observations)
    top3 = PRIORITIES[asset_type][:3]
    missing_top3 = [metric for metric in top3 if metric not in observations]
    if missing_top3:
        return "偏中性", MISSING_IMPACT
    if positive >= 1 and negative >= 2:
        return "信号分化", SPLIT_IMPACT
    if positive >= 2 and negative == 0:
        return "偏正面", "核心驱动整体偏顺风。"
    if negative >= 2:
        return "偏谨慎", "核心驱动偏逆风。"
    return "偏中性", "核心驱动暂未形成一致方向。"


def analyze_asset(
    asset_type: str,
    observations: dict[str, MetricObservation],
    data_gaps: list[dict[str, str]],
) -> dict[str, object]:
    priorities = PRIORITIES[asset_type]
    gaps = list(data_gaps)
    for metric in priorities[:3]:
        if metric not in observations and metric not in {gap["metric"] for gap in gaps}:
            gaps.append(_build_gap(metric))

    for metric in priorities[3:]:
        if metric not in observations:
            gaps.append(_build_gap(metric, severity="non_core"))

    stance, explanation = _stance(asset_type, observations, gaps)
    confidence = "low" if any(gap["severity"] == "core" for gap in gaps) else "medium"

    def append_key_data(metric_key: str, priority: int) -> None:
        obs = observations[metric_key]
        obs.implication = obs.implication or _implication(metric_key, obs.direction)
        key_data.append(
            {
                "name": obs.name,
                "latest_value": obs.latest_value,
                "previous_value": obs.previous_value,
                "comparison_basis": obs.comparison_basis,
                "direction": obs.direction,
                "implication": obs.implication,
                "priority": priority,
            }
        )

    key_data = []
    used_keys: set[str] = set()
    for priority, key in enumerate(priorities, start=1):
        if key in observations:
            append_key_data(key, priority)
            used_keys.add(key)
        if len(key_data) >= 6:
            break

    if len(key_data) < 4:
        for offset, key in enumerate(SECONDARY_PRIORITIES.get(asset_type, []), start=len(priorities) + 1):
            if key in observations and key not in used_keys:
                append_key_data(key, offset)
                used_keys.add(key)
            if len(key_data) >= 4:
                break

    sentiment = {}
    for key in ("cnn_fear_greed", "vix"):
        if key in observations:
            obs = observations[key]
            obs.implication = obs.implication or _implication(key, obs.direction)
            sentiment[key] = {
                "latest_value": obs.latest_value,
                "previous_value": obs.previous_value,
                "direction": obs.direction,
                "role": "auxiliary_confirmation",
                "implication": obs.implication,
            }
        else:
            gaps.append(_build_gap(key, severity="non_core"))

    analysis_json = {
        "asset": ASSET_LABELS[asset_type],
        "stance": stance,
        "core_driver": explanation,
        "key_data": key_data,
        "sentiment": sentiment,
        "risks": [gap["impact"] for gap in gaps if gap["severity"] == "core"][:2] or ["暂无额外风险提示"],
        "watchlist": [gap["metric"] for gap in gaps[:2]] or ["继续跟踪核心数据是否补齐"],
        "data_gaps": gaps,
        "confidence": confidence,
    }
    return {
        "analysis_json": analysis_json,
        "report_text": render_report(analysis_json),
    }


def render_report(analysis_json: dict[str, object]) -> str:
    key_lines = []
    for index, item in enumerate(analysis_json["key_data"], start=1):
        key_lines.append(
            f"{index}. {item['name']}：最新值 {item['latest_value']}，较前值{item['direction']}。{item['implication']}。"
        )

    sentiment = analysis_json["sentiment"]
    sentiment_lines = []
    fear = sentiment.get("cnn_fear_greed")
    if fear:
        sentiment_lines.append(
            f"- CNN恐惧贪婪指数：最新值 {fear['latest_value']}，较前值{fear['direction']}。{fear['implication']}。"
        )
    else:
        sentiment_lines.append("- CNN恐惧贪婪指数：当前缺失，辅助情绪确认暂不可用。")
    vix = sentiment.get("vix")
    if vix:
        sentiment_lines.append(f"- VIX：最新值 {vix['latest_value']}，较前值{vix['direction']}。{vix['implication']}。")
    else:
        sentiment_lines.append("- VIX：当前缺失，辅助情绪确认暂不可用。")

    risks = "\n".join(f"- {risk}" for risk in analysis_json["risks"][:2])
    watchlist = "\n".join(f"- {item}" for item in analysis_json["watchlist"][:2])

    extra = ""
    if analysis_json["stance"] == "信号分化":
        extra = f"\n{SPLIT_IMPACT}"

    return (
        f"【资产】\n{analysis_json['asset']}\n\n"
        f"【结论】\n{analysis_json['stance']}\n\n"
        f"【最新关键数据】\n" + "\n".join(key_lines) + "\n\n"
        f"【情绪指标】\n" + "\n".join(sentiment_lines) + "\n\n"
        f"【一句解释】\n{analysis_json['core_driver']}{extra}\n\n"
        f"【风险点】\n{risks}\n\n"
        f"【观察重点】\n{watchlist}\n"
    )
