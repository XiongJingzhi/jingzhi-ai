---
name: frontend-review-runner
description: 当编码 agent 需要打开真实前端页面、采集浏览器证据、编排多个评审 critic，并产出能驱动下一轮代码修改的最终评审结果时使用。
---

# Frontend Review Runner

## 概述

这个 skill 用来编排一次基于真实页面的前端评审循环。

它不负责给页面打分。它的职责是：
- 从真实运行页面采集证据
- 规范化评审输入
- 调用合适的 critics
- 把 critic 结果交给 judge
- 返回给主 coding agent 一份可执行的最终评审结果

## 什么时候使用

在以下情况使用：
- 主 agent 已经实现或修改了前端页面，想派一个 review subagent 来打分
- 评审必须基于真实页面证据，而不是只看源码推测
- 输出结果需要决定是否继续改代码

以下情况不要用：
- 任务本身是直接写 UI 代码
- 没有可运行页面，也没有任何截图证据，而用户只想听泛化建议

## 必要输入

- 页面背景信息（如果有）
- 本地启动命令或可访问的预览 URL
- 目标路由
- 访问该页面所需的登录、fixture、种子数据说明
- 当前阈值设置（如果不同于默认值）
- 当前是第几轮评审（如果不是首轮）

参见 `../frontend-review-shared/references/PAGE_REVIEW_TASK_TEMPLATE.md`。

## 工具契约

这个 skill 预期运行环境提供浏览器类能力，例如：
- `browser`
- `screenshot`
- `dom_inspector`
- `console`
- `network`
- `lighthouse`
- `accessibility`

这些是 runtime/tool 能力，不是独立的评分 skill。

如果某些工具缺失：
- 尽可能采集现有证据
- 明确标出缺失项
- 降低最终评审的置信度
- 不要假装完成了完整覆盖

## 工作流程

### 1. 确认评审范围

先确认：
- 页面类型（如果已知）
- 页面目标（如果已知）
- 目标路由
- 主操作
- 当前阈值

如果缺失，就根据页面证据做最小必要推断，并标记为推测。

### 2. 确认页面可达

- 打开目标 URL 或路由
- 确认页面至少渲染到了可评审状态
- 如果页面无法打开，直接返回 blocker，并附证据

### 3. 采集证据

尽可能采集以下内容：
- desktop screenshot
- mobile screenshot
- DOM snapshot
- 关键交互后的状态
- console logs
- network summary
- accessibility summary
- Lighthouse summary

至少应尝试拿到：
- 一个桌面视图
- 一个移动端视图
- 主内容区域 DOM
- 初始渲染期间的 console logs

### 4. 构建统一评审包

把评审输入规范化为：
- 页面背景
- 页面类型，以及是否为推测
- 页面目标，以及是否为推测
- 当前阈值
- 证据清单
- 缺失证据列表

### 5. 调用 Critics

将同一份评审包发送给：
- `frontend-ui-critic`
- `frontend-qa-critic`
- `frontend-a11y-perf-critic`

如果某个 critic 需要补充交互检查，只在确实影响最终判断时再补采。

### 6. 调用 Judge

将所有 critic 输出以及统一评审包交给 `frontend-review-judge`。

### 7. 返回最终结果

将 judge 的输出作为本轮评审的最终结果返回给主 coding agent。

## 升级规则

- 页面打不开，直接视为 blocker
- 目标路由需要登录或前置数据，但当前无法满足时，应明确说明缺失前提，不要硬猜
- 证据不完整但仍有评审价值时，可以继续做降级评审

## 输出要求

最终结果必须让主 agent 能明确知道：
- 是否要继续迭代
- 哪些问题阻塞发布
- 下一轮最值得改的 3 到 5 个点是什么
- 哪些区域不该无关扩散修改

runner 应保持简洁，重点做编排，不替 critics 和 judge 代打分。
