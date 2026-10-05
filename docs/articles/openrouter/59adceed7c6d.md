---
vendor: openrouter
title: 开饭了
original_title: Dinner is Served
url: https://openrouter.ai/blog/insights/dinner-is-served
date: 2026-06-11
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 开饭了

几周前我和团队在旧金山参加一个会议。我们原本订了一家很普通的美式餐厅吃晚饭，但另有打算的我临时快速改主意，改订了一家寿司店。临时变更不算理想，但在展台站了一整天之后吃一顿平庸的饭同样不理想。再说，谁不爱寿司呢？

过去十年，我和太太每一个庆祝活动都是吃寿司 omakase（主厨发办）。不看菜单我也知道怎么点。大多数寿司新人直奔 O-toro（金枪鱼大腹），但那之外的世界大得多。所以很自然地，我告诉大家这桌由我来点。朋友、家人、同事，我一直都这么干，而且百分之百的情况下，大家都愿意在这个特定场景里把决定权外包出去，安心享受一顿饭。

关于怎么吃饭，我有一个坚定的主张：家庭式共享，永远如此。

## 保留选择权的理由

为什么？一方面，它降低了单独点菜踩雷的风险——免得你那份 Hawaiian ribeye 难吃得要命；另一方面，它放大了那种记忆——「天哪，那口鱼子酱配和牛是我今年吃过最好的一口」。那个时刻会留在我们心里。我一直说，第一次去某家店，什么都尝一点，不够随时再加。但这只有在家庭式共享的前提下才成立。

把 LLM 标准化在一家上，就等于每人各点各的主菜。你可能在优化「安全的选择」，而不是最好的结果。我和数以百计的公司聊过，他们开始 AI 之旅时选定了一家 provider——比如 OpenAI、Anthropic 或 Gemini。当你在一家上标准化时，你下的赌注基于你今天知道的和你今天需要的。就是那句老话「买 Salesforce 不会有人被开除」，只是这老话也在变了。等我聊到这些公司时，他们大多已经准备好「毕业」——不止用一家模型家族、不止用一种模态。新用例每天都在冒出来。常见剧本长这样：

- 从 OpenAI enterprise 起步，给少数几个团队发放 license。
- 监控首批用户的使用情况，趋势一路上扬。
- 把访问权限开放给更多团队。
- 图像生成、转录、创意写作等新用例开始出现。
- 发现 OpenAI 并不是你这些场景的最佳模型，你需要 Gemini。
- 去 Gemini 或其他 provider 配置接入，然后发现 observability、governance 和 provisioning 全都散了架。

