---
vendor: aws_bedrock
title: Agent Skills for Automated Reasoning policies in Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/agent-skills-for-automated-reasoning-policies-in-amazon-bedrock
date: 2026-08-06
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 38a00ab4de40
---

# 用于 Amazon Bedrock 中 Automated Reasoning 策略的 Agent Skills

采用 Amazon Bedrock Automated Reasoning 检查的团队，往往希望用代码来运行策略生命周期。用代码运行可以让工作可重复、可审查，并由他们已经在用的编码 agent 驱动。编写一份好的 Automated Reasoning 策略存在学习曲线，生命周期里也有一些容易让人踩坑的约束。你需要用 SMT-LIB 的一个子集（面向自动定理证明器的标准输入格式）来编写规则，并反复调整变量描述，直到服务能正确翻译真实用户的语言。你还要让策略走完一个构建、测试与完善的循环，而这个循环有自己的 API 和约束。

[Automated Reasoning 检查](https://aws.amazon.com/blogs/machine-learning/minimize-generative-ai-hallucinations-with-amazon-bedrock-automated-reasoning-checks/)值得这份投入，因为它依据形式逻辑来验证输出，而不是对输出做统计抽样。这种做法让你可以数学上确定 AI 响应符合你的规则。在 [Build reliable AI systems with Automated Reasoning on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-systems-with-automated-reasoning-on-amazon-bedrock-part-1/) 一文中，我们在 Amazon Bedrock 控制台里走完了这个循环。控制台是合适的起点，也适合与主题专家协作。

本文介绍如何使用一套 Agent Skills，从编码 agent 出发端到端地构建、测试、部署和验证 Amazon Bedrock Automated Reasoning 策略。你还会看到，把这套技能跑在 Amazon Bedrock 上，揭示了该服务行为方式的哪些特点。

## 什么是 Agent Skills？

[Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) 是 Anthropic 推出的一种轻量、开放的格式。技能（skill）用专门的知识和工作流来扩展编码 agent。它是一个结构化的上下文包，教会 agent 如何正确使用某项特定服务或领域。agent 不再依赖可能不完整或已过时的通用训练数据。每项技能都带有经过验证的模式、需要避免的常见错误，以及分步骤的工作流。有了这些指导，agent 会针对任务给出正确的调用，而不是一个看似合理的猜测。由于格式是开放的，技能可以安装到任何支持它的 agent 中，包括 Kiro、Claude Code、Cursor 和 Codex。之后当你向 agent 询问该技能覆盖的任务时，它会自动激活。

## 为什么 agent 契合 Automated Reasoning 生命周期

一次 Automated Reasoning 检查分两步运行，理解这种分工是使用它的关键。首先，一组基础模型（foundation model，FM）把问题和回答翻译成形式逻辑，把自然语言映射到策略中的变量。然后由一个 SMT 求解器（Satisfiability Modulo Theories，即按约束检查逻辑公式的自动推理引擎）依据你的规则验证该逻辑并返回裁决。验证这一步在数学上是可靠的：如果翻译忠实，裁决就是正确的。这种可靠性也正是结果可解释的原因。每个裁决都会带回支持或反驳它的具体规则。

图 1：Automated Reasoning 检查的工作方式

真正的工作在于围绕这次检查的生命周期。你要从源文档中抽取规则、审查服务产出的结果、编写能反映用户真实提问方式的测试、诊断失败，并把带版本的策略部署在 guardrail 之后。每一步都有特定的 API 形态，其中几步还有容易踩坑的约束。这是规则清晰、失败模式明确的重复性细节工作，正是编码 agent 在给对指令时能够处理得好的那类工作。

## 策略生命周期中的六项技能

这套技能由六项 Agent Skills 组成，对应生命周期的每个阶段。每项技能都是一个简短的指令文件，教会 agent 在该阶段应有的判断，并配有小巧可运行的脚本，用于调用 Amazon Bedrock Automated Reasoning API。所有技能共享一份参考文档，描述 API 接口面、发现（finding）类型和规则语法，从而让整套技能的指导保持一致。

图 2：贯穿策略生命周期的六项技能

在编写阶段，**builder** 技能从源文档创建策略，并抽取其中的规则和变量。**reviewer** 技能读取构建产出的质量和保真度报告，标记冲突规则、未使用变量和裸断言（bare assertion）等问题。**tester** 技能生成场景并运行问答测试，检查策略是否按你预期的方式翻译和验证真实输入。**debugger** 技能诊断失败并修复策略，遵循的原则是：错误的裁决几乎总是来自翻译问题，而不是规则本身。

在运行时，**deployer** 技能为编号的策略版本做快照，并把它挂到 guardrail 上。**validator** 技能使用 `ApplyGuardrail` API 检查回答。它还可以运行一个重写循环：把失败回答所违反的规则回传给模型，直到回答站得住脚。

## 技能的结构

每项技能都遵循标准的 Agent Skills 布局。`SKILL.md` 文件存放该阶段的核心指令，包括技能的适用时机以及该技能特有的判断取舍。`references/` 目录存放更深入的材料，例如发现类型和规则语法，agent 只在需要细节时才加载它们。`scripts/` 目录存放可运行的 Python 代码，用于调用 Amazon Bedrock Automated Reasoning API。脚本是独立的，并提供 `--help` 和 `--dry-run` 两个开关。你可以了解某个操作做了什么，并在请求真正到达 Amazon Bedrock 之前检查确切的请求内容。六项技能底下的一个共享库负责处理公共工作：创建客户端、轮询构建工作流、解析发现，以及管理本文后面会提到的构建槽位上限。

## 从策略文档到经过验证的回答

下面的演练在一份关于育儿假资格的简短人力资源策略上跑完整生命周期。这个例子很紧凑，以便流程清晰；同样的步骤也适用于贷款资格策略、保险承保策略，以及其他回答必须遵循书面规则的领域。

### 前置条件

你需要一个 AWS 账号，能够访问提供 Automated Reasoning 检查的 AWS 区域中的 Amazon Bedrock；需要 Amazon Bedrock 控制平面和运行时 API 的权限；还需要带 [uv](https://docs.astral.sh/uv/) 的 Python 来运行脚本。关于各区域的功能可用性，请参阅 Amazon Bedrock 文档中的 [Automated Reasoning 检查](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html)。克隆仓库，然后把技能安装到你的编码 agent 中。

在 Claude Code 中，把这套技能添加为插件市场，然后安装你需要的技能：

```
/plugin marketplace add ./amazon-bedrock-samples/responsible_ai/automated-reasoning-checks-skills
/plugin install ar-policy-builder@automated-reasoning-skills
```

对于支持该开放格式的其他 agent，例如 Kiro、Cursor 和 Codex，可使用 `npx` 安装：

```
# the skills live in a subfolder, so point npx at the full tree URL
REPO=https://github.com/aws-samples/amazon-bedrock-samples
SUBDIR=responsible_ai/automated-reasoning-checks-skills

npx skills add $REPO/tree/main/$SUBDIR --skill '*'
```

无论用哪种方式，当你向 agent 询问匹配的任务时（例如从文档创建策略，或调试失败的测试），技能都会自动激活。

### 创建策略并抽取规则

从一份用平实语言陈述规则的简短源文档开始，例如：任职超过 12 个月的全职员工有资格享受育儿假，兼职员工则不符合。builder 技能创建策略资源，并启动一次构建，从文档中抽取形式化规则和变量 schema。

```
uv run create_policy.py --name "hr-leave-policy" \
--description "Validates parental leave eligibility answers"

uv run build_from_document.py --policy-arn <policy-arn> \
--file leave-policy.txt --doc-name "Leave Policy" \
--instructions "Capture full-time status and tenure in months; focus on eligibility."
```

在一次运行中，构建从三句源文本里抽取了六条规则、四个变量和一个自定义类型，其中包含一条保证任职时长为非负的边界规则。

### 审查服务的产出

规则抽取不是确定性的，所以在测试之前先审查结果。reviewer 技能会拉取质量报告和策略定义并做汇总。

```
uv run audit_policy.py --policy-arn <policy-arn>
```

审计会报告规则、变量和类型的数量，然后按严重级别标记结构性问题。对这份策略，它指出一个未使用的变量和一个彼此不相交的规则集，二者都是低严重级别的“可考虑项”而非错误。它还会报告没有生成保真度报告，因为标准的内容构建不会生成该报告。当你需要为主题专家提供源文本溯源视图时，可以用单独的构建类型来请求它。

### 编写并运行测试

tester 技能创建一个问答测试，并针对已完成的构建运行它。一个测试会陈述用户可能提出的问题、你的模型可能给出的回答，以及你期望的裁决。

```
uv run create_test.py --policy-arn <policy-arn> \
--input "I'm full-time with 18 months. Am I eligible for leave?" \
--output "Yes, you are eligible for parental leave." \
--expected VALID

uv run run_tests.py --policy-arn <policy-arn>
```

测试工作流返回期望裁决和实际裁决，以及两者是否一致。对这份策略，回答验证为 `VALID`，实际结果与期望结果一致。

### 部署到 guardrail 之后并验证回答

策略通过测试后，deployer 技能为一个不可变的编号版本做快照并把它挂到 guardrail 上，validator 技能则检查一个真实回答。

```
uv run create_version.py --policy-arn <policy-arn>
uv run deploy_guardrail.py --policy-arn <policy-arn> \
--policy-version 1 --guardrail-name hr-leave-guardrail

uv run validate_response.py --guardrail-id <guardrail-id> --guardrail-version 1 \
--question "I'm full-time with 18 months. Am I eligible for parental leave?" \
--answer "Yes, you are eligible for parental leave."
```

validator 返回发现结果，并确认检查确实执行了。这里回答返回 `VALID`，并附上支持它的规则，这就是你为经过验证的响应所保留的审计轨迹。

## 运行这套技能给我们的启示

在 Amazon Bedrock 上跑完整个生命周期后，有两点经验格外突出，它们也决定了这些技能的行为方式。

第一点是，可解释性处于该特性工作方式的核心。每个裁决都会返回其背后的规则：对 `VALID` 的回答返回支持规则，对 `INVALID` 的回答返回相冲突的规则。validator 技能会记录这些内容，因此一个通过验证的回答会附带它为何被允许的、可在数学上核验的证明，而被拒绝的回答会把它所违反的确切规则带入重写步骤。下图描绘了运行时的这个重写循环。检查返回非 VALID 的裁决并给出回答所违反的规则，模型按该规则重写回答，检查再次运行，直到回答站得住脚。

图 3：运行时的重写循环

第二点是，`SATISFIABLE` 裁决并不是失败。Automated Reasoning 区分两种情况：回答与你的策略一致，以及回答被你的策略所蕴含。假设有一条规定说任职时长达标的全职员工符合条件。一个断言其符合条件的回答与策略一致，但并未被策略证明，因此服务返回 `SATISFIABLE` 而不是 `VALID`。把这个结果当成失败，会让你去改动本来正确的规则。debugger 技能把这一区分固化下来，使 agent 按服务定义的方式来解读裁决。

还有一个实际约束值得一提，因为技能已经替你处理了它。一份策略允许的并发构建工作流数量有限，而一次较长的细化会话可能会触及该上限。技能会在每次构建之前自动删除最早完成的构建来释放一个槽位，因此经过多轮细化的 agent 不会因这个上限而卡住。

## 清理

为避免持续产生费用，请按依赖顺序删除你创建的资源，因为当测试用例、构建工作流或版本仍然存在时，策略无法删除。先移除测试用例，再移除构建工作流和编号版本，然后移除策略，最后移除 guardrail。技能在拆除资源时遵循这一顺序，你也可以从 Amazon Bedrock 控制台删除所有内容。

## 结论

Automated Reasoning 检查为 AI 回答提供可验证、可解释的裁决，而这些裁决的质量取决于它们背后的策略。本文介绍的 Agent Skills 把完整的编写生命周期搬进代码，使策略的构建、审查、测试、调试、部署和验证成为编码 agent 可以执行、你可以审查的可重复步骤。这种做法并不局限于育儿假这个例子，也不局限于某一个 agent。它适用于从金融到保险再到医疗的各种策略领域，并且可以安装到你已经在用的编码 agent 中。

要开始使用：

- 从[代码仓库](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/responsible_ai/automated-reasoning-checks-skills)把技能安装到你的编码 agent 中。
- 让 builder 技能指向你自己的策略文档，并审查质量报告。
- 添加能反映用户提问方式的问答测试，并不断细化直到它们通过。
- 把带版本的策略部署到 guardrail 之后，并用运行时技能验证回答。

要进一步深入，请浏览以下相关资源：

- [Build reliable AI systems with Automated Reasoning on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-systems-with-automated-reasoning-on-amazon-bedrock-part-1/)，了解控制台工作流。
- [How Automated Reasoning checks in Amazon Bedrock transform generative AI compliance](https://aws.amazon.com/blogs/machine-learning/how-automated-reasoning-checks-in-amazon-bedrock-transform-generative-ai-compliance/)，了解合规视角。
- [Automated Reasoning checks rewriting chatbot](https://aws.amazon.com/blogs/machine-learning/automated-reasoning-checks-rewriting-chatbot-reference-implementation/)，了解一个运行时参考实现。
- [Amazon Bedrock Automated Reasoning 检查用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html)和 [Amazon Bedrock API 参考](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html)。

## 关于作者
