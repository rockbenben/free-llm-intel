---
vendor: aws_bedrock
title: Control agent behaviors and cost beyond a single action: new capabilities in Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/control-agent-behaviors-and-cost-beyond-a-single-action-new-capabilities-in-amazon-bedrock-agentcore
date: 2026-08-06
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 308ae473ee0a
---

# 控制单个动作之外的 agent 行为与成本：Amazon Bedrock AgentCore 的新能力

agent 正变得越来越自主，团队运行的 agent 也越来越多，但信任与安全并没有跟上。根据 McKinsey 的数据，大约 80% 的组织已经遇到过 AI agent 的危险行为。因此，安全与风险方面的顾虑成为扩展 agentic AI 的首要障碍（McKinsey 的《2026 年 AI 信任状况》与《AI agent 时代的信任（2026）》）。

这使得信任成为 agent 创新与采用的节拍因素。要赢得信任，需要在很广的范围上建立控制，包括身份、访问、可观测性、评估和可追溯性。我们相信，对信任与安全的投入将加速 agent 在企业中的采用。当护栏可靠时，批准一个新 agent 就不再是一次性谈判，而成为平台能够规模化处理的事情。

问题在于，如今大多数护栏是为行为可预测的软件设计的。agent 边走边决定自己的路径，因此每一步单独看都可能通过，而整体的形态却无人审视。一个 agent 查询了客户的账户，然后把钱转到另一个账号，因为每次调用都是单独判定的。一个 agent 下了一系列订单，每笔都在批准阈值之下，因为没有任何机制跟踪总额是否超出预算。一个 agent 遇到失败的工具便整夜重试，把 token 预算耗尽，因为没有任何机制限制它能消耗多少。这些请求每一个都是合法的。问题只出现在模式之中，而 agent 恰恰是你最不能指望来发现它的东西。

我们构建 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)，是为了让团队在规模化构建、连接和优化 agent 时无需自己拼装基础设施。从一开始就有一条原则指引它：安全控制属于基础设施层，应在每个 agent 上一致地强制执行，而不是放在应用代码里、由每个团队各自实现成不同的样子。

AgentCore 的 gateway 正是这一想法落地的地方。gateway 是面向 AI 流量的全托管、无服务器入口，把请求路由到 Model Context Protocol（MCP）服务器、大语言模型（LLM）、agent 和知识库。由于每一次调用都经过它，gateway 自然是施加限制的合适位置——无论 agent 如何行事，这些限制都成立。今天我们以新能力推进这项工作：由 [Dogwood](https://github.com/dogwood-policy)（一种专为 AI agent 打造的新开源策略语言）驱动的时间策略，以及 gateway 中的速率限制。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/05/Screenshot-2026-08-05-at-6.32.14 PM.png)

## 不只约束单个动作，还用时间策略约束动作序列

AgentCore 中现有的策略让团队对 agent 行为拥有确定性控制：在每次动作运行前检查，评估谁能调用哪个工具、在什么条件下。这些检查在设计上是无状态的。每个请求都按其自身情况被快速、可证明地判定，这正是授权一贯的要求。当 agent 承担更长、更少监督的任务时，另一个问题就出现了：它的这些动作合在一起，是否构成某种本应被允许的东西？这只有在你查看动作序列、而不只是单个动作时才可见。

时间策略扩展了 AgentCore 中的策略，以填补这一缺口。策略引擎不再孤立地判定请求，还会查看 agent 在该会话中已经做了什么，然后基于这段动作序列允许或拒绝该调用。转错账号的那笔转账，可以被一条要求「传入某次调用的值必须与先前某次调用返回的值一致」的策略拦下。策略可以累计 agent 在一个会话中已花费的金额，并在达到预算后阻止下一笔购买，即使这笔购买低于单笔限额。团队还可以要求各步骤按固定顺序发生，或者要求重大动作必须有一次记录在案的人工批准。当人员不再参与时，权限可以自动收窄。

时间策略在 gateway 层强制执行，位于 agent 自身代码之外。agent 看不到策略逻辑，也无法绕过它推理，无论它被如何提示，或带有何种缺陷。对于需要批准自主系统的安全负责人而言，这才是关键的区别：信任一个 agent 会好好表现，与知道边界在它一串动作的整个过程中都成立，是两回事。决策是确定性的、默认拒绝，并连同完整上下文一起记录。复核者不只能看到某次调用被阻止，还能看到为什么。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/05/Screenshot-2026-08-05-at-6.32.28 PM.png)

