---
vendor: deepseek
title: DeepSeek-V4-Pro 正式版上线
original_title: 
url: https://api-docs.deepseek.com/zh-cn/news/news260813
date: 2026-08-13
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: native
status: translated
body_sha: e6b8cfb91842
---

# DeepSeek-V4-Pro 正式版上线

今天，我们发布 DeepSeek V4 Pro 正式版。

当前，DeepSeek V4 Pro 正式版已同步在 APP、网页端和 API 更新上线。用户可以通过 APP 或网页端选择“专家模式”使用全新的 V4 Pro 正式版模型，API 模型名不变，其他更新细节详见 DeepSeek API 官方接口文档。

## Agent 能力大幅提升

正式版 DeepSeek V4 Pro 增强了 Agent 能力，在生产环境中的性能表现提升尤为显著。

*对于公开基准测试集中的 Code Agent 任务，DeepSeek-V4-Pro-0813 使用 DeepSeek Harness 极简模式作为框架进行测试（使用 max 档位，topp=0.95，temperature=1.0），其他框架下结果可能略有不同。

## API 支持

### 原生支持 Responses API

DeepSeek API 现已原生支持 OpenAI Responses API 格式，并针对性适配 Codex。用户可以参考官方 API 文档：[快速开始 - 接入 Agent 工具 - Codex](https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/codex)，通过一键配置脚本完成 Codex 的配置。

### 更灵活的思考强度控制

V4-Pro 和 V4-Flash 思考模式现支持 low / high / max 三档思考强度，用户在实际使用中可以根据任务复杂度灵活选择：简单任务使用 low，日常 Agent 任务使用 high，高度复杂的任务场景使用 max。设置方法请参考官方 API 文档：[API 指南 - 思考模式](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode)。

## API 定价调整

随着 DeepSeek V4 全系列模型正式版上线，我们将对 API 价格进行更新调整。为了更加合理地调配资源，我们将采用峰谷定价，**闲时价格为高峰时段价格的一半**，鼓励用户根据实际使用情况调整任务时间。新价格将于**北京时间 2026 年 8 月 17 日 0 时**开始生效。

- [Agent 能力大幅提升](https://api-docs.deepseek.com/zh-cn/news/news260813/#agent-能力大幅提升)
- [API 支持](https://api-docs.deepseek.com/zh-cn/news/news260813/#api-支持)[原生支持 Responses API](https://api-docs.deepseek.com/zh-cn/news/news260813/#原生支持-responses-api)[更灵活的思考强度控制](https://api-docs.deepseek.com/zh-cn/news/news260813/#更灵活的思考强度控制)
- [API 定价调整](https://api-docs.deepseek.com/zh-cn/news/news260813/#api-定价调整)
