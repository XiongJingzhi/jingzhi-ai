# daily-investment-brief

为四类资产生成“少而硬”的每日投资简报：
- 标普500
- 纳斯达克100
- 半导体指数
- A股红利低波

这个 skill 只保留最关键的数据和方向变化，先给结构化 `analysis_json`，再输出固定格式的中文短报告。

核心特点：
- 只用限定指标池
- 按数据频率自适应比较前值
- 用硬规则落地 `偏正面 / 偏中性 / 偏谨慎 / 信号分化`
- 情绪指标必须出现，但只能辅助确认
- 核心数据缺失时自动保守，不强下判断

验证：

```bash
python3 skills/daily-investment-brief/validate_skill.py
```
