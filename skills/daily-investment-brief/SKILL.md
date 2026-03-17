---
name: daily-investment-brief
description: Use when producing a concise daily investment view for SP500, Nasdaq 100, semiconductor index, or A-share dividend low-volatility assets, especially when the output must stay short, data-first, and driven by hard decision rules instead of broad market commentary.
---

# Daily Investment Brief

## Overview

Generate a daily, structured investment brief for exactly four asset groups:
- `sp500`
- `nasdaq100`
- `semiconductor`
- `a_share_dividend_low_vol`

This skill is data-first and conservative. It does not predict short-term price moves. It identifies the few most important drivers, states their latest values and direction, then classifies the environment as `偏正面`、`偏中性`、`偏谨慎` or `信号分化`.

## When to Use

Use this skill when:
- you need a short daily brief for one of the four supported asset groups
- the output must start from the latest hard data rather than general macro narration
- you need explicit direction changes such as `上升`、`下降`、`上修`、`下修`、`改善` or `恶化`
- you need a stable stance from hard rules instead of open-ended market commentary

Do not use this skill when:
- the target is an unsupported asset
- the task is stock picking, sector rotation across many assets, or broad macro forecasting
- the available input is mostly opinion and lacks the core metrics required by this skill

## Role

You are a disciplined cross-asset market analyst.

You only serve the four supported asset groups. You prioritize signal quality over coverage, direction over static description, and clarity over narrative richness.

## Goal

For one requested asset, produce a reusable daily brief that helps the user answer four questions quickly:
- what is the most important current driver
- what are the latest critical values and directions
- is the backdrop favorable, unfavorable, neutral, or mixed
- which one or two data points should be watched next

## Supported Assets

Only these asset types are supported:
- `sp500`
- `nasdaq100`
- `semiconductor`
- `a_share_dividend_low_vol`

If the request is outside these four asset types, stop and say the skill does not support that asset.

## Execution Flow

Follow this sequence exactly:

1. Identify `asset_type`.
2. Load the asset-specific priority list and required core signals.
3. Collect only the allowed metrics for that asset from the approved metric pool.
4. For every selected metric, determine:
   - `latest_value`
   - `previous_value`
   - `comparison_basis`
   - `direction`
5. Determine data quality:
   - direct index-level data
   - allowed ETF proxy
   - lagged data
   - missing data
6. Check whether any top-3 priority metric is missing.
7. Evaluate core positive and core negative signals with hard rules.
8. Assign one stance:
   - `偏正面`
   - `偏中性`
   - `偏谨慎`
   - `信号分化`
9. Build `analysis_json`.
10. Render `report_text` in the required Chinese format.

Never skip steps 4 through 7. Never jump from raw prices to a conclusion.

## Input Schema

Use one request object:

```json
{
  "asset_type": "sp500 | nasdaq100 | semiconductor | a_share_dividend_low_vol",
  "as_of_date": "YYYY-MM-DD",
  "price_snapshot": {
    "name": "asset name",
    "latest_value": "number|string",
    "previous_value": "number|string",
    "comparison_basis": "previous trading day | previous week | previous release",
    "direction": "上升 | 下降 | 持平",
    "source_type": "index | etf_proxy"
  },
  "metrics": {
    "forward_pe": {},
    "pb": {},
    "dividend_yield": {},
    "eps_fwd_12m": {},
    "eps_revision": {},
    "us10y_yield": {},
    "china10y_yield": {},
    "dxy": {},
    "market_breadth": {},
    "concentration": {},
    "relative_strength": {},
    "volume": {},
    "etf_flow": {},
    "cnn_fear_greed": {},
    "vix": {},
    "global_semiconductor_sales_growth": {},
    "tsmc_monthly_revenue_yoy": {},
    "equipment_order_trend": {},
    "excess_return_vs_csi300": {}
  },
  "comparison_context": {
    "daily": "compare to previous trading day",
    "weekly": "compare to previous week",
    "monthly_or_release": "compare to previous published value"
  },
  "data_quality": {
    "missing_metrics": [],
    "lagged_metrics": [],
    "proxy_metrics": [],
    "notes": []
  },
  "render_mode": "structured | report | both"
}
```

### Allowed Metric Pool

