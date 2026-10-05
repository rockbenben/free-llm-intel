---
vendor: openai
title: Choco 用 AI agent 自动化食品配送
original_title: Choco automates food distribution with AI agents
url: https://openai.com/index/choco
date: 2026-10-02
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Choco 用 AI agent 自动化食品配送

借助 OpenAI API，Choco 处理数百万订单，减少人工操作，让全球食品供应链实现全天候运转。

公司规模：中型市场企业；区域：全球；行业：餐饮、科技；产品：API。

成果：年处理订单 880 万+；生产环境处理 AI token 2,000 亿+；人工录单减少 50%；不增加人手，销售团队生产力翻倍。

## 为 AI 时代重建食品配送

[Choco](https://choco.com/us?utm_campaign=391918817-Global%20%7C%202026%20%7C%20OpenAI%20Case%20Study&utm_source=OpenAI%20Website&utm_medium=OpenAI&utm_term=Case%20Study) 是一个 AI 驱动的平台，正在为食品饮料配送现代化，服务美国、英国、欧洲和海湾国家的 21,000 多家经销商和 100,000 家买方。通过把餐厅、供应商和经销商连接进统一系统，Choco 简化了食品供应链上的下单、销售和客户管理。

随着订单量增长，Choco 撞上了一个大瓶颈：订单仍然通过邮件、短信、语音留言、图片甚至手写便条进来。团队要人工把这些输入翻译成结构化的 ERP 订单——缓慢、易错，限制规模，还制造持续不断的经营摩擦。

> "处理这些输入是第一道门槛，却不是最难的一道。真正的问题在隐性上下文：客户专属的 SKU 映射、单位偏好、配送习惯。这些知识存在订单客服的脑子里，我们需要把它们编码进推理层，在订单录入的那一刻消解歧义。"
>
> ——Narbeh Mirzaei，工程副总裁

随着可用于生产的 LLM 成熟，Choco 看到机会：超越工作流软件，构建能直接执行工作的 AI 系统。OpenAI API 成为这场转型的核心。

## 部署内幕

Choco 把 OpenAI API 嵌入平台核心，驱动新一代 AI 原生产品。公司推出了 [**OrderAgent**](https://choco.com/us/orderagent?utm_campaign=391918817-Global%20%7C%202026%20%7C%20OpenAI%20Case%20Study&utm_source=OpenAI%20Website&utm_medium=OpenAI&utm_term=Case%20Study&utm_content=OrderAgent)，处理包括邮件、短信、图片和文档在内的多模态输入，并将其转换为结构化、可直接进入 ERP 的订单。

> "转写与抽取能力给了我们坚实的基础。真正的工程挑战是构建动态的上下文内学习（in-context learning）基础设施，让系统针对每个客户的下单历史和商品目录来消解歧义。这才是自动化与智能的分界线。"
>
> ——Narbeh Mirzaei，工程副总裁

Choco 还构建了由 OpenAI Realtime API 驱动的 [**VoiceAgent**](https://choco.com/uk/stories/suppliers/introducing-the-choco-voice-agent-built-by-choco-in-collaboration-with-openai)，让客户可以自然地通过电话下单，延迟低于一秒——即便在非营业时间。

选择 OpenAI，是看中其模型性能、多模态能力、结构化输出和大规模生产可靠性。能在一个生态内同时处理文本、视觉和音频，Choco 得以把此前彼此割裂的工作流统一成一个智能系统。

实施快速且可扩展。借助 OpenAI 的 SDK 和 API，Choco 迅速把语音转文字、embeddings、function calling 等能力集成进自己的基础设施。团队还搭建了严格的评估框架，配备基准真值数据集、持续监控和 A/B 测试，确保生产环境的准确性与性能。

采纳的推动力来自贯穿整个下单流程的无缝集成。客户不需要改变下单方式——无论电话、短信还是邮件，系统来适应他们。

> "一旦客户看到它真的在处理自己的订单，信任很快就来了。采纳就是从那时开始加速的。"
>
> ——Daniel Khachab，联合创始人兼 CEO

通过可选的"Autopilot"模式，经销商可以在置信度阈值满足时自动化订单处理，同时对边缘案例保留人工审核。随着时间推移，系统持续从纠错中学习，准确性和可靠性不断提升。

## 成果速览

- 年处理订单超过 880 万，消除了数百万次人工流程
- 人工录单最多减少 50%，释放团队投入更高价值的工作
- 实现 2 倍生产力提升，让团队无需加人即可扩张
- 在可配置的自动化阈值下，把错误率控制在 1%–5% 以内
- 支持 7×24 小时接收订单，消除夜间和周末造成的延迟

## 领导力经验

- 从第一天就做评估：即使是很小的基准真值数据集（10–20 个样本），也能让团队度量进展、验证改进、有信心地迭代。
- 投入 AI 原生的可观测性：调试 AI 系统远不止传统日志——捕获模型输入、输出和推理轨迹，对理解和提升性能至关重要。
- 尽早设定正确预期：与确定性软件不同，LLM 是概率性的。让团队和用户理解这一差别，是建立信任、避免采纳摩擦的关键。

## 下一步

Choco 持续在食品配送生态中扩展其 AI 能力，加深 agent 在执行复杂运营工作流中的角色。随着 AI 系统承担更多责任，公司正在赋能一类新的用户——不写工程的"agent 编排者"，他们设计并管理驱动业务成果的智能系统。

> "我们正从'辅助工作的软件'走向'真正干活的系统'。这一转变让我们的客户运营得更快、更精干、也更有韧性。"
>
> ——Daniel Khachab，联合创始人兼 CEO

展望未来，Choco 计划进一步扩展 OpenAI API 的使用，为销售、商贸和供应链运营中更自主、懂上下文的系统提供动力，继续完成从工作流软件到 AI 驱动的执行基础设施的转型。
