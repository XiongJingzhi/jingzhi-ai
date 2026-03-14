# Analyze Prompt Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 用中文重写分析提示词，并新增对关键章节结构的测试。

**Architecture:** 保持分析阶段的数据流不变，仅替换 prompt 内容。测试直接读取 prompt 文件断言关键章节，避免依赖真实 LLM 输出。

**Tech Stack:** Markdown prompt files, pytest

---

### Task 1: Add a failing prompt-structure test

**Files:**
- Modify: `skills/video-remix/tests/stages/test_analyze.py`
- Test: `skills/video-remix/tests/stages/test_analyze.py`

**Step 1: Write the failing test**

新增一个测试，断言 `analyze.md` 包含中文章节：
- `## 原文的分段文稿（完整）`
- `## 核心论点`
- `## 金字塔结构拆解`
- `## 反对者视角`
- `## 传播营销视角`

**Step 2: Run test to verify it fails**

Run: `pytest skills/video-remix/tests/stages/test_analyze.py -q`

Expected: FAIL，因为当前 prompt 仍是旧结构。

### Task 2: Rewrite the analyze prompt

**Files:**
- Modify: `skills/video-remix/resources/prompts/analyze.md`

**Step 1: Write minimal implementation**

将提示词改成中文固定结构，明确要求完整分段文稿、核心论点、金字塔结构、反对者视角、传播营销视角等。

**Step 2: Run tests to verify they pass**

Run: `pytest skills/video-remix/tests/stages/test_analyze.py -q`

Expected: PASS

### Task 3: Verify the skill package

**Files:**
- Test: `skills/video-remix/tests`

**Step 1: Run relevant suite**

Run: `pytest skills/video-remix/tests -q`

Expected: PASS
