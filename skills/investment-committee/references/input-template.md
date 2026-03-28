# Household Investment Case Input Template

Ask the user to provide the following information. Keep the labels stable so different role agents can analyze the same normalized case.

```md
# 家庭投资案例输入模板

请基于以下背景进行分析，不要脱离这些事实自行脑补。

## 我的背景

* 投资目标：
* 投资期限：
* 家庭年新增可投资金：
* 当前总资产概况：
* 当前持仓明细：
* 现金及固收占比：
* 权益占比：
* 是否有房贷/车贷/其他固定负债：
* 未来 1-3 年是否有大额用钱计划：

## 本次决策问题

* 我现在想做的动作：
* 涉及金额：
* 为什么想这么做：
* 我担心的点：
* 如果不做，我担心错过什么：

## 约束条件

* 我不接受的风险：
* 最大可接受回撤：
* 是否允许分批：
* 是否允许长期被套：
* 是否需要保留应急金：

## 输出要求

请只根据我的目标、约束和资金属性分析，不要默认我是激进投资者。若信息不足，请明确指出“这会影响判断”，但仍然要基于现有信息给出最佳分析。
```

## Normalization Rules

- Preserve the user's original facts and numbers.
- If the user gives messy free text, rewrite it into the template before spawning role agents.
- If a field is unknown, mark it as `未提供`.
- Do not fill unknown fields with optimistic assumptions.
