---
vendor: aws_bedrock
title: 纵深信任：给 agent 更多自主权，同时不失去控制
original_title: Trust in Depth: Giving agents more autonomy without losing control
url: https://aws.amazon.com/blogs/machine-learning/trust-in-depth-giving-agents-more-autonomy-without-losing-control
date: 2026-10-15
lang: zh
captured: 2026-10-15
extractor: readability-v1
translator: agent
status: translated
body_sha: 647c4bebe28d
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 纵深信任：给 agent 更多自主权，同时不失去控制

我和企业领导者的每一次交谈，听到的都是同一句话。他们希望 agent 做得更多，但又不信任它每次都能做对。

这很合理。让 agent 有用的正是那份创造力和自主性，而让它们难以信任的也正是它。交给 agent 一个任务，它会自己找到完成任务的路径，挑选工具、编排步骤，而这些都不是开发者写死的。同一个任务跑两遍，它每次可能走不同的路线。今天通过的测试，几乎告诉不了你明天这个 agent 会做什么。

常见的答案是人在回路中，审批 agent 做的每一件事。小规模时这行得通，但随着 agent 承担更多工作，人工审批不断堆积，复核疲劳随之而来。被要求检查一切的人，会开始漏掉真正要紧的东西。谨慎变成了瓶颈，而那些本来能做得多得多的 agent，就闲置在最能发挥影响的有价值工作上。

解决办法是：当 agent 的行动可以被验证时，就让它自行行动；把人的判断留给确实需要判断的决策。随着 agent 承担风险更高的工作，比如金融交易，一次错误行动的危害会越来越大。组织需要有信心把重要工作交给一个 AI agent，相信它会待在被设定的界限之内——即使没有任何人在看着。这份信心必须被建立起来。

内容过滤、测试和监控各自都承担重要用途，但单靠其中任何一项能力，都无法承诺 agent 下一次运行的行为是正确的。信任来自相互强化的独立分层——也就是这个行业已经实践了二十年、称为 Defense in Depth 的那套分层纪律，被转向了一个新的用途。Defense in Depth 限制的是可能出错的范围，而这一套扩展的是你可以安全放开的范围。AWS 称之为 **Trust in Depth。**

## **Trust in Depth：你能够验证的信任**

你通过在 agent 生命周期的不同时刻回答一组问题来建立信任：

- **Scope，运行之前：** 这个 agent 是为了什么，工作需要哪些能力，它绝不能做什么？
- **Know，部署之时：** 是谁授权了它，它携带什么身份，你能否对每一个代表你行事的 agent 逐一说明？
- **Bound，运行期间：** 它的行动是否待在你设定的界限之内，它还能不能完成工作？
- **Observe，每次运行之后：** 你能否重建 agent 做了什么、为什么这么做，并从中学习？

在这些问题上，有些要求可以表达为精确的规则，另一些则需要靠判断。一家公司可能要求只有经理才能批准访问，或者员工的邮箱在被共享之前必须先屏蔽其登录。而另一些期望，比如保持友好的语气、或恰当地处理敏感情形，取决于上下文和人的判断。

对于精确定义的规则，测试能显示控制措施在你预料到的情形里是否有效，但 agent 会走你没预料到的路径。走得更远的技术是 automated reasoning，即用数学逻辑检查一条规则是否在所有可能情形下都成立。它可以证明一条规则在“对该系统及其假设的精确描述”所覆盖的每一条路径上都成立，或者找出它失效的确切情形。这个结果是一个证明，而它只和背后的规则与假设一样可靠，这也是最难的功课要放在 agent 运行之前的原因。

AWS 已经在生产环境中[运行 automated reasoning 超过十年](https://www.amazon.science/blog/a-decade-of-mathematical-certainty-reflections-on-the-automated-reasoning-group)，从每秒超过 21 亿次请求的 Identity and Access Management (IAM)，到 AWS Nitro Hypervisor、Amazon S3 Block Public Access、VPC Reachability Analyzer 这样的关键系统。现在我们把它带到 agent 上。只要 agent 的规则能够被精确表述，automated reasoning 就能检查它们。

然而，并非每条规则都能被精确表述。“只有经理才能批准访问”可以被证明。“保持友好的语气”不能。在证明用不上的地方，就限制 agent 的访问与行动、评估它的行为，并把真正含糊的情形交给人来运用判断。当你确认相关规则得到执行、agent 在该任务上表现可靠、失败能够被发现和处理时，就给予更多自主权。

以下是 Trust in Depth 每一层对你的要求，以及 AWS 如何帮你回答它。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/15/trust-in-depth-hero-image-v2.png)

### 界定你的 agent，只覆盖工作真正需要的部分

信任始于 agent 运行之前，而这里正是最该投入精力的地方。在这里发现的问题修起来最便宜。界定范围意味着决定 agent 负责哪些工作、它可以触达哪些工具、数据和服务、它必须遵守哪些规则，以及哪些决策留在人手里。