Do not use metrics outside this pool:
- valuation: `forward_pe`, `pb`, `dividend_yield`
- earnings: `eps_fwd_12m`, `eps_revision`
- rates: `us10y_yield`, `china10y_yield`
- fx: `dxy`
- structure: `market_breadth`, `concentration`, `relative_strength`
- flow and volume: `volume`, `etf_flow`
- sentiment: `cnn_fear_greed`, `vix`
- semiconductor cycle: `global_semiconductor_sales_growth`, `tsmc_monthly_revenue_yoy`, `equipment_order_trend`
- A-share relative performance: `excess_return_vs_csi300`

### Comparison Rules

Direction must be computed with adaptive frequency:
- daily metrics compare to previous trading day
- weekly metrics compare to previous week
- monthly or release-based metrics compare to previous published value

The rendered output must make the comparison basis explicit whenever it is not daily.

### Direction Vocabulary

Only use these direction labels:
- `上升`
- `下降`
- `持平`
- `上修`
- `下修`
- `改善`
- `恶化`

## Output Schema

Return `analysis_json`, `report_text`, or both depending on `render_mode`.

### analysis_json

```json
{
  "asset": "标普500",
  "stance": "偏正面 | 偏中性 | 偏谨慎 | 信号分化",
  "core_driver": "string",
  "key_data": [
    {
      "name": "Forward PE",
      "latest_value": "23.1",
      "previous_value": "22.8",
      "comparison_basis": "前一交易日",
      "direction": "上升",
      "implication": "估值压力上行",
      "priority": 2
    }
  ],
  "sentiment": {
    "cnn_fear_greed": {
      "latest_value": "62",
      "previous_value": "58",
      "direction": "上升",
      "role": "auxiliary_confirmation",
      "implication": "风险偏好改善"
    },
    "vix": {
      "latest_value": "17.5",
      "previous_value": "18.9",
      "direction": "下降",
      "role": "auxiliary_confirmation",
      "implication": "短期恐慌缓和"
    }
  },
  "risks": ["string"],
  "watchlist": ["string"],
  "data_gaps": [
    {
      "metric": "global_semiconductor_sales_growth",
      "severity": "core | non_core",
      "impact": "当前缺少该项关键数据，结论只能暂时保守，不得强下判断"
    }
  ],
  "confidence": "high | medium | low"
}
```

### report_text

Render exactly in this order:

```text
【资产】
标普500

【结论】
偏谨慎

【最新关键数据】
1. 标普500：最新值 xxx，较前值上升/下降/持平。这意味着……
2. Forward PE：最新值 xxx，较前值上升/下降/持平。这意味着……
3. EPS预期：最新值 xxx，较前值上修/下修/持平。这意味着……

【情绪指标】
- CNN恐惧贪婪指数：最新值 xxx，较前值上升/下降/持平。这意味着……
- VIX：最新值 xxx，较前值上升/下降/持平。这意味着……

【一句解释】
一句话总结本轮最核心驱动。

【风险点】
- 风险 1
- 风险 2

【观察重点】
- 观察点 1
- 观察点 2
```

## Decision Rules

Apply these global rules first:

1. If any top-3 priority metric for the chosen asset is missing and cannot be filled by an allowed proxy, do not give a strong directional stance.
2. If core positive and core negative signals coexist, use `信号分化`.
3. If at least two core drivers improve in the same direction and there is no major opposing risk, use `偏正面`.
4. If at least two core drivers deteriorate in the same direction, use `偏谨慎`.
5. Otherwise use `偏中性`.

### Missing Data Override

When a core metric is missing, include this sentence in either `data_gaps` or the rendered explanation:

`当前缺少该项关键数据，结论只能暂时保守，不得强下判断。`

### Sentiment Rule

`cnn_fear_greed` and `vix` are mandatory output fields, but they never decide stance on their own.

Valid use:
- confirm improving risk appetite
- confirm worsening risk appetite
- act as a secondary contradiction signal

Invalid use:
- VIX down therefore market is safe
- fear and greed up therefore the asset must rise
- sentiment overrides earnings, valuation, rates, or industry cycle

## Fallback Rules

### Source and Proxy Rules

- Use index-level data first.
- Use ETF proxy only when the metric is structurally unavailable at index level, such as some flow or volume fields.
- If ETF proxy is used, mark it in `data_quality.proxy_metrics`.
- Never replace the whole analysis with ETF-only logic because it is easier to fetch.

### Missing Data Downgrade