驱动时间策略的是 Dogwood，一种专为 AI agent 打造的新策略语言。Dogwood 以 Cedar 为基础构建，旨在应对 agent 控制的一个新维度：在 agent 的动作序列展开的过程中，评估它是否符合策略。Dogwood 内嵌 Cedar，并增加了用于 agent 治理的时间构造，包括速率限制、时间窗口、前置步骤和升级触发条件。Dogwood 以 Apache 2.0 许可证提供开源规范和参考实现。这让客户能完整看到其策略是如何被求值的，也让更广泛的生态可以构建配套工具。

## 用 gateway 上的限流控制 agent 的消耗

AI 成本本身就是一个治理问题，而在 agent 场景下，它首先取决于 agent 消耗 token 和调用的速度。agent 会按它判断的必要程度执行任意多的步骤，因此一个任务花多少钱取决于它选择怎样工作，而不是某个预先确定的速率。如果不加限制，一个重试循环或一次异常繁重的会话就会以 agent 自定的速度消耗资源。这种不可预测性是审批的真实障碍。Forrester 发现，agentic AI 很少能规模化，其起点就是成本（[《2026 年 agentic AI 状况》](https://www.forrester.com/blogs/the-state-of-agentic-ai-in-2026-companies-are-chasing-few-are-catching/)）。团队需要一个无论 agent 如何行事都成立的上限。

这项能力今天已经可用，你可以直接在 AgentCore 的 gateway 上设置这些上限。[限流](https://aws.amazon.com/blogs/machine-learning/configure-rate-limits-for-ai-traffic-on-agentcore-gateway/)让团队按照他们已通过 OAuth 或 IAM 管理的身份，对 gateway 背后所有工具、模型和 agent 的每用户消耗设定上限。限制可以覆盖某人发起多少次请求、模型为其处理多少个 token，以及他们把连接保持打开多久。三者都重要，因为 agent 抬高成本的方式各不相同。重试循环表现为请求量，推理密集的任务表现为 token，而长时间的研究会话则表现为连接一直打开却几乎没有流量通过。任何单一度量都会留下耗尽服务却不触发限制的空档。

限制以每秒和每分钟的窗口生效，这正是为了抑制团队实际遇到的失败模式：agent 以没人想要的速率消耗资源，且是事后才发现。速率限制在配置后立即生效，无需改动 agent 代码。容量分配于是变成平台团队去配置、而不是去构建的东西。不同用户、团队、工具和模型可以有不同的上限，而无需把限流逻辑写进它们中的任何一个。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/06/Screenshot-2026-08-06-at-11.41.58 AM.png)

## 接下来的方向

模型在持续进步，正是这种进步让 agent 值得部署。它同时抬高了风险，因为能力更强的 agent 会在更少监督下采取更有后果的动作。企业从更好的模型中获得的回报，取决于它能否以对待生产中其他一切事务同样的纪律来运行这些 agent。

对 agent 的信任其实并不是对模型的判断，而是对模型运行在其中的那个系统的判断，以及当 agent 出现意外行为时该系统是否守得住。构建这样的系统是一门年轻的学科，如今客户带给我们的问题明显比一年前更精细。我们预计会在这里持续快速推进，同时继续在身份、可观测性、评估和可追溯性上投入。每一项从应用代码转移到平台的控制，都意味着少了一件必须为每个 agent 单独重建、审阅和信任的事情。平台越能可靠地限定 agent 做什么、消耗多少，你就能越放心地给予更多自主权。

这两项能力都不需要重新架构已在生产中的 agent，你也可以单独采用其中任意一项。要了解更多，请参阅 AgentCore 的[文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)和[定价页面](https://aws.amazon.com/bedrock/agentcore/pricing/)，并探索 [Dogwood 参考实现](https://github.com/dogwood-policy)。

## 关于作者