我今天看到的现状表面上是成本压力，但比那更深。公司们[已经烧穿了年度预算](https://fortune.com/2026-05-26/uber-coo-ai-spending-tokens-claude-code/)，而现在才六月。大家强烈希望减少 token 用量，这我理解。如果你不小心用了 Opus 4.8，可能一天预算就没了，然后你毫无选项。合上笔记本电脑，出门散步去吧。

Opus 4.7 的牌价没变，但不少人写了关于「tokenizer tax」的事。这是 Anthropic 做的一次静默变更，输入 token 几乎增加了 35%。这是实打实的变化。更强更新款的模型也在涨价。Anthropic 发布了 Fable，定价每百万输入 token $10、每百万输出 $50。还有更贵的：OpenAI 的 GPT-5.5 Pro 达到每百万输入 $30、每百万输出 $180。谨慎使用！

成本压力是一种强制机制，它可能导向更好或更坏的结果。从我的参照系看，我乐观地认为它正带来一些更好的结果。我也够幸运，正在促成这些结果。这在我做数据基础设施的年代是共同主题。太多对话绕着算力成本和数据仓库的花费转。但那过于关注**显性**成本，而忽略了**隐性**成本。最有战略眼光的领导者会把这场对话倒过来讲。我经常听到的是：「我一年已经在算力上花 $1M 了，所以把它砍 30% 我没那么在意。更值钱的是我那 40 个分析师、一年 $7M 的团队能干得更快更好。开发者工具上我既要**速度**也要**效率**。」

## 路由是一等公民

在进入下一节之前，先快速说明 OpenRouter 到底是什么。OpenRouter 是访问 AI 的权威市场。我们让推理开箱即用。我们移除围绕选 provider、选模型，以及搞清延迟、价格、TPS、模型基准等等的一切开销。

于是你可以通过 OpenRouter 在一个干净、标准化的 API 规范里访问数百个 LLM。这东西存在多了不起？这一切听起来好到你似乎可以「既要蛋糕又吃掉它」——但现实中人们实际怎么做？

幸运的是我拉到了一些相关数据。今天团队正好发布了我们的 [analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data)， timing 堪称天意！

![Multi-Model Adoption Is Accelerating: indexed growth of users trying 2+, 5+, and 10+ models, Jan–May 2026, reaching 2.13x](https://openrouter.ai/blog/images/dinner-is-served/multi-model-adoption.png)

多模型采用一直是我们的一个假设，现在能清楚看到与这个故事同步的增长趋势。这合乎预期，但它掩盖了一个事实：大多数人也许只是在追每款模型的最新版本。例如，Anthropic 在这张图的时间线内发布了 Opus 4.6、Opus 4.7 和 Opus 4.8。更有意思的是用户跨模型家族的采用情况。

![Cross-Family Model Adoption Is Accelerating: indexed growth of users spreading inference across 2+, 3+, 5+, and 7+ model families, Jan–May 2026, reaching 2.10x](https://openrouter.ai/blog/images/dinner-is-served/cross-family-adoption.png)

这里我们捕捉到的，是用户真正把推理负载铺到多个模型家族上的真实增长。它描绘出「持续毕业」更现实的样子。再叠一个关于模型发布的数据点。

![New Models Added to OpenRouter: cumulative new models Jan–May 2026, climbing from 17 to 233](https://openrouter.ai/blog/images/dinner-is-served/new-models-added.png)

因为发布节奏并不总是均匀，这是累计图。但能看到 3 月到 4 月之间一个大异常：**90** 款新模型发布。太猛了！可选项以越来越快的速度暴增。

这也会让人有点压力。就像走进一家菜单有 [225 道菜](https://jitladala.com/menu/)的餐厅（我最爱的餐厅之一），就算家庭式共享你也点不完。我们当然想过这个，不希望用户必须分清每个模型之间的差别。所以我们做了 [auto-router](https://openrouter.ai/docs/guides/routing/routers/auto-router) 和 [pareto-router](https://openrouter.ai/docs/guides/routing/routers/pareto-router)，让「该用哪个模型」变得更容易。

这一切又绕回我前面说的成本压力。公司们实际在用一种很有意思的方式使用 OpenRouter：他们能把平均每加权 token 成本**随时间降下来**。怎么做到的？如果你按所需结果把特定负载路由到特定 provider 和模型，你就可以利用像 DeepSeek V4 Flash 这样的模型——输入约每百万 token $0.10、输出 $0.20。

再进一步，用上像 Cerebras 这样吞吐名列前茅的 provider，你就是 Bradley Cooper 那位 maestro（指挥家）——只不过脏活累活我们替干了。

![OpenRouter model page for gpt-oss-120b showing the Cerebras provider with 0.23s latency and 362 tps throughput](https://openrouter.ai/blog/images/dinner-is-served/gpt-oss-120b-cerebras.png)

或者，把你的部分流量路由到 Gemini 模型的 **flex** 优先级档，吃下五折优惠。选择权在你。

![OpenRouter model page for Google Gemini 3.5 Flash highlighting the flex tier pricing at 50% off](https://openrouter.ai/blog/images/dinner-is-served/gemini-flex-pricing.png)

围绕模型智能，我们还有一些令人兴奋的东西很快会分享。总体而言主题不变：我们让推理开箱即用。

## Semper ad meliora（永远朝向更好）

驱动 AI 采用的顺风，正在转向 AI 优化。我们明白，花在 AI 推理上的钱不会以什么有意义的幅度减少，那退而求其次是什么？是把平均每加权 token 成本降下来。组织在治理降风险的同时，也正更有意识地把使用民主化到各团队。而只有当你不被锁死在单一 vendor 时，这事才真正发生。当你为不同用例选择不同模型，你在每一步都获得杠杆。你终于能坐上饭桌，家庭式共享，随便吃。
