---
vendor: minimax
title: MiniMax M2.1: 大幅提升多语言编程，为真实世界复杂任务而生 - MiniMax Research | MiniMax
original_title: 
url: https://www.minimax.cn/blog/minimax-m21
date: 2025-12-23
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: native
status: translated
body_sha: 773f223815af
---

MiniMax一直在用更AI原生的方式改造自己。这个过程的核心驱动力是模型、Agent脚手架和组织。在探索过程中，我们对上述三点也有了越来越深刻的认知。今天我们开放模型部分的更新，也就是MiniMax M2.1，希望有机会能帮助到更多的企业和个人早日找到更AI原生的工作方式。

在10月底的M2中，我们主要解决模型成本和模型开放性的问题。在M2.1中，我们致力于提升真实世界复杂任务中的表现：**重点聚焦于更多编程语言和办公场景的可用性，并在这个领域做到最好的水平**。

MiniMax M2.1 具体模型亮点如下:

- **卓越多编程语言能力** — 系统性提升了 Rust / Java / Golang / C++ / Kotlin / Objective-C / TypeScript / JavaScript 等语言的能力，多语言任务整体表现达到业内领先水平。
- **WebDev 与 AppDev：能力与美学的整体跃迁** — 显著加强了原生 Android / iOS 开发能力，系统性提升了模型在 Web 与 App 场景中的设计理解与美学表达能力。
- **复合指令约束提升，办公场景变为可能** — 率先系统性引入 Interleaved Thinking，systematic problem-solving 能力再次升级。
- **更简洁高效的回复** — 模型回复与思维链更加简洁，响应速度显著提升，Token 消耗明显下降。
- **出色的 Agent / 工具脚手架泛化能力** — 在 Claude Code、Cline、Kilo Code、Roo Code、BlackBox 等工具中展现一致且稳定的效果。
- **高质量对话和写作** — 在日常对话、技术说明与写作场景中提供更具细节与结构性的回答。

### 基准测试概览

在软件工程相关场景的核心榜单上，MiniMax-M2.1 相比于 M2 有了显著的提升，尤其是在多语言场景上，超过 Claude Sonnet 4.5 和 Gemini 3 Pro，并接近 Claude Opus 4.5。

我们在不同 coding agent 框架上测试了 SWE-bench Verified，结果表明 MiniMax-M2.1 具有良好的框架泛化性和稳定的表现。

为了衡量模型从零到一构建完整应用程序的全栈能力，我们构建并开源了全新基准 VIBE 测试集。MiniMax-M2.1 以平均 88.6 分展现了接近 Claude Opus 4.5 的全栈构建能力。

### 使用者评价

Eno Reyes (Factory), Benny Chen (Fireworks), Saoud Rizwan (Cline), Scott Breitenother (Kilo), Matt Rubens (RooCode), Robert Rizk (BlackBox AI) 等国际头部 AI 平台合作方一致认可 M2.1 在多语言编程、框架泛化性和生产级工程质量方面的突破性表现。

## Showcases

### 物理世界 Agent

M2.1 驱动维他动力的机器狗，展示了从虚拟世界到物理世界的泛化能力。

### 多语言 Coding

### 3D 交互式动画

基于 React Three Fiber 与 InstancedMesh 构建 3D 梦幻圣诞树，渲染 7000+ 实例，支持手势交互与复杂粒子动画。

### Web UI 前卫设计

### 原生 App - Android

### 原生 App - iOS

### Web 音频模拟

### Rust 安全审计 TUI

### Python 数据监控看板

### C++ 图像渲染

### Java 实时弹幕

## Agentic Tool Use

## 数字员工

M2.1 能够在日常办公场景下完成行政、数据科学、财务、人力资源、软件开发类的端到端任务。

## 如何使用

- API: platform.minimaxi.com
- Agent: agent.minimaxi.com
- Open Source: HuggingFace | GitHub

提供 M2.1 和 M2.1-lightning 两个版本 API，全面支持自动 Cache。

### 联系我们

算法和模型：model@minimax.io | 商务合作：api@minimax.io