“解决客户的问题”说的是要达成什么，而不是 agent 可以采取哪些行动去达成。agent 仍然需要界限：它能看到什么、能做什么、什么时候必须停下来询问。只给它的工作所需的访问权，一点不多。留意那些没有人有意授予的能力，那些随某个工具或某个角色打包而来的能力。为一个任务授予管理员角色，agent 就可能继承你整个环境范围内的权限。

界定范围始于构建阶段，始于你如何定义 agent。agentic 编码系统 [Kiro](https://kiro.dev/) 为 agent 的构建阶段带来严谨性和成熟的工程实践。它把高层意图转化为结构化、规格驱动的需求，并使用 automated reasoning 在写下任何代码之前暴露矛盾、歧义和缺口。Kiro 还会推导出基于属性的测试，在很宽的输入范围上拿这些需求校验实现，从而抓住那些难以检测的缺陷。[Strands](https://strandsagents.com/) 提供一套开源工具包，用于定义 agent 的模型、指令和工具，并提供一个托管运行时来运行它。无论你选择哪个框架，定义 agent 的工作及其边界这份责任都是一样的。

下一步是把这些边界变成你可以用来约束 agent 的规则。[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 提供治理控制，让 agent 能安全地规模化，并管住 agent 做了什么。使用 Bedrock AgentCore 中的 Policies，你用自然语言描述 agent 可以触达哪些工具、API 和数据，automated reasoning 会在策略生效之前检查策略的缺口，比如抓出一条授予了过多访问权的规则，并检查那些让规则永远无法被满足的矛盾。

为 agent 界定范围是困难的部分，因为把人的意图变成持久、可执行的策略需要精确和完备。但它同时也是回报最高的部分。后面的一切都建立在你此处设定什么之上，而策略越精确，你的 agent 就能越安全地自主做越多事。

### 了解每一个代表你行事的 agent，以及它受谁的授权

你无法治理你看不见的东西。团队创建 agent 的速度比任何人能跟踪的速度都快，而一个没人知道的 agent 就是一个没人控制的 agent。每个 agent 都需要自己的身份，并在它每次行动时都被校验。不应有任何行动成为无主之举。当出问题的时候，你要能说出是哪个 agent 做了什么、谁授权了它。

[AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) 提供一份托管的、经过审批的目录，覆盖你整个组织的 agent、Model Context Protocol (MCP) 服务器、工具和技能。管理员使用审批工作流来把关什么才可被发现，并移除不再满足安全、合规与质量标准的东西。人和 agent 都能找到并复用已经存在的资产，而不必重新构建。但目录只告诉你存在什么。一旦 agent 被知晓，AgentCore 会为每个 agent 签发自己的身份，并在每一次请求上校验它，于是每个行动都能追溯到一个在已知授权下运行的具体 agent。这就是你如何了解每一个代表你行事的 agent。

### 约束你的 agent 所言所行，使其待在你设定的界限之内

设定界限之所以重要，是因为 agent 可以走出 10 步你都批准了的行动，最终仍抵达一个没人想要的结果。它可能暴露敏感数据、偏离主题，或者以你策略禁止的方式组合被允许的行动。界限会在两个方向上失效。太松，agent 就会做它不该做的事；太紧，它就完全无法完成工作。所以，让 agent 自己选择如何推进任务，但绝不要指望它来执行自己的界限。这些界限定义了 agent 的边界，属于 agent 周围的环境，应当以确定性方式强制执行，并在整个行动序列上评估，而不是一步一步地看。

这一步正是你在 Scope 中定义的策略开始生效的地方。[AgentCore 中的 Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) 会在每一个经由 [AgentCore Gateway](https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-agentcore-gateway-transforming-enterprise-ai-agent-tool-development/)（面向 agent、工具和模型的安全入口）路由的工具调用上执行它。因为执行位于 agent 的推理之外，即使 agent 存在缺陷、被操纵、或遭到 prompt injection，同样的检查依然成立：它关不掉一个不由它运行的控制。权限也不必一直固定不变。由于任务的风险会随着推进而改变，[temporal policies](https://aws.amazon.com/blogs/machine-learning/securing-ai-agents-with-temporal-policies-in-amazon-bedrock-agentcore/) 会权衡会话中已经发生了什么，并在工作继续的过程中调整权限。[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 管住 agent 说什么、以及它被告知什么。它过滤有害或离题的内容，并对敏感数据做脱敏。[Automated Reasoning checks](https://www.youtube.com/watch?v=0uprEe_uCgc) 走得更远，它们证明一次回应与你设定的策略一致，而不是与模型对该策略的解读一致。

界限还管住 agent 一开始能够触达什么：它能碰哪些文件、能调用哪些服务、能使用哪些凭证。开源沙箱 [Strands Box](https://strandsagents.com/blog/strands-box-the-big-picture/) 从 agent 指令之外的位置强制执行这些界限，于是 agent 可以带着真实的工具和数据工作，却只能触达你允许的部分。同样的界限从开发者第一次本地会话一直成立到生产环境，因此 agent 在生产环境里做不了它在开发环境里做不到的事。

### 观察你的 agent 做了什么，然后改进它

即使界定范围、身份和界限都已就位，agent 仍可能在毫秒内给出回应、没有任何错误、每个仪表盘都一片绿灯，却做了错事。它可能检索了错误的信息、选错了工具，或者走了一条没人预料到的路径。系统健康并不等于任务成功。要分辨二者，你必须重建 agent 实际做了什么：它收到的上下文、它调用的工具、所适用的策略判定以及结果。部署前的测试依然必不可少。生产环境补充的是关于真实条件下行为的证据，并给运维人员提供调查、干预和改进所需的东西。

[Amazon CloudWatch Omni](https://aws.amazon.com/cloudwatch/omni/) 为持续观察而生。它捕获每一条 trace，并把 agent 走过的每一步——从模型调用到工具调用——铺陈在一条团队可以调查的时间线上。其内置的评估器会为 agent 的回应打分，评估那些标准监控漏掉的品质，例如正确性、忠实度，以及 agent 是否选对了工具。而 agent 出错的那些 trace 会变成你用来验证修复方案的数据集，于是运维一个 agent 与改进一个 agent 依赖的是同一份证据。

## **Trust in Depth 在实践中是什么样子**

一位经理请 help desk agent 为 Sam 办理离职，Sam 是一位即将离开公司的客户经理。agent 需要移除 Sam 的访问权限、把他的邮箱转交给继任者，并释放公司不再需要的 license。但 Sam 的邮件里也可能包含客户纠纷所需的证据。错误的顺序可能让 Sam 在离职后仍保有访问权限，或者让那份证据陷入风险。安全、消息系统、法务和财务各自都有 agent 必须遵守的要求，尽管没有人把完整的工作流写成脚本。

两条规则管辖着执行顺序。Sam 的登录必须先被屏蔽，他的邮箱才能被转换并与继任者共享。在更改他的邮件 license 之前，agent 必须检查是否存在 legal hold——为纠纷而保留记录的要求——并确认这次更改会让那些记录继续受到保护。

**Scope**。在 agent 运行之前，团队把这些规则写成 AgentCore 中的策略。每条策略都要求：Sam 账户上的前置步骤已经成功，下一步才能执行。agent 恰好拿到六个工具：屏蔽登录、检查 legal holds、施加 hold、转换邮箱、授予继任者访问权、更改 license。它没有拿到任何删除账户的工具，因为共享邮箱需要这个账户继续存在。

**Know**。agent 携带自己的身份，因此对 Sam 账户的每一项改动都能追溯到它。

**Bound**。agent 尝试把 Sam 的邮箱转换成共享邮箱，交给继任者 Priya。在 AgentCore Gateway 上执行的 AgentCore Policy 拦下了这次调用：Sam 仍然可以登录，而转换邮箱不会更改他的密码，所以他旧的凭证照样能打开它。agent 于是屏蔽了 Sam 的登录，然后转换邮箱并授予 Priya 访问权。接下来它转向经理真正的请求——释放 license，但网关也把它拦下了，因为还没人检查过法务的 hold 清单。agent 检查后发现，法务要求为一起客户纠纷保留 Sam 的邮件。它施加了 hold，确认其已生效，然后把 Sam 的 license 改为支持这种保护的那一档。公司因此可以收回那个更大的 license，同时让证据保持完整。

**Observe**。每一步都被记录下来：agent 试图做什么、规则如何裁定、那个 hold，以及结果。

agent 完成了任务，而没有让人审批每一个步骤。它的权限限制了它能改动什么，它的身份让那些改动可追溯，而策略在必要的保护措施就位之前阻止它行动。记录的步骤让团队得以验证 Sam 的访问已被屏蔽、他的继任者可以使用该邮箱，而所需的证据仍处于受保护状态。

## **当 agent 值得信任时，什么变得可能**

AWS 把这些层聚合在一起，让你能够把一个 agent 界定到它的职责、知道哪些 agent 正在代表你行事、约束它们做什么和说什么、看见它们做了什么并随时间改进，并在规则可以被精确表述的地方证明它们成立。没有任何单独一层能凭自己赢得这份信任。合在一起，它们就是 Trust in Depth，也正是它们把一个有能力的 agent 变成值得信任、可以去做重要工作的 agent。

线由你来画：agent 可以独自做什么、什么需要人批准、它什么时候必须停下。这就把你的人解放出来，去做只有人能做的事：权衡艰难的取舍、化解灰色地带、承担你选择留在人手里的决策。随着 agent 待在这些线内的证据不断累积，你可以扩大或收窄它的职责。

在 AWS，我们相信每一个部署 agent 的组织，无论使用哪个平台，都应当能用证据回答这四个问题，并在适用的地方用证明来回答。这就是 AWS 为我们的客户搭建的标杆，也是我们邀请整个行业用以自我要求的标准。Defense in Depth 让系统安全地接入世界，Trust in Depth 则让 agent 安全地在其中自主行动。

从一个 agent、一个工作流、一条你能证明的界限开始。然后随着信任被赢得，再向外扩展。

若要开始实现可执行的规则，可以了解 [Amazon Bedrock AgentCore 中的 Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) 与 [Amazon Bedrock Guardrails 中的 Automated Reasoning checks](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html)。

## 关于作者