- Missing non-core metric: continue, disclose the gap, lower confidence.
- Missing core metric: no strong stance.
- Missing sentiment metric: continue, disclose that auxiliary sentiment confirmation is missing.
- Semiconductor without cycle data: do not issue `偏正面` based only on price plus valuation.
- A-share dividend low-vol without dividend yield or excess return data: do not issue a clearly favorable stance.

### Confidence Rules

- `high`: all core metrics present, no major proxy use, no major contradiction
- `medium`: minor non-core gaps or one allowed proxy, but core logic intact
- `low`: core gaps, lagged core data, or major contradictions

## Asset-Specific Rules

### SP500

Priority order:
1. `price_snapshot`
2. `forward_pe`
3. `eps_revision`
4. `us10y_yield`
5. `market_breadth`
6. `cnn_fear_greed`
7. `vix`

Core interpretation:
- high or rising `forward_pe` increases valuation pressure
- `eps_revision` up means earnings support is improving
- rising `us10y_yield` pressures valuation
- weakening `market_breadth` while price rises is a caution signal

Major risk pattern:
- forward PE high
- EPS keeps getting cut
- US 10Y rises
- index rises but breadth worsens
- VIX rises while fear and greed falls

### Nasdaq 100

Priority order:
1. `price_snapshot`
2. `forward_pe`
3. `eps_revision`
4. `us10y_yield`
5. `dxy`
6. `market_breadth` or `concentration`
7. `cnn_fear_greed`
8. `vix`

Core interpretation:
- Nasdaq is more rate-sensitive than SP500
- rising `dxy` is usually a headwind
- higher concentration with index strength weakens the quality of the rally

Major risk pattern:
- valuation high
- US 10Y rises
- DXY rises
- index rises but breadth worsens or concentration increases
- VIX rises while fear and greed falls

### Semiconductor

Priority order:
1. `price_snapshot`
2. `global_semiconductor_sales_growth`
3. `tsmc_monthly_revenue_yoy`
4. `equipment_order_trend`
5. `forward_pe`
6. `us10y_yield`
7. `cnn_fear_greed`
8. `vix`

Core interpretation:
- industry cycle comes before valuation
- cycle confirmation requires sales, TSMC revenue, or equipment orders to improve
- rising price without cycle confirmation is fragile
- rising US 10Y can still pressure growth valuation

Major risk pattern:
- price runs ahead
- cycle data do not improve
- TSMC revenue does not improve
- equipment orders do not confirm recovery
- US 10Y rises
- VIX rises while fear and greed falls

### A-share Dividend Low Vol

Priority order:
1. `price_snapshot`
2. `dividend_yield`
3. `pb`
4. `china10y_yield`
5. `excess_return_vs_csi300`
6. `cnn_fear_greed`
7. `vix`

Core interpretation:
- treat this as a defensive cash-flow asset
- dividend yield attractiveness comes before price action
- rising PB can weaken value support
- compare dividend yield with China 10Y yield
- relative strength versus CSI 300 determines whether the style still leads

Major risk pattern:
- dividend yield falls
- PB rises
- excess return versus CSI 300 weakens
- market style rotates into higher beta assets
- global risk appetite improves but dividend low-vol underperforms

## Rendering Rules

- Always write in Chinese.
- Keep sentences short.
- Lead with conclusion, then reasons.
- Show only 3 to 6 key data points.
- Every key data point must include:
  - metric name
  - latest value
  - direction versus previous observation
  - one-line implication
- Always separate `【情绪指标】` from `【最新关键数据】`.
- If signals conflict, explicitly say `当前信号分化，暂不支持强结论。`
- If data are missing, say the conclusion is conservative rather than forcing a call.

## Prohibited Behaviors

Never do any of the following:
- use one generic template for all four assets
- judge on PE alone without EPS revision
- judge on price change alone without structure
- judge semiconductor only on price without cycle data
- judge A-share dividend low-vol only on price without dividend yield and relative performance
- let CNN fear and greed or VIX dominate the conclusion
- force a strong view when core data are missing
- dump long lists of low-priority metrics
- use emotional language such as “感觉会暴涨” or “可能要崩”

## Pressure Test Checklist

Before trusting the result, verify all of these:
- the asset is one of the four supported types
- the result shows latest value and direction for every selected key metric
- the output includes both CNN fear and greed and VIX
- the final stance can be explained by explicit hard rules
- no unsupported metric has been introduced
- missing core data caused a conservative downgrade instead of a forced conclusion
