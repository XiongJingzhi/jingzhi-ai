# daily-investment-brief pressure tests

这些样例用于验证 skill 不会退化成空洞总结，也不会让情绪指标喧宾夺主。

## 1. SP500 上涨但内核转弱

输入特征：
- `price_snapshot.direction = 上升`
- `forward_pe.direction = 上升`
- `eps_revision.direction = 下修`
- `us10y_yield.direction = 上升`
- `market_breadth.direction = 恶化`
- `cnn_fear_greed.direction = 下降`
- `vix.direction = 上升`

期望：
- 结论不能是 `偏正面`
- 优先为 `偏谨慎` 或 `信号分化`
- 风险点必须提到“指数上涨但广度恶化”

## 2. 纳指上涨但利率和美元施压

输入特征：
- `price_snapshot.direction = 上升`
- `forward_pe.direction = 上升`
- `eps_revision.direction = 持平`
- `us10y_yield.direction = 上升`
- `dxy.direction = 上升`
- `concentration.direction = 上升`
- `cnn_fear_greed.direction = 上升`
- `vix.direction = 持平`

期望：
- 结论不能直接给 `偏正面`
- 必须说明“上涨质量依赖少数龙头”或同义表达

## 3. 半导体价格强但景气未确认

输入特征：
- `price_snapshot.direction = 上升`
- `global_semiconductor_sales_growth.direction = 持平` 或 `恶化`
- `tsmc_monthly_revenue_yoy.direction = 持平` 或 `恶化`
- `equipment_order_trend.direction = 持平` 或 `恶化`
- `forward_pe.direction = 上升`
- `us10y_yield.direction = 上升`

期望：
- 结论应保守，不能给 `偏正面`
- 一句解释必须把“价格走强”和“景气未确认”同时写出来

## 4. A股红利低波上涨但相对优势走弱

输入特征：
- `price_snapshot.direction = 上升`
- `dividend_yield.direction = 下降`
- `pb.direction = 上升`
- `china10y_yield.direction = 持平` 或 `上升`
- `excess_return_vs_csi300.direction = 恶化`

期望：
- 结论不能给明确顺风
- 风险点必须提到相对沪深300不再占优

## 5. 只有情绪指标改善

输入特征：
- 仅 `cnn_fear_greed` 与 `vix` 有值
- 其他核心指标缺失

期望：
- 结论只能保守
- 必须出现“当前缺少该项关键数据，结论只能暂时保守，不得强下判断”
- 不得把情绪指标写进 `【最新关键数据】`

## 6. 缺少前三优先级关键数据之一

输入特征：
- 任一资产缺少前 3 优先级中的 1 项

期望：
- `confidence = low`
- 结论不能是强方向
- `data_gaps` 必须把该项标为 `core`

## 7. 多项信号冲突

输入特征：
- 至少两项核心顺风
- 至少两项核心逆风

期望：
- 结论为 `信号分化`
- 报告中明确写出 `当前信号分化，暂不支持强结论。`

## 8. 关键数据展示不完整

输入特征：
- 任一关键数据只有名称和最新值，没有方向或含义

期望：
- 输出视为不合格
- 需要补齐“最新值 + 方向 + 含义”三要素后才可交付
