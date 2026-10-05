---
vendor: openai
title: “Helgoland Bite” 行动：德语影响活动
original_title: Operation “Helgoland Bite”: German-language influence activity
url: https://openai.com/index/disrupting-malicious-uses-of-ai-helgoland-bite
date: 2025-06-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# “Helgoland Bite” 行动：德语影响活动

OpenAI 封禁了疑似源自俄罗斯的账号，这些账号使用 AI 生成关于乌克兰、北约及德国国内议题的德语政治内容。

*本案例研究最初发表于 OpenAI 的 [*2025 年 6 月⁠（在新窗口打开）*](https://cdn.openai.com/threat-intelligence-reports/5f73af09-a3a3-4a55-992e-069237681620/disrupting-malicious-uses-of-ai-june-2025.pdf)* 报告。*

## 行为者

我们封禁了疑似源自俄罗斯的 ChatGPT 账号。它们使用我们的模型生成关于德国 2025 年选举的德语内容，并批评美国和北约。相关内容通过 Telegram 和 X 分发。

## 行为

通过平台外调查，我们确认相关的生成内容在一个名为 [“Nachhall von Helgoland”⁠（在新窗口打开）](https://t.me/nachhallvonhelgoland)（意为“黑尔戈兰的回响”，指北海黑尔戈兰湾的一座岛屿）的 Telegram 频道上被欺骗性地分发。该频道自称是本地运营的独立德语新闻，当时有 1,755 名订阅者。鉴于其名称以及该活动试图生成批评性评论的行为，我们将此行动命名为“Helgoland Bite”（黑尔戈兰之咬）。

该频道的内容被定期原文转发到一个与 [Pravda 网络⁠（在新窗口打开）](https://dfrlab.org/2025-03-12/pravda-network-wikipedia-llm-x/) 有关联、面向德语受众的域名上。相关的 Pravda（DE）网站是法国政府 VIGINUM 部门此前已识别的、与莫斯科有关联的隐蔽影响行动网络 [“Portal Kombat”⁠（在新窗口打开）](https://www.diplomatie.gouv.fr/en/french-foreign-policy/security-disarmament-and-non-proliferation/news/2024/article/foreign-digital-interference-result-of-investigations-into-the-russian) 中的一个已知节点。

*Pravda DE 网站上的文章，来源于 Nachhall von Helgoland。标题为“欧尔班会见魏德尔：‘AfD 是德国的未来’”。*

该网络还通过一个拥有超过 27,000 名粉丝的 X 账号分发由我们模型生成的内容，频繁发布支持德国选择党（AfD）的 AI 生成内容，并使用 AI 生成的头像。

*该威胁行为者使用我们的模型生成的推文。头像同样由我们的模型生成。推文写道：“等 AfD 最终上台，我们急需一个‘DOGE 部门’。它首先应该做的事是评估政客是否胜任，并在证明其不称职时追缴相关费用。我认为这能省下一大笔钱。”*

## 补全请求

除了生成短文章和社交媒体评论外，这些账号还向我们的模型询问德国反对派活动人士和博主的公开信息，包括联系他们的方式。他们还要求把短文本从俄语翻译成德语，其用语风格与信息传递或会话流量一致。其中一些消息似乎涉及协调社交媒体内容的发布时间，另一些则提及付款。

## 影响

如上所述，在我们调查时该 Telegram 频道有 1,755 名订阅者，其内容被定期原文转发到与 Pravda 网络有关联的域名上。那个 X 账号拥有超过 27,000 名粉丝。

按照 IO 影响评估的 [Breakout Scale⁠（在新窗口打开）](https://www.brookings.edu/articles/the-breakout-scale-measuring-the-impact-of-influence-operations/)，我们将其评估为第 2 类的偏上端：在多个平台活动，但几乎没有真实互动，也没有其内容被广泛传播的证据。
